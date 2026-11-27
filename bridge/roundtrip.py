"""Prove that an empty answer from this account means "nothing there".

    uv run python -m bridge.live --roundtrip        # on Practice first

docs/ARTIFACT_CLASSES.md class 3. ``Order/searchOpen`` and
``Position/searchOpen`` answer ``success`` with an empty list both when there
is nothing open and when the request is subtly wrong -- an account id for a
different account, a key the response no longer uses, a ``contractId`` that
comes back in a different format from the one ``LiveEngine.ours`` filters on.
The engine reads empty as flat, ends the day, exits 0, and the wrapper shuts
the machine down. With a position open, that is an unattended position.

So the engine is not allowed to believe an empty answer until this account and
this contract id have been seen to give a NON-empty one. This places a single
one-lot buy limit far below the market, where it cannot fill, requires it to
appear in ``ours(open_orders())``, cancels it, and requires it to disappear.
Only then is a proof written. ``bridge.live --live`` reads the proof; without a
matching one it never ends the day clean (so never triggers a shutdown) and the
deadline sweep cancels every order it sent rather than trusting an empty book.

Positions cannot be proven this way without a fill. What this does prove is
the half that breaks them: the account id is right, the response key is right,
and the ``contractId`` the server echoes matches the one we filter on.

Re-run after every contract roll and every account switch: the proof is keyed
on both and a mismatch is treated as no proof.
"""

from __future__ import annotations

import json
import pathlib
import re
import time
from typing import Any, Callable

import pandas as pd

from ict import data as D

from .config import Config
from .topstepx import BrokerError, Order

PROOF_PATH = D.REPO_ROOT / "data" / "roundtrip_proof.json"

#: How far below the last close the probe order rests. 30% on NQ is a move
#: that has never happened in a session; the order cannot fill.
PROBE_DISTANCE = 0.30
POLLS = 10
POLL_S = 1.0


def proof_path(cfg: Config) -> pathlib.Path:
    """One proof file per engine, so several accounts on one computer do not overwrite each other's proof.

    The original Topstep NQ engine keeps the original path."""
    if cfg.broker == "topstepx" and cfg.market == "NQ":
        return PROOF_PATH
    slug = re.sub(r"[^A-Za-z0-9]+", "_", cfg.engine_id).strip("_")
    return PROOF_PATH.with_name(f"roundtrip_proof_{slug}.json")


def proof_holds(cfg: Config, path: pathlib.Path = PROOF_PATH) -> bool:
    """A proof exists for exactly this account and this contract id."""
    try:
        proof = json.loads(pathlib.Path(path).read_text())
    except (OSError, ValueError):
        return False
    return (proof.get("account_id") == cfg.account_id
            and proof.get("account_name") == cfg.account_name
            and proof.get("contract_id") == cfg.contract_id
            and proof.get("ok") is True)


def _ours(rows: list[dict[str, Any]], cfg: Config) -> list[dict[str, Any]]:
    # Same test as LiveEngine.ours -- the thing being proven is that filter.
    return [r for r in rows if r.get("contractId") == cfg.contract_id]


def prove(cfg: Config, broker, journal, *, path: pathlib.Path = PROOF_PATH,
          sleep: Callable[[float], None] = time.sleep,
          now: Callable[[], pd.Timestamp] | None = None) -> bool:
    """Place, see, cancel, see gone. Writes the proof only if all four hold."""
    clock = now or (lambda: pd.Timestamp.now(tz="UTC"))
    pathlib.Path(path).unlink(missing_ok=True)

    t = clock()
    bars = broker.retrieve_bars(t - pd.Timedelta(days=4), t)
    if bars.empty:
        journal.write("roundtrip_failed", step="bars",
                      why="no bars to price the probe from; fix the bar feed first")
        return False
    last = float(bars["close"].iloc[-1])
    entry = round(last * (1 - PROBE_DISTANCE) / cfg.tick_size) * cfg.tick_size
    probe = Order(side="buy", size=1, entry=entry, stop=entry - 20.0,
                  target=entry + 20.0, tag="roundtrip probe")

    try:
        placed = broker.place(probe)
        order_id = placed["orderId"]
        if order_id is None or str(order_id) == "":
            raise ValueError("no orderId in the place response")
    except (BrokerError, KeyError, TypeError, ValueError) as exc:
        journal.write("roundtrip_failed", step="place", error=str(exc))
        return False
    journal.write("roundtrip_placed", order_id=order_id, entry=entry, last=last)

    def visible() -> bool | None:
        try:
            return any(str(r.get("id")) == str(order_id)
                       for r in _ours(broker.open_orders(), cfg))
        except (BrokerError, KeyError, TypeError, ValueError) as exc:
            journal.write("roundtrip_query_failed", error=str(exc))
            return None

    seen = False
    for _ in range(POLLS):
        if visible():
            seen = True
            break
        sleep(POLL_S)

    try:
        broker.cancel(order_id)
    except BrokerError as exc:
        journal.write("roundtrip_failed", step="cancel", order_id=order_id,
                      error=str(exc))
        return False

    if not seen:
        journal.write("roundtrip_failed", step="see", order_id=order_id,
                      why="a resting order of ours never appeared in "
                          "ours(open_orders()): an empty answer from this "
                          "account cannot be trusted")
        return False

    gone = False
    for _ in range(POLLS):
        if visible() is False:
            gone = True
            break
        sleep(POLL_S)
    if not gone:
        journal.write("roundtrip_failed", step="gone", order_id=order_id,
                      why="the probe is still listed after cancel; check the "
                          "platform by hand")
        return False

    proof = {"ok": True, "account_id": cfg.account_id, "account_name": cfg.account_name,
             "contract_id": cfg.contract_id, "order_id": order_id,
             "at": clock().isoformat()}
    pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)
    pathlib.Path(path).write_text(json.dumps(proof, indent=2))
    journal.write("roundtrip_ok", **proof)
    return True


#: Bracket probe (CrossTrade only): how far above the last close the buy limit goes, so it fills at once on a sim
#: account, and how far the stop and target sit from the entry (points).
BRACKET_PROBE_ABOVE = 10.0
BRACKET_PROBE_DISTANCE = 40.0
BRACKET_POLLS = 20


def bracket_probe(cfg: Config, broker, journal, *, sleep: Callable[[float], None] = time.sleep,
                  now: Callable[[], pd.Timestamp] | None = None, drive: Callable[[], None] | None = None) -> bool:
    """Prove the part ``prove`` cannot: a FILLED entry gets its stop and target, and flattening clears both.

    CrossTrade attaches the stop and target only after the entry fills (bridge/crosstrade.py), and a never-filling
    probe never reaches that code. This buys 1 contract at the market on a SIM account, requires the position plus
    exactly the two protective orders at the intended prices, then flattens and requires no position and no
    order left. Refuses any account whose name does not start with "Sim". ``drive`` is for tests (runs the fill
    watcher in step); the real broker runs it on its own thread.
    """
    clock = now or (lambda: pd.Timestamp.now(tz="UTC"))
    if cfg.broker != "crosstrade" or not str(cfg.account_name or "").lower().startswith("sim"):
        journal.write("bracket_probe_refused", why="CrossTrade sim accounts only (name must start with 'Sim')",
                      account=cfg.account_name)
        return False
    t = clock()
    bars = broker.retrieve_bars(t - pd.Timedelta(days=4), t)
    if bars.empty:
        journal.write("bracket_probe_failed", step="bars", why="no bars to price the probe from")
        return False
    last = float(bars["close"].iloc[-1])
    entry = round((last + BRACKET_PROBE_ABOVE) / cfg.tick_size) * cfg.tick_size
    probe = Order(side="buy", size=1, entry=entry, stop=entry - BRACKET_PROBE_DISTANCE,
                  target=entry + BRACKET_PROBE_DISTANCE, tag="bracket probe")
    try:
        placed = broker.place(probe)
    except (BrokerError, KeyError, TypeError, ValueError) as exc:
        journal.write("bracket_probe_failed", step="place", error=str(exc))
        return False
    want = placed.get("bracket") or {}
    journal.write("bracket_probe_placed", order_id=placed.get("orderId"), entry=entry, last=last, bracket=want)

    def state():
        orders = _ours(broker.open_orders(), cfg)
        held = _ours(broker.open_positions(), cfg)
        stops = [o for o in orders if "stop" in str(o.get("orderType", "")).lower()]
        limits = [o for o in orders if str(o.get("orderType", "")).lower() == "limit"]
        return orders, held, stops, limits

    protected, last_seen = False, None
    for _ in range(BRACKET_POLLS):
        if drive:
            drive()
        try:
            orders, held, stops, limits = state()
        except (BrokerError, KeyError, TypeError, ValueError) as exc:
            journal.write("bracket_probe_query_failed", error=str(exc))
            sleep(POLL_S)
            continue
        last_seen = {"orders": len(orders), "positions": len(held)}
        if (held and len(stops) == 1 and len(limits) == 1
                and abs(float(stops[0].get("stopPrice", 0)) - float(want.get("stopLoss", -1))) < 1e-6
                and abs(float(limits[0].get("limitPrice", 0)) - float(want.get("takeProfit", -1))) < 1e-6):
            protected = True
            journal.write("bracket_probe_protected", position=int(held[0].get("size", 0)),
                          stop=stops[0].get("stopPrice"), target=limits[0].get("limitPrice"),
                          oco=[stops[0].get("ocoId"), limits[0].get("ocoId")])
            break
        sleep(POLL_S)

    # Flatten whatever happened, protected or not: this probe must never leave anything behind.
    try:
        broker.close_position()
    except BrokerError as exc:
        journal.write("bracket_probe_failed", step="flatten", error=str(exc),
                      why="CHECK NINJATRADER: the sim position may still be open")
        return False
    clean = False
    for _ in range(POLLS):
        try:
            orders, held, _, _ = state()
        except (BrokerError, KeyError, TypeError, ValueError) as exc:
            journal.write("bracket_probe_query_failed", error=str(exc))
            sleep(POLL_S)
            continue
        if not orders and not held:
            clean = True
            break
        sleep(POLL_S)
    if not protected:
        journal.write("bracket_probe_failed", step="protect", last_seen=last_seen,
                      why="no position with exactly one stop and one target at the intended prices")
    if not clean:
        journal.write("bracket_probe_failed", step="flatten", why="orders or a position still listed after flatten")
    ok = protected and clean
    if ok:
        journal.write("bracket_probe_ok", account=cfg.account_name, contract_id=cfg.contract_id, at=clock().isoformat())
    return ok


#: Exit probe: a SHORT whose stop and target are this close (points) so one of them is hit within minutes.
EXIT_PROBE_DISTANCE = 3.0
EXIT_PROBE_WAIT_S = 600.0


def exit_probe(cfg: Config, broker, journal, *, sleep: Callable[[float], None] = time.sleep,
               now: Callable[[], pd.Timestamp] | None = None, drive: Callable[[], None] | None = None,
               wait_s: float = EXIT_PROBE_WAIT_S) -> bool:
    """Prove the exit half on a SIM account: a short entry is protected, then the market hits the stop or the target
    and the position goes flat BY ITSELF with the other order cancelled (one-cancels-other). Sells 1 contract at the
    market with stop and target 3 points away. If neither is hit within ``wait_s`` the probe flattens and fails as
    inconclusive. Refuses any account whose name does not start with "Sim".
    """
    clock = now or (lambda: pd.Timestamp.now(tz="UTC"))
    if cfg.broker != "crosstrade" or not str(cfg.account_name or "").lower().startswith("sim"):
        journal.write("exit_probe_refused", why="CrossTrade sim accounts only (name must start with 'Sim')",
                      account=cfg.account_name)
        return False
    t = clock()
    bars = broker.retrieve_bars(t - pd.Timedelta(days=4), t)
    if bars.empty:
        journal.write("exit_probe_failed", step="bars", why="no bars to price the probe from")
        return False
    last = float(bars["close"].iloc[-1])
    entry = round((last - BRACKET_PROBE_ABOVE) / cfg.tick_size) * cfg.tick_size   # sell limit below: fills at once
    probe = Order(side="sell", size=1, entry=entry, stop=entry + EXIT_PROBE_DISTANCE,
                  target=entry - EXIT_PROBE_DISTANCE, tag="exit probe")
    try:
        placed = broker.place(probe)
    except (BrokerError, KeyError, TypeError, ValueError) as exc:
        journal.write("exit_probe_failed", step="place", error=str(exc))
        return False
    journal.write("exit_probe_placed", order_id=placed.get("orderId"), entry=entry, last=last,
                  bracket=placed.get("bracket"))

    protected, flat, waited = False, False, 0.0
    while waited <= wait_s:
        if drive:
            drive()
        try:
            orders = _ours(broker.open_orders(), cfg)
            held = _ours(broker.open_positions(), cfg)
        except (BrokerError, KeyError, TypeError, ValueError) as exc:
            journal.write("exit_probe_query_failed", error=str(exc))
            orders = held = None
        if held is not None:
            if held and len(orders) == 2 and not protected:
                protected = True
                journal.write("exit_probe_protected", position=int(held[0].get("size", 0)),
                              side=held[0].get("marketPosition"))
            if protected and not held and not orders:
                flat = True
                journal.write("exit_probe_exited", after_s=waited,
                              why="stop or target filled and the other was cancelled; no order left")
                break
        sleep(POLL_S)
        waited += POLL_S

    if not flat:
        try:
            broker.close_position()
        except BrokerError as exc:
            journal.write("exit_probe_failed", step="flatten", error=str(exc),
                          why="CHECK NINJATRADER: the sim position may still be open")
            return False
        journal.write("exit_probe_failed", step="exit", protected=protected,
                      why="no exit by itself within the wait (quiet market?) or the bracket never appeared; "
                          "flattened by the probe")
        return False
    journal.write("exit_probe_ok", account=cfg.account_name, contract_id=cfg.contract_id, at=clock().isoformat())
    return True

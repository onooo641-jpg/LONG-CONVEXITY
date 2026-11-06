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


def proof_holds(cfg: Config, path: pathlib.Path = PROOF_PATH) -> bool:
    """A proof exists for exactly this account and this contract id."""
    try:
        proof = json.loads(pathlib.Path(path).read_text())
    except (OSError, ValueError):
        return False
    return (proof.get("account_id") == cfg.account_id
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
        order_id = int(placed["orderId"])
    except (BrokerError, KeyError, TypeError, ValueError) as exc:
        journal.write("roundtrip_failed", step="place", error=str(exc))
        return False
    journal.write("roundtrip_placed", order_id=order_id, entry=entry, last=last)

    def visible() -> bool | None:
        try:
            return any(int(r.get("id", -10**9)) == order_id
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

    proof = {"ok": True, "account_id": cfg.account_id,
             "contract_id": cfg.contract_id, "order_id": order_id,
             "at": clock().isoformat()}
    pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)
    pathlib.Path(path).write_text(json.dumps(proof, indent=2))
    journal.write("roundtrip_ok", **proof)
    return True

"""CrossTrade client: NinjaTrader 8 accounts (Lucid, DayTraders, FFN) through the CrossTrade NT8 Add-On.

Every path, field and response below is from CrossTrade's API reference (crosstrade.io/docs/api, rendered
2026-11-27 by GitHub Actions run 45929437254, saved as data/public/propverify/expand_osstrade_io_docs_api_*.json).
None of it has met a real server yet; `python -m bridge.live --roundtrip` is the first time it does.

    Auth            Authorization: Bearer <CrossTrade secret key>  (one key per CrossTrade user; no login call)
    GET  /v1/api/accounts                                   -> {accounts: [{id, name, status}], success}
    GET  /v1/api/accounts/{account}                         -> {name, connectionStatus, item: {...}, success}
    POST /v1/api/accounts/{account}/orders/place            {instrument, action BUY|SELL, quantity, orderType LIMIT,
                                                             timeInForce DAY, limitPrice, orderId (ours)}
                                                            -> {orderId (NT8's), disposition, success}
    GET  /v1/api/accounts/{account}/orders/{id}             full NT8 order: orderState, filled, ... (our id works too)
    GET  /v1/api/accounts/{account}/orders?activeOnly=true  -> {orders: [...], success}
    POST /v1/api/accounts/{account}/orders/{id}/cancel      -> {orderId, success}   (missing/terminal -> HTTP 400)
    POST /v1/api/accounts/{account}/orders/cancel_and_bracket
                                                            {instrument, action (side of the POSITION), quantity,
                                                             takeProfit, stopLoss} -> {cancelled, placed, ocoId}
    GET  /v1/api/accounts/{account}/positions               -> {positions: [{instrument, marketPosition, quantity}]}
    POST /v1/api/accounts/{account}/positions/flatten       {instrument, cancelOrders: true}
    POST /v1/api/market/bars                                {instrument, periodType minute, period 1, from, to, limit}
                                                            -> {bars: [{time, open, high, low, close, volume}]}
    Rate limit      3 requests/s per CrossTrade user (burst 20), shared by every engine using the same key.
                    HTTP 429 means "refused before execution" and carries Retry-After, so it is safe to retry.
    Plan            The Trading API needs CrossTrade Pro or above.

Three differences from TopstepX that the code has to absorb:

* **No bracket attached at entry.** ProjectX takes the stop and target with the entry; NT8 through CrossTrade
  does not (its REST place order has no stop-loss / take-profit fields, and NT8 has no one-sends-other order).
  So the entry goes in alone, and a watcher thread polls it; on the first fill it calls cancel_and_bracket, which
  cancels everything still working on the instrument (the unfilled rest of the entry too) and places an OCO
  stop + target for the position actually held. The position is unprotected for at most about one poll
  (``CROSSTRADE_PROTECT_POLL_S``, 2 s by default) plus the request time. If the bracket cannot be placed after
  three tries the watcher flattens the position: an open position with no stop is worse than a closed one.
  If the engine process dies while an entry rests, nothing protects that entry -- cancel it by hand in NT8.
* **Order ids are strings and can change.** NT8 may re-assign its own id; CrossTrade keeps the id we chose
  (stored in the order's UserData as AutomatedTradingOrderId) and accepts it for lookup and cancel. This client
  sends its own id with every entry, returns that id, and reports listed orders under it.
* **Bars are stamped at their close.** NinjaTrader times a bar by its end; the research engine (and TopstepX)
  time it by its start. ``parse_bars`` moves every bar back one period, so an NT8 bar stamped 10:01 is the
  10:00 bar here. The real server says so itself (``timestampConvention: bar_close``, 2026-11-27). It also
  sends the bar still forming and bars older than ``from``; both are cut off on this side.
"""

from __future__ import annotations

import json
import re
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from dataclasses import dataclass, field
from typing import Any, Callable

import pandas as pd

from .config import Config
from .topstepx import BAR_COLUMNS, BrokerError, Order, bracket_ticks, snap_entry

#: NinjaTrader OrderState values after which an order can never fill again.
DEAD_STATES = {"Cancelled", "Rejected"}
#: Bracket attempts before the watcher gives up and flattens the position.
PROTECT_TRIES = 3
#: 429 retries per request (each waits Retry-After). A 429 is refused before execution, so a retry cannot double.
RATE_LIMIT_RETRIES = 3

_CUSTOM_ID = re.compile(r"AutomatedTradingOrderId\s*(?:>|=\s*[\"'])\s*([^<\"']+)")


def new_order_id() -> str:
    """Our id for an entry: unique, and short enough for NT8's UserData."""
    return f"lc-{uuid.uuid4().hex[:20]}"


def _need(cfg: Config) -> None:
    if not cfg.account_name:
        raise BrokerError("no NinjaTrader account name; set CROSSTRADE_ACCOUNT")
    if not cfg.instrument:
        raise BrokerError("no NinjaTrader instrument; set CROSSTRADE_INSTRUMENT (e.g. 'MNQ 12-26')")


def bracket_levels(order: Order, cfg: Config) -> tuple[float, float, float]:
    """(entry, stop, target) on the tick grid.

    The entry is snapped exactly as for TopstepX (``snap_entry``), and the stop and target sit the same whole
    number of ticks from it as the TopstepX bracket would (``bracket_ticks``), so both connectors put the exits
    at the same prices for the same signal.
    """
    entry = snap_entry(order.entry, order.side, cfg.tick_size)
    sl = bracket_ticks(entry, order.stop, cfg.tick_size) * cfg.tick_size
    tp = bracket_ticks(entry, order.target, cfg.tick_size) * cfg.tick_size
    if order.side == "buy":
        stop, target = entry - sl, entry + tp
    else:
        stop, target = entry + sl, entry - tp
    return round(entry, 10), round(stop, 10), round(target, 10)


def entry_payload(order: Order, cfg: Config, order_id: str) -> dict[str, Any]:
    """Body of POST /orders/place for the entry. Pure, so the tests can read it."""
    if order.size < 1:
        raise BrokerError(f"refusing to send an order for {order.size} contracts")
    _need(cfg)
    entry, _, _ = bracket_levels(order, cfg)
    return {
        "instrument": cfg.instrument,
        "action": "BUY" if order.side == "buy" else "SELL",
        "quantity": int(order.size),
        "orderType": "LIMIT",
        # DAY, not GTC: an entry the engine failed to cancel must not survive into tomorrow's session.
        "timeInForce": "DAY",
        "limitPrice": entry,
        "orderId": order_id,
    }


def bracket_payload(order: Order, cfg: Config) -> dict[str, Any]:
    """Body of POST /orders/cancel_and_bracket once the entry has filled.

    ``action`` is the side of the position being protected (CrossTrade then sends the opposite-side exits), and
    ``quantity`` is the order size; CrossTrade clamps it to the position actually held, so a partial fill gets a
    bracket for what filled.
    """
    _need(cfg)
    _, stop, target = bracket_levels(order, cfg)
    return {
        "instrument": cfg.instrument,
        "action": "Buy" if order.side == "buy" else "Sell",
        "quantity": int(order.size),
        "takeProfit": target,
        "stopLoss": stop,
    }


def _utc(ts) -> str:
    """A ``from``/``to`` value for /market/bars: UTC, with a space where ISO 8601 has ``T``.

    Seen on the real server (2026-11-27, Add-On 1.14.2, PC locale en-MY): the ``T`` form is turned into a
    day/month date on the way to the Add-On and refused with HTTP 400 "Invalid 'from' date format:
    26/11/2026 11:00:00 PM". The space form is accepted.
    """
    return pd.Timestamp(ts).tz_convert("UTC").strftime("%Y-%m-%d %H:%M:%SZ")


def bars_payload(cfg: Config, start, end, *, limit: int = 2000) -> dict[str, Any]:
    """Body of POST /market/bars for 1-minute bars. CrossTrade returns closed bars only."""
    _need(cfg)
    return {"instrument": cfg.instrument, "periodType": "minute", "period": 1,
            "from": _utc(start), "to": _utc(end), "limit": int(limit)}


def parse_bars(payload: dict[str, Any], *, period_min: int = 1, now=None) -> pd.DataFrame:
    """Turn a /market/bars response into the research engine's frame (``ts`` = bar OPEN, oldest first).

    NT8 stamps each bar at its close, so ``ts = time - period``. With ``now`` given, a bar whose close is after
    ``now`` is dropped: the endpoint promises closed bars only, and this keeps that promise if it ever slips.
    """
    rows = payload.get("bars") or []
    frame = pd.DataFrame(
        [(r["time"], r["open"], r["high"], r["low"], r["close"], r.get("volume", 0)) for r in rows],
        columns=list(BAR_COLUMNS),
    )
    if frame.empty:
        return frame.astype({"ts": "datetime64[ns, UTC]", "open": "float64", "high": "float64",
                             "low": "float64", "close": "float64", "volume": "float64"})
    close = pd.to_datetime(frame["ts"], utc=True, format="ISO8601")
    if now is not None:
        keep = close <= pd.Timestamp(now)
        frame, close = frame[keep], close[keep]
    frame["ts"] = close - pd.Timedelta(minutes=period_min)
    for col in ("open", "high", "low", "close", "volume"):
        frame[col] = frame[col].astype("float64")
    return frame.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)


def custom_id(user_data: str | None) -> str | None:
    """Our id, as CrossTrade stores it in the NT8 order's UserData XML (element or attribute form)."""
    m = _CUSTOM_ID.search(user_data or "")
    return m.group(1).strip() if m else None


_MONTHS = ("JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC")
_MONTH_NAMED = re.compile(rf"^(\S+) ({'|'.join(_MONTHS)})(\d\d)$", re.I)


def instrument_name(name: str | None) -> str | None:
    """A futures name in the form the engine is configured with: ``MNQ DEC26`` becomes ``MNQ 12-26``.

    The server accepts ``MNQ 12-26`` in requests but answers with ``MNQ DEC26`` (order lookup and bars, seen
    2026-11-27). Compared as sent, ``LiveEngine.ours`` matched none of our own rows: a resting order was
    invisible, and an open position named that way would have read as flat. Any other name is left alone.
    """
    m = _MONTH_NAMED.match((name or "").strip())
    if not m:
        return name
    return f"{m.group(1).upper()} {_MONTHS.index(m.group(2).upper()) + 1:02d}-{m.group(3)}"


def order_row(raw: dict[str, Any], known: dict[str, str] | None = None) -> dict[str, Any]:
    """An NT8 order in the shape the engine reads: ``id`` (ours where we have one) and ``contractId``.

    ``contractId`` is the NT8 instrument name in the configured form (``instrument_name``), which is what
    ``Config.contract_id`` holds for this broker, so ``LiveEngine.ours`` filters CrossTrade rows with the same
    test it uses for TopstepX.
    """
    nt_id = str(raw.get("id", ""))
    ours = custom_id(raw.get("userData")) or (known or {}).get(nt_id)
    return {**raw, "id": ours or nt_id, "ntId": nt_id, "contractId": instrument_name(raw.get("instrument")),
            "status": raw.get("orderState")}


def position_row(raw: dict[str, Any]) -> dict[str, Any] | None:
    """An NT8 position as the engine reads it, or None when flat (the endpoint keeps flat rows)."""
    qty = int(raw.get("quantity") or 0)
    if qty == 0 or str(raw.get("marketPosition", "")).lower() == "flat":
        return None
    name = instrument_name(raw.get("instrument"))
    return {**raw, "id": name, "contractId": name, "size": qty}


Transport = Callable[[str, str, dict[str, Any] | None], dict[str, Any]]


@dataclass
class CrossTradeBroker:
    """Same surface as ``TopstepXBroker``. ``dry_run=True`` reads bars, orders and positions from CrossTrade but
    records every order instead of sending it (the go-live guide's dry-run step)."""

    cfg: Config
    dry_run: bool = False
    #: Where the watcher reports what it did. main() sets it to the engine's journal.
    journal: Any = None
    poll_s: float = 2.0
    #: Test hook: (method, path_with_query, body) -> parsed JSON. None = real HTTPS.
    transport: Transport | None = None
    sleep: Callable[[float], None] = time.sleep
    sent: list[dict[str, Any]] = field(default_factory=list)
    _dry_cancelled: set[str] = field(default_factory=set)
    _pending: dict[str, dict[str, Any]] = field(default_factory=dict)
    _known: dict[str, str] = field(default_factory=dict)
    _lock: threading.Lock = field(default_factory=threading.Lock)
    _thread: threading.Thread | None = None

    # ---- transport ------------------------------------------------------------------------------------------
    def _acct(self) -> str:
        _need(self.cfg)
        return "/v1/api/accounts/" + urllib.parse.quote(self.cfg.account_name, safe="")

    def _http(self, method: str, path: str, body: dict[str, Any] | None) -> dict[str, Any]:
        for attempt in range(RATE_LIMIT_RETRIES + 1):
            req = urllib.request.Request(
                f"{self.cfg.base_url.rstrip('/')}{path}",
                data=None if body is None else json.dumps(body).encode(),
                headers={"Content-Type": "application/json", "Accept": "application/json",
                         "Authorization": f"Bearer {self.cfg.api_key}"},
                method=method)
            try:
                with urllib.request.urlopen(req, timeout=20) as resp:
                    return json.loads(resp.read().decode() or "{}")
            except urllib.error.HTTPError as exc:
                text = exc.read()[:400]
                if exc.code == 429 and attempt < RATE_LIMIT_RETRIES:
                    self.sleep(float(exc.headers.get("Retry-After") or 2))
                    continue
                # 408 = NT8 closed or the Add-On disconnected (CrossTrade's error table).
                raise BrokerError(f"{method} {path} -> HTTP {exc.code}: {text!r}") from exc
            except urllib.error.URLError as exc:
                raise BrokerError(f"{method} {path} -> {exc.reason}") from exc
        raise BrokerError(f"{method} {path} -> still rate limited after {RATE_LIMIT_RETRIES} retries")

    def _call(self, method: str, path: str, body: dict[str, Any] | None = None) -> dict[str, Any]:
        out = (self.transport or self._http)(method, path, body)
        if not isinstance(out, dict) or out.get("success") is False or "error" in out:
            raise BrokerError(f"{method} {path} -> {out!r}"[:500])
        return out

    def _note(self, event: str, **fields) -> None:
        if self.journal is not None:
            self.journal.write(event, **fields)

    # ---- the TopstepXBroker surface -------------------------------------------------------------------------
    def authenticate(self) -> None:
        """No login exists (the key is the bearer token). Prove the account is visible and connected instead."""
        acct = self.account()
        status = acct.get("connectionStatus")
        if status not in (None, "Connected"):
            raise BrokerError(f"NT8 account {self.cfg.account_name} connection is {status!r}, not Connected")

    def account(self) -> dict[str, Any]:
        return self._call("GET", self._acct())

    def accounts(self) -> list[dict[str, Any]]:
        return self._call("GET", "/v1/api/accounts").get("accounts", [])

    def place(self, order: Order) -> dict[str, Any]:
        oid = new_order_id()
        payload = entry_payload(order, self.cfg, oid)
        bracket = bracket_payload(order, self.cfg)
        if self.dry_run:
            self.sent.append({"entry": payload, "bracket": bracket})
            return {"orderId": oid, "success": True, "dryRun": True, "bracket": bracket}
        try:
            out = self._call("POST", f"{self._acct()}/orders/place", payload)
        except BrokerError as first:
            # Timeout or dropped connection: the order may exist. CrossTrade's advice is to look it up by the id
            # we sent before ever placing again.
            try:
                found = self._call("GET", f"{self._acct()}/orders/{urllib.parse.quote(oid, safe='')}")
            except BrokerError:
                raise first
            out = {"orderId": found.get("id"), "disposition": "found after error", "success": True}
        nt_id = str(out.get("orderId") or "")
        with self._lock:
            if nt_id:
                self._known[nt_id] = oid
            self._pending[oid] = {"order": order, "bracket": bracket, "tries": 0, "read_errors": 0}
        self._note("entry_watch", order_id=oid, nt_order_id=nt_id, bracket=bracket)
        self._ensure_watcher()
        return {"orderId": oid, "ntOrderId": nt_id, "success": True, "disposition": out.get("disposition"),
                "bracket": bracket}

    def cancel(self, order_id) -> dict[str, Any]:
        if self.dry_run:
            self._dry_cancelled.add(str(order_id))
            return {"orderId": str(order_id), "success": True, "dryRun": True}
        # The watcher keeps watching a cancelled entry: if part of it filled first, it still needs its bracket.
        return self._call("POST", f"{self._acct()}/orders/{urllib.parse.quote(str(order_id), safe='')}/cancel", {})

    def open_orders(self) -> list[dict[str, Any]]:
        out = self._call("GET", f"{self._acct()}/orders?activeOnly=true")
        with self._lock:
            known = dict(self._known)
        rows = [order_row(o, known) for o in out.get("orders", [])]
        if self.dry_run:
            # As DryRunBroker does: a recorded entry counts as resting until cancelled, so a dry run follows the day to
            # the entry deadline and its cancel, instead of reading the (untouched) real account as "nothing left to do".
            rows += [{"id": e["entry"]["orderId"], "ntId": None, "contractId": self.cfg.contract_id, "status": "DryRun"}
                     for e in self.sent if "entry" in e and e["entry"]["orderId"] not in self._dry_cancelled]
        return rows

    def open_positions(self) -> list[dict[str, Any]]:
        out = self._call("GET", f"{self._acct()}/positions")
        return [r for r in (position_row(p) for p in out.get("positions", [])) if r is not None]

    def close_position(self) -> dict[str, Any]:
        """Flatten this instrument and sweep its working orders (stop/target leftovers included)."""
        _need(self.cfg)
        body = {"instrument": self.cfg.instrument, "cancelOrders": True}
        if self.dry_run:
            self.sent.append({"flatten": body})
            return {"success": True, "dryRun": True}
        return self._call("POST", f"{self._acct()}/positions/flatten", body)

    def retrieve_bars(self, start, end, *, limit: int = 2000) -> pd.DataFrame:
        out = self._call("POST", "/v1/api/market/bars", bars_payload(self.cfg, start, end, limit=limit))
        bars = parse_bars(out, now=end)
        # The real server does not keep to ``from``: asked on 2026-11-27 for 10 minutes, it sent two sessions.
        # The engine must see only what it asked for (TopstepX does that itself), so cut here, on the bar OPEN.
        return bars[bars["ts"] >= pd.Timestamp(start)].reset_index(drop=True)

    # ---- the fill watcher ------------------------------------------------------------------------------------
    def pending(self) -> list[str]:
        with self._lock:
            return list(self._pending)

    def protect_once(self) -> None:
        """One pass: bracket every watched entry that has any fill; forget ones that ended unfilled."""
        for oid in self.pending():
            with self._lock:
                p = self._pending.get(oid)
            if p is None:
                continue
            try:
                raw = self._call("GET", f"{self._acct()}/orders/{urllib.parse.quote(oid, safe='')}")
            except BrokerError as exc:
                p["read_errors"] += 1
                if p["read_errors"] in (1, 10, 100):
                    self._note("entry_watch_read_failed", order_id=oid, error=str(exc), count=p["read_errors"])
                continue
            p["read_errors"] = 0
            filled = int(raw.get("filled") or 0)
            state = str(raw.get("orderState") or "")
            if filled > 0:
                self._bracket(oid, p, filled, state)
            elif state in DEAD_STATES:
                self._drop(oid)
                self._note("entry_ended_unfilled", order_id=oid, state=state)

    def _bracket(self, oid: str, p: dict[str, Any], filled: int, state: str) -> None:
        try:
            out = self._call("POST", f"{self._acct()}/orders/cancel_and_bracket", p["bracket"])
        except BrokerError as exc:
            p["tries"] += 1
            self._note("protect_failed", order_id=oid, filled=filled, attempt=p["tries"], error=str(exc))
            if p["tries"] < PROTECT_TRIES:
                return
            try:
                flat = self.close_position()
                self._note("protect_gave_up_flattened", order_id=oid, broker=flat)
            except BrokerError as exc2:
                self._note("protect_gave_up_flatten_failed", order_id=oid, error=str(exc2),
                           why="POSITION MAY BE OPEN WITHOUT A STOP -- check NinjaTrader now")
            self._drop(oid)
            return
        self._drop(oid)
        self._note("protected", order_id=oid, filled=filled, entry_state=state,
                   cancelled=out.get("cancelled"), oco_id=out.get("ocoId"), warning=out.get("warning"),
                   stop=p["bracket"]["stopLoss"], target=p["bracket"]["takeProfit"],
                   partial=state != "Filled")

    def _drop(self, oid: str) -> None:
        with self._lock:
            self._pending.pop(oid, None)

    def _ensure_watcher(self) -> None:
        if self.transport is not None:
            return  # tests drive protect_once() themselves
        if self._thread is not None and self._thread.is_alive():
            return
        self._thread = threading.Thread(target=self._watch, name="crosstrade-protect", daemon=True)
        self._thread.start()

    def _watch(self) -> None:
        while self.pending():
            try:
                self.protect_once()
            except Exception as exc:  # noqa: BLE001 - the watcher must never die silently
                self._note("entry_watch_error", error=f"{type(exc).__name__}: {exc}")
            self.sleep(self.poll_s)

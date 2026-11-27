"""CrossTrade connector, checked against response shapes copied from CrossTrade's API reference (2026-11-27 render).

Nothing here has touched a real server: these tests prove the client says what the docs say, not that the docs
are right. The practice round trip (`python -m bridge.live --roundtrip`) is the first real check.
"""
import io
import json
import urllib.error

import pandas as pd
import pytest

from bridge.config import Config
from bridge.crosstrade import (CrossTradeBroker, bracket_levels, bracket_payload, custom_id, entry_payload,
                               order_row, parse_bars)
from bridge.journal import Journal
from bridge.live import LiveEngine, make_broker
from bridge.roundtrip import PROOF_PATH, proof_holds, proof_path, prove
from bridge.topstepx import BrokerError, DryRunBroker, Order, order_payload


def _cfg(**kw):
    base = dict(username="", api_key="k", base_url="https://app.crosstrade.io", account_id=None,
                contract_id="MNQ 12-26", tick_size=0.25, point_value=2.0, webhook_secret="", live=True,
                live_data=False, cutoff_minute=930, flat_minute=960, max_bar_age_s=150.0, preset="LucidFlex 50K",
                account_start=50000.0, profit_target=3000.0, max_loss_limit=2000.0, daily_loss_limit=1200.0,
                max_contracts=40, safety_mult=1.5, use_guard=False, scaling_plan=False, consistency=0.4,
                broker="crosstrade", account_name="LUCID FLEX 1", instrument="MNQ 12-26")
    base.update(kw)
    return Config(**base)


class Fake:
    """Records every call; answers from a queue per (method, path) or a default."""

    def __init__(self):
        self.calls = []
        self.answers = {}

    def on(self, method, path, *answers):
        self.answers.setdefault((method, path), []).extend(answers)

    def __call__(self, method, path, body):
        self.calls.append((method, path, body))
        queue = self.answers.get((method, path), [])
        ans = queue.pop(0) if len(queue) > 1 else (queue[0] if queue else {"success": True})
        if isinstance(ans, Exception):
            raise ans
        return ans


ACCT = "/v1/api/accounts/LUCID%20FLEX%201"


def _broker(fake, journal=None, **kw):
    return CrossTradeBroker(_cfg(**kw), transport=fake, journal=journal or Journal(None), sleep=lambda s: None)


def test_entry_is_a_day_limit_on_the_tick_grid_with_our_own_id():
    o = Order(side="buy", size=3, entry=1930.375, stop=1920.1, target=1940.6)
    p = entry_payload(o, _cfg(), "lc-1")
    assert p == {"instrument": "MNQ 12-26", "action": "BUY", "quantity": 3, "orderType": "LIMIT",
                 "timeInForce": "DAY", "limitPrice": 1930.25, "orderId": "lc-1"}


def test_bracket_prices_match_the_topstepx_tick_distances():
    cfg = _cfg()
    for side, entry, stop, target in (("buy", 1930.375, 1920.1, 1940.6), ("sell", 18000.1, 18012.3, 17990.0)):
        o = Order(side=side, size=2, entry=entry, stop=stop, target=target)
        e, s, t = bracket_levels(o, cfg)
        tx = order_payload(o, _cfg(broker="topstepx", account_id=7, contract_id="CON.F.US.MNQ.Z26"))
        assert round(abs(e - s) / 0.25) == tx["stopLossBracket"]["ticks"]
        assert round(abs(t - e) / 0.25) == tx["takeProfitBracket"]["ticks"]
        assert e == tx["limitPrice"]
        b = bracket_payload(o, cfg)
        assert (b["stopLoss"], b["takeProfit"], b["quantity"]) == (s, t, 2)
        assert b["action"] == ("Buy" if side == "buy" else "Sell")      # side of the POSITION, per the docs
        assert (s < e < t) if side == "buy" else (t < e < s)


def test_nt8_bars_are_moved_from_their_close_to_their_open_and_unclosed_bars_dropped():
    payload = {"bars": [
        {"time": "2026-03-18T14:32:00.0000000Z", "epoch": 0, "open": 2, "high": 3, "low": 1, "close": 2.5, "volume": 4},
        {"time": "2026-03-18T14:31:00.0000000Z", "epoch": 0, "open": 1, "high": 2, "low": 0.5, "close": 2, "volume": 9},
        {"time": "2026-03-18T14:33:00.0000000Z", "epoch": 0, "open": 9, "high": 9, "low": 9, "close": 9, "volume": 1},
    ], "success": True}
    f = parse_bars(payload, now=pd.Timestamp("2026-03-18 14:32:30", tz="UTC"))
    assert list(f["ts"].dt.strftime("%H:%M")) == ["14:30", "14:31"]          # opens, oldest first
    assert list(f["close"]) == [2.0, 2.5]


def test_bar_request_and_window_match_what_the_real_server_does():
    """2026-11-27: the 'T' date form was refused, and bars from before ``from`` came back."""
    fake = Fake()
    fake.on("POST", "/v1/api/market/bars", {"success": True, "timestampConvention": "bar_close", "bars": [
        {"time": f"2026-11-27T{t}:00.0000000Z", "open": 1, "high": 1, "low": 1, "close": 1, "volume": 1}
        for t in ("01:59", "02:00", "02:01", "02:02", "02:03")]})
    start, end = pd.Timestamp("2026-11-27 02:00", tz="UTC"), pd.Timestamp("2026-11-27 02:02:30", tz="UTC")
    bars = _broker(fake).retrieve_bars(start, end)
    body = fake.calls[0][2]
    assert (body["from"], body["to"]) == ("2026-11-27 02:00:00Z", "2026-11-27 02:02:30Z")
    assert list(bars["ts"].dt.strftime("%H:%M")) == ["02:00", "02:01"]     # not before start, nothing unclosed


def test_month_named_instruments_from_the_server_count_as_ours():
    """2026-11-27, real server: asked with 'MNQ 12-26', orders came back as 'MNQ DEC26' and were filtered out."""
    fake = Fake()
    fake.on("GET", f"{ACCT}/orders?activeOnly=true", {"success": True, "orders": [
        {"id": "nt9", "instrument": "MNQ DEC26", "orderState": "Working",
         "userData": "<NinjaTrader>\r\n  <AutomatedTradingOrderId>lc-abc</AutomatedTradingOrderId>\r\n</NinjaTrader>"}]})
    fake.on("GET", f"{ACCT}/positions", {"success": True, "positions": [
        {"instrument": "MNQ DEC26", "marketPosition": "Long", "quantity": 2},
        {"instrument": "MES MAR27", "marketPosition": "Long", "quantity": 1}]})
    b = _broker(fake)
    [order] = b.open_orders()
    assert (order["id"], order["contractId"]) == ("lc-abc", "MNQ 12-26")
    assert [p["contractId"] for p in b.open_positions()] == ["MNQ 12-26", "MES 03-27"]


def test_place_sends_the_documented_request_and_watches_the_entry():
    fake = Fake()
    fake.on("POST", f"{ACCT}/orders/place", {"orderId": "cb1fc8d4", "effectiveAction": "Buy",
                                             "effectiveQuantity": 3, "disposition": "submitted", "success": True})
    b = _broker(fake)
    out = b.place(Order(side="buy", size=3, entry=100.0, stop=95.0, target=105.0))
    method, path, body = fake.calls[0]
    assert (method, path) == ("POST", f"{ACCT}/orders/place")       # account name URL-encoded
    assert out["orderId"] == body["orderId"] and out["orderId"].startswith("lc-")
    assert out["ntOrderId"] == "cb1fc8d4"
    assert b.pending() == [out["orderId"]]


def _placed(fake, journal=None, size=3):
    fake.on("POST", f"{ACCT}/orders/place", {"orderId": "nt1", "disposition": "submitted", "success": True})
    b = _broker(fake, journal)
    oid = b.place(Order(side="sell", size=size, entry=100.0, stop=105.0, target=95.0))["orderId"]
    return b, oid


def test_first_fill_gets_the_bracket_and_the_watch_ends(tmp_path):
    fake, j = Fake(), Journal(tmp_path / "j.jsonl")
    b, oid = _placed(fake, j)
    fake.on("GET", f"{ACCT}/orders/{oid}",
            {"id": "nt1", "orderState": "Working", "filled": 0, "success": True},
            {"id": "nt1", "orderState": "PartFilled", "filled": 1, "success": True})
    fake.on("POST", f"{ACCT}/orders/cancel_and_bracket", {"success": True, "cancelled": 1, "placed": [{}, {}],
                                                          "ocoId": "a1"})
    b.protect_once()
    assert not any("cancel_and_bracket" in c[1] for c in fake.calls)    # working, nothing filled: wait
    b.protect_once()
    sent = [c for c in fake.calls if c[1].endswith("cancel_and_bracket")]
    assert sent[0][2] == {"instrument": "MNQ 12-26", "action": "Sell", "quantity": 3, "takeProfit": 95.0,
                          "stopLoss": 105.0}
    assert b.pending() == []
    row = [r for r in j.read() if r["event"] == "protected"][0]
    assert row["partial"] is True and row["oco_id"] == "a1"


def test_a_cancelled_entry_that_partly_filled_still_gets_its_bracket():
    fake = Fake()
    b, oid = _placed(fake)
    fake.on("GET", f"{ACCT}/orders/{oid}", {"id": "nt1", "orderState": "Cancelled", "filled": 2, "success": True})
    b.protect_once()
    assert any(c[1].endswith("cancel_and_bracket") for c in fake.calls)


def test_an_entry_that_ends_unfilled_is_forgotten_without_a_bracket():
    fake = Fake()
    b, oid = _placed(fake)
    fake.on("GET", f"{ACCT}/orders/{oid}", {"id": "nt1", "orderState": "Cancelled", "filled": 0, "success": True})
    b.protect_once()
    assert b.pending() == [] and not any("bracket" in c[1] for c in fake.calls)


def test_if_the_bracket_cannot_be_placed_the_position_is_flattened(tmp_path):
    fake, j = Fake(), Journal(tmp_path / "j.jsonl")
    b, oid = _placed(fake, j)
    fake.on("GET", f"{ACCT}/orders/{oid}", {"id": "nt1", "orderState": "Filled", "filled": 3, "success": True})
    fake.on("POST", f"{ACCT}/orders/cancel_and_bracket", BrokerError("HTTP 500"))
    for _ in range(3):
        b.protect_once()
    flat = [c for c in fake.calls if c[1].endswith("/positions/flatten")]
    assert flat and flat[0][2] == {"instrument": "MNQ 12-26", "cancelOrders": True}
    assert b.pending() == []
    assert [r["event"] for r in j.read()].count("protect_failed") == 3
    assert any(r["event"] == "protect_gave_up_flattened" for r in j.read())


def test_listed_orders_carry_our_id_and_the_instrument_as_contract_id():
    assert custom_id("<NinjaTrader><AutomatedTradingOrderId>lc-abc</AutomatedTradingOrderId></NinjaTrader>") == "lc-abc"
    assert custom_id('<NinjaTrader AutomatedTradingOrderId="lc-xyz" />') == "lc-xyz"
    assert custom_id("<NinjaTrader />") is None
    raw = {"id": "3cac", "instrument": "MNQ 12-26", "orderState": "Working", "userData": "<NinjaTrader />"}
    assert order_row(raw)["id"] == "3cac"
    assert order_row(raw, {"3cac": "lc-1"})["id"] == "lc-1"              # id remembered from the place answer
    assert order_row(raw)["contractId"] == "MNQ 12-26"


def test_flat_rows_are_not_positions():
    fake = Fake()
    fake.on("GET", f"{ACCT}/positions", {"positions": [
        {"instrument": "MNQ 12-26", "marketPosition": "Flat", "quantity": 0},
        {"instrument": "MES 12-26", "marketPosition": "Long", "quantity": 2, "unrealizedProfitLoss": 5.0}],
        "success": True})
    rows = _broker(fake).open_positions()
    assert [(r["contractId"], r["size"]) for r in rows] == [("MES 12-26", 2)]


def test_a_place_that_errors_is_looked_up_by_our_id_before_anything_else():
    fake = Fake()
    fake.on("POST", f"{ACCT}/orders/place", BrokerError("timed out"))
    b = _broker(fake)

    def answer(method, path, body):
        fake.calls.append((method, path, body))
        if method == "POST":
            raise BrokerError("timed out")
        return {"id": "nt9", "orderState": "Working", "success": True}
    b.transport = answer
    out = b.place(Order(side="buy", size=1, entry=100.0, stop=99.0, target=101.0))
    assert fake.calls[1][1] == f"{ACCT}/orders/{out['orderId']}" and out["ntOrderId"] == "nt9"

    def nothing(method, path, body):
        raise BrokerError("timed out" if method == "POST" else "HTTP 400 not found")
    b.transport = nothing
    with pytest.raises(BrokerError, match="timed out"):
        b.place(Order(side="buy", size=1, entry=100.0, stop=99.0, target=101.0))


def test_dry_run_records_and_never_sends_an_order():
    fake = Fake()
    b = CrossTradeBroker(_cfg(), dry_run=True, transport=fake)
    out = b.place(Order(side="buy", size=2, entry=100.0, stop=95.0, target=105.0))
    b.cancel(out["orderId"])
    b.close_position()
    assert fake.calls == [] and out["dryRun"] and b.pending() == []
    assert b.sent[0]["entry"]["limitPrice"] == 100.0 and b.sent[0]["bracket"]["stopLoss"] == 95.0


def test_a_429_waits_retry_after_then_retries(monkeypatch):
    waits, seen = [], []

    class Resp(io.BytesIO):
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    def urlopen(req, timeout):
        seen.append(req)
        if len(seen) == 1:
            raise urllib.error.HTTPError(req.full_url, 429, "Too Many", {"Retry-After": "2"},
                                         io.BytesIO(b'{"error": "Rate limit exceeded", "retryAfter": 2}'))
        return Resp(json.dumps({"accounts": [{"id": 2, "name": "LUCID FLEX 1", "status": "Enabled"}],
                                "success": True}).encode())
    monkeypatch.setattr("urllib.request.urlopen", urlopen)
    b = CrossTradeBroker(_cfg(), sleep=waits.append)
    assert b.accounts()[0]["name"] == "LUCID FLEX 1"
    assert waits == [2.0] and len(seen) == 2
    assert seen[0].get_header("Authorization") == "Bearer k"
    assert seen[0].full_url == "https://app.crosstrade.io/v1/api/accounts"


def test_broker_choice_and_one_proof_file_per_engine():
    assert isinstance(make_broker(_cfg(), live=True), CrossTradeBroker)
    assert make_broker(_cfg(), live=False).dry_run is True
    tx = _cfg(broker="topstepx", account_id=7, account_name=None, instrument=None, contract_id="CON.F.US.MNQ.Z26")
    assert isinstance(make_broker(tx, live=False), DryRunBroker)
    assert proof_path(tx) == PROOF_PATH                                     # the original engine is unchanged
    a, b = proof_path(_cfg()), proof_path(_cfg(account_name="DT150-1"))
    assert a != b and a != PROOF_PATH


def test_round_trip_proves_the_crosstrade_order_book(tmp_path):
    fake = Fake()
    fake.on("POST", "/v1/api/market/bars", {"bars": [{"time": "2026-11-27T15:00:00Z", "open": 21000, "high": 21001,
                                                      "low": 20999, "close": 21000, "volume": 5}], "success": True})
    fake.on("POST", f"{ACCT}/orders/place", {"orderId": "ntP", "disposition": "submitted", "success": True})
    b = _broker(fake)
    listed = {"orders": [{"id": "ntP", "instrument": "MNQ 12-26", "orderState": "Working",
                          "userData": "<NinjaTrader />"}], "success": True}
    fake.on("GET", f"{ACCT}/orders?activeOnly=true", listed, {"orders": [], "success": True})
    path = tmp_path / "proof.json"
    assert prove(_cfg(), b, Journal(None), path=path, sleep=lambda s: None,
                 now=lambda: pd.Timestamp("2026-11-27 15:05", tz="UTC"))
    cancel = [c for c in fake.calls if c[1].endswith("/cancel")][0]
    assert cancel[1].startswith(f"{ACCT}/orders/lc-")                       # cancelled by our own id
    assert proof_holds(_cfg(), path) and not proof_holds(_cfg(account_name="OTHER"), path)


def test_cutoff_cancels_a_resting_crosstrade_entry_by_its_string_id():
    fake = Fake()
    b = _broker(fake)
    fake.on("GET", f"{ACCT}/orders?activeOnly=true",
            {"orders": [{"id": "ntE", "instrument": "MNQ 12-26", "orderState": "Working",
                         "userData": "<NinjaTrader><AutomatedTradingOrderId>lc-e</AutomatedTradingOrderId></NinjaTrader>"}],
             "success": True})
    eng = LiveEngine(cfg=_cfg(), broker=b, journal=Journal(None), risk_usd=900.0)
    eng.outstanding = {"k1": "lc-e", "k2": "lc-gone"}
    eng.close_out(pd.Timestamp("2026-11-27 20:30", tz="UTC"))
    cancels = [c[1] for c in fake.calls if c[1].endswith("/cancel")]
    assert cancels == [f"{ACCT}/orders/lc-e/cancel"]                        # the filled one is not cancelled
    assert eng.outstanding == {}


def test_newest_bar_line_names_the_nt8_label_to_compare():
    """The connected check prints the newest bar so a person can find the same bar on the NT8 chart.

    Response shape from the docs (7-digit fractional seconds, Z). NT8 stamps 14:31 UTC -> bar opened 14:30 UTC,
    i.e. 09:30-09:31 New York and 22:30-22:31 Malaysia; the NT8 chart labels it 22:31.
    """
    from bridge.preflight import newest_bar_line
    bars = parse_bars({"bars": [{"time": "2026-12-01T14:31:00.0000000Z", "epoch": 0, "open": 21000.25,
                                 "high": 21010.5, "low": 20990.0, "close": 21005.75, "volume": 812}]})
    line = newest_bar_line(bars, "crosstrade", local_tz="Asia/Kuala_Lumpur")
    assert "22:30-22:31 PC time (09:30-09:31 New York)" in line
    assert "O 21000.25 H 21010.5 L 20990 C 21005.75 V 812" in line
    assert line.endswith("find the bar labelled 22:31 (NT8 labels a bar by its close)")
    assert "NT8" not in newest_bar_line(bars, "topstepx", local_tz="Asia/Kuala_Lumpur")


class SimNT8:
    """A tiny stateful stand-in for NT8 behind CrossTrade: the entry fills at once, cancel_and_bracket rests a stop and
    a target, flatten clears everything. Instrument names come back month-named, as the real server does."""

    def __init__(self, bracket_ok=True):
        self.calls, self.orders, self.position, self.bracket_ok = [], [], 0, bracket_ok

    def __call__(self, method, path, body):
        self.calls.append((method, path, body))
        if path == "/v1/api/market/bars":
            return {"bars": [{"time": "2026-11-27T15:00:00Z", "open": 21000, "high": 21001, "low": 20999,
                              "close": 21000, "volume": 5}], "success": True}
        if path.endswith("/orders/place"):
            self.position += body["quantity"]
            self.entry = body
            return {"orderId": "ntE", "disposition": "submitted", "success": True}
        if "/orders/lc-" in path and method == "GET":
            return {"id": "ntE", "orderState": "Filled", "filled": self.entry["quantity"], "success": True}
        if path.endswith("/cancel_and_bracket"):
            if not self.bracket_ok:
                raise BrokerError("HTTP 500")
            self.orders = [{"id": "s1", "instrument": "MNQ DEC26", "orderType": "StopMarket", "orderAction": "Sell",
                            "stopPrice": body["stopLoss"], "limitPrice": 0.0, "ocoId": "o1", "userData": ""},
                           {"id": "t1", "instrument": "MNQ DEC26", "orderType": "Limit", "orderAction": "Sell",
                            "stopPrice": 0.0, "limitPrice": body["takeProfit"], "ocoId": "o1", "userData": ""}]
            return {"success": True, "cancelled": 0, "placed": self.orders, "ocoId": "o1"}
        if path.endswith("/orders?activeOnly=true"):
            return {"orders": list(self.orders), "success": True}
        if path.endswith("/positions"):
            pos = [{"instrument": "MNQ DEC26", "marketPosition": "Long", "quantity": self.position}] if self.position else []
            return {"positions": pos, "success": True}
        if path.endswith("/positions/flatten"):
            self.orders, self.position = [], 0
            return {"success": True}
        return {"success": True}


def test_bracket_probe_proves_a_filled_entry_gets_its_stop_and_target_then_flattens(tmp_path):
    from bridge.roundtrip import bracket_probe
    sim, j = SimNT8(), Journal(tmp_path / "j.jsonl")
    cfg = _cfg(account_name="Sim101")
    b = CrossTradeBroker(cfg, transport=sim, journal=j, sleep=lambda s: None)
    assert bracket_probe(cfg, b, j, sleep=lambda s: None, drive=b.protect_once,
                         now=lambda: pd.Timestamp("2026-11-27 15:05", tz="UTC"))
    entry = sim.entry
    assert entry["action"] == "BUY" and entry["limitPrice"] == 21010.0 and entry["quantity"] == 1   # fills at once
    ev = [r["event"] for r in j.read()]
    assert "bracket_probe_protected" in ev and "bracket_probe_ok" in ev
    prot = [r for r in j.read() if r["event"] == "bracket_probe_protected"][0]
    assert (prot["stop"], prot["target"]) == (20970.0, 21050.0)
    assert sim.position == 0 and sim.orders == []


def test_bracket_probe_fails_and_still_flattens_when_no_bracket_appears(tmp_path):
    from bridge.roundtrip import bracket_probe
    sim, j = SimNT8(bracket_ok=False), Journal(tmp_path / "j.jsonl")
    cfg = _cfg(account_name="Sim101")
    b = CrossTradeBroker(cfg, transport=sim, journal=j, sleep=lambda s: None)
    assert not bracket_probe(cfg, b, j, sleep=lambda s: None, drive=b.protect_once,
                             now=lambda: pd.Timestamp("2026-11-27 15:05", tz="UTC"))
    assert sim.position == 0
    assert any(r["event"] == "bracket_probe_failed" and r["step"] == "protect" for r in j.read())


def test_bracket_probe_refuses_anything_but_a_sim_account(tmp_path):
    from bridge.roundtrip import bracket_probe
    sim, j = SimNT8(), Journal(tmp_path / "j.jsonl")
    cfg = _cfg(account_name="LUCID FLEX 1")
    assert not bracket_probe(cfg, CrossTradeBroker(cfg, transport=sim), j, sleep=lambda s: None)
    assert sim.calls == [] and j.read()[0]["event"] == "bracket_probe_refused"


class ShortSimNT8(SimNT8):
    """Short side; after ``hit_after`` position checks the stop or target fills: position gone, OCO partner cancelled."""

    def __init__(self, hit_after=3, **kw):
        super().__init__(**kw)
        self.hit_after, self.checks = hit_after, 0

    def __call__(self, method, path, body):
        if path.endswith("/positions") and self.position and self.orders:
            self.checks += 1
            if self.checks >= self.hit_after:
                self.position, self.orders = 0, []
        out = super().__call__(method, path, body)
        if path.endswith("/orders/place"):
            assert body["action"] == "SELL"
        if path.endswith("/positions") and self.position:
            out["positions"][0]["marketPosition"] = "Short"
        return out


def test_exit_probe_sees_a_short_close_by_itself_through_its_bracket(tmp_path):
    from bridge.roundtrip import exit_probe
    sim, j = ShortSimNT8(), Journal(tmp_path / "j.jsonl")
    cfg = _cfg(account_name="Sim101")
    b = CrossTradeBroker(cfg, transport=sim, journal=j, sleep=lambda s: None)
    assert exit_probe(cfg, b, j, sleep=lambda s: None, drive=b.protect_once,
                      now=lambda: pd.Timestamp("2026-11-27 15:05", tz="UTC"))
    assert sim.entry["limitPrice"] == 20990.0
    br = [c[2] for c in sim.calls if c[1].endswith("cancel_and_bracket")][0]
    assert (br["action"], br["stopLoss"], br["takeProfit"]) == ("Sell", 20993.0, 20987.0)
    assert not any(c[1].endswith("/positions/flatten") for c in sim.calls)        # closed by its own bracket
    assert [r["event"] for r in j.read()][-1] == "exit_probe_ok"


def test_exit_probe_flattens_and_fails_when_nothing_is_hit(tmp_path):
    from bridge.roundtrip import exit_probe
    sim, j = ShortSimNT8(hit_after=10**9), Journal(tmp_path / "j.jsonl")
    cfg = _cfg(account_name="Sim101")
    b = CrossTradeBroker(cfg, transport=sim, journal=j, sleep=lambda s: None)
    assert not exit_probe(cfg, b, j, sleep=lambda s: None, drive=b.protect_once, wait_s=5.0,
                          now=lambda: pd.Timestamp("2026-11-27 15:05", tz="UTC"))
    assert sim.position == 0 and any(c[1].endswith("/positions/flatten") for c in sim.calls)


def test_exit_probe_refuses_anything_but_a_sim_account(tmp_path):
    from bridge.roundtrip import exit_probe
    sim, j = ShortSimNT8(), Journal(tmp_path / "j.jsonl")
    cfg = _cfg(account_name="LUCID FLEX 1")
    assert not exit_probe(cfg, CrossTradeBroker(cfg, transport=sim), j, sleep=lambda s: None)
    assert sim.calls == []


def test_dry_run_keeps_a_recorded_entry_resting_until_the_deadline_cancels_it():
    fake = Fake()
    fake.on("GET", f"{ACCT}/orders?activeOnly=true", {"orders": [], "success": True})
    b = CrossTradeBroker(_cfg(), dry_run=True, transport=fake)
    oid = b.place(Order(side="sell", size=6, entry=26553.875, stop=26619.0, target=26488.75))["orderId"]
    eng = LiveEngine(cfg=_cfg(), broker=b, journal=Journal(None), risk_usd=900.0)
    assert [r["id"] for r in eng.ours(b.open_orders())] == [oid]          # the day is not "done" while it rests
    eng.outstanding = {"k": oid}
    eng.close_out(pd.Timestamp("2026-11-27 20:30", tz="UTC"))
    assert b.open_orders() == [] and eng.outstanding == {}
    assert not any(c[0] == "POST" for c in fake.calls)                      # still nothing sent

"""Unit tests for scripts/liq_shadow.py (ABI helpers, simulation math) and liq_shadow_summary.py (matching rules)."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import liq_shadow as ls  # noqa: E402
import liq_shadow_summary as sm  # noqa: E402

A = "0x" + "aa" * 20
B = "0x" + "bb" * 20
USER = "0x" + "cc" * 20


def test_aggregate3_roundtrip():
    calls = [(A, "0x1234"), (B, "0x" + "ab" * 40)]
    enc = ls.encode_aggregate3(calls)
    assert enc.startswith(ls.SEL["aggregate3"])
    body = enc[10:]
    ws = [int(body[i:i + 64], 16) for i in range(0, len(body), 64)]
    assert ws[0] == 0x20 and ws[1] == 2          # offset, length
    assert ws[4] == int(A, 16) and ws[5] == 1     # first tuple: target, allowFailure
    # decode a fake Result[] (success, bytes)
    def tup(ok, data):
        b = data[2:]
        blen = len(b) // 2
        pad = (-blen) % 32
        return ls.w(ok) + ls.w(0x40) + ls.w(blen) + b + "00" * pad
    t1, t2 = tup(1, "0x" + "11" * 32), tup(0, "0x")
    off1 = 2 * 32
    off2 = off1 + len(t1) // 2
    ret = "0x" + ls.w(0x20) + ls.w(2) + ls.w(off1) + ls.w(off2) + t1 + t2
    out = ls.decode_aggregate3(ret)
    assert out == [(True, "0x" + "11" * 32), (False, "0x")]


def test_tier_interval():
    assert ls.tier_interval(1.01) == 0 and ls.tier_interval(1.1) == 10 and ls.tier_interval(1.3) == 60 and ls.tier_interval(2.0) == 300


class FakeRpc:
    def __init__(self):
        self.stats = {}

    def multicall(self, calls):
        # getUserReserveData for 2 reserves: A = collateral 10 units (18 dec), B = debt 10000 units (6 dec)
        out = []
        for target, data in calls:
            asset = "0x" + data[34:74]
            if asset == A:
                ww = [10 * 10**18, 0, 0, 0, 0, 0, 0, 0, 1]
            else:
                ww = [0, 0, 10_000 * 10**6, 0, 0, 0, 0, 0, 0]
            out.append((True, "0x" + "".join(ls.w(x) for x in ww)))
        return out

    def head(self):
        return 123


def make_chain():
    c = ls.Chain.__new__(ls.Chain)
    c.name, c.c, c.stats = "base", ls.CFG["base"], {}
    c.rpc = FakeRpc()
    c.meta = dict(dp="0x" + "dd" * 20, oracle="0x" + "ee" * 20, premium=0.0005, assets=[A, B], dec={A: 18, B: 6},
                  cfg={A: dict(bonus=1.05, lt=8000, coll=True, active=True), B: dict(bonus=1.05, lt=8000, coll=False, active=True)})
    c.prices = lambda assets: {A: 2000.0, B: 1.0}
    return c


def test_simulate_math():
    c = make_chain()
    c.quote_route = lambda tin, tout, amt: (int(amt / 10**18 * 2000 * 0.998 * 10**6), "500")   # 0.2% slippage+fee
    sim = c.simulate(USER, 0.97)           # HF >= 0.95: close factor 50%
    assert sim["ok"]
    assert abs(sim["debt_usd"] - 5000) < 1e-6
    assert abs(sim["seized_usd"] - 5250) < 1e-6
    assert abs(sim["premium_usd"] - 2.5) < 1e-6
    # proceeds = 5250 * 0.998 = 5239.5 ; net = 5239.5 - 5000 - 2.5 = 237
    assert abs(sim["net_before_gas_usd"] - 237.0) < 0.01
    sim2 = c.simulate(USER, 0.9)           # HF < 0.95: close factor 100% but capped by collateral value ($20,000): debt 10000 -> seized 10500
    assert abs(sim2["debt_usd"] - 10_000) < 1e-6
    c.quote_route = lambda *a: None
    assert c.simulate(USER, 0.97)["reason"] == "no_quote"


def mk_dir(tmp_path, chains_events):
    for c in sm.CHAINS:
        d = tmp_path / c
        d.mkdir()
        up = [dict(kind="start", wall=1000.0, block=1, ver=2)] + [dict(kind="hb", wall=1000.0 + 30 * i, block=1, ver=2) for i in range(1, 2000)]
        (d / "uptime.jsonl").write_text("\n".join(json.dumps(x) for x in up))
        (d / "borrowers.json").write_text(json.dumps([USER]))
        liq = [e for e in chains_events.get(c, {}).get("liq", [])]
        unh = [e for e in chains_events.get(c, {}).get("unh", [])]
        (d / "liquidations.jsonl").write_text("\n".join(json.dumps(x) for x in liq))
        (d / "unhealthy.jsonl").write_text("\n".join(json.dumps(x) for x in unh))


def test_matching(tmp_path):
    def ev(block, user, bonus=100.0, gas=1.0, ts=5000.0):
        return dict(block=block, tx=f"tx{block}", user=user, bonus_usd=bonus, gas_usd=gas, ts=ts, seen_wall=ts + 2)
    rec = dict(ver=2, user=USER, wall=4990.0, n_ready=100, sim=dict(ok=True, net_before_gas_usd=20.0))
    late = dict(ver=2, user="0x" + "dd" * 20, wall=4999.0, n_ready=199, sim=dict(ok=True, net_before_gas_usd=20.0))
    neg = dict(ver=2, user="0x" + "ee" * 20, wall=4990.0, n_ready=100, sim=dict(ok=True, net_before_gas_usd=0.5))
    events = {"base": dict(unh=[rec, late, neg], liq=[
        ev(110, USER),                       # fire first: net 19 > 0 and 100+1 < 110
        ev(200, "0x" + "dd" * 20),           # record too late (199 + 1 >= 200)
        ev(120, "0x" + "ee" * 20),           # sim net 0.5 - 1 < 0
        ev(130, "0x" + "ff" * 20),           # no record, user not in tracked set
        ev(140, USER, bonus=10.0),           # below $50: not eligible
    ])}
    mk_dir(tmp_path, events)
    data = sm.load(tmp_path)
    start_ts, evs = sm.evaluate(data)
    assert start_ts == 1000.0
    cls = sorted(e["cls"] for e in evs)
    assert cls == ["fire_first", "no_record_not_in_set", "record_too_late", "sim_net_le0"]
    ff = [e for e in evs if e["cls"] == "fire_first"][0]
    assert abs(ff["net"] - 19.0) < 1e-9


def test_local_hf():
    # collateral 10 units of asset 0 at $2000, LT 0.8, income grew 1%; debt 10,000 USD stable-ish asset 1: scaled 9,900 x index 1.01
    pos = dict(c=[(0, 10.0, 1.00, 0.8)], d=[(1, 9900.0, 0.0)], t=0)
    mk = ([2000.0, 1.0], [1.01, 1.0], [1.0, 1.01])
    hf = ls.Chain.local_hf(pos, mk)
    assert abs(hf - (10 * 1.01 * 2000 * 0.8) / (9900 * 1.01)) < 1e-9
    mk2 = ([1200.0, 1.0], [1.01, 1.0], [1.0, 1.01])
    assert ls.Chain.local_hf(pos, mk2) < 1.0 < hf
    assert ls.Chain.local_hf(dict(c=[(0, 1.0, 1.0, 0.8)], d=[], t=0), mk) == 99.0


def test_local_hf_calibration_factor():
    pos = dict(c=[(0, 10.0, 1.00, 0.8)], d=[(1, 9900.0, 0.0)], t=0, k=1.5)
    mk = ([2000.0, 1.0], [1.0, 1.0], [1.0, 1.0])
    assert abs(ls.Chain.local_hf(pos, mk) - 1.5 * (10 * 2000 * 0.8) / 9900) < 1e-9


# ---- addendum 4: near-the-line buckets, stress flag, alert dedupe, crash window
import liq_alert as al  # noqa: E402
import liq_crash_window as cw  # noqa: E402


def test_hf_buckets_sums():
    items = [(1.001, 100.0), (1.019, 50.0), (1.02, 10.0), (1.049, 5.0), (1.05, 1.0), (1.099, 2.0), (1.10, 999.0), (0.99, 777.0)]
    b = ls.hf_buckets(items)
    assert b["1.00-1.02"] == {"users": 2, "debt_usd": 150.0}
    assert b["1.02-1.05"] == {"users": 2, "debt_usd": 15.0}
    assert b["1.05-1.10"] == {"users": 2, "debt_usd": 3.0}      # 1.10 and below 1.00 are outside every bucket


def test_stress_flag():
    assert ls.stress_flag(10, [2000.0, 2001.0])[0] is True                 # count rule
    assert ls.stress_flag(9, [2000.0, 2001.0])[0] is False
    flag, move = ls.stress_flag(0, [2000.0, 2100.0, 2050.0])              # 5% range within the hour
    assert flag and abs(move - 5.0) < 1e-9
    assert ls.stress_flag(0, [2000.0, 2099.0])[0] is False
    assert ls.stress_flag(0, [])[0] is False


def test_alert_decide_dedupe():
    status = {"arbitrum": 5.0, "base": 90.0, "polygon": 200.0, "optimism": None}
    # base has an open issue already: no duplicate; polygon needs one; arbitrum is fine; optimism has no data: silent
    acts = al.decide(status, {"liq watcher down: base"})
    assert acts == [("create", "liq watcher down: polygon")]
    # recovery closes the open issue
    assert al.decide({"base": 3.0}, {"liq watcher down: base"}) == [("close", "liq watcher down: base")]
    # exactly at threshold is not down
    assert al.decide({"base": 60.0}, set()) == []


def test_crash_window_detection():
    d0 = 1_800_000_000 - 1_800_000_000 % 86400
    ev = [(d0 + 3 * 86400 + 100, 400_000.0), (d0 + 10 * 86400, 700_000.0), (d0 + 80 * 86400, 5_000_000.0)]
    now = d0 + 100 * 86400
    start, end, state = cw.find_window(ev, d0, now)
    assert start == d0 and end == d0 + 30 * 86400 and state == "complete"      # first start day whose 30d sum > 1M
    # no window when the sum stays under the line
    assert cw.find_window([(d0 + 86400, 900_000.0)], d0, now)[2] == "none"
    # window still open when `now` is inside it
    s, e, st = cw.find_window([(d0 + 86400, 600_000.0), (d0 + 2 * 86400, 600_000.0)], d0, d0 + 5 * 86400)
    assert st == "open" and s == d0

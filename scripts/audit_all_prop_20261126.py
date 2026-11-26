"""Every Malaysia-eligible prop product that qualified before, re-priced on the corrected model (loss limit on open P&L in real
time), with the same qualification rule: real >= 50% of Topstep, coin-flip median >= $5,000, worst dip no worse than 1.5x Topstep's
(Topstep = Topstep 50K Standard path on the same model and the same entry delay). docs/AUDIT_PRE_LIVE_20261126.md addendum 1.

    uv run python -m scripts.audit_all_prop_20261126 | tee docs/jx_runs/audit_all_prop_20261126.txt
"""
import contextlib
import dataclasses as dc
import io

import numpy as np
import pandas as pd

from backtest.recycle import Policy, recycle
from ict import data as D
from scripts.firms2_20261120 import TRADEDAY, worst_dip
from scripts.radar_price import flip, trades

with contextlib.redirect_stdout(io.StringIO()):
    from scripts.manual_my_20261123 import topone, m

R = dc.replace
bars = D.load("1m")
orders = pd.read_parquet(D.PROCESSED_DIR / "ideas_orders_NQ.parquet")
ts, _ = m("topstep50"); ttp, _ = m("ttp_prime50_r79"); dte, _ = m("dt_eod50"); ld, _ = m("lucid_daily50"); lf, _ = m("lucidflex50")
TS_CONS = R(ts, combine_consistency=0.55, consistency_target=0.4, consistency_days=3, payout_cap=3000.0, winning_days_required=0)
LD = R(ld, payout_cap=float("inf"), payout_min=500.0, one_time_price=85.4, reset=85.4)
BOT = [("Topstep 50K Standard (benchmark)", ts, None), ("Topstep 50K Consistency", TS_CONS, None),
       ("TTP Futures Prime 50K", ttp, None),
       ("DayTraders EOD 50K $105", R(dte, one_time_price=105.0, reset=105.0, activation=5.0, monthly=0.0), 1250.0),
       ("LucidDaily 50K $85.40, funded trails intraday", R(LD, intraday_trail_funded=True), None),
       ("LucidDaily 50K $85.40, funded EOD", LD, None),
       ("LucidFlex 50K DLL ON $80.50", R(lf, one_time_price=80.5, reset=80.0, monthly=0.0), 1200.0),
       ("TradeDay 50K $85", R(TRADEDAY, monthly=85, reset=85), None)]
MANUAL = [("Topstep 50K Standard (benchmark, manual)", ts, None), ("Topstep 50K Consistency (manual)", TS_CONS, None),
          ("TTP Futures Prime 50K (manual)", ttp, None),
          ("DayTraders EOD 50K $105 (manual)", R(dte, one_time_price=105.0, reset=105.0, activation=5.0, monthly=0.0), 1250.0),
          ("LucidDaily 50K $85.40, intraday funded (manual)", R(LD, intraday_trail_funded=True), None),
          ("LucidFlex 50K DLL ON $80.50 (manual)", R(lf, one_time_price=80.5, reset=80.0, monthly=0.0), 1200.0),
          ("Top One Elite ACCESS 50K $39 promo (manual only)", topone(39.0, 142.0), None)]


def price(t, rules, dll):
    if dll:
        t = t.assign(net_pnl=np.maximum(t["net_pnl"].to_numpy(), -dll))
    pol = Policy.IMMEDIATE if rules.mll_locks_at is None else Policy.LOCK_FIRST
    real = recycle(t, rules, policy=pol)
    closed = recycle(t, R(rules, realtime_mll=False, intraday_trail_funded=False), policy=pol)["net"]
    g, comm = t["gross_pnl"].to_numpy(), (t["gross_pnl"] - t["net_pnl"]).to_numpy()
    rng = np.random.default_rng(1)
    fl = np.array([recycle(flip(t, g, comm, rng.choice([-1, 1], len(t))), rules, policy=pol)["net"] for _ in range(200)])
    return real["net"], worst_dip(real), float(np.median(fl)), float((fl > 0).mean()), closed


n_pass = 0
for label, delay, rows in [("BOT (orders at signal time)", 0, BOT), ("MANUAL (every entry 3 minutes late)", 3, MANUAL)]:
    t = trades(orders, bars, delay)
    ref = price(t, rows[0][1], rows[0][2])
    print(f"\n{label}. Bar: real >= ${0.5 * ref[0]:,.0f}, coin flip >= $5,000, dip >= ${1.5 * ref[1]:,.0f}")
    for name, rules, dll in rows:
        real, dip, fmed, fpos, closed = price(t, rules, dll)
        ok = real >= 0.5 * ref[0] and fmed >= 5000 and dip >= 1.5 * ref[1]
        n_pass += ok and "benchmark" not in name
        print(f"  {name:<50} real ${real:>8,.0f} (closed-P&L model ${closed:>8,.0f}) | coin flip ${fmed:>8,.0f} ({fpos:.0%}) | "
              f"dip ${dip:>7,.0f} | {'QUALIFIES' if ok else 'fails'}", flush=True)
print(f"\nqualifying rows (excluding the benchmark rows): {n_pass}")

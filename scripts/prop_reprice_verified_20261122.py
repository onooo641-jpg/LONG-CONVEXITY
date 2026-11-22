"""Re-price prop products whose official rules differ from the earlier models (docs/PROP_VERIFY_20261122.md, section 4).

    uv run python -m scripts.prop_reprice_verified_20261122 | tee docs/jx_runs/prop_reprice_verified_20261122.txt
"""
import dataclasses

import pandas as pd

from backtest.recycle import Policy
from ict import data as D
from scripts.radar_models2 import MODELS2
from scripts.radar_price import MODELS, price, trades

orders, bars = pd.read_parquet(D.PROCESSED_DIR / "ideas_orders_NQ.parquet"), D.load("1m")
T = {0: trades(orders, bars, 0), 3: trades(orders, bars, 3)}
REF = {0: (44359, -3520), 3: (37348, -3094)}
R = dataclasses.replace


def m2(key, i=0):
    return MODELS2[key][1][i][1:]


ts, ts_risk = MODELS["topstep50"][0][1:]
ld, ld_risk = m2("lucid_daily50")
s2f, s2f_risk = m2("dt_s2f50")
fei, fei_risk = m2("fe_instant50")
tti, tti_risk = m2("ttp_instant50")
ROWS = [
    ("Topstep 50K Standard (+55% combine consistency, official)", 0, R(ts, combine_consistency=0.55), ts_risk),
    ("Topstep 50K Consistency path (3 days, 40%, cap $3,000)", 0, R(ts, combine_consistency=0.55, consistency_target=0.4, consistency_days=3,
                                                                   payout_cap=3000.0, winning_days_required=0), ts_risk),
    ("Topstep 50K No-Activation ($95/mo, reset $85)", 0, R(ts, combine_consistency=0.55, monthly=95.0, reset=85.0, activation=0.0), ts_risk),
    ("TTP Futures Instant 50K at official $499", 0, R(tti, one_time_price=499.0, reset=499.0), tti_risk),
    ("LucidDaily 50K corrected (no cap, min $500) at $99 [sens]", 0, R(ld, payout_cap=float("inf"), payout_min=500.0), ld_risk),
    ("LucidDaily 50K corrected (no cap, min $500) at $199 [sens]", 0, R(ld, payout_cap=float("inf"), payout_min=500.0, one_time_price=199.0,
                                                                         reset=199.0), ld_risk),
    ("DayTraders S2F 50K corrected (targets $3,500/$3,000) at $199 [sens]", 0, R(s2f, payout_goal=(3500.0, 3000.0), payout_buffer=0.0), s2f_risk),
    ("DayTraders S2F 50K corrected (targets $3,500/$3,000) at $399 [sens]", 0, R(s2f, payout_goal=(3500.0, 3000.0), payout_buffer=0.0,
                                                                              one_time_price=399.0, reset=399.0), s2f_risk),
    ("FuturesElite Instant 50K corrected (20% consistency, $2,500 buffer) $199 [restricted MY]", 3,
     R(fei, consistency_target=0.2, payout_buffer=2500.0), fei_risk),
]
print("re-priced with official rules; flag rule as the radar (real >= 50% of Topstep, coin flip >= $5,000, dip >= 1.5x Topstep's)\n")
for name, d, rules, risk in ROWS:
    pol = Policy.IMMEDIATE if rules.mll_locks_at is None else Policy.LOCK_FIRST
    real, dip, flip, prof = price(T[d], rules, risk, pol)
    flag = real >= 0.5 * REF[d][0] and flip >= 5000 and dip >= 1.5 * REF[d][1]
    print(f"{name:<86} d{d} | real ${real:>9,.0f} | coin flip ${flip:>8,.0f} ({prof:.0%}) | dip ${dip:>8,.0f} | {'meets flag rule' if flag else '-'}", flush=True)

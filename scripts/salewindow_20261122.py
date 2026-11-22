"""#298 buy prop evaluations only in sale windows (docs/PREREG_BATCH10_20261122.md): ranking at 0/40/60/80% off purchase + reset prices.

    uv run python -m scripts.salewindow_20261122 | tee docs/jx_runs/salewindow_20261122.txt
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
REG = pd.read_csv("docs/radar/prop_firms.csv").fillna("")
AUTO = {r["model_key"]: r["automation"] for _, r in REG.iterrows() if r["model_key"]}
items = []
for key, v in MODELS.items():
    for it in v:
        items.append((key, AUTO.get(key, "full_bots"), it[0], it[1], it[2]))
for key, (auto, lst) in MODELS2.items():
    for name, rules, risk in lst:
        items.append((key, auto, name, rules, risk))
print("ranking (no pass/fail). Discount applies to the purchase price (monthly or one-time) and resets, not activation fees.")
print("flag rule as the radar: real >= 50% of Topstep, coin flip >= $5,000, dip >= 1.5x Topstep's (3-min delay products vs Topstep at 3 min)\n")
for key, auto, name, rules, risk in items:
    d = 3 if auto == "alert_assisted" else 0
    pol = Policy.IMMEDIATE if rules.mll_locks_at is None else Policy.LOCK_FIRST
    row = []
    for off in (0.0, 0.4, 0.6, 0.8):
        r2 = dataclasses.replace(rules, monthly=rules.monthly * (1 - off), reset=rules.reset * (1 - off),
                                 one_time_price=None if rules.one_time_price is None else rules.one_time_price * (1 - off))
        real, dip, flip, _ = price(T[d], r2, risk, pol)
        flag = real >= 0.5 * REF[d][0] and flip >= 5000 and dip >= 1.5 * REF[d][1]
        row.append(f"{int(off * 100):>2}% off ${real:>8,.0f}/${flip:>7,.0f}/${dip:>7,.0f}{'*' if flag else ' '}")
    print(f"{name[:42]:<42} d{d} | " + " | ".join(row), flush=True)
print("\n* = meets the flag rule at that price (real / coin flip / worst dip)")

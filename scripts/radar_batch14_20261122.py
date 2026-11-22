"""Run every addendum-14 product (#237-#258) with the sweep procedure; output docs/jx_runs/radar_batch14_20261122.txt.

    uv run python scripts/radar_batch14_20261122.py | tee docs/jx_runs/radar_batch14_20261122.txt
"""
import pandas as pd

from ict import data as D
from scripts.radar_models2 import MODELS2
from scripts.radar_price import price, trades

orders, bars = pd.read_parquet(D.PROCESSED_DIR / "ideas_orders_NQ.parquet"), D.load("1m")
T = {0: trades(orders, bars, 0), 3: trades(orders, bars, 3)}
REF = {0: (44359, -3520), 3: (37348, -3094)}
print("flag: real >= 50% of Topstep (no delay $22,180; 3-min $18,674), coin flip >= $5,000, dip >= 1.5x Topstep's (-$5,280 / -$4,641); [sens] never flagged\n")
for key, (auto, items) in MODELS2.items():
    d = 3 if auto == "alert_assisted" else 0
    for name, rules, risk in items:
        real, dip, flip, prof = price(T[d], rules, risk)
        flag = (real >= 0.5 * REF[d][0] and flip >= 5000 and dip >= 1.5 * REF[d][1])
        tag = ("would flag" if flag else "-") if "[sens]" in name else ("EXTRA SLOT CANDIDATE" if flag else "-")
        print(f"{key:<16} {name:<40} delay {d} | real ${real:>9,.0f} | coin flip ${flip:>8,.0f} ({prof:.0%}) | dip ${dip:>8,.0f} | {tag}", flush=True)

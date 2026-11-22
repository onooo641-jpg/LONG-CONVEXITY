"""Price one model key from scripts/radar_models.py with the sweep procedure (no delay unless --delay).

    uv run python scripts/radar_price_one.py mffu_studio | tee docs/jx_runs/radar_price_mffu_studio.txt
"""
import sys

import pandas as pd

from ict import data as D
from scripts.radar_price import DELAY_MIN, MODELS, price, trades
from backtest.recycle import Policy

key = sys.argv[1]
delay = DELAY_MIN if "--delay" in sys.argv else 0
t = trades(pd.read_parquet(D.PROCESSED_DIR / "ideas_orders_NQ.parquet"), D.load("1m"), delay)
print(f"{key}, entry delay {delay} min; flag needs real >= $22,180 (or $18,674 delayed), coin flip >= $5,000, dip >= -$5,280 (-$4,641 delayed)")
for item in MODELS[key]:
    name, rules, risk = item[:3]
    pol = item[3] if len(item) > 3 else Policy.LOCK_FIRST
    real, dip, flip, prof = price(t, rules, risk, pol)
    ref = (37348, -3094) if delay else (44359, -3520)
    flag = real >= 0.5 * ref[0] and flip >= 5000 and dip >= 1.5 * ref[1]
    print(f"{name:<34} risk ${risk:>4} | real ${real:>9,.0f} | coin flip ${flip:>8,.0f} ({prof:.0%}) | dip ${dip:>7,.0f} | {'EXTRA SLOT CANDIDATE' if flag else '-'}", flush=True)

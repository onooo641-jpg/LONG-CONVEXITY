"""Post-hoc sensitivity (labelled, not pre-registered) for FuturesElite Elite 50K's two assumed rules: price, funded lock.

    uv run python scripts/radar_fe_sens_20261121.py | tee docs/jx_runs/radar_fe_sens_20261121.txt
"""
import dataclasses

import pandas as pd

from ict import data as D
from scripts.radar_models import FE_ELITE50
from scripts.radar_price import price, trades

bars = D.load("1m")
orders = pd.read_parquet(D.PROCESSED_DIR / "ideas_orders_NQ.parquet")
t = trades(orders, bars, 3)
for name, r in [("as priced ($128, lock at start)", FE_ELITE50),
                ("price $200", dataclasses.replace(FE_ELITE50, one_time_price=200.0, reset=200.0)),
                ("funded floor never locks", dataclasses.replace(FE_ELITE50, mll_locks_at=1e9)),
                ("price $200 + never locks", dataclasses.replace(FE_ELITE50, one_time_price=200.0, reset=200.0, mll_locks_at=1e9))]:
    real, dip, flip, prof = price(t, r, 900)
    print(f"FuturesElite Elite 50K, 3-min delay, {name:<32} real ${real:>9,.0f} | coin flip ${flip:>8,.0f} ({prof:.0%}) | dip ${dip:>7,.0f}", flush=True)

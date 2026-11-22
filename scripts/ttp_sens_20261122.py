"""Sensitivity (labelled, not a verdict) for TTP Futures Prime 50K: purchase price and the 30-day challenge limit.

    uv run python scripts/ttp_sens_20261122.py | tee docs/jx_runs/ttp_sens_20261122.txt
"""
import dataclasses

import pandas as pd

from ict import data as D
from scripts.radar_models import TTP_PRIME50
from scripts.radar_price import price, trades

t = trades(pd.read_parquet(D.PROCESSED_DIR / "ideas_orders_NQ.parquet"), D.load("1m"), 0)
for name, r in [("as registered ($99, 30-day limit)", TTP_PRIME50),
                ("price $59.40 (directory discount)", dataclasses.replace(TTP_PRIME50, one_time_price=59.4, reset=59.4)),
                ("price $149", dataclasses.replace(TTP_PRIME50, one_time_price=149.0, reset=149.0)),
                ("price $199", dataclasses.replace(TTP_PRIME50, one_time_price=199.0, reset=199.0)),
                ("no 40% eval consistency", dataclasses.replace(TTP_PRIME50, combine_consistency=None)),
                ("3-min delay (manual entry)", None)]:
    if r is None:
        tt = trades(pd.read_parquet(D.PROCESSED_DIR / "ideas_orders_NQ.parquet"), D.load("1m"), 3)
        real, dip, flip, prof = price(tt, TTP_PRIME50, 875)
    else:
        real, dip, flip, prof = price(t, r, 875)
    print(f"TTP Futures Prime 50K, {name:<36} real ${real:>9,.0f} | coin flip ${flip:>8,.0f} ({prof:.0%}) | dip ${dip:>7,.0f}", flush=True)

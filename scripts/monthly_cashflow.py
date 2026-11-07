"""What a calendar month looks like: fees out, payouts in.

    uv run python scripts/monthly_cashflow.py
    uv run python scripts/monthly_cashflow.py --orders cached.parquet

The 11-year net is an average over months that are mostly negative. This
counts them: one unbroken chain from 2016, $900/trade, XFARules() defaults,
LOCK_FIRST, cash withdrawn minus cost accrued, bucketed by New York calendar
month. Cost is booked at account events (recycle()'s timeline), so a month's
cost can lag the calendar slightly; the total is exact.
"""

from __future__ import annotations

import argparse

import numpy as np
import pandas as pd

from backtest.recycle import Policy, XFARules, recycle
from scripts.recycling_report import HISTORY_START, between, fills, load_bars
from strategies.ltf_sweep import generate_orders

NY = "America/New_York"


def month(ts) -> pd.PeriodIndex:
    return pd.DatetimeIndex(ts).tz_convert(NY).tz_localize(None).to_period("M")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--orders", default=None, help="cached orders parquet")
    args = ap.parse_args(argv)

    bars = load_bars(HISTORY_START)
    orders = pd.read_parquet(args.orders) if args.orders else generate_orders(bars)
    h = between(fills(orders, bars, 900.0), HISTORY_START, "2027-01-01")

    g = h.assign(mo=month(h["exit_ts"])).groupby("mo")["net_pnl"]
    raw, win = g.sum(), g.apply(lambda x: (x > 0).mean())
    print(f"strategy alone, {len(raw)} months: losing {np.mean(raw < 0):.0%}, "
          f"win rate <= 42% (October 2026's forward log was 41.7%): "
          f"{np.mean(win <= 0.42):.0%}")

    out = recycle(h, XFARules(), policy=Policy.LOCK_FIRST)
    tl = pd.DataFrame(out["timeline"]).assign(mo=lambda d: month(d["ts"]))
    last = tl.groupby("mo")[["cash", "cost"]].last().reindex(raw.index).ffill().fillna(0)
    flow = last.diff().fillna(last)
    net = flow["cash"] - flow["cost"]
    pre = net[net.index < pd.Period("2026-01", "M")]
    print(f"recycling, {len(net)} months: no payout {np.mean(flow['cash'] == 0):.0%}, "
          f"positive {np.mean(net > 0):.0%}")
    print(f"  median month ${net.median():,.0f}  average ${net.mean():,.0f}  "
          f"(2016-2025 only ${pre.mean():,.0f})  best ${net.max():,.0f}  "
          f"worst ${net.min():,.0f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Prop search 2, Stage D (docs/PREREG_PROP_SEARCH2_20261126.md): DayTraders 50K Static, 50K Trail and 25K S2F at Jx's checkout prices,
official rules (DayTraders help articles, Oct 2026), real-time model (DayTraders' pages).

    uv run python -m scripts.prop_search2_d_20261126 | tee docs/jx_runs/prop_search2_d_20261126.txt
"""
import dataclasses as dc

import pandas as pd

from backtest.recycle import Policy, XFARules
from ict import data as D
from scripts.radar_models2 import instant
from scripts.radar_price import MODELS, price, trades

R = dc.replace
B = XFARules()
COMMON = dict(funded_scaling=False, combine_consistency=0.50, consistency_target=0.30, consistency_days=1, payout_needs_both=True,
              winning_days_required=8, winning_day_min=200.0, payout_share=1.0, payout_cap=2000.0, payout_min=500.0, profit_split=1.0,
              profit_since_payout_required=True, monthly=0.0, activation=5.0, api_monthly=0.0)
DT_STATIC50 = R(B, profit_target=3750, loss_limit=1000, funded_loss_limit=1000, static_dd=True, mll_locks_at=None, lock_level=-1000.0,
                combine_max_contracts=60, one_time_price=50.0, reset=50.0, **COMMON)
DT_TRAIL50 = R(B, profit_target=3000, loss_limit=2500, funded_loss_limit=2500, mll_locks_at=2500, lock_level=0.0, combine_max_contracts=100,
               intraday_trail_funded=True, intraday_trail_eval=True, one_time_price=70.0, reset=70.0, **COMMON)
DT_S2F25 = instant(1000, 1000, 0.0, 20, 2000, 1500, 0.20, 1000, 500, 1.0, 222.0, wdays=10, wmin=100.0)
ROWS = [("DayTraders 50K Static ($50 + $5)", DT_STATIC50, 450.0), ("DayTraders 50K Trail ($70 + $5)", DT_TRAIL50, 1125.0),
        ("DayTraders 25K S2F ($222)", DT_S2F25, 450.0)]


def main():
    orders, bars = pd.read_parquet(D.PROCESSED_DIR / "ideas_orders_NQ.parquet"), D.load("1m")
    t0 = trades(orders, bars, 0)
    ts, ts_risk = MODELS["topstep50"][0][1:]
    ref_real, ref_dip, _, _ = price(t0, ts, ts_risk, Policy.LOCK_FIRST)
    print(f"Bar: real >= ${0.5 * ref_real:,.0f}, coin flip >= $5,000, dip >= ${1.5 * ref_dip:,.0f}\n")
    n = 0
    for name, rules, risk in ROWS:
        pol = Policy.IMMEDIATE if rules.mll_locks_at is None else Policy.LOCK_FIRST
        real, dip, fmed, fpos = price(t0, rules, risk, pol)
        ok = real >= 0.5 * ref_real and fmed >= 5000 and dip >= 1.5 * ref_dip
        n += ok
        print(f"  {name:<36} risk ${risk:>5,.0f} | real ${real:>8,.0f} | coin flip ${fmed:>8,.0f} ({fpos:.0%}) | dip ${dip:>8,.0f} | "
              f"{'QUALIFIES' if ok else 'fails'}", flush=True)
    print(f"\nqualifying: {n}")


if __name__ == "__main__":
    main()

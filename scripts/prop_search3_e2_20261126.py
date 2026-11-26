"""Prop search 3, addendum E2 (docs/PREREG_PROP_SEARCH3_20261126.md): break-even one-time prices for Funded Futures Network Standard MAX
and DayTraders 100K/150K Static (prices unknown).

    uv run python -m scripts.prop_search3_e2_20261126 | tee docs/jx_runs/prop_search3_e2_20261126.txt
"""
import dataclasses as dc

import pandas as pd

from backtest.recycle import Policy, XFARules
from ict import data as D
from scripts.prop_search2_d_20261126 import COMMON
from scripts.prop_search3_20261126 import ffn_max, run_one
from scripts.radar_price import MODELS, price, trades

R = dc.replace
B = XFARules()


def main():
    orders, bars = pd.read_parquet(D.PROCESSED_DIR / "ideas_orders_NQ.parquet"), D.load("1m")
    t0 = trades(orders, bars, 0)
    ts, ts_risk = MODELS["topstep50"][0][1:]
    ref_real, ref_dip, _, _ = price(t0, ts, ts_risk, Policy.LOCK_FIRST)
    print(f"Registered bar: real >= ${0.5 * ref_real:,.0f}, coin flip >= $5,000, dip >= ${1.5 * ref_dip:,.0f}\n")
    rows = []
    for size, listp in ((50, 178.0), (100, 348.0), (150, 408.0)):
        for act in (0.0, 120.0):
            r, dll = ffn_max(size, listp, act, 100.0)
            for risk in sorted({900.0, 0.45 * r.loss_limit}):
                rows.append((f"FFN Std MAX {size}K, activation ${act:.0f}", r, risk, dll, listp))
    for size, (tgt, dd, micros, cap) in {100: (5750, 1500, 80, 3000.0), 150: (6750, 1750, 80, 3500.0)}.items():
        r = R(B, profit_target=tgt, loss_limit=dd, funded_loss_limit=dd, static_dd=True, mll_locks_at=None, lock_level=-float(dd),
              combine_max_contracts=micros, one_time_price=55.0, reset=55.0,
              **{**COMMON, "payout_cap": cap, "winning_day_min": 300.0, "activation": 5.0})
        for risk in sorted({900.0, 0.45 * dd}):
            rows.append((f"DayTraders {size}K Static", r, risk, None, float("nan")))
    for name, rules, risk, dll, listp in rows:
        def ok(p):
            rr = R(rules, one_time_price=float(p), reset=min(float(p), rules.reset) if "FFN" in name else float(p))
            real, dip, fmed, _ = run_one(t0, rr, risk, dll)
            return real >= 0.5 * ref_real and fmed >= 5000 and dip >= 1.5 * ref_dip
        if not ok(0):
            print(f"  {name:<34} risk ${risk:>5,.0f} | no price works", flush=True)
            continue
        lo, hi = 0, 3000
        if ok(hi):
            print(f"  {name:<34} risk ${risk:>5,.0f} | qualifies at any price up to $3,000", flush=True)
            continue
        while hi - lo > 1:
            mid = (lo + hi) // 2
            lo, hi = (mid, hi) if ok(mid) else (lo, mid)
        tail = "" if listp != listp else f" (list ${listp:,.0f}: {'QUALIFIES' if listp <= lo else f'needs {1 - lo / listp:.0%} off'})"
        print(f"  {name:<34} risk ${risk:>5,.0f} | break-even ${lo:,}{tail}", flush=True)


if __name__ == "__main__":
    main()

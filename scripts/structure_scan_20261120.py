"""Structure scan: coin-flip net per prop-firm product (docs/PREREG_STRUCTURE_SCAN_20261120.md).

    uv run python scripts/structure_scan_20261120.py
"""

from __future__ import annotations

import dataclasses

import numpy as np
import pandas as pd

from backtest.engine import BacktestConfig, simulate
from backtest.recycle import Policy, XFARules, recycle
from ict import data as D

LO, HI = "2016-01-01", "2026-10-29"
B = XFARules()


def topstep(size, path, noact=False):
    t, mll, cap_std, cap_con, micros, monthly = {
        50: (3000, 2000, 2000, 3000, 50, 49), 100: (6000, 3000, 3000, 4000, 100, 99),
        150: (9000, 4500, 5000, 6000, 150, 149)}[size]
    kw = dict(profit_target=t, loss_limit=mll, funded_loss_limit=mll, mll_locks_at=mll,
              combine_max_contracts=micros, monthly=monthly, reset=monthly, scaling_mult=size // 50,
              payout_cap=cap_con if path == "Consistency" else cap_std,
              consistency_target=0.40 if path == "Consistency" else None)
    if noact:
        kw.update(monthly=95, reset=95, activation=0.0)
    return dataclasses.replace(B, **kw)


def lucidflex(size):
    t, mll, cap, micros, price, reset, win = {
        25: (1250, 1000, 1000, 20, 100, 80, 100), 50: (3000, 2000, 2000, 40, 115, 90, 150),
        100: (6000, 3000, 2500, 60, 279, 195, 200), 150: (9000, 4500, 3000, 100, 379, 265, 250)}[size]
    return dataclasses.replace(
        B, profit_target=t, loss_limit=mll, funded_loss_limit=mll, mll_locks_at=mll + 100, lock_level=100.0,
        combine_max_contracts=micros, funded_scaling=False, winning_day_min=win, payout_cap=cap,
        payout_min=500.0, max_payouts_per_xfa=5, one_time_price=price, reset=reset, monthly=0.0,
        activation=0.0, api_monthly=15.0)


def tradeify_flex50():
    return dataclasses.replace(
        B, profit_target=3000, loss_limit=2000, funded_loss_limit=2000, mll_locks_at=2100, lock_level=100.0,
        combine_max_contracts=40, funded_scaling=False, winning_day_min=150, payout_cap=2500,
        payout_min=250.0, max_payouts_per_xfa=5, monthly=159.0, reset=95.0, activation=0.0, api_monthly=15.0)


PRODUCTS = {
    "Topstep 50K Standard": (topstep(50, "Standard"), 2000),
    "Topstep 50K Consistency": (topstep(50, "Consistency"), 2000),
    "Topstep 50K No-Activation": (topstep(50, "Standard", noact=True), 2000),
    "Topstep 100K Standard": (topstep(100, "Standard"), 3000),
    "Topstep 100K Consistency": (topstep(100, "Consistency"), 3000),
    "Topstep 150K Standard": (topstep(150, "Standard"), 4500),
    "Topstep 150K Consistency": (topstep(150, "Consistency"), 4500),
    "LucidFlex 25K": (lucidflex(25), 1000),
    "LucidFlex 50K": (lucidflex(50), 2000),
    "LucidFlex 100K": (lucidflex(100), 3000),
    "LucidFlex 150K": (lucidflex(150), 4500),
    "Tradeify Select Flex 50K": (tradeify_flex50(), 2000),
}


def main() -> int:
    bars = D.load("1m")
    orders = pd.read_parquet(D.PROCESSED_DIR / "ideas_orders_NQ.parquet")
    cache, rows = {}, []
    yrs = (pd.Timestamp(HI) - pd.Timestamp(LO)).days / 365.25
    for name, (rules, mll) in PRODUCTS.items():
        risk = 0.45 * mll
        if risk not in cache:
            t = simulate(orders, bars, BacktestConfig(risk_per_trade_usd=risk))
            t = t[t["filled"]]
            t = t[(t.entry_ts >= pd.Timestamp(LO, tz="UTC")) & (t.entry_ts < pd.Timestamp(HI, tz="UTC"))]
            cache[risk] = t.sort_values("exit_ts").reset_index(drop=True)
        t = cache[risk]
        real = recycle(t, rules, policy=Policy.LOCK_FIRST)
        g = t["gross_pnl"].to_numpy()
        comm = (t["gross_pnl"] - t["net_pnl"]).to_numpy()
        rng = np.random.default_rng(1)
        flips = np.array([recycle(t.assign(net_pnl=np.abs(g) * rng.choice([-1, 1], len(t)) - comm),
                                  rules, policy=Policy.LOCK_FIRST)["net"] for _ in range(200)])
        rows.append({"product": name, "risk": risk, "flip_median": np.median(flips), "flip_p10": np.percentile(flips, 10),
                     "flip_profitable": (flips > 0).mean(), "real": real["net"], "real_spent": real["cost"]})
        print(f"{name:<28} risk ${risk:>5,.0f}  coin-flip median ${np.median(flips):>9,.0f} "
              f"(${np.median(flips) / yrs:>6,.0f}/yr, profitable {(flips > 0).mean():>4.0%}, 10th pct ${np.percentile(flips, 10):>8,.0f})  "
              f"real ${real['net']:>9,.0f}", flush=True)
    df = pd.DataFrame(rows).sort_values("flip_median", ascending=False)
    print("\n=== RANKING by coin-flip median net (2016-2026)")
    for i, r in enumerate(df.itertuples(), 1):
        print(f"  {i:>2}. {r.product:<28} ${r.flip_median:>9,.0f}  profitable {r.flip_profitable:>4.0%}  real ${r.real:>9,.0f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

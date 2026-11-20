"""FTMO Futures vs Topstep 50K (docs/PREREG_FTMO_FUTURES_20261120.md).

    uv run python scripts/ftmo_futures_20261120.py
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
FTMO_COMMON = dict(profit_target=3000, combine_max_contracts=100, lock_level=0.0, profit_split=0.90,
                   activation=0.0, api_monthly=15.0, free_reset_per_rebill=False)
GROWTH = dataclasses.replace(B, **FTMO_COMMON, loss_limit=2000, funded_loss_limit=2000, mll_locks_at=2000,
                             winning_day_min=150, winning_days_required=4, payout_share=0.5, payout_cap=2500,
                             combine_consistency=0.40, monthly=119, reset=109)
PRO = dataclasses.replace(B, **FTMO_COMMON, loss_limit=3000, funded_loss_limit=3000, mll_locks_at=3000,
                          daily_loss_limit=1000, winning_day_min=200, winning_days_required=5, payout_share=1.0,
                          payout_cap=5000, combine_consistency=0.50, monthly=139, reset=129)
PRODUCTS = {
    "Topstep 50K (reference)": (B, 900),
    "FTMO Futures Growth 50K": (GROWTH, 900),
    "FTMO Futures Pro 50K, withdraw 100%": (PRO, 800),
    "FTMO Futures Pro 50K, withdraw 50%": (dataclasses.replace(PRO, payout_share=0.5), 800),
}


def worst_dip(out):
    tl = pd.DataFrame(out["timeline"])
    if tl.empty:
        return 0.0
    net = tl["net"].to_numpy()
    return float((net - np.maximum.accumulate(np.maximum(net, 0))).min())


def main() -> int:
    bars = D.load("1m")
    orders = pd.read_parquet(D.PROCESSED_DIR / "ideas_orders_NQ.parquet")
    yrs = (pd.Timestamp(HI) - pd.Timestamp(LO)).days / 365.25
    cache = {}
    for name, (rules, risk) in PRODUCTS.items():
        if risk not in cache:
            t = simulate(orders, bars, BacktestConfig(risk_per_trade_usd=risk))
            t = t[t["filled"]]
            t = t[(t.entry_ts >= pd.Timestamp(LO, tz="UTC")) & (t.entry_ts < pd.Timestamp(HI, tz="UTC"))]
            cache[risk] = t.sort_values("exit_ts").reset_index(drop=True)
        t = cache[risk]
        real = recycle(t, rules, policy=Policy.LOCK_FIRST)
        g, comm = t["gross_pnl"].to_numpy(), (t["gross_pnl"] - t["net_pnl"]).to_numpy()
        rng = np.random.default_rng(1)
        flips = np.array([recycle(t.assign(net_pnl=np.abs(g) * rng.choice([-1, 1], len(t)) - comm),
                                  rules, policy=Policy.LOCK_FIRST)["net"] for _ in range(200)])
        print(f"{name:<38} risk ${risk}: real net ${real['net']:>9,.0f} (${real['net'] / yrs:>6,.0f}/yr; "
              f"withdrawn ${real['cash']:,.0f}, spent ${real['cost']:,.0f}, worst dip ${worst_dip(real):,.0f}, "
              f"funded {real['funded_earned']}, payouts {real['payouts']}) | coin-flip median ${np.median(flips):>9,.0f}, "
              f"profitable {(flips > 0).mean():.0%}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

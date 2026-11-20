"""TradeDay Fast Pass / Bulenox Momentum vs Topstep 50K (docs/PREREG_FIRMS2_20261120.md).

    uv run python scripts/firms2_20261120.py
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
TRADEDAY = dataclasses.replace(
    B, profit_target=3000, loss_limit=2000, combine_max_contracts=50, combine_consistency=0.45,
    funded_loss_limit=2000, mll_locks_at=2000, funded_scaling=False, winning_day_min=150,
    winning_days_required=5, consistency_target=0.45, consistency_days=5, payout_needs_both=True,
    payout_share=0.5, payout_cap=1500, payout_min=250, profit_split=0.80, monthly=189, reset=189,
    activation=0.0, api_monthly=15.0)
BULENOX = dataclasses.replace(
    B, profit_target=3000, loss_limit=2000, combine_max_days=30, funded_loss_limit=2000, mll_locks_at=2100,
    lock_level=100.0, ladder=((1500.0, 20), (4000.0, 40), (float("inf"), 70)), winning_day_min=150,
    winning_days_required=5, consistency_target=0.35, consistency_days=5, payout_needs_both=True,
    payout_buffer=3000.0, payout_cap=1500, max_payouts_per_xfa=3, profit_split=0.90,
    one_time_price=143.0, reset=143.0, monthly=0.0, activation=0.0, api_monthly=15.0)
PRODUCTS = {
    "Topstep 50K (reference)": B,
    "TradeDay Fast Pass 50K, list $189/mo": TRADEDAY,
    "TradeDay Fast Pass 50K, $85/mo with code": dataclasses.replace(TRADEDAY, monthly=85, reset=85),
    "Bulenox Momentum 50K Opt 2": BULENOX,
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
    t = simulate(orders, bars, BacktestConfig(risk_per_trade_usd=900))
    t = t[t["filled"]]
    t = t[(t.entry_ts >= pd.Timestamp(LO, tz="UTC")) & (t.entry_ts < pd.Timestamp(HI, tz="UTC"))]
    t = t.sort_values("exit_ts").reset_index(drop=True)
    g, comm = t["gross_pnl"].to_numpy(), (t["gross_pnl"] - t["net_pnl"]).to_numpy()
    for name, rules in PRODUCTS.items():
        real = recycle(t, rules, policy=Policy.LOCK_FIRST)
        rng = np.random.default_rng(1)
        flips = np.array([recycle(t.assign(net_pnl=np.abs(g) * rng.choice([-1, 1], len(t)) - comm),
                                  rules, policy=Policy.LOCK_FIRST)["net"] for _ in range(200)])
        print(f"{name:<42} real net ${real['net']:>9,.0f} (${real['net'] / yrs:>6,.0f}/yr; withdrawn ${real['cash']:,.0f}, "
              f"spent ${real['cost']:,.0f}, worst dip ${worst_dip(real):,.0f}, funded {real['funded_earned']}, "
              f"payouts {real['payouts']}, eval busts {real['combine_busts']}) | coin-flip median ${np.median(flips):>9,.0f}, "
              f"profitable {(flips > 0).mean():.0%}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

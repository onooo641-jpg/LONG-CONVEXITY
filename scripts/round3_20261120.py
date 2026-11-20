"""Round 3: MFFU Rapid EOD 50K, TFD Static Core/Pro vs Topstep 50K (docs/PREREG_ROUND3_20261120.md).

    uv run python scripts/round3_20261120.py
"""
from __future__ import annotations

import dataclasses

import numpy as np
import pandas as pd

from backtest.engine import BacktestConfig, simulate
from backtest.recycle import Policy, XFARules, recycle
from ict import data as D

LO, HI = "2016-01-01", "2026-10-29"
INF = float("inf")
B = XFARules()
MFFU = dataclasses.replace(
    B, profit_target=3000, loss_limit=2000, combine_max_contracts=30, combine_consistency=0.30,
    combine_max_days=365, funded_loss_limit=2000, mll_locks_at=2100, lock_level=100.0,
    funded_scaling=False, winning_days_required=0, payout_buffer=2100.0, payout_cap=INF,
    payout_min=500.0, payout_goal=(0.0, 500.0), profit_split=0.90, one_time_price=157.0,
    reset=157.0, monthly=0.0, activation=0.0)
TFD_CORE = dataclasses.replace(
    B, profit_target=4000, loss_limit=2000, static_dd=True, combine_max_contracts=20,
    funded_loss_limit=2000, mll_locks_at=2000, lock_level=0.0, funded_scaling=False,
    winning_days_required=0, payout_buffer=2000.0, payout_cap=INF, payout_min=100.0,
    profit_split=0.80, one_time_price=139.0, reset=99.0, monthly=29.0, activation=0.0)
TFD_PRO = dataclasses.replace(
    TFD_CORE, profit_target=6000, loss_limit=3000, combine_max_contracts=30, funded_loss_limit=3000,
    mll_locks_at=3000, payout_buffer=3000.0, one_time_price=179.0)
# (name, rules, risk per trade, ranked?)
PRODUCTS = [
    ("Topstep 50K (reference)", B, 900, True),
    ("MFFU Rapid EOD 50K", MFFU, 900, True),
    ("TFD Static Core", TFD_CORE, 700, True),
    ("TFD Static Pro", TFD_PRO, 1050, True),
    ("TFD Static Core, payouts down to floor (upper bound)",
     dataclasses.replace(TFD_CORE, payout_buffer=0.0), 700, False),
]


def worst_dip(out):
    tl = pd.DataFrame(out["timeline"])
    if tl.empty:
        return 0.0
    net = tl["net"].to_numpy()
    return float((net - np.maximum.accumulate(np.maximum(net, 0))).min())


def scaled(t, k):
    s = t.copy()
    for c in ("net_pnl", "gross_pnl"):
        s[c] = s[c] * k
    s["contracts"] = np.maximum(1, np.round(s["contracts"] * k)).astype(int)
    return s


def main() -> int:
    bars = D.load("1m")
    orders = pd.read_parquet(D.PROCESSED_DIR / "ideas_orders_NQ.parquet")
    yrs = (pd.Timestamp(HI) - pd.Timestamp(LO)).days / 365.25
    t = simulate(orders, bars, BacktestConfig(risk_per_trade_usd=900))
    t = t[t["filled"]]
    t = t[(t.entry_ts >= pd.Timestamp(LO, tz="UTC")) & (t.entry_ts < pd.Timestamp(HI, tz="UTC"))]
    t = t.sort_values("exit_ts").reset_index(drop=True)
    for name, rules, risk, ranked in PRODUCTS:
        s = scaled(t, risk / 900)
        g, comm = s["gross_pnl"].to_numpy(), (s["gross_pnl"] - s["net_pnl"]).to_numpy()
        real = recycle(s, rules, policy=Policy.LOCK_FIRST)
        rng = np.random.default_rng(1)
        flips = np.array([recycle(s.assign(net_pnl=np.abs(g) * rng.choice([-1, 1], len(s)) - comm),
                                  rules, policy=Policy.LOCK_FIRST)["net"] for _ in range(200)])
        capped = (s["contracts"] > rules.combine_max_contracts).mean()
        tag = "" if ranked else "  [sensitivity, not ranked]"
        print(f"{name:<52} risk ${risk:>5} | real net ${real['net']:>9,.0f} (${real['net'] / yrs:>6,.0f}/yr; "
              f"withdrawn ${real['cash']:,.0f}, spent ${real['cost']:,.0f}, worst dip ${worst_dip(real):,.0f}, "
              f"funded {real['funded_earned']}, payouts {real['payouts']}, eval busts {real['combine_busts']}, "
              f"trades over cap {capped:.0%}) | coin-flip median ${np.median(flips):>9,.0f}, "
              f"profitable {(flips > 0).mean():.0%}{tag}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

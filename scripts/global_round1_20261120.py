"""Global round 1: Breakout static 1-Step 50K and Tradeify Lightning 50K (docs/PREREG_GLOBAL_20261120.md).

    uv run python scripts/global_round1_20261120.py
"""
from __future__ import annotations

import dataclasses

import numpy as np
import pandas as pd

from backtest.engine import BacktestConfig, simulate
from backtest.recycle import Policy, XFARules, recycle
from ict import data as D

LO, HI = "2016-01-01", "2026-10-29"
SPLIT, MIN_GROSS = 0.80, 62.5          # $50 net minimum at 80%
BREAKOUT = {"Classic": (400.0, 5000.0, 3000.0), "Pro": (280.0, 6000.0, 2500.0), "Turbo": (180.0, 4500.0, 1500.0)}
DAILY = 1500.0                          # 3% of 50K
LIGHTNING = dataclasses.replace(
    XFARules(), instant_funded=True, one_time_price=492.0, reset=492.0, monthly=0.0, activation=0.0,
    api_monthly=15.0, funded_loss_limit=2000.0, mll_locks_at=2100.0, lock_level=100.0, funded_scaling=False,
    ladder=((float("inf"), 40),), consistency_target=0.25, consistency_days=1, payout_goal=(3000.0, 2000.0),
    payout_share=1.0, payout_cap=1500.0, profit_split=0.90)


def breakout(pnl, fee, target, maxl, refund):
    """Static floor, on-demand payouts; returns net, spent, funded count, worst dip."""
    spent, paid, bal, phase, refund_due, funded = fee, 0.0, 0.0, 0, False, 0
    peak_net, worst = 0.0, 0.0
    for p in pnl:
        bal += p
        if bal <= -maxl or p <= -DAILY:
            spent += fee
            bal, phase, refund_due = 0.0, 0, False
        elif phase == 0 and bal >= target:
            phase, bal, refund_due, funded = 1, 0.0, refund, funded + 1
        elif phase == 1 and bal >= MIN_GROSS:
            paid += SPLIT * bal + (fee if refund_due else 0.0)
            bal, refund_due = 0.0, False
        net = paid - spent
        peak_net = max(peak_net, net)
        worst = min(worst, net - peak_net)
    return paid - spent, spent, funded, worst


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

    def trades(risk):
        if risk not in cache:
            t = simulate(orders, bars, BacktestConfig(risk_per_trade_usd=risk))
            t = t[t["filled"]]
            t = t[(t.entry_ts >= pd.Timestamp(LO, tz="UTC")) & (t.entry_ts < pd.Timestamp(HI, tz="UTC"))]
            cache[risk] = t.sort_values("exit_ts").reset_index(drop=True)
        return cache[risk]

    def capped(t, lev):
        """Shrink each trade so its notional stays within lev x the 50K account (Kraken Prop index cap)."""
        notional = t["contracts"] * t["entry_price"] * 2.0
        k = np.minimum(1.0, lev * 50_000 / notional).to_numpy()
        return t.net_pnl.to_numpy() * k, t.gross_pnl.to_numpy() * k, (t.gross_pnl - t.net_pnl).to_numpy() * k

    print("Topstep 50K reference (C2/C6): real net $44,359, coin-flip median $18,046 (98% profitable), worst dip -$3,520\n")
    for plan, (fee, target, maxl) in BREAKOUT.items():
        for frac in (0.25, 0.33, 0.43):
            risk = int(min(frac * maxl, 0.85 * DAILY) // 50 * 50)
            t = trades(risk)
            for lev in (None, 10, 5):
              if lev is None:
                  net, g, comm = t.net_pnl.to_numpy(), t.gross_pnl.to_numpy(), (t.gross_pnl - t.net_pnl).to_numpy()
              else:
                  net, g, comm = capped(t, lev)
              for refund in (False, True):
                real = breakout(net, fee, target, maxl, refund)
                rng = np.random.default_rng(1)
                flips = np.array([breakout(np.abs(g) * rng.choice([-1, 1], len(t)) - comm, fee, target, maxl, refund)[0]
                                  for _ in range(200)])
                print(f"Breakout {plan:<7} 50K risk ${risk:>5} ({frac:.0%}) lev {('none' if lev is None else f'{lev}x'):>4} refund={'yes' if refund else 'no ':<3} | "
                      f"real net ${real[0]:>9,.0f} (${real[0] / yrs:>6,.0f}/yr, spent ${real[1]:>7,.0f}, funded {real[2]:>3}, "
                      f"worst dip ${real[3]:>8,.0f}) | coin-flip median ${np.median(flips):>9,.0f}, profitable {(flips > 0).mean():.0%}",
                      flush=True)
    t = trades(900)
    g, comm = t.gross_pnl.to_numpy(), (t.gross_pnl - t.net_pnl).to_numpy()
    for cap in (1500.0, 2000.0):
        rules = dataclasses.replace(LIGHTNING, payout_cap=cap)
        real = recycle(t, rules, policy=Policy.LOCK_FIRST)
        rng = np.random.default_rng(1)
        flips = np.array([recycle(t.assign(net_pnl=np.abs(g) * rng.choice([-1, 1], len(t)) - comm), rules,
                                  policy=Policy.LOCK_FIRST)["net"] for _ in range(200)])
        print(f"\nTradeify Lightning 50K cap ${cap:,.0f}: real net ${real['net']:>9,.0f} (spent ${real['cost']:,.0f}, "
              f"accounts {real['accounts_bought']}, payouts {real['payouts']}, worst dip ${worst_dip(real):,.0f}) | "
              f"coin-flip median ${np.median(flips):>9,.0f}, profitable {(flips > 0).mean():.0%}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

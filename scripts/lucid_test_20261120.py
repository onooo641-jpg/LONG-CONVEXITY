"""Lucid (LucidFlex 50K) vs Topstep, as docs/PREREG_LUCID_20261120.md defines it.

    uv run python scripts/lucid_test_20261120.py
"""

from __future__ import annotations

import dataclasses

import numpy as np
import pandas as pd

from backtest.engine import BacktestConfig, simulate
from backtest.recycle import Policy, XFARules, recycle
from ict import data as D

WINDOWS = {"2016-2026": ("2016-01-01", "2026-10-29"), "2010-2015": ("2010-07-01", "2016-01-01")}
TOPSTEP = XFARules()
LUCID = dataclasses.replace(
    XFARules(), profit_target=3000, loss_limit=2000, combine_max_contracts=40,
    funded_loss_limit=2000, mll_locks_at=2100, lock_level=100.0,
    winning_day_min=150, winning_days_required=5, payout_share=0.5, payout_cap=2000,
    payout_min=500.0, max_payouts_per_xfa=5, funded_scaling=False,
    one_time_price=115.0, reset=90.0, monthly=0.0, activation=0.0, api_monthly=15.0)


def window(t, lo, hi):
    t = t[(t["entry_ts"] >= pd.Timestamp(lo, tz="UTC")) & (t["entry_ts"] < pd.Timestamp(hi, tz="UTC"))]
    return t.sort_values("exit_ts").reset_index(drop=True)


def flips(t, rules, n=200):
    g = t["gross_pnl"].to_numpy()
    comm = (t["gross_pnl"] - t["net_pnl"]).to_numpy()
    rng = np.random.default_rng(1)
    return np.array([recycle(t.assign(net_pnl=np.abs(g) * rng.choice([-1, 1], len(t)) - comm),
                             rules, policy=Policy.LOCK_FIRST)["net"] for _ in range(n)])


def worst_start(t, rules):
    """Deepest cumulative net over chains started at each month (as jx_capital.py)."""
    exits = pd.DatetimeIndex(t["exit_ts"])
    start, worst = exits.min(), []
    while start < exits.max() - pd.DateOffset(months=12):
        chunk = t[exits >= start].reset_index(drop=True)
        tl = pd.DataFrame(recycle(chunk, rules, policy=Policy.LOCK_FIRST)["timeline"])
        worst.append(min(0.0, float(tl["net"].min())))
        start = start + pd.DateOffset(months=1)
    return float(np.median(worst)), float(min(worst)), len(worst)


def main() -> int:
    bars = D.load("1m")
    orders = pd.read_parquet(D.PROCESSED_DIR / "ideas_orders_NQ.parquet")
    t = simulate(orders, bars, BacktestConfig(risk_per_trade_usd=900.0))
    t = t[t["filled"]].sort_values("exit_ts").reset_index(drop=True)
    res = {}
    for firm, rules in (("Topstep 50K", TOPSTEP), ("LucidFlex 50K", LUCID)):
        print(f"\n=== {firm}")
        for wname, (lo, hi) in WINDOWS.items():
            tw = window(t, lo, hi)
            out = recycle(tw, rules, policy=Policy.LOCK_FIRST)
            tl = pd.DataFrame(out["timeline"])
            p, b = (tl.event == "passed").sum(), (tl.event == "combine_bust").sum()
            nets = flips(tw, rules)
            line = (f"  {wname}: net ${out['net']:,.0f}  withdrawn ${out['cash']:,.0f}  spent ${out['cost']:,.0f}  "
                    f"pass {p / max(1, p + b):.1%}  payouts {out['payouts']}  dry {out['longest_dry_days']:,.0f} d  "
                    f"| flip median ${np.median(nets):,.0f}  95th ${np.percentile(nets, 95):,.0f}  "
                    f"beats {np.mean(nets < out['net']):.0%}")
            print(line, flush=True)
            res[(firm, wname)] = (out["net"], float(np.percentile(nets, 95)))
            if wname == "2016-2026":
                med, worst, n = worst_start(tw, rules)
                print(f"  deepest cash dip over {n} monthly starts: median ${med:,.0f}  worst ${worst:,.0f}", flush=True)
                res[(firm, "worst")] = worst
                print("  cost lines: " + ", ".join(f"{k} ${v:,.0f}" for k, v in out["cost_lines"].items()
                                                   if k not in ("total",) and isinstance(v, float)))
    ln, lq = res[("LucidFlex 50K", "2016-2026")]
    tn = res[("Topstep 50K", "2016-2026")][0]
    l_eff = ln / abs(res[("LucidFlex 50K", "worst")])
    t_eff = tn / abs(res[("Topstep 50K", "worst")])
    a, bcond = ln > lq, l_eff >= t_eff
    print("\n=== VERDICT (pre-registered)")
    print(f"  (a) Lucid net ${ln:,.0f} vs its coin-flip 95th pct ${lq:,.0f}: {'yes' if a else 'no'}")
    print(f"  (b) net per $ of worst dip: Lucid {l_eff:.1f} vs Topstep {t_eff:.1f}: {'yes' if bcond else 'no'}")
    print(f"  -> {'PASS' if a and bcond else 'fail'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

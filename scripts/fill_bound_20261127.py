"""Fill bound without money (docs/PREREG_FILL_BOUND_20261127.md): Topstep 50K Consistency, orders on time, pessimistic fills.

    uv run python -m scripts.fill_bound_20261127 | tee docs/jx_runs/fill_bound_20261127.txt
"""
import contextlib
import dataclasses as dc
import io

import numpy as np
import pandas as pd

from backtest.engine import BacktestConfig, simulate
from backtest.recycle import Policy, recycle
from ict import data as D
from scripts.firms2_20261120 import worst_dip
from scripts.radar_price import flip

with contextlib.redirect_stdout(io.StringIO()):
    from scripts.portfolio_my_20261123 import P

R = dc.replace
LO, HI = "2016-01-01", "2026-10-29"
rules = P["Topstep 50K Consistency path"][0]
pol = Policy.IMMEDIATE if rules.mll_locks_at is None else Policy.LOCK_FIRST
bars = D.load("1m")
orders = pd.read_parquet(D.PROCESSED_DIR / "ideas_orders_NQ.parquet")
base = BacktestConfig(risk_per_trade_usd=900)


def tr(cfg):
    t = simulate(orders, bars, cfg)
    t = t[t["filled"]]
    t = t[(t.entry_ts >= pd.Timestamp(LO, tz="UTC")) & (t.entry_ts < pd.Timestamp(HI, tz="UTC"))]
    return t.sort_values("exit_ts").reset_index(drop=True)


def starts(t):
    entry = pd.DatetimeIndex(t["entry_ts"])
    worst, s0 = [], pd.Timestamp("2016-01-01", tz=entry.tz)
    while s0 <= pd.Timestamp("2025-10-01", tz=entry.tz):
        ch = t[entry >= s0].reset_index(drop=True)
        tl = pd.DataFrame(recycle(ch, rules, policy=pol)["timeline"])
        worst.append(np.concatenate([[0.0], tl["net"].to_numpy()]).min())
        s0 += pd.DateOffset(months=1)
    return pd.Series(worst)


variants = [
    ("1 baseline: touch fills, stop slips 1 tick", base),
    ("2 entry needs price 1 tick through", R(base, entry_fill_mode="through")),
    ("3 stops slip 2 ticks", R(base, exit_slippage_ticks=2.0)),
    ("4 = 2 + 3 (PASS/FAIL row)", R(base, entry_fill_mode="through", exit_slippage_ticks=2.0)),
    ("5 = 2 + stops slip 3 ticks (reported only)", R(base, entry_fill_mode="through", exit_slippage_ticks=3.0)),
]
print("Topstep 50K Consistency, real-time loss limit, $900 risk, $1.24 round trip, orders ON TIME, 2016-01..2026-10.")
print("Coin flip: 200 runs, seed 1, random sign, commission kept, excursions swapped (radar_price.flip).\n")
res = {}
for label, cfg in variants:
    t = tr(cfg)
    out = recycle(t, rules, policy=pol)
    g, comm = t["gross_pnl"].to_numpy(), (t["gross_pnl"] - t["net_pnl"]).to_numpy()
    rng = np.random.default_rng(1)
    flips = np.array([recycle(flip(t, g, comm, rng.choice([-1, 1], len(t))), rules, policy=pol)["net"] for _ in range(200)])
    w = starts(t)
    res[label] = (t, out, flips)
    print(f"{label}\n   trades {len(t):,} | net ${out['net']:>8,.0f} ({out['payouts']} payouts) | worst dip ${worst_dip(out):,.0f} | "
          f"coin-flip median ${np.median(flips):,.0f} ({np.mean(flips > 0):.0%} positive) | start money: median ${w.median():,.0f}, "
          f"1 in 10 ${w.quantile(.10):,.0f}, worst ${w.min():,.0f}")

n1, n2 = len(res[variants[0][0]][0]), len(res[variants[1][0]][0])
print(f"\nTouch-only fills (filled on touch, not when 1 tick through is required): {n1 - n2:,} of {n1:,} = {(n1 - n2) / n1:.1%}")
_, o4, f4 = res[variants[3][0]]
ok = o4["net"] > 0 and np.median(f4) >= 5000
print(f"\nVERDICT (variant 4: net > $0 and coin-flip median >= $5,000): {'PASS' if ok else 'FAIL'} "
      f"(net ${o4['net']:,.0f}, coin-flip median ${np.median(f4):,.0f})")

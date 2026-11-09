"""Which Topstep account size and payout path earns most per account slot?

    uv run python scripts/account_size_test.py

Topstep allows five funded accounts at once, so earnings per account is the
scaling limit. Risk is kept at the same fraction of the loss limit as the
50K plan ($900 / $2,000 = 0.45).

Rules: Topstep help centre / pricing page, read 2026-11-09:
  sizes 50K/100K/150K: target 3,000/6,000/9,000, MLL 2,000/3,000/4,500,
  50/100/150 micros, monthly $49/$99/$149 (reset assumed = monthly), $149
  activation. Payout caps Standard $2,000/$3,000/$5,000, Consistency
  $3,000/$4,000/$6,000 (50% of balance). Consistency path: 3 days, 40% target.
Assumed, not read: the funded scaling ladder for 100K/150K (50K ladder x2/x3);
a $150 winning day at every size.
"""

from __future__ import annotations

import dataclasses
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, "scripts")
from backtest.engine import BacktestConfig, simulate  # noqa: E402
from backtest.recycle import Policy, XFARules, recycle  # noqa: E402
from ict import data as D  # noqa: E402

WINDOWS = {"2016-2026": ("2016-01-01", "2026-10-29"), "2010-2015": ("2010-07-01", "2016-01-01")}
SIZES = {
    "50K": dict(profit_target=3000, loss_limit=2000, funded_loss_limit=2000, mll_locks_at=2000,
                combine_max_contracts=50, monthly=49, reset=49, scaling_mult=1),
    "100K": dict(profit_target=6000, loss_limit=3000, funded_loss_limit=3000, mll_locks_at=3000,
                 combine_max_contracts=100, monthly=99, reset=99, scaling_mult=2),
    "150K": dict(profit_target=9000, loss_limit=4500, funded_loss_limit=4500, mll_locks_at=4500,
                 combine_max_contracts=150, monthly=149, reset=149, scaling_mult=3),
}
CAPS = {"50K": (2000, 3000), "100K": (3000, 4000), "150K": (5000, 6000)}


def window(t, lo, hi):
    t = t[(t["entry_ts"] >= pd.Timestamp(lo, tz="UTC")) & (t["entry_ts"] < pd.Timestamp(hi, tz="UTC"))]
    return t.sort_values("exit_ts").reset_index(drop=True)


def main() -> int:
    bars = D.load("1m")
    orders = pd.read_parquet(D.PROCESSED_DIR / "ideas_orders_NQ.parquet")
    print("size  path         window      risk   net        flip med   margin     deepest   payouts  pass")
    for size, kw in SIZES.items():
        risk = 0.45 * kw["loss_limit"]
        t = simulate(orders, bars, BacktestConfig(risk_per_trade_usd=risk))
        t = t[t["filled"]].sort_values("exit_ts").reset_index(drop=True)
        for path, cap, cons in (("Standard", CAPS[size][0], None), ("Consistency", CAPS[size][1], 0.40)):
            rules = dataclasses.replace(XFARules(), payout_cap=cap, consistency_target=cons, **kw)
            for wname, (lo, hi) in WINDOWS.items():
                tw = window(t, lo, hi)
                out = recycle(tw, rules, policy=Policy.LOCK_FIRST)
                tl = pd.DataFrame(out["timeline"])
                deepest = min(0.0, float(tl["net"].min()))
                p, b = (tl.event == "passed").sum(), (tl.event == "combine_bust").sum()
                g = tw["gross_pnl"].to_numpy()
                comm = (tw["gross_pnl"] - tw["net_pnl"]).to_numpy()
                rng = np.random.default_rng(1)
                med = float(np.median([recycle(tw.assign(net_pnl=np.abs(g) * rng.choice([-1, 1], len(tw)) - comm),
                                               rules, policy=Policy.LOCK_FIRST)["net"] for _ in range(100)]))
                print(f"{size:<5} {path:<12} {wname:<10} {risk:>6,.0f}  ${out['net']:>9,.0f}  ${med:>9,.0f}  "
                      f"${out['net'] - med:>9,.0f}  ${deepest:>8,.0f}  {out['payouts']:>6}  {p / max(1, p + b):5.1%}",
                      flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Topstep cost-structure tests, as docs/PREREG_20261120.md Part B defines them.

    uv run python scripts/topstep_costs_20261120.py
"""

from __future__ import annotations

import dataclasses
import sys

import pandas as pd

sys.path.insert(0, "scripts")
from account_size_test import CAPS, SIZES  # noqa: E402
from backtest.engine import BacktestConfig, simulate  # noqa: E402
from backtest.recycle import Policy, XFARules, recycle  # noqa: E402
from ict import data as D  # noqa: E402

WINDOWS = {"2016-2026": ("2016-01-01", "2026-10-29"), "2010-2015": ("2010-07-01", "2016-01-01")}


def window(t, lo, hi):
    t = t[(t["entry_ts"] >= pd.Timestamp(lo, tz="UTC")) & (t["entry_ts"] < pd.Timestamp(hi, tz="UTC"))]
    return t.sort_values("exit_ts").reset_index(drop=True)


def summary(t, rules):
    out = recycle(t, rules, policy=Policy.LOCK_FIRST)
    tl = pd.DataFrame(out["timeline"])
    return out, min(0.0, float(tl["net"].min()))


def main() -> int:
    bars = D.load("1m")
    orders = pd.read_parquet(D.PROCESSED_DIR / "ideas_orders_NQ.parquet")
    t900 = simulate(orders, bars, BacktestConfig(risk_per_trade_usd=900.0))
    t900 = t900[t900["filled"]].sort_values("exit_ts").reset_index(drop=True)

    print("P1/P2  Back2Funded, NQ 50K, $900, LOCK_FIRST")
    print(f"  {'variant':<22}{'window':<11}{'net':>10}{'withdrawn':>11}{'spent':>9}{'b2f':>5}"
          f"{'payouts':>8}{'deepest':>10}")
    res = {}
    for name, mx in (("never (baseline)", 0), ("P1 always (max 2)", 2), ("P2 once (max 1)", 1)):
        rules = dataclasses.replace(XFARules(), back2funded_max=mx)
        for wname, (lo, hi) in WINDOWS.items():
            out, deep = summary(window(t900, lo, hi), rules)
            res[(name, wname)] = (out["net"], deep)
            print(f"  {name:<22}{wname:<11}${out['net']:>9,.0f}${out['cash']:>10,.0f}${out['cost']:>8,.0f}"
                  f"{out.get('reactivations', 0):>5}{out['payouts']:>8}${deep:>9,.0f}")
    print("\n  VERDICTS (net higher in both windows, deepest no worse by > $500)")
    for name in ("P1 always (max 2)", "P2 once (max 1)"):
        ok = all(res[(name, w)][0] > res[("never (baseline)", w)][0] and
                 res[(name, w)][1] >= res[("never (baseline)", w)][1] - 500 for w in WINDOWS)
        print(f"  {name:<22} {'PASS' if ok else 'fail'}")

    print("\nP3  doubled payout caps (limited-time DLL offer), Standard path, descriptive")
    print(f"  {'size':<6}{'window':<11}{'normal cap':>12}{'net':>10}{'doubled cap':>13}{'net':>10}{'diff':>9}")
    for size, kw in SIZES.items():
        risk = 0.45 * kw["loss_limit"]
        t = simulate(orders, bars, BacktestConfig(risk_per_trade_usd=risk))
        t = t[t["filled"]].sort_values("exit_ts").reset_index(drop=True)
        cap = CAPS[size][0]
        for wname, (lo, hi) in WINDOWS.items():
            tw = window(t, lo, hi)
            a = recycle(tw, dataclasses.replace(XFARules(), payout_cap=cap, **kw), policy=Policy.LOCK_FIRST)["net"]
            b = recycle(tw, dataclasses.replace(XFARules(), payout_cap=2 * cap, **kw), policy=Policy.LOCK_FIRST)["net"]
            print(f"  {size:<6}{wname:<11}${cap:>11,}${a:>9,.0f}${2 * cap:>12,}${b:>9,.0f}${b - a:>8,.0f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

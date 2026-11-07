"""Addendum A of docs/HOLDOUT_PREREG.md: the seven registry strategies on 2010-07..2015-12.

    uv run python scripts/holdout_registry.py
"""
from __future__ import annotations
import sys
import pandas as pd
sys.path.insert(0, "scripts")
from compare_strategies import run_period
from backtest.engine import BacktestConfig
from ict import data as D

RISK = 500.0
FEE_TODAY = 0.018


def pf(x):
    return x[x > 0].sum() / -x[x < 0].sum() if (x < 0).any() else float("inf")


def main() -> int:
    df5, df1 = D.load("5m"), D.load("1m")
    out = run_period(df5, df1, "2010-07-01", "2016-01-01", BacktestConfig(risk_per_trade_usd=RISK))
    print(f"{'strategy':<18}{'trades':>7}{'win%':>7}{'net $':>11}{'net PF':>8}{'gross PF':>9}"
          f"{'PF@1.8%':>9}  verdict")
    for name, r in out["results"].items():
        t = r["trades"]
        t = t[t["filled"]] if "filled" in t else t
        if t.empty:
            print(f"{name:<18} no trades"); continue
        net, gross = t["net_pnl"], t["gross_pnl"]
        adj = gross - FEE_TODAY * RISK
        ok = pf(net) > 1 and pf(adj) > 1
        tag = " (unreliable: Asian session thin pre-2013)" if name == "po3_judas" else ""
        if name == "_portfolio":
            tag = " (combined, context)"
        print(f"{name:<18}{len(t):>7}{(net > 0).mean():>7.1%}{net.sum():>11,.0f}{pf(net):>8.3f}"
              f"{pf(gross):>9.3f}{pf(adj):>9.3f}  {'PASS' if ok and not name.startswith('_') else ('-' if name.startswith('_') else 'fail')}{tag}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

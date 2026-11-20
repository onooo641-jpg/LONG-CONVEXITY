"""Staggered account starts and corrected platform costs (docs/PREREG_PORTFOLIO2_20261120.md).

    uv run python scripts/portfolio2_20261120.py
"""
from __future__ import annotations

import dataclasses

import numpy as np
import pandas as pd

from backtest.engine import BacktestConfig, simulate
from backtest.recycle import XFARules
from ict import data as D
from scripts.portfolio_20261120 import DAYS, HI, LO, daily_from_recycle, stats
from scripts.round3_20261120 import MFFU
from scripts.structure_scan_20261120 import lucidflex

PROJECTX, CROSSTRADE = 14.50, 49.0
RULES = {"Topstep": dataclasses.replace(XFARules(), api_monthly=0.0),
         "Lucid": dataclasses.replace(lucidflex(50), api_monthly=0.0),
         "MFFU": dataclasses.replace(MFFU, api_monthly=0.0)}


def slot(t, firm, start):
    """Daily net of one account pipeline that starts trading on ``start``."""
    s = t[t.entry_ts >= pd.Timestamp(start, tz="UTC")].reset_index(drop=True)
    d, _ = daily_from_recycle(s, RULES[firm])
    return d.where(DAYS >= pd.Timestamp(start, tz="UTC"), 0.0)


def platform_costs(firms):
    months = np.floor((DAYS - DAYS[0]).days / 30.4375) + 1
    per_month = (PROJECTX if "Topstep" in firms else 0.0) + (CROSSTRADE if {"Lucid", "MFFU"} & set(firms) else 0.0)
    return pd.Series(months * per_month, index=DAYS)


def main() -> int:
    bars = D.load("1m")
    orders = pd.read_parquet(D.PROCESSED_DIR / "ideas_orders_NQ.parquet")
    t = simulate(orders, bars, BacktestConfig(risk_per_trade_usd=900))
    t = t[t["filled"]]
    t = t[(t.entry_ts >= pd.Timestamp(LO, tz="UTC")) & (t.entry_ts < pd.Timestamp(HI, tz="UTC"))]
    t = t.sort_values("exit_ts").reset_index(drop=True)
    cache = {}

    def get(firm, start):
        if (firm, start) not in cache:
            cache[(firm, start)] = slot(t, firm, start)
        return cache[(firm, start)]

    m = lambda k: (pd.Timestamp(LO) + pd.DateOffset(months=k)).strftime("%Y-%m-%d")
    ports = {
        "A    Topstep x1": [("Topstep", m(0))],
        "B-c  Topstep+Lucid+MFFU x1, corrected costs": [("Topstep", m(0)), ("Lucid", m(0)), ("MFFU", m(0))],
        "C-sync 5T/5L/3M same start": [("Topstep", m(2))] * 5 + [("Lucid", m(2))] * 5 + [("MFFU", m(1))] * 3,
        "C-stag 5T/5L/3M monthly stagger": [("Topstep", m(k)) for k in range(5)] + [("Lucid", m(k)) for k in range(5)]
                                           + [("MFFU", m(k)) for k in range(3)],
    }
    yearly, res = {}, {}
    for name, slots in ports.items():
        s = sum(get(f, st) for f, st in slots) - platform_costs({f for f, _ in slots})
        yearly[name.split()[0]] = stats(name, s)
        peak = s.cummax().clip(lower=0)
        res[name.split()[0]] = (s.iloc[-1], max(-(s - peak).min(), -min(0.0, s.min())))
    print("\nyearly income:")
    print(pd.DataFrame(yearly).to_string(float_format=lambda x: f"{x:,.0f}"))
    (ns, cs), (nt, ct) = res["C-sync"], res["C-stag"]
    print(f"\nstagger vs sync: net {nt / ns - 1:+.1%}, cash on hand {ct / cs - 1:+.1%} -> "
          f"{'WORTH DOING' if ct <= 0.85 * cs and abs(nt / ns - 1) <= 0.05 else 'equivalent / not worth it'} (pre-registered rule)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

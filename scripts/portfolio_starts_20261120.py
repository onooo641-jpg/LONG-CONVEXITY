"""Start-date test for portfolios A and B- (docs/PREREG_PORTFOLIO_20261120.md, addendum).

    uv run python scripts/portfolio_starts_20261120.py
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from backtest.engine import BacktestConfig, simulate
from backtest.recycle import Policy, XFARules, _months, recycle
from ict import data as D
from scripts.round3_20261120 import MFFU
from scripts.structure_scan_20261120 import lucidflex

LO, HI = "2016-01-01", "2026-10-29"
FIRMS = {"Topstep": XFARules(), "Lucid": lucidflex(50), "MFFU": MFFU}


def year_one(t, rules, start):
    end = start + pd.DateOffset(months=12)
    s = t[(t.entry_ts >= start) & (t.exit_ts < end)].reset_index(drop=True)
    out = recycle(s, rules, policy=Policy.LOCK_FIRST)
    tl = pd.DataFrame(out["timeline"])
    per_month = rules.monthly + rules.api_monthly
    days = pd.date_range(start, end - pd.Timedelta(days=1), freq="D")
    first = s.entry_ts.iloc[0]
    m_at = tl.ts.map(lambda ts: _months((ts - first).total_seconds() / 86400))
    tl["base"] = tl.cost - m_at * per_month
    x = tl.set_index(tl.ts.dt.floor("D"))[["cash", "base"]].groupby(level=0).last().reindex(days).ffill()
    x = x.fillna({"cash": 0.0, "base": float(tl.base.iloc[0]) if len(tl) else 0.0})
    months = np.array([_months(max(0.0, (d - first).total_seconds() / 86400)) for d in days])
    return x.cash - (x.base + months * per_month)


def main() -> int:
    bars = D.load("1m")
    orders = pd.read_parquet(D.PROCESSED_DIR / "ideas_orders_NQ.parquet")
    t = simulate(orders, bars, BacktestConfig(risk_per_trade_usd=900))
    t = t[t["filled"]]
    t = t[(t.entry_ts >= pd.Timestamp(LO, tz="UTC")) & (t.entry_ts < pd.Timestamp(HI, tz="UTC"))]
    t = t.sort_values("exit_ts").reset_index(drop=True)
    rows = []
    for start in pd.date_range("2016-01-01", "2025-10-01", freq="MS", tz="UTC"):
        paths = {f: year_one(t, r, start) for f, r in FIRMS.items()}
        for name, firms in (("A", ["Topstep"]), ("B-", list(FIRMS))):
            s = sum(paths[f] for f in firms)
            rows.append({"port": name, "start": start, "net": s.iloc[-1],
                         "dip": float((s - s.cummax().clip(lower=0)).min()), "pocket": float(min(0.0, s.min()))})
    r = pd.DataFrame(rows)
    for name, g in r.groupby("port", sort=False):
        print(f"{name:<3} year-one net: median ${g.net.median():>8,.0f}, 10th pct ${g.net.quantile(.1):>8,.0f}, "
              f"90th pct ${g.net.quantile(.9):>8,.0f}, starts losing money {(g.net < 0).mean():.0%} | "
              f"worst dip median ${g.dip.median():>7,.0f}, 10th pct ${g.dip.quantile(.1):>7,.0f} | "
              f"out of pocket median ${g.pocket.median():>7,.0f}, 10th pct ${g.pocket.quantile(.1):>7,.0f}, worst ${g.pocket.min():>7,.0f}")
        by = g.groupby(g.start.dt.year).net.median()
        print("    median year-one net by start year: " + ", ".join(f"{y} ${v:,.0f}" for y, v in by.items()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Multi-firm portfolio on the same trades (docs/PREREG_PORTFOLIO_20261120.md).

    uv run python scripts/portfolio_20261120.py
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from backtest.engine import BacktestConfig, simulate
from backtest.recycle import Policy, XFARules, _months, recycle
from ict import data as D
from scripts.global_round1_20261120 import BREAKOUT, DAILY, MIN_GROSS, SPLIT
from scripts.round3_20261120 import MFFU
from scripts.structure_scan_20261120 import lucidflex

LO, HI = "2016-01-01", "2026-10-29"
DAYS = pd.date_range(LO, HI, freq="D", tz="UTC")


def daily_from_recycle(t, rules):
    out = recycle(t, rules, policy=Policy.LOCK_FIRST)
    tl = pd.DataFrame(out["timeline"])
    first = t.entry_ts.iloc[0]
    per_month = rules.monthly + rules.api_monthly
    m_at = tl.ts.map(lambda ts: _months((ts - first).total_seconds() / 86400))
    tl["base"] = tl.cost - m_at * per_month             # one-off costs so far
    s = tl.set_index(tl.ts.dt.floor("D"))[["cash", "base"]].groupby(level=0).last()
    s = s.reindex(DAYS).ffill().fillna(0.0)
    months = np.array([_months(max(0.0, (d - first).total_seconds() / 86400)) if d >= first.floor("D") else 0
                       for d in DAYS])
    return s.cash - (s.base + months * per_month), out["net"]


def daily_breakout(t, lev=10, refund=False):
    fee, target, maxl = BREAKOUT["Classic"]
    notional = t["contracts"] * t["entry_price"] * 2.0
    k = np.minimum(1.0, lev * 50_000 / notional).to_numpy()
    pnl = t.net_pnl.to_numpy() * k
    spent, paid, bal, phase, due = fee, 0.0, 0.0, 0, False
    path = []
    for p in pnl:
        bal += p
        if bal <= -maxl or p <= -DAILY:
            spent += fee
            bal, phase, due = 0.0, 0, False
        elif phase == 0 and bal >= target:
            phase, bal, due = 1, 0.0, refund
        elif phase == 1 and bal >= MIN_GROSS:
            paid += SPLIT * bal + (fee if due else 0.0)
            bal, due = 0.0, False
        path.append(paid - spent)
    s = pd.Series(path, index=t.exit_ts.dt.floor("D")).groupby(level=0).last()
    s = s.reindex(DAYS).ffill().fillna(-fee)
    return s, path[-1]


def stats(name, s):
    peak = s.cummax().clip(lower=0)
    dip = float((s - peak).min())
    pocket = float(min(0.0, s.min()))
    below = (s < peak)
    run = longest = 0
    for b in below:
        run = run + 1 if b else 0
        longest = max(longest, run)
    yearly = s.groupby(s.index.year).last().diff()
    yearly.iloc[0] = s.groupby(s.index.year).last().iloc[0]
    yrs = len(s) / 365.25
    h1 = s[s.index.year <= 2020].iloc[-1]
    h2 = s.iloc[-1] - h1
    cash = max(-dip, -pocket)
    print(f"{name:<44} net ${s.iloc[-1]:>9,.0f} (${s.iloc[-1] / yrs:>7,.0f}/yr) | 2016-20 ${h1:>9,.0f}, 2021-26 ${h2:>9,.0f} | "
          f"worst dip ${dip:>9,.0f} | most out of pocket ${pocket:>8,.0f} | cash on hand ${cash:>8,.0f} | "
          f"longest below peak {longest / 30.4:4.1f} mo | losing years {(yearly < 0).sum()}")
    return yearly


def build(t9, t95):
    parts = {"Topstep": daily_from_recycle(t9, XFARules()), "Lucid": daily_from_recycle(t9, lucidflex(50)),
             "MFFU": daily_from_recycle(t9, MFFU), "Breakout": daily_breakout(t95)}
    return {k: v[0] for k, v in parts.items()}, {k: v[1] for k, v in parts.items()}


def main() -> int:
    bars = D.load("1m")
    orders = pd.read_parquet(D.PROCESSED_DIR / "ideas_orders_NQ.parquet")

    def trades(risk):
        t = simulate(orders, bars, BacktestConfig(risk_per_trade_usd=risk))
        t = t[t["filled"]]
        t = t[(t.entry_ts >= pd.Timestamp(LO, tz="UTC")) & (t.entry_ts < pd.Timestamp(HI, tz="UTC"))]
        return t.sort_values("exit_ts").reset_index(drop=True)

    t9, t95 = trades(900), trades(950)
    d, totals = build(t9, t95)
    print("single-slot totals (check vs earlier runs): " + ", ".join(f"{k} ${v:,.0f}" for k, v in totals.items()) + "\n")
    ports = {
        "A  Topstep x1": {"Topstep": 1},
        "B  one slot each (4 firms)": {"Topstep": 1, "Lucid": 1, "MFFU": 1, "Breakout": 1},
        "B- one slot each, no Breakout": {"Topstep": 1, "Lucid": 1, "MFFU": 1},
        "C  max slots (5 Topstep, 5 Lucid, 3 MFFU, 1 BO)": {"Topstep": 5, "Lucid": 5, "MFFU": 3, "Breakout": 1},
        "C- max slots, no Breakout": {"Topstep": 5, "Lucid": 5, "MFFU": 3},
    }
    yearly = {}
    for name, w in ports.items():
        yearly[name.split()[0]] = stats(name, sum(n * d[f] for f, n in w.items()))
    print("\nyearly income by portfolio:")
    print(pd.DataFrame(yearly).to_string(float_format=lambda x: f"{x:,.0f}"))
    corr = pd.DataFrame({f: d[f].resample("ME").last().diff() for f in d}).corr()
    print("\nmonthly P&L correlation between firms:\n" + corr.to_string(float_format=lambda x: f"{x:.2f}"))

    # coin flip on portfolio B: one sign per trade, shared by every firm
    rng = np.random.default_rng(1)
    key = lambda t: t.entry_ts.astype("int64").to_numpy()
    nets, dips = [], []
    for _ in range(200):
        signs = dict(zip(key(t9), rng.choice([-1, 1], len(t9))))
        f9 = t9.assign(net_pnl=np.abs(t9.gross_pnl) * np.array([signs[k] for k in key(t9)]) - (t9.gross_pnl - t9.net_pnl))
        s95 = np.array([signs.get(k, rng.choice([-1, 1])) for k in key(t95)])
        f95 = t95.assign(net_pnl=np.abs(t95.gross_pnl) * s95 - (t95.gross_pnl - t95.net_pnl))
        dd, _ = build(f9, f95)
        s = sum(dd.values())
        nets.append(s.iloc[-1]); dips.append(float((s - s.cummax().clip(lower=0)).min()))
    nets, dips = np.array(nets), np.array(dips)
    print(f"\ncoin flip, portfolio B: median net ${np.median(nets):,.0f}, profitable {(nets > 0).mean():.0%}, "
          f"5th-pct net ${np.percentile(nets, 5):,.0f}, median worst dip ${np.median(dips):,.0f}, "
          f"5th-pct worst dip ${np.percentile(dips, 5):,.0f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

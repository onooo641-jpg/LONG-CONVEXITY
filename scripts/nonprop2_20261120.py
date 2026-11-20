"""Non-prop round 2 (docs/PREREG_NONPROP2_20261120.md): #57 funding carry, #58 strategy on own money.

    uv run python scripts/nonprop2_20261120.py
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from backtest.engine import BacktestConfig, simulate
from ict import data as D

TARGET = 4098.0
COST = 0.0025


def carry():
    f = pd.read_parquet("data/public/hl_funding.parquet")
    coins = pd.read_parquet("data/public/hl_baseline_coins.parquet").coin.tolist()
    f = f[f.coin.isin(coins)].copy()
    f["t"] = pd.to_datetime(f.time, unit="ms", utc=True).dt.floor("h")
    h = f.pivot_table(index="t", columns="coin", values="rate", aggfunc="mean").sort_index()
    weeks = pd.date_range(h.index[0].ceil("D") + pd.Timedelta(days=7 - h.index[0].ceil("D").weekday()),
                          h.index[-1], freq="7D", tz="UTC")
    rows, held = [], set()
    for a, b in zip(weeks[:-1], weeks[1:]):
        trail = h.loc[a - pd.Timedelta(days=7):a - pd.Timedelta(hours=1)].mean()
        pick = [c for c in trail[trail > 0].sort_values(ascending=False).index[:3]]
        nxt = h.loc[a:b - pd.Timedelta(hours=1)].sum()          # funding earned per $1 short
        earn = sum(nxt[c] for c in pick) / 3                     # equal weight, empty slots in cash
        turnover = (len(set(pick) ^ held)) / 3                   # coins entered or exited, per slot
        held = set(pick)
        bb = (nxt["BTC"] + nxt["ETH"]) / 2
        rows.append({"week": a, "rot": earn - COST * turnover, "ctl": bb, "n": len(pick)})
    r = pd.DataFrame(rows)
    r.loc[0, "ctl"] -= COST                                      # control enters once...
    r.loc[len(r) - 1, "ctl"] -= COST                             # ...and exits once
    yrs = (r.week.iloc[-1] - r.week.iloc[0]).days / 365.25 + 7 / 365.25
    mid = r.week.iloc[len(r) // 2]
    for col, name in (("rot", "rotating top-3"), ("ctl", "BTC+ETH hold")):
        notional_ret = r[col].sum() / yrs                        # per $1 notional per year
        cap_ret = notional_ret / 2                               # capital = 2 x notional
        h1 = r.loc[r.week < mid, col].sum(); h2 = r.loc[r.week >= mid, col].sum()
        need = TARGET / cap_ret if cap_ret > 0 else float("inf")
        print(f"#57 {name:<16} return on capital {cap_ret:6.1%}/yr | halves {h1 / 2:+.1%} / {h2 / 2:+.1%} "
              f"(on capital, whole half) | worst week {r[col].min() / 2:+.2%} | capital to make ${TARGET:,.0f}/yr: "
              f"${need:,.0f}" + (f" | weeks fully invested {(r.n == 3).mean():.0%}" if col == "rot" else ""))
    yr = r.assign(y=r.week.dt.year).groupby("y")[["rot", "ctl"]].sum() / 2
    print("#57 by calendar year (return on capital, partial years as-is):\n" + yr.to_string(float_format=lambda x: f"{x:+.1%}"))


def own_money():
    bars = D.load("1m")
    orders = pd.read_parquet(D.PROCESSED_DIR / "ideas_orders_NQ.parquet")
    t = simulate(orders, bars, BacktestConfig(risk_per_trade_usd=900))
    t = t[t["filled"]]
    t = t[(t.entry_ts >= pd.Timestamp("2016-01-01", tz="UTC")) & (t.entry_ts < pd.Timestamp("2026-10-29", tz="UTC"))]
    t = t.sort_values("exit_ts").reset_index(drop=True)
    eq = t.net_pnl.cumsum()
    dd = float((eq - eq.cummax()).min())
    yrs = (t.exit_ts.iloc[-1] - t.exit_ts.iloc[0]).days / 365.25
    per = t.net_pnl.sum() / yrs
    cap = -dd / 0.25
    by = t.groupby(t.exit_ts.dt.year).net_pnl.sum()
    h1 = t[t.exit_ts.dt.year <= 2020].net_pnl.sum(); h2 = t[t.exit_ts.dt.year >= 2021].net_pnl.sum()
    print(f"#58 own money, $900 risk: {len(t)} trades, net ${t.net_pnl.sum():,.0f} (${per:,.0f}/yr), max drawdown ${dd:,.0f}, "
          f"worst year ${by.min():,.0f}, halves 2016-20 ${h1:,.0f} / 2021-26 ${h2:,.0f}")
    print(f"#58 capital for max DD = 25%: ${cap:,.0f}; return on it {per / cap:.1%}/yr; "
          f"capital to make ${TARGET:,.0f}/yr at that sizing: ${TARGET / (per / cap):,.0f}")
    print("#58 by year: " + ", ".join(f"{y} ${v:,.0f}" for y, v in by.items()))


if __name__ == "__main__":
    carry()
    own_money()

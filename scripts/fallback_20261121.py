"""Non-prop fallback tests (docs/PREREG_FALLBACK_20261121.md): #204 stable yield rotation, #205 Hyperliquid HLP vault.

    uv run python scripts/fallback_20261121.py | tee docs/jx_runs/fallback_20261121.txt
"""
from __future__ import annotations

import sys

import numpy as np
import pandas as pd

LO, HI = pd.Timestamp("2024-11-01", tz="UTC"), pd.Timestamp("2026-11-01", tz="UTC")
MID = pd.Timestamp("2025-11-01", tz="UTC")
PILOT = pd.Timestamp("2026-08-01", tz="UTC")
BAR, KILL, SIZE, FEE, TOPK, STRESS = 8.0, 4.0, 10_000, 5.0, 5, 0.20
AAVE_USDC_ETH = "aa70268e-4b52-42bf-a116-608b370f9501"


def ann(r):  # mean daily simple return -> %/yr
    return float(r.mean() * 365 * 100) if len(r) else float("nan")


def rotation():
    ch = pd.read_parquet("data/public/fallback_stable_charts.parquet")
    ch["day"] = ch["ts"].dt.floor("D")
    ch = ch.drop_duplicates(["pool", "day"])
    ch["y"] = ch["apyBase"].fillna(0) + 0.9 * ch["apyReward"].fillna(0)
    ch["y"] = ch["y"].clip(upper=1000)
    y = ch.pivot(index="day", columns="pool", values="y").sort_index()
    tvl = ch.pivot(index="day", columns="pool", values="tvlUsd").sort_index().ffill(limit=3)
    first = ch.groupby("pool")["day"].min()
    days = pd.date_range(LO, HI - pd.Timedelta(days=1), freq="D", tz="UTC")
    daily, held_prev, log, events = [], set(), [], 0
    for m in pd.date_range(LO, HI - pd.Timedelta(days=1), freq="MS", tz="UTC"):
        prev = m - pd.Timedelta(days=1)
        if prev not in tvl.index:
            continue
        ok = [p for p in y.columns if tvl.at[prev, p] >= 5e6 and (prev - first[p]).days >= 90]
        trail = y.loc[prev - pd.Timedelta(days=29):prev, ok].mean()
        held = list(trail.dropna().sort_values(ascending=False).index[:TOPK])
        changes = len(set(held) ^ held_prev)
        held_prev = set(held)
        mdays = [d for d in days if d.year == m.year and d.month == m.month]
        alive = {p: True for p in held}
        cost_day = changes * FEE / SIZE  # charged on the first day
        for k, d in enumerate(mdays):
            r = []
            for p in held:
                if not alive[p]:
                    r.append(0.0)
                    continue
                t7 = tvl.loc[d - pd.Timedelta(days=7):d, p]
                if len(t7) > 1 and t7.iloc[-1] < 0.5 * t7.max():
                    alive[p] = False
                    events += 1
                    r.append(-STRESS)
                    continue
                v = y.at[d, p] if d in y.index else np.nan
                r.append((v if pd.notna(v) else 0.0) / 100 / 365)
            daily.append((d, float(np.mean(r)) - (cost_day if k == 0 else 0.0)))
        log.append(f"  {m:%Y-%m}: " + ", ".join(f"{p[:8]} {trail[p]:.1f}%" for p in held))
    s = pd.Series(dict(daily)).sort_index()
    print("#204 stablecoin yield rotation (top 5 by trailing 30-day yield, monthly)")
    pools = pd.read_parquet("data/public/fallback_stable_pools.parquet").set_index("pool")
    print(f"  universe {y.shape[1]} pools; loss-stress events {events}")
    for line in log[-3:]:
        print(line)
    pilot = ann(s[s.index >= PILOT])
    print(f"  Stage 1 (2026-08..10): {pilot:.2f}%/yr -> {'KILL' if pilot < KILL else 'continue'}")
    if pilot < KILL:
        print("  VERDICT: FAIL (Stage 1)\n")
        return
    h1, h2 = ann(s[s.index < MID]), ann(s[s.index >= MID])
    mon = s.groupby(s.index.strftime("%Y-%m")).sum() * 100
    base = y[AAVE_USDC_ETH].reindex(days).fillna(0) / 100 / 365 if AAVE_USDC_ETH in y.columns else None
    print(f"  half 1 {h1:.2f}%/yr, half 2 {h2:.2f}%/yr, whole {ann(s):.2f}%/yr; worst month {mon.min():.2f}%; months negative {(mon < 0).sum()}")
    if base is not None:
        print(f"  baseline Aave v3 USDC Ethereum: {ann(base[base.index < MID]):.2f}% / {ann(base[base.index >= MID]):.2f}%")
    print(f"  $ per year: ${ann(s) * 100:,.0f} on $10K, ${ann(s) * 400:,.0f} on $40K (Topstep slot $4,097/yr on ~$3.5K at risk)")
    held_names = sorted({pools.at[p, 'project'] for p in held_prev if p in pools.index})
    print(f"  last month's holdings (projects): {', '.join(held_names)}")
    print(f"  VERDICT: {'PASS' if h1 >= BAR and h2 >= BAR else 'FAIL (a half below ' + str(BAR) + '%/yr)'}\n")


def hlp():
    h = pd.read_parquet("data/public/fallback_hlp.parquet").dropna().sort_values("ts")
    h["day"] = h["ts"].dt.floor("D")
    h = h.groupby("day").last()
    r = (h["pnl"].diff() / h["account_value"].shift()).dropna()
    r = r[(r.index >= LO) & (r.index < HI)]
    print("#205 Hyperliquid HLP vault")
    print(f"  {len(h)} daily points {h.index.min().date()}..{h.index.max().date()}; in window {len(r)}")
    gaps = r.index.to_series().diff().dt.days.max()
    print(f"  largest gap between points: {gaps} days")
    span = lambda x: (x.index.max() - x.index.min()).days or 1  # noqa: E731
    pr = r[r.index >= PILOT]
    pilot = float(((1 + pr).prod() - 1) * 365 / span(pr) * 100) if len(pr) else float("nan")
    print(f"  Stage 1 (2026-08..10): {pilot:.2f}%/yr -> {'KILL' if pilot < KILL else 'continue'}")
    if pilot < KILL:
        print("  VERDICT: FAIL (Stage 1)\n")
        return
    a, b = r[r.index < MID], r[r.index >= MID]
    h1 = float(((1 + a).prod() - 1) * 365 / span(a) * 100)
    h2 = float(((1 + b).prod() - 1) * 365 / span(b) * 100)
    idx = (1 + r).cumprod()
    dd = float((idx / idx.cummax() - 1).min() * 100)
    mon = r.groupby(r.index.strftime("%Y-%m")).apply(lambda x: (1 + x).prod() - 1) * 100
    tot = float(((1 + r).prod() - 1) * 365 / span(r) * 100)
    print(f"  half 1 {h1:.2f}%/yr, half 2 {h2:.2f}%/yr, whole {tot:.2f}%/yr; worst drawdown {dd:.2f}%; worst month {mon.min():.2f}%; months negative {(mon < 0).sum()}")
    print(f"  $ per year: ${tot * 100:,.0f} on $10K, ${tot * 400:,.0f} on $40K")
    ok = h1 >= BAR and h2 >= BAR and dd > -15
    print(f"  VERDICT: {'PASS' if ok else 'FAIL'}\n")


def main() -> int:
    print(f"bar: net >= {BAR}%/yr in both halves (2024-11..2025-10, 2025-11..2026-10); pilot kill < {KILL}%\n")
    rotation()
    hlp()
    return 0


if __name__ == "__main__":
    sys.exit(main())

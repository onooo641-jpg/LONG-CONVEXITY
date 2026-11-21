"""Paid to borrow: same-asset stablecoin loops (docs/PREREG_BORROWLOOP_20261121.md, #209).

    uv run python scripts/borrowloop_20261121.py | tee docs/jx_runs/borrowloop_20261121.txt
"""
from __future__ import annotations

import sys

import numpy as np
import pandas as pd

LO, HI = pd.Timestamp("2024-11-01", tz="UTC"), pd.Timestamp("2026-11-01", tz="UTC")
MID, PILOT = pd.Timestamp("2025-11-01", tz="UTC"), pd.Timestamp("2026-08-01", tz="UTC")
SIZE, FEE, TOPK, STRESS, BAR, KILL, KMAX = 10_000, 20.0, 5, 0.20, 8.0, 4.0, 5.0


def main() -> int:
    pools = pd.read_parquet("data/public/borrowloop_pools.parquet").set_index("pool")
    ch = pd.read_parquet("data/public/borrowloop_charts.parquet")
    ch["day"] = pd.to_datetime(ch["day"], utc=True)
    ch = ch.drop_duplicates(["pool", "day"])
    ltv = pd.to_numeric(pools["ltv"], errors="coerce").fillna(0).clip(0, 0.95)
    k = (1 / (1 - 0.8 * ltv)).clip(upper=KMAX)
    ch["s"] = ch["apyBase"].fillna(0) + 0.9 * ch["apyReward"].fillna(0)
    ch["b"] = ch["apyBaseBorrow"].fillna(0) - 0.9 * ch["apyRewardBorrow"].fillna(0)
    ch["k"] = ch["pool"].map(k).fillna(1.0)
    ch["roe"] = (ch["s"] + (ch["k"] - 1) * (ch["s"] - ch["b"])).clip(-200, 500)
    R = ch.pivot(index="day", columns="pool", values="roe").sort_index()
    T = ch.pivot(index="day", columns="pool", values="tvlUsd").sort_index().ffill(limit=3)
    first = ch.groupby("pool")["day"].min()
    print(f"pools: {R.shape[1]}; median leverage {k.median():.2f}; days with paid-to-borrow (b < 0): "
          f"{(ch['b'] < 0).mean():.1%} of pool-days")
    days = pd.date_range(LO, HI - pd.Timedelta(days=1), freq="D", tz="UTC")
    daily, prev_held, events, log = [], set(), 0, []
    for m in pd.date_range(LO, HI - pd.Timedelta(days=1), freq="MS", tz="UTC"):
        pday = m - pd.Timedelta(days=1)
        if pday not in T.index:
            continue
        ok = [p for p in R.columns if T.at[pday, p] >= 5e6 and (pday - first[p]).days >= 90]
        trail = R.loc[pday - pd.Timedelta(days=29):pday, ok].mean().dropna().sort_values(ascending=False)
        held = list(trail.index[:TOPK])
        changes = len(set(held) ^ prev_held)
        prev_held = set(held)
        alive = {p: True for p in held}
        log.append(f"  {m:%Y-%m}: " + ", ".join(f"{pools.at[p, 'project']}/{pools.at[p, 'symbol']} {trail[p]:.1f}%" for p in held))
        for j, d in enumerate([x for x in days if x.year == m.year and x.month == m.month]):
            r = []
            for p in held:
                if not alive[p]:
                    r.append(0.0)
                    continue
                t7 = T.loc[d - pd.Timedelta(days=7):d, p]
                if len(t7) > 1 and t7.iloc[-1] < 0.5 * t7.max():
                    alive[p] = False
                    events += 1
                    r.append(-STRESS)
                    continue
                v = R.at[d, p] if d in R.index else np.nan
                r.append((v if pd.notna(v) else 0.0) / 100 / 365)
            cost = changes * FEE / SIZE if j == 0 else 0.0
            daily.append((d, (float(np.mean(r)) if r else 0.0) - cost))
    s = pd.Series(dict(daily))
    ann = lambda x: float(x.mean() * 365 * 100)  # noqa: E731
    for line in log[-3:]:
        print(line)
    pilot = ann(s[s.index >= PILOT])
    print(f"loss-stress events {events}; Stage 1 (2026-08..10): {pilot:.2f}%/yr -> {'KILL' if pilot < KILL else 'continue'}")
    if pilot < KILL:
        print("VERDICT: FAIL (Stage 1)")
        return 0
    h1, h2 = ann(s[s.index < MID]), ann(s[s.index >= MID])
    mon = s.groupby(s.index.strftime("%Y-%m")).sum() * 100
    print(f"half 1 {h1:.2f}%/yr, half 2 {h2:.2f}%/yr, whole {ann(s):.2f}%/yr on equity; worst month {mon.min():.2f}%; months negative {(mon < 0).sum()}")
    print(f"$ per year: ${ann(s) * 100:,.0f} on $10K, ${ann(s) * 400:,.0f} on $40K (Topstep slot $4,097/yr)")
    print(f"VERDICT: {'PASS' if h1 >= BAR and h2 >= BAR else 'FAIL'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

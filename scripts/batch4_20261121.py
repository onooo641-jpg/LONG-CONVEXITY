"""Batch 4 Stage 1 + Stage 2 (docs/PREREG_BATCH4_20261121.md): #220-#225, #227.

    uv run python scripts/batch4_20261121.py | tee docs/jx_runs/batch4_20261121.txt
"""
from __future__ import annotations

import sys

import numpy as np
import pandas as pd

LO, HI = pd.Timestamp("2024-11-01", tz="UTC"), pd.Timestamp("2026-11-01", tz="UTC")
MID, PILOT = pd.Timestamp("2025-11-01", tz="UTC"), pd.Timestamp("2026-08-01", tz="UTC")
BAR, KILL = 8.0, 4.0
ann = lambda x: float(x.mean() * 365 * 100)  # noqa: E731


def judge(label, s, extra=""):
    pilot = ann(s[s.index >= PILOT])
    if not np.isfinite(pilot) or pilot < KILL:
        print(f"{label}: Stage 1 (2026-08..10) {pilot:.2f}%/yr -> KILL. VERDICT: FAIL (Stage 1){extra}\n")
        return
    h1, h2 = ann(s[s.index < MID]), ann(s[s.index >= MID])
    days = (s.index.max() - s.index.min()).days
    ok = h1 >= BAR and h2 >= BAR and days >= 180
    print(f"{label}: Stage 1 {pilot:.2f}%/yr; halves {h1:.2f}% / {h2:.2f}% ({days} days); ${ann(s) * 100:,.0f}/yr on $10K{extra} -> "
          f"VERDICT: {'PASS' if ok else 'FAIL'}\n")


def rotation(Y, T, tmin, names, fee=5.0, size=10_000, k=5, stress=0.20):
    first = Y.apply(lambda c: c.first_valid_index())
    days = pd.date_range(LO, HI - pd.Timedelta(days=1), freq="D", tz="UTC")
    out, prev, hits, last = [], set(), 0, ""
    for m in pd.date_range(LO, HI - pd.Timedelta(days=1), freq="MS", tz="UTC"):
        pday = m - pd.Timedelta(days=1)
        if pday not in T.index:
            continue
        ok = [p for p in Y.columns if pd.notna(T.at[pday, p]) and T.at[pday, p] >= tmin and first[p] is not None and (pday - first[p]).days >= 90]
        trail = Y.loc[pday - pd.Timedelta(days=29):pday, ok].mean().dropna().sort_values(ascending=False)
        held = list(trail.index[:k])
        ch = len(set(held) ^ prev)
        prev = set(held)
        last = ", ".join(f"{names.get(p, p[:8])} {trail[p]:.1f}%" for p in held)
        alive = {p: True for p in held}
        for j, d in enumerate([x for x in days if x.year == m.year and x.month == m.month]):
            r = []
            for p in held:
                if not alive[p]:
                    r.append(0.0)
                    continue
                t7 = T.loc[d - pd.Timedelta(days=7):d, p]
                if len(t7) > 1 and t7.iloc[-1] < 0.5 * t7.max():
                    alive[p] = False
                    hits += 1
                    r.append(-stress)
                    continue
                v = Y.at[d, p] if d in Y.index else np.nan
                r.append((v if pd.notna(v) else 0.0) / 100 / 365)
            out.append((d, (float(np.mean(r)) if r else 0.0) - (ch * fee / size if j == 0 else 0.0)))
    return pd.Series(dict(out)), hits, last


def main() -> int:
    pools = pd.read_parquet("data/public/batch4_pools.parquet").set_index("pool")
    ch = pd.read_parquet("data/public/batch4_charts.parquet")
    ch["day"] = ch["ts"].dt.floor("D")
    ch = ch.drop_duplicates(["pool", "day"])
    ch["y"] = (ch["apyBase"].fillna(0) + 0.9 * ch["apyReward"].fillna(0)).clip(upper=500)
    names = {p: f"{pools.at[p, 'project']}/{pools.at[p, 'symbol']}" for p in pools.index}
    grp = lambda g: set(pools.index[pools["group"].astype(str).str.contains(g)])  # noqa: E731
    f = pd.read_parquet("data/public/hl_funding.parquet")
    f["day"] = pd.to_datetime(f["time"], unit="ms", utc=True).dt.floor("D")
    F = f.groupby(["coin", "day"])["rate"].sum().mul(365 * 100)
    print(f"bar {BAR}%/yr both halves; Stage 1 kill < {KILL}% (2026-08..10)\n")

    # 220 JLP hedged
    ids = grp("220")
    if not ids:
        print("#220 Jupiter JLP: not listed by DefiLlama yields; Jupiter API probe in the fetch log -> no data. VERDICT: not testable (no data)\n")
    # 221 GM hedged
    ids = grp("221")
    g = ch[ch.pool.isin(ids)].copy()
    if len(g):
        g["idx"] = g.pool.map(pools["symbol"]).str.split("-").str[0].str.replace("WETH", "ETH").str.replace("WBTC", "BTC").str.replace(".B", "", regex=False)
        g["F"] = [F.get((c, d), np.nan) for c, d in zip(g.idx, g.day)]
        g = g[g.F.notna()]
        g["h"] = (g.y + 0.5 * g.F) / (1 + 0.5 / 3)
        Y, T = g.pivot(index="day", columns="pool", values="h"), g.pivot(index="day", columns="pool", values="tvlUsd").ffill(limit=3)
        s, hits, last = rotation(Y, T, 20e6, names, fee=10.0, size=2000 * len(Y.columns) or 2000)
        judge("#221 GMX GM pools hedged", s, f"; stress hits {hits}; last holdings {last}")
    # 224 stable-pair LPs
    for gid, label, tmin in (("224", "#224 stable-pair DEX LPs (top 5 monthly)", 5e6), ("227", "#227 other savings rates (top 5 monthly)", 5e6)):
        g = ch[ch.pool.isin(grp(gid))]
        if g.empty:
            print(f"{label}: no data\n")
            continue
        Y, T = g.pivot(index="day", columns="pool", values="y"), g.pivot(index="day", columns="pool", values="tvlUsd").ffill(limit=3)
        s, hits, last = rotation(Y, T, tmin, names)
        judge(label, s, f"; {Y.shape[1]} pools; stress hits {hits}; last holdings {last}")
    # 225 trader-counterparty vaults: best-ceiling vault held + equal weight of all
    g = ch[ch.pool.isin(grp("225"))]
    if len(g):
        Y = g.pivot(index="day", columns="pool", values="y")
        now = pools.loc[list(Y.columns), "tvlUsd"]
        best = Y.iloc[-30:].mean().idxmax()
        judge(f"#225 trader-counterparty vault, best ceiling ({names[best]})", Y[best].dropna() / 100 / 365)
        judge("#225 trader-counterparty vaults, equal weight", Y.mean(axis=1).dropna() / 100 / 365, f"; {len(now)} vaults")
    # 222 MegaVault
    mv = pd.read_parquet("data/public/batch4_megavault.parquet")
    if len(mv) and {"equity", "totalPnl", "createdAt"} <= set(mv.columns):
        mv["day"] = pd.to_datetime(mv["createdAt"], utc=True).dt.floor("D")
        mv = mv.groupby("day").last().sort_index()
        eq, pnl = pd.to_numeric(mv["equity"]), pd.to_numeric(mv["totalPnl"])
        r = (pnl.diff() / eq.shift()).dropna()
        r = r[(r.index >= LO) & (r.index < HI)]
        judge("#222 dYdX MegaVault", r, f"; {len(r)} daily points")
    else:
        print(f"#222 dYdX MegaVault: data shape {list(mv.columns)[:6]} -> not testable as fetched\n")
    print("#223 Lighter LLP: see PROBE lines in the fetch log; no history endpoint fetched -> not testable (no data)\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())

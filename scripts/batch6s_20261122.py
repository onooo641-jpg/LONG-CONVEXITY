"""Batch 6 Stage 1/2 for Stage-0.5 survivors (docs/PREREG_BATCH6_20261122.md): #263, #264, #276, #278.

    uv run python scripts/batch6s_20261122.py | tee docs/jx_runs/batch6s_20261122.txt
"""
import numpy as np
import pandas as pd

LO, MID, HI, PILOT = [pd.Timestamp(x, tz="UTC") for x in ("2024-11-01", "2025-11-01", "2026-11-01", "2026-08-01")]
ann = lambda x: float(x.mean() * 365 * 100)  # noqa: E731


def verdict(lab, s):
    s = s.dropna()
    if s.empty:
        print(f"{lab}: no data -> not testable\n"); return
    st1 = ann(s[s.index >= PILOT])
    days = (s.index.max() - s.index.min()).days
    mid = s.index.min() + (s.index.max() - s.index.min()) / 2
    h1, h2 = ann(s[s.index <= mid]), ann(s[s.index > mid])
    if st1 < 4:
        print(f"{lab}: Stage 1 {st1:.2f}%/yr -> KILL. FAIL\n"); return
    ok = days >= 180 and h1 >= 8 and h2 >= 8
    print(f"{lab}: Stage 1 {st1:.2f}%; {days} days from {s.index.min().date()}; halves {h1:.2f}% / {h2:.2f}% -> {'PASS' if ok else 'FAIL'}\n")


# 263 / 264 tranches: equal weight of each group's pools, yield from DefiLlama apy (vault share-price based), TVL-collapse stress as #204
tp = pd.read_parquet("data/public/batch6_tranche_pools.parquet").set_index("pool")
tc = pd.read_parquet("data/public/batch6_tranche_charts.parquet")
tc["day"] = pd.to_datetime(tc["ts"], utc=True).dt.floor("D")
tc = tc.drop_duplicates(["pool", "day"])
tc["y"] = (pd.to_numeric(tc.apyBase, errors="coerce").fillna(0) + 0.9 * pd.to_numeric(tc.apyReward, errors="coerce").fillna(0)).clip(upper=500)
sym = tp.symbol.str.upper()
for lab, ids in (("#263 junior tranches (equal weight)", tp.index[sym.str.startswith("JR") | (sym == "RLP")]),
                 ("#264 senior tranches (equal weight)", tp.index[sym.str.startswith("SR") & (tp.project == "strata-markets")])):
    g = tc[tc.pool.isin(ids)]
    if g.empty:
        print(f"{lab}: no chart data\n"); continue
    Y = g.pivot(index="day", columns="pool", values="y")
    T = g.pivot(index="day", columns="pool", values="tvlUsd").ffill(limit=3)
    out, dead, hits = [], set(), 0
    for d in Y.index:
        r = []
        for p in Y.columns:
            if p in dead or pd.isna(Y.at[d, p]):
                continue
            t7 = T.loc[d - pd.Timedelta(days=7):d, p]
            if len(t7) > 1 and t7.iloc[-1] < 0.5 * t7.max():
                dead.add(p); hits += 1; r.append(-0.20 * 365 * 100); continue
            r.append(Y.at[d, p])
        out.append((d, np.mean(r) / 100 / 365 if r else np.nan))
    print(f"  {lab}: {Y.shape[1]} pools, stress hits {hits}")
    verdict(lab, pd.Series(dict(out)))
# 276 HYPE native staking hedged: assumed constant 2.5% APR + realised HL HYPE short funding, / 1.333
f = pd.read_parquet("data/public/hedged_hlfunding.parquet")
f["day"] = pd.to_datetime(f["t"], unit="s", utc=True).dt.floor("D")
h = f[f.coin == "HYPE"].groupby("day").rate.sum()
s = (2.5 / 100 / 365 + h) / (4 / 3)
verdict("#276 native HYPE staking hedged (staking APR assumed 2.5%)", s[(s.index >= LO) & (s.index < HI)])
# 278 new-chain stable incentives: monthly top 5 by trailing 30-d yield among stable single pools on new chains (as #204, $5 per change)
pools = pd.read_parquet("data/public/llama_pools_now.parquet")
NEW = ["Monad", "Plasma", "Stable", "MegaETH", "Katana", "Hyperliquid L1", "Plume Mainnet", "Unichain", "Berachain", "Sonic", "Ink", "Soneium"]
ids = set(pools.pool[pools.chain.isin(NEW)])
ch = pd.read_parquet("data/public/fallback_stable_charts.parquet")
ch = ch[ch.pool.isin(ids)].copy()
ch["day"] = ch["ts"].dt.floor("D")
ch = ch.drop_duplicates(["pool", "day"])
ch["y"] = (ch.apyBase.fillna(0) + 0.9 * ch.apyReward.fillna(0)).clip(upper=500)
if ch.empty:
    print("#278: no history for new-chain pools in fallback_stable_charts -> not testable")
else:
    Y = ch.pivot(index="day", columns="pool", values="y")
    T = ch.pivot(index="day", columns="pool", values="tvlUsd").ffill(limit=3)
    first = ch.groupby("pool").day.min()
    out, prev, hits = [], set(), 0
    for m in pd.date_range(LO, HI - pd.Timedelta(days=1), freq="MS", tz="UTC"):
        pday = m - pd.Timedelta(days=1)
        if pday not in T.index:
            continue
        ok = [p for p in Y.columns if pd.notna(T.at[pday, p]) and T.at[pday, p] >= 5e6 and (pday - first[p]).days >= 30]
        held = list(Y.loc[pday - pd.Timedelta(days=29):pday, ok].mean().dropna().sort_values(ascending=False).index[:5])
        ch_n = len(set(held) ^ prev); prev = set(held); alive = {p: True for p in held}
        for j, d in enumerate(pd.date_range(m, m + pd.offsets.MonthEnd(0), freq="D", tz="UTC")):
            r = []
            for p in held:
                if not alive[p]:
                    r.append(0.0); continue
                t7 = T.loc[d - pd.Timedelta(days=7):d, p]
                if len(t7) > 1 and t7.iloc[-1] < 0.5 * t7.max():
                    alive[p] = False; hits += 1; r.append(-0.20); continue
                v = Y.at[d, p] if d in Y.index else np.nan
                r.append((v if pd.notna(v) else 0.0) / 100 / 365)
            out.append((d, (np.mean(r) if r else np.nan) - (ch_n * 5 / 10_000 if j == 0 else 0)))
    print(f"  #278: {Y.shape[1]} new-chain pools with history; stress hits {hits}")
    verdict("#278 new-chain stable incentives (monthly top 5)", pd.Series(dict(out)))

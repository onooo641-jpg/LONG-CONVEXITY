"""#214 robustness: hedged governance-token yields including the wrapper discount (PREREG_HEDGED addendum).

    uv run python scripts/hedged_wrappers_20261121.py | tee docs/jx_runs/hedged_wrappers_20261121.txt
"""
import numpy as np
import pandas as pd

import scripts.hedged_20261121 as H

pools = pd.read_parquet("data/public/hedged_pools.parquet").set_index("pool")
ch = pd.read_parquet("data/public/hedged_charts.parquet")
ch["day"] = ch["ts"].dt.floor("D")
ch = ch.drop_duplicates(["pool", "day"])
f = pd.read_parquet("data/public/hedged_hlfunding.parquet")
f["day"] = pd.to_datetime(f["t"], unit="s", utc=True).dt.floor("D")
F = f.groupby(["coin", "day"])["rate"].sum().mul(365 * 100)
px = pd.read_parquet("data/public/wrappers_prices.parquet")
px["day"] = pd.to_datetime(px["ts"], unit="s", utc=True).dt.floor("D")
P = px.pivot_table(index="day", columns="token", values="price", aggfunc="last").sort_index()
print("price days per token:", P.notna().sum().to_dict())
under = {"YCRV": "CRV", "ST-YCRV": "CRV", "CVXCRV": "CRV", "SDCRV": "CRV", "SDPENDLE": "PENDLE"}
disc = {}
for w, u in under.items():
    if w in P and u in P:
        r = np.log(P[w] / P[u]).diff()
        disc[w] = r
        lv = (P[w] / P[u]).dropna()
        if len(lv):
            print(f"  {w}/{u} ratio: start {lv.iloc[0]:.3f}, end {lv.iloc[-1]:.3f}, min {lv.min():.3f}")
D = pd.DataFrame(disc)
worst = D.min(axis=1)  # conservative fill for wrappers without prices
gov = pools[pools["coin"].isin(["CRV", "AAVE", "ENA", "PENDLE", "LDO", "MORPHO", "AERO", "FXS"])]
ch = ch[ch.pool.isin(gov.index)].copy()
ch["coin"] = ch.pool.map(pools["coin"])
ch["F"] = [F.get((c, d), np.nan) for c, d in zip(ch.coin, ch.day)]
ch = ch[ch.F.notna()]
sym = ch.pool.map(pools["symbol"].str.upper())
key = sym.map(lambda s: "ST-YCRV" if s == "YCRV" and "ST-YCRV" in D else s)
dd = []
for k, d in zip(key, ch.day):
    if k in under:
        v = D[k].get(d, np.nan) if k in D else np.nan
        if pd.isna(v):
            v = worst.get(d, 0.0) if pd.notna(worst.get(d, np.nan)) else 0.0
        dd.append(v)
    else:
        dd.append(0.0)
ch["disc"] = np.array(dd) * 365 * 100  # annualised % for that day
ch["y"] = ((ch.apyBase.fillna(0) + 0.9 * ch.apyReward.fillna(0)).clip(upper=500) + ch.F + ch.disc) / (4 / 3)
names = {p: f"{pools.at[p, 'project']}/{pools.at[p, 'symbol']}" for p in pools.index}
Y = ch.pivot(index="day", columns="pool", values="y").sort_index()
T = ch.pivot(index="day", columns="pool", values="tvlUsd").sort_index().ffill(limit=3)
H.rotate(Y, T, ch.groupby("pool")["day"].min(), 0.0005 + 0.00045 + 10 / H.SLOT, lambda p: 0.20, "#214 with wrapper discount", names, 2e6)

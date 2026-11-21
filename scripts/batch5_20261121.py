"""Batch 5 (docs/PREREG_BATCH5_20261121.md): #228 hedged resource/revenue staking, #229 hedged native L1 staking. Stage 0.5 then Stage 1.

    uv run python scripts/batch5_20261121.py | tee docs/jx_runs/batch5_20261121.txt
"""
import numpy as np
import pandas as pd

f = pd.read_parquet("data/public/batch5_hlfunding.parquet")
f["day"] = pd.to_datetime(f["t"], unit="s", utc=True).dt.floor("D")
end = f["day"].max()
F90 = {c: g[g.day > end - pd.Timedelta(days=90)].rate.sum() / 90 * 365 * 100 for c, g in f.groupby("coin")}
Fd = f.groupby(["coin", "day"])["rate"].sum().mul(365 * 100)
print(f"HL funding to {end.date()}; 90-day short funding (annualised %): " + ", ".join(f"{c} {v:.1f}" for c, v in sorted(F90.items())) + "\n")

# 228
pools = pd.read_parquet("data/public/batch5_pools.parquet").set_index("pool")
ch = pd.read_parquet("data/public/batch5_charts.parquet")
ch["day"] = ch["ts"].dt.floor("D")
ch["y"] = pd.to_numeric(ch.apyBase, errors="coerce").fillna(0) + 0.9 * pd.to_numeric(ch.apyReward, errors="coerce").fillna(0)
coin = {"tr-energy": "TRX", "sky-lending": "SKY"}
best = None
for p, g in ch.groupby("pool"):
    proj = pools.at[p, "project"]
    c = coin[proj]
    g = g.drop_duplicates("day").set_index("day").sort_index()
    cur = g.y.iloc[-30:].mean()
    ceil = (cur + F90.get(c, np.nan)) / (4 / 3)
    real = ((g.y + Fd.loc[c].reindex(g.index)) / (4 / 3)).dropna() if c in Fd.index.get_level_values(0) else pd.Series(dtype=float)
    s1 = real[real.index >= pd.Timestamp("2026-08-01", tz="UTC")].mean()
    print(f"#228 {proj}/{pools.at[p, 'symbol']} (TVL ${pools.at[p, 'tvlUsd']:,.0f}): yield (30 d) {cur:.2f}% + {c} short funding {F90.get(c, float('nan')):.2f}% "
          f"-> ceiling {ceil:.2f}%; Stage 1 realised (Aug-Oct, days with funding) {s1:.2f}%")
    best = max(best or -1e9, ceil if ceil == ceil else -1e9)
print(f"#228 verdict: {'Stage 0.5 KILL (best ceiling < 8%)' if best < 8 else 'survives Stage 0.5 -> check Stage 1 lines above (kill if < 4%)'}\n")

# 229
st = pd.read_parquet("data/public/staking_apr.parquet")
for c in ("inflation", "community_tax", "bonded", "supply"):
    st[c] = pd.to_numeric(st[c], errors="coerce")
st["apr"] = st.inflation * (1 - st.community_tax.fillna(0.02)) / (st.bonded / st.supply) * 0.95 * 100
best = -1e9
for r in st.itertuples():
    fc = F90.get(r.coin, np.nan)
    ceil = (r.apr + fc) / (4 / 3)
    print(f"#229 {r.coin}: staking APR {r.apr:.2f}% (inflation {r.inflation:.3f}, bonded ratio {r.bonded / r.supply:.2f}) + short funding {fc:.2f}% -> ceiling {ceil:.2f}%")
    if ceil == ceil:
        best = max(best, ceil)
for c in ("APT", "NEAR", "DOT"):
    print(f"#229 {c}: no free staking-APR source fetched; short funding {F90.get(c, float('nan')):.2f}% (not testable)")
print(f"#229 verdict: {'Stage 0.5 KILL (best ceiling < 8%)' if best < 8 else 'survives Stage 0.5 for the coins >= 8% (Stage 1 needs historical APR: not available free -> not testable beyond Stage 0.5)'}")

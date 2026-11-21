"""#228 Stage 2: hedged SKY staking (the pool that survived Stage 1), full history (docs/PREREG_BATCH5_20261121.md).

    uv run python scripts/sky_stage2_20261121.py | tee docs/jx_runs/sky_stage2_20261121.txt
"""
import pandas as pd

LO, HI, PILOT = [pd.Timestamp(x, tz="UTC") for x in ("2024-11-01", "2026-11-01", "2026-08-01")]
pools = pd.read_parquet("data/public/batch5_pools.parquet").set_index("pool")
ch = pd.read_parquet("data/public/batch5_charts.parquet")
ch["day"] = ch["ts"].dt.floor("D")
ch["y"] = pd.to_numeric(ch.apyBase, errors="coerce").fillna(0) + 0.9 * pd.to_numeric(ch.apyReward, errors="coerce").fillna(0)
f = pd.read_parquet("data/public/batch5_hlfunding_full.parquet")
f["day"] = pd.to_datetime(f["t"], unit="s", utc=True).dt.floor("D")
F = f[f.coin == "SKY"].groupby("day")["rate"].sum() * 365 * 100
for p in pools.index[pools.project == "sky-lending"]:
    g = ch[ch.pool == p].drop_duplicates("day").set_index("day").sort_index()
    s = ((g.y + F.reindex(g.index)) / (4 / 3)).dropna()
    s = s[(s.index >= LO) & (s.index < HI)]
    if s.empty:
        print(f"{p}: no overlapping data"); continue
    mid = s.index.min() + (s.index.max() - s.index.min()) / 2
    days = (s.index.max() - s.index.min()).days
    st1, h1, h2 = s[s.index >= PILOT].mean(), s[s.index <= mid].mean(), s[s.index > mid].mean()
    ok = st1 >= 4 and days >= 180 and h1 >= 8 and h2 >= 8
    print(f"#228 SKY pool {p[:8]} (TVL ${pools.at[p, 'tvlUsd']:,.0f}): {days} days from {s.index.min().date()}; Stage 1 {st1:.2f}%; "
          f"halves {h1:.2f}% / {h2:.2f}%; pool yield mean {g.y.reindex(s.index).mean():.2f}%, SKY short funding mean {F.reindex(s.index).mean():.2f}% "
          f"-> {'PASS' if ok else 'FAIL'}")

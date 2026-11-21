"""Gold carry (docs/PREREG_GOLDCARRY_20261121.md, #216)."""
import pandas as pd

f = pd.read_parquet("data/public/hedged_hlfunding.parquet")
f = f[f.coin == "PAXG"].copy()
f["day"] = pd.to_datetime(f["t"], unit="s", utc=True).dt.floor("D")
d = f.groupby("day")["rate"].sum()
d = d[(d.index >= pd.Timestamp("2024-11-01", tz="UTC")) & (d.index < pd.Timestamp("2026-11-01", tz="UTC"))]
if d.empty:
    print("no PAXG funding data"); raise SystemExit
r = d / (4 / 3)  # daily return on capital
ann = lambda x: float(x.mean() * 365 * 100)
days = (d.index.max() - d.index.min()).days
mid = d.index.min() + (d.index.max() - d.index.min()) / 2
pilot = ann(r[r.index >= pd.Timestamp("2026-08-01", tz="UTC")])
h1, h2 = ann(r[r.index <= mid]), ann(r[r.index > mid])
print(f"PAXG funding days {len(d)} ({d.index.min().date()}..{d.index.max().date()}); Stage 1 {pilot:.2f}%/yr; halves {h1:.2f}% / {h2:.2f}% on capital; "
      f"share of days shorts paid {(d < 0).mean():.0%}; ${ann(r) * 100:,.0f}/yr on $10K")
if pilot < 4:
    print("VERDICT: FAIL (Stage 1)")
else:
    print(f"VERDICT: {'PASS' if days >= 180 and h1 >= 8 and h2 >= 8 else 'FAIL'}")

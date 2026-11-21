"""Best-venue funding carry on DeFi perps (docs/PREREG_BESTVENUE_20261121.md, #217)."""
import numpy as np
import pandas as pd

from scripts.fundgap_20261121 import hourly

LO, HI = pd.Timestamp("2024-11-01", tz="UTC"), pd.Timestamp("2026-11-01", tz="UTC")
MID, PILOT = pd.Timestamp("2025-11-01", tz="UTC"), pd.Timestamp("2026-08-01", tz="UTC")
df = pd.read_parquet("data/public/fundgap_funding.parquet")
df = df[df.venue.isin(["hl", "dydx", "aevo"])]
H = hourly(df)
D = {k: v.resample("D").sum(min_count=12) * 365 * 100 for k, v in H.items()}  # funding received by a short, annualised %
days = pd.date_range(LO, HI - pd.Timedelta(days=1), freq="D", tz="UTC")
out, prev, log = [], set(), []
for m in pd.date_range(LO, HI - pd.Timedelta(days=1), freq="MS", tz="UTC"):
    w = slice(m - pd.Timedelta(days=30), m - pd.Timedelta(days=1))
    sc = sorted(((float(s[w].mean()), k) for k, s in D.items() if s[w].notna().sum() >= 20), reverse=True)
    held, coins = [], set()
    for v, (ven, c) in sc:
        if c not in coins:
            held.append((ven, c)); coins.add(c)
        if len(held) == 3:
            break
    ch = len(set(held) ^ prev); prev = set(held)
    log.append(f"  {m:%Y-%m}: " + ", ".join(f"{c}@{v}" for v, c in held))
    for j, d in enumerate([x for x in days if x.year == m.year and x.month == m.month]):
        r = [((D[k].get(d, np.nan)) if pd.notna(D[k].get(d, np.nan)) else 0.0) / 100 / 365 for k in held]
        cost = ch * (0.001 + 0.0005) / 3 if j == 0 else 0.0
        out.append((d, (np.mean(r) if r else 0.0) / (4 / 3) - cost))
s = pd.Series(dict(out))
ann = lambda x: float(x.mean() * 365 * 100)
for line in log[-3:]:
    print(line)
pilot, h1, h2 = ann(s[s.index >= PILOT]), ann(s[s.index < MID]), ann(s[s.index >= MID])
print(f"Stage 1 {pilot:.2f}%/yr; halves {h1:.2f}% / {h2:.2f}% on capital; ${ann(s) * 100:,.0f}/yr on $10K")
print("VERDICT:", "FAIL (Stage 1)" if pilot < 4 else ("PASS" if h1 >= 8 and h2 >= 8 else "FAIL"))

"""#221 robustness: hedged GM pools with real GM token prices (PREREG_BATCH4 addendum).

    uv run python scripts/gm_robust_20261121.py | tee docs/jx_runs/gm_robust_20261121.txt
"""
import numpy as np
import pandas as pd

LO, MID, HI, PILOT = [pd.Timestamp(x, tz="UTC") for x in ("2024-11-01", "2025-11-01", "2026-11-01", "2026-08-01")]
h = 0.5
px = pd.read_parquet("data/public/wrappers_prices.parquet")
px["day"] = pd.to_datetime(px["ts"], unit="s", utc=True).dt.floor("D")
P = px.pivot_table(index="day", columns="token", values="price", aggfunc="last").sort_index()
f = pd.read_parquet("data/public/hedged_hlfunding.parquet")
f["day"] = pd.to_datetime(f["t"], unit="s", utc=True).dt.floor("D")
F = f.groupby(["coin", "day"])["rate"].sum()  # daily funding fraction received by a short
need = ["GM_ETH", "GM_BTC", "ETH", "BTC"]
missing = [c for c in need if c not in P or P[c].notna().sum() < 100]
if missing:
    print(f"#221 robustness: price history missing for {missing} -> 'passes fee-APY rule, not verified'")
    raise SystemExit
legs = []
for gm, idx in (("GM_ETH", "ETH"), ("GM_BTC", "BTC")):
    r = np.log(P[gm]).diff() - h * np.log(P[idx]).diff() + h * F.loc[idx].reindex(P.index).fillna(0)
    legs.append(r / (1 + h / 3))
    print(f"  {gm}: price days {P[gm].notna().sum()}, first {P[gm].first_valid_index().date()}")
s = pd.concat(legs, axis=1).mean(axis=1).dropna()
s = s[(s.index >= LO) & (s.index < HI)]
ann = lambda x: float(x.mean() * 365 * 100)  # noqa: E731
pilot, h1, h2 = ann(s[s.index >= PILOT]), ann(s[s.index < MID]), ann(s[s.index >= MID])
dd = float(((s.cumsum().apply(np.exp)) / (s.cumsum().apply(np.exp)).cummax() - 1).min() * 100)
print(f"#221 with real GM prices: Stage 1 {pilot:.2f}%/yr; halves {h1:.2f}% / {h2:.2f}% on capital; worst drawdown {dd:.1f}%; ${ann(s) * 100:,.0f}/yr on $10K")
print("VERDICT:", "FAIL (Stage 1)" if pilot < 4 else ("PASS" if h1 >= 8 and h2 >= 8 else "FAIL"))

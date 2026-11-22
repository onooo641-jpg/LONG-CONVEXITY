"""POST-HOC robustness for #276 (labelled, not a verdict): hedged native HYPE staking.

    uv run python scripts/hype_robust_20261122.py | tee docs/jx_runs/hype_robust_20261122.txt
"""
import pandas as pd

LO, HI = pd.Timestamp("2024-11-01", tz="UTC"), pd.Timestamp("2026-11-01", tz="UTC")
f = pd.read_parquet("data/public/hedged_hlfunding.parquet")
f["day"] = pd.to_datetime(f["t"], unit="s", utc=True).dt.floor("D")
h = f[f.coin == "HYPE"].groupby("day").rate.sum()
h = h[(h.index >= LO) & (h.index < HI)]
mid = h.index.min() + (h.index.max() - h.index.min()) / 2
ann = lambda x: float(x.mean() * 365 * 100)  # noqa: E731
for lab, stk, cap in (("as registered (2.5% staking, 3x short, capital 1.333)", 2.5, 4 / 3), ("no staking yield, 3x", 0.0, 4 / 3),
                      ("2.5% staking, 2x short (capital 1.5)", 2.5, 1.5), ("no staking, 2x", 0.0, 1.5)):
    s = (stk / 100 / 365 + h) / cap
    print(f"{lab:<52} halves {ann(s[s.index <= mid]):6.2f}% / {ann(s[s.index > mid]):6.2f}%; last 90 d {ann(s[s.index > s.index.max() - pd.Timedelta(days=90)]):6.2f}%")
print(f"share of days HYPE shorts paid funding: {(h < 0).mean():.0%}; monthly funding received (annualised %):")
m = h.groupby(h.index.strftime("%Y-%m")).mean() * 365 * 100
print("  " + ", ".join(f"{k} {v:.0f}" for k, v in m.items()))
try:
    c = pd.read_parquet("data/public/hl_candles.parquet")
    c = c[c.coin == "HYPE"].copy()
    if len(c):
        c["day"] = pd.to_datetime(c["t"], unit="ms", utc=True).dt.floor("D")
        d = c.groupby("day").agg(o=("o", "first"), h=("h", "max"), c=("c", "last"))
        up = (d.h / d.o - 1).max()
        print(f"largest intraday rise open->high in one day: {up:.1%} (a 3x short is liquidated near +33%, a 2x near +50%, unless margin is topped up)")
    else:
        print("HYPE not in hl_candles -> liquidation check not possible from repo data")
except Exception as e:  # noqa: BLE001
    print("candles check failed:", e)

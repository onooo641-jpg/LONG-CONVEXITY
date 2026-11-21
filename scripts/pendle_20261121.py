"""#211 Pendle stable PTs held to maturity, Stage 1 pilot (docs/PREREG_PENDLE_20261121.md).

    uv run python scripts/pendle_20261121.py | tee docs/jx_runs/pendle_20261121.txt
"""
import pandas as pd

NOW = pd.Timestamp("2026-11-21", tz="UTC")
h = pd.read_parquet("data/public/pendle_pilot_history.parquet")
h["day"] = pd.to_datetime(h["timestamp"], utc=True).dt.floor("D")
h["exp"] = pd.to_datetime(h["expiry"], utc=True)
u = pd.read_parquet("data/public/pendle_pilot_underlying.parquet").set_index("address")["price_at_expiry_or_now"]
COST_SWAP, LEG = 0.001, 10_000 / 6 / 3
rows = []
for entry in pd.date_range("2026-05-01", "2026-07-01", freq="MS", tz="UTC"):
    d = h[(h.day == entry) & (h.tvl >= 5e6) & ((h.exp - entry).dt.days >= 30)].sort_values("impliedApy", ascending=False).head(3)
    for r in d.itertuples():
        end = min(r.exp, NOW)
        days = (end - entry).days
        px = u.get(r.address)
        if px is not None and pd.notna(px) and px < 0.98:
            ret = px - 1  # depeg: loss instead of the fixed yield
            tag = f"DEPEG underlying {px:.3f}"
        else:
            ret = (1 + r.impliedApy) ** (days / 365) - 1
            tag = "matured" if r.exp <= NOW else "open, accrued"
        ret -= COST_SWAP + 10 / LEG
        rows.append({"entry": entry.date(), "market": r.name, "chain": r.chain, "implied": r.impliedApy * 100, "days": days, "ret": ret * 100,
                     "ann": ret * 365 / max(days, 1) * 100, "tag": tag})
df = pd.DataFrame(rows)
print(df.round(2).to_string(index=False))
if df.empty:
    print("no eligible markets (TVL >= $5M, >= 30 days) -> not testable")
else:
    pilot = df.ann.mean()
    print(f"\nStage 1 (cohorts 2026-05..07): mean annualised {pilot:.2f}%/yr; positions hit by depeg {int(df.tag.str.startswith('DEPEG').sum())} of {len(df)}")
    print("VERDICT:", "FAIL (Stage 1 KILL < 4%)" if pilot < 4 else "survives Stage 1 -> Stage 2 needs expired-market history 2024-11..2026-04 (next fetch)")

"""Stage 0.5 ceiling check (docs/PREREG_RADAR_20261121.md addendum 7) from data already in the repo.

    uv run python scripts/ceiling_20261121.py | tee docs/jx_runs/ceiling_20261121.txt
"""
import pandas as pd

f = pd.read_parquet("data/public/hl_funding.parquet")
f["ts"] = pd.to_datetime(f["time"], unit="ms", utc=True)
end = f.ts.max()


def fund(c, days):
    g = f[(f.coin == c) & (f.ts > end - pd.Timedelta(days=days))]
    return g.rate.sum() / days * 365 * 100 if len(g) else float("nan")


print("Stage 0.5 ceiling check from data already in the repo (HL funding to", end.date(), "; DefiLlama pools snapshot 2026-11-20)\n")
print("HL funding received by a SHORT, annualised % (last 90 d / last 365 d):")
coins = ["BTC", "ETH", "SOL", "HYPE", "AVAX", "BNB", "PAXG", "CRV", "AAVE", "ENA", "PENDLE", "LDO", "MORPHO", "AERO", "FXS", "XRP", "DOGE", "LINK", "SUI"]
F = {}
for c in coins:
    F[c] = (fund(c, 90), fund(c, 365))
    print(f"  {c:<7} {F[c][0]:6.1f} / {F[c][1]:6.1f}")
p = pd.read_parquet("data/public/llama_pools_now.parquet")
p["y"] = p.apyBase.fillna(0) + 0.9 * p.apyReward.fillna(0)
fam = {"ETH": ["STETH", "WSTETH", "RETH", "CBETH", "WEETH", "EZETH", "RSETH", "METH", "SFRXETH", "OSETH", "WBETH", "ETHX", "WETH", "ETH"],
       "SOL": ["SOL", "JITOSOL", "MSOL", "JUPSOL", "BSOL", "INF", "BNSOL", "HSOL"], "HYPE": ["HYPE", "KHYPE", "STHYPE", "WHYPE"],
       "BTC": ["BTC", "WBTC", "CBBTC", "TBTC", "LBTC"], "AVAX": ["AVAX", "SAVAX", "WAVAX"], "BNB": ["BNB", "SLISBNB", "BNBX", "WBNB"],
       "CRV": ["CRV", "CVXCRV", "SDCRV", "YCRV", "ST-YCRV", "ASDCRV"], "AAVE": ["AAVE", "STKAAVE"], "ENA": ["ENA", "SENA"],
       "PENDLE": ["PENDLE", "VEPENDLE", "SPENDLE", "MPENDLE", "SDPENDLE"], "LDO": ["LDO"], "MORPHO": ["MORPHO"], "AERO": ["AERO", "VEAERO"],
       "FXS": ["FXS", "CVXFXS", "SDFXS"]}
GOV = ["CRV", "AAVE", "ENA", "PENDLE", "LDO", "MORPHO", "AERO", "FXS"]
print("\nBest current pool yield (TVL >= $20M; governance tokens >= $2M) + HL short funding (90 d), / 1.333 capital factor = hedged ceiling:")
rows = []
for c, ts in fam.items():
    q = p[(p.symbol.str.upper().isin(ts)) & (p.exposure == "single") & (p.tvlUsd >= (2e6 if c in GOV else 20e6)) & (p.y < 200)]
    if q.empty:
        continue
    b = q.sort_values("y", ascending=False).iloc[0]
    top5 = q.sort_values("y", ascending=False).head(5).y.mean()
    rows.append((c, b.project, b.symbol, b.y, F[c][0], (b.y + F[c][0]) / (4 / 3), (top5 + F[c][0]) / (4 / 3)))
for r in sorted(rows, key=lambda r: -(r[5] if r[5] == r[5] else -1)):
    print(f"  {r[0]:<7} best {r[1]}/{r[2]} {r[3]:5.1f}% + funding {r[4]:5.1f}% -> ceiling {r[5]:5.1f}% (top-5 avg {r[6]:5.1f}%)")
print(f"\n#216 gold carry ceiling: {F['PAXG'][0] / (4 / 3):.1f}% (90 d), {F['PAXG'][1] / (4 / 3):.1f}% (365 d)  [nan = PAXG not in this HL file]")
U217 = ["BTC", "ETH", "SOL", "XRP", "DOGE", "AVAX", "LINK", "SUI", "ARB", "OP", "LTC", "BNB"]  # #217's pre-registered coins
best = sorted(((fund(c, 90), c) for c in U217 if fund(c, 90) == fund(c, 90)), reverse=True)[:3]
print(f"#217 best-venue carry, HL leg only, top-3 coins last 90 d (hindsight): {sum(x for x, _ in best) / 3 / (4 / 3):.1f}% ({', '.join(c for _, c in best)})")

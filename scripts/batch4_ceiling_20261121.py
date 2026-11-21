"""Stage 0.5 ceilings for batch 4 (docs/PREREG_BATCH4_20261121.md)."""
import pandas as pd

f = pd.read_parquet("data/public/hl_funding.parquet")
f["ts"] = pd.to_datetime(f["time"], unit="ms", utc=True)
end = f.ts.max()
fund = lambda c: (lambda g: g.rate.sum() / 90 * 365 * 100 if len(g) else float("nan"))(f[(f.coin == c) & (f.ts > end - pd.Timedelta(days=90))])  # noqa: E731
p = pd.read_parquet("data/public/llama_pools_now.parquet")
p["y"] = p.apyBase.fillna(0) + 0.9 * p.apyReward.fillna(0)
p = p[p.y < 300]
print(f"snapshot pools {len(p)}; HL funding to {end.date()}\n")


def verdict(c):
    return "KILL" if not (c == c) or c < 8 else "survives -> Stage 1 pilot"


# 221 GMX GM pools: index token from symbol 'ETH-USDC' style
g = p[p.project.isin(["gmx-evm", "gmx-solana"]) & (p.tvlUsd >= 20e6)].copy()
g["idx"] = g.symbol.str.split("-").str[0].str.replace("WETH", "ETH").str.replace("WBTC", "BTC").str.replace(".B", "", regex=False)
g["F"] = g.idx.map(lambda c: fund(c))
g = g[g.F.notna()]
g["hedged"] = (g.y + 0.5 * g.F) / (1 + 0.5 / 3)
top = g.sort_values("hedged", ascending=False)
if len(top):
    b = top.iloc[0]
    print(f"#221 GMX GM hedged: {len(g)} pools; best {b.symbol} {b.y:.1f}% + 0.5 x funding {b.F:.1f}% -> ceiling {b.hedged:.1f}% "
          f"(top-5 avg {top.head(5).hedged.mean():.1f}%) => {verdict(b.hedged)}")
else:
    print("#221: no GM pools with HL-listed index token => KILL (no candidates)")
# 224 stable-pair LPs
s = p[(p.stablecoin == True) & (p.exposure == "multi") & (p.ilRisk == "no") & (p.tvlUsd >= 5e6)].sort_values("y", ascending=False)  # noqa: E712
if len(s):
    b = s.iloc[0]
    print(f"#224 stable-pair LPs: {len(s)} pools; best {b.project}/{b.symbol} {b.y:.1f}%; top-5 avg {s.head(5).y.mean():.1f}% => {verdict(s.head(5).y.mean())} "
          f"(judged on the top-5 average, the Stage-2 holding)")
# 225 trader-counterparty vaults
v = p[p.project.isin(["gains-network", "avantis", "ostium"]) & (p.stablecoin == True)].sort_values("y", ascending=False)  # noqa: E712
if len(v):
    b = v.iloc[0]
    print(f"#225 trader-counterparty vaults in snapshot: {len(v)} ({', '.join(v.project + '/' + v.symbol)}); best {b.project}/{b.symbol} {b.y:.1f}% (TVL ${b.tvlUsd:,.0f}) => {verdict(b.y)}")
else:
    print("#225: none in snapshot => pilot fetch")
# 227 savings rates not in #210
sav = p[(p.stablecoin == True) & (p.exposure == "single") & (p.tvlUsd >= 5e6) &  # noqa: E712
        p.symbol.str.upper().isin(["SCRVUSD", "SFRXUSD", "SUSDAI", "SAVUSD", "SUSDX", "STUSR", "SDOLA", "SYRUPUSDC", "SYRUPUSDT", "SUSDF", "SNUSD", "WSRUSD", "SRUSD", "YUSD", "SUSDU"])]
sav = sav[~sav.project.isin(["ethena-usde", "falcon-finance", "sky-lending", "spark-savings", "usual-usd0", "maple"])].sort_values("y", ascending=False)
if len(sav):
    print(f"#227 other savings rates: {len(sav)} pools; best {sav.iloc[0].project}/{sav.iloc[0].symbol} {sav.iloc[0].y:.1f}%; top-5 avg {sav.head(5).y.mean():.1f}% => {verdict(sav.head(5).y.mean())}")
else:
    print("#227: none found => KILL (no candidates)")
print("#220 Jupiter JLP, #222 dYdX MegaVault, #223 Lighter LLP: not in the snapshot => go to a 90-day pilot fetch")

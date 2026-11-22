"""Batch 6 part A: Stage 0 / 0.5 from data already in the repo (docs/PREREG_BATCH6_20261122.md).

    uv run python scripts/batch6a_20261122.py | tee docs/jx_runs/batch6a_20261122.txt
"""
import pandas as pd

p = pd.read_parquet("data/public/llama_pools_now.parquet")
p["S"] = p.symbol.str.upper()
p["y"] = p.apyBase.fillna(0) + 0.9 * p.apyReward.fillna(0)
v = lambda c: "KILL" if not c == c or c < 8 else "survives Stage 0.5"  # noqa: E731

rwa = p[p.project.str.contains("ondo|superstate|hashnote|circle-usyc|blackrock|invesco|franklin|openeden|mountain|backed", case=False)]
c = rwa.y.max()
print(f"#269 RWA / tokenised T-bills: {len(rwa)} pools; best yield {c:.2f}% -> {v(c)}")
tm = p[p.project.str.contains("term", case=False) & (p.tvlUsd >= 1e6)]
c = tm.y.max() if len(tm) else float("nan")
print(f"#270 fixed-rate auctions (TermMax etc., TVL >= $1M): {len(tm)} pools; best {c:.2f}% -> {v(c)}")
f = pd.read_parquet("data/public/hedged_hlfunding.parquet")
f["ts"] = pd.to_datetime(f["t"], unit="s", utc=True)
h = f[(f.coin == "HYPE") & (f.ts > f.ts.max() - pd.Timedelta(days=90))]
fh = h.rate.sum() / 90 * 365 * 100
c = (2.5 + fh) / (4 / 3)
print(f"#276 native HYPE staking hedged: 2.5% (assumed) + HYPE 90-d short funding {fh:.2f}% -> ceiling {c:.2f}% -> {v(c)}")
b5 = pd.read_parquet("data/public/batch5_hlfunding.parquet")
b5["ts"] = pd.to_datetime(b5["t"], unit="s", utc=True)
hl = pd.read_parquet("data/public/hl_funding.parquet")
hl["ts"] = pd.to_datetime(hl["time"], unit="ms", utc=True)
end = hl.ts.max()
neg = (hl[hl.ts > end - pd.Timedelta(days=90)].groupby("coin").rate.sum() / 90 * 365 * 100)
b = b5[b5.ts > b5.ts.max() - pd.Timedelta(days=90)].groupby("coin").rate.sum() / 90 * 365 * 100
neg = pd.concat([neg, b]).groupby(level=0).last().sort_values().head(8)
lb = pd.read_parquet("data/public/lendborrow_now.parquet")
lb["S"] = lb.symbol.str.upper()
lb["bb"] = pd.to_numeric(lb.apyBaseBorrow, errors="coerce") - 0.9 * pd.to_numeric(lb.apyRewardBorrow, errors="coerce").fillna(0)
print("#277 reverse carry (long perp receives |negative funding|, short spot via borrowing):")
best = float("-inf")
for coin, fr in neg.items():
    q = lb[lb.S.isin([coin, "W" + coin]) & lb.bb.notna() & (lb.borrowable.astype(str) != "False")
           & (pd.to_numeric(lb.get("totalBorrowUsd"), errors="coerce").fillna(0) > 10_000) & (lb.bb > 0)].sort_values("bb")  # real, open borrow markets only
    br = float(q.bb.iloc[0]) if len(q) else float("nan")
    c = (-fr - br) / (4 / 3) if fr < 0 and br == br else float("nan")
    best = max(best, c) if c == c else best
    print(f"   {coin}: 90-d funding {fr:.2f}% (long receives {-fr:.2f}%), cheapest borrow {br:.2f}% "
          f"({q.project.iloc[0] + '/' + q.chain.iloc[0] if len(q) else 'no borrow market'}) -> ceiling {c:.2f}%")
print(f"   #277 best ceiling {best:.2f}% -> {v(best if best > float('-inf') else float('nan'))}")
newchains = ["Monad", "Plasma", "Stable", "MegaETH", "Katana", "Hyperliquid L1", "Plume Mainnet", "Unichain", "Berachain", "Sonic", "Ink", "Soneium"]
nc = p[p.chain.isin(newchains) & (p.stablecoin == True) & (p.exposure == "single") & (p.tvlUsd >= 5e6) & (p.y < 200)].sort_values("y", ascending=False)  # noqa: E712
c = nc.y.head(5).mean() if len(nc) else float("nan")
print(f"#278 new-chain stable incentives ({', '.join(sorted(set(nc.chain)))}): {len(nc)} pools; top-5 mean {c:.2f}% -> {v(c)}")
print("   top:", "; ".join(f"{r.project}/{r.symbol}/{r.chain} {r.y:.1f}%" for r in nc.head(5).itertuples()))
tr = p[p.project.isin(["strata-markets", "resolv", "reflect-tranches", "reservoir-protocol"]) | p.S.isin(["RLP", "JRUSDE", "SRUSDE", "SRUSDAT", "JRUSDAT"])]
jr = tr[tr.S.str.startswith("JR") | (tr.S == "RLP")]
sr = tr[tr.S.str.startswith("SR") & (tr.project == "strata-markets")]
for lab, q, n in (("#263 junior tranches", jr, 263), ("#264 senior tranches", sr, 264)):
    c = q.y.max() if len(q) else float("nan")
    print(f"{lab}: {', '.join(q.project + '/' + q.symbol + f' ' + q.y.round(1).astype(str) + '%')} -> best {c:.2f}% -> {v(c)}")
print("#268 veAERO hedged: Stage 0 KILL (4-year lock; exit only by selling the veNFT at an unknown discount; F4 unverifiable)")
print("#272 tokenised-stock premium arbitrage: Stage 0 KILL (securities access for a Malaysian resident unverified -> grey)")
print("#273 Solana LST instant-unstake spreads: Stage 0 KILL (instant-unstake pools arbitrage the discount by design; #41 analogue tiny)")
print("#274 hedged volatile v3 LP: Stage 0 NOT TESTABLE (concentrated-range IL/LVR not modelable from daily APY data)")
print("#275 bridge / intent relayers: Stage 0 KILL (bonded professional fillers, speed race; as M10)")

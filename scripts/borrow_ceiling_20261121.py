"""#209 / #219 Stage 0.5 ceilings from today's lendBorrow snapshot (PREREG_HEDGED addendum; borrow history is paywalled).

    uv run python scripts/borrow_ceiling_20261121.py | tee docs/jx_runs/borrow_ceiling_20261121.txt
"""
import pandas as pd

m = pd.read_parquet("data/public/lendborrow_now.parquet")
for c in ("apyBase", "apyReward", "apyBaseBorrow", "apyRewardBorrow", "ltv", "tvlUsd"):
    m[c] = pd.to_numeric(m[c], errors="coerce")
m["S"] = m.symbol.str.upper()
m["s"] = m.apyBase.fillna(0) + 0.9 * m.apyReward.fillna(0)
m["b"] = m.apyBaseBorrow - 0.9 * m.apyRewardBorrow.fillna(0)
ST = {"USDC", "USDT", "DAI", "USDE", "USDS", "GHO", "CRVUSD", "FRAX", "LUSD", "PYUSD", "RLUSD", "USD0", "USDT0", "USDC.E", "USDG", "FDUSD", "BOLD", "DOLA", "FRXUSD", "USD1", "AUSD", "USR"}
st = m[m.S.isin(ST) & (m.tvlUsd >= 5e6) & m.b.notna() & (m.borrowable.astype(str) == "True")].copy()
k = (1 / (1 - 0.8 * st.ltv.fillna(0).clip(0, 0.95))).clip(upper=5)
st["roe"] = st.s + (k - 1) * (st.s - st.b)
st = st.sort_values("roe", ascending=False)
print(f"#209 same-asset stable loops: {len(st)} pools with today's borrow rate; paid-to-borrow (b < 0): {(st.b < 0).sum()}")
print(st[["project", "chain", "symbol", "s", "b", "ltv", "roe"]].head(8).round(2).to_string(index=False))
c209 = st.roe.head(5).mean()
print(f"#209 ceiling (top-5 mean ROE, today): {c209:.2f}% -> {'KILL' if c209 < 8 else 'survives; full test not possible (borrow history paywalled)'}\n")
fam = {"ETH": ({"STETH", "WSTETH", "RETH", "CBETH", "WEETH", "EZETH", "RSETH", "METH", "SFRXETH", "OSETH", "WBETH", "ETHX"}, {"WETH", "ETH"}),
       "SOL": ({"JITOSOL", "MSOL", "JUPSOL", "BSOL", "INF", "BNSOL", "HSOL"}, {"SOL"}), "HYPE": ({"KHYPE", "STHYPE"}, {"HYPE", "WHYPE"}),
       "AVAX": ({"SAVAX"}, {"AVAX", "WAVAX"}), "USD": ({"SUSDE", "SUSDS", "SDAI", "SFRXUSD"}, {"USDC", "USDT", "USDT0", "USDS", "DAI"})}
snap = pd.read_parquet("data/public/llama_pools_now.parquet")
snap["S"] = snap.symbol.str.upper()
snap["yi"] = snap.apyBase.fillna(0)
intrinsic = {}
for sym in set().union(*[a for a, _ in fam.values()]):
    q = snap[(snap.S == sym) & (snap.exposure == "single") & snap.project.str.contains("stak|lido|rocket|ether.fi|kelp|renzo|stader|frax|ethena|sky|spark|jito|marinade|sanctum|helius|jupiter-staked|kinetiq|benqi|coinbase|binance|mantle|stakewise|swell|origin", case=False)]
    intrinsic[sym] = float(q.sort_values("tvlUsd").yi.iloc[-1]) if len(q) else 0.0
print("intrinsic yields used:", {k: round(v, 2) for k, v in sorted(intrinsic.items()) if v})
rows = []
for (proj, chain), g in m[m.tvlUsd >= 5e6].groupby(["project", "chain"]):
    for c, (sup, base) in fam.items():
        for _, a in g[g.S.isin(sup)].iterrows():
            for _, bb in g[g.S.isin(base) & g.b.notna()].iterrows():
                kk = min(1 / (1 - 0.8 * min(max(a.ltv or 0, 0), 0.95)), 6)
                sa = a.s + intrinsic.get(a.S, 0.0)
                rows.append((proj, chain, a.S, bb.S, sa, bb.b, kk, sa + (kk - 1) * (sa - bb.b)))
r = pd.DataFrame(rows, columns=["project", "chain", "supply", "borrow", "s", "b", "k", "roe"]).sort_values("roe", ascending=False)
print(f"#219 correlated-pair loops: {len(r)} pairs with today's rates")
print(r.head(8).round(2).to_string(index=False))
c219 = r.roe.head(5).mean() if len(r) else float("nan")
print(f"#219 ceiling (top-5 mean ROE, today): {c219:.2f}% -> {'KILL' if not c219 == c219 or c219 < 8 else 'survives; full test not possible (borrow history paywalled)'}")

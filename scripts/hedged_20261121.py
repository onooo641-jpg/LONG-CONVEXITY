"""Hedged yield mechanisms (docs/PREREG_HEDGED_20261121.md): #212 hedged staking, #213 hedged reward farming, #219 correlated loops.

    uv run python scripts/hedged_20261121.py | tee docs/jx_runs/hedged_20261121.txt
"""
from __future__ import annotations

import sys

import numpy as np
import pandas as pd

LO, HI = pd.Timestamp("2024-11-01", tz="UTC"), pd.Timestamp("2026-11-01", tz="UTC")
MID, PILOT = pd.Timestamp("2025-11-01", tz="UTC"), pd.Timestamp("2026-08-01", tz="UTC")
TOPK, SLOT, BAR, KILL = 5, 2000.0, 8.0, 4.0
STAKING = {"Liquid Staking", "Liquid Restaking", "Restaking"}
ann = lambda x: float(x.mean() * 365 * 100)  # noqa: E731


def rotate(Y, T, first, cost_frac, stress_fn, label, names):
    """Monthly top-K by trailing 30-day mean of Y (annualised % per day); returns daily return series (fraction of capital)."""
    days = pd.date_range(LO, HI - pd.Timedelta(days=1), freq="D", tz="UTC")
    daily, prev, events, log = [], set(), 0, []
    for m in pd.date_range(LO, HI - pd.Timedelta(days=1), freq="MS", tz="UTC"):
        pday = m - pd.Timedelta(days=1)
        if pday not in T.index:
            continue
        ok = [p for p in Y.columns if pd.notna(T.at[pday, p]) and T.at[pday, p] >= 20e6 and (pday - first[p]).days >= 90]
        trail = Y.loc[pday - pd.Timedelta(days=29):pday, ok].mean().dropna().sort_values(ascending=False)
        held = list(trail.index[:TOPK])
        ch = len(set(held) ^ prev)
        prev = set(held)
        alive = {p: True for p in held}
        log.append(f"    {m:%Y-%m}: " + ", ".join(f"{names.get(p, p[:8])} {trail[p]:.1f}%" for p in held))
        for j, d in enumerate([x for x in days if x.year == m.year and x.month == m.month]):
            r = []
            for p in held:
                if not alive[p]:
                    r.append(0.0)
                    continue
                t7 = T.loc[d - pd.Timedelta(days=7):d, p]
                if len(t7) > 1 and t7.iloc[-1] < 0.5 * t7.max():
                    alive[p] = False
                    events += 1
                    r.append(-stress_fn(p))
                    continue
                v = Y.at[d, p] if d in Y.index else np.nan
                r.append((v if pd.notna(v) else 0.0) / 100 / 365)
            c = ch * cost_frac / max(len(held), 1) if j == 0 else 0.0
            daily.append((d, (float(np.mean(r)) if r else 0.0) - c))
    s = pd.Series(dict(daily))
    print(f"{label}: universe {Y.shape[1]} pools; stress events {events}")
    for line in log[-3:]:
        print(line)
    pilot = ann(s[s.index >= PILOT])
    print(f"  Stage 1 (2026-08..10): {pilot:.2f}%/yr -> {'KILL' if pilot < KILL else 'continue'}")
    if pilot < KILL:
        print("  VERDICT: FAIL (Stage 1)\n")
        return
    h1, h2 = ann(s[s.index < MID]), ann(s[s.index >= MID])
    mon = s.groupby(s.index.strftime("%Y-%m")).sum() * 100
    print(f"  halves {h1:.2f}% / {h2:.2f}% on capital; worst month {mon.min():.2f}%; months negative {(mon < 0).sum()}; "
          f"${ann(s) * 100:,.0f}/yr on $10K, ${ann(s) * 400:,.0f}/yr on $40K")
    print(f"  VERDICT: {'PASS' if h1 >= BAR and h2 >= BAR else 'FAIL'}\n")


def hedged():
    pools = pd.read_parquet("data/public/hedged_pools.parquet").set_index("pool")
    ch = pd.read_parquet("data/public/hedged_charts.parquet")
    ch["day"] = ch["ts"].dt.floor("D")
    ch = ch.drop_duplicates(["pool", "day"])
    f = pd.read_parquet("data/public/hedged_hlfunding.parquet")
    f["day"] = pd.to_datetime(f["t"], unit="s", utc=True).dt.floor("D")
    F = f.groupby(["coin", "day"])["rate"].sum().mul(365 * 100)  # funding received by a short, annualised %
    ch["coin"] = ch["pool"].map(pools["coin"])
    ch["F"] = [F.get((c, d), np.nan) for c, d in zip(ch["coin"], ch["day"])]
    ch["y"] = ((ch["apyBase"].fillna(0) + 0.9 * ch["apyReward"].fillna(0)).clip(upper=500) + ch["F"]) / (4 / 3)
    ch = ch[ch["F"].notna()]
    names = {p: f"{pools.at[p, 'project']}/{pools.at[p, 'symbol']}" for p in pools.index}
    cost = 0.0005 + 0.00045 + 10 / SLOT
    for label, sel in (("#212 hedged staking", pools["category"].isin(STAKING)), ("#213 hedged reward farming (all mapped pools)", pools["category"].notna() | True)):
        ids = set(pools.index[sel])
        g = ch[ch["pool"].isin(ids)]
        if g.empty:
            print(f"{label}: no data\n")
            continue
        Y = g.pivot(index="day", columns="pool", values="y").sort_index()
        T = g.pivot(index="day", columns="pool", values="tvlUsd").sort_index().ffill(limit=3)
        rotate(Y, T, g.groupby("pool")["day"].min(), cost, lambda p: 0.20, label, names)


def corrloops():
    pools = pd.read_parquet("data/public/corrloop_pools.parquet")
    ch = pd.read_parquet("data/public/corrloop_charts.parquet")
    ch["day"] = pd.to_datetime(ch["day"], utc=True)
    ch = ch.drop_duplicates(["pool", "day"]).set_index(["pool", "day"])
    fam = {"ETH": {"STETH", "WSTETH", "RETH", "CBETH", "WEETH", "EZETH", "RSETH", "METH", "SFRXETH", "OSETH", "WBETH", "ETHX"},
           "SOL": {"JITOSOL", "MSOL", "JUPSOL", "BSOL", "INF", "BNSOL", "HSOL"}, "HYPE": {"KHYPE", "STHYPE"}, "AVAX": {"SAVAX"},
           "BNB": {"SLISBNB", "BNBX"}, "USD": {"SUSDE", "SUSDS", "SDAI", "SFRXUSD"}}
    base = {"ETH": {"WETH", "ETH"}, "SOL": {"SOL"}, "HYPE": {"HYPE", "WHYPE"}, "AVAX": {"AVAX", "WAVAX"}, "BNB": {"BNB", "WBNB"},
            "USD": {"USDC", "USDT", "USDT0", "USDS", "DAI"}}
    pools["SYM"] = pools["symbol"].str.upper()
    pairs = []
    for (proj, chain), g in pools.groupby(["project", "chain"]):
        for c in fam:
            sup = g[g["SYM"].isin(fam[c])]
            bor = g[g["SYM"].isin(base[c]) & (g.get("borrowable", True) != False)]  # noqa: E712
            for _, a in sup.iterrows():
                for _, b in bor.iterrows():
                    pairs.append((a["pool"], b["pool"], float(a.get("ltv") or 0), f"{proj}/{chain}:{a['SYM']}-{b['SYM']}"))
    print(f"#219 correlated-pair loops: {len(pairs)} pairs")
    cols, tv, names, kk = {}, {}, {}, {}
    for a, b, ltv, name in pairs:
        if a not in ch.index.get_level_values(0) or b not in ch.index.get_level_values(0):
            continue
        A, B = ch.loc[a], ch.loc[b]
        s = A["apyBase"].fillna(0) + 0.9 * A["apyReward"].fillna(0)
        bb = (B["apyBaseBorrow"] - 0.9 * B["apyRewardBorrow"].fillna(0))
        k = min(1 / (1 - 0.8 * min(max(ltv, 0), 0.95)), 6.0)
        roe = (s + (k - 1) * (s - bb)).dropna().clip(-300, 500)
        if roe.empty:
            continue
        key = f"{a}|{b}"
        cols[key], names[key], kk[key] = roe, name, k
        tv[key] = pd.concat([A["tvlUsd"], B["tvlUsd"]], axis=1).min(axis=1)
    if not cols:
        print("  no usable pairs\n")
        return
    Y = pd.DataFrame(cols).sort_index()
    T = pd.DataFrame(tv).sort_index().ffill(limit=3)
    first = Y.apply(lambda x: x.first_valid_index())
    rotate(Y, T, first, 20 / SLOT, lambda p: 0.10 * kk[p], "#219 correlated-pair loops", names)


def main() -> int:
    print(f"bar >= {BAR}%/yr on capital both halves; Stage 1 kill < {KILL}%\n")
    hedged()
    corrloops()
    return 0


if __name__ == "__main__":
    sys.exit(main())

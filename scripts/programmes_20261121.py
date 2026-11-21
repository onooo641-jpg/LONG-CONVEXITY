"""Named structural stablecoin programmes, buy-and-hold (docs/PREREG_PROGRAMMES_20261121.md, #210)."""
import pandas as pd

LO, HI, PILOT = pd.Timestamp("2024-11-01", tz="UTC"), pd.Timestamp("2026-11-01", tz="UTC"), pd.Timestamp("2026-08-01", tz="UTC")
PROG = {"Liquity v2 BOLD": "liquity-v2", "Felix feUSD": "felix-cdp", "Ethena sUSDe": "ethena-usde", "Falcon sUSDf": "falcon-finance",
        "Sky savings": "sky-lending", "Spark Savings": "spark-savings", "Usual bUSD0": "usual-usd0", "Hyperliquid Earn": "hyperliquid-earn",
        "Maple": "maple", "Pendle v2 stables": "pendle-v2"}
pools = pd.read_parquet("data/public/fallback_stable_pools.parquet")
ch = pd.read_parquet("data/public/fallback_stable_charts.parquet")
ch["day"] = ch["ts"].dt.floor("D")
ch = ch.drop_duplicates(["pool", "day"])
ch["y"] = (ch["apyBase"].fillna(0) + 0.9 * ch["apyReward"].fillna(0)).clip(upper=1000)
print("pass: >= 8.0%/yr both halves, no stress hit, >= 180 days; Stage 1 last 3 months < 4.0% -> KILL\n")
for name, proj in PROG.items():
    ids = pools.loc[pools.project == proj, "pool"]
    g = ch[ch.pool.isin(ids) & (ch.day >= LO) & (ch.day < HI)]
    if g.empty:
        print(f"{name}: no data in window\n"); continue
    Y = g.pivot(index="day", columns="pool", values="y").sort_index()
    T = g.pivot(index="day", columns="pool", values="tvlUsd").sort_index().ffill(limit=3)
    alive, r, hits = {p: True for p in Y.columns}, [], 0
    for d in Y.index:
        vals = []
        for p in Y.columns:
            if not alive[p] or pd.isna(Y.at[d, p]):
                continue
            t7 = T.loc[d - pd.Timedelta(days=7):d, p]
            if len(t7) > 1 and t7.iloc[-1] < 0.5 * t7.max():
                alive[p] = False; hits += 1; vals.append(-0.20 * 365 * 100); continue
            vals.append(Y.at[d, p])
        r.append((d, sum(vals) / len(vals) if vals else 0.0))
    s = pd.Series(dict(r)) / 100 / 365
    days = (s.index.max() - s.index.min()).days
    mid = s.index.min() + (s.index.max() - s.index.min()) / 2
    ann = lambda x: float(x.mean() * 365 * 100)
    pilot, h1, h2 = ann(s[s.index >= PILOT]), ann(s[s.index <= mid]), ann(s[s.index > mid])
    ok = days >= 180 and h1 >= 8 and h2 >= 8 and hits == 0 and pilot >= 4
    why = [w for w, bad in (("Stage 1 kill", pilot < 4), ("< 180 days", days < 180), ("half 1 < 8%", h1 < 8), ("half 2 < 8%", h2 < 8), (f"{hits} stress hit(s)", hits > 0)) if bad]
    print(f"{name}: {len(Y.columns)} pool(s), {days} days from {s.index.min().date()}; last 3 mo {pilot:.2f}%; halves {h1:.2f}% / {h2:.2f}%; "
          f"${ann(s) * 100:,.0f}/yr on $10K -> {'PASS' if ok else 'FAIL (' + '; '.join(why) + ')'}\n")

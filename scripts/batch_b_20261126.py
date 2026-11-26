"""Batch B #422-#428 (docs/PREREG_BATCH_B_20261126.md).

    uv run python -m scripts.batch_b_20261126 | tee docs/jx_runs/batch_b_20261126.txt
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

PUB = Path(__file__).resolve().parent.parent / "data" / "public"
FEE = 0.00045


def tstat(r):
    r = pd.Series(r).dropna()
    return r.mean() / (r.std(ddof=1) / np.sqrt(len(r))) if len(r) > 1 else np.nan


def hl():
    cd = pd.read_parquet(PUB / "uncharted_385_candles.parquet")
    cd["day"] = pd.to_datetime(cd["t"], unit="ms", utc=True).dt.normalize()
    C = cd.drop_duplicates(["coin", "day"]).pivot(index="day", columns="coin", values="c").sort_index()
    fu = pd.read_parquet(PUB / "hl_funding.parquet")
    fu["ts"] = pd.to_datetime(fu["time"], unit="ms", utc=True)
    return C, fu


def charts():
    p = PUB / "batchb_charts.parquet"
    if not p.exists():
        return None, None
    pools = {x["pool"]: x for x in json.loads((PUB / "batchb_pools.json").read_text())}
    ch = pd.read_parquet(p)
    ch["day"] = pd.to_datetime(ch["ts"], utc=True).dt.normalize()
    return pools, ch


def part422(pools, ch):
    print("#### #422 year-one house vaults on newer perp DEXes (DefiLlama APY)")
    if ch is None:
        print("  data not fetched yet")
        return
    rows = []
    for pool, g in ch.groupby("pool"):
        p = pools[pool]
        if p["project"].lower().startswith(("liquity", "hyperlend", "hypurr")):
            continue
        g = g.sort_values("day")
        if (g["day"].iloc[-1] - g["day"].iloc[0]).days < 300:
            continue
        s = g["day"].iloc[0]
        tvl3 = g[g["day"] <= s + pd.Timedelta(days=90)]["tvlUsd"].iloc[-1] if len(g) else 0
        if not tvl3 or tvl3 < 5e6:
            continue
        y1 = g[g["day"] < s + pd.Timedelta(days=365)]["apy"].mean()
        rows.append({"project": p["project"], "chain": p["chain"], "symbol": p["symbol"], "start": s.date(), "tvl_m3": tvl3 / 1e6, "apy_y1": y1})
    t = pd.DataFrame(rows)
    if t.empty:
        print("  no vault with >= 300 days and >= $5M TVL at month 3")
        return
    t["start"] = pd.to_datetime(t["start"])
    print(t.sort_values("start").to_string(index=False, float_format=lambda x: f"{x:8.1f}"))
    old, new = t[t["start"] < "2025-01-01"], t[t["start"] >= "2025-01-01"]
    m1 = old["apy_y1"].median() if len(old) else np.nan
    print(f"  Stage 1 (launched before 2025): {len(old)} vaults, median first-year APY {m1:.1f}%")
    s1 = not (pd.isna(m1) or m1 < 15)
    print(f"  STAGE 1 VERDICT: {'survives (kill-only)' if s1 else 'KILL'}")
    m2 = new["apy_y1"].median() if len(new) else np.nan
    print(f"  Stage 2 (launched 2025+, out-of-sample): {len(new)} vaults, median first-year APY {m2:.1f}%")
    ok = s1 and len(new) >= 3 and m2 >= 30
    print(f"  STAGE 2 VERDICT: {'PASS' if ok else ('FAIL' if s1 else 'not judged — context')}")


def part423(C, fu):
    print("\n#### #423 funding-cap crowding short (HL funding >= 0.05%/h for 6 h)")
    rows = []
    for coin, g in fu.groupby("coin"):
        if coin not in C.columns or coin == "BTC":
            continue
        g = g.sort_values("ts")
        hot = (g["rate"] >= 0.0005).astype(int)
        run = hot.groupby((hot != hot.shift()).cumsum()).cumsum()
        trig = g.loc[(run == 6) & (hot == 1), "ts"]
        busy = None
        for ts in trig:
            d = (ts + pd.Timedelta(days=1)).normalize() - pd.Timedelta(seconds=0)
            d = ts.normalize()
            if busy is not None and d <= busy:
                continue
            ex = d + pd.Timedelta(days=3)
            if d not in C.index or ex not in C.index or pd.isna(C.at[d, coin]) or pd.isna(C.at[ex, coin]):
                continue
            w = g[(g["ts"] > d + pd.Timedelta(days=1)) & (g["ts"] <= ex + pd.Timedelta(days=1))]["rate"].sum()
            wb = fu[(fu["coin"] == "BTC") & (fu["ts"] > d + pd.Timedelta(days=1)) & (fu["ts"] <= ex + pd.Timedelta(days=1))]["rate"].sum()
            ret = -(C.at[ex, coin] / C.at[d, coin] - 1) + (C.at[ex, "BTC"] / C.at[d, "BTC"] - 1) + w - wb - 4 * FEE
            rows.append({"day": d, "coin": coin, "ret": ret})
            busy = ex
    t = pd.DataFrame(rows)
    if t.empty:
        print("  no events")
        return

    def seg(x, label):
        r = x["ret"]
        print(f"  {label}: events {len(r)}, mean {r.mean():.2%}, median {r.median():.2%}, t {tstat(r):.2f}, win {(r > 0).mean():.0%}, worst {r.min():.1%}")
        return len(r), r.mean(), tstat(r)
    n1, m1, t1 = seg(t[t["day"] < "2025-01-01"], "Stage 1 (2024)")
    s1 = n1 >= 20 and not (m1 < 0.01 or t1 < 1)
    v1 = "survives (kill-only)" if s1 else ("not testable (< 20 events)" if n1 < 20 else "KILL")
    print(f"  STAGE 1 VERDICT: {v1}")
    n2, m2, t2 = seg(t[t["day"] >= "2025-01-01"], "Stage 2 (out-of-sample 2025-01..2026-10)")
    ok = s1 and n2 >= 20 and m2 >= 0.02 and t2 >= 2
    print(f"  STAGE 2 VERDICT: {'PASS' if ok else ('FAIL' if s1 else 'not judged — context')}")


def part424(pools, ch):
    print("\n#### #424 Liquity v2 stability pools (DefiLlama APY)")
    if ch is None:
        print("  data not fetched yet")
        return
    lq = [p for p, v in pools.items() if v["project"].lower().startswith("liquity-v2")]
    res = []
    for p in lq:
        g = ch[ch["pool"] == p].sort_values("day")
        if len(g) < 60:
            continue
        h = len(g) // 2
        res.append((pools[p]["symbol"], g["apy"].iloc[:h].mean(), g["apy"].iloc[h:].mean(), g["tvlUsd"].iloc[-1]))
    for r in res:
        print(f"  {r[0]}: first half {r[1]:.1f}%, second half {r[2]:.1f}%, TVL now ${r[3] / 1e6:.1f}M")
    if not res:
        print("  no Liquity v2 pools with >= 60 days: not testable")
        return
    s1 = np.mean([r[1] for r in res]) >= 10
    print(f"  STAGE 1 VERDICT: {'survives (kill-only)' if s1 else 'KILL'}")
    ok = s1 and len(res) >= 2 and np.mean([r[2] for r in res]) >= 15
    print(f"  STAGE 2 VERDICT: {'PASS' if ok else ('FAIL' if s1 else 'not judged — context')}")


def part425():
    print("\n#### #425 #389 wick bids on Orderly-network perps")
    p = PUB / "batchb_orderly_1d.parquet"
    if not p.exists():
        print("  data not fetched yet")
        return
    from scripts.wick_scale_20261125 import fills_daily, pot_scale
    d = pd.read_parquet(p)
    if d.empty:
        print("  no candles: not testable")
        return
    d["day"] = pd.to_datetime(d["t"], unit="s", utc=True).dt.normalize()
    d["usdvol"] = d["v"] * d["c"]
    d = d.drop_duplicates(["coin", "day"]).sort_values(["coin", "day"])[["coin", "day", "o", "h", "l", "c", "usdvol"]]
    f = fills_daily(d)
    span = (d["day"].max() - d["day"].min()).days / 365
    if f.empty:
        print("  no fills")
        return
    f["pnl"] = pot_scale(f, "day")
    r = f["ret"]
    py = f["pnl"].sum() / span
    print(f"  Orderly: {d['coin'].nunique()} perps {d['day'].min().date()}..{d['day'].max().date()}; fills {len(f)}, mean {r.mean():.2%}, t {tstat(r):.2f}, ${py:,.0f}/yr")
    ok = r.mean() >= 0.005 and tstat(r) >= 3 and py >= 3000
    print(f"  STAGE 2 VERDICT: {'PASS' if ok else 'FAIL'}")


def part426(pools, ch):
    print("\n#### #426 cascade-day lending (HyperLend / HypurrFi stablecoin supply APY)")
    if ch is None:
        print("  data not fetched yet")
        return
    sel = [p for p, v in pools.items() if v["project"].lower().startswith(("hyperlend", "hypurr")) and str(v["symbol"]).upper() in ("USDC", "USDT0", "USDE", "USDHL", "USDH")]
    if not sel:
        print("  no stablecoin pools found: not testable")
        return
    cd = pd.read_parquet(PUB / "uncharted_385_candles.parquet")
    cd["day"] = pd.to_datetime(cd["t"], unit="ms", utc=True).dt.normalize()
    cd = cd.drop_duplicates(["coin", "day"]).sort_values(["coin", "day"])
    cd["prev"] = cd.groupby("coin")["c"].shift()
    share = (cd["l"] <= cd["prev"] * 0.85).groupby(cd["day"]).mean()
    casc = set(share[share >= 0.25].index)
    win = set(d + pd.Timedelta(days=k) for d in casc for k in range(4))
    a = ch[ch["pool"].isin(sel)].groupby("day")["apy"].mean()
    for label, lo, hi in (("Stage 1 (2025)", "2025-01-01", "2025-12-31"), ("Stage 2 (2026)", "2026-01-01", "2026-12-31")):
        x = a[(a.index >= lo) & (a.index <= hi)]
        cw = x[x.index.isin(win)]
        print(f"  {label}: days {len(x)}, average APY {x.mean():.1f}%, cascade-window days {len(cw)}, their APY {cw.mean():.1f}%")
    x1 = a[(a.index >= "2025-01-01") & (a.index <= "2025-12-31")]
    s1 = len(x1[x1.index.isin(win)]) > 0 and x1[x1.index.isin(win)].mean() >= 2 * x1.mean()
    print(f"  STAGE 1 VERDICT: {'survives (kill-only)' if s1 else 'KILL'}")


def part427(C, fu):
    print("\n#### #427 Hyperliquid spot-perp carry (long spot / short perp when trailing funding > 0)")
    sp = pd.read_parquet(PUB / "fivehigh_hl_spot_1d.parquet")
    sp["day"] = pd.to_datetime(sp["t"], unit="ms", utc=True).dt.normalize()
    sp["tok"] = sp["label"].str.split("/").str[0]
    sp = sp[sp["label"].str.endswith("/USDC")]
    S = sp.drop_duplicates(["tok", "day"]).pivot(index="day", columns="tok", values="c")
    both = [t for t in S.columns if t in C.columns]
    fu = fu.copy()
    fu["day"] = fu["ts"].dt.normalize()
    F = fu.groupby(["day", "coin"])["rate"].sum().unstack()
    print(f"  tokens with HL spot and perp: {both}")
    rets = []
    for tok in both:
        s, p = S[tok], C[tok]
        f = F[tok] if tok in F else pd.Series(dtype=float)
        df = pd.concat([s.rename("s"), p.rename("p"), f.rename("f")], axis=1).dropna(subset=["s", "p"])
        if len(df) < 120:
            continue
        df["sig"] = (df["f"].fillna(0).rolling(7).sum().shift(1) > 0).astype(int)
        df["r"] = df["sig"] * (df["s"].pct_change() - df["p"].pct_change() + df["f"].fillna(0)) - df["sig"].diff().abs().fillna(0) * (0.0007 + FEE)
        rets.append(df["r"].rename(tok))
    if not rets:
        print("  not enough overlapping history")
        return
    port = pd.concat(rets, axis=1).mean(axis=1).dropna()

    def seg(r, label):
        if r.empty:
            print(f"  {label}: no days")
            return np.nan, np.nan
        eq = (1 + r).cumprod()
        ann = eq.iloc[-1] ** (365 / len(r)) - 1
        dd = float((eq / eq.cummax() - 1).min())
        print(f"  {label}: days {len(r)}, annualised {ann:.1%}, worst drawdown {dd:.1%}, t {tstat(r):.2f}")
        return ann, dd
    a1, _ = seg(port[(port.index >= "2024-06-01") & (port.index <= "2025-06-30")], "Stage 1 (2024-06..2025-06)")
    s1 = not (pd.isna(a1) or a1 < 0.10)
    print(f"  STAGE 1 VERDICT: {'survives (kill-only)' if s1 else 'KILL'}")
    a2, d2 = seg(port[(port.index >= "2025-07-01") & (port.index <= "2026-10-31")], "Stage 2 (out-of-sample 2025-07..2026-10)")
    ok = s1 and a2 >= 0.20 and d2 >= -0.15
    print(f"  STAGE 2 VERDICT: {'PASS' if ok else ('FAIL' if s1 else 'not judged — context')}")


def main():
    print("===== Batch B #422-#428")
    C, fu = hl()
    pools, ch = charts()
    part422(pools, ch)
    part423(C, fu)
    part424(pools, ch)
    part425()
    part426(pools, ch)
    part427(C, fu)
    print("\n#### #428 new-chain stablecoin launch premiums: not testable with free data (pre-registered)")


if __name__ == "__main__":
    main()

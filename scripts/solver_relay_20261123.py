"""#361 CoW solver rewards and #362 Across relayer fees (docs/PREREG_SOLVER_RELAY_20261123.md).

    uv run python -m scripts.solver_relay_20261123 | tee docs/jx_runs/solver_relay_20261123.txt
Reads data/public/solverrelay_* (fetched by Actions jobs cow361 / across362).
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

PUB = Path(__file__).resolve().parent.parent / "data" / "public"
BAR = 15_000.0
STABLE = {"USDC", "USDC.E", "USDBC", "USDT", "USDT0", "USD₮0", "DAI", "USDS", "USDZ", "USDT.E"}


def _price_series(pts):
    pairs = [(x["timestamp"], x["price"]) if isinstance(x, dict) else (x[0], x[1]) for x in (pts or [])]
    s = pd.Series({pd.Timestamp(int(t), unit="s", tz="UTC").normalize(): float(p) for t, p in pairs}) if pairs else pd.Series(dtype=float)
    return s[~s.index.duplicated()].sort_index()


def cow():
    print("===== #361 CoW solver rewards (COW sent from the Solver Payouts Safe)")
    meta = json.loads((PUB / "solverrelay_cow_meta.json").read_text())
    for url, pg in meta["pages"].items():
        flags = {k[:-12]: v for k, v in pg.items() if k.endswith("|in_raw_html")}
        print(f"  page {url}: {pg.get('error') or flags}")
    print(f"  safe has code: {meta.get('safe_has_code')}; blocks {meta['b0']}..{meta['b1']}; missed blocks {meta['missed_blocks']}; "
          f"transfers {meta['n_transfers']} in {meta['n_blocks']} blocks")
    print(f"  source {meta.get('source', 'rpc_scan')}; complete {meta.get('complete')}")
    span = (meta.get("b1") or 0) - (meta.get("b0") or 0)
    if meta.get("complete") is False or meta.get("missed_blocks") is None or meta["missed_blocks"] > 0.01 * max(span, 1):
        print("  coverage incomplete (> 1% of blocks missed or listing unfinished): no verdict")
        return
    df = pd.read_parquet(PUB / "solverrelay_cow.parquet")
    if df.empty:
        print("  no transfers: address or data problem; no verdict")
        return
    px = _price_series(meta["cow_price"])
    df["day"] = pd.to_datetime(df["ts"], unit="s", utc=True).dt.normalize()
    df["px"] = px.reindex(df["day"]).ffill().bfill().to_numpy() if len(px) else np.nan
    if df["px"].isna().any() and len(px):
        df["px"] = df["day"].map(lambda d: px.asof(d))
    df["usd"] = df["cow"] * df["px"]
    df["week"] = df["day"].dt.to_period("W-MON")
    print(f"  payout days: {df['day'].nunique()}; first {df['day'].min().date()}, last {df['day'].max().date()}; total COW {df['cow'].sum():,.0f}, "
          f"USD {df['usd'].sum():,.0f}")
    end = df["day"].max()

    def period(a, b, label):
        d = df[(df["day"] >= pd.Timestamp(a, tz="UTC")) & (df["day"] < pd.Timestamp(b, tz="UTC"))]
        days = (min(pd.Timestamp(b, tz="UTC"), end + pd.Timedelta(days=1)) - pd.Timestamp(a, tz="UTC")).days
        g = d.groupby("to").agg(usd=("usd", "sum"), weeks=("week", "nunique"))
        g = g[g["weeks"] >= 4].sort_values("usd", ascending=False)
        g["per_year"] = g["usd"] * 365 / days
        print(f"  {label} ({a}..{b}, {days} days): solvers paid in >= 4 weeks: {len(g)}; total ${g['usd'].sum():,.0f}")
        for k, (addr, r) in enumerate(g.head(15).iterrows(), 1):
            print(f"    {k:2d}. {addr}  ${r['per_year']:>12,.0f}/yr  ({int(r['weeks'])} weeks)")
        return g

    g1 = period("2026-01-01", "2026-11-01", "Stage 1")
    rest = g1["per_year"].iloc[5:]
    med = float(rest.median()) if len(rest) else 0.0
    print(f"  Stage 1: median solver outside the top 5 = ${med:,.0f}/yr (n {len(rest)}); 10th-ranked "
          f"${(g1['per_year'].iloc[9] if len(g1) >= 10 else 0):,.0f}/yr")
    if med < BAR:
        print("  STAGE 1 VERDICT: KILL (median outside the top 5 < $15,000/yr gross)")
    else:
        print("  STAGE 1 VERDICT: survives (kill-only)")
    ok = med >= BAR
    for a, b in (("2024-01-01", "2025-01-01"), ("2025-01-01", "2026-01-01"), ("2026-01-01", "2026-11-01")):
        g = period(a, b, f"Stage 2 year {a[:4]}")
        tenth = float(g["per_year"].iloc[9]) if len(g) >= 10 else 0.0
        print(f"    10th-ranked ${tenth:,.0f}/yr; after 15% service fee ${tenth * 0.85:,.0f}/yr")
        ok = ok and tenth * 0.85 >= BAR
    print(f"  STAGE 2 VERDICT: {'worth building a shadow solver' if ok else 'FAIL'}"
          + ("" if med >= BAR else " (Stage 1 already killed; Stage 2 shown as context only)"))


def across():
    print("===== #362 Across relayer fees, Base + Arbitrum, 2026-10-01..2026-10-31")
    meta = json.loads((PUB / "solverrelay_across_meta.json").read_text())
    for url, pg in meta["pages"].items():
        flags = {k[:12]: v for k, v in pg.items() if k.endswith("|in_raw_html")}
        print(f"  page {url}: {pg.get('error') or flags}")
    eth, btc = _price_series(meta["eth_price"]), _price_series(meta["btc_price"])
    frames = []
    for chain in ("base", "arbitrum"):
        m = meta.get(chain, {})
        print(f"  {chain}: code {m.get('has_code')}; blocks {m.get('b0')}..{m.get('b1')}; missed {m.get('missed_blocks')}; "
              f"probe topic0 {m.get('probe_topic0')}; error {m.get('error')}")
        f = PUB / f"solverrelay_fills_{chain}.parquet"
        if not f.exists():
            continue
        d = pd.read_parquet(f)
        if d.empty:
            continue
        ts = np.array(m["ts_sample"], dtype=float)
        d["ts"] = np.interp(d["block"].to_numpy(dtype=float), ts[:, 0], ts[:, 1])
        d["day"] = pd.to_datetime(d["ts"], unit="s", utc=True).dt.normalize()
        tok = {a: (str(v[0]).upper(), v[1]) for a, v in m["tokens"].items()}
        d["sym"] = d["out_tok"].map(lambda a: tok.get(a, ("?", None))[0])
        d["dec"] = d["out_tok"].map(lambda a: tok.get(a, ("?", None))[1])
        d["chain"] = chain
        frames.append(d)
    if not frames:
        print("  no fills: no verdict")
        return
    d = pd.concat(frames, ignore_index=True)
    n0 = len(d)
    d = d[d["ftype"] != 2]
    print(f"  fills {n0:,}; slow fills excluded {n0 - len(d):,}")
    d = d[d["dec"].notna()].copy()
    d["dec"] = d["dec"].astype(int)
    in_dec = d["dec"].copy()
    bsc = (d["origin"] == 56) & d["sym"].isin(["USDC", "USDT"])
    in_dec[bsc] = 18
    d["in_u"] = d["in_amt"] / 10.0 ** in_dec
    d["out_u"] = d["out_amt"] / 10.0 ** d["dec"]
    d["ratio"] = d["in_u"] / d["out_u"].replace(0, np.nan)
    bad = ~d["ratio"].between(0.9, 1.1)
    print(f"  excluded for token mismatch (ratio outside 0.9-1.1): {int(bad.sum()):,}")
    d = d[~bad].copy()

    def usd_px(r_sym, day):
        if r_sym in STABLE or r_sym.startswith("USD"):
            return 1.0
        if r_sym in ("WETH", "ETH"):
            return float(eth.asof(day)) if len(eth) else np.nan
        if r_sym in ("WBTC", "CBBTC", "TBTC"):
            return float(btc.asof(day)) if len(btc) else np.nan
        return np.nan

    keys = d[["sym", "day"]].drop_duplicates()
    pmap = {(s, dd): usd_px(s, dd) for s, dd in keys.itertuples(index=False)}
    d["px"] = [pmap[(s, dd)] for s, dd in zip(d["sym"], d["day"])]
    unpriced = d["px"].isna()
    print(f"  fills with unpriced tokens dropped: {int(unpriced.sum()):,} ({sorted(d.loc[unpriced, 'sym'].unique())[:10]})")
    d = d[~unpriced].copy()
    d["vol"] = d["out_u"] * d["px"]
    d["spread"] = (d["in_u"] - d["out_u"]) * d["px"]
    days = 31
    print(f"  priced fills {len(d):,}; volume ${d['vol'].sum():,.0f}; spread ${d['spread'].sum():,.0f} "
          f"({1e4 * d['spread'].sum() / d['vol'].sum():.2f} bps); by token: "
          + ", ".join(f"{s} {n:,}" for s, n in d["sym"].value_counts().head(6).items()))
    g = d.groupby("relayer").agg(fills=("vol", "size"), vol=("vol", "sum"), spread=("spread", "sum"),
                                 excl=("excl", "mean")).sort_values("spread", ascending=False)
    g["per_year"] = g["spread"] * 365 / days
    g["bps"] = 1e4 * g["spread"] / g["vol"]
    print(f"  relayers: {len(g)}; top 5 share of spread {g['spread'].head(5).sum() / g['spread'].sum():.1%}")
    for k, (a, r) in enumerate(g.head(15).iterrows(), 1):
        print(f"    {k:2d}. {a}  fills {int(r['fills']):>7,}  vol ${r['vol']:>14,.0f}  {r['bps']:6.2f} bps  ${r['per_year']:>11,.0f}/yr upper bound"
              f"  exclusive {r['excl']:.0%}")
    sixth = float(g["per_year"].iloc[5]) if len(g) >= 6 else 0.0
    small = d[d["vol"] <= BAR]
    med_bps = float((1e4 * small["spread"] / small["vol"]).median()) if len(small) else 0.0
    print(f"  Stage 1 (a): 6th-ranked relayer ${sixth:,.0f}/yr upper bound (bar $15,000)")
    print(f"  Stage 1 (b): median spread on fills <= $15K: {med_bps:.2f} bps (bar 2 bps); fills <= $15K {len(small):,} "
          f"(${small['vol'].sum():,.0f})")
    top5 = set(g.index[:5])
    sm_out = small[~small["relayer"].isin(top5)]
    print(f"  context: fills <= $15K won outside the top 5: {len(sm_out):,} ({len(sm_out) / max(1, len(small)):.1%}); their median "
          f"{float((1e4 * sm_out['spread'] / sm_out['vol']).median()) if len(sm_out) else 0:.2f} bps")
    for chain in ("base", "arbitrum"):
        c = d[d["chain"] == chain]
        if len(c):
            print(f"  context {chain}: fills {len(c):,}, volume ${c['vol'].sum():,.0f}, spread ${c['spread'].sum():,.0f}, relayers "
                  f"{c['relayer'].nunique()}")
    kill = sixth < BAR or med_bps < 2.0
    print(f"  STAGE 1 VERDICT: {'KILL' if kill else 'survives (kill-only)'}")


if __name__ == "__main__":
    for fn in (cow, across):
        try:
            fn()
        except FileNotFoundError as e:
            print(f"  missing data: {e}")

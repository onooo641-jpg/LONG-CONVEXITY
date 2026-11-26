"""#417 deBridge DLN takers and #418 UniswapX open fillers on Base: newcomer income by cohort (docs/PREREG_SOLVERS_20261125.md).

    uv run python -m scripts.solvers_20261125 | tee docs/jx_runs/solvers_20261125.txt
"""
from __future__ import annotations

import gzip
import json
from pathlib import Path

import numpy as np
import pandas as pd

PUB = Path(__file__).resolve().parent.parent / "data" / "public"
INFRA, BAR, KILL_BAR = 3000.0, 15_000.0, 5_000.0
WETH = "0x4200000000000000000000000000000000000006"


def verdict(cohorts):
    meds = {}
    for name, v in cohorts.items():
        v = [x for x in v if x is not None]
        meds[name] = (len(v), float(np.median(v)) if v else np.nan)
        print(f"  cohort {name}: newcomers {len(v)}, median annualised net ${meds[name][1]:,.0f}" if v else f"  cohort {name}: no newcomers")
    ok = all(n >= 3 and m >= BAR for n, m in meds.values())
    dead = all((np.isnan(m) or m < KILL_BAR) for _, m in meds.values())
    return "PASS" if ok else ("KILL" if dead else "inconclusive")


def part418():
    print("#### #418 UniswapX open fillers on Base (Priority reactor): newcomer income")
    mp = PUB / "solvers_base418_meta.json"
    if not mp.exists():
        print("  data not fetched yet (job ubase418)")
        return
    meta = json.loads(mp.read_text())
    tr = pd.read_parquet(PUB / "solvers_base418_transfers.parquet")
    gas = pd.read_parquet(PUB / "solvers_base418_gas.parquet")
    series = {}
    for tkn, pts in meta["hourly"].items():
        if pts:
            s = pd.Series({pd.Timestamp(int(p["timestamp"]), unit="s", tz="UTC").floor("h"): float(p["price"]) for p in pts}).sort_index()
            series[tkn] = s[~s.index.duplicated()]
    dec = meta["decimals"]

    def usd(tkn, raw, t):
        s, dd = series.get(tkn), dec.get(tkn)
        if s is None or dd is None:
            return np.nan
        px = s.asof(pd.Timestamp(t, unit="s", tz="UTC").floor("h"))
        return int(raw) / 10 ** dd * px if pd.notna(px) else np.nan
    tr["usd"] = [usd(a, b, c) for a, b, c in zip(tr["token"], tr["amount_raw"], tr["t"])]
    eth = series.get(WETH)
    gas["usd"] = [g / 1e18 * (eth.asof(pd.Timestamp(t, unit="s", tz="UTC").floor("h")) if eth is not None else np.nan)
                  for g, t in zip(gas["gas_wei"], gas["t"])]
    per = tr.groupby(["filler", "tx"]).apply(lambda g: pd.Series({
        "in_usd": g.loc[g["dir"] == "in", "usd"].sum(min_count=1), "out_usd": g.loc[g["dir"] == "out", "usd"].sum(min_count=1)}),
        include_groups=False).reset_index()
    per = per.merge(gas[["tx", "usd"]].rename(columns={"usd": "gas_usd"}), on="tx", how="left")
    per = per.dropna(subset=["in_usd", "out_usd"])
    per["net"] = per["in_usd"] - per["out_usd"] - per["gas_usd"].fillna(0)
    per = per[per["in_usd"] > 0]
    per = per[(per["net"].abs() / per["in_usd"]) < 0.05]  # drop mispriced transfers (> 5% of the trade)
    first = meta["first"]
    coh = {"A (2025-11-15..2026-03-31)": [], "B (2026-04-01..2026-07-31)": []}
    rows = []
    for f, g in per.groupby("filler"):
        ft = pd.Timestamp(first[f], unit="s", tz="UTC")
        n90 = meta["fills_90d"].get(f, 0)
        if len(g) < 30:
            continue
        ann = g["net"].mean() * n90 * 365 / 90 - INFRA
        key = "A (2025-11-15..2026-03-31)" if pd.Timestamp("2025-11-15", tz="UTC") <= ft <= pd.Timestamp("2026-03-31", tz="UTC") else (
            "B (2026-04-01..2026-07-31)" if pd.Timestamp("2026-04-01", tz="UTC") <= ft <= pd.Timestamp("2026-07-31", tz="UTC") else None)
        rows.append({"filler": f[:12], "first": ft.date(), "cohort": (key or "other")[:1], "sampled": len(g), "fills_90d": n90,
                     "net_per_fill": g["net"].mean(), "gas_per_fill": g["gas_usd"].mean(), "volume_per_fill": g["in_usd"].mean(), "ann_net": ann})
        if key:
            coh[key].append(ann)
    t = pd.DataFrame(rows).sort_values("first")
    pd.set_option("display.width", 220)
    print(f"  newcomers in data: {len(meta['newcomers'])}; with >= 30 priced sampled fills: {len(t)}")
    if len(t):
        print(t.to_string(index=False, float_format=lambda x: f"{x:10.2f}"))
    print(f"  STAGE VERDICT (#418): {verdict(coh)}")


def part417():
    print("\n#### #417 deBridge DLN takers: newcomer income (sampled order blocks, addendum)")
    p = PUB / "solvers_dln_sample.json.gz"
    if not p.exists():
        print("  sampled orders not fetched yet (job udln2)")
        return
    with gzip.open(p, "rt") as f:
        orders = json.load(f)
    px = pd.read_parquet(PUB / "solvers_dln_prices.parquet")
    px["day"] = pd.to_datetime(px["t"], unit="s", utc=True).dt.normalize()
    P = px.drop_duplicates(["id", "day"]).pivot(index="day", columns="id", values="price").sort_index()
    sym_id = {"ETH": "ethereum", "WETH": "ethereum", "BNB": "binancecoin", "WBNB": "binancecoin", "SOL": "solana", "WSOL": "solana",
              "BTC": "bitcoin", "WBTC": "bitcoin", "CBBTC": "bitcoin", "BTCB": "bitcoin", "AVAX": "avalanche-2", "WAVAX": "avalanche-2",
              "POL": "polygon-ecosystem-token", "WPOL": "polygon-ecosystem-token", "MATIC": "matic-network", "WMATIC": "matic-network"}
    stable = {"USDC", "USDT", "DAI", "USDC.E", "USDBC", "USDT0", "USD₮0", "USDT.E", "BUSD"}
    native = {1: "ethereum", 10: "ethereum", 42161: "ethereum", 8453: "ethereum", 59144: "ethereum", 56: "binancecoin",
              7565164: "solana", 43114: "avalanche-2", 137: "polygon-ecosystem-token"}

    def price(sym, day):
        sym = (sym or "").upper()
        if sym in stable:
            return 1.0
        g = sym_id.get(sym)
        if g is None or g not in P:
            return np.nan
        v = P[g].asof(day)
        return float(v) if pd.notna(v) else np.nan

    def sv(x, *ks):
        for k in ks:
            x = (x or {}).get(k)
        return x.get("stringValue") if isinstance(x, dict) else x
    rows, skipped = [], 0
    for o in orders:
        g, t = o.get("giveOfferWithMetadata") or {}, o.get("takeOfferWithMetadata") or {}
        ts = int(o.get("creationTimestamp") or 0)
        day = pd.Timestamp(ts, unit="s", tz="UTC").normalize()
        pg, pt = price(g.get("symbol"), day), price(t.get("symbol"), day)
        if pd.isna(pg) or pd.isna(pt):
            skipped += 1
            continue
        try:
            ga = int(sv(g, "finalAmount")) / 10 ** int(g.get("decimals"))
            ta = int(sv(t, "finalAmount")) / 10 ** int(t.get("decimals"))
            pf = int(sv(o, "finalPercentFee") or 0) / 10 ** int(g.get("decimals"))
            ff = int(sv(o, "fixFee") or 0) / 1e18
        except (TypeError, ValueError):
            skipped += 1
            continue
        chain = int(sv(g, "chainId") or 0)
        pn = price({"ethereum": "ETH", "binancecoin": "BNB", "solana": "SOL", "avalanche-2": "AVAX", "polygon-ecosystem-token": "POL"}.get(native.get(chain, ""), ""), day)
        give, take = ga * pg, ta * pt
        margin = give - take - pf * pg - (ff * pn if pd.notna(pn) else 0.0)
        if give <= 0 or abs(margin) / give > 0.05:
            skipped += 1
            continue
        rows.append({"offset": o.get("_offset"), "ts": ts, "taker": (sv(o, "unlockAuthorityDst") or "?").lower(), "give": give, "margin": margin})
    d = pd.DataFrame(rows)
    print(f"  sampled orders {len(orders)}; priced {len(d)}; excluded (unpriced token or > 5% mismatch) {skipped}")
    if d.empty:
        print("  STAGE VERDICT (#417): not testable (nothing priced)")
        return
    blk = d.groupby("offset").agg(n=("ts", "size"), t=("ts", "median"))
    blk_all = pd.Series({off: sum(1 for o in orders if o.get("_offset") == off) for off in blk.index})
    gap = pd.Series(sorted(blk.index)).diff().shift(-1).fillna(25000).values
    w = pd.Series(gap, index=sorted(blk.index)) / blk_all.reindex(sorted(blk.index)).values  # orders represented per sampled order
    d["w"] = d["offset"].map(w)
    d["day"] = pd.to_datetime(d["ts"], unit="s", utc=True)
    print(f"  blocks {len(blk)}; time span {d['day'].min().date()}..{d['day'].max().date()}; median weight {w.median():.1f} orders per sampled order")
    print(f"  volume-weighted margin {1e4 * (d['margin'] * d['w']).sum() / (d['give'] * d['w']).sum():.2f} bps; estimated annual margin pool "
          f"${(d['margin'] * d['w']).sum() / max((d['day'].max() - d['day'].min()).days, 1) * 365:,.0f}/yr")
    tot = (d["margin"] * d["w"]).groupby(d["taker"]).sum().sort_values(ascending=False)
    top3 = float(tot.head(3).sum() / tot[tot > 0].sum()) if (tot > 0).any() else np.nan
    print(f"  takers seen: {len(tot)}; top-3 share of positive margin {top3:.0%}")
    first = d.groupby("taker")["day"].min()
    start = d["day"].min()
    coh = {"A (first seen 2024)": [], "B (first seen 2025)": []}
    out = []
    for tk, ft in first.items():
        if ft < start + pd.Timedelta(days=30):
            continue  # present at the start of the sample: incumbent, not a newcomer
        fb = d[(d["taker"] == tk) & (d["day"] == ft)]["offset"].iloc[0]
        blk_rank = (d[d["offset"] == fb].groupby("taker")["margin"].sum().sort_values(ascending=False)).head(5).index
        if tk in blk_rank and len(d[d["offset"] == fb]["taker"].unique()) > 5:
            continue  # top-5 in its first block: likely an incumbent's new address
        g = d[(d["taker"] == tk) & (d["day"] <= ft + pd.Timedelta(days=365))]
        span = min(365, (d["day"].max() - ft).days)
        if span < 180:
            continue
        ann = (g["margin"] * g["w"]).sum() * 365 / span - INFRA
        key = "A (first seen 2024)" if ft.year == 2024 else ("B (first seen 2025)" if ft.year == 2025 else None)
        out.append({"taker": tk[:12], "first": ft.date(), "orders_sampled": len(g), "ann_net": ann})
        if key:
            coh[key].append(ann)
    t = pd.DataFrame(out)
    if len(t):
        print(t.sort_values("first").to_string(index=False, float_format=lambda x: f"{x:12,.0f}"))
    v = verdict(coh)
    if v == "PASS" and not (top3 < 0.90):
        v = "inconclusive (cohorts pass but top-3 share >= 90%)"
    print(f"  STAGE VERDICT (#417): {v}")


def main():
    print("===== #417-#418 permissionless filling roles: newcomer income by cohort")
    part418()
    part417()


if __name__ == "__main__":
    main()

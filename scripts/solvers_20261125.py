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
    print("\n#### #417 deBridge DLN takers: newcomer income")
    p = PUB / "solvers_dln_orders.json.gz"
    pr = PUB / "solvers_dln_probe.json"
    if not p.exists():
        if pr.exists():
            print("  probe only: " + json.dumps(json.loads(pr.read_text()))[:600])
        print("  orders not fetched: not testable yet")
        return
    with gzip.open(p, "rt") as f:
        orders = json.load(f)
    print(f"  orders fetched: {len(orders)}; first order keys: {sorted(orders[0].keys())[:40] if orders else None}")


def main():
    print("===== #417-#418 permissionless filling roles: newcomer income by cohort")
    part418()
    part417()


if __name__ == "__main__":
    main()

"""Batch NF29 #656-#659: HyperEVM DEX pools vs Hyperliquid's order book (docs/PREREG_BATCH_NF29_20261128.md).

    uv run python -m scripts.batch_nf29_20261128 | tee docs/jx_runs/batch_nf29_20261128.txt
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

PUB = Path(__file__).resolve().parent.parent / "data" / "public"
V3 = "0xc42079f94a6350d7e6235f29174924f928cc2ac818eb64fed8004e115fbcca67"
SYNC = "0x1c411e9a96e071241c2f21f7726b17ae89e3cab4c78be50e062b03a9fffbbad1"
HL_TAKER, BUF, CAP, HAIRCUT = 0.00045, 0.0005, 1500.0, 0.5


def words(h):
    h = h[2:] if h.startswith("0x") else h
    return [int(h[i:i + 64], 16) for i in range(0, len(h), 64)]


def signed(x):
    return x - (1 << 256) if x >= 1 << 255 else x


def decode(sw, pools):
    meta = {p["address"].lower(): p for p in pools}
    out = []
    for r in sw.itertuples(index=False):
        p = meta.get(r.pool)
        if p is None or p.get("base_dec") is None or p.get("quote_dec") is None:
            continue
        b0 = str(p.get("token0") or "").lower() == str(p.get("base_addr") or "").lower()
        d0, d1 = (int(p["base_dec"]), int(p["quote_dec"])) if b0 else (int(p["quote_dec"]), int(p["base_dec"]))
        w = words(r.data)
        if r.topic0 == V3 and len(w) >= 5:
            a0, a1, sp = signed(w[0]), signed(w[1]), w[2]
            p10 = (sp / 2 ** 96) ** 2 * 10 ** (d0 - d1)  # token1 per token0
            notional_q = abs(a1) / 10 ** d1 if b0 else abs(a0) / 10 ** d0
            sender = r.topics.split("|")[0] if r.topics else ""
        elif r.topic0 == SYNC and len(w) >= 2 and w[0] > 0:
            p10 = (w[1] / 10 ** d1) / (w[0] / 10 ** d0)
            notional_q, sender = np.nan, ""
        else:
            continue
        px = p10 if b0 else (1 / p10 if p10 > 0 else np.nan)
        out.append({"pool": r.pool, "base": p["base"], "block": r.block, "li": r.log_index, "px": px, "notional": notional_q,
                    "sender": sender, "fee": p.get("fee") if p.get("fee") is not None else 0.003, "v3": r.topic0 == V3})
    return pd.DataFrame(out)


def main():
    pools = json.loads((PUB / "batchnf29_pools.json").read_text())
    sw = pd.read_parquet(PUB / "batchnf29_swaps.parquet")
    marks = sorted(json.loads((PUB / "batchnf29_blocks.json").read_text()))
    hl = pd.read_parquet(PUB / "batchnf29_hl_1m.parquet")
    e = decode(sw, pools)
    bk, bt = np.array([m[0] for m in marks], float), np.array([m[1] for m in marks], float)
    e["ts"] = np.interp(e["block"], bk, bt)
    e["minute"] = (e["ts"] // 60 * 60_000).astype("int64")
    e = e.merge(hl.rename(columns={"t": "minute", "c": "hl"})[["base", "minute", "hl"]], on=["base", "minute"], how="left")
    e = e.dropna(subset=["hl", "px"]).sort_values(["pool", "block", "li"]).reset_index(drop=True)
    days = (bt.max() - bt.min()) / 86400 if len(bt) > 1 else np.nan
    print(f"pools {len(pools)} (with events {e['pool'].nunique()}), events {len(e):,}, window {days:.2f} days; "
          f"bases {sorted(e['base'].unique())}")
    e["gap"] = e["px"] / e["hl"] - 1
    e["cost"] = e["fee"] + HL_TAKER + BUF
    ratio = e.groupby("pool")["gap"].median()
    bad = ratio[ratio.abs() > 0.05].index  # unit/orientation mismatch guard (median gap > 5%)
    if len(bad):
        print(f"   dropped {len(bad)} pools with median |gap| > 5% (unit or orientation mismatch)")
    e = e[~e["pool"].isin(bad)]
    g = e.groupby("pool")
    e["nxt_block"], e["nxt_gap"], e["nxt_sender"] = g["block"].shift(-1), g["gap"].shift(-1), g["sender"].shift(-1)
    open_ = e["gap"].abs() > e["cost"]
    reach = open_ & (e["nxt_block"] > e["block"]) & (e["nxt_gap"].abs() > e["cost"]) & (np.sign(e["nxt_gap"]) == np.sign(e["gap"]))
    e["value"] = np.where(reach, (e["gap"].abs() - e["cost"]) * np.minimum(CAP, e["notional"].fillna(CAP)) * HAIRCUT, 0.0)
    yr = 365 / days if days and days > 0 else np.nan
    print(f"   gaps > cost after an event: {int(open_.sum()):,} ({open_.mean():.1%}); still open in a later block: {int(reach.sum()):,}\n")
    for num, label, m in (("#656", "all pools", e["pool"].notna()), ("#657", "WHYPE pools", e["base"] == "HYPE"),
                          ("#658", "non-HYPE bases", e["base"] != "HYPE")):
        s = e[m]
        print(f"{num} reachable value, {label}: ${s['value'].sum():,.0f} in the window -> ${s['value'].sum() * yr:,.0f}/yr "
              f"(events {len(s):,}, reachable {int(reach[m].sum()):,}, median reachable gap {s.loc[reach[m], 'gap'].abs().median():.2%})")
    closers = e[open_ & e["nxt_gap"].notna() & ((e["nxt_gap"].abs() <= 0.5 * e["gap"].abs()))]
    top = closers["nxt_sender"].value_counts()
    share = top.head(3).sum() / top.sum() if top.sum() else np.nan
    print(f"\n#659 gap-closing swaps {int(top.sum()):,} by {top.size} sender contracts; top-3 share {share:.0%}")
    total = e["value"].sum() * yr
    if total < 3600 or (share > 0.95 and total < 15000):
        print("VERDICT KILL (Stage 1): reachable value below the bar or closed by incumbents")
    else:
        print("VERDICT survives Stage 1 -> Stage 2 forward log (no PASS from this pilot)")


if __name__ == "__main__":
    main()

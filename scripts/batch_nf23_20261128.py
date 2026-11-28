"""Batch NF23 #635-#638: zero-fee retail venues (Lighter, Paradex): #520 wick bids and #569 hourly cascades
(docs/PREREG_BATCH_NF23_20261128.md).

    uv run python -m scripts.batch_nf23_20261128 | tee docs/jx_runs/batch_nf23_20261128.txt
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

import scripts.batch_nf14_20261128 as B14
import scripts.batch_nf15_20261128 as B15

PUB = Path(__file__).resolve().parent.parent / "data" / "public"
VENUES = [("lighter", "#635", "#637"), ("paradex", "#636", "#638")]


def hourly_raw(v):
    p = PUB / f"batchnf23_{v}_1h.parquet"
    d = pd.read_parquet(p) if p.exists() else pd.DataFrame()
    if len(d) and v == "paradex":  # addendum 1: kline volume is already USD
        d = d.assign(v_usd=d["v_usd"] / d["c"])
    return d


def daily(v):
    p = PUB / f"batchnf23_{v}_1d.parquet"
    d = pd.read_parquet(p) if p.exists() else pd.DataFrame()
    if d.empty and v == "paradex":  # addendum 1: daily bars built from the hourly ones
        h = hourly_raw(v)
        if len(h):
            h = h.sort_values(["coin", "t"]).assign(day=pd.to_datetime(h["t"], unit="ms", utc=True).dt.normalize())
            d = h.groupby(["coin", "day"]).agg(o=("o", "first"), h=("h", "max"), l=("l", "min"), c=("c", "last"), v_usd=("v_usd", "sum")).reset_index()
            d["t"] = (d["day"] - pd.Timestamp(0, tz="UTC")) // pd.Timedelta("1ms")
    if d.empty:
        return d
    d["day"] = pd.to_datetime(d["t"], unit="ms", utc=True).dt.normalize()
    d = d[(d["day"] <= B14.END) & (d["c"] > 0) & (d["l"] > 0)].drop_duplicates(["coin", "day"]).sort_values(["coin", "day"])
    return d.assign(venue=v).reset_index(drop=True)


def wick_test(num, v, d):
    print(f"{num} #520 wick bids on {v} (zero fees; stress at 0.02% + 0.05%)")
    if d.empty:
        print("   not testable (no daily candles)\n")
        return
    lo = d["day"].min()
    B14.SPLIT = pd.Timestamp("2025-07-01", tz="UTC") if lo <= pd.Timestamp("2025-03-01", tz="UTC") else pd.Timestamp("2026-05-01", tz="UTC")
    print(f"   markets {d['coin'].nunique()}, {lo.date()}..{d['day'].max().date()}; split {B14.SPLIT.date()}")
    B14.MK, B14.TK = 0.0, 0.0
    f = B14.pnl(B14.wick(d, "vol"))
    B14.MK, B14.TK = 0.0002 / 1.5, 0.0005 / 1.5  # wick(cost_mult=1.5) then charges exactly 0.02% + 0.05%
    fs = B14.pnl(B14.wick(d, "vol", 1.5))
    a, b, bs, vd = B14.judge(f, fs, lo)
    print(B14.fmt(f"Stage 1 {lo.date()}..{(B14.SPLIT - pd.Timedelta(days=1)).date()}", a))
    print(B14.fmt(f"Stage 2 {B14.SPLIT.date()}..2026-11-25", b))
    print(f"   stress (0.02% + 0.05%) Stage 2 mean {bs.get('m', np.nan):+.2%}")
    if vd == "PASS":
        vd += " (forward log)" if b["t"] >= 2.5 and bs.get("m", -1) > 0 else " (not forward-logged: t < 2.5 or stress <= 0)"
    print(f"   VERDICT {vd}\n")


def cascade_test(num, v):
    print(f"{num} #569 hourly cascade reversal on {v} (zero fees; stress at 0.07%)")
    raw = hourly_raw(v)
    if raw.empty:
        print("   not testable (no hourly candles)\n")
        return
    g = B15.prep(raw)
    print(f"   markets {g['coin'].nunique()}, hours {g['c'].notna().sum():,}, {g['ts'].min()}..{g['ts'].max()}")
    sig = (g["r"] <= -B15.K * g["sig"]) & (g["h"] > g["l"]) & (g["v_usd"] >= B15.MINVOL) & g["exit_c"].notna()
    e = g[sig].copy()
    e["ret"] = e["exit_c"] / e["c"] - 1
    e["size"] = np.minimum(B15.CAP, B15.SHARE * e["v_usd"])
    e = B15.one_per_market(e)
    B15.COST = 0.0007 / 0.5  # verdict's stress subtracts 0.5 x COST = the full 0.07% here
    B15.verdict(e, g["ts"].min())


def main():
    for v, n1, n2 in VENUES:
        wick_test(n1, v, daily(v))
    for v, n1, n2 in VENUES:
        cascade_test(n2, v)


if __name__ == "__main__":
    main()

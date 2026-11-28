"""Batch Z #534: #208's funding-gap rule on points-farming venues (docs/PREREG_BATCH_Z_20261128.md).

    uv run python -m scripts.batch_z_20261128 | tee docs/jx_runs/batch_z_20261128.txt
"""
from __future__ import annotations

import numpy as np
import pandas as pd

import scripts.fundgap_20261121 as FG

PAIRS = [("hl", "aster"), ("hl", "lighter"), ("aster", "lighter")]
END = pd.Timestamp("2026-11-01", tz="UTC")


def load():
    hl = pd.read_parquet("data/public/fundgap_funding.parquet")
    hl = hl[hl["venue"] == "hl"]
    z = pd.read_parquet("data/public/batchz_funding.parquet")
    aster = z[z["venue"] == "aster"].copy()
    lr = pd.read_parquet("data/public/batchz_lighter_raw.parquet")
    lr["rate"] = pd.to_numeric(lr["rate_raw"], errors="coerce") / 100.0  # addendum 1: percent per hour
    lr["rate"] *= np.where(lr["direction"].str.lower() == "short", -1.0, 1.0)
    lr["venue"] = "lighter"
    return hl, aster, lr[["venue", "coin", "t", "rate"]].dropna()


def hourly(hl, aster, lighter, lo):
    grid = pd.date_range(lo - pd.Timedelta(days=2), END, freq="h", tz="UTC")
    H = {}
    for df in (hl, lighter):
        for (v, c), g in df.groupby(["venue", "coin"]):
            s = g.assign(ts=pd.to_datetime(g["t"], unit="s", utc=True).dt.floor("h")).groupby("ts")["rate"].mean().sort_index()
            H[(v, c)] = s.reindex(grid)
    for c, g in aster.groupby("coin"):  # per-8h settlement rate -> per hour, spread over the interval ending at each settlement
        s = g.assign(ts=pd.to_datetime(g["t"], unit="s", utc=True).dt.floor("h")).groupby("ts")["rate"].mean().sort_index()
        iv = s.index.to_series().diff().dt.total_seconds().div(3600).fillna(8).clip(lower=1)
        H[("aster", c)] = (s / iv).reindex(grid).bfill(limit=8)
    return H


def main():
    hl, aster, lighter = load()
    starts = {v: pd.to_datetime(d["t"].min(), unit="s", utc=True).ceil("D") for v, d in (("hl", hl), ("aster", aster), ("lighter", lighter))}
    lo = max(starts["hl"], min(starts["aster"], starts["lighter"]))
    print("venue coverage starts:", {k: str(v.date()) for k, v in starts.items()}, "| coins aster", aster["coin"].nunique(),
          "lighter", lighter["coin"].nunique())
    print("Lighter units check (BTC median per hour, fraction):", f"{lighter[lighter.coin == 'BTC'].rate.median():.2e}",
          "| HL", f"{hl[hl.coin == 'BTC'].rate.median():.2e}", "| Aster per 8h", f"{aster[aster.coin == 'BTC'].rate.median():.2e}")
    # pooled window: from the first day both venues of at least one pair have data; halves split at the midpoint
    FG.LO, FG.HI = lo, END
    FG.MID = lo + (END - lo) / 2
    FG.PILOT = END - pd.Timedelta(days=92)
    print(f"window {lo.date()}..{(END - pd.Timedelta(days=1)).date()}; halves split {FG.MID.date()}; Stage 1 from {FG.PILOT.date()}\n")
    H = hourly(hl, aster, lighter, lo)
    s, trips, opens = FG.run(H, PAIRS)
    FG.report("#534 pooled HL/Aster/Lighter", s, trips, opens)
    for p in PAIRS:
        FG.report(f"  pair {p[0]}-{p[1]} alone", *FG.run(H, [p]), verdict=False)
    FG.FEE_SIDE = 0.0005 * 1.5
    s15, _, _ = FG.run(H, PAIRS)
    h2 = float(s15.r[s15.index >= FG.MID].mean() * 365 * 100)
    print(f"\nfees x 1.5, second half: {h2:.2f}%/yr on capital ({'clears' if h2 >= FG.BAR else 'misses'} the {FG.BAR}% bar)")


if __name__ == "__main__":
    main()

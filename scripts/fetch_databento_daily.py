"""Quote (free) or download Databento daily bars for #350 (docs/PREREG_FUTURES_TREND_CARRY_20261123.md).

    DATABENTO_API_KEY=... uv run python scripts/fetch_databento_daily.py quote
    DATABENTO_API_KEY=... uv run python scripts/fetch_databento_daily.py download --max-cost-usd 2.0
The key is read from the environment only.
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import databento as db

ROOTS = "ES NQ YM RTY ZT ZF ZN ZB 6E 6J 6B 6A 6C 6S GC SI HG CL NG RB HO ZC ZS ZW LE HE".split()
SYMS = [f"{r}.v.{k}" for r in ROOTS for k in (0, 1)]
OUT = Path(__file__).resolve().parent.parent / "data" / "public" / "databento_daily.parquet"
START, END = "2010-06-06", "2026-11-01"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["quote", "download"])
    ap.add_argument("--max-cost-usd", type=float, default=2.0)
    a = ap.parse_args()
    client = db.Historical(os.environ["DATABENTO_API_KEY"])
    kw = dict(dataset="GLBX.MDP3", symbols=SYMS, stype_in="continuous", schema="ohlcv-1d", start=START, end=END)
    cost = client.metadata.get_cost(**kw)
    print(f"quote: ${cost:.4f} for {len(SYMS)} continuous symbols, ohlcv-1d, {START}..{END}", flush=True)
    if a.mode == "quote":
        return 0
    if cost > a.max_cost_usd:
        print(f"ABORT: quote ${cost:.4f} exceeds the cap ${a.max_cost_usd:.2f} (needs Jx's approval)", flush=True)
        return 1
    df = client.timeseries.get_range(**kw).to_df().reset_index()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(OUT, index=False)
    print(f"downloaded {len(df)} rows, {df['symbol'].nunique() if 'symbol' in df else '?'} symbols -> {OUT}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())

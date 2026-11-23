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
    import time

    import pandas as pd
    parts = []
    for i in range(0, len(SYMS), 4):  # small chunks: one request for all symbols timed out (504)
        chunk = SYMS[i:i + 4]
        for k in range(4):
            try:
                parts.append(client.timeseries.get_range(**{**kw, "symbols": chunk}).to_df().reset_index())
                break
            except Exception as e:  # noqa: BLE001
                print(f"  chunk {chunk} try {k + 1}: {type(e).__name__}: {str(e)[:120]}", flush=True)
                time.sleep(10 * (k + 1))
        print(f"  fetched {min(i + 4, len(SYMS))}/{len(SYMS)} symbols", flush=True)
        if parts:
            OUT.parent.mkdir(parents=True, exist_ok=True)
            pd.concat(parts, ignore_index=True).to_parquet(OUT, index=False)
    df = pd.concat(parts, ignore_index=True) if parts else None
    print(f"downloaded {0 if df is None else len(df)} rows, {0 if df is None else df['symbol'].nunique()} symbols -> {OUT}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())

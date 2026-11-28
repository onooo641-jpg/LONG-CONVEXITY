"""Batch NF25: Hyperliquid volume during its points programme, from daily candles of every live HL perp (docs/PREREG_BATCH_NF25_20261128.md).

    uv run python -m scripts.batch_nf25_20261128 | tee docs/jx_runs/batch_nf25_20261128.txt

DefiLlama's volume API answers 402 (paid) and Hyperliquid's stats file 403 from GitHub Actions, so HL volume is rebuilt here. Candles
exist only for perps that are still listed, so volume is understated and yield per $1M overstated.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

PUB = Path(__file__).resolve().parent.parent / "data" / "public"
AIRDROP_USD = 1.2e9  # The Block: "over $1.2 billion" at TGE 2024-11-29 (third-party)


def main():
    c = pd.read_parquet(PUB / "uncharted_385_candles.parquet")
    c["day"] = pd.to_datetime(c["t"], unit="ms")
    c["usd"] = c["v"] * c["c"]
    print(f"HL daily candles: {c['coin'].nunique()} live perps, {c['day'].min().date()}..{c['day'].max().date()}")
    for a, b, label in (("2023-11-01", "2024-05-01", "points programme (1M points/week)"),
                        ("2023-11-01", "2024-11-29", "programme start to TGE")):
        w = c[(c["day"] >= a) & (c["day"] < b)]
        vol = w["usd"].sum()
        print(f"   {label} {a}..{b}: volume ${vol / 1e9:,.0f}B on {w['coin'].nunique()} perps -> ${AIRDROP_USD / vol * 1e6:,.0f} per $1M volume")


if __name__ == "__main__":
    main()

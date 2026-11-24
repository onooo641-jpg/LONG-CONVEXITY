"""#365 context (unregistered): how close are losing bids to the winning bid? (difficulty gauge for a new solver)

    uv run python -m scripts.cow_gate_gap_20261124 | tee docs/jx_runs/cow_gate_gap_20261124.txt
Per sampled auction with >= 2 scored bids (not filtered out): each solver's best score / the best score in the auction.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

PUB = Path(__file__).resolve().parent.parent / "data" / "public"


def main():
    c = pd.read_parquet(PUB / "cow365_competition.parquet")
    c = c[c["filtered"] != True].copy()  # noqa: E712
    c["s"] = pd.to_numeric(c["score"], errors="coerce")
    c = c[c["s"] > 0]
    print("===== #365 context: losing bids relative to the best bid in the same auction")
    for net, x in c.groupby("net"):
        best = x.groupby(["auction", "solver_addr"])["s"].max().reset_index()
        best["top"] = best.groupby("auction")["s"].transform("max")
        best["n"] = best.groupby("auction")["s"].transform("size")
        best = best[best["n"] >= 2]
        if best["auction"].nunique() < 50:
            continue
        lose = best[best["s"] < best["top"]].copy()
        lose["gap"] = 1 - lose["s"] / lose["top"]
        second = lose.groupby("auction")["gap"].min()
        print(f"  {net}: auctions {best['auction'].nunique()}, median bidders per auction {best.groupby('auction').size().median():.0f}; "
              f"2nd-best bid below the best by: median {second.median():.3%}, 75th pct {second.quantile(0.75):.3%}; "
              f"all losing bids: median gap {lose['gap'].median():.2%}; share of losing bids within 0.1% of the best "
              f"{(lose['gap'] <= 0.001).mean():.0%}, within 1% {(lose['gap'] <= 0.01).mean():.0%}")


if __name__ == "__main__":
    main()

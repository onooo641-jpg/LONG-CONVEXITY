"""#365 context (unregistered): concentration of winning score (value) vs auction counts, per network.

    uv run python -m scripts.cow_gate_value_20261124 | tee docs/jx_runs/cow_gate_value_20261124.txt
Score is in the chain's native token (wei); summed over sampled auctions with a winner. Networks with >= 50 sampled auctions.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

PUB = Path(__file__).resolve().parent.parent / "data" / "public"


def main():
    c = pd.read_parquet(PUB / "cow365_competition.parquet")
    w = c[c["winner"] == True].copy()  # noqa: E712
    w["s"] = pd.to_numeric(w["score"], errors="coerce")
    print("===== #365 context: share of winning score (value) vs share of auctions won")
    for net, x in w.groupby("net"):
        if x["auction"].nunique() < 50:
            continue
        v = x.groupby("solver_addr")["s"].sum().sort_values(ascending=False)
        n = x.groupby("solver_addr")["auction"].nunique().reindex(v.index)
        print(f"  {net}: auctions {x['auction'].nunique()}; top-3 by value take {v.head(3).sum() / v.sum():.0%} of winning score "
              f"(and {n.head(3).sum() / n.sum():.0%} of wins); outside the top 5 by value: {v.iloc[5:].sum() / v.sum():.0%} of score, "
              f"{n.iloc[5:].sum() / n.sum():.0%} of wins")


if __name__ == "__main__":
    main()

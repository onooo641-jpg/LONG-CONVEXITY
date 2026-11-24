"""#366 analysis (docs/PREREG_COW_SHADOW_20261124.md): baseline solver vs production winners, from data/public/cowshadow_*.parquet.

    uv run python -m scripts.cow_shadow_20261124 | tee docs/jx_runs/cow_shadow_20261124.txt
The main run is the file with the most auctions seen.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

PUB = Path(__file__).resolve().parent.parent / "data" / "public"


def main():
    files = sorted(PUB.glob("cowshadow_*.parquet"))
    print("===== #366 CoW baseline solver vs production (shadow mode)")
    if not files:
        print("  no shadow runs yet")
        return
    runs = {f.stem.split("_", 1)[1]: pd.read_parquet(f) for f in files}
    for rid, d in runs.items():
        print(f"  run {rid}: auctions seen {len(d)}, baseline solutions {int(d['ours'].notna().sum())}, "
              f"with production data {int(d['prod_best'].notna().sum())}")
    rid = max(runs, key=lambda k: len(runs[k]))
    d = runs[rid]
    d = d[d["prod_best"].notna() & (d["prod_best"] > 0)]
    bid = d[d["ours"].notna() & (d["ours"] > 0)]
    print(f"  main run {rid}: auctions with production data {len(d)}; baseline bid rate {len(bid) / max(1, len(d)):.1%}")
    if len(bid):
        ratio = bid["ours"] / bid["prod_best"]
        won = float((bid["ours"] >= bid["prod_best"]).sum()) / max(1, len(d))
        print(f"  baseline score / best production score: median {ratio.median():.3f}, 25th {ratio.quantile(0.25):.3f}, "
              f"75th {ratio.quantile(0.75):.3f}; would-have-won share of all auctions {won:.2%}; median production bidders "
              f"{d['prod_n'].median():.0f}")
        med = float(ratio.median())
    else:
        won, med = 0.0, 0.0
        print("  no baseline bids with production data")
    kill = won < 0.01 and med < 0.5
    print(f"  VERDICT (route 'start from the free baseline'): {'KILL' if kill else 'baseline is a usable starting point (not a pass)'}")


if __name__ == "__main__":
    main()

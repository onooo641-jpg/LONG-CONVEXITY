"""PREREG_LIQ_REPLAY_20261121: deterministic sample of eligible liquidations -> data/public/liq_replay_sample.parquet"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import liquidations_20261120 as L  # noqa: E402

POOL = {"arbitrum": "0x794a61358d6845594f94dc1db02a252b5b4814ad", "base": "0xa238dd80c259a72e81d7e4664a9801593f98d1c5",
        "avalanche": "0x794a61358d6845594f94dc1db02a252b5b4814ad", "polygon": "0x794a61358d6845594f94dc1db02a252b5b4814ad",
        "optimism": "0x794a61358d6845594f94dc1db02a252b5b4814ad"}
N2, N1_STEP = 400, 4


def main():
    out = []
    for c, pool in POOL.items():
        df = L.load(c)
        e = df[(df["venue"] == pool) & df["valid"] & (df["gross"] > 50) & (df["month"] >= 17)].sort_values(["block", "tx", "user"], kind="mergesort")
        e = e.reset_index(drop=True)
        k = max(1, int(np.ceil(len(e) / N2)))
        s = e.iloc[::k].head(N2).copy()
        s["s1"] = (np.arange(len(s)) % N1_STEP == 0)
        s["chain"] = c
        print(f"{c:10s} eligible {len(e):6d}  every {k}th -> {len(s)} (stage 1: {int(s['s1'].sum())})  blocks {s['block'].min()}..{s['block'].max()}")
        out.append(s[["chain", "block", "tx", "user", "collateral", "debt", "gross", "ts", "month", "s1"]])
    pd.concat(out, ignore_index=True).to_parquet(Path(__file__).resolve().parent.parent / "data" / "public" / "liq_replay_sample.parquet")


if __name__ == "__main__":
    main()

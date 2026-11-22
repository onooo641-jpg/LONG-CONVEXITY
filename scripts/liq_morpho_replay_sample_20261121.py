"""PREREG_LIQ_MORPHO_REPLAY_20261121: deterministic sample of eligible Morpho Base liquidations (with market id) -> data/public/liq_morpho_replay_sample.parquet"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import liquidations_20261120 as L  # noqa: E402

L.NATIVE["morphobase"] = "coingecko:ethereum"
L.LKEY["morphobase"] = "base"
D = Path(L.D)


def main():
    df = L.load("morphobase")
    raw = pd.concat([pd.read_parquet(D / f"liq_morphobase_s{i}_raw.parquet") for i in range(3)], ignore_index=True)[["tx", "user", "block", "coll_amt", "mid"]].drop_duplicates()
    e = df[df["valid"] & (df["gross"] > 50) & (df["month"] >= 17)].merge(raw, on=["tx", "user", "block", "coll_amt"], how="left")
    e = e.sort_values(["block", "tx", "user"], kind="mergesort").reset_index(drop=True)
    k = max(1, int(np.ceil(len(e) / 400)))
    s = e.iloc[::k].head(400).copy()
    s["s1"] = (np.arange(len(s)) % 4 == 0)
    print(f"eligible {len(e)} (mid missing {int(e['mid'].isna().sum())}); every {k}th -> {len(s)} (stage 1: {int(s['s1'].sum())}); months {sorted(s['month'].unique())}")
    s[["tx", "user", "block", "gross", "mid", "month", "s1"]].to_parquet(D / "liq_morpho_replay_sample.parquet")


if __name__ == "__main__":
    main()

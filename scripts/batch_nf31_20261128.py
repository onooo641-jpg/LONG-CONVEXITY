"""Batch NF31 #664-#667: Clanker tokens on Base with NF30's rules, ETH-hedged (docs/PREREG_BATCH_NF31_20261128.md).

    uv run python -m scripts.batch_nf31_20261128 | tee docs/jx_runs/batch_nf31_20261128.txt
"""
from __future__ import annotations

import pandas as pd

import scripts.batch_nf30_20261128 as N


def load():
    d = pd.read_parquet(N.PUB / "batchnf31_ohlcv.parquet")
    d = d[d["quote"].astype(str).str.upper().isin(["WETH", "ETH"])].copy()
    d["day"] = pd.to_datetime(d["t"], unit="s").dt.normalize()
    d = d[d["c"] > 0].drop_duplicates(["lp", "day"]).sort_values(["lp", "day"])
    c = d.pivot(index="day", columns="lp", values="c")
    v = d.pivot(index="day", columns="lp", values="v_usd").fillna(0.0)
    full = pd.date_range(c.index.min(), c.index.max(), freq="D")
    return d, c.reindex(full), v.reindex(full).fillna(0.0)


def eth_funding():
    f = pd.read_parquet(N.PUB / "fundgap_funding.parquet")
    f = f[(f["venue"] == "hl") & (f["coin"] == "ETH")]
    daily = f.assign(day=pd.to_datetime(f["t"], unit="s").dt.normalize()).groupby("day")["rate"].sum()
    return daily, float(daily.mean()) if len(daily) else 0.0


def main():
    N.load, N.virtual_funding = load, eth_funding
    print("NF31: Clanker WETH-quoted pools, ETH hedge (NF30 engine; labels below say VIRTUAL where NF30's printout does)")
    N.main()


if __name__ == "__main__":
    main()

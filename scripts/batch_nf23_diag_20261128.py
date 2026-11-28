"""NF23 #636 stale-print check (required by the pre-registration before a PASS is accepted).

    uv run python -m scripts.batch_nf23_diag_20261128 | tee docs/jx_runs/batch_nf23_diag_20261128.txt

For each Stage 2 fill: USD volume traded in the hour that made the day's low, the share of fills by market, and whether the HL perp
(same coin, NF14 norm) traded at least 5% below its previous close the same day (a real market-wide wick) or not (a Paradex-only print).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

import scripts.batch_nf14_20261128 as B14
import scripts.batch_nf23_20261128 as M


def main():
    d = M.daily("paradex")
    B14.SPLIT = pd.Timestamp("2026-05-01", tz="UTC")
    B14.MK, B14.TK = 0.0, 0.0
    f = B14.wick(d, "vol")
    f = f[f["day"] >= B14.SPLIT].copy()
    h = M.hourly_raw("paradex").assign(ts=lambda x: pd.to_datetime(x["t"], unit="ms", utc=True))
    h["day"] = h["ts"].dt.normalize()
    low_hour = h.loc[h.groupby(["coin", "day"])["l"].idxmin()].set_index(["coin", "day"])
    f["v_low_hour"] = [float(low_hour.at[(c, dy), "v_usd"]) if (c, dy) in low_hour.index else np.nan for c, dy in zip(f["coin"], f["day"])]
    hl = pd.read_parquet(M.PUB / "uncharted_385_candles.parquet")
    hl["day"] = pd.to_datetime(hl["t"], unit="ms", utc=True).dt.normalize()
    hl = hl.drop_duplicates(["coin", "day"]).sort_values(["coin", "day"])
    hl["drop"] = hl["l"] / hl.groupby("coin")["c"].shift() - 1
    hk = hl.assign(k=hl["coin"].map(B14.norm)).set_index(["k", "day"])["drop"]
    hk = hk[~hk.index.duplicated()]
    f["hl_drop"] = [float(hk.get((B14.norm(c), dy), np.nan)) for c, dy in zip(f["coin"], f["day"])]
    print(f"#636 Stage 2 fills {len(f)}, mean {f['ret'].mean():+.2%}")
    print(f"   USD volume in the hour that made the low: median ${f['v_low_hour'].median():,.0f}; "
          f"share < $1,500 (smaller than one fill): {(f['v_low_hour'] < 1500).mean():.0%}")
    big = f[f["v_low_hour"] >= 1500]
    print(f"   fills whose low hour traded >= $1,500: n {len(big)}, mean {big['ret'].mean():+.2%}")
    m = f.dropna(subset=["hl_drop"])
    real = m[m["hl_drop"] <= -0.05]
    local = m[m["hl_drop"] > -0.05]
    print(f"   matched to HL: {len(m)}; HL also fell >= 5% that day: n {len(real)}, mean {real['ret'].mean():+.2%}; "
          f"Paradex-only wick: n {len(local)}, mean {local['ret'].mean():+.2%}")
    top = f.groupby("coin")["ret"].agg(["size", "mean"]).sort_values("size", ascending=False).head(5)
    print("   most fills: " + "; ".join(f"{k} n {int(r['size'])} {r['mean']:+.2%}" for k, r in top.iterrows()))


if __name__ == "__main__":
    main()

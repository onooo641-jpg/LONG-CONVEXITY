"""#371 Stage 4: gross spread UniswapX fillers keep on Arbitrum, Aug-Oct 2026 (docs/PREREG_UNISWAPX_20261124.md).

    uv run python -m scripts.uniswapx_margin_20261124 | tee docs/jx_runs/uniswapx_margin_20261124.txt
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

PUB = Path(__file__).resolve().parent.parent / "data" / "public"
DAYS, BAR, MIN_BPS, OUTLIER_BPS = 92, 15_000.0, 2.0, 500.0
NEWCOMERS = {"0xd767473b74397fa9c1e7a2bdb210020c648a6836": "newcomer A (7.3% of volume)",
             "0xe0763177d7e80e290fc4fea055fae11f5024f687": "newcomer B (5.2% of volume)"}


def main():
    meta = json.loads((PUB / "uniswapx371_stage4_meta.json").read_text())
    tr = pd.read_parquet(PUB / "uniswapx371_stage4_transfers.parquet")
    print(f"===== #371 Stage 4: Arbitrum UniswapX fills Aug-Oct 2026; fills {meta['fills']:,}; transfers {len(tr):,}")
    series = {}
    for tkn, pts in meta["hourly"].items():
        if pts:
            s = pd.Series({pd.Timestamp(int(p["timestamp"]), unit="s", tz="UTC").floor("h"): float(p["price"]) for p in pts}).sort_index()
            series[tkn] = s[~s.index.duplicated()]
    print(f"  tokens with hourly prices: {len(series)}")
    tr["hour"] = pd.to_datetime(tr["t"], unit="s", utc=True).dt.floor("h")
    usd = []
    for r in tr.itertuples():
        dec, s = meta["decimals"].get(r.token), series.get(r.token)
        if dec is None or s is None or r.hour < s.index[0] - pd.Timedelta(hours=2):
            usd.append(np.nan)
            continue
        usd.append(int(r.amount_raw) / 10 ** dec * float(s.asof(r.hour)))
    tr["usd"] = usd
    rows, dropped_unpriced = [], 0
    for tx, g in tr.groupby("tx"):
        ins, outs = g[g["dir"] == "in"], g[g["dir"] == "out"]
        outs = outs[~outs["token"].isin(set(ins["token"]))]          # refunds of the input token are not output
        if ins.empty or outs.empty or ins["usd"].isna().any() or outs["usd"].isna().any():
            dropped_unpriced += 1
            continue
        vin, vout = float(ins["usd"].sum()), float(outs["usd"].sum())
        rows.append({"tx": tx, "filler": g["filler"].iloc[0], "vin": vin, "spread": vin - vout,
                     "bps": 1e4 * (vin - vout) / vin if vin > 0 else np.nan})
    f = pd.DataFrame(rows)
    out = f[f["bps"].abs() > OUTLIER_BPS]
    f = f[f["bps"].abs() <= OUTLIER_BPS]
    print(f"  fills measured {len(f):,}; dropped: unpriced/incomplete {dropped_unpriced:,}, |spread| > {OUTLIER_BPS:.0f} bps {len(out):,}")
    vw = 1e4 * f["spread"].sum() / f["vin"].sum()
    print(f"  measured volume ${f['vin'].sum():,.0f}; volume-weighted gross spread {vw:.2f} bps; median {f['bps'].median():.2f} bps; "
          f"total gross ${f['spread'].sum():,.0f} in {DAYS} days (${f['spread'].sum() * 365 / DAYS:,.0f}/yr)")
    by = f.groupby("filler").agg(fills=("tx", "size"), vol=("vin", "sum"), gross=("spread", "sum")).sort_values("vol", ascending=False)
    by["bps"] = 1e4 * by["gross"] / by["vol"]
    by["gross_yr"] = by["gross"] * 365 / DAYS
    for a, r in by.head(8).iterrows():
        tag = NEWCOMERS.get(a, "")
        print(f"    {a}  fills {int(r['fills']):>6,}  vol ${r['vol']:>13,.0f}  {r['bps']:7.2f} bps  gross ${r['gross_yr']:>10,.0f}/yr  {tag}")
    kill = vw < MIN_BPS
    for a, tag in NEWCOMERS.items():
        g = float(by.loc[a, "gross_yr"]) if a in by.index else 0.0
        print(f"  {tag}: annualised gross ${g:,.0f}/yr ({int(by.loc[a, 'fills']) if a in by.index else 0} fills)")
        kill = kill or g < BAR
    print(f"  STAGE 4 VERDICT: {'KILL' if kill else 'worth a no-money filler prototype (not a pass)'} "
          f"(bars: volume-weighted spread >= {MIN_BPS} bps and each newcomer >= $15,000/yr gross)")


if __name__ == "__main__":
    main()

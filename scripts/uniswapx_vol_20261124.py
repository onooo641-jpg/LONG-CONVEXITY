"""#371 Stage 3: UniswapX Arbitrum fill volume ceiling (docs/PREREG_UNISWAPX_20261124.md).

    uv run python -m scripts.uniswapx_vol_20261124 | tee docs/jx_runs/uniswapx_vol_20261124.txt
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

PUB = Path(__file__).resolve().parent.parent / "data" / "public"
DAYS, BPS, SHARE, BAR = 92, 0.001, 0.10, 15_000.0


def main():
    meta = json.loads((PUB / "uniswapx371b_meta.json").read_text())
    tr = pd.read_parquet(PUB / "uniswapx371b_inputs.parquet")
    print(f"===== #371 Stage 3: Arbitrum UniswapX fills 2026-08-01..10-31; fills considered {meta['fills_considered']:,}; "
          f"input transfers {len(tr):,}; tokens {tr['token'].nunique() if len(tr) else 0}")
    if tr.empty:
        print("  no input transfers: no verdict")
        return
    tr["day"] = pd.to_datetime(tr["t"], unit="s", utc=True).dt.normalize()
    usd, unpriced = [], 0
    for r in tr.itertuples():
        dec = meta["decimals"].get(r.token)
        pts = meta["prices"].get(r.token) or []
        if dec is None or not pts:
            usd.append(None)
            unpriced += 1
            continue
        s = pd.Series({pd.Timestamp(int(p["timestamp"]), unit="s", tz="UTC").round("D"): float(p["price"]) for p in pts}).sort_index()
        s = s[~s.index.duplicated()]
        usd.append(int(r.amount_raw) / 10 ** dec * float(s.asof(r.day)) if len(s) and r.day >= s.index[0] else None)
    tr["usd"] = pd.to_numeric(pd.Series(usd), errors="coerce")
    pr = tr.dropna(subset=["usd"])
    tx_n, tx_p = tr["tx"].nunique(), pr["tx"].nunique()
    vol = float(pr["usd"].sum())
    ann = vol * 365 / DAYS
    print(f"  priced input transfers {len(pr):,} of {len(tr):,} (txs {tx_p:,} of {tx_n:,}); unpriced {unpriced:,}")
    print(f"  priced fill volume ${vol:,.0f} in {DAYS} days -> ${ann:,.0f}/yr; median fill ${pr.groupby('tx')['usd'].sum().median():,.0f}")
    by = pr.groupby("filler")["usd"].sum().sort_values(ascending=False)
    print("  volume share by filler: " + ", ".join(f"{a[:10]} {v / vol:.1%}" for a, v in by.head(6).items()))
    ceil = ann * BPS
    print(f"  ceiling at {BPS * 1e4:.0f} bps: ${ceil:,.0f}/yr for all fillers; a newcomer with {SHARE:.0%}: ${ceil * SHARE:,.0f}/yr")
    print(f"  STAGE 3 VERDICT: {'KILL (10% of the ceiling < $15,000/yr)' if ceil * SHARE < BAR else 'survives (ceiling allows >= $15K/yr)'}")


if __name__ == "__main__":
    main()

"""#387 U-T5: Uniswap Continuous Clearing Auctions, buy at the clearing price and sell 1 / 7 / 30 days after the auction ends
(docs/PREREG_UNCHARTED_20261125.md).

    uv run python -m scripts.uncharted_cca_20261125 | tee docs/jx_runs/uncharted_cca_20261125.txt
Reads data/public/uncharted_387_{auctions.json,eth.json,keep.json,llama.parquet,gt.parquet} (Actions jobs u387cca, u387ccab).
Clearing price per whole token = clearingPriceQ96 / 2^96 x 10^(token decimals - currency decimals); checked against the average
price (currency raised / tokens cleared). Post-auction price: GeckoTerminal daily close of the token's largest pool (USD), else DefiLlama.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

PUB = Path(__file__).resolve().parent.parent / "data" / "public"


def h(x):
    try:
        return int(x, 16)
    except (TypeError, ValueError):
        return None


def main():
    print("===== #387 U-T5 Uniswap CCA auctions (buy at clearing price, sell after 7 days)")
    base = json.loads((PUB / "uncharted_387_auctions.json").read_text())
    eth = json.loads((PUB / "uncharted_387_eth.json").read_text()) if (PUB / "uncharted_387_eth.json").exists() else []
    allr = pd.DataFrame(base + eth)
    print(f"  auctions created by the canonical factories: {len(allr)} "
          f"({', '.join(f'{c} {n}' for c, n in allr['chain'].value_counts().items())})")
    allr["grad"] = allr["isGraduated"].map(h) == 1
    print(f"  graduated: {int(allr['grad'].sum())}")
    keep = pd.DataFrame(json.loads((PUB / "uncharted_387_keep.json").read_text()))
    print(f"  graduated + ended + real USDC/USDT/ETH + raised >= $10K (>= 4 ETH): {len(keep)}")
    if keep.empty:
        print("  STAGE 1 VERDICT: not testable (fewer than 5 auctions)")
        return
    lp = pd.read_parquet(PUB / "uncharted_387_llama.parquet") if (PUB / "uncharted_387_llama.parquet").stat().st_size else pd.DataFrame()
    gp = pd.read_parquet(PUB / "uncharted_387_gt.parquet") if (PUB / "uncharted_387_gt.parquet").stat().st_size else pd.DataFrame()
    if len(lp):
        lp["day"] = pd.to_datetime(lp["t"], unit="s", utc=True).dt.round("D")
    if len(gp):
        gp["day"] = pd.to_datetime(gp["t"], unit="s", utc=True).dt.normalize()
    rows = []
    for _, r in keep.iterrows():
        td, cd = h(r["token_decimals"]), h(r["currency_decimals"])
        q = h(r["clearingPrice"])
        clear = q / 2**96 * 10 ** (td - cd) if q is not None and td is not None and cd is not None else np.nan
        cleared = h(r.get("totalCleared"))
        avg = r["raised"] / (cleared / 10**td) if cleared else np.nan
        end = pd.Timestamp(int(r["end_ts"]), unit="s", tz="UTC").normalize()
        cur = (r.get("currency_addr") or "0x0").lower()
        is_eth = int(cur, 16) == 0
        ck = "coingecko:ethereum" if is_eth else f"{r['chain']}:{cur}"
        out = {"chain": r["chain"], "token": r.get("token_symbol"), "currency": r.get("currency_symbol"), "raised": r["raised"],
               "end": end.date(), "clear": clear, "avg_px": avg}
        g = gp[gp["auction"] == r["auction"]].set_index("day")["c"] if len(gp) else pd.Series(dtype=float)
        tk = lp[lp["key"] == f"{r['chain']}:{r['token']}"].drop_duplicates("day").set_index("day")["price"] if len(lp) else pd.Series(dtype=float)
        cu = lp[lp["key"] == ck].drop_duplicates("day").set_index("day")["price"] if len(lp) else pd.Series(dtype=float)
        for k in (1, 7, 30):
            d = end + pd.Timedelta(days=k)
            usd = g.get(d, np.nan) if len(g) else np.nan
            src = "gt"
            if pd.isna(usd):
                usd, src = tk.get(d, np.nan), "llama"
            cur_usd = cu.get(d, np.nan) if is_eth else 1.0
            out[f"ret{k}"] = (float(usd) / float(cur_usd)) / clear - 1 if clear and not pd.isna(usd) and not pd.isna(cur_usd) else np.nan
            out[f"src{k}"] = src if not pd.isna(usd) else None
        rows.append(out)
    t = pd.DataFrame(rows)
    pd.set_option("display.width", 250)
    print(t.to_string(index=False, float_format=lambda x: f"{x:10.4g}"))
    r7 = t["ret7"].dropna()
    print(f"\n  auctions with a 7-day price: {len(r7)}; median 7-day return {r7.median():.1%}; mean {r7.mean():.1%}" if len(r7) else
          "\n  no auction has a 7-day price")
    for k in (1, 30):
        rk = t[f"ret{k}"].dropna()
        if len(rk):
            print(f"  {k}-day: n {len(rk)} median {rk.median():.1%} mean {rk.mean():.1%}")
    if len(r7) < 5:
        print("  STAGE 1 VERDICT: not testable (fewer than 5 auctions with a 7-day price)")
    else:
        print(f"  STAGE 1 VERDICT: {'KILL (median 7-day return <= 0)' if r7.median() <= 0 else 'survives (kill-only)'}")


if __name__ == "__main__":
    main()

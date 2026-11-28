"""Batch NF6 #556-#559: BtcTurk / Indodax retail frenzies traded on Hyperliquid (docs/PREREG_BATCH_NF6_20261128.md).

    uv run python -m scripts.batch_nf6_20261128 | tee docs/jx_runs/batch_nf6_20261128.txt
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from ict import data as D

PUB = D.REPO_ROOT / "data" / "public"
SPLIT = pd.Timestamp("2025-01-01")
BASE = (-0.0015, 0.0033)


def main():
    loc = pd.read_parquet(PUB / "batchnf6_local_1d.parquet")
    loc["day"] = pd.to_datetime(loc["t"], unit="s").dt.normalize()
    hl = pd.read_parquet(PUB / "uncharted_385_candles.parquet")
    hl["day"] = pd.to_datetime(hl["t"], unit="ms").dt.normalize()
    hl = hl.drop_duplicates(["coin", "day"])
    hl["up"] = hl["coin"].str.replace(r"^k", "", regex=True).str.upper()
    px = hl.pivot(index="day", columns="up", values="c").sort_index()
    btc = px["BTC"]
    ideas = {556: ("btcturk", True), 557: ("indodax", True), 558: ("btcturk", False), 559: ("indodax", False)}
    yrs = (pd.Timestamp("2026-11-25") - SPLIT).days / 365.25
    for k, (venue, pump) in ideas.items():
        tr = []
        for coin, g in loc[loc["venue"] == venue].groupby("coin"):
            if coin in ("BTC", "USDT", "USDC") or coin not in px:
                continue
            g = g.drop_duplicates("day").set_index("day").sort_index()
            vol = g["v"] * g["c"]
            med = vol.shift().rolling(30, min_periods=20).median()
            chg = g["c"].pct_change()
            busy = None
            for d in g.index:
                hit = vol[d] >= 10 * med[d] and (chg[d] >= 0.3 if pump else True)
                if not bool(hit) or (busy is not None and d <= busy):
                    continue
                d1 = d + pd.Timedelta(days=3)
                if d in px.index and d1 in px.index and px.at[d, coin] > 0 and px.at[d1, coin] > 0:
                    tr.append((d, coin, -((px.at[d1, coin] / px.at[d, coin] - 1) - (btc[d1] / btc[d] - 1)) - 0.0009))
                    busy = d1
        t = pd.DataFrame(tr, columns=["d", "coin", "r"])
        n_coins = loc[loc["venue"] == venue]["coin"].nunique()
        print(f"#{k} {venue} {'pump day' if pump else 'frenzy'} -> short HL 3 d ({n_coins} local pairs on HL): {len(t)} trades")
        if n_coins == 0:
            print("   NOT TESTABLE (no history fetched)\n")
            continue
        res = {}
        for label, g in (("Stage 1 (< 2025)", t[t.d < SPLIT] if len(t) else t), ("Stage 2 (2025-26)", t[t.d >= SPLIT] if len(t) else t)):
            r = g["r"] if len(g) else pd.Series(dtype=float)
            n = len(r)
            tt = r.mean() / (r.std(ddof=1) / np.sqrt(n)) if n > 1 and r.std(ddof=1) > 0 else np.nan
            ex3 = r.sort_values().iloc[:-3].sum() if n > 3 else np.nan
            res[label] = (n, r.mean() if n else np.nan, tt, ex3)
            print(f"   {label}: n {n}, mean {r.mean() if n else np.nan:+.2%} (median {r.median() if n else np.nan:+.2%}, t {tt:.2f}), "
                  f"sum without the 3 best {ex3:+.2f}")
        n1, m1, _, _ = res["Stage 1 (< 2025)"]
        n2, m2, t2, ex3 = res["Stage 2 (2025-26)"]
        if n1 >= 8 and not (m1 > BASE[0]):
            v = "KILL (Stage 1)"
        else:
            ok = n2 >= 15 and m2 >= 0.02 and t2 >= 2 and ex3 > 0 and m2 >= BASE[1] + 0.01
            v = ("PASS" if ok else "FAIL") + (" (Stage 1 < 8: no kill possible)" if n1 < 8 else "")
        print(f"   VERDICT {v} | $/yr at $3,000 per trade: ${(m2 * 3000 * n2 / yrs) if n2 else 0:,.0f}\n")


if __name__ == "__main__":
    main()

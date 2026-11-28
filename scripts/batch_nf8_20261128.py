"""Batch NF8 #564-#567: Binance leverage signals traded on Hyperliquid (docs/PREREG_BATCH_NF8_20261128.md).

    uv run python -m scripts.batch_nf8_20261128 | tee docs/jx_runs/batch_nf8_20261128.txt
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from ict import data as D

PUB = D.REPO_ROOT / "data" / "public"
SPLIT = pd.Timestamp("2025-01-01")
SB = {3: (-0.0015, 0.0033), 7: (-0.0021, 0.0095)}  # short baselines (Stage 1, Stage 2)


def main():
    hl = pd.read_parquet(PUB / "uncharted_385_candles.parquet")
    hl["day"] = pd.to_datetime(hl["t"], unit="ms").dt.normalize()
    hl = hl.drop_duplicates(["coin", "day"])
    px = hl.pivot(index="day", columns="coin", values="c").sort_index()
    btc = px["BTC"]
    oi = pd.read_parquet(PUB / "batchj_cz_oi_binance.parquet")
    oi["coin"] = oi["symbol"].str.replace("USDT_PERP.A", "", regex=False)
    oi["day"] = pd.to_datetime(oi["t"], unit="s").dt.normalize()
    oi = oi.pivot_table(index="day", columns="coin", values="c")
    lq = pd.read_parquet(PUB / "batchj_cz_liq_binance.parquet")
    lq["coin"] = lq["symbol"].str.replace("USDT_PERP.A", "", regex=False)
    lq["day"] = pd.to_datetime(lq["t"], unit="s").dt.normalize()
    ll = lq.pivot_table(index="day", columns="coin", values="l")
    fu = pd.read_parquet(PUB / "hl_funding.parquet")
    fu["day"] = pd.to_datetime(fu["time"], unit="ms").dt.normalize()
    fd = fu.groupby(["day", "coin"])["rate"].mean().unstack() * 24 * 365  # daily mean hourly rate -> annualised
    holds, sides = {564: 7, 565: 7, 566: 3, 567: 7}, {564: -1, 565: +1, 566: +1, 567: +1}
    tr = {k: [] for k in holds}
    coins = [c for c in px.columns if c not in ("BTC", "ETH")]
    for c in coins:
        p = px[c]
        busy = {k: None for k in holds}
        o = oi[c].reindex(px.index) if c in oi else None
        liq = ll[c].reindex(px.index).fillna(0) if c in ll else None
        f = fd[c].reindex(px.index) if c in fd else None
        for i, d in enumerate(px.index):
            if i < 8 or not (p.iloc[i] > 0):
                continue
            hits = {}
            if o is not None and o.iloc[i - 7] > 0 and p.iloc[i - 7] > 0:
                oig7 = o.iloc[i] / o.iloc[i - 7] - 1
                pc7 = p.iloc[i] / p.iloc[i - 7] - 1
                hits[564] = oig7 >= 0.5 and abs(pc7) < 0.05
                hits[567] = oig7 >= 0.3 and pc7 <= -0.10
            if o is not None and liq is not None and o.iloc[i - 3] > 0 and p.iloc[i - 3] > 0:
                hits[565] = (o.iloc[i] / o.iloc[i - 3] - 1 <= -0.3) and liq.iloc[i - 2:i + 1].sum() >= 0.03 * o.iloc[i - 3] * p.iloc[i - 3]
            if f is not None and i >= 6:
                hits[566] = f.iloc[i - 5:i - 2].mean() >= 0.30 and f.iloc[i] <= -0.10
            for k, h in hits.items():
                if not bool(h) or (busy[k] is not None and d <= busy[k]):
                    continue
                d1 = d + pd.Timedelta(days=holds[k])
                if d1 in px.index and p.get(d1, np.nan) > 0:
                    tr[k].append((d, c, sides[k] * ((p[d1] / p[d] - 1) - (btc[d1] / btc[d] - 1)) - 0.0009))
                    busy[k] = d1
    names = {564: "Silent leverage build-up -> short 7 d", 565: "Deleveraging complete -> long 7 d",
             566: "HL funding capitulation -> long 3 d", 567: "Short-squeeze fuel -> long 7 d"}
    yrs = (pd.Timestamp("2026-11-25") - SPLIT).days / 365.25
    for k, name in names.items():
        t = pd.DataFrame(tr[k], columns=["d", "coin", "r"])
        b1, b2 = (SB[holds[k]][0], SB[holds[k]][1]) if sides[k] < 0 else (-SB[holds[k]][0], -SB[holds[k]][1])
        print(f"#{k} {name}: {len(t)} trades | baseline for this side: Stage 1 {b1:+.2%}, Stage 2 {b2:+.2%}")
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
        if n1 >= 8 and not (m1 > b1):
            v = "KILL (Stage 1)"
        else:
            ok = n2 >= 15 and m2 >= 0.02 and t2 >= 2 and ex3 > 0 and m2 >= b2 + 0.01
            v = ("PASS" if ok else "FAIL") + (" (Stage 1 < 8: no kill possible)" if n1 < 8 else "")
        print(f"   VERDICT {v} | $/yr at $3,000 per trade: ${(m2 * 3000 * n2 / yrs) if n2 else 0:,.0f}\n")


if __name__ == "__main__":
    main()

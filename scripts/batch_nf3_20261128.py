"""Batch NF3 #543-#546: Binance events traded on Hyperliquid (docs/PREREG_BATCH_NF3_20261128.md).

    uv run python -m scripts.batch_nf3_20261128 | tee docs/jx_runs/batch_nf3_20261128.txt
"""
from __future__ import annotations

import json
import re

import numpy as np
import pandas as pd

from ict import data as D

PUB = D.REPO_ROOT / "data" / "public"
SPLIT, END = pd.Timestamp("2025-01-01", tz="UTC"), pd.Timestamp("2026-11-25", tz="UTC")
PATS = {543: r"Will List .*Seed Tag|with Seed Tag", 544: r"Will Add .* on .*(Earn|VIP Loan|Margin)",
        545: r"Futures Will Launch (USDⓈ-M|USDⓈ-Margined) [A-Z0-9]+USDT Perpetual", 546: r"Futures Will Launch (USDⓈ-M|USDⓈ-Margined) [A-Z0-9]+USDT Perpetual"}
NAMES = {543: "Seed-tag listing -> short on HL 7 d", 544: "Earn/loan/margin add -> short on HL 7 d",
         545: "Binance perp launch (coin already on HL) -> short on HL 7 d", 546: "Binance pre-market perp launch -> short on HL 7 d"}


def catalog():
    d = json.loads((PUB / "uncharted_w3_binance_ann.json").read_text())
    rows = []

    def walk(x):
        if isinstance(x, dict):
            if "title" in x and "releaseDate" in x:
                rows.append(x)
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
    walk(d)
    return {r["code"]: r for r in rows}.values()


def main():
    cd = pd.read_parquet(PUB / "uncharted_385_candles.parquet")
    cd["day"] = pd.to_datetime(cd["t"], unit="ms", utc=True).dt.normalize()
    cd = cd.drop_duplicates(["coin", "day"])
    px = {c: g.set_index("day")["c"].sort_index() for c, g in cd.groupby("coin")}
    btc = px["BTC"]
    hl = set(px)
    cat = list(catalog())
    for k, name in NAMES.items():
        ev = []
        for r in cat:
            t = r["title"]
            if not re.search(PATS[k], t) or "Remov" in t:
                continue
            if k == 545 and "Pre-Market" in t:
                continue
            if k == 546 and "Pre-Market" not in t:
                continue
            coins = (set(re.findall(r"([A-Z0-9]{2,12})USDT", t)) | set(re.findall(r"\(([A-Z0-9]{2,12})\)", t))) & hl
            coins -= {"BTC", "ETH", "USDC", "USDT"}
            if not coins:
                continue
            a = pd.Timestamp(int(r["releaseDate"]), unit="ms", tz="UTC")
            d0 = a.normalize() + pd.Timedelta(days=1)
            d1 = d0 + pd.Timedelta(days=7)
            if d1 > END:
                continue
            rs = []
            for c in coins:
                s = px[c]
                if d0 not in s.index or d1 not in s.index or d0 not in btc.index or d1 not in btc.index:
                    continue
                rs.append(-((s[d1] / s[d0] - 1) - (btc[d1] / btc[d0] - 1)) - 0.0009)
            if rs:
                ev.append((a, float(np.mean(rs)), ",".join(sorted(coins))))
        e = pd.DataFrame(ev, columns=["a", "r", "coins"])
        print(f"#{k} {name}: {len(e)} events with HL prices")
        res = {}
        for label, g in (("Stage 1 (< 2025)", e[e.a < SPLIT] if len(e) else e), ("Stage 2 (2025-26)", e[e.a >= SPLIT] if len(e) else e)):
            r = g["r"] if len(g) else pd.Series(dtype=float)
            n = len(r)
            t = r.mean() / (r.std(ddof=1) / np.sqrt(n)) if n > 1 and r.std(ddof=1) > 0 else np.nan
            ex3 = r.sort_values().iloc[:-3].sum() if n > 3 else np.nan
            res[label] = (n, r.mean() if n else np.nan, t, ex3)
            print(f"   {label}: n {n}, mean excess {r.mean() if n else np.nan:+.2%} (median {r.median() if n else np.nan:+.2%}, t {t:.2f}), "
                  f"sum without the 3 best {ex3:+.2f}")
        n1, m1, _, _ = res["Stage 1 (< 2025)"]
        n2, m2, t2, ex3 = res["Stage 2 (2025-26)"]
        if n1 >= 8 and not (m1 > 0):
            v = "KILL (Stage 1)"
        else:
            v = ("PASS" if (n2 >= 15 and m2 >= 0.02 and t2 >= 2 and ex3 > 0) else "FAIL") + (" (Stage 1 < 8 events: no kill possible)" if n1 < 8 else "")
        yrs = (END - SPLIT).days / 365.25
        print(f"   VERDICT {v} | $/yr at $3,000 per event: ${(m2 * 3000 * n2 / yrs) if n2 else 0:,.0f}\n")


if __name__ == "__main__":
    main()

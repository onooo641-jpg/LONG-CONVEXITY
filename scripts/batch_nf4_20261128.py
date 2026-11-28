"""Batch NF4 #547-#550: Korean retail flows traded on Hyperliquid (docs/PREREG_BATCH_NF4_20261128.md).

    uv run python -m scripts.batch_nf4_20261128 | tee docs/jx_runs/batch_nf4_20261128.txt
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from ict import data as D

PUB = D.REPO_ROOT / "data" / "public"
SPLIT = pd.Timestamp("2025-01-01")
EXCL = {"BTC", "USDT", "USDC", "USDE", "USD1"}


def main():
    up = pd.read_parquet(PUB / "distinct_upbit_1d.parquet")
    up["day"] = pd.to_datetime(up["day"])
    hl = pd.read_parquet(PUB / "uncharted_385_candles.parquet")
    hl["day"] = pd.to_datetime(hl["t"], unit="ms").dt.normalize()
    hl = hl.drop_duplicates(["coin", "day"])
    hl["up"] = hl["coin"].str.replace(r"^k", "", regex=True).str.upper()
    hpx = {u: g.set_index("day")["c"].sort_index() for u, g in hl.groupby("up")}
    btc_h, btc_k = hpx["BTC"], up[up.coin == "BTC"].set_index("day")["krw_close"].sort_index()
    trades = {547: [], 548: [], 549: [], 550: []}

    def rec(k, coin, d, h, side):
        s = hpx[coin]
        d1 = d + pd.Timedelta(days=h)
        if d not in s.index or d1 not in s.index or d not in btc_h.index or d1 not in btc_h.index:
            return False
        trades[k].append((d, coin, side * ((s[d1] / s[d] - 1) - (btc_h[d1] / btc_h[d] - 1)) - 0.0009))
        return True

    for coin, g in up.groupby("coin"):
        if coin in EXCL or coin not in hpx:
            continue
        g = g.set_index("day").sort_index()
        val = g["krw_value"]
        med = val.shift().rolling(30, min_periods=20).median()
        hk = hpx[coin].reindex(g.index)
        prem = (g["krw_close"] / hk) / (btc_k.reindex(g.index) / btc_h.reindex(g.index)) - 1
        busy = {547: None, 548: None, 549: None}
        for i, d in enumerate(g.index):
            for k, hit, side in ((547, val.iloc[i] >= 10 * med.iloc[i] and val.iloc[i] >= 5e10, -1),
                                 (548, i > 0 and prem.iloc[i] >= 0.08 and prem.iloc[i - 1] < 0.08, +1),
                                 (549, i > 0 and prem.iloc[i] <= -0.05 and prem.iloc[i - 1] > -0.05, -1)):
                if bool(hit) and (busy[k] is None or d > busy[k]) and rec(k, coin, d, 3, side):
                    busy[k] = d + pd.Timedelta(days=3)
    kor = pd.read_parquet(PUB / "uncharted_w3b_korea.parquet")
    kor = kor[kor["venue"].str.lower().str.contains("upbit")]
    for _, r in kor.iterrows():
        coin, l0 = r["coin"], pd.Timestamp(r["first_day"])
        g = up[up.coin == coin].set_index("day").sort_index()["krw_value"] if coin in set(up.coin) else None
        if coin in EXCL or coin not in hpx or g is None:
            continue
        d1, d7 = l0, l0 + pd.Timedelta(days=6)
        if d1 in g.index and d7 in g.index and g[d1] > 0 and g[d7] < 0.2 * g[d1]:
            rec(550, coin, d7, 14, -1)

    names = {547: "Upbit retail frenzy fade (short 3 d)", 548: "Coin kimchi premium >= +8% -> long HL 3 d",
             549: "Coin kimchi discount <= -5% -> short HL 3 d", 550: "Dying Upbit KRW listing -> short HL day 7 -> 21"}
    yrs = (pd.Timestamp("2026-11-25") - SPLIT).days / 365.25
    for k, name in names.items():
        t = pd.DataFrame(trades[k], columns=["d", "coin", "r"])
        print(f"#{k} {name}: {len(t)} trades")
        res = {}
        for label, g in (("Stage 1 (< 2025)", t[t.d < SPLIT]), ("Stage 2 (2025-26)", t[t.d >= SPLIT])):
            r = g["r"]
            n = len(r)
            tt = r.mean() / (r.std(ddof=1) / np.sqrt(n)) if n > 1 and r.std(ddof=1) > 0 else np.nan
            ex3 = r.sort_values().iloc[:-3].sum() if n > 3 else np.nan
            res[label] = (n, r.mean() if n else np.nan, tt, ex3)
            print(f"   {label}: n {n}, mean excess {r.mean() if n else np.nan:+.2%} (median {r.median() if n else np.nan:+.2%}, t {tt:.2f}, "
                  f"win {(r > 0).mean() if n else np.nan:.0%}), sum without the 3 best {ex3:+.2f}")
        n1, m1, _, _ = res["Stage 1 (< 2025)"]
        n2, m2, t2, ex3 = res["Stage 2 (2025-26)"]
        v = "KILL (Stage 1)" if (n1 >= 8 and not (m1 > 0)) else \
            (("PASS" if (n2 >= 15 and m2 >= 0.02 and t2 >= 2 and ex3 > 0) else "FAIL") + (" (Stage 1 < 8: no kill possible)" if n1 < 8 else ""))
        print(f"   VERDICT {v} | $/yr at $3,000 per trade: ${(m2 * 3000 * n2 / yrs) if n2 else 0:,.0f}\n")


if __name__ == "__main__":
    main()

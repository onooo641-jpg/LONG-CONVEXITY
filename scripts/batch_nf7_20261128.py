"""Batch NF7 #560-#563 (docs/PREREG_BATCH_NF7_20261128.md).

    uv run python -m scripts.batch_nf7_20261128 | tee docs/jx_runs/batch_nf7_20261128.txt
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from ict import data as D

PUB = D.REPO_ROOT / "data" / "public"
SPLIT = pd.Timestamp("2025-01-01")
EXCL = {"BTC", "USDT", "USDC", "USDE", "USD1"}
BASE = {3: (-0.0015, 0.0033), 7: (-0.0021, 0.0095)}


def main():
    up = pd.read_parquet(PUB / "distinct_upbit_1d.parquet")
    up["day"] = pd.to_datetime(up["day"])
    hl = pd.read_parquet(PUB / "uncharted_385_candles.parquet")
    hl["day"] = pd.to_datetime(hl["t"], unit="ms").dt.normalize()
    hl = hl.drop_duplicates(["coin", "day"])
    hl["up"] = hl["coin"].str.replace(r"^k", "", regex=True).str.upper()
    px = hl.pivot(index="day", columns="up", values="c").sort_index()
    btc = px["BTC"]
    btc_k = up[up.coin == "BTC"].set_index("day")["krw_close"].sort_index()
    holds = {560: 7, 561: 7, 562: 3, 563: 7}
    tr = {k: [] for k in holds}

    def rec(k, coin, d):
        d1 = d + pd.Timedelta(days=holds[k])
        if d in px.index and d1 in px.index and px.at[d, coin] > 0 and px.at[d1, coin] > 0:
            tr[k].append((d, coin, -((px.at[d1, coin] / px.at[d, coin] - 1) - (btc[d1] / btc[d] - 1)) - 0.0009))
            return d1
        return None

    for coin, g in up.groupby("coin"):
        if coin in EXCL or coin not in px:
            continue
        g = g.set_index("day").sort_index()
        val, cl = g["krw_value"], g["krw_close"]
        med = val.shift().rolling(30, min_periods=20).median()
        chg = cl.pct_change()
        frenzy = val >= 10 * med
        prem = (cl / px[coin].reindex(g.index)) / (btc_k.reindex(g.index) / btc.reindex(g.index)) - 1
        streak = (prem >= 0.03).astype(int).groupby((prem < 0.03).cumsum()).cumsum()
        busy = {k: None for k in holds}
        last_frenzy = None
        for d in g.index:
            hits = {560: bool(frenzy[d] and chg[d] >= 0.3),
                    561: last_frenzy is not None and (d - last_frenzy).days <= 30 and d != last_frenzy and val[d] < 0.2 * val[last_frenzy],
                    562: bool(frenzy[d] and chg[d] <= -0.2),
                    563: bool(streak[d] == 5)}
            if frenzy[d]:
                last_frenzy = d
            for k, h in hits.items():
                if h and (busy[k] is None or d > busy[k]):
                    e = rec(k, coin, d)
                    if e is not None:
                        busy[k] = e
                        if k == 561:
                            last_frenzy = None
    names = {560: "Pump day -> short 7 d", 561: "Post-frenzy dry-up -> short 7 d", 562: "Dump-day continuation -> short 3 d",
             563: "Persistent Korean premium (5 days >= +3%) -> short 7 d"}
    yrs = (pd.Timestamp("2026-11-25") - SPLIT).days / 365.25
    for k, name in names.items():
        t = pd.DataFrame(tr[k], columns=["d", "coin", "r"])
        b1, b2 = BASE[holds[k]]
        print(f"#{k} {name}: {len(t)} trades | short baseline {holds[k]} d: Stage 1 {b1:+.2%}, Stage 2 {b2:+.2%}")
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

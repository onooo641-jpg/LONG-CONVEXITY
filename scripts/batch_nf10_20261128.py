"""Batch NF10 #572-#575 (docs/PREREG_BATCH_NF10_20261128.md).

    uv run python -m scripts.batch_nf10_20261128 | tee docs/jx_runs/batch_nf10_20261128.txt
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from ict import data as D

PUB = D.REPO_ROOT / "data" / "public"
MID = pd.Timestamp("2026-08-16", tz="UTC")


def show(k, name, t, split, min_mean, label="VERDICT", evidence=False):
    print(f"#{k} {name}: {len(t)} trades")
    res = []
    for lab, g in (("Stage 1", t[t.ts < split]), ("Stage 2", t[t.ts >= split])):
        r = g["r"]
        n = len(r)
        tt = r.mean() / (r.std(ddof=1) / np.sqrt(n)) if n > 1 and r.std(ddof=1) > 0 else np.nan
        ex3 = r.sort_values().iloc[:-3].sum() if n > 3 else np.nan
        res.append((n, r.mean() if n else np.nan, tt, ex3))
        print(f"   {lab}: n {n}, mean {r.mean() if n else np.nan:+.3%} (median {r.median() if n else np.nan:+.3%}, t {tt:.2f}, "
              f"win {(r > 0).mean() if n else np.nan:.0%}), sum without the 3 best {ex3:+.2f}")
    (n1, m1, _, _), (n2, m2, t2, ex3) = res
    if n1 >= 30 and not (m1 > 0):
        v = "KILL (Stage 1)"
    else:
        ok = n2 >= 30 and m2 >= min_mean and t2 >= 2 and ex3 > 0
        v = ("MECHANISM CONFIRMED" if ok else "NOT CONFIRMED") if evidence else ("PASS" if ok else "FAIL")
    print(f"   {label} {v}\n")


def main():
    h = pd.read_parquet(PUB / "wickscale_hl_1h.parquet")
    h["ts"] = pd.to_datetime(h["t"], unit="ms" if h["t"].max() > 1e11 else "s", utc=True)
    h = h.drop_duplicates(["coin", "ts"])
    for c in ("c", "v"):
        h[c] = h[c].astype(float)
    piv = h.pivot(index="ts", columns="coin", values="c").sort_index()
    btc = piv["BTC"]
    upc = set(pd.read_parquet(PUB / "distinct_upbit_1d.parquet")["coin"].unique())
    basket = [c for c in piv.columns if c.lstrip("k").upper() in upc and c not in ("BTC", "ETH")]
    rows = {572: [], 573: []}
    for day in pd.date_range(piv.index.min().normalize() + pd.Timedelta(days=1), piv.index.max().normalize(), freq="D"):
        for k, a, b, side in ((572, day - pd.Timedelta(hours=1), day + pd.Timedelta(hours=3), +1),
                              (573, day + pd.Timedelta(hours=3), day + pd.Timedelta(hours=9), -1)):
            if a in piv.index and b in piv.index:
                rr = (piv.loc[b, basket] / piv.loc[a, basket] - 1).dropna()
                if len(rr) >= 10:
                    rows[k].append((a, side * (float(rr.mean()) - (btc[b] / btc[a] - 1)) - 0.0009))
    print(f"Upbit-listed HL coins in the basket: {len(basket)}\n")
    show(572, "Korean morning buying (long basket 23:00 -> 03:00 UTC)", pd.DataFrame(rows[572], columns=["ts", "r"]), MID, 0.002)
    show(573, "Korean morning give-back (short basket 03:00 -> 09:00 UTC)", pd.DataFrame(rows[573], columns=["ts", "r"]), MID, 0.002)

    u = pd.read_parquet(PUB / "batchh2_unseen_1h.parquet")
    u["ts"] = pd.to_datetime(u["t"], unit="ms" if u["t"].max() > 1e11 else "s", utc=True)
    tr = []
    for sym, g in u.drop_duplicates(["sym", "ts"]).sort_values(["sym", "ts"]).groupby("sym"):
        c = g["close"].astype(float).to_numpy()
        ts = g["ts"].to_numpy()
        r = pd.Series(c).pct_change()
        sig = r.rolling(168, min_periods=120).std().shift().to_numpy()
        busy = -1
        for i in range(170, len(c) - 4):
            if i > busy and r.iloc[i] <= -5 * sig[i]:
                tr.append((ts[i], c[i + 4] / c[i] - 1 - 0.0009))
                busy = i + 4
    t = pd.DataFrame(tr, columns=["ts", "r"])
    t["ts"] = pd.to_datetime(t["ts"], utc=True)
    show(574, "#569 on Binance hourly (evidence only)", t, pd.Timestamp("2025-01-01", tz="UTC"), 0.003, evidence=True)

    tr = []
    for coin, g in h.sort_values(["coin", "ts"]).groupby("coin"):
        g = g.reset_index(drop=True)
        r = g["c"].pct_change()
        sig = r.rolling(168, min_periods=120).std().shift()
        usd = g["v"] * g["c"]
        med = usd.shift().rolling(168, min_periods=120).median()
        busy = -1
        for i in range(170, len(g) - 4):
            if i > busy and usd.iloc[i] >= 10 * med.iloc[i] and r.iloc[i] >= 3 * sig.iloc[i]:
                tr.append((g["ts"].iloc[i], -(g["c"].iloc[i + 4] / g["c"].iloc[i] - 1) - 0.0009))
                busy = i + 4
    show(575, "Intraday frenzy pump (short 4 h)", pd.DataFrame(tr, columns=["ts", "r"]), MID, 0.003)


if __name__ == "__main__":
    main()

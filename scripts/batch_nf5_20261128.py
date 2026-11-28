"""Batch NF5 #552-#555 (docs/PREREG_BATCH_NF5_20261128.md).

    uv run python -m scripts.batch_nf5_20261128 | tee docs/jx_runs/batch_nf5_20261128.txt
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
    px = hl.pivot(index="day", columns="up", values="c").sort_index()
    btc = px["BTC"]
    tr = {552: [], 553: [], 554: [], 555: []}

    def rec(k, coin, d, h, side):
        if coin not in px or d not in px.index:
            return False
        d1 = d + pd.Timedelta(days=h)
        if d1 not in px.index or not (px.at[d, coin] > 0) or not (px.at[d1, coin] > 0):
            return False
        tr[k].append((d, coin, side * ((px.at[d1, coin] / px.at[d, coin] - 1) - (btc[d1] / btc[d] - 1)) - 0.0009))
        return True

    for coin, g in up.groupby("coin"):
        if coin in EXCL or coin not in px:
            continue
        g = g.set_index("day").sort_index()
        val, cl = g["krw_value"], g["krw_close"]
        med = val.shift().rolling(30, min_periods=20).median()
        ret = cl.pct_change()
        a30 = val.rolling(30).mean()
        busy = {552: None, 554: None, 555: None}
        for i, d in enumerate(g.index):
            for k, hit, h, side in ((552, i >= 180 and a30.iloc[i] < 0.2 * a30.shift(90).iloc[i], 14, -1),
                                    (554, val.iloc[i] >= 10 * med.iloc[i] and ret.iloc[i] <= -0.2, 3, +1),
                                    (555, val.iloc[i] >= 10 * med.iloc[i] and ret.iloc[i] >= 0.3, 3, -1)):
                if bool(hit) and (busy[k] is None or d > busy[k]) and rec(k, coin, d, h, side):
                    busy[k] = d + pd.Timedelta(days=h if k != 552 else 60)
    kor = pd.read_parquet(PUB / "uncharted_w3b_korea.parquet")
    for _, r in kor[kor["venue"].str.lower().str.contains("bithumb")].iterrows():
        coin, l0 = str(r["coin"]).upper(), pd.Timestamp(r["first_day"])
        d1, d7 = l0, l0 + pd.Timedelta(days=6)
        if coin in EXCL or coin not in px or d1 not in px.index or d7 not in px.index:
            continue
        if px.at[d7, coin] < px.at[d1, coin]:
            rec(553, coin, d7, 14, -1)

    rr = px.drop(columns=[c for c in ("BTC", "ETH") if c in px])
    base = {}
    for h in (3, 14):
        ex = -((rr.shift(-h) / rr - 1).sub(btc.shift(-h) / btc - 1, axis=0)) - 0.0009
        base[h] = {"s1": float(ex.loc["2023-06-01":"2024-12-31"].stack().mean()), "s2": float(ex.loc["2025-01-01":"2026-10-31"].stack().mean())}
    names = {552: ("Korean interest collapse -> short HL 14 d", 14, -1), 553: ("Dying Bithumb listing -> short HL day 7 -> 21", 14, -1),
             554: ("Upbit panic dump -> long HL 3 d", 3, +1), 555: ("Upbit pump day -> short HL 3 d", 3, -1)}
    yrs = (pd.Timestamp("2026-11-25") - SPLIT).days / 365.25
    for k, (name, h, side) in names.items():
        t = pd.DataFrame(tr[k], columns=["d", "coin", "r"])
        b1, b2 = (base[h]["s1"], base[h]["s2"]) if side < 0 else (0.0, 0.0)
        print(f"#{k} {name}: {len(t)} trades" + (f" | short baseline {h} d: Stage 1 {b1:+.2%}, Stage 2 {b2:+.2%}" if side < 0 else ""))
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
            ok = n2 >= 15 and m2 >= 0.02 and t2 >= 2 and ex3 > 0 and (side > 0 or m2 >= b2 + 0.01)
            v = ("PASS" if ok else "FAIL") + (" (Stage 1 < 8: no kill possible)" if n1 < 8 else "")
        print(f"   VERDICT {v} | $/yr at $3,000 per trade: ${(m2 * 3000 * n2 / yrs) if n2 else 0:,.0f}\n")


if __name__ == "__main__":
    main()

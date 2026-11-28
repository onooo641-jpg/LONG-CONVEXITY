"""Batch NF11 #576-#579: Reg SHO threshold-list forced buy-ins (docs/PREREG_BATCH_NF11_20261128.md).

    uv run python -m scripts.batch_nf11_20261128 | tee docs/jx_runs/batch_nf11_20261128.txt
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from ict import data as D

PUB = D.REPO_ROOT / "data" / "public"
SPLIT = pd.Timestamp("2023-01-01")


def main():
    th = pd.read_parquet(PUB / "batchnf11_threshold.parquet")
    th["day"] = pd.to_datetime(th["day"])
    files = sorted(th["day"].unique())
    pos = {d: i for i, d in enumerate(files)}
    px = pd.read_parquet(PUB / "batchnf11_px.parquet")
    px["d"] = pd.to_datetime(px["t"], unit="s").dt.normalize()
    P = {s: g.drop_duplicates("d").set_index("d").sort_index() for s, g in px.groupby("sym")}
    spy = P["SPY"]["adj"]

    def ret(sym, d0, h, side):
        """side x (stock - SPY) from the close on/before d0 to h trading days later; None if missing or entry close < $1."""
        if sym not in P:
            return None
        s = P[sym]
        i = s.index.searchsorted(d0, side="right") - 1
        if i < 0 or i + h >= len(s) or (d0 - s.index[i]).days > 4 or s["close"].iloc[i] < 1:
            return None
        a, b = s["adj"].iloc[i], s["adj"].iloc[i + h]
        j = spy.index.searchsorted(s.index[i], side="right") - 1
        k = spy.index.searchsorted(s.index[i + h], side="right") - 1
        return side * ((b / a - 1) - (spy.iloc[k] / spy.iloc[j] - 1)) - 0.002

    ev = {576: [], 577: [], 578: [], 579: []}
    tried = {k: 0 for k in ev}
    for sym, g in th.groupby("sym"):
        idx = sorted(pos[d] for d in g["day"])
        runs, start = [], idx[0]
        for a, b in zip(idx, idx[1:] + [None]):
            if b is None or b != a + 1:
                runs.append((start, a))
                start = b
        for s0, s1 in runs:
            n = s1 - s0 + 1
            day = lambda k: files[s0 + k - 1]  # noqa: E731
            plan = [(577, day(1), 12, +1)]
            if n >= 11:
                plan.append((576, day(11), 5, +1))
            if n >= 13 and s1 + 1 < len(files):
                plan.append((578, files[s1 + 1], 5, -1))
            if n >= 20:
                plan.append((579, day(20), 5, +1))
            for k, d0, h, side in plan:
                tried[k] += 1
                r = ret(sym, pd.Timestamp(d0), h, side)
                if r is not None:
                    ev[k].append((pd.Timestamp(d0), sym, r))
    print(f"threshold files {len(files)} ({pd.Timestamp(files[0]).date()}..{pd.Timestamp(files[-1]).date()}), tickers {th.sym.nunique()}, "
          f"priced tickers {len(P) - 1}\n")
    names = {576: "Close-out deadline: long day 11 -> 16", 577: "Addition: long day 1 -> 13", 578: "Removal: short 5 d", 579: "Long stay: long day 20 -> 25"}
    yrs = (pd.Timestamp("2026-11-25") - SPLIT).days / 365.25
    for k, name in names.items():
        t = pd.DataFrame(ev[k], columns=["d", "sym", "r"])
        cover = len(t) / tried[k] if tried[k] else 0
        print(f"#{k} {name}: {len(t)} priced events of {tried[k]} ({cover:.0%} with prices)")
        res = []
        for lab, g in (("Stage 1 (< 2023)", t[t.d < SPLIT]), ("Stage 2 (2023-26)", t[t.d >= SPLIT])):
            r = g["r"]
            n = len(r)
            tt = r.mean() / (r.std(ddof=1) / np.sqrt(n)) if n > 1 and r.std(ddof=1) > 0 else np.nan
            ex3 = r.sort_values().iloc[:-3].sum() if n > 3 else np.nan
            res.append((n, r.mean() if n else np.nan, tt, ex3))
            print(f"   {lab}: n {n}, mean {r.mean() if n else np.nan:+.2%} (median {r.median() if n else np.nan:+.2%}, t {tt:.2f}, "
                  f"win {(r > 0).mean() if n else np.nan:.0%}), sum without the 3 best {ex3:+.2f}")
        (n1, m1, _, _), (n2, m2, t2, ex3) = res
        if n1 >= 20 and not (m1 > 0):
            v = "KILL (Stage 1)"
        else:
            ok = n2 >= 30 and m2 >= 0.01 and t2 >= 2 and ex3 > 0
            v = ("PASS" if ok else "FAIL") + ("" if cover >= 0.6 else " (survivorship-limited: < 60% of events priced)")
        print(f"   VERDICT {v} | $/yr at $3,000 per event: ${(m2 * 3000 * n2 / yrs) if n2 else 0:,.0f}\n")


if __name__ == "__main__":
    main()

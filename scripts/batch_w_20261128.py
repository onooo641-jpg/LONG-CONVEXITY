"""Batch W #530-#531: energy hedging-pressure seasonals (docs/PREREG_BATCH_W_20261128.md).

    uv run python -m scripts.batch_w_20261128 | tee docs/jx_runs/batch_w_20261128.txt
"""
import numpy as np
import pandas as pd

from ict import data as D

OUT = D.REPO_ROOT / "data" / "public"


def stats(x):
    x = pd.Series(x, dtype=float).dropna()
    n = len(x)
    t = x.mean() / (x.std(ddof=1) / np.sqrt(n)) if n > 1 and x.std(ddof=1) > 0 else np.nan
    return n, (x.mean() if n else np.nan), t


def show(label, x):
    n, m, t = stats(x)
    return f"   {label}: n {n}, mean {m:+.2%}, t {t:.2f}"


def last_close(s, y, m):
    end = pd.Timestamp(year=y, month=m, day=1) + pd.offsets.MonthEnd(0)
    i = s.index.searchsorted(end, side="right") - 1
    return float(s.iloc[i]) if i >= 0 and s.index[i].year == y and s.index[i].month == m else None


def main():
    e = pd.read_parquet(OUT / "batchw_etf_1d.parquet")
    e["d"] = pd.to_datetime(e["t"], unit="s").dt.normalize()
    px = {s: g.set_index("d")["adj"].sort_index() for s, g in e.groupby("sym")}
    print("coverage: " + ", ".join(f"{s} {v.index.min().date()}..{v.index.max().date()}" for s, v in px.items()) + "\n")

    r = {}
    for y in range(2009, 2027):
        a = [last_close(px[s], y, 1) for s in ("UGA", "USO")]
        b = [last_close(px[s], y, 4) for s in ("UGA", "USO")]
        if all(a) and all(b):
            r[y] = (b[0] / a[0] - 1) - (b[1] / a[1] - 1) - 0.002
    r = pd.Series(r)
    dev, oos = r[r.index <= 2016], r[r.index >= 2017]
    n1, m1, _ = stats(dev)
    n2, m2, t2 = stats(oos)
    v = "KILL (Stage 1)" if not (m1 > 0) else ("PASS" if (m2 >= 0.02 and t2 >= 2) else "FAIL")
    print("#530 Spring refinery maintenance (long UGA, short USO, end-Jan -> end-Apr)")
    print(show("Stage 1 2009-2016", dev))
    print(show("Stage 2 2017-2026", oos))
    print(f"   VERDICT {v} | $/yr at $45K: ${m2 * 45000:,.0f}\n")

    u = px["UNG"]
    w, rest = {}, {}
    for y in range(2008, 2026):
        a, b = last_close(u, y, 11), last_close(u, y + 1, 3)
        if a and b:
            w[y] = -(b / a - 1) - 0.001
        c, d = last_close(u, y, 4), last_close(u, y, 10)
        if c and d:
            rest[y] = -(d / c - 1) - 0.001
    w, rest = pd.Series(w), pd.Series(rest)
    dev, oos = w[w.index <= 2015], w[w.index >= 2016]
    n1, m1, _ = stats(dev)
    n2, m2, t2 = stats(oos)
    v = "KILL (Stage 1)" if not (m1 > 0) else ("PASS" if (m2 >= 0.03 and t2 >= 2) else "FAIL")
    print("#531 Natural-gas winter hedging premium (short UNG end-Nov -> end-Mar)")
    print(show("Stage 1 winters 2008-2015", dev))
    print(show("Stage 2 winters 2016-2025", oos))
    print(show("check: short UNG end-Apr -> end-Oct, 2016-2025 (reported only)", rest[rest.index >= 2016]))
    print(f"   VERDICT {v} | $/yr at $45K: ${m2 * 45000:,.0f}")


if __name__ == "__main__":
    main()

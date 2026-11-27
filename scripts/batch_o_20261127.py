"""Batch O #512-#514 (docs/PREREG_BATCH_O_20261127.md).

    uv run python -m scripts.batch_o_20261127 | tee docs/jx_runs/batch_o_20261127.txt
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


def verdict(dev, oos, min_n, min_mean):
    n1, m1, _ = stats(dev)
    n2, m2, t2 = stats(oos)
    if n1 >= 3 and not (m1 > 0):
        return "KILL (Stage 1)"
    return "PASS" if (n2 >= min_n and m2 >= min_mean and t2 >= 2) else "FAIL"


def last_close(s, y, m):
    end = pd.Timestamp(year=y, month=m, day=1) + pd.offsets.MonthEnd(0)
    i = s.index.searchsorted(end, side="right") - 1
    return float(s.iloc[i]) if i >= 0 and s.index[i].month == m and s.index[i].year == y else None


def seasonal(etfs, syms, m0, m1, years, cross_year):
    out = {}
    for y in years:
        rs = []
        for sym in syms:
            s = etfs[sym]
            a = last_close(s, y, m0)
            b = last_close(s, y + (1 if cross_year else 0), m1)
            if a and b:
                rs.append(b / a - 1)
        if len(rs) == len(syms):
            out[y] = float(np.mean(rs)) - 0.001
    return pd.Series(out)


def main():
    e = pd.read_parquet(OUT / "batcho_etf_1d.parquet")
    e["d"] = pd.to_datetime(e["t"], unit="s").dt.normalize()
    etfs = {s: g.set_index("d")["adj"].sort_index() for s, g in e.groupby("sym")}
    print("ETF coverage: " + ", ".join(f"{s} {v.index.min().date()}..{v.index.max().date()}" for s, v in etfs.items()) + "\n")

    r = seasonal(etfs, ["CORN", "SOYB"], 10, 2, range(2011, 2026), True)
    dev, oos = r[r.index <= 2017], r[r.index >= 2018]
    print("#512 Post-harvest recovery, corn + soybeans (long end-Oct -> end-Feb)")
    print(show("Stage 1 seasons 2011-2017", dev))
    print(show("Stage 2 seasons 2018-2025", oos))
    print(f"   VERDICT {verdict(dev, oos, 6, 0.02)} | $/yr at $45K: ${stats(oos)[1] * 45000:,.0f}\n")

    r = seasonal(etfs, ["WEAT"], 7, 10, range(2012, 2027), False)
    dev, oos = r[r.index <= 2018], r[r.index >= 2019]
    print("#513 Post-harvest recovery, wheat (long end-Jul -> end-Oct)")
    print(show("Stage 1 2012-2018", dev))
    print(show("Stage 2 2019-2026", oos))
    print(f"   VERDICT {verdict(dev, oos, 6, 0.02)} | $/yr at $45K: ${stats(oos)[1] * 45000:,.0f}\n")

    f = pd.read_parquet(OUT / "batcho_fred.parquet")
    f["date"] = pd.to_datetime(f["date"])
    hk = f[f.sid == "DEXHKUS"].set_index("date")["value"].sort_index()
    us = f[f.sid == "IR3TIB01USM156N"].set_index("date")["value"].sort_index()
    hkr_sid = next((s for s in ("IR3TIB01HKM156N", "HKGIR3TIB01STM") if (f.sid == s).any()), None)
    hkr = f[f.sid == hkr_sid].set_index("date")["value"].sort_index() if hkr_sid else None
    print(f"#514 HKD peg weak side (USD/HKD {hk.index.min().date()}..{hk.index.max().date()}; HK rate series: {hkr_sid or 'MISSING -> no carry'})")
    trades, i, below = [], 0, 0
    vals, idx = hk.to_numpy(), hk.index
    while i < len(vals):
        if vals[i] < 7.845:
            below += 1
            i += 1
            continue
        if below >= 30:
            j = i + 1
            while j < len(vals) and vals[j] > 7.80 and (idx[j] - idx[i]).days <= 120:
                j += 1
            j = min(j, len(vals) - 1)
            ret = -(vals[j] / vals[i] - 1) - 0.0001
            carry = 0.0
            if hkr is not None:
                ui = us.index.searchsorted(idx[i], side="right") - 1
                hi = hkr.index.searchsorted(idx[i], side="right") - 1
                if ui >= 0 and hi >= 0:
                    carry = (us.iloc[ui] - hkr.iloc[hi]) / 100 * (idx[j] - idx[i]).days / 365
            trades.append((idx[i], idx[j], vals[i], vals[j], ret - carry))
            i = j + 1
            below = 0
            continue
        below = 0
        i += 1
    t = pd.DataFrame(trades, columns=["entry", "exit", "px_in", "px_out", "r"])
    for _, x in t.iterrows():
        print(f"   {x.entry.date()} {x.px_in:.4f} -> {x.exit.date()} {x.px_out:.4f}: {x.r:+.3%}")
    dev, oos = t[(t.entry.dt.year >= 1990) & (t.entry.dt.year <= 2012)].r, t[t.entry.dt.year >= 2013].r
    print(show("Stage 1 entries 1990-2012", dev))
    print(show("Stage 2 entries 2013-2026", oos))
    print(f"   VERDICT {verdict(dev, oos, 4, 0.003)} | $/yr at $1.5M notional: ${stats(oos)[1] * 1_500_000 * len(oos) / 13.9:,.0f}\n")


if __name__ == "__main__":
    main()

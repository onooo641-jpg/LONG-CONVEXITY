"""Batch P #515-#518 (docs/PREREG_BATCH_P_20261127.md). Needs xlrd for the MOF .xls:

    uv run --with xlrd python -m scripts.batch_p_20261127 | tee docs/jx_runs/batch_p_20261127.txt
"""
import io

import numpy as np
import pandas as pd

from ict import data as D

OUT = D.REPO_ROOT / "data" / "public"
SHEETS = {"40年債": "40Y", "30年債": "30Y", "20年債": "20Y", "10年債": "10Y", "5年債": "5Y", "2年債": "2Y"}


def mof_yields():
    frames = []
    for f in ("batchp_mof_hist.csv", "batchp_mof_cur.csv"):
        txt = (OUT / f).read_bytes().decode("utf-8", "replace")
        d = pd.read_csv(io.StringIO(txt), skiprows=1)
        d["Date"] = pd.to_datetime(d["Date"], format="%Y/%m/%d", errors="coerce")
        frames.append(d.dropna(subset=["Date"]))
    y = pd.concat(frames).drop_duplicates("Date", keep="last").set_index("Date").sort_index()
    return y.apply(pd.to_numeric, errors="coerce")


def auctions():
    x = pd.read_excel(OUT / "batchp_mof_auctions.xls", sheet_name=None, header=None)
    rows = []
    for sheet, tenor in SHEETS.items():
        v = x[sheet].iloc[5:, 1]
        for d in pd.to_datetime(v, errors="coerce").dropna():
            rows.append((pd.Timestamp(d).normalize(), tenor))
    return pd.DataFrame(rows, columns=["date", "tenor"]).drop_duplicates()


def stats(x):
    x = pd.Series(x, dtype=float).dropna()
    n = len(x)
    t = x.mean() / (x.std(ddof=1) / np.sqrt(n)) if n > 1 and x.std(ddof=1) > 0 else np.nan
    return n, (x.mean() if n else np.nan), t


def idea_515(y):
    a = auctions()
    out = []
    for _, r in a.iterrows():
        s = y[r.tenor].dropna()
        i = s.index.searchsorted(r.date)
        if i >= len(s) or s.index[i] != r.date or i < 5 or i + 5 >= len(s):
            continue
        pre = s.iloc[i] - s.iloc[i - 5]
        post = s.iloc[i + 5] - s.iloc[i]
        out.append((r.date, r.tenor, (pre - post) * 100 - 1.0))
    e = pd.DataFrame(out, columns=["date", "tenor", "bp"])
    print(f"#515 JGB auction concession ({len(e)} auctions matched to a same-tenor MOF yield; by tenor: "
          + ", ".join(f"{k} {v}" for k, v in e.tenor.value_counts().sort_index().items()) + ")")
    res = {}
    for label, lo, hi in (("Stage 1 2009-2016", 2009, 2016), ("Stage 2 2017-2026", 2017, 2026)):
        g = e[(e.date.dt.year >= lo) & (e.date.dt.year <= hi)]
        wk = g.groupby(g.date.dt.to_period("W"))["bp"].mean()
        n, m, _ = stats(g.bp)
        _, _, tw = stats(wk)
        yrs_pos = (g.groupby(g.date.dt.year)["bp"].mean() > 0)
        usd = m * 50 * n / (hi - lo + 1) if n else 0.0
        res[label] = (n, m, tw, yrs_pos.sum(), len(yrs_pos), usd)
        print(f"   {label}: n {n}, mean net {m:+.2f} bp, week-clustered t {tw:.2f}, years positive {yrs_pos.sum()}/{len(yrs_pos)}, "
              f"${usd:,.0f}/yr at DV01 $50")
    s1, s2 = res["Stage 1 2009-2016"], res["Stage 2 2017-2026"]
    if not (s1[1] > 0):
        v = "KILL (Stage 1)"
    else:
        v = "PASS" if (s2[1] >= 1.0 and s2[2] >= 2 and s2[3] >= 6 and s2[5] >= 10000) else "FAIL"
    print(f"   VERDICT {v}\n")


def month_end(s, label, dev_lo, dev_hi, oos_lo):
    s = s.dropna().sort_index()
    out = {}
    for _, g in s.groupby(s.index.to_period("M")):
        if len(g) < 3:
            continue
        out[g.index[-1]] = -(g.iloc[-1] - g.iloc[-3]) * 100 - 0.5
    e = pd.Series(out)
    dev = e[(e.index.year >= dev_lo) & (e.index.year <= dev_hi)]
    oos = e[e.index.year >= oos_lo]
    n1, m1, t1 = stats(dev)
    n2, m2, t2 = stats(oos)
    v = "KILL (Stage 1)" if (n1 >= 24 and not (m1 > 0)) else ("PASS" if (m2 >= 0.5 and t2 >= 2) else "FAIL")
    print(f"{label} (data {s.index.min().date()}..{s.index.max().date()})")
    print(f"   Stage 1 {dev_lo}-{dev_hi}: n {n1}, mean {m1:+.2f} bp, t {t1:.2f}")
    print(f"   Stage 2 {oos_lo}-2026: n {n2}, mean {m2:+.2f} bp, t {t2:.2f}")
    print(f"   VERDICT {v} | $/yr at DV01 $50: ${m2 * 50 * 12:,.0f}\n")


def main():
    y = mof_yields()
    idea_515(y)
    month_end(y["10Y"], "#516 JGB 10y month-end extension", 1990, 2009, 2010)
    b = pd.read_csv(OUT / "batchp_bbk_10y.csv", sep=";", skiprows=8, header=None, names=["d", "v", "f"], dtype=str)
    b = pd.Series(pd.to_numeric(b["v"].str.replace(",", ".", regex=False), errors="coerce").to_numpy(),
                  index=pd.to_datetime(b["d"], errors="coerce")).dropna()
    month_end(b[b.index.notna()], "#517 Bund 10y month-end extension", 1990, 2009, 2010)
    g = pd.read_csv(OUT / "batchp_boe_10y.csv")
    g = pd.Series(pd.to_numeric(g["IUDMNZC"], errors="coerce").to_numpy(), index=pd.to_datetime(g["DATE"], format="%d %b %Y")).dropna()
    month_end(g, "#518 Gilt 10y month-end extension", 1990, 2009, 2010)


if __name__ == "__main__":
    main()

"""Batch M #505-#508 (docs/PREREG_BATCH_M_20261127.md).

    uv run python -m scripts.batch_m_20261127 | tee docs/jx_runs/batch_m_20261127.txt
"""
import json
import re
import sys

import numpy as np
import pandas as pd

from ict import data as D

OUT = D.REPO_ROOT / "data" / "public"
sys.path.insert(0, str(D.REPO_ROOT / "scripts"))


def stats(x):
    x = pd.Series(x, dtype=float).dropna()
    n = len(x)
    t = x.mean() / (x.std(ddof=1) / np.sqrt(n)) if n > 1 and x.std(ddof=1) > 0 else np.nan
    return n, (x.mean() if n else np.nan), t


def line(label, x):
    n, m, t = stats(x)
    return f"   {label}: n {n}, mean {m:+.2%}, t {t:.2f}"


def verdict(dev, oos, min_n, min_mean, kill_min=8):
    n1, m1, _ = stats(dev)
    n2, m2, t2 = stats(oos)
    if n1 >= kill_min and not (m1 > 0):
        return "KILL (Stage 1)"
    ok = n2 >= min_n and m2 >= min_mean and t2 >= 2
    return ("PASS" if ok else "FAIL") + (" (Stage 1 < 8 events: no kill possible)" if n1 < kill_min else "")


def last_on_or_before(s, day):
    i = s.index.searchsorted(pd.Timestamp(day), side="right") - 1
    return (s.index[i], float(s.iloc[i])) if i >= 0 else (None, None)


# ---------------------------------------------------------------- #505
def idea_505():
    from batch_l_20261127 import exit_time  # same T_x as #502
    ev = json.loads((OUT / "batchl_events.json").read_text())
    bodies = json.loads((OUT / "batchl_bodies.json").read_text())
    sp = pd.read_parquet(OUT / "batchm_spot_1h.parquet")
    sp["ts"] = pd.to_datetime(sp["t"], unit="s", utc=True) + pd.Timedelta(hours=1)
    px = {s: g.set_index("ts")["close"].sort_index() for s, g in sp.groupby("sym")}
    rows = []
    for e in ev:
        if e["idea"] != 502 or not re.search(r"[A-Z0-9]{2,15}USDT", e["title"]):
            continue
        a = pd.Timestamp(e["ms"], unit="ms", tz="UTC")
        te = a.ceil("h") + pd.Timedelta(hours=1)
        t0 = exit_time(e, bodies.get(e["code"], ""), te) + pd.Timedelta(hours=1)
        t1 = t0 + pd.Timedelta(days=7)
        if t1 > pd.Timestamp("2026-11-27", tz="UTC") or "BTCUSDT" not in px:
            continue
        b = px["BTCUSDT"]
        _, b0 = last_on_or_before(b, t0)
        _, b1 = last_on_or_before(b, t1)
        rs = []
        for s in e["syms"]:
            if s not in px:
                continue
            k0, p0 = last_on_or_before(px[s], t0)
            k1, p1 = last_on_or_before(px[s], t1)
            if p0 is None or p1 is None or k0 < t0 - pd.Timedelta(hours=3) or k1 <= k0:
                continue
            rs.append((p1 / p0 - 1) - (b1 / b0 - 1) - 0.006)
        if rs:
            rows.append((a, float(np.mean(rs))))
    d = pd.DataFrame(rows, columns=["a", "r"])
    split = pd.Timestamp("2025-01-01", tz="UTC")
    dev, oos = (d[d.a < split].r, d[d.a >= split].r) if len(d) else (pd.Series(dtype=float), pd.Series(dtype=float))
    yrs = (pd.Timestamp("2026-11-27", tz="UTC") - split).days / 365.25
    usd = stats(oos)[1] * 3000 * len(oos) / yrs if len(oos) else 0.0
    print("#505 Rebound after a perp delisting (long spot 7 d from settlement + 1 h; excess vs BTC - 0.6%)")
    print(line("Stage 1 (< 2025)", dev))
    print(line("Stage 2 (2025-26)", oos))
    print(f"   VERDICT {verdict(dev, oos, 12, 0.02)} | $/yr at $3,000 per event: ${usd:,.0f}\n")


# ---------------------------------------------------------------- #506
def idea_506():
    fx = pd.read_parquet(OUT / "batchg_dexjpus.parquet")
    s = fx.assign(date=pd.to_datetime(fx["date"])).set_index("date")["rate"].astype(float).dropna().sort_index()
    ir = pd.read_parquet(OUT / "batchi_ir3m.parquet")
    ir["date"] = pd.to_datetime(ir["date"])
    us = ir[ir.cc == "US"].set_index("date")["rate"]
    jp = ir[ir.cc == "JP"].set_index("date")["rate"]

    def window(y, m0, d0, m1, d1, rate_month):
        k0, p0 = last_on_or_before(s, f"{y}-{m0:02d}-{d0:02d}")
        k1, p1 = last_on_or_before(s, f"{y}-{m1:02d}-{d1:02d}")
        rm = pd.Timestamp(f"{y}-{rate_month:02d}-01")
        if p0 is None or rm not in us.index or rm not in jp.index:
            return None
        carry = (us[rm] - jp[rm]) / 100 / 12
        return -(p1 / p0 - 1) - carry - 0.00003

    main, half = {}, {}
    for y in range(2003, 2027):
        feb_end = (pd.Timestamp(f"{y}-03-01") - pd.Timedelta(days=1)).day
        r = window(y, 2, feb_end, 3, 31, 2)
        if r is not None:
            main[y] = r
        r2 = window(y, 8, 31, 9, 30, 8)
        if r2 is not None and pd.Timestamp(f"{y}-09-30") <= s.index[-1]:
            half[y] = r2
    m = pd.Series(main)
    dev, oos = m[m.index <= 2013], m[m.index >= 2014]
    h = pd.Series(half)
    print("#506 Japanese fiscal-year-end repatriation (long JPY, end-Feb -> 31 Mar, net of carry)")
    print(line("Stage 1 (2003-2013)", dev))
    print(line("Stage 2 (2014-2026)", oos))
    print(line("variant half-year (end-Aug -> 30 Sep), 2014-2026 (reported only)", h[h.index >= 2014]))
    print(f"   VERDICT {verdict(dev, oos, 10, 0.005)} | $/yr at $150K notional: ${stats(oos)[1] * 150000:,.0f}\n")


# ---------------------------------------------------------------- #507
DEADLINES = {2007: "2007-04-17", 2011: "2011-04-18", 2012: "2012-04-17", 2016: "2016-04-18", 2017: "2017-04-18",
             2018: "2018-04-17", 2020: "2020-07-15", 2021: "2021-05-17", 2022: "2022-04-18", 2023: "2023-04-18"}


def deadline(y):
    if y in DEADLINES:
        return pd.Timestamp(DEADLINES[y])
    d = pd.Timestamp(f"{y}-04-15")
    while d.weekday() >= 5:
        d += pd.Timedelta(days=1)
    return d


def idea_507():
    etf = pd.read_parquet(OUT / "batchg_etf_1d.parquet")
    col = "adj" if "adj" in etf.columns else "close"
    spy = etf[etf.sym == "SPY"].assign(d=lambda x: pd.to_datetime(x["t"], unit="s").dt.normalize()).set_index("d")[col].sort_index()
    btc = pd.read_parquet(OUT / "batchg_btc_1d.parquet")
    btc = btc.assign(d=pd.to_datetime(btc["t"], unit="s").dt.normalize()).set_index("d")["c"].sort_index()

    def run(s, years, rebound=False, cost=0.0004):
        out = {}
        for y in years:
            dl = deadline(y)
            i = s.index.searchsorted(dl, side="right") - 1
            if i < 10 or i + 10 >= len(s):
                continue
            if rebound:
                out[y] = s.iloc[i + 10] / s.iloc[i] - 1 - cost
            else:
                out[y] = -(s.iloc[i] / s.iloc[i - 10] - 1) - cost
        return pd.Series(out)
    a = run(spy, range(2001, 2027))
    dev, oos = a[a.index <= 2012], a[a.index >= 2013]
    print("#507 US tax-payment selling (short SPY 10 sessions into the filing deadline)")
    print(line("Stage 1 (2001-2012)", dev))
    print(line("Stage 2 (2013-2026)", oos))
    b = run(spy, range(2013, 2027), rebound=True)
    print(line("variant rebound: long SPY deadline -> +10 sessions, 2013-2026 (reported only)", b))
    c = run(btc, range(2015, 2027), cost=0.0009)
    print(line("variant BTC short into the deadline, 2015-2026 (reported only)", c))
    print(f"   VERDICT {verdict(dev, oos, 10, 0.005)} | $/yr at $30K: ${stats(oos)[1] * 30000:,.0f}\n")


# ---------------------------------------------------------------- #508
DIWALI = ["2004-11-12", "2005-11-01", "2006-10-21", "2007-11-09", "2008-10-28", "2009-10-17", "2010-11-05", "2011-10-26",
          "2012-11-13", "2013-11-03", "2014-10-23", "2015-11-11", "2016-10-30", "2017-10-19", "2018-11-07", "2019-10-27",
          "2020-11-14", "2021-11-04", "2022-10-24", "2023-11-12", "2024-11-01", "2025-10-20", "2026-11-08"]


def idea_508():
    g = pd.read_parquet(OUT / "batchm_gld_1d.parquet")
    s = g.assign(d=pd.to_datetime(g["t"], unit="s").dt.normalize()).set_index("d")["close"].sort_index()
    out = {}
    for ds in DIWALI:
        d = pd.Timestamp(ds)
        i = s.index.searchsorted(d, side="right") - 1
        if i < 15 or d > s.index[-1] + pd.Timedelta(days=3):
            continue
        out[d.year] = s.iloc[i] / s.iloc[i - 15] - 1 - 0.0004
    r = pd.Series(out)
    dev, oos = r[r.index <= 2014], r[r.index >= 2015]
    print("#508 Gold before Diwali (long GLD 15 sessions into Diwali)")
    print(line("Stage 1 (2004-2014)", dev))
    print(line("Stage 2 (2015-2026)", oos))
    print(f"   VERDICT {verdict(dev, oos, 10, 0.01)} | $/yr at $45K: ${stats(oos)[1] * 45000:,.0f}\n")


def main():
    for f in (idea_505, idea_506, idea_507, idea_508):
        try:
            f()
        except FileNotFoundError as e:
            print(f"{f.__name__}: data missing ({e.filename}); NOT RUN\n")


if __name__ == "__main__":
    main()

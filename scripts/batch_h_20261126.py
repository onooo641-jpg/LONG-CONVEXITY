"""Batch H (#468-#477), exactly as docs/PREREG_BATCH_H_20261126.md defines it.

    uv run python -m scripts.batch_h_20261126 | tee docs/jx_runs/batch_h_20261126.txt
"""
from __future__ import annotations

import io
import json

import numpy as np
import pandas as pd

from scripts.batch_d_20261126 import PUB, tstat
from scripts.batch_g_20261126 import at, fred_series, hourly, judge

FEE = 0.00045


def clustered(rows, key="day", val="ret"):
    """average events that share a signal time into one observation (the pre-registered t is on these)."""
    r = pd.DataFrame(rows)
    if r.empty:
        return []
    g = r.groupby(key)[val].mean().reset_index()
    return g.to_dict("records")


def part468():
    print("\n#### #468 funding-settlement pressure (40 Binance perps; prev funding >= +0.05% -> short T-2h..T)")
    k = pd.read_parquet(PUB / "batchd_alts_1h.parquet")
    f = pd.read_parquet(PUB / "batchd_alts_funding.parquet")
    px = {s: pd.Series(g["close"].to_numpy(), index=pd.to_datetime(g["t"], unit="s", utc=True)).sort_index() for s, g in k.groupby("sym")}
    px = {s: v[~v.index.duplicated()] for s, v in px.items()}
    main, var = [], []
    for s, g in f.groupby("sym"):
        if s not in px:
            continue
        x = px[s]
        g = g.sort_values("t")
        ts = pd.to_datetime(g["t"], unit="s", utc=True).dt.floor("h").to_numpy()
        rt = g["rate"].to_numpy()
        for i in range(1, len(g)):
            sig = rt[i - 1]
            if abs(sig) < 0.0005:
                continue
            side = -1 if sig > 0 else 1
            T = pd.Timestamp(ts[i])
            p0, p1, p2 = at(x, T - pd.Timedelta(hours=2)), at(x, T), at(x, T + pd.Timedelta(hours=2))
            if p0 is None or p1 is None or not (p0 > 0):
                continue
            main.append({"day": T, "ret": side * (p1 / p0 - 1) - 2 * FEE})
            if p2 is not None:
                var.append({"day": T, "ret": -side * (p2 / p1 - 1) - 2 * FEE})
    print(f"  raw symbol-events: {len(main)}")
    judge("#468 main (per timestamp)", clustered(main), "2023-01-01", "2020-01-01", "2026-11-01", 100, 0.0005, 45000)
    judge("#468 variant re-entry T..T+2h", clustered(var), "2023-01-01", "2020-01-01", "2026-11-01", 100, 0.0005, 45000)


def vx_panel():
    d = json.load(open(PUB / "batch9_vx.json"))
    rows = []
    for exp, csv in d.items():
        try:
            t = pd.read_csv(io.StringIO(csv))
        except Exception:  # noqa: BLE001
            continue
        if t.empty or "Trade Date" not in t:
            continue
        t["exp"] = pd.Timestamp(exp)
        rows.append(t)
    p = pd.concat(rows, ignore_index=True)
    p["date"] = pd.to_datetime(p["Trade Date"])
    p["px"] = np.where(pd.to_numeric(p["Settle"], errors="coerce") > 0, pd.to_numeric(p["Settle"], errors="coerce"),
                       pd.to_numeric(p["Close"], errors="coerce"))
    return p[p["px"] > 0][["date", "exp", "px"]]


def part469():
    print("\n#### #469 VIX ETP rebalancing (front VX move >= +8% -> short next day; <= -8% -> long)")
    p = vx_panel()
    rows = []
    dates = sorted(p["date"].unique())
    by = {e: g.set_index("date")["px"].sort_index() for e, g in p.groupby("exp")}
    for i in range(1, len(dates) - 1):
        d0, d, d1 = dates[i - 1], dates[i], dates[i + 1]
        cand = [e for e in by if e >= d + pd.Timedelta(days=7)]
        if not cand:
            continue
        s = by[min(cand)]
        if not (d0 in s.index and d in s.index and d1 in s.index):
            continue
        r = s[d] / s[d0] - 1
        if abs(r) < 0.08:
            continue
        side = -1 if r > 0 else 1
        rows.append({"day": pd.Timestamp(d), "pts": side * (s[d1] - s[d]) - 0.06, "up": r > 0})
    judge("#469 main", rows, "2018-03-01", "2013-01-01", "2026-11-01", 30, 1e-9, 1000, unit="pts")
    r = pd.DataFrame(rows)
    if len(r):
        for lab, g in r.groupby("up"):
            s2 = g[g["day"] >= "2018-03-01"]["pts"]
            print(f"    split {'up-day shorts' if lab else 'down-day longs'} Stage 2: n {len(s2)}, mean {s2.mean():.2f} pts, t {tstat(s2):.2f}")


def yahoo():
    p = PUB / "batchh_yahoo_1d.parquet"
    if not p.exists():
        return None
    d = pd.read_parquet(p)
    d["day"] = pd.to_datetime(d["t"], unit="s", utc=True).dt.tz_convert("America/New_York").dt.normalize().dt.tz_localize(None)
    return d.drop_duplicates(["sym", "day"]).sort_values(["sym", "day"])


def part470(y):
    print("\n#### #470 single-stock leveraged-ETF rebalancing (|close-close| >= 7% -> fade close -> next open)")
    if y is None:
        print("  data not fetched yet (ubatchh)")
        return
    main, var = [], []
    for s in ("TSLA", "NVDA", "MSTR", "COIN", "PLTR", "SMCI", "AMD"):
        g = y[y["sym"] == s].dropna(subset=["open", "close", "adj"]).reset_index(drop=True)
        ao = g["open"] * g["adj"] / g["close"]
        a = g["adj"]
        for i in range(1, len(g) - 1):
            r = a[i] / a[i - 1] - 1
            if abs(r) < 0.07:
                continue
            side = -1 if r > 0 else 1
            main.append({"day": g["day"][i], "ret": side * (ao[i + 1] / a[i] - 1) - 0.0010, "sym": s})
            var.append({"day": g["day"][i], "ret": side * (a[i + 1] / a[i] - 1) - 0.0010})
    print(f"  raw stock-events: {len(main)}")
    judge("#470 main close->open (per day)", clustered(main), "2024-07-01", "2023-01-01", "2026-11-01", 50, 0.002, 30000)
    judge("#470 variant close->close (per day)", clustered(var), "2024-07-01", "2023-01-01", "2026-11-01", 50, 0.002, 30000)


def part471():
    print("\n#### #471 BTC spot-ETF NAV window (long BTC 15:00 -> 16:00 New York, weekdays)")
    x = hourly("BTCUSDT")
    rows = []
    for day in pd.date_range("2021-01-01", "2026-10-31", freq="B"):
        a = pd.Timestamp(day.strftime("%Y-%m-%d") + " 15:00", tz="America/New_York").tz_convert("UTC")
        b = a + pd.Timedelta(hours=1)
        p0, p1 = at(x, a), at(x, b)
        if p0 is None or p1 is None:
            continue
        rows.append({"day": a.tz_localize(None), "ret": p1 / p0 - 1 - 2 * FEE})
    r = pd.DataFrame(rows)
    c = r[r["day"] < "2024-01-11"]["ret"]
    print(f"  control 2021-2023 (pre-ETF): n {len(c)}, mean net {c.mean():.4%}, gross {c.mean() + 2 * FEE:.4%}, t {tstat(c):.2f}")
    judge("#471 main", r[r["day"] >= "2024-01-11"].to_dict("records"), "2025-01-01", "2024-01-11", "2026-11-01", 0, 0.0003, 45000)
    for lab, lo, hi in (("Stage 1", "2024-01-11", "2025-01-01"), ("Stage 2", "2025-01-01", "2026-11-01")):
        g = r[(r["day"] >= lo) & (r["day"] < hi)]["ret"] + 2 * FEE
        print(f"    gross {lab}: mean {g.mean():.4%}, t {tstat(g):.2f}")


def part472():
    print("\n#### #472 mortgage convexity hedging (DGS10 5-day move >= 20 bp -> extend 5 days)")
    y = fred_series("DGS10")
    y = y[y.index >= "1985-01-01"]
    v = y.to_numpy()
    idx = y.index
    for tag, thr, hold in (("#472 main 20bp/5d", 0.20, 5), ("#472 variant 10bp/5d", 0.10, 5), ("#472 variant 20bp/2d", 0.20, 2)):
        rows, i = [], 5
        while i + hold < len(v):
            d5 = v[i] - v[i - 5]
            if abs(d5) >= thr:
                side = 1 if d5 > 0 else -1  # short duration after rises: P&L = +dy
                rows.append({"day": idx[i], "bp": side * (v[i + hold] - v[i]) * 100 - 0.5})
                i += hold
            else:
                i += 1
        judge(tag, rows, "2010-01-01", "1990-01-01", "2026-11-01", 0, 1.0, 50, unit="bp")


def part473():
    print("\n#### #473 Tether quarter-end BTC buying (long 5 days before quarter's last day -> next 00:00)")
    x = hourly("BTCUSDT")
    daily = x[x.index.hour == 23]
    daily.index = daily.index.normalize() + pd.Timedelta(days=1)  # price at 00:00 of that date
    rows = []
    for q in pd.period_range("2023Q2", "2026Q3", freq="Q"):
        last = q.end_time.normalize()
        a, b = last - pd.Timedelta(days=5), last + pd.Timedelta(days=1)
        a, b = a.tz_localize("UTC"), b.tz_localize("UTC")
        if a not in daily.index or b not in daily.index:
            continue
        rows.append({"day": a.tz_localize(None), "ret": daily[b] / daily[a] - 1 - 2 * FEE})
    r = pd.DataFrame(rows)
    six = (daily.shift(-6) / daily - 1 - 2 * FEE).dropna()
    six.index = six.index.tz_localize(None)
    for lab, lo, hi in (("S1", "2023-04-01", "2025-01-01"), ("S2", "2025-01-01", "2026-10-01")):
        base = six[(six.index >= lo) & (six.index < hi)].mean()
        m = (r["day"] >= lo) & (r["day"] < hi)
        r.loc[m, "ex"] = r.loc[m, "ret"] - base
        print(f"  {lab} baseline 6-day BTC mean net {base:.2%}")
    print("  events: " + "; ".join(f"{d.date()} {v:+.1%}" for d, v in zip(r["day"], r["ret"])))
    judge("#473 excess", r.rename(columns={"ret": "raw", "ex": "ret"}).to_dict("records"), "2025-01-01", "2023-04-01", "2026-10-01", 0, 0.01, 45000)


def part474(y):
    print("\n#### #474 quarter-end window dressing (long MTUM / short SPY, last 5 trading days of the quarter)")
    if y is None:
        print("  data not fetched yet (ubatchh)")
        return
    a = y.pivot(index="day", columns="sym", values="adj")[["MTUM", "SPY"]].dropna()
    d = a.index
    qe = [d[d.to_period("Q") == q][-1] for q in d.to_period("Q").unique()]
    main, var = [], []
    for e in qe[:-1] if d[-1] < d[d.to_period("Q") == d[-1].to_period("Q")][-1] else qe:
        i = d.get_loc(e)
        if i < 5:
            continue
        s = d[i - 5]
        main.append({"day": e, "ret": (a["MTUM"][e] / a["MTUM"][s] - 1) - (a["SPY"][e] / a["SPY"][s] - 1) - 0.0008})
        if i + 5 < len(d):
            n = d[i + 5]
            var.append({"day": e, "ret": -((a["MTUM"][n] / a["MTUM"][e] - 1) - (a["SPY"][n] / a["SPY"][e] - 1)) - 0.0008})
    judge("#474 main", main, "2020-01-01", "2013-06-01", "2026-10-01", 0, 0.003, 30000)
    judge("#474 variant (reverse, first 5 days next quarter)", var, "2020-01-01", "2013-06-01", "2026-10-01", 0, 0.003, 30000)


def part475(y):
    print("\n#### #475 Nikkei dividend reinvestment (long into the last cum-dividend close, Mar/Sep)")
    if y is None:
        print("  data not fetched yet (ubatchh)")
        return
    n = y[y["sym"] == "^N225"].set_index("day")["close"].dropna()
    d = n.index
    for tag, months in (("#475 main Mar/Sep", (3, 9)), ("#475 variant all quarter-ends", (3, 6, 9, 12))):
        rows = []
        for (yr, mo), g in pd.Series(d, index=d).groupby([d.year, d.month]):
            if mo not in months:
                continue
            rec = g.iloc[-1]
            i = d.get_loc(rec)
            lag = 2 if rec >= pd.Timestamp("2019-07-16") else 3
            cum = i - lag
            if cum - 5 < 0:
                continue
            rows.append({"day": d[cum], "ret": n.iloc[cum] / n.iloc[cum - 5] - 1 - 0.0004})
        judge(tag, rows, "2013-01-01", "2000-01-01", "2026-10-01", 0, 0.005, 30000)


def part476():
    print("\n#### #476 crypto leveraged-token rebalance (|00:00->00:00| >= 5% -> trade the move 00:00 -> 01:00)")
    rows, var = [], []
    for sym in ("BTCUSDT", "ETHUSDT"):
        x = hourly(sym)
        for day in pd.date_range("2020-01-02", "2026-10-31", freq="D", tz="UTC"):
            p_prev, p0, p1, p4 = at(x, day - pd.Timedelta(days=1)), at(x, day), at(x, day + pd.Timedelta(hours=1)), at(x, day + pd.Timedelta(hours=4))
            if p_prev is None or p0 is None or p1 is None:
                continue
            r = p0 / p_prev - 1
            if abs(r) < 0.05:
                continue
            s = 1 if r > 0 else -1
            rows.append({"day": day.tz_localize(None), "ret": s * (p1 / p0 - 1) - 2 * FEE})
            if p4 is not None:
                var.append({"day": day.tz_localize(None), "ret": -s * (p4 / p1 - 1) - 2 * FEE})
    judge("#476 main (per day)", clustered(rows), "2023-01-01", "2020-01-01", "2026-11-01", 30, 0.001, 45000)
    judge("#476 variant fade 01:00->04:00 (per day)", clustered(var), "2023-01-01", "2020-01-01", "2026-11-01", 30, 0.001, 45000)


def part477(y):
    print("\n#### #477 tax-date selling (short SPY the 5 sessions before the 15th of Jan/Apr/Jun/Sep/Dec)")
    if y is None:
        p = PUB / "batchg_etf_1d.parquet"
        if not p.exists():
            print("  data not fetched yet (ubatchh / ubatchg)")
            return
        e = pd.read_parquet(p)
        e = e[e["sym"] == "SPY"]
        spy = pd.Series(e["adj"].to_numpy(), index=pd.to_datetime(e["t"], unit="s", utc=True).dt.tz_convert("America/New_York").dt.normalize().dt.tz_localize(None))
    else:
        spy = y[y["sym"] == "SPY"].set_index("day")["adj"]
    spy = spy[~spy.index.duplicated()].sort_index().dropna()
    d = spy.index
    rows = []
    for yr in range(2000, 2027):
        for mo in (1, 4, 6, 9, 12):
            due = pd.Timestamp(yr, mo, 15)
            before = d[d < due]
            if len(before) < 6 or due > d[-1]:
                continue
            D = before[-1]
            i = d.get_loc(D)
            rows.append({"day": D, "ret": -(spy.iloc[i] / spy.iloc[i - 5] - 1) - 0.0004})
    judge("#477 main", rows, "2013-01-01", "2000-01-01", "2026-11-01", 0, 0.002, 30000)


def main():
    print("===== Batch H (#468-#477)  docs/PREREG_BATCH_H_20261126.md")
    y = yahoo()
    part468()
    part469()
    part470(y)
    part471()
    part472()
    part473()
    part474(y)
    part475(y)
    part476()
    part477(y)


if __name__ == "__main__":
    main()

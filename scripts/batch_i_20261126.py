"""Batch I (#478-#487), exactly as docs/PREREG_BATCH_I_20261126.md defines it.

    uv run python -m scripts.batch_i_20261126 | tee docs/jx_runs/batch_i_20261126.txt
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from scripts.batch_d_20261126 import PUB
from scripts.batch_g_20261126 import at, hourly, judge
from scripts.batch_h_20261126 import clustered
from scripts.fetch_uncharted import delist_events

PAIRS = ("EURUSD", "GBPUSD", "USDJPY", "AUDUSD")
STABLE = {"USDP", "TUSD", "BUSD", "USDC", "DAI", "FDUSD", "PAX"}


def duka(ins):
    """price at each 5-minute mark (UTC) = close of the 1-minute candle ending there. Field order is detected from the low/high check."""
    p = PUB / f"batchi_duka_{ins.lower()}.parquet"
    if not p.exists():
        return None
    d = pd.read_parquet(p)
    if d.empty:
        return None
    a = ((d["f3"] <= d[["f1", "f2"]].min(axis=1)) & (d["f4"] >= d[["f1", "f2"]].max(axis=1))).mean()
    b = ((d["f3"] <= d[["f1", "f4"]].min(axis=1)) & (d["f2"] >= d[["f1", "f4"]].max(axis=1))).mean()
    close = d["f2"] if a >= b else d["f4"]
    ts = pd.to_datetime(d["day"]).dt.tz_localize("UTC") + pd.to_timedelta(d["sec"] + 60, unit="s")
    s = pd.Series(close.to_numpy(), index=ts).sort_index()
    s = s[~s.index.duplicated()]
    print(f"  {ins}: {d['day'].nunique()} days; field order {'O,C,L,H' if a >= b else 'O,H,L,C'} (check {max(a, b):.3f})")
    return s


def loc(day, hhmm, tz):
    return pd.Timestamp(f"{day:%Y-%m-%d} {hhmm}", tz=tz).tz_convert("UTC")


def yahoo_adj():
    out = {}
    for f in ("batchh_yahoo_1d.parquet", "batchi_yahoo_1d.parquet"):
        p = PUB / f
        if not p.exists():
            continue
        d = pd.read_parquet(p)
        d["day"] = pd.to_datetime(d["t"], unit="s", utc=True).dt.tz_convert("America/New_York").dt.normalize().dt.tz_localize(None)
        for s, g in d.groupby("sym"):
            col = "close" if s == "^N225" else "adj"
            v = g.drop_duplicates("day").set_index("day")[col].sort_index().dropna()
            out[s] = v
    return out


def part478(P):
    print("\n#### #478 FX triple-rollover avoidance (Wednesday: long the higher-yield currency 15:00 -> 16:55 New York)")
    rp = PUB / "batchi_ir3m.parquet"
    if not rp.exists() or not any(P.get(x) is not None for x in PAIRS):
        print("  data not fetched yet (ubatchi)")
        return
    r = pd.read_parquet(rp)
    r["m"] = pd.to_datetime(r["date"]).dt.to_period("M")
    R = r.pivot_table(index="m", columns="cc", values="rate")
    foreign = {"EURUSD": "EZ", "GBPUSD": "GB", "AUDUSD": "AU", "USDJPY": "JP"}
    for tag, wd in (("#478 main Wednesdays", (2,)), ("#478 variant every weekday", (0, 1, 2, 3, 4))):
        rows = []
        for day in pd.date_range("2012-01-02", "2026-10-31", freq="B"):
            if day.weekday() not in wd:
                continue
            pm = day.to_period("M") - 1
            if pm not in R.index:
                continue
            a, b = loc(day, "15:00", "America/New_York"), loc(day, "16:55", "America/New_York")
            for pair, cc in foreign.items():
                s = P.get(pair)
                if s is None or pd.isna(R.at[pm, cc]) or pd.isna(R.at[pm, "US"]):
                    continue
                p0, p1 = s.get(a), s.get(b)
                if p0 is None or p1 is None:
                    continue
                hi_foreign = R.at[pm, cc] > R.at[pm, "US"]
                side = (1 if hi_foreign else -1) if pair != "USDJPY" else (-1 if hi_foreign else 1)
                rows.append({"day": day, "bp": side * (p1 / p0 - 1) * 1e4 - 0.3})
        judge(tag, clustered(rows, val="bp"), "2019-01-01", "2012-01-01", "2026-11-01", 0, 0.3, 15, unit="bp")


def _fade(s, day, m0, m1, e0, e1, tz="Europe/London"):
    a, b = s.get(loc(day, m0, tz)), s.get(loc(day, m1, tz))
    c, d = s.get(loc(day, e0, tz)), s.get(loc(day, e1, tz))
    if None in (a, b, c, d) or b == a:
        return None
    return -np.sign(b - a) * (d / c - 1) * 1e4


def part479(P):
    print("\n#### #479 WM/R 4 pm fix reversal (fade 15:30->16:00 from 16:00 to 16:30 London; month's last day excluded)")
    if not any(P.get(x) is not None for x in PAIRS):
        print("  data not fetched yet (ubatchi)")
        return
    days = pd.date_range("2012-01-02", "2026-10-31", freq="B")
    last = set(pd.Series(days, index=days).groupby(days.to_period("M")).max())
    rows = []
    for day in days:
        if day in last:
            continue
        for pair in PAIRS:
            s = P.get(pair)
            if s is None:
                continue
            v = _fade(s, day, "15:30", "16:00", "16:00", "16:30")
            if v is not None:
                rows.append({"day": day, "bp": v - 0.3})
    judge("#479 main", clustered(rows, val="bp"), "2019-01-01", "2012-01-01", "2026-11-01", 0, 0.3, 15, unit="bp")


def part480(P):
    print("\n#### #480 LBMA gold PM auction reversal (fade 14:30->15:00 from 15:05 to 15:35 London)")
    g, sv = P.get("XAUUSD"), P.get("XAGUSD")
    if g is None:
        print("  data not fetched yet (ubatchi)")
        return
    days = pd.date_range("2012-01-02", "2026-10-31", freq="B")
    for tag, s, w in (("#480 main gold PM", g, ("14:30", "15:00", "15:05", "15:35")), ("#480 variant gold AM", g, ("10:00", "10:30", "10:35", "11:05")),
                      ("#480 variant silver 12:00", sv, ("11:30", "12:00", "12:05", "12:35"))):
        if s is None:
            print(f"  {tag}: no data")
            continue
        rows = []
        for day in days:
            v = _fade(s, day, *w)
            if v is not None:
                rows.append({"day": day, "bp": v - 1.0})
        judge(tag, rows, "2019-01-01", "2012-01-01", "2026-11-01", 0, 1.0, 4.5, unit="bp")


def part481():
    print("\n#### #481 Solana epoch-boundary unstake selling (short SOL 24 h from the first full hour after the epoch start)")
    p = PUB / "batchi_sol_epochs.parquet"
    if not p.exists():
        print("  data not fetched yet (ubatchi)")
        return
    e = pd.read_parquet(p)
    k = pd.read_parquet(PUB / "batchd_alts_1h.parquet")
    k = k[k["sym"] == "SOLUSDT"]
    x = pd.Series(k["close"].to_numpy(), index=pd.to_datetime(k["t"], unit="s", utc=True)).sort_index()
    x = x[~x.index.duplicated()]
    rows = []
    for t in pd.to_datetime(e["t"], unit="s", utc=True):
        h = t.ceil("h")
        p0, p1 = at(x, h), at(x, h + pd.Timedelta(hours=24))
        if p0 is None or p1 is None:
            continue
        rows.append({"day": h.tz_localize(None), "ret": -(p1 / p0 - 1) - 0.0009})
    print(f"  epochs {len(e)} ({pd.to_datetime(e['t'], unit='s').min():%Y-%m-%d}..{pd.to_datetime(e['t'], unit='s').max():%Y-%m-%d}), events with prices {len(rows)}")
    judge("#481 main", rows, "2023-01-01", "2021-01-01", "2026-11-01", 100, 0.001, 45000)


def part482():
    print("\n#### #482 Binance spot-delisting overreaction (buy announcement + 24 h -> 00:00 UTC on the delisting date, excess vs BTC)")
    p = PUB / "batchi_delist_spot_1h.parquet"
    if not p.exists():
        print("  data not fetched yet (ubatchi)")
        return
    k = pd.read_parquet(p)
    px = {s: (lambda v: v[~v.index.duplicated()])(pd.Series(g["close"].to_numpy(), index=pd.to_datetime(g["t"], unit="s", utc=True)).sort_index())
          for s, g in k.groupby("sym")}
    btc = hourly("BTCUSDT")
    rows, ntok = [], 0
    for ms, dd, toks in delist_events():
        a = pd.Timestamp(ms, unit="ms", tz="UTC").ceil("h") + pd.Timedelta(hours=24)
        b = pd.Timestamp(dd, tz="UTC")
        if b <= a:
            continue
        b0, b1 = at(btc, a), at(btc, b)
        for tok in toks:
            if tok in STABLE or f"{tok}USDT" not in px or b0 is None or b1 is None:
                continue
            x = px[f"{tok}USDT"]
            p0, p1 = at(x, a), at(x, b)
            if p0 is None or p1 is None or not (p0 > 0):
                continue
            ntok += 1
            rows.append({"day": pd.Timestamp(ms, unit="ms"), "ret": (p1 / p0 - 1) - (b1 / b0 - 1) - 0.006, "tok": tok})
    r = pd.DataFrame(rows)
    print(f"  token events {ntok}; announcements {r['day'].nunique() if len(r) else 0}")
    if len(r):
        print("  worst/best tokens: " + "; ".join(f"{t.tok} {t.ret:+.1%}" for t in pd.concat([r.nsmallest(3, 'ret'), r.nlargest(3, 'ret')]).itertuples()))
    judge("#482 main (per announcement)", clustered(rows), "2024-07-01", "2022-12-01", "2026-11-01", 15, 0.03, 15000)


def _roll(Y, long, short, d0=6, d1=10):
    if long not in Y or short not in Y:
        return []
    a = pd.concat([Y[long], Y[short]], axis=1, keys=["L", "S"]).dropna()
    rows = []
    for m, g in a.groupby(a.index.to_period("M")):
        if len(g) < d1:
            continue
        i0, i1 = g.index[d0 - 1], g.index[d1 - 1]
        rows.append({"day": i0, "ret": (g.at[i1, "L"] / g.at[i0, "L"] - 1) - (g.at[i1, "S"] / g.at[i0, "S"] - 1) - 0.0008})
    return rows


def part483(Y):
    print("\n#### #483 USO monthly roll (long USL / short USO, close of trading day 6 -> close of day 10)")
    if "USO" not in Y:
        print("  data not fetched yet (ubatchi)")
        return
    judge("#483 main USO", _roll(Y, "USL", "USO"), "2018-01-01", "2010-01-01", "2026-11-01", 0, 0.001, 30000)
    judge("#483 variant UNG", _roll(Y, "UNL", "UNG"), "2018-01-01", "2010-01-01", "2026-11-01", 0, 0.001, 30000)


def part484(Y):
    print("\n#### #484 Japanese ETF dividend cash-raising (short ^N225 into the last trading day <= July 10)")
    n = Y.get("^N225")
    if n is None:
        print("  data not fetched yet (ubatchh)")
        return
    d = n.index
    for tag, months in (("#484 main July", (7,)), ("#484 variant July + January", (1, 7))):
        rows = []
        for yr in range(2000, 2027):
            for mo in months:
                D = d[d <= pd.Timestamp(yr, mo, 10)]
                if len(D) < 5 or D[-1].month != mo or pd.Timestamp(yr, mo, 10) > d[-1]:
                    continue
                i = d.get_loc(D[-1])
                rows.append({"day": D[-1], "ret": -(n.iloc[i] / n.iloc[i - 4] - 1) - 0.0004})
        judge(tag, rows, "2013-01-01", "2000-01-01", "2026-11-01", 0, 0.005, 30000)


def part485(Y):
    print("\n#### #485 MSCI quarterly review close (fade the review-day move the next day; last business day of Feb/May/Aug/Nov)")
    for tag, sym in (("#485 main EEM", "EEM"), ("#485 variant EFA", "EFA")):
        a = Y.get(sym)
        if a is None:
            print(f"  {tag}: data not fetched yet (ubatchi)")
            continue
        rows = []
        for m, g in a.groupby(a.index.to_period("M")):
            if m.month not in (2, 5, 8, 11):
                continue
            rd = g.index[-1]
            i = a.index.get_loc(rd)
            if i < 1 or i + 1 >= len(a):
                continue
            r = a.iloc[i] / a.iloc[i - 1] - 1
            if r == 0:
                continue
            rows.append({"day": rd, "ret": -np.sign(r) * (a.iloc[i + 1] / a.iloc[i] - 1) - 0.0004})
        judge(tag, rows, "2013-01-01", "2004-01-01", "2026-11-01", 0, 0.002, 30000)


def part486(P, Y):
    print("\n#### #486 Australian super-fund hedge rebalancing (month-end, |SPY/EFA MTD| > 2% -> AUDUSD 14:00 -> 16:05 London)")
    s = P.get("AUDUSD")
    if s is None or "SPY" not in Y or "EFA" not in Y:
        print("  data not fetched yet (ubatchi)")
        return
    a = pd.concat([Y["SPY"], Y["EFA"]], axis=1, keys=["SPY", "EFA"]).dropna()
    rows = []
    months = a.groupby(a.index.to_period("M"))
    prev_last = None
    for m, g in months:
        if prev_last is not None and len(g) >= 2:
            last, before = g.index[-1], g.index[-2]
            R = ((a.at[before, "SPY"] / a.at[prev_last, "SPY"] - 1) + (a.at[before, "EFA"] / a.at[prev_last, "EFA"] - 1)) / 2
            if abs(R) > 0.02:
                p0, p1 = s.get(loc(last, "14:00", "Europe/London")), s.get(loc(last, "16:05", "Europe/London"))
                if p0 is not None and p1 is not None:
                    rows.append({"day": last, "bp": (1 if R > 0 else -1) * (p1 / p0 - 1) * 1e4 - 0.3})
        prev_last = g.index[-1]
    judge("#486 main", rows, "2019-01-01", "2012-01-01", "2026-11-01", 0, 0.5, 15, unit="bp")


def part487(Y):
    print("\n#### #487 tax-loss rebound (long IWM / short SPY, last trading day <= Dec 15 -> last trading day <= Jan 15)")
    if "IWM" not in Y or "SPY" not in Y:
        print("  data not fetched yet (ubatchi)")
        return
    a = pd.concat([Y["IWM"], Y["SPY"]], axis=1, keys=["I", "S"]).dropna()
    d = a.index
    rows = []
    for yr in range(2000, 2026):
        e0, e1 = d[d <= pd.Timestamp(yr, 12, 15)], d[d <= pd.Timestamp(yr + 1, 1, 15)]
        if not len(e0) or not len(e1) or e1[-1].year != yr + 1:
            continue
        i0, i1 = e0[-1], e1[-1]
        rows.append({"day": i0, "ret": (a.at[i1, "I"] / a.at[i0, "I"] - 1) - (a.at[i1, "S"] / a.at[i0, "S"] - 1) - 0.0008})
    judge("#487 main", rows, "2013-01-01", "2001-01-01", "2026-11-01", 0, 0.005, 30000)


def main():
    print("===== Batch I (#478-#487)  docs/PREREG_BATCH_I_20261126.md")
    P = {ins: duka(ins) for ins in (*PAIRS, "XAUUSD", "XAGUSD")}
    Y = yahoo_adj()
    part478(P)
    part479(P)
    part480(P)
    part481()
    part482()
    part483(Y)
    part484(Y)
    part485(Y)
    part486(P, Y)
    part487(Y)


if __name__ == "__main__":
    main()

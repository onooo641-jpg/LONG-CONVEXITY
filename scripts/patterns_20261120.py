"""Futures timing patterns, exactly as docs/PREREG_20261120.md Part A defines them.

    uv run python scripts/patterns_20261120.py

Pre-registered in 005220e. Own-account micro futures, not Topstep.
"""

from __future__ import annotations

import datetime as dt

import numpy as np
import pandas as pd

from ict import data as D

#: market -> (raw pattern or None for processed NQ, round-trip cost in points, $ per point for the micro)
MARKETS = {"NQ": (None, 1.12, 2.0), "ES": ("ES", 0.748, 5.0),
           "YM": ("YM", 4.48, 0.5), "RTY": ("RTY", 0.448, 5.0)}
OLD = (dt.date(2010, 7, 1), dt.date(2016, 1, 1))
SEEN = (dt.date(2016, 1, 1), dt.date(2026, 10, 29))
H3_SEEN = (dt.date(2024, 1, 1), dt.date(2026, 10, 29))
GAP_MIN = 0.0025
ROLL_DAYS = 10

#: FOMC statement days 2024-01..2026-10, as listed by third-party calendars on
#: 2026-11-20 (the Fed's own page was not read). See the pre-registration.
FOMC_RECENT = [
    "2024-01-31", "2024-03-20", "2024-05-01", "2024-06-12", "2024-07-31", "2024-09-18",
    "2024-11-07", "2024-12-18", "2025-01-29", "2025-03-19", "2025-05-07", "2025-06-18",
    "2025-07-30", "2025-09-17", "2025-10-29", "2025-12-10", "2026-01-28", "2026-03-18",
    "2026-04-29", "2026-06-17", "2026-07-29", "2026-09-16", "2026-10-28",
]


def tstat(x):
    x = np.asarray(x, dtype=float)
    return float(x.mean() / (x.std(ddof=1) / np.sqrt(len(x)))) if len(x) > 2 else float("nan")


def welch(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    if len(a) < 3 or len(b) < 3:
        return float("nan")
    return float((a.mean() - b.mean()) / np.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b)))


def third_friday(y, m):
    d = dt.date(y, m, 15)
    return d + dt.timedelta(days=(4 - d.weekday()) % 7)


def daily_table(bars):
    m = bars["minutes_from_midnight"]
    rth = bars[(m >= 570) & (m < 960)]
    g = rth.groupby("ny_date")
    first_min = g["minutes_from_midnight"].first()
    last_min = g["minutes_from_midnight"].last()
    day = pd.DataFrame({"open": g["open"].first(), "close": g["close"].last(),
                        "first": first_min, "last": last_min})
    day = day[(day["first"] == 570) & (day["last"] >= 955)].copy()
    at = lambda minute, col: bars[m == minute].groupby("ny_date")[col].first()  # noqa: E731
    day["o1400"] = at(840, "open")
    day["c1359"] = at(839, "close")
    day.index = pd.Index(day.index, name="date")
    return day.sort_index(), rth


def roll_days(dates):
    dates = list(dates)
    out = set()
    for y in range(dates[0].year, dates[-1].year + 1):
        for mo in (3, 6, 9, 12):
            exp = third_friday(y, mo)
            before = [d for d in dates if d < exp][-ROLL_DAYS:]
            out.update(before)
    return out


def in_window(d, w):
    return w[0] <= d < w[1]


def run_market(name, bars, cost, ppt, fomc_old):
    day, rth = daily_table(bars)
    dates = list(day.index)
    idx = {d: i for i, d in enumerate(dates)}
    roll = roll_days(dates)
    clean = lambda *ds: not any(d in roll for d in ds)  # noqa: E731
    o, c = day["open"].to_numpy(), day["close"].to_numpy()
    rec = []  # (hyp, window_key, kind, date, net)

    # H1 overnight vs intraday
    for i in range(1, len(dates)):
        d, p = dates[i], dates[i - 1]
        if (d - p).days > 4 or not clean(p, d):
            continue
        rec.append(("H1", d, "event", o[i] - c[i - 1] - cost))
        rec.append(("H1", d, "base", c[i] - o[i] - cost))

    # H2 turn of month: close(day -2) -> close(day +3)
    s = pd.Series(dates)
    month = s.map(lambda d: (d.year, d.month))
    tom_spans = []
    for (y, mo), grp in s.groupby(month):
        ix = list(grp.index)
        if len(ix) < 2:
            continue
        start = ix[-2]
        nxt = [k for k in range(ix[-1] + 1, min(ix[-1] + 6, len(dates)))
               if (dates[k].year, dates[k].month) != (y, mo)]
        if len(nxt) < 3:
            continue
        end = nxt[2]
        tom_spans.append((start, end))
        if clean(*dates[start:end + 1]):
            rec.append(("H2", dates[start], "event", c[end] - c[start] - cost))
    covered = set()
    for a, b in tom_spans:
        covered.update(range(a, b + 1))
    k = 0
    while k + 4 < len(dates):
        span = range(k, k + 5)
        if not covered.intersection(span) and clean(*dates[k:k + 5]) and (dates[k + 4] - dates[k]).days < 10:
            rec.append(("H2", dates[k], "base", c[k + 4] - c[k] - cost))
            k += 4
        else:
            k += 1

    # H3 pre-FOMC: 14:00 day before -> 13:59 statement day
    fomc = set(fomc_old) | {dt.date.fromisoformat(x) for x in FOMC_RECENT}
    o14, c1359 = day["o1400"].to_numpy(), day["c1359"].to_numpy()
    for i in range(1, len(dates)):
        d, p = dates[i], dates[i - 1]
        if (d - p).days > 4 or not clean(p, d) or np.isnan(o14[i - 1]) or np.isnan(c1359[i]):
            continue
        if p in fomc:
            continue
        rec.append(("H3", d, "event" if d in fomc else "base", c1359[i] - o14[i - 1] - cost))

    # H5 gap fade
    for i in range(1, len(dates)):
        d, p = dates[i], dates[i - 1]
        if (d - p).days > 4 or not clean(p, d):
            continue
        prev, op = c[i - 1], o[i]
        gap = (op - prev) / prev
        if abs(gap) < GAP_MIN:
            continue
        direction = -1 if gap > 0 else 1
        bars_d = rth[rth["ny_date"] == d]
        hit = (bars_d["high"] >= prev) if direction > 0 else (bars_d["low"] <= prev)
        exit_px = prev if hit.any() else c[i]
        rec.append(("H5", d, "event", direction * (exit_px - op) - cost))

    # H6 day of week (one test per weekday)
    for i, d in enumerate(dates):
        if not clean(d):
            continue
        for wd in range(5):
            rec.append((f"H6-{'MTWRF'[wd]}", d, "event" if d.weekday() == wd else "base", c[i] - o[i] - cost))

    df = pd.DataFrame(rec, columns=["hyp", "date", "kind", "net"])
    df["ppt"] = ppt
    df["market"] = name
    return df


def main() -> int:
    cal = pd.read_csv(D.REPO_ROOT / "docs" / "tier1_calendar_2010_2015.csv")
    fomc_old = {dt.date.fromisoformat(x) for x in cal.loc[cal["release"] == "FOMC", "date"]}
    frames = []
    for name, (raw, cost, ppt) in MARKETS.items():
        bars = D.load("1m") if raw is None else D.add_time_columns(D.load_raw(f"{raw}_v_0_1m_*.parquet"))
        frames.append(run_market(name, bars, cost, ppt, fomc_old))
        print(f"{name}: done", flush=True)
    allr = pd.concat(frames, ignore_index=True)

    hyps = ["H1", "H2", "H3", "H5"] + [f"H6-{x}" for x in "MTWRF"]
    print("\nper market and window: n events, mean net pts, t(event), t(event vs base), $/yr per micro")
    verdicts = {}
    for h in hyps:
        thr = 2.6 if h.startswith("H6") else 2.0
        print(f"\n{h}  (t threshold {thr})")
        passes = {"OLD": [], "SEEN": []}
        for wname, w in (("OLD", OLD), ("SEEN", H3_SEEN if h == "H3" else SEEN)):
            for mkt in MARKETS:
                sub = allr[(allr.hyp == h) & (allr.market == mkt) & allr.date.map(lambda d: in_window(d, w))]
                ev, base = sub[sub.kind == "event"]["net"], sub[sub.kind == "base"]["net"]
                if len(ev) < 10:
                    print(f"  {wname:<4} {mkt:<3} not enough data ({len(ev)} events)")
                    continue
                t1 = tstat(ev)
                t2 = welch(ev, base) if len(base) else float("nan")
                years = (w[1] - w[0]).days / 365.25
                usd = ev.mean() * len(ev) / years * MARKETS[mkt][2]
                ok = ev.mean() > 0 and t1 > thr and (np.isnan(t2) if not len(base) else t2 > thr)
                passes[wname].append(ok)
                print(f"  {wname:<4} {mkt:<3} n {len(ev):>5}  mean {ev.mean():>8.2f}  t {t1:>6.2f}  "
                      f"vs base {t2:>6.2f}  ${usd:>8,.0f}/yr  {'PASS' if ok else '-'}")
        seen_ok = sum(passes["SEEN"]) >= 3
        old_ok = sum(passes["OLD"]) >= 2
        verdicts[h] = seen_ok and old_ok
        print(f"  -> SEEN {sum(passes['SEEN'])}/{len(passes['SEEN'])}, OLD {sum(passes['OLD'])}/{len(passes['OLD'])}"
              f"  => {'PASS' if verdicts[h] else 'fail'}")

    # sanity: largest overnight moves kept, in points, to show roll jumps are gone
    h1 = allr[(allr.hyp == "H1") & (allr.kind == "event")]
    print("\nsanity: largest kept overnight moves (pts, before costs) by market")
    for mkt in MARKETS:
        x = h1[h1.market == mkt]
        top = x.assign(a=(x["net"] + MARKETS[mkt][1]).abs()).nlargest(3, "a")
        print(f"  {mkt}: " + ", ".join(f"{r.date} {r.net + MARKETS[mkt][1]:+.1f}" for r in top.itertuples()))

    print("\n=== VERDICTS")
    for h, v in verdicts.items():
        print(f"  {h:<6} {'PASS' if v else 'fail'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

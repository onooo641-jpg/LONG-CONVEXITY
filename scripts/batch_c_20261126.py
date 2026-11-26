"""Batch C #429-#438 (docs/PREREG_BATCH_C_20261126.md).

    uv run python -m scripts.batch_c_20261126 | tee docs/jx_runs/batch_c_20261126.txt
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

PUB = Path(__file__).resolve().parent.parent / "data" / "public"
FEE = 0.00045


def tstat(r):
    r = pd.Series(r).dropna()
    return r.mean() / (r.std(ddof=1) / np.sqrt(len(r))) if len(r) > 1 else np.nan


def show(x, label):
    if len(x) == 0:
        print(f"  {label}: no events")
        return 0, np.nan, np.nan, np.nan
    r = x["ret"]
    print(f"  {label}: events {len(r)}, mean {r.mean():.2%}, median {r.median():.2%}, t {tstat(r):.2f}, win {(r > 0).mean():.0%}, worst {r.min():.1%}")
    return len(r), r.mean(), tstat(r), (r > 0).mean()


def depegs(ids, buy_at, label):
    p = PUB / "batchc_stables_1h.parquet"
    print(f"\n#### {label}")
    if not p.exists():
        print("  data not fetched yet")
        return
    d = pd.read_parquet(p)
    d = d[d["id"].isin(ids)].copy()
    d["ts"] = pd.to_datetime(d["t"], unit="s", utc=True)
    rows = []
    for g, x in d.groupby("id"):
        x = x.drop_duplicates("ts").set_index("ts")["price"].sort_index()
        x = x[(x > 0.3) & (x < 1.5)]
        busy = None
        for ts, v in x.items():
            if busy is not None and ts <= busy:
                continue
            if v > buy_at:
                continue
            after = x[(x.index > ts) & (x.index <= ts + pd.Timedelta(days=30))]
            hit = after[after >= 0.997]
            ex_ts, ex = (hit.index[0], hit.iloc[0]) if len(hit) else ((after.index[-1], after.iloc[-1]) if len(after) else (None, None))
            if ex_ts is None:
                continue
            rows.append({"id": g, "ts": ts, "buy": v, "ret": ex / v - 1 - 0.001, "days": (ex_ts - ts).days})
            busy = ex_ts
    t = pd.DataFrame(rows)
    if len(t):
        print(t.assign(ts=t["ts"].dt.date).to_string(index=False, float_format=lambda v: f"{v:8.4f}"))
    s = t[t["ts"] < "2023-01-01"] if len(t) else t
    o = t[t["ts"] >= "2023-01-01"] if len(t) else t
    n1, m1, _, _ = show(s, "Stage 1 (2020-2022)")
    s1 = not (n1 < 3 or m1 <= 0)
    print(f"  STAGE 1 VERDICT: {'survives (kill-only)' if s1 else 'KILL'}")
    n2, m2, _, w2 = show(o, "Stage 2 (out-of-sample 2023-01..2026-10)")
    ok = s1 and n2 >= 3 and m2 >= 0.01 and w2 >= 0.75
    print(f"  STAGE 2 VERDICT: {'PASS' if ok else ('FAIL' if s1 else 'not judged — context')}")


def part431():
    print("\n#### #431 Binance deposit/withdrawal suspension convergence")
    p = PUB / "batchc_binance_ann.json"
    if not p.exists():
        print("  data not fetched yet")
        return
    a = json.loads(p.read_text())
    items = {x["code"]: x for v in a.values() for x in v}.values()
    sus = [x for x in items if re.search(r"Suspend|Suspension", x["title"] or "", re.I) and re.search(r"Deposit|Withdrawal", x["title"] or "", re.I)]
    print(f"  suspension announcements: {len(sus)} (of {len(items)} items)")
    for x in sus[:5]:
        print(f"     {pd.Timestamp(int(x['releaseDate']), unit='ms').date()} {x['title'][:110]}")
    print("  STAGE 1: event list needs token + suspension window from each announcement body (titles only here) -> not testable from titles; recorded")


def part432_433():
    print("\n#### #432/#433 funding-sentiment extremes (median daily funding of top-50 Binance perps)")
    bf = pd.read_parquet(PUB / "cryptotrend370_funding.parquet")
    b = pd.read_parquet(PUB / "uncharted_389_binance_ohlc.parquet", columns=["sym", "t", "c", "qvol"])
    b["day"] = pd.to_datetime(b["t"], unit="s", utc=True).dt.normalize()
    b = b.drop_duplicates(["sym", "day"])
    vol = b.pivot(index="day", columns="sym", values="qvol").rolling(30, min_periods=10).sum().shift(1)
    F = bf.pivot_table(index="date", columns="sym", values="rate", aggfunc="sum").reindex(vol.index)
    med = pd.Series({d: F.loc[d, vol.loc[d].nlargest(50).index].median() for d in vol.index if vol.loc[d].notna().sum() >= 50})
    lo, hi = med.rolling(365, min_periods=180).quantile(0.05).shift(1), med.rolling(365, min_periods=180).quantile(0.95).shift(1)
    C = b.pivot(index="day", columns="sym", values="c")
    for sym, tag in (("BTCUSDT", "#432 BTC"), ("ETHUSDT", "#433 ETH")):
        rows, busy = [], None
        for d in med.index:
            if busy is not None and d <= busy or pd.isna(lo.get(d)):
                continue
            side = 1 if med[d] < lo[d] else (-1 if med[d] > hi[d] else 0)
            if side == 0:
                continue
            ex = d + pd.Timedelta(days=7)
            if ex not in C.index:
                continue
            rows.append({"day": d, "ret": side * (C.at[ex, sym] / C.at[d, sym] - 1) - 2 * FEE})
            busy = ex
        t = pd.DataFrame(rows)
        print(f"  {tag}:")
        n1, m1, t1, _ = show(t[t["day"] < "2023-01-01"], "Stage 1 (2020-2022)")
        s1 = not (m1 < 0.005 or t1 < 1)
        print(f"  STAGE 1 VERDICT ({tag}): {'survives (kill-only)' if s1 else 'KILL'}")
        n2, m2, t2, _ = show(t[t["day"] >= "2023-01-01"], "Stage 2 (out-of-sample 2023-2026)")
        ok = s1 and n2 >= 10 and m2 >= 0.015 and t2 >= 2
        print(f"  STAGE 2 VERDICT ({tag}): {'PASS' if ok else ('FAIL' if s1 else 'not judged — context')}")


def part434_435():
    print("\n#### #434/#435 CME weekend-gap fill (Fri 21:00 -> Sun 22:00 UTC)")
    p = PUB / "batchc_btceth_1h.parquet"
    if not p.exists():
        print("  data not fetched yet")
        return
    d = pd.read_parquet(p)
    d["ts"] = pd.to_datetime(d["t"], unit="s", utc=True)
    for sym, tag in (("BTCUSDT", "#434 BTC"), ("ETHUSDT", "#435 ETH")):
        x = d[d["sym"] == sym].drop_duplicates("ts").set_index("ts")["c"].sort_index()
        rows = []
        for sun in x.index[(x.index.weekday == 6) & (x.index.hour == 22)]:
            fri = sun - pd.Timedelta(days=2, hours=1)
            if fri not in x.index:
                continue
            gap = x[sun] / x[fri] - 1
            if abs(gap) < 0.015:
                continue
            side = -np.sign(gap)
            path = x[(x.index > sun) & (x.index <= sun + pd.Timedelta(days=3))]
            hit = path[(path - x[fri]) * np.sign(gap) <= 0]
            ex = hit.iloc[0] if len(hit) else path.iloc[-1]
            rows.append({"day": sun, "ret": side * (ex / x[sun] - 1) - 2 * FEE})
        t = pd.DataFrame(rows)
        print(f"  {tag}:")
        n1, m1, t1, _ = show(t[t["day"] < "2023-01-01"], "Stage 1 (2020-2022)")
        s1 = not (m1 < 0.003 or t1 < 1)
        print(f"  STAGE 1 VERDICT ({tag}): {'survives (kill-only)' if s1 else 'KILL'}")
        n2, m2, t2, _ = show(t[t["day"] >= "2023-01-01"], "Stage 2 (out-of-sample 2023-2026)")
        ok = s1 and n2 >= 30 and m2 >= 0.005 and t2 >= 2
        print(f"  STAGE 2 VERDICT ({tag}): {'PASS' if ok else ('FAIL' if s1 else 'not judged — context')}")


def part436_437():
    print("\n#### #436/#437 HIP-3 weekend fade (Sat+Sun move >= 2%, fade Sunday close -> Monday close)")
    d = pd.read_parquet(PUB / "fivehigh_hip3_1d.parquet")
    d["day"] = pd.to_datetime(d["t"], unit="ms", utc=True).dt.normalize()
    d = d.drop_duplicates(["coin", "day"])
    comm = re.compile(r"GOLD|SILVER|XAU|XAG|OIL|WTI|BRENT|NATGAS|COPPER|PLAT|PALL", re.I)
    idx = re.compile(r"SPX|SP500|NDX|NAS|US500|US100|DJI|US30|NIK|DAX|HSI|INDEX|QQQ|SPY", re.I)
    C = d.pivot(index="day", columns="coin", values="c").sort_index()
    for pat, tag in ((comm, "#436 commodities"), (idx, "#437 stock indices")):
        cols = [c for c in C.columns if pat.search(c.split(":")[-1])]
        rows = []
        for c in cols:
            s = C[c].dropna()
            for mon in s.index[s.index.weekday == 0]:
                fri, sun_close, mon_close = mon - pd.Timedelta(days=3), mon, mon + pd.Timedelta(days=1)
                if fri not in s.index or mon_close not in s.index:
                    continue
                wk = s[sun_close] / s[fri] - 1  # Sat + Sun move (daily closes at 00:00 UTC)
                if abs(wk) < 0.02:
                    continue
                rows.append({"day": mon, "coin": c, "ret": -np.sign(wk) * (s[mon_close] / s[sun_close] - 1) - 2 * FEE})
        t = pd.DataFrame(rows)
        print(f"  {tag}: markets {len(cols)} ({cols[:8]})")
        if t.empty:
            print(f"  STAGE VERDICT ({tag}): not testable (no events)")
            continue
        mid = t["day"].min() + (t["day"].max() - t["day"].min()) / 2
        n1, m1, _, _ = show(t[t["day"] < mid], "Stage 1 (first half)")
        s1 = not (pd.isna(m1) or m1 <= 0)
        print(f"  STAGE 1 VERDICT ({tag}): {'survives (kill-only)' if s1 else 'KILL'}")
        n2, m2, t2, _ = show(t[t["day"] >= mid], "Stage 2 (second half, out-of-sample)")
        ok = s1 and n2 >= 15 and m2 >= 0.005 and t2 >= 2
        print(f"  STAGE 2 VERDICT ({tag}): {'PASS' if ok else ('FAIL' if s1 else 'not judged — context')}")


def _hourly():
    p = PUB / "batchc_btceth_1h.parquet"
    if not p.exists():
        return None
    d = pd.read_parquet(p)
    d["ts"] = pd.to_datetime(d["t"], unit="s", utc=True)
    return {s: g.drop_duplicates("ts").set_index("ts")["c"].sort_index() for s, g in d.groupby("sym")}


def _judge(t, tag, s1_min_mean, s2_n, s2_mean, split="2023-01-01", s1_start=None):
    x1 = t[(t["day"] < split) & ((t["day"] >= s1_start) if s1_start else True)] if len(t) else t
    x2 = t[t["day"] >= split] if len(t) else t
    n1, m1, t1, _ = show(x1, "Stage 1")
    s1 = not (pd.isna(m1) or m1 < s1_min_mean or t1 < 1)
    print(f"  STAGE 1 VERDICT ({tag}): {'survives (kill-only)' if s1 else 'KILL'}")
    n2, m2, t2, _ = show(x2, "Stage 2 (out-of-sample)")
    ok = s1 and n2 >= s2_n and m2 >= s2_mean and t2 >= 2
    print(f"  STAGE 2 VERDICT ({tag}): {'PASS' if ok else ('FAIL' if s1 else 'not judged — context')}")


def part439(H):
    print("\n#### #439 options-expiry unwind (last Friday of the month, 08:00 UTC)")
    for sym in ("BTCUSDT", "ETHUSDT"):
        x, rows = H[sym], []
        fridays = x.index[(x.index.weekday == 4) & (x.index.hour == 8)]
        last = pd.Series(fridays).groupby(pd.Series(fridays).dt.to_period("M")).max()
        for fri in last:
            prev, mon = fri - pd.Timedelta(days=7), fri + pd.Timedelta(days=3)
            if prev not in x.index or mon not in x.index:
                continue
            side = 1 if x[fri] < x[prev] else -1
            rows.append({"day": fri, "ret": side * (x[mon] / x[fri] - 1) - 2 * FEE})
        print(f"  {sym}:")
        _judge(pd.DataFrame(rows), f"#439 {sym}", 0.003, 30, 0.005)


def part440(H):
    print("\n#### #440 funding-settlement drift (2 h before -> 1 h after, |last funding| >= 0.03%)")
    fp = PUB / "batchc_funding8h.parquet"
    if not fp.exists():
        print("  funding events not fetched yet")
        return
    fr = pd.read_parquet(fp)
    fr["ts"] = pd.to_datetime(fr["t"], unit="s", utc=True).dt.round("h")
    for sym in ("BTCUSDT", "ETHUSDT"):
        x, f, rows = H[sym], fr[fr["sym"] == sym].drop_duplicates("ts").set_index("ts")["rate"].sort_index(), []
        for ts, last in f.shift(1).dropna().items():
            if abs(last) < 0.0003:
                continue
            a, b = ts - pd.Timedelta(hours=2), ts + pd.Timedelta(hours=1)
            if a not in x.index or b not in x.index:
                continue
            side = -1 if last > 0 else 1
            rows.append({"day": ts, "ret": side * (x[b] / x[a] - 1) - 2 * FEE})
        print(f"  {sym}:")
        _judge(pd.DataFrame(rows), f"#440 {sym}", 0.0005, 100, 0.0008)


def part441(H):
    print("\n#### #441 US spot-ETF fix window (18:00 -> 21:00 UTC, direction of the previous US session)")
    for sym in ("BTCUSDT", "ETHUSDT"):
        x, rows = H[sym], []
        days = sorted({t.normalize() for t in x.index if t >= pd.Timestamp("2024-01-11", tz="UTC") and t.weekday() < 5})
        for d in days[1:]:
            p0, p1 = d - pd.Timedelta(days=1) + pd.Timedelta(hours=13, minutes=0), d - pd.Timedelta(days=1) + pd.Timedelta(hours=21)
            a, b = d + pd.Timedelta(hours=18), d + pd.Timedelta(hours=21)
            if any(t not in x.index for t in (p0, p1, a, b)):
                continue
            side = 1 if x[p1] > x[p0] else -1
            rows.append({"day": d, "ret": side * (x[b] / x[a] - 1) - 2 * FEE})
        print(f"  {sym}:")
        _judge(pd.DataFrame(rows), f"#441 {sym}", 0.0005, 150, 0.0008, split="2025-01-01")


def part442():
    print("\n#### #442 Coinbase premium extremes (3-day hold)")
    cp = PUB / "batchc_coinbase_1d.parquet"
    if not cp.exists():
        print("  Coinbase candles not fetched yet")
        return
    cb = pd.read_parquet(cp)
    cb["day"] = pd.to_datetime(cb["t"], unit="s", utc=True).dt.normalize()
    b = pd.read_parquet(PUB / "uncharted_389_binance_ohlc.parquet", columns=["sym", "t", "c"])
    b["day"] = pd.to_datetime(b["t"], unit="s", utc=True).dt.normalize()
    for prod, sym in (("BTC-USD", "BTCUSDT"), ("ETH-USD", "ETHUSDT")):
        c = cb[cb["prod"] == prod].drop_duplicates("day").set_index("day")["c"].sort_index()
        bn = b[b["sym"] == sym].drop_duplicates("day").set_index("day")["c"].sort_index()
        prem = (c / bn - 1).dropna()
        hi, lo = prem.rolling(90, min_periods=60).quantile(0.95).shift(1), prem.rolling(90, min_periods=60).quantile(0.05).shift(1)
        rows, busy = [], None
        for d, v in prem.items():
            if (busy is not None and d <= busy) or pd.isna(hi.get(d)):
                continue
            side = 1 if v > hi[d] else (-1 if v < lo[d] else 0)
            ex = d + pd.Timedelta(days=3)
            if side == 0 or ex not in bn.index:
                continue
            rows.append({"day": d, "ret": side * (bn[ex] / bn[d] - 1) - 2 * FEE})
            busy = ex
        print(f"  {prod}:")
        _judge(pd.DataFrame(rows), f"#442 {prod}", 0.005, 20, 0.01)


def main():
    print("===== Batch C #429-#438")
    depegs(["usd-coin", "tether", "first-digital-usd", "paypal-usd", "true-usd", "binance-usd", "paxos-standard"], 0.98,
           "#429 fiat-backed stablecoin depeg buying (buy <= 0.98, exit >= 0.997 or 30 days)")
    depegs(["dai", "ethena-usde", "frax", "crvusd", "gho", "liquity-usd", "usdd", "usual-usd", "usds"], 0.97,
           "#430 crypto-backed/synthetic stablecoin depeg buying (buy <= 0.97)")
    part431()
    part432_433()
    part434_435()
    part436_437()
    print("\n#### #438 token-split / redenomination arbitrage: not testable (pre-registered desk result)")
    H = _hourly()
    if H is None:
        print("\n#439-#441: hourly data not fetched yet")
    else:
        part439(H)
        part440(H)
        part441(H)
    part442()


if __name__ == "__main__":
    main()

"""Batch G (#458-#467), exactly as docs/PREREG_BATCH_G_20261126.md defines it.

    uv run python -m scripts.batch_g_20261126 | tee docs/jx_runs/batch_g_20261126.txt
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from scripts.batch_d_20261126 import PUB, tstat

FEE = 0.00045


def judge(tag, r, split, s1_lo, s2_hi, n2, m2, usd_per_unit, unit="ret"):
    r = pd.DataFrame(r)
    if r.empty:
        print(f"  {tag}: no events")
        return
    s1 = r[(r["day"] >= s1_lo) & (r["day"] < split)][unit]
    s2 = r[(r["day"] >= split) & (r["day"] < s2_hi)][unit]
    fmt = (lambda v: f"{v:.3%}") if unit == "ret" else (lambda v: f"{v:.2f}")
    print(f"  {tag} Stage 1: n {len(s1)}, mean {fmt(s1.mean())}, t {tstat(s1):.2f}, win {(s1 > 0).mean():.0%}")
    print(f"  {tag} Stage 2: n {len(s2)}, mean {fmt(s2.mean())}, t {tstat(s2):.2f}, win {(s2 > 0).mean():.0%}")
    if not len(s1) or not (s1.mean() > 0):
        print(f"  VERDICT ({tag}): KILL")
        return
    ok = len(s2) >= n2 and s2.mean() >= m2 and tstat(s2) >= 2
    yrs = (pd.Timestamp(s2_hi) - pd.Timestamp(split)).days / 365.25
    print(f"  VERDICT ({tag}): {'PASS' if ok else 'FAIL'} (Stage 1 survives); ${s2.sum() * usd_per_unit / yrs:,.0f}/yr at safe size")


def btc_daily():
    p = PUB / "batchg_btc_1d.parquet"
    if not p.exists():
        return None
    d = pd.read_parquet(p)
    s = pd.Series(d["c"].to_numpy(), index=pd.to_datetime(d["t"], unit="s", utc=True).dt.normalize()).sort_index()
    return s[~s.index.duplicated()]


def hourly(sym):
    d = pd.read_parquet(PUB / "batchc_btceth_1h.parquet")
    d = d[d["sym"] == sym]
    s = pd.Series(d["c"].to_numpy(), index=pd.to_datetime(d["t"], unit="s", utc=True)).sort_index()
    return s[~s.index.duplicated()]


def at(x, T):
    """price at T = close of the 1h bar opening at T - 1h."""
    return x.get(T - pd.Timedelta(hours=1))


def fred_series(sid):
    f = pd.read_parquet(PUB / "batchd_fred_cmt.parquet")
    f = f[f["sid"] == sid]
    return pd.Series(f["y"].to_numpy(), index=pd.to_datetime(f["date"])).sort_index().dropna()


def part458():
    print("\n#### #458 miner margin squeeze (difficulty +5% -> short BTC 7 days)")
    btc, dp = btc_daily(), PUB / "batchg_difficulty.parquet"
    if btc is None or not dp.exists():
        print("  data not fetched yet (ubatchg)")
        return
    d = pd.read_parquet(dp)
    s = pd.Series(d["difficulty"].to_numpy(), index=pd.to_datetime(d["t"], unit="s", utc=True).dt.normalize()).sort_index()
    s = s[~s.index.duplicated()]
    ch = s.pct_change()
    for tag, cond, side in (("#458 up>=5% short", ch >= 0.05, -1), ("#458 variant down<=-5% long", ch <= -0.05, 1)):
        rows, busy = [], None
        for day in ch[cond].index:
            a = day + pd.Timedelta(days=1)
            b = a + pd.Timedelta(days=7)
            if (busy is not None and a < busy) or a not in btc.index or b not in btc.index:
                continue
            rows.append({"day": a, "ret": side * (btc[b] / btc[a] - 1) - 2 * FEE})
            busy = b
        judge(tag, rows, "2021-01-01", "2014-01-01", "2026-11-01", 20, 0.005, 45000)


def part459():
    print("\n#### #459 Treasury coupon reinvestment around the 15th (long duration, DGS10)")
    y = fred_series("DGS10")
    idx = y.index
    for tag, months in (("#459 Feb/May/Aug/Nov", (2, 5, 8, 11)), ("#459 variant all months", tuple(range(1, 13)))):
        rows = []
        for yr in range(1990, 2027):
            for mo in months:
                d15 = pd.Timestamp(yr, mo, 15)
                before = idx[idx < d15]
                after = idx[idx > d15]
                if len(before) < 3 or not len(after) or after[0] > pd.Timestamp("2026-11-01"):
                    continue
                a, b = before[-3], after[0]
                rows.append({"day": b, "bp": -(y[b] - y[a]) * 100 - 0.5})
        judge(tag, rows, "2010-01-01", "1990-01-01", "2026-11-01", 1, 0.5, 50, unit="bp")


def part460():
    print("\n#### #460 FX month-end hedge rebalancing at the London 16:00 fix (EURUSD)")
    ep, sp = PUB / "batchg_eurusd_monthend.parquet", PUB / "batchg_etf_1d.parquet"
    if not ep.exists() or not sp.exists():
        print("  data not fetched yet (ubatchg)")
        return
    e = pd.read_parquet(ep)
    etf = pd.read_parquet(sp)
    spy = etf[etf["sym"] == "SPY"]
    spy = pd.Series(spy["adj"].to_numpy(), index=pd.to_datetime(spy["t"], unit="s", utc=True).dt.tz_convert("America/New_York").dt.normalize().dt.tz_localize(None)).sort_index()
    spy = spy[~spy.index.duplicated()]
    rows = []
    for day, g in e.groupby("day"):
        dd = pd.Timestamp(day)
        fix_utc = 15 if pd.Timestamp(dd, tz="Europe/London").dst() != pd.Timedelta(0) else 16
        g = g.sort_values("sec")
        a = g[g["sec"] <= (fix_utc - 2) * 3600]
        b = g[g["sec"] <= fix_utc * 3600 + 300]
        if a.empty or b.empty:
            continue
        prev = spy[spy.index < dd]
        mstart = spy[spy.index < dd.replace(day=1)]
        if len(prev) < 2 or mstart.empty:
            continue
        mtd = prev.iloc[-1] / mstart.iloc[-1] - 1
        if abs(mtd) <= 0.02:
            continue
        side = 1 if mtd > 0 else -1  # long EURUSD = short USD after US equities rose
        rows.append({"day": dd, "pip": side * (b["mid"].iloc[-1] - a["mid"].iloc[-1]) * 10000 - 0.3})
    judge("#460 EURUSD", rows, "2019-01-01", "2012-01-01", "2026-11-01", 1, 0.5, 150000 / 10000, unit="pip")


def part461():
    print("\n#### #461 crypto funding carry cross-section (40 Binance perps, weekly)")
    k = pd.read_parquet(PUB / "batchd_alts_1h.parquet")
    k["ts"] = pd.to_datetime(k["t"], unit="s", utc=True)
    C = k.pivot_table(index="ts", columns="sym", values="close", aggfunc="last").sort_index()
    f = pd.read_parquet(PUB / "batchd_alts_funding.parquet")
    f["ts"] = pd.to_datetime(f["t"], unit="s", utc=True).dt.round("h")
    F = f.pivot_table(index="ts", columns="sym", values="rate", aggfunc="last").sort_index()
    mondays = [t for t in C.index if t.weekday() == 0 and t.hour == 0 and t >= pd.Timestamp("2021-01-04", tz="UTC")]
    rows = []
    for a in mondays:
        b = a + pd.Timedelta(days=7)
        pa, pb = C.loc[:a - pd.Timedelta(hours=1)].iloc[-1:] if False else C.shift(1).reindex([a]), C.shift(1).reindex([b])
        if pb.isna().all(axis=None):
            continue
        trail = F[(F.index > a - pd.Timedelta(days=7)) & (F.index <= a)].mean()
        hold = F[(F.index > a) & (F.index <= b)].sum()
        ok = trail.dropna().index.intersection(pa.columns[pa.notna().iloc[0] & pb.notna().iloc[0]])
        if len(ok) < 15:
            continue
        rk = trail[ok].sort_values()
        lo, hi = list(rk.index[:5]), list(rk.index[-5:])
        ret = lambda s: (pb[s].iloc[0] / pa[s].iloc[0] - 1)  # noqa: E731
        long_leg = np.mean([ret(s) - hold.get(s, 0) for s in lo])
        short_leg = np.mean([-ret(s) + hold.get(s, 0) for s in hi])
        rows.append({"day": a, "ret": (long_leg + short_leg) / 2 - 0.001})
    r = pd.DataFrame(rows)
    for lab, lo_, hi_ in (("Stage 1 2021-2022", "2021-01-01", "2023-01-01"), ("Stage 2 2023-2026-10", "2023-01-01", "2026-11-01")):
        x = r[(r["day"] >= lo_) & (r["day"] < hi_)]["ret"]
        print(f"  {lab}: weeks {len(x)}, mean weekly {x.mean():.3%}, t {tstat(x):.2f}, annualised {x.mean() * 52:.1%}, worst week {x.min():.1%}")
    s1 = r[r["day"] < "2023-01-01"]["ret"]
    s2 = r[(r["day"] >= "2023-01-01") & (r["day"] < "2026-11-01")]["ret"]
    if s1.mean() <= 0:
        print("  VERDICT (#461): KILL")
        return
    ok = s2.mean() > 0 and tstat(s2) >= 2 and s2.mean() * 52 >= 0.15
    print(f"  VERDICT (#461): {'PASS' if ok else 'FAIL'}; ${s2.mean() * 52 * 30000:,.0f}/yr on $30K gross ($15K x2)")


def part462():
    print("\n#### #462 payday recurring buys (BTC, 24th -> 27th)")
    btc = btc_daily()
    if btc is None:
        print("  data not fetched yet (ubatchg)")
        return
    for tag, spans in (("#462 25th", [(24, 27)]), ("#462 variant 1st/15th", [(0, 2), (14, 16)])):
        rows = []
        for m in pd.period_range("2014-01", "2026-10", freq="M"):
            for d0, d1 in spans:
                a = (pd.Timestamp(m.year, m.month, 1, tz="UTC") + pd.Timedelta(days=d0 - 1)) if d0 else pd.Timestamp(m.year, m.month, 1, tz="UTC") - pd.Timedelta(days=1)
                b = pd.Timestamp(m.year, m.month, 1, tz="UTC") + pd.Timedelta(days=d1 - 1)
                pa, pb = btc.get(a - pd.Timedelta(days=1)), btc.get(b - pd.Timedelta(days=1))  # daily close = 00:00 next day
                if pa is None or pb is None:
                    continue
                rows.append({"day": a, "ret": pb / pa - 1 - 2 * FEE})
        judge(tag, rows, "2021-01-01", "2014-01-01", "2026-11-01", 1, 0.003, 45000)


def part463():
    print("\n#### #463 buyback open windows (SPY, excess over same-length windows)")
    sp = PUB / "batchg_etf_1d.parquet"
    if not sp.exists():
        print("  data not fetched yet (ubatchg)")
        return
    etf = pd.read_parquet(sp)
    spy = etf[etf["sym"] == "SPY"]
    spy = pd.Series(spy["adj"].to_numpy(), index=pd.to_datetime(spy["t"], unit="s", utc=True).dt.tz_convert("America/New_York").dt.normalize().dt.tz_localize(None)).sort_index()
    spy = spy[~spy.index.duplicated()]
    idx = spy.index
    lr = np.log(spy).diff()
    rows = []
    for yr in range(2000, 2027):
        for mo in (1, 4, 7, 10):
            after25 = idx[idx > pd.Timestamp(yr, mo, 25)]
            end = idx[idx <= pd.Timestamp(yr, mo + 2, 14)]
            if len(after25) < 3 or not len(end) or end[-1] <= after25[2]:
                continue
            a, b = after25[2], end[-1]
            n = len(idx[(idx > a) & (idx <= b)])
            mean_window = lr.mean() * n
            rows.append({"day": a, "ret": np.log(spy[b] / spy[a]) - mean_window - 0.0004})
    judge("#463 SPY", rows, "2013-01-01", "2000-01-01", "2026-11-01", 1, 0.0, 30000)


def part464():
    print("\n#### #464 fixed-time DCA buying (long BTC 00:00 -> 02:00 UTC daily)")
    x = hourly("BTCUSDT")
    rows = []
    for d in pd.date_range("2020-01-02", "2026-10-31", freq="D", tz="UTC"):
        pa, pb = at(x, d), at(x, d + pd.Timedelta(hours=2))
        if pa is None or pb is None:
            continue
        rows.append({"day": d, "ret": pb / pa - 1 - 2 * FEE})
    judge("#464 BTC", rows, "2023-01-01", "2020-01-01", "2026-11-01", 1, 0.0005, 45000)


def part465():
    print("\n#### #465 CME bitcoin-futures expiry (short BTC 4 h before BRR end, last Friday)")
    x = hourly("BTCUSDT")
    rows = []
    for m in pd.period_range("2020-01", "2026-10", freq="M"):
        last = m.to_timestamp(how="end").normalize()
        while last.weekday() != 4:
            last -= pd.Timedelta(days=1)
        end_utc = 15 if pd.Timestamp(last, tz="Europe/London").dst() != pd.Timedelta(0) else 16
        b = pd.Timestamp(last.date(), tz="UTC") + pd.Timedelta(hours=end_utc)
        a = b - pd.Timedelta(hours=4)
        pa, pb = at(x, a), at(x, b)
        if pa is None or pb is None:
            continue
        rows.append({"day": a, "ret": -(pb / pa - 1) - 2 * FEE})
    judge("#465 BTC", rows, "2024-01-01", "2020-01-01", "2026-11-01", 20, 0.002, 45000)


def part466():
    print("\n#### #466 Japanese month-start buying (long USD/JPY, last business day -> 3rd business day)")
    p = PUB / "batchg_dexjpus.parquet"
    if not p.exists():
        print("  data not fetched yet (ubatchg)")
        return
    f = pd.read_parquet(p)
    s = pd.Series(f["rate"].to_numpy(), index=pd.to_datetime(f["date"])).sort_index()
    per = s.index.to_period("M")
    rows = []
    months = sorted(set(per))
    for m0, m1 in zip(months[:-1], months[1:]):
        a = s[per == m0].index[-1]
        nxt = s[per == m1].index
        if len(nxt) < 3:
            continue
        rows.append({"day": a, "ret": s[nxt[2]] / s[a] - 1 - 0.00004})
    judge("#466 USDJPY", rows, "2019-01-01", "2010-01-01", "2026-11-01", 1, 0.0015, 150000)


def part467():
    print("\n#### #467 large USDT supply jumps (>= $500M day over day) -> long BTC 24 h")
    btc, p = btc_daily(), PUB / "batchg_usdt_supply.parquet"
    if btc is None or not p.exists():
        print("  data not fetched yet (ubatchg)")
        return
    d = pd.read_parquet(p)
    s = pd.Series(d["supply"].to_numpy(), index=pd.to_datetime(d["t"], unit="s", utc=True).dt.normalize()).sort_index()
    s = s[~s.index.duplicated()]
    jump = s.diff()
    rows = []
    for day in jump[jump >= 5e8].index:
        a, b = day + pd.Timedelta(days=1), day + pd.Timedelta(days=2)
        pa, pb = btc.get(day), btc.get(a)  # close of day = 00:00 next day
        if pa is None or pb is None:
            continue
        rows.append({"day": a, "ret": pb / pa - 1 - 2 * FEE})
    judge("#467 BTC", rows, "2023-01-01", "2020-01-01", "2026-11-01", 30, 0.003, 45000)


def main():
    print("===== Batch G (docs/PREREG_BATCH_G_20261126.md)")
    for fn in (part458, part459, part460, part461, part462, part463, part464, part465, part466, part467):
        fn()


if __name__ == "__main__":
    main()

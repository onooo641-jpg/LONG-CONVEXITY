"""Batch F (#448-#457), exactly as docs/PREREG_BATCH_F_20261126.md defines it.

    uv run python -m scripts.batch_f_20261126 | tee docs/jx_runs/batch_f_20261126.txt
"""
from __future__ import annotations

import datetime as dt
import json
import re

import numpy as np
import pandas as pd

from scripts.batch_d_20261126 import MARKETS, PUB, S1, S2, CAP, load, tstat, third_friday

FEE = 0.00045


def in_w(d, w):
    return (d >= w[0]) & (d < w[1])


# ------------------------------------------------------------------ futures helpers
def judge_futures(label, ev):
    """ev: DataFrame date, mkt, pts, price. Futures rule of the pre-registration."""
    print(f"\n#### {label}")
    if ev.empty:
        print("  no events")
        return
    ev = ev.copy()
    ev["net"] = ev["pts"] - ev["mkt"].map(lambda m: MARKETS[m][1])
    ev["pct"] = ev["net"] / ev["price"]
    res = {}
    for wname, w in (("S1", S1), ("S2", S2)):
        sub = ev[in_w(ev["date"], w)]
        yrs = (w[1] - w[0]).days / 365.25
        for m in MARKETS:
            x = sub[sub["mkt"] == m]
            if len(x) < 3:
                print(f"  {wname} {m:<3} n {len(x)}")
                continue
            print(f"  {wname} {m:<3} n {len(x):>4} ({len(x) / yrs:4.1f}/yr) mean net {x['net'].mean():8.3f} pts ({x['pct'].mean():.3%}) "
                  f"t {tstat(x['net']):5.2f} win {(x['net'] > 0).mean():.0%}")
            res[(wname, m)] = x["net"].mean()
        pooled = sub.groupby("date")["pct"].mean()
        print(f"  {wname} pooled: events {len(pooled)}, mean {pooled.mean():.3%}, t {tstat(pooled):.2f}")
        res[(wname, "pooled_t")] = tstat(pooled)
    if all(res.get(("S1", m), 1) <= 0 for m in ("NQ", "ES")):
        print("  STAGE 1 VERDICT: KILL")
        return
    print("  STAGE 1 VERDICT: survives (kill-only)")
    pos = sum(1 for m in MARKETS if res.get(("S2", m), -1) > 0)
    ok = pos >= 3 and res.get(("S2", "pooled_t"), 0) >= 2
    sub = ev[in_w(ev["date"], S2)].copy()
    k = sub.groupby("date")["mkt"].transform("count")
    sub["n"] = np.maximum(1, np.floor(CAP / k / (sub["price"] * sub["mkt"].map(lambda m: MARKETS[m][2]))))
    usd = (sub["net"] * sub["mkt"].map(lambda m: MARKETS[m][2]) * sub["n"]).sum() / ((S2[1] - S2[0]).days / 365.25)
    print(f"  Stage 2: markets with mean net > 0: {pos}/4; pooled t {res.get(('S2', 'pooled_t')):.2f}; ${usd:,.0f}/yr at 10x notional")
    print(f"  STAGE 2 VERDICT: {'PASS' if ok else 'FAIL'}")


def fred(sid):
    f = pd.read_parquet(PUB / "batchd_fred_cmt.parquet")
    f = f[f["sid"] == sid]
    return pd.Series(f["y"].to_numpy(), index=pd.to_datetime(f["date"]).dt.date).sort_index()


def month_last_idx(dates):
    s = pd.Series(range(len(dates)), index=dates)
    per = pd.Series([pd.Timestamp(d).to_period("M") for d in dates], index=dates)
    return {p: list(g.index) for p, g in s.groupby(per)}


def part450(tabs):
    y10 = fred("DGS10")
    rows = []
    for m, t in tabs.items():
        months = month_last_idx(list(t.index))
        keys = sorted(months)
        for a, b in zip(keys[:-1], keys[1:]):
            days = months[b]
            if len(days) < 6:
                continue
            prev_close_day, d4, dl = months[a][-1], days[-4], days[-1]
            if t.at[d4, "roll"] or t.at[dl, "roll"]:
                continue
            re_ = t.at[d4, 959] / t.at[prev_close_day, 959] - 1
            ya, yb = y10.asof(pd.Timestamp(prev_close_day).date()) if False else y10[:prev_close_day].iloc[-1], y10[:d4].iloc[-1]
            rb = -7.5 * (yb - ya) / 100
            s = re_ - rb
            if abs(s) <= 0.02:
                continue
            side = -np.sign(s)
            rows.append({"date": dl, "mkt": m, "pts": side * (t.at[dl, 959] - t.at[d4, 959]), "price": t.at[d4, 959]})
    judge_futures("#450 month-end pension rebalancing (|R_e - R_b| > 2% at day -4, trade against it to month-end)", pd.DataFrame(rows))


def part451():
    print("\n#### #451 Treasury month-end index extension (long duration, close of day -3 -> last day; FRED)")
    for sid in ("DGS10", "DGS30"):
        y = fred(sid).dropna()
        months = month_last_idx(list(y.index))
        rows = []
        for p, days in months.items():
            if len(days) < 4:
                continue
            a, b = days[-3], days[-1]
            rows.append({"date": b, "bp": -(y[b] - y[a]) * 100 - 0.5})
        r = pd.DataFrame(rows)
        r["date"] = pd.to_datetime(r["date"])
        for lab, lo, hi in (("Stage 1 1990-2009", "1990-01-01", "2010-01-01"), ("Stage 2 2010-2026-10", "2010-01-01", "2026-11-01")):
            x = r[(r["date"] >= lo) & (r["date"] < hi)]["bp"]
            print(f"  {sid} {lab}: months {len(x)}, mean net {x.mean():.2f} bp, t {tstat(x):.2f}, win {(x > 0).mean():.0%}")
        if sid == "DGS10":
            s1 = r[(r["date"] >= "1990-01-01") & (r["date"] < "2010-01-01")]["bp"]
            s2 = r[(r["date"] >= "2010-01-01") & (r["date"] < "2026-11-01")]["bp"]
            if s1.mean() <= 0:
                print("  STAGE 1 VERDICT (#451): KILL")
            else:
                ok = s2.mean() >= 0.5 and tstat(s2) >= 2
                print(f"  STAGE 1 VERDICT (#451): survives; STAGE 2 VERDICT: {'PASS' if ok else 'FAIL'}; "
                      f"${s2.mean() * 50 * 12:,.0f}/yr at DV01 $50")


def part452(tabs):
    rows = []
    for m, t in tabs.items():
        dates = list(t.index)
        ds = set(dates)
        for y in range(2010, 2027):
            for mo in range(1, 13):
                if mo in (3, 6, 9, 12):
                    continue
                opex = third_friday(y, mo)
                pre, post = opex - dt.timedelta(days=7), opex + dt.timedelta(days=7)
                if not all(d in ds for d in (pre, opex, post)):
                    continue
                if any(t.at[d, "roll"] for d in (pre, opex, post)):
                    continue
                pts = (t.at[opex, 959] - t.at[pre, 959]) - (t.at[post, 959] - t.at[opex, 959])
                rows.append({"date": post, "mkt": m, "pts": pts, "price": t.at[pre, 959], "_cost2": True})
    ev = pd.DataFrame(rows)
    if len(ev):
        ev["pts"] = ev["pts"] - ev["mkt"].map(lambda mm: MARKETS[mm][1])  # two round trips: one extra cost here, one in judge
    judge_futures("#452 OPEX week long + post-OPEX week short (non-quarterly months)", ev.drop(columns=["_cost2"], errors="ignore"))


def part455(tabs):
    rows = []
    for m, t in tabs.items():
        dates = list(t.index)
        for y in range(2010, 2027):
            for mo in range(1, 13):
                d15 = dt.date(y, mo, 15)
                before = [d for d in dates if d < d15 and d.year == y and d.month == mo]
                after = [d for d in dates if d >= d15 and d.year == y and d.month == mo]
                if not before or len(after) < 2:
                    continue
                a, b = before[-1], after[1]
                if t.at[a, "roll"] or t.at[b, "roll"]:
                    continue
                rows.append({"date": b, "mkt": m, "pts": t.at[b, 959] - t.at[a, 959], "price": t.at[a, 959]})
    judge_futures("#455 mid-month 401(k) contributions (long last day before the 15th -> 2nd day on/after)", pd.DataFrame(rows))


def part456(tabs):
    rows = []
    for m, t in tabs.items():
        dates = list(t.index)
        for y in range(2010, 2027):
            for mo in (3, 6, 9, 12):
                f = third_friday(y, mo)
                if f not in t.index:
                    continue
                nxt = [d for d in dates if d > f][:1]
                if not nxt or pd.isna(t.at[nxt[0], 599]):
                    continue
                side = -np.sign(t.at[f, 959] - t.at[f, 899])
                if side == 0:
                    continue
                rows.append({"date": f, "mkt": m, "pts": side * (t.at[nxt[0], 599] - t.at[f, 959]), "price": t.at[f, 959]})
    judge_futures("#456 quarterly index-rebalance close: fade 15:00->16:00 until 10:00 next day", pd.DataFrame(rows))


# ------------------------------------------------------------------ crypto / FX / equities
def binance_daily(sym):
    b = pd.read_parquet(PUB / "uncharted_389_binance_ohlc.parquet", columns=["sym", "t", "c"])
    b = b[b["sym"] == sym]
    s = pd.Series(b["c"].to_numpy(), index=pd.to_datetime(b["t"], unit="s", utc=True).dt.normalize()).sort_index()
    return s[~s.index.duplicated()]


def crypto_judge(tag, rows, split, s1_lo, s2_hi, n2, m2):
    r = pd.DataFrame(rows)
    if r.empty:
        print(f"  {tag}: no events")
        return
    s1 = r[(r["day"] >= s1_lo) & (r["day"] < split)]["ret"]
    s2 = r[(r["day"] >= split) & (r["day"] < s2_hi)]["ret"]
    print(f"  {tag} Stage 1: events {len(s1)}, mean {s1.mean():.2%}, t {tstat(s1):.2f}, win {(s1 > 0).mean():.0%}")
    print(f"  {tag} Stage 2: events {len(s2)}, mean {s2.mean():.2%}, t {tstat(s2):.2f}, win {(s2 > 0).mean():.0%}, worst {s2.min():.1%}")
    if not len(s1) or s1.mean() <= 0:
        print(f"  VERDICT ({tag}): KILL")
        return
    ok = len(s2) >= n2 and s2.mean() >= m2 and tstat(s2) >= 2
    yrs = (pd.Timestamp(s2_hi) - pd.Timestamp(split)).days / 365.25
    print(f"  VERDICT ({tag}): {'PASS' if ok else 'FAIL'} (Stage 1 survives); ${s2.sum() * 45000 / yrs:,.0f}/yr at $15K x3")


def part448():
    print("\n#### #448 stablecoin supply surges -> 7-day BTC/ETH")
    p = PUB / "batchf_stable_supply.parquet"
    if not p.exists():
        print("  data not fetched yet (ubatchf)")
        return
    s = pd.read_parquet(p)
    sup = pd.Series(s["supply"].to_numpy(), index=pd.to_datetime(s["t"], unit="s", utc=True).normalize()).sort_index()
    sup = sup[sup > 0]
    g = sup / sup.shift(7) - 1
    for sym, tag in (("BTCUSDT", "#448 BTC"), ("ETHUSDT", "#448 ETH (variant)")):
        px = binance_daily(sym)
        rows, busy = [], None
        for d in [x for x in px.index if x.weekday() == 0]:
            if busy is not None and d < busy:
                continue
            hist = g[(g.index < d) & (g.index >= d - pd.Timedelta(days=364))]
            gd = g.get(d - pd.Timedelta(days=1))
            if len(hist) < 300 or gd is None or pd.isna(gd):
                continue
            side = 1 if gd > hist.quantile(0.8) else (-1 if gd < hist.quantile(0.2) else 0)
            e = d + pd.Timedelta(days=7)
            if side == 0 or e not in px.index:
                continue
            rows.append({"day": d, "ret": side * (px[e] / px[d] - 1) - 2 * FEE})
            busy = e
        crypto_judge(tag, rows, "2023-01-01", "2020-01-01", "2026-11-01", 30, 0.005)


def part449():
    print("\n#### #449 US spot-ETF net flows -> next UTC day")
    for coin, sym, thr, tag in (("btc", "BTCUSDT", 200, "#449 BTC"), ("eth", "ETHUSDT", 50, "#449 ETH (variant)")):
        p = PUB / f"batchf_farside_{coin}.html"
        if not p.exists():
            print(f"  {tag}: Farside page not fetched")
            continue
        html = p.read_text(errors="replace")
        flows = {}
        for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", html, re.S):
            cells = [re.sub(r"<[^>]+>", "", c).strip() for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", tr, re.S)]
            if len(cells) < 3:
                continue
            try:
                day = pd.Timestamp(dt.datetime.strptime(cells[0], "%d %b %Y"), tz="UTC")
            except ValueError:
                continue
            tot = cells[-1].replace(",", "")
            neg = tot.startswith("(") and tot.endswith(")")
            tot = tot.strip("()")
            try:
                v = float(tot) * (-1 if neg else 1)
            except ValueError:
                continue
            flows[day] = v
        print(f"  {tag}: {len(flows)} flow days parsed")
        if not flows:
            continue
        px = binance_daily(sym)
        rows = []
        for d, f in sorted(flows.items()):
            if abs(f) < thr:
                continue
            a, b = d + pd.Timedelta(days=1), d + pd.Timedelta(days=2)
            # daily closes are 23:59 UTC; price at 00:00 of a = close of day d
            if d not in px.index or a not in px.index:
                continue
            rows.append({"day": d, "ret": np.sign(f) * (px[a] / px[d] - 1) - 2 * FEE})
        crypto_judge(tag, rows, "2025-01-01", "2024-01-01", "2026-11-01", 50, 0.002)


def part453():
    print("\n#### #453 USD/JPY gotobi Tokyo fix (long 00:00 -> 00:55 UTC)")
    p = PUB / "batchf_usdjpy_fix.parquet"
    if not p.exists():
        print("  data not fetched yet (ubatchf2)")
        return
    d = pd.read_parquet(p).dropna(subset=["p0000", "p0055"])
    d["day"] = pd.to_datetime(d["day"])
    got = set()
    for m in pd.period_range("2012-01", "2026-10", freq="M"):
        last = m.to_timestamp(how="end").normalize()
        for dd in [pd.Timestamp(m.year, m.month, k) for k in (5, 10, 15, 20, 25)] + [last]:
            while dd.weekday() >= 5:
                dd -= pd.Timedelta(days=1)
            got.add(dd.normalize())
    d["gotobi"] = d["day"].isin(got)
    d["pip"] = (d["p0055"] - d["p0000"]) * 100 - 0.3
    d["post"] = -(d["p0200"] - d["p0055"]) * 100 - 0.3
    for lab, lo, hi in (("Stage 1 2012-2018", "2012-01-01", "2019-01-01"), ("Stage 2 2019-2026-10", "2019-01-01", "2026-11-01")):
        x = d[(d["day"] >= lo) & (d["day"] < hi)]
        g, b = x[x["gotobi"]]["pip"], x[~x["gotobi"]]["pip"]
        w = (g.mean() - b.mean()) / np.sqrt(g.var(ddof=1) / len(g) + b.var(ddof=1) / len(b))
        print(f"  {lab}: gotobi {len(g)} mean net {g.mean():.2f} pip t {tstat(g):.2f} win {(g > 0).mean():.0%}; other days {b.mean():.2f} pip; "
              f"Welch {w:.2f}; post-fix short variant {x[x['gotobi']]['post'].mean():.2f} pip t {tstat(x[x['gotobi']]['post']):.2f}")
        if lo == "2012-01-01" and g.mean() <= 0:
            print("  STAGE 1 VERDICT (#453): KILL")
            return
        if lo == "2019-01-01":
            ok = g.mean() >= 0.5 and tstat(g) >= 2 and w >= 1.5
            print(f"  STAGE 1 survives; STAGE 2 VERDICT (#453): {'PASS' if ok else 'FAIL'}; "
                  f"${g.mean() / 100 / 150 * 150000 * len(g) / 7.8:,.0f}/yr at $150K")


def part454():
    print("\n#### #454 IPO lock-up expiry short (hedged with IWM)")
    ip, pp = PUB / "batchf_ipos.parquet", PUB / "batchf_ipo_px.parquet"
    if not ip.exists() or not pp.exists():
        print("  data not fetched yet (ubatchf3)")
        return
    ipo = pd.read_parquet(ip)
    px = pd.read_parquet(pp)
    px["day"] = pd.to_datetime(px["t"], unit="s", utc=True).dt.normalize()
    P = {s: g.drop_duplicates("day").set_index("day")["c"].sort_index() for s, g in px.groupby("sym")}
    iwm = P.get("IWM")
    num = lambda v: pd.to_numeric(str(v).replace("$", "").replace(",", ""), errors="coerce")  # noqa: E731
    rows = []
    for _, r in ipo.drop_duplicates("proposedTickerSymbol").iterrows():
        sym, price, size = r.get("proposedTickerSymbol"), num(r.get("proposedSharePrice")), num(r.get("dollarValueOfSharesOffered"))
        d0 = pd.to_datetime(r.get("pricedDate"), errors="coerce")
        if sym not in P or pd.isna(d0) or not (price >= 5) or not (size >= 50e6) or iwm is None:
            continue
        lock = (d0 + pd.Timedelta(days=180)).tz_localize("UTC")
        x = P[sym]
        after = x.index[x.index >= lock]
        before = x.index[x.index < lock]
        if len(after) == 0 or len(before) < 5:
            continue
        a, b = before[-5], after[0]
        if a not in iwm.index or b not in iwm.index:
            continue
        ret = -(x[b] / x[a] - 1) + (iwm[b] / iwm[a] - 1) - 4 * 0.001 - 0.30 * 6 / 252
        rows.append({"day": d0.tz_localize("UTC"), "ret": ret})
    r = pd.DataFrame(rows)
    print(f"  usable IPOs: {len(r)}")
    if r.empty:
        return
    s1 = r[(r["day"] >= "2016-01-01") & (r["day"] < "2020-01-01")]["ret"]
    s2 = r[(r["day"] >= "2020-01-01") & (r["day"] < "2026-05-01")]["ret"]
    print(f"  Stage 1 (IPOs 2016-19): n {len(s1)}, mean {s1.mean():.2%}, t {tstat(s1):.2f}, win {(s1 > 0).mean():.0%}")
    print(f"  Stage 2 (IPOs 2020-26-04): n {len(s2)}, mean {s2.mean():.2%}, t {tstat(s2):.2f}, win {(s2 > 0).mean():.0%}, worst {s2.min():.1%}")
    if not len(s1) or s1.mean() <= 0:
        print("  VERDICT (#454): KILL")
        return
    ok = len(s2) >= 100 and s2.mean() >= 0.005 and tstat(s2) >= 2
    print(f"  VERDICT (#454): {'PASS' if ok else 'FAIL'}; ${s2.sum() * 5000 / 6.33:,.0f}/yr at $5K per event")


def part457():
    print("\n#### #457 DVOL spike -> long 7 days (dealer hedge unwind)")
    raw = json.loads((PUB / "batcha_raw.json").read_text())
    for cur, sym, tag in (("BTC", "BTCUSDT", "#457 BTC"), ("ETH", "ETHUSDT", "#457 ETH (variant)")):
        dv = raw.get(f"dvol_{cur}") or []
        iv = pd.Series({pd.Timestamp(int(x[0]), unit="ms", tz="UTC").normalize(): float(x[4]) for x in dv}).sort_index()
        px = binance_daily(sym)
        med = iv.shift(1).rolling(20, min_periods=15).median()
        rows, busy = [], None
        for d, v in iv.items():
            if busy is not None and d < busy:
                continue
            if pd.isna(med.get(d)) or v - med[d] < 10:
                continue
            e = d + pd.Timedelta(days=7)
            if d not in px.index or e not in px.index:
                continue
            rows.append({"day": d, "ret": px[e] / px[d] - 1 - 2 * FEE})
            busy = e
        crypto_judge(tag, rows, "2024-01-01", "2021-03-01", "2026-11-01", 15, 0.01)


def main():
    print("===== Batch F (docs/PREREG_BATCH_F_20261126.md)")
    tabs = {m: load(m) for m in MARKETS}
    part450(tabs)
    part451()
    part452(tabs)
    part455(tabs)
    part456(tabs)
    part448()
    part449()
    part453()
    part454()
    part457()


if __name__ == "__main__":
    main()

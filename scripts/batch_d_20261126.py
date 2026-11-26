"""Batch D (#443-#446 + #440 alt variant) exactly as docs/PREREG_BATCH_D_20261126.md defines them.

    uv run python -m scripts.batch_d_20261126 | tee docs/jx_runs/batch_d_20261126.txt
"""
from __future__ import annotations

import datetime as dt

import numpy as np
import pandas as pd

from ict import data as D

PUB = D.REPO_ROOT / "data" / "public"
MARKETS = {"NQ": (None, 1.12, 2.0), "ES": ("ES", 0.748, 5.0), "YM": ("YM", 4.48, 0.5), "RTY": ("RTY", 0.448, 5.0)}
S1 = (dt.date(2010, 7, 1), dt.date(2016, 1, 1))
S2 = (dt.date(2016, 1, 1), dt.date(2026, 10, 29))
CAP = 150_000.0


def tstat(x):
    x = np.asarray(x, float)
    return float(x.mean() / (x.std(ddof=1) / np.sqrt(len(x)))) if len(x) > 2 and x.std(ddof=1) > 0 else float("nan")


def third_friday(y, m):
    d = dt.date(y, m, 15)
    return d + dt.timedelta(days=(4 - d.weekday()) % 7)


def roll_days(dates):
    dates = sorted(dates)
    out = set()
    for y in range(dates[0].year, dates[-1].year + 1):
        for mo in (3, 6, 9, 12):
            out.update([d for d in dates if d < third_friday(y, mo)][-10:])
    return out


def day_table(bars):
    m = bars["minutes_from_midnight"]
    keep = m.isin([599, 614, 899, 929, 944, 959])
    x = bars[keep].pivot_table(index="ny_date", columns="minutes_from_midnight", values="close", aggfunc="first")
    rth = bars[(m >= 570) & (m < 960)].groupby("ny_date")["minutes_from_midnight"].agg(["first", "last"])
    x = x.join(rth)
    x = x[(x["first"] == 570) & (x["last"] == 959)].dropna(subset=[899, 929, 959]).sort_index()
    x["prev"] = x[959].shift(1)
    x = x.dropna(subset=["prev"])
    roll = roll_days(list(x.index))
    x["roll"] = [d in roll for d in x.index]
    return x


def load(name):
    raw = MARKETS[name][0]
    bars = D.load("1m") if raw is None else D.add_time_columns(D.load_raw(f"{raw}_v_0_1m_*.parquet"))
    return day_table(bars)


def trades_443(t, thr=0.010, entry=929, mode="main"):
    x = t[~t["roll"]].copy()
    if mode == "gao":
        r = x[599] / x["prev"] - 1
        side = np.sign(r)
        ok = side != 0
    else:
        r = x[entry] / x["prev"] - 1
        side = np.sign(r)
        ok = r.abs() >= thr
    x = x[ok]
    side = side[ok]
    if mode == "reversal":
        nxt = t[599].shift(-1).reindex(x.index)
        pts = -side * (nxt - x[959])
    else:
        pts = side * (x[959] - x[entry])
    return pd.DataFrame({"date": x.index, "pts": pts.to_numpy(), "price": x[entry].to_numpy()}).dropna()


def trades_444(t, thr=0.05, same_day=False):
    x = t.copy()
    r = x[959] / x["prev"] - 1
    s20 = r.rolling(20).std()
    if same_day:
        r_part = x[899] / x["prev"] - 1
        vals = []
        rv = r.to_numpy()
        rp = r_part.to_numpy()
        for i in range(len(x)):
            if i < 21:
                vals.append(np.nan)
                continue
            a = np.std(np.r_[rv[i - 19:i], rp[i]], ddof=1)
            b = np.std(rv[i - 20:i], ddof=1)
            vals.append(a / b - 1)
        delta = pd.Series(vals, index=x.index)
    else:
        delta = s20.shift(1) / s20.shift(2) - 1
    side = pd.Series(np.where(delta >= thr, -1, np.where(delta <= -thr, 1, 0)), index=x.index)
    keep = (side != 0) & (~x["roll"]) & delta.notna()
    y = x[keep]
    pts = side[keep] * (y[959] - y[899])
    return pd.DataFrame({"date": y.index, "pts": pts.to_numpy(), "price": y[899].to_numpy()})


def in_w(d, w):
    return (d >= w[0]) & (d < w[1])


def summarize(label, per_mkt, stage_rule=True):
    """per_mkt: {mkt: trades df}. Prints stats, returns verdict dict."""
    print(f"\n#### {label}")
    res = {}
    for wname, w in (("S1 2010-07..2015", S1), ("S2 2016..2026-10", S2)):
        for mkt, tr in per_mkt.items():
            cost, ppt = MARKETS[mkt][1], MARKETS[mkt][2]
            sub = tr[in_w(tr["date"], w)]
            if len(sub) < 10:
                print(f"  {wname} {mkt:<3} n {len(sub)} (too few)")
                res[(wname, mkt)] = None
                continue
            net = sub["pts"] - cost
            yrs = (w[1] - w[0]).days / 365.25
            print(f"  {wname} {mkt:<3} n {len(sub):>5} ({len(sub) / yrs:5.1f}/yr)  mean net {net.mean():8.3f} pts  t {tstat(net):6.2f}  "
                  f"win {(net > 0).mean():.0%}  $/yr per micro {net.mean() * len(sub) / yrs * ppt:9,.0f}")
            res[(wname, mkt)] = (net.mean(), tstat(net))
    return res


def portfolio(per_mkt, mkts, w):
    """Equal split of the $150K notional cap across markets signalling that day; micros floored, min 1."""
    rows = []
    for mkt in mkts:
        tr = per_mkt[mkt]
        tr = tr[in_w(tr["date"], w)]
        cost, ppt = MARKETS[mkt][1], MARKETS[mkt][2]
        for d, p, px in zip(tr["date"], tr["pts"], tr["price"]):
            rows.append((d, mkt, (p - cost) * ppt, px * ppt))
    df = pd.DataFrame(rows, columns=["date", "mkt", "usd1", "notional1"])
    if df.empty:
        return df, pd.Series(dtype=float)
    k = df.groupby("date")["mkt"].transform("count")
    df["n"] = np.maximum(1, np.floor(CAP / k / df["notional1"]))
    df["usd"] = df["usd1"] * df["n"]
    yr = df.groupby(pd.to_datetime(df["date"]).dt.year)["usd"].sum()
    return df, yr


def verdict_futures(label, per_mkt):
    res = summarize(label, per_mkt)
    s1 = [res.get(("S1 2010-07..2015", m)) for m in ("NQ", "ES")]
    killed = all(v is not None and v[0] <= 0 for v in s1)
    print(f"  Stage 1 (kill if mean net <= 0 on both NQ and ES): {'KILL' if killed else 'survives'}")
    if killed:
        return "KILL"
    good = [m for m in MARKETS if (v := res.get(("S2 2016..2026-10", m))) is not None and v[0] > 0 and v[1] > 2]
    df, yr = portfolio(per_mkt, list(MARKETS), S2)
    yrs = (S2[1] - S2[0]).days / 365.25
    usd = df["usd"].sum() / yrs if len(df) else 0.0
    nq = per_mkt["NQ"]
    nq = nq[in_w(nq["date"], S2)]
    nq_yr = (nq["pts"] - MARKETS["NQ"][1]).groupby(pd.to_datetime(nq["date"]).dt.year).sum()
    print(f"  Stage 2: markets with mean>0 & t>2: {good}; portfolio (all 4, $150K cap) ${usd:,.0f}/yr; worst year ${yr.min():,.0f}; "
          f"NQ positive years {(nq_yr > 0).sum()}/{len(nq_yr)}")
    print("  portfolio by year: " + ", ".join(f"{y} ${v:,.0f}" for y, v in yr.items()))
    ok = len(good) >= 3 and usd >= 10_000 and yr.min() >= -5_000 and (nq_yr > 0).sum() >= 6
    print(f"  VERDICT: {'PASS' if ok else 'FAIL'}")
    return "PASS" if ok else "FAIL"


def part_futures():
    tabs = {m: load(m) for m in MARKETS}
    for m, t in tabs.items():
        print(f"  {m}: {len(t)} clean RTH days {t.index.min()}..{t.index.max()}", flush=True)
    v443 = verdict_futures("#443 LETF close rebalancing (|15:30 vs prev close| >= 1.0%, trade with it 15:30 -> close)",
                           {m: trades_443(t) for m, t in tabs.items()})
    print("\n  #443 variants (reported only):")
    for lab, kw in (("thr 0.5%", {"thr": 0.005}), ("thr 1.5%", {"thr": 0.015}), ("entry 15:45", {"entry": 944}),
                    ("Gao first-half-hour sign, every day", {"mode": "gao"}), ("next-morning reversal to 10:00", {"mode": "reversal"})):
        summarize(f"#443 variant: {lab}", {m: trades_443(t, **kw) for m, t in tabs.items()})
    v444 = verdict_futures("#444 vol-target de-leveraging (sigma20 change >= +/-5%, 15:00 -> close, short if vol rose)",
                           {m: trades_444(t) for m, t in tabs.items()})
    print("\n  #444 variants (reported only):")
    for lab, kw in (("thr 2%", {"thr": 0.02}), ("thr 10%", {"thr": 0.10}), ("same-day sigma incl. return to 15:00", {"same_day": True})):
        summarize(f"#444 variant: {lab}", {m: trades_444(t, **kw) for m, t in tabs.items()})
    return v443, v444


# ---------------------------------------------------------------- crypto / rates parts (data: job ubatchd)
FEE_HL = 0.0005


def _h1(name):
    p = PUB / name
    if not p.exists():
        return None
    d = pd.read_parquet(p)
    d["ts"] = pd.to_datetime(d["t"], unit="s", utc=True)
    return {s: g.drop_duplicates("ts").set_index("ts")["close"].sort_index() for s, g in d.groupby("sym")}


def _fund(name):
    p = PUB / name
    if not p.exists():
        return None
    d = pd.read_parquet(p)
    d["ts"] = pd.to_datetime(d["t"], unit="s", utc=True).dt.round("h")
    return {s: g.drop_duplicates("ts").set_index("ts")["rate"].sort_index() for s, g in d.groupby("sym")}


def _at(x, T):
    """Price at time T = close of the 1h bar opening at T - 1h."""
    return x.get(T - pd.Timedelta(hours=1))


def _wk_t(df, col="ret"):
    w = df.groupby(df["ts"].dt.to_period("W"))[col].mean()
    return tstat(w), len(w)


def _pair_trades(K, F, weekday):
    btc, fb = K.get("BTCUSDT"), (F or {}).get("BTCUSDT", pd.Series(dtype=float))
    rows = []
    for sym, x in K.items():
        if sym == "BTCUSDT":
            continue
        ft = (F or {}).get(sym, pd.Series(dtype=float))
        days = sorted({t.normalize() for t in x.index if t.weekday() == weekday})
        for d in days:
            a, b = d, d + pd.Timedelta(days=1)
            q = [_at(x, a), _at(x, b), _at(btc, a), _at(btc, b)]
            if any(v is None or not np.isfinite(v) for v in q):
                continue
            f_tok = ft[(ft.index > a) & (ft.index <= b)].sum()
            f_btc = fb[(fb.index > a) & (fb.index <= b)].sum()
            ret = -(q[1] / q[0] - 1) + (q[3] / q[2] - 1) + f_tok - f_btc - 4 * FEE_HL
            rows.append({"sym": sym, "ts": a, "ret": ret})
    return pd.DataFrame(rows)


def part445():
    print("\n#### #445 ve-token weekly epoch selling (short token / long BTC, Thu 00:00 -> Fri 00:00 UTC)")
    K, F = _h1("batchd_epoch_1h.parquet"), _fund("batchd_epoch_funding.parquet")
    if K is None or "BTCUSDT" not in K:
        print("  data not fetched yet (job ubatchd)")
        return
    print("  coverage: " + ", ".join(f"{s} {x.index.min().date()}..{x.index.max().date()}" for s, x in K.items()))
    ev = _pair_trades(K, F, 3)
    base = pd.concat([_pair_trades(K, F, wd) for wd in (0, 1, 2, 4, 5, 6)], ignore_index=True)
    s1, s2 = ev[ev["ts"] < "2024-01-01"], ev[(ev["ts"] >= "2024-01-01") & (ev["ts"] < "2026-11-01")]
    b2 = base[(base["ts"] >= "2024-01-01") & (base["ts"] < "2026-11-01")]
    t1, _ = _wk_t(s1) if len(s1) else (np.nan, 0)
    print(f"  Stage 1 (..2023): events {len(s1)}, mean {s1['ret'].mean():.3%}, week-clustered t {t1:.2f}")
    if len(s1) == 0 or s1["ret"].mean() <= 0:
        print("  STAGE 1 VERDICT (#445): KILL")
        return
    print("  STAGE 1 VERDICT (#445): survives (kill-only)")
    t2, nw = _wk_t(s2)
    welch = (s2["ret"].mean() - b2["ret"].mean()) / np.sqrt(s2["ret"].var(ddof=1) / len(s2) + b2["ret"].var(ddof=1) / len(b2))
    by_tok = s2.groupby("sym")["ret"].mean()
    yrs = (pd.Timestamp("2026-11-01", tz="UTC") - pd.Timestamp("2024-01-01", tz="UTC")).days / 365.25
    usd = s2["ret"].sum() * 5000 / yrs
    print(f"  Stage 2 (2024..2026-10): events {len(s2)} ({nw} weeks), mean {s2['ret'].mean():.3%}, week t {t2:.2f}, "
          f"vs other weekdays (mean {b2['ret'].mean():.3%}) Welch t {welch:.2f}, ${usd:,.0f}/yr at $5K per token-leg")
    print("  by token: " + ", ".join(f"{k} {v:.2%}" for k, v in by_tok.items()))
    ok = s2["ret"].mean() >= 0.003 and t2 >= 2 and welch >= 1.5 and (by_tok > 0).sum() >= 4 and usd >= 10_000
    print(f"  STAGE 2 VERDICT (#445): {'PASS (pending verification V on Hyperliquid)' if ok else 'FAIL'}")
    pre = _pair_trades(K, F, 2)
    pre2 = pre[(pre["ts"] >= "2024-01-01") & (pre["ts"] < "2026-11-01")]
    if len(pre2):
        print(f"  variant pre-epoch (Wed->Thu, short) 2024..2026-10: events {len(pre2)}, mean {pre2['ret'].mean():.3%}, week t {_wk_t(pre2)[0]:.2f}")


TERM_SID = {2: "DGS2", 3: "DGS3", 5: "DGS5", 7: "DGS7", 10: "DGS10", 20: "DGS20", 30: "DGS30"}


def part446():
    print("\n#### #446 US Treasury auction concession (short A-5 -> A, long A -> A+5; FRED CMT; 1.0 bp costs)")
    fp, ap = PUB / "batchd_fred_cmt.parquet", PUB / "batchd_auctions.parquet"
    if not fp.exists() or not ap.exists():
        print("  data not fetched yet (job ubatchd)")
        return
    fr = pd.read_parquet(fp)
    fr["date"] = pd.to_datetime(fr["date"]).dt.date
    Y = {s: g.drop_duplicates("date").set_index("date")["y"].sort_index() for s, g in fr.groupby("sid")}
    a = pd.read_parquet(ap)
    print(f"  auctions rows {len(a)}; columns: {', '.join(a.columns[:30])}")
    col = lambda *names: next((c for c in names if c in a.columns), None)  # noqa: E731
    c_type, c_term = col("security_type"), col("original_security_term", "security_term")
    c_date, c_tips, c_frn = col("auction_date"), col("inflation_index_security", "tips"), col("floating_rate", "frn")
    a = a[a[c_type].isin(["Note", "Bond"])]
    if c_tips:
        a = a[a[c_tips].str.lower() != "yes"]
    if c_frn:
        a = a[a[c_frn].str.lower() != "yes"]
    a = a.assign(term=a[c_term].str.extract(r"^(\d+)-Year")[0].astype(float), A=pd.to_datetime(a[c_date], errors="coerce").dt.date)
    a = a[a["term"].isin(TERM_SID.keys())].dropna(subset=["A"]).drop_duplicates(["A", "term"])
    rows = []
    for _, e in a.iterrows():
        y = Y.get(TERM_SID[int(e["term"])])
        if y is None or e["A"] not in y.index:
            continue
        i = y.index.get_loc(e["A"])
        if i < 5 or i + 5 >= len(y):
            continue
        pre, post = (y.iloc[i] - y.iloc[i - 5]) * 100, (y.iloc[i + 5] - y.iloc[i]) * 100
        rows.append({"A": e["A"], "term": int(e["term"]), "pre": pre, "post": post, "net": pre - post - 1.0,
                     "start": y.index[i - 5], "end": y.index[i + 5]})
    t = pd.DataFrame(rows).sort_values("A")
    t["ts"] = pd.to_datetime(t["A"])
    print(f"  events {len(t)} ({t['A'].min()}..{t['A'].max()}); by term: {dict(t['term'].value_counts().sort_index())}")
    s1 = t[(t["ts"] >= "2009-01-01") & (t["ts"] < "2017-01-01")]
    s2 = t[(t["ts"] >= "2017-01-01") & (t["ts"] < "2026-11-01")]
    t1, _ = _wk_t(s1, "net")
    print(f"  Stage 1 (2009-2016): events {len(s1)}, mean net {s1['net'].mean():.2f} bp (pre {s1['pre'].mean():.2f}, post {s1['post'].mean():.2f}), "
          f"week t {t1:.2f}")
    if s1["net"].mean() <= 0 or t1 < 1:
        print("  STAGE 1 VERDICT (#446): KILL")
        return
    print("  STAGE 1 VERDICT (#446): survives (kill-only)")
    t2, nw = _wk_t(s2, "net")
    kept, active = [], []
    for _, e in s2.iterrows():
        active = [x for x in active if x > e["start"]]
        if len(active) < 3:
            kept.append(e)
            active.append(e["end"])
    k = pd.DataFrame(kept)
    yr = (k["net"] * 50).groupby(k["ts"].dt.year).sum()
    years_pos = (s2.groupby(s2["ts"].dt.year)["net"].mean() > 0).sum()
    usd = yr.sum() / ((pd.Timestamp("2026-11-01") - pd.Timestamp("2017-01-01")).days / 365.25)
    print(f"  Stage 2 (2017-2026-10): events {len(s2)} ({nw} weeks), mean net {s2['net'].mean():.2f} bp (pre {s2['pre'].mean():.2f}, "
          f"post {s2['post'].mean():.2f}), week t {t2:.2f}, positive years {years_pos}/10")
    print(f"  sized (DV01 $50, <= 3 overlapping, {len(k)} trades): ${usd:,.0f}/yr; by year " + ", ".join(f"{y} ${v:,.0f}" for y, v in yr.items()))
    ok = s2["net"].mean() >= 1.0 and t2 >= 2 and years_pos >= 6 and usd >= 10_000 and yr.min() >= -5_000
    print(f"  STAGE 2 VERDICT (#446): {'PASS' if ok else 'FAIL'}")
    for lab, c in (("PRE leg alone", s2["pre"] - 0.5), ("POST leg alone (long)", -s2["post"] - 0.5)):
        print(f"  variant {lab}: mean {c.mean():.2f} bp, t {tstat(c):.2f}")
    ten = s2[s2["term"] == 10]
    if len(ten) > 2:
        print(f"  variant 10-year only: events {len(ten)}, mean net {ten['net'].mean():.2f} bp, t {tstat(ten['net']):.2f}")


def part440alt():
    print("\n#### #440 alt-coin variant (40 Binance perps, #440's exact rule; t clustered by settlement time)")
    K, F = _h1("batchd_alts_1h.parquet"), _fund("batchd_alts_funding.parquet")
    if K is None or F is None:
        print("  data not fetched yet (job ubatchd)")
        return
    rows = []
    for sym, x in K.items():
        f = F.get(sym)
        if f is None:
            continue
        for ts, last in f.shift(1).dropna().items():
            if abs(last) < 0.0003:
                continue
            pa, pb = _at(x, ts - pd.Timedelta(hours=2)), _at(x, ts + pd.Timedelta(hours=1))
            if pa is None or pb is None:
                continue
            side = -1 if last > 0 else 1
            rows.append({"sym": sym, "ts": ts, "ret": side * (pb / pa - 1) - 2 * 0.00045})
    t = pd.DataFrame(rows)
    for lab, lo, hi, s2 in (("Stage 1 2021-2022", "2021-01-01", "2023-01-01", False), ("Stage 2 2023-2026-10", "2023-01-01", "2026-11-01", True)):
        x = t[(t["ts"] >= lo) & (t["ts"] < hi)]
        if x.empty:
            print(f"  {lab}: no events")
            continue
        g = x.groupby("ts")["ret"].mean()
        print(f"  {lab}: events {len(x)} ({x['sym'].nunique()} symbols, {len(g)} settlement times), mean {x['ret'].mean():.3%}, "
              f"settlement-clustered t {tstat(g):.2f}, win {(x['ret'] > 0).mean():.0%}")
        if not s2:
            killed = x["ret"].mean() < 0.0005 or tstat(g) < 1
            print(f"  STAGE 1 VERDICT (#440 alt): {'KILL' if killed else 'survives (kill-only)'}")
            if killed:
                return
        else:
            ok = len(x) >= 100 and x["ret"].mean() >= 0.0008 and tstat(g) >= 2
            print(f"  STAGE 2 VERDICT (#440 alt): {'PASS' if ok else 'FAIL'}")


def main():
    print("===== Batch D (docs/PREREG_BATCH_D_20261126.md)")
    part_futures()
    for fn in ("part445", "part446", "part440alt"):
        f = globals().get(fn)
        if f:
            f()


if __name__ == "__main__":
    main()

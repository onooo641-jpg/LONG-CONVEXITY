"""Batch 10 Stage 1 (docs/PREREG_BATCH10_20261122.md): #300/#314 stock- and index-perp funding carry, #301 dividend gap, #302 weekend gap,
#303 index additions, #304 unlocks, #305/#306 redemption-floor and cooldown discounts, #307/#308 Upbit notices.

    uv run python -m scripts.batch10_20261122 | tee docs/jx_runs/batch10_20261122.txt
"""
from __future__ import annotations

import json
import os
import re
import sys

import numpy as np
import pandas as pd

P0, P1 = pd.Timestamp("2026-08-01", tz="UTC"), pd.Timestamp("2026-11-01", tz="UTC")
R8 = json.load(open("data/public/batch8_raw.json"))
R10 = json.load(open("data/public/batch10_raw.json")) if os.path.exists("data/public/batch10_raw.json") else {}
if os.path.exists("data/public/batch10b_raw.json"):  # remainder fetched after the GeckoTerminal crash
    R10.update(json.load(open("data/public/batch10b_raw.json")))
INDEX = {"US500", "USA500", "USTECH", "SMALL2000", "XYZ100", "JP225", "KR200"}
NONSTOCK = INDEX | {"GOLD", "SILVER", "CL", "COPPER", "NATGAS", "JPY", "EUR", "USBOND", "XMR", "URNM", "EWY"}
#: names whose shares are listed on a US exchange (the registered rule hedges the perp 1:1 with shares; pre-IPO / private / non-US names
#: such as ANTH, UNITREE, TREAD, SMSN, SOFTBANK cannot be hedged at a retail broker and are outside the rule)
HEDGEABLE = {"TSLA", "NVDA", "HOOD", "INTC", "PLTR", "COIN", "META", "AAPL", "MSFT", "ORCL", "GOOGL", "AMZN", "AMD", "MU", "SNDK", "MSTR", "CRCL",
             "NFLX", "COST", "TSM", "RIVN", "BABA", "GME", "GDX"}
ann = lambda s: float(s.mean() * 365 * 100) if len(s) else float("nan")  # noqa: E731


def stage1(label, v, n, extra=""):
    verdict = "not testable (no pilot data)" if not n else ("KILL -> FAIL (Stage 1)" if not v > 0 else "continue to Stage 2")
    return f"{label}: {extra} -> {verdict}"


def funding_panel():
    rows = []
    for k, v in R8.items():
        if k.startswith("hip3|") and v:
            nm = k.split("|")[1]
            rows += [(nm, pd.Timestamp(int(x["time"]), unit="ms", tz="UTC").floor("h"), float(x["fundingRate"]), float(x.get("premium") or 0)) for x in v]
    d = pd.DataFrame(rows, columns=["coin", "t", "rate", "prem"]).drop_duplicates(["coin", "t"])
    return d


def carry(label, d, kill=4.0):
    H = d.pivot(index="t", columns="coin", values="rate").sort_index()
    days = pd.date_range(max(H.index.min().floor("D") + pd.Timedelta(days=8), pd.Timestamp("2026-07-09", tz="UTC")), P1 - pd.Timedelta(days=1), freq="D")
    out, prev = [], set()
    for dd in days:
        tr = H.loc[dd - pd.Timedelta(days=7):dd - pd.Timedelta(hours=1)]
        sc = tr.mean().abs().dropna()
        sc = sc[tr.notna().sum() >= 72]
        pick = list(sc.sort_values(ascending=False).index[:5])
        sign = np.sign(tr[pick].mean())
        today = H.loc[dd:dd + pd.Timedelta(hours=23), pick]
        earn = float((today.fillna(0).sum() * sign).mean()) if pick else 0.0  # receive side, per unit notional
        ch = len(set(pick) ^ prev)
        prev = set(pick)
        cost = ch / max(len(pick), 1) * 4 * 0.0005  # each change: open + close, two legs (shares + perp)
        out.append((dd, (earn - cost) / (4 / 3)))
    s = pd.Series(dict(out))
    p = s[(s.index >= P0) & (s.index < P1)]
    v = ann(p)
    print(f"{label}: {H.shape[1]} markets; Stage 1 2026-08..10 {v:.2f}%/yr on capital ({len(p)} days) -> "
          f"{'KILL -> FAIL (Stage 1)' if not v >= kill else 'continue to Stage 2'}")
    last = H.loc[P1 - pd.Timedelta(days=7):P1].mean().abs().sort_values(ascending=False).head(5) * 24 * 365 * 100
    print("  last-week top funding (annualised %): " + ", ".join(f"{k} {x:.1f}" for k, x in last.items()) + "\n")


def yahoo(t):
    y = R10.get(f"yahoo|{t}")
    if not y or not (y.get("chart") or {}).get("result"):
        return None, {}
    r = y["chart"]["result"][0]
    ts = pd.to_datetime(r["timestamp"], unit="s", utc=True)
    q = r["indicators"]["quote"][0]
    df = pd.DataFrame({"open": q["open"], "close": q["close"]}, index=ts)
    df.index = df.index.tz_convert("America/New_York").normalize()
    divs = {pd.Timestamp(int(k), unit="s", tz="UTC").tz_convert("America/New_York").normalize(): v["amount"]
            for k, v in ((r.get("events") or {}).get("dividends") or {}).items()}
    return df, divs


def p301(fp):
    ev = []
    for nm in sorted(fp.coin.unique()):
        dex, tk = nm.split(":")
        if tk in NONSTOCK:
            continue
        px, divs = yahoo(tk)
        if px is None:
            continue
        g = fp[fp.coin == nm].set_index("t")
        for exd, D in divs.items():
            if not (pd.Timestamp("2026-07-02", tz="America/New_York") <= exd < pd.Timestamp("2026-11-01", tz="America/New_York")):
                continue
            prior = px.index[px.index < exd]
            if not len(prior) or exd not in px.index:
                continue
            p0 = float(px.loc[prior[-1], "close"])
            t0 = (prior[-1] + pd.Timedelta(hours=16)).tz_convert("UTC")
            t1 = (exd + pd.Timedelta(hours=16)).tz_convert("UTC")
            w = g.loc[t0:t1]
            if len(w) < 12:
                continue
            fund_paid = float(-w["rate"].sum())  # short receives positive funding
            dprem = float(w["prem"].iloc[-1] - w["prem"].iloc[0])  # short loses if premium rises
            net = 0.7 * D / p0 - 4 * 0.0005 - fund_paid - dprem
            ev.append((nm, exd.date(), D / p0 * 100, net * 100))
    if not ev:
        print("#301 dividend gap: no ex-dates with perp data -> not testable (no data)\n")
        return
    e = pd.DataFrame(ev, columns=["perp", "ex", "yield_pct", "net_pct"])
    print(f"#301 dividend gap: {len(e)} ex-dates; mean net per event {e.net_pct.mean():.3f}% (median {e.net_pct.median():.3f}%) -> "
          f"{'KILL -> FAIL (Stage 1)' if not e.net_pct.mean() > 0 else 'continue to Stage 2'}")
    print("  " + e.sort_values("net_pct").to_string(index=False).replace("\n", "\n  ") + "\n")


def p302():
    rows = []
    for k, v in R10.items():
        if not k.startswith("hip3c|") or not v:
            continue
        nm = k.split("|")[1]
        if nm.split(":")[1] in NONSTOCK - INDEX:
            continue
        c = pd.DataFrame(v, columns=["t", "o", "c"])
        c.index = pd.to_datetime(c.t, unit="ms", utc=True).dt.tz_convert("America/New_York")
        for fri in c.index.normalize().unique():
            if fri.weekday() != 4 or not (P0.tz_convert("America/New_York") <= fri < P1.tz_convert("America/New_York")):
                continue
            f16 = c.loc[fri + pd.Timedelta(hours=15):fri + pd.Timedelta(hours=15, minutes=59)]
            mon = fri + pd.Timedelta(days=3)
            m9 = c.loc[mon + pd.Timedelta(hours=9):mon + pd.Timedelta(hours=9, minutes=59)]
            m10 = c.loc[mon + pd.Timedelta(hours=10):mon + pd.Timedelta(hours=10, minutes=59)]
            if not (len(f16) and len(m9) and len(m10)):
                continue
            mv = m9.o.iloc[0] / f16.c.iloc[-1] - 1
            if abs(mv) > 0.01:
                rows.append((nm, mon.date(), mv * 100, (-np.sign(mv) * (m10.o.iloc[0] / m9.o.iloc[0] - 1) - 0.001) * 100))
    if not rows:
        print("#302 weekend gap: no candle data -> not testable (no data)\n")
        return
    e = pd.DataFrame(rows, columns=["perp", "monday", "weekend_move_pct", "fade_net_pct"])
    print(f"#302 weekend gap (fade > 1% weekend moves, 09:00-10:00 ET Monday): {len(e)} trades; mean {e.fade_net_pct.mean():.3f}% per trade, "
          f"hit rate {(e.fade_net_pct > 0).mean():.0%} -> {'KILL -> FAIL (Stage 1)' if not e.fade_net_pct.mean() > 0 else 'continue to Stage 2'}\n")


def p303():
    wt = R10.get("wiki_sp500", "")
    if not wt:
        print("#303 index additions: no Wikipedia data -> not testable\n")
        return
    # The wikitext has no "Selected changes" table; additions are read from the constituents table's "Date added" column (current members
    # only: a stock added and removed again inside the window is missed).
    ev = []
    for row in wt.split("|-")[1:]:
        sym = re.search(r"\{\{(?:NyseSymbol|NasdaqSymbol|Nyse|Nasdaq|Ticker|BZX link|NYSE American link)[^|}]*\|([A-Z.]+)", row)
        dt = re.search(r"\|\|\s*(\d{4}-\d{2}-\d{2})\s", row)
        if sym and dt:
            ev.append((pd.Timestamp(dt.group(1)), sym.group(1)))
    spy, _ = yahoo("SPY")
    res = []
    for d, tk in ev:
        if not (pd.Timestamp("2024-11-01") <= d < pd.Timestamp("2026-11-01")):
            continue
        px, _ = yahoo(tk)
        if px is None or spy is None:
            continue
        dd = pd.Timestamp(d, tz="America/New_York")
        idx = px.index[px.index <= dd]
        if len(idx) < 6:
            continue
        t0, t1 = idx[-6], idx[-1]
        if t0 not in spy.index or t1 not in spy.index:
            continue
        r = px.at[t1, "close"] / px.at[t0, "close"] - spy.at[t1, "close"] / spy.at[t0, "close"] - 0.001
        res.append((tk, d.date(), r * 100))
    if not res:
        print(f"#303 index additions: {len(ev)} constituent rows parsed, no priced events in 2024-11..2026-10 -> not testable (data)\n")
        return
    e = pd.DataFrame(res, columns=["ticker", "effective", "excess_pct"])
    print(f"#303 S&P 500 additions (t-5 -> effective close, vs SPY, 10 bps): {len(e)} events; mean excess {e.excess_pct.mean():.3f}% "
          f"(median {e.excess_pct.median():.3f}%) -> {'KILL -> FAIL (Stage 1)' if not e.excess_pct.mean() > 0.2 else 'continue to Stage 2'}\n")


def p304():
    ok = any(v not in (None, "large") for k, v in R10.items() if k.startswith("emissions|"))
    print(f"#304 token-unlock shorts: unlock calendar {'answered (parser to be registered by addendum)' if ok else 'did not answer'} -> "
          f"{'pending addendum' if ok else 'not testable (no data)'}\n")


def floor(label, keys, fee, gain_frac=0.5, kill=6.0):
    lows = []
    for k, v in R10.items():
        if k.startswith("gecko|") and k.split("|")[1] in keys and v.get("ohlcv"):
            o = pd.DataFrame(v["ohlcv"], columns=["t", "o", "h", "l", "c", "v"])
            o["d"] = pd.to_datetime(o.t, unit="s", utc=True).dt.floor("D")
            if o.c.median() > 2 or o.c.median() < 0.5:  # quote orientation inverted or not a $1 pool
                o[["o", "h", "l", "c"]] = 1 / o[["o", "l", "h", "c"]].values if o.c.median() > 2 else o[["o", "h", "l", "c"]]
            lows.append(o.set_index("d")["l"].rename(k))
    if not lows:
        print(f"{label}: no pool data -> not testable (no data)\n")
        return
    L = pd.concat(lows, axis=1).min(axis=1)
    L = L[(L.index >= P0) & (L.index < P1)]
    gain = ((1 - fee - L).clip(lower=0) * gain_frac)
    tot = 4.0 + gain.sum() * 365 / max(len(L), 1) * 100
    print(f"{label}: {len(L)} days; days with low < $1 - {fee * 100:.1f}%: {(L < 1 - fee).sum()}; deepest low {L.min():.4f}; "
          f"total {tot:.2f}%/yr (4% park + half-capture) -> {'KILL -> FAIL (Stage 1)' if not tot >= kill else 'continue to Stage 2'}\n")


def p306():
    v = R10.get("susde_value") or {}
    vals = (((v.get("coins") or {}).get("ethereum:0x9d39a5de30e57443bff2a8307a4256c8797a3497") or {}).get("prices") or [])
    if not vals:
        print("#306 sUSDe cooldown discount: no reference value -> not testable (no data)\n")
        return
    ref = pd.Series({pd.Timestamp(x["timestamp"], unit="s", tz="UTC").floor("D"): x["price"] for x in vals})
    lows = []
    for k, d in R10.items():
        if k.startswith("gecko|sUSDe") and d.get("ohlcv"):
            o = pd.DataFrame(d["ohlcv"], columns=["t", "o", "h", "l", "c", "v"])
            o["d"] = pd.to_datetime(o.t, unit="s", utc=True).dt.floor("D")
            s = o.set_index("d")["l"]
            if s.median() < 0.5:
                s = 1 / o.set_index("d")["h"]
            lows.append((s / ref.reindex(s.index)).rename(k))
    if not lows:
        print("#306 sUSDe cooldown discount: no pool data -> not testable (no data)\n")
        return
    L = pd.concat(lows, axis=1).min(axis=1)
    L = L[(L.index >= P0) & (L.index < P1)].dropna()
    gain = ((1 - 0.003 - L).clip(lower=0) * 0.5)
    tot = 4.0 + gain.sum() * 365 / max(len(L), 1) * 100
    print(f"#306 sUSDe cooldown discount: {len(L)} days; days below value - 0.3%: {(L < 0.997).sum()}; deepest {L.min():.4f}; total {tot:.2f}%/yr "
          f"-> {'KILL -> FAIL (Stage 1)' if not tot >= 6 else 'continue to Stage 2'}\n")


def p307_308():
    notes = R10.get("upbit_notices") or []
    if not notes:
        print("#307 / #308 Upbit notices: did not answer -> not testable (no data)\n")
        return
    hl = {k.split("|")[1]: pd.DataFrame(v, columns=["t", "o", "c"]).assign(ts=lambda x: pd.to_datetime(x.t, unit="ms", utc=True)).set_index("ts")
          for k, v in R10.items() if k.startswith("hlc|") and v}
    btc = hl.get("BTC")
    res = {"list": [], "warn": []}
    for n in notes:
        title = str(n.get("title", ""))
        t = pd.to_datetime(n.get("listed_at") or n.get("first_listed_at") or n.get("created_at"), utc=True, errors="coerce")
        if t is pd.NaT or not (pd.Timestamp("2026-07-01", tz="UTC") <= t < P1):
            continue
        kind = "list" if re.search(r"KRW|마켓 디지털 자산 추가|신규 거래지원|추가", title) and not re.search(r"유의|종료|warning|delist", title, re.I) else \
               ("warn" if re.search(r"유의|종료|warning|delist", title, re.I) else None)
        if not kind:
            continue
        for sym in re.findall(r"\(([A-Z0-9]{2,10})\)", title):
            c = hl.get(sym)
            if c is None:
                continue
            a = c.c[c.index >= t + pd.Timedelta(hours=1)]
            hold = 24 if kind == "list" else 72
            b = c.c[c.index >= t + pd.Timedelta(hours=1 + hold)]
            if not len(a) or not len(b):
                continue
            r = b.iloc[0] / a.iloc[0] - 1
            res[kind].append((sym, t.date(), ((r if kind == "list" else -r) - 0.001) * 100))
    for kind, lab in (("list", "#307 listing drift (long +1h -> +25h)"), ("warn", "#308 warning/delist shorts (+1h -> +73h)")):
        e = pd.DataFrame(res[kind], columns=["coin", "date", "net_pct"])
        if e.empty:
            print(f"{lab}: no matched events with HL perps -> not testable (no data)")
            continue
        print(f"{lab}: {len(e)} events; mean {e.net_pct.mean():.2f}%, median {e.net_pct.median():.2f}%, hit {(e.net_pct > 0).mean():.0%} -> "
              f"{'KILL -> FAIL (Stage 1)' if not e.net_pct.mean() > 0 else 'continue to Stage 2'}")
    print()


def main() -> int:
    print("Stage 1 pilots, kill-only (docs/PREREG_BATCH10_20261122.md)\n")
    fp = funding_panel()
    carry("#300 stock-perp funding carry (HIP-3, US-listed shares only: the registered 1:1 share hedge)", fp[fp.coin.str.split(":").str[1].isin(HEDGEABLE)])
    carry("  (context, not tradeable as registered) all single-name perps incl. pre-IPO / non-US", fp[~fp.coin.str.split(":").str[1].isin(NONSTOCK)])
    carry("#314 index-perp funding carry (HIP-3 index names)", fp[fp.coin.str.split(":").str[1].isin(INDEX)])
    if not R10:
        print("(batch-10 data not yet fetched: #301-#308 pending)")
        return 0
    p301(fp)
    p302()
    p303()
    p304()
    floor("#305 redemption-floor stables (LUSD, BOLD, feUSD)", {"LUSD", "BOLD", "feUSD"}, 0.005)
    p306()
    p307_308()
    return 0


if __name__ == "__main__":
    sys.exit(main())

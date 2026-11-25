"""Wave 3 tests #392-#401 (docs/PREREG_UNCHARTED_WAVE3_20261125.md).

    uv run python -m scripts.uncharted_wave3_20261125 | tee docs/jx_runs/uncharted_wave3_20261125.txt
Reads data/public/uncharted_385_candles.parquet (Hyperliquid daily), hl_funding.parquet, uncharted_389_binance_ohlc.parquet and the
uncharted_w3_* files from Actions job uwave3. A part whose data file is missing prints "data not fetched".
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

PUB = Path(__file__).resolve().parent.parent / "data" / "public"
FEE = 0.00045
W_START, W_END = pd.Timestamp("2023-06-01", tz="UTC"), pd.Timestamp("2026-10-31", tz="UTC")


def load_hl():
    cd = pd.read_parquet(PUB / "uncharted_385_candles.parquet")
    cd["day"] = pd.to_datetime(cd["t"], unit="ms", utc=True).dt.normalize()
    cd = cd.drop_duplicates(["coin", "day"])
    C = cd.pivot(index="day", columns="coin", values="c").sort_index()
    fu = pd.read_parquet(PUB / "hl_funding.parquet")
    fu["day"] = pd.to_datetime(fu["time"], unit="ms", utc=True).dt.normalize()
    F = fu.groupby(["day", "coin"])["rate"].sum().unstack()
    return cd, C, F, cd.groupby("coin")["day"].min()


def hl_name(tok, cols):
    tok = tok.upper().strip()
    if tok in cols:
        return tok
    m = re.match(r"^(1000000|1000)(.+)$", tok)
    if m and ("k" + m.group(2)) in cols:
        return "k" + m.group(2)
    if ("k" + tok) in cols:
        return "k" + tok
    return None


def event_short(ev, H, C, F, first, min_age=7, max_delay=0, long_coin=None):
    """ev: DataFrame(day, token[, label]). Short token (or long `long_coin` vs BTC) from the event-day close for H days, BTC hedge."""
    rows = []
    for _, e in ev.iterrows():
        coin = long_coin or hl_name(e["token"], C.columns)
        if coin is None or coin == "BTC":
            continue
        d0 = e["day"]
        entry = None
        for k in range(max_delay + 1):
            d = d0 + pd.Timedelta(days=k)
            if d in C.index and pd.notna(C.at[d, coin]) and (max_delay == 0 or d > first.get(coin, d)):
                entry = d
                break
        if entry is None or (min_age and first.get(coin, entry) > entry - pd.Timedelta(days=min_age)):
            continue
        ex = entry + pd.Timedelta(days=H)
        if ex not in C.index or pd.isna(C.at[ex, coin]):
            continue
        p0, p1, b0, b1 = C.at[entry, coin], C.at[ex, coin], C.at[entry, "BTC"], C.at[ex, "BTC"]
        win = F.loc[entry + pd.Timedelta(days=1):ex]
        fc = float(win[coin].sum()) if coin in win else 0.0
        fb = float(win["BTC"].sum()) if "BTC" in win else 0.0
        sign = 1 if long_coin else -1  # long_coin: long the coin, short BTC
        ret = sign * (p1 / p0 - 1) - sign * (b1 / b0 - 1) - sign * fc + sign * fb - 4 * FEE
        rows.append({"day": entry.date(), "coin": coin, "ret": ret, "coin_move": p1 / p0 - 1, "btc_move": b1 / b0 - 1,
                     "label": e.get("label", "")})
    return pd.DataFrame(rows).drop_duplicates(["day", "coin"]) if rows else pd.DataFrame()


def verdict_e(t, label, n_min=15, mean_min=0.01):
    print(f"\n#### {label}: events {len(t)}")
    if t.empty:
        print("  STAGE 1 VERDICT: not testable (no events)")
        return
    r = t["ret"]
    n = len(r)
    ts = r.mean() / (r.std(ddof=1) / np.sqrt(n)) if n > 1 else np.nan
    print(f"  mean {r.mean():.2%}  median {r.median():.2%}  t {ts:.2f}  win {(r > 0).mean():.0%}  worst {r.min():.1%}  best {r.max():.1%}")
    by = t.groupby(pd.to_datetime(t["day"]).dt.year)["ret"].agg(["size", "mean"])
    print("  by year: " + "; ".join(f"{y} n {int(a['size'])} mean {a['mean']:.2%}" for y, a in by.iterrows()))
    if n < n_min:
        print(f"  STAGE 1 VERDICT: not testable (fewer than {n_min} events)")
    else:
        kill = r.mean() < mean_min or ts < 1
        s2 = r.mean() >= 2 * mean_min and ts >= 2
        print(f"  STAGE 1 VERDICT: {'KILL' if kill else 'survives (kill-only)'}" + (" — Stage 2 worthy" if s2 and not kill else ""))


def binance_ann():
    p = PUB / "uncharted_w3_binance_ann.json"
    if not p.exists():
        return None
    d = json.loads(p.read_text())
    items = [x for v in d.values() for x in v]
    a = pd.DataFrame(items).drop_duplicates("code")
    a["day"] = pd.to_datetime(a["releaseDate"].astype("int64"), unit="ms", utc=True).dt.normalize()
    return a[(a["day"] >= W_START) & (a["day"] <= W_END)]


def tickers_from(title):
    paren = re.findall(r"\(([A-Z0-9]{2,12})\)", title)
    if paren:
        return paren
    m = re.search(r"(?:Tag (?:on|to Include)|Include|List|on)\s+(.+?)(?:\s+on\s+\d|\s+with\s|\s*\(|$)", title)
    if not m:
        return []
    return [x.strip() for x in re.split(r",|&| and ", m.group(1)) if re.fullmatch(r"[A-Z0-9]{2,12}", x.strip())]


def main():
    print("===== Wave 3 (#392-#401)")
    cd, C, F, first = load_hl()
    print(f"  Hyperliquid perps {C.shape[1]}, days {C.index.min().date()}..{C.index.max().date()}; funding coins {F.shape[1]} (zero before 2024)")
    a = binance_ann()
    if a is None:
        print("\n#392-#394, #398: Binance announcements not fetched yet")
    else:
        print(f"  Binance announcements in window: {len(a)}")
        mt = a[a["title"].str.contains("Monitoring Tag", case=False) & a["title"].str.contains("Add|Extend", case=False)
               & ~a["title"].str.contains("Remove", case=False)]
        ev = pd.DataFrame([{"day": r["day"], "token": t, "label": r["title"][:60]} for _, r in mt.iterrows() for t in tickers_from(r["title"])])
        print(f"  #392 monitoring-tag announcements {len(mt)}, tokens {len(ev)}")
        verdict_e(event_short(ev, 7, C, F, first) if len(ev) else pd.DataFrame(), "#392 U9b Binance monitoring-tag additions (H 7)")
        ls = a[a["title"].str.match(r"^Binance Will List", case=False)]
        ev = pd.DataFrame([{"day": r["day"], "token": t, "label": r["title"][:60]} for _, r in ls.iterrows() for t in tickers_from(r["title"])])
        print(f"\n  #393 'Binance Will List' announcements {len(ls)}, tokens {len(ev)}")
        verdict_e(event_short(ev, 7, C, F, first) if len(ev) else pd.DataFrame(), "#393 U23 Binance spot listings, fade (H 7)")
        ad = a[a["title"].str.contains("HODLer Airdrop|Launchpool|Megadrop", case=False)]
        ev = pd.DataFrame([{"day": r["day"], "token": t, "label": r["title"][:60]} for _, r in ad.iterrows() for t in tickers_from(r["title"])])
        print(f"\n  #394 airdrop-programme announcements {len(ad)}, tokens {len(ev)}")
        verdict_e(event_short(ev, 14, C, F, first, min_age=0, max_delay=5) if len(ev) else pd.DataFrame(),
                  "#394 U24 airdrop-distribution listings, short (H 14)")
        lp = a[a["title"].str.contains("Launchpool|Megadrop", case=False)].drop_duplicates("day")
        ev = pd.DataFrame({"day": lp["day"], "token": "BNB", "label": lp["title"].str[:60]})
        t = event_short(ev, 5, C, F, first, min_age=0, long_coin="BNB") if len(ev) else pd.DataFrame()
        verdict_e(t, "#398 U28 long BNB vs BTC after Launchpool/Megadrop announcements (H 5)", n_min=10, mean_min=0.005)
    kp = PUB / "uncharted_w3_korea.parquet"
    if kp.exists():
        k = pd.read_parquet(kp)
        k["day"] = pd.to_datetime(k["first_day"], utc=True).dt.normalize()
        k = k.sort_values("day").drop_duplicates("coin")
        print(f"\n  #395 Korean KRW markets with a first candle: {len(k)} (Upbit {int((k.venue == 'upbit').sum())}, "
              f"Bithumb {int((k.venue == 'bithumb').sum())}); in window {int(((k.day >= W_START) & (k.day <= pd.Timestamp('2026-10-24', tz='UTC'))).sum())}")
        k = k[(k["day"] >= W_START) & (k["day"] <= pd.Timestamp("2026-10-24", tz="UTC"))]
        verdict_e(event_short(pd.DataFrame({"day": k["day"], "token": k["coin"], "label": k["venue"]}), 7, C, F, first),
                  "#395 U25 Korean KRW listings, fade (H 7)")
    else:
        print("\n#395: Korean listing data not fetched yet")
    b = pd.read_parquet(PUB / "uncharted_389_binance_ohlc.parquet", columns=["sym", "t"])
    fb = b.groupby("sym")["t"].min()
    ev = pd.DataFrame({"day": pd.to_datetime(fb.values, unit="s", utc=True).normalize(), "token": [s[:-4] for s in fb.index]})
    ev = ev[(ev["day"] >= W_START) & (ev["day"] <= W_END)]
    print(f"\n  #396 Binance USDT perps first listed in window: {len(ev)}")
    verdict_e(event_short(ev, 14, C, F, first, min_age=14), "#396 U26 Binance perp launch on a token already on Hyperliquid (H 14)")
    cascade(cd, F)
    bo = pd.read_parquet(PUB / "uncharted_389_binance_ohlc.parquet").rename(columns={"sym": "coin"})
    bo["day"] = pd.to_datetime(bo["t"], unit="s", utc=True).dt.normalize()
    cascade(bo.drop_duplicates(["coin", "day"]), None, label="#397 Stage 2: cascade-day reversal on Binance USD-M (out-of-sample)",
            start=pd.Timestamp("2020-01-01", tz="UTC"))
    print("\n#399 net-nets, #400 CoW AMM, #401 LBPs: see below" if (PUB / "uncharted_w3_treasuries.json").exists() else
          "\n#399-#401: data not fetched yet")
    if (PUB / "uncharted_w3_treasuries.json").exists():
        netnets()
    if (PUB / "uncharted_w3_cowamm_charts.parquet").exists():
        cowamm()
    if (PUB / "uncharted_w3_lbp_pools.json").exists():
        lbp()


def cascade(cd, F, share=0.25, wick=0.15, hold=3, label="#397 U27 cascade-day reversal (Hyperliquid)", start=None):
    print(f"\n#### {label}")
    W_START_ = start or W_START
    cd = cd.sort_values(["coin", "day"]).copy()
    cd["prev"] = cd.groupby("coin")["c"].shift()
    cd["age"] = (cd["day"] - cd.groupby("coin")["day"].transform("min")).dt.days
    elig = cd[(cd["age"] >= 30) & cd["prev"].notna() & (cd["day"] >= W_START_) & (cd["day"] <= W_END)].copy()
    elig["wicked"] = elig["l"] <= elig["prev"] * (1 - wick)
    C = cd.pivot(index="day", columns="coin", values="c")
    for thr in (share, 0.10):
        g = elig.groupby("day")["wicked"].mean()
        days = sorted(g[g >= thr].index)
        res, busy = [], None
        for d in days:
            if busy is not None and d <= busy:
                continue
            ex = d + pd.Timedelta(days=hold)
            if ex not in C.index:
                continue
            coins = elig[(elig["day"] == d) & elig["wicked"]]["coin"].tolist()
            r = (C.loc[ex, coins] / C.loc[d, coins] - 1).dropna()
            win = F.loc[d + pd.Timedelta(days=1):ex] if F is not None else pd.DataFrame()
            fund = np.nanmean([float(win[c].sum()) if c in win else 0.0 for c in r.index]) if len(r) and len(win) else 0.0
            res.append({"day": d.date(), "n_coins": len(r), "share": float(g[d]), "ret": float(r.mean()) - fund - 2 * FEE})
            busy = ex
        t = pd.DataFrame(res)
        tag = "(registered)" if thr == share else "(context)"
        if t.empty:
            print(f"  threshold {thr:.0%} {tag}: no cascade days")
            continue
        tst = t["ret"].mean() / (t["ret"].std(ddof=1) / np.sqrt(len(t))) if len(t) > 1 else np.nan
        print(f"  threshold {thr:.0%} {tag}: events {len(t)}; mean basket 3-day return {t['ret'].mean():.2%}, median {t['ret'].median():.2%}, "
              f"t {tst:.2f}, positive {(t['ret'] > 0).mean():.0%}")
        print("    " + "; ".join(f"{r.day} ({r.n_coins} perps, {r.share:.0%}) {r.ret:+.1%}" for r in t.itertuples()))
        if thr == share:
            if start is not None:  # Stage 2 (Binance)
                ok = len(t) >= 8 and t["ret"].mean() >= 0.02 and (t["ret"] > 0).mean() >= 0.6 and tst >= 2
                print(f"  STAGE 2 VERDICT (Binance out-of-sample): {'PASS' if ok else 'FAIL'}")
            elif len(t) < 8:
                print("  STAGE 1 VERDICT: not testable (fewer than 8 cascade days)")
            else:
                kill = t["ret"].mean() < 0.02 or (t["ret"] > 0).mean() < 0.6
                print(f"  STAGE 1 VERDICT: {'KILL' if kill else 'survives (kill-only)'}")


def netnets():
    print("\n#### #399 U18 crypto net-nets")
    tr = json.loads((PUB / "uncharted_w3_treasuries.json").read_text())
    mp = PUB / "uncharted_w3_mcaps.parquet"
    if not mp.exists() or not mp.stat().st_size:
        print("  no market caps fetched: not testable")
        return
    mc = pd.read_parquet(mp)
    if mc.empty:
        print("  no market caps fetched: not testable")
        return
    mc["day"] = pd.to_datetime(mc["t"], unit="s", utc=True).dt.normalize()
    M = mc.drop_duplicates(["id", "day"]).pivot(index="day", columns="id", values="mcap").sort_index()
    liq = {}
    for t in tr:
        g = t.get("gecko_id")
        bd = t.get("tokenBreakdowns") or {}
        if g and bd:
            liq[g] = float(bd.get("stablecoins") or 0) + float(bd.get("majors") or 0)
    print(f"  protocols with treasury breakdown + gecko id: {len(liq)}; with market caps: {len(set(liq) & set(M.columns))}")
    print("  NOTE: today's treasury used for every month (treasury history not used); look-ahead in the treasury figure")
    months = [d for d in M.index if d.day == 1]
    rows = []
    for d in months:
        ex = d + pd.DateOffset(months=3)
        if ex > M.index.max():
            continue
        exd = M.index[M.index.get_indexer([ex], method="nearest")[0]]
        univ = [g for g in liq if g in M.columns and pd.notna(M.at[d, g]) and M.at[d, g] > 0 and pd.notna(M.at[exd, g])]
        if not univ:
            continue
        ret = {g: M.at[exd, g] / M.at[d, g] - 1 for g in univ}  # market-cap change ~ price change (supply changes ignored)
        nn = [g for g in univ if M.at[d, g] < liq[g]]
        bench = np.mean(list(ret.values()))
        for g in nn:
            rows.append({"month": d.date(), "id": g, "ret": ret[g], "excess": ret[g] - bench})
    t = pd.DataFrame(rows)
    if t.empty or len(t) < 10:
        print(f"  positions {len(t)}: STAGE 1 VERDICT: KILL (fewer than 10 positions)")
        return
    print(f"  positions {len(t)} over {t['month'].nunique()} months; mean 3-month return {t['ret'].mean():.1%}, mean excess {t['excess'].mean():.1%}, "
          f"median excess {t['excess'].median():.1%}")
    print(f"  STAGE 1 VERDICT: {'KILL' if t['excess'].mean() < 0.05 else 'survives (kill-only)'}")


def cowamm():
    print("\n#### #400 U12 CoW AMM liquidity")
    pools = json.loads((PUB / "uncharted_w3_cowamm.json").read_text())
    ch = pd.read_parquet(PUB / "uncharted_w3_cowamm_charts.parquet")
    px = pd.read_parquet(PUB / "uncharted_w3_cowamm_prices.parquet") if (PUB / "uncharted_w3_cowamm_prices.parquet").stat().st_size else pd.DataFrame()
    if ch.empty:
        print("  no pools: not testable")
        return
    ch["day"] = pd.to_datetime(ch["ts"], utc=True).dt.normalize()
    if len(px):
        px["day"] = pd.to_datetime(px["t"], unit="s", utc=True).dt.round("D")
        P = px.drop_duplicates(["key", "day"]).pivot(index="day", columns="key", values="price")
    rows = []
    for p in pools:
        g = ch[ch["pool"] == p["pool"]].sort_values("day")
        if len(g) < 180 or g["tvlUsd"].max() < 1e6:
            continue
        toks = [f"{(p.get('chain') or '').lower()}:{a.lower()}" for a in (p.get("underlyingTokens") or [])]
        il = np.nan
        if len(px) and len(toks) == 2 and all(k in P for k in toks):
            r = (P[toks[0]] / P[toks[1]]).reindex(g["day"]).dropna()
            vals = []
            for i in range(0, len(r) - 30, 30):
                k_ = r.iloc[i + 30] / r.iloc[i]
                vals.append(2 * np.sqrt(k_) / (1 + k_) - 1)  # 50/50 constant-product IL over the window
            il = -np.mean(vals) * 365 / 30 * 100 if vals else np.nan
        rows.append({"symbol": p.get("symbol"), "chain": p.get("chain"), "days": len(g), "tvl_max_m": g["tvlUsd"].max() / 1e6,
                     "apyBase": g["apyBase"].mean(), "il_ann": il, "net": g["apyBase"].mean() - (il if pd.notna(il) else 0)})
    t = pd.DataFrame(rows)
    if t.empty:
        print("  no pool with >= 180 days and >= $1M TVL: not testable")
        return
    print(t.to_string(index=False, float_format=lambda x: f"{x:8.2f}"))
    med = t["net"].median()
    print(f"  median (base APY - IL) {med:.1f}%/yr; STAGE 1 VERDICT: {'KILL (< 10%/yr)' if med < 10 else 'survives (kill-only)'}")


def lbp():
    print("\n#### #401 U4 LBP end-of-sale buying")
    info = json.loads((PUB / "uncharted_w3_lbp_pools.json").read_text())
    o = pd.read_parquet(PUB / "uncharted_w3_lbp_ohlcv.parquet") if (PUB / "uncharted_w3_lbp_ohlcv.parquet").stat().st_size else pd.DataFrame()
    pr = pd.read_parquet(PUB / "uncharted_w3_lbp_prices.parquet") if (PUB / "uncharted_w3_lbp_prices.parquet").stat().st_size else pd.DataFrame()
    print(f"  LBP pools with GeckoTerminal info: {len(info)}; with candles: {o['pool'].nunique() if len(o) else 0}")
    if o.empty or pr.empty:
        print("  STAGE 1 VERDICT: not testable (no candle/price data)")
        return
    o["day"] = pd.to_datetime(o["t"], unit="s", utc=True).dt.normalize()
    pr["day"] = pd.to_datetime(pr["t"], unit="s", utc=True).dt.round("D")
    rows = []
    for p in info:
        g = o[(o["pool"] == p["pool"]) & (o["v_usd"] > 0)].sort_values("day")
        if g.empty or g["v_usd"].sum() < 50_000:
            continue
        end = g["day"].iloc[-1]
        if end < W_START or end > W_END:
            continue
        px = pr[(pr["pool"] == p["pool"])]
        best = None
        for k, s in px.groupby("key"):
            s = s.drop_duplicates("day").set_index("day")["price"]
            if end in s.index and (end + pd.Timedelta(days=7)) in s.index:
                lbp_close = float(g["c"].iloc[-1])
                if s[end] > 0 and abs(s[end] / lbp_close - 1) < 0.5:  # the token (not the reserve asset) matches the LBP close
                    best = s[end + pd.Timedelta(days=7)] / lbp_close - 1
        if best is not None:
            rows.append({"pool": p["pool"], "name": p.get("name"), "end": end.date(), "vol_usd": g["v_usd"].sum(), "ret7": best})
    t = pd.DataFrame(rows)
    if len(t) < 10:
        print(f"  LBPs with >= $50K volume, an end in the window and a 7-day price: {len(t)} -> STAGE 1 VERDICT: not testable (fewer than 10)")
        if len(t):
            print(t.to_string(index=False))
        return
    print(t.sort_values("end").to_string(index=False, float_format=lambda x: f"{x:10.3f}"))
    print(f"  median 7-day return {t['ret7'].median():.1%}; STAGE 1 VERDICT: {'KILL' if t['ret7'].median() <= 0 else 'survives (kill-only)'}")


if __name__ == "__main__":
    main()

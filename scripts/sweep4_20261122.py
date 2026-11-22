"""Sweep 4 (docs/PREREG_SWEEP4_20261122.md): #330 pump.fun graduation, #334 Coinbase listing short, #335 buyback rotation, #339 tokenised gold,
#337 S&P 500 deletions, #342 unlock shorts (the last two on job sweep4b).

    uv run python -m scripts.sweep4_20261122 | tee docs/jx_runs/sweep4_20261122.txt
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np
import pandas as pd

R = json.load(open("data/public/sweep4_raw.json"))
RB = json.load(open("data/public/sweep4b_raw.json")) if os.path.exists("data/public/sweep4b_raw.json") else {}
S1, E0, E1, SPLIT = pd.Timestamp("2026-05-01", tz="UTC"), pd.Timestamp("2024-11-01", tz="UTC"), pd.Timestamp("2026-11-01", tz="UTC"), \
    pd.Timestamp("2025-11-01", tz="UTC")


def event_verdict(label, ev, min_mean=0.0, s2_min=0.5, hold_days=1):
    """ev: DataFrame with columns t (UTC Timestamp) and r (net return, fraction)."""
    if ev.empty:
        print(f"{label}: no events -> not testable (no data)\n")
        return
    p = ev[(ev.t >= S1) & (ev.t < E1)]
    print(f"{label}: events {len(ev)} (Stage 1 slice {len(p)}): Stage 1 mean {p.r.mean() * 100:.3f}% per event", end="")
    if not len(p) or not p.r.mean() * 100 > min_mean:
        print(" -> KILL -> FAIL (Stage 1)\n")
        return
    a = ev[(ev.t >= E0) & (ev.t < E1)]
    m, sd = a.r.mean() * 100, a.r.std(ddof=1) * 100
    t = m / (sd / np.sqrt(len(a))) if len(a) > 1 else float("nan")
    h1, h2 = a[a.t < SPLIT].r.mean() * 100, a[a.t >= SPLIT].r.mean() * 100
    per_year = len(a) / 2.0
    capital = min(per_year * hold_days / 252, 1.0)  # share of the year a single position is open
    yr = (np.prod(1 + a.r.values) ** (1 / 2.0) - 1) * 100 if capital >= 1 else m * per_year
    ok = m > s2_min and t > 2 and h1 > 0 and h2 > 0 and yr >= 8
    print(f"\n  Stage 2 (n {len(a)}): mean {m:.3f}%, t {t:.2f}, halves {h1:.3f}% / {h2:.3f}%, hit {(a.r > 0).mean():.0%}, ~{yr:.1f}%/yr "
          f"(one position at a time)\n  VERDICT: {'PASS' if ok else 'FAIL'}\n")


def p330():
    rows = []
    for c in R.get("pump_coins", []):
        o = R.get(f"pump_ohlcv|{c['mint']}")
        if not o or len(o) < 30:
            continue
        df = pd.DataFrame(o, columns=["t", "o", "h", "l", "c", "v"]).sort_values("t")
        t0 = df.t.iloc[0]  # first AMM candle = migration hour
        a = df[df.t >= t0 + 3600]
        b = df[df.t >= t0 + 25 * 3600]
        if a.empty or b.empty:
            continue
        rows.append({"t": pd.Timestamp(int(t0), unit="s", tz="UTC"), "r": b.c.iloc[0] / a.c.iloc[0] - 1 - 0.02})
    ev = pd.DataFrame(rows)
    if len(ev):
        print(f"  (#330 context) median {ev.r.median() * 100:.1f}%, share losing > 50%: {(ev.r < -0.5).mean():.0%}, window "
              f"{ev.t.min():%Y-%m-%d}..{ev.t.max():%Y-%m-%d}")
    event_verdict("#330 pump.fun graduation (buy +1 h after migration, sell +24 h, 2% costs)", ev)


def hl_daily(src, coin):
    v = src.get(f"hld|{coin}")
    if not v:
        return None
    return pd.Series([x[1] for x in v], index=pd.to_datetime([x[0] for x in v], unit="ms", utc=True).floor("D"))


def p334():
    btc = hl_daily(R, "BTC")
    rows = []
    for coin, t in (R.get("coinbase_first_day") or {}).items():
        d = pd.Timestamp(int(t), unit="s", tz="UTC").floor("D")
        if d < pd.Timestamp("2024-06-10", tz="UTC"):  # first candle at the search start = listed earlier
            continue
        px = hl_daily(R, coin)
        if px is None or btc is None or d not in px.index or d + pd.Timedelta(days=7) not in px.index:
            continue
        d7 = d + pd.Timedelta(days=7)
        r = -(px[d7] / px[d] - 1) + (btc[d7] / btc[d] - 1) - 0.001
        rows.append({"t": d, "r": r, "coin": coin})
    event_verdict("#334 Coinbase listing: short HL perp at the listing-day close for 7 days, BTC hedge", pd.DataFrame(rows), hold_days=7)


def p335():
    prot = R.get("buyback_protocols", [])
    btcp = R.get("price|bitcoin") or []
    btc = pd.Series({pd.Timestamp(x["timestamp"], unit="s", tz="UTC").floor("D"): x["price"] for x in btcp})
    REV, PX, MC = {}, {}, {}
    for p_ in prot:
        g = p_.get("gecko_id")
        pr = R.get(f"price|{g}") if g else None
        if not pr or not p_.get("chart") or not p_.get("mcap"):
            continue
        px = pd.Series({pd.Timestamp(x["timestamp"], unit="s", tz="UTC").floor("D"): x["price"] for x in pr})
        rev = pd.Series({pd.Timestamp(int(x[0]), unit="s", tz="UTC").floor("D"): x[1] for x in p_["chart"]})
        REV[p_["slug"]], PX[p_["slug"]] = rev, px
        MC[p_["slug"]] = float(p_["mcap"]) * px / px.iloc[-1]
    if not REV:
        print("#335 buyback rotation: no usable protocols -> not testable\n")
        return
    days = pd.date_range(E0, E1 - pd.Timedelta(days=1), freq="D", tz="UTC")
    out, prev = [], set()
    for m in pd.date_range(E0, E1 - pd.Timedelta(days=1), freq="MS", tz="UTC"):
        pday = m - pd.Timedelta(days=1)
        sc = {}
        for s_ in REV:
            rv = REV[s_].loc[pday - pd.Timedelta(days=29):pday].sum() * 365 / 30
            mc = MC[s_].asof(pday) if len(MC[s_]) else np.nan
            if mc and mc >= 50e6 and rv > 0:
                sc[s_] = rv / mc
        pick = [k for k, _ in sorted(sc.items(), key=lambda x: -x[1])[:5]]
        sw = len(set(pick) ^ prev)
        prev = set(pick)
        for j, d in enumerate([x for x in days if x.year == m.year and x.month == m.month]):
            rr = []
            for s_ in pick:
                a, b = PX[s_].asof(d - pd.Timedelta(days=1)), PX[s_].asof(d)
                if a and b:
                    rr.append(b / a - 1)
            bt = btc.asof(d) / btc.asof(d - pd.Timedelta(days=1)) - 1 if len(btc) else 0.0
            r = (np.mean(rr) - bt) if rr else 0.0
            out.append((d, r - (sw / max(len(pick), 1) * 0.001 if j == 0 else 0.0)))
    s = pd.Series(dict(out))
    ann = lambda x: float(x.mean() * 365 * 100)  # noqa: E731
    p = s[s.index >= pd.Timestamp("2026-08-01", tz="UTC")]
    print(f"#335 buyback-yield rotation (top-5, short BTC): {len(REV)} protocols; Stage 1 2026-08..10 {ann(p):.2f}%/yr", end="")
    if not ann(p) >= 4:
        print(" -> KILL -> FAIL (Stage 1)\n")
        return
    h1, h2 = ann(s[s.index < SPLIT]), ann(s[s.index >= SPLIT])
    print(f"\n  Stage 2 halves {h1:.2f}% / {h2:.2f}%\n  VERDICT: {'PASS' if h1 >= 8 and h2 >= 8 else 'FAIL'}\n")


def p339():
    y = R.get("yahoo|GC=F")
    if not y or not (y.get("chart") or {}).get("result"):
        print("#339 tokenised gold: no gold futures prices -> not testable\n")
        return
    r = y["chart"]["result"][0]
    gold = pd.Series(r["indicators"]["quote"][0]["close"], index=pd.to_datetime(r["timestamp"], unit="s", utc=True).floor("D")).dropna()
    for nm in ("paxg", "xaut"):
        pr = R.get(f"price|{nm}") or []
        px = pd.Series({pd.Timestamp(x["timestamp"], unit="s", tz="UTC").floor("D"): x["price"] for x in pr})
        prem = (px / gold.reindex(px.index) - 1).dropna()
        p = prem[prem.index >= S1]
        big = p[p.abs() > 0.01]
        days_yr = len(big) / max(len(p), 1) * 252
        excess = (big.abs() - 0.01).mean() * 100 if len(big) else 0.0
        kill = days_yr < 12 or excess < 0.3
        print(f"#339 {nm.upper()} vs gold futures: Stage 1 slice {len(p)} days; median premium {p.median() * 100:.2f}%; days |prem| > 1%: {len(big)} "
              f"(~{days_yr:.0f}/yr); mean excess beyond 1%: {excess:.2f}% -> {'KILL -> FAIL (Stage 1)' if kill else 'continue to Stage 2'}")
    print("  (premium vs the front gold future includes a small futures basis; monetising needs issuer mint/redeem with KYC)\n")


def main() -> int:
    print("Sweep 4. Event Stage 1 slice 2026-05..10 (KILL if mean <= 0); Stage 2 2024-11..2026-10: mean > 0.5%, t > 2, halves > 0, >= 8%/yr.\n")
    p330()
    p334()
    p335()
    p339()
    if not RB:
        print("(job sweep4b pending: #337 deletions, #342 unlocks, #303 announcement-date check)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

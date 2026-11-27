"""Batch L #501-#504: exchange risk-parameter forced closes (docs/PREREG_BATCH_L_20261127.md).

    uv run python -m scripts.batch_l_20261127 | tee docs/jx_runs/batch_l_20261127.txt
"""
import json
import re

import numpy as np
import pandas as pd

from ict import data as D

OUT = D.REPO_ROOT / "data" / "public"
COST, SIZE, SPLIT = 0.0009, 5000.0, pd.Timestamp("2025-01-01", tz="UTC")
END = pd.Timestamp("2026-11-27", tz="UTC")
NAMES = {501: "Leverage-tier cuts", 502: "Perp delistings", 503: "Margin-pair delistings", 504: "Collateral-ratio cuts"}


def hl_listed():
    c = pd.read_parquet(OUT / "hl_coins.parquet")["coin"].astype(str)
    return {x.upper().lstrip("K") if x.startswith("k") else x.upper() for x in c}


def price_at(px, sym, ts):
    """Close of the last 1h bar that has closed by ts (bar open + 1 h <= ts); None if the symbol has no bar by then."""
    s = px.get(sym)
    if s is None:
        return None, None
    i = s.index.searchsorted(ts, side="right") - 1
    return (float(s.iloc[i]), s.index[i]) if i >= 0 else (None, None)


def exit_time(e, body, te):
    cap = te + pd.Timedelta(days=14)
    if e["idea"] in (501, 504):
        return te + pd.Timedelta(hours=72)
    m = re.search(r"(20\d\d-\d\d-\d\d)", e["title"]) or (re.search(r"(20\d\d-\d\d-\d\d)", body) if e["idea"] == 502 else None)
    if not m:
        return te + pd.Timedelta(hours=72)
    hh = 9 if e["idea"] == 502 else 6
    tx = pd.Timestamp(m.group(1), tz="UTC") + pd.Timedelta(hours=hh)
    return min(max(tx, te + pd.Timedelta(hours=1)), cap)


def cut_coins(body):
    """#504: coins whose collateral ratio is lowered (shared parser with the fetch job; reads Binance's one-cell-per-line tables)."""
    import sys
    sys.path.insert(0, str(D.REPO_ROOT / "scripts"))
    from fetch_uncharted import collateral_cuts
    return {c + "USDT" for c in collateral_cuts(body)}


def main():
    events = json.loads((OUT / "batchl_events.json").read_text())
    bodies = json.loads((OUT / "batchl_bodies.json").read_text())
    df = pd.read_parquet(OUT / "batchl_1h")
    df["ts"] = pd.to_datetime(df["t"], unit="s", utc=True) + pd.Timedelta(hours=1)  # close time
    px = {s: g.set_index("ts")["close"].sort_index() for s, g in df.groupby("sym")}
    hl = hl_listed()
    print(f"events {len(events)}; bodies {len(bodies)} ({sum(str(b).startswith('__ERROR__') for b in bodies.values())} errors); "
          f"1h symbols {len(px)}; Hyperliquid coins {len(hl)}")
    print("Short the coin from A rounded up + 1 h to the exit; excess = -(coin - BTC) - 0.09%. One announcement = one event.\n")
    rows = []
    for e in events:
        body = bodies.get(e["code"], "")
        syms = list(e["syms"])
        if e["idea"] == 504:
            syms = sorted(set(syms) & cut_coins(body))
        if not syms:
            continue
        a = pd.Timestamp(e["ms"], unit="ms", tz="UTC")
        te = a.ceil("h") + pd.Timedelta(hours=1)
        tx = exit_time(e, body, te)
        if tx > END:
            continue
        b0, _ = price_at(px, "BTCUSDT", te)
        rets, hl_rets = [], []
        for s in syms:
            p0, t0 = price_at(px, s, te)
            p1, t1 = price_at(px, s, tx)
            if p0 is None or p1 is None or t0 < te - pd.Timedelta(hours=2) or t1 <= t0:
                continue
            bx, _ = price_at(px, "BTCUSDT", t1)
            if b0 is None or bx is None:
                continue
            r = -((p1 / p0 - 1) - (bx / b0 - 1)) - COST
            rets.append(r)
            coin = s[:-4].replace("1000", "", 1) if s.startswith("1000") else s[:-4]
            if coin in hl:
                hl_rets.append(r)
        if rets:
            title_only = bool(re.search(r"[A-Z0-9]{2,15}USDT", e["title"]))
            rows.append(dict(idea=e["idea"], a=a, r=float(np.mean(rets)), r_hl=float(np.mean(hl_rets)) if hl_rets else np.nan,
                             n_sym=len(rets), reduce=bool(re.search(r"reduc|lower|decreas", body, re.I)),
                             title_sym=title_only, hold_h=(tx - te).total_seconds() / 3600))
    ev = pd.DataFrame(rows)

    def stats(x):
        x = pd.Series(x).dropna()
        n = len(x)
        if n == 0:
            return n, np.nan, np.nan
        t = x.mean() / (x.std(ddof=1) / np.sqrt(n)) if n > 1 and x.std(ddof=1) > 0 else np.nan
        return n, x.mean(), t

    yrs = (END - SPLIT).days / 365.25
    for idea, name in NAMES.items():
        g = ev[ev.idea == idea] if len(ev) else ev
        print(f"#{idea} {name}")
        if g.empty:
            print("   no usable events: NOT TESTABLE\n")
            continue
        s1, s2 = g[g.a < SPLIT], g[g.a >= SPLIT]
        n1, m1, t1 = stats(s1.r)
        n2, m2, t2 = stats(s2.r)
        nh, mh, th = stats(s2.r_hl)
        print(f"   Stage 1 (< 2025): n {n1}, mean {m1:+.2%}, t {t1:.2f} | median hold {s1.hold_h.median() if n1 else np.nan:.0f} h")
        print(f"   Stage 2 (2025-26): n {n2}, mean {m2:+.2%}, t {t2:.2f} | Hyperliquid-listed: n {nh}, mean {mh:+.2%}, t {th:.2f}")
        kill = n1 >= 8 and not (m1 > 0)
        ok = (not kill) and n2 >= 15 and m2 >= 0.01 and t2 >= 2 and nh >= 15 and mh >= 0.01 and th >= 2
        usd = m2 * SIZE * n2 / yrs if n2 else 0.0
        if idea == 501:
            nv, mv, tv = stats(s2[s2.reduce].r)
            print(f"   variant (body says reduce/lower/decrease), Stage 2: n {nv}, mean {mv:+.2%}, t {tv:.2f} (reported only)")
        nt, mt, tt = stats(s2[s2.title_sym].r)
        print(f"   diagnostic: Stage 2 events with symbols in the title: n {nt}, mean {mt:+.2%}, t {tt:.2f} (reported only)")
        verdict = "KILL (Stage 1)" if kill else ("PASS" if ok else "FAIL")
        if n1 < 8 and not kill:
            verdict += " (Stage 1 had < 8 events: no kill possible)"
        print(f"   VERDICT {verdict} | $/yr at $5,000 per event: ${usd:,.0f}\n")


if __name__ == "__main__":
    main()

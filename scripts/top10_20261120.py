"""Top-10 crypto / prediction-market tests, as docs/PREREG_TOP10_20261120.md defines them.

    uv run python scripts/top10_20261120.py

Pre-registered in bb5f06e (N1 baseline amended in fd1ab68, before any data).
Reads data/public/*.parquet written by scripts/fetch_public.py.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

P = Path(__file__).resolve().parent.parent / "data" / "public"
H = 3600 * 1000


def tstat(x):
    x = np.asarray(x, float)
    x = x[~np.isnan(x)]
    return float(x.mean() / (x.std(ddof=1) / np.sqrt(len(x)))) if len(x) > 2 else float("nan")


def welch(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    a, b = a[~np.isnan(a)], b[~np.isnan(b)]
    if len(a) < 3 or len(b) < 3:
        return float("nan")
    return float((a.mean() - b.mean()) / np.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b)))


def load(name):
    f = P / f"{name}.parquet"
    return pd.read_parquet(f) if f.exists() else None


def halves(df, col):
    df = df.sort_values(col)
    mid = len(df) // 2
    return df.iloc[:mid], df.iloc[mid:]


# ------------------------------------------------------------------ N1
def n1():
    print("\n=== N1 new-perp funding spikes (Hyperliquid)")
    coins, fund, candles, base = (load(x) for x in ("hl_coins", "hl_funding", "hl_candles", "hl_baseline_coins"))
    if coins is None or fund is None or fund.empty:
        print("  no data")
        return None
    base_coins = set(base.coin) if base is not None else set()
    listed = coins[coins.first_funding_ms.notna() & (coins.first_funding_ms >= pd.Timestamp("2024-01-01", tz="UTC").timestamp() * 1000)]
    listed = listed[~listed.coin.isin(base_coins)]
    rows = []
    bf = fund[fund.coin.isin(base_coins)]
    for coin, L in zip(listed.coin, listed.first_funding_ms):
        lo, hi = L + H, L + 337 * H
        f = fund[(fund.coin == coin) & (fund.time >= lo) & (fund.time < hi)]
        if len(f) < 24:
            continue
        carry = f.rate.sum() * 1000 - 2.30
        b = bf[(bf.time >= lo) & (bf.time < hi)].groupby("coin").rate.sum() * 1000 - 2.30
        c = candles[(candles.coin == coin) & (candles.t >= lo) & (candles.t < hi)] if candles is not None else pd.DataFrame()
        pump = unhedged = np.nan
        if len(c):
            entry = c.sort_values("t").o.iloc[0]
            pump = c.h.max() / entry - 1
            unhedged = (entry - c.sort_values("t").c.iloc[-1]) / entry * 1000 + carry
        rows.append({"coin": coin, "L": L, "hours": len(f), "net": carry,
                     "base": b.mean() if len(b) else np.nan, "pump": pump, "unhedged": unhedged})
    df = pd.DataFrame(rows)
    if df.empty:
        print("  no listings with data")
        return None
    print(f"  {len(df)} listings with >= 24h of funding; delisted in meta: {int(coins.delisted.sum())}")
    ok_all = True
    for name, part in zip(("first half", "second half"), halves(df, "L")):
        t1, t2 = tstat(part.net), welch(part.net, part.base)
        ok = part.net.mean() > 0 and t1 > 2 and t2 > 2
        ok_all &= ok
        print(f"  {name}: n {len(part)}  mean net ${part.net.mean():.2f} per $1,000 per 14d  t {t1:.2f}  "
              f"baseline ${part.base.mean():.2f}  vs base t {t2:.2f}  {'PASS' if ok else '-'}")
    print(f"  median net ${df.net.median():.2f}; share with net > 0: {(df.net > 0).mean():.0%}")
    print(f"  rose >= 50% within 14d (liquidation risk for a 2x short leg): {(df.pump >= 0.5).mean():.0%}")
    print(f"  unhedged short incl. funding: mean ${df.unhedged.mean():.2f}, median ${df.unhedged.median():.2f}")
    print(f"  -> N1 {'PASS' if ok_all else 'fail'}")
    return ok_all


# ------------------------------------------------------------------ N2
def n2():
    print("\n=== N2 utilisation-threshold arbitrage (Aave v3)")
    d = load("llama_lend")
    if d is None or d.empty:
        print("  no data")
        return None
    d["day"] = pd.to_datetime(d["timestamp"]).dt.tz_localize(None).dt.normalize()
    lend_mode = "totalSupplyUsd" in d and d["totalSupplyUsd"].notna().any()
    print(f"  mode: {'utilisation (lendBorrow)' if lend_mode else 'FALLBACK apyBase spike'}; pools {d.pool.nunique()}")
    d = d.sort_values(["pool", "day"]).drop_duplicates(["pool", "day"])
    bench = d.groupby(["symbol", "day"]).apyBase.median().rename("bench")
    d = d.join(bench, on=["symbol", "day"])
    events = []
    for pid, g in d.groupby("pool"):
        g = g.reset_index(drop=True)
        if lend_mode:
            u = g.totalBorrowUsd / g.totalSupplyUsd
            thr = u.shift(1).rolling(90, min_periods=60).quantile(0.9)
            hit = (u > thr) & (u.shift(1) <= thr.shift(1))
        else:
            med = g.apyBase.shift(1).rolling(30, min_periods=20).median()
            hit = (g.apyBase > 2 * med) & ~(g.apyBase.shift(1) > 2 * med.shift(1))
        for i in np.flatnonzero(hit.fillna(False).to_numpy()):
            nxt = g.iloc[i + 1:i + 8]
            if len(nxt) < 7:
                continue
            excess = ((nxt.apyBase - nxt.bench) / 100 / 365 * 10_000).sum() - 20
            events.append({"pool": pid, "day": g.day.iloc[i], "net": excess})
    ev = pd.DataFrame(events)
    if ev.empty:
        print("  no events")
        return None
    ok_all = True
    for name, part in zip(("first half", "second half"), halves(ev, "day")):
        t1 = tstat(part.net)
        ok = part.net.mean() > 0 and t1 > 2
        ok_all &= ok
        print(f"  {name}: n {len(part)}  mean net ${part.net.mean():.2f} per event on $10K  t {t1:.2f}  {'PASS' if ok else '-'}")
    per_pool = ev.groupby("pool").net.agg(["count", "mean"])
    big = per_pool[per_pool["count"] >= 5]
    share = (big["mean"] > 0).mean() if len(big) else float("nan")
    ok_all &= bool(share >= 0.5) if len(big) else False
    print(f"  pools with >= 5 events: {len(big)}, positive on {share:.0%}")
    print(f"  -> N2 {'PASS' if ok_all else 'fail'}")
    return ok_all


# ------------------------------------------------------------------ N3
def n3():
    print("\n=== N3 liquidity incentive mispricing (DEX LP pools)")
    ch = load("llama_charts")
    if ch is None or ch.empty:
        print("  no data")
        return None
    lp = ch[ch.kind == "lp"].copy()
    lp["day"] = pd.to_datetime(lp["timestamp"]).dt.tz_localize(None).dt.normalize()
    if "il7d" not in lp or lp.il7d.notna().sum() == 0:
        print("  no il7d series in the data -> cannot compute impermanent loss; no test")
        return None
    lp = lp.sort_values(["pool", "day"])
    for c in ("apyBase", "apyReward", "il7d", "tvlUsd"):
        lp[c] = pd.to_numeric(lp[c], errors="coerce")
    inc, base = [], []
    for pid, g in lp.groupby("pool"):
        g = g.reset_index(drop=True)
        if g.il7d.notna().sum() < 30:
            continue

        def ret(i):
            w = g.iloc[i:i + 30]
            if len(w) < 30:
                return np.nan
            return ((w.apyBase.fillna(0) + 0.99 * w.apyReward.fillna(0)) / 100 / 365).sum() - (w.il7d.fillna(0) / 100 / 7).abs().sum()
        q = (g.tvlUsd >= 1e6)
        hi = np.flatnonzero((q & (g.apyReward >= 20)).to_numpy())
        if len(hi):
            inc.append({"pool": pid, "day": g.day.iloc[hi[0]], "r": ret(hi[0])})
        lo = q & (g.apyReward.fillna(0) < 1)
        for m, gm in g[lo].groupby(g.day.dt.to_period("M")):
            i = gm.index[0]
            base.append({"pool": pid, "day": g.day.iloc[i], "month": m, "r": ret(i)})
    inc, base = pd.DataFrame(inc).dropna(), pd.DataFrame(base).dropna()
    if inc.empty:
        print("  no incentivised entries")
        return None
    inc["month"] = inc.day.dt.to_period("M")
    ok_all = True
    for name, part in zip(("first half", "second half"), halves(inc, "day")):
        b = base[base.month.isin(part.month)]
        t1, t2 = tstat(part.r), welch(part.r, b.r)
        ok = part.r.mean() > 0 and t1 > 2 and t2 > 2
        ok_all &= ok
        print(f"  {name}: n {len(part)}  mean 30d net {part.r.mean():.2%}  t {t1:.2f}  baseline n {len(b)} "
              f"{b.r.mean():.2%}  vs base t {t2:.2f}  {'PASS' if ok else '-'}")
    print(f"  -> N3 {'PASS' if ok_all else 'fail'}")
    return ok_all


# ------------------------------------------------------------------ N4
def n4():
    print("\n=== N4 multi-outcome probability arbitrage (Polymarket, upper bound)")
    pr, ev = load("poly_prices"), load("poly_events")
    if pr is None or pr.empty:
        print("  no data")
        return None
    pr["h"] = pr.t // 3600
    hits, n_ev, edges = 0, 0, []
    for eid, g in pr.groupby("event"):
        n_m = g.market.nunique()
        if n_m < 3:
            continue
        n_ev += 1
        piv = g.pivot_table(index="h", columns="market", values="p", aggfunc="last").sort_index()
        piv = piv.reindex(range(piv.index.min(), piv.index.max() + 1)).ffill(limit=2)
        full = piv.dropna()
        if full.empty:
            continue
        s = full.sum(axis=1)
        opp = ((s <= 0.97) | (s >= 1.03)).astype(int)
        run = (opp.groupby((opp != opp.shift()).cumsum()).transform("size") * opp)
        if (run >= 2).any():
            hits += 1
            edges.append(float((1 - s[run >= 2]).abs().max()))
    share = hits / n_ev if n_ev else float("nan")
    print(f"  events analysed {n_ev}; with a >=3% gap lasting >=2h: {hits} ({share:.0%})")
    if edges:
        print(f"  largest gap in those events: median {np.median(edges):.1%}, max {max(edges):.1%}")
    ok = n_ev > 0 and share >= 0.10
    print(f"  -> N4 {'PASS (screen: worth a live order-book scanner)' if ok else 'fail'}")
    return ok


# ------------------------------------------------------------------ N5
def n5():
    print("\n=== N5 stETH redemption discounts")
    px = load("llama_prices")
    if px is None or px.empty:
        print("  no data")
        return None
    st = [c for c in px.coin.unique() if "staked-ether" in c]
    eth = [c for c in px.coin.unique() if c.endswith(":ethereum")]
    if not st or not eth:
        print(f"  missing series: {list(px.coin.unique())}")
        return None
    # Pair each stETH price with the ETH price nearest in time (within 1 hour).
    # Grouping by calendar day mis-paired 23:59 and 00:00 prints ~24h apart.
    a = px[px.coin == st[0]].sort_values("t")[["t", "price"]].rename(columns={"price": "st"})
    b = px[px.coin == eth[0]].sort_values("t")[["t", "price"]].rename(columns={"price": "eth"})
    m = pd.merge_asof(a, b, on="t", direction="nearest", tolerance=3600).dropna()
    m["day"] = pd.to_datetime(m.t, unit="s").dt.normalize()
    m = m.drop_duplicates("day", keep="last").set_index("day")
    r = (m.st / m.eth).dropna()
    r = r[r.index >= "2023-04-12"]
    below = r <= 0.997
    runs = (below != below.shift()).cumsum()
    events = []
    for _, g in r[below].groupby(runs[below]):
        gain = (1 / g.min() - 1) - 0.001 - 0.002
        events.append({"day": g.idxmin(), "ratio": g.min(), "usd": max(0.0, gain) * 10_000})
    ev = pd.DataFrame(events)
    print(f"  days {len(r)}, ratio min {r.min():.4f}, median {r.median():.4f}; events (runs <= 0.997): {len(ev)}")
    mid = r.index[len(r) // 2]
    ok_all = True
    for name, lo, hi in (("first half", r.index[0], mid), ("second half", mid, r.index[-1] + pd.Timedelta(days=1))):
        years = (hi - lo).days / 365.25
        part = ev[(ev.day >= lo) & (ev.day < hi)] if len(ev) else ev
        usd = part.usd.sum() / years if len(part) else 0.0
        ok = usd >= 500
        ok_all &= ok
        print(f"  {name}: {len(part)} events, ${usd:,.0f} a year per $10K  {'PASS' if ok else '-'}")
    print(f"  -> N5 {'PASS' if ok_all else 'fail'}")
    return ok_all


# ------------------------------------------------------------------ N6
def n6():
    print("\n=== N6 vault allocation inefficiencies (USDC/USDT)")
    ch, now = load("llama_charts"), load("llama_pools_now")
    if ch is None or now is None:
        print("  no data")
        return None
    meta = now.set_index("pool")[["chain", "symbol", "project"]]
    x = ch[ch.kind.isin(["vault", "lend"])].join(meta, on="pool")
    x["day"] = pd.to_datetime(x["timestamp"]).dt.tz_localize(None).dt.normalize()
    x["apyv"] = pd.to_numeric(x["apy"], errors="coerce")
    x["apyb"] = pd.to_numeric(x.get("apyBase"), errors="coerce").fillna(x["apyv"])
    res = []
    for pid, v in x[x.kind == "vault"].groupby("pool"):
        chain, sym = meta.loc[pid, "chain"], meta.loc[pid, "symbol"]
        lend = x[(x.kind == "lend") & (x.chain == chain) & (x.symbol == sym)]
        if lend.empty:
            continue
        L = lend.pivot_table(index="day", columns="pool", values="apyb", aggfunc="last").sort_index()
        V = v.set_index("day").apyv.sort_index()
        days = V.index.intersection(L.index)
        if len(days) < 60:
            continue
        L, V = L.loc[days], V.loc[days]
        prev = L.shift(1)
        choice = prev.apply(lambda r: r.idxmax() if r.notna().any() else np.nan, axis=1)
        got = pd.Series([L.loc[d, c] if isinstance(c, str) else np.nan for d, c in zip(days, choice)], index=days)
        switches = (choice != choice.shift()).sum()
        cost = 20 if chain == "Ethereum" else 2
        frame = pd.DataFrame({"got": got, "vault": V}).dropna()
        if len(frame) < 60:
            continue
        mid = len(frame) // 2
        out = []
        for part in (frame.iloc[:mid], frame.iloc[mid:]):
            yrs = len(part) / 365
            sw = switches * len(part) / len(frame)
            out.append((part.got - part.vault).mean() / 100 - sw * cost / 10_000 / yrs)
        res.append({"pool": pid, "chain": chain, "sym": sym, "first": out[0], "second": out[1]})
    r = pd.DataFrame(res)
    if r.empty:
        print("  no vaults with overlapping lending data")
        return None
    good = ((r["first"] > 0.01) & (r["second"] > 0.01)).mean()
    print(f"  vaults {len(r)}; switching beats vault by > 1%/yr in both halves for {good:.0%}")
    print(f"  median excess: first half {r['first'].median():.2%}, second half {r['second'].median():.2%}")
    ok = good >= 0.5
    print(f"  -> N6 {'PASS' if ok else 'fail'}")
    return ok


def main() -> int:
    verdicts = {k: f() for k, f in (("N1", n1), ("N2", n2), ("N3", n3), ("N4", n4), ("N5", n5), ("N6", n6))}
    print("\n=== VERDICTS")
    for k, v in verdicts.items():
        print(f"  {k}: {'no data / not testable' if v is None else 'PASS' if v else 'fail'}")
    print("  N7: not data-testable (needs manual case review)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

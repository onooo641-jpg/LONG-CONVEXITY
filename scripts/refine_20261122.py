"""Refinement studies R1-R7 (docs/PREREG_REFINE_20261122.md): best variant chosen on year 1, tested once on year 2, cost x1.5 check.

    uv run python scripts/refine_20261122.py | tee docs/jx_runs/refine_20261122.txt
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from scripts.fundgap_20261121 import hourly

LO, MID, HI = [pd.Timestamp(x, tz="UTC") for x in ("2024-11-01", "2025-11-01", "2026-11-01")]
DAYS = pd.date_range(LO, HI - pd.Timedelta(days=1), freq="D", tz="UTC")
ann = lambda s: float(s.mean() * 365 * 100) if len(s) else float("nan")  # noqa: E731
PARK = 0.04 / 365


def halves(s):
    s = s.dropna()
    return ann(s[(s.index >= LO) & (s.index < MID)]), ann(s[(s.index >= MID) & (s.index < HI)])


def report(name, variants):
    """variants: {label: fn(cost_mult) -> daily return Series}."""
    print(f"===== {name}")
    res = {}
    for lab, fn in variants.items():
        y1, y2 = halves(fn(1.0))
        res[lab] = (y1, y2)
        print(f"  {lab:<58} year 1 {y1:7.2f}%   (year 2 {y2:7.2f}%, not used to choose)")
    best = max(res, key=lambda k: res[k][0] if res[k][0] == res[k][0] else -1e9)
    y1, y2 = res[best]
    _, y2c = halves(variants[best](1.5))
    ok = y1 >= 8 and y2 >= 8 and y2c >= 8
    print(f"  CHOSEN on year 1: {best} -> year 1 {y1:.2f}%, year 2 {y2:.2f}%, year 2 with costs x1.5 {y2c:.2f}% -> {'PASS' if ok else 'FAIL'}\n")


# ---------------- R1 funding gaps
def r1():
    df = pd.read_parquet("data/public/fundgap_funding.parquet")
    H = hourly(df[df.venue.isin(["hl", "dydx", "aevo"])])
    pairs = [("hl", "dydx"), ("hl", "aevo"), ("dydx", "aevo")]

    def run(entry, exit_thr, coins_only, leg_fee, cm):
        coins = sorted({c for (_, c) in H} if coins_only is None else coins_only)
        fee_open = leg_fee * 2 * cm
        pos, out = {}, []
        for d in DAYS:
            prev, today = slice(d - pd.Timedelta(hours=24), d - pd.Timedelta(hours=1)), slice(d, d + pd.Timedelta(hours=23))
            pnl = 0.0
            for k in list(pos):
                a, b, c = k
                sig = (H[(a, c)][prev] - H[(b, c)][prev]).mean() * 24 * 365 * 100
                if (not np.isfinite(sig)) or np.sign(sig) != pos[k] or abs(sig) < exit_thr:
                    pnl -= fee_open
                    pos.pop(k)
            cands = []
            for a, b in pairs:
                for c in coins:
                    if (a, c) in H and (b, c) in H and (a, b, c) not in pos:
                        sig = (H[(a, c)][prev] - H[(b, c)][prev]).mean() * 24 * 365 * 100
                        if np.isfinite(sig) and abs(sig) >= entry:
                            cands.append((-abs(sig), a, b, c, np.sign(sig)))
            for _, a, b, c, sg in sorted(cands):
                if len(pos) >= 5:
                    break
                pos[(a, b, c)] = sg
                pnl -= fee_open
            for (a, b, c), sg in pos.items():
                pnl += sg * (H[(a, c)][today] - H[(b, c)][today]).fillna(0).sum()
            out.append((d, pnl / (5 * 2 / 3)))
        return pd.Series(dict(out))
    maj = ["BTC", "ETH", "SOL"]
    report("R1 #208 funding gaps", {
        "V1 entry 15%, exit sign flip, taker": lambda cm: run(15, 0, None, 0.0005, cm),
        "V2 entry 25%, exit |signal| < 5%, taker": lambda cm: run(25, 5, None, 0.0005, cm),
        "V3 entry 10%, exit sign flip, BTC/ETH/SOL, taker": lambda cm: run(10, 0, maj, 0.0005, cm),
        "V4 entry 15%, exit sign flip, maker 0.015%": lambda cm: run(15, 0, None, 0.00015, cm),
        "V5 entry 25%, exit < 5%, maker 0.015%": lambda cm: run(25, 5, None, 0.00015, cm),
    })


# ---------------- R2 GM pools
def r2():
    px = pd.read_parquet("data/public/wrappers_prices.parquet")
    px["day"] = pd.to_datetime(px["ts"], unit="s", utc=True).dt.floor("D")
    P = px.pivot_table(index="day", columns="token", values="price", aggfunc="last").sort_index()
    f = pd.read_parquet("data/public/hedged_hlfunding.parquet")
    f["day"] = pd.to_datetime(f["t"], unit="s", utc=True).dt.floor("D")
    F = f.groupby(["coin", "day"])["rate"].sum()

    def run(h, cm):
        legs = []
        for gm, idx in (("GM_ETH", "ETH"), ("GM_BTC", "BTC")):
            rg, ri = np.log(P[gm]).diff(), np.log(P[idx]).diff()
            fd = F.loc[idx].reindex(P.index).fillna(0)
            if h == "dyn":
                beta = (rg.rolling(30).cov(ri) / ri.rolling(30).var()).clip(0, 1.2).shift(1).fillna(0.5)
                cost = beta.diff().abs().fillna(0) * 0.00045 * cm
                r = (rg - beta * ri + beta * fd - cost) / (1 + beta / 3)
            else:
                r = (rg - h * ri + h * fd) / (1 + h / 3)
            legs.append(r)
        return pd.concat(legs, axis=1).mean(axis=1)
    report("R2 #221 GMX GM pools, real GM prices", {f"h = {h}": (lambda cm, h=h: run(h, cm)) for h in (0.3, 0.5, 0.7, 0.9)}
           | {"dynamic h (trailing-30-d beta)": lambda cm: run("dyn", cm)})


# ---------------- R3 stable-yield selection
def r3():
    ch = pd.read_parquet("data/public/fallback_stable_charts.parquet")
    ch["day"] = ch["ts"].dt.floor("D")
    ch = ch.drop_duplicates(["pool", "day"])
    ch["y"] = (ch["apyBase"].fillna(0) + 0.9 * ch["apyReward"].fillna(0)).clip(upper=1000)
    ch["rs"] = ch["apyReward"].fillna(0) / (ch["apyBase"].fillna(0) + ch["apyReward"].fillna(0)).replace(0, np.nan)
    Y = ch.pivot(index="day", columns="pool", values="y").sort_index()
    RS = ch.pivot(index="day", columns="pool", values="rs").sort_index()
    T = ch.pivot(index="day", columns="pool", values="tvlUsd").sort_index().ffill(limit=3)
    first = ch.groupby("pool")["day"].min()

    def run(tvl, age, k, excl, every, window, cm):
        out, prev, held = [], set(), []
        for i, m in enumerate(pd.date_range(LO, HI - pd.Timedelta(days=1), freq="MS", tz="UTC")):
            pday = m - pd.Timedelta(days=1)
            if pday not in T.index:
                continue
            if i % every == 0:
                ok = [p for p in Y.columns if pd.notna(T.at[pday, p]) and T.at[pday, p] >= tvl and (pday - first[p]).days >= age]
                score = Y.loc[pday - pd.Timedelta(days=window - 1):pday, ok].mean()
                if excl:
                    rs = RS.loc[pday - pd.Timedelta(days=29):pday, ok].mean()
                    score = score[rs.reindex(score.index).fillna(0) <= 0.5]
                held = list(score.dropna().sort_values(ascending=False).index[:k])
                ch_n = len(set(held) ^ prev)
                prev = set(held)
            else:
                ch_n = 0
            alive = {p: True for p in held}
            for j, d in enumerate(pd.date_range(m, m + pd.offsets.MonthEnd(0), freq="D", tz="UTC")):
                r = []
                for p in held:
                    if not alive[p]:
                        r.append(0.0)
                        continue
                    t7 = T.loc[d - pd.Timedelta(days=7):d, p]
                    if len(t7) > 1 and t7.iloc[-1] < 0.5 * t7.max():
                        alive[p] = False
                        r.append(-0.20)
                        continue
                    v = Y.at[d, p] if d in Y.index else np.nan
                    r.append((v if pd.notna(v) else 0.0) / 100 / 365)
                out.append((d, (np.mean(r) if r else 0.0) - (ch_n * 5 / 10_000 * cm if j == 0 else 0.0)))
        return pd.Series(dict(out))
    report("R3 #204 stable-yield selection", {
        "V1 TVL>=5M age>=90 top5 30-d monthly": lambda cm: run(5e6, 90, 5, False, 1, 30, cm),
        "V2 TVL>=50M age>=365 top5": lambda cm: run(50e6, 365, 5, False, 1, 30, cm),
        "V3 TVL>=50M age>=365 top10 reward share<=50%": lambda cm: run(50e6, 365, 10, True, 1, 30, cm),
        "V4 TVL>=100M age>=365 top5 quarterly": lambda cm: run(100e6, 365, 5, False, 3, 30, cm),
        "V5 TVL>=20M age>=180 top10 by 90-d mean": lambda cm: run(20e6, 180, 10, False, 1, 90, cm),
    })


# ---------------- R4 new reward programmes
def r4():
    ch = pd.read_parquet("data/public/fallback_stable_charts.parquet")
    ch["day"] = ch["ts"].dt.floor("D")
    ch = ch.drop_duplicates(["pool", "day"]).sort_values(["pool", "day"])
    ch["rw"] = ch["apyReward"].fillna(0)
    ch["y"] = (ch["apyBase"].fillna(0) + 0.9 * ch["rw"]).clip(upper=1000)
    Y = ch.pivot(index="day", columns="pool", values="y")
    T = ch.pivot(index="day", columns="pool", values="tvlUsd").ffill(limit=3)
    first = ch.groupby("pool")["day"].min()
    ev = []
    for p, g in ch.groupby("pool"):
        g = g.set_index("day")
        rw = g["rw"]
        for i, (d, r) in enumerate(rw.items()):
            if r <= 0 or r > 1000 or not (LO - pd.Timedelta(days=1) <= d < HI - pd.Timedelta(days=1)):
                continue
            prev = rw[(rw.index < d) & (rw.index >= d - pd.Timedelta(days=14))]
            if i == 0 or (len(prev) > 0 and (prev <= 0).all()) or (len(prev) == 0 and i > 0):
                ev.append((d + pd.Timedelta(days=1), p, r, g.at[d, "tvlUsd"]))
    ev.sort()

    def run(tvl, age, rmin, size, cm):
        held, out, evi = {}, [], 0
        for d in DAYS:
            cost = 0.0
            for p in [p for p, (s, alive) in held.items() if (d - s).days >= 30 or not alive]:
                held.pop(p)
                cost += 5 / size * cm
            while evi < len(ev) and ev[evi][0] <= d:
                s, p, r, tv = ev[evi]
                evi += 1
                if s == d and len(held) < 5 and p not in held and tv >= tvl and (s - first[p]).days >= age and r >= rmin:
                    held[p] = (d, True)
                    cost += 5 / size * cm
            rets = []
            for p, (s, alive) in list(held.items()):
                t7 = T.loc[d - pd.Timedelta(days=7):d, p]
                if len(t7) > 1 and t7.iloc[-1] < 0.5 * t7.max():
                    rets.append(-0.20)
                    held[p] = (s, False)
                    continue
                v = Y.at[d, p] if d in Y.index else np.nan
                rets.append((v if pd.notna(v) else 0.0) / 100 / 365)
            out.append((d, sum(rets) / 5 + (5 - len(rets)) / 5 * PARK - cost))
        return pd.Series(dict(out))
    report("R4 #207 new reward programmes", {
        "V1 original (TVL>=1M at start)": lambda cm: run(1e6, 0, 0, 10_000, cm),
        "V2 start TVL >= $20M": lambda cm: run(20e6, 0, 0, 10_000, cm),
        "V3 V2 + pool age >= 180 d": lambda cm: run(20e6, 180, 0, 10_000, cm),
        "V4 V3 + reward >= 5%": lambda cm: run(20e6, 180, 5, 10_000, cm),
        "V5 V4 on $50,000": lambda cm: run(20e6, 180, 5, 50_000, cm),
    })


# ---------------- R5 hedged HYPE staking
def r5():
    f = pd.read_parquet("data/public/hedged_hlfunding.parquet")
    f["day"] = pd.to_datetime(f["t"], unit="s", utc=True).dt.floor("D")
    h = f[f.coin == "HYPE"].groupby("day").rate.sum().reindex(DAYS)

    def run(lev, thr, cm):
        trail = (h.rolling(30, min_periods=10).mean() * 365 * 100).shift(1)
        inpos = (trail > thr) if thr is not None else pd.Series(True, index=h.index)
        if thr is None:
            inpos[:] = True
        switch = inpos.astype(int).diff().abs().fillna(0)
        carry = (0.025 / 365 + h.fillna(0)) / (1 + 1 / lev)
        r = np.where(inpos, carry, PARK) - switch * 0.00145 * cm
        return pd.Series(r, index=h.index)
    report("R5 #276 hedged HYPE staking", {
        "V1 3x always": lambda cm: run(3, None, cm),
        "V2 2x always": lambda cm: run(2, None, cm),
        "V3 3x, in only if trailing funding > 8%": lambda cm: run(3, 8, cm),
        "V4 2x, in only if trailing funding > 8%": lambda cm: run(2, 8, cm),
        "V5 3x, exit only if trailing funding < 0": lambda cm: run(3, 0, cm),
    })


# ---------------- R6 Gains vaults
def r6():
    pools = pd.read_parquet("data/public/batch4_pools.parquet")
    ids = pools[pools["group"].astype(str).str.contains("225")].set_index("pool")
    ch = pd.read_parquet("data/public/batch4_charts.parquet")
    ch = ch[ch.pool.isin(ids.index)].copy()
    ch["day"] = ch["ts"].dt.floor("D")
    ch = ch.drop_duplicates(["pool", "day"])
    ch["y"] = (ch["apyBase"].fillna(0) + 0.9 * ch["apyReward"].fillna(0)).clip(upper=500) / 100 / 365
    Y = ch.pivot(index="day", columns="pool", values="y")
    T = ch.pivot(index="day", columns="pool", values="tvlUsd").ffill()
    big = ids.tvlUsd.idxmax()

    def top2(cm):
        out, prev = [], set()
        for m in pd.date_range(LO, HI - pd.Timedelta(days=1), freq="MS", tz="UTC"):
            sc = Y.loc[m - pd.Timedelta(days=90):m - pd.Timedelta(days=1)].mean().dropna().sort_values(ascending=False)
            held = list(sc.index[:2])
            n = len(set(held) ^ prev)
            prev = set(held)
            for j, d in enumerate(pd.date_range(m, m + pd.offsets.MonthEnd(0), freq="D", tz="UTC")):
                r = Y.loc[d, held].mean() if d in Y.index and held else np.nan
                out.append((d, (r if pd.notna(r) else 0.0) - (n * 5 / 10_000 * cm if j == 0 else 0)))
        return pd.Series(dict(out))
    w = T.div(T.sum(axis=1), axis=0)
    report("R6 #225 Gains vaults", {
        "V1 largest-TVL vault": lambda cm: Y[big],
        "V2 equal weight": lambda cm: Y.mean(axis=1),
        "V3 TVL-weighted": lambda cm: (Y * w).sum(axis=1, min_count=1),
        "V4 top 2 by trailing-90-d yield, monthly": top2,
        "V5 equal weight, vaults >= $1M TVL": lambda cm: Y.where(T >= 1e6).mean(axis=1),
    })


# ---------------- R7 conditional carry
def r7():
    hl = pd.read_parquet("data/public/hl_funding.parquet")
    hl["day"] = pd.to_datetime(hl["time"], unit="ms", utc=True).dt.floor("D")
    x = pd.read_parquet("data/public/hedged_hlfunding.parquet")
    x["day"] = pd.to_datetime(x["t"], unit="s", utc=True).dt.floor("D")
    coins = ["BTC", "ETH", "SOL", "HYPE", "BNB", "XRP", "DOGE", "LINK", "SUI", "AVAX", "PAXG"]
    D = pd.concat([hl[["coin", "day", "rate"]], x[["coin", "day", "rate"]]]).groupby(["coin", "day"]).rate.sum().unstack(0)
    D = D[[c for c in coins if c in D.columns]].reindex(DAYS)

    def run(k, thr, cm):
        out, prev = [], set()
        for m in pd.date_range(LO, HI - pd.Timedelta(days=1), freq="MS", tz="UTC"):
            tr = (D.loc[m - pd.Timedelta(days=30):m - pd.Timedelta(days=1)].mean() * 365 * 100).dropna().sort_values(ascending=False)
            held = [c for c in tr.index[:k] if tr[c] > thr]
            n = len(set(held) ^ prev)
            prev = set(held)
            for j, d in enumerate(pd.date_range(m, m + pd.offsets.MonthEnd(0), freq="D", tz="UTC")):
                slots = [(D.at[d, c] if pd.notna(D.at[d, c]) else 0.0) / (4 / 3) for c in held] + [PARK] * (k - len(held))
                out.append((d, np.mean(slots) - (n * 0.00145 / k * cm if j == 0 else 0)))
        return pd.Series(dict(out))
    report("R7 conditional carry (#216 / #217 / #57 family)", {
        "V1 k=3, T=0": lambda cm: run(3, 0, cm), "V2 k=3, T=10%": lambda cm: run(3, 10, cm),
        "V3 k=5, T=10%": lambda cm: run(5, 10, cm), "V4 k=1, T=15%": lambda cm: run(1, 15, cm),
        "V5 k=3, T=15%": lambda cm: run(3, 15, cm),
    })


if __name__ == "__main__":
    print("chosen = best year-1 variant; PASS needs year 1 >= 8%, year 2 >= 8%, year 2 with costs x1.5 >= 8%\n")
    for fn in (r1, r2, r3, r4, r5, r6, r7):
        try:
            fn()
        except Exception as e:  # noqa: BLE001
            print(f"{fn.__name__} crashed: {type(e).__name__}: {e}\n")

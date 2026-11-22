"""Walk-forward retest with large configuration grids (docs/PREREG_WALKFORWARD_20261122.md).

    uv run python scripts/walkforward_20261122.py | tee docs/jx_runs/walkforward_20261122.txt
    uv run python scripts/walkforward_20261122.py G1 G5    # selected grids only
"""
from __future__ import annotations

import itertools
import sys

import numpy as np
import pandas as pd

from scripts.fundgap_20261121 import hourly

LO, HI = pd.Timestamp("2024-11-01", tz="UTC"), pd.Timestamp("2026-11-01", tz="UTC")
DAYS = pd.date_range(LO, HI - pd.Timedelta(days=1), freq="D", tz="UTC")
OOS = pd.date_range("2025-05-01", "2026-10-01", freq="MS", tz="UTC")
SPLIT = pd.Timestamp("2026-02-01", tz="UTC")
PARK = 0.04 / 365
ann = lambda s: float(s.mean() * 365 * 100) if len(s) else float("nan")  # noqa: E731


def walk(series, switch_cost):
    """series: {cfg: daily Series on DAYS}. Each month pick best trailing-6-month mean; return OOS series, #switches, picks."""
    M = pd.DataFrame(series).reindex(DAYS).fillna(0.0)
    out, prev, sw, picks = [], None, 0, []
    for m in OOS:
        w = M.loc[m - pd.DateOffset(months=6):m - pd.Timedelta(days=1)].mean()
        best = w.idxmax()
        picks.append(best)
        seg = M.loc[m:m + pd.offsets.MonthEnd(0), best].copy()
        if prev is not None and best != prev:
            seg.iloc[0] -= switch_cost
            sw += 1
        prev = best
        out.append(seg)
    return pd.concat(out), sw, picks


def judge(name, build, switch_cost):
    """build(cost_mult) -> {cfg: Series}."""
    s1 = build(1.0)
    oos, sw, picks = walk(s1, switch_cost)
    h1, h2 = ann(oos[oos.index < SPLIT]), ann(oos[oos.index >= SPLIT])
    oos15, _, _ = walk(build(1.5), switch_cost * 1.5)
    allc = ann(oos15)
    full = pd.DataFrame(s1).reindex(DAYS)
    hind = full.mean().idxmax()
    ok = h1 >= 8 and h2 >= 8 and allc >= 8
    common = pd.Series(picks).value_counts().head(2)
    print(f"===== {name}: {len(s1)} configs")
    print(f"  walk-forward OOS 2025-05..2026-10: halves {h1:.2f}% / {h2:.2f}%; all 18 months with costs x1.5 {allc:.2f}%; switches {sw}")
    print(f"  most-picked configs: " + "; ".join(f"{k} ({v}x)" for k, v in common.items()))
    print(f"  (context only) best fixed config in hindsight: {hind} -> {ann(full[hind].dropna()):.2f}%/yr over 2024-11..2026-10")
    print(f"  VERDICT: {'PASS' if ok else 'FAIL'}\n", flush=True)


# ---------------------------------------------------------------- G1 funding gaps (vectorised)
def g1():
    df = pd.read_parquet("data/public/fundgap_funding.parquet")
    H = hourly(df[df.venue.isin(["hl", "dydx", "aevo"])])
    pairs = [("hl", "dydx"), ("hl", "aevo"), ("dydx", "aevo")]
    coins = sorted({c for (_, c) in H})
    inst, sig, gap = [], [], []
    for pi, (a, b) in enumerate(pairs):
        for c in coins:
            if (a, c) in H and (b, c) in H:
                g = (H[(a, c)] - H[(b, c)])
                dsum = g.resample("D").sum(min_count=1).reindex(DAYS)
                dmean = g.resample("D").mean().reindex(DAYS - pd.Timedelta(days=1))
                inst.append((pi, c))
                sig.append(dmean.to_numpy() * 8760 * 100)
                gap.append(dsum.fillna(0).to_numpy())
    S, G = np.array(sig).T, np.array(gap).T  # days x J
    PI = np.array([p for p, _ in inst])

    def sim(entry, exitb, leg, pairset, maxpos, cm):
        allowed = np.isin(PI, pairset)
        pos = np.zeros(S.shape[1])
        fee = leg * 2 * cm
        out = np.zeros(len(DAYS))
        for d in range(len(DAYS)):
            s = S[d]
            fin = np.isfinite(s)
            close = (pos != 0) & ((~fin) | (np.sign(np.nan_to_num(s)) != pos) | (np.abs(np.nan_to_num(s)) < exitb))
            pnl = -fee * close.sum()
            pos[close] = 0
            room = maxpos - int((pos != 0).sum())
            if room > 0:
                cand = np.where((pos == 0) & allowed & fin & (np.abs(np.nan_to_num(s)) >= entry))[0]
                if len(cand):
                    cand = cand[np.argsort(-np.abs(s[cand]))][:room]
                    pos[cand] = np.sign(s[cand])
                    pnl -= fee * len(cand)
            pnl += float((pos * G[d]).sum())
            out[d] = pnl / (maxpos * 2 / 3)
        return pd.Series(out, index=DAYS)
    psets = {"all3": [0, 1, 2], "noHLdYdX": [1, 2], "dYdXAevo": [2]}

    def build(cm):
        return {f"e{e}/x{x}/{'mk' if leg < 0.0004 else 'tk'}/{pn}/k{k}": sim(e, x, leg, ps, k, cm)
                for e, x, leg, (pn, ps), k in itertools.product((5, 10, 15, 20, 30), (0, 5, 10), (0.0005, 0.00015), psets.items(), (3, 5, 8))}
    judge("G1 #208 funding gaps", build, switch_cost=0.0005 * 4)


# ---------------------------------------------------------------- G2 GM pools
def g2():
    px = pd.read_parquet("data/public/wrappers_prices.parquet")
    px["day"] = pd.to_datetime(px["ts"], unit="s", utc=True).dt.floor("D")
    P = px.pivot_table(index="day", columns="token", values="price", aggfunc="last").sort_index().reindex(DAYS)
    f = pd.read_parquet("data/public/hedged_hlfunding.parquet")
    f["day"] = pd.to_datetime(f["t"], unit="s", utc=True).dt.floor("D")
    F = f.groupby(["coin", "day"])["rate"].sum()

    def run(h, cm):
        legs = []
        for gm, idx in (("GM_ETH", "ETH"), ("GM_BTC", "BTC")):
            rg, ri = np.log(P[gm]).diff(), np.log(P[idx]).diff()
            fd = F.loc[idx].reindex(DAYS).fillna(0)
            if h == "dyn":
                beta = (rg.rolling(30).cov(ri) / ri.rolling(30).var()).clip(0, 1.2).shift(1).fillna(0.5)
                legs.append((rg - beta * ri + beta * fd - beta.diff().abs().fillna(0) * 0.00045 * cm) / (1 + beta / 3))
            else:
                legs.append((rg - h * ri + h * fd) / (1 + h / 3))
        return pd.concat(legs, axis=1).mean(axis=1)
    judge("G2 #221 GMX GM pools", lambda cm: {f"h{h:.1f}": run(h, cm) for h in np.arange(0, 1.01, 0.1)} | {"dyn": run("dyn", cm)}, 0.001)


# ---------------------------------------------------------------- G3 family: stable-yield selection (vectorised)
def _sel_universe(ch):
    ch = ch.copy()
    ch["day"] = pd.to_datetime(ch["ts"], utc=True).dt.floor("D")
    ch = ch.drop_duplicates(["pool", "day"])
    ch["y"] = (ch["apyBase"].fillna(0) + 0.9 * ch["apyReward"].fillna(0)).clip(upper=1000)
    ch["rs"] = ch["apyReward"].fillna(0) / (ch["apyBase"].fillna(0) + ch["apyReward"].fillna(0)).replace(0, np.nan)
    Y = ch.pivot(index="day", columns="pool", values="y").reindex(DAYS)
    RS = ch.pivot(index="day", columns="pool", values="rs").reindex(DAYS)
    T = ch.pivot(index="day", columns="pool", values="tvlUsd").reindex(DAYS).ffill(limit=3)
    first = ch.groupby("pool")["day"].min().reindex(Y.columns)
    roll7 = T.rolling(8, min_periods=2).max()
    crash = (T < 0.5 * roll7).fillna(False)
    return Y, RS, T, first, crash


def _sel_run(U, tvl, age, k, window, excl, cm, fee=5 / 10_000):
    Y, RS, T, first, crash = U
    yv, cv = Y.to_numpy(), crash.to_numpy()
    out = np.zeros(len(DAYS))
    prev = set()
    for m in pd.date_range(LO, HI - pd.Timedelta(days=1), freq="MS", tz="UTC"):
        i0 = DAYS.get_loc(m)
        pday = m - pd.Timedelta(days=1)
        if pday < LO:
            continue
        tv = T.loc[pday].to_numpy()
        agev = (pday - first).dt.days.to_numpy()
        sc = Y.loc[pday - pd.Timedelta(days=window - 1):pday].mean().to_numpy()
        ok = (tv >= tvl) & (agev >= age) & np.isfinite(sc)
        if excl:
            ok &= np.nan_to_num(RS.loc[pday - pd.Timedelta(days=29):pday].mean().to_numpy()) <= 0.5
        idx = np.where(ok)[0]
        held = idx[np.argsort(-sc[idx])][:k]
        n = len(set(held) ^ prev)
        prev = set(held)
        i1 = DAYS.get_loc(min(m + pd.offsets.MonthEnd(0), DAYS[-1])) + 1
        if not len(held):
            out[i0:i1] = PARK
            continue
        seg_y = np.nan_to_num(yv[i0:i1, held]) / 100 / 365
        seg_c = cv[i0:i1, held]
        dead = np.cumsum(seg_c, axis=0) > 0
        first_crash = seg_c & (np.cumsum(seg_c, axis=0) == 1)
        r = np.where(dead, 0.0, seg_y)
        r = np.where(first_crash, -0.20, r)
        out[i0:i1] = r.mean(axis=1)
        out[i0] -= n * fee * cm
    return pd.Series(out, index=DAYS)


def g3():
    U = _sel_universe(pd.read_parquet("data/public/fallback_stable_charts.parquet"))
    judge("G3 #201-204 stable-yield selection", lambda cm: {
        f"tvl{int(t / 1e6)}M/age{a}/k{k}/w{w}/{'rs' if e else 'all'}": _sel_run(U, t, a, k, w, e, cm)
        for t, a, k, w, e in itertools.product((5e6, 20e6, 50e6, 100e6), (90, 180, 365), (3, 5, 10), (30, 90), (False, True))}, 10 / 10_000)


def g3b():
    pools = pd.read_parquet("data/public/batch4_pools.parquet")
    ch = pd.read_parquet("data/public/batch4_charts.parquet")
    us = {}
    for name, grp in (("224", ["224"]), ("227", ["227"]), ("both", ["224", "227"])):
        ids = pools.pool[pools["group"].astype(str).isin(grp) | pools["group"].astype(str).apply(lambda g: any(x in g for x in grp))]
        us[name] = _sel_universe(ch[ch.pool.isin(ids)])
    judge("G3b #224 stable-pair LPs / #227 savings", lambda cm: {
        f"{u}/tvl{int(t / 1e6)}M/k{k}/w{w}": _sel_run(us[u], t, 90, k, w, False, cm)
        for u, t, k, w in itertools.product(us, (5e6, 20e6, 50e6), (3, 5), (30, 90))}, 10 / 10_000)


def g3c():
    pools = pd.read_parquet("data/public/llama_pools_now.parquet")
    NEW = ["Monad", "Plasma", "Stable", "MegaETH", "Katana", "Hyperliquid L1", "Plume Mainnet", "Unichain", "Berachain", "Sonic", "Ink", "Soneium"]
    ch = pd.read_parquet("data/public/fallback_stable_charts.parquet")
    U = _sel_universe(ch[ch.pool.isin(set(pools.pool[pools.chain.isin(NEW)]))])
    judge("G3c #278 new-chain incentives", lambda cm: {
        f"tvl{int(t / 1e6)}M/k{k}/w{w}/age{a}": _sel_run(U, t, a, k, w, False, cm)
        for t, k, w, a in itertools.product((5e6, 20e6), (3, 5, 10), (30, 90), (30, 90))}, 10 / 10_000)


# ---------------------------------------------------------------- G4 new reward programmes
def g4():
    ch = pd.read_parquet("data/public/fallback_stable_charts.parquet")
    ch["day"] = ch["ts"].dt.floor("D")
    ch = ch.drop_duplicates(["pool", "day"]).sort_values(["pool", "day"])
    ch["rw"] = ch["apyReward"].fillna(0)
    ch["y"] = (ch["apyBase"].fillna(0) + 0.9 * ch["rw"]).clip(upper=1000)
    Y = ch.pivot(index="day", columns="pool", values="y").reindex(DAYS)
    T = ch.pivot(index="day", columns="pool", values="tvlUsd").reindex(DAYS).ffill(limit=3)
    crash = (T < 0.5 * T.rolling(8, min_periods=2).max()).fillna(False)
    first = ch.groupby("pool")["day"].min()
    ev = []
    for p, g in ch.groupby("pool"):
        g = g.set_index("day")
        rw = g["rw"]
        vals, idxs = rw.to_numpy(), rw.index
        for i in range(len(vals)):
            d, r = idxs[i], vals[i]
            if r <= 0 or r > 1000 or not (LO - pd.Timedelta(days=1) <= d < HI - pd.Timedelta(days=1)):
                continue
            prev = rw[(idxs < d) & (idxs >= d - pd.Timedelta(days=14))]
            if i == 0 or (len(prev) > 0 and (prev <= 0).all()) or (len(prev) == 0 and i > 0):
                ev.append((d + pd.Timedelta(days=1), p, r, g.at[d, "tvlUsd"], (d - first[p]).days))
    ev = pd.DataFrame(ev, columns=["start", "pool", "r", "tvl", "age"]).sort_values("start")
    yv, cv = Y.to_numpy(), crash.to_numpy()
    col = {p: i for i, p in enumerate(Y.columns)}

    def run(tvl, age, rmin, hold, cm):
        e = ev[(ev.tvl >= tvl) & (ev.age >= age) & (ev.r >= rmin)]
        out = np.full(len(DAYS), 0.0)
        slots = np.zeros(len(DAYS))
        active = []  # (end_index, col, start_index)
        es = {d: grp for d, grp in e.groupby("start")}
        for di, d in enumerate(DAYS):
            active = [a for a in active if a[0] > di]
            cost = 0.0
            for _, row in (es.get(d, pd.DataFrame()).iterrows() if d in es else []):
                if len(active) < 5 and all(a[1] != col[row.pool] for a in active):
                    active.append((di + hold, col[row.pool], di))
                    cost += 2 * 5 / 10_000 * cm
            r = 0.0
            for (_end, c, s0) in active:
                seg = cv[s0:di + 1, c]
                if seg.any():
                    r += (-0.20 if seg[-1] and seg.sum() == 1 else 0.0)
                else:
                    r += np.nan_to_num(yv[di, c]) / 100 / 365
            out[di] = r / 5 + (5 - len(active)) / 5 * PARK - cost
            slots[di] = len(active)
        return pd.Series(out, index=DAYS)
    judge("G4 #207 new reward programmes", lambda cm: {
        f"tvl{int(t / 1e6)}M/age{a}/r{r}/h{h}": run(t, a, r, h, cm)
        for t, a, r, h in itertools.product((1e6, 5e6, 20e6, 50e6), (0, 180, 365), (0, 3, 5, 10), (30, 60, 90))}, 10 / 10_000)


# ---------------------------------------------------------------- G5 hedged HYPE staking
def g5():
    f = pd.read_parquet("data/public/hedged_hlfunding.parquet")
    f["day"] = pd.to_datetime(f["t"], unit="s", utc=True).dt.floor("D")
    h = f[f.coin == "HYPE"].groupby("day").rate.sum().reindex(DAYS)

    def run(lev, thr, cm):
        trail = (h.rolling(30, min_periods=10).mean() * 365 * 100).shift(1)
        inpos = pd.Series(True, index=DAYS) if thr is None else (trail > thr).fillna(False)
        sw = inpos.astype(int).diff().abs().fillna(0)
        carry = (0.025 / 365 + h.fillna(0)) / (1 + 1 / lev)
        return pd.Series(np.where(inpos, carry, PARK), index=DAYS) - sw * 0.00145 * cm
    judge("G5 #276 hedged HYPE staking", lambda cm: {f"lev{l}/{'always' if t is None else 'gt' + str(t)}": run(l, t, cm)
                                                     for l, t in itertools.product((1.5, 2, 3), (None, 0, 5, 8, 12))}, 0.00145 * 2)


# ---------------------------------------------------------------- G6 Gains vaults
def g6():
    pools = pd.read_parquet("data/public/batch4_pools.parquet")
    ids = pools[pools["group"].astype(str).str.contains("225")].pool
    ch = pd.read_parquet("data/public/batch4_charts.parquet")
    ch = ch[ch.pool.isin(ids)].copy()
    ch["day"] = ch["ts"].dt.floor("D")
    ch = ch.drop_duplicates(["pool", "day"])
    ch["y"] = (ch["apyBase"].fillna(0) + 0.9 * ch["apyReward"].fillna(0)).clip(upper=500) / 100 / 365
    Y = ch.pivot(index="day", columns="pool", values="y").reindex(DAYS)
    T = ch.pivot(index="day", columns="pool", values="tvlUsd").reindex(DAYS).ffill()

    def run(k, wt, tmin, window, cm):
        out, prev = [], set()
        for m in pd.date_range(LO, HI - pd.Timedelta(days=1), freq="MS", tz="UTC"):
            pday = m - pd.Timedelta(days=1)
            if pday < LO:
                seg = pd.Series(PARK, index=pd.date_range(m, m + pd.offsets.MonthEnd(0), freq="D", tz="UTC"))
                out.append(seg)
                continue
            tv = T.loc[pday]
            sc = Y.loc[pday - pd.Timedelta(days=window - 1):pday].mean()
            okp = sc[(tv.reindex(sc.index) >= tmin) & sc.notna()].sort_values(ascending=False)
            held = list(okp.index if k == "all" else okp.index[:k])
            n = len(set(held) ^ prev)
            prev = set(held)
            dd = pd.date_range(m, min(m + pd.offsets.MonthEnd(0), DAYS[-1]), freq="D", tz="UTC")
            if not held:
                out.append(pd.Series(PARK, index=dd))
                continue
            seg = Y.loc[dd, held]
            w = (tv[held] / tv[held].sum()) if wt == "tvl" else pd.Series(1 / len(held), index=held)
            r = (seg.fillna(0) * w).sum(axis=1)
            r.iloc[0] -= n * 5 / 10_000 * cm
            out.append(r)
        return pd.concat(out).reindex(DAYS).fillna(0)
    judge("G6 #225 Gains vaults", lambda cm: {f"k{k}/{wt}/tmin{int(t / 1e6)}M/w{w}": run(k, wt, t, w, cm)
                                              for k, wt, t, w in itertools.product((1, 2, 3, "all"), ("eq", "tvl"), (0, 1e6, 2e6), (30, 90))}, 10 / 10_000)


# ---------------------------------------------------------------- G7 carry family
def g7():
    hl = pd.read_parquet("data/public/hl_funding.parquet")
    hl["day"] = pd.to_datetime(hl["time"], unit="ms", utc=True).dt.floor("D")
    x = pd.read_parquet("data/public/hedged_hlfunding.parquet")
    x["day"] = pd.to_datetime(x["t"], unit="s", utc=True).dt.floor("D")
    D = pd.concat([hl[["coin", "day", "rate"]], x[["coin", "day", "rate"]]]).groupby(["coin", "day"]).rate.sum().unstack(0).reindex(DAYS)
    unis = {"maj": ["BTC", "ETH", "SOL"], "all11": ["BTC", "ETH", "SOL", "HYPE", "BNB", "XRP", "DOGE", "LINK", "SUI", "AVAX", "PAXG"]}

    def run(u, k, thr, cm):
        cs = [c for c in unis[u] if c in D.columns]
        out, prev = [], set()
        for m in pd.date_range(LO, HI - pd.Timedelta(days=1), freq="MS", tz="UTC"):
            tr = (D.loc[m - pd.Timedelta(days=30):m - pd.Timedelta(days=1), cs].mean() * 365 * 100).dropna().sort_values(ascending=False)
            held = [c for c in tr.index[:k] if tr[c] > thr]
            n = len(set(held) ^ prev)
            prev = set(held)
            dd = pd.date_range(m, min(m + pd.offsets.MonthEnd(0), DAYS[-1]), freq="D", tz="UTC")
            seg = (D.loc[dd, held].fillna(0) / (4 / 3)).sum(axis=1) if held else pd.Series(0.0, index=dd)
            r = (seg + (k - len(held)) * PARK) / k
            r.iloc[0] -= n * 0.00145 / k * cm
            out.append(r)
        return pd.concat(out)
    judge("G7 carry family (#216/#217/#57)", lambda cm: {f"{u}/k{k}/T{t}": run(u, k, t, cm)
                                                         for u, k, t in itertools.product(unis, (1, 2, 3, 5), (0, 5, 10, 15, 20))}, 0.00145 * 2)


# ---------------------------------------------------------------- G8 hedged staking / farming, no churn
def g8():
    pools = pd.read_parquet("data/public/hedged_pools.parquet")
    ch = pd.read_parquet("data/public/hedged_charts.parquet")
    ch["day"] = ch["ts"].dt.floor("D")
    ch = ch.drop_duplicates(["pool", "day"])
    f = pd.read_parquet("data/public/hedged_hlfunding.parquet")
    f["day"] = pd.to_datetime(f["t"], unit="s", utc=True).dt.floor("D")
    F = f.groupby(["coin", "day"])["rate"].sum()
    stak = pools[pools.category.isin(["Liquid Staking", "Liquid Restaking"])]
    base = {}
    for fam in ("ETH", "SOL", "HYPE", "AVAX", "BNB"):
        q = stak[stak.coin == fam]
        if len(q):
            pid = q.sort_values("tvlUsd").pool.iloc[-1]
            g = ch[ch.pool == pid].set_index("day")
            base[fam] = ((g.apyBase.fillna(0) + 0.9 * g.apyReward.fillna(0)) / 100 / 365).reindex(DAYS), F.loc[fam].reindex(DAYS) if fam in F.index.get_level_values(0) else None

    def run(fam, rule, lev, cm):
        y, fd = base[fam]
        if fd is None:
            return pd.Series(np.nan, index=DAYS)
        trail = (fd.rolling(30, min_periods=10).mean() * 365 * 100).shift(1)
        hedge = pd.Series(True, index=DAYS) if rule == "always" else (trail > float(rule)).fillna(False)
        sw = hedge.astype(int).diff().abs().fillna(0)
        hedged = (y.fillna(0) + fd.fillna(0)) / (1 + 1 / lev)
        return pd.Series(np.where(hedge, hedged, PARK), index=DAYS) - sw * 0.00145 * cm  # unhedged periods park in stables (sell LST)

    def build(cm):
        d = {f"{fam}/{rule}/lev{lev}": run(fam, rule, lev, cm) for fam, rule, lev in itertools.product(base, ("always", "0", "5"), (2, 3))}
        return {k: v for k, v in d.items() if v.notna().any()}
    judge("G8 #212/#213 hedged staking (largest LST per family, no churn)", build, 0.00145 * 2 + 0.001)


if __name__ == "__main__":
    print("walk-forward: monthly pick of the best trailing-6-month config; OOS 2025-05..2026-10; PASS needs both OOS halves >= 8% and costs x1.5 >= 8%\n")
    grids = {"G1": g1, "G2": g2, "G3": g3, "G3b": g3b, "G3c": g3c, "G4": g4, "G5": g5, "G6": g6, "G7": g7, "G8": g8}
    for k in (sys.argv[1:] or grids):
        try:
            grids[k]()
        except Exception as e:  # noqa: BLE001
            import traceback
            print(f"{k} crashed: {type(e).__name__}: {e}")
            traceback.print_exc(limit=3)

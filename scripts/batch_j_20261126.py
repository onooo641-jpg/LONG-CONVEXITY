"""Batch J (#488-#492), exactly as docs/PREREG_BATCH_J_20261126.md defines it.

    uv run python -m scripts.batch_j_20261126 | tee docs/jx_runs/batch_j_20261126.txt
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from scripts.batch_d_20261126 import PUB, tstat

S1, S2, END = "2020-07-01", "2023-01-01", "2026-11-01"
FEE = 0.0009


def daily_close(path):
    k = pd.read_parquet(PUB / path)
    k = k[pd.to_datetime(k["t"], unit="s", utc=True).dt.hour == 23]
    k = k.assign(day=pd.to_datetime(k["t"], unit="s").dt.normalize())
    return k.pivot_table(index="day", columns="sym", values="close", aggfunc="last").sort_index()


def daily_funding(path):
    f = pd.read_parquet(PUB / path)
    ts = pd.to_datetime(f["t"], unit="s")
    return f.assign(day=ts.dt.normalize(), ts=ts)


def cz(name, col):
    d = pd.read_parquet(PUB / f"batchj_{name}.parquet")
    d["day"] = pd.to_datetime(d["t"], unit="s").dt.normalize()
    d["sym"] = d["symbol"].str.replace("_PERP.A", "", regex=False).str.replace(".6", "", regex=False)
    return d.pivot_table(index="day", columns="sym", values=col, aggfunc="last").sort_index()


def show(tag, x, lab):
    x = pd.Series(x, dtype=float)
    print(f"  {tag} {lab}: n {len(x)}, mean {x.mean():.3%}, t {tstat(x):.2f}, win {(x > 0).mean():.0%}")
    return len(x), x.mean(), tstat(x)


def capped_usd(ev, lo, hi, notional=45000, cap=3):
    e = ev[(ev["day"] >= lo) & (ev["day"] < hi)].sort_values("day")
    open_, tot = [], 0.0
    for r in e.itertuples():
        open_ = [x for x in open_ if x > r.day]
        if len(open_) < cap:
            tot += r.ret * notional
            open_.append(r.exit)
    return tot / ((pd.Timestamp(hi) - pd.Timestamp(lo)).days / 365.25)


def verdict(tag, s1, s2, s3, n_min, m_min, t3_min=2.0, s3_m_min=0.0):
    n1, m1, _ = s1
    if not n1 or not (m1 > 0):
        print(f"  VERDICT ({tag}): KILL")
        return False
    ok2 = s2[0] >= n_min and s2[1] >= m_min and s2[2] >= 2
    ok3 = s3 is not None and s3[1] > s3_m_min and s3[2] >= t3_min
    print(f"  VERDICT ({tag}): {'PASS' if ok2 and ok3 else 'FAIL'} (Stage 2 {'holds' if ok2 else 'fails'}, Stage 3 {'holds' if ok3 else 'fails'})")
    return ok2 and ok3


def part488(P, OI, alts, unseen):
    print("\n#### #488 OI-growth crowding (weekly: short top-quintile 7-day OI growth, long bottom quintile)")
    out = {}
    for uni_tag, uni in (("40 alts", alts), ("unseen 110", unseen)):
        rows = []
        for mon in pd.date_range("2020-07-06", END, freq="W-MON"):
            d, d0, d7 = mon - pd.Timedelta(days=1), mon - pd.Timedelta(days=8), mon + pd.Timedelta(days=6)
            if d not in OI.index or d0 not in OI.index or d7 not in P.index or d not in P.index:
                continue
            g, val = {}, {}
            for s in uni:
                if s not in OI or s not in P:
                    continue
                hist = OI[s].loc[:d].dropna()
                if len(hist) < 30 or pd.isna(OI.at[d0, s]) or OI.at[d0, s] <= 0 or pd.isna(P.at[d, s]) or pd.isna(P.at[d7, s]):
                    continue
                if OI.at[d, s] * P.at[d, s] < 5e6:
                    continue
                g[s] = OI.at[d, s] / OI.at[d0, s] - 1
            if len(g) < 10:
                continue
            gs = pd.Series(g).sort_values()
            q = max(1, len(gs) // 5)
            r = {s: P.at[d7, s] / P.at[d, s] - 1 for s in gs.index}
            rows.append({"day": mon, "ret": np.mean([r[s] for s in gs.index[:q]]) - np.mean([r[s] for s in gs.index[-q:]]) - 0.0018})
        out[uni_tag] = pd.DataFrame(rows)
    a, u = out["40 alts"], out["unseen 110"]
    s1 = show("#488", a[a["day"] < S2]["ret"], "Stage 1 (40 alts 2020-07..2022)")
    s2 = show("#488", a[a["day"] >= S2]["ret"], "Stage 2 (40 alts 2023..2026-10)")
    s3 = show("#488", u[u["day"] >= S2]["ret"], "Stage 3 (unseen 110, 2023..2026-10)") if len(u) else None
    verdict("#488", s1, s2, s3, 100, 1e-9)
    yrs = (pd.Timestamp(END) - pd.Timestamp(S2)).days / 365.25
    print(f"  $/yr at $22.5K per side (Stage 2): ${a[a['day'] >= S2]['ret'].sum() * 22500 / yrs:,.0f}")
    return out


def coin_events(P, uni, cond, hold, side, extra=None):
    rows = []
    for s in uni:
        if s not in P:
            continue
        p = P[s].dropna()
        idx = p.index
        busy = None
        for i in range(1, len(idx) - hold):
            d = idx[i]
            if busy is not None and d < busy:
                continue
            if not cond(s, d, p, i):
                continue
            ex = idx[i + hold]
            if (ex - d).days != hold:
                continue
            r = side * (p.iloc[i + hold] / p.iloc[i] - 1)
            if extra is not None:
                r += extra(s, d, ex)
            rows.append({"day": d, "exit": ex, "sym": s, "ret": r - (FEE if extra is None else 2 * FEE)})
            busy = ex
    return pd.DataFrame(rows)


def stage_report(tag, ev_a, ev_u, n_min, m_min):
    def clus(e, lo, hi):
        e = e[(e["day"] >= lo) & (e["day"] < hi)] if len(e) else e
        return e.groupby("day")["ret"].mean() if len(e) else pd.Series(dtype=float)
    s1 = show(tag, clus(ev_a, S1, S2), "Stage 1 (40 alts 2020-07..2022, per day)")
    s2 = show(tag, clus(ev_a, S2, END), "Stage 2 (40 alts 2023..2026-10, per day)")
    s3 = show(tag, clus(ev_u, S2, END), "Stage 3 (unseen 110 2023..2026-10, per day)")
    ok = verdict(tag, s1, s2, s3, n_min, m_min)
    if len(ev_a):
        print(f"  $/yr at $45K, <= 3 open (Stage 2): ${capped_usd(ev_a, S2, END):,.0f}; raw events S2 {((ev_a['day'] >= S2) & (ev_a['day'] < END)).sum()}")
    return ok


def part489(P, OI, F, alts, unseen):
    print("\n#### #489 crowded-funding short (daily funding >= 0.05%/settlement and OI at a 30-day high -> short 7 days vs BTC)")
    fd = F.groupby(["sym", "day"])["rate"].mean()
    fs = {s: g.set_index("ts")["rate"].sort_index() for s, g in F.groupby("sym")}
    btc = P["BTCUSDT"]

    def cond(s, d, p, i):
        if s == "BTCUSDT" or s not in OI or d not in OI.index:
            return False
        v = fd.get((s, d))
        if v is None or v < 0.0005:
            return False
        w = OI[s].loc[d - pd.Timedelta(days=29):d].dropna()
        return len(w) >= 25 and OI.at[d, s] >= w.max()

    def extra(s, d, ex):
        a, b = d + pd.Timedelta(days=1), ex + pd.Timedelta(days=1)
        if d not in btc.index or ex not in btc.index or pd.isna(btc[d]) or pd.isna(btc[ex]):
            return np.nan
        cf = fs[s][(fs[s].index > a) & (fs[s].index <= b)].sum() if s in fs else 0.0
        bf = fs["BTCUSDT"][(fs["BTCUSDT"].index > a) & (fs["BTCUSDT"].index <= b)].sum()
        return (btc[ex] / btc[d] - 1) + cf - bf
    ea = coin_events(P, alts, cond, 7, -1, extra).dropna()
    eu = coin_events(P, unseen, cond, 7, -1, extra).dropna()
    stage_report("#489", ea, eu, 30, 0.01)


def part490(P, OIb, OIy):
    print("\n#### #490 aggregate leverage extreme (BTC coin-unit OI Binance+Bybit z >= 2 after a 7-day rally -> short BTC 7 days)")
    res = {}
    for coin in ("BTCUSDT", "ETHUSDT"):
        if coin not in OIb or coin not in OIy:
            print(f"  {coin}: no OI data")
            continue
        oi = (OIb[coin] + OIy[coin]).dropna()
        p = P[coin].dropna()
        rows, busy = [], None
        for d in oi.index:
            if busy is not None and d < busy:
                continue
            w = oi.loc[d - pd.Timedelta(days=90):d - pd.Timedelta(days=1)]
            if len(w) < 80 or w.std() <= 0:
                continue
            z = (oi[d] - w.mean()) / w.std()
            d7, e = d - pd.Timedelta(days=7), d + pd.Timedelta(days=7)
            if z < 2 or d7 not in p.index or d not in p.index or e not in p.index or not (p[d] / p[d7] - 1 > 0):
                continue
            rows.append({"day": d, "exit": e, "ret": -(p[e] / p[d] - 1) - FEE})
            busy = e
        res[coin] = pd.DataFrame(rows)
    b = res.get("BTCUSDT", pd.DataFrame(columns=["day", "ret"]))
    e = res.get("ETHUSDT", pd.DataFrame(columns=["day", "ret"]))
    s1 = show("#490", b[b["day"] < S2]["ret"] if len(b) else [], "Stage 1 (BTC 2020-07..2022)")
    s2 = show("#490", b[(b["day"] >= S2) & (b["day"] < END)]["ret"] if len(b) else [], "Stage 2 (BTC 2023..2026-10)")
    s3 = show("#490", e[(e["day"] >= S2) & (e["day"] < END)]["ret"] if len(e) else [], "Stage 3 (ETH 2023..2026-10)")
    verdict("#490", s1, s2, s3, 10, 0.01, t3_min=1.5)
    if len(b):
        yrs = (pd.Timestamp(END) - pd.Timestamp(S2)).days / 365.25
        print(f"  $/yr at $45K (Stage 2): ${b[(b['day'] >= S2) & (b['day'] < END)]['ret'].sum() * 45000 / yrs:,.0f}")


def part491_492(P, OI, LQ, alts, unseen):
    print("\n#### #491 OI flush rebound (family 1: OI -20% and price -8% on the day -> long 3 days)")

    def c491(s, d, p, i):
        if s not in OI or d not in OI.index:
            return False
        d0 = p.index[i - 1]
        if (d - d0).days != 1 or d0 not in OI.index or pd.isna(OI.at[d0, s]) or OI.at[d0, s] <= 0 or pd.isna(OI.at[d, s]):
            return False
        return OI.at[d, s] / OI.at[d0, s] - 1 <= -0.20 and p.iloc[i] / p.iloc[i - 1] - 1 <= -0.08
    stage_report("#491", coin_events(P, alts, c491, 3, 1), coin_events(P, unseen, c491, 3, 1), 30, 0.01)
    print("\n#### #492 short-squeeze fade (family 1 mirror: shorts liquidated >= 2% of OI value and price +10% -> short 3 days)")

    def c492(s, d, p, i):
        if s not in OI or s not in LQ or d not in LQ.index:
            return False
        d0 = p.index[i - 1]
        if (d - d0).days != 1 or d0 not in OI.index or pd.isna(OI.at[d0, s]) or pd.isna(LQ.at[d, s]):
            return False
        return LQ.at[d, s] >= 0.02 * OI.at[d0, s] * p.iloc[i - 1] and p.iloc[i] / p.iloc[i - 1] - 1 >= 0.10
    stage_report("#492", coin_events(P, alts, c492, 3, -1), coin_events(P, unseen, c492, 3, -1), 30, 0.01)


def bybit_check(alts, unseen):
    print("\n#### Bybit second-venue check (reported only; Bybit OHLCV/OI/liquidations, all bases, 2023..2026-10)")
    try:
        PB, OIy, LQy = cz("cz_ohlcv_bybit", "c"), cz("cz_oi_bybit", "c"), cz("cz_liq_bybit", "s")
    except Exception as e:  # noqa: BLE001
        print(f"  no Bybit data ({e})")
        return
    uni = [s for s in alts + unseen if s in PB]
    for tag, cond, side in (("#491 Bybit", "flush", 1), ("#492 Bybit", "squeeze", -1)):
        def c(s, d, p, i, kind=cond):
            d0 = p.index[i - 1]
            if s not in OIy or d not in OIy.index or d0 not in OIy.index or (d - d0).days != 1:
                return False
            o0, o1 = OIy.at[d0, s], OIy.at[d, s]
            if pd.isna(o0) or pd.isna(o1) or o0 <= 0:
                return False
            r = p.iloc[i] / p.iloc[i - 1] - 1
            if kind == "flush":
                return o1 / o0 - 1 <= -0.20 and r <= -0.08
            lq = LQy.at[d, s] if (s in LQy and d in LQy.index) else np.nan
            return not pd.isna(lq) and lq >= 0.02 * o0 * p.iloc[i - 1] and r >= 0.10
        ev = coin_events(PB, uni, c, 3, side)
        ev = ev[(ev["day"] >= S2) & (ev["day"] < END)] if len(ev) else ev
        show(tag, ev.groupby("day")["ret"].mean() if len(ev) else [], "2023..2026-10 (per day)")


def main():
    print("===== Batch J (#488-#492)  docs/PREREG_BATCH_J_20261126.md")
    P = pd.concat([daily_close("batchd_alts_1h.parquet"), daily_close("batchh2_unseen_1h.parquet")], axis=1)
    P = P.loc[:, ~P.columns.duplicated()]
    F = pd.concat([daily_funding("batchd_alts_funding.parquet"), daily_funding("batchh2_unseen_funding.parquet")], ignore_index=True)
    OI, LQ = cz("cz_oi_binance", "c"), cz("cz_liq_binance", "s")
    alts = sorted(pd.read_parquet(PUB / "batchd_alts_1h.parquet")["sym"].unique())
    unseen = sorted(pd.read_parquet(PUB / "batchh2_unseen_funding.parquet")["sym"].unique())
    print(f"  prices {P.shape[1]} symbols; Binance OI {OI.shape[1]} symbols ({OI.index.min():%Y-%m-%d}..{OI.index.max():%Y-%m-%d}); liquidations {LQ.shape[1]}")
    part488(P, OI, alts, unseen)
    part489(P, OI, F, alts, unseen)
    part490(P, OI, cz("cz_oi_bybit", "c"))
    part491_492(P, OI, LQ, alts, unseen)
    bybit_check(alts, unseen)


if __name__ == "__main__":
    main()

"""Batch K part 2 (#496-#499), exactly as docs/PREREG_BATCH_K2_20261126.md defines it.

    uv run python -m scripts.batch_k2_20261126 | tee docs/jx_runs/batch_k2_20261126.txt
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from scripts.batch_d_20261126 import PUB, tstat
from scripts.batch_g_20261126 import at, hourly

FEE = 0.0009
END = "2026-11-01"


def show(tag, x, lab):
    x = pd.Series(x, dtype=float).dropna()
    print(f"  {tag} {lab}: n {len(x)}, mean {x.mean():.3%}, t {tstat(x):.2f}, win {(x > 0).mean():.0%}")
    return len(x), x.mean(), tstat(x)


def verdict(tag, s1, s2, s3, n2, m2, t3=2.0):
    if not s1[0] or not (s1[1] > 0):
        print(f"  VERDICT ({tag}): KILL")
        return
    ok2 = s2[0] >= n2 and s2[1] >= m2 and s2[2] >= 2
    ok3 = s3 is None or (s3[1] > 0 and s3[2] >= t3)
    print(f"  VERDICT ({tag}): {'PASS' if ok2 and ok3 else 'FAIL'} (Stage 2 {'holds' if ok2 else 'fails'}, Stage 3 {'holds' if ok3 else 'fails'})")


def part496():
    print("\n#### #496 Ethena hedge flows (USDe supply day-over-day <= -1.5% -> long, >= +1.5% -> short, next day 00:00 UTC, 2 days)")
    p = PUB / "batchk2_usde_supply.parquet"
    if not p.exists():
        print("  data not fetched yet (ubatchk2)")
        return
    u = pd.read_parquet(p)
    s = pd.Series(u["supply"].to_numpy(), index=pd.to_datetime(u["t"], unit="s", utc=True).dt.normalize()).sort_index()
    s = s[~s.index.duplicated()]
    s = s[s > 1e8]  # ignore the launch weeks below $100M
    d = s.pct_change().dropna()
    out = {}
    for coin in ("ETHUSDT", "BTCUSDT"):
        x = hourly(coin)
        rows, busy = [], None
        for day, ch in d.items():
            if abs(ch) < 0.015:
                continue
            a = day + pd.Timedelta(days=1)
            if busy is not None and a < busy:
                continue
            b = a + pd.Timedelta(days=2)
            p0, p1 = at(x, a), at(x, b)
            if p0 is None or p1 is None:
                continue
            side = 1 if ch < 0 else -1
            rows.append({"day": a.tz_localize(None), "ret": side * (p1 / p0 - 1) - FEE})
            busy = b
        out[coin] = pd.DataFrame(rows)
    e, b = out["ETHUSDT"], out["BTCUSDT"]
    s1 = show("#496", e[(e["day"] >= "2024-03-01") & (e["day"] < "2025-01-01")]["ret"], "Stage 1 (ETH 2024-03..2024-12)")
    s2 = show("#496", e[(e["day"] >= "2025-01-01") & (e["day"] < END)]["ret"], "Stage 2 (ETH 2025-01..2026-10)")
    s3 = show("#496", b[(b["day"] >= "2025-01-01") & (b["day"] < END)]["ret"], "Stage 3 (BTC 2025-01..2026-10)")
    verdict("#496", s1, s2, s3, 20, 0.005, t3=1.5)
    yrs = (pd.Timestamp(END) - pd.Timestamp("2025-01-01")).days / 365.25
    print(f"  $/yr at $45K (Stage 2): ${e[(e['day'] >= '2025-01-01') & (e['day'] < END)]['ret'].sum() * 45000 / yrs:,.0f}")


def last_friday(y, m):
    d = pd.Timestamp(y, m, 1) + pd.offsets.MonthEnd(0)
    while d.weekday() != 4:
        d -= pd.Timedelta(days=1)
    return d


def part497():
    print("\n#### #497 CME basis-trade unwind (annualised basis falls >= 5 points over 5 days -> short 5 days)")
    p = PUB / "batchk2_yahoo_1d.parquet"
    if not p.exists():
        print("  data not fetched yet (ubatchk2)")
        return
    y = pd.read_parquet(p)
    y["day"] = pd.to_datetime(y["t"], unit="s", utc=True).dt.tz_convert("America/New_York").dt.normalize().dt.tz_localize(None)
    Y = y.drop_duplicates(["sym", "day"]).pivot(index="day", columns="sym", values="close").sort_index()
    out = {}
    for fut, spot in (("BTC=F", "BTC-USD"), ("ETH=F", "ETH-USD")):
        if fut not in Y or spot not in Y:
            out[fut] = pd.DataFrame(columns=["day", "ret"])
            continue
        f, s = Y[fut].dropna(), Y[spot].dropna()
        days = f.index.intersection(s.index)
        basis = {}
        for d in days:
            ex = last_friday(d.year, d.month)
            if d > ex:
                nm = d + pd.offsets.MonthBegin(1)
                ex = last_friday(nm.year, nm.month)
            prev = last_friday((d - pd.offsets.MonthBegin(1)).year, (d - pd.offsets.MonthBegin(1)).month)
            if min(abs((ex - d).days), abs((d - prev).days)) <= 3:
                continue
            basis[d] = (f[d] / s[d] - 1) * 365 / max((ex - d).days, 1) * 100
        b = pd.Series(basis).sort_index()
        rows, busy = [], None
        bi = list(b.index)
        for i in range(5, len(bi)):
            d = bi[i]
            if busy is not None and d < busy:
                continue
            if b.iloc[i] - b.iloc[i - 5] > -5:
                continue
            e = d + pd.Timedelta(days=5)
            if d not in s.index or e not in s.index:
                continue
            rows.append({"day": d, "ret": -(s[e] / s[d] - 1) - FEE})
            busy = e
        out[fut] = pd.DataFrame(rows)
    bt, et = out["BTC=F"], out["ETH=F"]
    s1 = show("#497", bt[(bt["day"] >= "2021-01-01") & (bt["day"] < "2024-01-01")]["ret"] if len(bt) else [], "Stage 1 (BTC 2021..2023)")
    s2 = show("#497", bt[(bt["day"] >= "2024-01-01") & (bt["day"] < END)]["ret"] if len(bt) else [], "Stage 2 (BTC 2024..2026-10)")
    s3 = show("#497", et[(et["day"] >= "2024-01-01") & (et["day"] < END)]["ret"] if len(et) else [], "Stage 3 (ETH 2024..2026-10)")
    verdict("#497", s1, s2, s3, 15, 0.005, t3=1.5)
    if len(bt):
        yrs = (pd.Timestamp(END) - pd.Timestamp("2024-01-01")).days / 365.25
        print(f"  $/yr at $45K (Stage 2): ${bt[(bt['day'] >= '2024-01-01') & (bt['day'] < END)]['ret'].sum() * 45000 / yrs:,.0f}")


def cz(name, col, strip):
    d = pd.read_parquet(PUB / name)
    d["day"] = pd.to_datetime(d["t"], unit="s").dt.normalize()
    d["base"] = d["symbol"].str.replace(strip, "", regex=False)
    return d.pivot_table(index="day", columns="base", values=col, aggfunc="last").sort_index()


def part498():
    print("\n#### #498 Hyperliquid retail funding premium (weekly: short top quintile of HL - Binance 7-day funding, long bottom)")
    need = [PUB / f"batchk2_{n}.parquet" for n in ("k2_fund_hl", "k2_ohlcv_hl", "k2_fund_binance")]
    if not all(p.exists() for p in need):
        print("  data not fetched yet (Coinalyze --k2)")
        return
    FH, PH, FB = cz(need[0].name, "c", ".H"), cz(need[1].name, "c", ".H"), cz(need[2].name, "c", "USDT_PERP.A")
    # unit check on BTC (mechanical): Hyperliquid funds hourly, Binance every 8 h; put both on a per-8h basis
    k = 1.0
    if "BTC" in FH and "BTC" in FB:
        mh, mb = FH["BTC"].abs().median(), FB["BTC"].abs().median()
        k = 8.0 if mh > 0 and mb / mh > 4 else 1.0
        print(f"  unit check: median |BTC funding| HL {mh:.5f}, Binance {mb:.5f} -> HL x{k:g} to per-8h")
    FH = FH * k
    alts = {s[:-4] for s in pd.read_parquet(PUB / "batchd_alts_1h.parquet")["sym"].unique()}
    unseen = {s[:-4] for s in pd.read_parquet(PUB / "batchh2_unseen_funding.parquet")["sym"].unique()}
    res = {}
    for tag, uni in (("a", alts), ("u", unseen)):
        coins = [c for c in FH.columns if c in uni and c in FB.columns and c in PH.columns]
        rows = []
        for mon in pd.date_range("2024-10-14", END, freq="W-MON"):
            w0, w1, e = mon - pd.Timedelta(days=7), mon - pd.Timedelta(days=1), mon + pd.Timedelta(days=6)
            prem, ret = {}, {}
            for c in coins:
                h, b = FH[c].loc[w0:w1].dropna(), FB[c].loc[w0:w1].dropna()
                if len(h) < 5 or len(b) < 5 or w1 not in PH.index or e not in PH.index or pd.isna(PH.at[w1, c]) or pd.isna(PH.at[e, c]):
                    continue
                prem[c], ret[c] = h.mean() - b.mean(), PH.at[e, c] / PH.at[w1, c] - 1
            if len(prem) < 10:
                continue
            g = pd.Series(prem).sort_values()
            q = max(1, len(g) // 5)
            rows.append({"day": mon, "ret": np.mean([ret[c] for c in g.index[:q]]) - np.mean([ret[c] for c in g.index[-q:]]) - 0.0018,
                         "n": len(g)})
        res[tag] = pd.DataFrame(rows)
    a, u = res["a"], res["u"]
    s1 = show("#498", a[a["day"] < "2025-07-01"]["ret"] if len(a) else [], "Stage 1 (40-alt coins 2024-10..2025-06)")
    s2 = show("#498", a[a["day"] >= "2025-07-01"]["ret"] if len(a) else [], "Stage 2 (40-alt coins 2025-07..2026-10)")
    s3 = show("#498", u[u["day"] >= "2025-07-01"]["ret"] if len(u) else [], "Stage 3 (unseen coins 2025-07..2026-10)")
    verdict("#498", s1, s2, s3, 50, 1e-9)
    if len(a):
        yrs = (pd.Timestamp(END) - pd.Timestamp("2025-07-01")).days / 365.25
        print(f"  $/yr at $22.5K per side (Stage 2): ${a[a['day'] >= '2025-07-01']['ret'].sum() * 22500 / yrs:,.0f}")


def part499():
    print("\n#### #499 crowded-funding short, re-test of #489 on Bybit (funding >= 0.05%/settlement and OI at a 30-day high -> short 7 days vs BTC)")
    pf = PUB / "batchk2_k2_fund_bybit.parquet"
    if not pf.exists():
        print("  data not fetched yet (Coinalyze --k2)")
        return
    F = cz(pf.name, "c", "USDT.6")
    OI = cz("batchj_cz_oi_bybit.parquet", "c", "USDT.6")
    P = cz("batchj_cz_ohlcv_bybit.parquet", "c", "USDT.6")
    if "BTC" not in P:
        print("  no Bybit BTC prices")
        return
    btc, fb = P["BTC"], F.get("BTC")
    rows = []
    for c in [x for x in F.columns if x != "BTC" and x in OI.columns and x in P.columns]:
        busy = None
        for d in F.index:
            if busy is not None and d < busy:
                continue
            v = F.at[d, c]
            if pd.isna(v) or v < 0.05 or d not in OI.index or pd.isna(OI.at[d, c]):
                continue
            w = OI[c].loc[d - pd.Timedelta(days=29):d].dropna()
            if len(w) < 25 or OI.at[d, c] < w.max():
                continue
            e = d + pd.Timedelta(days=7)
            if d not in P.index or e not in P.index or any(pd.isna(z) for z in (P.at[d, c], P.at[e, c], btc.get(d), btc.get(e))):
                continue
            hold = pd.date_range(d + pd.Timedelta(days=1), e)
            cf = 3 * F[c].reindex(hold).fillna(0).sum() / 100
            bf = 3 * (fb.reindex(hold).fillna(0).sum() / 100 if fb is not None else 0.0)
            r = -(P.at[e, c] / P.at[d, c] - 1) + (btc[e] / btc[d] - 1) + cf - bf - 0.0018
            rows.append({"day": d, "exit": e, "ret": r})
            busy = e
    ev = pd.DataFrame(rows)
    if ev.empty:
        print("  no events")
        return
    c1 = ev[(ev["day"] >= "2021-01-01") & (ev["day"] < "2023-01-01")].groupby("day")["ret"].mean()
    c2 = ev[(ev["day"] >= "2023-01-01") & (ev["day"] < END)].groupby("day")["ret"].mean()
    s1 = show("#499", c1, "Stage 1 (Bybit 2021..2022, per day)")
    s2 = show("#499", c2, "Stage 2 (Bybit 2023..2026-10, per day)")
    verdict("#499", s1, s2, None, 30, 0.01)
    e2 = ev[(ev["day"] >= "2023-01-01") & (ev["day"] < END)].sort_values("day")
    open_, tot = [], 0.0
    for r in e2.itertuples():
        open_ = [x for x in open_ if x > r.day]
        if len(open_) < 3:
            tot += r.ret * 45000
            open_.append(r.exit)
    print(f"  $/yr at $45K, <= 3 open (Stage 2): ${tot / ((pd.Timestamp(END) - pd.Timestamp('2023-01-01')).days / 365.25):,.0f}")


def part500():
    print("\n#### #500 hedger-paid carry on Hyperliquid (HL funding <= -0.03%/8h -> long coin, short BTC, 7 days)")
    need = [PUB / f"batchk2_{n}.parquet" for n in ("k2_fund_hl", "k2_ohlcv_hl", "k2_fund_binance")]
    if not all(x.exists() for x in need):
        print("  data not fetched yet (Coinalyze --k2)")
        return
    FH, PH, FB = cz(need[0].name, "c", ".H"), cz(need[1].name, "c", ".H"), cz(need[2].name, "c", "USDT_PERP.A")
    k = 8.0 if FH["BTC"].abs().median() > 0 and FB["BTC"].abs().median() / FH["BTC"].abs().median() > 4 else 1.0
    FH = FH * k  # per-8h, in %
    if "BTC" not in PH:
        print("  no HL BTC prices")
        return
    btc, fbtc = PH["BTC"], FH["BTC"]
    rows = []
    for c in [x for x in FH.columns if x != "BTC" and x in PH.columns]:
        busy = None
        for d in FH.index:
            if busy is not None and d < busy:
                continue
            v = FH.at[d, c]
            if pd.isna(v) or v > -0.03:
                continue
            e = d + pd.Timedelta(days=7)
            if any(pd.isna(z) for z in (PH[c].get(d, np.nan), PH[c].get(e, np.nan), btc.get(d, np.nan), btc.get(e, np.nan))):
                continue
            hold = pd.date_range(d + pd.Timedelta(days=1), e)
            cf = -3 * FH[c].reindex(hold).fillna(0).sum() / 100 + 3 * fbtc.reindex(hold).fillna(0).sum() / 100
            rows.append({"day": d, "exit": e, "ret": (PH[c][e] / PH[c][d] - 1) - (btc[e] / btc[d] - 1) + cf - 0.0018})
            busy = e
    ev = pd.DataFrame(rows)
    c1 = ev[(ev["day"] >= "2024-10-01") & (ev["day"] < "2025-07-01")].groupby("day")["ret"].mean() if len(ev) else []
    c2 = ev[(ev["day"] >= "2025-07-01") & (ev["day"] < END)].groupby("day")["ret"].mean() if len(ev) else []
    s1 = show("#500", c1, "Stage 1 (HL 2024-10..2025-06, per day)")
    s2 = show("#500", c2, "Stage 2 (HL 2025-07..2026-10, per day)")
    # Stage 3: Binance archive, 110 unseen perps, 2023-01..2026-10
    k1 = pd.read_parquet(PUB / "batchh2_unseen_1h.parquet")
    k1 = k1[pd.to_datetime(k1["t"], unit="s", utc=True).dt.hour == 23].assign(day=lambda z: pd.to_datetime(z["t"], unit="s").dt.normalize())
    PB = k1.pivot_table(index="day", columns="sym", values="close", aggfunc="last")
    kb = pd.read_parquet(PUB / "batchd_alts_1h.parquet")
    kb = kb[(kb["sym"] == "BTCUSDT") & (pd.to_datetime(kb["t"], unit="s", utc=True).dt.hour == 23)]
    bb = pd.Series(kb["close"].to_numpy(), index=pd.to_datetime(kb["t"], unit="s").dt.normalize()).sort_index()
    bb = bb[~bb.index.duplicated()]
    fu = pd.read_parquet(PUB / "batchh2_unseen_funding.parquet").assign(day=lambda z: pd.to_datetime(z["t"], unit="s").dt.normalize())
    fdm = fu.groupby(["day", "sym"])["rate"].mean().unstack()
    fsum = fu.groupby(["day", "sym"])["rate"].sum().unstack()
    fa = pd.read_parquet(PUB / "batchd_alts_funding.parquet")
    fa = fa[fa["sym"] == "BTCUSDT"].assign(day=lambda z: pd.to_datetime(z["t"], unit="s").dt.normalize())
    fbs = fa.groupby("day")["rate"].sum()
    rows3 = []
    for c in [x for x in fdm.columns if x in PB.columns]:
        busy = None
        for d in fdm.index:
            if d < pd.Timestamp("2023-01-01") or d >= pd.Timestamp(END) or (busy is not None and d < busy):
                continue
            v = fdm.at[d, c]
            if pd.isna(v) or v > -0.0003:
                continue
            e = d + pd.Timedelta(days=7)
            if any(pd.isna(z) for z in (PB[c].get(d, np.nan), PB[c].get(e, np.nan), bb.get(d, np.nan), bb.get(e, np.nan))):
                continue
            hold = pd.date_range(d + pd.Timedelta(days=1), e)
            cf = -fsum[c].reindex(hold).fillna(0).sum() + fbs.reindex(hold).fillna(0).sum()
            rows3.append({"day": d, "ret": (PB[c][e] / PB[c][d] - 1) - (bb[e] / bb[d] - 1) + cf - 0.0018})
            busy = e
    e3 = pd.DataFrame(rows3)
    s3 = show("#500", e3.groupby("day")["ret"].mean() if len(e3) else [], "Stage 3 (Binance unseen 110, 2023..2026-10, per day)")
    verdict("#500", s1, s2, s3, 20, 0.01)
    if len(ev):
        e2 = ev[(ev["day"] >= "2025-07-01") & (ev["day"] < END)].sort_values("day")
        open_, tot = [], 0.0
        for r in e2.itertuples():
            open_ = [x for x in open_ if x > r.day]
            if len(open_) < 3:
                tot += r.ret * 45000
                open_.append(r.exit)
        print(f"  $/yr at $45K, <= 3 open (Stage 2): ${tot / ((pd.Timestamp(END) - pd.Timestamp('2025-07-01')).days / 365.25):,.0f}")


def main():
    print("===== Batch K part 2 (#496-#499)  docs/PREREG_BATCH_K2_20261126.md")
    part496()
    part497()
    part498()
    part499()
    part500()


if __name__ == "__main__":
    main()

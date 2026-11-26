"""Batch K (#493-#495), exactly as docs/PREREG_BATCH_K_20261126.md defines it.

    uv run python -m scripts.batch_k_20261126 | tee docs/jx_runs/batch_k_20261126.txt
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from scripts.batch_d_20261126 import PUB, tstat
from scripts.batch_g_20261126 import at, fred_series

FEE = 0.0009
S1A, S2, END = "2020-07-01", "2023-01-01", "2026-11-01"


def show(tag, x, lab):
    x = pd.Series(x, dtype=float).dropna()
    print(f"  {tag} {lab}: n {len(x)}, mean {x.mean():.3%}, t {tstat(x):.2f}, win {(x > 0).mean():.0%}")
    return len(x), x.mean(), tstat(x)


def verdict(tag, s1, s2, s3, n2, m2):
    if not s1[0] or not (s1[1] > 0):
        print(f"  VERDICT ({tag}): KILL")
        return
    ok2 = s2[0] >= n2 and s2[1] >= m2 and s2[2] >= 2
    ok3 = s3[1] > 0 and s3[2] >= 2
    print(f"  VERDICT ({tag}): {'PASS' if ok2 and ok3 else 'FAIL'} (Stage 2 {'holds' if ok2 else 'fails'}, Stage 3 {'holds' if ok3 else 'fails'})")


def hourly_panel(path):
    k = pd.read_parquet(PUB / path)
    return {s: (lambda v: v[~v.index.duplicated()])(pd.Series(g["close"].to_numpy(), index=pd.to_datetime(g["t"], unit="s", utc=True)).sort_index())
            for s, g in k.groupby("sym")}


def part493():
    print("\n#### #493 recurring-buy calendar (equal-weight basket long: last day of month -> 2nd, and 14th -> 16th, 00:00 UTC)")
    A = hourly_panel("batchd_alts_1h.parquet")
    A.pop("BTCUSDT", None)
    U = hourly_panel("batchh2_unseen_1h.parquet")

    def windows():
        for m in pd.period_range("2020-07", "2026-10", freq="M"):
            first = pd.Timestamp(m.year, m.month, 1, tz="UTC")
            yield first - pd.Timedelta(days=1), first + pd.Timedelta(days=1)
            yield first + pd.Timedelta(days=13), first + pd.Timedelta(days=15)

    def basket(panel):
        rows = []
        for a, b in windows():
            r = [x_b / x_a - 1 for x in panel.values() for x_a, x_b in [(at(x, a), at(x, b))] if x_a is not None and x_b is not None and x_a > 0]
            if len(r) >= 5:
                rows.append({"day": a.tz_localize(None), "ret": float(np.mean(r)) - FEE, "n": len(r)})
        return pd.DataFrame(rows)
    a, u = basket(A), basket(U)
    s1 = show("#493", a[(a["day"] >= S1A) & (a["day"] < S2)]["ret"], "Stage 1 (40 alts ex BTC, 2020-07..2022)")
    s2 = show("#493", a[(a["day"] >= S2) & (a["day"] < END)]["ret"], "Stage 2 (40 alts ex BTC, 2023..2026-10)")
    s3 = show("#493", u[(u["day"] >= S2) & (u["day"] < END)]["ret"], "Stage 3 (unseen 110, 2023..2026-10)")
    verdict("#493", s1, s2, s3, 0, 0.003)
    yrs = (pd.Timestamp(END) - pd.Timestamp(S2)).days / 365.25
    print(f"  $/yr at $45K per window (Stage 2): ${a[(a['day'] >= S2) & (a['day'] < END)]['ret'].sum() * 45000 / yrs:,.0f}")


def etf():
    p = PUB / "batchk_etf_1d.parquet"
    if not p.exists():
        return None
    d = pd.read_parquet(p)
    d["day"] = pd.to_datetime(d["t"], unit="s", utc=True).dt.tz_convert("America/New_York").dt.normalize().dt.tz_localize(None)
    return d.drop_duplicates(["sym", "day"]).pivot(index="day", columns="sym", values="adj").sort_index()


def part494():
    print("\n#### #494 pension month-end rebalancing, bond leg (#450 signal on SPY; SPY leg Stage 2, TLT leg Stage 3)")
    E = etf()
    if E is None or "TLT" not in E:
        print("  data not fetched yet (ubatchk)")
        return
    y10 = fred_series("DGS10")
    spy = E["SPY"].dropna()
    days = spy.index
    months = pd.Series(days, index=days).groupby(days.to_period("M")).apply(list)
    rows = []
    keys = list(months.index)
    for ka, kb in zip(keys[:-1], keys[1:]):
        dd = months[kb]
        if len(dd) < 6:
            continue
        prev, d4, dl = months[ka][-1], dd[-4], dd[-1]
        re_ = spy[d4] / spy[prev] - 1
        ya, yb = y10[:prev].iloc[-1], y10[:d4].iloc[-1]
        s = re_ - (-7.5 * (yb - ya) / 100)
        if abs(s) <= 0.02:
            continue
        side = -np.sign(s)  # side on equities; bonds take the opposite side
        row = {"day": dl, "spy": side * (spy[dl] / spy[d4] - 1) - 0.0004}
        for sym in ("TLT", "EFA"):
            v = E[sym]
            if d4 in v.index and dl in v.index and not pd.isna(v[d4]) and not pd.isna(v[dl]):
                row[sym] = (-side if sym == "TLT" else side) * (v[dl] / v[d4] - 1) - 0.0004
        rows.append(row)
    r = pd.DataFrame(rows)
    s1 = show("#494", r[(r["day"] >= "2003-01-01") & (r["day"] < "2016-01-01")]["spy"], "Stage 1 (SPY leg 2003..2015)")
    s2 = show("#494", r[(r["day"] >= "2016-01-01") & (r["day"] < END)]["spy"], "Stage 2 (SPY leg 2016..2026-10)")
    s3 = show("#494", r[(r["day"] >= "2016-01-01") & (r["day"] < END)].get("TLT", pd.Series(dtype=float)), "Stage 3 (TLT leg 2016..2026-10)")
    show("#494", r[(r["day"] >= "2016-01-01") & (r["day"] < END)].get("EFA", pd.Series(dtype=float)), "reported: EFA leg 2016..2026-10")
    verdict("#494", s1, s2, s3, 0, 0.002)
    s2r = r[(r["day"] >= "2016-01-01") & (r["day"] < END)]
    yrs = (pd.Timestamp(END) - pd.Timestamp("2016-01-01")).days / 365.25
    print(f"  $/yr at $30K per leg, both legs (2016..2026-10): ${(s2r['spy'].sum() + s2r.get('TLT', pd.Series(dtype=float)).sum()) * 30000 / yrs:,.0f}")


def part495():
    print("\n#### #495 retail positioning crowding (weekly: short top-quintile long-account share, long bottom quintile)")
    p = PUB / "batchk_cz_lsr_binance.parquet"
    if not p.exists():
        print("  data not fetched yet (Coinalyze --k)")
        return
    L = pd.read_parquet(p)
    L["day"] = pd.to_datetime(L["t"], unit="s").dt.normalize()
    L["sym"] = L["symbol"].str.replace("_PERP.A", "", regex=False)
    L = L.pivot_table(index="day", columns="sym", values="l", aggfunc="last").sort_index()
    P = {**hourly_panel("batchd_alts_1h.parquet"), **hourly_panel("batchh2_unseen_1h.parquet")}
    alts = sorted(pd.read_parquet(PUB / "batchd_alts_1h.parquet")["sym"].unique())
    unseen = sorted(pd.read_parquet(PUB / "batchh2_unseen_funding.parquet")["sym"].unique())
    out = {}
    for tag, uni in (("a", alts), ("u", unseen)):
        rows = []
        for mon in pd.date_range("2020-10-05", END, freq="W-MON", tz="UTC"):
            d = (mon - pd.Timedelta(days=1)).tz_localize(None)
            if d not in L.index:
                continue
            sh, ret = {}, {}
            for s in uni:
                if s not in L or s not in P or pd.isna(L.at[d, s]) or L[s].loc[:d].notna().sum() < 30:
                    continue
                a, b = at(P[s], mon), at(P[s], mon + pd.Timedelta(days=7))
                if a is None or b is None or not (a > 0):
                    continue
                sh[s], ret[s] = L.at[d, s], b / a - 1
            if len(sh) < 10:
                continue
            g = pd.Series(sh).sort_values()
            q = max(1, len(g) // 5)
            rows.append({"day": d, "ret": np.mean([ret[s] for s in g.index[:q]]) - np.mean([ret[s] for s in g.index[-q:]]) - 0.0018})
        out[tag] = pd.DataFrame(rows)
    a, u = out["a"], out["u"]
    s1 = show("#495", a[a["day"] < S2]["ret"] if len(a) else [], "Stage 1 (40 alts 2020-10..2022)")
    s2 = show("#495", a[a["day"] >= S2]["ret"] if len(a) else [], "Stage 2 (40 alts 2023..2026-10)")
    s3 = show("#495", u[u["day"] >= S2]["ret"] if len(u) else [], "Stage 3 (unseen 110, 2023..2026-10)")
    verdict("#495", s1, s2, s3, 100, 1e-9)
    yrs = (pd.Timestamp(END) - pd.Timestamp(S2)).days / 365.25
    if len(a):
        print(f"  $/yr at $22.5K per side (Stage 2): ${a[a['day'] >= S2]['ret'].sum() * 22500 / yrs:,.0f}")


def main():
    print("===== Batch K (#493-#495)  docs/PREREG_BATCH_K_20261126.md")
    part493()
    part494()
    part495()


if __name__ == "__main__":
    main()

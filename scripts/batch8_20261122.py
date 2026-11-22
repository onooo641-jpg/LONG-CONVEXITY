"""Batch 8 Stage 1 pilots (docs/PREREG_BATCH8_20261122.md) + batch 7 part D (#276 liquidations).

    uv run python -m scripts.batch8_20261122 | tee docs/jx_runs/batch8_20261122.txt
"""
from __future__ import annotations

import json
import math
import sys

import numpy as np
import pandas as pd

from scripts import fundgap_20261121 as FG

P0, P1 = pd.Timestamp("2026-08-01", tz="UTC"), pd.Timestamp("2026-11-01", tz="UTC")
KILL = 4.0
R = json.load(open("data/public/batch8_raw.json"))
ann = lambda s: float(s.mean() * 365 * 100) if len(s) else float("nan")  # noqa: E731


def stage1(label, daily, extra=""):
    s = daily[(daily.index >= P0) & (daily.index < P1)]
    v = ann(s)
    verdict = "not testable (no pilot data)" if not len(s) else ("KILL -> FAIL (Stage 1)" if not v >= KILL else "continue to Stage 2")
    print(f"{label}: Stage 1 2026-08..10 {v:.2f}%/yr on capital ({len(s)} days){extra} -> {verdict}\n")


def gaps(label, extra_rows, pairs):
    base = pd.read_parquet("data/public/fundgap_funding.parquet")
    df = pd.concat([base[base.venue.isin(["hl", "dydx"])], pd.DataFrame(extra_rows)], ignore_index=True)
    H = FG.hourly(df)
    s, trips, opens = FG.run(H, pairs)
    opened = sum(1 for o in opens if o >= P0)
    stage1(label, s.r, f"; positions opened in pilot {opened}")


def p280():
    rows = []
    for k, v in R.items():
        if k.startswith("deribit_funding|"):
            c = k.split("|")[1]
            rows += [{"venue": "deribit", "coin": c, "t": x["timestamp"] // 1000 - 3600, "rate": x["interest_1h"]} for x in v
                     if x.get("interest_1h") is not None]
    gaps("#280 funding gaps Deribit <-> HL/dYdX", rows, [("hl", "deribit"), ("dydx", "deribit")])


def p284():
    by = {}
    for k, v in R.items():
        if k.startswith("hip3|") and v:
            dex, nm = k.split("|")[1].split(":")
            by.setdefault(nm, []).append((dex, v))
    shared = {nm: L for nm, L in by.items() if len(L) >= 2}
    print(f"#284 HIP-3: {sum(len(L) for L in by.values())} markets with funding data; names listed on >= 2 dexes: {sorted(shared)}")
    rows, pairs = [], set()
    for nm, L in shared.items():
        for dex, v in L:
            rows += [{"venue": dex, "coin": nm, "t": int(x["time"]) // 1000, "rate": float(x["fundingRate"])} for x in v]
        dx = sorted(d for d, _ in L)
        pairs |= {(a, b) for i, a in enumerate(dx) for b in dx[i + 1:]}
    if not rows:
        print("  no shared names -> not testable\n")
        return
    H = FG.hourly(pd.DataFrame(rows))
    s, _, opens = FG.run(H, sorted(pairs))
    stage1("#284 HIP-3 cross-dex funding gaps", s.r, f"; pairs {sorted(pairs)}; opened in pilot {sum(1 for o in opens if o >= P0)}")


def chart(name):
    c = R.get(f"deribit_chart|{name}") or {}
    if not c or not c.get("ticks"):
        return pd.Series(dtype=float)
    return pd.Series(c["close"], index=pd.to_datetime(c["ticks"], unit="ms", utc=True).floor("D")).groupby(level=0).last()


def p281():
    out = []
    for cur in ("BTC", "ETH"):
        perp = chart(f"{cur}-PERPETUAL")
        futs = {i["instrument_name"]: pd.Timestamp(i["expiration_timestamp"], unit="ms", tz="UTC")
                for i in R[f"deribit_instruments|{cur}"] if i["settlement_period"] != "perpetual"}
        C = {n: chart(n) for n in futs}
        days = pd.date_range(P0, P1 - pd.Timedelta(days=1), freq="D", tz="UTC")
        r = []
        for d in days:
            ok = [(futs[n], n) for n in futs if (futs[n] - d).days >= 30 and d in C[n].index and d in perp.index]
            if not ok:
                r.append(np.nan)
                continue
            e, n = min(ok)
            basis = C[n][d] / perp[d] - 1
            r.append(basis * 365 / (e - d).days / (4 / 3) / 365 - 0.001 * 4 / 365)
        out.append(pd.Series(r, index=days))
        used = sorted({min([(futs[n], n) for n in futs if (futs[n] - d).days >= 30])[1] for d in days})
        print(f"  {cur}: contracts used {used} (expired Sep-2026 quarterly not in the API listing; nearest listed used)")
    stage1("#281 Deribit futures cash-and-carry (BTC+ETH)", pd.concat(out, axis=1).mean(axis=1).dropna())


def bs_straddle(S, K, s, T):
    d1 = (math.log(S / K) + 0.5 * s * s * T) / (s * math.sqrt(T))
    N = lambda x: 0.5 * (1 + math.erf(x / math.sqrt(2)))  # noqa: E731
    call = S * N(d1) - K * N(d1 - s * math.sqrt(T))
    return 2 * call - S + K  # put-call parity, r = 0


def p282():
    series = []
    for cur in ("BTC", "ETH"):
        dv = pd.Series({pd.Timestamp(x[0], unit="ms", tz="UTC").floor("D"): x[4] for x in R[f"dvol|{cur}"]["data"]})
        px = chart(f"{cur}-PERPETUAL")
        start = pd.date_range(P0 - pd.Timedelta(days=30), P1 - pd.Timedelta(days=31), freq="D", tz="UTC")
        pnl = pd.Series(0.0, index=pd.date_range(P0 - pd.Timedelta(days=30), P1, freq="D", tz="UTC"))
        for d in start:
            e = d + pd.Timedelta(days=30)
            if d not in dv.index or d not in px.index or e not in px.index:
                continue
            S = px[d]
            prem = bs_straddle(S, S, dv[d] / 100, 30 / 365)
            res = (prem - abs(px[e] - S) - 0.0006 * S) / S / 30  # on 1/30 of capital, booked at expiry
            pnl[e] += res
        series.append(pnl)
        print(f"  {cur}: mean DVOL in pilot {dv[(dv.index >= P0) & (dv.index < P1)].mean():.1f}")
    stage1("#282 Deribit short 30-day ATM straddle ladder (BTC+ETH)", pd.concat(series, axis=1).mean(axis=1))


def p285():
    def hist(sym):
        h = (R.get(f"kamino|{sym}") or {}).get("history", [])
        return pd.DataFrame([{"day": pd.Timestamp(x["timestamp"]).floor("D"), "sup": x["metrics"].get("supplyInterestAPY"),
                              "bor": x["metrics"].get("borrowInterestAPY"), "ltv": x["metrics"].get("loanToValue"),
                              "tvl": float(x["metrics"].get("depositTvl") or 0)} for x in h]).set_index("day")

    def price(nm):
        return pd.Series({pd.Timestamp(x["timestamp"], unit="s", tz="UTC").floor("D"): x["price"] for x in R.get(f"price|{nm}") or []})
    sol = hist("SOL")
    solp = price("sol")
    best = {}
    for sym, pn in (("JITOSOL", "jitosol"), ("MSOL", "msol"), ("JupSOL", "jupsol")):
        h = hist(sym)
        ratio = (price(pn) / solp).dropna()
        intr = ratio.pct_change(30) * 365 / 30  # trailing 30-day intrinsic yield
        df = pd.DataFrame({"s": intr, "sup": h.sup, "b": sol.bor, "ltv": h.ltv, "tvl": h.tvl}).dropna()
        df["s"] = df.s + df.sup
        k = (1 / (1 - 0.8 * df.ltv.clip(0, 0.95))).clip(upper=6)
        df["roe"] = df.s + (k - 1) * (df.s - df.b)
        best[sym] = df
        p = df[(df.index >= P0) & (df.index < P1)]
        print(f"  {sym}: pilot intrinsic {p.s.mean() * 100:.2f}%, SOL borrow {p.b.mean() * 100:.2f}%, LTV {p.ltv.mean():.2f}, k {k[p.index].mean():.2f}, "
              f"ROE {p.roe.mean() * 100:.2f}%/yr, TVL ${p.tvl.mean() / 1e6:.0f}M")
    roe = pd.DataFrame({s: d.roe for s, d in best.items()})
    tvl = pd.DataFrame({s: d.tvl for s, d in best.items()})
    out = []
    for m in pd.date_range(P0, P1 - pd.Timedelta(days=1), freq="MS", tz="UTC"):  # registered rule: monthly top-5 by trailing 30-day ROE, TVL >= $20M
        pday = m - pd.Timedelta(days=1)
        sc = roe.loc[pday - pd.Timedelta(days=29):pday].mean()
        ok = [c for c in sc.index if pd.notna(sc[c]) and tvl[c].get(pday, 0) >= 20e6]
        held = list(sc[ok].sort_values(ascending=False).index[:5])
        seg = roe.loc[m:m + pd.offsets.MonthEnd(0), held].mean(axis=1) / 365 if held else pd.Series(dtype=float)
        if len(seg):
            seg.iloc[0] -= len(held) * 20 / 2000 / max(len(held), 1) if m == P0 else 0.0
        out.append(seg)
        print(f"  {m:%Y-%m}: held {held}")
    stage1("#285 Kamino SOL-LST loops (monthly top-5 rule)", pd.concat(out))


def p288():
    rows = {}
    for v in R["hl_vault_list"]:
        if v.get("relationship", {}).get("type") != "normal":
            continue
        d = R.get(f"hl_vault|{v['vaultAddress']}") or {}
        at = dict(d.get("portfolio") or []).get("allTime")
        if not at:
            continue
        av = pd.Series({pd.Timestamp(int(t), unit="ms", tz="UTC"): float(x) for t, x in at["accountValueHistory"]})
        pn = pd.Series({pd.Timestamp(int(t), unit="ms", tz="UTC"): float(x) for t, x in at["pnlHistory"]})
        r = (pn.diff() / av.shift()).replace([np.inf, -np.inf], np.nan).dropna()
        rows[v["name"]] = (r, pd.Timestamp(v["createTimeMillis"], unit="ms", tz="UTC"), float(v["tvl"]))
    months = pd.date_range(P0, P1 - pd.Timedelta(days=1), freq="MS", tz="UTC")
    out = []
    for m in months:
        cand = []
        for nm, (r, born, tvl) in rows.items():
            if tvl < 1e6 or (m - born).days < 180:
                continue
            tr = r[(r.index >= m - pd.Timedelta(days=90)) & (r.index < m)]
            if len(tr):
                cand.append(((1 + tr).prod() - 1, nm))
        pick = [nm for _, nm in sorted(cand, reverse=True)[:5]]
        res = []
        for nm in pick:
            r = rows[nm][0]
            g = (1 + r[(r.index >= m) & (r.index < m + pd.offsets.MonthBegin(1))]).prod() - 1
            res.append(g * 0.9 if g > 0 else g)
        mr = float(np.mean(res)) if res else 0.0
        out.append(pd.Series(mr / m.days_in_month, index=pd.date_range(m, m + pd.offsets.MonthEnd(0), freq="D", tz="UTC")))
        print(f"  {m:%Y-%m}: picks {pick} -> month {mr * 100:.2f}%")
    stage1("#288 Hyperliquid user vaults, top-5 trailing 90 days (current list: survivorship favours a pass)", pd.concat(out),
           f"; eligible vaults {sum(1 for _, b, t in rows.values() if t >= 1e6)}")


def not_testable():
    print("#279 Drift gaps: data.api.drift.trade does not resolve (DNS) -> not testable (no data)")
    print("#289 Orderly gaps: public funding_rate_history returned 0 rows for all 12 symbols -> not testable (no data)")
    print("#283 Boros: no endpoint answered (3 probes) -> not testable (no data)")
    print("#286 Aave e-mode loops: aave-api-v2 rates-history returns non-JSON (retired) -> not testable (no data)")
    print("#287 Morpho loops / #290 Morpho vaults: blue-api GraphQL 400 / 403 -> not testable (no data)\n")


def part_d():
    from scripts.batch7_20261122 import part_d as d
    d()


def main() -> int:
    print(f"Stage 1 pilot 2026-08..10, kill < {KILL}%/yr on capital (kill-only; survivors need full-history Stage 2)\n")
    p280()
    p284()
    p281()
    p282()
    p285()
    p288()
    not_testable()
    part_d()
    return 0


if __name__ == "__main__":
    sys.exit(main())

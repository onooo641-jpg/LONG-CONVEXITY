"""Batch 8 Stage 2 (docs/PREREG_BATCH8_20261122.md addendum 1): #280 Deribit<->HL/dYdX gaps, #288 HL user vaults without survivorship.

    uv run python -m scripts.batch8s_20261122 | tee docs/jx_runs/batch8s_20261122.txt
"""
from __future__ import annotations

import json
import sys

import numpy as np
import pandas as pd

from scripts import fundgap_20261121 as FG

R = json.load(open("data/public/batch8s_raw.json"))
LO, HI, MID = pd.Timestamp("2024-11-01", tz="UTC"), pd.Timestamp("2026-11-01", tz="UTC"), pd.Timestamp("2025-11-01", tz="UTC")
ann = lambda s: float(s.mean() * 365 * 100) if len(s) else float("nan")  # noqa: E731


def slip(levels, usd, inverse):
    left, coins = usd, 0.0
    for p_, a_ in levels:
        val = a_ if inverse else p_ * a_
        take = min(left, val)
        coins += take / p_
        left -= take
        if left <= 0:
            break
    return np.nan if left > 1e-6 else usd / coins


def p280():
    rows = []
    for k, v in R.items():
        if k.startswith("deribit_funding|"):
            rows += [{"venue": "deribit", "coin": k.split("|")[1], "t": x["t"] // 1000 - 3600, "rate": x["r"]} for x in v if x["r"] is not None]
    d = pd.DataFrame(rows)
    print(f"#280 Deribit funding rows {len(d)}; from {pd.Timestamp(d.t.min(), unit='s'):%Y-%m-%d} to {pd.Timestamp(d.t.max(), unit='s'):%Y-%m-%d}")
    base = pd.read_parquet("data/public/fundgap_funding.parquet")
    H = FG.hourly(pd.concat([base[base.venue.isin(["hl", "dydx"])], d], ignore_index=True))
    FG.report("#280 Deribit <-> HL/dYdX pooled (registered)", *FG.run(H, [("hl", "deribit"), ("dydx", "deribit")]))
    FG.report("  (context) HL-Deribit pair alone", *FG.run(H, [("hl", "deribit")]), verdict=False)
    out = []
    for b in R.get("deribit_books", []):
        if not b["bids"] or not b["asks"]:
            continue
        mid = (b["bids"][0][0] + b["asks"][0][0]) / 2
        buy, sell = slip(b["asks"], 10_000, b["inverse"]), slip(b["bids"], 10_000, b["inverse"])
        s = np.nanmean([(buy - mid) / mid * 1e4 if buy == buy else np.nan, (mid - sell) / mid * 1e4 if sell == sell else np.nan])
        out.append({"coin": b["coin"], "slip_bps": s, "spread_bps": (b["asks"][0][0] - b["bids"][0][0]) / mid * 1e4})
    if out:
        e = pd.DataFrame(out).groupby("coin").median().round(2)
        print("  Deribit $10K execution (median over snapshots):\n" + e.to_string())
        print(f"  coins within 2.5 bps/side: {list(e.index[e.slip_bps <= 2.5])}; over: {list(e.index[~(e.slip_bps <= 2.5)])}\n")


def p288():
    vl = {v["vaultAddress"]: v for v in R["hl_vault_list"]}
    V = {}
    for a, v in vl.items():
        d = R.get(f"hl_vault|{a}") or {}
        if not d.get("av") or not d.get("pnl"):
            continue
        av = pd.Series({pd.Timestamp(int(t), unit="ms", tz="UTC"): float(x) for t, x in d["av"]}).sort_index()
        pn = pd.Series({pd.Timestamp(int(t), unit="ms", tz="UTC"): float(x) for t, x in d["pnl"]}).sort_index()
        r = (pn.diff() / av.shift()).replace([np.inf, -np.inf], np.nan).dropna()
        V[a] = (r, av, pd.Timestamp(int(v.get("createTimeMillis") or 0), unit="ms", tz="UTC"), v.get("name", a[:8]), bool(v.get("isClosed")))
    print(f"#288 vaults with history {len(V)} of {len(vl)} selected ({sum(1 for x in V.values() if x[4])} closed)")
    out, log = [], []
    for m in pd.date_range(LO, HI - pd.Timedelta(days=1), freq="MS", tz="UTC"):
        cand = []
        for a, (r, av, born, nm, _) in V.items():
            prev = av[av.index < m]
            if not len(prev) or prev.iloc[-1] < 1e6 or (m - born).days < 180:
                continue
            tr = r[(r.index >= m - pd.Timedelta(days=90)) & (r.index < m)]
            if len(tr):
                cand.append(((1 + tr).prod() - 1, a))
        pick = [a for _, a in sorted(cand, reverse=True)[:5]]
        res = []
        for a in pick:
            r = V[a][0]
            g = (1 + r[(r.index >= m) & (r.index < m + pd.offsets.MonthBegin(1))]).prod() - 1
            res.append(g * 0.9 if g > 0 else g)
        mr = float(np.mean(res)) if res else 0.0
        out.append(pd.Series(mr / m.days_in_month, index=pd.date_range(m, m + pd.offsets.MonthEnd(0), freq="D", tz="UTC")))
        log.append(f"    {m:%Y-%m}: eligible {len(cand)}, month {mr * 100:+.2f}%")
    s = pd.concat(out)
    print("\n".join(log))
    h1, h2 = ann(s[s.index < MID]), ann(s[s.index >= MID])
    mon = s.groupby(s.index.strftime("%Y-%m")).sum() * 100
    print(f"#288 HL user vaults top-5 (no survivorship): halves {h1:.2f}% / {h2:.2f}%; worst month {mon.min():.2f}%; months negative {(mon < 0).sum()}")
    print(f"  VERDICT: {'PASS' if h1 >= 8 and h2 >= 8 else 'FAIL'}\n")


def main() -> int:
    print("Stage 2: PASS = both halves (2024-11..2025-10, 2025-11..2026-10) >= 8%/yr on capital\n")
    p280()
    p288()
    return 0


if __name__ == "__main__":
    sys.exit(main())

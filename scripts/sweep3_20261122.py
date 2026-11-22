"""Sweep 3 Stage 1 (docs/PREREG_SWEEP3_20261122.md): #322 thin-venue market making, #323 hedged extreme-funding harvest,
#324 counterparty/option vaults, #325 small stable lending markets.

    uv run python -m scripts.sweep3_20261122 | tee docs/jx_runs/sweep3_20261122.txt
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np
import pandas as pd

P0, P1 = pd.Timestamp("2026-08-01", tz="UTC"), pd.Timestamp("2026-11-01", tz="UTC")
KILL = 25.0
R = json.load(open("data/public/sweep3_raw.json")) if os.path.exists("data/public/sweep3_raw.json") else {}
ann = lambda s: float(s.mean() * 365 * 100) if len(s) else float("nan")  # noqa: E731


def verdict(v):
    return "KILL -> FAIL (Stage 1)" if not v >= KILL else "continue to Stage 2"


def p323():
    f = pd.read_parquet("data/public/hl_funding.parquet")
    f["t"] = pd.to_datetime(f["time"], unit="ms", utc=True).dt.floor("h")
    H = f.drop_duplicates(["coin", "t"]).pivot(index="t", columns="coin", values="rate").sort_index()
    big = {"BTC", "ETH", "SOL", "XRP", "DOGE", "BNB"}
    H = H[[c for c in H.columns if c not in big]]
    tr = H.rolling(24, min_periods=20).mean() * 24 * 365 * 100  # trailing 24h, annualised %
    days = pd.date_range(pd.Timestamp("2026-07-01", tz="UTC"), P1 - pd.Timedelta(days=1), freq="D")
    held, out, trips = {}, [], 0
    for d in days:
        prev = d - pd.Timedelta(hours=1)
        if prev not in tr.index:
            out.append((d, 0.0))
            continue
        sig = tr.loc[prev]
        pnl = 0.0
        for c in list(held):
            if not sig.get(c, np.nan) > 20:
                held.pop(c)
                pnl -= 0.011 / 2  # exit half of the 1.1% round trip
                trips += 1
        for c in sig[sig > 100].sort_values(ascending=False).index:
            if len(held) >= 5:
                break
            if c not in held:
                held[c] = d
                pnl -= 0.011 / 2
        today = H.loc[d:d + pd.Timedelta(hours=23), list(held)].fillna(0).sum()
        pnl += float(today.sum())
        out.append((d, pnl / 5 * (1 / 1.25)))  # 5 slots; 25% margin on the short (capital = spot + margin)
    s = pd.Series(dict(out))
    p = s[(s.index >= P0) & (s.index < P1)]
    v = ann(p)
    print(f"#323 hedged extreme-funding harvest (HL small caps): Stage 1 2026-08..10 {v:.2f}%/yr on capital; round trips {trips}; "
          f"{H.shape[1]} coins -> {verdict(v)}")
    s2 = []
    for d in pd.date_range(pd.Timestamp("2024-02-01", tz="UTC"), P1 - pd.Timedelta(days=1), freq="D"):
        prev = d - pd.Timedelta(hours=1)
        s2.append((d, int((tr.loc[prev] > 100).sum()) if prev in tr.index else 0))
    n = pd.Series(dict(s2))
    print(f"  (context) coins above 100%/yr trailing-24h funding per day: median {n.median():.0f}, 2024 {n[n.index.year == 2024].mean():.1f}, "
          f"2025 {n[n.index.year == 2025].mean():.1f}, 2026 {n[n.index.year == 2026].mean():.1f}\n")


def p322():
    rows = []
    for k, v in R.items():
        if not k.startswith("dydx_trades|") or not v:
            continue
        c = k.split("|")[1]
        hl = pd.DataFrame(R.get(f"hl1m|{c}") or [], columns=["t", "o", "c"])
        if hl.empty:
            continue
        mid = pd.Series(hl["c"].values, index=pd.to_datetime(hl["t"], unit="ms", utc=True)).sort_index()
        tr = pd.DataFrame(v)
        tr["ts"] = pd.to_datetime(tr["t"], utc=True)
        tr = tr[(tr.ts >= mid.index.min()) & (tr.ts <= mid.index.max() - pd.Timedelta(minutes=6))]
        if tr.empty:
            continue
        f5 = mid.reindex(tr.ts + pd.Timedelta(minutes=5), method="ffill").values
        maker_sign = np.where(tr["side"].str.upper() == "BUY", -1, 1)  # taker buys -> maker sold
        edge = maker_sign * (f5 - tr["price"].values) / tr["price"].values - 0.0003  # 2 bps hedge + 1 bp maker fee
        notional = tr["size"].values * tr["price"].values
        days = (tr.ts.max() - tr.ts.min()).total_seconds() / 86400
        rows.append((c, len(tr), notional.sum() / max(days, 1e-9), float(np.average(edge, weights=notional)) * 1e4,
                     float((edge * notional).sum() / max(days, 1e-9))))
    if not rows:
        print("#322 thin-venue market making: no trade data -> not testable (no data)\n")
        return
    e = pd.DataFrame(rows, columns=["coin", "trades", "usd_per_day", "edge_bps", "edge_usd_per_day"])
    cap = 5000.0
    yr = 0.20 * e.edge_usd_per_day.clip(lower=0).sum() * 365 / cap * 100
    mean_edge = float(np.average(e.edge_bps, weights=e.usd_per_day))
    print("#322 thin-venue market making on dYdX hedged on HL (last ~3 days of trades):")
    print("  " + e.round(2).to_string(index=False).replace("\n", "\n  "))
    print(f"  flow-weighted mean edge {mean_edge:.2f} bps; 20% capture of positive-edge pairs on $5K -> {yr:.1f}%/yr -> "
          f"{'KILL -> FAIL (Stage 1)' if not (yr >= KILL and mean_edge > 0) else 'continue to Stage 2'}\n")


def pools_rotation(label, grp, k, slot_cost, stable_floor=False):
    rows = []
    for key, v in R.items():
        if key.startswith(f"chart|{grp}|"):
            p = key.split("|")[2]
            rows += [(p, pd.Timestamp(x["ts"]).floor("D"), x.get("tvl"), (x.get("b") or 0) + 0.9 * (x.get("r") or 0)) for x in v]
    if not rows:
        print(f"{label}: no data -> not testable (no data)\n")
        return
    d = pd.DataFrame(rows, columns=["pool", "day", "tvl", "y"]).drop_duplicates(["pool", "day"])
    Y = d.pivot(index="day", columns="pool", values="y").clip(upper=1000)
    T = d.pivot(index="day", columns="pool", values="tvl")
    out = []
    for m in pd.date_range(P0, P1 - pd.Timedelta(days=1), freq="MS", tz="UTC"):
        pday = m - pd.Timedelta(days=1)
        if pday not in Y.index:
            continue
        sc = Y.loc[pday - pd.Timedelta(days=29):pday].mean().dropna().sort_values(ascending=False)
        held = list(sc.index[:k])
        for j, dd in enumerate(pd.date_range(m, m + pd.offsets.MonthEnd(0), freq="D", tz="UTC")):
            r = []
            for p in held:
                t7 = T.loc[dd - pd.Timedelta(days=7):dd, p].dropna() if dd in T.index else pd.Series(dtype=float)
                if len(t7) > 1 and t7.iloc[-1] < 0.3 * t7.max():
                    r.append(-0.5 / 30)
                    continue
                v = Y.at[dd, p] if dd in Y.index else np.nan
                r.append((v if pd.notna(v) else 0.0) / 100 / 365)
            out.append((dd, float(np.mean(r)) if r else 0.0) if j else (dd, (float(np.mean(r)) if r else 0.0) - slot_cost))
    s = pd.Series(dict(out))
    v = ann(s)
    print(f"{label}: {Y.shape[1]} pools; Stage 1 2026-08..10 {v:.2f}%/yr (APY-based) -> {verdict(v)}\n")


def main() -> int:
    print(f"Stage 1 pilots, kill-only < {KILL}%/yr (docs/PREREG_SWEEP3_20261122.md)\n")
    p323()
    if not R:
        print("(sweep-3 fetch not yet landed: #322, #324, #325 pending)")
        return 0
    p322()
    pools_rotation("#324 counterparty / option vaults (APY-based; may omit trader P&L)", "vault", 5, 2 * 10 / 2000)
    pools_rotation("#325 small stable lending markets at high utilisation", "lend", 10, 2 * 15 / 1500)
    return 0


if __name__ == "__main__":
    sys.exit(main())

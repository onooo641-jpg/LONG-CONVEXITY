"""Batch 2 of the 64, as docs/PREREG_BATCH2_20261120.md defines it (140bcf9).

    uv run python scripts/batch2_20261120.py
"""

from __future__ import annotations

import sys

import numpy as np
import pandas as pd

sys.path.insert(0, "scripts")
from top10_20261120 import P  # noqa: E402


def m1():
    print("=== M1 cross-chain lending-rate arbitrage (weekly)")
    ch, now = pd.read_parquet(P / "batch2_lending.parquet"), pd.read_parquet(P / "llama_pools_now.parquet")
    meta = now.set_index("pool")[["chain", "symbol", "project"]]
    x = ch.join(meta, on="pool")
    x["day"] = pd.to_datetime(x["timestamp"]).dt.tz_localize(None).dt.normalize()
    x["apyb"] = pd.to_numeric(x["apyBase"], errors="coerce")
    ok_all = True
    for sym in ("USDC", "USDT"):
        s = x[x.symbol == sym]
        L = s.pivot_table(index="day", columns="pool", values="apyb", aggfunc="last").sort_index()
        base_pool = (s[(s.project == "aave-v3") & (s.chain == "Ethereum")].groupby("pool").tvlUsd.last().idxmax()
                     if len(s[(s.project == "aave-v3") & (s.chain == "Ethereum")]) else None)
        if base_pool is None or L.shape[1] < 2:
            print(f"  {sym}: not enough pools")
            ok_all = False
            continue
        L = L[L[base_pool].notna()]
        trail = L.rolling(7, min_periods=5).mean().shift(1)
        held, got, cost = None, [], 0.0
        chain_of = meta.chain.to_dict()
        for i, d in enumerate(L.index):
            if i % 7 == 0 and trail.loc[d].notna().any():
                pick = trail.loc[d].idxmax()
                if pick != held:
                    eth = "Ethereum" in (chain_of.get(pick), chain_of.get(held))
                    cost += (20 if eth else 5) + 0.0005 * 10_000 if held is not None else 0
                    held = pick
            got.append(L.loc[d, held] if held is not None and pd.notna(L.loc[d, held]) else L.loc[d, base_pool])
        got = pd.Series(got, index=L.index)
        mid = len(got) // 2
        for name, sl in (("first half", slice(0, mid)), ("second half", slice(mid, None))):
            g, b = got.iloc[sl], L[base_pool].iloc[sl]
            yrs = len(g) / 365
            ex = (g - b).mean() / 100 - cost * (len(g) / len(got)) / 10_000 / yrs
            ok = ex > 0.01
            ok_all &= ok
            print(f"  {sym} {name}: {len(g)} days, net excess {ex:.2%}/yr vs Aave Ethereum  {'PASS' if ok else '-'}")
    print(f"  -> M1 {'PASS' if ok_all else 'fail'}")


def m2():
    print("\n=== M2 stablecoin depeg buying")
    px = pd.read_parquet(P / "batch2_prices.parquet")
    px = px[px.coin.str.startswith("coingecko:")].copy()
    px["day"] = pd.to_datetime(px.t, unit="s").dt.round("D")
    events = []
    for coin, g in px.groupby("coin"):
        s = g.drop_duplicates("day", keep="last").set_index("day").price.sort_index()
        i, idx = 0, list(s.index)
        while i < len(idx):
            if s.iloc[i] <= 0.99:
                buy = s.iloc[i]
                j = i + 1
                while j < len(idx) and s.iloc[j] < 0.999 and (idx[j] - idx[i]).days < 60:
                    j += 1
                j = min(j, len(idx) - 1)
                ret = s.iloc[j] / buy - 1 - 0.002
                events.append({"coin": coin, "day": idx[i], "buy": buy, "sell": s.iloc[j], "ret": ret,
                               "days": (idx[j] - idx[i]).days})
                i = j + 1
            else:
                i += 1
    ev = pd.DataFrame(events)
    print(f"  coins with data: {px.coin.nunique()}; events: {len(ev)}")
    if ev.empty:
        print("  -> M2 fail (no events)")
        return
    print(ev.assign(day=ev.day.dt.date).to_string(index=False, float_format=lambda v: f"{v:.4f}"))
    lo, hi = px.day.min(), px.day.max()
    mid = lo + (hi - lo) / 2
    ok_all = ev.ret.min() >= -0.05
    for name, a, b in (("first half", lo, mid), ("second half", mid, hi + pd.Timedelta(days=1))):
        part = ev[(ev.day >= a) & (ev.day < b)]
        yrs = (b - a).days / 365.25
        usd = (part.ret.clip(lower=-1) * 10_000).sum() / yrs if len(part) else 0.0
        ok = usd >= 300
        ok_all &= ok
        print(f"  {name}: {len(part)} events, ${usd:,.0f} a year per $10K  {'PASS' if ok else '-'}")
    print(f"  worst event {ev.ret.min():.1%}  ({'ok' if ev.ret.min() >= -0.05 else 'breaks the 5% loss limit'})")
    print(f"  -> M2 {'PASS' if ok_all else 'fail'}")


def m3():
    print("\n=== M3 cross-chain USDC dislocations")
    px = pd.read_parquet(P / "batch2_prices.parquet")
    px = px[~px.coin.str.startswith("coingecko:")].copy()
    if px.empty:
        print("  no chain prices returned -> no data")
        return
    px["day"] = pd.to_datetime(px.t, unit="s").dt.round("D")
    w = px.pivot_table(index="day", columns="coin", values="price", aggfunc="last").dropna(thresh=2)
    gap = (w.max(axis=1) - w.min(axis=1))
    print(f"  chains with data: {w.shape[1]}; days {len(w)}; max gap {gap.max():.4%}; days > 0.05%: {(gap > 0.0005).sum()}")
    if (gap <= 0.0005).all():
        print("  -> M3: no measurable gap at daily resolution (prices look aggregated)")
        return
    yrs = (w.index.max() - w.index.min()).days / 365.25
    n = int((gap > 0.003).sum())
    print(f"  days with a gap > 0.3%: {n} ({n / yrs:.1f} a year)")
    print(f"  -> M3 {'PASS' if n / yrs >= 12 else 'fail'}")


if __name__ == "__main__":
    m1()
    m2()
    m3()

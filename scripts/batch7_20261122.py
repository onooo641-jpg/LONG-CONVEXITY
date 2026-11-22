"""Batch 7 (docs/PREREG_BATCH7_20261122.md): A Gains price check, B Pendle G9 walk-forward, C free execution pilot.

    uv run python scripts/batch7_20261122.py | tee docs/jx_runs/batch7_20261122.txt
"""
from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from scripts.walkforward_20261122 import DAYS, LO, HI, OOS, SPLIT, ann, judge

D = Path("data/public")


def part_a():
    print("===== A. #225 Gains vault, price-based return (Arbitrum gUSDC)")
    p = pd.read_parquet(D / "batch7_gains_prices.parquet")
    if p.empty:
        print("  no gToken price data -> not testable\n")
        return
    p["day"] = pd.to_datetime(p["ts"], unit="s", utc=True).dt.floor("D")
    px = p.drop_duplicates("day").set_index("day")["price"].sort_index()
    r = px.pct_change().dropna()
    r = r[(r.index >= LO) & (r.index < HI)]
    print(f"  price points {len(px)}: {px.index.min():%Y-%m-%d} {px.iloc[0]:.4f} -> {px.index.max():%Y-%m-%d} {px.iloc[-1]:.4f}; "
          f"worst day {r.min() * 100:.2f}%, days down {int((r < 0).sum())}")
    pools = pd.read_parquet(D / "batch4_charts.parquet")
    a = pools[pools.pool == "c48595c8-49bc-4853-80e4-f18c470bbfc3"].copy()
    a["day"] = a["ts"].dt.floor("D")
    a = a.drop_duplicates("day").set_index("day")
    apy = ((a["apyBase"].fillna(0) + 0.9 * a["apyReward"].fillna(0)) / 100 / 365).reindex(r.index)
    both = r.index[apy.notna()]
    print(f"  same {len(both)} days: price-based {ann(r[both]):.2f}%/yr vs DefiLlama APY-based {ann(apy[both]):.2f}%/yr")
    o = r[(r.index >= OOS[0]) & (r.index < HI)]
    h1, h2 = ann(o[o.index < SPLIT]), ann(o[o.index >= SPLIT])
    c15 = ann(o) - 1.5 * 2 * 5 / 10_000 * 100 / 1.5  # one entry+exit 5 bps each, x1.5, spread over the 18-month hold
    ok = h1 >= 8 and h2 >= 8 and c15 >= 8
    print(f"  fixed hold OOS 2025-05..2026-10: halves {h1:.2f}% / {h2:.2f}%; costs x1.5 {c15:.2f}%")
    print(f"  VERDICT: {'PASS' if ok else 'FAIL'}\n")


BLUE = ("USDE", "SUSDE", "USDS", "SUSDS", "USDC", "USDT", "DAI", "GHO", "FRAX", "CRVUSD")


def part_b():
    h = pd.read_parquet(D / "batch7_pendle_history.parquet")
    mk = pd.read_parquet(D / "batch7_pendle_markets.parquet")
    up = pd.read_parquet(D / "batch7_pendle_underlying.parquet")
    print(f"===== B. G9 Pendle PTs incl. expired markets: {len(mk)} markets, {h.address.nunique()} with history, {len(h)} rows")
    if h.empty:
        print("  no history -> not testable\n")
        return
    h["day"] = pd.to_datetime(h["timestamp"], utc=True).dt.floor("D")
    h = h.drop_duplicates(["address", "day"])
    exp = pd.to_datetime(mk.set_index("address")["expiry"], utc=True)
    name = mk.set_index("address")["name"]
    A = h.pivot(index="day", columns="address", values="impliedApy").reindex(DAYS)
    T = h.pivot(index="day", columns="address", values="tvl").reindex(DAYS)
    loss = {}
    for _, u in up.iterrows():
        if pd.notna(u["price"]) and u["price"] < 0.98:
            loss[u["address"]] = 1 - float(u["price"])
    print(f"  depegged at expiry (< $0.98): {len(loss)} -> " + ", ".join(f"{name.get(a, a[:8])} -{v * 100:.0f}%" for a, v in loss.items()))
    blue = {a for a in A.columns if any(b in str(name.get(a, "")).upper().replace("-", "") for b in BLUE)}

    def run(k, tmin, mind, uni, cm):
        legs = np.zeros(len(DAYS))
        cost = 2 * (0.001 + 10 / (10_000 / 6 / k)) * cm  # buy + redeem
        for m in pd.date_range(LO, HI - pd.Timedelta(days=1), freq="MS", tz="UTC"):
            pday = m - pd.Timedelta(days=1)
            if pday < LO:
                continue
            ok = [a for a in A.columns if pd.notna(A.at[pday, a]) and pd.notna(T.at[pday, a]) and T.at[pday, a] >= tmin
                  and a in exp and (exp[a] - m).days >= mind and (uni == "all" or a in blue)]
            pick = A.loc[pday, ok].sort_values(ascending=False).index[:k]
            i0 = DAYS.get_loc(m)
            for a in pick:
                i1 = min(DAYS.searchsorted(exp[a]), len(DAYS))
                daily = A.at[pday, a] / 365
                legs[i0:i1] += daily / 6 / k
                legs[i0] -= cost / 6 / k
                if a in loss and i1 < len(DAYS):
                    legs[i1] -= loss[a] / 6 / k
            # months with fewer than k picks leave that slice idle (0%)
        return pd.Series(legs, index=DAYS)
    judge("G9 #211 Pendle PTs (expired markets included)", lambda cm: {f"k{k}/tvl{int(t / 1e6)}M/d{d}/{u}": run(k, t, d, u, cm)
          for k, t, d, u in itertools.product((1, 3, 5), (1e6, 5e6, 20e6), (30, 60, 90), ("all", "blue"))}, 0.0)


def slip(levels, usd):
    """bps cost vs mid of filling usd notional against levels [[px, sz], ...]."""
    left, cost_px, filled = usd, 0.0, 0.0
    for p_, s_ in levels:
        take = min(left, p_ * s_)
        cost_px += take / p_
        filled += take
        left -= take
        if left <= 0:
            break
    return np.nan if left > 1e-6 else filled / cost_px


def part_c():
    f = D / "batch7_orderbooks.json"
    print("===== C. #208 free execution pilot (paper)")
    if not f.exists():
        print("  no snapshots -> not testable\n")
        return
    rows = []
    for s in json.loads(f.read_text()):
        b, a = s["bids"], s["asks"]
        if not b or not a:
            continue
        mid = (b[0][0] + a[0][0]) / 2
        buy = slip(a, 10_000)
        sell = slip(b, 10_000)
        rows.append({"venue": s["venue"], "coin": s["coin"], "spread": (a[0][0] - b[0][0]) / mid * 1e4,
                     "slip": np.nanmean([(buy - mid) / mid * 1e4 if buy == buy else np.nan, (mid - sell) / mid * 1e4 if sell == sell else np.nan]),
                     "tob": min(b[0][0] * b[0][1], a[0][0] * a[0][1])})
    r = pd.DataFrame(rows)
    print(f"  snapshots used: {len(r)} books ({r.groupby('venue').size().to_dict()})")
    g = r.groupby(["venue", "coin"]).median().round(2)
    print(g.to_string())
    v = r.groupby("venue").median(numeric_only=True).round(2)
    print("\n  by venue (median):\n" + v.to_string())
    for ven in v.index:
        print(f"  {ven}: taker $10K slippage {v.at[ven, 'slip']:.2f} bps/side -> {'within' if v.at[ven, 'slip'] <= 2.5 else 'OVER'} 2.5 bps budget; "
              f"top-of-book ${v.at[ven, 'tob']:,.0f} -> maker {'plausible' if v.at[ven, 'tob'] >= 10_000 else 'thin'}")
    print()


def liq_losses(bars, lev, rehedge_next_bar, mm=0.05, fee=0.005):
    """Daily loss series (fraction of capital) from short liquidations, weekly rebalance (PREREG part D)."""
    notional, margin = lev / (lev + 1), 1 / (lev + 1)
    loss = pd.Series(0.0, index=DAYS)
    n, i = 0, 0
    while i < len(bars):
        p0 = bars.c.iloc[i]
        j_end = min(i + 42, len(bars) - 1)  # 42 four-hour bars = 7 days
        for j in range(i + 1, j_end + 1):
            ph = bars.h.iloc[j]
            pliq = p0 * (1 + margin / notional) / (1 + mm)  # equity == mm * notional * P/P0
            if ph >= pliq:
                n += 1
                d = bars.index[j].floor("D")
                lost = mm * notional * pliq / p0 + fee * notional
                if not rehedge_next_bar:
                    lost += -notional * (bars.c.iloc[j_end] / pliq - 1) * pliq / p0  # unhedged spot P&L to next rebalance
                if d in loss.index:
                    loss[d] -= lost
                break
        i = j_end if j_end > i else i + 1
    return loss, n


def part_d():
    f = D / "batch7_hype4h.parquet"
    print("===== D. #276 hedged HYPE staking with liquidations (weekly rebalance)")
    if not f.exists():
        print("  no HYPE candles -> not testable\n")
        return
    b = pd.read_parquet(f)
    b.index = pd.to_datetime(b.t, unit="ms", utc=True)
    b = b.sort_index()
    print(f"  bars {len(b)}: {b.index.min():%Y-%m-%d} .. {b.index.max():%Y-%m-%d}; max 7-day rise {((b.h.rolling(42).max() / b.c.shift(42)) - 1).max() * 100:.0f}%")
    fu = pd.read_parquet(D / "hedged_hlfunding.parquet")
    fu["day"] = pd.to_datetime(fu["t"], unit="s", utc=True).dt.floor("D")
    h = fu[fu.coin == "HYPE"].groupby("day").rate.sum().reindex(DAYS)
    from scripts.walkforward_20261122 import PARK
    for variant in (False, True):
        L = {lev: liq_losses(b, lev, variant) for lev in (1.5, 2, 3)}
        print(f"  {'re-hedge next bar' if variant else 'unhedged until weekly rebalance'}: liquidations " +
              ", ".join(f"{k}x: {v[1]} (loss {-v[0].sum() * 100:.1f}% of capital)" for k, v in L.items()))

        def run(lev, thr, cm, L=L):
            trail = (h.rolling(30, min_periods=10).mean() * 365 * 100).shift(1)
            inpos = pd.Series(True, index=DAYS) if thr is None else (trail > thr).fillna(False)
            sw = inpos.astype(int).diff().abs().fillna(0)
            carry = (0.025 / 365 + h.fillna(0)) / (1 + 1 / lev)
            return pd.Series(np.where(inpos, carry + L[lev][0].values, PARK), index=DAYS) - sw * 0.00145 * cm
        if not variant:
            judge("G5-liq #276 hedged HYPE staking with liquidations", lambda cm: {f"lev{l}/{'always' if t is None else 'gt' + str(t)}": run(l, t, cm)
                  for l, t in itertools.product((1.5, 2, 3), (None, 0, 5, 8, 12))}, 0.00145 * 2)
        else:
            judge("(context) G5-liq re-hedge-next-bar variant", lambda cm: {f"lev{l}/{'always' if t is None else 'gt' + str(t)}": run(l, t, cm)
                  for l, t in itertools.product((1.5, 2, 3), (None, 0, 5, 8, 12))}, 0.00145 * 2)


def main() -> int:
    part_a()
    part_b()
    part_c()
    part_d()
    return 0


if __name__ == "__main__":
    sys.exit(main())

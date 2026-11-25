"""#415 withdrawal-queue discounts against on-chain NAV (docs/PREREG_DISTINCT_20261125.md).

    uv run python -m scripts.nav_discount_20261125 | tee docs/jx_runs/nav_discount_20261125.txt
Reads data/public/distinct_nav_1h.parquet (Actions job unav).
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

PUB = Path(__file__).resolve().parent.parent / "data" / "public"
TOK = {"weETH": ("ethereum:0xcd5fe23c85820f7b72d0926fc9b05b43e359b7ee", "coingecko:wrapped-eeth", "coingecko:ethereum", 0.03),
       "sUSDe": ("ethereum:0x9d39a5de30e57443bff2a8307a4256c8797a3497", "coingecko:ethena-staked-usde", "coingecko:ethena-usde", 0.08),
       "pufETH": ("ethereum:0xd9a442856c234a39a81a089c06451ebaa4306a72", "coingecko:pufeth", "coingecko:ethereum", 0.03),
       "rsETH": ("ethereum:0xa1290d69c65a6fe4df752f95823fae25cb99e5a7", "coingecko:kelp-dao-restaked-eth", "coingecko:ethereum", 0.03)}
Q, SIZE, FEE = 7, 5000.0, 0.001


def run(P, start, end, label):
    trades = []
    for name, (nav_k, mkt_k, und_k, y) in TOK.items():
        if not all(k in P for k in (nav_k, mkt_k, und_k)):
            continue
        nav = (P[nav_k] / P[und_k]).dropna()
        hop = nav.pct_change()
        if (hop < -0.005).sum() > 3:  # NAV check from the pre-registration
            continue
        disc = (P[mkt_k] / P[nav_k]).dropna()
        disc = disc[(disc.index >= start) & (disc.index <= end)]
        busy = None
        for ts, v in disc.items():
            if busy is not None and ts <= busy:
                continue
            if v > 0.99:
                continue
            red = ts + pd.Timedelta(days=Q)
            if red > P.index[-1]:
                continue
            nav_in = P[nav_k].asof(ts)
            nav_out = P[nav_k].asof(red)
            und_in, und_out = P[und_k].asof(ts), P[und_k].asof(red)
            if any(pd.isna(x) for x in (nav_in, nav_out, und_in, und_out)):
                continue
            # bought at market (v x NAV), redeemed for the underlying at NAV after the queue; measured in the underlying
            ret = (nav_out / und_out) / (v * nav_in / und_in) - 1 - FEE - y * Q / 365
            trades.append({"tok": name, "ts": ts, "disc": 1 - v, "ret": ret})
            busy = red
    t = pd.DataFrame(trades)
    yrs = (end - start).days / 365
    if t.empty:
        print(f"  {label}: no events")
        return t, 0.0
    t = t.sort_values("ts")
    kept, open_ = [], []
    for _, x in t.iterrows():
        open_ = [u for u in open_ if u > x["ts"]]
        if len(open_) < 3:
            kept.append(x)
            open_.append(x["ts"] + pd.Timedelta(days=Q))
    k = pd.DataFrame(kept)
    per_yr = (k["ret"] * SIZE).sum() / yrs
    print(f"  {label}: events {len(k)} ({k.groupby('tok').size().to_dict()}); mean {k['ret'].mean():.2%}, profitable {(k['ret'] > 0).mean():.0%}, "
          f"median discount {k['disc'].median():.2%}; ${per_yr:,.0f}/yr")
    return k, per_yr


def main():
    print("===== #415 withdrawal-queue discounts vs on-chain NAV")
    p = PUB / "distinct_nav_1h.parquet"
    if not p.exists():
        print("  data not fetched yet (job unav)")
        return
    d = pd.read_parquet(p)
    d["ts"] = pd.to_datetime(d["t"], unit="s", utc=True).dt.round("h")
    P = d.drop_duplicates(["key", "ts"]).pivot(index="ts", columns="key", values="price").sort_index()
    for name, (nav_k, mkt_k, und_k, _) in TOK.items():
        if not all(k in P for k in (nav_k, mkt_k, und_k)):
            print(f"  {name}: missing series")
            continue
        nav = (P[nav_k] / P[und_k]).dropna()
        hop = nav.pct_change()
        same_as_mkt = (P[nav_k] / P[mkt_k]).dropna()
        print(f"  NAV check {name}: hours {len(nav)}, NAV/underlying {nav.iloc[0]:.4f} -> {nav.iloc[-1]:.4f}, hourly drops > 0.5%: "
              f"{int((hop < -0.005).sum())} ({'dropped' if (hop < -0.005).sum() > 3 else 'kept'}); NAV equals market price in "
              f"{(same_as_mkt.sub(1).abs() < 1e-6).mean():.0%} of hours")
    s1, py1 = run(P, pd.Timestamp("2024-01-01", tz="UTC"), pd.Timestamp("2024-12-31 23:00", tz="UTC"), "Stage 1, 2024")
    kill = len(s1) < 4 or py1 < 3000
    print(f"  STAGE 1 VERDICT: {'KILL' if kill else 'survives (kill-only)'}")
    s2, py2 = run(P, pd.Timestamp("2025-01-01", tz="UTC"), pd.Timestamp("2026-10-31", tz="UTC"), "Stage 2 (out-of-sample), 2025-01..2026-10")
    ok = (not kill) and len(s2) >= 4 and py2 >= 3000 and (s2["ret"] > 0).mean() >= 0.75 if len(s2) else False
    print(f"  STAGE 2 VERDICT: {'PASS' if ok else ('FAIL' if not kill else 'not run (Stage 1 killed) — context')}")


if __name__ == "__main__":
    main()

"""Post-listing short on unseen 2023 Hyperliquid listings, per docs/PREREG_POSTLISTING_20261120.md.

    uv run python scripts/postlisting_20261120.py
"""

from __future__ import annotations

import sys

import numpy as np
import pandas as pd

sys.path.insert(0, "scripts")
from top10_20261120 import P, tstat  # noqa: E402

H = 3600 * 1000


def pnl(fund, cand, coin, lo, hi):
    c = cand[(cand.coin == coin) & (cand.t >= lo) & (cand.t < hi)].sort_values("t")
    if len(c) < 24:
        return None
    entry, exit_ = c.o.iloc[0], c.c.iloc[-1]
    f = fund[(fund.coin == coin) & (fund.time >= lo) & (fund.time < hi)]
    carry = f.rate.sum() * 1000
    return (entry - exit_) / entry * 1000 + carry - 0.90, c.h.max() / entry - 1


def main() -> int:
    coins = pd.read_parquet(P / "hl_coins.parquet")
    fund = pd.read_parquet(P / "hl2023_funding.parquet")
    cand = pd.read_parquet(P / "hl2023_candles.parquet")
    lo_ms = pd.Timestamp("2023-05-20", tz="UTC").timestamp() * 1000
    hi_ms = pd.Timestamp("2024-01-01", tz="UTC").timestamp() * 1000
    sel = coins[coins.first_funding_ms.notna() & (coins.first_funding_ms >= lo_ms) & (coins.first_funding_ms < hi_ms)]
    rows = []
    for coin, L in zip(sel.coin, sel.first_funding_ms):
        lo, hi = L + H, L + 337 * H
        a = pnl(fund, cand, coin, lo, hi)
        b = pnl(fund, cand, "BTC", lo, hi)
        if a is None or b is None:
            continue
        rows.append({"coin": coin, "L": pd.to_datetime(L, unit="ms").date(), "pnl": a[0], "pump": a[1], "btc": b[0]})
    df = pd.DataFrame(rows)
    print(f"holdout listings with data: {len(df)} of {len(sel)}")
    if len(df) < 20:
        print("VERDICT: too few to decide")
        return 0
    ex = df.pnl - df.btc
    c1 = df.pnl.mean() > 0 and tstat(df.pnl) > 2
    c2 = ex.mean() > 0 and tstat(ex) > 2
    c3 = df.pnl.median() > 0
    print(f"  mean P&L ${df.pnl.mean():.2f} per $1,000 per 14d  t {tstat(df.pnl):.2f}  -> {'yes' if c1 else 'no'}")
    print(f"  mean excess over BTC short ${ex.mean():.2f}  t {tstat(ex):.2f}  -> {'yes' if c2 else 'no'}")
    print(f"  median P&L ${df.pnl.median():.2f}  -> {'yes' if c3 else 'no'}")
    print(f"  share profitable {(df.pnl > 0).mean():.0%}; rose >= 50% at some point {(df.pump >= 0.5).mean():.0%}; "
          f"worst ${df.pnl.min():.0f}; best ${df.pnl.max():.0f}")
    print(f"VERDICT: {'PASS' if c1 and c2 and c3 else 'fail'}")
    print("\nper listing:")
    print(df.sort_values("L").to_string(index=False, float_format=lambda v: f"{v:.2f}"))
    return 0


if __name__ == "__main__" and "--daily" not in sys.argv:
    raise SystemExit(main())


def main_daily() -> int:
    """Version 2 (daily candles), as registered in the pre-registration's v2 section."""
    coins = pd.read_parquet(P / "hl_coins.parquet")
    fund = pd.read_parquet(P / "hl2023_funding.parquet")
    d = pd.read_parquet(P / "hl2023_daily.parquet").sort_values("t")
    lo_ms = pd.Timestamp("2023-05-20", tz="UTC").timestamp() * 1000
    hi_ms = pd.Timestamp("2024-01-01", tz="UTC").timestamp() * 1000
    sel = coins[coins.first_funding_ms.notna() & (coins.first_funding_ms >= lo_ms) & (coins.first_funding_ms < hi_ms)]
    day = 86400 * 1000

    def leg(coin, start):
        c = d[(d.coin == coin) & (d.t >= start)].head(14)
        if len(c) < 14:
            return None
        entry, exit_ = c.o.iloc[0], c.c.iloc[-1]
        span_end = c.t.iloc[-1] + day
        f = fund[(fund.coin == coin) & (fund.time >= c.t.iloc[0]) & (fund.time < span_end)]
        return (entry - exit_) / entry * 1000 + f.rate.sum() * 1000 - 0.90, c.h.max() / entry - 1

    rows = []
    for coin, L in zip(sel.coin, sel.first_funding_ms):
        start = (int(L + H) // day + 1) * day  # first UTC day starting after L+1h
        a, b = leg(coin, start), leg("BTC", start)
        if a is None or b is None:
            continue
        rows.append({"coin": coin, "L": pd.to_datetime(L, unit="ms").date(), "pnl": a[0], "pump": a[1], "btc": b[0]})
    df = pd.DataFrame(rows)
    print(f"[v2 daily] holdout listings with data: {len(df)} of {len(sel)}")
    if len(df) < 20:
        print("VERDICT v2: too few to decide")
        return 0
    ex = df.pnl - df.btc
    c1 = df.pnl.mean() > 0 and tstat(df.pnl) > 2
    c2 = ex.mean() > 0 and tstat(ex) > 2
    c3 = df.pnl.median() > 0
    print(f"  mean P&L ${df.pnl.mean():.2f} per $1,000 per 14d  t {tstat(df.pnl):.2f}  -> {'yes' if c1 else 'no'}")
    print(f"  mean excess over BTC short ${ex.mean():.2f}  t {tstat(ex):.2f}  -> {'yes' if c2 else 'no'}")
    print(f"  median P&L ${df.pnl.median():.2f}  -> {'yes' if c3 else 'no'}")
    print(f"  share profitable {(df.pnl > 0).mean():.0%}; rose >= 50% at some point {(df.pump >= 0.5).mean():.0%}; "
          f"worst ${df.pnl.min():.0f}; best ${df.pnl.max():.0f}")
    print(f"VERDICT v2: {'PASS' if c1 and c2 and c3 else 'fail'}")
    return 0


if __name__ == "__main__" and "--daily" in sys.argv:
    raise SystemExit(main_daily())

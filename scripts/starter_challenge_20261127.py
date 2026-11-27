"""Topstep Starter Challenge ($10) payout probability with the bot (docs/PREREG_STARTER_20261127.md).

    uv run python -m scripts.starter_challenge_20261127 | tee docs/jx_runs/starter_challenge_20261127.txt
"""
import numpy as np
import pandas as pd

from ict import data as D
from scripts.radar_price import trades

TARGET, MLL, CAP, PAYOUT, COST, DAYS, ATTEMPTS = 100.0, 100.0, 1, 100.0, 24.5, 90, 3


def round_(pnl, mae, ts, i, end, attempts):
    """Trade from index i until +TARGET (pass), -MLL on worst open P&L (fail; reset if attempts remain), or the round's end.
    Returns (outcome, next index)."""
    bal, left = 0.0, attempts
    while i < len(pnl) and ts[i] < end:
        if bal - mae[i] <= -MLL or bal + pnl[i] <= -MLL:
            left -= 1
            if left == 0:
                return "fail", i + 1
            bal = 0.0
        else:
            bal += pnl[i]
            if bal >= TARGET:
                return "pass", i + 1
        i += 1
    return "expired", i


def main():
    t = trades(pd.read_parquet(D.PROCESSED_DIR / "ideas_orders_NQ.parquet"), D.load("1m"), 0)
    t = t.sort_values("entry_ts").reset_index(drop=True)
    k = np.minimum(1.0, CAP / np.maximum(t["contracts"].to_numpy(), 1))
    pnl, mae = t["net_pnl"].to_numpy() * k, t["mae_usd"].to_numpy() * k
    ts = pd.DatetimeIndex(t["entry_ts"])
    print(f"1-micro trades 2016-26: {len(t):,}; per-trade P&L median ${np.median(pnl):.2f}, "
          f"loss on losers median ${np.median(pnl[pnl < 0]):.2f}, win on winners median ${np.median(pnl[pnl > 0]):.2f}\n")
    rows, s0 = [], pd.Timestamp("2016-01-01", tz=ts.tz)
    while s0 <= pd.Timestamp("2025-10-01", tz=ts.tz):
        i = int(np.searchsorted(ts, s0))
        r1, j = round_(pnl, mae, ts, i, ts[i] + pd.Timedelta(days=DAYS), ATTEMPTS)
        if r1 != "pass":
            rows.append(("round 1 " + r1, np.nan))
        else:
            r2, j2 = round_(pnl, mae, ts, j, ts[min(j, len(ts) - 1)] + pd.Timedelta(days=DAYS), 1)
            rows.append(("payout" if r2 == "pass" else "round 2 " + r2,
                         (ts[j2 - 1] - ts[i]).days if r2 == "pass" else np.nan))
        s0 += pd.DateOffset(months=1)
    d = pd.DataFrame(rows, columns=["outcome", "days"])
    p = (d.outcome == "payout").mean()
    print(f"118 monthly starts 2016-01..2025-10 (round 1: 1 + 2 resets within 90 days; round 2: 1 attempt, 90 days)")
    for o, n in d.outcome.value_counts().items():
        print(f"   {o:<18} {n:>3}  ({n / len(d):.0%})")
    print(f"\nP(payout) {p:.0%} | median days to payout {d.days.median():.0f} | expected net per start "
          f"${PAYOUT * p - COST:,.2f} (payout $100 x P - $10 fee - $14.50 API month)")
    print(f"DECISION (registered: Starter Challenge first if P(payout) >= 30%): "
          f"{'Starter Challenge first' if p >= 0.30 else 'go straight to one Topstep 50K'}")


if __name__ == "__main__":
    main()

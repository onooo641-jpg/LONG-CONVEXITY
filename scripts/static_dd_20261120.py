"""CANDIDATES #52: coin-flip test of a static-drawdown prop firm (FTMO 2-Step 100K).

Rules (third-party summaries of FTMO's 2026 rules, docs/PREREG_LOOPHOLES_20261120.md):
fee EUR540 (~$585), refunded with the first payout; phase 1 +10%, phase 2 +5%,
4 trading days minimum per phase; 5% max daily loss, 10% static max loss;
funded: payout every 14 days of 80% of profit, balance back to start.
Daily loss is checked on realised P&L after each trade (slightly optimistic).

    uv run python scripts/static_dd_20261120.py
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from backtest.engine import BacktestConfig, simulate
from ict import data as D

LO, HI = "2016-01-01", "2026-10-29"
START, FEE, SPLIT = 100_000.0, 585.0, 0.80
DAILY, MAXL, T1, T2 = 5_000.0, 10_000.0, 10_000.0, 5_000.0


def run(pnl: np.ndarray, day: np.ndarray, ts: np.ndarray) -> dict:
    spent = paid = 0.0
    phase, bal, days, last_day, day_pnl = 1, 0.0, set(), None, 0.0
    fee_refund_due, last_payout, n_funded = False, None, 0
    spent += FEE
    for p, d, t in zip(pnl, day, ts):
        if d != last_day:
            day_pnl, last_day = 0.0, d
        bal += p
        day_pnl += p
        days.add(d)
        if bal <= -MAXL or day_pnl <= -DAILY:          # breach -> buy a new challenge
            spent += FEE
            phase, bal, days, fee_refund_due = 1, 0.0, set(), False
            day_pnl = 0.0
            continue
        if phase == 1 and bal >= T1 and len(days) >= 4:
            phase, bal, days = 2, 0.0, set()
        elif phase == 2 and bal >= T2 and len(days) >= 4:
            phase, bal, days, fee_refund_due, last_payout, n_funded = 3, 0.0, set(), True, t, n_funded + 1
        elif phase == 3 and bal > 0 and (t - last_payout) >= np.timedelta64(14, "D"):
            paid += SPLIT * bal
            if fee_refund_due:
                paid += FEE
                fee_refund_due = False
            bal, last_payout = 0.0, t
    return {"net": paid - spent, "paid": paid, "spent": spent, "funded": n_funded}


def main() -> int:
    bars = D.load("1m")
    orders = pd.read_parquet(D.PROCESSED_DIR / "ideas_orders_NQ.parquet")
    yrs = (pd.Timestamp(HI) - pd.Timestamp(LO)).days / 365.25
    for risk in (1000, 2000, 3000):
        t = simulate(orders, bars, BacktestConfig(risk_per_trade_usd=risk))
        t = t[t["filled"]]
        t = t[(t.entry_ts >= pd.Timestamp(LO, tz="UTC")) & (t.entry_ts < pd.Timestamp(HI, tz="UTC"))]
        t = t.sort_values("exit_ts").reset_index(drop=True)
        day = t.exit_ts.dt.tz_convert("America/New_York").dt.date.to_numpy()
        ts = t.exit_ts.dt.tz_localize(None).to_numpy()
        real = run(t.net_pnl.to_numpy(), day, ts)
        g, comm = t.gross_pnl.to_numpy(), (t.gross_pnl - t.net_pnl).to_numpy()
        rng = np.random.default_rng(1)
        flips = [run(np.abs(g) * rng.choice([-1, 1], len(t)) - comm, day, ts) for _ in range(200)]
        nets = np.array([f["net"] for f in flips])
        print(f"risk ${risk:>5,}/trade: coin-flip median net ${np.median(nets):>9,.0f} (${np.median(nets) / yrs:>6,.0f}/yr), "
              f"profitable {(nets > 0).mean():.0%}, 10th pct ${np.percentile(nets, 10):>9,.0f}, "
              f"median funded {np.median([f['funded'] for f in flips]):.0f}, median spent ${np.median([f['spent'] for f in flips]):,.0f} | "
              f"real net ${real['net']:>9,.0f} (funded {real['funded']}, spent ${real['spent']:,.0f})", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

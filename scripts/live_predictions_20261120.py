"""Pre-registered predictions for the live Topstep account (docs/PREREG_LIVE_20261120.md).

Writes docs/live_predictions.json (read by scripts/live_compare.py) and prints a summary.

    uv run python scripts/live_predictions_20261120.py
"""
from __future__ import annotations

import json
import pathlib

import numpy as np
import pandas as pd

from backtest.engine import BacktestConfig, simulate
from backtest.recycle import Policy, XFARules, recycle
from ict import data as D

RISK = 900.0
WINDOWS = {"full 2016-01..2026-10": ("2016-01-01", "2026-10-29"),
           "recent 2024-01..2026-10": ("2024-01-01", "2026-10-29")}
NS = (20, 40, 60, 100)
PCTS = (5, 25, 50, 75, 95)
OUT = pathlib.Path("docs/live_predictions.json")


def main() -> int:
    bars = D.load("1m")
    orders = pd.read_parquet(D.PROCESSED_DIR / "ideas_orders_NQ.parquet")
    allt = simulate(orders, bars, BacktestConfig(risk_per_trade_usd=RISK))
    preds = {"risk_usd": RISK, "tick": 0.25, "commission_per_micro_rt_model": 1.24,
             "exit_slippage_ticks_model": 1.0, "entry_slippage_ticks_model": 0.0, "windows": {}}
    for name, (lo, hi) in WINDOWS.items():
        lo_ts, hi_ts = pd.Timestamp(lo, tz="UTC"), pd.Timestamp(hi, tz="UTC")
        sig = allt[(allt.valid_from >= lo_ts) & (allt.valid_from < hi_ts)]
        t = sig[sig.filled].sort_values("exit_ts").reset_index(drop=True)
        months = (hi_ts - lo_ts).days / 30.44
        r = (t.net_pnl / RISK).to_numpy()
        w = {"trades": int(len(t)), "trades_per_month": len(t) / months,
             "signal_fill_rate": float(sig.filled.mean()),
             "win_rate": float((t.net_pnl > 0).mean()), "mean_net_r": float(r.mean()),
             "sd_net_r": float(r.std(ddof=1)),
             "stop_exit_share": float((t.exit_reason == "stop").mean()),
             "median_contracts": float(t.contracts.median()),
             "rolling_cum_net_r": {}}
        for n in NS:
            roll = np.convolve(r, np.ones(n), "valid")      # every run of n consecutive trades
            w["rolling_cum_net_r"][str(n)] = {str(p): float(np.percentile(roll, p)) for p in PCTS}
        # Topstep 50K account path from every monthly start in the window
        starts = pd.date_range(lo, pd.Timestamp(hi) - pd.DateOffset(months=12), freq="MS", tz="UTC")
        rows = []
        for s in starts:
            seg = t[t.entry_ts >= s].reset_index(drop=True)
            out = recycle(seg, XFARules(), policy=Policy.LOCK_FIRST)
            tl = pd.DataFrame(out["timeline"])
            first = lambda ev: (tl.loc[tl.event == ev, "ts"].min() - s).days if (tl.event == ev).any() else np.nan
            def net_at(m):
                cut = s + pd.DateOffset(months=m)
                sub = recycle(seg[seg.exit_ts < cut].reset_index(drop=True), XFARules(), policy=Policy.LOCK_FIRST)
                return sub["net"]
            busts_before_pass = int(((tl.event == "combine_bust") & (tl.ts < tl.loc[tl.event == "passed", "ts"].min())).sum()) \
                if (tl.event == "passed").any() else int((tl.event == "combine_bust").sum())
            rows.append({"days_to_first_pass": first("passed"), "days_to_first_payout": first("payout"),
                         "evals_before_first_pass": busts_before_pass + 1,
                         "net_3m": net_at(3), "net_6m": net_at(6), "net_12m": net_at(12)})
        a = pd.DataFrame(rows)
        q = lambda c: {str(p): float(np.nanpercentile(a[c], p)) for p in PCTS}
        w["topstep_from_monthly_starts"] = {
            "n_starts": int(len(a)),
            "days_to_first_pass": q("days_to_first_pass"),
            "days_to_first_payout": q("days_to_first_payout"),
            "share_first_payout_within_90d": float((a.days_to_first_payout <= 90).mean()),
            "share_first_payout_within_180d": float((a.days_to_first_payout <= 180).mean()),
            "evals_bought_before_first_pass": q("evals_before_first_pass"),
            "net_3m": q("net_3m"), "net_6m": q("net_6m"), "net_12m": q("net_12m"),
            "share_losing_12m": float((a.net_12m < 0).mean())}
        preds["windows"][name] = w
        print(f"\n== {name}: {len(t)} trades, {w['trades_per_month']:.1f}/month, fill rate {w['signal_fill_rate']:.0%}, "
              f"win rate {w['win_rate']:.1%}, mean {w['mean_net_r']:+.3f}R (sd {w['sd_net_r']:.2f}), "
              f"stop exits {w['stop_exit_share']:.0%}, median {w['median_contracts']:.0f} micros")
        for n in NS:
            b = w["rolling_cum_net_r"][str(n)]
            print(f"   cumulative net R after {n:>3} trades: 5% {b['5']:+.1f} | 25% {b['25']:+.1f} | 50% {b['50']:+.1f} | "
                  f"75% {b['75']:+.1f} | 95% {b['95']:+.1f}")
        ts = w["topstep_from_monthly_starts"]
        f = lambda d: f"5% {d['5']:,.0f} | 25% {d['25']:,.0f} | 50% {d['50']:,.0f} | 75% {d['75']:,.0f} | 95% {d['95']:,.0f}"
        print(f"   Topstep 50K, {ts['n_starts']} monthly starts:")
        print(f"     days to first pass: {f(ts['days_to_first_pass'])}")
        print(f"     evaluations bought before first pass: {f(ts['evals_bought_before_first_pass'])}")
        print(f"     days to first payout: {f(ts['days_to_first_payout'])} "
              f"(within 90d {ts['share_first_payout_within_90d']:.0%}, within 180d {ts['share_first_payout_within_180d']:.0%})")
        for m in ("net_3m", "net_6m", "net_12m"):
            print(f"     {m}: ${f(ts[m])}")
        print(f"     share of starts losing money over 12 months: {ts['share_losing_12m']:.0%}")
    OUT.write_text(json.dumps(preds, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

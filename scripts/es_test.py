"""The ES unseen-market test, exactly as docs/ES_PREREG.md defines it.

    uv run python scripts/es_test.py            # ES (MES), the registered test
    uv run python scripts/es_test.py --market NQ   # same code on NQ, as a check
                                                   # that it reproduces the ledger

Definitions and the win rule live in docs/ES_PREREG.md (committed first,
e24926e); this file only implements them.
"""

from __future__ import annotations

import argparse

import numpy as np
import pandas as pd

from backtest.engine import (COMMISSION_MNQ, TICK_VALUE_MNQ, BacktestConfig,
                             simulate)
from backtest.recycle import Policy, XFARules, recycle
from ict import data as D
from strategies.ltf_sweep import generate_orders

DECIDE = ("2016-01-01", "2026-10-29")
CONTEXT = ("2010-07-01", "2016-01-01")
RISK = 900.0
RULES, POLICY = XFARules(), Policy.LOCK_FIRST
N_FLIPS, SEED = 200, 1

#: MES: 0.25-point tick, $5 per point. Commission assumed equal to MNQ's model.
TICK_VALUE_MES = 1.25
COMMISSION_MES = COMMISSION_MNQ


def bars_for(market: str) -> pd.DataFrame:
    if market == "ES":
        return D.add_time_columns(D.load_raw("ES_v_0_1m_*.parquet"))
    return D.load("1m")


def config_for(market: str) -> BacktestConfig:
    if market == "ES":
        return BacktestConfig(risk_per_trade_usd=RISK, tick_value=TICK_VALUE_MES,
                              commission_per_round_turn=COMMISSION_MES)
    return BacktestConfig(risk_per_trade_usd=RISK, tick_value=TICK_VALUE_MNQ,
                          commission_per_round_turn=COMMISSION_MNQ)


def window(trades, lo, hi):
    t = trades[(trades["entry_ts"] >= pd.Timestamp(lo, tz="UTC"))
               & (trades["entry_ts"] < pd.Timestamp(hi, tz="UTC"))]
    return t.sort_values("exit_ts").reset_index(drop=True)


def chain(trades):
    out = recycle(trades, RULES, policy=POLICY)
    tl = pd.DataFrame(out["timeline"])
    p, b = (tl.event == "passed").sum(), (tl.event == "combine_bust").sum()
    return out, p / max(1, p + b)


def coin_flips(trades):
    """Same trade sizes, random sign on gross P&L, commission kept (jx_zero_edge.py)."""
    g = trades["gross_pnl"].to_numpy()
    comm = (trades["gross_pnl"] - trades["net_pnl"]).to_numpy()
    rng = np.random.default_rng(SEED)
    nets, passes = [], []
    for _ in range(N_FLIPS):
        s = rng.choice([-1, 1], len(trades))
        out, pr = chain(trades.assign(net_pnl=np.abs(g) * s - comm))
        nets.append(out["net"])
        passes.append(pr)
    return np.array(nets), np.array(passes)


def report(name, t):
    p = t["net_pnl"]
    pf = p[p > 0].sum() / -p[p < 0].sum()
    out, pr = chain(t)
    nets, passes = coin_flips(t)
    q95 = float(np.percentile(nets, 95))
    fee = float((t["gross_pnl"] - t["net_pnl"]).sum())
    print(f"\n=== {name}")
    print(f"  trades {len(t):,}   win {float((p > 0).mean()):.1%}   PF {pf:.3f}   "
          f"raw net ${p.sum():,.0f}   fees ${fee:,.0f}   "
          f"median contracts {int(t['contracts'].median())}   "
          f"median stop {t['risk_points'].median():.2f} pts")
    print(f"  recycling: net ${out['net']:,.0f}   withdrawn ${out['cash']:,.0f}   "
          f"spent ${out['cost']:,.0f}   pass {pr:.1%}   payouts {out['payouts']}   "
          f"longest dry {out['longest_dry_days']:,.0f} d")
    print(f"  coin flip x{N_FLIPS}: net median ${np.median(nets):,.0f}   "
          f"95th pct ${q95:,.0f}   pass median {np.median(passes):.1%}   "
          f"real beats {np.mean(nets < out['net']):.0%} of flips")
    years = t.assign(y=pd.DatetimeIndex(t["exit_ts"]).tz_convert(
        "America/New_York").year).groupby("y")["net_pnl"].sum()
    print("  raw net by year: " + "  ".join(f"{y} {v:,.0f}" for y, v in years.items()))
    return out["net"], q95


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--market", choices=["ES", "NQ"], default="ES")
    args = ap.parse_args(argv)

    bars = bars_for(args.market)
    print(f"{args.market}: {len(bars):,} bars  {bars.ts.min()} -> {bars.ts.max()}")
    orders = generate_orders(bars)
    trades = simulate(orders, bars, config_for(args.market))
    trades = trades[trades["filled"]].sort_values("exit_ts").reset_index(drop=True)

    net, q95 = report(f"DECIDES {DECIDE[0]} .. 2026-10-28", window(trades, *DECIDE))
    report(f"CONTEXT {CONTEXT[0]} .. 2015-12-31 (does not decide)",
           window(trades, *CONTEXT))

    verdict = "CONFIRMS" if net > q95 else "DOES NOT CONFIRM"
    print(f"\n=== VERDICT ({args.market}, pre-registered rule, deciding window)")
    print(f"  recycling net ${net:,.0f} vs coin-flip 95th pct ${q95:,.0f} -> {verdict}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

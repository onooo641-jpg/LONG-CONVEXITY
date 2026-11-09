"""Idea batch, exactly as docs/PREREG_BATCH_20261109.md defines it (fb76f72).

    uv run python scripts/idea_batch_20261109.py
"""

from __future__ import annotations

import dataclasses
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, "scripts")
from es_test import TICK_VALUE_MES  # noqa: E402
from backtest.engine import COMMISSION_MNQ, TICK_VALUE_MNQ, BacktestConfig, simulate  # noqa: E402
from backtest.recycle import Policy, XFARules, recycle  # noqa: E402
from ict import data as D  # noqa: E402
from strategies.ltf_sweep import LTFSweepConfig, generate_orders  # noqa: E402

RISK, COMM, N_FLIPS = 900.0, COMMISSION_MNQ, 100
RULES, POLICY = XFARules(), Policy.LOCK_FIRST
#: market -> (raw pattern or None for processed NQ, $ per 0.25 pt, exit slip in engine ticks)
MARKETS = {"NQ": (None, TICK_VALUE_MNQ, 1.0), "ES": ("ES", TICK_VALUE_MES, 1.0),
           "YM": ("YM", 0.125, 4.0), "RTY": ("RTY", 1.25, 0.4)}
DATASETS = [("NQ-S", "NQ", "2016-01-01", "2026-10-29"), ("NQ-O", "NQ", "2010-07-01", "2016-01-01"),
            ("ES", "ES", "2016-01-01", "2026-10-29"), ("YM", "YM", "2016-01-01", "2026-10-29"),
            ("RTY", "RTY", "2017-08-01", "2026-10-29")]


def window(t, lo, hi):
    t = t[(t["entry_ts"] >= pd.Timestamp(lo, tz="UTC")) & (t["entry_ts"] < pd.Timestamp(hi, tz="UTC"))]
    return t.sort_values("exit_ts").reset_index(drop=True)


def margin(t, funded_scale=1.0):
    """(recycling net, coin-flip median, margin)."""
    net = recycle(t, RULES, policy=POLICY, funded_scale=funded_scale)["net"]
    g = t["gross_pnl"].to_numpy()
    comm = (t["gross_pnl"] - t["net_pnl"]).to_numpy()
    rng = np.random.default_rng(1)
    flips = [recycle(t.assign(net_pnl=np.abs(g) * rng.choice([-1, 1], len(t)) - comm),
                     RULES, policy=POLICY, funded_scale=funded_scale)["net"] for _ in range(N_FLIPS)]
    med = float(np.median(flips))
    return net, med, net - med


def streak_pause(t):
    keep, streak, pause = [], 0, 0
    for pnl in t["net_pnl"]:
        keep.append(pause == 0)
        if pause:
            pause -= 1
        streak = streak + 1 if pnl < 0 else 0
        if streak >= 3:
            pause, streak = 5, 0
    return np.array(keep)


def equity_filter(t):
    prev = t["net_pnl"].rolling(20).sum().shift(1)
    return (prev > 0).to_numpy()


def main() -> int:
    bars, base_orders, base_trades, cfgs = {}, {}, {}, {}
    for mkt, (raw, tv, slip) in MARKETS.items():
        b = D.load("1m") if raw is None else D.add_time_columns(D.load_raw(f"{raw}_v_0_1m_*.parquet"))
        path = D.PROCESSED_DIR / f"ideas_orders_{mkt}.parquet"
        o = pd.read_parquet(path) if path.exists() else generate_orders(b)
        if not path.exists():
            o.to_parquet(path)
        cfg = BacktestConfig(risk_per_trade_usd=RISK, tick_value=tv,
                             commission_per_round_turn=COMM, exit_slippage_ticks=slip)
        t = simulate(o, b, cfg)
        bars[mkt], base_orders[mkt], cfgs[mkt] = b, o, cfg
        base_trades[mkt] = t[t["filled"]].sort_values("exit_ts").reset_index(drop=True)
        print(f"{mkt}: {len(o):,} orders, {len(base_trades[mkt]):,} fills", flush=True)

    def sim(mkt, orders, **cfg_changes):
        t = simulate(orders, bars[mkt], dataclasses.replace(cfgs[mkt], **cfg_changes))
        return t[t["filled"]].sort_values("exit_ts").reset_index(drop=True)

    def runner(orders, r):
        risk = (orders["entry_price"] - orders["stop_price"]).abs()
        return orders.assign(runner_target=orders["entry_price"] + orders["direction"] * r * risk)

    def time_stop(orders):
        cut = (orders["valid_from"] + pd.Timedelta("120min")).astype(orders["time_exit_ts"].dtype)
        return orders.assign(time_exit_ts=orders["time_exit_ts"].where(orders["time_exit_ts"] <= cut, cut))

    wide_orders = {}

    def wide(mkt):
        if mkt not in wide_orders:
            wide_orders[mkt] = generate_orders(bars[mkt], dataclasses.replace(LTFSweepConfig(),
                                                                               stop_buffer_points=2.0))
        return sim(mkt, wide_orders[mkt])

    fee = lambda t, pct: t[(t["contracts"] * COMM) <= pct * RISK].reset_index(drop=True)  # noqa: E731
    # Each idea: market -> (trades over the whole history, funded_scale).
    ideas = {
        "baseline": lambda m: (base_trades[m], 1.0),
        "17 long only": lambda m: (base_trades[m][base_trades[m]["direction"] > 0].reset_index(drop=True), 1.0),
        "18 short only": lambda m: (base_trades[m][base_trades[m]["direction"] < 0].reset_index(drop=True), 1.0),
        "19 runner 2R": lambda m: (sim(m, runner(base_orders[m], 2.0), scale_out_fraction=0.5,
                                       runner_stop_offset=0.0), 1.0),
        "20 runner 3R": lambda m: (sim(m, runner(base_orders[m], 3.0), scale_out_fraction=0.5,
                                       runner_stop_offset=0.0), 1.0),
        "21 funded x0.5": lambda m: (base_trades[m], 0.5),
        "22 funded x0.75": lambda m: (base_trades[m], 0.75),
        "23 streak pause": lambda m: (base_trades[m][streak_pause(base_trades[m])].reset_index(drop=True), 1.0),
        "24 equity filter": lambda m: (base_trades[m][equity_filter(base_trades[m])].reset_index(drop=True), 1.0),
        "25 fee cap 5%": lambda m: (fee(base_trades[m], 0.05), 1.0),
        "26 fee cap 3%": lambda m: (fee(base_trades[m], 0.03), 1.0),
        "27 stop buffer 2": lambda m: (wide(m), 1.0),
        "28 time stop 120m": lambda m: (sim(m, time_stop(base_orders[m])), 1.0),
    }

    res = {}
    for name, make in ideas.items():
        cache = {}
        for ds, mkt, lo, hi in DATASETS:
            if mkt not in cache:
                cache[mkt] = make(mkt)
            t, fs = cache[mkt]
            tw = window(t, lo, hi)
            p = tw["net_pnl"]
            pf = p[p > 0].sum() / -p[p < 0].sum()
            res[(name, ds)] = (*margin(tw, fs), pf, len(tw))
        line = "  ".join(f"{ds} {res[(name, ds)][2]:>8,.0f}" for ds, *_ in DATASETS)
        print(f"{name:<18} margin: {line}", flush=True)

    print("\n=== DETAIL  (trades / PF / recycling net / flip median / margin)")
    for name in ideas:
        print(f"  {name}")
        for ds, *_ in DATASETS:
            net, med, mg, pf, n = res[(name, ds)]
            print(f"    {ds:<5} {n:>5}  PF {pf:.3f}  net ${net:>9,.0f}  flip ${med:>9,.0f}  margin ${mg:>9,.0f}")

    print("\n=== VERDICTS  (margin beats baseline on NQ-S and NQ-O and >=2 of ES/YM/RTY)")
    for name in ideas:
        if name == "baseline":
            continue
        better = {ds: res[(name, ds)][2] > res[("baseline", ds)][2] for ds, *_ in DATASETS}
        others = sum(better[d] for d in ("ES", "YM", "RTY"))
        ok = better["NQ-S"] and better["NQ-O"] and others >= 2
        print(f"  {name:<18} NQ-S {'+' if better['NQ-S'] else '-'}  NQ-O {'+' if better['NQ-O'] else '-'}  "
              f"others {others}/3  -> {'PASS' if ok else 'fail'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Frozen 50K baseline (Jx, 2026-11-22): prices products from docs/radar/prop_assumptions_20261122.csv.

Promotions and rule changes go in the CSV, not in this script.
    uv run python -m scripts.prop_baseline_20261122 | tee docs/jx_runs/prop_baseline_20261122.txt
"""
import dataclasses

import numpy as np
import pandas as pd

from backtest.recycle import Policy, recycle
from ict import data as D
from scripts.firms2_20261120 import worst_dip
from scripts.radar_models2 import MODELS2
from scripts.radar_price import MODELS, scaled, trades

R = dataclasses.replace
A = pd.read_csv("docs/radar/prop_assumptions_20261122.csv")
T = trades(pd.read_parquet(D.PROCESSED_DIR / "ideas_orders_NQ.parquet"), D.load("1m"), 0)


def base(key):
    if key in MODELS:
        return MODELS[key][0][1], MODELS[key][0][2]
    return MODELS2[key][1][0][1], MODELS2[key][1][0][2]


def rules_of(row):
    r, risk = base(row.base_model)
    kw = dict(reset=float(row.reset_eval), activation=float(row.activation_on_pass))
    if row.billing == "monthly":
        kw.update(monthly=float(row.entry_price), one_time_price=None)
    else:
        kw.update(one_time_price=float(row.entry_price), monthly=0.0)
    if pd.notna(row.eval_consistency):
        kw["combine_consistency"] = float(row.eval_consistency)
    kw["combine_max_days"] = int(row.eval_time_limit_days) if pd.notna(row.eval_time_limit_days) else None
    return R(r, **kw), risk


def priced(rules, risk, dll):
    """Real net, worst dip, coin-flip median and share profitable; a soft DLL stops the day at -DLL (one trade per day in this data)."""
    s = scaled(T, risk / 900)
    g, comm = s["gross_pnl"].to_numpy(), (s["gross_pnl"] - s["net_pnl"]).to_numpy()
    cap = (lambda x: np.maximum(x, -dll)) if dll else (lambda x: x)
    pol = Policy.IMMEDIATE if rules.mll_locks_at is None else Policy.LOCK_FIRST
    real = recycle(s.assign(net_pnl=cap(s["net_pnl"].to_numpy())), rules, policy=pol)
    rng = np.random.default_rng(1)
    flips = np.array([recycle(s.assign(net_pnl=cap(np.abs(g) * rng.choice([-1, 1], len(s)) - comm)), rules, policy=pol)["net"] for _ in range(200)])
    return real["net"], worst_dip(real), float(np.median(flips)), float((flips > 0).mean())


def show(name, rules, risk, dll):
    real, dip, flip, prof = priced(rules, risk, dll)
    flag = real >= 22180 and flip >= 5000 and dip >= -5280
    print(f"{name:<62} | real ${real:>8,.0f} ({real / 44359:.0%}) | ${real / 10.83:>6,.0f}/yr | coin flip ${flip:>7,.0f} ({prof:.0%}) | "
          f"dip ${dip:>7,.0f} | {'MEETS FLAG RULE' if flag else '-'}", flush=True)


print("Frozen 50K baseline (inputs: docs/radar/prop_assumptions_20261122.csv). Friend's NQ trades 2016-01..2026-10, $900 risk.")
print("Flag rule: real >= $22,180, coin flip >= $5,000, worst dip >= -$5,280. Topstep 50K: $44,359 / $18,046 / -$3,520.\n")
for row in A.itertuples():
    r, risk = rules_of(row)
    dll = float(row.soft_dll) if pd.notna(row.soft_dll) else None
    if row.base_model == "blueberry_ascent50":
        show(f"{row.product}: expiry = $125 evaluation reset; no funded reset", r, risk, dll)
        show(f"{row.product}: expiry = $125 reset; $500 funded reset used", R(r, back2funded_max=99, back2funded_price=float(row.reset_funded)), risk, dll)
        show(f"{row.product}: (context) no 30-day limit", R(r, combine_max_days=None), risk, dll)
    else:
        show(row.product, r, risk, dll)

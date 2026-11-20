"""Free-reset sensitivity for scripts/ftmo_futures_20261120.py.

    uv run python scripts/ftmo_futures_sensitivity_20261120.py
"""
import dataclasses, sys
sys.argv=['x']
import importlib.util
spec=importlib.util.spec_from_file_location("f","scripts/ftmo_futures_20261120.py"); f=importlib.util.module_from_spec(spec); spec.loader.exec_module(f)
import pandas as pd
from backtest.engine import BacktestConfig, simulate
from backtest.recycle import Policy, recycle
from ict import data as D
bars=D.load("1m"); orders=pd.read_parquet(D.PROCESSED_DIR/"ideas_orders_NQ.parquet")
for risk, rules, name in [(900, f.GROWTH, "Growth"), (800, f.PRO, "Pro 100%")]:
    t=simulate(orders,bars,BacktestConfig(risk_per_trade_usd=risk)); t=t[t.filled]
    t=t[(t.entry_ts>=pd.Timestamp(f.LO,tz="UTC"))&(t.entry_ts<pd.Timestamp(f.HI,tz="UTC"))].sort_values("exit_ts").reset_index(drop=True)
    for fr in (False, True):
        o=recycle(t, dataclasses.replace(rules, free_reset_per_rebill=fr), policy=Policy.LOCK_FIRST)
        print(f"{name} free_reset={fr}: net ${o['net']:,.0f} spent ${o['cost']:,.0f}")

"""Topstep 50K with the optional $1,000 Daily Loss Limit, which doubles XFA payout caps ($2,000 -> $4,000 Standard, $3,000 -> $6,000
Consistency; topstep.com blog "trading risk management", topstep.com/no-activation-fee). The DLL counts open P&L in real time
(help.topstep.com 10490293) and liquidates for the day, it does not close the account: a trade whose open loss reaches $1,000 is cut
at -$1,000 (minus commission). Corrected model (real-time MLL). docs/AUDIT_PRE_LIVE_20261126.md addendum 3.

    uv run python -m scripts.audit_topstep_dll_20261127 | tee docs/jx_runs/audit_topstep_dll_20261127.txt
"""
import contextlib
import dataclasses as dc
import io

import numpy as np
import pandas as pd

from backtest.recycle import Policy, recycle
from ict import data as D
from scripts.firms2_20261120 import worst_dip
from scripts.radar_price import flip, trades

with contextlib.redirect_stdout(io.StringIO()):
    from scripts.manual_my_20261123 import m
    from scripts.audit_pre_live_20261126 import starts

R = dc.replace
ts, _ = m("topstep50")
CONS = R(ts, combine_consistency=0.55, consistency_target=0.4, consistency_days=3, payout_cap=3000.0, winning_days_required=0)
T = trades(pd.read_parquet(D.PROCESSED_DIR / "ideas_orders_NQ.parquet"), D.load("1m"), 0)


def dll_cut(t, dll=1000.0):
    comm = (t["gross_pnl"] - t["net_pnl"]).to_numpy()
    hit = t["mae_usd"].to_numpy() >= dll
    return t.assign(net_pnl=np.where(hit, -dll - comm, t["net_pnl"].to_numpy()),
                    mae_usd=np.minimum(t["mae_usd"].to_numpy(), dll))


ROWS = [("Standard, no DLL (cap $2,000)", ts, False), ("Standard + $1,000 DLL (cap $4,000)", R(ts, payout_cap=4000.0), True),
        ("Consistency, no DLL (cap $3,000)", CONS, False), ("Consistency + $1,000 DLL (cap $6,000)", R(CONS, payout_cap=6000.0), True),
        ("No-Activation $85/mo + DLL -$10 = $75/mo, reset $85, Consistency (cap $6,000)",
         R(CONS, payout_cap=6000.0, monthly=75.0, reset=85.0, activation=0.0), True)]
print("Topstep 50K, bot, 2016-01..2026-10, corrected model. Coin flip: 200 runs, seed 1, excursions swapped, DLL applied after the flip.")
print(f"trades whose open loss reaches $1,000: {(T.mae_usd >= 1000).sum()} of {len(T)} (winners among them: {((T.mae_usd >= 1000) & (T.net_pnl > 0)).sum()})\n")
for name, rules, dll in ROWS:
    t = dll_cut(T) if dll else T
    out = recycle(t, rules, policy=Policy.LOCK_FIRST)
    g, comm = T["gross_pnl"].to_numpy(), (T["gross_pnl"] - T["net_pnl"]).to_numpy()
    rng = np.random.default_rng(1)
    fl = []
    for _ in range(200):
        f = flip(T, g, comm, rng.choice([-1, 1], len(T)))
        fl.append(recycle(dll_cut(f) if dll else f, rules, policy=Policy.LOCK_FIRST)["net"])
    fl = np.array(fl)
    d = starts(t, rules)
    print(f"{name:<78} net ${out['net']:>8,.0f} | coin flip ${np.median(fl):>7,.0f} ({np.mean(fl > 0):.0%}) | dip ${worst_dip(out):>7,.0f} | "
          f"start median ${d.worst.median():,.0f}, 1 in 10 ${d.worst.quantile(.1):,.0f}, worst ${d.worst.min():,.0f} | 12m ${d.net12.median():,.0f}",
          flush=True)

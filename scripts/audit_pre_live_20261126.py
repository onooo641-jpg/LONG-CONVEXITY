"""Pre-live audit (docs/AUDIT_PRE_LIVE_20261126.md): what changes when the loss limit is checked on open P&L in real time,
and how sensitive the plan is to fills and costs.

    uv run python -m scripts.audit_pre_live_20261126 | tee docs/jx_runs/audit_pre_live_20261126.txt
"""
import contextlib
import dataclasses as dc
import io

import numpy as np
import pandas as pd

from backtest.engine import BacktestConfig, simulate
from backtest.recycle import Policy, recycle
from ict import data as D
from scripts.firms2_20261120 import worst_dip
from scripts.radar_price import flip

with contextlib.redirect_stdout(io.StringIO()):
    from scripts.portfolio_my_20261123 import P, T

R = dc.replace
LO, HI = "2016-01-01", "2026-10-29"
LD = P["LucidDaily 50K EOD (promo $85.40)"][0]
PRODUCTS = {
    "Topstep 50K Consistency path": P["Topstep 50K Consistency path"],
    "LucidDaily 50K, EOD eval + intraday funded (default), $85.40": (R(LD, intraday_trail_funded=True), 900, None),
    "LucidDaily 50K, EOD eval + EOD funded add-on, $165.20": (R(LD, one_time_price=165.2, reset=165.2), 900, None),
    "TTP Futures Prime 50K": P["TTP Futures Prime 50K"],
    "DayTraders EOD 50K ($105)": P["DayTraders EOD 50K ($105)"],
}


def pol(r):
    return Policy.IMMEDIATE if r.mll_locks_at is None else Policy.LOCK_FIRST


def prep(t, dll):
    if dll:
        t = t.assign(net_pnl=np.maximum(t["net_pnl"].to_numpy(), -dll))
    return t


def starts(t, rules):
    entry = pd.DatetimeIndex(t["entry_ts"])
    rows, s0 = [], pd.Timestamp("2016-01-01", tz=entry.tz)
    while s0 <= pd.Timestamp("2025-10-01", tz=entry.tz):
        ch = t[entry >= s0].reset_index(drop=True)
        tl = pd.DataFrame(recycle(ch, rules, policy=pol(rules))["timeline"])
        net = np.concatenate([[0.0], tl["net"].to_numpy()])
        pay = tl[tl.event == "payout"]
        t0 = ch["entry_ts"].iloc[0]
        y1 = tl[pd.to_datetime(tl.ts) < t0 + pd.DateOffset(months=12)]
        rows.append(dict(worst=net.min(), days=(pay["ts"].iloc[0] - t0).days if len(pay) else np.nan,
                         first=float(pay["cash"].iloc[0]) if len(pay) else np.nan,
                         net12=float(y1["net"].iloc[-1]) if len(y1) else 0.0, pos=bool((net > 0).any())))
        s0 += pd.DateOffset(months=1)
    return pd.DataFrame(rows)


print("A. Closed-P&L model (all figures before 2026-11-26) vs open P&L checked in real time (Topstep's verified rule).")
print("   2016-01..2026-10, friend's NQ trades at $900 risk. Coin flip: 200 runs, seed 1, random sign, commission kept, excursions swapped.\n")
for name, (rules, risk, dll) in PRODUCTS.items():
    t = prep(T, dll)
    a = recycle(t, R(rules, realtime_mll=False, intraday_trail_funded=False), policy=pol(rules))
    b = recycle(t, rules, policy=pol(rules))
    g, comm = t["gross_pnl"].to_numpy(), (t["gross_pnl"] - t["net_pnl"]).to_numpy()
    rng = np.random.default_rng(1)
    flips = np.array([recycle(flip(t, g, comm, rng.choice([-1, 1], len(t))), rules, policy=pol(rules))["net"] for _ in range(200)])
    print(f"{name}\n   closed-P&L ${a['net']:>8,.0f} ({a['payouts']} payouts) -> real-time ${b['net']:>8,.0f} ({b['payouts']} payouts), "
          f"worst dip ${worst_dip(b):,.0f}; coin-flip median ${np.median(flips):,.0f}, positive {np.mean(flips > 0):.0%}")

print("\nB. Money needed to start (real-time model), 118 monthly starts 2016-01..2025-10")
for name in ["Topstep 50K Consistency path", "LucidDaily 50K, EOD eval + intraday funded (default), $85.40",
             "LucidDaily 50K, EOD eval + EOD funded add-on, $165.20"]:
    rules, risk, dll = PRODUCTS[name]
    d = starts(prep(T, dll), rules)
    w = d.worst
    print(f"{name}\n   deepest loss median ${w.median():,.0f} | 1 in 4 worse than ${w.quantile(.25):,.0f} | 1 in 10 ${w.quantile(.10):,.0f} | "
          f"worst ${w.min():,.0f} | first payout median ${d['first'].median():,.0f} after {d.days.median():.0f} days | "
          f"12-month net median ${d.net12.median():,.0f} ({(d.net12 < 0).mean():.0%} losing) | never positive {(~d.pos).sum()}")

print("\nC. Fill and cost sensitivity, Topstep 50K Consistency, real-time model")
bars = D.load("1m")
orders = pd.read_parquet(D.PROCESSED_DIR / "ideas_orders_NQ.parquet")
base = BacktestConfig(risk_per_trade_usd=900)


def tr(cfg, o=orders):
    t = simulate(o, bars, cfg)
    t = t[t["filled"]]
    t = t[(t.entry_ts >= pd.Timestamp(LO, tz="UTC")) & (t.entry_ts < pd.Timestamp(HI, tz="UTC"))]
    return t.sort_values("exit_ts").reset_index(drop=True)


late = orders.assign(valid_from=orders.valid_from + pd.Timedelta(minutes=1))
late = late[late.valid_from < late.expires_at]
ts_rules = PRODUCTS["Topstep 50K Consistency path"][0]
for label, t in [("baseline: limit fills on touch, stop slips 1 tick, $1.24", tr(base)),
                 ("entry needs price 1 tick through the limit", tr(R(base, entry_fill_mode="through"))),
                 ("stop slips 2 ticks", tr(R(base, exit_slippage_ticks=2.0))),
                 ("orders placed 1 minute late", tr(base, late)),
                 ("all three together", tr(R(base, entry_fill_mode="through", exit_slippage_ticks=2.0),
                                           late))]:
    out = recycle(t, ts_rules, policy=pol(ts_rules))
    d = starts(t, ts_rules)
    print(f"   {label:<52} net ${out['net']:>8,.0f} dip ${worst_dip(out):>7,.0f} | start: median ${d.worst.median():,.0f}, "
          f"1 in 10 ${d.worst.quantile(.10):,.0f}, worst ${d.worst.min():,.0f}")

"""Malaysia-eligible multi-firm portfolio (docs/PREREG_PORTFOLIO_MY_20261123.md).

    uv run python -m scripts.portfolio_my_20261123 | tee docs/jx_runs/portfolio_my_20261123.txt
"""
import dataclasses

import numpy as np
import pandas as pd

from backtest.recycle import Policy, recycle
from ict import data as D
from scripts.radar_models2 import MODELS2
from scripts.radar_price import MODELS, scaled, trades

R = dataclasses.replace
T = trades(pd.read_parquet(D.PROCESSED_DIR / "ideas_orders_NQ.parquet"), D.load("1m"), 0)
MONTHS = pd.period_range("2016-01", "2026-10", freq="M")


def m(key):
    v = MODELS.get(key)
    return (v[0][1], v[0][2]) if v else (MODELS2[key][1][0][1], MODELS2[key][1][0][2])


ts, ts_r = m("topstep50")
ttp, ttp_r = m("ttp_prime50_r79")
dte, dte_r = m("dt_eod50")
ld, ld_r = m("lucid_daily50")
lf, lf_r = m("lucidflex50")
P = {
    "Topstep 50K Consistency path": (R(ts, combine_consistency=0.55, consistency_target=0.4, consistency_days=3, payout_cap=3000.0,
                                       winning_days_required=0), ts_r, None),
    "TTP Futures Prime 50K": (ttp, ttp_r, None),
    "DayTraders EOD 50K ($105)": (R(dte, one_time_price=105.0, reset=105.0, activation=5.0, monthly=0.0), dte_r, 1250.0),
    "LucidDaily 50K EOD (list $122)": (R(ld, payout_cap=float("inf"), payout_min=500.0, one_time_price=122.0, reset=122.0), ld_r, None),
    "LucidDaily 50K EOD (promo $85.40)": (R(ld, payout_cap=float("inf"), payout_min=500.0, one_time_price=85.4, reset=85.4), ld_r, None),
    "LucidFlex 50K DLL ON ($80.50)": (R(lf, one_time_price=80.5, reset=80.0, monthly=0.0), lf_r, 1200.0),
}


def monthly(rules, risk, dll):
    s = scaled(T, risk / 900)
    if dll:
        s = s.assign(net_pnl=np.maximum(s["net_pnl"].to_numpy(), -dll))
    out = recycle(s, rules, policy=Policy.IMMEDIATE if rules.mll_locks_at is None else Policy.LOCK_FIRST)
    tl = pd.DataFrame(out["timeline"])
    tl["m"] = pd.to_datetime(tl.ts).dt.tz_localize(None).dt.to_period("M")
    net = tl.groupby("m")["net"].last().reindex(MONTHS).ffill().fillna(0)
    return net, out["net"]


def rep(name, cum):
    mon = cum.diff().fillna(cum.iloc[0])
    r12 = mon.rolling(12).sum().dropna()
    dip = float((cum - np.maximum.accumulate(np.maximum(cum, 0))).min())
    print(f"{name:<44} net ${cum.iloc[-1]:>9,.0f} | ${cum.iloc[-1] / 10.83:>7,.0f}/yr | avg ${mon.mean():>6,.0f}/mo | last 36m ${mon[-36:].mean():>6,.0f}/mo | "
          f"months >= $300 {(mon >= 300).mean():>4.0%} | worst 12m ${r12.min():>8,.0f} | worst dip ${dip:>8,.0f}", flush=True)


print("Malaysia-eligible portfolio; friend's NQ trades 2016-01..2026-10 at $900 risk; same trades on every account.\n")
C = {}
for name, (rules, risk, dll) in P.items():
    C[name], _ = monthly(rules, risk, dll)
    rep(name, C[name])
print()
core = ["Topstep 50K Consistency path", "TTP Futures Prime 50K", "DayTraders EOD 50K ($105)", "LucidDaily 50K EOD (list $122)"]
rep("COMBINED: Topstep + TTP + DayTraders + LucidDaily (1 each)", sum(C[k] for k in core))
rep("COMBINED, LucidDaily at promo $85.40 (1 each)", sum(C[k] for k in core[:3]) + C["LucidDaily 50K EOD (promo $85.40)"])
rep("COMBINED x5 per firm (per-firm caps; same trades)", 5 * sum(C[k] for k in core))

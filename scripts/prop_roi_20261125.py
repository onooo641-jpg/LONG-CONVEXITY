"""ROI of the approved Malaysia-eligible prop products (START_HERE 4a), same runs as scripts/portfolio_my_20261123.py.

    uv run python -m scripts.prop_roi_20261125 | tee docs/jx_runs/prop_roi_20261125.txt
ROI on fees = net / total fees paid 2016-26 (recycle()'s "roi"). Return on cash needed = average net per year / |worst dip| (the cash
you must be able to lose before the income comes back).
"""
import contextlib
import io

import numpy as np
import pandas as pd

from backtest.recycle import Policy, recycle
with contextlib.redirect_stdout(io.StringIO()):  # the imported module prints its own portfolio report on import
    from scripts.portfolio_my_20261123 import MONTHS, P, T
from scripts.radar_price import MODELS, scaled

YEARS = 10.83
ts_std = MODELS["topstep50"][0]
td = [x for x in MODELS["tradeday"] if "85" in x[0]][0]
ROWS = [
    ("LucidDaily 50K EOD ($85.40 promo)", P["LucidDaily 50K EOD (promo $85.40)"]),
    ("TTP Futures Prime 50K ($99, reset $79)", P["TTP Futures Prime 50K"]),
    ("DayTraders EOD 50K ($105 + $5)", P["DayTraders EOD 50K ($105)"]),
    ("Topstep 50K Consistency path", P["Topstep 50K Consistency path"]),
    ("Topstep 50K Standard path", (ts_std[1], ts_std[2], None)),
    ("LucidFlex 50K DLL ON ($80.50)", P["LucidFlex 50K DLL ON ($80.50)"]),
    ("TradeDay 50K ($85 code)", (td[1], td[2], None)),
]


def run(rules, risk, dll):
    s = scaled(T, risk / 900)
    if dll:
        s = s.assign(net_pnl=np.maximum(s["net_pnl"].to_numpy(), -dll))
    out = recycle(s, rules, policy=Policy.IMMEDIATE if rules.mll_locks_at is None else Policy.LOCK_FIRST)
    tl = pd.DataFrame(out["timeline"])
    tl["m"] = pd.to_datetime(tl.ts).dt.tz_localize(None).dt.to_period("M")
    cum = tl.groupby("m")["net"].last().reindex(MONTHS).ffill().fillna(0)
    dip = float((cum - np.maximum.accumulate(np.maximum(cum, 0))).min())
    return out, dip


print("ROI of approved prop products, friend's NQ trades 2016-01..2026-10 (same model as portfolio_my_20261123)\n")
print(f"{'Product':<40} {'net':>9} {'fees paid':>10} {'withdrawn':>10} {'ROI on fees':>12} {'per yr':>8} {'worst dip':>10} "
      f"{'return on cash/yr':>18} {'accounts':>9} {'payouts':>8}")
tot = {"net": 0.0, "cost": 0.0, "cash": 0.0}
for name, (rules, risk, dll) in ROWS:
    out, dip = run(rules, risk, dll)
    py = out["net"] / YEARS
    print(f"{name:<40} ${out['net']:>8,.0f} ${out['cost']:>9,.0f} ${out['cash']:>9,.0f} {out['roi']:>11.0%} ${py:>7,.0f} ${dip:>9,.0f} "
          f"{py / abs(dip) if dip else float('nan'):>17.0%} {out['accounts_bought']:>9} {out['payouts']:>8}")
    if name.split(" (")[0] in ("LucidDaily 50K EOD", "TTP Futures Prime 50K", "DayTraders EOD 50K", "Topstep 50K Consistency path"):
        for k in tot:
            tot[k] += out[k]
print(f"\n4-firm portfolio (LucidDaily promo + TTP + DayTraders + Topstep Consistency, 1 account each): net ${tot['net']:,.0f}, fees "
      f"${tot['cost']:,.0f}, ROI on fees {tot['net'] / tot['cost']:.0%}; per year ${tot['net'] / YEARS:,.0f}; against the combined worst dip "
      f"$12,248 (portfolio_my_20261123.txt) = {tot['net'] / YEARS / 12248:.0%}/yr on cash needed")

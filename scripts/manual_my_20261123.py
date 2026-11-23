"""Manual-entry options for a Malaysian account holder (3-minute entry delay, vs Topstep at 3 minutes $37,348).

Top One Elite ACCESS 50K (bots banned; rules from help.toponefutures.com, 2026-10) and the approved bot firms traded manually.
    uv run python -m scripts.manual_my_20261123 | tee docs/jx_runs/manual_my_20261123.txt
"""
import dataclasses

import pandas as pd

from backtest.recycle import Policy, XFARules
from ict import data as D
from scripts.radar_models2 import MODELS2
from scripts.radar_price import MODELS, price, trades

R = dataclasses.replace
T = trades(pd.read_parquet(D.PROCESSED_DIR / "ideas_orders_NQ.parquet"), D.load("1m"), 3)
REF = (37348, -3094)


def topone(price_, activation):
    return XFARules(profit_target=3000, loss_limit=2000, combine_max_contracts=30, combine_max_days=30, combine_consistency=None,
                    funded_loss_limit=2000, mll_locks_at=2100, lock_level=100.0, winning_day_min=250.0, winning_days_required=5,
                    consistency_target=0.4, consistency_days=1, payout_needs_both=True, payout_buffer=2000.0, payout_goal=(2500.0, 750.0),
                    payout_min=500.0, payout_cap=1500.0, payout_share=0.5, profit_split=0.9, profit_since_payout_required=True,
                    one_time_price=price_, reset=35.0, monthly=0.0, activation=activation, combine_mll_locks=True, payout_locks_mll=True)


def m(key):
    v = MODELS.get(key)
    return (v[0][1], v[0][2]) if v else (MODELS2[key][1][0][1], MODELS2[key][1][0][2])


ts, ts_r = m("topstep50")
ttp, ttp_r = m("ttp_prime50_r79")
dte, dte_r = m("dt_eod50")
ld, ld_r = m("lucid_daily50")
lf, lf_r = m("lucidflex50")
ROWS = [
    ("Top One Elite ACCESS 50K, $189 list + $189 activation", topone(189.0, 189.0), 900),
    ("Top One Elite ACCESS 50K, $39 promo + $142 activation", topone(39.0, 142.0), 900),
    ("Topstep 50K Consistency path (manual)", R(ts, combine_consistency=0.55, consistency_target=0.4, consistency_days=3, payout_cap=3000.0,
                                                  winning_days_required=0), ts_r),
    ("TTP Futures Prime 50K (manual)", ttp, ttp_r),
    ("DayTraders EOD 50K $105 (manual)", R(dte, one_time_price=105.0, reset=105.0, activation=5.0, monthly=0.0), dte_r),
    ("LucidDaily 50K EOD $85.40 promo (manual)", R(ld, payout_cap=float("inf"), payout_min=500.0, one_time_price=85.4, reset=85.4), ld_r),
    ("LucidFlex 50K DLL ON $80.50 (manual)", R(lf, one_time_price=80.5, reset=80.0, monthly=0.0), lf_r),
]
print("Manual entry (3-minute delay). Flag rule vs Topstep at 3 minutes: real >= $18,674, coin flip >= $5,000, dip >= -$4,641.\n")
for name, rules, risk in ROWS:
    pol = Policy.IMMEDIATE if rules.mll_locks_at is None else Policy.LOCK_FIRST
    real, dip, flip, prof = price(T, rules, risk, pol)
    flag = real >= 0.5 * REF[0] and flip >= 5000 and dip >= 1.5 * REF[1]
    print(f"{name:<58} | real ${real:>8,.0f} ({real / REF[0]:.0%} of Topstep 3-min) | coin flip ${flip:>7,.0f} ({prof:.0%}) | dip ${dip:>7,.0f} | "
          f"{'QUALIFIES' if flag else '-'}", flush=True)
print("\nTop One: bots banned (manual only), Malaysia not on its restricted list; soft DLL / daily pauses not modelled; the 50%-new-profit rule")
print("from the 2nd payout is approximated by a $750 profit-since-last-payout goal.")

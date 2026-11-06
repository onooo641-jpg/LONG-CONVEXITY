"""Rough LucidFlex 50K model on the same $900 LTF-sweep trades. ESTIMATE.

    uv run python scripts/jx_lucid.py

Rules are from third-party summaries found 2026-11-06, NOT Lucid's own pages
(the official page fetch was not approved): one-time eval ~$140 (often ~$95
discounted), reset ~$95, target $3,000, $2,000 EOD trailing MLL that locks near
the start (+$100), a payout request moves the floor up the same way, 5 winning
days of $150, 50% of balance, 90/10, no activation fee, no monthly fee.
Payout cap unknown -> run at $2,000 and $4,000. The +$100 lock is modelled as
$0 (XFARules' lock), a small optimism.

Cost is computed here, not by backtest.recycle.costs(), because that function
assumes a monthly subscription with a free reset credit each month.
"""
import sys
sys.path.insert(0, "scripts")
import dataclasses
import pandas as pd
from jx_checks import load, filled, report_history
from backtest.recycle import recycle, Policy, XFARules
from ict import data as D

bars = load(None, "2015-11-17")
orders = pd.read_parquet(D.PROCESSED_DIR / "jx_orders_all.parquet")
h = report_history(filled(orders, bars, 900.0))
for price, reset in ((140.0, 95.0), (95.0, 95.0)):
    for cap in (2000.0, 4000.0):
        for pol in (Policy.LOCK_FIRST, Policy.IMMEDIATE):
            r = dataclasses.replace(XFARules(), payout_cap=cap, mll_locks_at=2000.0,
                                    monthly=0.0, reset=0.0, activation=0.0, api_monthly=0.0)
            o = recycle(h, r, policy=pol)
            cost = price + (o["accounts_bought"] - 1) * reset
            print(f"eval ${price:.0f} reset ${reset:.0f} cap ${cap:,.0f} {pol.name:<10} "
                  f"accounts {o['accounts_bought']} xfa {o['funded_earned']} pay {o['payouts']} "
                  f"withdrawn ${o['cash']:,.0f} cost ${cost:,.0f} net ${o['cash'] - cost:,.0f}")

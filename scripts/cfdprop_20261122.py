"""#296 CFD prop recycling (docs/PREREG_BATCH10_20261122.md): FTMO 2-Step priced with recycle.py (phase2_target, fee refund).

Rules from FTMO's own pages (data/public/propverify): 10% then 5% target, 5% max daily loss, 10% static max loss, no consistency on 2-Step,
up to 90% split (80% used), fee refunded with the first reward, EAs / algorithmic trading allowed, $400K max allocation, Malaysia not restricted.
Price not readable -> [sens] brackets. CFD cost: 1.5 index points per round trip per NQ-equivalent contract ($30) replaces the commission.
    uv run python -m scripts.cfdprop_20261122 | tee docs/jx_runs/cfdprop_20261122.txt
"""
import dataclasses

import numpy as np
import pandas as pd

from backtest.recycle import Policy, XFARules, recycle
from ict import data as D
from scripts.firms2_20261120 import worst_dip
from scripts.radar_price import scaled, trades

T = trades(pd.read_parquet(D.PROCESSED_DIR / "ideas_orders_NQ.parquet"), D.load("1m"), 0)


def ftmo2(size, price, split=0.8):
    tgt1, tgt2, mll, dll = 0.10 * size, 0.05 * size, 0.10 * size, 0.05 * size
    return XFARules(profit_target=tgt1, phase2_target=tgt2, loss_limit=mll, funded_loss_limit=mll, static_dd=True, mll_locks_at=None,
                    daily_loss_limit=dll, combine_max_contracts=10_000, winning_day_min=0.0, winning_days_required=0, payout_share=1.0,
                    payout_cap=float("inf"), payout_buffer=0.0, payout_min=0.0, profit_split=split, combine_consistency=None,
                    consistency_target=None, combine_mll_locks=False, payout_locks_mll=False, profit_since_payout_required=True,
                    one_time_price=price, reset=price, monthly=0.0, activation=0.0, refund_fee_on_first_payout=True)


def price(rules, risk):
    s = scaled(T, risk / 900)
    g = s["gross_pnl"].to_numpy()
    comm = s["contracts"].to_numpy() * 3.0  # contracts are micros ($2/pt): 1.5 pts round trip = $3 per micro (= $30 per NQ-equivalent)
    real = recycle(s.assign(net_pnl=g - comm), rules, policy=Policy.IMMEDIATE)
    rng = np.random.default_rng(1)
    flips = np.array([recycle(s.assign(net_pnl=np.abs(g) * rng.choice([-1, 1], len(s)) - comm), rules, policy=Policy.IMMEDIATE)["net"]
                      for _ in range(200)])
    return real, float(np.median(flips)), float((flips > 0).mean())


print("FTMO 2-Step (CFD, US100 stand-in for NQ). Flag rule: real >= $22,180, coin flip >= $5,000, worst dip >= -$5,280 (Topstep 50K $44,359).\n")
for size in (50_000, 100_000):
    mll, dll = 0.10 * size, 0.05 * size
    risk = min(0.45 * mll, 0.875 * dll)
    for p in ((300, 400) if size == 50_000 else (500, 650)):
        real, flip, prof = price(ftmo2(size, float(p)), risk)
        dip = worst_dip(real)
        flag = real["net"] >= 22180 and flip >= 5000 and dip >= -5280
        print(f"FTMO 2-Step {size // 1000}K at ${p} [sens], risk ${risk:,.0f}/trade | real ${real['net']:>9,.0f} ({real['net'] / 44359:.0%} of Topstep) | "
              f"coin flip ${flip:>9,.0f} ({prof:.0%}) | dip ${dip:>8,.0f} | {'would flag' if flag else '-'}", flush=True)
print("\nCaveats: price unverified (not on the rendered pages); payouts modelled as soon as profit exists (FTMO pays on a 14-day cycle);")
print("80% split (up to 90% with scaling); running the strategy on FTMO needs an MT5 / cTrader / DXtrade EA port (engineering work).")
print("\n(context, not the registered sizing) FTMO 2-Step 100K at $500 with smaller risk per trade:")
for risk in (900.0, 1500.0, 2500.0):
    real, flip, prof = price(ftmo2(100_000, 500.0), risk)
    print(f"  risk ${risk:,.0f}/trade | real ${real['net']:>9,.0f} | coin flip ${flip:>9,.0f} ({prof:.0%}) | dip ${worst_dip(real):>8,.0f}", flush=True)

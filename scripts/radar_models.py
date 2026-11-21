"""Prop-firm models written from the firms' own pages as collected by the radar (data/radar/snapshots, 2026-11-21).
Used by scripts/radar_price.py. See docs/PREREG_RADAR_20261121.md addendum 2.
"""
from __future__ import annotations

import dataclasses

from backtest.recycle import XFARules

B = XFARules()

# Alpha Futures Standard 50K (help.alpha-futures.com: Standard Account Overview, Payout Policy, MLL, Scaling Plan,
# Daily Loss Guard; all dated July 2026). EOD trailing $2,000 that stops at the starting balance (eval and qualified);
# target $3,000 with 50% eval consistency; $129/month, reset $109, no activation fee; 50 micros in eval;
# qualified scaling 20/30/50 micros at <$1,500 / $1,500-2,000 / >$2,000 profit (= the Topstep 50K ladder);
# payouts: up to 50% of profit, every 5 winning days >= $200, 40% consistency, min $500, max $3,000, 90% split;
# a payout does not move the MLL. Qualified daily loss guard $1,000 is a soft lock (risk sized below it: $875).
ALPHA_STD50 = dataclasses.replace(
    B, profit_target=3000, loss_limit=2000, combine_max_contracts=50, combine_consistency=0.50, combine_mll_locks=True,
    funded_loss_limit=2000, mll_locks_at=2000, lock_level=0.0, funded_scaling=True, winning_day_min=200.0,
    winning_days_required=5, consistency_target=0.40, payout_needs_both=True, payout_share=0.50, payout_cap=3000.0,
    payout_min=500.0, payout_locks_mll=False, profit_since_payout_required=False, profit_split=0.90,
    monthly=129.0, reset=109.0, activation=0.0, api_monthly=0.0)

# Blue Guardian Elite 50K (help.blueguardian.com "Elite account rules", updated 2026-11-13). One phase: target $3,000,
# EOD trailing $2,000 that trails for the whole evaluation; funded floor locks at start + $100 (also after any payout);
# 40 micros both phases; payouts from 3 days after the first trade, profit above $52,100 buffer, 40% consistency,
# first cap $2,500 (later $3,000; modelled $2,500 throughout, conservative), min $500, 90% split; reset $141 fixed;
# one-time purchase, no monthly or activation fee. Daily loss limit $1,000 soft (risk $875).
# Purchase price NOT readable from the static pages (loaded by script) -> bracketed, sensitivity only.
BG_ELITE50 = dataclasses.replace(
    B, profit_target=3000, loss_limit=2000, combine_max_contracts=40, combine_mll_locks=False, funded_loss_limit=2000,
    mll_locks_at=2100, lock_level=100.0, funded_scaling=False, winning_days_required=0, consistency_target=0.40,
    consistency_days=3, payout_buffer=2100.0, payout_cap=2500.0, payout_min=500.0, profit_split=0.90,
    one_time_price=141.0, reset=141.0, monthly=0.0, activation=0.0, api_monthly=0.0)

MODELS = {
    "alpha_std50": [("Alpha Futures Standard 50K", ALPHA_STD50, 875)],
    "bg_elite50": [("Blue Guardian Elite 50K, price $141 [sens]", BG_ELITE50, 875),
                   ("Blue Guardian Elite 50K, price $350 [sens]", dataclasses.replace(BG_ELITE50, one_time_price=350.0), 875)],
}

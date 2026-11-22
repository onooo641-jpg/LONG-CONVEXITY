"""Prop-firm models written from the firms' own pages as collected by the radar (data/radar/snapshots, 2026-11-21).
Used by scripts/radar_price.py. See docs/PREREG_RADAR_20261121.md addendum 2.
"""
from __future__ import annotations

import dataclasses

from backtest.recycle import Policy, XFARules

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

# Addendum 5: directory-found firms (rules own help centre; price third-party directory listing).
GOAT_FLEX50 = dataclasses.replace(
    B, profit_target=3000, loss_limit=2000, combine_max_contracts=30, combine_consistency=0.50, combine_mll_locks=True,
    funded_loss_limit=2000, mll_locks_at=2000, lock_level=0.0, funded_scaling=False, winning_day_min=250.0,
    winning_days_required=5, payout_share=0.50, payout_cap=2000.0, payout_min=500.0, profit_split=0.80,
    one_time_price=218.0, reset=218.0, monthly=0.0, activation=0.0, api_monthly=0.0)
BLUEBERRY_ASCENT50 = dataclasses.replace(
    B, profit_target=3000, loss_limit=2000, combine_max_contracts=20, combine_max_days=30, combine_mll_locks=False,
    funded_loss_limit=2000, mll_locks_at=2100, lock_level=100.0, funded_scaling=False, winning_day_min=200.0,
    winning_days_required=5, consistency_target=0.35, payout_needs_both=True, payout_buffer=2100.0, payout_cap=2500.0,
    payout_min=500.0, profit_split=0.90, one_time_price=245.0, reset=125.0, monthly=0.0, activation=0.0, api_monthly=0.0)
# Addendum 6: lock and contract scaling read from "Elite drawdown, daily loss limit and contracts" (2026-10-18): floor locks at start + $100;
# funded contracts 2 / 3 / 4 minis below $2,500 / from $2,500 / from $3,499 (the model's ladder applies in both phases: conservative,
# since the evaluation really has 4 from day one).
FE_ELITE50 = dataclasses.replace(
    B, profit_target=3000, loss_limit=2000, combine_max_contracts=40, combine_consistency=0.50, combine_mll_locks=True,
    funded_loss_limit=2000, mll_locks_at=2100, lock_level=100.0, funded_scaling=False,
    ladder=((2500.0, 20), (3499.0, 30), (float("inf"), 40)), winning_day_min=150.0,
    winning_days_required=6, payout_share=0.50, payout_cap=2000.0, payout_min=500.0, profit_split=0.90,
    one_time_price=128.0, reset=89.0, monthly=0.0, activation=0.0, api_monthly=0.0)  # reset $89: own 'Reset fees' page (addendum 13)

# Addendum 8: MFFU Builder 50K (own help centre, 2026-10-21)
MFFU_BUILDER50 = dataclasses.replace(
    B, profit_target=3000, loss_limit=2000, combine_max_contracts=40, combine_mll_locks=False, funded_loss_limit=2000,
    mll_locks_at=2000, lock_level=0.0, funded_scaling=False, winning_days_required=0, consistency_target=0.50, consistency_days=2,
    payout_buffer=2100.0, payout_goal=(500.0, 500.0), payout_cap=2000.0, payout_min=500.0, max_payouts_per_xfa=5, profit_split=0.80,
    one_time_price=153.0, reset=153.0, monthly=0.0, activation=0.0, api_monthly=0.0)

# Addendum 9: MFFU Studio (static MLL, payouts of all profit above $0 any time, min $250/$100, 80/20; own help centre 2026-10-14).
def _studio(size, price, mll, target, micros, pmin):
    return dataclasses.replace(
        B, profit_target=target, loss_limit=mll, static_dd=True, combine_max_contracts=micros, funded_loss_limit=mll, mll_locks_at=None,
        lock_level=0.0, funded_scaling=False, winning_days_required=0, payout_buffer=0.0, payout_cap=float("inf"), payout_min=pmin,
        payout_locks_mll=False, profit_since_payout_required=False, profit_split=0.80, one_time_price=price, reset=price, monthly=0.0,
        activation=0.0, api_monthly=0.0)


# Addendum 10
TTP_PRIME50 = dataclasses.replace(
    B, profit_target=3000, loss_limit=2000, combine_max_contracts=50, combine_consistency=0.40, combine_max_days=30, combine_mll_locks=True,
    funded_loss_limit=2000, mll_locks_at=2000, lock_level=0.0, funded_scaling=False, winning_day_min=150.0, winning_days_required=5,
    payout_share=0.50, payout_cap=2500.0, payout_min=0.0, profit_split=0.80, one_time_price=99.0, reset=99.0, monthly=0.0, activation=0.0,
    api_monthly=0.0)


def _tl(dd, target, micros, price):
    return dataclasses.replace(
        B, profit_target=target, loss_limit=dd, combine_max_contracts=micros, combine_consistency=0.40, combine_max_days=60,
        combine_mll_locks=True, funded_loss_limit=dd, mll_locks_at=dd, lock_level=0.0, funded_scaling=False, winning_days_required=0,
        payout_buffer=dd, payout_cap=float("inf"), payout_min=0.0, profit_split=0.80, one_time_price=price, reset=price, monthly=0.0,
        activation=0.0, api_monthly=0.0)


# Addendum 12: DayTraders EOD 50K (own help centre 2026-10-22); price bracket, sensitivity only
DT_EOD50 = dataclasses.replace(
    B, profit_target=3000, loss_limit=2000, combine_max_contracts=100, combine_consistency=0.50, combine_mll_locks=True,
    funded_loss_limit=2000, mll_locks_at=2000, lock_level=0.0, funded_scaling=False, winning_day_min=200.0, winning_days_required=8,
    consistency_target=0.30, consistency_days=8, payout_needs_both=True, payout_buffer=2000.0, payout_cap=2000.0, payout_min=500.0,
    profit_split=1.0, one_time_price=99.0, reset=99.0, monthly=0.0, activation=5.0, api_monthly=0.0)

MODELS = {
    "dt_eod50": [("DayTraders EOD 50K, $99 [sens]", DT_EOD50, 875),
                 ("DayTraders EOD 50K, $199 [sens]", dataclasses.replace(DT_EOD50, one_time_price=199.0, reset=199.0), 875)],
    "ttp_prime50": [("TTP Futures Prime 50K ($99)", TTP_PRIME50, 875)],
    "ttp_prime150": [("TTP Futures Prime 150K ($289)", dataclasses.replace(
        TTP_PRIME50, profit_target=9000, loss_limit=4500, combine_max_contracts=150, funded_loss_limit=4500, mll_locks_at=4500,
        payout_cap=5000.0, one_time_price=289.0, reset=289.0), 2025)],
    "traders_launch": [("Traders Launch 100K ($159)", _tl(1000.0, 2000.0, 20, 159.0), 450),
                       ("Traders Launch 200K ($299)", _tl(2000.0, 4000.0, 40, 299.0), 900)],
    "mffu_studio": [("MFFU Studio #001 $10K ($140)", _studio(10_000, 140.0, 500.0, 1000.0, 10, 250.0), 225, Policy.IMMEDIATE),
                    ("MFFU Studio #002 $20K ($280)", _studio(20_000, 280.0, 1000.0, 2000.0, 20, 250.0), 450, Policy.IMMEDIATE),
                    ("MFFU Studio #003 $5K ($75)", _studio(5_000, 75.0, 250.0, 500.0, 5, 100.0), 112, Policy.IMMEDIATE)],
    "mffu_builder50": [("MFFU Builder 50K ($153)", MFFU_BUILDER50, 875),
                       ("MFFU Builder 50K ($107 code) [sens]", dataclasses.replace(MFFU_BUILDER50, one_time_price=107.0, reset=107.0), 875)],
    "goat_flex50": [("Goat Flex 50K", GOAT_FLEX50, 900)],
    "blueberry_ascent50": [("Blueberry Ascent 50K", BLUEBERRY_ASCENT50, 900)],
    "fe_elite50": [("FuturesElite Elite 50K", FE_ELITE50, 900)],
    "alpha_std50": [("Alpha Futures Standard 50K", ALPHA_STD50, 875)],
    "bg_elite50": [("Blue Guardian Elite 50K, price $141 [sens]", BG_ELITE50, 875),
                   ("Blue Guardian Elite 50K, price $350 [sens]", dataclasses.replace(BG_ELITE50, one_time_price=350.0), 875)],
}

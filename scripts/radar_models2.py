"""Prop-firm models for PREREG_RADAR addendum 14 (#237-#258). Rules from the firms' own help centres (radar crawl 2026-11-21/22).
Each entry: (name, rules, risk[, policy]). [sens] = price not readable on the firm's own page (bracket, never ranked or flagged).
"""
from __future__ import annotations

import dataclasses

from backtest.recycle import XFARules
from scripts.radar_models import ALPHA_STD50, TTP_PRIME50

B = XFARules()
R = dataclasses.replace
INF = float("inf")
ZERO = dict(monthly=0.0, activation=0.0, api_monthly=0.0)


def instant(mll, lock_at, lock_lvl, micros, goal1, goal2, cons, cap, pmin, split, price, buffer=0.0, ladder=None, wdays=0, wmin=0.0):
    return R(B, instant_funded=True, profit_target=0.0, loss_limit=mll, funded_loss_limit=mll, mll_locks_at=lock_at, lock_level=lock_lvl,
             combine_max_contracts=micros, funded_scaling=False, ladder=ladder, winning_days_required=wdays, winning_day_min=wmin,
             consistency_target=cons, consistency_days=1, payout_needs_both=bool(wdays) and cons is not None, payout_goal=(goal1, goal2),
             payout_buffer=buffer, payout_cap=cap, payout_min=pmin, profit_split=split, one_time_price=price, reset=price, **ZERO)


TTP_PRIME50_R79 = R(TTP_PRIME50, reset=79.0)
TTP_PRIME100 = R(TTP_PRIME50, profit_target=6000, loss_limit=3000, combine_max_contracts=100, funded_loss_limit=3000, mll_locks_at=3000,
                 payout_cap=3500.0, one_time_price=189.0, reset=189.0)
TTP_INSTANT50 = instant(2000, 2000, 0.0, 40, 3000, 3000, 0.20, 2500, 500, 0.90, 499.0, wdays=5, wmin=0.0)
LUCID_DAILY50 = R(B, profit_target=3000, loss_limit=2000, combine_max_contracts=40, combine_consistency=0.50, funded_loss_limit=2000,
                  mll_locks_at=2100, lock_level=100.0, funded_scaling=False, winning_days_required=0, payout_buffer=2100.0, payout_cap=2000.0,
                  payout_min=0.0, profit_since_payout_required=True, profit_split=0.90, one_time_price=99.0, reset=99.0, **ZERO)
LUCID_DIRECT50 = instant(2000, 2100, 100.0, 40, 3000, 2500, 0.20, 2000, 500, 0.90, 299.0)
MFFU_PRO50 = R(B, profit_target=3000, loss_limit=2000, combine_max_contracts=30, combine_consistency=0.50, funded_loss_limit=2000,
               mll_locks_at=2100, lock_level=100.0, funded_scaling=False, winning_days_required=0, payout_buffer=2100.0, payout_cap=INF,
               payout_min=1000.0, payout_locks_mll=True, profit_split=0.80, one_time_price=127.0, reset=127.0, **ZERO)
MFFU_PRO50_1D = R(MFFU_PRO50, profit_target=4000, combine_consistency=None)
DT_S2F50 = instant(2500, 2500, 0.0, 100, 500, 500, 0.20, 2000, 500, 1.0, 199.0, buffer=2500.0, wdays=10, wmin=200.0)
GOAT_1DAY50 = R(B, profit_target=3000, loss_limit=2000, combine_max_contracts=40, combine_mll_locks=True, funded_loss_limit=2000,
                mll_locks_at=2000, lock_level=0.0, funded_scaling=False, winning_day_min=100.0, winning_days_required=5, consistency_target=0.35,
                consistency_days=5, payout_needs_both=True, payout_share=0.50, payout_cap=1750.0, payout_min=500.0, profit_split=0.80,
                one_time_price=218.0, reset=218.0, **ZERO)
GOAT_EOD50 = R(GOAT_1DAY50, combine_max_contracts=50, combine_consistency=0.50, winning_days_required=7, consistency_target=0.30,
               consistency_days=7, payout_cap=2000.0, one_time_price=150.0, reset=150.0)
ALPHA_ZERO50 = R(ALPHA_STD50, combine_max_contracts=30, combine_consistency=None, funded_scaling=False,
                 ladder=((1500.0, 10), (2000.0, 20), (INF, 30)), payout_cap=1500.0, payout_min=200.0, monthly=169.0, reset=149.0)
ALPHA_ADV50 = R(ALPHA_STD50, profit_target=4000, loss_limit=1750, funded_loss_limit=1750, mll_locks_at=1750, combine_max_contracts=50,
                combine_consistency=0.40, funded_scaling=False, consistency_target=None, payout_needs_both=False, payout_cap=15000.0,
                payout_min=1000.0, monthly=209.0, reset=189.0)
ALPHA_DIRECT50 = instant(2000, 2000, 0.0, 40, 3000, 2000, 0.20, 2000, 500, 0.90, 519.0)
FE_PRIME50 = R(B, profit_target=3000, loss_limit=2000, combine_max_contracts=40, combine_mll_locks=True, funded_loss_limit=2000,
               mll_locks_at=2100, lock_level=100.0, funded_scaling=False, winning_days_required=0, consistency_target=0.40, consistency_days=1,
               payout_goal=(500.0, 500.0), payout_buffer=2100.0, payout_cap=2500.0, payout_min=500.0, profit_split=0.90,
               one_time_price=129.0, reset=109.0, **ZERO)
FE_NITRO50 = R(FE_PRIME50, combine_max_contracts=50, combine_consistency=0.50, consistency_target=None, payout_goal=None,
               payout_cap=2000.0, one_time_price=152.0, reset=99.0)
FE_INSTANT50 = instant(2500, None, 0.0, 40, 0.0, 0.0, None, 2500, 500, 1.0, 199.0, buffer=1500.0,
                       ladder=((1500.0, 20), (2500.0, 30), (INF, 40)), wdays=6, wmin=250.0)
BG_RESERVE50 = R(B, profit_target=3000, loss_limit=2000, combine_max_contracts=40, combine_mll_locks=False, combine_consistency=0.50,
                 funded_loss_limit=2000, mll_locks_at=2100, lock_level=100.0, funded_scaling=False, winning_day_min=150.0,
                 winning_days_required=5, payout_share=0.50, payout_cap=2000.0, payout_goal=(0.0, 750.0), payout_min=500.0,
                 max_payouts_per_xfa=5, profit_split=0.90, one_time_price=150.0, reset=135.0, **ZERO)
BG_DIRECT50 = instant(2000, 2100, 100.0, 40, 3000, 2000, 0.30, 2000, 500, 0.90, 299.0)
ALPHA_STD100 = R(ALPHA_STD50, profit_target=6000, loss_limit=3000, funded_loss_limit=3000, mll_locks_at=3000, combine_max_contracts=100,
                 scaling_mult=2, payout_cap=4000.0, monthly=239.0, reset=199.0)
ALPHA_ZERO100 = R(ALPHA_ZERO50, profit_target=6000, loss_limit=3000, funded_loss_limit=3000, mll_locks_at=3000, combine_max_contracts=60,
                  ladder=((1500.0, 20), (2000.0, 30), (3000.0, 40), (4500.0, 50), (INF, 60)), payout_cap=2500.0, monthly=279.0, reset=249.0)
ALPHA_DIRECT25 = instant(1000, 1000, 0.0, 20, 1500, 1000, 0.20, 1000, 500, 0.90, 349.0)
GOAT_1DAY100 = R(GOAT_1DAY50, profit_target=6000, loss_limit=3000, combine_max_contracts=60, funded_loss_limit=3000, mll_locks_at=3000,
                 payout_cap=2500.0, one_time_price=358.0, reset=358.0)

S = "[sens]"
MODELS2 = {  # key: (automation, [(name, rules, risk), ...])
    "ttp_prime50_r79": ("full_bots", [("TTP Prime 50K, reset $79", TTP_PRIME50_R79, 875)]),
    "ttp_prime100": ("full_bots", [("TTP Prime 100K ($189)", TTP_PRIME100, 1350)]),
    "ttp_instant50": ("full_bots", [(f"TTP Instant 50K $299 {S}", R(TTP_INSTANT50, one_time_price=299.0, reset=299.0), 900),
                                    (f"TTP Instant 50K $499 {S}", TTP_INSTANT50, 900)]),
    "lucid_daily50": ("full_bots", [(f"LucidDaily 50K $99 {S}", LUCID_DAILY50, 900),
                                    (f"LucidDaily 50K $199 {S}", R(LUCID_DAILY50, one_time_price=199.0, reset=199.0), 900)]),
    "lucid_direct50": ("full_bots", [(f"LucidDirect 50K $299 {S}", LUCID_DIRECT50, 900),
                                     (f"LucidDirect 50K $499 {S}", R(LUCID_DIRECT50, one_time_price=499.0, reset=499.0), 900)]),
    "mffu_pro50": ("full_bots", [(f"MFFU Pro 50K $127 {S}", MFFU_PRO50, 900),
                                 (f"MFFU Pro 50K $227 {S}", R(MFFU_PRO50, one_time_price=227.0, reset=227.0), 900)]),
    "mffu_pro50_1d": ("full_bots", [(f"MFFU Pro 50K One-Day $127 {S}", MFFU_PRO50_1D, 900),
                                    (f"MFFU Pro 50K One-Day $227 {S}", R(MFFU_PRO50_1D, one_time_price=227.0, reset=227.0), 900)]),
    "dt_s2f50": ("full_bots", [(f"DayTraders S2F 50K $199 {S}", DT_S2F50, 1094),
                               (f"DayTraders S2F 50K $399 {S}", R(DT_S2F50, one_time_price=399.0, reset=399.0), 1094)]),
    "goat_1day50": ("full_bots", [("Goat 1-Day Pass 50K ($218)", GOAT_1DAY50, 900)]),
    "goat_eod50": ("full_bots", [(f"Goat EOD 50K $150 {S}", GOAT_EOD50, 900),
                                 (f"Goat EOD 50K $250 {S}", R(GOAT_EOD50, one_time_price=250.0, reset=250.0), 900)]),
    "alpha_zero50": ("alert_assisted", [("Alpha Zero 50K ($169/mo)", ALPHA_ZERO50, 875)]),
    "alpha_adv50": ("alert_assisted", [("Alpha Advanced 50K ($209/mo)", ALPHA_ADV50, 787)]),
    "alpha_direct50": ("alert_assisted", [("Alpha Direct 50K ($519)", ALPHA_DIRECT50, 875)]),
    "fe_prime50": ("alert_assisted", [(f"FuturesElite Prime 50K $129 {S}", FE_PRIME50, 900),
                                      (f"FuturesElite Prime 50K $229 {S}", R(FE_PRIME50, one_time_price=229.0), 900)]),
    "fe_nitro50": ("alert_assisted", [("FuturesElite Nitro 50K ($152)", FE_NITRO50, 900)]),
    "fe_instant50": ("alert_assisted", [(f"FuturesElite Instant 50K $199 {S}", FE_INSTANT50, 1125),
                                        (f"FuturesElite Instant 50K $349 {S}", R(FE_INSTANT50, one_time_price=349.0, reset=349.0), 1125)]),
    "bg_reserve50": ("alert_assisted", [(f"Blue Guardian Reserve 50K $150 {S}", BG_RESERVE50, 900),
                                        (f"Blue Guardian Reserve 50K $250 {S}", R(BG_RESERVE50, one_time_price=250.0, reset=225.0), 900)]),
    "bg_direct50": ("alert_assisted", [(f"Blue Guardian Direct 50K $299 {S}", BG_DIRECT50, 900),
                                       (f"Blue Guardian Direct 50K $499 {S}", R(BG_DIRECT50, one_time_price=499.0, reset=499.0), 900)]),
    "alpha_std100": ("alert_assisted", [("Alpha Standard 100K ($239/mo)", ALPHA_STD100, 1350)]),
    "alpha_zero100": ("alert_assisted", [("Alpha Zero 100K ($279/mo)", ALPHA_ZERO100, 1350)]),
    "alpha_direct25": ("alert_assisted", [("Alpha Direct 25K ($349)", ALPHA_DIRECT25, 437)]),
    "goat_1day100": ("full_bots", [("Goat 1-Day Pass 100K ($358)", GOAT_1DAY100, 1350)]),
}

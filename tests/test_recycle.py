"""Tests for the buy / pass / earn / lose cycle.

Built from hand-made sequences rather than real trades: a test that runs the
backtest is testing the data, and the point here is the accounting.
"""
from __future__ import annotations

import dataclasses
import pathlib
import sys

import pandas as pd
import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))

from backtest.recycle import Policy, XFARules, costs, recycle

RULES = XFARules()


def seq(pnls, contracts=1):
    """One trade a day, in order, at a size that never hits a ceiling."""
    days = pd.date_range("2026-01-01", periods=len(pnls), freq="1D", tz="UTC")
    return pd.DataFrame({
        "net_pnl": [float(p) for p in pnls],
        "contracts": [contracts] * len(pnls),
        "entry_ts": days, "exit_ts": days,
        "trading_date": days.date,
    })


def test_a_clean_pass_buys_one_account_and_pays_activation_once():
    out = recycle(seq([1000.0] * 3))
    assert out["accounts_bought"] == 1
    assert out["funded_earned"] == 1
    assert out["cost_lines"]["activation"] == RULES.activation


def test_the_evaluation_breaches_at_exactly_the_limit():
    assert recycle(seq([-2000.0]))["combine_busts"] == 1
    assert recycle(seq([-1999.0]))["combine_busts"] == 0


def test_every_bust_buys_another_account():
    # Three failed evaluations, then one that passes.
    out = recycle(seq([-2000.0, -2000.0, -2000.0] + [1000.0] * 3))
    assert out["combine_busts"] == 3
    assert out["accounts_bought"] == 4
    assert out["funded_earned"] == 1


def test_the_bust_streak_counts_consecutive_dead_accounts():
    out = recycle(seq([-2000.0, -2000.0, -2000.0] + [1000.0] * 3))
    assert out["longest_bust_streak"] == 3


def test_the_funded_limit_locks_once_the_balance_reaches_it():
    """The rule the whole model turns on: past +$2,000 an XFA cannot be killed,
    only emptied. Peak $2,500 would leave a trailing floor of $500; locked, the
    floor is $0 and a fall to $300 survives."""
    out = recycle(seq([1000.0] * 3 + [2500.0, -2200.0]))
    assert out["funded_earned"] == 1
    assert out["funded_busts"] == 0
    assert out["unrealised"] == pytest.approx(300.0)


def test_an_unlocked_funded_account_still_dies():
    """Same shape below the lock: peak $1,800, so the floor is -$200."""
    out = recycle(seq([1000.0] * 3 + [1800.0, -2100.0]))
    assert out["funded_earned"] == 1
    assert out["funded_busts"] == 1
    assert out["accounts_bought"] == 2


def test_a_limit_that_never_locks_is_a_rule_the_model_can_run():
    """mll_locks_at=None used to raise TypeError on the payout check. With no
    lock the same fall that survives above now kills: peak $2,500 leaves a
    trailing floor of $500, and $300 is under it. LOCK_FIRST never pays,
    because the lock it waits for does not exist."""
    rules = XFARules(mll_locks_at=None)
    out = recycle(seq([1000.0] * 3 + [2500.0, -2200.0]), rules)
    assert out["funded_busts"] == 1
    pays = seq([1000.0] * 3 + [200.0] * 5)
    assert recycle(pays, rules, policy=Policy.LOCK_FIRST)["payouts"] == 0
    assert recycle(pays, rules, policy=Policy.IMMEDIATE)["payouts"] == 1


def test_a_payout_needs_five_winning_days():
    # Funded, then four winning days: eligible on the fifth, not before.
    four = recycle(seq([1000.0] * 3 + [600.0] * 4, ))
    assert four["payouts"] == 0
    five = recycle(seq([1000.0] * 3 + [600.0] * 5))
    assert five["payouts"] == 1


def test_a_day_under_the_minimum_is_not_a_winning_day():
    under = recycle(seq([1000.0] * 3 + [3000.0] + [149.0] * 5))
    assert under["payouts"] == 0
    over = recycle(seq([1000.0] * 3 + [3000.0] + [150.0] * 5))
    assert over["payouts"] == 1


def test_a_payout_is_half_the_balance_capped_and_split():
    out = recycle(seq([1000.0] * 3 + [600.0] * 5))
    balance = 600.0 * 5
    expect = balance * RULES.payout_share
    assert out["gross_payout"] == pytest.approx(expect)
    assert out["cash"] == pytest.approx(expect * RULES.profit_split)
    # Half was taken out, so half is left in.
    assert out["unrealised"] == pytest.approx(balance - expect)


def test_the_payout_cap_binds():
    out = recycle(seq([1000.0] * 3 + [4000.0] * 5))
    assert out["gross_payout"] == pytest.approx(RULES.payout_cap)


def test_the_winning_day_count_restarts_after_a_payout():
    once = recycle(seq([1000.0] * 3 + [600.0] * 9))
    twice = recycle(seq([1000.0] * 3 + [600.0] * 10))
    assert once["payouts"] == 1
    assert twice["payouts"] == 2


def test_taking_money_early_is_what_the_policy_chooses():
    """Five small winning days that never reach the lock. LOCK_FIRST waits and
    holds nothing back; IMMEDIATE takes the cash and keeps the account exposed."""
    trades = seq([1000.0] * 3 + [300.0] * 5)
    assert recycle(trades, policy=Policy.LOCK_FIRST)["payouts"] == 0
    assert recycle(trades, policy=Policy.IMMEDIATE)["payouts"] == 1


def test_the_scaling_plan_clamps_a_funded_position():
    """At a $1,400 balance the plan allows 20 micros, so a 25-contract trade
    earns four fifths of what the backtest gave it."""
    trades = seq([1000.0] * 3 + [1400.0, 500.0], contracts=25)
    # The first four are sized 25 too, but only the funded ones are clamped.
    out = recycle(trades)
    assert out["unrealised"] == pytest.approx(1400.0 * 20 / 25 + 500.0 * 20 / 25)


def test_the_funded_phase_can_be_sized_differently():
    """The two-stage plan: $900 evaluations, $250 once funded."""
    trades = seq([1000.0] * 3 + [800.0])
    out = recycle(trades, funded_scale=0.25)
    assert out["unrealised"] == pytest.approx(200.0)


def test_money_left_in_the_account_is_not_cash():
    out = recycle(seq([1000.0] * 3 + [2900.0]))
    assert out["unrealised"] == pytest.approx(2900.0)
    assert out["cash"] == 0.0
    assert out["net"] < 0


def test_two_trades_on_one_day_is_refused():
    """The end-of-day loss limit is only walkable trade by trade while a day
    holds one trade. Silently averaging two would misstate every breach."""
    trades = seq([100.0, 100.0])
    trades["trading_date"] = trades["trading_date"].iloc[0]
    with pytest.raises(ValueError, match="one day"):
        recycle(trades)


def test_costs_match_the_quarterly_report_for_a_single_pass():
    """recycle.costs is path_cost generalised to several activations. They have
    to agree wherever both apply, or the two reports disagree about spend."""
    from quarterly_report import PATHS, path_cost

    mine = costs(RULES, days=104, resets=10, activations=1)
    theirs = path_cost(PATHS["Standard"], accounts=11, days=104, passed=True)
    assert mine["total"] == pytest.approx(theirs["total"])
    assert mine["reset_count"] == theirs["reset_count"]


def test_costs_are_hand_checkable():
    c = costs(RULES, days=90, resets=5, activations=2)
    assert c["months"] == 3                      # ceil(90 / 30.4)
    assert c["free_credits"] == 2                # one per rebill after the first
    assert c["reset_count"] == 3                 # 5 resets less 2 credits
    assert c["total"] == pytest.approx(3 * 49.0 + 3 * 49.0 + 3 * 14.5 + 2 * 149.0)


def test_the_timeline_says_which_trade_caused_each_event():
    """Accounts do not outlive the loop, so how long one lived is recoverable
    only from the trade index on the event that ended it."""
    out = recycle(seq([1000.0] * 3 + [600.0] * 5))
    events = [(e["event"], e["trade"]) for e in out["timeline"]]
    assert events == [("passed", 2), ("payout", 7)]


def test_which_pricing_path_wins_turns_on_a_ratio_not_a_count():
    """The threshold is (months + paid resets) per funded account EARNED.

    Written as a bare count it is only right when exactly one account is
    earned, and a plan built on recycling earns many -- which is how
    docs/GO_LIVE.md came to recommend the more expensive path for the case it
    was actually describing.
    """
    noaf = XFARules(monthly=85.0, reset=85.0, activation=0.0)
    # 36 x (M + P) < 149 x A is the break-even, so the ratio is 149/36 = 4.14.
    days, resets = 365.0, 5

    def cheaper(activations):
        a = costs(RULES, days, resets, activations)["total"]
        b = costs(noaf, days, resets, activations)["total"]
        return "standard" if a < b else "no-activation"

    months = costs(RULES, days, resets, 1)["months"]
    paid = costs(RULES, days, resets, 1)["reset_count"]
    units = months + paid
    # One funded account: the ratio is the whole count, far above 4.14.
    assert units / 1 > 4.14 and cheaper(1) == "standard"
    # Enough funded accounts to bring the ratio under it, and it flips.
    enough = int(units / 4.14) + 1
    assert units / enough < 4.14 and cheaper(enough) == "no-activation"


def test_activation_is_the_only_line_that_scales_with_funded_accounts():
    base = costs(RULES, 365.0, 5, 1)
    more = costs(RULES, 365.0, 5, 4)
    assert more["activation"] == 4 * RULES.activation
    for line in ("subscription", "paid_resets", "api_access"):
        assert more[line] == base[line]


# --- the guard ---------------------------------------------------------------
# bridge/guards.py blocks a trade when the room left is under safety_mult times
# the risk about to be taken. docs/GO_LIVE.md runs it off on an evaluation and
# on once funded, so the model has to be able to express both.

def test_the_guard_is_off_unless_asked_for():
    """Every figure this project has published assumes no guard."""
    plain = recycle(seq([-1900.0, 1000.0, 1000.0, 1000.0, 1000.0]))
    assert plain["retired_combine"] == 0 and plain["retired_funded"] == 0


def test_a_guard_needs_to_know_the_risk_it_is_protecting_against():
    with pytest.raises(ValueError, match="risk_usd"):
        recycle(seq([100.0] * 5), rules=XFARules(combine_guard=True))


def test_the_guard_stops_short_of_the_breach():
    """Room left is 2000 - 1900 = 100, and the next $900 trade needs 1350 of
    it, so the account is retired instead of taking the trade that would have
    ended it."""
    rules = XFARules(combine_guard=True)
    out = recycle(seq([-1900.0, -1000.0]), rules=rules, risk_usd=900.0)
    assert out["retired_combine"] == 1
    assert out["combine_busts"] == 0          # it never breached
    assert [e["event"] for e in out["timeline"]] == ["retired"]


def test_the_same_sequence_breaches_with_the_guard_off():
    out = recycle(seq([-1900.0, -1000.0]))
    assert out["combine_busts"] == 1 and out["retired_combine"] == 0


def test_a_retired_account_still_costs_a_reset():
    """Stopping is not free: it neither passes nor busts, and the replacement
    is bought either way."""
    rules = XFARules(combine_guard=True)
    out = recycle(seq([-1900.0, -1000.0]), rules=rules, risk_usd=900.0)
    assert out["accounts_bought"] == 2


def test_the_guard_can_be_on_for_one_phase_only():
    """The two-stage plan: off while the evaluation is cheap to replace, on
    once it is not."""
    rules = XFARules(funded_guard=True)
    # Passes on trade 3, then the funded account drifts down toward its floor.
    out = recycle(seq([1000.0] * 3 + [500.0, -1400.0, -100.0]),
                  rules=rules, risk_usd=900.0)
    assert out["retired_combine"] == 0        # the evaluation ran unguarded
    assert out["retired_funded"] == 1


def test_a_payout_moves_the_funded_floor_to_zero():
    """Topstep, read 2026-11-06: after a payout the MLL resets to $0 for good.
    Pass, then five $300 days (balance $1,500, peak $1,500, trailing floor
    -$500) -> IMMEDIATE pays $750 and the balance is $750. A -$800 day leaves
    -$50: alive under the old model (floor -$500), dead under the rule."""
    path = seq([1000.0] * 3 + [300.0] * 5 + [-800.0])
    new = recycle(path, policy=Policy.IMMEDIATE)
    old = recycle(path, XFARules(payout_locks_mll=False,
                                 profit_since_payout_required=False),
                  policy=Policy.IMMEDIATE)
    assert new["payouts"] == old["payouts"] == 1
    assert new["funded_busts"] == 1
    assert old["funded_busts"] == 0


def test_a_second_payout_needs_profit_since_the_first():
    """Five winning days that net to a loss since the last payout pay nothing."""
    rules = XFARules(payout_locks_mll=False)
    path = seq([1000.0] * 3 + [600.0] * 5 + [200.0, 200.0, 200.0, 200.0, -1100.0, 200.0])
    out = recycle(path, rules, policy=Policy.IMMEDIATE)
    assert out["payouts"] == 1
    off = recycle(path, XFARules(payout_locks_mll=False,
                                 profit_since_payout_required=False),
                  policy=Policy.IMMEDIATE)
    assert off["payouts"] == 2


def test_the_evaluation_floor_locks_at_the_starting_balance():
    """Topstep MLL article: in the Combine too, the trailing limit locks once
    it reaches the starting balance. Up $2,500 (floor would trail to +$500),
    then a fall to +$100: dead under a floor that trails forever, alive once
    the floor locks at $0."""
    path = seq([2500.0, -2400.0])
    assert recycle(path)["combine_busts"] == 0
    assert recycle(path, XFARules(combine_mll_locks=False))["combine_busts"] == 1


# --- options added 2026-11-20 for other firms (FTMO Futures) ---

def test_a_hard_daily_loss_limit_ends_the_evaluation_on_one_bad_day():
    rules = dataclasses.replace(RULES, loss_limit=3000.0, daily_loss_limit=1000.0)
    assert recycle(seq([-1000.0]), rules)["combine_busts"] == 1
    assert recycle(seq([-999.0]), rules)["combine_busts"] == 0
    assert recycle(seq([-1000.0]))["combine_busts"] == 0   # default: no daily limit


def test_evaluation_consistency_delays_but_does_not_fail_a_pass():
    rules = dataclasses.replace(RULES, combine_consistency=0.40)
    # one $3,000 day is 100% of the profit: not passed yet, not busted
    out = recycle(seq([3000.0]), rules)
    assert out["funded_earned"] == 0 and out["combine_busts"] == 0
    # best day $3,000 needs $7,500 total before it is 40% of the profit
    assert recycle(seq([3000.0] + [500.0] * 8), rules)["funded_earned"] == 0
    assert recycle(seq([3000.0] + [500.0] * 9), rules)["funded_earned"] == 1


def test_no_free_reset_per_rebill_charges_every_reset():
    rules = dataclasses.replace(RULES, free_reset_per_rebill=False)
    with_free = costs(RULES, 90, resets=3, activations=0)
    without = costs(rules, 90, resets=3, activations=0)
    assert with_free["free_credits"] > 0 and without["free_credits"] == 0
    assert without["paid_resets"] == 3 * rules.reset


def test_an_evaluation_past_its_time_limit_expires_and_is_bought_again():
    rules = dataclasses.replace(RULES, combine_max_days=30)
    days = pd.to_datetime(["2026-01-01", "2026-01-20", "2026-02-15"], utc=True)
    t = pd.DataFrame({"net_pnl": [1000.0, 1000.0, 1000.0], "contracts": [1] * 3,
                      "entry_ts": days, "exit_ts": days, "trading_date": days.date})
    out = recycle(t, rules)
    assert out["combine_busts"] == 1 and out["funded_earned"] == 0
    assert recycle(t)["funded_earned"] == 1          # no limit: $3,000 passes


def test_a_payout_buffer_pays_only_what_sits_above_it():
    rules = dataclasses.replace(RULES, payout_buffer=3000.0, payout_cap=1500.0, winning_days_required=1)
    out = recycle(seq([3000.0] + [3500.0]), rules, policy=Policy.IMMEDIATE)
    assert out["gross_payout"] == 500.0               # 3,500 balance - 3,000 buffer


def test_a_firm_ladder_caps_contracts_in_both_phases():
    rules = dataclasses.replace(RULES, ladder=((1500.0, 2), (float("inf"), 4)))
    # 10 contracts asked, 2 allowed: P&L scales to 20%
    out = recycle(seq([-10000.0], contracts=10), rules)
    assert out["combine_busts"] == 1                  # -2,000 after scaling still breaches
    out2 = recycle(seq([-9000.0], contracts=10), rules)
    assert out2["combine_busts"] == 0                 # -1,800 after scaling does not


def test_instant_funded_accounts_skip_the_evaluation_and_rebuy_on_a_bust():
    rules = dataclasses.replace(RULES, instant_funded=True, one_time_price=500.0, reset=500.0,
                                monthly=0.0, activation=0.0, api_monthly=0.0)
    out = recycle(seq([-2000.0, -2000.0]), rules)
    assert out["combine_busts"] == 0 and out["funded_busts"] == 2
    assert out["cost"] == 3 * 500.0                  # first account + two replacements


def test_a_payout_goal_needs_fresh_profit():
    rules = dataclasses.replace(RULES, winning_days_required=1, payout_goal=(3000.0, 2000.0))
    # funded profit of 2,500 is under the 3,000 goal: no payout
    assert recycle(seq([3000.0, 2500.0]), rules, policy=Policy.IMMEDIATE)["payouts"] == 0
    assert recycle(seq([3000.0, 3000.0]), rules, policy=Policy.IMMEDIATE)["payouts"] == 1


def test_static_drawdown_never_trails_and_locks_once_funded_buffer_is_built():
    rules = dataclasses.replace(RULES, static_dd=True, mll_locks_at=2000.0, lock_level=0.0)
    # evaluation: +1,500 then -3,000 is -1,500, above the static -2,000 floor
    assert recycle(seq([1500.0, -3000.0]))["combine_busts"] == 1      # trailing busts
    assert recycle(seq([1500.0, -3000.0]), rules)["combine_busts"] == 0
    # funded before the buffer: same static -2,000 floor
    assert recycle(seq([3000.0, 1500.0, -3000.0]), rules)["funded_busts"] == 0
    # funded after the buffer (+2,000): floor jumps to 0, so -2,100 busts
    assert recycle(seq([3000.0, 2000.0, -2100.0]), rules)["funded_busts"] == 1


def test_two_phase_evaluation_needs_both_targets():
    r = dataclasses.replace(RULES, phase2_target=1500.0, combine_consistency=None)
    one = recycle(seq([1000.0] * 3), r)  # 3,000 passes phase 1, then 0 left over: phase 2 not reached
    assert one["funded_earned"] == 0
    two = recycle(seq([1000.0] * 5), r)  # 3,000 then 2,000 >= 1,500
    assert two["funded_earned"] == 1


def test_fee_refund_paid_once_with_first_payout():
    base = dataclasses.replace(RULES, one_time_price=300.0, reset=300.0, monthly=0.0)
    trades = seq([1000.0] * 30)
    a = recycle(trades, base, policy=Policy.IMMEDIATE)
    b = recycle(trades, dataclasses.replace(base, refund_fee_on_first_payout=True), policy=Policy.IMMEDIATE)
    assert a["payouts"] >= 1
    assert b["net"] == pytest.approx(a["net"] + 300.0)


def test_an_open_loss_through_the_floor_closes_the_account_even_if_the_trade_wins():
    # Balance +1,500 sits $2,000 above the floor (-500 after a +1,500 peak). The next trade
    # dips $2,100 while open, then closes +900: Topstep liquidates on open P&L.
    t = seq([1500.0, 900.0]).assign(mae_usd=[0.0, 2100.0], mfe_usd=[1500.0, 900.0])
    out = recycle(t)
    assert out["combine_busts"] == 1 and out["funded_earned"] == 0
    # Judged on closed P&L only (the pre-2026-11-26 model) the account survives.
    closed = recycle(t, dataclasses.replace(RULES, realtime_mll=False))
    assert closed["combine_busts"] == 0


def test_an_open_loss_that_stays_above_the_floor_changes_nothing():
    t = seq([1000.0] * 3).assign(mae_usd=[500.0] * 3, mfe_usd=[1000.0] * 3)
    assert recycle(t)["net"] == recycle(seq([1000.0] * 3))["net"]


def test_without_the_excursion_columns_the_model_falls_back_to_closed_pnl():
    t = seq([1500.0, 900.0])
    assert recycle(t)["combine_busts"] == 0


def test_intraday_trail_raises_the_funded_floor_on_open_profit():
    # Pass, then funded: +1,000 closed after +1,900 open (peak 1,900 -> floor -100);
    # next trade closes -1,150 -> balance -150, above an EOD floor (-1,000)
    # but below the intraday-trailed floor (-100).
    rules = dataclasses.replace(RULES, intraday_trail_funded=True, funded_scaling=False)
    t = seq([3000.0, 1000.0, -1150.0]).assign(mae_usd=[0.0, 0.0, 1150.0], mfe_usd=[3000.0, 1900.0, 0.0])
    assert recycle(t, rules)["funded_busts"] == 1
    assert recycle(t, dataclasses.replace(rules, intraday_trail_funded=False))["funded_busts"] == 0


def test_an_eod_evaluation_ignores_open_losses_when_the_firm_says_so():
    t = seq([1500.0, 900.0]).assign(mae_usd=[0.0, 2100.0], mfe_usd=[1500.0, 900.0])
    assert recycle(t, dataclasses.replace(RULES, realtime_eval=False))["combine_busts"] == 0

"""Buying evaluations, passing them, getting paid, and losing the account.

``scripts/quarterly_report.py`` answers "what does it cost to reach a funded
account": it walks the real sequence of trades, buys a fresh evaluation after
every breach, and stops at the first pass. That is where the money starts, not
where it ends, so it cannot say whether any of this is a business.

This module keeps going. An account that passes becomes an Express Funded
Account, trades on, pays out when it is eligible, and eventually dies; then the
cycle starts again. What comes out is cash actually withdrawn, against cash
actually spent.

**Money left in a funded account is not money.** It is the single thing this
model exists to say: a run that ends with $2,800 of unrealised balance and an
account that then breaches has earned nothing. Every figure here is either
withdrawn or spent.

The rule that decides most of it
--------------------------------
An XFA's loss limit trails the *highest end-of-day balance* and never moves
down -- and once the balance reaches the limit's own size, the limit locks at
$0 permanently. A 50K XFA that reaches +$2,000 can never again fall below
breakeven; it can only give back its profits. Evaluations have no such rule:
there the target and the limit race each other and one of them always wins.

So an XFA's whole life turns on whether it reaches +$2,000 before it falls
$2,000 from its peak, and a withdrawal taken before that point pushes the
balance back down while leaving the high-water mark where it was. Taking money
early is not free: it is paid for in the insurance you then never buy. Both
orderings are modelled -- see :class:`Policy`.

Rules are Topstep's 50K figures, read from their help centre on 2026-09-14 and
recorded with their sources in :class:`XFARules`. They change; the dataclass is
there so a change is one edit rather than a hunt.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum

import numpy as np
import pandas as pd

from bridge.guards import scaling_tier


class Policy(Enum):
    """When to take money out of a funded account.

    The choice is not cosmetic. A payout lowers the balance but not the
    high-water mark the loss limit trails, so withdrawing before the limit
    locks keeps the account killable for longer -- possibly forever, if every
    payout resets the climb. LOCK_FIRST buys the insurance before taking
    anything out; IMMEDIATE takes the cash and stays exposed.
    """

    IMMEDIATE = "immediate"
    LOCK_FIRST = "lock_first"


@dataclass(frozen=True)
class XFARules:
    """Topstep 50K, from their help centre on 2026-09-14, plus the two payout
    rules read on 2026-11-06 (``payout_locks_mll``,
    ``profit_since_payout_required``). The 2026-09-14 model is
    ``XFARules(payout_locks_mll=False, profit_since_payout_required=False)``.

    Sources:
      - help.topstep.com/en/articles/8284233-topstep-payout-policy
      - topstep.com/express-funded-account-rules
      - help.topstep.com/en/articles/8284204-what-is-the-maximum-loss-limit
    """

    #: Evaluation: reach this and the account passes.
    profit_target: float = 3000.0
    #: Evaluation: fall this far from the peak and it is over.
    loss_limit: float = 2000.0
    #: Evaluation contract ceiling for a 50K, matching bridge PRESETS.
    combine_max_contracts: int = 50

    #: XFA: same size of trailing limit, but it locks (see below).
    funded_loss_limit: float = 2000.0
    #: Balance at which the trailing limit locks at $0 and stops following.
    #: Topstep states this as "once your balance reaches $2,000, the MLL locks
    #: at $0 permanently" for a 50K.
    mll_locks_at: float = 2000.0

    #: A winning day needs this much net profit to count toward a payout.
    winning_day_min: float = 150.0
    #: Winning days needed per payout. They need not be consecutive, and the
    #: count restarts at zero after each payout.
    winning_days_required: int = 5
    #: A payout may take at most this share of the balance...
    payout_share: float = 0.50
    #: ...and at most this many dollars. Topstep's 50K cap is $2,000; adding
    #: the optional Daily Loss Limit at purchase doubles it, and this plan
    #: keeps the Responsible Trading Advantage on, so $4,000 applies.
    #: 2026-11-06: the payout page says the $4,000 applies only to NEW
    #: Combines with the DLL added at checkout, as a limited-time offer from
    #: "June 2nd". If that offer has ended, this is $2,000. Check at purchase.
    payout_cap: float = 2000.0
    #: 2026-11-07: $2,000 is the standing 50K Standard cap on Topstep's payout
    #: page. The $4,000 above needs the limited-time DLL offer at checkout, and
    #: nothing shows this account would get it. Set to 2000.
    #:
    #: Evaluation MLL lock. Topstep's MLL article (read 2026-11-06): "In the
    #: Trading Combine and Express Funded Account, the Maximum Loss Limit
    #: trails your highest end-of-day balance ... Once it reaches your
    #: starting balance, it locks in permanently." Before 2026-11-07 the model
    #: let the evaluation floor trail forever, which is pessimistic about
    #: passing. False reproduces that.
    combine_mll_locks: bool = True
    #: "After a payout: Your Maximum Loss Limit (MLL) resets to $0
    #: permanently" -- help.topstep.com payout policy, read 2026-11-06. Not in
    #: the 2026-09-14 model: there a payout before the lock left the trailing
    #: floor below $0. True moves the floor to $0 on the first payout.
    payout_locks_mll: bool = True
    #: "Positive net profit since your last Payout" is required for every
    #: payout after the first (same page, read 2026-11-06).
    profit_since_payout_required: bool = True

    #: Trader's share. The "100% of your first $10,000" arrangement is limited
    #: to accounts on the new dashboard before 2026-01-12, which this one will
    #: not be.
    profit_split: float = 0.90

    #: Stop trading rather than breach -- the live guard in bridge/guards.py,
    #: which blocks a trade when the room left is under ``safety_mult`` times
    #: the risk about to be taken. docs/GO_LIVE.md runs it OFF on an evaluation
    #: and ON once funded, because stopping short of a target neither passes
    #: nor busts while the monthly fee runs either way.
    #:
    #: A stopped account is stuck, not saved: it takes no more trades, so its
    #: balance never moves, so the condition that stopped it stays true. The
    #: model retires it and buys another rather than pretending it recovers.
    combine_guard: bool = False
    funded_guard: bool = False
    safety_mult: float = 1.5

    #: Standard path pricing, matching PATHS["Standard"] in the quarterly
    #: report. Every monthly rebill banks one free reset credit.
    #: XFA Consistency path (Topstep, since 2026-02-05): payout needs at least
    #: ``consistency_days`` trading days and the best day since the last payout
    #: at most this share of the profit since then. None = Standard path.
    consistency_target: float | None = None
    consistency_days: int = 3
    #: Multiplies the 50K funded scaling ladder for bigger accounts. Topstep's
    #: 100K/150K ladders were not read; x2 / x3 is an assumption.
    scaling_mult: int = 1
    #: Back2Funded: reactivate a lost XFA (same size, fresh $0 balance and
    #: trailing MLL) up to this many times instead of going back to a Combine.
    #: Topstep allows 2, at $599 for a 50K (read 2026-11-20). 0 = never.
    back2funded_max: int = 0
    back2funded_price: float = 599.0

    #: Other firms. Defaults reproduce Topstep exactly.
    #: Where the loss limit settles once it locks (and after a payout):
    #: Topstep $0, Lucid +$100 above the starting balance.
    lock_level: float = 0.0
    #: Smallest payout the firm accepts (Lucid $500). A smaller one is skipped.
    payout_min: float = 0.0
    #: Payouts allowed per funded account before it ends (Lucid 5, then
    #: "moved live"; modelled as the account finishing). None = no limit.
    max_payouts_per_xfa: int | None = None
    #: False = no funded scaling ladder: the evaluation's contract cap applies.
    funded_scaling: bool = True
    #: One-time pricing (Lucid): the first evaluation and every replacement
    #: after a funded account ends cost this; an evaluation bust costs
    #: ``reset``; ``monthly`` should be 0. None = Topstep's subscription model.
    one_time_price: float | None = None

    #: Hard daily loss limit: a day that loses this much ends the account
    #: (FTMO Futures Pro). With at most one trade a day this is "one trade may
    #: not lose this much". None = no daily limit (Topstep on TopstepX).
    daily_loss_limit: float | None = None
    #: Evaluation consistency (FTMO Futures Growth 40%, Pro 50%): the
    #: evaluation passes only once the best day is at most this share of the
    #: profit. Exceeding it is not a breach; it just delays passing.
    combine_consistency: float | None = None
    #: Topstep banks one free reset per monthly rebill. False = every reset is
    #: paid (firms that do not state a free reset).
    free_reset_per_rebill: bool = True
    #: Evaluation must pass within this many calendar days of its first trade
    #: or it expires and is bought again (Bulenox: 30). None = no time limit.
    combine_max_days: int | None = None
    #: Payout needs the winning-day count AND the consistency test (TradeDay
    #: Fast Pass since 2026-07-26). False = consistency replaces winning days.
    payout_needs_both: bool = False
    #: Payout is whatever sits above this balance, up to the cap (Bulenox
    #: Momentum keeps $3,000 in the account). None = payout_share of balance.
    payout_buffer: float | None = None
    #: Firm-specific contract ladder in micros, ((balance below, cap), ...),
    #: top cap last as (inf, cap); used in BOTH phases when set. None = the
    #: Topstep funded ladder and ``combine_max_contracts``.
    ladder: tuple | None = None
    #: No evaluation: every account bought starts funded (Tradeify Lightning).
    instant_funded: bool = False
    #: Payout needs this much fresh profit since the last payout: (first, later).
    payout_goal: tuple | None = None

    monthly: float = 49.0
    reset: float = 49.0
    #: Charged once per funded account EARNED -- so it is charged again every
    #: time a dead XFA is replaced by a new pass.
    activation: float = 149.0
    api_monthly: float = 14.50


@dataclass
class _Account:
    """One evaluation or funded account, while it is alive."""

    balance: float = 0.0
    peak: float = 0.0
    winning_days: int = 0
    #: Set by a payout when ``XFARules.payout_locks_mll``: the limit is then $0
    #: for good, whatever the peak was.
    paid_out: bool = False
    #: Balance right after the last payout, for the profit-since-payout test.
    after_payout: float | None = None
    #: Consistency path: days traded and best day since the last payout.
    days_traded: int = 0
    best_day: float = 0.0
    #: Back2Funded reactivations already used on this XFA.
    reactivations: int = 0
    #: Payouts taken from this XFA.
    n_payouts: int = 0
    #: Time of the first trade on this account (for combine_max_days).
    opened: object = None

    def floor(self, limit: float, locks_at: float | None, lock_level: float = 0.0) -> float:
        """The balance at which this account is closed.

        For an evaluation the limit simply trails the peak. For a funded
        account the same expression already produces the lock: once the peak
        reaches the limit's size the floor would rise above zero, and the rule
        is that it never does.
        """
        if self.paid_out:
            return lock_level
        trailing = self.peak - limit
        return trailing if locks_at is None else min(trailing, lock_level)


def _months(days: float) -> int:
    """Billing months covered by a run of this many days."""
    return max(1, int(math.ceil(days / 30.4)))


def costs(rules: XFARules, days: float, resets: int, activations: int,
          rebuys: int = 0) -> dict:
    """Itemised spend. ``scripts/quarterly_report.py``'s ``path_cost`` is this
    same rule for a run that passes once; tests/test_recycle.py asserts the two
    agree on that case so the duplication cannot drift.

    Every monthly rebill banks one free reset credit, so the first month earns
    none and each later month covers one reset.
    """
    months = _months(days)
    if rules.one_time_price is not None:
        # One-time pricing: no rebill credits. An evaluation bust is a reset;
        # a funded account that ends is replaced by a new evaluation.
        lines = {
            "evaluations": (1 + rebuys) * rules.one_time_price,
            "paid_resets": max(0, resets - rebuys) * rules.reset,
            "subscription": months * rules.monthly,
            "api_access": months * rules.api_monthly,
            "activation": activations * rules.activation,
        }
        return {"months": months, "free_credits": 0, "reset_count": max(0, resets - rebuys),
                **lines, "total": float(sum(lines.values()))}
    free = max(0, months - 1) if rules.free_reset_per_rebill else 0
    paid = max(0, resets - free)
    lines = {
        "subscription": months * rules.monthly,
        "paid_resets": paid * rules.reset,
        "api_access": months * rules.api_monthly,
        "activation": activations * rules.activation,
    }
    return {"months": months, "free_credits": free, "reset_count": paid,
            **lines, "total": float(sum(lines.values()))}


def recycle(trades: pd.DataFrame, rules: XFARules = XFARules(),
            policy: Policy = Policy.LOCK_FIRST,
            funded_scale: float = 1.0, risk_usd: float | None = None) -> dict:
    """Run one real sequence of trades through buy / pass / earn / lose.

    ``trades`` must already be simulated at the evaluation's risk per trade and
    carry ``net_pnl``, ``contracts``, ``exit_ts`` and ``trading_date``.

    ``funded_scale`` re-sizes the funded phase relative to the evaluation --
    0.28 puts a $900 evaluation onto $250 a trade once funded, which is the
    two-stage plan in docs/GO_LIVE.md. P&L and commission both scale with
    contracts, so scaling net_pnl is the same thing as re-running the sizing.

    ``risk_usd`` is the dollars risked per evaluation trade, and is required
    only when a guard is on: the guard's test is about the room left against
    the size of the next trade, so it cannot be evaluated without knowing it.

    Returns cash withdrawn, money spent, and the counts behind both.
    """
    if trades.empty:
        raise ValueError("no trades to recycle")
    # The loss limit trails the highest END-OF-DAY balance. Walking trade by
    # trade is only the same thing while a day holds at most one trade, which
    # is what this strategy generates. If that ever stops being true the whole
    # model needs rewriting, so it is an assertion rather than a comment.
    per_day = trades.groupby("trading_date").size().max()
    if per_day > 1:
        raise ValueError(
            f"{per_day} trades on one day: the end-of-day loss limit cannot be "
            "walked trade by trade")

    def mark(ts, event, at):
        """Record where the money stands, not just that something happened.

        A total says the run made money; this says when. The two are different
        questions and only the second one is survivable or not.

        ``at`` is the index of the trade that caused the event, which is what
        lets a caller reconstruct how many trades each account lived for --
        recoverable from nothing else, since accounts are not objects that
        outlive the loop.
        """
        spent = (costs(rules, (ts - first).total_seconds() / 86400,
                       resets, activations, rebuys)["total"]
                 + reactivations * rules.back2funded_price)
        timeline.append({"ts": ts, "event": event, "trade": at, "cash": cash,
                         "cost": spent, "net": cash - spent})

    if (rules.combine_guard or rules.funded_guard) and risk_usd is None:
        raise ValueError("a guard needs risk_usd: its test compares the room "
                         "left against the size of the next trade")

    account, funded = _Account(), rules.instant_funded
    combine_busts = funded_busts = resets = activations = payouts = 0
    reactivations = 0
    rebuys = 0  # funded accounts ended and replaced (one-time pricing)
    retired_combine = retired_funded = 0
    bust_streak = worst_streak = 0
    cash = gross = 0.0
    first = trades["entry_ts"].iloc[0]
    last_cash_ts, worst_dry = first, 0.0
    funded_days = 0.0
    funded_since = first if rules.instant_funded else None
    timeline: list[dict] = []

    for at, (pnl, contracts, exit_ts) in enumerate(
            zip(trades["net_pnl"], trades["contracts"], trades["exit_ts"])):
        # The backtest sizes on risk alone; neither ceiling exists there.
        if not funded and rules.combine_max_days is not None:
            if account.opened is None:
                account.opened = exit_ts
            elif (exit_ts - account.opened).total_seconds() > rules.combine_max_days * 86400:
                combine_busts += 1
                resets += 1
                bust_streak += 1
                worst_streak = max(worst_streak, bust_streak)
                account = _Account(opened=exit_ts)
                mark(exit_ts, "combine_expired", at)
        if rules.ladder is not None:
            cap = next(c for lim, c in rules.ladder if account.balance < lim)
        elif funded and rules.funded_scaling:
            cap = scaling_tier(account.balance) * rules.scaling_mult
        else:
            cap = rules.combine_max_contracts
        scale = min(int(contracts), cap) / contracts if contracts else 0.0
        day = float(pnl) * scale * (funded_scale if funded else 1.0)

        # The guard looks at the room left BEFORE the trade, which is the
        # only order in which it could ever prevent one.
        guarded = rules.funded_guard if funded else rules.combine_guard
        if guarded:
            limit = rules.funded_loss_limit if funded else rules.loss_limit
            locks = (rules.mll_locks_at if funded
                     else rules.loss_limit if rules.combine_mll_locks else None)
            planned = risk_usd * (funded_scale if funded else 1.0)
            if account.balance - account.floor(limit, locks, rules.lock_level) < planned * rules.safety_mult:
                if funded:
                    retired_funded += 1
                    rebuys += 1
                    funded_days += (exit_ts - funded_since).total_seconds() / 86400
                    funded, funded_since = False, None
                else:
                    retired_combine += 1
                resets += 1
                bust_streak += 1
                worst_streak = max(worst_streak, bust_streak)
                account = _Account()
                mark(exit_ts, "retired", at)
                continue

        account.balance += day
        account.peak = max(account.peak, account.balance)

        hard_dll = rules.daily_loss_limit is not None and day <= -rules.daily_loss_limit

        if not funded:
            account.best_day = max(account.best_day, day)
            consistent = (rules.combine_consistency is None
                          or account.best_day <= rules.combine_consistency * account.balance)
            if account.balance >= rules.profit_target and consistent and not hard_dll:
                activations += 1
                funded, account, funded_since = True, _Account(), exit_ts
                mark(exit_ts, "passed", at)
                continue
            if hard_dll or account.balance <= account.floor(
                    rules.loss_limit,
                    rules.loss_limit if rules.combine_mll_locks else None,
                    rules.lock_level):
                combine_busts += 1
                resets += 1
                bust_streak += 1
                worst_streak = max(worst_streak, bust_streak)
                account = _Account()
                mark(exit_ts, "combine_bust", at)
            continue

        # --- funded ---
        if day >= rules.winning_day_min:
            account.winning_days += 1
        account.days_traded += 1
        account.best_day = max(account.best_day, day)

        if hard_dll or account.balance <= account.floor(rules.funded_loss_limit,
                                                        rules.mll_locks_at, rules.lock_level):
            funded_busts += 1
            if account.reactivations < rules.back2funded_max:
                # Back2Funded: same XFA, fresh start, no Combine needed.
                reactivations += 1
                account = _Account(reactivations=account.reactivations + 1)
                mark(exit_ts, "back2funded", at)
                continue
            funded_days += (exit_ts - funded_since).total_seconds() / 86400
            # A dead XFA sends you back through an evaluation, which is a
            # reset against the same subscription.
            resets += 1
            rebuys += 1
            bust_streak += 1
            worst_streak = max(worst_streak, bust_streak)
            funded, account, funded_since = rules.instant_funded, _Account(), (exit_ts if rules.instant_funded else None)
            mark(exit_ts, "funded_bust", at)
            continue

        # mll_locks_at=None is the rule with no lock at all: the limit trails
        # forever, so the account is never "locked" and LOCK_FIRST never pays.
        locked = (rules.mll_locks_at is not None
                  and account.peak >= rules.mll_locks_at)
        if rules.consistency_target is None:
            days_ok = account.winning_days >= rules.winning_days_required
        else:
            since = account.balance - (account.after_payout or 0.0)
            days_ok = (account.days_traded >= rules.consistency_days and since > 0
                       and account.best_day <= rules.consistency_target * since)
            if rules.payout_needs_both:
                days_ok = days_ok and account.winning_days >= rules.winning_days_required
        if rules.payout_goal is not None:
            goal = rules.payout_goal[0] if account.n_payouts == 0 else rules.payout_goal[1]
            days_ok = days_ok and account.balance - (account.after_payout or 0.0) >= goal
        eligible = (days_ok
                    and account.balance > 0
                    and not (rules.profit_since_payout_required
                             and account.after_payout is not None
                             and account.balance <= account.after_payout)
                    and (locked or policy is Policy.IMMEDIATE))
        def _amount():
            if rules.payout_buffer is not None:
                return min(account.balance - rules.payout_buffer, rules.payout_cap)
            return min(account.balance * rules.payout_share, rules.payout_cap)
        if eligible and (_amount() < rules.payout_min or _amount() <= 0):
            eligible = False
        if eligible:
            amount = _amount()
            # The balance falls; the high-water mark the limit trails does not.
            # That is what makes an early payout expensive.
            account.balance -= amount
            account.winning_days = 0
            account.days_traded, account.best_day = 0, 0.0
            account.after_payout = account.balance
            if rules.payout_locks_mll:
                account.paid_out = True
            gross += amount
            cash += amount * rules.profit_split
            payouts += 1
            bust_streak = 0
            worst_dry = max(worst_dry,
                            (exit_ts - last_cash_ts).total_seconds() / 86400)
            last_cash_ts = exit_ts
            mark(exit_ts, "payout", at)
            account.n_payouts += 1
            if (rules.max_payouts_per_xfa is not None
                    and account.n_payouts >= rules.max_payouts_per_xfa):
                # The account ends after its last allowed payout (Lucid moves
                # it live; not modelled) and a new evaluation is bought.
                funded_days += (exit_ts - funded_since).total_seconds() / 86400
                resets += 1
                rebuys += 1
                funded, account, funded_since = rules.instant_funded, _Account(), (exit_ts if rules.instant_funded else None)
                mark(exit_ts, "xfa_complete", at)

    end = trades["exit_ts"].iloc[-1]
    if funded and funded_since is not None:
        funded_days += (end - funded_since).total_seconds() / 86400
    worst_dry = max(worst_dry, (end - last_cash_ts).total_seconds() / 86400)

    days = (end - first).total_seconds() / 86400
    spend = costs(rules, days, resets, activations, rebuys)
    if reactivations:
        spend["back2funded"] = reactivations * rules.back2funded_price
        spend["total"] += spend["back2funded"]
    net = cash - spend["total"]
    return {
        "days": days,
        # One evaluation is bought up front; every bust buys another.
        "accounts_bought": (1 + combine_busts + funded_busts
                            + retired_combine + retired_funded),
        "combine_busts": combine_busts,
        # Stopped by the guard rather than breached: no bust, no pass, and the
        # reset still bought.
        "retired_combine": retired_combine,
        "retired_funded": retired_funded,
        "funded_earned": activations,
        "funded_busts": funded_busts,
        "reactivations": reactivations,
        "funded_days": funded_days,
        "payouts": payouts,
        "gross_payout": gross,
        "cash": cash,
        "cost": spend["total"],
        "cost_lines": spend,
        "net": net,
        "roi": net / spend["total"] if spend["total"] else float("nan"),
        "longest_bust_streak": worst_streak,
        "longest_dry_days": worst_dry,
        # What is still sitting in the account at the end, and therefore what
        # the run did NOT earn.
        "unrealised": account.balance if funded else 0.0,
        "timeline": timeline,
    }

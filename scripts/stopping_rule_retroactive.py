"""Would reconcile.py's own stopping rule have survived the history it is
measured on?

    uv run python scripts/stopping_rule_retroactive.py

``PAYOUT_DROUGHT_DAYS`` and ``TRAILING_PF_MIN`` (scripts/reconcile.py) are
measured percentiles of the same 2016-2026 run reported everywhere else in
this project (docs/FIGURES_LEDGER.md #15, #18). A percentile is silent about
whether someone holding the rule would have stopped trading before the
headline number was reached -- the rule and the headline are both read off
the same history, but never against each other. This asks that question
directly: replay the account timeline and the raw trade sequence, find every
date a human actually watching the two thresholds would have stopped, and
report what net would have been frozen at that point if trading never
resumed.

Two different notions of "net" are at stake. The payout-drought rule reads
the account-structure timeline (``backtest.recycle.recycle``'s own events:
cash only moves on "payout", cost accrues every month regardless of trades).
The trailing-PF rule reads the raw strategy trades, independent of the
account wrapper -- but stopping because of it still means no further trades,
so the frozen net is read off the same account timeline, just triggered by a
different signal.
"""

from __future__ import annotations

import pathlib

import numpy as np
import pandas as pd

from backtest.recycle import Policy, XFARules, costs, recycle
from scripts.reconcile import PAYOUT_DROUGHT_DAYS, TRAILING_PF_MIN, TRAILING_PF_TRADES
from scripts.recycling_report import HISTORY_START, between, fills, load_bars
from strategies.ltf_sweep import generate_orders

RULES = XFARules()
#: The value this constant held before 2026-11-06's rule correction (see
#: scripts/reconcile.py's own comment on PAYOUT_DROUGHT_DAYS). Checked
#: alongside the current 239 because that is the number actually quoted back
#: at this project, even though it is already superseded in the live code.
SUPERSEDED_DROUGHT_DAYS = 213


def account_state_asof(timeline: list[dict], first_ts, target_ts):
    """Cumulative cash, reset count and activation count as of ``target_ts``.

    ``recycle()``'s own timeline only records a row per event; this walks it
    once and keeps a running state so a net can be asked for ANY timestamp,
    not just the ones an event happened to land on -- the stopping rule fires
    mid-drought, not at the next account event.
    """
    cash = 0.0
    resets = 0
    activations = 0
    for e in timeline:
        if e["ts"] > target_ts:
            break
        if e["event"] == "payout":
            cash = e["cash"]
        if e["event"] in ("retired", "combine_bust", "funded_bust"):
            resets += 1
        if e["event"] == "passed":
            activations += 1
    return cash, resets, activations


def net_asof(rules: XFARules, timeline: list[dict], first_ts, target_ts) -> float:
    """What a frozen, never-resumed account would show on this date.

    Cash is whatever has actually been withdrawn by ``target_ts``. Cost is
    recomputed fresh at ``target_ts`` (not read off the last event) because
    the monthly subscription keeps accruing between events -- a long drought
    costs money even though nothing else happens.
    """
    cash, resets, activations = account_state_asof(timeline, first_ts, target_ts)
    days = (target_ts - first_ts).total_seconds() / 86400
    cost = costs(rules, days, resets, activations)["total"]
    return cash - cost


def drought_firings(timeline: list[dict], first_ts, last_ts, threshold_days: int):
    """Every payout-to-payout gap (plus start-to-first and last-to-end) that
    exceeds ``threshold_days``, with the exact date the threshold was crossed.
    """
    payout_ts = [e["ts"] for e in timeline if e["event"] == "payout"]
    boundaries = [first_ts] + payout_ts + [last_ts]
    firings = []
    for start, end in zip(boundaries[:-1], boundaries[1:]):
        gap_days = (end - start).total_seconds() / 86400
        if gap_days > threshold_days:
            fired = start + pd.Timedelta(days=threshold_days)
            firings.append({
                "gap_start": start, "gap_end": end, "gap_days": gap_days,
                "fired": fired,
            })
    return firings


def trailing_pf_firings(trades: pd.DataFrame, window: int, pf_min: float):
    """First date of every stretch where the trailing-``window``-trade profit
    factor drops below ``pf_min``, on the raw strategy trades alone."""
    pnl = trades["net_pnl"].to_numpy()
    pos = np.clip(pnl, 0, None)
    neg = -np.clip(pnl, None, 0)
    pos_roll = pd.Series(pos).rolling(window).sum().to_numpy()
    neg_roll = pd.Series(neg).rolling(window).sum().to_numpy()
    with np.errstate(divide="ignore", invalid="ignore"):
        pf = np.where(neg_roll > 0, pos_roll / neg_roll, np.inf)
    fired = pf < pf_min
    fired[:window - 1] = False  # undefined before the first full window
    firings = []
    in_episode = False
    for i, f in enumerate(fired):
        if f and not in_episode:
            firings.append({"index": i, "date": trades["exit_ts"].iloc[i],
                            "pf": float(pf[i])})
            in_episode = True
        elif not f:
            in_episode = False
    return firings


def main() -> int:
    bars = load_bars(HISTORY_START)
    orders = generate_orders(bars)
    history = between(fills(orders, bars, 900.0), HISTORY_START, "2027-01-01")

    whole = recycle(history, rules=RULES, policy=Policy.LOCK_FIRST)
    timeline = whole["timeline"]
    first_ts = history["entry_ts"].iloc[0]
    last_ts = history["exit_ts"].iloc[-1]
    final_net = whole["net"]

    print(f"reference: straight-through 2016-{last_ts.year} net = ${final_net:,.0f} "
          f"({whole['payouts']} payouts, longest dry spell "
          f"{whole['longest_dry_days']:,.0f} days)\n")

    print("=== payout-drought rule ===")
    for label, threshold in (
        (f"current PAYOUT_DROUGHT_DAYS={PAYOUT_DROUGHT_DAYS}", PAYOUT_DROUGHT_DAYS),
        (f"superseded PAYOUT_DROUGHT_DAYS={SUPERSEDED_DROUGHT_DAYS}", SUPERSEDED_DROUGHT_DAYS),
    ):
        print(f"\n{label}")
        firings = drought_firings(timeline, first_ts, last_ts, threshold)
        if not firings:
            print("  never fires over 2016-2026")
            continue
        for f in firings:
            frozen = net_asof(RULES, timeline, first_ts, f["fired"])
            print(f"  gap {f['gap_start'].date()} -> {f['gap_end'].date()} "
                  f"({f['gap_days']:,.0f} days): rule fires {f['fired'].date()}, "
                  f"frozen net ${frozen:,.0f} (final was ${final_net:,.0f}, "
                  f"{'resumed and recovered' if frozen < final_net else 'already past final'})")

    print(f"\n=== trailing-PF rule (TRAILING_PF_TRADES={TRAILING_PF_TRADES}, "
          f"TRAILING_PF_MIN={TRAILING_PF_MIN}) ===")
    pf_firings = trailing_pf_firings(history, TRAILING_PF_TRADES, TRAILING_PF_MIN)
    if not pf_firings:
        print("  never fires over 2016-2026")
    else:
        for f in pf_firings:
            frozen = net_asof(RULES, timeline, first_ts, f["date"])
            print(f"  {f['date'].date()}  trailing PF {f['pf']:.2f}  "
                  f"frozen net ${frozen:,.0f}")
        print(f"  {len(pf_firings)} separate episodes; first one at "
              f"{pf_firings[0]['date'].date()}, frozen net "
              f"${net_asof(RULES, timeline, first_ts, pf_firings[0]['date']):,.0f}")

    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

"""Every stopping rule, from every monthly start date -- and the one that doesn't
always fire.

    uv run python scripts/stopping_rule_all_starts.py
    uv run python scripts/stopping_rule_all_starts.py --orders cached.parquet

scripts/stopping_rule_retroactive.py (FIGURES_LEDGER #20) asks the question
for one start date, 2016-01-01, and two of the three rules. This asks it for
all 118 monthly start dates 2016-01 to 2025-10, with all three of
scripts/reconcile.py's rules:

* STOPPING_RULE        -- this many evaluations burned since the last pass
* PAYOUT_DROUGHT_DAYS  -- days since the last payout, OR since the start if
                          there has not been one yet (the case #20 found)
* TRAILING_PF_MIN      -- over the last TRAILING_PF_TRADES raw trades

A rule that is the 90th percentile of single events, checked continuously for
years, fires almost surely. That is what this measures. It then measures the
alternative: a cumulative cash limit (fees paid minus payouts received),
whose false-alarm rate is over the whole horizon, not per event.

Thresholds are imported from reconcile.py and not changed here.
Account rules: XFARules() defaults. Policy: LOCK_FIRST. $900/trade.
"""

from __future__ import annotations

import argparse

import numpy as np
import pandas as pd

from backtest.recycle import Policy, XFARules, recycle
from scripts.reconcile import (PAYOUT_DROUGHT_DAYS, STOPPING_RULE,
                               TRAILING_PF_MIN, TRAILING_PF_TRADES)
from scripts.recycling_report import HISTORY_START, between, fills, load_bars
from strategies.ltf_sweep import generate_orders

RULES = XFARules()
POLICY = Policy.LOCK_FIRST
STARTS = pd.date_range("2016-01-01", "2025-10-01", freq="MS", tz="UTC")
CASH_LIMITS = (1500, 2000, 2600, 3000, 3600)


def first_stop(chunk: pd.DataFrame, timeline: list[dict], *, drought: int | None,
               burn: int | None, pf_min: float | None):
    """Index of the first trade at which any enabled rule fires, and which."""
    ex = pd.DatetimeIndex(chunk["exit_ts"])
    events: dict[int, list[str]] = {}
    for e in timeline:
        events.setdefault(e["trade"], []).append(e["event"])
    pnl = chunk["net_pnl"].to_numpy()
    last_pay, burned = ex[0], 0
    for i in range(len(chunk)):
        for name in events.get(i, []):
            if name == "payout":
                last_pay = ex[i]
            elif name == "passed":
                burned = 0
            elif name == "combine_bust":
                burned += 1
        if drought is not None and (ex[i] - last_pay).days > drought:
            return i, "drought"
        if burn is not None and burned >= burn:
            return i, f"{burn} evaluations burned"
        if pf_min is not None and i >= TRAILING_PF_TRADES - 1:
            w = pnl[i - TRAILING_PF_TRADES + 1:i + 1]
            loss = -w[w < 0].sum()
            if loss > 0 and w[w > 0].sum() / loss < pf_min:
                return i, "trailing PF"
    return None, "never"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--orders", default=None, help="cached orders parquet")
    args = ap.parse_args(argv)

    bars = load_bars(HISTORY_START)
    orders = pd.read_parquet(args.orders) if args.orders else generate_orders(bars)
    history = between(fills(orders, bars, 900.0), HISTORY_START, "2027-01-01")
    ex = pd.DatetimeIndex(history["exit_ts"])

    runs = []
    for s in STARTS:
        chunk = history[ex >= s].reset_index(drop=True)
        out = recycle(chunk, RULES, policy=POLICY)
        runs.append((s, chunk, out))
    print(f"{len(runs)} start dates, {STARTS[0].date()} .. {STARTS[-1].date()}; "
          f"rules {STOPPING_RULE} evals / {PAYOUT_DROUGHT_DAYS} days / "
          f"PF<{TRAILING_PF_MIN} over {TRAILING_PF_TRADES}")

    def apply(label, **kw):
        rows = []
        for s, chunk, out in runs:
            k, why = first_stop(chunk, out["timeline"], **kw)
            at = out["net"] if k is None else recycle(
                chunk.iloc[:k + 1].reset_index(drop=True), RULES, policy=POLICY)["net"]
            days = None if k is None else (chunk["exit_ts"].iloc[k]
                                           - chunk["exit_ts"].iloc[0]).days
            rows.append({"why": why, "days": days, "at": at, "full": out["net"]})
        df = pd.DataFrame(rows)
        fired = df[df.why != "never"]
        print(f"\n{label}")
        print(f"  fires on {len(fired)}/{len(df)} starts"
              + (f", median {fired.days.median():.0f} days in" if len(fired) else ""))
        if len(fired):
            print("  " + ", ".join(f"{k}: {v}" for k, v in df.why.value_counts().items()))
        print(f"  net when stopped (or at end): median ${df["at"].median():,.0f}, "
              f"mean ${df["at"].mean():,.0f}, positive {np.mean(df["at"] > 0):.0%}")
        return df

    base = apply("never stop", drought=None, burn=None, pf_min=None)
    apply("all three rules", drought=PAYOUT_DROUGHT_DAYS, burn=STOPPING_RULE,
          pf_min=TRAILING_PF_MIN)
    apply(f"STOPPING_RULE={STOPPING_RULE} only", drought=None, burn=STOPPING_RULE,
          pf_min=None)
    apply(f"PAYOUT_DROUGHT_DAYS={PAYOUT_DROUGHT_DAYS} only (counted from start "
          "until the first payout)", drought=PAYOUT_DROUGHT_DAYS, burn=None, pf_min=None)
    apply(f"TRAILING_PF_MIN={TRAILING_PF_MIN} only", drought=None, burn=None,
          pf_min=TRAILING_PF_MIN)

    print("\ncumulative cash limit: stop the first time (fees paid - payouts "
          "received) reaches -limit")
    for limit in CASH_LIMITS:
        fired, at = 0, []
        for (s, chunk, out), full in zip(runs, base.full):
            tl = pd.DataFrame(out["timeline"])
            hit = tl[tl.net <= -limit]
            if len(hit):
                fired += 1
                at.append(float(hit.net.iloc[0]))
            else:
                at.append(full)
        at = np.array(at)
        print(f"  -${limit:>5,}: fires on {fired:>3}/{len(runs)} ({fired / len(runs):.0%}); "
              f"net median ${np.median(at):,.0f}, mean ${np.mean(at):,.0f}, "
              f"positive {np.mean(at > 0):.0%}")
    deepest = [min(0.0, pd.DataFrame(o["timeline"]).net.min()) for _, _, o in runs]
    print(f"\ndeepest cumulative net before recovery: median ${np.median(deepest):,.0f}, "
          f"90th pct ${np.percentile(deepest, 10):,.0f}, worst ${min(deepest):,.0f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

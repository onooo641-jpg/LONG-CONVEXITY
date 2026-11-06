"""Which of the two new payout rules actually flips LOCK_FIRST vs IMMEDIATE?

    uv run python scripts/payout_rule_decomposition.py

``backtest.recycle.XFARules`` carries two rules ported 2026-11-06 from an
independent session's rule re-check, both now confirmed against Topstep's
own pages (docs/TOPSTEP_RULES.md): ``payout_locks_mll`` and
``profit_since_payout_required``. Turning both on at once flipped the policy
winner from IMMEDIATE to LOCK_FIRST (docs/CANDIDATES.md #15) -- but a payout
locking the MLL to $0 should, on its own, *help* IMMEDIATE (it hands IMMEDIATE
the same $0 floor LOCK_FIRST was waiting for, for free, on the first payout),
not hurt it. If turning on ``payout_locks_mll`` alone also favours
LOCK_FIRST, that rule is wired backwards somewhere.

Pre-registered expectation:
  (a) payout_locks_mll only            -> should favour IMMEDIATE
  (b) profit_since_payout_required only -> should favour LOCK_FIRST
  (c) both (current default)            -> net of (a) and (b)

Reports plain 11-year net (h=0, no firm-failure hazard) for LOCK_FIRST and
IMMEDIATE under all four rule configurations: neither new rule, (a) alone,
(b) alone, both.
"""

from __future__ import annotations

import dataclasses

import pandas as pd

from backtest.engine import BacktestConfig, simulate
from backtest.recycle import Policy, XFARules, recycle
from ict import data as D
from strategies.ltf_sweep import generate_orders

RISK = 900.0
HISTORY_START = "2016-01-01"


def load_trades(risk: float) -> pd.DataFrame:
    lead = (pd.Timestamp(HISTORY_START) - pd.Timedelta(days=45)).strftime("%Y-%m-%d")
    bars = pd.read_parquet(D.PROCESSED_DIR / "nq_1m.parquet",
                           filters=[("ts", ">=", pd.Timestamp(lead, tz="UTC"))])
    bars = D.add_time_columns(bars).reset_index(drop=True)
    orders = generate_orders(bars)
    trades = simulate(orders, bars, BacktestConfig(risk_per_trade_usd=risk))
    trades = trades[trades["filled"]].sort_values("exit_ts").reset_index(drop=True)
    inside = trades["entry_ts"] >= pd.Timestamp(HISTORY_START, tz="UTC")
    return trades[inside].reset_index(drop=True)


CONFIGS = {
    "neither (pre-correction rules)": dict(payout_locks_mll=False, profit_since_payout_required=False),
    "(a) payout_locks_mll only": dict(payout_locks_mll=True, profit_since_payout_required=False),
    "(b) profit_since_payout_required only": dict(payout_locks_mll=False, profit_since_payout_required=True),
    "(c) both (current default)": dict(payout_locks_mll=True, profit_since_payout_required=True),
}


def main() -> None:
    trades = load_trades(RISK)

    rows = []
    for label, overrides in CONFIGS.items():
        rules = dataclasses.replace(XFARules(), **overrides)
        for policy in (Policy.LOCK_FIRST, Policy.IMMEDIATE):
            result = recycle(trades, rules=rules, policy=policy)
            rows.append({"config": label, "policy": policy.value, "net": result["net"]})

    table = pd.DataFrame(rows).pivot(index="config", columns="policy", values="net")
    table = table.reindex(CONFIGS.keys())
    table["lock_first_minus_immediate"] = (
        table[Policy.LOCK_FIRST.value] - table[Policy.IMMEDIATE.value])
    table["winner"] = table["lock_first_minus_immediate"].apply(
        lambda d: "LOCK_FIRST" if d > 0 else "IMMEDIATE")

    print(table.round(0).to_string())

    print()
    a_winner = table.loc["(a) payout_locks_mll only", "winner"]
    b_winner = table.loc["(b) profit_since_payout_required only", "winner"]
    print(f"(a) payout_locks_mll alone favours {a_winner} "
          f"(expected IMMEDIATE -- {'MATCHES' if a_winner == 'IMMEDIATE' else 'CONTRADICTS'} prediction)")
    print(f"(b) profit_since_payout_required alone favours {b_winner} "
          f"(expected LOCK_FIRST -- {'MATCHES' if b_winner == 'LOCK_FIRST' else 'CONTRADICTS'} prediction)")
    if a_winner != "IMMEDIATE":
        print("\n(a) contradicts the mechanism prediction -- payout_locks_mll "
              "may be implemented backwards. Check the floor()/paid_out logic "
              "in backtest/recycle.py before trusting the combined result.")


if __name__ == "__main__":
    main()

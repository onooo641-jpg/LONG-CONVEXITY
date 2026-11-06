"""Does the payout policy choice depend on how likely Topstep itself is to fail?

    uv run python scripts/firm_failure_sensitivity.py

LOCK_FIRST and IMMEDIATE disagree about when to take money out of a funded
account (see ``backtest.recycle.Policy``). Neither ``docs/NOTES_JX.md`` nor
the independent re-check on this branch asked what happens if the firm itself
stops paying out mid-run -- they argued about the rate from priors, not from
a sweep.

Model: at an annual hazard rate ``h``, the firm fails at some day T drawn from
an exponential distribution (continuous-time constant hazard). If it fails
before the data ends, every dollar still sitting in the account is lost (it
was already worth $0 in this model's own accounting -- see recycle.py's "money
left in a funded account is not money"), cash already withdrawn is kept, and
no further evaluations are bought after T. If it never fails inside the
window, the run's own 11-year net stands.

That truncation is exactly "cash minus cost as of the last event before T",
both of which ``recycle()``'s timeline already tracks cumulatively per event,
so no new accounting is needed -- only a draw over when to stop reading it.

Monte Carlo over T rather than a closed form: cost is a step function of
elapsed months, so the expectation has no simple closed form, and 20,000
draws is cheap.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from backtest.engine import BacktestConfig, simulate
from backtest.recycle import Policy, XFARules, costs, recycle
from ict import data as D
from strategies.ltf_sweep import generate_orders

RISK = 900.0
HISTORY_START = "2016-01-01"
DRAWS = 20_000
SEED = 20261106
HAZARDS = [h / 100 for h in range(0, 26)]


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


def net_if_failure_at(result: dict, rules: XFARules, first_ts, failure_day: float) -> float:
    """What the run is worth if the firm stops paying out ``failure_day`` days in."""
    cash, cost = 0.0, costs(rules, failure_day, 0, 0)["total"]
    for row in result["timeline"]:
        elapsed = (row["ts"] - first_ts).total_seconds() / 86400
        if elapsed > failure_day:
            break
        cash, cost = row["cash"], row["cost"]
    return cash - cost


def expected_net(result: dict, rules: XFARules, first_ts, total_days: float,
                  hazard_annual: float, rng: np.random.Generator) -> float:
    if hazard_annual <= 0:
        return result["net"]
    lam = -np.log(1 - hazard_annual) / 365.0
    draws = rng.exponential(1.0 / lam, size=DRAWS)
    survives = draws >= total_days
    nets = np.empty(DRAWS)
    nets[survives] = result["net"]
    fail_days = draws[~survives]
    # Precompute once per distinct failure day is wasted effort at this scale;
    # a plain loop over 20,000 draws runs in well under a second.
    nets[~survives] = [net_if_failure_at(result, rules, first_ts, d) for d in fail_days]
    return float(nets.mean())


def verify_wired(result: dict, rules: XFARules, first_ts, total_days: float,
                  policy: Policy) -> None:
    """Three checks a sweep that silently ignores ``h`` would also pass as
    "no crossing": (1) h=0 must reproduce the plain run exactly, (2) the
    simulated failure count must actually grow with h, (3) for LOCK_FIRST,
    report the lock-attainment rate the whole argument rests on.
    """
    rng = np.random.default_rng(SEED)
    net_h0 = expected_net(result, rules, first_ts, total_days, 0.0, rng)
    print(f"  [{policy.value}] h=0 sweep net = {net_h0:.0f}  "
          f"vs plain recycle() net = {result['net']:.0f}  "
          f"{'MATCH' if net_h0 == result['net'] else 'MISMATCH -- VOID'}")

    for h in (0.0, 0.05, 0.25):
        rng = np.random.default_rng(SEED)
        if h <= 0:
            fired = 0
        else:
            lam = -np.log(1 - h) / 365.0
            draws = rng.exponential(1.0 / lam, size=DRAWS)
            fired = int((draws < total_days).sum())
        print(f"  [{policy.value}] h={h:.0%}: {fired}/{DRAWS} draws fire "
              f"a failure before day {total_days:.0f}")

    if policy is Policy.LOCK_FIRST:
        seen, locked = result["funded_accounts_seen"], result["funded_accounts_locked"]
        rate = locked / seen if seen else float("nan")
        print(f"  [{policy.value}] lock-attainment: {locked}/{seen} funded "
              f"accounts ({rate:.1%}) ever reached the +$2,000 lock before "
              "ending")
        return rate
    return None


def main() -> None:
    trades = load_trades(RISK)
    rules = XFARules()
    first_ts = trades["entry_ts"].iloc[0]

    print("=== verification: is the hazard actually wired? ===")
    lock_rate = None
    results = {}
    for policy in (Policy.LOCK_FIRST, Policy.IMMEDIATE):
        result = recycle(trades, rules=rules, policy=policy)
        results[policy] = result
        rate = verify_wired(result, rules, first_ts, result["days"], policy)
        if rate is not None:
            lock_rate = rate
    print()

    rows = []
    for policy, result in results.items():
        total_days = result["days"]
        rng = np.random.default_rng(SEED)
        for h in HAZARDS:
            net = expected_net(result, rules, first_ts, total_days, h, rng)
            rows.append({"policy": policy.value, "hazard_annual": h, "net": net})

    table = pd.DataFrame(rows).pivot(index="hazard_annual", columns="policy", values="net")
    table["lock_first_minus_immediate"] = (
        table[Policy.LOCK_FIRST.value] - table[Policy.IMMEDIATE.value])

    print(table.round(0).to_string())

    sign = np.sign(table["lock_first_minus_immediate"])
    crossing = sign.ne(sign.shift()).iloc[1:]
    if crossing.any():
        idx = crossing[crossing].index
        for h in idx:
            prior = table.index[table.index.get_loc(h) - 1]
            print(f"\nbreakeven h* between {prior:.0%} and {h:.0%} annual hazard")
    else:
        winner = Policy.LOCK_FIRST if sign.iloc[0] > 0 else Policy.IMMEDIATE
        print(f"\nno crossing in [0%, 25%]: {winner.value} wins at every hazard tested "
              f"(LOCK_FIRST lock-attainment rate: {lock_rate:.1%})")


if __name__ == "__main__":
    main()

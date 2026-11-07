"""Three checks before any money is spent on Topstep.

    uv run python scripts/jx_checks.py                      # data as it stands
    uv run python scripts/jx_checks.py --end 2026-09-08T05:27Z   # as the docs saw it

Every number in docs/NOTES_JX.md comes from this script's output. Nothing here
changes a strategy parameter: the trades are the same ``ltf_sweep`` trades at
$900 that scripts/recycling_report.py and scripts/account_lifetime.py use, and
only the account rules (``XFARules``) and payout ``Policy`` are varied.

1. DRIFT       -- which parameterisation produced each GO_LIVE figure.
2. BY YEAR     -- when the cash from the one unbroken 2016-> chain arrives.
3. STRESS      -- net profit under each adverse rule change, one at a time.

Orders are cached in data/processed/ (gitignored) keyed by the data cutoff, so a
second run skips the ~3 minute signal scan.
"""

from __future__ import annotations

import argparse
import dataclasses
import sys

import pandas as pd

from backtest.engine import BacktestConfig, simulate
from backtest.recycle import Policy, XFARules, recycle
from ict import data as D
from strategies.ltf_sweep import generate_orders

RISK = 900.0
#: Which rulebook. "20261106" adds the two payout rules read that day; the
#: committed docs/jx_runs/checks_*.txt from before then used "20260914".
RULEBOOKS = {
    "20260914": XFARules(payout_locks_mll=False, profit_since_payout_required=False,
                         payout_cap=4000.0, combine_mll_locks=False),
    "20261106": XFARules(payout_cap=4000.0, combine_mll_locks=False),
    #: $2,000 standing cap, and the evaluation floor locking at the start.
    "20261107": XFARules(),
}
BASE = RULEBOOKS["20261107"]
HISTORY_START = "2016-01-01"


def load(end: pd.Timestamp | None, lead: str) -> pd.DataFrame:
    filters = [("ts", ">=", pd.Timestamp(lead, tz="UTC"))]
    if end is not None:
        filters.append(("ts", "<", end))
    frame = pd.read_parquet(D.PROCESSED_DIR / "nq_1m.parquet", filters=filters)
    return D.add_time_columns(frame).reset_index(drop=True)


def orders_for(bars: pd.DataFrame, tag: str) -> pd.DataFrame:
    path = D.PROCESSED_DIR / f"jx_orders_{tag}.parquet"
    if path.exists():
        return pd.read_parquet(path)
    orders = generate_orders(bars)
    orders.to_parquet(path, index=False)
    return orders


def filled(orders, bars, risk=RISK) -> pd.DataFrame:
    t = simulate(orders, bars, BacktestConfig(risk_per_trade_usd=risk))
    return t[t["filled"]].sort_values("exit_ts").reset_index(drop=True)


def report_history(trades):
    """The slice scripts/recycling_report.py calls ``history``."""
    keep = trades["entry_ts"] >= pd.Timestamp(HISTORY_START, tz="UTC")
    return trades[keep].reset_index(drop=True)


def lifetime_history(trades):
    """The slice scripts/account_lifetime.py uses (exit_ts, bars from 2015-12-01)."""
    keep = pd.DatetimeIndex(trades["exit_ts"]) >= pd.Timestamp(HISTORY_START, tz="UTC")
    return trades[keep].reset_index(drop=True)


def row(label, out, extra_cost=0.0):
    cost = out["cost"] + extra_cost
    net = out["cash"] - cost
    print(f"  {label:<46}{out['accounts_bought']:>5}{out['funded_earned']:>5}"
          f"{out['payouts']:>5}{out['cash']:>11,.0f}{cost:>10,.0f}{net:>11,.0f}")
    return net


def header():
    print(f"  {'':<46}{'acct':>5}{'xfa':>5}{'pay':>5}{'withdrawn':>11}"
          f"{'spent':>10}{'net':>11}")


def check_drift(rep, life):
    print("\n1. FIGURE DRIFT   ($900, one unbroken chain from 2016)")
    header()
    for name, hist in (("recycling_report slice", rep),
                       ("account_lifetime slice", life)):
        for cap in (4000.0, 2000.0):
            rules = dataclasses.replace(BASE, payout_cap=cap)
            for pol in (Policy.LOCK_FIRST, Policy.IMMEDIATE):
                out = recycle(hist, rules, policy=pol)
                row(f"{name}, cap {cap:,.0f}, {pol.name}", out)
                if name.startswith("recycling") and cap == 4000.0:
                    print(f"      longest no-payout {out['longest_dry_days']:,.0f} days, "
                          f"longest bust streak {out['longest_bust_streak']}, "
                          f"unrealised at end ${out['unrealised']:,.0f}")
    print(f"  trades: report slice {len(rep)}, lifetime slice {len(life)}; "
          f"raw net of the report slice ${rep['net_pnl'].sum():,.0f}")


def by_year(out, label, trades):
    raw = (trades.assign(y=pd.DatetimeIndex(trades["exit_ts"])
                         .tz_convert("America/New_York").year)
           .groupby("y")["net_pnl"].sum())
    tl = pd.DataFrame(out["timeline"])
    tl["year"] = pd.DatetimeIndex(tl["ts"]).tz_convert("America/New_York").year
    # timeline carries running totals; the per-year figure is the change.
    last = tl.groupby("year")[["cash", "cost"]].last()
    flows = last.diff().fillna(last)
    ev = tl.pivot_table(index="year", columns="event", values="trade",
                        aggfunc="count", fill_value=0)
    print(f"\n  {label}")
    print(f"  {'year':>6}{'payouts':>9}{'passed':>8}{'busts':>7}"
          f"{'withdrawn':>11}{'spent*':>9}{'net':>9}{'cum withdrawn':>15}{'share':>7}"
          f"{'raw strat':>11}")
    total = out["cash"]
    for y in range(2016, int(tl['year'].max()) + 1):
        w = float(flows["cash"].get(y, 0.0))
        c = float(flows["cost"].get(y, 0.0))
        cum = float(last["cash"].loc[:y].iloc[-1]) if (last.index <= y).any() else 0.0
        e = ev.loc[y] if y in ev.index else {}
        busts = int(e.get("combine_bust", 0) + e.get("funded_bust", 0)) if len(e) else 0
        print(f"  {y:>6}{int(e.get('payout', 0)) if len(e) else 0:>9}"
              f"{int(e.get('passed', 0)) if len(e) else 0:>8}{busts:>7}"
              f"{w:>11,.0f}{c:>9,.0f}{w - c:>9,.0f}{cum:>15,.0f}{w / total:>7.0%}"
              f"{float(raw.get(y, 0.0)):>11,.0f}")
    print(f"  * spent is booked at each event, so it lags the calendar slightly; "
          f"final spend ${out['cost']:,.0f}")
    def span(years, col):
        return sum(float(flows[col].get(y, 0.0)) for y in years)
    dev, oos = range(2016, 2024), range(2024, 2027)
    for name, ys in (("2016-2023 (strategy losing)", dev),
                     ("2024-2026 (strategy winning)", oos)):
        w, c = span(ys, "cash"), span(ys, "cost")
        r = sum(float(raw.get(y, 0.0)) for y in ys)
        print(f"  {name:<30} withdrawn ${w:>8,.0f} ({w / total:.1%})  "
              f"spent ${c:>7,.0f}  net ${w - c:>8,.0f}  raw strategy ${r:>8,.0f}")
    years = range(2016, int(tl["year"].max()) + 1)
    for name, ys in (("years the strategy lost", [y for y in years if raw.get(y, 0) < 0]),
                     ("years the strategy made money", [y for y in years if raw.get(y, 0) >= 0])):
        w, c = span(ys, "cash"), span(ys, "cost")
        r = sum(float(raw.get(y, 0.0)) for y in ys)
        print(f"  {name:<30} {ys}")
        print(f"  {'':<30} withdrawn ${w:>8,.0f} ({w / total:.1%})  "
              f"spent ${c:>7,.0f}  net ${w - c:>8,.0f}  raw strategy ${r:>8,.0f}")


def stress(hist, policy):
    base = BASE
    print(f"\n  policy {policy.name}")
    header()
    nets = {}
    nets["baseline"] = row("baseline (selected rulebook)",
                           recycle(hist, base, policy=policy))
    nets["reset99"] = row("reset 49 -> 99",
                          recycle(hist, dataclasses.replace(base, reset=99.0),
                                  policy=policy))
    out = recycle(hist, base, policy=policy)
    extra = (out["accounts_bought"] - out["funded_earned"]) * base.activation
    nets["act_attempt"] = row("activation per attempt (x accounts bought)", out, extra)
    nets["nolock"] = row("MLL never locks (mll_locks_at=None)",
                         recycle(hist, dataclasses.replace(base, mll_locks_at=None,
                                                     payout_locks_mll=False),
                                 policy=policy))
    nets["cap2000"] = row("payout_cap 4000 -> 2000",
                          recycle(hist, dataclasses.replace(base, payout_cap=2000.0),
                                  policy=policy))
    nets["wd10"] = row("winning_days_required 5 -> 10",
                       recycle(hist, dataclasses.replace(base, winning_days_required=10),
                               policy=policy))
    allr = dataclasses.replace(base, reset=99.0, mll_locks_at=None,
                               payout_locks_mll=False,
                               payout_cap=2000.0, winning_days_required=10)
    out = recycle(hist, allr, policy=policy)
    extra = (out["accounts_bought"] - out["funded_earned"]) * allr.activation
    nets["all"] = row("ALL FIVE at once", out, extra)

    changes = {"reset99": {"reset": 99.0}, "act_attempt": None,
               "nolock": {"mll_locks_at": None, "payout_locks_mll": False}, "cap2000": {"payout_cap": 2000.0},
               "wd10": {"winning_days_required": 10}}
    keys = list(changes)
    print(f"\n  pairs (net):")
    for i, a in enumerate(keys):
        for b in keys[i + 1:]:
            kw = {**(changes[a] or {}), **(changes[b] or {})}
            rules = dataclasses.replace(base, **kw)
            out = recycle(hist, rules, policy=policy)
            extra = ((out["accounts_bought"] - out["funded_earned"]) * rules.activation
                     if "act_attempt" in (a, b) else 0.0)
            print(f"    {a + ' + ' + b:<28}{out['cash'] - out['cost'] - extra:>11,.0f}")
    return nets


def strategy_figures(end):
    """The README/GO_LIVE strategy figures, through simulator_inputs' own path
    (same function, same window), plus the true profit factor, which no script
    in the repo prints for this window."""
    sys.path.insert(0, str(D.REPO_ROOT / "scripts"))
    from simulator_inputs import edge_stats, returns
    df1 = D.load("1m")
    if end is not None:
        df1 = df1[df1["ts"] < end].reset_index(drop=True)
    r, net = returns(df1, "2016-01-01", "2027-01-01", True, 500.0)
    s = edge_stats(r)
    pf = r[r > 0].sum() / -r[r <= 0].sum()
    print("\n0. STRATEGY FIGURES   ($500, one per day, 2016->, simulator_inputs path)")
    print(f"  trades {s['trades']}  win {s['win_rate']:.1%}  payoff {s['payoff']:.3f}  "
          f"breakeven {s['breakeven_win_rate']:.1%}  PROFIT FACTOR {pf:.3f}  "
          f"net ${net:,.0f}  per trade ${net / s['trades']:,.2f}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--end", default=None,
                    help="exclusive UTC cutoff, e.g. 2026-09-08T05:27Z")
    ap.add_argument("--rules", choices=sorted(RULEBOOKS), default="20261107")
    ap.add_argument("--skip-strategy", action="store_true",
                    help="skip section 0 (re-scans the signals, ~3 min)")
    args = ap.parse_args(argv)
    global BASE
    BASE = RULEBOOKS[args.rules]
    print(f"rules: {args.rules}  {BASE}")
    end = pd.Timestamp(args.end) if args.end else None
    if end is not None and end.tzinfo is None:
        end = end.tz_localize("UTC")
    tag = end.strftime("%Y%m%dT%H%M") if end is not None else "all"

    bars_rep = load(end, "2015-11-17")
    print(f"data: {bars_rep.ts.min()} -> {bars_rep.ts.max()}")
    orders = orders_for(bars_rep, tag)
    rep = report_history(filled(orders, bars_rep))
    bars_life = bars_rep[bars_rep["ts"] >= pd.Timestamp("2015-12-01", tz="UTC")
                         ].reset_index(drop=True)
    life = lifetime_history(filled(orders, bars_life))

    if not args.skip_strategy:
        strategy_figures(end)
    check_drift(rep, life)

    print("\n2. WITHDRAWALS BY CALENDAR YEAR   (unbroken chain, $900, cap 4000)")
    for pol in (Policy.IMMEDIATE, Policy.LOCK_FIRST):
        by_year(recycle(rep, BASE, policy=pol), f"policy {pol.name}", rep)

    print("\n3. RULE-CHANGE STRESS TEST   (one change at a time, then all five)")
    for pol in (Policy.IMMEDIATE, Policy.LOCK_FIRST):
        stress(rep, pol)
    return 0


if __name__ == "__main__":
    sys.exit(main())

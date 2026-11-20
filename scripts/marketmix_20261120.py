"""Market mix across accounts (docs/PREREG_MARKETMIX_20261120.md).

    uv run python scripts/marketmix_20261120.py              # part 1 (before compliance)
    uv run python scripts/marketmix_20261120.py --compliant  # part 2 (addendum)
"""
from __future__ import annotations

import sys

import numpy as np
import pandas as pd

sys.path.insert(0, "scripts")
from backtest.engine import COMMISSION_MNQ, BacktestConfig, simulate  # noqa: E402
from backtest.recycle import Policy, XFARules, recycle  # noqa: E402
from es_test import bars_for, config_for  # noqa: E402
from ict import data as D  # noqa: E402
from scripts.portfolio2_20261120 import RULES, platform_costs  # noqa: E402
from scripts.portfolio_20261120 import DAYS, HI, LO, daily_from_recycle, stats  # noqa: E402

EXPECT = {"NQ": 44359.0, "ES": 20338.0, "YM": 11744.0}


def trades(mkt):
    if mkt in ("NQ", "ES"):
        bars, cfg = bars_for(mkt), config_for(mkt)
    else:  # YM, unscaled settings, config as scripts/ym_rty_test.py
        bars = D.add_time_columns(D.load_raw("YM_v_0_1m_*.parquet"))
        cfg = BacktestConfig(risk_per_trade_usd=900.0, tick_value=0.50 * 0.25,
                             commission_per_round_turn=COMMISSION_MNQ, exit_slippage_ticks=1.0 / 0.25)
    orders = pd.read_parquet(D.PROCESSED_DIR / f"ideas_orders_{mkt}.parquet")
    t = simulate(orders, bars, cfg)
    t = t[t["filled"]]
    t = t[(t.entry_ts >= pd.Timestamp(LO, tz="UTC")) & (t.entry_ts < pd.Timestamp(HI, tz="UTC"))]
    return t.sort_values("exit_ts").reset_index(drop=True)


def no_cross_hedge(tr: dict) -> tuple[dict, dict]:
    """Skip any trade opposite to a position still open in another market (addendum, part 2)."""
    rows = pd.concat([t.assign(mkt_=m, i_=range(len(t))) for m, t in tr.items()]).sort_values("entry_ts")
    open_pos, keep = [], {m: [] for m in tr}
    skipped = {m: 0 for m in tr}
    for r in rows.itertuples():
        open_pos = [p for p in open_pos if p[2] > r.entry_ts]
        if any(p[0] != r.mkt_ and p[1] != r.direction for p in open_pos):
            skipped[r.mkt_] += 1
            continue
        keep[r.mkt_].append(r.i_)
        open_pos.append((r.mkt_, r.direction, r.exit_ts))
    return {m: tr[m].iloc[sorted(keep[m])].reset_index(drop=True) for m in tr}, skipped


def main() -> int:
    tr = {m: trades(m) for m in ("NQ", "ES", "YM")}
    for m, t in tr.items():
        got = recycle(t, XFARules(), policy=Policy.LOCK_FIRST)["net"]
        ok = abs(got / EXPECT[m] - 1) <= 0.01
        print(f"check {m}: Topstep single-account net ${got:,.0f} vs earlier ${EXPECT[m]:,.0f} -> {'OK' if ok else 'MISMATCH'}")
        if not ok:
            print("stopping: trades do not reproduce the earlier figure (pre-registered rule)")
            return 1
    raw = tr
    if "--compliant" in sys.argv:
        tr, skipped = no_cross_hedge(tr)
        print("compliance filter: skipped " + ", ".join(f"{m} {n}" for m, n in skipped.items()) + " trades")
        for m, t in tr.items():
            print(f"  {m} single Topstep account after filter: ${recycle(t, XFARules(), policy=Policy.LOCK_FIRST)['net']:,.0f}")
    d = {(f, m): daily_from_recycle(tr[m], RULES[f])[0] for f in RULES for m in tr}
    # Single-market portfolios hold nothing to hedge against: they use the unfiltered trades.
    d_raw = {(f, "NQ"): daily_from_recycle(raw["NQ"], RULES[f])[0] for f in RULES}
    corr = pd.DataFrame({m: d[("Topstep", m)].resample("ME").last().diff() for m in tr}).corr()
    print("\nmonthly P&L correlation, one Topstep account per market:\n" + corr.to_string(float_format=lambda x: f"{x:.2f}"))
    ports = {
        "T5-NQ  5 Topstep all NQ": {("Topstep", "NQ"): 5},
        "T5-mix 5 Topstep 3NQ/1ES/1YM": {("Topstep", "NQ"): 3, ("Topstep", "ES"): 1, ("Topstep", "YM"): 1},
        "C-NQ   5T/5L/3M all NQ": {("Topstep", "NQ"): 5, ("Lucid", "NQ"): 5, ("MFFU", "NQ"): 3},
        "C-mix  5T/5L/3M mixed": {("Topstep", "NQ"): 3, ("Topstep", "ES"): 1, ("Topstep", "YM"): 1,
                                  ("Lucid", "NQ"): 3, ("Lucid", "ES"): 1, ("Lucid", "YM"): 1,
                                  ("MFFU", "NQ"): 2, ("MFFU", "ES"): 1},
    }
    print()
    res, yearly = {}, {}
    for name, w in ports.items():
        src = d_raw if {m for _, m in w} == {"NQ"} else d
        s = sum(n * src[k] for k, n in w.items()) - platform_costs({f for f, _ in w})
        yearly[name.split()[0]] = stats(name, s)
        peak = s.cummax().clip(lower=0)
        res[name.split()[0]] = (s.iloc[-1], max(-(s - peak).min(), -min(0.0, s.min())))
    print("\nyearly income:\n" + pd.DataFrame(yearly).to_string(float_format=lambda x: f"{x:,.0f}"))
    for a, b in (("T5-NQ", "T5-mix"), ("C-NQ", "C-mix")):
        (na, ca), (nb, cb) = res[a], res[b]
        better = (nb / cb) / (na / ca) - 1
        verdict = "WORTH DOING" if better >= 0.15 and nb >= 0.75 * na else "not worth it"
        print(f"{b} vs {a}: net {nb / na - 1:+.1%}, cash on hand {cb / ca - 1:+.1%}, "
              f"net per $ of cash {better:+.1%} -> {verdict} (pre-registered rule)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

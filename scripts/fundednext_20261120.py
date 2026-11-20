"""FundedNext Futures Rapid Pro 50K, alone and added to the mixed plan (docs/PREREG_FUNDEDNEXT_20261120.md).

    uv run python scripts/fundednext_20261120.py
"""
from __future__ import annotations

import dataclasses
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, "scripts")
from backtest.recycle import Policy, XFARules, recycle  # noqa: E402
from marketmix_20261120 import no_cross_hedge, trades  # noqa: E402
from scripts.portfolio2_20261120 import RULES, platform_costs  # noqa: E402
from scripts.portfolio_20261120 import daily_from_recycle, stats  # noqa: E402

FN = dataclasses.replace(
    XFARules(), profit_target=3000, loss_limit=2000, combine_max_contracts=40, funded_loss_limit=2000,
    mll_locks_at=2100, lock_level=100.0, funded_scaling=False, consistency_target=0.40, consistency_days=3,
    winning_days_required=0, payout_goal=(500.0, 500.0), payout_share=0.5, payout_cap=1000.0, payout_min=250.0,
    max_payouts_per_xfa=5, profit_split=0.90, one_time_price=159.99, reset=159.99, monthly=0.0,
    activation=0.0, api_monthly=0.0)
MIX5 = {"NQ": 3, "ES": 1, "YM": 1}


def main() -> int:
    raw = {m: trades(m) for m in ("NQ", "ES", "YM")}
    t = raw["NQ"]
    g, comm = t.gross_pnl.to_numpy(), (t.gross_pnl - t.net_pnl).to_numpy()
    for cap in (1000.0, 1250.0):
        rules = dataclasses.replace(FN, payout_cap=cap)
        real = recycle(t, rules, policy=Policy.LOCK_FIRST)
        rng = np.random.default_rng(1)
        flips = np.array([recycle(t.assign(net_pnl=np.abs(g) * rng.choice([-1, 1], len(t)) - comm), rules,
                                  policy=Policy.LOCK_FIRST)["net"] for _ in range(200)])
        print(f"FundedNext Rapid Pro 50K, cap ${cap:,.0f}, NQ single account: real net ${real['net']:,.0f} "
              f"(spent ${real['cost']:,.0f}, payouts {real['payouts']}) | coin-flip median ${np.median(flips):,.0f}, "
              f"profitable {(flips > 0).mean():.0%}   [Topstep 50K: $44,359 real / $18,046 coin flip]")
    tr, _ = no_cross_hedge(raw)
    firms = {**RULES, "FundedNext": FN}
    d = {(f, m): daily_from_recycle(tr[m], firms[f])[0] for f in firms for m in tr}
    base = {("Topstep", "NQ"): 3, ("Topstep", "ES"): 1, ("Topstep", "YM"): 1,
            ("Lucid", "NQ"): 3, ("Lucid", "ES"): 1, ("Lucid", "YM"): 1, ("MFFU", "NQ"): 2, ("MFFU", "ES"): 1}
    plus = {**base, **{("FundedNext", m): n for m, n in MIX5.items()}}
    res = {}
    print()
    for name, w in (("C-mix", base), ("C-mix + 5 FundedNext", plus)):
        s = sum(n * d[k] for k, n in w.items()) - platform_costs({f for f, _ in w})
        stats(name, s)
        peak = s.cummax().clip(lower=0)
        res[name] = (s.iloc[-1], max(-(s - peak).min(), -min(0.0, s.min())))
    (n0, c0), (n1, c1) = res["C-mix"], res["C-mix + 5 FundedNext"]
    ok = n1 >= 1.10 * n0 and (n1 / c1) >= 0.90 * (n0 / c0)
    print(f"\nadding FundedNext: net {n1 / n0 - 1:+.1%}, cash {c1 / c0 - 1:+.1%}, net per $ cash "
          f"{(n1 / c1) / (n0 / c0) - 1:+.1%} -> {'WORTH ADDING' if ok else 'not worth adding'} (pre-registered rule)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

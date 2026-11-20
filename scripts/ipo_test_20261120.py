"""CANDIDATES #49: Bursa IPO public ballot (docs/PREREG_LOOPHOLES_20261120.md).

Data: data/public/ipo_sample_20261120.csv, 19 IPOs (2024-05..2026-11) hand-collected
from news search results, one source per row. The pre-registered "every IPO" data
was not reachable (Bursa and i3investor block automated access; see results).

    uv run python scripts/ipo_test_20261120.py
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

P = Path(__file__).resolve().parent.parent / "data" / "public" / "ipo_sample_20261120.csv"
IPOS_PER_YEAR = 55          # Bursa Main+ACE IPOs: 51 in 2024, ~55 in 2025 (news counts)
FEE = 2.0                   # RM per e-IPO application
SELL = 0.0025               # brokerage + clearing + stamp duty, approx


def main() -> int:
    d = pd.read_csv(P, parse_dates=["listing"]).sort_values("listing").reset_index(drop=True)
    d["r"] = d.close / d.price - 1
    print(f"{len(d)} IPOs {d.listing.min():%Y-%m}..{d.listing.max():%Y-%m}; first-day close vs issue: mean {d.r.mean():+.1%}, "
          f"median {d.r.median():+.1%}, below issue {(d.r < 0).mean():.0%}")

    # pre-registered metric: value per RM applied e = r/(1+X)
    e = d.r / (1 + d.x_all)
    h = len(d) // 2
    passed = e.mean() > 0.005 and e.iloc[:h].mean() > 0 and e.iloc[h:].mean() > 0 and (d.r < 0).mean() < 0.35
    print(f"pre-registered: mean value per RM applied {e.mean():.2%} (halves {e.iloc[:h].mean():.2%} / {e.iloc[h:].mean():.2%}), "
          f"r<0 {(d.r < 0).mean():.0%} -> {'PASS' if passed else 'FAIL'}")
    print(f"  RM10,000 pro-rata application: mean RM{(1e4 * e).mean():,.0f} per IPO, median RM{(1e4 * e).median():,.0f}")

    # average profit per application (no allotment-rule assumption): tranche shares x price x r / applications
    for tag, n, m, x, s in (("all public", "n_all", "m_all_mn", "x_all", "s_all_mn"), ("general portion", "n_gen", "m_gen_mn", "x_gen", None)):
        q = d[d[n].notna()].copy()
        shares = q[s].fillna(q[m] / (1 + q[x])) if s else q[m] / (1 + q[x])
        q["stake_rm"] = shares * 1e6 * q.price / q[n]                 # average allotment value per application
        q["g"] = q.stake_rm * q.r - FEE - SELL * q.stake_rm.clip(lower=0)
        q["avg_app_rm"] = q[m] * 1e6 * q.price / q[n]
        print(f"\n{tag}: {len(q)} IPOs. Average application RM{q.avg_app_rm.median():,.0f} (median); "
              f"average allotment RM{q.stake_rm.median():,.0f} (median)")
        for _, r in q.iterrows():
            print(f"   {r['name']:<22} {r.listing:%Y-%m} r {r.r:+6.1%}  X {r[x]:6.1f}  allotment/app RM{r.stake_rm:7,.0f}  profit/app RM{r.g:7,.0f}")
        print(f"  profit per application: mean RM{q.g.mean():,.0f}, median RM{q.g.median():,.0f}; "
              f"x {IPOS_PER_YEAR} IPOs/yr = RM{q.g.mean() * IPOS_PER_YEAR:,.0f}/yr (mean) or RM{q.g.median() * IPOS_PER_YEAR:,.0f}/yr (median)")
        rng = np.random.default_rng(1)
        boot = [rng.choice(q.g.to_numpy(), len(q)).mean() * IPOS_PER_YEAR for _ in range(5000)]
        print(f"  bootstrap 90% range for RM/yr: {np.percentile(boot, 5):,.0f} .. {np.percentile(boot, 95):,.0f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

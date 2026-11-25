"""What the payouts look like: LucidDaily 50K EOD ($85.40) vs Topstep 50K Consistency (descriptive; docs/PREREG_LUCID_START_20261125.md addendum).

    uv run python -m scripts.payout_size_20261126 | tee docs/jx_runs/payout_size_20261126.txt
"""
import contextlib
import io

import numpy as np
import pandas as pd

from backtest.recycle import Policy, recycle
from scripts.radar_price import scaled

with contextlib.redirect_stdout(io.StringIO()):
    from scripts.portfolio_my_20261123 import P, T


def tl_of(trades, rules):
    pol = Policy.IMMEDIATE if rules.mll_locks_at is None else Policy.LOCK_FIRST
    tl = pd.DataFrame(recycle(trades, rules, policy=pol)["timeline"])
    tl["paid"] = tl["cash"].diff().fillna(tl["cash"])
    return tl


print("Payouts to the trader (after the firm's split), friend's NQ trades at $900 risk, rules as in portfolio_my_20261123.\n")
for name in ["LucidDaily 50K EOD (promo $85.40)", "Topstep 50K Consistency path"]:
    rules, risk, dll = P[name]
    s = scaled(T, risk / 900)
    if dll:
        s = s.assign(net_pnl=np.maximum(s["net_pnl"].to_numpy(), -dll))
    full = tl_of(s, rules)
    pays = full[full.event == "payout"]["paid"]
    yrs = 10.83
    print(f"{name}")
    print(f"  whole history 2016-26: {len(pays)} payouts ({len(pays) / yrs:.1f}/yr); size median ${pays.median():,.0f}, 25-75% ${pays.quantile(.25):,.0f}-${pays.quantile(.75):,.0f}, "
          f"largest ${pays.max():,.0f}; total paid ${pays.sum():,.0f}, fees ${full.cost.iloc[-1]:,.0f}")
    entry = pd.DatetimeIndex(s["entry_ts"])
    rows, start = [], pd.Timestamp("2016-01-01", tz=entry.tz)
    while start <= pd.Timestamp("2025-10-01", tz=entry.tz):
        chunk = s[entry >= start].reset_index(drop=True)
        tl = tl_of(chunk, rules)
        t0 = chunk["entry_ts"].iloc[0]
        p = tl[tl.event == "payout"]
        y1 = tl[pd.to_datetime(tl.ts) < t0 + pd.DateOffset(months=12)]
        p1 = y1[y1.event == "payout"]
        fees_before = float(tl.loc[p.index[0], "cost"]) if len(p) else np.nan
        rows.append(dict(first=float(p["paid"].iloc[0]) if len(p) else np.nan, fees_before=fees_before,
                         n12=len(p1), paid12=float(p1["paid"].sum()), fees12=float(y1["cost"].iloc[-1]) if len(y1) else 0.0))
        start += pd.DateOffset(months=1)
    d = pd.DataFrame(rows)
    print(f"  per start (118 monthly starts 2016-01..2025-10):")
    print(f"    first payout: median ${d['first'].median():,.0f} (25-75% ${d['first'].quantile(.25):,.0f}-${d['first'].quantile(.75):,.0f}); "
          f"fees paid by then: median ${d.fees_before.median():,.0f}")
    print(f"    first 12 months: payouts median {d.n12.median():.0f} (none in {(d.n12 == 0).mean():.0%} of starts); "
          f"paid median ${d.paid12.median():,.0f} (25-75% ${d.paid12.quantile(.25):,.0f}-${d.paid12.quantile(.75):,.0f}); fees median ${d.fees12.median():,.0f}\n")

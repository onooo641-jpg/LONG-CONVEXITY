"""Money needed to start: LucidDaily 50K EOD vs Topstep 50K, fresh chain on every monthly start date 2016-01..2025-10.

Same rules and trades as scripts/portfolio_my_20261123.py (docs/PREREG_LUCID_START_20261125.md).
    uv run python -m scripts.lucid_start_capital_20261125 | tee docs/jx_runs/lucid_start_capital_20261125.txt
"""
import contextlib
import io

import numpy as np
import pandas as pd

from backtest.recycle import Policy, recycle
from scripts.radar_price import scaled

with contextlib.redirect_stdout(io.StringIO()):  # the portfolio module prints its own report on import
    from scripts.portfolio_my_20261123 import P, T

PRODUCTS = ["LucidDaily 50K EOD (promo $85.40)", "LucidDaily 50K EOD (list $122)", "Topstep 50K Consistency path"]


def run(rules, risk, dll):
    s = scaled(T, risk / 900)
    if dll:
        s = s.assign(net_pnl=np.maximum(s["net_pnl"].to_numpy(), -dll))
    pol = Policy.IMMEDIATE if rules.mll_locks_at is None else Policy.LOCK_FIRST
    entry = pd.DatetimeIndex(s["entry_ts"])
    rows, start = [], pd.Timestamp("2016-01-01", tz=entry.tz)
    while start <= pd.Timestamp("2025-10-01", tz=entry.tz):
        chunk = s[entry >= start].reset_index(drop=True)
        tl = pd.DataFrame(recycle(chunk, rules, policy=pol)["timeline"])
        net = np.concatenate([[0.0], tl["net"].to_numpy()])
        pay = tl[tl.event == "payout"]
        t0 = chunk["entry_ts"].iloc[0]
        rows.append(dict(start=start, worst=net.min(), ever_positive=bool((net > 0).any()),
                         days_first_payout=(pay["ts"].iloc[0] - t0).days if len(pay) else np.nan,
                         net_12m=float(tl[pd.to_datetime(tl.ts) < t0 + pd.DateOffset(months=12)]["net"].iloc[-1])
                         if (pd.to_datetime(tl.ts) < t0 + pd.DateOffset(months=12)).any() else 0.0))
        start += pd.DateOffset(months=1)
    return pd.DataFrame(rows)


print("Fresh chain started on each month 2016-01..2025-10 (118 starts); friend's NQ trades at $900 risk; rules as in portfolio_my_20261123.")
print("worst = deepest cumulative cash (fees - payouts) before recovering; negative = money out of pocket.\n")
for name in PRODUCTS:
    df = run(*P[name])
    w = df.worst
    rec = df[df.start >= pd.Timestamp("2023-01-01", tz=df.start.iloc[0].tz)]
    print(f"{name}  (n={len(df)})")
    print(f"  deepest loss: median ${w.median():,.0f} | 1 in 4 worse than ${w.quantile(.25):,.0f} | 1 in 10 worse than ${w.quantile(.10):,.0f} | worst ${w.min():,.0f}")
    d = df.days_first_payout.dropna()
    print(f"  days to first payout: median {d.median():.0f} | 75th pct {d.quantile(.75):.0f} | 90th pct {d.quantile(.9):.0f} | no payout {df.days_first_payout.isna().sum()}")
    print(f"  net after 12 months: median ${df.net_12m.median():,.0f} | share losing {(df.net_12m < 0).mean():.0%} | never positive {(~df.ever_positive).sum()}")
    print(f"  starts 2023+: median deepest ${rec.worst.median():,.0f}, median days to first payout {rec.days_first_payout.median():.0f}\n")

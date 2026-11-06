import sys; sys.path.insert(0,"scripts")
import numpy as np, pandas as pd
from jx_checks import load, filled, report_history
from backtest.recycle import recycle, Policy, XFARules
from ict import data as D
bars = load(None, "2015-11-17")
orders = pd.read_parquet(D.PROCESSED_DIR/"jx_orders_all.parquet")
h = report_history(filled(orders, bars, 900.0))
r = XFARules()
out = recycle(h, r, policy=Policy.LOCK_FIRST)
ev = pd.DataFrame(out["timeline"])
evals = out["accounts_bought"]; passed = out["funded_earned"]
print("chain: evaluations", evals, "passed", passed, f"pass rate {passed/evals:.1%}")
# per-attempt: evaluation outcomes only (combine_bust vs passed)
cb=(ev.event=="combine_bust").sum(); ps=(ev.event=="passed").sum()
print(f"evaluation attempts that ended: bust {cb} pass {ps} -> {ps/(cb+ps):.1%}")
# capital: start a fresh chain every month, measure worst cumulative net (cash-cost) and days to first positive
exits = pd.DatetimeIndex(h["exit_ts"])
rows=[]
start=exits.min()
while start < exits.max() - pd.DateOffset(months=12):
    chunk=h[exits>=start].reset_index(drop=True)
    o=recycle(chunk, r, policy=Policy.LOCK_FIRST)
    tl=pd.DataFrame(o["timeline"])
    net=np.concatenate([[0.0], tl["net"].to_numpy()])
    worst=net.min()
    pos = tl[tl["net"]>0]
    days = (pos["ts"].iloc[0]-chunk["entry_ts"].iloc[0]).days if len(pos) else None
    first_pay = tl[tl.event=="payout"]
    fp = (first_pay["ts"].iloc[0]-chunk["entry_ts"].iloc[0]).days if len(first_pay) else None
    # cost before first payout
    cost_fp = float(first_pay["cost"].iloc[0]) if len(first_pay) else None
    rows.append(dict(start=start.date(), worst=worst, days_to_positive=days, days_to_first_payout=fp, cost_before_first_payout=cost_fp))
    start += pd.DateOffset(months=1)
df=pd.DataFrame(rows)
print(len(df),"monthly start dates")
for c in ["worst","days_to_positive","days_to_first_payout","cost_before_first_payout"]:
    s=df[c].dropna().astype(float)
    print(f"{c:<26} median {s.median():>8,.0f}  p75 {s.quantile(.75):>8,.0f}  p90 {s.quantile(.9):>8,.0f}  worst {s.min() if c=='worst' else s.max():>8,.0f}  n={len(s)}")
print("never positive:", df.days_to_positive.isna().sum())
print("worst p25 p10:", df.worst.quantile(.25), df.worst.quantile(.10)); print("starts 2023+ worst median:", df[pd.to_datetime(df.start)>="2023-01-01"].worst.median(), "days_to_first_payout median", df[pd.to_datetime(df.start)>="2023-01-01"].days_to_first_payout.median())

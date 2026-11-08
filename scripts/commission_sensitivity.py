import pandas as pd
from backtest.engine import BacktestConfig, simulate
from backtest.recycle import recycle, Policy, XFARules
from ict import data as D
from strategies.ltf_sweep import generate_orders
bars=D.load("1m"); o=generate_orders(bars)
for c in (1.24, 0.74):
    t=simulate(o,bars,BacktestConfig(risk_per_trade_usd=900.0, commission_per_round_turn=c)); t=t[t.filled].sort_values("exit_ts")
    for lab,lo,hi in (("holdout 2010-07..2015","2010-07-01","2016-01-01"),("2016..2026-10","2016-01-01","2027-01-01")):
        h=t[(t.entry_ts>=pd.Timestamp(lo,tz="UTC"))&(t.entry_ts<pd.Timestamp(hi,tz="UTC"))].reset_index(drop=True)
        p=h.net_pnl; r=recycle(h,XFARules(),policy=Policy.LOCK_FIRST); tl=pd.DataFrame(r["timeline"])
        ps=(tl.event=="passed").sum(); b=(tl.event=="combine_bust").sum()
        print(f"MNQ ${c:.2f} RT | {lab:<22} raw PF {p[p>0].sum()/-p[p<0].sum():.3f}  raw ${p.sum():>9,.0f} | recycle net ${r['net']:>8,.0f}  pass {ps/(ps+b):.1%}")

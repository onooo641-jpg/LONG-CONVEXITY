"""POST-HOC (not pre-registered): fee drag by year, and the holdout re-run at today's fee ratio.

    uv run python scripts/holdout_fee_check.py

Written after scripts/holdout_test.py was run, to explain its baseline.
It does not change the pre-registered verdict.
"""
import sys; sys.path.insert(0,"scripts")
import numpy as np, pandas as pd
from backtest.engine import BacktestConfig, simulate
from ict import data as D
from strategies.ltf_sweep import generate_orders
bars=D.load("1m"); o=generate_orders(bars)
t=simulate(o,bars,BacktestConfig(risk_per_trade_usd=900.0)); t=t[t.filled]
t=t[t.entry_ts>=pd.Timestamp("2010-07-01",tz="UTC")]
t["y"]=pd.DatetimeIndex(t.exit_ts).tz_convert("America/New_York").year
t["fee"]=t.gross_pnl-t.net_pnl
def pf(x): return x[x>0].sum()/-x[x<0].sum()
g=t.groupby("y")
print(pd.DataFrame({"trades":g.size(),"price":g.entry_fill.median().round(0),"stop_pts":g.risk_points.median(),
 "contracts":g.contracts.median(),"fee_per_trade":g.fee.mean().round(0),"fee_%_of_risk":(g.fee.mean()/900*100).round(1),
 "gross_PF":g.gross_pnl.apply(pf).round(3),"net_PF":g.net_pnl.apply(pf).round(3)}).to_string())
for lab,lo,hi in (("holdout 2010-15",2010,2015),("seen 2016-26",2016,2026)):
    s=t[(t.y>=lo)&(t.y<=hi)]
    print(f"{lab}: gross PF {pf(s.gross_pnl):.3f}  net PF {pf(s.net_pnl):.3f}  gross ${s.gross_pnl.sum():,.0f}  fees ${s.fee.sum():,.0f}  win(gross) {(s.gross_pnl>0).mean():.1%}")
from backtest.recycle import recycle, Policy, XFARules
h=t[(t.y>=2010)&(t.y<=2015)].sort_values("exit_ts").reset_index(drop=True)
for pct in (0.018, 0.024, 0.03):
    hh=h.copy(); hh["net_pnl"]=hh.gross_pnl - pct*900.0
    o=recycle(hh, XFARules(), policy=Policy.LOCK_FIRST); tl=pd.DataFrame(o["timeline"])
    p=(tl.event=="passed").sum(); b=(tl.event=="combine_bust").sum()
    print(f"holdout, fees at {pct:.1%} of risk: raw PF {pf(hh.net_pnl):.3f} raw ${hh.net_pnl.sum():,.0f} | recycle net ${o['net']:,.0f} cash ${o['cash']:,.0f} cost ${o['cost']:,.0f} pass {p/(p+b):.1%} payouts {o['payouts']}")

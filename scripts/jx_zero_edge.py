"""Zero-edge baseline: same trade sizes, random sign, fees kept. uv run python scripts/jx_zero_edge.py"""
import sys; sys.path.insert(0,"scripts")
import numpy as np, pandas as pd, dataclasses
from jx_checks import load, filled, report_history
from backtest.recycle import recycle, Policy, XFARules
from ict import data as D
bars = load(None, "2015-11-17")
orders = pd.read_parquet(D.PROCESSED_DIR/"jx_orders_all.parquet")
h = report_history(filled(orders, bars, 900.0))
def passrate(o):
    tl=pd.DataFrame(o["timeline"]); p=(tl.event=="passed").sum(); b=(tl.event=="combine_bust").sum()
    return p/(p+b), o["net"]
r=XFARules()
pr,net=passrate(recycle(h,r,policy=Policy.LOCK_FIRST))
print(f"real trades:            pass {pr:.1%}  net ${net:,.0f}")
# zero edge: same trade sizes, random sign on gross P&L, commission still paid
gross = h["net_pnl"].to_numpy() + 0.0
comm = (h["gross_pnl"]-h["net_pnl"]).to_numpy() if "gross_pnl" in h else np.zeros(len(h))
g = h["gross_pnl"].to_numpy()
rng=np.random.default_rng(1); res=[]
for i in range(200):
    s=rng.choice([-1,1],len(h))
    hh=h.copy(); hh["net_pnl"]=np.abs(g)*s - comm
    res.append(passrate(recycle(hh,r,policy=Policy.LOCK_FIRST)))
res=np.array(res)
print(f"zero edge (coin flip):  pass median {np.median(res[:,0]):.1%} [{np.percentile(res[:,0],5):.1%}-{np.percentile(res[:,0],95):.1%}]  net median ${np.median(res[:,1]):,.0f}  profitable {np.mean(res[:,1]>0):.0%}")
# no commission coin flip
res2=[]
for i in range(200):
    s=rng.choice([-1,1],len(h)); hh=h.copy(); hh["net_pnl"]=np.abs(g)*s
    res2.append(passrate(recycle(hh,r,policy=Policy.LOCK_FIRST)))
res2=np.array(res2)
print(f"zero edge, no fees:     pass median {np.median(res2[:,0]):.1%}  net median ${np.median(res2[:,1]):,.0f}")

import pandas as pd, numpy as np
from backtest.engine import BacktestConfig, simulate
from ict import data as D
bars=D.load("1m"); orders=pd.read_parquet(D.PROCESSED_DIR/"ideas_orders_NQ.parquet")
t=simulate(orders,bars,BacktestConfig(risk_per_trade_usd=950)); t=t[t.filled]
t=t[(t.entry_ts>="2016-01-01")]
print(t.columns.tolist()[:30])
px=t["entry_price"] if "entry_price" in t else t["entry"]
notional=t["contracts"]*px*2.0   # micro NQ = $2/pt
lev=notional/50000
print("micros median", t.contracts.median(), "p90", t.contracts.quantile(.9))
print("leverage on 50K: median %.1fx, p10 %.1fx, p90 %.1fx"%(lev.median(), lev.quantile(.1), lev.quantile(.9)))
for L in (2,5,10,20):
    print(f"share of trades within {L}x: {(lev<=L).mean():.0%}; risk if capped at {L}x: median ${ (np.minimum(lev,L)/lev*950).median():.0f}")

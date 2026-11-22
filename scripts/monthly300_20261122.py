"""Monthly-income view: how often prop products clear $300/month (Jx question 2026-11-22). uv run python -m scripts.monthly300_20261122"""
import pandas as pd
from ict import data as D
from backtest.recycle import recycle, Policy
from scripts.radar_price import MODELS, trades, scaled
from scripts.radar_models2 import MODELS2
orders, bars = pd.read_parquet(D.PROCESSED_DIR / "ideas_orders_NQ.parquet"), D.load("1m")
t = trades(orders, bars, 0)
def monthly(rules, risk):
    out = recycle(scaled(t, risk / 900), rules, policy=Policy.LOCK_FIRST)
    tl = pd.DataFrame(out["timeline"]); tl["m"] = pd.to_datetime(tl.ts).dt.to_period("M")
    net = tl.groupby("m")["net"].last().reindex(pd.period_range("2016-01", "2026-10", freq="M")).ffill().fillna(0)
    return net.diff().fillna(net.iloc[0])
prods = {"Topstep 50K": MODELS["topstep50"][0][1:], "LucidFlex 50K": MODELS["lucidflex50"][0][1:],
         "TTP Prime 50K": MODELS2["ttp_prime50_r79"][1][0][1:] if isinstance(MODELS2["ttp_prime50_r79"][1], list) else MODELS2["ttp_prime50_r79"][1][1:]}
M = {k: monthly(*v) for k, v in prods.items()}
def rep(name, s):
    r12 = s.rolling(12).sum().dropna()
    print(f"{name:32s} avg ${s.mean():6,.0f}/mo | months >= $300: {(s >= 300).mean():4.0%} | rolling-12m avg >= $300/mo: {(r12 >= 3600).mean():4.0%} "
          f"| last 36m avg ${s[-36:].mean():6,.0f}/mo | worst 12m ${r12.min():8,.0f}")
for k, s in M.items(): rep(k, s)
rep("Topstep+Lucid+TTP (1 each)", sum(M.values()))
rep("Topstep x3 (same trades)", M["Topstep 50K"] * 3)

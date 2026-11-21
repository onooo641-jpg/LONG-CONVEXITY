"""Per-month view of every priced prop-firm product (real trades; same models and rules as scripts/radar_price.py).

    uv run python scripts/radar_monthly_20261121.py | tee docs/jx_runs/radar_monthly_20261121.txt
"""
import numpy as np
import pandas as pd

from backtest.recycle import Policy, recycle
from ict import data as D
from scripts.radar_price import DELAY_MIN, LO, HI, MODELS, registry_rows, scaled, trades

bars = D.load("1m")
orders = pd.read_parquet(D.PROCESSED_DIR / "ideas_orders_NQ.parquet")
cache = {d: trades(orders, bars, d) for d in (0, DELAY_MIN)}
reg = pd.read_csv("docs/radar/prop_firms.csv").fillna("")
months = pd.period_range(LO, pd.Timestamp(HI) - pd.Timedelta(days=1), freq="M")
rows = []
items = [({"automation": "full_bots"}, MODELS["topstep50"][0]), ({"automation": "alert_assisted"}, ("Topstep 50K, 3-min delay (ref)",) + MODELS["topstep50"][0][1:])]
items += [(r, m) for r in registry_rows(reg) if r["model_key"] != "topstep50" for m in MODELS[r["model_key"]]]
for r, (name, rules, risk) in items:
    d = DELAY_MIN if r["automation"] == "alert_assisted" else 0
    out = recycle(scaled(cache[d], risk / 900), rules, policy=Policy.LOCK_FIRST)
    tl = pd.DataFrame(out["timeline"])
    tl["m"] = pd.to_datetime(tl["ts"], utc=True).dt.tz_localize(None).dt.to_period("M")
    net = tl.groupby("m")["net"].last().reindex(months).ffill().fillna(0)
    cash = tl.groupby("m")["cash"].last().reindex(months).ffill().fillna(0)
    mnet, paid = net.diff().fillna(net.iloc[0]), cash.diff().fillna(cash.iloc[0]) > 0
    last24 = mnet[-24:]
    roll12 = net.diff(12).min()
    rows.append((name, d, out["net"] / len(months), float(mnet.median()), paid.mean(), float(mnet[paid].mean()) if paid.any() else 0.0,
                 float(last24.mean()), float(roll12)))
print(f"{'product':<44}{'delay':>6}{'avg $/mo':>10}{'median mo':>11}{'% months paid':>15}{'avg paid mo':>13}{'last 24 mo avg':>16}{'worst 12 mo':>13}")
for x in sorted(rows, key=lambda x: -x[2]):
    print(f"{x[0][:43]:<44}{x[1]:>6}{x[2]:>10,.0f}{x[3]:>11,.0f}{x[4]:>15.0%}{x[5]:>13,.0f}{x[6]:>16,.0f}{x[7]:>13,.0f}")

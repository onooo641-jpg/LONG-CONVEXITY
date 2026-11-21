"""Radar pricing step (docs/PREREG_RADAR_20261121.md, "Prop-firm sweep").

For every firm in docs/radar/prop_firms.csv whose `automation` is full_bots (or conditional / no_api variants) or
alert_assisted and that has a `model_key`: real trades and the coin-flip test (random sign, commission kept, 200 runs,
seed 1) on the friend's NQ orders 2016-01..2026-10. alert_assisted firms: every entry 3 minutes late
(PREREG_DELAY_20261121). Ranking, no pass/fail; flag "extra slot candidate" per the pre-registered reading.

    uv run python scripts/radar_price.py | tee docs/jx_runs/radar_price_20261121.txt
"""
from __future__ import annotations

import dataclasses
import sys

import numpy as np
import pandas as pd

from backtest.engine import BacktestConfig, simulate
from backtest.recycle import Policy, XFARules, recycle
from ict import data as D
from scripts.firms2_20261120 import BULENOX, TRADEDAY, worst_dip
from scripts.ftmo_futures_20261120 import GROWTH, PRO
from scripts.fundednext_20261120 import FN
from scripts.round3_20261120 import MFFU, TFD_CORE, TFD_PRO
from scripts.structure_scan_20261120 import lucidflex, topstep, tradeify_flex50

LO, HI = "2016-01-01", "2026-10-29"
DELAY_MIN = 3
# key -> [(product, rules, risk per trade)]. Risk rule from PREREG_ROUND3: min(0.45*loss limit, 0.875*daily limit).
MODELS = {
    "topstep50": [("Topstep 50K", topstep(50, "Standard", False), 900)],
    "lucidflex50": [("LucidFlex 50K", lucidflex(50), 900)],
    "mffu_rapid50": [("MFFU Rapid EOD 50K", MFFU, 900)],
    "tradeify_flex50": [("Tradeify Select Flex 50K", tradeify_flex50(), 900)],
    "tradeday": [("TradeDay $189", TRADEDAY, 900), ("TradeDay $85 (code)", dataclasses.replace(TRADEDAY, monthly=85, reset=85), 900)],
    "bulenox": [("Bulenox Momentum 50K", BULENOX, 900)],
    "fundednext_rapid": [("FundedNext Rapid Pro 50K", dataclasses.replace(FN, payout_cap=1000.0), 900)],
    "ftmo_growth": [("FTMO Futures Growth 50K", GROWTH, 900), ("FTMO Futures Pro 50K", PRO, 800)],
    "tfd_core": [("TFD Static Core", TFD_CORE, 700), ("TFD Static Pro", TFD_PRO, 1050)],
}
try:  # models added later from firms' own pages
    from scripts.radar_models import MODELS as EXTRA
    MODELS.update(EXTRA)
except ImportError:
    pass


def scaled(t, k):
    s = t.copy()
    for c in ("net_pnl", "gross_pnl"):
        s[c] = s[c] * k
    s["contracts"] = np.maximum(1, np.round(s["contracts"] * k)).astype(int)
    return s


def trades(orders, bars, delay):
    o = orders.copy()
    if delay:
        o["valid_from"] = o["valid_from"] + pd.Timedelta(minutes=delay)
        o = o[o["valid_from"] < o["expires_at"]]
    t = simulate(o, bars, BacktestConfig(risk_per_trade_usd=900))
    t = t[t["filled"]]
    t = t[(t.entry_ts >= pd.Timestamp(LO, tz="UTC")) & (t.entry_ts < pd.Timestamp(HI, tz="UTC"))]
    return t.sort_values("exit_ts").reset_index(drop=True)


def price(t, rules, risk):
    s = scaled(t, risk / 900)
    g, comm = s["gross_pnl"].to_numpy(), (s["gross_pnl"] - s["net_pnl"]).to_numpy()
    real = recycle(s, rules, policy=Policy.LOCK_FIRST)
    rng = np.random.default_rng(1)
    flips = np.array([recycle(s.assign(net_pnl=np.abs(g) * rng.choice([-1, 1], len(s)) - comm), rules,
                              policy=Policy.LOCK_FIRST)["net"] for _ in range(200)])
    return real["net"], worst_dip(real), float(np.median(flips)), float((flips > 0).mean())


def main() -> int:
    bars = D.load("1m")
    orders = pd.read_parquet(D.PROCESSED_DIR / "ideas_orders_NQ.parquet")
    reg = pd.read_csv("docs/radar/prop_firms.csv").fillna("")
    cache = {d: trades(orders, bars, d) for d in (0, DELAY_MIN)}
    ref = {d: price(cache[d], *MODELS["topstep50"][0][1:]) for d in cache}
    print(f"reference Topstep 50K: no delay real ${ref[0][0]:,.0f} dip ${ref[0][1]:,.0f} flip ${ref[0][2]:,.0f}; "
          f"{DELAY_MIN}-min delay real ${ref[DELAY_MIN][0]:,.0f} dip ${ref[DELAY_MIN][1]:,.0f} flip ${ref[DELAY_MIN][2]:,.0f}\n")
    rows = []
    for r in registry_rows(reg):
        for name, rules, risk in MODELS[r["model_key"]]:
            d = DELAY_MIN if r["automation"] == "alert_assisted" else 0
            real, dip, flip, prof = price(cache[d], rules, risk)
            rf = ref[d]
            flag = real >= 0.5 * rf[0] and flip >= 5000 and dip >= 1.5 * rf[1]
            rows.append((name, r["automation"], d, real, flip, prof, dip, flag))
            print(f"{name:<28} {r['automation']:<22} delay {d} min | real ${real:>9,.0f} | coin-flip median ${flip:>9,.0f} "
                  f"(profitable {prof:.0%}) | worst dip ${dip:>7,.0f} | {'EXTRA SLOT CANDIDATE' if flag else '-'}", flush=True)
    print("\nRANKING by coin-flip median")
    for x in sorted(rows, key=lambda x: -x[4]):
        print(f"  {x[0]:<28} flip ${x[4]:>9,.0f}  real ${x[3]:>9,.0f}  {'EXTRA SLOT CANDIDATE' if x[7] else ''}")
    return 0


def registry_rows(reg):
    for r in reg.to_dict("records"):
        if r["model_key"] and r["model_key"] in MODELS and r["automation"].split("_")[0] in ("full", "alert") \
                and r["automation"] != "full_bots_conditional":
            yield r


if __name__ == "__main__":
    sys.exit(main())

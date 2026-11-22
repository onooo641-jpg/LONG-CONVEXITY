"""Price products at checkout prices supplied by Jx (2026-11-22; labelled 'Jx checkout', not read by the radar).

    uv run python -m scripts.prop_price_jx_20261122 | tee docs/jx_runs/prop_price_jx_20261122.txt
"""
import dataclasses

import pandas as pd

from backtest.recycle import Policy
from ict import data as D
from scripts.radar_models2 import MODELS2
from scripts.radar_price import MODELS, price, trades

orders, bars = pd.read_parquet(D.PROCESSED_DIR / "ideas_orders_NQ.parquet"), D.load("1m")
T = trades(orders, bars, 0)
R = dataclasses.replace
lf, lf_risk = MODELS["lucidflex50"][0][1:]
ld, ld_risk = MODELS2["lucid_daily50"][1][0][1:]
ld = R(ld, payout_cap=float("inf"), payout_min=500.0)  # official rules (PROP_VERIFY section 2)
dte, dte_risk = MODELS["dt_eod50"][0][1:3]
s2f, s2f_risk = MODELS2["dt_s2f50"][1][0][1:]
s2f = R(s2f, payout_goal=(3500.0, 3000.0), payout_buffer=0.0)


def one(r, p, reset=None):
    """Purchase price from Jx; reset = the model's reset when the repo has one (LucidFlex $90), else the purchase price (assumed)."""
    return R(r, one_time_price=p, reset=p if reset is None else reset, monthly=0.0)


print(f"LucidFlex model as in repo: price {lf.one_time_price if lf.one_time_price is not None else str(lf.monthly) + '/mo'}, reset {lf.reset}")
ROWS = [("LucidFlex 50K DLL OFF, $165 list", one(lf, 165.0, lf.reset), lf_risk), ("LucidFlex 50K DLL OFF, $115.50 promo", one(lf, 115.5, lf.reset), lf_risk),
        ("LucidFlex 50K DLL ON*, $115 list", one(lf, 115.0, lf.reset), lf_risk), ("LucidFlex 50K DLL ON*, $80.50 promo", one(lf, 80.5, lf.reset), lf_risk),
        ("LucidDaily 50K EOD eval**, $122 list", one(ld, 122.0), ld_risk), ("LucidDaily 50K EOD eval**, $85.40 promo", one(ld, 85.4), ld_risk),
        ("LucidDaily 50K Intraday eval**, $94 list", one(ld, 94.0), ld_risk), ("LucidDaily 50K Intraday eval**, $65.80 promo", one(ld, 65.8), ld_risk),
        ("LucidDaily 50K EOD funded, $236 list", one(ld, 236.0), ld_risk), ("LucidDaily 50K EOD funded, $165.20 promo", one(ld, 165.2), ld_risk),
        ("DayTraders EOD 50K, $105 + $5 activation", one(dte, 105.0), dte_risk),
        ("DayTraders S2F 50K, $570 list", one(s2f, 570.0), s2f_risk), ("DayTraders S2F 50K, $342 promo", one(s2f, 342.0), s2f_risk)]
print("flag rule: real >= $22,180, coin flip >= $5,000, worst dip >= -$5,280 (Topstep 50K: $44,359 / $18,046 / -$3,520)\n")
for name, r, risk in ROWS:
    pol = Policy.IMMEDIATE if r.mll_locks_at is None else Policy.LOCK_FIRST
    real, dip, flip, prof = price(T, r, risk, pol)
    flag = real >= 22180 and flip >= 5000 and dip >= -5280
    print(f"{name:<46} | real ${real:>8,.0f} ({real / 44359:.0%} of Topstep) | coin flip ${flip:>7,.0f} ({prof:.0%}) | dip ${dip:>7,.0f} | "
          f"{'MEETS FLAG RULE' if flag else '-'}", flush=True)
print("\nResets: LucidFlex keeps the model's $90; other products assume reset = purchase price (not supplied).")
print("* DLL is a soft pause (not a breach) and its 50K amount is not published: modelled as no DLL (optimistic).")
print("** recycle.py works on closed-trade P&L, so intraday vs end-of-day drawdown is not distinguished (intraday versions are optimistic).")

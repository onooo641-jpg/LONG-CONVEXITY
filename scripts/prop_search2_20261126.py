"""Prop search 2, Stage A (docs/PREREG_PROP_SEARCH2_20261126.md): every modelled product the audit did not re-price, on the corrected
model: (i) loss limit on open P&L in real time (default) and (ii) end-of-day / closed P&L. Same qualification rule as the audit.

    uv run python -m scripts.prop_search2_20261126 | tee docs/jx_runs/prop_search2_20261126.txt
"""
import dataclasses as dc

import pandas as pd

from backtest.recycle import Policy
from ict import data as D
from scripts.radar_models2 import MODELS2
from scripts.radar_price import MODELS, price, trades

R = dc.replace


def all_rows(key):
    v = MODELS.get(key) or MODELS2[key][1]
    return [(x[0], x[1], x[2]) for x in v]


PRODUCTS = []
for key in ("ttp_instant50", "ttp_prime100", "ttp_prime150", "lucid_direct50", "tradeify_flex50", "ftmo_growth", "tfd_core",
            "blueberry_ascent50", "fundednext_rapid", "bulenox", "traders_launch"):
    PRODUCTS += all_rows(key)
for name, rules, risk in all_rows("dt_s2f50"):  # official targets (PROP_VERIFY section 4)
    PRODUCTS.append((name + " (official targets $3,500/$3,000)", R(rules, payout_goal=(3500.0, 3000.0), payout_buffer=0.0), risk))


def run():
    orders, bars = pd.read_parquet(D.PROCESSED_DIR / "ideas_orders_NQ.parquet"), D.load("1m")
    t = trades(orders, bars, 0)
    ts, ts_risk = MODELS["topstep50"][0][1:]
    ref_real, ref_dip, _, _ = price(t, ts, ts_risk, Policy.IMMEDIATE if ts.mll_locks_at is None else Policy.LOCK_FIRST)
    print(f"Benchmark Topstep 50K Standard (real-time model, bot): real ${ref_real:,.0f}, dip ${ref_dip:,.0f}")
    print(f"Bar: real >= ${0.5 * ref_real:,.0f}, coin flip >= $5,000, dip >= ${1.5 * ref_dip:,.0f}\n")
    n = {"rt": 0, "eod": 0}
    for name, rules, risk in PRODUCTS:
        pol = Policy.IMMEDIATE if rules.mll_locks_at is None else Policy.LOCK_FIRST
        out = []
        for tag, rr in (("rt", rules), ("eod", R(rules, realtime_mll=False, intraday_trail_funded=False))):
            real, dip, fmed, fpos = price(t, rr, risk, pol)
            ok = real >= 0.5 * ref_real and fmed >= 5000 and dip >= 1.5 * ref_dip
            n[tag] += ok
            out.append(f"{tag}: real ${real:>8,.0f} flip ${fmed:>8,.0f} ({fpos:.0%}) dip ${dip:>8,.0f} {'QUALIFIES' if ok else 'fails'}")
        print(f"  {name:<62} | {out[0]} | {out[1]}", flush=True)
    print(f"\nqualifying products: real-time model {n['rt']}, end-of-day model {n['eod']} (EOD counts only once a firm's own page confirms it)")


if __name__ == "__main__":
    run()

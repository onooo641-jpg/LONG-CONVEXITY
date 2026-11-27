"""Prop search 3, part 3 (docs/PREREG_PROP_SEARCH3_20261126.md): confirmation at Jx's prices (2026-11-27).

    uv run python -m scripts.prop_search3_p3_20261127 | tee docs/jx_runs/prop_search3_p3_20261127.txt
"""
import pandas as pd

from backtest.recycle import Policy
from ict import data as D
from scripts.prop_search3_20261126 import ffn_max, run_one
from scripts.prop_search3_p2_20261126 import dt_static, prep, starts
from scripts.radar_price import MODELS, price, trades


def main():
    orders, bars = pd.read_parquet(D.PROCESSED_DIR / "ideas_orders_NQ.parquet"), D.load("1m")
    nq = trades(orders, bars, 0)
    ts, ts_risk = MODELS["topstep50"][0][1:]
    ref_real, ref_dip, _, _ = price(nq, ts, ts_risk, Policy.LOCK_FIRST)
    print(f"Registered bar: real >= ${0.5 * ref_real:,.0f}, coin flip >= $5,000, dip >= ${1.5 * ref_dip:,.0f}\n")
    f50, d50 = ffn_max(50, 89.0, 0.0, 100.0)
    f100, d100 = ffn_max(100, 174.0, 0.0, 100.0)
    f150, d150 = ffn_max(150, 204.0, 0.0, 100.0)
    rows = [("DayTraders 100K Static $75 + $5", dt_static(100, 75.0), 900.0, None),
            ("DayTraders 150K Static $90 + $5", dt_static(150, 90.0), 900.0, None),
            ("FFN Std MAX 50K $89 (50% off), no activation", f50, 900.0, d50),
            ("FFN Std MAX 100K $174 (50% off), no activation", f100, 1620.0, d100),
            ("FFN Std MAX 150K $204 (50% off), no activation", f150, 2250.0, d150)]
    ok_rows = []
    for name, rules, risk, dll in rows:
        real, dip, fmed, fpos = run_one(nq, rules, risk, dll)
        ok = real >= 0.5 * ref_real and fmed >= 5000 and dip >= 1.5 * ref_dip
        print(f"  {name:<48} risk ${risk:>5,.0f} | real ${real:>8,.0f} ({real / 10.83:>6,.0f}/yr) | flip ${fmed:>8,.0f} ({fpos:.0%}) | "
              f"dip ${dip:>8,.0f} | {'QUALIFIES' if ok else 'fails'}", flush=True)
        if ok:
            ok_rows.append((name, rules, risk, dll))
    print("\nMONEY NEEDED TO START (118 monthly starts 2016-01..2025-10), qualifying rows")
    for name, rules, risk, dll in ok_rows:
        d = starts(prep(nq, risk, dll), rules)
        print(f"  {name:<48} median ${d.worst.median():>7,.0f} | 1 in 10 ${d.worst.quantile(.10):>7,.0f} | worst ${d.worst.min():>7,.0f} | "
              f"first payout ${d['first'].median():>6,.0f} after {d.days.median():>4.0f} days | 12-month net ${d.net12.median():>7,.0f} "
              f"({(d.net12 < 0).mean():.0%} losing)", flush=True)


if __name__ == "__main__":
    main()

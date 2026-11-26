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


def addendum_prices():
    """Addendum A1 (2026-11-26): the two Stage A qualifiers re-priced at third-party prices (checkout pages unreadable from here) with the
    daily loss limits their pages state. DayTraders: hitting the DLL pauses the account until the next session (modelled as a per-trade
    loss cap, as the audit did for DayTraders EOD). LucidDirect 50K: DLL amount not on the stored pages -> $1,200 assumed (as LucidFlex)
    and no-DLL shown. Lucid rows also with CrossTrade $49/month (needed to run the bot on Lucid)."""
    import numpy as np
    orders, bars = pd.read_parquet(D.PROCESSED_DIR / "ideas_orders_NQ.parquet"), D.load("1m")
    t0 = trades(orders, bars, 0)
    ts, ts_risk = MODELS["topstep50"][0][1:]
    ref_real, ref_dip, _, _ = price(t0, ts, ts_risk, Policy.IMMEDIATE if ts.mll_locks_at is None else Policy.LOCK_FIRST)
    s2f, s2f_risk = MODELS2["dt_s2f50"][1][0][1:]
    s2f = R(s2f, payout_goal=(3500.0, 3000.0), payout_buffer=0.0)
    ldr, ldr_risk = MODELS2["lucid_direct50"][1][0][1:]
    rows = []
    for p_ in (342.0, 570.0):
        rows.append((f"DayTraders S2F 50K ${p_:.0f}, DLL $1,250 (pause)", R(s2f, one_time_price=p_, reset=p_), s2f_risk, 1250.0))
    for p_ in (360.5, 520.0):
        for dll in (None, 1200.0):
            for api in (0.0, 49.0):
                rows.append((f"LucidDirect 50K ${p_:.2f}, DLL {'none' if dll is None else '$1,200'}, CrossTrade ${api:.0f}/mo",
                             R(ldr, one_time_price=p_, reset=p_, api_monthly=api), ldr_risk, dll))
    print(f"\nADDENDUM A1 - third-party prices and stated daily loss limits. Bar: real >= ${0.5 * ref_real:,.0f}, flip >= $5,000, "
          f"dip >= ${1.5 * ref_dip:,.0f}")
    for name, rules, risk, dll in rows:
        cap = None if dll is None else dll * 900 / risk  # cap in the units of the 900-risk trades before price() rescales
        t = t0 if cap is None else t0.assign(net_pnl=np.maximum(t0["net_pnl"].to_numpy(), -cap))
        pol = Policy.IMMEDIATE if rules.mll_locks_at is None else Policy.LOCK_FIRST
        out = []
        for tag, rr in (("rt", rules), ("eod", R(rules, realtime_mll=False, intraday_trail_funded=False))):
            real, dip, fmed, fpos = price(t, rr, risk, pol)
            ok = real >= 0.5 * ref_real and fmed >= 5000 and dip >= 1.5 * ref_dip
            out.append(f"{tag}: real ${real:>8,.0f} flip ${fmed:>8,.0f} ({fpos:.0%}) dip ${dip:>8,.0f} {'QUALIFIES' if ok else 'fails'}")
        print(f"  {name:<62} | {out[0]} | {out[1]}", flush=True)


def stage_c1():
    """Stage C1: other sizes of the qualifying firms (models from scripts/structure_scan_20261120.py), risk 0.45 x MLL."""
    import contextlib
    import io
    with contextlib.redirect_stdout(io.StringIO()):
        from scripts.structure_scan_20261120 import lucidflex, topstep
    orders, bars = pd.read_parquet(D.PROCESSED_DIR / "ideas_orders_NQ.parquet"), D.load("1m")
    t0 = trades(orders, bars, 0)
    ts, ts_risk = MODELS["topstep50"][0][1:]
    ref_real, ref_dip, _, _ = price(t0, ts, ts_risk, Policy.IMMEDIATE if ts.mll_locks_at is None else Policy.LOCK_FIRST)
    rows = []
    for size, mll in ((100, 3000), (150, 4500)):
        std = R(topstep(size, "Standard"), combine_consistency=0.55)
        con = R(topstep(size, "Consistency"), combine_consistency=0.55, consistency_days=3, winning_days_required=0)
        rows += [(f"Topstep {size}K Standard (real-time)", std, 0.45 * mll), (f"Topstep {size}K Consistency (real-time)", con, 0.45 * mll)]
    for size, mll in ((25, 1000), (100, 3000), (150, 4500)):
        rows.append((f"LucidFlex {size}K (EOD, no DLL; dated price)", R(lucidflex(size), realtime_mll=False), 0.45 * mll))
    print(f"\nSTAGE C1 - other sizes. Bar: real >= ${0.5 * ref_real:,.0f}, flip >= $5,000, dip >= ${1.5 * ref_dip:,.0f}")
    for name, rules, risk in rows:
        pol = Policy.IMMEDIATE if rules.mll_locks_at is None else Policy.LOCK_FIRST
        real, dip, fmed, fpos = price(t0, rules, risk, pol)
        ok = real >= 0.5 * ref_real and fmed >= 5000 and dip >= 1.5 * ref_dip
        print(f"  {name:<46} risk ${risk:>5,.0f} | real ${real:>8,.0f} flip ${fmed:>8,.0f} ({fpos:.0%}) dip ${dip:>8,.0f} "
              f"{'QUALIFIES' if ok else 'fails'}", flush=True)


if __name__ == "__main__":
    import sys
    if "--c1" in sys.argv:
        stage_c1()
    else:
        run()
        addendum_prices()
        stage_c1()

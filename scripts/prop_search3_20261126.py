"""Prop search 3 (docs/PREREG_PROP_SEARCH3_20261126.md): (B) bigger accounts with the same $900 risk, (C/D) Funded Futures Network
Standard MAX (EOD: open losses do not breach, per its rules article 3.1), (E) break-even prices, (F) size-scaled dip reading.

    uv run python -m scripts.prop_search3_20261126 | tee docs/jx_runs/prop_search3_20261126.txt
"""
import contextlib
import dataclasses as dc
import io

import numpy as np
import pandas as pd

from backtest.recycle import Policy, XFARules
from ict import data as D
from scripts.prop_search2_c2_20261126 import challenge, static_combine
from scripts.prop_search2_d_20261126 import COMMON
from scripts.radar_models2 import MODELS2
from scripts.radar_price import MODELS, flip, price, trades

with contextlib.redirect_stdout(io.StringIO()):
    from scripts.structure_scan_20261120 import lucidflex, topstep

R = dc.replace
B = XFARules()


def ffn_max(size, price_, activation, reset):
    """FFN Standard MAX (rules articles 2.3, 3.1, 3.2, 4.2, 5.2, 5.3): EOD trailing, breach judged at the session close (open losses
    not caught), locks at buffer + $100; DLL soft (session lockout); withdraw only above the buffer, >= $500, per-account cap 1-3."""
    t, dd, dll, micros, cap = {50: (3000, 2000, 1250, 40, 1000), 100: (6000, 3600, 2500, 100, 1500), 150: (9000, 5000, 3750, 150, 1750)}[size]
    r = R(B, profit_target=t, loss_limit=dd, funded_loss_limit=dd, mll_locks_at=dd + 100, lock_level=100.0, combine_max_contracts=micros,
          funded_scaling=False, combine_consistency=None, consistency_target=0.40, consistency_days=1, payout_needs_both=False,
          winning_days_required=0, payout_buffer=float(dd), payout_cap=float(cap), payout_min=500.0, profit_split=0.80,
          profit_since_payout_required=True, one_time_price=price_, reset=reset, activation=activation, monthly=0.0, api_monthly=0.0,
          realtime_mll=False, realtime_eval=False)
    return r, dll


def verdicts(real, fmed, dip, ref_real, ref_dip, mll):
    reg = real >= 0.5 * ref_real and fmed >= 5000 and dip >= 1.5 * ref_dip
    scaled = real >= 0.5 * ref_real and fmed >= 5000 and dip >= 1.5 * ref_dip * (mll / 2000.0)
    return reg, scaled


def run_one(t0, rules, risk, dll_usd=None):
    t = t0
    if dll_usd:
        cap = dll_usd * 900.0 / risk
        t = t0.assign(net_pnl=np.maximum(t0["net_pnl"].to_numpy(), -cap))
    pol = Policy.IMMEDIATE if rules.mll_locks_at is None else Policy.LOCK_FIRST
    return price(t, rules, risk, pol)


def main():
    orders, bars = pd.read_parquet(D.PROCESSED_DIR / "ideas_orders_NQ.parquet"), D.load("1m")
    t0 = trades(orders, bars, 0)
    ts, ts_risk = MODELS["topstep50"][0][1:]
    ref_real, ref_dip, _, _ = price(t0, ts, ts_risk, Policy.LOCK_FIRST)
    print(f"Registered bar: real >= ${0.5 * ref_real:,.0f}, coin flip >= $5,000, dip >= ${1.5 * ref_dip:,.0f}. "
          f"(F) size-scaled reading: dip limit x (MLL / $2,000).\n")

    def show(name, rules, risk, mll, dll=None):
        real, dip, fmed, fpos = run_one(t0, rules, risk, dll)
        reg, sc = verdicts(real, fmed, dip, ref_real, ref_dip, mll)
        print(f"  {name:<58} risk ${risk:>5,.0f} | real ${real:>8,.0f} | flip ${fmed:>8,.0f} ({fpos:.0%}) | dip ${dip:>8,.0f} | "
              f"registered {'QUALIFIES' if reg else 'fails'} | size-scaled {'QUALIFIES' if sc else 'fails'}", flush=True)
        return reg, sc

    print("(C/D) FUNDED FUTURES NETWORK Standard MAX (EOD: open losses not caught; DLL soft)")
    for label, p_, act, rst in (("list $178 + $120 activation, reset $100", 178.0, 120.0, 100.0),
                                ("promo $53.40, activation waived, reset $100", 53.4, 0.0, 100.0)):
        for size in (50, 100, 150):
            r, dll = ffn_max(size, p_ * {50: 1, 100: 348 / 178, 150: 408 / 178}[size] if size != 50 else p_, act, rst)
            dd = r.loss_limit
            for risk in ((900.0,) if size == 50 else (900.0, 0.45 * dd)):
                show(f"FFN Std MAX {size}K, {label}", r, risk, dd, dll)

    print("\n(B) BIGGER ACCOUNTS: same $900 risk (and 0.45 x MLL for comparison)")
    rows = []
    for size, mll in ((100, 3000), (150, 4500)):
        rows += [(f"Topstep {size}K Standard", R(topstep(size, "Standard"), combine_consistency=0.55), mll, None),
                 (f"Topstep {size}K Consistency", R(topstep(size, "Consistency"), combine_consistency=0.55, consistency_days=3,
                                                     winning_days_required=0), mll, None),
                 (f"LucidFlex {size}K (EOD)", R(lucidflex(size), realtime_mll=False), mll, None)]
    for size in (100, 150):
        for path in ("Standard", "Consistency"):
            r, _ = static_combine(ts, size, path)
            rows.append((f"Topstep {size}K Static, {path}", r, r.loss_limit, r.loss_limit / 2))
    for key in ("ttp_prime100", "ttp_prime150"):
        name, rr, _ = MODELS2[key][1][0] if key in MODELS2 else MODELS[key][0]
        rows.append((name, rr, rr.loss_limit, None))
    dt_static = {100: (5750, 1500, 80), 150: (6750, 1750, 80)}
    for size, (tgt, dd, micros) in dt_static.items():
        rr = R(B, profit_target=tgt, loss_limit=dd, funded_loss_limit=dd, static_dd=True, mll_locks_at=None, lock_level=-float(dd),
               combine_max_contracts=micros, one_time_price=55.0, reset=55.0, **{**COMMON, "payout_cap": {100: 3000.0, 150: 3500.0}[size],
                                                                                   "winning_day_min": 300.0, "activation": 0.0})
        rows.append((f"DayTraders {size}K Static (price unknown: $55 floor, FLAGGED)", rr, dd, None))
    rr = R(B, profit_target=8500, loss_limit=4500, funded_loss_limit=4500, mll_locks_at=4500, lock_level=0.0, combine_max_contracts=200,
           intraday_trail_funded=True, intraday_trail_eval=True, one_time_price=75.0, reset=75.0,
           **{**COMMON, "payout_cap": 3500.0, "winning_day_min": 300.0})
    rows.append(("DayTraders 150K Trail (price unknown: $75 floor, FLAGGED)", rr, 4500, None))
    for name, rules, mll, dll in rows:
        for risk in (900.0, 0.45 * mll):
            show(name, rules, risk, mll, dll)

    print("\n(E) BREAK-EVEN PRICES (highest one-time price meeting the registered bar; $1 steps)")
    s2f, s2f_risk = MODELS2["dt_s2f50"][1][0][1:]
    ldr, ldr_risk = MODELS2["lucid_direct50"][1][0][1:]
    tti, tti_risk = MODELS2["ttp_instant50"][1][0][1:]
    from scripts.prop_search2_d_20261126 import DT_TRAIL50
    cands = [("DayTraders S2F 50K (DLL $1,250)", R(s2f, payout_goal=(3500.0, 3000.0), payout_buffer=0.0), s2f_risk, 1250.0, 342.0),
             ("LucidDirect 50K (EOD)", R(ldr, realtime_mll=False), ldr_risk, None, 360.5),
             ("TTP Instant 50K (real-time)", tti, tti_risk, None, 499.0),
             ("DayTraders 50K Trail", DT_TRAIL50, 1125.0, None, 70.0),
             ("LucidFlex 25K (EOD)", R(lucidflex(25), realtime_mll=False), 450.0, None, 100.0)]
    for name, rules, risk, dll, now in cands:
        def ok(p):
            rr = R(rules, one_time_price=float(p), reset=float(p))
            real, dip, fmed, _ = run_one(t0, rr, risk, dll)
            return verdicts(real, fmed, dip, ref_real, ref_dip, rules.loss_limit)[0]
        if not ok(0):
            print(f"  {name:<40} no price works (fails even at $0); current ${now:,.2f}", flush=True)
            continue
        lo, hi = 0, 2000
        if ok(hi):
            print(f"  {name:<40} qualifies at every price up to $2,000", flush=True)
            continue
        while hi - lo > 1:
            mid = (lo + hi) // 2
            lo, hi = (mid, hi) if ok(mid) else (lo, mid)
        print(f"  {name:<40} break-even ${lo:,} (current ${now:,.2f}: {'QUALIFIES' if now <= lo else 'needs a promo'})", flush=True)
    g, comm = t0["gross_pnl"].to_numpy(), (t0["gross_pnl"] - t0["net_pnl"]).to_numpy()

    def ch_ok(p):
        real, dip = challenge(t0, float(p), 3000, 1000, 10, 3000)
        rng = np.random.default_rng(1)
        fl = np.array([challenge(flip(t0, g, comm, rng.choice([-1, 1], len(t0))), float(p), 3000, 1000, 10, 3000)[0] for _ in range(200)])
        return real >= 0.5 * ref_real and float(np.median(fl)) >= 5000 and dip >= 1.5 * ref_dip
    print(f"  {'Topstep $3K Challenge':<40} {'qualifies at $0' if ch_ok(0) else 'no price works (fails even at $0)'}; current $49", flush=True)


if __name__ == "__main__":
    main()

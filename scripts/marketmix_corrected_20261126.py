"""Prop search 3 (A): market mix on the corrected model (docs/PREREG_PROP_SEARCH3_20261126.md). Reuses the trade builder and the
anti-hedge filter of scripts/marketmix_20261120.py. MFFU is dropped (does not accept Malaysian residents); Lucid uses its own EOD rule.

    uv run python -m scripts.marketmix_corrected_20261126 | tee docs/jx_runs/marketmix_corrected_20261126.txt
"""
from __future__ import annotations

import contextlib
import dataclasses as dc
import io
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, "scripts")
from backtest.recycle import Policy, XFARules, recycle  # noqa: E402
from scripts.firms2_20261120 import worst_dip  # noqa: E402
from scripts.marketmix_20261120 import EXPECT, no_cross_hedge, trades  # noqa: E402
from scripts.portfolio2_20261120 import platform_costs  # noqa: E402
from scripts.portfolio_20261120 import daily_from_recycle, stats  # noqa: E402
from scripts.radar_price import flip  # noqa: E402

with contextlib.redirect_stdout(io.StringIO()):
    from scripts.manual_my_20261123 import m

R = dc.replace
ts, _ = m("topstep50")
ld, _ = m("lucid_daily50")
lf, _ = m("lucidflex50")
TS_CONS = R(ts, combine_consistency=0.55, consistency_target=0.4, consistency_days=3, payout_cap=3000.0, winning_days_required=0)
LF = R(lf, one_time_price=80.5, reset=80.0, monthly=0.0, realtime_mll=False)  # LucidFlex 50K DLL ON, EOD (Lucid's page)
LD = R(ld, payout_cap=float("inf"), payout_min=500.0, one_time_price=85.4, reset=85.4, realtime_eval=False, intraday_trail_funded=True)
PRODUCTS = {"Topstep 50K Consistency": (TS_CONS, None), "LucidFlex 50K DLL ON (EOD)": (LF, 1200.0), "LucidDaily $85.40": (LD, None)}


def capped(t, dll):
    return t if not dll else t.assign(net_pnl=np.maximum(t["net_pnl"].to_numpy(), -dll))


def single(t, rules, dll):
    t = capped(t, dll)
    pol = Policy.IMMEDIATE if rules.mll_locks_at is None else Policy.LOCK_FIRST
    real = recycle(t, rules, policy=pol)
    g, comm = t["gross_pnl"].to_numpy(), (t["gross_pnl"] - t["net_pnl"]).to_numpy()
    rng = np.random.default_rng(1)
    fl = np.array([recycle(flip(t, g, comm, rng.choice([-1, 1], len(t))), rules, policy=pol)["net"] for _ in range(200)])
    return real["net"], worst_dip(real), float(np.median(fl)), float((fl > 0).mean())


def main() -> int:
    tr = {mk: trades(mk) for mk in ("NQ", "ES", "YM")}
    for mk, t in tr.items():
        got = recycle(t, R(XFARules(), realtime_mll=False), policy=Policy.LOCK_FIRST)["net"]
        ok = abs(got / EXPECT[mk] - 1) <= 0.01
        print(f"check {mk} (closed-P&L model): ${got:,.0f} vs earlier ${EXPECT[mk]:,.0f} -> {'OK' if ok else 'MISMATCH'}")
        if not ok:
            print("stopping: regenerated trades do not reproduce the earlier figure (pre-registered rule)")
            return 1
    ref_real, ref_dip, _, _ = single(tr["NQ"], XFARules(), None)
    print(f"\nBar (Topstep 50K Standard, NQ, real-time): real >= ${0.5 * ref_real:,.0f}, flip >= $5,000, dip >= ${1.5 * ref_dip:,.0f}")
    print("\n(A1) SINGLE ACCOUNTS by market, corrected model")
    for name, (rules, dll) in PRODUCTS.items():
        for mk in ("NQ", "ES", "YM"):
            real, dip, fmed, fpos = single(tr[mk], rules, dll)
            ok = real >= 0.5 * ref_real and fmed >= 5000 and dip >= 1.5 * ref_dip
            print(f"  {name:<28} {mk} | real ${real:>8,.0f} | flip ${fmed:>8,.0f} ({fpos:.0%}) | dip ${dip:>8,.0f} | "
                  f"{'QUALIFIES' if ok else 'fails'}", flush=True)

    print("\n(A2) PORTFOLIOS with the anti-hedge filter (mixed portfolios), corrected model")
    raw = tr
    trf, skipped = no_cross_hedge(tr)
    print("  compliance filter skipped " + ", ".join(f"{k} {n}" for k, n in skipped.items()) + " trades")
    firms = {"Topstep": (R(TS_CONS, api_monthly=0.0), None), "Lucid": (R(LF, api_monthly=0.0), 1200.0)}
    d = {(f, mk): daily_from_recycle(capped(trf[mk], dll), rules)[0] for f, (rules, dll) in firms.items() for mk in trf}
    d_raw = {(f, "NQ"): daily_from_recycle(capped(raw["NQ"], dll), rules)[0] for f, (rules, dll) in firms.items()}
    corr = pd.DataFrame({mk: d[("Topstep", mk)].resample("ME").last().diff() for mk in trf}).corr()
    print("  monthly P&L correlation, one Topstep account per market:\n" + corr.to_string(float_format=lambda x: f"{x:.2f}"))
    ports = {"T5-NQ": {("Topstep", "NQ"): 5}, "T5-mix": {("Topstep", "NQ"): 3, ("Topstep", "ES"): 1, ("Topstep", "YM"): 1},
             "L5-NQ": {("Lucid", "NQ"): 5}, "L5-mix": {("Lucid", "NQ"): 3, ("Lucid", "ES"): 1, ("Lucid", "YM"): 1},
             "TL-NQ": {("Topstep", "NQ"): 5, ("Lucid", "NQ"): 5},
             "TL-mix": {("Topstep", "NQ"): 3, ("Topstep", "ES"): 1, ("Topstep", "YM"): 1, ("Lucid", "NQ"): 3, ("Lucid", "ES"): 1,
                        ("Lucid", "YM"): 1}}
    res = {}
    for name, w in ports.items():
        src = d_raw if {mk for _, mk in w} == {"NQ"} else d
        s = sum(n * src[k] for k, n in w.items()) - platform_costs({f for f, _ in w})
        stats(name, s)
        peak = s.cummax().clip(lower=0)
        res[name] = (s.iloc[-1], max(-(s - peak).min(), -min(0.0, s.min())))
    for a, b in (("T5-NQ", "T5-mix"), ("L5-NQ", "L5-mix"), ("TL-NQ", "TL-mix")):
        (na, ca), (nb, cb) = res[a], res[b]
        better = (nb / cb) / (na / ca) - 1
        verdict = "WORTH DOING" if better >= 0.15 and nb >= 0.75 * na else "not worth it"
        print(f"  {b} vs {a}: net ${nb:,.0f} vs ${na:,.0f} ({nb / na - 1:+.1%}), cash on hand ${cb:,.0f} vs ${ca:,.0f} ({cb / ca - 1:+.1%}), "
              f"net per $ of cash {better:+.1%} -> {verdict} (pre-registered rule)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

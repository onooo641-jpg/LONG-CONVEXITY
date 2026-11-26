"""Prop search 3, part 2 (docs/PREREG_PROP_SEARCH3_20261126.md): money needed to start for the new qualifiers, ES/YM on the new firms,
$3K Challenge break-even.

    uv run python -m scripts.prop_search3_p2_20261126 | tee docs/jx_runs/prop_search3_p2_20261126.txt
"""
import contextlib
import dataclasses as dc
import io
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, "scripts")
from backtest.recycle import Policy, XFARules, recycle  # noqa: E402
from ict import data as D  # noqa: E402
from scripts.marketmix_20261120 import trades as mkt_trades  # noqa: E402
from scripts.prop_search2_c2_20261126 import challenge, static_combine  # noqa: E402
from scripts.prop_search2_d_20261126 import COMMON  # noqa: E402
from scripts.prop_search3_20261126 import ffn_max, run_one  # noqa: E402
from scripts.radar_price import MODELS, flip, price, scaled, trades  # noqa: E402

with contextlib.redirect_stdout(io.StringIO()):
    from scripts.manual_my_20261123 import m

R = dc.replace
B = XFARules()


def pol(rules):
    return Policy.IMMEDIATE if rules.mll_locks_at is None else Policy.LOCK_FIRST


def prep(t, risk, dll):
    s = scaled(t, risk / 900.0)
    return s if not dll else s.assign(net_pnl=np.maximum(s["net_pnl"].to_numpy(), -dll))


def starts(t, rules):
    entry = pd.DatetimeIndex(t["entry_ts"])
    rows, s0 = [], pd.Timestamp("2016-01-01", tz=entry.tz)
    while s0 <= pd.Timestamp("2025-10-01", tz=entry.tz):
        ch = t[entry >= s0].reset_index(drop=True)
        tl = pd.DataFrame(recycle(ch, rules, policy=pol(rules))["timeline"])
        net = np.concatenate([[0.0], tl["net"].to_numpy()])
        pay = tl[tl.event == "payout"]
        t0 = ch["entry_ts"].iloc[0]
        y1 = tl[pd.to_datetime(tl.ts) < t0 + pd.DateOffset(months=12)]
        rows.append(dict(worst=net.min(), days=(pay["ts"].iloc[0] - t0).days if len(pay) else np.nan,
                         first=float(pay["cash"].iloc[0]) if len(pay) else np.nan, net12=float(y1["net"].iloc[-1]) if len(y1) else 0.0))
        s0 += pd.DateOffset(months=1)
    return pd.DataFrame(rows)


def dt_static(size, price_):
    tgt, dd, micros, cap = {100: (5750, 1500, 80, 3000.0), 150: (6750, 1750, 80, 3500.0)}[size]
    return R(B, profit_target=tgt, loss_limit=dd, funded_loss_limit=dd, static_dd=True, mll_locks_at=None, lock_level=-float(dd),
             combine_max_contracts=micros, one_time_price=price_, reset=price_,
             **{**COMMON, "payout_cap": cap, "winning_day_min": 300.0, "activation": 5.0})


def main():
    orders, bars = pd.read_parquet(D.PROCESSED_DIR / "ideas_orders_NQ.parquet"), D.load("1m")
    nq = trades(orders, bars, 0)
    es, ym = mkt_trades("ES"), mkt_trades("YM")
    ts, ts_risk = MODELS["topstep50"][0][1:]
    ref_real, ref_dip, _, _ = price(nq, ts, ts_risk, Policy.LOCK_FIRST)
    print(f"Registered bar: real >= ${0.5 * ref_real:,.0f}, coin flip >= $5,000, dip >= ${1.5 * ref_dip:,.0f}\n")
    lf, _ = m("lucidflex50")
    LF = R(lf, one_time_price=80.5, reset=80.0, monthly=0.0, realtime_mll=False)
    f50, d50 = ffn_max(50, 53.4, 0.0, 100.0)
    f100, d100 = ffn_max(100, 104.4, 0.0, 100.0)
    f150, d150 = ffn_max(150, 122.4, 0.0, 100.0)
    tsc150, _ = static_combine(ts, 150, "Consistency")
    prods = [("LucidFlex 50K DLL ON, NQ (reference)", LF, 900.0, 1200.0, nq),
             ("LucidFlex 50K DLL ON, ES", LF, 900.0, 1200.0, es),
             ("FFN Std MAX 50K promo $53.40", f50, 900.0, d50, nq),
             ("FFN Std MAX 100K promo $104.40, risk $1,620", f100, 1620.0, d100, nq),
             ("FFN Std MAX 150K promo $122.40, risk $2,250", f150, 2250.0, d150, nq),
             ("DayTraders 100K Static at $90 (placeholder)", dt_static(100, 90.0), 900.0, None, nq),
             ("DayTraders 150K Static at $93 (placeholder)", dt_static(150, 93.0), 900.0, None, nq),
             ("Topstep 150K Static Consistency (option), risk $2,700", tsc150, 2700.0, 3000.0, nq)]
    print("1. MONEY NEEDED TO START (118 monthly starts 2016-01..2025-10)")
    for name, rules, risk, dll, t in prods:
        d = starts(prep(t, risk, dll), rules)
        print(f"  {name:<56} median ${d.worst.median():>7,.0f} | 1 in 10 ${d.worst.quantile(.10):>7,.0f} | worst ${d.worst.min():>7,.0f} | "
              f"first payout ${d['first'].median():>6,.0f} after {d.days.median():>4.0f} days | 12-month net ${d.net12.median():>7,.0f} "
              f"({(d.net12 < 0).mean():.0%} losing)", flush=True)

    print("\n2. ES AND YM ON THE NEW FIRMS (single accounts, registered bar)")
    for name, rules, risk, dll, _ in prods[2:]:
        for mk, t in (("ES", es), ("YM", ym)):
            real, dip, fmed, fpos = run_one(t, rules, risk, dll)
            ok = real >= 0.5 * ref_real and fmed >= 5000 and dip >= 1.5 * ref_dip
            print(f"  {name:<56} {mk} | real ${real:>8,.0f} | flip ${fmed:>8,.0f} ({fpos:.0%}) | dip ${dip:>8,.0f} | "
                  f"{'QUALIFIES' if ok else 'fails'}", flush=True)

    print("\n3. $3K CHALLENGE BREAK-EVEN PRICE")
    g, comm = nq["gross_pnl"].to_numpy(), (nq["gross_pnl"] - nq["net_pnl"]).to_numpy()

    def ok(p):
        real, dip = challenge(nq, float(p), 3000, 1000, 10, 3000)
        rng = np.random.default_rng(1)
        fl = np.array([challenge(flip(nq, g, comm, rng.choice([-1, 1], len(nq))), float(p), 3000, 1000, 10, 3000)[0] for _ in range(200)])
        return real >= 0.5 * ref_real and float(np.median(fl)) >= 5000 and dip >= 1.5 * ref_dip
    lo, hi = 0, 500
    while hi - lo > 1:
        mid = (lo + hi) // 2
        lo, hi = (mid, hi) if ok(mid) else (lo, mid)
    print(f"  Topstep $3K Challenge: break-even ${lo} (price $49: {'QUALIFIES' if 49 <= lo else 'fails'})")


if __name__ == "__main__":
    main()

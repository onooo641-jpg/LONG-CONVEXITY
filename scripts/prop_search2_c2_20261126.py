"""Prop search 2, Stage C2 (docs/PREREG_PROP_SEARCH2_20261126.md): Topstep Labs products with official parameters: static-drawdown
combines (25K/50K/100K/150K x Standard/Consistency), 50K Daily Payouts+ (EOD and Static), and the two-round Challenges ($1.5K/$3K/$6K).

    uv run python -m scripts.prop_search2_c2_20261126 | tee docs/jx_runs/prop_search2_c2_20261126.txt
"""
import dataclasses as dc

import numpy as np
import pandas as pd

from backtest.recycle import Policy
from ict import data as D
from scripts.radar_price import MODELS, flip, price, trades

R = dc.replace
DLL_CAP_BASE = 1000.0  # DLL = MLL/2 and risk = 0.45 x MLL  ->  DLL in $900-risk units = $1,000 for every size


def static_combine(ts, size, path):
    t, mll, micros, p, cap, mult = {25: (2000, 1000, 20, 75.0, 4000, 1), 50: (4000, 2000, 40, 149.0, 8000, 1),
                                    100: (8000, 4000, 100, 199.0, 10000, 2), 150: (12000, 6000, 150, 279.0, 12000, 3)}[size]
    r = R(ts, profit_target=t, loss_limit=mll, funded_loss_limit=mll, static_dd=True, mll_locks_at=None, lock_level=0.0,
          combine_max_contracts=micros, combine_consistency=0.55, payout_cap=cap, one_time_price=p, reset=p, monthly=0.0,
          activation=0.0, funded_scaling=size != 25, scaling_mult=mult)
    if path == "Consistency":
        r = R(r, consistency_target=0.40, consistency_days=3, winning_days_required=0)
    return r, 0.45 * mll


def challenge(t, price_, target, mll, cap, payout):
    """Two rounds from $0: reach +target before the worst open P&L touches -mll (static). Pass both -> fixed payout, account closes,
    buy another. Returns net and the cumulative-net timeline."""
    k = np.minimum(1.0, cap / np.maximum(t["contracts"].to_numpy(), 1))
    pnl, mae = t["net_pnl"].to_numpy() * k, t["mae_usd"].to_numpy() * k
    net, bal, rnd, curve = -price_, 0.0, 1, [-price_]
    for x, m in zip(pnl, mae):
        if bal - m <= -mll:
            net -= price_
            bal, rnd = 0.0, 1
        else:
            bal += x
            if bal <= -mll:
                net -= price_
                bal, rnd = 0.0, 1
            elif bal >= target:
                if rnd == 1:
                    bal, rnd = 0.0, 2
                else:
                    net += payout - price_
                    bal, rnd = 0.0, 1
        curve.append(net)
    c = np.array(curve)
    return net, float((c - np.maximum.accumulate(np.maximum(c, 0))).min())


def main():
    orders, bars = pd.read_parquet(D.PROCESSED_DIR / "ideas_orders_NQ.parquet"), D.load("1m")
    t0 = trades(orders, bars, 0)
    ts, ts_risk = MODELS["topstep50"][0][1:]
    ref_real, ref_dip, _, _ = price(t0, ts, ts_risk, Policy.LOCK_FIRST)
    bar = (0.5 * ref_real, 5000.0, 1.5 * ref_dip)
    print(f"Benchmark Topstep 50K Standard (real-time, bot): real ${ref_real:,.0f}, dip ${ref_dip:,.0f}")
    print(f"Bar: real >= ${bar[0]:,.0f}, coin flip >= $5,000, dip >= ${bar[2]:,.0f}\n")
    tcap = t0.assign(net_pnl=np.maximum(t0["net_pnl"].to_numpy(), -DLL_CAP_BASE))
    rows = []
    for size in (25, 50, 100, 150):
        for path in ("Standard", "Consistency"):
            r, risk = static_combine(ts, size, path)
            rows.append((f"Topstep {size}K Static, {path}", r, risk))
    dp_eod = R(ts, profit_target=3000, combine_max_contracts=50, combine_consistency=0.55, payout_cap=4000, one_time_price=119.0,
               reset=119.0, monthly=0.0, activation=0.0)
    dp_static = R(static_combine(ts, 50, "Standard")[0], combine_max_contracts=50, one_time_price=149.0, reset=149.0)
    rows += [("Topstep 50K Daily Payouts+ EOD (5-winning-day path)", dp_eod, 900.0),
             ("Topstep 50K Daily Payouts+ Static (5-winning-day path)", dp_static, 900.0)]
    n_ok = 0
    print("STATIC COMBINES and DAILY PAYOUTS+ (real-time model, DLL as a per-trade cap)")
    for name, rules, risk in rows:
        pol = Policy.IMMEDIATE if rules.mll_locks_at is None else Policy.LOCK_FIRST
        real, dip, fmed, fpos = price(tcap, rules, risk, pol)
        ok = real >= bar[0] and fmed >= bar[1] and dip >= bar[2]
        n_ok += ok
        print(f"  {name:<56} risk ${risk:>5,.0f} | real ${real:>8,.0f} | coin flip ${fmed:>8,.0f} ({fpos:.0%}) | dip ${dip:>8,.0f} | "
              f"{'QUALIFIES' if ok else 'fails'}", flush=True)
    print("\nCHALLENGES (two rounds, static MLL, fixed payout; risk $900 scaled down to the contract cap)")
    g, comm = t0["gross_pnl"].to_numpy(), (t0["gross_pnl"] - t0["net_pnl"]).to_numpy()
    for name, p_, tgt, mll, cap, pay in (("$1.5K Challenge ($39, 2 micros)", 39.0, 1500, 500, 2, 1500),
                                         ("$3K Challenge ($49, 10 micros)", 49.0, 3000, 1000, 10, 3000),
                                         ("$6K Challenge ($149, 10 micros)", 149.0, 6000, 2000, 10, 6000)):
        real, dip = challenge(t0, p_, tgt, mll, cap, pay)
        rng = np.random.default_rng(1)
        fl = np.array([challenge(flip(t0, g, comm, rng.choice([-1, 1], len(t0))), p_, tgt, mll, cap, pay)[0] for _ in range(200)])
        fmed, fpos = float(np.median(fl)), float((fl > 0).mean())
        ok = real >= bar[0] and fmed >= bar[1] and dip >= bar[2]
        n_ok += ok
        print(f"  {name:<56} | real ${real:>8,.0f} | coin flip ${fmed:>8,.0f} ({fpos:.0%}) | dip ${dip:>8,.0f} | "
              f"{'QUALIFIES' if ok else 'fails'}", flush=True)
    print(f"\nqualifying Topstep Labs products: {n_ok}")


if __name__ == "__main__":
    main()

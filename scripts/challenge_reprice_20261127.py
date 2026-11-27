"""Re-price the Topstep $3K Challenge at what is on sale (docs/PREREG_CHALLENGE_REPRICE_20261127.md).

    uv run python -m scripts.challenge_reprice_20261127 | tee docs/jx_runs/challenge_reprice_20261127.txt
"""
import numpy as np
import pandas as pd

from backtest.recycle import Policy
from ict import data as D
from scripts.prop_search2_c2_20261126 import challenge
from scripts.radar_price import MODELS, flip, price, trades

ROWS = [("Past Labs Drop #003: $49, 10 micros, $1,000 MLL (PS3b check)", 49.0, 1000, 10),
        ("$3K Challenge on sale: $199, 50 micros, $1,000 MLL (= Labs Undead)", 199.0, 1000, 50),
        ("Labs Slasher: $65, 20 micros, $500 MLL (target/payout ASSUMED $3K)", 65.0, 500, 20)]
TARGET = PAYOUT = 3000


def main():
    orders, bars = pd.read_parquet(D.PROCESSED_DIR / "ideas_orders_NQ.parquet"), D.load("1m")
    nq = trades(orders, bars, 0)
    ts, ts_risk = MODELS["topstep50"][0][1:]
    ref_real, ref_dip, _, _ = price(nq, ts, ts_risk, Policy.LOCK_FIRST)
    bar = (0.5 * ref_real, 5000.0, 1.5 * ref_dip)
    print(f"Registered bar: real >= ${bar[0]:,.0f}, coin flip >= $5,000, dip >= ${bar[2]:,.0f}")
    print("Two rounds of +$3,000 from $0 against a static loss limit on worst open P&L; fixed $3,000 payout; $900 risk scaled to the cap.\n")
    g, comm = nq["gross_pnl"].to_numpy(), (nq["gross_pnl"] - nq["net_pnl"]).to_numpy()

    def run(p, mll, cap):
        real, dip = challenge(nq, float(p), TARGET, mll, cap, PAYOUT)
        rng = np.random.default_rng(1)
        fl = np.array([challenge(flip(nq, g, comm, rng.choice([-1, 1], len(nq))), float(p), TARGET, mll, cap, PAYOUT)[0]
                       for _ in range(200)])
        return real, float(np.median(fl)), float((fl > 0).mean()), dip

    for name, p, mll, cap in ROWS:
        real, fmed, fpos, dip = run(p, mll, cap)
        ok = real >= bar[0] and fmed >= bar[1] and dip >= bar[2]
        lo, hi = 0, 2000
        while hi - lo > 1:
            mid = (lo + hi) // 2
            r2, f2, _, d2 = run(mid, mll, cap)
            lo, hi = (mid, hi) if (r2 >= bar[0] and f2 >= bar[1] and d2 >= bar[2]) else (lo, mid)
        be = f"break-even ${lo}" if lo > 0 else "fails at any price"
        print(f"{name}\n   real ${real:>8,.0f} | coin flip ${fmed:>8,.0f} ({fpos:.0%}) | dip ${dip:>8,.0f} | "
              f"{'QUALIFIES' if ok else 'fails'} | {be}", flush=True)


if __name__ == "__main__":
    main()

"""Batch NF21 #627-#630: price signals in thin Bittensor subnet pools (docs/PREREG_BATCH_NF21_20261128.md). Uses NF20's data and model.

    uv run python -m scripts.batch_nf21_20261128 | tee docs/jx_runs/batch_nf21_20261128.txt
"""
from __future__ import annotations

import numpy as np
import pandas as pd

import scripts.batch_nf20_20261128 as N

S1 = (pd.Timestamp("2025-04-01"), pd.Timestamp("2026-01-01"))


def signals(w):
    w = w.sort_values(["netuid", "day"]).copy()
    g = w.groupby("netuid")
    w["n_hist"] = g.cumcount() + 1
    w["px4"] = g["px"].shift(4)
    w["tao4"] = g["tao_in"].shift(4)
    w["sup"] = w["alpha_in"] + w["alpha_out"]
    w["sup4"] = g["sup"].shift(4)
    w["reg4"] = g["registered_at"].shift(4)
    same = w["reg4"] == w["registered_at"]  # lookback only within one registration
    w["mom"] = (w["px"] / w["px4"] - 1).where(same)
    w["flow"] = (w["tao_in"] / w["tao4"] - 1).where(same)
    w["dil"] = (w["sup"] / w["sup4"] - 1).where(same)
    return w


def main():
    w, _ = N.load()
    snaps = sorted(w["day"].unique())
    span = (snaps[-1] - snaps[0]).days if snaps else 0
    ok = len(snaps) >= 29 and span >= 200 and w["netuid"].nunique() >= 30
    print(f"NF20 data: weekly snapshots {len(snaps)}, {span} days, subnets {w['netuid'].nunique()} -> Stage 0 bar {'met' if ok else 'NOT MET: not testable'}\n")
    if not ok:
        return
    usd, (fund, fmean) = N.tao_usd(), N.tao_funding()
    w = signals(w)
    elig = lambda s: s[(s["tao_in"] >= N.MIN_TAO) & (s["n_hist"] >= 4)]  # noqa: E731
    specs = [("#627", "Alpha momentum (top 10 by 4-week price change)", lambda s: elig(s).dropna(subset=["mom"]).nlargest(10, "mom")),
             ("#628", "Alpha reversal (bottom 10 by 4-week price change)", lambda s: elig(s).dropna(subset=["mom"]).nsmallest(10, "mom")),
             ("#629", "TAO inflow chase (top 10 by 4-week tao_in growth)", lambda s: elig(s).dropna(subset=["flow"]).nlargest(10, "flow")),
             ("#630", "Low dilution (bottom 10 by 4-week alpha supply growth)", lambda s: elig(s).dropna(subset=["dil"]).nsmallest(10, "dil"))]
    N.S1 = S1
    for num, label, pick in specs:
        print(f"{num} {label}")
        p = lambda s, pick=pick: pick(s)["netuid"].tolist()  # noqa: E731
        e, e15 = N.portfolio(w, p, usd, fund, fmean), N.portfolio(w, p, usd, fund, fmean, 1.5)
        e = e[e["start"] >= S1[0]] if len(e) else e
        e15 = e15[e15["start"] >= S1[0]] if len(e15) else e15
        if len(e):
            print(f"   holds with a deregistered subnet: {int(e['dead'].sum())}; mean subnets per hold {e['n'].mean():.1f}")
        a = N.summ(e, S1)
        print(N.fmt("Stage 1 holds starting 2025-04..2025-12", a))
        b, b15 = N.summ(e, N.S2), N.summ(e15, N.S2)
        print(N.fmt("Stage 2 holds starting 2026-01..2026-10", b))
        print(f"   slippage x1.5 Stage 2 mean {b15.get('m', np.nan):+.2%}")
        if a.get("n", 0) >= 6 and not (a["m"] > 0):
            v = "KILL (Stage 1)"
        else:
            v = "PASS" if (b.get("n", 0) >= 10 and b["m"] >= 0.03 and b["t"] >= 2 and b["ex3"] > 0 and b15.get("m", -1) > 0) else "FAIL"
        if v == "PASS":
            v += " (subject to NF20's yield sanity check; forward log only if t >= 2.5)"
        print(f"   VERDICT {v}\n")


if __name__ == "__main__":
    main()

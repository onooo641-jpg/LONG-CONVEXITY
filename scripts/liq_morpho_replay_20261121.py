"""PREREG_LIQ_MORPHO_REPLAY_20261121 analysis. uv run python -I scripts/liq_morpho_replay_20261121.py [1|2]"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
L_IDEAL = 2          # blocks: 0.3 s detection, 2 s blocks (PREREG)


def main():
    stage = sys.argv[1] if len(sys.argv) > 1 else "2"
    f = ROOT / "data" / "public" / f"liq_replay_gaps_s{stage}_morphobase.parquet"
    d = pd.read_parquet(f)
    n_all = len(d)
    res = d[d["has_c"] & d["g_ev"].notna() & ~d["err_ev"].fillna(False)]
    print(f"stage {stage}: sampled {n_all}, oracle feeds resolved {int(d['has_c'].sum())}, usable {len(res)} ({len(res) / max(n_all, 1):.0%}); markets {d['mid'].nunique()}")
    if not len(res):
        print("no usable events")
        return
    noup = (res["g_ev"] == -1).mean()
    bad = len(res) >= 10 and noup > 0.50
    print(f"feed check: no-update-in-window share {noup:.2f} -> {'FEEDS NOT CREDIBLE (excluded)' if bad else 'ok'}")
    reach = (res["g_ev"] == -1) | (res["g_ev"] > L_IDEAL)
    R, Rv = reach.mean(), (res["gross"] * reach).sum() / res["gross"].sum()
    nul = res[res["g_null"].notna() & ~res["err_null"].fillna(False)]
    nr = ((nul["g_null"] == -1) | (nul["g_null"] > L_IDEAL)).mean() if len(nul) else float("nan")
    print(f"IDEAL arm (L={L_IDEAL} blocks): reachable R(events) {R:.3f}  R(value) {Rv:.3f}  gap==0 {(res['g_ev'] == 0).mean():.3f}  gap<=1 {((res['g_ev'] >= 0) & (res['g_ev'] <= 1)).mean():.3f}  null R {nr:.3f}")
    print("\npost-hoc: reachable share R(events)/R(value) if our delay were L blocks")
    print("  ".join(f"L={x:<2d} {((res['g_ev'] == -1) | (res['g_ev'] > x)).mean():5.3f}/{(res['gross'] * ((res['g_ev'] == -1) | (res['g_ev'] > x))).sum() / res['gross'].sum():5.3f}" for x in (1, 2, 3, 5, 8, 12)))
    print("\ndescriptive splits (ideal arm): group, usable, R(events), R(value)")
    for name, mask in (("Jun 2026", res["month"] == 19), ("Oct 2026", res["month"] == 23), ("other months", ~res["month"].isin([19, 23]))):
        x = res[mask]
        if len(x):
            r_ = (x["g_ev"] == -1) | (x["g_ev"] > L_IDEAL)
            print(f"  {name:12s} {len(x):4d}  {r_.mean():.3f}  {(x['gross'] * r_).sum() / x['gross'].sum():.3f}")
    top = res["mid"].value_counts().head(5).index
    print("  by market (top 5 by events): market, usable, R(events), R(value)")
    for m in top:
        x = res[res["mid"] == m]
        r_ = (x["g_ev"] == -1) | (x["g_ev"] > L_IDEAL)
        print(f"  {m[:10]}  {len(x):4d}  {r_.mean():.3f}  {(x['gross'] * r_).sum() / x['gross'].sum():.3f}")
    if bad:
        verdict = "NOT CREDIBLE (feed check failed): no verdict"
    elif stage == "1":
        verdict = "STAGE 1 KILL (R < 3% and R_value < 3%)" if (R < 0.03 and Rv < 0.03) else "STAGE 1: not killed, run stage 2"
    else:
        verdict = "DROP (R < 5% and R_value < 5%)" if (R < 0.05 and Rv < 0.05) else ("PLAUSIBLE (R >= 10% and R_value >= 10%)" if (R >= 0.10 and Rv >= 0.10) else "MARGINAL")
    print(f"\nverdict: {verdict}")


if __name__ == "__main__":
    main()

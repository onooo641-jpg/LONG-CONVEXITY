"""PREREG_LIQ_REPLAY_20261121 analysis. uv run python -I scripts/liq_replay_20261121.py [stage]  (stage 1 or 2; default 2)"""
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import liquidations_20261120 as L  # noqa: E402
import liq_replay_sample_20261121 as S  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
BT = {"arbitrum": 0.25, "base": 2.0, "avalanche": 2.0, "polygon": 2.0, "optimism": 2.0}
BUCKETS = [(50, 200), (200, 1000), (1000, 5000), (5000, 1e12)]


def part_ab():
    print("== A. gas bidding by bonus size (eligible events, last 12 months, main pools)")
    print("chain      bucket        events   median gas/bonus  p90 gas/bonus  share gas_price>2x month-p10")
    comp = []
    for c, pool in S.POOL.items():
        df = L.load(c)
        df = df[df["venue"] == pool].copy()
        p10 = df[df["gas_price"].notna()].groupby("month")["gas_price"].quantile(0.10)
        df["gp_ratio"] = df["gas_price"] / df["month"].map(p10)
        e = df[df["valid"] & (df["gross"] > 50) & (df["month"] >= 12)]
        for lo, hi in BUCKETS:
            b = e[(e["gross"] > lo) & (e["gross"] <= hi)]
            g = b[b["has_receipt"]]
            gs = g["gas_usd"] * g["n_in_tx"] / g["gross"] if len(g) else pd.Series(dtype=float)  # gas of the whole tx over this event's bonus is not meaningful: use per-event gas
            gs = g["gas_usd"] / g["gross"]
            print(f"{c:10s} {lo:>5.0f}-{('inf' if hi > 1e11 else int(hi)):>5}  {len(b):7d}   {gs.median() if len(gs) else float('nan'):16.4f}  {gs.quantile(.9) if len(gs) else float('nan'):13.4f}  "
                  f"{(g['gp_ratio'] > 2).mean() if len(g) else float('nan'):10.2f}")
        allp = df[df["valid"] & (df["month"] >= 12)]
        wins = allp.groupby("liquidator").size()
        rep = set(wins[wins >= 50].index)
        for lo, hi in BUCKETS:
            b = e[(e["gross"] > lo) & (e["gross"] <= hi)]
            if not len(b):
                continue
            by = b.groupby("liquidator")["gross"].sum().sort_values(ascending=False, kind="mergesort")
            comp.append((c, lo, hi, len(b), len(by), by.head(3).sum() / by.sum(), by.head(10).sum() / by.sum(), b[b["liquidator"].isin(rep)]["gross"].sum() / b["gross"].sum()))
    print("\n== B. competition by bonus size (winner = liquidator field)")
    print("chain      bucket         events  winners  top3   top10  repeat(>=50 wins) share")
    for c, lo, hi, n, nw, t3, t10, rp in comp:
        print(f"{c:10s} {lo:>5.0f}-{('inf' if hi > 1e11 else int(hi)):>5}  {n:7d} {nw:8d}  {t3:.2f}   {t10:.2f}   {rp:.2f}")


def latency(chain):
    f = ROOT / "data" / "shadow" / chain / "unhealthy.jsonl"
    ms = []
    if f.exists():
        for line in f.read_text().splitlines():
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            if r.get("ver") == 2 and "detect_ms" in r:
                ms.append(r["detect_ms"])
    med = float(np.median(ms)) if ms else float("nan")
    out = {}
    for arm, ls in (("actions", med / 1000 + 1.0), ("ideal", 0.3)):
        out[arm] = int(math.ceil((ls + BT[chain]) / BT[chain])) if ls == ls else None
    return med, len(ms), out


def part_c(stage):
    print(f"\n== C. replay gap (stage {stage}): reachable = no price update of the collateral/debt feed within L blocks before the liquidation")
    rows = []
    for c in S.POOL:
        f = ROOT / "data" / "public" / f"liq_replay_gaps_s{stage}_{c}.parquet"
        if not f.exists():
            print(f"{c}: no replay data")
            continue
        d = pd.read_parquet(f)
        med, nrec, Ls = latency(c)
        print(f"{c:10s} rows {len(d)}  median detect_ms {med:.0f} (n={nrec})  L blocks: actions {Ls['actions']}, ideal {Ls['ideal']}")
        d = d[(d["has_c"] | d["has_d"]) & d["g_ev"].notna() & ~d["err_ev"].fillna(False)]
        for arm in ("actions", "ideal"):
            L_ = Ls[arm]
            if L_ is None:
                continue
            reach = (d["g_ev"] == -1) | (d["g_ev"] > L_)
            nul = d["g_null"].notna() & ~d["err_null"].fillna(False)
            nreach = ((d["g_null"] == -1) | (d["g_null"] > L_))[nul]
            rows.append(dict(chain=c, arm=arm, n=len(d), R=reach.mean() if len(d) else np.nan, Rv=(d["gross"] * reach).sum() / d["gross"].sum() if len(d) else np.nan,
                             g0=(d["g_ev"] == 0).mean(), g1=((d["g_ev"] >= 0) & (d["g_ev"] <= 1)).mean(), inf=(d["g_ev"] == -1).mean(), null=nreach.mean() if len(nreach) else np.nan))
    r = pd.DataFrame(rows)
    if r.empty:
        print("no data")
        return
    print("\nchain      arm      resolved  R(events)  R(value)  gap==0  gap<=1  no-update-in-window  null R")
    for _, x in r.iterrows():
        print(f"{x['chain']:10s} {x['arm']:8s} {x['n']:8d}  {x['R']:8.3f}  {x['Rv']:8.3f}  {x['g0']:6.3f}  {x['g1']:6.3f}  {x['inf']:18.3f}  {x['null']:6.3f}")
    for arm in ("actions", "ideal"):
        a = r[r["arm"] == arm]
        n = a["n"].sum()
        if n == 0:
            continue
        R = (a["R"] * a["n"]).sum() / n
        print(f"\npooled {arm}: resolved {n}  R {R:.3f}")
    a = r[r["arm"] == "ideal"]
    if len(a):
        n = a["n"].sum()
        R = (a["R"] * a["n"]).sum() / n
        Rv = (a["Rv"] * a["n"]).sum() / n          # event-weighted mean of value shares (approximation; per-chain Rv shown above)
        ven10 = int((a["R"] >= 0.10).sum())
        if stage == "1":
            verdict = "STAGE 1 KILL (R < 3% and R_value < 3%): stop" if (R < 0.03 and Rv < 0.03) else "STAGE 1: not killed, run stage 2"
        else:
            verdict = ("DROP fast price-triggered bot (ideal arm R < 5% and R_value < 5%)" if (R < 0.05 and Rv < 0.05)
                       else "PLAUSIBLE (R >= 10% and R >= 10% on >= 3 venues)" if (R >= 0.10 and ven10 >= 3) else "MARGINAL")
        print(f"\nverdict (ideal arm, pooled R {R:.3f}, R_value {Rv:.3f}, venues with R >= 10%: {ven10}/5): {verdict}")


def main():
    stage = sys.argv[1] if len(sys.argv) > 1 else "2"
    part_ab()
    part_c(stage)


if __name__ == "__main__":
    main()

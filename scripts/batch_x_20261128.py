"""Batch X #532-#533: the wick mechanism on US ETFs and FX (docs/PREREG_BATCH_X_20261128.md).

    uv run python -m scripts.batch_x_20261128 | tee docs/jx_runs/batch_x_20261128.txt
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from ict import data as D

OUT = D.REPO_ROOT / "data" / "public"
SIZE, POT = 5000.0, 15_000.0
COST = {"etf": 0.0002, "fx": 0.00005}
DEV, OOS = (2006, 2015), (2016, 2026)


def fills(df, kind, next_day=False):
    out = []
    for sym, g in df[df["kind"] == kind].groupby("sym"):
        g = g.sort_values("d").reset_index(drop=True)
        prev = g["c"].shift()
        x = (4 * g["c"].pct_change().rolling(30).std().shift()).clip(0.01, 0.30)
        lvl = prev * (1 - x)
        hit = prev.notna() & x.notna() & (g["l"] <= lvl * (1 - 0.1 * x))
        for i in np.flatnonzero(hit.to_numpy()):
            j = i + (1 if next_day else 0)
            if j >= len(g):
                continue
            px = min(float(lvl.iloc[i]), float(g["o"].iloc[i]))
            out.append({"sym": sym, "d": g["d"].iloc[i], "ret": float(g["c"].iloc[j]) / px - 1 - 2 * COST[kind]})
    f = pd.DataFrame(out)
    if not f.empty:
        f["pnl"] = SIZE * np.minimum(1.0, POT / (SIZE * f.groupby("d")["ret"].transform("size"))) * f["ret"]
    return f


def summ(f, yrs):
    g = f[(f["d"].dt.year >= yrs[0]) & (f["d"].dt.year <= yrs[1])] if not f.empty else f
    if g.empty:
        return dict(n=0, m=np.nan, t=np.nan, usd=0.0, ex=0.0, win=np.nan)
    r = g["ret"]
    span = (min(g["d"].max(), pd.Timestamp(f"{yrs[1]}-12-31")) - pd.Timestamp(f"{yrs[0]}-01-01")).days / 365.25
    best = g.groupby("d")["pnl"].sum().idxmax()
    return dict(n=len(g), m=r.mean(), t=r.mean() / (r.std(ddof=1) / np.sqrt(len(r))) if len(r) > 1 else np.nan,
                usd=g["pnl"].sum() / span, ex=g[g["d"] != best]["pnl"].sum() / span, win=(r > 0).mean())


def fmt(label, s):
    if not s["n"]:
        return f"   {label}: no fills"
    return (f"   {label}: fills {s['n']} | mean net {s['m']:+.2%} (t {s['t']:.2f}, win {s['win']:.0%}) | ${s['usd']:,.0f}/yr "
            f"| without best day ${s['ex']:,.0f}/yr")


def main():
    df = pd.read_parquet(OUT / "batchx_ohlc_1d.parquet")
    df["d"] = pd.to_datetime(df["t"], unit="s").dt.normalize()
    df = df.drop_duplicates(["kind", "sym", "d"])
    for num, kind, label in (("#532", "etf", "US ETFs"), ("#533", "fx", "FX pairs")):
        n_sym = df[df["kind"] == kind]["sym"].nunique()
        f = fills(df, kind)
        a, b = summ(f, DEV), summ(f, OOS)
        print(f"{num} {label} ({n_sym} instruments): bid at previous close x (1 - 4*sigma30, clipped 1%..30%), exit at the close")
        print(fmt("Stage 1 2006-2015", a))
        print(fmt("Stage 2 2016-2026", b))
        nb = summ(fills(df, kind, next_day=True), OOS)
        print(fmt("context: exit at next day's close, Stage 2", nb))
        if not f.empty:
            by = f[f["d"].dt.year >= OOS[0]].groupby(f["d"].dt.year)["ret"].agg(["size", "mean"])
            print("   Stage 2 by year: " + "; ".join(f"{y} n {int(r['size'])} {r['mean']:+.2%}" for y, r in by.iterrows()))
        kill = a["n"] >= 30 and not (a["m"] > 0)
        ok = (not kill) and b["n"] >= 30 and b["m"] >= 0.002 and b["t"] >= 2 and b["usd"] >= 3000
        print(f"   VERDICT {'KILL (Stage 1)' if kill else ('PASS' if ok else 'FAIL')}\n")


if __name__ == "__main__":
    main()

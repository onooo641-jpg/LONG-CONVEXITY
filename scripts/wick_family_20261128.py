"""#519 resting asks above squeeze spikes; #520 volatility-scaled wick bids (docs/PREREG_WICK_FAMILY_20261128.md).

    uv run python -m scripts.wick_family_20261128 | tee docs/jx_runs/wick_family_20261128.txt
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

PUB = Path(__file__).resolve().parent.parent / "data" / "public"
MAKER, TAKER, THROUGH, CAP_FILL, VOL_SHARE, POT = 0.00015, 0.00045, 0.005, 1500.0, 0.01, 15_000.0
S1 = (pd.Timestamp("2023-06-01", tz="UTC"), pd.Timestamp("2024-12-31", tz="UTC"))
S2 = (pd.Timestamp("2025-01-01", tz="UTC"), pd.Timestamp("2026-10-31", tz="UTC"))


def fills(cd, side, dist):
    """side +1 = resting buy below (#389/#520), -1 = resting sell above (#519). dist(g) -> per-day distance Series."""
    out = []
    for coin, g in cd.groupby("coin"):
        g = g.sort_values("day")
        g = g[g["day"] >= g["day"].iloc[0] + pd.Timedelta(days=30)].reset_index(drop=True)
        if len(g) < 2:
            continue
        prev = g["c"].shift()
        x = dist(g)
        if side > 0:
            lvl = prev * (1 - x)
            hit = (g["l"] <= lvl * (1 - THROUGH)) & prev.notna() & x.notna()
        else:
            lvl = prev * (1 + x)
            hit = (g["h"] >= lvl * (1 + THROUGH)) & prev.notna() & x.notna()
        for i in np.flatnonzero(hit.to_numpy()):
            r = g.iloc[i]
            if side > 0:
                px = min(float(lvl.iloc[i]), float(r["o"]))
                ret = float(r["c"]) / px - 1
            else:
                px = max(float(lvl.iloc[i]), float(r["o"]))
                ret = 1 - float(r["c"]) / px
            size = min(CAP_FILL, VOL_SHARE * float(r["v"]) * float(r["c"]))
            out.append({"coin": coin, "day": r["day"], "ret": ret - MAKER - TAKER, "size": size})
    f = pd.DataFrame(out)
    if not f.empty:
        f["pnl"] = f["size"] * np.minimum(1.0, POT / f.groupby("day")["size"].transform("sum")) * f["ret"]
    return f


def window(f, lo, hi):
    return f[(f["day"] >= lo) & (f["day"] <= hi)]


def report(label, f):
    yrs = lambda w: ((w[1] - w[0]).days + 1) / 365  # noqa: E731
    res = {}
    for name, w in (("Stage 1", S1), ("Stage 2", S2)):
        g = window(f, *w) if not f.empty else f
        if g.empty:
            print(f"   {name}: no fills")
            res[name] = (0, np.nan, np.nan, 0.0)
            continue
        r = g["ret"]
        t = r.mean() / (r.std(ddof=1) / np.sqrt(len(r))) if len(r) > 1 else np.nan
        best = g.groupby("day")["pnl"].sum().idxmax()
        per = g["pnl"].sum() / yrs(w)
        print(f"   {name} {w[0].date()}..{w[1].date()}: fills {len(g)} | mean net {r.mean():+.2%} (median {r.median():+.2%}, t {t:.2f}, "
              f"win {(r > 0).mean():.0%}) | ${per:,.0f}/yr | without best day ${(g[g['day'] != best]['pnl'].sum()) / yrs(w):,.0f}/yr")
        res[name] = (len(g), r.mean(), t, per)
    return res


def verdict(res):
    n1, m1, _, _ = res["Stage 1"]
    n2, m2, t2, usd = res["Stage 2"]
    if n1 >= 30 and not (m1 > 0.003):
        return "KILL (Stage 1)"
    return "PASS" if (n2 >= 30 and m2 >= 0.003 and t2 >= 2 and usd >= 3000) else "FAIL"


def monthly(f):
    return f.groupby(f["day"].dt.to_period("M"))["pnl"].sum() if not f.empty else pd.Series(dtype=float)


def main():
    cd = pd.read_parquet(PUB / "uncharted_385_candles.parquet")
    cd["day"] = pd.to_datetime(cd["t"], unit="ms", utc=True).dt.normalize()
    cd = cd.drop_duplicates(["coin", "day"])
    print(f"Hyperliquid perps {cd['coin'].nunique()}, {cd['day'].min().date()}..{cd['day'].max().date()}\n")
    base = fills(cd, +1, lambda g: pd.Series(0.15, index=g.index))
    print("#389 reference (resting bids, X 15%)")
    report("#389", base)

    print("\n#519 Resting asks above short-squeeze spikes")
    main519 = None
    for j, x in enumerate((0.15, 0.10, 0.20, 0.30)):
        f = fills(cd, -1, lambda g, x=x: pd.Series(x, index=g.index))
        print(f"  X {x:.0%}{' (primary)' if j == 0 else ' (context)'}")
        res = report("#519", f)
        if j == 0:
            main519 = (f, res)
            print(f"   VERDICT {verdict(res)}")

    print("\n#520 Volatility-scaled bids (X = 4 x sigma30, clipped 5%..30%)")

    def vol_dist(g):
        sig = g["c"].pct_change().rolling(30).std().shift()
        return (4 * sig).clip(0.05, 0.30)
    f520 = fills(cd, +1, vol_dist)
    res520 = report("#520", f520)
    print(f"   VERDICT {verdict(res520)}")

    f519 = main519[0]
    for name, w in (("Stage 1", S1), ("Stage 2", S2)):
        a = monthly(window(base, *w))
        b = monthly(window(f519, *w)) if not f519.empty else pd.Series(dtype=float)
        idx = a.index.union(b.index)
        a, b = a.reindex(idx, fill_value=0.0), b.reindex(idx, fill_value=0.0)
        corr = a.corr(b) if len(idx) > 2 else np.nan
        comb = a + b
        yrs = ((w[1] - w[0]).days + 1) / 365
        print(f"\n#389 + #519 (X 15%) {name}: monthly P&L correlation {corr:+.2f} | worst month #389 ${a.min():,.0f}, combined ${comb.min():,.0f} "
              f"| $/yr #389 ${a.sum() / yrs:,.0f}, combined ${comb.sum() / yrs:,.0f}")


if __name__ == "__main__":
    main()

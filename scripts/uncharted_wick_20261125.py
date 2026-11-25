"""#389 U-T6: resting bids under liquidation wicks on Hyperliquid perps (docs/PREREG_UNCHARTED_20261125.md).

    uv run python -m scripts.uncharted_wick_20261125 | tee docs/jx_runs/uncharted_wick_20261125.txt
Reads data/public/uncharted_385_candles.parquet (daily candles of every Hyperliquid perp; Actions job u385hyperp).
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

PUB = Path(__file__).resolve().parent.parent / "data" / "public"
MAKER, TAKER, THROUGH, CAP_FILL, VOL_SHARE, POT = 0.00015, 0.00045, 0.005, 1500.0, 0.01, 15_000.0
START, END = pd.Timestamp("2023-06-01", tz="UTC"), pd.Timestamp("2026-10-31", tz="UTC")


def fills(cd, x):
    out = []
    for coin, g in cd.groupby("coin"):
        g = g.sort_values("day")
        g = g[g["day"] >= g["day"].iloc[0] + pd.Timedelta(days=30)]
        prev = g["c"].shift()
        lvl = prev * (1 - x)
        hit = (g["l"] <= lvl * (1 - THROUGH)) & prev.notna() & (g["day"] >= START) & (g["day"] <= END)
        for i in np.flatnonzero(hit.to_numpy()):
            r = g.iloc[i]
            px = min(float(lvl.iloc[i]), float(r["o"]))
            size = min(CAP_FILL, VOL_SHARE * float(r["v"]) * float(r["c"]))
            net = float(r["c"]) / px - 1 - MAKER - TAKER
            out.append({"coin": coin, "day": r["day"], "ret": net, "size": size})
    return pd.DataFrame(out)


def main():
    print("===== #389 U-T6 resting bids under liquidation wicks (Hyperliquid perps, daily candles)")
    cd = pd.read_parquet(PUB / "uncharted_385_candles.parquet")
    cd["day"] = pd.to_datetime(cd["t"], unit="ms", utc=True).dt.normalize()
    cd = cd.drop_duplicates(["coin", "day"])
    yrs = ((min(cd["day"].max(), END) - START).days + 1) / 365
    print(f"  perps {cd['coin'].nunique()}; days {cd['day'].min().date()}..{cd['day'].max().date()}; window {START.date()}..{END.date()} "
          f"({yrs:.2f} yr)")
    verdict = "KILL (no fills)"
    for x in (0.15, 0.10, 0.20, 0.30):
        f = fills(cd, x)
        if f.empty:
            print(f"  X {x:.0%}: no fills")
            continue
        day_sz = f.groupby("day")["size"].transform("sum")
        f["size_pot"] = f["size"] * np.minimum(1.0, POT / day_sz)
        f["pnl"] = f["size_pot"] * f["ret"]
        per_yr = f["pnl"].sum() / yrs
        r = f["ret"]
        t = r.mean() / (r.std(ddof=1) / np.sqrt(len(r)))
        top = f.groupby("day")["pnl"].sum().sort_values()
        print(f"  X {x:.0%}{' (primary)' if x == 0.15 else ''}: fills {len(f)} on {f['day'].nunique()} days; mean net per fill {r.mean():.2%} "
              f"(median {r.median():.2%}, t {t:.2f}, win {(r > 0).mean():.0%}); net ${f['pnl'].sum():,.0f} -> ${per_yr:,.0f}/yr; "
              f"worst day ${top.iloc[0]:,.0f} ({top.index[0].date()}), best day ${top.iloc[-1]:,.0f} ({top.index[-1].date()})")
        by_y = f.groupby(f["day"].dt.year).agg(n=("ret", "size"), mean=("ret", "mean"), pnl=("pnl", "sum"))
        print("     by year: " + "; ".join(f"{y} n {int(a.n)} mean {a['mean']:.2%} ${a['pnl']:,.0f}" for y, a in by_y.iterrows()))
        ex = f[f["day"] != top.index[-1]]
        print(f"     without the best day: ${ex['pnl'].sum() / yrs:,.0f}/yr, mean per fill {ex['ret'].mean():.2%}")
        if x == 0.15:
            kill = r.mean() <= 0.003 or per_yr < 3000
            verdict = "KILL (" + ("mean net per fill <= 0.3%" if r.mean() <= 0.003 else "net < $3,000/yr") + ")" if kill else "survives (kill-only)"
    print(f"  STAGE 1 VERDICT (X 15%): {verdict}")


if __name__ == "__main__":
    main()

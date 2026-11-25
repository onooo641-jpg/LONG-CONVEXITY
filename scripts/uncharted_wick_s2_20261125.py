"""#389 U-T6 Stage 2: S2a out-of-sample on Binance USD-M perps, S2b risk path on Hyperliquid (docs/PREREG_UNCHARTED_20261125.md).

    uv run python -m scripts.uncharted_wick_s2_20261125 | tee docs/jx_runs/uncharted_wick_s2_20261125.txt
Reads data/public/uncharted_385_candles.parquet (Hyperliquid) and data/public/uncharted_389_binance_ohlc.parquet (Actions job u389binance).
Same rule as Stage 1 (scripts/uncharted_wick_20261125.fills); nothing changed.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from scripts.uncharted_wick_20261125 import POT, fills

PUB = Path(__file__).resolve().parent.parent / "data" / "public"


def pot_pnl(f):
    day_sz = f.groupby("day")["size"].transform("sum")
    f = f.assign(size_pot=f["size"] * np.minimum(1.0, POT / day_sz))
    f["pnl"] = f["size_pot"] * f["ret"]
    return f


def path_stats(f, label):
    d = f.groupby("day")["pnl"].sum()
    d = d.reindex(pd.date_range(d.index.min(), d.index.max(), freq="D", tz="UTC"), fill_value=0.0)
    eq = POT + d.cumsum()
    dd = float((eq - eq.cummax()).min())
    print(f"  {label}: worst peak-to-trough ${dd:,.0f}; worst day ${d.min():,.0f} ({d.idxmin().date()}); best day ${d.max():,.0f}; "
          f"losing months {(d.resample('ME').sum() < 0).sum()} of {len(d.resample('ME').sum())}")
    return dd, float(d.min())


def halves(f, name):
    f = f.copy()
    f["h"] = f["day"].dt.year.astype(str) + "H" + ((f["day"].dt.month > 6) + 1).astype(str)
    g = f.groupby("h").agg(n=("ret", "size"), mean=("ret", "mean"), pnl=("pnl", "sum"))
    print(f"  half-years, {name}: " + "; ".join(f"{h} n {int(r.n)} {r['mean']:+.2%} ${r.pnl:,.0f}" for h, r in g.iterrows()))


def sizing_checks(hl):
    """Mechanical fix (previous day's volume for size) and the margin-reservation case for S2d."""
    import json as _j
    import scripts.uncharted_wick_20261125 as w
    meta = {u["name"]: u.get("maxLeverage", 3) for u in _j.loads((PUB / "uncharted_385_meta.json").read_text())}
    yrs = ((w.END - w.START).days + 1) / 365
    out, rest = [], []
    for coin, g in hl.sort_values(["coin", "day"]).groupby("coin"):
        g = g[g["day"] >= g["day"].iloc[0] + pd.Timedelta(days=30)]
        prev, pvol = g["c"].shift(), (g["v"] * g["c"]).shift()
        lvl, size = prev * 0.85, np.minimum(w.CAP_FILL, w.VOL_SHARE * pvol)
        ok = prev.notna() & (g["day"] >= w.START) & (g["day"] <= w.END)
        rest.append(pd.DataFrame({"day": g["day"][ok], "size": size[ok], "margin": size[ok] / meta.get(coin, 3)}))
        hit = ok & (g["l"] <= lvl * (1 - w.THROUGH))
        ret = g["c"] / np.minimum(lvl, g["o"]) - 1 - w.MAKER - w.TAKER
        out.append(pd.DataFrame({"day": g["day"][hit], "ret": ret[hit], "size": size[hit]}))
    f, R = pd.concat(out), pd.concat(rest)
    f = f[f["size"] > 0]
    f["pnl"] = f["size"] * np.minimum(1, POT / f.groupby("day")["size"].transform("sum")) * f["ret"]
    m = R.groupby("day")[["size", "margin"]].sum()
    sc = np.minimum(1, 0.8 * POT / m["margin"])
    print(f"  sizing fix (previous day's volume): fills {len(f)}, mean {f['ret'].mean():.2%}, ${f['pnl'].sum() / yrs:,.0f}/yr")
    print(f"  resting bids per day: median notional ${m['size'].median():,.0f}; margin at max leverage median ${m['margin'].median():,.0f}")
    print(f"  if resting orders reserve that margin (posted share <= $12,000 of margin a day): "
          f"${(f['pnl'] * f['day'].map(sc).fillna(1)).sum() / yrs:,.0f}/yr (median share posted {sc.median():.2f})")


def main():
    print("===== #389 U-T6 Stage 2")
    hl = pd.read_parquet(PUB / "uncharted_385_candles.parquet")
    hl["day"] = pd.to_datetime(hl["t"], unit="ms", utc=True).dt.normalize()
    hl = hl.drop_duplicates(["coin", "day"])
    fh = pot_pnl(fills(hl, 0.15))
    print("S2b risk path, Hyperliquid, X 15% ($15,000 pot):")
    dd, worst = path_stats(fh, "Hyperliquid 2023-06..2026-10")
    s2b = dd >= -3750 and worst >= -3000
    print(f"  S2b: {'PASS' if s2b else 'FAIL'} (needs drawdown >= -$3,750 and worst day >= -$3,000)")
    halves(fh, "Hyperliquid X 15%")
    sizing_checks(hl)
    bp = PUB / "uncharted_389_binance_ohlc.parquet"
    if not bp.exists():
        print("S2a: Binance data not fetched yet")
        return
    b = pd.read_parquet(bp)
    b = b.rename(columns={"sym": "coin"})
    b["day"] = pd.to_datetime(b["t"], unit="s", utc=True).dt.normalize()
    b = b.drop_duplicates(["coin", "day"]).sort_values(["coin", "day"])
    b["v"] = b["qvol"] / b["c"].where(b["c"] > 0)  # fills() sizes on v x close = quote volume
    print(f"S2a out-of-sample, Binance USD-M: {b['coin'].nunique()} symbols, {len(b)} symbol-days, {b['day'].min().date()}..{b['day'].max().date()}")
    import scripts.uncharted_wick_20261125 as w
    w.START = pd.Timestamp("2020-01-01", tz="UTC")
    yrs = ((min(b["day"].max(), w.END) - w.START).days + 1) / 365
    res = {}
    for x in (0.15, 0.10, 0.20, 0.30):
        f = fills(b, x)
        if f.empty:
            print(f"  X {x:.0%}: no fills")
            continue
        f = pot_pnl(f)
        r = f["ret"]
        t = r.mean() / (r.std(ddof=1) / np.sqrt(len(r)))
        per_yr = f["pnl"].sum() / yrs
        by = f.groupby(f["day"].dt.year)["pnl"].sum()
        full = by[(by.index >= 2020) & (by.index <= 2025)]
        print(f"  X {x:.0%}{' (primary)' if x == 0.15 else ''}: fills {len(f)}; mean net per fill {r.mean():.2%} (median {r.median():.2%}, t {t:.2f}, "
              f"win {(r > 0).mean():.0%}); ${per_yr:,.0f}/yr; positive full years {int((full > 0).sum())} of {len(full)}")
        print("     by year: " + "; ".join(f"{y} ${v:,.0f} (n {int((f['day'].dt.year == y).sum())}, mean {f.loc[f['day'].dt.year == y, 'ret'].mean():.2%})"
                                         for y, v in by.items()))
        res[x] = (r.mean(), t, per_yr, int((full > 0).sum()))
        if x == 0.15:
            path_stats(f, "Binance path (context)")
            halves(f, "Binance X 15%")
    m, t, py, pos = res.get(0.15, (np.nan, np.nan, 0, 0))
    s2a = m >= 0.005 and t >= 3 and py >= 3000 and pos >= 4
    print(f"  S2a: {'PASS' if s2a else 'FAIL'} (needs mean >= 0.5%, t >= 3, >= $3,000/yr, >= 4 of 6 full years positive)")


if __name__ == "__main__":
    main()

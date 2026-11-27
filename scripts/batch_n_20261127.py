"""Batch N #509-#511: #389's wick rule on Hyperliquid markets it never covered (docs/PREREG_BATCH_N_20261127.md).

    uv run python -m scripts.batch_n_20261127 | tee docs/jx_runs/batch_n_20261127.txt
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

PUB = Path(__file__).resolve().parent.parent / "data" / "public"
THROUGH, CAP_FILL, VOL_SHARE, POT = 0.005, 1500.0, 0.01, 15_000.0
T = lambda s: pd.Timestamp(s, tz="UTC")  # noqa: E731


def load(name, key):
    cd = pd.read_parquet(PUB / f"{name}.parquet").rename(columns={key: "coin"})
    cd["day"] = pd.to_datetime(cd["t"], unit="ms", utc=True).dt.normalize()
    return cd.drop_duplicates(["coin", "day"]).sort_values(["coin", "day"])


def fills(cd, x, maker, taker, first30):
    out = []
    for coin, g in cd.groupby("coin"):
        g = g.sort_values("day")
        first = g["day"].iloc[0]
        cut = first + pd.Timedelta(days=30)
        prev = g["c"].shift()
        lvl = prev * (1 - x)
        ok = (g["day"] < cut) if first30 else (g["day"] >= cut)
        hit = (g["l"] <= lvl * (1 - THROUGH)) & prev.notna() & ok
        for i in np.flatnonzero(hit.to_numpy()):
            r = g.iloc[i]
            px = min(float(lvl.iloc[i]), float(r["o"]))
            if not px > 0:
                continue
            size = min(CAP_FILL, VOL_SHARE * float(r["v"]) * float(r["c"]))
            out.append({"coin": coin, "day": r["day"], "listed": first, "ret": float(r["c"]) / px - 1 - maker - taker, "size": size})
    return pd.DataFrame(out)


def summarize(f, lo, hi, label):
    g = f[(f["day"] >= lo) & (f["day"] <= hi)].copy()
    yrs = ((hi - lo).days + 1) / 365
    if g.empty:
        return 0, np.nan, np.nan, 0.0, f"   {label}: no fills"
    day_sz = g.groupby("day")["size"].transform("sum")
    g["pnl"] = g["size"] * np.minimum(1.0, POT / day_sz) * g["ret"]
    r = g["ret"]
    t = r.mean() / (r.std(ddof=1) / np.sqrt(len(r))) if len(r) > 1 and r.std(ddof=1) > 0 else np.nan
    per_yr = g["pnl"].sum() / yrs
    best = g.groupby("day")["pnl"].sum().idxmax()
    ex = g[g["day"] != best]
    txt = (f"   {label}: fills {len(g)} on {g['day'].nunique()} days | mean net {r.mean():+.2%} (median {r.median():+.2%}, t {t:.2f}, "
           f"win {(r > 0).mean():.0%}) | ${per_yr:,.0f}/yr | without best day ${ex['pnl'].sum() / yrs:,.0f}/yr")
    return len(g), r.mean(), t, per_yr, txt


def verdict(dev, oos):
    n1, m1, _, _, _ = dev
    n2, m2, t2, usd, _ = oos
    if n1 >= 30 and not (m1 > 0.003):
        return "KILL (Stage 1)"
    ok = n2 >= 30 and m2 >= 0.003 and t2 >= 2 and usd >= 1000
    v = "PASS" if ok else "FAIL"
    if ok:
        v += " (counts toward the goal)" if usd >= 10000 else " (below $10K/yr: added capacity only)"
    return v + (" (Stage 1 < 30 fills: no kill possible)" if n1 < 30 else "")


def main():
    base = load("uncharted_385_candles", "coin")
    base389 = fills(base, 0.15, 0.00015, 0.00045, first30=False)
    days389 = set(base389["day"])
    specs = [
        ("#509 HIP-3 builder perps", load("fivehigh_hip3_1d", "coin"), (0.05, 0.10, 0.15), 0.00015, 0.00045, False,
         (T("2025-11-01"), T("2026-04-30")), (T("2026-05-01"), T("2026-11-25")), None),
        ("#510 Hyperliquid spot tokens", load("fivehigh_hl_spot_1d", "pair"), (0.15, 0.10, 0.20), 0.0004, 0.0007, False,
         (T("2024-05-01"), T("2025-06-30")), (T("2025-07-01"), T("2026-11-25")), None),
        ("#511 perps in their first 30 days", base, (0.15, 0.10, 0.20), 0.00015, 0.00045, True,
         (T("2023-06-01"), T("2024-12-31")), (T("2025-01-01"), T("2026-11-25")), T("2025-01-01")),
    ]
    print("Rule: bid at previous close x (1 - X); fill if low >= 0.5% through; sell at the close; size min($1,500, 1% of volume); "
          "$15,000 daily pot.\n")
    for name, cd, xs, mk, tk, first30, dev_w, oos_w, split_listing in specs:
        print(f"{name}: {cd['coin'].nunique()} markets, {cd['day'].min().date()}..{cd['day'].max().date()}")
        for j, x in enumerate(xs):
            f = fills(cd, x, mk, tk, first30)
            if f.empty:
                print(f"  X {x:.0%}: no fills")
                continue
            if split_listing is not None:  # #511 splits by listing date, not fill date
                dev_f, oos_f = f[f["listed"] < split_listing], f[f["listed"] >= split_listing]
                dev = summarize(dev_f, dev_w[0], dev_w[1] + pd.Timedelta(days=31), "Stage 1 (listed before 2025)")
                oos = summarize(oos_f, oos_w[0], oos_w[1], "Stage 2 (listed 2025 onward)")
            else:
                dev = summarize(f, *dev_w, f"Stage 1 {dev_w[0].date()}..{dev_w[1].date()}")
                oos = summarize(f, *oos_w, f"Stage 2 {oos_w[0].date()}..{oos_w[1].date()}")
            tag = " (primary)" if j == 0 else " (context)"
            print(f"  X {x:.0%}{tag}")
            print(dev[4])
            print(oos[4])
            if j == 0:
                ov = f[f["day"] >= oos_w[0]]
                share = ov["day"].isin(days389).mean() if len(ov) else np.nan
                print(f"   overlap: {share:.0%} of Stage 2 fills fall on days #389 also fills")
                print(f"   VERDICT {verdict(dev, oos)}")
        print()


if __name__ == "__main__":
    main()

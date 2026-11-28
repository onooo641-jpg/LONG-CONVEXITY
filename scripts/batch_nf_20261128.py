"""Batch NF #535-#536: niche new markets (docs/PREREG_BATCH_NF_20261128.md).

    uv run python -m scripts.batch_nf_20261128 | tee docs/jx_runs/batch_nf_20261128.txt
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

PUB = Path(__file__).resolve().parent.parent / "data" / "public"
THROUGH, CAP, VOLS, POT = 0.005, 1500.0, 0.01, 15_000.0
T = lambda s: pd.Timestamp(s, tz="UTC")  # noqa: E731


def load(name, key, tcol, volcol):
    d = pd.read_parquet(PUB / f"{name}.parquet").rename(columns={key: "coin"})
    if tcol == "start":
        d["day"] = pd.to_datetime(d["start"], utc=True).dt.normalize()
    else:
        unit = "ms" if d[tcol].max() > 1e11 else "s"
        d["day"] = pd.to_datetime(d[tcol], unit=unit, utc=True).dt.normalize()
    for c in ("o", "h", "l", "c"):
        d[c] = d[c].astype(float)
    d["usd"] = d[volcol].astype(float) * (d["c"] if volcol == "v" else 1.0)
    return d.drop_duplicates(["coin", "day"])


def fills(d, x, window_days, mk, tk, drop_early=False, venue=""):
    start = d["day"].min()
    out = []
    for coin, g in d.groupby("coin"):
        g = g.sort_values("day").reset_index(drop=True)
        first = g["day"].iloc[0]
        if drop_early and first <= start + pd.Timedelta(days=30):
            continue
        prev = g["c"].shift()
        lvl = prev * (1 - x)
        inwin = g["day"] < first + pd.Timedelta(days=window_days)
        hit = inwin & prev.notna() & (g["l"] <= lvl * (1 - THROUGH))
        for i in np.flatnonzero(hit.to_numpy()):
            px = min(float(lvl.iloc[i]), float(g["o"].iloc[i]))
            if not px > 0:
                continue
            out.append({"venue": venue, "coin": coin, "listed": first, "day": g["day"].iloc[i],
                        "ret": float(g["c"].iloc[i]) / px - 1 - mk - tk, "size": min(CAP, VOLS * float(g["usd"].iloc[i]))})
    return pd.DataFrame(out)


def summ(f, label):
    if f.empty:
        print(f"   {label}: no fills")
        return dict(n=0, m=np.nan, t=np.nan, usd=0.0)
    f = f.copy()
    f["pnl"] = f["size"] * np.minimum(1.0, POT / f.groupby("day")["size"].transform("sum")) * f["ret"]
    yrs = max((f["day"].max() - f["day"].min()).days + 1, 30) / 365
    r = f["ret"]
    t = r.mean() / (r.std(ddof=1) / np.sqrt(len(r))) if len(r) > 1 else np.nan
    best = f.groupby("day")["pnl"].sum().idxmax()
    usd = f["pnl"].sum() / yrs
    print(f"   {label}: fills {len(f)} ({f['coin'].nunique()} markets) | mean net {r.mean():+.2%} (median {r.median():+.2%}, t {t:.2f}, "
          f"win {(r > 0).mean():.0%}) | ${usd:,.0f}/yr | without best day ${f[f['day'] != best]['pnl'].sum() / yrs:,.0f}/yr")
    return dict(n=len(f), m=r.mean(), t=t, usd=usd)


def verdict(a, b):
    if a["n"] >= 30 and not (a["m"] > 0.003):
        return "KILL (Stage 1)"
    return ("PASS" if (b["n"] >= 30 and b["m"] >= 0.003 and b["t"] >= 2 and b["usd"] >= 1000) else "FAIL") + \
        (" (Stage 1 < 30 fills: no kill possible)" if a["n"] < 30 else "")


def main():
    spot = load("fivehigh_hl_spot_1d", "pair", "t", "v")
    print(f"#535 New HL spot tokens, days 1-14 ({spot['coin'].nunique()} pairs, {spot['day'].min().date()}..{spot['day'].max().date()})")
    for j, x in enumerate((0.20, 0.10, 0.30)):
        f = fills(spot, x, 14, 0.0004, 0.0007)
        print(f"  X {x:.0%}{' (primary)' if j == 0 else ' (context)'}")
        a = summ(f[f["listed"] < T("2025-07-01")] if not f.empty else f, "Stage 1 (first traded before 2025-07-01)")
        b = summ(f[f["listed"] >= T("2025-07-01")] if not f.empty else f, "Stage 2 (2025-07-01 onward)")
        if j == 0:
            print(f"   VERDICT {verdict(a, b)}")
    aster = load("wickscale_aster_1d", "coin", "t", "qvol")
    dydx = load("wickscale_dydx_1d", "coin", "start", "usdvol")
    print(f"\n#536 New Aster/dYdX perps, days 1-30 (Aster {aster['coin'].nunique()} markets from {aster['day'].min().date()}, "
          f"dYdX {dydx['coin'].nunique()} from {dydx['day'].min().date()})")
    for j, x in enumerate((0.15, 0.10, 0.20)):
        f = pd.concat([fills(aster, x, 30, 0.0002, 0.0005, True, "aster"), fills(dydx, x, 30, 0.0002, 0.0005, True, "dydx")],
                      ignore_index=True)
        print(f"  X {x:.0%}{' (primary)' if j == 0 else ' (context)'}")
        a = summ(f[f["listed"] < T("2025-01-01")] if not f.empty else f, "Stage 1 (listed before 2025)")
        b = summ(f[f["listed"] >= T("2025-01-01")] if not f.empty else f, "Stage 2 (listed 2025 onward)")
        if j == 0:
            for v in ("aster", "dydx"):
                summ(f[(f["venue"] == v) & (f["listed"] >= T("2025-01-01"))], f"   Stage 2 {v} only")
            print(f"   VERDICT {verdict(a, b)}")


if __name__ == "__main__":
    main()

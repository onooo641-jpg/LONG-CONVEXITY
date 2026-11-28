"""Batch NF2 #537-#540: new perps on Aster/dYdX (docs/PREREG_BATCH_NF2_20261128.md).

    uv run python -m scripts.batch_nf2_20261128 | tee docs/jx_runs/batch_nf2_20261128.txt
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from scripts.batch_nf_20261128 import load

COST, SIZE = 0.001, 1500.0
SPLIT = pd.Timestamp("2025-01-01", tz="UTC")


def markets(d, venue):
    start = d["day"].min()
    for coin, g in d.groupby("coin"):
        g = g.sort_values("day").reset_index(drop=True)
        if g["day"].iloc[0] <= start + pd.Timedelta(days=30):
            continue
        yield venue, coin, g


def trades(all_markets):
    out = {537: [], 538: [], 539: [], 540: []}
    for venue, coin, g in all_markets:
        first = g["day"].iloc[0]
        c, usd = g["c"].to_numpy(), g["usd"].to_numpy()
        rec = lambda k, i, j, side: out[k].append(dict(venue=venue, coin=coin, listed=first, day=g["day"].iloc[i],  # noqa: E731
                                                       ret=side * (c[j] / c[i] - 1) - COST))
        if len(g) > 14:
            rec(537, 0, 14, -1)
        for k, cond, side in ((538, lambda r: r >= 0.5, -1), (539, lambda r: r <= -0.3, +1)):
            busy = -1
            for i in range(1, min(len(g), 60)):
                if i <= busy or i + 3 >= len(g) or not c[i - 1] > 0:
                    continue
                if cond(c[i] / c[i - 1] - 1):
                    rec(k, i, i + 3, side)
                    busy = i + 3
        if len(g) > 21 and usd[0] > 0 and usd[6] < 0.2 * usd[0]:
            rec(540, 6, 20, -1)
    return {k: pd.DataFrame(v) for k, v in out.items()}


def summ(t, label):
    if t.empty:
        print(f"   {label}: no trades")
        return dict(n=0, m=np.nan, t=np.nan, ex3=np.nan)
    r = t["ret"]
    tt = r.mean() / (r.std(ddof=1) / np.sqrt(len(r))) if len(r) > 1 else np.nan
    ex3 = r.sort_values().iloc[:-3].sum() if len(r) > 3 else np.nan
    print(f"   {label}: trades {len(r)} | mean net {r.mean():+.2%} (median {r.median():+.2%}, t {tt:.2f}, win {(r > 0).mean():.0%}) | "
          f"sum without the 3 best trades {ex3:+.2f} (in units of trade size)")
    return dict(n=len(r), m=r.mean(), t=tt, ex3=ex3)


NAMES = {537: "Post-listing fade (short day 1 -> day 15)", 538: "Pump exhaustion (short after a +50% close, 3 days)",
         539: "Crash bounce (long after a -30% close, 3 days)", 540: "Dying-listing bleed (short day 7 -> day 21 if volume < 20% of day 1)"}


def main():
    aster = load("wickscale_aster_1d", "coin", "t", "qvol")
    dydx = load("wickscale_dydx_1d", "coin", "start", "usdvol")
    T = trades(list(markets(aster, "aster")) + list(markets(dydx, "dydx")))
    yrs = (max(aster["day"].max(), dydx["day"].max()) - SPLIT).days / 365.25
    for k, name in NAMES.items():
        t = T[k]
        print(f"#{k} {name}")
        a = summ(t[t["listed"] < SPLIT] if not t.empty else t, "Stage 1 (listed before 2025)")
        b = summ(t[t["listed"] >= SPLIT] if not t.empty else t, "Stage 2 (listed 2025 onward)")
        for v in ("aster", "dydx"):
            if not t.empty:
                summ(t[(t["listed"] >= SPLIT) & (t["venue"] == v)], f"   Stage 2 {v} only")
        if a["n"] >= 20 and not (a["m"] > 0):
            v = "KILL (Stage 1)"
        else:
            ok = b["n"] >= 30 and b["m"] >= 0.01 and b["t"] >= 2 and b["ex3"] > 0
            v = ("PASS" if ok else "FAIL") + (" (Stage 1 < 20 trades: no kill possible)" if a["n"] < 20 else "")
        usd = (b["m"] * SIZE * b["n"] / yrs) if b["n"] else 0.0
        print(f"   VERDICT {v} | $/yr at $1,500 per trade: ${usd:,.0f}\n")


if __name__ == "__main__":
    main()

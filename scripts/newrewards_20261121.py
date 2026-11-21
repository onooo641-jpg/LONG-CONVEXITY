"""New reward programmes in their first 30 days (docs/PREREG_NEWREWARDS_20261121.md, #207).

    uv run python scripts/newrewards_20261121.py | tee docs/jx_runs/newrewards_20261121.txt
"""
from __future__ import annotations

import sys

import numpy as np
import pandas as pd

LO, HI = pd.Timestamp("2024-11-01", tz="UTC"), pd.Timestamp("2026-11-01", tz="UTC")
MID, PILOT = pd.Timestamp("2025-11-01", tz="UTC"), pd.Timestamp("2026-08-01", tz="UTC")
SIZE, FEE, MAXPOS, HOLD, STRESS, BAR, KILL = 10_000, 5.0, 5, 30, 0.20, 8.0, 4.0
AAVE = "aa70268e-4b52-42bf-a116-608b370f9501"


def main() -> int:
    ch = pd.read_parquet("data/public/fallback_stable_charts.parquet")
    ch["day"] = ch["ts"].dt.floor("D")
    ch = ch.drop_duplicates(["pool", "day"]).sort_values(["pool", "day"])
    ch["rw"] = ch["apyReward"].fillna(0)
    y = (ch["apyBase"].fillna(0) + 0.9 * ch["rw"]).clip(upper=1000)
    ch["y"] = y
    Y = ch.pivot(index="day", columns="pool", values="y")
    T = ch.pivot(index="day", columns="pool", values="tvlUsd").ffill(limit=3)
    days = pd.date_range(LO, HI - pd.Timedelta(days=1), freq="D", tz="UTC")
    base = (Y[AAVE].reindex(days).ffill().fillna(0) if AAVE in Y else pd.Series(0.0, index=days)) / 100 / 365

    # events
    ev = []
    for p, g in ch.groupby("pool"):
        g = g.set_index("day")
        rw = g["rw"]
        for i, (d, r) in enumerate(rw.items()):
            if r <= 0 or r > 1000 or g.at[d, "tvlUsd"] < 1e6 or not (LO - pd.Timedelta(days=1) <= d < HI - pd.Timedelta(days=1)):
                continue
            prev = rw[(rw.index < d) & (rw.index >= d - pd.Timedelta(days=14))]
            first = i == 0
            if first or (len(prev) > 0 and (prev <= 0).all()) or (len(prev) == 0 and i > 0):
                ev.append((d + pd.Timedelta(days=1), p, r))
    ev.sort()
    print(f"events (reward starts, TVL >= $1M) in window: {len(ev)}")

    held, daily, taken, stressed = {}, [], [], 0
    evi = 0
    for d in days:
        cost = 0.0
        for p in [p for p, (s, alive) in held.items() if (d - s).days >= HOLD or not alive]:
            held.pop(p)
            cost += FEE / SIZE
        while evi < len(ev) and ev[evi][0] <= d:
            s, p, r = ev[evi]
            evi += 1
            if s == d and len(held) < MAXPOS and p not in held:
                held[p] = (d, True)
                taken.append((d, p, r))
                cost += FEE / SIZE
        rets = []
        for p, (s, alive) in list(held.items()):
            t7 = T.loc[d - pd.Timedelta(days=7):d, p]
            if len(t7) > 1 and t7.iloc[-1] < 0.5 * t7.max():
                rets.append(-STRESS)
                held[p] = (s, False)
                stressed += 1
                continue
            v = Y.at[d, p] if d in Y.index else np.nan
            rets.append((v if pd.notna(v) else 0.0) / 100 / 365)
        idle = (MAXPOS - len(rets)) / MAXPOS
        r = (sum(rets) / MAXPOS) + idle * base.get(d, 0.0) - cost
        daily.append((d, r))
    s = pd.Series(dict(daily))
    ann = lambda x: float(x.mean() * 365 * 100)  # noqa: E731
    tk = pd.DataFrame(taken, columns=["d", "pool", "reward_at_start"])
    n1, n2 = int((tk.d < MID).sum()), int((tk.d >= MID).sum())
    pilot = ann(s[s.index >= PILOT])
    print(f"events taken: {len(tk)} (half 1 {n1}, half 2 {n2}); stress hits {stressed} ({stressed / max(len(tk), 1):.0%} of taken)")
    print(f"median reward APR at start of taken events {tk.reward_at_start.median():.1f}%")
    print(f"Stage 1 (2026-08..10): {pilot:.2f}%/yr -> {'KILL' if pilot < KILL else 'continue'}")
    if pilot < KILL:
        print("VERDICT: FAIL (Stage 1)")
        return 0
    h1, h2 = ann(s[s.index < MID]), ann(s[s.index >= MID])
    mon = s.groupby(s.index.strftime("%Y-%m")).sum() * 100
    print(f"half 1 {h1:.2f}%/yr, half 2 {h2:.2f}%/yr, whole {ann(s):.2f}%/yr; baseline {ann(base[base.index < MID]):.2f}% / "
          f"{ann(base[base.index >= MID]):.2f}%; worst month {mon.min():.2f}%; months negative {(mon < 0).sum()}")
    print(f"$ per year: ${ann(s) * 100:,.0f} on $10K, ${ann(s) * 400:,.0f} on $40K (Topstep slot $4,097/yr)")
    ok = h1 >= BAR and h2 >= BAR and n1 >= 30 and n2 >= 30
    print(f"VERDICT: {'PASS' if ok else 'FAIL'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

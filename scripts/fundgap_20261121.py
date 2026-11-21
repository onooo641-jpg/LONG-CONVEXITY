"""Cross-venue funding gaps (docs/PREREG_FUNDGAP_20261121.md, #208).

    uv run python scripts/fundgap_20261121.py | tee docs/jx_runs/fundgap_20261121.txt
"""
from __future__ import annotations

import sys

import numpy as np
import pandas as pd

LO, HI = pd.Timestamp("2024-11-01", tz="UTC"), pd.Timestamp("2026-11-01", tz="UTC")
MID, PILOT = pd.Timestamp("2025-11-01", tz="UTC"), pd.Timestamp("2026-08-01", tz="UTC")
ENTRY, FEE_SIDE, SLOTS, LEV, BAR, KILL = 15.0, 0.001, 5, 3.0, 8.0, 4.0
TESTED = [("hl", "dydx"), ("hl", "aevo"), ("dydx", "aevo")]


def hourly(df):
    """dict (venue, coin) -> hourly rate Series on the full hour grid."""
    grid = pd.date_range(LO - pd.Timedelta(days=2), HI, freq="h", tz="UTC")
    out = {}
    for (v, c), g in df.groupby(["venue", "coin"]):
        s = g.assign(ts=pd.to_datetime(g["t"], unit="s", utc=True).dt.floor("h")).groupby("ts")["rate"].mean().sort_index()
        if v == "gate":  # rate per settlement interval -> per hour, spread over the interval that ends at each settlement
            iv = s.index.to_series().diff().dt.total_seconds().div(3600).fillna(8).clip(lower=1)
            s = (s / iv).reindex(grid).bfill(limit=8)
        else:
            s = s.reindex(grid)
        out[(v, c)] = s
    return out


def run(H, pairs):
    coins = sorted({c for (_, c) in H})
    days = pd.date_range(LO, HI - pd.Timedelta(days=1), freq="D", tz="UTC")
    open_pos, daily, trips = {}, [], []
    for d in days:
        pnl = 0.0
        prev = slice(d - pd.Timedelta(hours=24), d - pd.Timedelta(hours=1))
        today = slice(d, d + pd.Timedelta(hours=23))
        # close
        for k in list(open_pos):
            a, b, c = k
            sig = (H[(a, c)][prev] - H[(b, c)][prev]).mean() * 24 * 365 * 100
            if not np.isfinite(sig) or np.sign(sig) != open_pos[k]["dir"]:
                pnl -= FEE_SIDE * 2
                trips.append((open_pos[k]["open"], d))
                open_pos.pop(k)
        # open
        cands = []
        for a, b in pairs:
            for c in coins:
                if (a, c) not in H or (b, c) not in H or (a, b, c) in open_pos:
                    continue
                sig = (H[(a, c)][prev] - H[(b, c)][prev]).mean() * 24 * 365 * 100
                if np.isfinite(sig) and abs(sig) >= ENTRY:
                    cands.append((-abs(sig), a, b, c, np.sign(sig)))
        for _, a, b, c, sgn in sorted(cands):
            if len(open_pos) >= SLOTS:
                break
            open_pos[(a, b, c)] = {"dir": sgn, "open": d}
            pnl -= FEE_SIDE * 2
        # earn today's funding difference (missing hours earn 0)
        for (a, b, c), p in open_pos.items():
            pnl += p["dir"] * (H[(a, c)][today] - H[(b, c)][today]).fillna(0).sum()
        daily.append((d, pnl / (SLOTS * 2 / LEV), len(open_pos)))
    s = pd.DataFrame(daily, columns=["d", "r", "n"]).set_index("d")
    return s, trips


def report(name, s, trips, verdict=True):
    ann = lambda x: float(x.mean() * 365 * 100)  # noqa: E731
    t1 = sum(1 for o, _ in trips if o < MID)
    t2 = len(trips) - t1
    pilot = ann(s.r[s.index >= PILOT])
    h1, h2 = ann(s.r[s.index < MID]), ann(s.r[s.index >= MID])
    mon = s.r.groupby(s.index.strftime("%Y-%m")).sum() * 100
    inv = float((s.n > 0).mean())
    print(f"{name}: round trips {t1} / {t2}; invested {inv:.0%} of days; Stage 1 {pilot:.2f}%/yr; halves {h1:.2f}% / {h2:.2f}% on capital; "
          f"worst month {mon.min():.2f}%; $ per year ${ann(s.r) * 100:,.0f} on $10K, ${ann(s.r) * 400:,.0f} on $40K")
    if verdict:
        if pilot < KILL:
            print(f"  VERDICT: FAIL (Stage 1 {pilot:.2f} < {KILL})")
        else:
            ok = h1 >= BAR and h2 >= BAR and t1 >= 20 and t2 >= 20
            print(f"  VERDICT: {'PASS' if ok else 'FAIL'}")


def main() -> int:
    df = pd.read_parquet("data/public/fundgap_funding.parquet")
    print("rows per venue:", df.groupby("venue").size().to_dict())
    H = hourly(df)
    s, trips = run(H, TESTED)
    report("TESTED: HL/dYdX/Aevo pooled", s, trips)
    for p in TESTED:
        report(f"  pair {p[0]}-{p[1]} alone", *run(H, [p]), verdict=False)
    report("NOT ELIGIBLE (Malaysia): HL-Gate", *run(H, [("hl", "gate")]), verdict=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())

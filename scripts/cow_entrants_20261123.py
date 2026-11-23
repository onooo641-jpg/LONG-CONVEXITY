"""#364 CoW new-solver first-year earnings (docs/PREREG_COW_ENTRANTS_20261123.md).

    uv run python -m scripts.cow_entrants_20261123 | tee docs/jx_runs/cow_entrants_20261123.txt
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

PUB = Path(__file__).resolve().parent.parent / "data" / "public"
BAR, FEE = 15_000.0, 0.85


def main():
    meta = json.loads((PUB / "solverrelay_cow_meta.json").read_text())
    print(f"===== #364 CoW new-solver first-year earnings (source {meta.get('source')}, complete {meta.get('complete')})")
    df = pd.read_parquet(PUB / "solverrelay_cow.parquet")
    pts = meta["cow_price"]
    px = pd.Series({pd.Timestamp(int(x["timestamp"]), unit="s", tz="UTC").round("D"): float(x["price"]) for x in pts}).sort_index()
    px = px[~px.index.duplicated()]
    df["day"] = pd.to_datetime(df["ts"], unit="s", utc=True).dt.normalize()
    df["usd"] = df["cow"] * df["day"].map(lambda d: float(px.asof(d)))
    df["week"] = df["day"].dt.to_period("W-MON")
    first = df.groupby("to")["day"].min()
    rows = []
    for addr, f0 in first.items():
        if not (pd.Timestamp("2024-03-01", tz="UTC") <= f0 <= pd.Timestamp("2025-10-31", tz="UTC")):
            continue
        d = df[(df["to"] == addr) & (df["day"] >= f0) & (df["day"] < f0 + pd.Timedelta(days=365))]
        rows.append({"to": addr, "first": f0, "cohort": "A" if f0.year == 2024 else "B", "weeks": d["week"].nunique(),
                     "net": d["usd"].sum() * FEE})
    e = pd.DataFrame(rows)
    print(f"  incumbents (first paid before 2024-03-01): {int((first < pd.Timestamp('2024-03-01', tz='UTC')).sum())}; "
          f"entrants 2024-03-01..2025-10-31: {len(e)}")
    out = {}
    for c in ("A", "B"):
        g = e[e["cohort"] == c]
        a = g[g["weeks"] >= 4].sort_values("net", ascending=False)
        share = float((a["net"] >= BAR).mean()) if len(a) else 0.0
        med = float(a["net"].median()) if len(a) else 0.0
        out[c] = (share, med, len(a))
        q = a["net"].quantile([0.25, 0.5, 0.75]).round(0).tolist() if len(a) else []
        print(f"  cohort {c}: entrants {len(g)}, active (>= 4 weeks) {len(a)}; first-year net after 15% fee: quartiles {q}; "
              f">= $15K: {share:.0%}; >= $50K: {float((a['net'] >= 50_000).mean()) if len(a) else 0:.0%}")
        for k, r in enumerate(a.itertuples(), 1):
            print(f"    {k:2d}. {r.to}  first {r.first.date()}  weeks {r.weeks:2d}  ${r.net:>11,.0f}")
    s1 = out["A"][0]
    print(f"  STAGE 1 (cohort A share >= $15K, bar 25%): {s1:.0%} -> {'KILL' if s1 < 0.25 else 'survives (kill-only)'}")
    ok = s1 >= 0.25 and all(out[c][1] >= BAR for c in ("A", "B"))
    print(f"  STAGE 2 (median active entrant >= $15K in both cohorts: A ${out['A'][1]:,.0f}, B ${out['B'][1]:,.0f}): "
          f"{'worth a no-money shadow-solver build test' if ok else 'FAIL'}"
          + ("" if s1 >= 0.25 else " (Stage 1 already killed; context only)"))


if __name__ == "__main__":
    main()

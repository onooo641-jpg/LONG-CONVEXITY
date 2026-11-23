"""#364 unregistered sensitivity: are 'entrants' existing solvers moving to a new payout address?

    uv run python -m scripts.cow_entrants_check_20261123 | tee docs/jx_runs/cow_entrants_check_20261123.txt
An entrant is flagged as a likely migration if (a) 3+ addresses received their first payout on the same day, or (b) an address paid in
>= 4 weeks received its last payout within 21 days before the entrant's first payout. Context only (not part of the registered rule).
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

PUB = Path(__file__).resolve().parent.parent / "data" / "public"


def main():
    meta = json.loads((PUB / "solverrelay_cow_meta.json").read_text())
    df = pd.read_parquet(PUB / "solverrelay_cow.parquet")
    px = pd.Series({pd.Timestamp(int(x["timestamp"]), unit="s", tz="UTC").round("D"): float(x["price"]) for x in meta["cow_price"]})
    px = px[~px.index.duplicated()].sort_index()
    df["day"] = pd.to_datetime(df["ts"], unit="s", utc=True).dt.normalize()
    df["usd"] = df["cow"] * df["day"].map(lambda d: float(px.asof(d)))
    df["week"] = df["day"].dt.to_period("W-MON")
    g = df.groupby("to").agg(first=("day", "min"), last=("day", "max"), weeks=("week", "nunique"))
    same_day = g.groupby("first").size()
    print("===== #364 sensitivity (unregistered): likely payout-address migrations")
    print("  days on which 3+ addresses got their first payout: "
          + ", ".join(f"{d.date()} ({n})" for d, n in same_day[same_day >= 3].items()))
    leavers = g[(g["weeks"] >= 4) & (g["last"] < df["day"].max() - pd.Timedelta(days=21))]
    rows = []
    for addr, r in g.iterrows():
        f0 = r["first"]
        if not (pd.Timestamp("2024-03-01", tz="UTC") <= f0 <= pd.Timestamp("2025-10-31", tz="UTC")):
            continue
        d = df[(df["to"] == addr) & (df["day"] >= f0) & (df["day"] < f0 + pd.Timedelta(days=365))]
        if d["week"].nunique() < 4:
            continue
        lv = leavers[(leavers["last"] < f0) & (leavers["last"] >= f0 - pd.Timedelta(days=21))]
        rows.append({"to": addr, "first": f0, "cohort": "A" if f0.year == 2024 else "B", "net": d["usd"].sum() * 0.85,
                     "cluster": same_day[f0] >= 3, "leaver": len(lv) > 0})
    e = pd.DataFrame(rows)
    e["flag"] = e["cluster"] | e["leaver"]
    for c in ("A", "B"):
        x = e[e["cohort"] == c]
        y = x[~x["flag"]]
        print(f"  cohort {c}: active entrants {len(x)}, flagged as likely migrations {int(x['flag'].sum())} "
              f"(same-day cluster {int(x['cluster'].sum())}, follows a leaver {int(x['leaver'].sum())}); unflagged {len(y)}: "
              f"median first-year net ${float(y['net'].median()) if len(y) else 0:,.0f}, >= $15K {float((y['net'] >= 15000).mean()) if len(y) else 0:.0%}")
        for r in y.sort_values("net", ascending=False).itertuples():
            print(f"     {r.to}  first {r.first.date()}  ${r.net:>11,.0f}")


if __name__ == "__main__":
    main()

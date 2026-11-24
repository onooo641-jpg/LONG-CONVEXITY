"""#365 CoW solver gate tests, Stage 1 (docs/PREREG_COW_GATE_20261124.md).

    uv run python -m scripts.cow_gate_20261124 | tee docs/jx_runs/cow_gate_20261124.txt
Reads data/public/solverrelay_cow.parquet + solverrelay_cow_meta.json (as #361/#364) and, when fetched, cow365_competition.parquet,
cow365_inflows.parquet, cow365_meta.json (Actions job cow365).
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

PUB = Path(__file__).resolve().parent.parent / "data" / "public"
BAR, FEE = 15_000.0, 0.85
TS = lambda s: pd.Timestamp(s, tz="UTC")  # noqa: E731
END = TS("2026-10-31")


def load():
    meta = json.loads((PUB / "solverrelay_cow_meta.json").read_text())
    df = pd.read_parquet(PUB / "solverrelay_cow.parquet")
    px = pd.Series({TS(pd.Timestamp(int(x["timestamp"]), unit="s")).round("D"): float(x["price"]) for x in meta["cow_price"]})
    px = px[~px.index.duplicated()].sort_index()
    df["day"] = pd.to_datetime(df["ts"], unit="s", utc=True).dt.normalize()
    df["usd"] = df["cow"] * df["day"].map(lambda d: float(px.asof(d)))
    df["week"] = df["day"].dt.to_period("W-MON")
    return df


def flags(df):
    g = df.groupby("to").agg(first=("day", "min"), last=("day", "max"), weeks=("week", "nunique"))
    same_day = g.groupby("first").size()
    leavers = g[(g["weeks"] >= 4) & (g["last"] < df["day"].max() - pd.Timedelta(days=21))]
    g["cluster"] = g["first"].map(same_day) >= 3
    g["leaver"] = [bool(((leavers["last"] < f) & (leavers["last"] >= f - pd.Timedelta(days=21))).any()) for f in g["first"]]
    g["flag"] = g["cluster"] | g["leaver"]
    return g


def window(df, addr, a, b):
    return df[(df["to"] == addr) & (df["day"] >= a) & (df["day"] <= b)]


def main():
    print("===== #365 CoW solver gate tests, Stage 1 (Stage 0 desk check: see the pre-registration file)")
    df = load()
    g = flags(df)
    kills = []

    # (a) 2026 newcomers
    print("  (a) 2026 newcomers: genuine entrants first paid 2025-11-01..2026-08-31, >= 4 weeks paid, annualised to 2026-10-31 (x 0.85)")
    cand = g[(g["first"] >= TS("2025-11-01")) & (g["first"] <= TS("2026-08-31"))]
    rows = []
    for addr, r in cand.iterrows():
        d = window(df, addr, r["first"], END)
        days = (END - r["first"]).days + 1
        rows.append({"to": addr, "first": r["first"], "weeks": d["week"].nunique(), "flag": r["flag"], "cluster": r["cluster"],
                     "leaver": r["leaver"], "ann": d["usd"].sum() * FEE * 365 / days})
    a = pd.DataFrame(rows)
    print(f"      first paid in the window: {len(a)}; flagged as likely migrations: {int(a['flag'].sum()) if len(a) else 0}")
    for r in a.sort_values("ann", ascending=False).itertuples():
        tag = "migration?" if r.flag else ("<4 weeks" if r.weeks < 4 else "GENUINE")
        print(f"      {r.to}  first {r.first.date()}  weeks {r.weeks:2d}  ${r.ann:>11,.0f}/yr  {tag}")
    ga = a[(~a["flag"]) & (a["weeks"] >= 4)] if len(a) else a
    if len(ga) >= 3:
        med = float(ga["ann"].median())
        ok = med >= BAR
        print(f"      genuine active 2026 entrants {len(ga)}; median ${med:,.0f}/yr; >= $15K {float((ga['ann'] >= BAR).mean()):.0%} -> "
              f"{'pass' if ok else 'KILL'}")
        if not ok:
            kills.append("a")
    else:
        print(f"      genuine active 2026 entrants {len(ga)} (< 3): not enough 2026 entrants (not a kill by itself)")

    # (b) persistence of 2024-25 genuine entrants
    print("  (b) do newcomers last? #364 genuine active entrants (first paid 2024-03-01..2025-10-31), 2026-01-01..10-31 annualised (x 0.85)")
    rows = []
    for addr, r in g[(g["first"] >= TS("2024-03-01")) & (g["first"] <= TS("2025-10-31")) & (~g["flag"])].iterrows():
        y1 = window(df, addr, r["first"], r["first"] + pd.Timedelta(days=364))
        if y1["week"].nunique() < 4:
            continue
        d26 = window(df, addr, TS("2026-01-01"), END)
        rows.append({"to": addr, "first": r["first"], "y1": y1["usd"].sum() * FEE, "y26": d26["usd"].sum() * FEE * 365 / 304,
                     "last": r["last"]})
    b = pd.DataFrame(rows)
    for r in b.sort_values("y26", ascending=False).itertuples():
        print(f"      {r.to}  first {r.first.date()}  first-year ${r.y1:>11,.0f}  2026 ${r.y26:>11,.0f}/yr  last paid {r.last.date()}")
    sh = float((b["y26"] >= BAR).mean()) if len(b) else 0.0
    ok = sh >= 0.30
    print(f"      {len(b)} entrants; share earning >= $15K/yr in 2026: {sh:.0%} (bar 30%) -> {'pass' if ok else 'KILL'}")
    if not ok:
        kills.append("b")

    # (c) reward pool trend
    print("  (c) reward pool: USD paid by quarter (COW in brackets); top recipient's share by year")
    q = df[df["day"] <= END].groupby(df["day"].dt.to_period("Q")).agg(usd=("usd", "sum"), cow=("cow", "sum"), n=("to", "nunique"))
    for p, r in q.iterrows():
        print(f"      {p}: ${r['usd']:>12,.0f}  ({r['cow']:>12,.0f} COW)  recipients {int(r['n'])}")
    for y in (2024, 2025, 2026):
        d = df[(df["day"].dt.year == y) & (df["day"] <= END)]
        t = d.groupby("to")["usd"].sum().sort_values(ascending=False)
        print(f"      {y}: total ${t.sum():,.0f}; top 1 {t.iloc[0] / t.sum():.0%}; top 5 {t.head(5).sum() / t.sum():.0%}")
    t25 = df[df["day"].dt.year == 2025]["usd"].sum()
    h2 = df[(df["day"] >= TS("2026-05-01")) & (df["day"] <= END)]["usd"].sum() * 365 / 184
    ratio = h2 / t25
    print(f"      2026-05..10 annualised ${h2:,.0f} vs 2025 ${t25:,.0f}: {ratio:.0%} (bar 50%) -> {'pass' if ratio >= 0.5 else 'KILL'}")
    if ratio < 0.5:
        kills.append("c")

    # (d) live competition
    print("  (d) live competition (CoW solver-competition API sample, ~30 days per network)")
    cf = PUB / "cow365_competition.parquet"
    pending = not cf.exists()
    if pending:
        print("      data not fetched yet: (d) pending")
    else:
        cm = json.loads((PUB / "cow365_meta.json").read_text())
        c = pd.read_parquet(cf)
        all_closed = True
        n_nets = 0
        for net, m in cm["nets"].items():
            x = c[c["net"] == net] if len(c) else c
            if not len(x):
                print(f"      {net}: no data ({m.get('status') or 'no solutions'})")
                continue
            n_nets += 1
            x = x.copy()
            x["who"] = x["solver"].fillna(x["solver_addr"]).astype(str)
            w = x[x["winner"] == True]  # noqa: E712
            wins = w.groupby("who")["auction"].nunique().sort_values(ascending=False)
            tot = wins.sum()
            top3 = wins.head(3).sum() / tot if tot else np.nan
            out5 = wins.iloc[5:].sum() / tot if tot else np.nan
            print(f"      {net}: auctions {x['auction'].nunique()}, with a winner {w['auction'].nunique()}; solvers bidding {x['who'].nunique()}; "
                  f"distinct winners {len(wins)}; top-3 win share {top3:.1%}; outside top 5 {out5:.1%}; top winners "
                  + ", ".join(f"{k} {v}" for k, v in wins.head(6).items()))
            if tot and top3 < 0.95:
                all_closed = False
        if n_nets == 0:
            pending = True
            print("      no network returned data: (d) not measurable")
        elif all_closed:
            kills.append("d")
            print("      every network: top 3 win >= 95% -> KILL")
        else:
            print("      at least one network with top-3 share < 95% -> pass")

    # (e) repayments into the Safe
    print("  (e) context: COW repaid into the Payouts Safe since 2024-01-01")
    inf = PUB / "cow365_inflows.parquet"
    if inf.exists():
        i = pd.read_parquet(inf)
        if len(i):
            by = i.groupby("frm")["cow"].sum().sort_values(ascending=False)
            known = set(df["to"])
            print(f"      transfers {len(i)}, COW {i['cow'].sum():,.0f}; from payout recipients: {by[by.index.isin(known)].sum():,.0f} COW "
                  f"from {int(by.index.isin(known).sum())} addresses; largest senders: "
                  + ", ".join(f"{k[:10]} {v:,.0f}" for k, v in by.head(5).items()))
        else:
            print("      none")
    else:
        print("      data not fetched yet")

    if kills:
        print(f"  STAGE 1 VERDICT: KILL ({', '.join(kills)})")
    elif pending:
        print("  STAGE 1 VERDICT: incomplete ((d) pending); no kill so far")
    else:
        print("  STAGE 1 VERDICT: survives (kill-only) -> Stage 2 (shadow or local test of a real solver) is the next and only pass route")


if __name__ == "__main__":
    main()

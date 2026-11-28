"""Batch NF12 #580-#583: TSE daily price limits and retail margin calls (docs/PREREG_BATCH_NF12_20261128.md).

    uv run python -m scripts.batch_nf12_20261128 | tee docs/jx_runs/batch_nf12_20261128.txt
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

PUB = Path(__file__).resolve().parent.parent / "data" / "public"
COST, CAP, SHARE, POT, FX, MAXLOT, MINTURN = 0.0025, 1500.0, 0.01, 15_000.0, 150.0, 3000.0, 20e6
S1 = (pd.Timestamp("2015-01-01"), pd.Timestamp("2020-12-31"))
S2 = (pd.Timestamp("2021-01-01"), pd.Timestamp("2026-11-27"))
BANDS = [(100, 30), (200, 50), (500, 80), (700, 100), (1000, 150), (1500, 300), (2000, 400), (3000, 500), (5000, 700),
         (7000, 1000), (10000, 1500), (15000, 3000), (20000, 4000), (30000, 5000), (50000, 7000), (70000, 10000),
         (100000, 15000)]


def limit(pc):
    out = np.full(len(pc), 30000.0)
    for hi, lim in reversed(BANDS):
        out = np.where(pc < hi, lim, out)
    return out


def load():
    df = pd.concat([pd.read_parquet(PUB / f"batchnf12_px_{k}.parquet") for k in "abcd"], ignore_index=True)
    sp = pd.read_parquet(PUB / "batchnf12_splits.parquet")
    df["day"] = pd.to_datetime(df["t"], unit="s", utc=True).dt.tz_convert("Asia/Tokyo").dt.tz_localize(None).dt.normalize()
    df = df.drop_duplicates(["sym", "day"]).sort_values(["sym", "day"]).reset_index(drop=True)
    for c in ("o", "h", "l", "c", "v"):
        df[c] = df[c].astype("float64")
    # raw price = split-adjusted price x product of split ratios after that day
    df["fac"] = 1.0
    sp["sday"] = pd.to_datetime(sp["t"], unit="s", utc=True).dt.tz_convert("Asia/Tokyo").dt.tz_localize(None).dt.normalize()
    for sym, g in sp[sp["num"] > 0].groupby("sym"):
        m = (df["sym"] == sym).to_numpy()
        days = df.loc[m, "day"].to_numpy()
        f = np.ones(m.sum())
        for _, e in g.iterrows():
            f *= np.where(days < np.datetime64(e["sday"]), e["num"] / e["den"], 1.0)
        df.loc[m, "fac"] = f
    return df, sp


def features(df):
    g = df.groupby("sym", sort=False)
    df["pc"] = g["c"].shift()
    df["raw_c"] = df["c"] * df["fac"]
    df["raw_pc"] = g["raw_c"].shift()
    df["turn"] = df["c"] * df["v"]
    df["med20"] = g["turn"].transform(lambda s: s.rolling(20).median().shift())
    df["ld"] = ((df["c"] == df["l"]) & (df["raw_c"] <= df["raw_pc"] - 0.95 * limit(df["raw_pc"].fillna(0).to_numpy()))
                & (df["v"] > 0) & df["raw_pc"].notna())
    df["ld1"] = g["ld"].shift(1, fill_value=False).astype(bool)
    df["ld2"] = g["ld"].shift(2, fill_value=False).astype(bool)
    df["c_n1"], df["o_n1"], df["c_n2"] = g["c"].shift(-1), g["o"].shift(-1), g["c"].shift(-2)
    df["c_p1"] = g["c"].shift(1)
    df["sig"] = g["c"].transform(lambda s: s.pct_change().rolling(30).std().shift())
    df["age"] = g.cumcount()
    df["liq"] = (df["med20"] >= MINTURN)
    df["lot_ok"] = df["raw_c"] * 100 / FX <= MAXLOT
    df["size"] = np.minimum(CAP, SHARE * df["turn"] / FX)
    return df


def with_pnl(f):
    f = f.copy()
    f["pnl"] = f["size"] * np.minimum(1.0, POT / f.groupby("day")["size"].transform("sum")) * f["ret"]
    return f


def summ(f, w):
    g = f[(f["day"] >= w[0]) & (f["day"] <= w[1])] if len(f) else f
    if g.empty:
        return dict(n=0)
    yrs = ((min(w[1], g["day"].max()) - w[0]).days + 1) / 365.25
    r = g["ret"]
    daily = g.groupby("day")["pnl"].sum().sort_values()
    return dict(n=len(g), m=r.mean(), t=r.mean() / (r.std(ddof=1) / np.sqrt(len(r))) if len(r) > 1 else np.nan,
                win=(r > 0).mean(), usd=g["pnl"].sum() / yrs, ex3=daily.iloc[:-3].sum() if len(daily) > 3 else np.nan,
                m15=(r - COST).mean(), xs=g["xs"].mean() if "xs" in g else np.nan)


def fmt(label, s):
    if not s.get("n"):
        return f"   {label}: no trades"
    return (f"   {label}: trades {s['n']} | mean net {s['m']:+.2%} (t {s['t']:.2f}, win {s['win']:.0%}) | ${s['usd']:,.0f}/yr "
            f"| sum without 3 best days ${s['ex3']:,.0f} | costs x1.5 mean {s['m15']:+.2%} | vs TOPIX {s['xs']:+.2%}")


def verdict(a, b):
    if a.get("n", 0) >= 30 and not (a["m"] > 0):
        return "KILL (Stage 1)"
    ok = b.get("n", 0) >= 30 and b["m"] >= 0.003 and b["t"] >= 2 and b["usd"] >= 3000 and b["ex3"] > 0 and b["m15"] > 0
    return "PASS" if ok else "FAIL"


def by_year(f):
    y = f.groupby(f["day"].dt.year)["ret"].agg(["size", "mean"])
    return "   by year: " + "; ".join(f"{k} n {int(r['size'])} {r['mean']:+.2%}" for k, r in y.iterrows())


def report(num, label, f):
    f = with_pnl(f) if len(f) else pd.DataFrame(columns=["sym", "day", "ret", "xs", "size", "pnl"])
    a, b = summ(f, S1), summ(f, S2)
    print(f"{num} {label}")
    print(fmt("Stage 1 2015-2020", a))
    print(fmt("Stage 2 2021-2026", b))
    if len(f):
        print(by_year(f))
    print(f"   VERDICT {verdict(a, b)}\n")
    return f


def main():
    df, sp = load()
    tpx = df[df["sym"] == "1306.T"].set_index("day")["c"].sort_index()
    df = features(df[df["sym"] != "1306.T"].copy())
    tret = lambda d0, d1: tpx.reindex(d1).to_numpy() / tpx.reindex(d0).to_numpy() - 1  # noqa: E731
    cal = tpx.index
    print(f"TSE equities {df['sym'].nunique()}, rows {len(df):,}, {df['day'].min().date()}..{df['day'].max().date()}; "
          f"split events {len(sp)}; TOPIX ETF days {len(tpx)}\n")
    nxt = pd.Series(cal[1:], index=cal[:-1])

    base = df["liq"] & df["c_n1"].notna()
    for num, label, m in (("#580", "First limit-down close: buy at the limit, sell at the next close", df["ld"] & ~df["ld1"]),
                          ("#581", "Second consecutive limit-down close: buy, sell at the next close", df["ld"] & df["ld1"] & ~df["ld2"])):
        ev = df[m & base]
        lot = ev["lot_ok"].mean() if len(ev) else np.nan
        e = ev[ev["lot_ok"]].copy()
        e["ret"] = e["c_n1"] / e["c"] - 1 - 2 * COST
        e["xs"] = e["ret"] - tret(e["day"], e["day"].map(nxt))
        f = report(num, label + f" (liquid events {len(ev)}, {1 - lot:.0%} skipped for lot size)", e[["sym", "day", "ret", "xs", "size"]])
        if num == "#580":
            o = e.copy()
            o["ret"] = o["o_n1"] / o["c"] - 1 - 2 * COST
            print("   context, exit at the next open:")
            print(fmt("Stage 1", summ(with_pnl(o), S1)))
            print(fmt("Stage 2", summ(with_pnl(o), S2)) + "\n")
        del f

    x = (4 * df["sig"]).clip(0.05, 0.30)
    lvl = df["pc"] * (1 - x)
    hit = df["liq"] & df["lot_ok"] & (df["age"] >= 30) & x.notna() & df["pc"].notna() & (df["l"] <= lvl * (1 - 0.005))
    e = df[hit].copy()
    px = np.minimum(lvl[hit], e["o"])
    e["ret"] = e["c"] / px - 1 - 2 * COST
    e = e[px > 0]
    e["xs"] = e["ret"] - (tpx.reindex(e["day"]).to_numpy() / tpx.shift().reindex(e["day"]).to_numpy() - 1)
    report("#582", "TSE wick bids (4 x sigma30, clipped 5%..30%), exit at the close", e[["sym", "day", "ret", "xs", "size"]])

    drops = tpx.index[(tpx / tpx.shift() - 1) <= -0.03]
    print(f"TOPIX ETF days down >= 3%: {len(drops)} ({', '.join(str(d.date()) for d in drops[:6])}, ...)")
    pos = {d: i for i, d in enumerate(cal)}
    rows = []
    idx = df.set_index(["day", "sym"]).sort_index()
    for d0 in drops:
        i = pos[d0]
        if i < 1 or i + 3 >= len(cal):
            continue
        dm1, d1, d3 = cal[i - 1], cal[i + 1], cal[i + 3]
        try:
            a1 = idx.xs(d1, level="day")
        except KeyError:
            continue
        cm1 = idx["c"].xs(dm1, level="day") if dm1 in idx.index.get_level_values(0) else pd.Series(dtype=float)
        c3 = idx["c"].xs(d3, level="day")
        a1 = a1[a1["liq"] & a1["lot_ok"] & (a1["v"] > 0)].copy()
        a1["r2"] = a1["c"] / cm1.reindex(a1.index) - 1
        a1["c3"] = c3.reindex(a1.index)
        pick = a1.dropna(subset=["r2", "c3"]).nsmallest(10, "r2")
        for sym, r in pick.iterrows():
            rows.append({"sym": sym, "day": d1, "ret": r["c3"] / r["c"] - 1 - 2 * COST, "size": CAP,
                         "xs": r["c3"] / r["c"] - 1 - 2 * COST - (tpx[d3] / tpx[d1] - 1)})
    report("#583", "Margin-call day: day +1 close buy the 10 worst two-day losers, sell at the day +3 close", pd.DataFrame(rows))


if __name__ == "__main__":
    main()

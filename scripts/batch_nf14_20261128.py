"""Batch NF14 #589-#597: wick bids and venue discounts on untested thin perp venues (docs/PREREG_BATCH_NF14_20261128.md).

    uv run python -m scripts.batch_nf14_20261128 | tee docs/jx_runs/batch_nf14_20261128.txt
"""
from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd

PUB = Path(__file__).resolve().parent.parent / "data" / "public"
MK, TK, THROUGH, CAP, SHARE, POT = 0.0002, 0.0005, 0.005, 1500.0, 0.01, 15_000.0
SPLIT, END = pd.Timestamp("2025-07-01", tz="UTC"), pd.Timestamp("2026-11-25", tz="UTC")
VENUES = [("#589", "drift"), ("#590", "bluefin"), ("#591", "apex"), ("#592", "edgex"), ("#593", "extended"), ("#594", "pacifica"),
          ("#595", "backpack")]


def norm(s):
    s = str(s).upper()
    s = re.sub(r"(_USDC_PERP|-PERP|PERP|-USDT|USDT|-USDC|USDC|-USD|USD)$", "", s)
    s = re.sub(r"^(1000000|1000|K)(?=[A-Z])", "", s)
    return s.strip("-_")


def load(v):
    p = PUB / f"batchnf14_{v}_1d.parquet"
    if not p.exists():
        return pd.DataFrame()
    d = pd.read_parquet(p)
    if d.empty:
        return d
    d["day"] = pd.to_datetime(d["t"], unit="ms", utc=True).dt.normalize()
    d = d[(d["day"] <= END) & (d["c"] > 0) & (d["l"] > 0)].drop_duplicates(["coin", "day"]).sort_values(["coin", "day"])
    d["venue"] = v
    return d.reset_index(drop=True)


def wick(d, mode, cost_mult=1.0):
    out = []
    v0 = d["day"].min()
    for coin, g in d.groupby("coin"):
        g = g.reset_index(drop=True)
        prev = g["c"].shift()
        if mode == "vol":
            x = (4 * g["c"].pct_change().rolling(30).std().shift()).clip(0.05, 0.30)
            ok = (g.index >= 30) & x.notna() & prev.notna()
        else:  # new listing, first 30 days
            if g["day"].iloc[0] <= v0 + pd.Timedelta(days=30):
                continue
            x = pd.Series(0.15, index=g.index)
            ok = (g["day"] <= g["day"].iloc[0] + pd.Timedelta(days=29)) & prev.notna()
        lvl = prev * (1 - x)
        hit = ok & (g["l"] <= lvl * (1 - THROUGH))
        for i in np.flatnonzero(hit.to_numpy()):
            px = min(float(lvl.iloc[i]), float(g["o"].iloc[i]))
            if not px > 0:
                continue
            out.append({"venue": g["venue"].iloc[i], "coin": coin, "day": g["day"].iloc[i],
                        "ret": float(g["c"].iloc[i]) / px - 1 - cost_mult * (MK + TK),
                        "size": min(CAP, SHARE * float(g["v_usd"].iloc[i]))})
    return pd.DataFrame(out)


def pnl(f):
    if f.empty:
        return f
    f = f.copy()
    f["pnl"] = f["size"] * np.minimum(1.0, POT / f.groupby("day")["size"].transform("sum")) * f["ret"]
    return f


def summ(f, lo, hi):
    g = f[(f["day"] >= lo) & (f["day"] < hi)] if len(f) else f
    if g.empty:
        return dict(n=0)
    yrs = max((hi - lo).days, 1) / 365.25
    r = g["ret"]
    daily = g.groupby("day")["pnl"].sum().sort_values()
    return dict(n=len(g), m=r.mean(), med=r.median(), t=r.mean() / (r.std(ddof=1) / np.sqrt(len(r))) if len(r) > 1 else np.nan,
                win=(r > 0).mean(), usd=g["pnl"].sum() / yrs, ex1=daily.iloc[:-1].sum() / yrs,
                ex3=daily.iloc[:-3].sum() if len(daily) > 3 else np.nan)


def fmt(label, s):
    if not s.get("n"):
        return f"   {label}: no fills"
    return (f"   {label}: fills {s['n']} | mean net {s['m']:+.2%} (median {s['med']:+.2%}, t {s['t']:.2f}, win {s['win']:.0%}) | "
            f"${s['usd']:,.0f}/yr | without best day ${s['ex1']:,.0f}/yr | sum without 3 best days ${s['ex3']:,.0f}")


def judge(f, f15, lo):
    a, b = summ(f, lo, SPLIT), summ(f, max(lo, SPLIT), END + pd.Timedelta(days=1))
    b15 = summ(f15, max(lo, SPLIT), END + pd.Timedelta(days=1))
    if a.get("n", 0) >= 30 and not (a["m"] > 0.003):
        v = "KILL (Stage 1)"
    else:
        ok = (b.get("n", 0) >= 30 and b["m"] >= 0.003 and b["t"] >= 2 and b["usd"] >= 1000 and b["ex3"] > 0
              and b15.get("n", 0) and b15["m"] > 0)
        v = "PASS" if ok else "FAIL"
    return a, b, b15, v


def main():
    data = {v: load(v) for _, v in VENUES}
    print("Venue coverage:")
    for _, v in VENUES:
        d = data[v]
        print(f"   {v:<9} " + (f"markets {d['coin'].nunique():>4}, rows {len(d):>6}, {d['day'].min().date()}..{d['day'].max().date()}"
                               if len(d) else "NO DATA (not testable)"))
    print()
    passes = []
    for num, v in VENUES:
        d = data[v]
        print(f"{num} #520 wick bids on {v}")
        if d.empty:
            print("   not testable (no candles)\n")
            continue
        f, f15 = pnl(wick(d, "vol")), pnl(wick(d, "vol", 1.5))
        lo = d["day"].min()
        a, b, b15, verdict = judge(f, f15, lo)
        print(fmt(f"Stage 1 {lo.date()}..2025-06-30", a))
        print(fmt("Stage 2 2025-07-01..2026-11-25", b))
        print(f"   costs x1.5 Stage 2 mean {b15.get('m', np.nan):+.2%}")
        if verdict == "PASS":
            passes.append((num, b["t"]))
        print(f"   VERDICT {verdict}\n")
    print(f"#589-#595 summary: {len(passes)} of {sum(1 for _, v in VENUES if len(data[v]))} testable venues pass "
          f"{passes}; forward log only if Stage 2 t >= 2.5\n")

    alld = pd.concat([d for d in data.values() if len(d)], ignore_index=True) if any(len(d) for d in data.values()) else pd.DataFrame()
    print("#596 #536 rule (first 30 days, X 15%) on all seven venues pooled")
    if alld.empty:
        print("   not testable\n")
    else:
        parts = [wick(data[v], "new") for _, v in VENUES if len(data[v])]
        parts15 = [wick(data[v], "new", 1.5) for _, v in VENUES if len(data[v])]
        f = pnl(pd.concat([p for p in parts if len(p)], ignore_index=True)) if any(len(p) for p in parts) else pd.DataFrame()
        f15 = pnl(pd.concat([p for p in parts15 if len(p)], ignore_index=True)) if any(len(p) for p in parts15) else pd.DataFrame()
        if f.empty:
            print("   no fills\n")
        else:
            lo = alld["day"].min()
            a, b, b15, verdict = judge(f, f15, lo)
            print(fmt("Stage 1", a))
            print(fmt("Stage 2", b))
            print("   per venue (Stage 2): " + "; ".join(f"{v} n {len(g)} {g['ret'].mean():+.2%}" for v, g in f[f['day'] >= SPLIT].groupby("venue")))
            print(f"   VERDICT {verdict}\n")

    print("#597 Venue close >= 3% below HL close: long venue / short HL, exit next close")
    hl = pd.read_parquet(PUB / "uncharted_385_candles.parquet")
    hl["day"] = pd.to_datetime(hl["t"], unit="ms", utc=True).dt.normalize()
    hl = hl.drop_duplicates(["coin", "day"]).assign(k=lambda x: x["coin"].map(norm)).sort_values(["k", "day"])
    hl["c_n1"] = hl.groupby("k")["c"].shift(-1)
    hl["d_n1"] = hl.groupby("k")["day"].shift(-1)
    rows = []
    for _, v in VENUES:
        d = data[v]
        if d.empty:
            continue
        d = d.assign(k=d["coin"].map(norm)).sort_values(["k", "day"])
        d["c_n1"] = d.groupby("coin")["c"].shift(-1)
        d["d_n1"] = d.groupby("coin")["day"].shift(-1)
        m = d.merge(hl[["k", "day", "c", "c_n1", "d_n1"]], on=["k", "day"], suffixes=("", "_hl"))
        ratio = (m["c"] / m["c_hl"]).groupby(m["coin"]).median()
        same = ratio[(ratio > 0.95) & (ratio < 1.05)].index  # addendum 1: drop pairs that are not the same asset or unit
        print(f"   {v}: {m['coin'].nunique()} coins matched to HL, {len(same)} kept after the unit check")
        m = m[m["coin"].isin(same)]
        m = m[(m["c"] <= 0.97 * m["c_hl"]) & (m["d_n1"] == m["day"] + pd.Timedelta(days=1)) & (m["d_n1_hl"] == m["d_n1"])]
        for _, r in m.iterrows():
            rows.append({"venue": v, "coin": r["coin"], "day": r["day"], "size": min(CAP, SHARE * r["v_usd"]),
                         "ret": (r["c_n1"] / r["c"] - 1) - (r["c_n1_hl"] / r["c_hl"] - 1) - 4 * 0.00035,
                         "ret15": (r["c_n1"] / r["c"] - 1) - (r["c_n1_hl"] / r["c_hl"] - 1) - 6 * 0.00035})
    e = pd.DataFrame(rows)
    if e.empty:
        print("   no events (no venue coin matched HL with a >= 3% discount)\n")
    else:
        f = pnl(e)
        f15 = pnl(e.assign(ret=e["ret15"]))
        lo = e["day"].min()
        a, b, b15, verdict = judge(f, f15, lo)
        print(f"   events {len(e)} across {e['venue'].nunique()} venues, {e['coin'].nunique()} coins")
        print(fmt("Stage 1", a))
        print(fmt("Stage 2", b))
        print("   per venue (all): " + "; ".join(f"{v} n {len(g)} {g['ret'].mean():+.2%}" for v, g in e.groupby("venue")))
        print(f"   VERDICT {verdict}")


if __name__ == "__main__":
    main()

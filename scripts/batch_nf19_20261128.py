"""Batch NF19 #619-#622: gaps between thin crypto copies of the same coin, entered one hour late (docs/PREREG_BATCH_NF19_20261128.md).

    uv run python -m scripts.batch_nf19_20261128 | tee docs/jx_runs/batch_nf19_20261128.txt
"""
from __future__ import annotations

import json
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd

from scripts.batch_nf14_20261128 import norm

PUB = Path(__file__).resolve().parent.parent / "data" / "public"
CAP, SHARE, MINVOL = 1500.0, 0.01, 5_000.0
LEG_COST = {"hlmain": 0.0009, "hlspot": 0.0014, "hyna": 0.0018}  # round trip per leg; others 0.10%
T = lambda s: pd.Timestamp(s, tz="UTC")  # noqa: E731
S1_END, S2 = T("2026-08-16"), (T("2026-08-16"), T("2026-11-26"))
THIN = ["backpack", "extended", "pacifica", "apex"]


def frame(d):
    d = d.copy()
    d["ts"] = pd.to_datetime(d["t"], unit="ms", utc=True).dt.floor("h")
    d = d[(d["c"] > 0) & (d["l"] > 0)].drop_duplicates(["venue", "market", "ts"])
    d["id"] = d["venue"] + "|" + d["market"]
    d["traded"] = (d["h"] > d["l"]) & (d["v_usd"] >= MINVOL)
    return d


def cost(i):
    return LEG_COST.get(i.split("|")[0], 0.0010)


def gap_trades(d, x, pair_ok):
    rows = []
    for key, g in d.groupby("key"):
        if g["id"].nunique() < 2:
            continue
        c = g.pivot(index="ts", columns="id", values="c")
        full = pd.date_range(c.index.min(), c.index.max(), freq="h")
        c = c.reindex(full)
        tr = g.pivot(index="ts", columns="id", values="traded").reindex(full).fillna(False).astype(bool)
        v = g.pivot(index="ts", columns="id", values="v_usd").reindex(full).fillna(0.0)
        for a, b in combinations(c.columns, 2):
            if not pair_ok(a, b):
                continue
            both = tr[a] & tr[b]
            if both.sum() < 50 or not (0.95 < (c[a] / c[b])[both].median() < 1.05):
                continue
            for cheap, rich in ((a, b), (b, a)):
                sg = c[cheap] / c[rich] - 1
                for ts in sg.index[both & (sg <= -x)]:
                    t1 = ts + pd.Timedelta(hours=1)
                    if t1 not in c.index or not (tr.at[t1, cheap] and tr.at[t1, rich]):
                        continue
                    ex = next((ts + pd.Timedelta(hours=k) for k in range(5, 10) if ts + pd.Timedelta(hours=k) in c.index
                               and tr.at[ts + pd.Timedelta(hours=k), cheap] and tr.at[ts + pd.Timedelta(hours=k), rich]), None)
                    if ex is None:
                        continue
                    cst = cost(cheap) + cost(rich)
                    rows.append({"ts": ts, "key": key, "pair": "~".join(sorted((a, b))), "gap": float(sg[ts]), "exit_ts": ex, "cost": cst,
                                 "ret": (c.at[ex, cheap] / c.at[t1, cheap] - 1) - (c.at[ex, rich] / c.at[t1, rich] - 1) - cst,
                                 "size": min(CAP, SHARE * min(v.at[t1, cheap], v.at[t1, rich])),
                                 "vmin_entry": min(v.at[t1, cheap], v.at[t1, rich]), "vmin_exit": min(v.at[ex, cheap], v.at[ex, rich])})
    e = pd.DataFrame(rows)
    if e.empty:
        return e
    e = e.sort_values(["ts", "gap"]).drop_duplicates(["ts", "key"])
    keep, busy = [], {}
    for i, r in e.sort_values("ts").iterrows():
        if r["pair"] in busy and r["ts"] < busy[r["pair"]]:
            continue
        busy[r["pair"]] = r["exit_ts"]
        keep.append(i)
    return e.loc[keep]


def summ(e, lo, hi, stress=False):
    g = e[(e["ts"] >= lo) & (e["ts"] < hi)] if len(e) else e
    if g.empty:
        return dict(n=0)
    r = g["ret"] - (0.5 * g["cost"] if stress else 0.0)
    srt = (g["size"] * r).sort_values()
    return dict(n=len(g), m=r.mean(), t=r.mean() / (r.std(ddof=1) / np.sqrt(len(r))) if len(r) > 1 else np.nan, win=(r > 0).mean(),
                usd=(g["size"] * r).sum() * 365 / max((hi - lo).days, 1), ex3=srt.iloc[:-3].sum() if len(srt) > 3 else np.nan)


def fmt(label, s):
    if not s.get("n"):
        return f"   {label}: no trades"
    return (f"   {label}: trades {s['n']} | mean net {s['m']:+.2%} (t {s['t']:.2f}, win {s['win']:.0%}) | ${s['usd']:,.0f}/yr "
            f"| sum without 3 best ${s['ex3']:,.0f}")


def verdict(e, lo):
    a, b, b15 = summ(e, lo, S1_END), summ(e, *S2), summ(e, *S2, stress=True)
    print(fmt(f"Stage 1 {lo.date()}..2026-08-15", a))
    print(fmt("Stage 2 2026-08-16..2026-11-25", b))
    print(f"   costs x1.5 Stage 2 mean {b15.get('m', np.nan):+.2%}")
    if len(e):
        print(f"   events {len(e)} on {e['pair'].nunique()} pairs; median gap at signal {e['gap'].median():+.2%}")
        top = e.groupby("key")["ret"].agg(["size", "mean"]).sort_values("size", ascending=False).head(6)
        print("   by key: " + "; ".join(f"{k} n {int(r['size'])} {r['mean']:+.2%}" for k, r in top.iterrows()))
        print(f"   smaller-leg USD volume, median: entry ${e['vmin_entry'].median():,.0f}, exit ${e['vmin_exit'].median():,.0f}")
    if a.get("n", 0) >= 30 and not (a["m"] > 0):
        v = "KILL (Stage 1)"
    else:
        v = "PASS" if (b.get("n", 0) >= 30 and b["m"] >= 0.003 and b["t"] >= 2 and b["ex3"] > 0 and b15["m"] > 0) else "FAIL"
    if v == "PASS":
        v += " (forward log after the stale-print check)" if b["t"] >= 2.5 else " (t < 2.5: not forward-logged)"
    print(f"   VERDICT {v}\n")


def main():
    main_keys = set(json.loads((PUB / "batchnf19_main_perps.json").read_text())) if (PUB / "batchnf19_main_perps.json").exists() else set()
    if not main_keys:
        main_keys = set(pd.read_parquet(PUB / "wickscale_hl_1h.parquet")["coin"].map(norm))

    print("#619 Thin-venue-only coins (not on HL main): cross-venue gap >= 2%, enter h+1, exit >= h+5")
    parts = []
    for v in THIN:
        p = PUB / f"batchnf15_{v}_1h.parquet"
        if p.exists():
            x = pd.read_parquet(p).rename(columns={"coin": "market"})
            parts.append(x.assign(venue=v, key=x["market"].map(norm)))
    d = frame(pd.concat(parts, ignore_index=True))
    d = d[~d["key"].isin(main_keys)]
    multi = d.groupby("key")["venue"].nunique()
    d = d[d["key"].isin(multi[multi >= 2].index)]
    print(f"   keys on >= 2 thin venues and not on HL main: {d['key'].nunique()}")
    verdict(gap_trades(d, 0.02, lambda a, b: a.split("|")[0] != b.split("|")[0]), d["ts"].min() if len(d) else T("2026-03-01"))

    parts = [pd.read_parquet(PUB / f"batchnf19_{n}_1h.parquet") for n in ("hyna", "hlmain", "hlspot", "grvt") if (PUB / f"batchnf19_{n}_1h.parquet").exists()]
    if not parts:
        print("#620-#622 not testable (no data)")
        return
    d = frame(pd.concat(parts, ignore_index=True))
    lo = d["ts"].min()
    print(f"HL/GRVT copies: markets {d['id'].nunique()}, {lo}..{d['ts'].max()}\n")
    for num, label, other in (("#620", "hyna vs HL main", "hyna"), ("#621", "HL spot vs HL perp", "hlspot"), ("#622", "GRVT crypto vs HL main", "grvt")):
        print(f"{num} {label}: gap >= 1%, enter h+1, exit >= h+5")
        sub = d[d["venue"].isin(["hlmain", other])]
        ok = lambda a, b, o=other: {a.split("|")[0], b.split("|")[0]} == {"hlmain", o}  # noqa: E731
        verdict(gap_trades(sub, 0.01, ok), lo)


if __name__ == "__main__":
    main()

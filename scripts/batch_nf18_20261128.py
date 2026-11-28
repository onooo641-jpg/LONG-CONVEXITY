"""Batch NF18 #614-#618: the same equity, pre-IPO or commodity perp on several thin venues (docs/PREREG_BATCH_NF18_20261128.md).

    uv run python -m scripts.batch_nf18_20261128 | tee docs/jx_runs/batch_nf18_20261128.txt
"""
from __future__ import annotations

import json
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd

PUB = Path(__file__).resolve().parent.parent / "data" / "public"
COST, CAP, SHARE, MINVOL = 0.0020, 1500.0, 0.01, 5_000.0
T = lambda s: pd.Timestamp(s, tz="UTC")  # noqa: E731
S1_END, S2 = T("2026-08-16"), (T("2026-08-16"), T("2026-11-26"))
PREIPO = {"ANTHROPIC", "OPENAI", "SPACEX"}
COMIDX = {"GOLD", "SILVER", "WTI", "BRENT", "SP500", "NDX", "R2000", "NATGAS", "PLATINUM", "PALLADIUM", "COPPER"}


def load():
    parts = [pd.read_parquet(PUB / f) for f in ("batchnf18_hip3_1h.parquet", "batchnf18_grvt_1h.parquet") if (PUB / f).exists()]
    d = pd.concat(parts, ignore_index=True)
    d["ts"] = pd.to_datetime(d["t"], unit="ms", utc=True).dt.floor("h")
    d = d[(d["c"] > 0) & (d["l"] > 0)].drop_duplicates(["venue", "market", "ts"])
    d["id"] = d["venue"] + "|" + d["market"]
    d["traded"] = (d["h"] > d["l"]) & (d["v_usd"] >= MINVOL)
    main = set(json.loads((PUB / "batchnf18_main_perps.json").read_text())) if (PUB / "batchnf18_main_perps.json").exists() else set()
    cls = json.loads((PUB / "batchnf18_grvt_classes.json").read_text()) if (PUB / "batchnf18_grvt_classes.json").exists() else {}
    crypto = main | set(d.loc[d["venue"] == "hyna", "key"]) | {k for m, k in d.loc[d["venue"] == "grvt", ["market", "key"]].drop_duplicates().itertuples(index=False)
                                                               if str(cls.get(m, "")).upper() == "CRYPTO"}
    d["cls"] = np.where(d["key"].isin(PREIPO), "preipo", np.where(d["key"].isin(COMIDX), "comidx",
                        np.where(d["key"].isin(crypto), "crypto", "equity")))
    return d


def cash_hour(ts):
    return (ts.dt.dayofweek < 5) & (ts.dt.hour >= 14) & (ts.dt.hour <= 20)


def gap_trades(d, cls, x):
    """Signals at h, entry at the h+1 closes, exit at the first hour >= h+5 (<= h+9) where both legs trade."""
    rows = []
    for key, g in d[d["cls"] == cls].groupby("key"):
        c = g.pivot(index="ts", columns="id", values="c")
        tr = g.pivot(index="ts", columns="id", values="traded").reindex(c.index).fillna(False).astype(bool)
        v = g.pivot(index="ts", columns="id", values="v_usd").reindex(c.index).fillna(0.0)
        full = pd.date_range(c.index.min(), c.index.max(), freq="h")
        c, tr, v = c.reindex(full), tr.reindex(full).fillna(False).astype(bool), v.reindex(full).fillna(0.0)
        for a, b in combinations(c.columns, 2):
            both = tr[a] & tr[b]
            if both.sum() < 50:
                continue
            ratio = (c[a] / c[b])[both].median()
            if not (0.95 < ratio < 1.05):
                continue
            ga = c[a] / c[b] - 1
            for cheap, rich, sg in ((a, b, ga), (b, a, c[b] / c[a] - 1)):
                hit = both & (sg <= -x)
                for ts in sg.index[hit]:
                    t1 = ts + pd.Timedelta(hours=1)
                    if t1 not in c.index or not (tr.at[t1, cheap] and tr.at[t1, rich]):
                        continue
                    ex = next((ts + pd.Timedelta(hours=k) for k in range(5, 10)
                               if ts + pd.Timedelta(hours=k) in c.index and tr.at[ts + pd.Timedelta(hours=k), cheap]
                               and tr.at[ts + pd.Timedelta(hours=k), rich]), None)
                    if ex is None:
                        continue
                    ret = (c.at[ex, cheap] / c.at[t1, cheap] - 1) - (c.at[ex, rich] / c.at[t1, rich] - 1) - 2 * COST
                    rows.append({"ts": ts, "key": key, "pair": "~".join(sorted((a, b))), "cheap": cheap, "gap": float(sg[ts]),
                                 "exit_ts": ex, "ret": ret, "size": min(CAP, SHARE * min(v.at[t1, cheap], v.at[t1, rich])),
                                 "vmin_entry": min(v.at[t1, cheap], v.at[t1, rich]), "vmin_exit": min(v.at[ex, cheap], v.at[ex, rich])})
    e = pd.DataFrame(rows)
    if e.empty:
        return e
    e = e.sort_values(["ts", "gap"]).drop_duplicates(["ts", "key"])  # widest gap per key and hour
    keep, busy = [], {}
    for i, r in e.sort_values("ts").iterrows():
        if r["pair"] in busy and r["ts"] < busy[r["pair"]]:
            continue
        busy[r["pair"]] = r["exit_ts"]
        keep.append(i)
    return e.loc[keep]


def summ(e, lo, hi, extra=0.0):
    g = e[(e["ts"] >= lo) & (e["ts"] < hi)] if len(e) else e
    if g.empty:
        return dict(n=0)
    r = g["ret"] - extra
    srt = (g["size"] * r).sort_values()
    return dict(n=len(g), m=r.mean(), t=r.mean() / (r.std(ddof=1) / np.sqrt(len(r))) if len(r) > 1 else np.nan, win=(r > 0).mean(),
                usd=(g["size"] * r).sum() * 365 / max((hi - lo).days, 1), ex3=srt.iloc[:-3].sum() if len(srt) > 3 else np.nan)


def fmt(label, s):
    if not s.get("n"):
        return f"   {label}: no trades"
    return (f"   {label}: trades {s['n']} | mean net {s['m']:+.2%} (t {s['t']:.2f}, win {s['win']:.0%}) | ${s['usd']:,.0f}/yr "
            f"| sum without 3 best ${s['ex3']:,.0f}")


def verdict(e, lo, legs, min_n):
    a, b = summ(e, lo, S1_END), summ(e, *S2)
    b15 = summ(e, *S2, extra=0.5 * COST * legs)
    print(fmt(f"Stage 1 {lo.date()}..2026-08-15", a))
    print(fmt("Stage 2 2026-08-16..2026-11-25", b))
    print(f"   costs x1.5 Stage 2 mean {b15.get('m', np.nan):+.2%}")
    if len(e):
        top = e.groupby("key")["ret"].agg(["size", "mean"]).sort_values("size", ascending=False).head(6)
        print("   by key: " + "; ".join(f"{k} n {int(r['size'])} {r['mean']:+.2%}" for k, r in top.iterrows()))
        if "vmin_entry" in e:
            print(f"   smaller-leg USD volume, median: entry ${e['vmin_entry'].median():,.0f}, exit ${e['vmin_exit'].median():,.0f}")
    if a.get("n", 0) >= min_n and not (a["m"] > 0):
        v = "KILL (Stage 1)"
    else:
        ok = b.get("n", 0) >= min_n and b["m"] >= 0.003 and b["t"] >= 2 and b["ex3"] > 0 and b15["m"] > 0
        v = "PASS" if ok else "FAIL"
    if v == "PASS":
        v += " (forward log after the stale-print check)" if b["t"] >= 2.5 else " (t < 2.5: not forward-logged)"
    print(f"   VERDICT {v}\n")


def weekend(d):
    rows = []
    eq = d[d["cls"] == "equity"]
    best = eq.groupby(["key", "id"])["v_usd"].median().reset_index().sort_values("v_usd").drop_duplicates("key", keep="last")
    for key, mid in best[["key", "id"]].itertuples(index=False):
        s = eq[eq["id"] == mid].set_index("ts").sort_index()
        for sun in s.index[(s.index.dayofweek == 6) & (s.index.hour == 21)]:
            fri, mon = sun - pd.Timedelta(hours=50), sun + pd.Timedelta(hours=18)
            if fri not in s.index or mon not in s.index or not (s.at[fri, "traded"] and s.at[sun, "traded"] and s.at[mon, "traded"]):
                continue
            m = s.at[sun, "c"] / s.at[fri, "c"] - 1
            if abs(m) >= 0.03:
                rows.append({"ts": sun, "key": key, "move": m, "size": min(CAP, SHARE * s.at[sun, "v_usd"]),
                             "ret": -np.sign(m) * (s.at[mon, "c"] / s.at[sun, "c"] - 1) - COST})
    return pd.DataFrame(rows)


def main():
    d = load()
    lo = d["ts"].min()
    print(f"markets {d['id'].nunique()} on {d['venue'].nunique()} venues, keys {d['key'].nunique()}, {lo}..{d['ts'].max()}")
    print("   keys by class: " + ", ".join(f"{k} {n}" for k, n in d.drop_duplicates("key")["cls"].value_counts().items()) + "\n")
    eq_all = gap_trades(d, "equity", 0.01)
    specs = [("#614", "Pre-IPO cross-venue gap >= 3%, enter h+1, exit >= h+5", gap_trades(d, "preipo", 0.03), 20),
             ("#615", "Equity cross-venue gap >= 1%, off-hours signal", eq_all[~cash_hour(eq_all["ts"])] if len(eq_all) else eq_all, 30),
             ("#616", "Equity cross-venue gap >= 1%, US cash-hours signal", eq_all[cash_hour(eq_all["ts"])] if len(eq_all) else eq_all, 30),
             ("#617", "Commodity/index cross-venue gap >= 1%", gap_trades(d, "comidx", 0.01), 30)]
    for num, label, e, n in specs:
        print(f"{num} {label}")
        if len(e):
            print(f"   events {len(e)} on {e['pair'].nunique()} pairs; median gap at signal {e['gap'].median():+.2%}")
        verdict(e, lo, legs=2, min_n=n)
    print("#618 Single-stock weekend fade (|Fri 20:00 -> Sun 22:00| >= 3%), exit Monday 16:00 UTC")
    e = weekend(d)
    if len(e):
        print(f"   events {len(e)} on {e['key'].nunique()} stocks; median |move| {e['move'].abs().median():.2%}")
    verdict(e, lo, legs=1, min_n=20)


if __name__ == "__main__":
    main()

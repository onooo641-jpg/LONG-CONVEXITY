"""Batch NF22 #631-#634: weekly signals across Hyperliquid's thin spot tokens, long-only, HYPE-hedged (docs/PREREG_BATCH_NF22_20261128.md).

    uv run python -m scripts.batch_nf22_20261128 | tee docs/jx_runs/batch_nf22_20261128.txt
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

PUB = Path(__file__).resolve().parent.parent / "data" / "public"
CAP, SHARE = 1500.0, 0.01
COST = 2 * (0.0007 + 0.0050) + 0.0009
LO, END = pd.Timestamp("2024-12-01"), pd.Timestamp("2026-11-25")
S1, S2 = (LO, pd.Timestamp("2025-07-01")), (pd.Timestamp("2025-07-01"), pd.Timestamp("2026-11-26"))


def load():
    s = pd.read_parquet(PUB / "fivehigh_hl_spot_1d.parquet")
    s = s[s["label"].str.endswith("/USDC")].copy()
    s["day"] = pd.to_datetime(s["t"], unit="ms").dt.normalize()
    s = s[(s["c"] > 0) & (s["day"] <= END)].drop_duplicates(["pair", "day"])
    s["usd"] = s["v"] * s["c"]
    s["traded"] = (s["h"] > s["l"]) & (s["v"] > 0)
    c = s.pivot(index="day", columns="label", values="c").sort_index()
    full = pd.date_range(c.index.min(), END, freq="D")
    c = c.reindex(full)
    usd = s.pivot(index="day", columns="label", values="usd").reindex(full).fillna(0.0)
    tr = s.pivot(index="day", columns="label", values="traded").reindex(full).fillna(False).astype(bool)
    h = pd.read_parquet(PUB / "uncharted_385_candles.parquet")
    h = h[h["coin"] == "HYPE"].copy()
    h["day"] = pd.to_datetime(h["t"], unit="ms").dt.normalize()
    hype = h.drop_duplicates("day").set_index("day")["c"].reindex(full)
    return c, usd, tr, hype


def run(c, usd, tr, hype, pick, cost_mult=1.0):
    rows, contrib = [], {}
    mondays = [d for d in c.index if d.dayofweek == 0 and LO <= d and d + pd.Timedelta(days=7) <= END]
    ffc = c.ffill()
    for d in mondays:
        x = d + pd.Timedelta(days=7)
        hist = (c.loc[:d].notna().sum() >= 60)
        med30 = usd.loc[d - pd.Timedelta(days=29):d].median()
        v7 = usd.loc[d - pd.Timedelta(days=6):d].sum()
        v30w = usd.loc[d - pd.Timedelta(days=36):d - pd.Timedelta(days=7)].sum() / 30 * 7
        r7 = ffc.loc[d] / ffc.loc[d - pd.Timedelta(days=7)] - 1
        r28 = ffc.loc[d - pd.Timedelta(days=7)] / ffc.loc[d - pd.Timedelta(days=35)] - 1
        ok_bar = tr.loc[d] & tr.loc[x]
        f = pd.DataFrame({"hist": hist, "med30": med30, "v7": v7, "v30w": v30w, "r7": r7, "r28": r28, "ok": ok_bar})
        sel = pick(f[f["hist"] & f["ok"]])
        if not len(sel) or not (hype.get(d) > 0 and hype.get(x) > 0):
            continue
        hr = hype[x] / hype[d] - 1
        rets = c.loc[x, sel] / c.loc[d, sel] - 1 - hr - cost_mult * COST
        size = np.minimum(CAP, SHARE * usd.loc[d, sel])
        for k, r in rets.items():
            contrib[k] = contrib.get(k, 0.0) + float(r * size[k])
        rows.append({"start": d, "ret": float(rets.mean()), "n": len(sel), "usd": float((rets * size).sum())})
    return pd.DataFrame(rows), contrib


def pct(f, col, q, top):
    f = f.dropna(subset=[col])
    if f.empty:
        return []
    k = max(3, int(round(len(f) * q)))
    return (f.nlargest(k, col) if top else f.nsmallest(k, col)).index.tolist()


def summ(e, w):
    g = e[(e["start"] >= w[0]) & (e["start"] < w[1])] if len(e) else e
    if g.empty:
        return dict(n=0)
    r = g["ret"]
    return dict(n=len(g), m=r.mean(), t=r.mean() / (r.std(ddof=1) / np.sqrt(len(r))) if len(r) > 1 else np.nan, win=(r > 0).mean(),
                ex3=r.sort_values().iloc[:-3].sum() if len(r) > 3 else np.nan, usd=g["usd"].sum() * 365 / max((w[1] - w[0]).days, 1),
                k=g["n"].mean())


def fmt(label, s):
    if not s.get("n"):
        return f"   {label}: no weeks"
    return (f"   {label}: weeks {s['n']} (mean {s['k']:.1f} tokens) | mean weekly net {s['m']:+.2%} (t {s['t']:.2f}, win {s['win']:.0%}) "
            f"| ${s['usd']:,.0f}/yr | sum without 3 best weeks {s['ex3']:+.2%}")


def main():
    c, usd, tr, hype = load()
    print(f"HL spot USDC tokens {c.shape[1]}, days {c.index.min().date()}..{c.index.max().date()}; HYPE hedge days {int(hype.notna().sum())}\n")
    liq = lambda f: f[f["med30"] >= 20_000]  # noqa: E731
    specs = [("#631", "Weekly reversal (bottom 10% by 7-day return)", lambda f: pct(liq(f), "r7", 0.10, top=False)),
             ("#632", "4-week momentum skipping a week (top 10%)", lambda f: pct(liq(f), "r28", 0.10, top=True)),
             ("#633", "Volume shock (7-day volume >= 5x, 7-day return >= 0)",
              lambda f: liq(f)[(liq(f)["v7"] >= 5 * liq(f)["v30w"]) & (liq(f)["v30w"] > 0) & (liq(f)["r7"] >= 0)].index.tolist()),
             ("#634", "Dormant awakening (30-day median < $5K, 7-day volume >= $50K)",
              lambda f: f[(f["med30"] < 5_000) & (f["v7"] >= 50_000)].index.tolist())]
    for num, label, pick in specs:
        e, contrib = run(c, usd, tr, hype, pick)
        e15, _ = run(c, usd, tr, hype, pick, 1.5)
        a, b, b15 = summ(e, S1), summ(e, S2), summ(e15, S2)
        print(f"{num} {label}")
        print(fmt("Stage 1 2024-12..2025-06", a))
        print(fmt("Stage 2 2025-07..2026-11", b))
        print(f"   costs x1.5 Stage 2 mean {b15.get('m', np.nan):+.2%}")
        tot = sum(contrib.values())
        top = max(contrib.items(), key=lambda kv: kv[1]) if contrib else ("-", 0.0)
        share = top[1] / tot if tot > 0 else np.nan
        print(f"   top token by $ profit: {top[0]} {top[1]:,.0f} of {tot:,.0f} ({share:.0%} of profit)" if contrib else "   no trades")
        if a.get("n", 0) >= 10 and not (a["m"] > 0):
            v = "KILL (Stage 1)"
        else:
            ok = (b.get("n", 0) >= 30 and b["m"] >= 0.01 and b["t"] >= 2 and b["ex3"] > 0 and b15.get("m", -1) > 0
                  and np.isfinite(share) and share <= 0.40)
            v = "PASS" if ok else "FAIL"
        if v == "PASS":
            v += " (forward log)" if b["t"] >= 2.5 else " (t < 2.5: not forward-logged)"
        print(f"   VERDICT {v}\n")


if __name__ == "__main__":
    main()

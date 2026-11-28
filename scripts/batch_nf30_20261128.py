"""Batch NF30 #660-#663: Virtuals agent-token ecosystem on Base, VIRTUAL-hedged (docs/PREREG_BATCH_NF30_20261128.md).

    uv run python -m scripts.batch_nf30_20261128 | tee docs/jx_runs/batch_nf30_20261128.txt
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

PUB = Path(__file__).resolve().parent.parent / "data" / "public"
FEE, HL_LEG, SIZE, MINVOL = 0.01, 0.0009, 1000.0, 20_000.0
SPLIT, END = pd.Timestamp("2025-07-01"), pd.Timestamp("2026-11-01")


def load():
    d = pd.read_parquet(PUB / "batchnf30_ohlcv.parquet")
    d = d[d["quote"].astype(str).str.upper() == "VIRTUAL"].copy()  # prices in VIRTUAL
    d["day"] = pd.to_datetime(d["t"], unit="s").dt.normalize()
    d = d[(d["c"] > 0)].drop_duplicates(["lp", "day"]).sort_values(["lp", "day"])
    c = d.pivot(index="day", columns="lp", values="c")
    v = d.pivot(index="day", columns="lp", values="v_usd").fillna(0.0)
    full = pd.date_range(c.index.min(), c.index.max(), freq="D")
    return d, c.reindex(full), v.reindex(full).fillna(0.0)


def virtual_funding():
    try:
        f = pd.read_parquet(PUB / "fivehigh_hl_premium.parquet")
        f = f[f["coin"] == "VIRTUAL"]
        daily = f.assign(day=pd.to_datetime(f["t"], unit="ms").dt.normalize()).groupby("day")["rate"].sum()
        return daily, float(daily.mean()) if len(daily) else 0.0
    except Exception:  # noqa: BLE001
        return pd.Series(dtype=float), 0.0


def cost(vol, mult=1.0):
    impact = min(0.10, SIZE / max(0.5 * vol, 1.0))
    return mult * (2 * (FEE + impact) + HL_LEG)


def hold_ret(c, lp, d0, d1, fund, fmean):
    s = c[lp]
    p0 = s.get(d0)
    if not (p0 and p0 > 0):
        return None
    tail = s.loc[:d1].dropna()
    p1 = tail.iloc[-1] if len(tail) else np.nan
    r = -1.0 if not (p1 > 0) or p1 < 0.01 * p0 else p1 / p0 - 1
    f = fund.reindex(pd.date_range(d0, d1 - pd.Timedelta(days=1))).fillna(fmean).sum()  # short VIRTUAL receives positive funding
    return r + f


def monthly(c, v, fund, fmean, pick, mult=1.0):
    rows, contrib = [], {}
    for m in pd.date_range(c.index.min() + pd.offsets.MonthBegin(1), END, freq="MS"):
        d0, d1 = m, m + pd.offsets.MonthBegin(1)
        if d0 not in c.index or d1 > c.index.max() + pd.Timedelta(days=1):
            continue
        lb = d0 - pd.Timedelta(days=28)
        if lb not in c.index:
            continue
        med = v.loc[d0 - pd.Timedelta(days=29):d0].median()
        r28 = c.loc[d0] / c.loc[lb] - 1
        elig = r28[(med >= MINVOL) & c.loc[d0].notna() & r28.notna()]
        sel = pick(elig)
        rs = []
        for lp in sel:
            r = hold_ret(c, lp, d0, d1, fund, fmean)
            if r is None:
                continue
            r -= cost(float(v.loc[d0, lp]), mult)
            rs.append(r)
            contrib[lp] = contrib.get(lp, 0.0) + r
        if rs:
            rows.append({"start": d0, "ret": float(np.mean(rs)), "n": len(rs)})
    return pd.DataFrame(rows), contrib


def events(c, v, fund, fmean, offset, hold, mult=1.0):
    rows, contrib = [], {}
    for lp in c.columns:
        s = c[lp].dropna()
        if len(s) < offset + 2:
            continue
        d0 = s.index[0] + pd.Timedelta(days=offset)
        if d0 not in c.index or not (c.at[d0, lp] > 0):
            continue
        hist = v.loc[s.index[0]:d0, lp]
        if hist.median() < MINVOL:
            continue
        d1 = d0 + pd.Timedelta(days=hold)
        if d1 > END:
            continue
        r = hold_ret(c, lp, d0, d1, fund, fmean)
        if r is None:
            continue
        r -= cost(float(v.loc[d0, lp]), mult)
        rows.append({"start": d0, "ret": r, "n": 1})
        contrib[lp] = contrib.get(lp, 0.0) + r
    return pd.DataFrame(rows), contrib


def summ(e, lo, hi):
    g = e[(e["start"] >= lo) & (e["start"] < hi)] if len(e) else e
    if g.empty:
        return dict(n=0)
    r = g["ret"]
    return dict(n=len(g), m=r.mean(), t=r.mean() / (r.std(ddof=1) / np.sqrt(len(r))) if len(r) > 1 else np.nan, win=(r > 0).mean(),
                ex3=r.sort_values().iloc[:-3].sum() if len(r) > 3 else np.nan)


def report(num, label, e, e15, contrib, min_s1, min_s2):
    a, b, b15 = summ(e, pd.Timestamp("2000-01-01"), SPLIT), summ(e, SPLIT, END), summ(e15, SPLIT, END)
    f = lambda s: (f"n {s['n']}, mean {s['m']:+.2%} (t {s['t']:.2f}, win {s['win']:.0%}), sum without 3 best {s['ex3']:+.2%}"  # noqa: E731
                   if s.get("n") else "no holds")
    print(f"{num} {label}")
    print(f"   Stage 1 (before 2025-07): {f(a)}")
    print(f"   Stage 2 (2025-07..2026-10): {f(b)}")
    print(f"   costs x1.5 Stage 2 mean {b15.get('m', np.nan):+.2%}")
    pos = {k: x for k, x in contrib.items() if x > 0}
    share = max(pos.values()) / sum(contrib.values()) if pos and sum(contrib.values()) > 0 else np.nan
    print(f"   top token share of summed return: {share:.0%}" if np.isfinite(share) else "   summed return <= 0")
    if a.get("n", 0) >= min_s1 and not (a["m"] > 0):
        v = "KILL (Stage 1)"
    else:
        ok = (b.get("n", 0) >= min_s2 and b["m"] >= 0.03 and b["t"] >= 2 and b["ex3"] > 0 and b15.get("m", -1) > 0
              and np.isfinite(share) and share <= 0.40)
        v = "PASS" if ok else "FAIL"
    if v == "PASS":
        v += " (forward log)" if b["t"] >= 2.5 else " (t < 2.5: not forward-logged)"
    print(f"   VERDICT {v}\n")


def main():
    d, c, v = load()
    fund, fmean = virtual_funding()
    print(f"VIRTUAL-quoted agent pools {c.shape[1]}, days {c.index.min().date()}..{c.index.max().date()}; "
          f"VIRTUAL funding days {len(fund)} (mean {fmean * 365:+.1%}/yr used where missing)\n")
    top = lambda e: e.nlargest(10).index.tolist()  # noqa: E731
    bot = lambda e: e.nsmallest(10).index.tolist()  # noqa: E731
    for num, label, pick in (("#660", "4-week momentum (top 10), monthly", top), ("#661", "4-week reversal (bottom 10), monthly", bot)):
        e, ctb = monthly(c, v, fund, fmean, pick)
        e15, _ = monthly(c, v, fund, fmean, pick, 1.5)
        report(num, label, e, e15, ctb, 6, 10)
    for num, label, off, hold in (("#662", "New agents: buy day 7 after first candle, hold 30 days", 7, 30),
                                  ("#663", "First-week drift: buy at the first full day's close, hold 7 days", 1, 7)):
        e, ctb = events(c, v, fund, fmean, off, hold)
        e15, _ = events(c, v, fund, fmean, off, hold, 1.5)
        report(num, label, e, e15, ctb, 30, 30)


if __name__ == "__main__":
    main()

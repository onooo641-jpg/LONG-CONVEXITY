"""Batch NF27 #651-#654: funding snapshot timing on Aster (docs/PREREG_BATCH_NF27_20261128.md).

    uv run python -m scripts.batch_nf27_20261128 | tee docs/jx_runs/batch_nf27_20261128.txt
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

PUB = Path(__file__).resolve().parent.parent / "data" / "public"
COST = 2 * (0.00035 + 0.0005)
CAP, SHARE = 1500.0, 0.01
T = lambda s: pd.Timestamp(s, tz="UTC")  # noqa: E731
S1, S2 = (T("2025-01-01"), T("2026-01-01")), (T("2026-01-01"), T("2026-11-26"))
MIN = 60_000


def trades(f, m, thr, w, cost_mult=1.0):
    by = {k: g.set_index("t") for k, g in m.groupby(["symbol", "settle_t"])}
    rows = []
    for s, t, rate in f[f["rate"].abs() >= thr].itertuples(index=False):
        g = by.get((s, t))
        if g is None:
            continue
        mm = (t // MIN) * MIN
        a, b = mm - (w + 1) * MIN, mm + (w - 1) * MIN  # bar opening at a closes w minutes before; bar opening at b closes w minutes after
        if a not in g.index or b not in g.index or not (g.at[a, "qv"] > 0 and g.at[b, "qv"] > 0):
            continue
        side = -np.sign(rate)
        win = g.loc[a:b, "qv"].sum()
        rows.append({"ts": pd.Timestamp(t, unit="ms", tz="UTC"), "symbol": s, "rate": rate,
                     "px": side * (g.at[b, "c"] / g.at[a, "c"] - 1),
                     "ret": abs(rate) + side * (g.at[b, "c"] / g.at[a, "c"] - 1) - cost_mult * COST,
                     "size": min(CAP, SHARE * win)})
    return pd.DataFrame(rows)


def summ(e, w):
    g = e[(e["ts"] >= w[0]) & (e["ts"] < w[1])] if len(e) else e
    if g.empty:
        return dict(n=0)
    r = g["ret"]
    pnl = (g["size"] * r).sort_values()
    return dict(n=len(g), m=r.mean(), t=r.mean() / (r.std(ddof=1) / np.sqrt(len(r))) if len(r) > 1 else np.nan, win=(r > 0).mean(),
                usd=pnl.sum() * 365 / max((min(w[1], g["ts"].max()) - w[0]).days, 1), ex3=pnl.iloc[:-3].sum() if len(pnl) > 3 else np.nan,
                fund=g["rate"].abs().mean(), px=g["px"].mean())


def fmt(label, s):
    if not s.get("n"):
        return f"   {label}: no trades"
    return (f"   {label}: trades {s['n']} | mean net {s['m']:+.2%} (t {s['t']:.2f}, win {s['win']:.0%}) | funding {s['fund']:+.2%}, "
            f"price leg {s['px']:+.2%} | ${s['usd']:,.0f}/yr | sum without 3 best ${s['ex3']:,.0f}")


def main():
    f = pd.read_parquet(PUB / "batchnf27_funding.parquet")
    m = pd.read_parquet(PUB / "batchnf27_minutes.parquet")
    print(f"Aster funding rows {len(f):,} on {f['symbol'].nunique()} perps; settlements with |rate| >= 0.10%: "
          f"{int((f['rate'].abs() >= 0.001).sum())}; with minute data: {m['settle_t'].nunique()}\n")
    for num, thr, w in (("#651", 0.001, 1), ("#652", 0.0025, 1), ("#653", 0.001, 5), ("#654", 0.001, 30)):
        e, e15 = trades(f, m, thr, w), trades(f, m, thr, w, 1.5)
        a, b, b15 = summ(e, S1), summ(e, S2), summ(e15, S2)
        print(f"{num} |rate| >= {thr:.2%}, hold {w} min each side of settlement, receiving side")
        print(fmt("Stage 1 2025", a))
        print(fmt("Stage 2 2026-01..11", b))
        print(f"   costs x1.5 Stage 2 mean {b15.get('m', np.nan):+.2%}")
        s2 = e[(e["ts"] >= S2[0])] if len(e) else e
        share = np.nan
        if len(s2):
            p = (s2["size"] * s2["ret"]).groupby(s2["symbol"]).sum()
            share = p.max() / p.sum() if p.sum() > 0 else np.nan
            print(f"   Stage 2 top symbol share of profit: {share:.0%} ({p.idxmax()})" if np.isfinite(share) else "   Stage 2 profit <= 0")
        if a.get("n", 0) >= 30 and not (a["m"] > 0):
            v = "KILL (Stage 1)"
        else:
            ok = (b.get("n", 0) >= 30 and b["m"] >= 0.001 and b["usd"] >= 3000 and b["t"] >= 2 and b["ex3"] > 0
                  and b15.get("m", -1) > 0 and np.isfinite(share) and share <= 0.40)
            v = "PASS" if ok else "FAIL"
        if v == "PASS":
            v += " (forward log)" if b["t"] >= 2.5 else " (t < 2.5: not forward-logged)"
        print(f"   VERDICT {v}\n")


if __name__ == "__main__":
    main()

"""Batch NF24 #639-#642: small reversal edges on a zero-fee thin venue (Paradex, hourly) (docs/PREREG_BATCH_NF24_20261128.md).

    uv run python -m scripts.batch_nf24_20261128 | tee docs/jx_runs/batch_nf24_20261128.txt
"""
from __future__ import annotations

import numpy as np
import pandas as pd

import scripts.batch_nf15_20261128 as B15
import scripts.batch_nf23_20261128 as N23

STRESS = 0.0007


def delayed(g, e, side):
    """One-hour-delayed entry: buy at the h+1 close (that hour traded), exit at the close 4 hours after that (traded)."""
    idx = g.set_index(["coin", "ts"])
    out = []
    for _, r in e.iterrows():
        t1, t5 = r["ts"] + pd.Timedelta(hours=1), r["ts"] + pd.Timedelta(hours=5)
        a, b = idx.loc[(r["coin"], t1)] if (r["coin"], t1) in idx.index else None, idx.loc[(r["coin"], t5)] if (r["coin"], t5) in idx.index else None
        if a is None or b is None or not (a["v_usd"] > 0 and b["v_usd"] > 0) or not (a["c"] > 0 and b["c"] > 0):
            out.append(np.nan)
            continue
        out.append(side * (b["c"] / a["c"] - 1))
    return pd.Series(out, index=e.index)


def report(num, label, g, e, side, lo):
    print(f"{num} {label}")
    if e.empty:
        print("   no trades\n")
        return
    e = e.copy()
    e["ret"] = side * (e["exit_c"] / e["c"] - 1)
    e["size"] = np.minimum(B15.CAP, B15.SHARE * e["v_usd"])
    e = B15.one_per_market(e)
    B15.COST = STRESS / 0.5  # verdict's stress line subtracts 0.5 x COST = 0.07% here
    B15.verdict(e, lo)
    s2 = e[e["ts"] >= B15.S2[0]].copy()
    if len(s2):
        s2["d"] = delayed(g, s2, side)
        dd = s2.dropna(subset=["d"])
        t = dd["d"].mean() / (dd["d"].std(ddof=1) / np.sqrt(len(dd))) if len(dd) > 1 else np.nan
        print(f"   stale-print check, Stage 2 one hour later: n {len(dd)}, mean {dd['d'].mean():+.2%} (t {t:.2f})\n")


def main():
    raw = N23.hourly_raw("paradex")
    g = B15.prep(raw)
    lo = g["ts"].min()
    print(f"Paradex markets {g['coin'].nunique()}, hours {g['c'].notna().sum():,}, {lo}..{g['ts'].max()}\n")
    ok = (g["h"] > g["l"]) & (g["v_usd"] >= B15.MINVOL) & g["exit_c"].notna()
    z = g["r"] / g["sig"]
    report("#639", "-3 sigma bounce (between -5 and -3 sigma), long, 4 hours", g, g[ok & (z <= -3) & (z > -5)], 1.0, lo)
    report("#640", "+5 sigma pump fade, short, 4 hours", g, g[ok & (z >= 5)], -1.0, lo)
    report("#641", "+3 sigma fade (between +3 and +5 sigma), short, 4 hours", g, g[ok & (z >= 3) & (z < 5)], -1.0, lo)

    print("#642 24-hour loser bounce: at 00:00 UTC buy the 3 worst 24h returns (>= $500K 24h volume), exit 24h later")
    w = g.set_index(["ts", "coin"]).sort_index()
    c = g.pivot(index="ts", columns="coin", values="c").ffill()
    v = g.pivot(index="ts", columns="coin", values="v_usd").fillna(0.0)
    rows = []
    for ts in c.index[c.index.hour == 0]:
        if ts - pd.Timedelta(hours=24) not in c.index:
            continue
        vol24 = v.loc[ts - pd.Timedelta(hours=23):ts].sum()
        r24 = c.loc[ts] / c.loc[ts - pd.Timedelta(hours=24)] - 1
        cand = r24[(vol24 >= 500_000) & r24.notna()].nsmallest(3)
        for coin in cand.index:
            x = next((ts + pd.Timedelta(hours=k) for k in range(24, 31) if (ts + pd.Timedelta(hours=k), coin) in w.index
                      and w.at[(ts + pd.Timedelta(hours=k), coin), "v_usd"] > 0), None)
            if x is None or not (w.at[(ts, coin), "c"] > 0) if (ts, coin) in w.index else True:
                continue
            rows.append({"ts": ts, "coin": coin, "ret": w.at[(x, coin), "c"] / c.at[ts, coin] - 1,
                         "size": min(B15.CAP, B15.SHARE * vol24[coin] / 24)})
    e = pd.DataFrame(rows)
    if e.empty:
        print("   no trades\n")
        return
    B15.COST = STRESS / 0.5
    B15.verdict(e, lo)


if __name__ == "__main__":
    main()

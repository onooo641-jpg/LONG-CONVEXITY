"""NF14 #597 post-hoc validity check (stale prints on dead venue markets). Not part of the registered verdict.

    uv run python -m scripts.batch_nf14_diag_20261128 | tee docs/jx_runs/batch_nf14_diag_20261128.txt
"""
from __future__ import annotations

import numpy as np
import pandas as pd

import scripts.batch_nf14_20261128 as B


def events():
    hl = pd.read_parquet(B.PUB / "uncharted_385_candles.parquet")
    hl["day"] = pd.to_datetime(hl["t"], unit="ms", utc=True).dt.normalize()
    hl = hl.drop_duplicates(["coin", "day"]).assign(k=lambda x: x["coin"].map(B.norm)).sort_values(["k", "day"])
    hl["c_n1"], hl["d_n1"] = hl.groupby("k")["c"].shift(-1), hl.groupby("k")["day"].shift(-1)
    out = []
    for _, v in B.VENUES:
        d = B.load(v)
        if d.empty:
            continue
        d = d.assign(k=d["coin"].map(B.norm)).sort_values(["k", "day"])
        g = d.groupby("coin")
        d["c_n1"], d["o_n1"], d["d_n1"] = g["c"].shift(-1), g["o"].shift(-1), g["day"].shift(-1)
        m = d.merge(hl[["k", "day", "c", "c_n1", "d_n1"]], on=["k", "day"], suffixes=("", "_hl"))
        ratio = (m["c"] / m["c_hl"]).groupby(m["coin"]).median()
        m = m[m["coin"].isin(ratio[(ratio > 0.95) & (ratio < 1.05)].index)]
        m = m[(m["c"] <= 0.97 * m["c_hl"]) & (m["d_n1"] == m["day"] + pd.Timedelta(days=1)) & (m["d_n1_hl"] == m["d_n1"])]
        out.append(m.assign(venue=v))
    e = pd.concat(out)
    e["venue_leg"] = e.c_n1 / e.c - 1
    e["hl_leg"] = -(e.c_n1_hl / e.c_hl - 1)
    e["ret"] = e.venue_leg + e.hl_leg - 4 * 0.00035
    e["disc"] = e.c / e.c_hl - 1
    return e


def line(label, g):
    r = g["ret"]
    t = r.mean() / (r.std(ddof=1) / np.sqrt(len(r))) if len(r) > 1 else np.nan
    return (f"   {label}: n {len(g)} | mean net {r.mean():+.2%} (t {t:.2f}) | venue leg {g.venue_leg.mean():+.2%}, "
            f"HL short leg {g.hl_leg.mean():+.2%} | median discount {g.disc.median():+.2%}")


def main():
    e = events()
    s2 = e[e["day"] >= B.SPLIT]
    flat = s2["h"] == s2["l"]
    print("#597 Stage 2 events by bar quality")
    print(line("all", s2))
    print(f"   flat bars (high == low) {flat.mean():.0%}; day volume < $10K {(s2.v_usd < 1e4).mean():.0%}")
    print(line("flat bars only", s2[flat]))
    print(line("traded bars (high > low)", s2[~flat]))
    clean = s2[(~flat) & (s2.v_usd >= 1e5)]
    print(line("traded bars with day volume >= $100K", clean))
    print(line("  same, discount 3%..10% only", clean[clean.disc >= -0.10]))
    print("\nHL short leg alone on the same coins and days is the alt-short baseline in disguise when the venue leg is ~0.")


if __name__ == "__main__":
    main()


def alignment():
    """Same-coin daily-return correlation, venue vs HL, at HL lag -1/0/+1 day. Aligned bars peak at lag 0."""
    hl = pd.read_parquet(B.PUB / "uncharted_385_candles.parquet")
    hl["day"] = pd.to_datetime(hl["t"], unit="ms", utc=True).dt.normalize()
    hl = hl.drop_duplicates(["coin", "day"]).assign(k=lambda x: x["coin"].map(B.norm))
    hr = hl.pivot(index="day", columns="k", values="c").pct_change(fill_method=None)
    print("\nBar alignment: median same-coin correlation of daily returns, venue vs HL shifted by L days")
    for _, v in B.VENUES:
        d = B.load(v)
        if d.empty:
            continue
        d = d[d["h"] > d["l"]].assign(k=d["coin"].map(B.norm))
        vr = d.pivot_table(index="day", columns="k", values="c").pct_change(fill_method=None)
        res = {}
        for L in (-1, 0, 1):
            cs = [vr[k].corr(hr[k].shift(-L)) for k in vr.columns if k in hr.columns and vr[k].notna().sum() > 60]
            res[L] = np.nanmedian(cs) if cs else np.nan
        print(f"   {v:<9} L -1 {res[-1]:+.2f} | L 0 {res[0]:+.2f} | L +1 {res[1]:+.2f}")


if __name__ == "__main__":
    alignment()

"""NF17 #611 stale-print check (required by the pre-registration before a PASS is accepted).

    uv run python -m scripts.batch_nf17_diag_20261128 | tee docs/jx_runs/batch_nf17_diag_20261128.txt

Rebuilds #611's events exactly, then (1) re-prices each one with entry one hour later (both legs at the h+1 closes; venue bar traded),
exit 4 hours after that; (2) reports the venue hour's USD volume at entry; (3) the gap at the next hour.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

import scripts.batch_nf17_20261128 as M


def main():
    hl = pd.read_parquet(M.PUB / "wickscale_hl_1h.parquet").rename(columns={"coin": "market"})
    hl["vol"] = hl["v"] * hl["c"]
    hg = M.grid(hl, "market")
    hg["k"] = hg["market"].map(M.norm)
    hk = hg.set_index(["k", "ts"])[["c"]].rename(columns={"c": "c_hl"})
    hk = hk[~hk.index.duplicated()]["c_hl"]
    rows = []
    for v in M.VENUES:
        g = M.grid(pd.read_parquet(M.PUB / f"batchnf15_{v}_1h.parquet").rename(columns={"coin": "market", "v_usd": "vol"}), "market")
        g["venue"], g["k"] = v, g["market"].map(M.norm)
        g["exit_ts"], g["exit_c"] = M.exit_at(g, M.HOLD)
        g = g.join(hk.rename("c_hl"), on=["k", "ts"]).join(hk.rename("hl_exit"), on=["k", "exit_ts"])
        ratio = (g["c"] / g["c_hl"]).groupby(g["market"]).median()
        g = g[g["market"].isin(ratio[(ratio > 0.95) & (ratio < 1.05)].index)].copy()
        g["size"] = np.minimum(M.CAP, M.SHARE * g["vol"])
        # one hour later: venue close and traded flag at ts+1, HL close at ts+1, and both 4 hours after that
        nxt = g[["market", "ts", "c", "vol", "h", "l"]].assign(ts=g["ts"] - pd.Timedelta(hours=1)).rename(
            columns={"c": "c1", "vol": "vol1", "h": "h1", "l": "l1"})
        g = g.merge(nxt, on=["market", "ts"], how="left")
        g["ts1"] = g["ts"] + pd.Timedelta(hours=1)
        g = g.join(hk.rename("c_hl1"), on=["k", "ts1"])
        g["ts5"] = g["ts"] + pd.Timedelta(hours=5)
        g5 = g[["market", "ts", "c"]].assign(ts=g["ts"] - pd.Timedelta(hours=5)).rename(columns={"c": "c5"})
        g = g.merge(g5, on=["market", "ts"], how="left").join(hk.rename("c_hl5"), on=["k", "ts5"])
        new = (g["first"] >= M.T("2026-04-25")) & (g["ts"] < g["first"] + pd.Timedelta(hours=72))
        gap = g["c"] / g["c_hl"] - 1
        base = (g["h"] > g["l"]) & (g["vol"] >= M.MINVOL) & g["c_hl"].notna() & (g["ts"] >= hg["ts"].min())
        m = base & g["exit_c"].notna() & g["hl_exit"].notna() & ~new & (gap.abs() >= 0.015)
        e = g[m].copy()
        d = -np.sign(gap[m])
        e["ret"] = d * ((e["exit_c"] / e["c"] - 1) - (e["hl_exit"] / e["c_hl"] - 1)) - 2 * M.COST
        ok1 = (e["h1"] > e["l1"]) & (e["vol1"] > 0) & e["c_hl1"].notna() & e["c5"].notna() & e["c_hl5"].notna()
        e["delayed"] = np.where(ok1, d * ((e["c5"] / e["c1"] - 1) - (e["c_hl5"] / e["c_hl1"] - 1)) - 2 * M.COST, np.nan)
        e["gap1"] = e["c1"] / e["c_hl1"] - 1
        e["gap0"] = gap[m]
        e["venue"] = v
        rows.append(e)
    e = M.one_open(pd.concat(rows, ignore_index=True))
    s2 = e[e["ts"] >= M.S2[0]]
    print(f"#611 events {len(e)} (Stage 2 {len(s2)}), as registered: Stage 2 mean {s2['ret'].mean():+.2%}")
    dd = s2.dropna(subset=["delayed"])
    t = dd["delayed"].mean() / (dd["delayed"].std(ddof=1) / np.sqrt(len(dd)))
    print(f"   one hour later (venue traded at h+1): n {len(dd)} of {len(s2)}; as registered {dd['ret'].mean():+.2%} -> delayed {dd['delayed'].mean():+.2%} (t {t:.2f})")
    same = (np.sign(s2["gap1"]) == np.sign(s2["gap0"])) & (s2["gap1"].abs() >= 0.005)
    print(f"   gap still >= 0.5% the same way at h+1: {same.mean():.0%}; median |gap| at h {s2['gap0'].abs().median():.2%} -> h+1 {s2['gap1'].abs().median():.2%}")
    print(f"   venue USD volume in the entry hour: median ${s2['vol'].median():,.0f}")
    for v, g in dd.groupby("venue"):
        print(f"      {v}: n {len(g)}, as registered {g['ret'].mean():+.2%}, delayed {g['delayed'].mean():+.2%}")


if __name__ == "__main__":
    main()

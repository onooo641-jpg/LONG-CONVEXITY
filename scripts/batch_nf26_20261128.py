"""Batch NF26 #647-#650: capped / extreme funding on thin venues, received hedged (docs/PREREG_BATCH_NF26_20261128.md).

    uv run python -m scripts.batch_nf26_20261128 | tee docs/jx_runs/batch_nf26_20261128.txt
"""
from __future__ import annotations

import numpy as np
import pandas as pd

import scripts.batch_nf17_20261128 as M

YR = 8760.0


def frames():
    hl = pd.read_parquet(M.PUB / "wickscale_hl_1h.parquet").rename(columns={"coin": "market"})
    hl["vol"] = hl["v"] * hl["c"]
    hg = M.grid(hl, "market")
    hg["k"] = hg["market"].map(M.norm)
    hg["x24_ts"], hg["x24_c"] = M.exit_at(hg.assign(market=hg["market"]), 24)
    hk = hg.set_index(["k", "ts"])
    hk = hk[~hk.index.duplicated()]
    hl_name = hg.drop_duplicates("k").set_index("k")["market"]
    out = []
    for v in M.VENUES:
        p = M.PUB / f"batchnf15_{v}_1h.parquet"
        g = M.grid(pd.read_parquet(p).rename(columns={"coin": "market", "v_usd": "vol"}), "market")
        g["venue"], g["k"] = v, g["market"].map(M.norm)
        g["x24_ts"], g["x24_c"] = M.exit_at(g, 24)
        g = g.join(hk[["c"]].rename(columns={"c": "c_hl"}), on=["k", "ts"])
        g = g.join(hk["c"].rename("hl_x24"), on=["k", "x24_ts"])
        ratio = (g["c"] / g["c_hl"]).groupby(g["market"]).median()
        g = g[g["market"].isin(ratio[(ratio > 0.95) & (ratio < 1.05)].index)]
        out.append(g)
    g = pd.concat(out, ignore_index=True)
    g["size"] = np.minimum(M.CAP, M.SHARE * g["vol"])
    return g, hg, hl_name


def trades(g, F, hl_name, lo, thr, side="venue", persist=1):
    rows = []
    for (v, mkt), fv in F.items():
        if v == "hl":
            continue
        k = M.norm(mkt)
        if k not in hl_name.index or ("hl", hl_name[k]) not in F:
            continue
        fh = F[("hl", hl_name[k])]
        gv = g[(g["venue"] == v) & (g["market"] == mkt) & (g["h"] > g["l"]) & (g["vol"] >= M.MINVOL) & g["c_hl"].notna()
               & (g["ts"] >= lo) & g["x24_c"].notna() & g["hl_x24"].notna()].set_index("ts")
        if gv.empty:
            continue
        full = pd.date_range(gv.index.min(), gv.index.max(), freq="h")
        rv, rh = fv.reindex(full), fh.reindex(full)
        a, b = (rv, rh) if side == "venue" else (rh, rv)  # a = the side that receives
        sgn = np.sign(a)
        cond = ((a.abs() * YR >= thr) & (sgn * (a - b) * YR >= thr)).fillna(False)
        if persist > 1:
            cond = cond.astype(int).groupby((~cond).cumsum()).cumsum() >= persist
        for ts in full[cond.to_numpy()]:
            if ts not in gv.index:
                continue
            x = gv.at[ts, "x24_ts"]
            hrs = pd.date_range(ts + M.H, x, freq="h")
            s = float(sgn[ts])
            fund = s * float((a.reindex(hrs).fillna(0) - b.reindex(hrs).fillna(0)).sum())
            pos = -s  # position on the receiving venue: short if its funding is positive
            leg_v = (gv.at[ts, "x24_c"] / gv.at[ts, "c"] - 1)
            leg_h = (gv.at[ts, "hl_x24"] / gv.at[ts, "c_hl"] - 1)
            px = pos * (leg_v - leg_h) if side == "venue" else pos * (leg_h - leg_v)
            rows.append({"ts": ts, "venue": v, "market": mkt, "exit_ts": x, "size": gv.at[ts, "size"], "fund": fund,
                         "ret": fund + px - 2 * M.COST})
    e = pd.DataFrame(rows)
    if e.empty:
        return e
    if side == "hl":  # one hedge venue per HL coin and hour: the largest funding gap
        e = e.assign(k=e["market"].map(M.norm)).sort_values("fund", ascending=False).drop_duplicates(["k", "ts"])
        e["market"] = "HL:" + e["k"]
        e["venue"] = "hl"
    return M.one_open(e)


def main():
    g, hg, hl_name = frames()
    lo = hg["ts"].min()
    F = M.per_hour(pd.read_parquet(M.PUB / "batchnf17_funding.parquet"))
    for num, label, kw in (("#647", "Venue funding >= 300%/yr, gap >= 300%/yr: receive on venue, hedge HL, 24h", dict(thr=3.0)),
                           ("#648", "Venue funding >= 1,000%/yr (cap level), gap >= 1,000%/yr", dict(thr=10.0)),
                           ("#649", "HL funding >= 300%/yr, gap vs thin venue >= 300%/yr: receive on HL, hedge on venue", dict(thr=3.0, side="hl")),
                           ("#650", "#613 trigger (>= 100%/yr) held >= 6 consecutive hours: enter at the 6th hour", dict(thr=1.0, persist=6))):
        print(num, label)
        e = trades(g, F, hl_name, lo, **kw)
        if e.empty:
            print("   no trades\n")
            continue
        print(f"   events {len(e)}; mean funding gap received {e['fund'].mean():+.2%}, price legs {(e['ret'] - e['fund'] + 2 * M.COST).mean():+.2%}")
        M.verdict(e, lo)


if __name__ == "__main__":
    main()

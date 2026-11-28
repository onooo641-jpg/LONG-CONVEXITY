"""NF16 #603 stale-print diagnostic (post-hoc, required by the pre-registration before a PASS is accepted).

    uv run python -m scripts.batch_nf16_diag_20261128 | tee docs/jx_runs/batch_nf16_diag_20261128.txt

Checks: (1) which leg is the thin one; (2) reference-leg volume at entry; (3) delayed entry: enter both legs at the close one hour
later (both must trade that hour), exit 4 hours after that. A real, executable gap should leave a positive part after a one-hour
delay; a gap made of stale last trades in a thin book vanishes or reverses.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

import scripts.batch_nf16_20261128 as M


def main():
    g = M.spot_grid(pd.read_parquet(M.PUB / "batchnf16_hlspot_1h.parquet"))
    idx = g.set_index(["pair", "ts"])
    rows = []
    multi = g[~g["base"].map(M.stable)].groupby("base")["pair"].nunique()
    for base in multi[multi >= 2].index:
        b = g[g["base"] == base]
        px = b.pivot(index="ts", columns="pair", values="px")
        tr = b.pivot(index="ts", columns="pair", values="traded").fillna(False).astype(bool)
        usdc = b.loc[b["quote"] == "USDC", "pair"].unique()
        for pair in px.columns:
            others = [c for c in px.columns if c != pair]
            if pair in usdc:
                ref = px[others].where(tr[others]).median(axis=1)
            elif len(usdc):
                ref = px[usdc[0]].where(tr[usdc[0]])
            else:
                continue
            me = idx.loc[pair]
            hit = (me["px"] <= 0.99 * ref.reindex(me.index)) & me["traded"] & (me["v_usd"] >= M.MINVOL) & me["exit_px"].notna()
            for ts in me.index[hit.fillna(False)]:
                if pair in usdc:
                    cand = [c for c in others if tr.at[ts, c]]
                    if not cand:
                        continue
                    rp = max(cand, key=lambda c: float(idx.at[(c, ts), "v_usd"]))
                else:
                    rp = usdc[0]
                if not np.isfinite(idx.at[(rp, ts), "exit_px"]):
                    continue
                ret = (me.at[ts, "exit_px"] / me.at[ts, "px"] - 1) - (idx.at[(rp, ts), "exit_px"] / idx.at[(rp, ts), "px"] - 1) - 4 * M.FEE
                t1 = ts + pd.Timedelta(hours=1)
                d = np.nan
                if (pair, t1) in idx.index and (rp, t1) in idx.index and idx.at[(pair, t1), "traded"] and idx.at[(rp, t1), "traded"]:
                    a, r = idx.loc[(pair, t1)], idx.loc[(rp, t1)]
                    if np.isfinite(a["exit_px"]) and np.isfinite(r["exit_px"]):
                        d = (a["exit_px"] / a["px"] - 1) - (r["exit_px"] / r["px"] - 1) - 4 * M.FEE
                rows.append({"ts": ts, "pair": pair, "ref": rp, "cheap_is_usdc": pair in usdc, "ret": ret, "delayed": d,
                             "v_cheap": me.at[ts, "v_usd"], "v_ref": idx.at[(rp, ts), "v_usd"],
                             "gap_next": (idx.at[(pair, t1), "px"] / idx.at[(rp, t1), "px"] - 1) if (pair, t1) in idx.index and (rp, t1) in idx.index else np.nan})
    e = pd.DataFrame(rows).sort_values("ts")
    keep, busy = [], {}
    for i, r in e.iterrows():
        if r["pair"] in busy and r["ts"] < busy[r["pair"]]:
            continue
        busy[r["pair"]] = r["ts"] + pd.Timedelta(hours=M.HOLD)
        keep.append(i)
    e = e.loc[keep]
    print(f"#603 events {len(e)} (as registered)")
    for k, s in e.groupby("cheap_is_usdc"):
        print(f"   cheap leg = {'USDC book (reference = thin book)' if k else 'thin book (reference = USDC book)'}: n {len(s)}, "
              f"mean {s['ret'].mean():+.2%}, median ref-leg volume ${s['v_ref'].median():,.0f}, median cheap-leg volume ${s['v_cheap'].median():,.0f}")
    d = e.dropna(subset=["delayed"])
    print(f"   delayed one hour (both legs traded at t+1): n {len(d)} of {len(e)}; as registered {d['ret'].mean():+.2%} -> delayed "
          f"{d['delayed'].mean():+.2%} (t {d['delayed'].mean() / (d['delayed'].std(ddof=1) / np.sqrt(len(d))):.2f})")
    for k, s in d.groupby("cheap_is_usdc"):
        print(f"      cheap leg {'USDC' if k else 'thin'}: n {len(s)}, delayed mean {s['delayed'].mean():+.2%}")
    print(f"   gap at the next hour's closes: median {e['gap_next'].median():+.2%}; share still <= -1%: {(e['gap_next'] <= -0.01).mean():.0%}")
    print(f"   by month: " + "; ".join(f"{m} n {len(s)} {s['ret'].mean():+.2%}" for m, s in e.groupby(e['ts'].dt.strftime('%Y-%m'))))


if __name__ == "__main__":
    main()

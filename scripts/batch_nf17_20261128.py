"""Batch NF17 #610-#613: thin-venue dislocations against Hyperliquid, hourly, hedged (docs/PREREG_BATCH_NF17_20261128.md).

    uv run python -m scripts.batch_nf17_20261128 | tee docs/jx_runs/batch_nf17_20261128.txt
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from scripts.batch_nf14_20261128 import norm

PUB = Path(__file__).resolve().parent.parent / "data" / "public"
COST, CAP, SHARE, MINVOL, HOLD, K = 0.0007, 1500.0, 0.01, 20_000.0, 4, 5.0
T = lambda s: pd.Timestamp(s, tz="UTC")  # noqa: E731
S1_END, S2 = T("2026-08-16"), (T("2026-08-16"), T("2026-11-26"))
VENUES = ["backpack", "extended", "pacifica", "apex"]
H = pd.Timedelta(hours=1)


def grid(d, key):
    """Hourly grid per market: close, return, sigma(168h), USD volume, traded flag."""
    d = d.copy()
    d["ts"] = pd.to_datetime(d["t"], unit="ms", utc=True).dt.floor("h")
    d = d[(d["c"] > 0) & (d["l"] > 0)].drop_duplicates([key, "ts"])
    out = []
    for m, g in d.groupby(key):
        g = g.set_index("ts").sort_index()
        g = g.reindex(pd.date_range(g.index.min(), g.index.max(), freq="h"))
        g[key] = m
        g["vol"] = g["vol"].fillna(0.0)
        c = g["c"].ffill()
        g["r"] = c.pct_change(fill_method=None)
        g["sig"] = g["r"].rolling(168, min_periods=100).std().shift()
        g["first"] = g.index.min()
        out.append(g.reset_index(names="ts"))
    return pd.concat(out, ignore_index=True)


def exit_at(g, hold):
    """Per row: timestamp and venue close of the first traded hour at +hold..+2*hold hours."""
    xt = pd.Series(pd.NaT, index=g.index, dtype="datetime64[ns, UTC]")
    xc = pd.Series(np.nan, index=g.index)
    for m, idx in g.groupby("market").groups.items():
        s = g.loc[idx]
        for k in range(hold, hold + max(hold, 4) + 1):
            ok = (s["vol"].shift(-k) > 0) & xc.loc[idx].isna()
            xc.loc[idx] = xc.loc[idx].where(~ok, s["c"].shift(-k))
            xt.loc[idx] = xt.loc[idx].where(~ok, s["ts"].shift(-k))
    return xt, xc


def one_open(e, hold_col="exit_ts"):
    keep, busy = [], {}
    for i, r in e.sort_values("ts").iterrows():
        k = r["venue"] + ":" + r["market"]
        if k in busy and r["ts"] < busy[k]:
            continue
        busy[k] = r[hold_col]
        keep.append(i)
    return e.loc[keep]


def summ(e, lo, hi, extra=0.0):
    g = e[(e["ts"] >= lo) & (e["ts"] < hi)]
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


def verdict(e, lo):
    a, b = summ(e, lo, S1_END), summ(e, *S2)
    b15 = summ(e, *S2, extra=0.5 * COST * 2)
    print(fmt(f"Stage 1 {lo.date()}..2026-08-15", a))
    print(fmt("Stage 2 2026-08-16..2026-11-25", b))
    print(f"   costs x1.5 Stage 2 mean {b15.get('m', np.nan):+.2%}")
    if len(e):
        print("   by venue: " + "; ".join(f"{v} n {len(g)} {g['ret'].mean():+.2%}" for v, g in e.groupby("venue")))
        top = e.groupby(["venue", "market"]).size().sort_values(ascending=False).head(3)
        print("   most events: " + "; ".join(f"{v}:{m} {n}" for (v, m), n in top.items()))
    if a.get("n", 0) >= 30 and not (a["m"] > 0):
        v = "KILL (Stage 1)"
    else:
        v = "PASS" if (b.get("n", 0) >= 30 and b["m"] >= 0.003 and b["t"] >= 2 and b["ex3"] > 0 and b15["m"] > 0) else "FAIL"
    if v == "PASS":
        v += " (forward log after the stale-print check)" if b["t"] >= 2.5 else " (t < 2.5: not forward-logged)"
    print(f"   VERDICT {v}\n")


def per_hour(f):
    """Funding rate per hour on the hour grid; per-interval rates divided by the market's median settlement gap."""
    f = f.copy()
    f["ts"] = pd.to_datetime(f["t"], unit="ms", utc=True).dt.floor("h")
    out = {}
    for (v, m), g in f.groupby(["venue", "market"]):
        s = g.groupby("ts")["rate_raw"].mean().sort_index()
        iv = float(s.index.to_series().diff().dt.total_seconds().div(3600).median()) if len(s) > 2 else 1.0
        iv = max(1.0, round(iv)) if np.isfinite(iv) else 1.0
        s = (s / iv).reindex(pd.date_range(s.index.min(), s.index.max(), freq="h")).bfill(limit=int(iv) - 1) if iv > 1 else s
        out[(v, m)] = s
    return out


def main():
    hl = pd.read_parquet(PUB / "wickscale_hl_1h.parquet").rename(columns={"coin": "market"})
    hl["vol"] = hl["v"] * hl["c"]
    hg = grid(hl, "market")
    hg["k"] = hg["market"].map(norm)
    hl_lo = hg["ts"].min()
    hk = hg.set_index(["k", "ts"])[["c", "r", "sig"]].rename(columns=lambda c: c + "_hl")
    hk = hk[~hk.index.duplicated()]
    hl_name = hg.drop_duplicates("k").set_index("k")["market"]

    frames = []
    for v in VENUES:
        p = PUB / f"batchnf15_{v}_1h.parquet"
        if not p.exists():
            print(f"{v}: no hourly candles")
            continue
        g = grid(pd.read_parquet(p).rename(columns={"coin": "market", "v_usd": "vol"}), "market")
        g["venue"], g["k"] = v, g["market"].map(norm)
        g["exit_ts"], g["exit_c"] = exit_at(g, HOLD)
        g["x24_ts"], g["x24_c"] = exit_at(g, 24)
        g = g.join(hk, on=["k", "ts"])
        ex = hk["c_hl"].rename("hl_exit")
        g = g.join(ex, on=["k", "exit_ts"]).join(ex.rename("hl_x24"), on=["k", "x24_ts"])
        ratio = (g["c"] / g["c_hl"]).groupby(g["market"]).median()
        keep = ratio[(ratio > 0.95) & (ratio < 1.05)].index
        print(f"{v}: markets {g['market'].nunique()}, matched to HL {g.loc[g['c_hl'].notna(), 'market'].nunique()}, kept by unit check {len(keep)}")
        frames.append(g[g["market"].isin(keep)])
    if not frames:
        return
    g = pd.concat(frames, ignore_index=True)
    g["size"] = np.minimum(CAP, SHARE * g["vol"])
    base = (g["h"] > g["l"]) & (g["vol"] >= MINVOL) & g["c_hl"].notna() & (g["ts"] >= hl_lo)
    hedged4 = base & g["exit_c"].notna() & g["hl_exit"].notna()
    gap = g["c"] / g["c_hl"] - 1
    leg = lambda d, xc, hx: d * ((g[xc] / g["c"] - 1) - (g[hx] / g["c_hl"] - 1))  # noqa: E731
    new = (g["first"] >= T("2026-04-25")) & (g["ts"] < g["first"] + pd.Timedelta(hours=72))
    print()

    print("#610 New-listing dislocation (first 72 hours, |gap| >= 2%), trade toward HL, 4 hours")
    m = hedged4 & new & (gap.abs() >= 0.02)
    e = g[m].assign(ret=leg(-np.sign(gap), "exit_c", "hl_exit")[m] - 2 * COST)
    print(f"   new listings with HL coin: {g.loc[new & g['c_hl'].notna(), 'market'].nunique()}")
    verdict(one_open(e), hl_lo)

    print("#611 Hourly gap convergence (|gap| >= 1.5%, outside first 72 hours), trade toward HL, 4 hours")
    m = hedged4 & ~new & (gap.abs() >= 0.015)
    e = g[m].assign(ret=leg(-np.sign(gap), "exit_c", "hl_exit")[m] - 2 * COST)
    verdict(one_open(e), hl_lo)

    print("#612 Venue-local pump fade (venue >= +5 sigma, HL < +1.5 sigma), short venue / long HL, 4 hours")
    m = hedged4 & (g["r"] >= K * g["sig"]) & (g["r_hl"] < 1.5 * g["sig_hl"])
    e = g[m].assign(ret=leg(-1.0, "exit_c", "hl_exit")[m] - 2 * COST)
    verdict(one_open(e), hl_lo)

    print("#613 Venue-local funding spike (|venue| >= 100%/yr and gap vs HL >= 100%/yr), receive on venue, hedge HL, 24 hours")
    p = PUB / "batchnf17_funding.parquet"
    if not p.exists():
        print("   not testable (no funding data)\n")
        return
    fr = pd.read_parquet(p)
    F = per_hour(fr)
    for v in ("hl", "backpack", "extended", "pacifica"):
        b = [s for (vv, mm), s in F.items() if vv == v and norm(mm) == "BTC"]
        print(f"   units check {v}: BTC median per hour {np.nanmedian(b[0]) if b else float('nan'):.2e}")
    rows = []
    for (v, mkt), fv in F.items():
        if v == "hl":
            continue
        k = norm(mkt)
        if k not in hl_name.index or ("hl", hl_name[k]) not in F:
            continue
        fh = F[("hl", hl_name[k])]
        gv = g[(g["venue"] == v) & (g["market"] == mkt) & base & g["x24_c"].notna() & g["hl_x24"].notna()].set_index("ts")
        if gv.empty:
            continue
        rv, rh = fv.reindex(gv.index), fh.reindex(gv.index)
        sgn = np.sign(rv)
        hit = (rv.abs() * 8760 >= 1.0) & (sgn * (rv - rh) * 8760 >= 1.0)
        for ts in gv.index[hit.fillna(False)]:
            x = gv.at[ts, "x24_ts"]
            hrs = pd.date_range(ts + H, x, freq="h")
            fund = float(sgn[ts] * (fv.reindex(hrs).fillna(0) - fh.reindex(hrs).fillna(0)).sum())
            s = -sgn[ts]  # venue position: short if venue funding is positive
            px = s * ((gv.at[ts, "x24_c"] / gv.at[ts, "c"] - 1) - (gv.at[ts, "hl_x24"] / gv.at[ts, "c_hl"] - 1))
            rows.append({"ts": ts, "venue": v, "market": mkt, "exit_ts": x, "size": gv.at[ts, "size"], "fund": fund,
                         "ret": fund + px - 2 * COST})
    e = pd.DataFrame(rows)
    if e.empty:
        print("   no events\n")
        return
    e = one_open(e)
    print(f"   events {len(e)}; mean funding gap received {e['fund'].mean():+.2%}, price legs {(e['ret'] - e['fund'] + 2 * COST).mean():+.2%}")
    verdict(e, hl_lo)


if __name__ == "__main__":
    main()

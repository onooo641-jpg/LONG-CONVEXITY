"""Batch NF15 #598-#602: hourly cascades on thin perp venues (docs/PREREG_BATCH_NF15_20261128.md).

    uv run python -m scripts.batch_nf15_20261128 | tee docs/jx_runs/batch_nf15_20261128.txt
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
VENUES = [("#598", "backpack"), ("#599", "extended"), ("#600", "pacifica"), ("#601", "apex")]


def prep(d):
    """Hourly grid per market (missing hours = no bar), sigma over the previous 168 hours, executable exit 4h later."""
    d = d.copy()
    d["ts"] = pd.to_datetime(d["t"], unit="ms", utc=True).dt.floor("h")
    d = d[(d["c"] > 0) & (d["l"] > 0)].drop_duplicates(["coin", "ts"])
    out = []
    for coin, g in d.groupby("coin"):
        g = g.set_index("ts").sort_index()
        g = g.reindex(pd.date_range(g.index.min(), g.index.max(), freq="h"))
        g["coin"] = coin
        g["v_usd"] = g["v_usd"].fillna(0.0)
        c = g["c"].ffill()
        g["r"] = c.pct_change(fill_method=None)
        g["sig"] = g["r"].rolling(168, min_periods=100).std().shift()
        # exit: close at +4h if that hour traded, else the next traded hour up to +8h
        ex = pd.Series(np.nan, index=g.index)
        for k in range(HOLD, 2 * HOLD + 1):
            cand = g["c"].shift(-k).where(g["v_usd"].shift(-k) > 0)
            ex = ex.fillna(cand)
        g["exit_c"] = ex
        out.append(g.reset_index(names="ts"))
    return pd.concat(out, ignore_index=True) if out else pd.DataFrame()


def one_per_market(e):
    keep, last = [], {}
    for i, r in e.sort_values("ts").iterrows():
        if r["coin"] in last and r["ts"] < last[r["coin"]] + pd.Timedelta(hours=HOLD):
            continue
        last[r["coin"]] = r["ts"]
        keep.append(i)
    return e.loc[keep]


def summ(e, lo, hi, extra=0.0):
    g = e[(e["ts"] >= lo) & (e["ts"] < hi)]
    if g.empty:
        return dict(n=0)
    r = g["ret"] - extra
    days = max((hi - lo).days, 1)
    srt = (g["size"] * r).sort_values()
    return dict(n=len(g), m=r.mean(), t=r.mean() / (r.std(ddof=1) / np.sqrt(len(r))) if len(r) > 1 else np.nan, win=(r > 0).mean(),
                usd=(g["size"] * r).sum() * 365 / days, ex3=srt.iloc[:-3].sum() if len(srt) > 3 else np.nan)


def fmt(label, s):
    if not s.get("n"):
        return f"   {label}: no trades"
    return (f"   {label}: trades {s['n']} | mean net {s['m']:+.2%} (t {s['t']:.2f}, win {s['win']:.0%}) | ${s['usd']:,.0f}/yr "
            f"| sum without 3 best ${s['ex3']:,.0f}")


def verdict(e, lo, legs=1):
    a, b = summ(e, lo, S1_END), summ(e, *S2)
    b15 = summ(e, *S2, extra=0.5 * COST * legs)
    print(fmt(f"Stage 1 {lo.date()}..2026-08-15", a))
    print(fmt("Stage 2 2026-08-16..2026-11-25", b))
    print(f"   costs x1.5 Stage 2 mean {b15.get('m', np.nan):+.2%}")
    if a.get("n", 0) >= 30 and not (a["m"] > 0):
        v = "KILL (Stage 1)"
    else:
        v = "PASS" if (b.get("n", 0) >= 30 and b["m"] >= 0.003 and b["t"] >= 2 and b["ex3"] > 0 and b15["m"] > 0) else "FAIL"
    if v == "PASS":
        v += " (forward log)" if b["t"] >= 2.5 else " (t < 2.5: not forward-logged)"
    print(f"   VERDICT {v}\n")


def main():
    hl = pd.read_parquet(PUB / "wickscale_hl_1h.parquet")
    hl["ts"] = pd.to_datetime(hl["t"], unit="ms", utc=True).dt.floor("h")
    hl = hl.drop_duplicates(["coin", "ts"]).sort_values(["coin", "ts"])
    hl["k"] = hl["coin"].map(norm)
    hl["r"] = hl.groupby("coin")["c"].pct_change(fill_method=None)
    hl["sig"] = hl.groupby("coin")["r"].transform(lambda s: s.rolling(168, min_periods=100).std().shift())
    hl["c4"] = hl.groupby("coin")["c"].shift(-HOLD)
    hl_lo = hl["ts"].min()
    local = []
    for num, v in VENUES:
        p = PUB / f"batchnf15_{v}_1h.parquet"
        raw = pd.read_parquet(p) if p.exists() else pd.DataFrame()
        print(f"{num} #569 hourly cascade reversal on {v}")
        if raw.empty:
            print("   not testable (no hourly candles)\n")
            continue
        g = prep(raw)
        print(f"   markets {g['coin'].nunique()}, hours {g['c'].notna().sum():,}, {g['ts'].min()}..{g['ts'].max()}")
        sig = (g["r"] <= -K * g["sig"]) & (g["h"] > g["l"]) & (g["v_usd"] >= MINVOL) & g["exit_c"].notna()
        e = g[sig].copy()
        e["ret"] = e["exit_c"] / e["c"] - 1 - COST
        e["size"] = np.minimum(CAP, SHARE * e["v_usd"])
        e = one_per_market(e)
        verdict(e, g["ts"].min())

        g["k"] = g["coin"].map(norm)
        m = g[sig].merge(hl[["k", "ts", "c", "sig", "r", "c4"]], on=["k", "ts"], suffixes=("", "_hl"))
        ratio = (m["c"] / m["c_hl"]).groupby(m["coin"]).median()
        m = m[m["coin"].isin(ratio[(ratio > 0.95) & (ratio < 1.05)].index) & m["c4"].notna()]
        m = m[m["r_hl"] > -1.5 * m["sig_hl"]]
        if len(m):
            m["ret"] = (m["exit_c"] / m["c"] - 1) - (m["c4"] / m["c_hl"] - 1) - 2 * COST
            m["size"] = np.minimum(CAP, SHARE * m["v_usd"])
            local.append(m.assign(venue=v))

    print("#602 Venue-local cascade (venue <= -5 sigma, HL > -1.5 sigma same hour), long venue / short HL, 4 hours")
    if not local:
        print("   no events\n")
        return
    e = one_per_market(pd.concat(local, ignore_index=True).assign(coin=lambda x: x["venue"] + ":" + x["coin"]))
    print("   events by venue: " + ", ".join(f"{v} {n}" for v, n in e["venue"].value_counts().items()))
    verdict(e, hl_lo, legs=2)


if __name__ == "__main__":
    main()

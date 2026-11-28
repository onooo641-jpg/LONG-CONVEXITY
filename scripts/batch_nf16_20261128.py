"""Batch NF16 #603-#609: HL spot duplicate and stablecoin books; #520/#536 on GRVT, Nado, Ethereal, Hibachi
(docs/PREREG_BATCH_NF16_20261128.md).

    uv run python -m scripts.batch_nf16_20261128 | tee docs/jx_runs/batch_nf16_20261128.txt
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

import scripts.batch_nf14_20261128 as B14

PUB = Path(__file__).resolve().parent.parent / "data" / "public"
FEE, CAP, SHARE, MINVOL, HOLD = 0.0007, 1500.0, 0.01, 5_000.0, 4
T = lambda s: pd.Timestamp(s, tz="UTC")  # noqa: E731
S1_END, S2 = T("2026-08-16"), (T("2026-08-16"), T("2026-11-26"))
VENUES = [("#605", "grvt"), ("#606", "nado"), ("#607", "ethereal"), ("#608", "hibachi")]
stable = lambda s: "USD" in str(s).upper() or str(s).upper() == "USDT0"  # noqa: E731


def spot_grid(d):
    """Hourly grid per book with USDC-valued prices, USD volume and the executable exit 4..8 hours later."""
    d = d.copy()
    d["ts"] = pd.to_datetime(d["t"], unit="ms", utc=True).dt.floor("h")
    d = d[(d["c"] > 0) & (d["l"] > 0)].drop_duplicates(["pair", "ts"])
    # quote -> USDC rate: close of the quote token's USDC book (base = quote token, quote = USDC)
    rate = {q: d[(d["base"] == q) & (d["quote"] == "USDC")].set_index("ts")["c"] for q in d["quote"].unique() if q != "USDC"}
    out = []
    for pair, g in d.groupby("pair"):
        g = g.set_index("ts").sort_index()
        g = g.reindex(pd.date_range(g.index.min(), g.index.max(), freq="h"))
        g["pair"], g["base"], g["quote"] = pair, g["base"].dropna().iloc[0], g["quote"].dropna().iloc[0]
        q = g["quote"].iloc[0]
        fx = pd.Series(1.0, index=g.index) if q == "USDC" else rate.get(q, pd.Series(dtype=float)).reindex(g.index).ffill(limit=6)
        traded = (g["v"] > 0) & (g["h"] > g["l"])
        g["traded"] = traded.fillna(False)
        g["px"] = g["c"] * fx
        g["v_usd"] = (g["v"] * g["c"] * fx).fillna(0.0)
        ex = pd.Series(np.nan, index=g.index)
        for k in range(HOLD, 2 * HOLD + 1):
            ex = ex.fillna(g["px"].shift(-k).where(g["v"].shift(-k) > 0))
        g["exit_px"] = ex
        out.append(g.reset_index(names="ts"))
    return pd.concat(out, ignore_index=True)


def one_open(e, key, hold_col=None):
    keep, busy = [], {}
    for i, r in e.sort_values("ts").iterrows():
        if r[key] in busy and r["ts"] < busy[r[key]]:
            continue
        busy[r[key]] = r[hold_col] if hold_col else r["ts"] + pd.Timedelta(hours=HOLD)
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


def verdict(e, lo, legs, min_n=30):
    a, b = summ(e, lo, S1_END), summ(e, *S2)
    b15 = summ(e, *S2, extra=0.5 * 2 * FEE * legs)
    print(fmt(f"Stage 1 {lo.date()}..2026-08-15", a))
    print(fmt("Stage 2 2026-08-16..2026-11-25", b))
    print(f"   costs x1.5 Stage 2 mean {b15.get('m', np.nan):+.2%}")
    if len(e):
        top = e.groupby("pair")["ret"].agg(["size", "mean"]).sort_values("size", ascending=False).head(6)
        print("   by book: " + "; ".join(f"{k} n {int(r['size'])} {r['mean']:+.2%}" for k, r in top.iterrows()))
    if a.get("n", 0) >= 30 and not (a["m"] > 0):
        v = "KILL (Stage 1)"
    else:
        ok = b.get("n", 0) >= min_n and b["m"] >= 0.003 and b["t"] >= 2 and b["ex3"] > 0 and b15["m"] > 0
        v = "PASS" if ok else "FAIL"
    if v == "PASS":
        v += " (forward log after the stale-print check)" if b["t"] >= 2.5 else " (t < 2.5: not forward-logged)"
    print(f"   VERDICT {v}\n")


def hl_spot():
    p = PUB / "batchnf16_hlspot_1h.parquet"
    if not p.exists() or pd.read_parquet(p).empty:
        print("#603/#604 not testable (no HL spot hourly candles)\n")
        return
    g = spot_grid(pd.read_parquet(p))
    print(f"HL spot books {g['pair'].nunique()}, hours {g['c'].notna().sum():,}, {g['ts'].min()}..{g['ts'].max()}\n")
    lo = g["ts"].min()

    print("#603 Duplicate-book discount: cheap book <= 0.99 x reference (same hour), buy cheap / sell reference, 4 hours")
    multi = g[~g["base"].map(stable)].groupby("base")["pair"].nunique()
    rows = []
    for base in multi[multi >= 2].index:
        b = g[g["base"] == base]
        px = b.pivot(index="ts", columns="pair", values="px")
        tr = b.pivot(index="ts", columns="pair", values="traded").fillna(False).astype(bool)
        usdc = b.loc[b["quote"] == "USDC", "pair"].unique()
        for pair in px.columns:
            if pair in usdc:
                others = [c for c in px.columns if c != pair]
                ref = px[others].where(tr[others]).median(axis=1)
                ref_pair = None
            elif len(usdc):
                ref_pair = usdc[0]
                ref = px[ref_pair].where(tr[ref_pair])
            else:
                continue
            me = b[b["pair"] == pair].set_index("ts")
            hit = (me["px"] <= 0.99 * ref.reindex(me.index)) & me["traded"] & (me["v_usd"] >= MINVOL) & me["exit_px"].notna()
            for ts in me.index[hit.fillna(False)]:
                if ref_pair is None:  # cheap book is USDC: sell the most liquid other book that traded this hour
                    cand = [c for c in others if tr.at[ts, c]]
                    if not cand:
                        continue
                    rp = max(cand, key=lambda c: float(b.loc[(b["pair"] == c) & (b["ts"] == ts), "v_usd"].iloc[0]))
                else:
                    rp = ref_pair
                rr = b[(b["pair"] == rp)].set_index("ts")
                if ts not in rr.index or not np.isfinite(rr.at[ts, "exit_px"]):
                    continue
                rows.append({"ts": ts, "pair": pair, "base": base, "ref": rp, "size": min(CAP, SHARE * me.at[ts, "v_usd"]),
                             "gap": me.at[ts, "px"] / ref.at[ts] - 1,
                             "ret": (me.at[ts, "exit_px"] / me.at[ts, "px"] - 1) - (rr.at[ts, "exit_px"] / rr.at[ts, "px"] - 1) - 4 * FEE})
    e = one_open(pd.DataFrame(rows), "pair") if rows else pd.DataFrame(columns=["ts", "pair", "ret", "size"])
    if len(e):
        print(f"   events {len(e)} on {e['pair'].nunique()} books; median gap at entry {e['gap'].median():+.2%}")
    verdict(e, lo, legs=2)

    print("#604 Stablecoin-book dip: USD stablecoin / USDC close <= 0.997 -> buy, exit at close >= 0.9995 or 168 hours")
    rows = []
    for pair, s in g[g["base"].map(stable) & (g["quote"] == "USDC")].groupby("pair"):
        s = s.set_index("ts").sort_index()
        c, v, trd = s["c"], s["v_usd"], s["traded"]
        hit = (c <= 0.997) & trd & (v >= MINVOL)
        for ts in s.index[hit]:
            fut = s.loc[ts + pd.Timedelta(hours=1): ts + pd.Timedelta(hours=168)]
            fut = fut[fut["v"] > 0]
            if fut.empty:
                continue
            ok = fut[fut["c"] >= 0.9995]
            if len(ok):
                xt, xp = ok.index[0], ok["c"].iloc[0]
            elif fut.index[-1] >= ts + pd.Timedelta(hours=160):
                xt, xp = fut.index[-1], fut["c"].iloc[-1]
            else:
                continue  # 168-hour exit not yet observable at the data end
            rows.append({"ts": ts, "pair": pair, "exit_ts": xt, "size": min(CAP, SHARE * v[ts]), "ret": xp / c[ts] - 1 - 2 * FEE,
                         "hold_h": (xt - ts) / pd.Timedelta(hours=1)})
    e = one_open(pd.DataFrame(rows), "pair", "exit_ts") if rows else pd.DataFrame(columns=["ts", "pair", "ret", "size"])
    if len(e):
        print(f"   events {len(e)} on {e['pair'].nunique()} books; median hold {e['hold_h'].median():.0f} h; worst {e['ret'].min():+.2%}")
    verdict(e, lo, legs=1, min_n=15)


def venues():
    B14.SPLIT, B14.END = T("2026-05-01"), T("2026-11-25")
    data = {}
    for _, v in VENUES:
        p = PUB / f"batchnf16_{v}_1d.parquet"
        d = pd.read_parquet(p) if p.exists() else pd.DataFrame()
        if len(d):
            d["day"] = pd.to_datetime(d["t"], unit="ms", utc=True).dt.normalize()
            d = d[(d["day"] <= B14.END) & (d["c"] > 0) & (d["l"] > 0)].drop_duplicates(["coin", "day"]).sort_values(["coin", "day"])
            d = d.assign(venue=v).reset_index(drop=True)
        data[v] = d
        print(f"   {v:<9} " + (f"markets {d['coin'].nunique():>4}, rows {len(d):>6}, {d['day'].min().date()}..{d['day'].max().date()}"
                               if len(d) else "NO DATA (not testable)"))
    print()
    for num, v in VENUES:
        d = data[v]
        print(f"{num} #520 wick bids on {v}")
        if d.empty:
            print("   not testable (no candles)\n")
            continue
        f, f15 = B14.pnl(B14.wick(d, "vol")), B14.pnl(B14.wick(d, "vol", 1.5))
        a, b, b15, vd = B14.judge(f, f15, d["day"].min())
        print(B14.fmt(f"Stage 1 {d['day'].min().date()}..2026-04-30", a))
        print(B14.fmt("Stage 2 2026-05-01..2026-11-25", b))
        print(f"   costs x1.5 Stage 2 mean {b15.get('m', np.nan):+.2%}")
        print(f"   VERDICT {vd}{' (t < 2.5: not forward-logged)' if vd == 'PASS' and b['t'] < 2.5 else ''}\n")

    print("#609 #536 rule (first 30 days, X 15%) pooled on the four venues")
    parts = [B14.wick(data[v], "new") for _, v in VENUES if len(data[v])]
    parts15 = [B14.wick(data[v], "new", 1.5) for _, v in VENUES if len(data[v])]
    parts, parts15 = [p for p in parts if len(p)], [p for p in parts15 if len(p)]
    if not parts:
        print("   no fills (not testable)\n")
        return
    f, f15 = B14.pnl(pd.concat(parts, ignore_index=True)), B14.pnl(pd.concat(parts15, ignore_index=True))
    a, b, b15, vd = B14.judge(f, f15, min(d["day"].min() for d in data.values() if len(d)))
    print(B14.fmt("Stage 1", a))
    print(B14.fmt("Stage 2", b))
    print("   per venue (all): " + "; ".join(f"{v} n {len(g)} {g['ret'].mean():+.2%}" for v, g in f.groupby("venue")))
    print(f"   VERDICT {vd}\n")


def main():
    hl_spot()
    print("Venue coverage:")
    venues()


if __name__ == "__main__":
    main()

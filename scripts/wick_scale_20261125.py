"""#402-#404: scaling and hardening #389 (docs/PREREG_WICK_SCALE_20261125.md).

    uv run python -m scripts.wick_scale_20261125 | tee docs/jx_runs/wick_scale_20261125.txt
Reads data/public/wickscale_* (Actions job uscale).
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

PUB = Path(__file__).resolve().parent.parent / "data" / "public"
MAKER, TAKER, THROUGH, CAP, VSHARE, POT = 0.00015, 0.00045, 0.005, 1500.0, 0.01, 15_000.0


def tstat(r):
    return r.mean() / (r.std(ddof=1) / np.sqrt(len(r))) if len(r) > 1 else np.nan


def path(pnl_by_day):
    d = pnl_by_day.sort_index()
    d = d.reindex(pd.date_range(d.index.min(), d.index.max(), freq="D", tz="UTC"), fill_value=0.0)
    eq = d.cumsum()
    return float((eq - eq.cummax()).min()), float(d.min())


def pot_scale(f, key, pot=POT):
    tot = f.groupby(key)["size"].transform("sum")
    return f["size"] * np.minimum(1.0, pot / tot) * f["ret"]


# ---------------------------------------------------------------- #402 hourly
def part402():
    print("#### #402 hourly wick bids")
    p = PUB / "wickscale_binance_1h_fills.parquet"
    if not p.exists():
        print("  Binance 1h fills not fetched")
        return
    f = pd.read_parquet(p)
    f = f[f["size"] > 0].copy()
    f["ts"] = pd.to_datetime(f["t"], unit="s", utc=True)
    f = f[(f["ts"] >= "2022-01-01") & (f["ts"] < "2026-11-01")]
    yrs = (pd.Timestamp("2026-11-01", tz="UTC") - pd.Timestamp("2022-01-01", tz="UTC")).days / 365
    print(f"  Binance 1h fills file: {len(f)} rows, symbols {f['sym'].nunique()}, {f['ts'].min()}..{f['ts'].max()}")
    verdict = "KILL (no fills)"
    for x in (0.08, 0.05, 0.12):
        g = f[f["x"] == x].copy()
        if g.empty:
            continue
        g["pnl"] = pot_scale(g, "t")
        r = g["ret"]
        per_yr = g["pnl"].sum() / yrs
        dd, worst = path(g.groupby(g["ts"].dt.normalize())["pnl"].sum())
        by = g.groupby(g["ts"].dt.year).agg(n=("ret", "size"), mean=("ret", "mean"), pnl=("pnl", "sum"))
        hy = g.groupby(g["ts"].dt.year.astype(str) + "H" + ((g["ts"].dt.month > 6) + 1).astype(str))["ret"].mean()
        print(f"  X {x:.0%}{' (primary)' if x == 0.08 else ''}: fills {len(g)}; mean {r.mean():.2%} (median {r.median():.2%}, t {tstat(r):.2f}, "
              f"win {(r > 0).mean():.0%}); ${per_yr:,.0f}/yr; worst peak-to-trough ${dd:,.0f}; worst day ${worst:,.0f}")
        print("     by year: " + "; ".join(f"{y} n {int(a.n)} {a['mean']:+.2%} ${a.pnl:,.0f}" for y, a in by.iterrows()))
        print("     half-year mean: " + "; ".join(f"{h} {v:+.2%}" for h, v in hy.items()))
        if x == 0.08:
            kill = r.mean() < 0.003 or tstat(r) < 3 or per_yr < 3000
            verdict = "KILL" if kill else "survives (kill-only)"
    print(f"  STAGE 1 VERDICT (Binance 1h, X 8%): {verdict}")
    hp = PUB / "wickscale_hl_1h.parquet"
    if hp.exists():
        h = pd.read_parquet(hp).drop_duplicates(["coin", "t"]).sort_values(["coin", "t"])
        h["ts"] = pd.to_datetime(h["t"], unit="ms", utc=True)
        h["usd"] = h["v"] * h["c"]
        h["day"] = h["ts"].dt.normalize()
        dv = h.groupby(["coin", "day"])["usd"].sum().groupby(level=0).shift().rename("pvol")
        h = h.join(dv, on=["coin", "day"])
        h["prev"] = h.groupby("coin")["c"].shift()
        lvl = h["prev"] * 0.92
        hit = (h["l"] <= lvl * (1 - THROUGH)) & h["prev"].notna() & h["pvol"].notna()
        g = h[hit].copy()
        g["ret"] = g["c"] / np.minimum(lvl[hit], g["o"]) - 1 - MAKER - TAKER
        g["size"] = np.minimum(CAP, VSHARE * g["pvol"])
        g["pnl"] = pot_scale(g, "t")
        days = (h["ts"].max() - h["ts"].min()).days
        print(f"  Hyperliquid 1h (second venue, context), {h['ts'].min().date()}..{h['ts'].max().date()}: fills {len(g)}, mean {g['ret'].mean():.2%}, "
              f"t {tstat(g['ret']):.2f}; ${g['pnl'].sum() / max(days, 1) * 365:,.0f}/yr")


# ---------------------------------------------------------------- #403 / #404 other venues
def load_venue(name):
    p = PUB / f"wickscale_{name}_1d.parquet"
    if not p.exists() or not p.stat().st_size:
        return None
    d = pd.read_parquet(p)
    if d.empty:
        return None
    if "start" in d:
        d["day"] = pd.to_datetime(d["start"], utc=True).dt.normalize()
    else:
        t = d["t"].astype("int64")
        d["day"] = pd.to_datetime(np.where(t > 1e12, t // 1000, t), unit="s", utc=True).normalize()
    if "usdvol" not in d:
        d["usdvol"] = d["qvol"] if "qvol" in d else d["vol"] * d["c"]
    d = d[(d["c"] > 0) & (d["l"] > 0)]
    return d.drop_duplicates(["coin", "day"]).sort_values(["coin", "day"])[["coin", "day", "o", "h", "l", "c", "usdvol"]]


def fills_daily(d, x=0.15):
    out = []
    for coin, g in d.groupby("coin"):
        g = g[g["day"] >= g["day"].iloc[0] + pd.Timedelta(days=30)]
        prev, pvol = g["c"].shift(), g["usdvol"].shift()
        lvl = prev * (1 - x)
        hit = (g["l"] <= lvl * (1 - THROUGH)) & prev.notna() & (pvol > 0)
        if not hit.any():
            continue
        ret = g["c"][hit] / np.minimum(lvl[hit], g["o"][hit]) - 1 - MAKER - TAKER
        out.append(pd.DataFrame({"coin": coin, "day": g["day"][hit], "ret": ret, "size": np.minimum(CAP, VSHARE * pvol[hit])}))
    return pd.concat(out) if out else pd.DataFrame(columns=["coin", "day", "ret", "size"])


def cascade_days(d, share=0.25, wick=0.15):
    d = d.copy()
    d["prev"] = d.groupby("coin")["c"].shift()
    d["age"] = (d["day"] - d.groupby("coin")["day"].transform("min")).dt.days
    e = d[(d["age"] >= 30) & d["prev"].notna()]
    g = (e["l"] <= e["prev"] * (1 - wick)).groupby(e["day"]).mean()
    return set(g[g >= share].index)


def part403():
    print("\n#### #403 / #404 the #389 rule on other perp venues")
    terms = json.loads((PUB / "wickscale_terms.json").read_text()) if (PUB / "wickscale_terms.json").exists() else {}
    for k, v in terms.items():
        snip = [s_ for hs in v["hits"].values() for s_ in hs][:2]
        print(f"  terms {k}: HTTP {v['status']}, {v['chars']} chars; 'Malaysia' found: {bool(v['hits'].get('Malaysia'))}")
        for s_ in snip:
            print(f"      ...{s_[:300]}...")
    pooled = {"base": [], "G1": [], "G2": []}
    for name in ("dydx", "aster", "lighter", "paradex"):
        d = load_venue(name)
        if d is None:
            print(f"  {name}: no data")
            continue
        span = (d["day"].max() - d["day"].min()).days / 365
        f = fills_daily(d)
        print(f"  {name}: {d['coin'].nunique()} markets, {d['day'].min().date()}..{d['day'].max().date()} ({span:.2f} yr); fills {len(f)}")
        if span < 1 or len(f) < 2:
            print(f"    {name}: < 1 year of data or no fills -> not judged")
            continue
        casc = cascade_days(d)
        res = {}
        for tag, ff, pot in (("base", f, POT), ("G1", f[~(f["day"] - pd.Timedelta(days=1)).isin(casc)], POT), ("G2", f, 5000.0)):
            ff = ff.copy()
            ff["pnl"] = pot_scale(ff, "day", pot)
            dd, worst = path(ff.groupby("day")["pnl"].sum()) if len(ff) else (0.0, 0.0)
            res[tag] = (ff["pnl"].sum() / span, dd, worst)
            pooled[tag].append(res[tag])
            r = ff["ret"]
            print(f"    {tag}: fills {len(ff)}, mean {r.mean():.2%}, t {tstat(r):.2f}; ${res[tag][0]:,.0f}/yr; worst peak-to-trough ${dd:,.0f}; "
                  f"worst day ${worst:,.0f}")
        r = f["ret"]
        kill = r.mean() < 0.005 or tstat(r) < 3
        print(f"    #403 STAGE 1 ({name}): {'KILL' if kill else 'survives (kill-only)'}")
    if pooled["base"]:
        b = np.array(pooled["base"])
        for tag in ("G1", "G2"):
            g = np.array(pooled[tag])
            dd_imp = 1 - g[:, 1].sum() / b[:, 1].sum() if b[:, 1].sum() < 0 else np.nan
            keep = g[:, 0].sum() / b[:, 0].sum() if b[:, 0].sum() > 0 else np.nan
            adopt = dd_imp >= 0.30 and keep >= 0.70
            print(f"  #404 {tag} pooled over judged venues: drawdown improvement {dd_imp:.0%}, $/yr kept {keep:.0%} -> "
                  f"{'ADOPTED' if adopt else 'not adopted'}")


def main():
    print("===== #402-#404 scaling and hardening #389")
    part402()
    part403()


if __name__ == "__main__":
    main()

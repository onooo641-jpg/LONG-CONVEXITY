"""Batch WK2 #526-#529 (docs/PREREG_BATCH_WK2_20261128.md).

    uv run python -m scripts.batch_wk2_20261128 | tee docs/jx_runs/batch_wk2_20261128.txt
"""
from __future__ import annotations

import warnings
from pathlib import Path

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore", message="Converting to PeriodArray")
PUB = Path(__file__).resolve().parent.parent / "data" / "public"
THROUGH, CAP, VOLS, POT, MK, TK = 0.005, 1500.0, 0.01, 15_000.0, 0.00015, 0.00045
T = lambda s: pd.Timestamp(s, tz="UTC")  # noqa: E731
S1, S2 = (T("2023-06-01"), T("2024-12-31")), (T("2025-01-01"), T("2026-10-31"))
REF522, REF389 = 8269.0, 14372.0


def load():
    cd = pd.read_parquet(PUB / "uncharted_385_candles.parquet")
    cd["day"] = pd.to_datetime(cd["t"], unit="ms", utc=True).dt.normalize()
    return cd.drop_duplicates(["coin", "day"])


def raw_fills(cd, mode, hold=1, cost_mult=1.0, eqrisk=False):
    """mode 'vol' (#520 distance 4*sigma30) or 'fix' (#389 15%). hold = closes after the fill day (0 = same day)."""
    out = []
    for coin, g in cd.groupby("coin"):
        g = g.sort_values("day").reset_index(drop=True)
        if len(g) < 32:
            continue
        prev = g["c"].shift()
        if mode == "vol":
            x = (4 * g["c"].pct_change().rolling(30).std().shift()).clip(0.05, 0.30)
        else:
            x = pd.Series(0.15, index=g.index)
        lvl = prev * (1 - x)
        ok = (g["day"] >= g["day"].iloc[0] + pd.Timedelta(days=30)) & x.notna() & prev.notna()
        for i in np.flatnonzero((ok & (g["l"] <= lvl * (1 - THROUGH))).to_numpy()):
            j = i + hold
            if j >= len(g):
                continue
            px = min(float(lvl.iloc[i]), float(g["o"].iloc[i]))
            if not px > 0:
                continue
            base = min(CAP, VOLS * float(g["v"].iloc[i]) * float(g["c"].iloc[i]))
            size = min(CAP * float(np.clip(0.10 / x.iloc[i], 0.5, 2.0)), VOLS * float(g["v"].iloc[i]) * float(g["c"].iloc[i])) if eqrisk else base
            out.append({"coin": coin, "day": g["day"].iloc[i], "ret": float(g["c"].iloc[j]) / px - 1 - cost_mult * (MK + TK), "size": size})
    return pd.DataFrame(out)


def pnl(f):
    f = f.copy()
    f["pnl"] = f["size"] * np.minimum(1.0, POT / f.groupby("day")["size"].transform("sum")) * f["ret"]
    return f


def summ(f, w):
    g = f[(f["day"] >= w[0]) & (f["day"] <= w[1])]
    yrs = ((w[1] - w[0]).days + 1) / 365
    if g.empty:
        return dict(n=0, m=np.nan, t=np.nan, usd=0.0, worst=np.nan)
    r = g["ret"]
    mon = g.groupby(g["day"].dt.to_period("M"))["pnl"].sum()
    return dict(n=len(g), m=r.mean(), t=r.mean() / (r.std(ddof=1) / np.sqrt(len(r))), usd=g["pnl"].sum() / yrs, worst=mon.min(),
                win=(r > 0).mean())


def fmt(label, s):
    return (f"   {label}: fills {s['n']} | mean net {s['m']:+.2%} (t {s['t']:.2f}, win {s.get('win', np.nan):.0%}) | ${s['usd']:,.0f}/yr "
            f"| worst month ${s['worst']:,.0f}") if s["n"] else f"   {label}: no fills"


def killed(s):
    return s["n"] >= 30 and not (s["m"] > 0.003)


def main():
    cd = load()
    base = pnl(raw_fills(cd, "vol", hold=1))
    r1, r2 = summ(base, S1), summ(base, S2)
    print("#522 reference (vol-scaled bids, exit next day's close)")
    print(fmt("Stage 1", r1))
    print(fmt("Stage 2", r2))

    print("\n#526 Hold length (pick h on Stage 1 from 2, 3, 5; Stage 2 once with costs x 1.5)")
    st1 = {}
    for h in (2, 3, 5):
        st1[h] = summ(pnl(raw_fills(cd, "vol", hold=h)), S1)
        print(fmt(f"h {h} Stage 1", st1[h]))
    h = max(st1, key=lambda k: st1[k]["usd"])
    s2 = summ(pnl(raw_fills(cd, "vol", hold=h, cost_mult=1.5)), S2)
    print(f"   chosen h {h}")
    print(fmt(f"h {h} Stage 2 (costs x 1.5)", s2))
    ok = not killed(st1[h]) and s2["n"] >= 30 and s2["m"] >= 0.003 and s2["t"] >= 2 and s2["usd"] > REF522
    print(f"   VERDICT {'KILL (Stage 1)' if killed(st1[h]) else ('PASS' if ok else 'FAIL')} (must beat #522's ${REF522:,.0f}/yr)\n")

    print("#527 Equal-risk sizing (size x clip(0.10 / X, 0.5, 2))")
    f = pnl(raw_fills(cd, "vol", hold=1, eqrisk=True))
    a, b = summ(f, S1), summ(f, S2)
    print(fmt("Stage 1", a))
    print(fmt("Stage 2", b))
    ok = not killed(a) and b["n"] >= 30 and b["m"] >= 0.003 and b["t"] >= 2 and b["usd"] > REF522
    print(f"   VERDICT {'KILL (Stage 1)' if killed(a) else ('PASS' if ok else 'FAIL')}\n")

    print("#528 Skip systemic crash days (BTC low >= 5% below its previous close)")
    btc = cd[cd["coin"] == "BTC"].sort_values("day").set_index("day")
    crash = set(btc.index[(btc["l"] <= btc["c"].shift() * 0.95)])
    raw = raw_fills(cd, "vol", hold=1)
    f = pnl(raw[~raw["day"].isin(crash)])
    a, b = summ(f, S1), summ(f, S2)
    print(f"   BTC crash days in the data: {len(crash)}")
    print(fmt("Stage 1", a))
    print(fmt("Stage 2", b))
    ok = not killed(a) and b["usd"] >= REF522 and b["worst"] >= r2["worst"]
    print(f"   VERDICT {'KILL (Stage 1)' if killed(a) else ('PASS' if ok else 'FAIL')} (needs $/yr >= ${REF522:,.0f} and worst month >= ${r2['worst']:,.0f})\n")

    print("#529 #389 + #522 on one pot (a coin-day filled by both counts once, as #522)")
    v = raw_fills(cd, "vol", hold=1)
    x = raw_fills(cd, "fix", hold=0)
    x = x[~(x["coin"] + x["day"].astype(str)).isin(set(v["coin"] + v["day"].astype(str)))]
    f = pnl(pd.concat([v, x], ignore_index=True))
    a, b = summ(f, S1), summ(f, S2)
    print(fmt("Stage 1", a))
    print(fmt("Stage 2", b))
    ok = not killed(a) and b["m"] >= 0.003 and b["t"] >= 2 and b["usd"] > max(REF389, REF522)
    print(f"   VERDICT {'KILL (Stage 1)' if killed(a) else ('PASS' if ok else 'FAIL')} (must beat ${max(REF389, REF522):,.0f}/yr)")


if __name__ == "__main__":
    main()

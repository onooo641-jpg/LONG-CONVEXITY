"""#291 option wrap of the friend's NQ trades (docs/PREREG_OPTIONWRAP_20261122.md).

    uv run python -m scripts.optionwrap_20261122 | tee docs/jx_runs/optionwrap_20261122.txt
"""
from __future__ import annotations

import math
import sys

import numpy as np
import pandas as pd

from ict import data as D
from scripts.radar_price import trades

PREM, MULT, HALF_SPREAD, COMM = 900.0, 2.0, 0.02, 0.50
N = lambda x: 0.5 * (1 + math.erf(x / math.sqrt(2)))  # noqa: E731


def bs(S, K, s, T, call):
    if T <= 0:
        return max(S - K, 0.0) if call else max(K - S, 0.0)
    d1 = (math.log(S / K) + 0.5 * s * s * T) / (s * math.sqrt(T))
    c = S * N(d1) - K * N(d1 - s * math.sqrt(T))
    return c if call else c - S + K


def dip(pnl):
    net = np.cumsum(pnl)
    return float((net - np.maximum.accumulate(np.maximum(net, 0))).min()) if len(net) else 0.0


def legs(t, bars, vxn, mult_sigma):
    close = bars.set_index("ts")["close"]
    if close.index.tz is None:
        close.index = close.index.tz_localize("UTC")
    out = []
    for r in t.itertuples():
        et = r.entry_ts.tz_convert("America/New_York")
        exp = et.normalize() + pd.Timedelta(hours=16)
        if exp <= et:
            exp += pd.Timedelta(days=1)
        v = vxn[vxn.index < et.normalize().tz_localize(None)]
        if not len(v):
            out.append((np.nan, np.nan))
            continue
        s = v.iloc[-1] / 100 * mult_sigma
        T0 = max((exp - et).total_seconds(), 1800) / (365 * 86400)
        S0 = float(r.entry_fill)
        xt = r.exit_ts.tz_convert("America/New_York")
        if xt >= exp:
            px = close[close.index <= exp.tz_convert("UTC")]
            S1, T1 = float(px.iloc[-1]), 0.0
        else:
            S1, T1 = float(r.exit_price), max((exp - xt).total_seconds(), 0) / (365 * 86400)
        res = []
        for call in (True, False):
            p0, p1 = bs(S0, S0, s, T0, call), bs(S1, S0, s, T1, call)
            q = PREM / (p0 * MULT)
            res.append(q * MULT * (p1 - p0) - HALF_SPREAD * q * MULT * (p0 + p1) - 2 * COMM * q)
        out.append(tuple(res))
    return np.array(out)


def main() -> int:
    vx = pd.read_csv("data/public/vxn_vxncls.csv")
    vx.columns = ["d", "v"]
    vxn = pd.to_numeric(vx.set_index(pd.to_datetime(vx["d"]))["v"], errors="coerce").dropna()
    bars = D.load("1m")
    orders = pd.read_parquet(D.PROCESSED_DIR / "ideas_orders_NQ.parquet")
    t = trades(orders, bars, 0)
    long_ = (t["direction"] == 1).to_numpy()
    print(f"trades {len(t)} ({long_.sum()} long); VXN {vxn.index.min():%Y-%m-%d}..{vxn.index.max():%Y-%m-%d}")
    print(f"benchmark Topstep 50K: real $44,359, coin flip $18,046, worst dip -$3,520; flag: real >= $22,180, flip >= $5,000, dip >= -$5,280\n")
    for m in (1.0, 0.8, 1.2):
        L = legs(t, bars, vxn, m)
        ok = ~np.isnan(L).any(axis=1)
        real = np.where(long_, L[:, 0], L[:, 1])[ok]
        wrong = np.where(long_, L[:, 1], L[:, 0])[ok]
        rng = np.random.default_rng(1)
        flips = np.array([np.where(rng.choice([True, False], ok.sum()), real, wrong).sum() for _ in range(200)])
        yrs = t.loc[ok, "exit_ts"].dt.year.to_numpy()
        h1, h2 = real[yrs <= 2020].sum(), real[yrs >= 2021].sum()
        tag = "REGISTERED" if m == 1.0 else "context"
        print(f"[{tag}] sigma x{m}: real net ${real.sum():,.0f} (2016-20 ${h1:,.0f}, 2021-26 ${h2:,.0f}); coin flip median ${np.median(flips):,.0f} "
              f"({(flips > 0).mean():.0%} profitable); worst dip ${dip(real):,.0f}; win rate {(real > 0).mean():.0%}; trades priced {ok.sum()}")
        if m == 1.0:
            p = real.sum() >= 22_180 and np.median(flips) >= 5_000 and dip(real) >= -5_280
            print(f"  VERDICT: {'PASS (would flag)' if p else 'FAIL'}\n")
    fut = t["net_pnl"].sum()
    print(f"(reference) same trades as futures on own money: net ${fut:,.0f}, worst dip ${dip(t['net_pnl'].to_numpy()):,.0f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

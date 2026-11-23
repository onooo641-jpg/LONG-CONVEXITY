"""#351b: can a small account trade #351 (cross-sectional futures momentum) with whole micro contracts?
(docs/PREREG_FUTURES_TREND_CARRY_20261123.md addendum 3)

    uv run python -m scripts.futures_xsmom_small_20261123 | tee docs/jx_runs/futures_xsmom_small_20261123.txt
"""
from __future__ import annotations

import sys

import numpy as np
import pandas as pd

from scripts.batch9_20261122 import F, spy_m, stats

# root: (multiplier in $ per 1.0 price unit, tick size, cost per contract per side) — micro / small contracts (assumed; verify on CME)
SPEC = {"ES": (5, 0.25, 1.5), "NQ": (2, 0.25, 1.5), "YM": (0.5, 1.0, 1.5), "RTY": (5, 0.1, 1.5), "6E": (12500, 0.0001, 1.5),
        "6A": (10000, 0.0001, 1.5), "6B": (6250, 0.0001, 1.5), "GC": (10, 0.1, 1.5), "SI": (1000, 0.005, 1.5), "HG": (2500, 0.0005, 1.5),
        "CL": (100, 0.01, 1.5), "ZN": (1000, 1 / 64, 2.5), "ZT": (2000, 1 / 128, 2.5)}
L, VT = 12, 0.15
S0, SPLIT, END = pd.Timestamp("2016-01-01"), pd.Timestamp("2021-05-01"), pd.Timestamp("2026-11-01")


def load():
    d = pd.read_parquet("data/public/databento_daily.parquet")
    d["day"] = pd.to_datetime(d["ts_event"], utc=True).dt.tz_localize(None).dt.normalize()
    px = d.pivot_table(index="day", columns="symbol", values="close", aggfunc="last").sort_index()
    return pd.DataFrame({r: px[f"{r}.v.0"] for r in SPEC if f"{r}.v.0" in px}).ffill()


def run(px, capital, fractional=False):
    ret = px.pct_change()
    sd = ret.rolling(250, min_periods=60).std()
    ret = ret.where(~(ret.abs() > 8 * sd), 0.0).fillna(0.0)  # continuous-contract roll jumps (as in #350)
    vol = ret.rolling(60, min_periods=40).std() * np.sqrt(252)
    tb = (F["DTB3"] / 100 / 252).reindex(px.index).ffill().fillna(0)
    days = px.index[(px.index >= S0 - pd.Timedelta(days=5)) & (px.index < END)]
    month_ends = set(pd.Series(days, index=days).groupby(days.to_period("M")).max())
    eq, n, out, prev_day = capital, pd.Series(0.0, index=px.columns), [], None
    for d in days:
        if prev_day is not None:
            pnl = float((n * pd.Series({r: SPEC[r][0] for r in px.columns}) * px.loc[prev_day] * ret.loc[d]).sum())
            eq_new = eq + pnl + eq * tb.loc[d]
            out.append((d, eq_new / eq - 1))
            eq = eq_new
        if d in month_ends:
            hist = ret.loc[:d]
            if len(hist) > 21 * L + 10:
                look = hist.iloc[-(21 * L + 5):-5]
                sc = (1 + look).prod() - 1
                rk = sc.rank(pct=True)
                s_ = (rk > 2 / 3).astype(float) - (rk < 1 / 3).astype(float)
                v = vol.loc[d].replace(0, np.nan)
                w = (s_ / v).fillna(0.0) * (VT / np.sqrt(len(px.columns)))
                cval = pd.Series({r: SPEC[r][0] * px.at[d, r] for r in px.columns})
                tgt = w * eq / cval
                new = tgt if fractional else tgt.round()
                dn = (new - n).abs()
                cost = float((dn * pd.Series({r: SPEC[r][2] * 2 / 2 + SPEC[r][0] * SPEC[r][1] for r in px.columns})).sum())
                eq -= cost
                n = new
        prev_day = d
    s = pd.Series(dict(out))
    s.index = pd.DatetimeIndex(s.index)
    return s


def main() -> int:
    px = load()
    spy, _ = spy_m()
    print(f"#351b universe {list(px.columns)}; config xsmom / L{L} / vt{int(VT * 100)}; 2016-01..2026-10; whole contracts; costs per contract side + 1 tick\n")
    spy_dd = stats(spy[(spy.index >= pd.Period("2016-01", "M")) & (spy.index <= pd.Period("2026-10", "M"))])[1]
    for cap, frac in ((None, True), (15_000, False), (50_000, False), (100_000, False), (250_000, False)):
        c = cap or 1_000_000
        s = run(px, c, fractional=frac)
        m = (1 + s).groupby(s.index.to_period("M")).prod() - 1
        h1 = stats(m[m.index < pd.Period("2021-05", "M")])[0]
        h2 = stats(m[m.index >= pd.Period("2021-05", "M")])[0]
        cagr, dd = stats(m)
        eq_end = c * float((1 + s).prod())
        ok = h1 >= 10 and h2 >= 10 and dd >= spy_dd
        label = "fractional (reference, this 13-market universe)" if frac else f"${cap:,} account, whole contracts"
        dollars = f"; avg ${(eq_end - c) / 10.83:,.0f}/yr on ${c:,}" if cap else ""
        print(f"{label:<48} CAGR {cagr:6.2f}% | halves {h1:6.2f}% / {h2:6.2f}% | worst DD {dd:6.1f}% (SPY {spy_dd:.1f}%) | "
              f"{'PASS' if ok else 'FAIL'}{dollars}", flush=True)
    print("\nMargin requirements not modelled (gross notional can exceed equity); multipliers and costs assumed; verify on CME before any use.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""#350 cross-asset futures trend and carry (docs/PREREG_FUTURES_TREND_CARRY_20261123.md).

    uv run python -m scripts.futures_trend_20261123 | tee docs/jx_runs/futures_trend_20261123.txt
"""
from __future__ import annotations

import io
import itertools
import json
import sys

import numpy as np
import pandas as pd

from scripts.batch9_20261122 import F, spy_m, stats, walk

ROOTS = "ES NQ YM RTY ZT ZF ZN ZB 6E 6J 6B 6A 6C 6S GC SI HG CL NG RB HO ZC ZS ZW LE HE".split()
AGS = {"ZC", "ZS", "ZW", "LE", "HE"}
SPACING = {**{r: 3 for r in "ES NQ YM RTY ZT ZF ZN ZB 6E 6J 6B 6A 6C 6S".split()}, **{r: 1 for r in "CL NG RB HO".split()},
           **{r: 2 for r in "GC SI HG LE HE ZC ZS ZW".split()}}


def load():
    d = pd.read_parquet("data/public/databento_daily.parquet")
    tcol = "ts_event" if "ts_event" in d else d.columns[0]
    d["day"] = pd.to_datetime(d[tcol], utc=True).dt.tz_localize(None).dt.normalize()
    px = d.pivot_table(index="day", columns="symbol", values="close", aggfunc="last").sort_index()
    return px


def build(px, cmult):
    tb = (F["DTB3"] / 100 / 252).reindex(px.index).ffill().fillna(0)
    front = {r: px.get(f"{r}.v.0") for r in ROOTS if f"{r}.v.0" in px}
    second = {r: px.get(f"{r}.v.1") for r in ROOTS if f"{r}.v.1" in px}
    ret = pd.DataFrame({r: s.pct_change() for r, s in front.items()})
    # continuous .v.0 jumps at rolls: drop daily moves beyond 8 sigma as roll artefacts (mechanical)
    sd = ret.rolling(250, min_periods=60).std()
    ret = ret.where(~(ret.abs() > 8 * sd), 0.0).fillna(0.0)
    vol = ret.rolling(60, min_periods=40).std() * np.sqrt(252)
    month_ends = ret.resample("ME").last().index
    cols = {}
    for L, vt, uni, sig in itertools.product((3, 6, 12), (0.10, 0.15), ("all", "exags"), ("tsmom", "carry", "combo")):
        names = [r for r in front if uni == "all" or r not in AGS]
        pos = pd.DataFrame(0.0, index=ret.index, columns=names)
        for me in month_ends:
            hist = ret.loc[:me, names]
            if len(hist) < 260:
                continue
            look = hist.iloc[-(21 * L + 5):-5]
            mom = np.sign((1 + look).prod() - 1)
            car = pd.Series({r: np.sign(np.log(front[r].asof(me) / second[r].asof(me)) * 12 / SPACING[r])
                             if r in second and second[r].asof(me) and front[r].asof(me) else 0.0 for r in names})
            s = mom if sig == "tsmom" else (car if sig == "carry" else np.sign(mom + car))
            v = vol.loc[:me, names].iloc[-1].replace(0, np.nan)
            w = (s / v).fillna(0.0) * (vt / np.sqrt(max(len(names), 1)))  # equal risk per market, book scaled ~ to vt
            nxt = pos.index[pos.index > me]
            if len(nxt):
                pos.loc[nxt[0]:, names] = w.values
        pr = (pos.shift(1) * ret[names]).sum(axis=1)
        turn = pos.diff().abs().sum(axis=1)
        daily = pr - turn * 0.0002 * cmult + tb
        cols[f"L{L}/vt{int(vt * 100)}/{uni}/{sig}"] = (1 + daily).groupby(daily.index.to_period("M")).prod() - 1
    return pd.DataFrame(cols)


def build_xs(px, cmult, factor):
    """#351-#354: cross-sectional factors, dollar-neutral (top third long, bottom third short, equal risk per market)."""
    tb = (F["DTB3"] / 100 / 252).reindex(px.index).ffill().fillna(0)
    front = {r: px.get(f"{r}.v.0") for r in ROOTS if f"{r}.v.0" in px}
    second = {r: px.get(f"{r}.v.1") for r in ROOTS if f"{r}.v.1" in px}
    ret = pd.DataFrame({r: s.pct_change() for r, s in front.items()})
    sd = ret.rolling(250, min_periods=60).std()
    ret = ret.where(~(ret.abs() > 8 * sd), 0.0).fillna(0.0)
    vol = ret.rolling(60, min_periods=40).std() * np.sqrt(252)
    month_ends = ret.resample("ME").last().index
    grid = {"xsmom": (3, 6, 12), "value": (36, 48, 60), "skew": (6, 12, 24), "multi": (3, 6, 12)}[factor]
    cols = {}
    for L, vt, uni in itertools.product(grid, (0.10, 0.15), ("all", "exags")):
        names = [r for r in front if uni == "all" or r not in AGS]
        pos = pd.DataFrame(0.0, index=ret.index, columns=names)
        for me in month_ends:
            hist = ret.loc[:me, names]
            need = 21 * max(L, 12) + 10 if factor in ("value", "skew") else 260
            if len(hist) < need:
                continue

            def cum(months, skip=5):
                return (1 + hist.iloc[-(21 * months + skip):-skip]).prod() - 1
            if factor == "xsmom":
                sc = cum(L)
            elif factor == "value":
                sc = -cum(L, 0)
            elif factor == "skew":
                sc = -hist.iloc[-21 * L:].skew()
            else:
                car = pd.Series({r: np.log(front[r].asof(me) / second[r].asof(me)) * 12 / SPACING[r]
                                 if r in second and second[r].asof(me) and front[r].asof(me) else 0.0 for r in names})
                parts = [np.sign(cum(L)), np.sign(car)]
                for x in (cum(L), -cum(60, 0) if len(hist) > 21 * 60 + 10 else None):
                    if x is not None:
                        rk = x.rank(pct=True)
                        parts.append(((rk > 2 / 3).astype(float) - (rk < 1 / 3).astype(float)))
                sc = sum(p_.reindex(names).fillna(0) for p_ in parts) / len(parts)
            if factor != "multi":
                rk = sc.rank(pct=True)
                s_ = (rk > 2 / 3).astype(float) - (rk < 1 / 3).astype(float)
            else:
                s_ = sc
            v = vol.loc[:me, names].iloc[-1].replace(0, np.nan)
            w = (s_ / v).fillna(0.0) * (vt / np.sqrt(max(len(names), 1)))
            nxt = pos.index[pos.index > me]
            if len(nxt):
                pos.loc[nxt[0]:, names] = w.reindex(names).fillna(0).values
        pr = (pos.shift(1) * ret[names]).sum(axis=1)
        turn = pos.diff().abs().sum(axis=1)
        daily = pr - turn * 0.0002 * cmult + tb
        cols[f"{factor}/L{L}/vt{int(vt * 100)}/{uni}"] = (1 + daily).groupby(daily.index.to_period("M")).prod() - 1
    return pd.DataFrame(cols)


def main() -> int:
    px = load()
    print(f"#350 data: {px.shape[1]} continuous series, {px.index.min():%Y-%m-%d}..{px.index.max():%Y-%m-%d}")
    spy, _ = spy_m()
    M1, M15 = build(px, 1.0), build(px, 1.5)
    s = M1.loc[(M1.index >= pd.Period("2025-11", "M")) & (M1.index <= pd.Period("2026-10", "M"))]
    print(f"(context) best Stage-1 config 2025-11..2026-10: {s.apply(lambda c: stats(c)[0]).max():.2f}%/yr")
    walk("#350 cross-asset futures trend / carry", (M1, M15), 0.0005, spy)
    for num, fac, label in (("351", "xsmom", "cross-sectional momentum"), ("352", "value", "value (5-year reversal)"),
                            ("353", "skew", "skewness"), ("354", "multi", "multi-factor")):
        walk(f"#{num} futures {label}", (build_xs(px, 1.0, fac), build_xs(px, 1.5, fac)), 0.0005, spy)
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""The 2010-2015 holdout test, exactly as docs/HOLDOUT_PREREG.md defines it.

    uv run python scripts/holdout_test.py

Run once. Definitions, account model and the win rule live in the
pre-registration file (committed first, 633a258), not here; this only
implements them. V1 uses docs/tier1_calendar_2010_2015.csv, which only
covers 2010-06..2015-12, so V1's SEEN-window row is not meaningful.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from backtest.engine import BacktestConfig, simulate
from backtest.recycle import Policy, XFARules, recycle
from ict import data as D
from strategies.ltf_sweep import generate_orders

HOLDOUT = ("2010-07-01", "2016-01-01")
SEEN = ("2016-01-01", "2027-01-01")
RISK = 900.0
RULES, POLICY = XFARules(), Policy.LOCK_FIRST


def daily(bars: pd.DataFrame) -> pd.DataFrame:
    """RTH open / close / range per New York date."""
    m = bars["minutes_from_midnight"]
    rth = bars[(m >= 9 * 60 + 30) & (m < 16 * 60)]
    g = rth.groupby("ny_date")
    return pd.DataFrame({"open": g["open"].first(), "close": g["close"].last(),
                         "range": g["high"].max() - g["low"].min()}).sort_index()


def v1_news(orders):
    """Pre-registered V1: skip release days for the six tier-1 series.
    Dates: docs/tier1_calendar_2010_2015.csv (BLS, federalreserve.gov, ALFRED)."""
    cal = pd.read_csv(D.REPO_ROOT / "docs" / "tier1_calendar_2010_2015.csv")
    days = set(pd.to_datetime(cal["date"]).dt.date)
    return ~orders["trading_date"].isin(days).to_numpy()


def v2_trend(orders, day):
    keep = []
    dates = np.array(day.index)
    closes = day["close"].to_numpy()
    for d, direction in zip(orders["trading_date"], orders["direction"]):
        k = np.searchsorted(dates, d)          # dates strictly before d
        if k < 20:
            keep.append(False)
            continue
        c1, sma = closes[k - 1], closes[k - 20:k].mean()
        keep.append(c1 >= sma if direction > 0 else c1 < sma)
    return np.array(keep)


def v3_wide(orders):
    o = orders.sort_values("valid_from")
    risk = o["risk_points"].to_numpy()
    keep = np.ones(len(o), dtype=bool)
    for i in range(len(o)):
        prev = risk[max(0, i - 60):i]
        if len(prev) >= 20 and risk[i] > 2.0 * np.median(prev):
            keep[i] = False
    return pd.Series(keep, index=o.index).reindex(orders.index).to_numpy()


def v4_gap(orders, day):
    dates = np.array(day.index)
    opens, closes, ranges = (day[c].to_numpy() for c in ("open", "close", "range"))
    keep = []
    for d in orders["trading_date"]:
        k = np.searchsorted(dates, d)
        if k < 20 or k >= len(dates) or dates[k] != d:
            keep.append(False)
            continue
        gap = abs(opens[k] - closes[k - 1])
        keep.append(gap <= 0.5 * ranges[k - 20:k].mean())
    return np.array(keep)


def window(trades, lo, hi):
    t = trades[(trades["entry_ts"] >= pd.Timestamp(lo, tz="UTC"))
               & (trades["entry_ts"] < pd.Timestamp(hi, tz="UTC"))]
    return t.sort_values("exit_ts").reset_index(drop=True)


def score(trades):
    p = trades["net_pnl"]
    pf = p[p > 0].sum() / -p[p < 0].sum()
    out = recycle(trades, RULES, policy=POLICY)
    tl = pd.DataFrame(out["timeline"])
    passed, bust = (tl.event == "passed").sum(), (tl.event == "combine_bust").sum()
    years = trades.assign(y=pd.DatetimeIndex(trades["exit_ts"]).tz_convert(
        "America/New_York").year).groupby("y")["net_pnl"].sum()
    return {"trades": len(trades), "win": float((p > 0).mean()), "pf": float(pf),
            "raw": float(p.sum()), "rec_net": out["net"], "cash": out["cash"],
            "cost": out["cost"], "pass": passed / max(1, passed + bust),
            "payouts": out["payouts"], "dry": out["longest_dry_days"], "years": years}


def main() -> int:
    bars = D.load("1m")
    print(f"bars {bars.ts.min()} -> {bars.ts.max()}")
    orders = generate_orders(bars)
    day = daily(bars)
    sim = lambda o: (lambda t: t[t["filled"]])(  # noqa: E731
        simulate(o, bars, BacktestConfig(risk_per_trade_usd=RISK)))

    variants = {
        "baseline": np.ones(len(orders), dtype=bool),
        "V1 news": v1_news(orders),
        "V2 trend": v2_trend(orders, day),
        "V3 wide stop": v3_wide(orders),
        "V4 gap": v4_gap(orders, day),
    }
    res = {}
    for name, keep in variants.items():
        t = sim(orders[keep].reset_index(drop=True))
        res[name] = {"holdout": score(window(t, *HOLDOUT)),
                     "seen": score(window(t, *SEEN)),
                     "kept": float(keep.mean())}

    for label, key in (("HOLDOUT 2010-07-01 .. 2015-12-31  (decides)", "holdout"),
                       ("SEEN 2016-01-01 .. 2026-10-28  (context only)", "seen")):
        print(f"\n=== {label}")
        print(f"  {'':<14}{'kept':>6}{'trades':>7}{'win':>7}{'PF':>7}{'raw net':>11}"
              f"{'recycle net':>13}{'cash':>9}{'cost':>9}{'pass':>7}{'pays':>6}{'dry d':>7}")
        for name, r in res.items():
            s = r[key]
            print(f"  {name:<14}{r['kept']:>6.0%}{s['trades']:>7}{s['win']:>7.1%}"
                  f"{s['pf']:>7.3f}{s['raw']:>11,.0f}{s['rec_net']:>13,.0f}"
                  f"{s['cash']:>9,.0f}{s['cost']:>9,.0f}{s['pass']:>7.1%}"
                  f"{s['payouts']:>6}{s['dry']:>7,.0f}")
        print("  raw net by year:")
        yrs = sorted(res["baseline"][key]["years"].index)
        print("  " + f"{'':<14}" + "".join(f"{y:>9}" for y in yrs))
        for name, r in res.items():
            ys = r[key]["years"]
            print(f"  {name:<14}" + "".join(f"{ys.get(y, 0):>9,.0f}" for y in yrs))

    print("\n=== VERDICT (pre-registered rule, holdout only)")
    b = res["baseline"]["holdout"]
    for name, r in res.items():
        if name == "baseline":
            continue
        s = r["holdout"]
        c1 = s["rec_net"] > b["rec_net"]
        c2 = s["pf"] > b["pf"]
        yrs = [y for y in b["years"].index if 2010 <= y <= 2015]
        better = sum(s["years"].get(y, 0) > b["years"].get(y, 0) for y in yrs)
        c3 = better >= 4
        print(f"  {name:<14} recycle net {'higher' if c1 else 'not higher'}, "
              f"PF {'higher' if c2 else 'not higher'}, better in {better}/{len(yrs)} years "
              f"-> {'WIN' if c1 and c2 and c3 else 'no'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

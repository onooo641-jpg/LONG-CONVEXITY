"""#405-#409: five high-ceiling liquidity ideas (docs/PREREG_FIVE_HIGH_20261125.md).

    uv run python -m scripts.five_high_20261125 | tee docs/jx_runs/five_high_20261125.txt
Data: uncharted_385_candles.parquet (Hyperliquid daily), hl_funding.parquet, uncharted_389_binance_ohlc.parquet, cryptotrend370_funding.parquet,
and fivehigh_* files from Actions job ufive.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

PUB = Path(__file__).resolve().parent.parent / "data" / "public"
MAKER, TAKER, THROUGH, CAP, VSHARE, POT = 0.00015, 0.00045, 0.005, 1500.0, 0.01, 15_000.0


def tstat(r):
    r = pd.Series(r).dropna()
    return r.mean() / (r.std(ddof=1) / np.sqrt(len(r))) if len(r) > 1 else np.nan


def hl_daily():
    d = pd.read_parquet(PUB / "uncharted_385_candles.parquet")
    d["day"] = pd.to_datetime(d["t"], unit="ms", utc=True).dt.normalize()
    d["usdvol"] = d["v"] * d["c"]
    return d.drop_duplicates(["coin", "day"]).sort_values(["coin", "day"])[["coin", "day", "o", "h", "l", "c", "usdvol"]]


def bn_daily():
    b = pd.read_parquet(PUB / "uncharted_389_binance_ohlc.parquet").rename(columns={"sym": "coin", "qvol": "usdvol"})
    b["day"] = pd.to_datetime(b["t"], unit="s", utc=True).dt.normalize()
    return b.drop_duplicates(["coin", "day"]).sort_values(["coin", "day"])[["coin", "day", "o", "h", "l", "c", "usdvol"]]


def wick_fills(d, x, age_lo, age_hi, maker=MAKER, taker=TAKER, exclude_first_day=None):
    out = []
    for coin, g in d.groupby("coin"):
        first = g["day"].iloc[0]
        if exclude_first_day is not None and first <= exclude_first_day:
            continue  # listed before the data start: not a new listing
        age = (g["day"] - first).dt.days
        prev, pvol = g["c"].shift(), g["usdvol"].shift()
        lvl = prev * (1 - x)
        hit = (g["l"] <= lvl * (1 - THROUGH)) & prev.notna() & (pvol > 0) & (age >= age_lo) & (age <= age_hi)
        if hit.any():
            ret = g["c"][hit] / np.minimum(lvl[hit], g["o"][hit]) - 1 - maker - taker
            out.append(pd.DataFrame({"coin": coin, "day": g["day"][hit], "ret": ret, "size": np.minimum(CAP, VSHARE * pvol[hit])}))
    f = pd.concat(out) if out else pd.DataFrame(columns=["coin", "day", "ret", "size"])
    if len(f):
        f["pnl"] = f["size"] * np.minimum(1.0, POT / f.groupby("day")["size"].transform("sum")) * f["ret"]
    return f


def report_fills(f, label, start, end):
    f = f[(f["day"] >= start) & (f["day"] <= end)]
    yrs = ((end - start).days + 1) / 365
    if f.empty:
        print(f"  {label}: no fills")
        return f, np.nan, np.nan, 0.0, 0
    r = f["ret"]
    by = f.groupby(f["day"].dt.year)["pnl"].sum()
    full = by[(by.index >= start.year) & (by.index <= 2025)]
    d = f.groupby("day")["pnl"].sum()
    d = d.reindex(pd.date_range(d.index.min(), d.index.max(), freq="D", tz="UTC"), fill_value=0.0)
    dd = float((d.cumsum() - d.cumsum().cummax()).min())
    print(f"  {label}: fills {len(f)} ({f['coin'].nunique()} coins); mean {r.mean():.2%} (median {r.median():.2%}, t {tstat(r):.2f}, "
          f"win {(r > 0).mean():.0%}); ${f['pnl'].sum() / yrs:,.0f}/yr; worst peak-to-trough ${dd:,.0f}")
    print("     by year: " + "; ".join(f"{y} ${v:,.0f}" for y, v in by.items()))
    return f, r.mean(), tstat(r), f["pnl"].sum() / yrs, int((full > 0).sum())


# ---------------------------------------------------------------- #407
def part407():
    print("#### #407 new-listing wick bids (days 2-30 after a perp's first candle)")
    hl = hl_daily()
    s1 = None
    for x in (0.15, 0.25):
        f = wick_fills(hl, x, 1, 29, exclude_first_day=pd.Timestamp("2023-04-02", tz="UTC"))
        _, m, t, py, _ = report_fills(f, f"Hyperliquid X {x:.0%}{' (primary)' if x == 0.15 else ''}", pd.Timestamp("2023-06-01", tz="UTC"),
                                      pd.Timestamp("2026-10-31", tz="UTC"))
        if x == 0.15:
            s1 = not (pd.isna(m) or m < 0.005 or t < 3)
    print(f"  STAGE 1 VERDICT (Hyperliquid): {'survives (kill-only)' if s1 else 'KILL'}")
    bn = bn_daily()
    for x in (0.15, 0.25):
        f = wick_fills(bn, x, 1, 29, exclude_first_day=pd.Timestamp("2020-01-02", tz="UTC"))
        _, m, t, py, pos = report_fills(f, f"Binance X {x:.0%}{' (Stage 2)' if x == 0.15 else ''}", pd.Timestamp("2020-01-01", tz="UTC"),
                                        pd.Timestamp("2026-10-31", tz="UTC"))
        if x == 0.15:
            ok = s1 and not pd.isna(m) and m >= 0.005 and t >= 3 and py >= 3000 and pos >= 4
            print(f"  STAGE 2 VERDICT (Binance): {'PASS' if ok else ('FAIL' if s1 else 'not run (Stage 1 killed) — shown as context')}")


# ---------------------------------------------------------------- #408
def reversal(d, F, label, start):
    d = d[d["day"] >= start - pd.Timedelta(days=60)].copy()
    C = d.pivot(index="day", columns="coin", values="c").sort_index()
    V = d.pivot(index="day", columns="coin", values="usdvol").reindex(C.index)
    first = d.groupby("coin")["day"].min()
    R = C.pct_change(fill_method=None)
    vol30 = V.rolling(30, min_periods=20).sum().shift(1)
    age_ok = pd.DataFrame({c: (C.index - first[c]).days >= 30 for c in C.columns}, index=C.index)
    rows, wl_prev, ws_prev = [], pd.Series(dtype=float), pd.Series(dtype=float)
    days = [x for x in C.index if x >= start]
    for i, day in enumerate(days[:-1]):
        nxt = days[i + 1]
        if (nxt - day).days != 1:
            continue
        ok = age_ok.loc[day] & R.loc[day].notna() & vol30.loc[day].notna() & R.loc[nxt].notna()
        cand = vol30.loc[day][ok].sort_values(ascending=False).head(100).index
        if len(cand) < 20:
            continue
        r = R.loc[day, cand].sort_values()
        k = max(1, int(len(cand) * 0.10))
        L, S = r.index[:k], r.index[-k:]
        wl, ws = pd.Series(1 / k, index=L), pd.Series(1 / k, index=S)
        turn = (wl.sub(wl_prev, fill_value=0).abs().sum() + ws.sub(ws_prev, fill_value=0).abs().sum())
        frow = F.loc[nxt] if F is not None and nxt in F.index else None
        fl = float(frow.reindex(L).fillna(0).mean()) if frow is not None else 0.0
        fs = float(frow.reindex(S).fillna(0).mean()) if frow is not None else 0.0
        net = R.loc[nxt, L].mean() - R.loc[nxt, S].mean() - fl + fs - TAKER * turn
        rows.append({"day": nxt, "net": net, "gross": R.loc[nxt, L].mean() - R.loc[nxt, S].mean(), "turn": turn})
        wl_prev, ws_prev = wl, ws
    t = pd.DataFrame(rows).set_index("day")
    m, ts = t["net"].mean(), tstat(t["net"])
    ann = (1 + t["net"]).prod() ** (365 / len(t)) - 1
    by = t.groupby(t.index.year)["net"].apply(lambda s: (1 + s).prod() - 1)
    eq = (1 + t["net"]).cumprod()
    dd = float((eq / eq.cummax() - 1).min())
    print(f"  {label}: days {len(t)}; mean daily net {m:.3%} (gross {t['gross'].mean():.3%}, turnover cost {TAKER * t['turn'].mean():.3%}); "
          f"t {ts:.2f}; annualised {ann:.1%}; worst drawdown {dd:.1%}")
    print("     by year: " + "; ".join(f"{y} {v:+.1%}" for y, v in by.items()))
    full = by[(by.index >= start.year) & (by.index <= 2025)]
    return m, ts, ann, int((full > 0).sum())


def part408():
    print("\n#### #408 market-neutral 1-day reversal (long day's losers, short day's winners, top 100 by volume)")
    hl = hl_daily()
    fu = pd.read_parquet(PUB / "hl_funding.parquet")
    fu["day"] = pd.to_datetime(fu["time"], unit="ms", utc=True).dt.normalize()
    F = fu.groupby(["day", "coin"])["rate"].sum().unstack()
    m, ts, ann, _ = reversal(hl, F, "Hyperliquid 2023-06..2026-10", pd.Timestamp("2023-06-01", tz="UTC"))
    s1 = not (m < 0.0005 or ts < 3 or ann < 0.20)
    print(f"  STAGE 1 VERDICT (Hyperliquid): {'survives (kill-only)' if s1 else 'KILL'}")
    bn = bn_daily()
    bf = pd.read_parquet(PUB / "cryptotrend370_funding.parquet")
    BF = bf.pivot_table(index="date", columns="sym", values="rate", aggfunc="sum")
    m, ts, ann, pos = reversal(bn, BF, "Binance 2020-01..2026-10", pd.Timestamp("2020-01-01", tz="UTC"))
    ok = s1 and ann >= 0.20 and ts >= 3 and pos >= 4
    print(f"  STAGE 2 VERDICT (Binance): {'PASS' if ok else ('FAIL' if s1 else 'not run (Stage 1 killed) — shown as context')}")


def part411():
    print("\n#### #411 wick bids on Hyperliquid HIP-3 markets")
    p = PUB / "fivehigh_hip3_1d.parquet"
    if not p.exists() or not p.stat().st_size:
        print("  data not fetched yet (Actions job uhip3)")
        return
    d = pd.read_parquet(p)
    if d.empty:
        print("  no HIP-3 candles: not testable")
        return
    d["day"] = pd.to_datetime(d["t"], unit="ms", utc=True).dt.normalize()
    d["usdvol"] = d["v"] * d["c"]
    d = d.drop_duplicates(["coin", "day"]).sort_values(["coin", "day"])[["coin", "day", "o", "h", "l", "c", "usdvol"]]
    print(f"  markets {d['coin'].nunique()} on {d['coin'].str.split(':').str[0].nunique()} dexes, {d['day'].min().date()}..{d['day'].max().date()}")
    f = wick_fills(d, 0.15, 30, 100000)
    end = min(d["day"].max(), pd.Timestamp("2026-10-31", tz="UTC"))
    _, m, t, py, _ = report_fills(f, "HIP-3 X 15%", d["day"].min(), end)
    if len(f) < 30:
        print("  STAGE 1 VERDICT: not testable (fewer than 30 fills)")
    else:
        kill = pd.isna(m) or m < 0.005 or t < 3 or py < 2000
        print(f"  STAGE 1 VERDICT: {'KILL' if kill else 'survives (kill-only)'}")


def main():
    print("===== #405-#409 five high-ceiling liquidity ideas")
    part407()
    part408()
    part411()
    for n, f in (("#405", "fivehigh_bn_premium_trades.parquet"), ("#406", "fivehigh_hl_spot_1d.parquet"), ("#409", "fivehigh_venues_1h.parquet")):
        if not (PUB / f).exists():
            print(f"\n{n}: data not fetched yet (Actions job ufive)")


if __name__ == "__main__":
    main()

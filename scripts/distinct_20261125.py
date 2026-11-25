"""#412 Korean-premium spikes and #413 withdrawal-queue discounts on hourly prices (docs/PREREG_DISTINCT_20261125.md).

    uv run python -m scripts.distinct_20261125 | tee docs/jx_runs/distinct_20261125.txt
Reads data/public/distinct_upbit_1d.parquet, distinct_llama_1h.parquet (Actions job udistinct), uncharted_385_candles.parquet,
hl_funding.parquet, uncharted_389_binance_ohlc.parquet, cryptotrend370_funding.parquet.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

PUB = Path(__file__).resolve().parent.parent / "data" / "public"
FEE, HOLD, SPIKE = 0.00045, 7, 0.05


def tstat(r):
    r = pd.Series(r).dropna()
    return r.mean() / (r.std(ddof=1) / np.sqrt(len(r))) if len(r) > 1 else np.nan


def premium_events(up, C, F, map_coin, start, end, btc):
    """Short when the Upbit premium spikes >= 5 pp above its trailing 30-day median (token on Upbit >= 30 days)."""
    usdt = up[up["coin"] == "USDT"].set_index("day")["krw_close"]
    rows = []
    for coin, g in up[up["coin"] != "USDT"].groupby("coin"):
        col = map_coin(coin)
        if col is None or col == btc:
            continue
        g = g.set_index("day").sort_index()
        first = g.index.min()
        px = C[col].reindex(g.index)
        prem = g["krw_close"] / usdt.reindex(g.index) / px - 1
        base = prem.rolling(30, min_periods=20).median().shift(1)
        sig = (prem - base >= SPIKE) & (g.index >= first + pd.Timedelta(days=30)) & (g.index >= start) & (g.index <= end)
        busy = None
        for d in sig[sig].index:
            if busy is not None and d <= busy:
                continue
            ex = d + pd.Timedelta(days=HOLD)
            if ex not in C.index or pd.isna(C.at[ex, col]) or pd.isna(C.at[d, col]):
                continue
            win = F.loc[d + pd.Timedelta(days=1):ex] if F is not None else pd.DataFrame()
            fs = float(win[col].sum()) if col in win else 0.0
            fb = float(win[btc].sum()) if btc in win else 0.0
            ret = -(C.at[ex, col] / C.at[d, col] - 1) + (C.at[ex, btc] / C.at[d, btc] - 1) + fs - fb - 4 * FEE
            rows.append({"day": d.date(), "coin": coin, "spike": float(prem[d] - base[d]), "ret": ret})
            busy = ex
    return pd.DataFrame(rows)


def show(t, label):
    if t.empty:
        print(f"  {label}: no events")
        return np.nan, np.nan, 0
    r = t["ret"]
    by = t.groupby(pd.to_datetime(t["day"]).dt.year)["ret"].agg(["size", "mean"])
    print(f"  {label}: events {len(t)} ({t['coin'].nunique()} tokens); mean {r.mean():.2%}, median {r.median():.2%}, t {tstat(r):.2f}, "
          f"win {(r > 0).mean():.0%}, worst {r.min():.1%}, best {r.max():.1%}; median spike {t['spike'].median():.1%}")
    print("     by year: " + "; ".join(f"{y} n {int(a['size'])} {a['mean']:+.2%}" for y, a in by.iterrows()))
    return r.mean(), tstat(r), len(t)


def part412():
    print("#### #412 Korean-premium spikes (short on Hyperliquid, 7 days, BTC hedge)")
    p = PUB / "distinct_upbit_1d.parquet"
    if not p.exists():
        print("  Upbit candles not fetched yet (job udistinct)")
        return
    up = pd.read_parquet(p)
    up["day"] = pd.to_datetime(up["day"], utc=True)
    up = up.drop_duplicates(["coin", "day"])
    print(f"  Upbit KRW markets with candles: {up['coin'].nunique()}, {up['day'].min().date()}..{up['day'].max().date()}; "
          f"KRW-USDT present: {'USDT' in set(up['coin'])}")
    hl = pd.read_parquet(PUB / "uncharted_385_candles.parquet")
    hl["day"] = pd.to_datetime(hl["t"], unit="ms", utc=True).dt.normalize()
    C = hl.drop_duplicates(["coin", "day"]).pivot(index="day", columns="coin", values="c")
    fu = pd.read_parquet(PUB / "hl_funding.parquet")
    fu["day"] = pd.to_datetime(fu["time"], unit="ms", utc=True).dt.normalize()
    F = fu.groupby(["day", "coin"])["rate"].sum().unstack()

    def hl_col(c):
        return c if c in C.columns else ("k" + c if ("k" + c) in C.columns else None)
    t = premium_events(up, C, F, hl_col, pd.Timestamp("2023-06-01", tz="UTC"), pd.Timestamp("2026-10-24", tz="UTC"), "BTC")
    m, ts, n = show(t, "Stage 1, Hyperliquid 2023-06..2026-10")
    if n < 15:
        print("  STAGE 1 VERDICT: not testable (fewer than 15 events)")
        return
    s1 = not (m < 0.01 or ts < 1)
    print(f"  STAGE 1 VERDICT: {'survives (kill-only)' if s1 else 'KILL'}")
    b = pd.read_parquet(PUB / "uncharted_389_binance_ohlc.parquet", columns=["sym", "t", "c"])
    b["day"] = pd.to_datetime(b["t"], unit="s", utc=True).dt.normalize()
    CB = b.drop_duplicates(["sym", "day"]).pivot(index="day", columns="sym", values="c")
    bf = pd.read_parquet(PUB / "cryptotrend370_funding.parquet")
    FB = bf.pivot_table(index="date", columns="sym", values="rate", aggfunc="sum")

    def bn_col(c):
        for s in (f"{c}USDT", f"1000{c}USDT"):
            if s in CB.columns:
                return s
        return None
    CBx = CB.copy()
    t2 = premium_events(up, CBx, FB, bn_col, pd.Timestamp("2020-01-01", tz="UTC"), pd.Timestamp("2023-05-31", tz="UTC"), "BTCUSDT")
    m2, ts2, n2 = show(t2, "Stage 2, Binance 2020-01..2023-05 (out-of-sample)")
    ok = s1 and n2 >= 15 and m2 >= 0.02 and ts2 >= 2
    print(f"  STAGE 2 VERDICT: {'PASS' if ok else ('FAIL' if s1 else 'not run (Stage 1 killed) — context')}")


def part413():
    print("\n#### #413 withdrawal-queue discounts on hourly prices (#384 Stage 1b)")
    p = PUB / "distinct_llama_1h.parquet"
    if not p.exists():
        print("  hourly prices not fetched yet (job udistinct)")
        return
    d = pd.read_parquet(p)
    d["ts"] = pd.to_datetime(d["t"], unit="s", utc=True).dt.round("h")
    P = d.drop_duplicates(["id", "ts"]).pivot(index="ts", columns="id", values="price").sort_index()
    pairs = {"khype": ("kinetic-staked-hype", "hyperliquid", 9, 0.025), "sthype": ("staked-hype", "hyperliquid", 9, 0.025),
             "behype": ("hyperbeat-x-ether-fi-hype", "hyperliquid", 9, 0.025), "ezeth": ("renzo-restaked-eth", "ethereum", 7, 0.03),
             "rseth": ("kelp-dao-restaked-eth", "ethereum", 7, 0.03), "weeth": ("wrapped-eeth", "ethereum", 7, 0.03),
             "pufeth": ("pufeth", "ethereum", 7, 0.03), "susde": ("ethena-staked-usde", "ethena-usde", 7, 0.08)}
    trades, span = [], 0.0
    for sym, (tok, und, q, y) in pairs.items():
        if tok not in P or und not in P:
            print(f"  {sym}: missing prices")
            continue
        r = (P[tok] / P[und]).dropna()
        r = r[(r > 0.3) & (r < 3)]
        if len(r) < 1000:
            print(f"  {sym}: {len(r)} hours -> skipped")
            continue
        nav = r.rolling(720, min_periods=240).max()
        span = max(span, (r.index[-1] - r.index[0]).days / 365)
        busy, n0 = None, len(trades)
        for ts, v in r.items():
            if busy is not None and ts <= busy:
                continue
            nv = nav.get(ts)
            if pd.isna(nv) or v > nv * 0.99:
                continue
            red = ts + pd.Timedelta(days=q)
            nr = nav.asof(red) if red <= nav.index[-1] else np.nan
            if pd.isna(nr):
                continue
            net = nr / v - 1 - 0.001 - y * q / 365
            trades.append({"sym": sym, "ts": ts, "disc": 1 - v / nv, "net": net, "pnl": 5000 * net})
            busy = red
        tt = pd.DataFrame(trades[n0:])
        print(f"  {sym}: {r.index[0].date()}..{r.index[-1].date()}, events {len(tt)}" +
              (f", mean net {tt['net'].mean():.2%}, P&L ${tt['pnl'].sum():,.0f}" if len(tt) else ""))
    t = pd.DataFrame(trades)
    if t.empty:
        print("  STAGE 1 VERDICT: KILL (fewer than 4 events)")
        return
    t = t.sort_values("ts")
    free, kept, cap = pd.Timestamp("1970-01-01", tz="UTC"), [], []
    open_until = []
    for _, x in t.iterrows():
        open_until = [u for u in open_until if u > x["ts"]]
        if len(open_until) < 3:  # $15,000 pot = three $5,000 positions at once
            kept.append(x)
            open_until.append(x["ts"] + pd.Timedelta(days=pairs[x["sym"]][2]))
    k = pd.DataFrame(kept)
    per_yr = k["pnl"].sum() / span
    print(f"  pot of $15,000 (3 x $5,000): events {len(k)}, mean net {k['net'].mean():.2%}, losing {int((k['net'] < 0).sum())}, "
          f"${per_yr:,.0f}/yr over {span:.2f} yr")
    kill = len(k) < 4 or per_yr < 3000
    print(f"  STAGE 1 VERDICT: {'KILL' if kill else 'survives (kill-only)'}")


def main():
    print("===== #412-#413 distinct mechanisms")
    part412()
    part413()


if __name__ == "__main__":
    main()

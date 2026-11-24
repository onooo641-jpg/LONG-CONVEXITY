"""#370 crypto perp trend + cross-sectional momentum, 52-config grid, walk-forward (docs/PREREG_CRYPTO_TREND_20261124.md).

    uv run python -m scripts.crypto_trend_20261124 | tee docs/jx_runs/crypto_trend_20261124.txt
Reads data/public/cryptotrend370_klines.parquet (sym, t, close, qvol) and cryptotrend370_funding.parquet (sym, date, rate: daily sum).
"""
from __future__ import annotations

import itertools
from pathlib import Path

import numpy as np
import pandas as pd

PUB = Path(__file__).resolve().parent.parent / "data" / "public"
COST = 0.00045 + 0.0005          # per side, per unit of notional traded
OOS0, END = pd.Timestamp("2021-01-01", tz="UTC"), pd.Timestamp("2026-10-31", tz="UTC")


def load():
    k = pd.read_parquet(PUB / "cryptotrend370_klines.parquet")
    k["date"] = pd.to_datetime(k["t"], unit="s", utc=True).dt.normalize()
    k = k.drop_duplicates(["sym", "date"], keep="last")
    close = k.pivot(index="date", columns="sym", values="close").sort_index()
    qvol = k.pivot(index="date", columns="sym", values="qvol").reindex(close.index)
    f = pd.read_parquet(PUB / "cryptotrend370_funding.parquet")
    fund = f.pivot(index="date", columns="sym", values="rate").reindex(index=close.index, columns=close.columns).fillna(0.0)
    close = close[close.index <= END]
    return close, qvol.loc[close.index], fund.loc[close.index]


def universe(close, qvol, n):
    """Boolean frame: member on day d if in the top-n by trailing-30-day quote volume at the previous month end and priced that day."""
    vol30 = qvol.rolling(30, min_periods=20).sum()
    month_ends = close.index[close.index.to_series().dt.is_month_end]
    mem = pd.DataFrame(False, index=close.index, columns=close.columns)
    for me in month_ends:
        v = vol30.loc[me].dropna()
        top = v.sort_values(ascending=False).index[:n]
        nxt = close.index[(close.index > me) & (close.index <= me + pd.offsets.MonthEnd(1))]
        mem.loc[nxt, top] = True
    return mem & close.notna()


def config_returns(close, fund, mem, ret, vol60, cfg, cost):
    kind = cfg[0]
    rebal = (close.index.dayofweek == 0) if (kind == "XS" or cfg[3] == "weekly") else np.ones(len(close), bool)
    if kind == "TS":
        _, L, mode, _reb, _n = cfg
        sig = np.sign(close / close.shift(L) - 1).shift(1)
        if mode == "long/flat":
            sig = sig.clip(lower=0)
        raw = (sig / vol60.shift(1)).where(mem.shift(1, fill_value=False) & mem)
        w = raw.div(raw.abs().sum(axis=1).replace(0, np.nan), axis=0).fillna(0.0)
    else:
        _, L, q, _n = cfg
        past = (close.shift(2) / close.shift(2 + L) - 1).where(mem)
        rk = past.rank(axis=1, pct=True)
        cnt = past.notna().sum(axis=1)
        k = np.maximum(1, np.floor(cnt * q)).where(cnt >= 4, 0)
        rank_n = past.rank(axis=1, ascending=False)
        rank_lo = past.rank(axis=1, ascending=True)
        long = (rank_n.le(k, axis=0)).astype(float)
        short = (rank_lo.le(k, axis=0)).astype(float)
        nl, ns = long.sum(axis=1).replace(0, np.nan), short.sum(axis=1).replace(0, np.nan)
        w = (0.5 * long.div(nl, axis=0) - 0.5 * short.div(ns, axis=0)).fillna(0.0)
        del rk
    w = w.where(pd.Series(rebal, index=close.index), np.nan).ffill().fillna(0.0)
    w = w.where(mem, 0.0)                       # delisted / out of universe -> flat
    turn = (w - w.shift(1).fillna(0.0)).abs().sum(axis=1)
    pnl = (w * ret.fillna(0.0)).sum(axis=1) - (w * fund).sum(axis=1) - cost * turn
    return pnl, w


def stats(r):
    r = r.dropna()
    if r.empty:
        return np.nan, np.nan, np.nan
    eq = (1 + r).cumprod()
    yrs = ((r.index[-1] - r.index[0]).days + 1) / 365.0
    cagr = eq.iloc[-1] ** (1 / yrs) - 1 if eq.iloc[-1] > 0 else -1.0
    dd = float((eq / eq.cummax() - 1).min())
    sh = float(r.mean() / r.std() * np.sqrt(365)) if r.std() > 0 else np.nan
    return cagr, dd, sh


def walk_forward(R, cost):
    months = pd.date_range(OOS0, END, freq="MS", tz="UTC")
    out, picks, prev = [], [], None
    for m in months:
        hist = R[(R.index < m) & (R.index >= m - pd.DateOffset(months=12))]
        comp = (1 + hist).prod() - 1
        dd = hist.apply(lambda s: float(((1 + s).cumprod() / (1 + s).cumprod().cummax() - 1).min()))
        best = sorted(comp.index, key=lambda c: (-round(comp[c], 12), -dd[c], c))[0]
        seg = R.loc[(R.index >= m) & (R.index < m + pd.offsets.MonthBegin(1)), best].copy()
        if prev is not None and best != prev and len(seg):
            seg.iloc[0] -= 2 * cost                     # close old book, open new one
        out.append(seg)
        picks.append((m.strftime("%Y-%m"), best))
        prev = best
    return pd.concat(out), picks


def main():
    close, qvol, fund = load()
    print(f"===== #370 crypto perp trend + XS momentum: {close.shape[1]} symbols, {close.index[0].date()}..{close.index[-1].date()}")
    ret = close.pct_change(fill_method=None).clip(-0.95, 3.0)
    vol60 = ret.rolling(60, min_periods=30).std()
    mems = {n: universe(close, qvol, n) for n in (20, 50)}
    grid = [("TS", L, m, rb, n) for L, m, rb, n in itertools.product((20, 50, 100, 200), ("long/flat", "long/short"),
                                                                       ("daily", "weekly"), (20, 50))]
    grid += [("XS", L, q, n) for L, q, n in itertools.product((7, 14, 30, 60, 90), (0.1, 0.2), (20, 50))]
    names = [" ".join(str(x) for x in c) for c in grid]
    res = {}
    for mult in (1.0, 1.5):
        cols, npos = {}, {}
        for c, nm in zip(grid, names):
            pnl, w = config_returns(close, fund, mems[c[-1]], ret, vol60, c, COST * mult)
            cols[nm] = pnl
            npos[nm] = (w != 0).sum(axis=1)
        res[mult] = (pd.DataFrame(cols), pd.DataFrame(npos))
    R, NP = res[1.0]
    btc = ret["BTCUSDT"] if "BTCUSDT" in ret else pd.Series(0.0, index=ret.index)

    s1 = R[(R.index >= pd.Timestamp("2024-01-01", tz="UTC"))]
    b1, b2 = "TS 100 long/short daily 20", "XS 30 0.2 50"
    c1, c2 = stats(s1[b1])[0], stats(s1[b2])[0]
    print(f"  Stage 1 (2024-01..2026-10): {b1} CAGR {c1:.1%}; {b2} CAGR {c2:.1%}")
    kill = c1 < 0 and c2 < 0
    print(f"  STAGE 1 VERDICT: {'KILL (both base configs lose money)' if kill else 'survives (kill-only)'}")

    wf, picks = walk_forward(R, COST)
    wf15, _ = walk_forward(res[1.5][0], COST * 1.5)
    mid = wf.index[0] + (wf.index[-1] - wf.index[0]) / 2
    cf, df_, sf = stats(wf)
    ch1, dh1, _ = stats(wf[wf.index < mid])
    ch2, dh2, _ = stats(wf[wf.index >= mid])
    c15, d15, _ = stats(wf15)
    bc, bd, bs = stats(btc[(btc.index >= OOS0)])
    print(f"  walk-forward OOS {wf.index[0].date()}..{wf.index[-1].date()}: CAGR {cf:.1%}, worst DD {df_:.1%}, Sharpe {sf:.2f}")
    print(f"    half 1 CAGR {ch1:.1%} (DD {dh1:.1%}); half 2 CAGR {ch2:.1%} (DD {dh2:.1%}); costs x1.5 CAGR {c15:.1%} (DD {d15:.1%})")
    print(f"    BTC buy-and-hold same window: CAGR {bc:.1%}, worst DD {bd:.1%}, Sharpe {bs:.2f}")
    for y in sorted(set(wf.index.year)):
        cy, dy, _ = stats(wf[wf.index.year == y])
        print(f"    {y}: CAGR {cy:.1%}, DD {dy:.1%}")
    pc = pd.Series([p[1] for p in picks]).value_counts()
    print("  configs picked (months): " + "; ".join(f"{k} x{v}" for k, v in pc.head(8).items()))
    used = [p[1] for p in picks]
    pos = np.mean([NP.loc[(NP.index >= pd.Timestamp(m + '-01', tz='UTC')) & (NP.index < pd.Timestamp(m + '-01', tz='UTC') + pd.offsets.MonthBegin(1)), c].mean()
                   for m, c in picks])
    print(f"  average open positions under the chosen configs: {pos:.1f} (at $15K: ~${15000 / max(pos, 1):,.0f} per position; HL minimum ~$10)")
    prop = min(ch1, ch2) >= 1.0 and c15 >= 1.0 and min(df_, dh1, dh2, d15) >= -0.30
    useful = min(ch1, ch2) >= 0.20 and c15 >= 0.20 and min(df_, d15) >= bd
    print(f"  STAGE 2 VERDICT: {'Prop-like PASS' if prop else ('Useful' if useful else 'FAIL')}"
          + (" (Stage 1 already killed; context only)" if kill else ""))
    print("  context only (hindsight, not a result): best fixed configs over the OOS window")
    oos = R[R.index >= OOS0]
    tab = sorted(((stats(oos[c])[0], stats(oos[c])[1], c) for c in R.columns), key=lambda x: -x[0])[:6]
    for cg, dd, c in tab:
        print(f"    {c:<30} CAGR {cg:.1%}  DD {dd:.1%}")
    del used
    print("  context only (unregistered): yearly CAGR of the best hindsight config and of BTC; 2026 monthly picks")
    best = tab[0][2]
    for y in sorted(set(oos.index.year)):
        cy = stats(oos.loc[oos.index.year == y, best])[0]
        by = stats(btc[(btc.index.year == y) & (btc.index >= OOS0)])[0]
        print(f"    {y}: {best} {cy:.1%}; BTC {by:.1%}")
    print("    2026 picks: " + ", ".join(f"{m} {c}" for m, c in picks if m.startswith("2026")))
    m26 = wf[wf.index.year == 2026]
    mo = (1 + m26).groupby(m26.index.strftime("%Y-%m")).prod() - 1
    print("    2026 monthly walk-forward returns: " + ", ".join(f"{k} {v:+.1%}" for k, v in mo.items()))
    # context only (unregistered): how much of the best hindsight config's profit is tradeable on Hyperliquid (Malaysia-usable venue)?
    hlf = PUB / "hl_funding.parquet"
    if hlf.exists():
        hl = set(pd.read_parquet(hlf)["coin"].unique())

        def to_hl(sym):
            b = sym[:-4]
            return "k" + b[7:] if b.startswith("1000000") else ("k" + b[4:] if b.startswith("1000") else b)
        onhl = [x for x in close.columns if to_hl(x) in hl or x[:-4] in hl]
        bc = tuple(best.split()[0:1]) + (int(best.split()[1]), float(best.split()[2]), int(best.split()[3]))
        _, wb = config_returns(close, fund, mems[bc[-1]], ret, vol60, bc, COST)
        contrib = wb * ret.fillna(0.0)
        print(f"  context only (unregistered): Hyperliquid-listed coins mapped {len(onhl)} of {close.shape[1]}")
        for y in (2024, 2025, 2026):
            m = contrib.index.year == y
            tot, on = contrib[m].sum().sum(), contrib[m][onhl].sum().sum()
            print(f"    {y}: price contribution {tot:+.0%}, from HL-listed coins {on:+.0%}, from Binance-only coins {tot - on:+.0%}")
        c2, q2, f2 = close[onhl], qvol[onhl], fund[onhl]
        r2 = c2.pct_change(fill_method=None).clip(-0.95, 3.0)
        p2, _ = config_returns(c2, f2, universe(c2, q2, bc[-1]), r2, r2.rolling(60, min_periods=30).std(), bc, COST)
        for y in (2023, 2024, 2025, 2026):
            cy, dy, _ = stats(p2[p2.index.year == y])
            print(f"    HL-listed coins only, {best}, {y}: CAGR {cy:.1%}, DD {dy:.1%}")


if __name__ == "__main__":
    main()

"""#382: #370's walk-forward restricted to coins tradeable on Hyperliquid (docs/PREREG_CRYPTO_TREND_HL_20261124.md).

    uv run python -m scripts.crypto_trend_hl_20261124 | tee docs/jx_runs/crypto_trend_hl_20261124.txt
"""
from __future__ import annotations

import itertools

import numpy as np
import pandas as pd

import scripts.crypto_trend_20261124 as M


def to_hl(sym):
    b = sym[:-4]
    return "k" + b[7:] if b.startswith("1000000") else ("k" + b[4:] if b.startswith("1000") else b)


def main():
    close, qvol, fund = M.load()
    hl = set(pd.read_parquet(M.PUB / "hl_funding.parquet")["coin"].unique())
    keep = [x for x in close.columns if to_hl(x) in hl or x[:-4] in hl]
    btc_all = close["BTCUSDT"].pct_change(fill_method=None)
    close, qvol, fund = close[keep], qvol[keep], fund[keep]
    print(f"===== #382 #370 restricted to Hyperliquid-listed coins: {len(keep)} of 918 Binance symbols")
    ret = close.pct_change(fill_method=None).clip(-0.95, 3.0)
    vol60 = ret.rolling(60, min_periods=30).std()
    mems = {n: M.universe(close, qvol, n) for n in (20, 50)}
    grid = [("TS", L, m, rb, n) for L, m, rb, n in itertools.product((20, 50, 100, 200), ("long/flat", "long/short"),
                                                                       ("daily", "weekly"), (20, 50))]
    grid += [("XS", L, q, n) for L, q, n in itertools.product((7, 14, 30, 60, 90), (0.1, 0.2), (20, 50))]
    names = [" ".join(str(x) for x in c) for c in grid]
    R = {mult: pd.DataFrame({nm: M.config_returns(close, fund, mems[c[-1]], ret, vol60, c, M.COST * mult)[0]
                             for c, nm in zip(grid, names)}) for mult in (1.0, 1.5)}
    wf, picks = M.walk_forward(R[1.0], M.COST)
    wf15, _ = M.walk_forward(R[1.5], M.COST * 1.5)
    mid = wf.index[0] + (wf.index[-1] - wf.index[0]) / 2
    cf, df_, sf = M.stats(wf)
    ch1, dh1, _ = M.stats(wf[wf.index < mid])
    ch2, dh2, _ = M.stats(wf[wf.index >= mid])
    c15, d15, _ = M.stats(wf15)
    bc, bd, _ = M.stats(btc_all[btc_all.index >= M.OOS0])
    print(f"  walk-forward OOS {wf.index[0].date()}..{wf.index[-1].date()}: CAGR {cf:.1%}, worst DD {df_:.1%}, Sharpe {sf:.2f}")
    print(f"    half 1 CAGR {ch1:.1%} (DD {dh1:.1%}); half 2 CAGR {ch2:.1%} (DD {dh2:.1%}); costs x1.5 CAGR {c15:.1%} (DD {d15:.1%})")
    print(f"    BTC buy-and-hold: CAGR {bc:.1%}, worst DD {bd:.1%}")
    for y in sorted(set(wf.index.year)):
        cy, dy, _ = M.stats(wf[wf.index.year == y])
        tot = float((1 + wf[wf.index.year == y]).prod() - 1)
        print(f"    {y}: return {tot:+.1%} (CAGR {cy:.1%}), DD {dy:.1%}")
    print("  by start date (walk-forward equity from that date to 2026-10-31):")
    for s in ("2021-01-01", "2022-01-01", "2023-01-01", "2024-01-01", "2025-01-01"):
        seg = wf[wf.index >= pd.Timestamp(s, tz="UTC")]
        eq = (1 + seg).cumprod()
        print(f"    start {s[:7]}: x{eq.iloc[-1]:.2f} at the end; worst drawdown {float((eq / eq.cummax() - 1).min()):.1%}; "
              f"lowest point x{eq.min():.2f}")
    prop = min(ch1, ch2) >= 1.0 and c15 >= 1.0 and min(df_, dh1, dh2, d15) >= -0.30
    useful = min(ch1, ch2) >= 0.20 and c15 >= 0.20 and min(df_, d15) >= bd
    print(f"  VERDICT: {'Prop-like PASS' if prop else ('Useful' if useful else 'FAIL')}")


if __name__ == "__main__":
    main()

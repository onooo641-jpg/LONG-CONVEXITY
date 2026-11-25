"""#414 short lottery coins (MAX effect), market-neutral, weekly (docs/PREREG_DISTINCT_20261125.md).

    uv run python -m scripts.lottery_20261125 | tee docs/jx_runs/lottery_20261125.txt
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

PUB = Path(__file__).resolve().parent.parent / "data" / "public"
TAKER = 0.00045


def tstat(r):
    r = pd.Series(r).dropna()
    return r.mean() / (r.std(ddof=1) / np.sqrt(len(r))) if len(r) > 1 else np.nan


def backtest(d, F, start, end, label):
    C = d.pivot(index="day", columns="coin", values="c").sort_index()
    V = d.pivot(index="day", columns="coin", values="usdvol").reindex(C.index)
    first = d.groupby("coin")["day"].min()
    R = C.pct_change(fill_method=None)
    MAX = R.rolling(30, min_periods=20).max()
    vol30 = V.rolling(30, min_periods=20).sum()
    mondays = [x for x in C.index if x.weekday() == 0 and start <= x <= end]
    rows, wl0, ws0 = [], pd.Series(dtype=float), pd.Series(dtype=float)
    for i, day in enumerate(mondays[:-1]):
        nxt = mondays[i + 1]
        if (nxt - day).days != 7:
            continue
        age_ok = pd.Series({c: (day - first[c]).days >= 60 for c in C.columns})
        ok = age_ok & MAX.loc[day].notna() & vol30.loc[day].notna() & C.loc[nxt].notna() & C.loc[day].notna()
        univ = vol30.loc[day][ok].sort_values(ascending=False).head(100).index
        if len(univ) < 30:
            continue
        m = MAX.loc[day, univ].sort_values()
        k = max(1, int(len(univ) * 0.10))
        L, S = m.index[:k], m.index[-k:]
        wl, ws = pd.Series(1 / k, index=L), pd.Series(1 / k, index=S)
        turn = wl.sub(wl0, fill_value=0).abs().sum() + ws.sub(ws0, fill_value=0).abs().sum()
        rl = (C.loc[nxt, L] / C.loc[day, L] - 1).mean()
        rs = (C.loc[nxt, S] / C.loc[day, S] - 1).mean()
        fw = F.loc[day + pd.Timedelta(days=1):nxt] if F is not None else None
        fl = float(fw.reindex(columns=L).fillna(0).sum().mean()) if fw is not None and len(fw) else 0.0
        fs = float(fw.reindex(columns=S).fillna(0).sum().mean()) if fw is not None and len(fw) else 0.0
        net = rl - rs - fl + fs - TAKER * turn
        rows.append({"day": nxt, "net": net, "long": rl, "short": -rs, "fund": fs - fl, "cost": TAKER * turn})
        wl0, ws0 = wl, ws
    t = pd.DataFrame(rows).set_index("day")
    ann = (1 + t["net"]).prod() ** (52 / len(t)) - 1
    eq = (1 + t["net"]).cumprod()
    dd = float((eq / eq.cummax() - 1).min())
    by = t.groupby(t.index.year)["net"].apply(lambda s: (1 + s).prod() - 1)
    print(f"  {label}: weeks {len(t)}; mean weekly {t['net'].mean():.2%} (long leg {t['long'].mean():+.2%}, short leg {t['short'].mean():+.2%}, "
          f"funding {t['fund'].mean():+.2%}, costs {t['cost'].mean():.2%}); t {tstat(t['net']):.2f}; annualised {ann:.1%}; worst drawdown {dd:.1%}")
    print("     by year: " + "; ".join(f"{y} {v:+.1%}" for y, v in by.items()))
    return ann, tstat(t["net"]), by


def main():
    print("===== #414 short lottery coins (MAX effect), market-neutral weekly")
    hl = pd.read_parquet(PUB / "uncharted_385_candles.parquet")
    hl["day"] = pd.to_datetime(hl["t"], unit="ms", utc=True).dt.normalize()
    hl["usdvol"] = hl["v"] * hl["c"]
    hl = hl.drop_duplicates(["coin", "day"])
    fu = pd.read_parquet(PUB / "hl_funding.parquet")
    fu["day"] = pd.to_datetime(fu["time"], unit="ms", utc=True).dt.normalize()
    F = fu.groupby(["day", "coin"])["rate"].sum().unstack()
    ann, ts, _ = backtest(hl, F, pd.Timestamp("2023-06-01", tz="UTC"), pd.Timestamp("2026-10-31", tz="UTC"), "Stage 1, Hyperliquid 2023-06..2026-10")
    s1 = ann >= 0.15 and ts >= 2
    print(f"  STAGE 1 VERDICT: {'survives (kill-only)' if s1 else 'KILL'}")
    b = pd.read_parquet(PUB / "uncharted_389_binance_ohlc.parquet").rename(columns={"sym": "coin", "qvol": "usdvol"})
    b["day"] = pd.to_datetime(b["t"], unit="s", utc=True).dt.normalize()
    b = b.drop_duplicates(["coin", "day"])
    bf = pd.read_parquet(PUB / "cryptotrend370_funding.parquet")
    BF = bf.pivot_table(index="date", columns="sym", values="rate", aggfunc="sum")
    ann2, ts2, by2 = backtest(b, BF, pd.Timestamp("2020-01-01", tz="UTC"), pd.Timestamp("2023-05-31", tz="UTC"),
                              "Stage 2 (out-of-sample), Binance 2020-01..2023-05")
    full = by2[[y for y in (2020, 2021, 2022) if y in by2.index]]
    ok = s1 and ann2 >= 0.15 and ts2 >= 2 and int((full > 0).sum()) >= 2
    print(f"  STAGE 2 VERDICT: {'PASS' if ok else ('FAIL' if s1 else 'not run (Stage 1 killed) — context')}")
    backtest(b, BF, pd.Timestamp("2023-06-01", tz="UTC"), pd.Timestamp("2026-10-31", tz="UTC"), "context, Binance 2023-06..2026-10")


if __name__ == "__main__":
    main()

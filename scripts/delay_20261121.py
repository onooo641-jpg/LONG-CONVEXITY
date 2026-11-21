"""Manual entry delay (docs/PREREG_DELAY_20261121.md).

    uv run python scripts/delay_20261121.py
"""
from __future__ import annotations

import pandas as pd

from backtest.engine import BacktestConfig, simulate
from backtest.recycle import Policy, XFARules, recycle
from ict import data as D
from scripts.firms2_20261120 import worst_dip

WIN = {"2016-26": ("2016-01-01", "2026-10-29"), "2024-26": ("2024-01-01", "2026-10-29")}


def main() -> int:
    bars = D.load("1m")
    orders = pd.read_parquet(D.PROCESSED_DIR / "ideas_orders_NQ.parquet")
    base, ratios = {}, {}
    for d in (0, 1, 2, 3, 5):
        o = orders.copy()
        o["valid_from"] = o["valid_from"] + pd.Timedelta(minutes=d)
        o = o[o["valid_from"] < o["expires_at"]]
        t = simulate(o, bars, BacktestConfig(risk_per_trade_usd=900))
        t = t[t["filled"]]
        line = [f"delay {d} min:"]
        for w, (lo, hi) in WIN.items():
            tw = t[(t.entry_ts >= pd.Timestamp(lo, tz="UTC")) & (t.entry_ts < pd.Timestamp(hi, tz="UTC"))]
            tw = tw.sort_values("exit_ts").reset_index(drop=True)
            out = recycle(tw, XFARules(), policy=Policy.LOCK_FIRST)
            net = out["net"]
            if d == 0:
                base[w] = net
            ratios[(d, w)] = net / base[w]
            line.append(f"{w}: {len(tw)} trades, win {float((tw.net_pnl > 0).mean()):.1%}, raw ${tw.net_pnl.sum():,.0f}, "
                        f"Topstep net ${net:,.0f} ({net / base[w]:.0%} of d=0), dip ${worst_dip(out):,.0f} |")
        ok = all(ratios[(d, w)] >= 0.8 for w in WIN)
        print(" ".join(line) + f" -> {'VIABLE' if ok else 'not viable'}", flush=True)
    viable = [d for d in (1, 2, 3, 5) if all(ratios[(d, w)] >= 0.8 for w in WIN)]
    print(f"\nlargest viable delay (pre-registered rule): {max(viable) if viable else 'none -> drop semi-automated category'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

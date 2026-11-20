"""Bigger Topstep accounts inside the market mix (docs/PREREG_SIZEMIX_20261120.md).

    uv run python scripts/sizemix_20261120.py
"""
from __future__ import annotations

import dataclasses
import sys

import pandas as pd

sys.path.insert(0, "scripts")
from account_size_test import CAPS, SIZES  # noqa: E402
from backtest.engine import COMMISSION_MNQ, BacktestConfig, simulate  # noqa: E402
from backtest.recycle import XFARules  # noqa: E402
from es_test import bars_for  # noqa: E402
from ict import data as D  # noqa: E402
from marketmix_20261120 import no_cross_hedge  # noqa: E402
from scripts.portfolio_20261120 import DAYS, HI, LO, daily_from_recycle, stats  # noqa: E402

MIX = {"NQ": 3, "ES": 1, "YM": 1}
PROJECTX = 14.50
TICKV = {"NQ": 2.0 * 0.25, "ES": 5.0 * 0.25, "YM": 0.50 * 0.25}
SLIP = {"NQ": 1.0, "ES": 1.0, "YM": 1.0 / 0.25}


def bars(m):
    return bars_for(m) if m in ("NQ", "ES") else D.add_time_columns(D.load_raw("YM_v_0_1m_*.parquet"))


def main() -> int:
    b = {m: bars(m) for m in MIX}
    o = {m: pd.read_parquet(D.PROCESSED_DIR / f"ideas_orders_{m}.parquet") for m in MIX}

    def trades(m, risk):
        cfg = BacktestConfig(risk_per_trade_usd=risk, tick_value=TICKV[m],
                             commission_per_round_turn=COMMISSION_MNQ, exit_slippage_ticks=SLIP[m])
        t = simulate(o[m], b[m], cfg)
        t = t[t["filled"]]
        t = t[(t.entry_ts >= pd.Timestamp(LO, tz="UTC")) & (t.entry_ts < pd.Timestamp(HI, tz="UTC"))]
        return t.sort_values("exit_ts").reset_index(drop=True)

    months = pd.Series(((DAYS - DAYS[0]).days // 30.4375 + 1) * PROJECTX, index=DAYS)
    res = {}
    yearly = {}
    for size, kw in SIZES.items():
        risk = 0.45 * kw["loss_limit"]
        tr, skipped = no_cross_hedge({m: trades(m, risk) for m in MIX})
        rules = dataclasses.replace(XFARules(), payout_cap=CAPS[size][0], api_monthly=0.0, **kw)
        s = sum(n * daily_from_recycle(tr[m], rules)[0] for m, n in MIX.items()) - months
        name = f"T5-mix {size} (risk ${risk:,.0f}; skipped {sum(skipped.values())})"
        yearly[size] = stats(name, s)
        peak = s.cummax().clip(lower=0)
        res[size] = (s.iloc[-1], max(-(s - peak).min(), -min(0.0, s.min())))
    print("\nyearly income:\n" + pd.DataFrame(yearly).to_string(float_format=lambda x: f"{x:,.0f}"))
    n50, c50 = res["50K"]
    for size in ("100K", "150K"):
        n, c = res[size]
        ok = n >= 1.30 * n50 and c <= 15336
        print(f"{size} vs 50K: net {n / n50 - 1:+.1%}, cash ${c:,.0f} ({c / c50 - 1:+.1%}), net per $ cash "
              f"{n / c:.1f} vs {n50 / c50:.1f} -> {'WORTH SWITCHING' if ok else 'not worth switching'} (pre-registered rule)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""YM and RTY unseen-market tests, exactly as docs/PREREG_YM_RTY.md defines them.

    uv run python scripts/ym_rty_test.py

Pre-registered in 23b0c8a, before the data reached the repo.
"""

from __future__ import annotations

import dataclasses
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, "scripts")
from es_test import chain, coin_flips, window  # noqa: E402
from backtest.engine import COMMISSION_MNQ, BacktestConfig, simulate  # noqa: E402
from ict import data as D  # noqa: E402
from strategies.ltf_sweep import LTFSweepConfig, generate_orders  # noqa: E402

SEEN = ("2016-01-01", "2026-10-29")
OLD = ("2010-07-01", "2016-01-01")
RISK = 900.0
#: point value ($/pt) and real tick size of the micro contract
SPECS = {"YM": (0.50, 1.0), "RTY": (5.00, 0.1)}
ENGINE_TICK = 0.25


def rth_close(bars):
    m = bars["minutes_from_midnight"]
    return bars[(m >= 570) & (m < 960)].groupby("ny_date")["close"].last()


def first_full_month(bars, lo):
    start = max(pd.Timestamp(lo, tz="UTC"), bars["ts"].min())
    if start > pd.Timestamp(lo, tz="UTC"):
        start = (start + pd.offsets.MonthBegin(1)).normalize()
    return start


def report(label, t):
    p = t["net_pnl"]
    pf = p[p > 0].sum() / -p[p < 0].sum()
    out, pr = chain(t)
    nets, passes = coin_flips(t)
    q95 = float(np.percentile(nets, 95))
    years = t.assign(y=pd.DatetimeIndex(t["exit_ts"]).tz_convert(
        "America/New_York").year).groupby("y")["net_pnl"].sum()
    print(f"  {label}")
    print(f"    trades {len(t):,}  win {float((p > 0).mean()):.1%}  PF {pf:.3f}  "
          f"raw ${p.sum():,.0f}  fees ${float((t['gross_pnl'] - t['net_pnl']).sum()):,.0f}  "
          f"median contracts {int(t['contracts'].median())}  median stop {t['risk_points'].median():.2f} pts")
    print(f"    recycling net ${out['net']:,.0f}  spent ${out['cost']:,.0f}  pass {pr:.1%}  "
          f"payouts {out['payouts']}  dry {out['longest_dry_days']:,.0f} d")
    print(f"    coin flip x200: median ${np.median(nets):,.0f}  95th pct ${q95:,.0f}  "
          f"pass median {np.median(passes):.1%}  real beats {np.mean(nets < out['net']):.0%}")
    print("    raw by year: " + "  ".join(f"{y} {v:,.0f}" for y, v in years.items()))
    return out["net"] > q95


def main() -> int:
    nq = D.load("1m")
    nq_close = rth_close(nq)
    verdicts = {}
    for mkt, (ppt, tick) in SPECS.items():
        bars = D.add_time_columns(D.load_raw(f"{mkt}_v_0_1m_*.parquet"))
        print(f"\n{'=' * 78}\n{mkt}: {len(bars):,} bars  {bars.ts.min()} -> {bars.ts.max()}")
        both = pd.concat([rth_close(bars), nq_close], axis=1, keys=["m", "nq"]).dropna()
        both = both[(both.index >= pd.Timestamp(SEEN[0]).date())
                    & (both.index < pd.Timestamp(SEEN[1]).date())]
        k = round(float((both["m"] / both["nq"]).median()), 2)
        base = LTFSweepConfig()
        scaled = dataclasses.replace(
            base, stop_buffer_points=base.stop_buffer_points * k,
            min_fvg_size=base.min_fvg_size * k, min_risk_points=base.min_risk_points * k,
            max_risk_points=base.max_risk_points * k, min_penetration=tick)
        cfg = BacktestConfig(risk_per_trade_usd=RISK, tick_value=ppt * ENGINE_TICK,
                             commission_per_round_turn=COMMISSION_MNQ,
                             exit_slippage_ticks=tick / ENGINE_TICK)
        seen_lo = first_full_month(bars, SEEN[0])
        print(f"  k = {k}   deciding window starts {seen_lo.date()}")
        for ver, sc in (("U", base), ("S", scaled)):
            t = simulate(generate_orders(bars, sc), bars, cfg)
            t = t[t["filled"]].sort_values("exit_ts").reset_index(drop=True)
            verdicts[(mkt, ver)] = report(f"{ver} DECIDES {seen_lo.date()} .. 2026-10-28",
                                          window(t, str(seen_lo.date()), SEEN[1]))
            old = window(t, *OLD)
            if len(old) >= 50:
                report(f"{ver} context 2010-07 .. 2015-12", old)
            else:
                print(f"  {ver} context: {len(old)} trades, not enough data to report")

    print(f"\n{'=' * 78}\nVERDICTS (net above coin-flip 95th pct)")
    for (mkt, ver), ok in verdicts.items():
        print(f"  {mkt} {ver}: {'CONFIRMS' if ok else 'does not confirm'}")
    s_both = verdicts[("YM", "S")] and verdicts[("RTY", "S")]
    s_any = verdicts[("YM", "S")] or verdicts[("RTY", "S")]
    print(f"  scaled hypothesis: {'SUPPORTED' if s_both else 'MIXED' if s_any else 'NOT SUPPORTED'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

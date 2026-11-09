"""Tests pre-registered in docs/PREREG_20261109.md (committed first, ab112d1).

    uv run python scripts/jx_ideas_20261109.py

1. risk per trade, 2. ES sensitivities (post-hoc), 3. NQ + ES side by side.
"""

from __future__ import annotations

import dataclasses
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, "scripts")
from es_test import (COMMISSION_MES, TICK_VALUE_MES, chain, coin_flips,  # noqa: E402
                     window)
from backtest.engine import COMMISSION_MNQ, TICK_VALUE_MNQ, BacktestConfig, simulate  # noqa: E402
from backtest.recycle import Policy, XFARules, recycle  # noqa: E402
from ict import data as D  # noqa: E402
from strategies.ltf_sweep import LTFSweepConfig, generate_orders  # noqa: E402

SEEN = ("2016-01-01", "2026-10-29")
OLD = ("2010-07-01", "2016-01-01")
LEVELS = [500.0, 700.0, 900.0, 1200.0, 1500.0]
RULES, POLICY = XFARules(), Policy.LOCK_FIRST


def flips_median(t, n):
    """Coin-flip median net with n flips (same method as es_test.coin_flips)."""
    g = t["gross_pnl"].to_numpy()
    comm = (t["gross_pnl"] - t["net_pnl"]).to_numpy()
    rng = np.random.default_rng(1)
    return float(np.median([recycle(t.assign(net_pnl=np.abs(g) * rng.choice([-1, 1], len(t)) - comm),
                                    RULES, policy=POLICY)["net"] for _ in range(n)]))


def sim(orders, bars, risk, tick_value, commission):
    t = simulate(orders, bars, BacktestConfig(risk_per_trade_usd=risk, tick_value=tick_value,
                                              commission_per_round_turn=commission))
    return t[t["filled"]].sort_values("exit_ts").reset_index(drop=True)


def rth_close(bars):
    m = bars["minutes_from_midnight"]
    return bars[(m >= 570) & (m < 960)].groupby("ny_date")["close"].last()


def test1(markets):
    print("\n" + "=" * 78 + "\nTEST 1  risk per trade  (recycling net; coin-flip median, 100 flips)")
    table = {}
    for name, (bars, orders, tv, cm) in markets.items():
        for lvl in LEVELS:
            t = sim(orders, bars, lvl, tv, cm)
            for wname, w in (("SEEN", SEEN), ("OLD", OLD)):
                tw = window(t, *w)
                out, pr = chain(tw)
                table[(name, wname, lvl)] = out["net"]
                print(f"  {name} {wname:<4} ${lvl:>5,.0f}: net ${out['net']:>9,.0f}  "
                      f"spent ${out['cost']:>7,.0f}  pass {pr:5.1%}  payouts {out['payouts']:>3}  "
                      f"dry {out['longest_dry_days']:>5,.0f} d  flip median ${flips_median(tw, 100):>9,.0f}")
    print("\n  RULE: replace $900 only if higher net in all four datasets")
    keys = [(m, w) for m in markets for w in ("SEEN", "OLD")]
    winners = []
    for lvl in LEVELS:
        if lvl == 900.0:
            continue
        better = [table[(m, w, lvl)] > table[(m, w, 900.0)] for m, w in keys]
        print(f"  ${lvl:,.0f}: higher in {sum(better)}/4 "
              f"({', '.join(f'{m} {w}' for (m, w), b in zip(keys, better) if b) or 'none'})")
        if all(better):
            winners.append(lvl)
    if winners:
        best = max(winners, key=lambda lv: table[("NQ", "SEEN", lv)])
        print(f"  VERDICT: switch to ${best:,.0f}")
    else:
        print("  VERDICT: $900 stays")


def es_line(label, t):
    p = t["net_pnl"]
    pf = p[p > 0].sum() / -p[p < 0].sum()
    out, pr = chain(t)
    nets, _ = coin_flips(t)
    print(f"  {label:<34} trades {len(t):>5}  PF {pf:.3f}  raw ${p.sum():>9,.0f}  "
          f"net ${out['net']:>9,.0f}  pass {pr:5.1%}  flip 95th ${np.percentile(nets, 95):>9,.0f}  "
          f"beats {np.mean(nets < out['net']):.0%}")


def test2(es_bars, es_orders, nq_bars):
    print("\n" + "=" * 78 + "\nTEST 2  ES sensitivities  (POST-HOC, exploratory; SEEN window)")
    base = window(sim(es_orders, es_bars, 900.0, TICK_VALUE_MES, COMMISSION_MES), *SEEN)
    es_line("as registered ($1.24)", base)
    es_line("2a commission $0.74", window(sim(es_orders, es_bars, 900.0, TICK_VALUE_MES, 0.74), *SEEN))

    es_c, nq_c = rth_close(es_bars), rth_close(nq_bars)
    both = pd.concat([es_c, nq_c], axis=1, keys=["es", "nq"]).dropna()
    both = both[(both.index >= pd.Timestamp(SEEN[0]).date()) & (both.index < pd.Timestamp(SEEN[1]).date())]
    k = round(float((both["es"] / both["nq"]).median()), 2)
    base_cfg = LTFSweepConfig()
    cfg = dataclasses.replace(base_cfg,
                              stop_buffer_points=base_cfg.stop_buffer_points * k,
                              min_fvg_size=base_cfg.min_fvg_size * k,
                              min_risk_points=base_cfg.min_risk_points * k,
                              max_risk_points=base_cfg.max_risk_points * k)
    print(f"  k = median ES/NQ close over SEEN = {k}")
    scaled = generate_orders(es_bars, cfg)
    es_line(f"2b settings x{k} ($1.24)",
            window(sim(scaled, es_bars, 900.0, TICK_VALUE_MES, COMMISSION_MES), *SEEN))


def monthly(timeline):
    tl = pd.DataFrame(timeline)
    tl["m"] = pd.DatetimeIndex(tl["ts"]).tz_convert("America/New_York").to_period("M")
    net = tl.groupby("m")["net"].last()
    pay = tl[tl.event == "payout"].groupby("m").size()
    return net, pay


def test3(nq_t, es_t):
    print("\n" + "=" * 78 + "\nTEST 3  NQ + ES side by side, $900 each, SEEN  (descriptive)")
    nq_o, _ = chain(nq_t)
    es_o, _ = chain(es_t)
    nq_net, nq_pay = monthly(nq_o["timeline"])
    es_net, es_pay = monthly(es_o["timeline"])
    months = pd.period_range(min(nq_net.index.min(), es_net.index.min()),
                             max(nq_net.index.max(), es_net.index.max()), freq="M")
    a = nq_net.reindex(months).ffill().fillna(0.0)
    b = es_net.reindex(months).ffill().fillna(0.0)
    comb = a + b
    flow_a, flow_b = a.diff().fillna(a), b.diff().fillna(b)
    paid_nq = nq_pay.reindex(months).fillna(0) > 0
    paid_any = paid_nq | (es_pay.reindex(months).fillna(0) > 0)
    print(f"  net: NQ ${nq_o['net']:,.0f}   ES ${es_o['net']:,.0f}   combined ${comb.iloc[-1]:,.0f}")
    print(f"  deepest cash position (month-end): NQ ${a.min():,.0f}   combined ${comb.min():,.0f}")
    print(f"  months with a payout: NQ alone {paid_nq.mean():.0%}   either {paid_any.mean():.0%}  "
          f"({len(months)} months)")
    print(f"  correlation of monthly cash flow NQ vs ES: {flow_a.corr(flow_b):.2f}")


def main() -> int:
    nq_bars = D.load("1m")
    es_bars = D.add_time_columns(D.load_raw("ES_v_0_1m_*.parquet"))
    def orders_cached(name, bars):
        path = D.PROCESSED_DIR / f"ideas_orders_{name}.parquet"
        if path.exists():
            return pd.read_parquet(path)
        o = generate_orders(bars)
        o.to_parquet(path)
        return o

    print("generating orders ...")
    nq_orders, es_orders = orders_cached("NQ", nq_bars), orders_cached("ES", es_bars)
    markets = {"NQ": (nq_bars, nq_orders, TICK_VALUE_MNQ, COMMISSION_MNQ),
               "ES": (es_bars, es_orders, TICK_VALUE_MES, COMMISSION_MES)}
    test1(markets)
    test2(es_bars, es_orders, nq_bars)
    test3(window(sim(nq_orders, nq_bars, 900.0, TICK_VALUE_MNQ, COMMISSION_MNQ), *SEEN),
          window(sim(es_orders, es_bars, 900.0, TICK_VALUE_MES, COMMISSION_MES), *SEEN))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

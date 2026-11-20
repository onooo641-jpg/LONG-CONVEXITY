"""Compare the live Topstep account with the model (docs/PREREG_LIVE_20261120.md).

Inputs (written on the trading computer by scripts/export_live_trades.py):
  data/live/fills.csv       ProjectX Trade/search fills
  data/live/decisions.csv   bridge journal: placed orders with planned entry/stop/target/qty
  docs/live_predictions.json  pre-registered predictions

    uv run python scripts/live_compare.py            # report to stdout and docs/live_report.md
    uv run python scripts/live_compare.py --backtest # also re-run the engine on the live days
"""
from __future__ import annotations

import argparse
import json
import pathlib

import numpy as np
import pandas as pd

NY = "America/New_York"
TICK = 0.25
FILLS = pathlib.Path("data/live/fills.csv")
DECISIONS = pathlib.Path("data/live/decisions.csv")
PREDS = pathlib.Path("docs/live_predictions.json")
REPORT = pathlib.Path("docs/live_report.md")

#: Pre-registered gates (docs/PREREG_LIVE_20261120.md).
GATE_PARITY = 0.95            # share of backtest signals the bot placed at the same levels
GATE_STOP_SLIP = 2.0          # mean stop-exit slippage, ticks
GATE_FILL_RATE_DIFF = 0.10    # live fill rate vs backtest fill rate
GATE_MIN_TRADES = 40          # trades before the outcome band is judged


def round_trips(fills: pd.DataFrame) -> pd.DataFrame:
    """One row per trading day: entry/exit VWAP, size, P&L, costs.

    ProjectX: ``profitAndLoss`` is null on opening fills; side 0 = buy, 1 = sell.
    The strategy takes at most one trade a day, so a day is a round trip.
    """
    f = fills.copy()
    f = f[~f["voided"].astype(str).str.lower().isin(["true", "1"])]
    f["ts"] = pd.to_datetime(f["creationTimestamp"], utc=True)
    f["day"] = f["ts"].dt.tz_convert(NY).dt.date.astype(str)
    f["opening"] = f["profitAndLoss"].isna()
    f["cost"] = f["fees"].fillna(0) + f["commissions"].fillna(0)
    rows = []
    for day, g in f.sort_values("ts").groupby("day"):
        op, cl = g[g.opening], g[~g.opening]
        if op.empty:
            continue
        side = 1 if int(op["side"].iloc[0]) == 0 else -1
        vwap = lambda x: float((x["price"] * x["size"]).sum() / x["size"].sum()) if len(x) else np.nan
        rows.append({"day": day, "direction": side, "size": int(op["size"].sum()),
                     "entry_fill": vwap(op), "exit_fill": vwap(cl),
                     "entry_ts": op["ts"].min(), "exit_ts": cl["ts"].max() if len(cl) else pd.NaT,
                     "gross_pnl": float(cl["profitAndLoss"].sum()), "costs": float(g["cost"].sum()),
                     "closed": bool(len(cl) and cl["size"].sum() >= op["size"].sum())})
    return pd.DataFrame(rows)


def placed_orders(decisions: pd.DataFrame) -> pd.DataFrame:
    d = decisions[decisions["event"] == "placed"].copy()
    if "dry_run" in d:
        d = d[~d["dry_run"].astype(str).str.lower().isin(["true", "1"])]
    d["direction"] = np.where(d["side"].astype(str).str.lower().isin(["buy", "long", "1"]), 1, -1)
    return d[["day", "direction", "qty", "entry", "stop", "target", "planned_risk"]].drop_duplicates("day", keep="last")


def execution(trips: pd.DataFrame, placed: pd.DataFrame) -> pd.DataFrame:
    """Join fills to the plan and measure slippage in ticks (positive = worse than planned)."""
    m = placed.merge(trips, on="day", how="left", suffixes=("_plan", ""))
    m["filled"] = m["entry_fill"].notna()
    d = m["direction_plan"]
    m["entry_slip_ticks"] = (m["entry_fill"] - m["entry"]) * d / TICK
    near_stop = (m["exit_fill"] - m["stop"]).abs() < (m["exit_fill"] - m["target"]).abs()
    m["exit_kind"] = np.where(m["exit_fill"].isna(), "open", np.where(near_stop, "stop", "target"))
    m["exit_slip_ticks"] = np.where(m["exit_kind"] == "stop", (m["stop"] - m["exit_fill"]) * d / TICK,
                                    np.where(m["exit_kind"] == "target", (m["target"] - m["exit_fill"]) * d / TICK, np.nan))
    m["net_pnl"] = m["gross_pnl"] - m["costs"]
    m["net_r"] = m["net_pnl"] / m["planned_risk"]
    m["cost_per_micro_rt"] = m["costs"] / m["size"]
    m["size_matches_plan"] = m["size"] == m["qty"]
    return m


def band_check(net_r: np.ndarray, preds: dict) -> list[str]:
    n = len(net_r)
    cum = float(net_r.sum())
    out = [f"live trades closed: {n}; cumulative net R {cum:+.2f}; mean {net_r.mean() if n else float('nan'):+.3f}R"]
    for name, w in preds["windows"].items():
        bands = w["rolling_cum_net_r"]
        ns = sorted(int(k) for k in bands if int(k) <= n)
        if not ns:
            out.append(f"  vs {name}: too early (band starts at {min(int(k) for k in bands)} trades)")
            continue
        k = ns[-1]
        b = bands[str(k)]
        c = float(net_r[-k:].sum())
        where = ("BELOW 5th pct" if c < b["5"] else "above 95th pct" if c > b["95"] else
                 "inside 5-95% band")
        out.append(f"  vs {name}: last {k} trades {c:+.1f}R; band 5% {b['5']:+.1f} / 50% {b['50']:+.1f} / "
                   f"95% {b['95']:+.1f} -> {where}")
    return out


def backtest_days(days: list[str]) -> pd.DataFrame:
    """Re-run the strategy on the live days (needs 1m bars covering them)."""
    from backtest.engine import BacktestConfig, simulate
    from ict import data as D
    from strategies.ltf_sweep import LTFSweepConfig, generate_orders
    bars = D.load("1m")
    lo = pd.Timestamp(min(days), tz=NY).tz_convert("UTC") - pd.Timedelta(days=3)
    b = bars[bars.index >= lo] if isinstance(bars.index, pd.DatetimeIndex) else bars
    orders = generate_orders(b, LTFSweepConfig())
    t = simulate(orders, b, BacktestConfig(risk_per_trade_usd=900))
    t["day"] = pd.to_datetime(t["valid_from"]).dt.tz_convert(NY).dt.date.astype(str)
    return t[t["day"].isin(days)]


def report(fills, decisions, preds, bt=None) -> str:
    trips = round_trips(fills)
    placed = placed_orders(decisions)
    m = execution(trips, placed)
    closed = m[m["filled"] & m["exit_fill"].notna()]
    lines = ["# Live vs model report", "",
             f"Days with a placed order: {len(placed)}; filled: {int(m['filled'].sum())}; closed: {len(closed)}", ""]
    w0 = next(iter(preds["windows"].values()))
    fr = m["filled"].mean() if len(m) else float("nan")
    lines += ["## 1. Execution",
              f"- fill rate of placed orders: {fr:.0%} (model {w0['signal_fill_rate']:.0%}; gate: within "
              f"{GATE_FILL_RATE_DIFF:.0%}) -> {'OK' if abs(fr - w0['signal_fill_rate']) <= GATE_FILL_RATE_DIFF else 'CHECK'}",
              f"- entry slippage: mean {m['entry_slip_ticks'].mean():+.2f} ticks (model 0)",
              f"- stop-exit slippage: mean {m.loc[m.exit_kind == 'stop', 'exit_slip_ticks'].mean():+.2f} ticks "
              f"(model 1; gate <= {GATE_STOP_SLIP})",
              f"- target-exit slippage: mean {m.loc[m.exit_kind == 'target', 'exit_slip_ticks'].mean():+.2f} ticks (model 0)",
              f"- costs per micro round turn: ${m['cost_per_micro_rt'].mean():.2f} (model ${preds['commission_per_micro_rt_model']:.2f})",
              f"- size matched the plan: {m.loc[m.filled, 'size_matches_plan'].mean():.0%}", ""]
    if bt is not None:
        bt_days = bt[["day", "direction", "entry_price", "stop_price", "target_price", "filled", "r_multiple", "net_pnl"]]
        j = bt_days.merge(placed, on="day", how="left", suffixes=("_bt", ""))
        same = ((j["direction_bt"] == j["direction"]) & ((j["entry_price"] - j["entry"]).abs() <= TICK)
                & ((j["stop_price"] - j["stop"]).abs() <= TICK) & ((j["target_price"] - j["target"]).abs() <= TICK))
        par = same.mean() if len(j) else float("nan")
        extra = set(placed["day"]) - set(bt_days["day"])
        lines += ["## 2. Signal parity (engine re-run on the live days)",
                  f"- backtest signals: {len(j)}; placed live at the same levels: {par:.0%} (gate >= {GATE_PARITY:.0%}) -> "
                  f"{'OK' if par >= GATE_PARITY else 'CHECK: find the cause before scaling'}",
                  f"- live orders with no backtest signal: {len(extra)} {sorted(extra)[:10]}", ""]
        jj = closed.merge(bt_days, on="day", suffixes=("", "_bt"))
        if len(jj):
            diff = jj["net_r"] - jj["net_pnl_bt"] / preds["risk_usd"]
            lines += [f"- same-day net R, live minus backtest: mean {diff.mean():+.3f}R over {len(jj)} trades", ""]
    lines += ["## 3. Outcome vs pre-registered bands"] + [f"- {x}" for x in band_check(closed["net_r"].to_numpy(), preds)]
    lines += ["", f"Outcome is judged from {GATE_MIN_TRADES} trades. Below the 5th percentile of both windows after "
              f"{GATE_MIN_TRADES}+ trades = the backtest does not describe live trading; do not scale."]
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fills", default=str(FILLS))
    ap.add_argument("--decisions", default=str(DECISIONS))
    ap.add_argument("--backtest", action="store_true")
    a = ap.parse_args()
    if not pathlib.Path(a.fills).exists():
        print(f"no live data yet: {a.fills} missing. Run scripts/export_live_trades.py on the trading computer.")
        return 0
    fills, decisions = pd.read_csv(a.fills), pd.read_csv(a.decisions)
    preds = json.loads(PREDS.read_text())
    bt = backtest_days(sorted(placed_orders(decisions)["day"].unique())) if a.backtest else None
    text = report(fills, decisions, preds, bt)
    REPORT.write_text(text + "\n")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

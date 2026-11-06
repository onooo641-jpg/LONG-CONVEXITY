"""One-off: add the ``ambiguous`` column to rows logged before it existed.

    uv run python scripts/backfill_forward_ambiguous.py           # check only
    uv run python scripts/backfill_forward_ambiguous.py --write

The log is append-only, so this must not recompute anything already written.
It re-runs the same signals at the log's $500, and refuses unless every
existing column of every row comes back identical. Only then does it take
the engine's ``ambiguous`` flag for those same trades and add it.
"""

from __future__ import annotations

import argparse
import sys

import pandas as pd

from backtest.engine import BacktestConfig, simulate
from ict import data as D
from strategies.ltf_sweep import LTFSweepConfig, generate_orders

sys.path.insert(0, "scripts")
from forward_log import COLUMNS, DEFAULT_LOG, FORWARD_START, trade_rows  # noqa: E402


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    log = pd.read_csv(DEFAULT_LOG, dtype={"date": str})
    if "ambiguous" in log.columns:
        print("log already has ambiguous; nothing to do")
        return 0
    df1 = D.load("1m")
    bars = df1[df1.ts >= FORWARD_START].reset_index(drop=True)
    trades = simulate(generate_orders(bars, LTFSweepConfig(), one_per_day=True),
                      bars, BacktestConfig(risk_per_trade_usd=500.0))
    rows = trade_rows(trades)
    rows = rows[rows["date"] <= log["date"].max()].reset_index(drop=True)

    old = [c for c in COLUMNS if c != "ambiguous"]
    # Compare through the same CSV round trip the log went through.
    fresh = pd.read_csv(pd.io.common.StringIO(rows[old].to_csv(index=False)),
                        dtype={"date": str})
    if len(fresh) != len(log) or not fresh.equals(log[old]):
        diff = fresh.compare(log[old]) if len(fresh) == len(log) else None
        raise SystemExit(f"re-run does not reproduce the log ({len(fresh)} vs "
                         f"{len(log)} rows); refusing to backfill\n{diff}")

    log["ambiguous"] = rows["ambiguous"].astype(bool).to_numpy()
    print(f"{len(log)} rows reproduced exactly; ambiguous True on "
          f"{int(log['ambiguous'].sum())}")
    if args.write:
        log.to_csv(DEFAULT_LOG, index=False)
        print(f"wrote {DEFAULT_LOG}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Export the live account's fills for the comparison (run on the trading computer).

Reads the same TOPSTEPX_* environment variables as the bridge, calls ProjectX
Trade/search and writes data/live/fills.csv. Also copies the order decisions
(placed / blocked / skipped / errors / session starts) from the bridge journal,
which is git-ignored, into data/live/decisions.csv. No credentials are written.

    uv run python scripts/export_live_trades.py --start 2026-11-01
    git add data/live && git commit -m "live data" && git push
"""
from __future__ import annotations

import argparse
import pathlib

import pandas as pd

from bridge.config import Config
from bridge.journal import Journal
from bridge.topstepx import TopstepXBroker

OUT = pathlib.Path("data/live/fills.csv")
DECISIONS = pathlib.Path("data/live/decisions.csv")
KEEP = {"placed", "blocked", "skipped", "broker_error", "session_start"}
COLS = ["id", "accountId", "contractId", "creationTimestamp", "price", "profitAndLoss",
        "fees", "commissions", "side", "size", "voided", "orderId"]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", required=True, help="first day to export, e.g. 2026-11-01")
    ap.add_argument("--end", default=None)
    ap.add_argument("--out", default=str(OUT))
    a = ap.parse_args()
    cfg = Config.from_env(live=True)
    broker = TopstepXBroker(cfg)
    broker.authenticate()
    fills = pd.DataFrame(broker.trades(pd.Timestamp(a.start, tz="UTC"),
                                       pd.Timestamp(a.end, tz="UTC") if a.end else None))
    fills = fills.reindex(columns=COLS)
    pathlib.Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    fills.to_csv(a.out, index=False)
    print(f"wrote {len(fills)} fills to {a.out}")
    rows = [{k: v for k, v in r.items() if k != "broker"} for r in Journal().read() if r.get("event") in KEEP]
    pd.DataFrame(rows).to_csv(DECISIONS, index=False)
    print(f"wrote {len(rows)} journal decisions to {DECISIONS}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

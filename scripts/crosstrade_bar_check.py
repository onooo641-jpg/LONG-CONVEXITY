"""Is the connector's bar time right? Compare its 1-minute bars with Yahoo Finance's, at shifts of -2..+2 minutes.

    uv run python scripts/crosstrade_bar_check.py      (needs the same CrossTrade variables as the check step)

Yahoo (third party, ``MNQ=F``, front month) stamps a bar at its OPEN, which is what the connector's ``ts`` should
be. If the connector's close-to-open shift is right, shift 0 matches far better than any other. Read only.
"""

from __future__ import annotations

import json
import pathlib
import sys
import urllib.request

import pandas as pd

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from bridge.config import Config  # noqa: E402
from bridge.crosstrade import CrossTradeBroker  # noqa: E402

URL = "https://query1.finance.yahoo.com/v8/finance/chart/MNQ=F?interval=1m&range=2d"
COLS = ["open", "high", "low", "close"]


def yahoo() -> pd.DataFrame:
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        res = json.loads(resp.read().decode())["chart"]["result"][0]
    quote = res["indicators"]["quote"][0]
    frame = pd.DataFrame({c: quote[c] for c in COLS})
    frame["ts"] = pd.to_datetime(res["timestamp"], unit="s", utc=True)
    return frame.dropna()


def main() -> int:
    now = pd.Timestamp.now(tz="UTC")
    ours = CrossTradeBroker(Config.from_env()).retrieve_bars(now - pd.Timedelta(days=3), now)
    ref = yahoo()
    # Yahoo lags and its newest rows are partial: leave the last 20 minutes out.
    ours = ours[ours["ts"] < now - pd.Timedelta(minutes=20)]
    print(f"connector bars {len(ours)}, yahoo bars {len(ref)}, run at {now:%Y-%m-%d %H:%M}Z")
    for shift in range(-2, 3):
        moved = ref.assign(ts=ref["ts"] + pd.Timedelta(minutes=shift))
        both = ours.merge(moved, on="ts", suffixes=("", "_y"))
        if both.empty:
            print(f"shift {shift:+d}: no common minutes")
            continue
        diff = pd.concat([(both[c] - both[f"{c}_y"]).abs() for c in COLS], axis=1)
        diff.columns = COLS
        print(f"shift {shift:+d} min: {len(both)} minutes, all four prices within 1 point "
              f"{(diff.max(axis=1) <= 1.0).mean():6.1%}, median |difference| "
              + " ".join(f"{c} {diff[c].median():.2f}" for c in COLS))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

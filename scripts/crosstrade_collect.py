"""After a CrossTrade practice run: copy that day's journal rows into docs/jx_runs and log one dated line in NOTES_JX.

    uv run python scripts/crosstrade_collect.py --step dryrun --exit-code 0            (today, New York date)
    uv run python scripts/crosstrade_collect.py --step dryrun --exit-code 0 --date 2026-12-01

Picks the rows of data/journal_crosstrade_test.jsonl whose UTC timestamp falls in that New York trading day
(18:00 ET the evening before to 18:00 ET), writes docs/jx_runs/crosstrade_test_journal_<YYYYMMDD>.jsonl, and appends
"- <date> <step>: PASS|FAIL ..." under the CrossTrade practice-test heading in docs/NOTES_JX.md.

Refuses to write anything (exit 2) if a row looks like it holds a secret: the value of CROSSTRADE_API_KEY when it is
set in this process, a "Bearer " header, or an api_key / secret field. Journals should never hold one; this checks.
PASS = the engine exited 0, no row is an error event, and (except for the check step) the day has rows.
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import re
import sys
from collections import Counter

import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
JOURNAL = ROOT / "data" / "journal_crosstrade_test.jsonl"
NOTES = ROOT / "docs" / "NOTES_JX.md"
HEADING = "## 2026-12 — CrossTrade practice test: run log (written by `scripts/crosstrade_collect.py`)"
NY = "America/New_York"

#: Journal events that mean something went wrong (from bridge/live.py, bridge/crosstrade.py, bridge/roundtrip.py).
ERROR_EVENTS = {
    "tick_error", "stale_feed", "roundtrip_failed", "roundtrip_query_failed", "protect_failed",
    "protect_gave_up_flattened", "protect_gave_up_flatten_failed", "open_orders_failed", "open_orders_unproven",
    "flatten_failed", "flatten_check_failed", "entry_watch_read_failed", "entry_watch_error", "done_check_failed",
    "cancel_failed", "empty_unproven", "session_end_unproven", "exit_alert",
}
_SECRETISH = re.compile(r"bearer\s+\S|\"(api_?key|secret|password|token)\"\s*:", re.I)


def trading_day(date: str | None) -> tuple[pd.Timestamp, pd.Timestamp, str]:
    """(start UTC, end UTC, YYYYMMDD) of the New York trading day: 18:00 ET the evening before to 18:00 ET."""
    day = pd.Timestamp(date) if date else pd.Timestamp.now(tz=NY).tz_localize(None).normalize()
    if not date and pd.Timestamp.now(tz=NY).hour >= 18:
        day += pd.Timedelta(days=1)
    end = (day.normalize() + pd.Timedelta(hours=18)).tz_localize(NY)
    start = end - pd.Timedelta(days=1)
    return start.tz_convert("UTC"), end.tz_convert("UTC"), day.strftime("%Y%m%d")


def secret_hits(lines: list[str], key: str | None) -> list[int]:
    """Line numbers (1-based) that look like they carry a credential."""
    hits = []
    for i, line in enumerate(lines, 1):
        if (key and len(key) >= 8 and key in line) or _SECRETISH.search(line):
            hits.append(i)
    return hits


def select(lines: list[str], start: pd.Timestamp, end: pd.Timestamp) -> list[str]:
    out = []
    for line in lines:
        try:
            ts = pd.Timestamp(json.loads(line)["ts"])
        except (ValueError, KeyError, TypeError):
            continue
        if start <= ts < end:
            out.append(line)
    return out


def summary(rows: list[str], step: str, exit_code: int, ymd: str) -> tuple[bool, str]:
    events = Counter(json.loads(r).get("event") for r in rows)
    errors = {e: n for e, n in events.items() if e in ERROR_EVENTS}
    # The check step writes no journal rows (it only prints), so it passes on its exit code alone.
    ok = exit_code == 0 and not errors and (bool(rows) or step == "check")
    detail = ", ".join(f"{e} x{n}" for e, n in sorted(events.items())) or "no journal rows"
    err = ("; errors: " + ", ".join(f"{e} x{n}" for e, n in sorted(errors.items()))) if errors else ""
    date = f"{ymd[:4]}-{ymd[4:6]}-{ymd[6:]}"
    line = (f"- {date} {step}: **{'PASS' if ok else 'FAIL'}** (exit {exit_code}; {len(rows)} rows: {detail}{err}). "
            f"Journal: `docs/jx_runs/crosstrade_test_journal_{ymd}.jsonl`.")
    return ok, line


def append_note(line: str, notes: pathlib.Path = NOTES) -> None:
    text = notes.read_text(encoding="utf-8")
    if HEADING not in text:
        text = text.rstrip("\n") + f"\n\n{HEADING}\n"
    # Each line goes at the end of the heading's section (the heading is the last section unless one was added later).
    head = text.index(HEADING)
    nxt = text.find("\n## ", head + len(HEADING))
    if nxt == -1:
        text = text.rstrip("\n") + "\n" + line + "\n"
    else:
        text = text[:nxt].rstrip("\n") + "\n" + line + "\n" + text[nxt:]
    notes.write_text(text, encoding="utf-8")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--step", required=True, choices=["check", "roundtrip", "dryrun"])
    ap.add_argument("--exit-code", type=int, required=True)
    ap.add_argument("--date", default=None, help="New York trading date, YYYY-MM-DD (default: today)")
    ap.add_argument("--journal", default=str(JOURNAL))
    args = ap.parse_args(argv)

    start, end, ymd = trading_day(args.date)
    path = pathlib.Path(args.journal)
    lines = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
    rows = select([l for l in lines if l.strip()], start, end)
    hits = secret_hits(rows, os.environ.get("CROSSTRADE_API_KEY"))
    if hits:
        print(f"REFUSED: {len(hits)} journal row(s) look like they hold a secret (rows {hits[:10]}). "
              "Nothing copied; tell Claude.", file=sys.stderr)
        return 2
    out = ROOT / "docs" / "jx_runs" / f"crosstrade_test_journal_{ymd}.jsonl"
    out.write_text("".join(r + "\n" for r in rows), encoding="utf-8")
    ok, line = summary(rows, args.step, args.exit_code, ymd)
    append_note(line)
    print(line)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

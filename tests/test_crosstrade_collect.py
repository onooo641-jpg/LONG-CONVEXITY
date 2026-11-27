"""scripts/crosstrade_collect.py: picks one New York trading day, refuses secrets, logs PASS/FAIL."""
import importlib.util
import json
import pathlib

import pandas as pd

_spec = importlib.util.spec_from_file_location(
    "crosstrade_collect", pathlib.Path(__file__).resolve().parents[1] / "scripts" / "crosstrade_collect.py")
cc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cc)


def _row(ts, event, **kw):
    return json.dumps({"ts": ts, "event": event, **kw}, sort_keys=True)


def test_trading_day_runs_18_to_18_new_york():
    start, end, ymd = cc.trading_day("2026-12-01")
    assert ymd == "20261201"
    assert start == pd.Timestamp("2026-11-30 23:00", tz="UTC")   # 18:00 EST
    assert end == pd.Timestamp("2026-12-01 23:00", tz="UTC")


def test_select_and_summary():
    lines = [_row("2026-11-30T22:59:59+00:00", "skipped"),           # previous trading day
             _row("2026-12-01T14:26:00+00:00", "session_done"),
             _row("2026-12-01T15:00:00+00:00", "tick_error", error="HTTP 408"),
             "not json"]
    start, end, ymd = cc.trading_day("2026-12-01")
    rows = cc.select(lines, start, end)
    assert len(rows) == 2
    ok, line = cc.summary(rows, "dryrun", 0, ymd)
    assert not ok and "**FAIL**" in line and "errors: tick_error x1" in line
    ok, line = cc.summary(rows[:1], "dryrun", 0, ymd)
    assert ok and line.startswith("- 2026-12-01 dryrun: **PASS** (exit 0; 1 rows")
    assert not cc.summary(rows[:1], "dryrun", 1, ymd)[0]
    assert not cc.summary([], "dryrun", 0, ymd)[0]                    # no rows is not a pass
    assert cc.summary([], "check", 0, ymd)[0]                         # ...except for the check step


def test_secret_scan():
    key = "ct_live_0123456789abcdef"
    rows = [_row("2026-12-01T14:26:00+00:00", "x", note="fine"),
            _row("2026-12-01T14:27:00+00:00", "x", note=f"got {key}"),
            _row("2026-12-01T14:28:00+00:00", "x", hdr="Bearer abc"),
            _row("2026-12-01T14:29:00+00:00", "x", api_key="abc")]
    assert cc.secret_hits(rows, key) == [2, 3, 4]
    assert cc.secret_hits(rows[:1], None) == []


def test_append_note_keeps_one_heading(tmp_path):
    notes = tmp_path / "NOTES.md"
    notes.write_text("# Notes\n\n## older\ntext\n", encoding="utf-8")
    cc.append_note("- a", notes)
    cc.append_note("- b", notes)
    text = notes.read_text(encoding="utf-8")
    assert text.count(cc.HEADING) == 1
    assert text.endswith(f"{cc.HEADING}\n- a\n- b\n")

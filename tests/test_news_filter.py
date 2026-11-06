"""Rule F2 (docs/or5_retest_spec.md): no entries on a tier-1 release or FOMC
day. Ported into strategies/ltf_sweep.py as an opt-in config flag -- see
docs/NOTES_JX.md check 6 for what turning it on costs over 11 years.
"""

from __future__ import annotations

import datetime

import pytest

from ict import data as D
from strategies.ltf_sweep import LTFSweepConfig, generate_orders, load_blackout_dates

pytestmark = pytest.mark.skipif(
    not (D.PROCESSED_DIR / "nq_1m.parquet").exists(),
    reason="run `uv run python scripts/ingest.py` first",
)


def test_a_known_fomc_day_is_in_the_calendar():
    assert datetime.date(2026, 1, 28) in load_blackout_dates()


def test_off_by_default():
    assert LTFSweepConfig().news_filter is False


def test_the_filter_removes_no_entries_from_a_window_with_no_blackout_days():
    df = D.load("1m")
    # A week with no tier-1 release or FOMC day in it.
    bars = df[(df.ts >= "2026-02-02") & (df.ts < "2026-02-06")].reset_index(drop=True)
    plain = generate_orders(bars, LTFSweepConfig(news_filter=False))
    filtered = generate_orders(bars, LTFSweepConfig(news_filter=True))
    assert len(filtered) == len(plain)


def test_the_filter_drops_orders_on_a_blackout_day():
    df = D.load("1m")
    # 2026-01-28 is an FOMC day inside this window.
    bars = df[(df.ts >= "2026-01-26") & (df.ts < "2026-01-30")].reset_index(drop=True)
    filtered = generate_orders(bars, LTFSweepConfig(news_filter=True))
    assert datetime.date(2026, 1, 28) not in set(filtered["trading_date"])

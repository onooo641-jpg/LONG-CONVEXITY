"""Proof that the empty-bar-array ambiguity (ARTIFACT_CLASSES.md class 3) is
actually wired as a hard preflight failure, not just a line in a checklist.

A wrong ``contract_id`` or a wrong ``BRIDGE_LIVE_DATA`` both come back from
the broker as an empty array, same as a legitimate "no bars yet." Without a
test pinning this, a future refactor of ``bar_feed_checks`` could turn the
hard FAIL back into a quiet pass-through and nothing here would catch it.
"""

from __future__ import annotations

import pandas as pd
import pytest

from bridge.config import Config
from bridge.preflight import bar_feed_checks


def cfg(**over) -> Config:
    base = dict(
        username="u", api_key="k", base_url="http://example.invalid", account_id=1,
        contract_id="CON.F.US.MNQ.Z26", tick_size=0.25, point_value=2.0,
        webhook_secret="s3cret-long-enough", live=False,
        live_data=False, cutoff_minute=15 * 60 + 30, flat_minute=16 * 60, max_bar_age_s=150.0,
        preset="Topstep 50K",
        account_start=50000.0, profit_target=3000.0, max_loss_limit=2000.0,
        daily_loss_limit=1000.0, max_contracts=50, safety_mult=1.5,
        use_guard=True, scaling_plan=False, consistency=0.55,
    )
    base.update(over)
    return Config(**base)


class _FakeBroker:
    def __init__(self, bars: pd.DataFrame):
        self._bars = bars

    def retrieve_bars(self, start, end, *, limit: int = 2000):
        return self._bars


def test_an_empty_bar_array_is_a_hard_preflight_failure_not_a_quiet_zero():
    """This is the exact ambiguity class 3 names: a wrong contract id and a
    wrong live-data flag both look like "no bars yet." Preflight must refuse
    to call that a pass.
    """
    broker = _FakeBroker(pd.DataFrame(columns=["ts"]))
    checks = bar_feed_checks(cfg(), broker)

    assert len(checks) == 1
    assert checks[0].name == "bar feed"
    assert checks[0].ok is False
    assert "CON.F.US.MNQ.Z26" in checks[0].detail
    assert "wrong contract id" in checks[0].detail
    assert "BRIDGE_LIVE_DATA" in checks[0].detail


def test_a_broker_exception_is_also_a_hard_failure_not_a_silent_empty_result():
    class _RaisingBroker:
        def retrieve_bars(self, start, end, *, limit: int = 2000):
            raise RuntimeError("connection reset")

    checks = bar_feed_checks(cfg(), _RaisingBroker())
    assert len(checks) == 1
    assert checks[0].ok is False
    assert "connection reset" in checks[0].detail


def test_fresh_bars_pass_the_bar_feed_and_timestamp_checks():
    now = pd.Timestamp.now(tz="UTC")
    bars = pd.DataFrame({
        "ts": [now - pd.Timedelta(minutes=3), now - pd.Timedelta(minutes=2)],
        "open": [100.0, 100.5], "high": [100.5, 101.0],
        "low": [99.5, 100.0], "close": [100.5, 100.8], "volume": [10, 12],
    })
    broker = _FakeBroker(bars)
    checks = bar_feed_checks(cfg(max_bar_age_s=300.0), broker)

    by_name = {c.name: c for c in checks}
    assert by_name["bar feed"].ok is True
    assert by_name["bar timestamps"].ok is True


def test_a_bar_stamped_at_its_close_rather_than_its_open_fails_the_age_check():
    """A feed that stamps the bar's close time rather than its open time looks
    healthy (non-empty, recent) but shifts every signal one bar out of place.
    """
    now = pd.Timestamp.now(tz="UTC")
    bars = pd.DataFrame({
        "ts": [now - pd.Timedelta(seconds=30)],
        "open": [100.0], "high": [100.5], "low": [99.5], "close": [100.2],
        "volume": [5],
    })
    broker = _FakeBroker(bars)
    checks = bar_feed_checks(cfg(), broker)

    by_name = {c.name: c for c in checks}
    assert by_name["bar timestamps"].ok is False
    assert "stamps at the close" in by_name["bar timestamps"].detail

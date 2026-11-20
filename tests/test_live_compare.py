import json
import pathlib

import pandas as pd
import pytest

from scripts.live_compare import band_check, execution, placed_orders, report, round_trips


def _fills():
    # Day 1: long 4 @ 100.00, stopped at 94.75 (stop 95.00 -> 1 tick slip). Day 2: short 2 @ 200, target 190.
    return pd.DataFrame([
        {"creationTimestamp": "2026-11-23T15:00:00Z", "price": 100.0, "profitAndLoss": None, "fees": 0.5, "commissions": 0.0, "side": 0, "size": 4, "voided": False},
        {"creationTimestamp": "2026-11-23T15:30:00Z", "price": 94.75, "profitAndLoss": -42.0, "fees": 0.5, "commissions": 0.0, "side": 1, "size": 4, "voided": False},
        {"creationTimestamp": "2026-11-24T15:00:00Z", "price": 200.0, "profitAndLoss": None, "fees": 0.25, "commissions": 0.0, "side": 1, "size": 2, "voided": False},
        {"creationTimestamp": "2026-11-24T16:00:00Z", "price": 190.0, "profitAndLoss": 40.0, "fees": 0.25, "commissions": 0.0, "side": 0, "size": 2, "voided": False},
        {"creationTimestamp": "2026-11-24T16:05:00Z", "price": 1.0, "profitAndLoss": 999.0, "fees": 9, "commissions": 0.0, "side": 0, "size": 1, "voided": True},
    ])


def _decisions():
    return pd.DataFrame([
        {"event": "session_start", "day": None, "side": None, "qty": None, "entry": None, "stop": None, "target": None, "planned_risk": None, "dry_run": None},
        {"event": "placed", "day": "2026-11-23", "side": "buy", "qty": 4, "entry": 100.0, "stop": 95.0, "target": 105.0, "planned_risk": 42.0, "dry_run": False},
        {"event": "placed", "day": "2026-11-24", "side": "sell", "qty": 2, "entry": 200.0, "stop": 210.0, "target": 190.0, "planned_risk": 40.0, "dry_run": False},
        {"event": "placed", "day": "2026-11-25", "side": "buy", "qty": 3, "entry": 300.0, "stop": 290.0, "target": 310.0, "planned_risk": 60.0, "dry_run": False},
    ])


def test_round_trips_drop_voided_and_pair_by_day():
    t = round_trips(_fills())
    assert list(t.day) == ["2026-11-23", "2026-11-24"]
    assert t.loc[0, "direction"] == 1 and t.loc[1, "direction"] == -1
    assert t.loc[1, "gross_pnl"] == 40.0                      # voided fill ignored


def test_execution_measures_slippage_and_unfilled_orders():
    m = execution(round_trips(_fills()), placed_orders(_decisions()))
    d1 = m[m.day == "2026-11-23"].iloc[0]
    assert d1.exit_kind == "stop" and d1.exit_slip_ticks == pytest.approx(1.0)
    assert d1.entry_slip_ticks == pytest.approx(0.0)
    d2 = m[m.day == "2026-11-24"].iloc[0]
    assert d2.exit_kind == "target" and d2.exit_slip_ticks == pytest.approx(0.0)
    assert not m[m.day == "2026-11-25"].iloc[0].filled
    assert d1.net_r == pytest.approx((-42.0 - 1.0) / 42.0)


def test_band_check_says_too_early_below_the_first_band():
    preds = json.loads(pathlib.Path("docs/live_predictions.json").read_text())
    assert "too early" in band_check(pd.Series([1.0] * 5).to_numpy(), preds)[1]


def test_report_runs_end_to_end():
    preds = json.loads(pathlib.Path("docs/live_predictions.json").read_text())
    text = report(_fills(), _decisions(), preds)
    assert "Execution" in text and "Outcome" in text

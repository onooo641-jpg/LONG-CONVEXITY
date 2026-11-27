"""Multi-firm go-live: engine-scoped hedge claims, firm presets, static and locked loss-limit floors, CrossTrade config."""
import pandas as pd
import pytest

from bridge.config import FIRM_PRESETS, PRESETS, Config
from bridge.guards import AccountState
from bridge.hedge import HedgeRegistry

T0 = pd.Timestamp("2026-11-23 15:00", tz="UTC")
FLAT = pd.Timestamp("2026-11-23 21:00", tz="UTC")


def test_two_accounts_on_the_same_market_cannot_hold_opposite_directions(tmp_path):
    reg = HedgeRegistry(tmp_path / "hedge.json")
    assert reg.claim("NQ", 1, "a", T0, FLAT, engine="topstepx:1:NQ") is None
    conflict = reg.claim("NQ", -1, "b", T0, FLAT, engine="crosstrade:LUCID1:NQ")
    assert conflict is not None and conflict["engine"] == "topstepx:1:NQ"
    assert reg.claim("NQ", 1, "c", T0, FLAT, engine="crosstrade:LUCID1:NQ") is None  # same direction: fine


def test_one_engine_finishing_never_releases_another_engines_claims(tmp_path):
    reg = HedgeRegistry(tmp_path / "hedge.json")
    reg.claim("NQ", 1, "a", T0, FLAT, engine="topstepx:1:NQ")
    reg.claim("NQ", 1, "b", T0, FLAT, engine="crosstrade:DT150:NQ")
    reg.release("NQ", engine="topstepx:1:NQ")
    left = reg.claims(T0)
    assert [r["engine"] for r in left] == ["crosstrade:DT150:NQ"]
    assert reg.claim("ES", -1, "c", T0, FLAT, engine="topstepx:2:ES") is not None  # the DayTraders NQ long still blocks


def test_old_rows_without_an_engine_still_read_as_their_market(tmp_path):
    import json
    p = tmp_path / "hedge.json"
    p.write_text(json.dumps([{"market": "ES", "direction": 1, "key": "k", "claimed_at": T0.isoformat(),
                              "expires_at": FLAT.isoformat()}]))
    assert HedgeRegistry(p).claim("NQ", -1, "n", T0, FLAT) is not None


def test_firm_presets_stay_out_of_the_pine_mirrored_table():
    assert not set(FIRM_PRESETS) & set(PRESETS)


def _cfg(**kw):
    base = dict(username="", api_key="x", base_url="", account_id=None, contract_id="", tick_size=0.25, point_value=2.0,
                webhook_secret="", live=False, live_data=False, cutoff_minute=930, flat_minute=960, max_bar_age_s=150.0,
                preset="t", account_start=100000.0, profit_target=5750.0, max_loss_limit=1500.0, daily_loss_limit=1e9,
                max_contracts=80, safety_mult=1.5, use_guard=True, scaling_plan=False, consistency=0.5)
    base.update(kw)
    return Config(**base)


def test_a_static_floor_never_moves():
    cfg = _cfg(floor_mode="static")
    st = AccountState()
    st.roll_day("d1", cfg)
    st.realized = 3000.0
    st.roll_day("d2", cfg)
    assert st.mll_floor == 100000.0 - 1500.0


def test_an_eod_floor_trails_then_locks_at_start_plus_lock_level():
    cfg = _cfg(account_start=50000.0, max_loss_limit=2000.0, floor_mode="eod", lock_at=2100.0, lock_level=100.0)
    st = AccountState()
    st.roll_day("d1", cfg)
    st.realized = 1000.0
    st.roll_day("d2", cfg)
    assert st.mll_floor == 49000.0                     # trailing
    st.realized = 3000.0
    st.roll_day("d3", cfg)
    assert st.mll_floor == 50100.0                     # locked at start + $100
    st.realized = 5000.0
    st.roll_day("d4", cfg)
    assert st.mll_floor == 50100.0                     # never trails past the lock


def test_crosstrade_config_reads_only_its_own_secret(monkeypatch):
    for k in ("TOPSTEPX_USERNAME", "TOPSTEPX_API_KEY", "TOPSTEPX_ACCOUNT_ID", "BRIDGE_CONTRACT_ID", "BRIDGE_MARKET"):
        monkeypatch.delenv(k, raising=False)
    monkeypatch.setenv("BRIDGE_BROKER", "crosstrade")
    monkeypatch.setenv("BRIDGE_PRESET", "DayTraders 150K Static")
    monkeypatch.setenv("CROSSTRADE_API_KEY", "secret")
    monkeypatch.setenv("CROSSTRADE_ACCOUNT", "DT150-1")
    monkeypatch.setenv("CROSSTRADE_INSTRUMENT", "MNQ 12-26")
    monkeypatch.setenv("BRIDGE_ACCOUNT_START", "150000")
    cfg = Config.from_env()
    assert (cfg.broker, cfg.account_name, cfg.instrument, cfg.floor_mode) == ("crosstrade", "DT150-1", "MNQ 12-26", "static")
    assert (cfg.profit_target, cfg.max_loss_limit, cfg.max_contracts) == (6750.0, 1750.0, 80)
    assert cfg.engine_id == "crosstrade:DT150-1:NQ"
    monkeypatch.delenv("CROSSTRADE_API_KEY")
    with pytest.raises(RuntimeError):
        Config.from_env()


def test_topstep_defaults_are_unchanged(monkeypatch):
    for k in ("BRIDGE_BROKER", "BRIDGE_PRESET", "BRIDGE_MARKET", "BRIDGE_CONTRACT_ID"):
        monkeypatch.delenv(k, raising=False)
    monkeypatch.setenv("TOPSTEPX_USERNAME", "u")
    monkeypatch.setenv("TOPSTEPX_API_KEY", "k")
    monkeypatch.setenv("TOPSTEPX_ACCOUNT_ID", "7")
    cfg = Config.from_env()
    assert (cfg.broker, cfg.floor_mode, cfg.lock_at, cfg.contract_id, cfg.engine_id) == \
        ("topstepx", "eod", None, "CON.F.US.MNQ.Z26", "topstepx:7:NQ")

import json

import pandas as pd
import pytest

from bridge.config import MARKETS, Config
from bridge.hedge import HedgeRegistry, HedgeRegistryError
from bridge.topstepx import snap_entry

T0 = pd.Timestamp("2026-11-23 15:00", tz="UTC")
FLAT = pd.Timestamp("2026-11-23 21:00", tz="UTC")


@pytest.mark.parametrize("price,side,tick,want", [
    (1930.375, "buy", 0.25, 1930.25), (1930.375, "sell", 0.25, 1930.5),
    (1930.25, "buy", 0.25, 1930.25), (1930.25, "sell", 0.25, 1930.25),
    (44001.5, "buy", 1.0, 44001.0), (44001.5, "sell", 1.0, 44002.0), (44001.0, "sell", 1.0, 44001.0),
])
def test_snap_entry_rounds_buys_down_and_sells_up(price, side, tick, want):
    assert snap_entry(price, side, tick) == want


def test_snap_matches_the_backtest_fill_condition():
    # Backtest: a buy limit at 1930.375 fills iff low <= 1930.375. On a 0.25 grid,
    # lows are multiples of 0.25, so that is iff low <= 1930.25 == the snapped price.
    for low in (1930.0, 1930.25, 1930.5):
        assert (low <= 1930.375) == (low <= snap_entry(1930.375, "buy", 0.25))


def test_registry_blocks_opposite_directions_across_markets(tmp_path):
    reg = HedgeRegistry(tmp_path / "hedge.json")
    assert reg.claim("NQ", 1, "k1", T0, FLAT) is None
    assert reg.claim("ES", 1, "k2", T0, FLAT) is None            # same direction: fine
    conflict = reg.claim("YM", -1, "k3", T0, FLAT)               # opposite: blocked
    assert conflict is not None and conflict["direction"] == 1
    assert {c["market"] for c in reg.claims(T0)} == {"NQ", "ES"}


def test_same_market_never_conflicts_with_itself(tmp_path):
    reg = HedgeRegistry(tmp_path / "hedge.json")
    assert reg.claim("NQ", 1, "a", T0, FLAT) is None
    assert reg.claim("NQ", -1, "b", T0, FLAT) is None


def test_release_and_expiry_free_the_direction(tmp_path):
    reg = HedgeRegistry(tmp_path / "hedge.json")
    reg.claim("NQ", 1, "k1", T0, FLAT)
    reg.release("NQ")
    assert reg.claim("ES", -1, "k2", T0, FLAT) is None
    # ES's claim expires at FLAT; after it, YM may go the other way
    assert reg.claim("YM", 1, "k3", FLAT + pd.Timedelta(minutes=1), FLAT + pd.Timedelta(hours=1)) is None


def test_unreadable_registry_refuses_rather_than_reads_as_flat(tmp_path):
    p = tmp_path / "hedge.json"
    p.write_text("{not json")
    with pytest.raises(HedgeRegistryError):
        HedgeRegistry(p).claim("NQ", 1, "k", T0, FLAT)


def test_market_presets_and_defaults(monkeypatch):
    for k in ("BRIDGE_MARKET", "BRIDGE_CONTRACT_ID", "BRIDGE_TICK_SIZE", "BRIDGE_POINT_VALUE",
              "BRIDGE_HEDGE_REGISTRY"):
        monkeypatch.delenv(k, raising=False)
    monkeypatch.setenv("TOPSTEPX_USERNAME", "u")
    monkeypatch.setenv("TOPSTEPX_API_KEY", "k")
    nq = Config.from_env()
    assert (nq.market, nq.contract_id, nq.tick_size, nq.point_value, nq.hedge_registry) == \
        ("NQ", "CON.F.US.MNQ.Z26", 0.25, 2.0, None)          # unchanged default setup
    monkeypatch.setenv("BRIDGE_MARKET", "YM")
    with pytest.raises(RuntimeError):                         # YM needs an explicit contract id
        Config.from_env()
    monkeypatch.setenv("BRIDGE_CONTRACT_ID", "CON.F.US.MYM.Z26")
    ym = Config.from_env()
    assert (ym.tick_size, ym.point_value) == MARKETS["YM"]


def test_engine_skips_an_entry_opposite_to_another_market(tmp_path, monkeypatch):
    from types import SimpleNamespace

    from bridge.journal import Journal
    from bridge.live import LiveEngine
    from bridge.topstepx import DryRunBroker

    for k in ("BRIDGE_MARKET", "BRIDGE_CONTRACT_ID"):
        monkeypatch.delenv(k, raising=False)
    monkeypatch.setenv("TOPSTEPX_USERNAME", "u")
    monkeypatch.setenv("TOPSTEPX_API_KEY", "k")
    monkeypatch.setenv("TOPSTEPX_ACCOUNT_ID", "1")
    cfg = Config.from_env()
    reg = HedgeRegistry(tmp_path / "hedge.json")
    reg.claim("ES", 1, "es-long", T0, FLAT)                   # ES is long
    eng = LiveEngine(cfg=cfg, broker=DryRunBroker(cfg), journal=Journal(tmp_path / "j.jsonl"),
                     risk_usd=900, hedge=reg)
    row = SimpleNamespace(direction=-1, entry_price=20000.0, stop_price=20020.0,
                          target_price=19980.0, trading_date="2026-11-23")
    d = eng.send(row, "nq-short", T0)                         # NQ short would hedge it
    assert d.status == "blocked" and eng.broker.sent == []
    rows = [json.loads(x) for x in (tmp_path / "j.jsonl").read_text().splitlines()]
    assert rows[-1]["event"] == "blocked_hedge"
    d2 = eng.send(SimpleNamespace(direction=1, entry_price=20000.0, stop_price=19980.0,
                                  target_price=20020.0, trading_date="2026-11-23"), "nq-long", T0)
    assert d2.ok and len(eng.broker.sent) == 1                # same direction is allowed

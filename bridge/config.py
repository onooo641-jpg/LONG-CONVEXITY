"""Bridge configuration. Secrets come from the environment, never from a file.

An API key in a config file ends up in git, in a backup, or in a screenshot.
The one in this repo's history already had to be rotated twice. Everything
secret is read from the environment and nothing here ever writes one back out.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

#: Account rules, mirroring the preset table in the Pine scripts.
#: (profit target, maximum loss limit, daily loss limit, max micro contracts)
#: tests/test_bridge.py asserts these stay identical to the Pine arrays: two
#: implementations of one rule are only safe while they agree.
PRESETS: dict[str, tuple[float, float, float, int]] = {
    "Topstep 50K":   (3000.0, 2000.0, 1000.0, 50),
    "Topstep 100K":  (6000.0, 3000.0, 2000.0, 100),
    "Topstep 150K":  (9000.0, 4500.0, 3000.0, 150),
    # Apex has no daily loss limit; the cell is a number too large to trigger
    # rather than zero, which would block every trade.
    "Apex 50K EOD":  (3000.0, 2500.0, 1e9, 20),
    "Apex 100K EOD": (6000.0, 3000.0, 1e9, 40),
}

#: Best single day, as a share of the profit target, before the target starts
#: rising: ``adjusted = best_day / consistency``. Not a failure -- it moves the
#: goalposts. Deliberately NOT part of PRESETS: that tuple is the set of numbers
#: that exist in the Pine guard too, and tests/test_bridge.py reads them back out
#: of the Pine source to prove the two agree. A value only one side has would
#: weaken exactly the thing that test is for.
#:
#: Topstep's own figure, read off the dashboard 2026-09-13. Apex is None because
#: it has not been checked -- the same reason its rows carry a warning above.
CONSISTENCY: dict[str, float | None] = {
    "Topstep 50K": 0.55, "Topstep 100K": 0.55, "Topstep 150K": 0.55,
    "Apex 50K EOD": None, "Apex 100K EOD": None,
}

#: Firms other than Topstep (prop search 3, docs/PREREG_PROP_SEARCH3_20261126.md). Kept OUT of PRESETS on
#: purpose: PRESETS must stay identical to the Pine preset table (tests/test_bridge.py). Each row:
#: (profit target, max loss limit, daily loss limit, max micros, consistency, floor mode, lock_at, lock_level)
#:   floor mode "eod"    -- floor trails the end-of-day closed balance (Topstep's model)
#:              "static" -- floor never moves (DayTraders Static; Topstep Labs static)
#:   lock_at / lock_level -- once the closed profit reaches lock_at, the floor stops at start + lock_level
#: A daily loss limit the firm does not have is 1e9 (never triggers), as for Apex above.
#: Sources: Lucid support pages (EOD; unrealized P&L ignored; LucidFlex 40% consistency, DLL $1,200 when on),
#: DayTraders help "Static evaluation at a glance" (Oct 2026), Topstep Labs page (2026-11-26).
FIRM_PRESETS: dict[str, tuple[float, float, float, int, float | None, str, float | None, float | None]] = {
    "LucidFlex 50K":          (3000.0, 2000.0, 1200.0, 40, 0.40, "eod", 2100.0, 100.0),
    "LucidDaily 50K":         (3000.0, 2000.0, 1e9, 40, 0.50, "eod", 2100.0, 100.0),
    "DayTraders 100K Static": (5750.0, 1500.0, 1e9, 80, 0.50, "static", None, None),
    "DayTraders 150K Static": (6750.0, 1750.0, 1e9, 80, 0.50, "static", None, None),
    "Topstep $3K Challenge":  (3000.0, 1000.0, 1e9, 10, None, "static", None, None),
}

#: Brokers the engine can talk to. "topstepx" is the ProjectX Gateway (Topstep). "crosstrade" drives
#: NinjaTrader 8 through the CrossTrade NT8 Add-On, which is how Lucid (CrossTrade) and DayTraders /
#: FFN (Rithmic accounts inside NinjaTrader) are reached without a custom Rithmic client.
BROKERS = ("topstepx", "crosstrade")

#: Micro contracts the strategy may trade, as (tick size, $ per point). NQ is the
#: default and keeps its old contract id default; ES and YM must name their
#: contract id explicitly (BRIDGE_CONTRACT_ID) because the TopstepX id format for
#: them has not been verified -- look it up with `python -m bridge.live --find-contract MES`.
MARKETS: dict[str, tuple[float, float]] = {
    "NQ": (0.25, 2.0),    # MNQ
    "ES": (0.25, 5.0),    # MES
    "YM": (1.0, 0.5),     # MYM
}

MISSING = object()


def _env(name: str, default=MISSING, cast=str):
    raw = os.environ.get(name)
    if raw is None or raw == "":
        if default is MISSING:
            raise RuntimeError(
                f"{name} is not set. The bridge reads all configuration from the "
                "environment; see bridge/README.md."
            )
        return default
    return cast(raw)


@dataclass(frozen=True)
class Config:
    """Everything the bridge needs. Built once, at startup, from the environment."""

    username: str
    api_key: str
    base_url: str
    account_id: int | None
    contract_id: str
    tick_size: float
    point_value: float
    webhook_secret: str
    live: bool

    live_data: bool
    cutoff_minute: int
    flat_minute: int
    max_bar_age_s: float

    preset: str
    account_start: float
    profit_target: float
    max_loss_limit: float
    daily_loss_limit: float
    max_contracts: int
    safety_mult: float
    use_guard: bool
    scaling_plan: bool
    consistency: float | None
    #: Which market this engine trades (MARKETS key). Defaults keep the NQ setup unchanged.
    market: str = "NQ"
    #: Shared file that every engine on this computer checks before entering, so no
    #: two markets ever hold opposite directions at once (the firms' cross-account
    #: hedging ban). None = off, which is the right setting for a single market.
    hedge_registry: str | None = None
    #: Which broker connector (BROKERS). Topstep stays the default.
    broker: str = "topstepx"
    #: Broker-side account name for connectors that address accounts by name (CrossTrade / NinjaTrader).
    account_name: str | None = None
    #: Broker-side instrument name (CrossTrade / NinjaTrader native, e.g. "MNQ 12-26").
    instrument: str | None = None
    #: How the loss-limit floor moves (see FIRM_PRESETS). Topstep presets keep "eod" with no lock.
    floor_mode: str = "eod"
    lock_at: float | None = None
    lock_level: float | None = None

    @property
    def engine_id(self) -> str:
        """Unique per firm account and market: the hedge registry's owner key."""
        acct = self.account_id if self.account_id is not None else (self.account_name or "-")
        return f"{self.broker}:{acct}:{self.market}"

    def best_day_cap(self) -> float | None:
        """Largest single day that does not push the profit target up."""
        return None if self.consistency is None else self.profit_target * self.consistency

    @classmethod
    def from_env(cls, live: bool = False, need_webhook: bool = False) -> "Config":
        market = _env("BRIDGE_MARKET", "NQ").upper()
        if market not in MARKETS:
            raise RuntimeError(f"BRIDGE_MARKET={market!r} is not one of {sorted(MARKETS)}")
        tick_default, pv_default = MARKETS[market]
        preset = _env("BRIDGE_PRESET", "Topstep 50K")
        if preset in PRESETS:
            target, mll, daily, max_ct = PRESETS[preset]
            cons, floor_mode, lock_at, lock_level = CONSISTENCY.get(preset), "eod", None, None
        elif preset in FIRM_PRESETS:
            target, mll, daily, max_ct, cons, floor_mode, lock_at, lock_level = FIRM_PRESETS[preset]
        else:
            raise RuntimeError(f"BRIDGE_PRESET={preset!r} is not one of {sorted(PRESETS) + sorted(FIRM_PRESETS)}")
        broker = _env("BRIDGE_BROKER", "topstepx").lower()
        if broker not in BROKERS:
            raise RuntimeError(f"BRIDGE_BROKER={broker!r} is not one of {BROKERS}")
        ct = broker == "crosstrade"
        return cls(
            username=_env("TOPSTEPX_USERNAME", "" if ct else MISSING),
            # Each connector reads only its own secret, and only from the environment.
            api_key=_env("CROSSTRADE_API_KEY") if ct else _env("TOPSTEPX_API_KEY"),
            base_url=_env("CROSSTRADE_BASE_URL", "https://app.crosstrade.io") if ct
            else _env("TOPSTEPX_BASE_URL", "https://api.topstepx.com"),
            account_id=None if ct else _env("TOPSTEPX_ACCOUNT_ID", None, int),
            contract_id=_env("BRIDGE_CONTRACT_ID", "" if ct else ("CON.F.US.MNQ.Z26" if market == "NQ" else MISSING)),
            tick_size=_env("BRIDGE_TICK_SIZE", tick_default, float),
            point_value=_env("BRIDGE_POINT_VALUE", pv_default, float),
            # The local signal engine has no inbound surface to protect, so the
            # secret is only required by the webhook server. Demanding one for
            # bridge.live would teach people to set a dummy, which is how a real
            # secret ends up being a dummy on the day it matters.
            webhook_secret=_env("BRIDGE_WEBHOOK_SECRET", MISSING if need_webhook else ""),
            live=live,
            # Which market-data subscription retrieveBars reads. A practice
            # account is on the sim feed; asking it for live data returns an
            # empty bar array rather than an error.
            live_data=_env("BRIDGE_LIVE_DATA", "0") not in ("0", "false", "False"),
            # The strategy's own entry deadline and flat time, not a second
            # opinion about them: tests/test_live.py asserts both against
            # LTFSweepConfig so a change to one that is not made to the other
            # fails the suite. An earlier cutoff was measured and rejected --
            # every candidate was a value picked by looking at its own P&L,
            # and the engine stops when the day's work is finished anyway.
            cutoff_minute=_env("BRIDGE_CUTOFF_MINUTE", 15 * 60 + 30, int),
            flat_minute=_env("BRIDGE_FLAT_MINUTE", 16 * 60, int),
            max_bar_age_s=_env("BRIDGE_MAX_BAR_AGE_S", 150.0, float),
            preset=preset,
            account_start=_env("BRIDGE_ACCOUNT_START", 50000.0, float),
            profit_target=target,
            max_loss_limit=mll,
            daily_loss_limit=daily,
            max_contracts=max_ct,
            safety_mult=_env("BRIDGE_SAFETY_MULT", 1.5, float),
            # The guard defaults ON even though docs/GO_LIVE.md now runs it
            # off in both phases. Forgetting the variable then costs money --
            # measured, it cuts the pass rate from 35% to 10% -- rather than
            # costing an account, and that is the right way round for a
            # default. Turning it off is a decision, so it stays explicit.
            use_guard=_env("BRIDGE_USE_GUARD", "1") not in ("0", "false", "False"),
            scaling_plan=_env("BRIDGE_SCALING_PLAN", "0") not in ("0", "false", "False"),
            consistency=cons,
            market=market,
            hedge_registry=_env("BRIDGE_HEDGE_REGISTRY", None),
            broker=broker,
            account_name=_env("CROSSTRADE_ACCOUNT") if ct else None,
            instrument=_env("CROSSTRADE_INSTRUMENT") if ct else None,
            floor_mode=floor_mode,
            lock_at=lock_at,
            lock_level=lock_level,
        )

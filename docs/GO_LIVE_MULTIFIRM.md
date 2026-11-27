# Go live beyond Topstep: Lucid and DayTraders (and optionally FFN)

Status 2026-11-27:
- **Groundwork built and tested:** broker choice, firm presets, static/locked floors, and the per-engine anti-hedge check.
- **CrossTrade connector (`bridge/crosstrade.py`):** written once CrossTrade's API reference has been captured and checked. It is verified
  only against those docs until a practice run (step 4).

Topstep keeps its own path (`docs/GO_LIVE.md`).

## Which products, and why
From `docs/PREREG_PROP_SEARCH3_20261126.md` (corrected model, registered bar). Prices are from Jx's third-party trackers; confirm each
at checkout.

| Product | Price | Real 2016–26 | Worst cash | First payout |
|---|---|---|---|---|
| LucidFlex 50K DLL ON, NQ | $80.50 | $40.5K | −$4.1K | ~4.5 months |
| LucidFlex 50K DLL ON, ES | $80.50 | $26.5K | −$2.4K | ~6 months |
| LucidDaily 50K | $85.40 | $35.8K | −$4.5K | — |
| DayTraders 100K Static | $75 + $5 | $22.0K | −$4.0K | ~13 months |
| DayTraders 150K Static | $90 + $5 | $48.4K | −$3.4K | ~12 months |
| Topstep $3K Challenge | $49 | $24.8K | −$1.2K | (Topstep path, no new connector) |

## How the bot reaches each firm

| Firm | Account lives on | Bot connects through | `BRIDGE_BROKER` |
|---|---|---|---|
| Topstep | TopstepX (ProjectX) | ProjectX API (`bridge/topstepx.py`) | `topstepx` (default) |
| Lucid | NinjaTrader 8 connection | **CrossTrade NT8 Add-On** | `crosstrade` |
| DayTraders | Rithmic, opened inside NinjaTrader 8 | **CrossTrade NT8 Add-On** | `crosstrade` |
| FFN (borderline) | Rithmic, inside NinjaTrader 8 | CrossTrade NT8 Add-On | `crosstrade` |

**Why not a direct Rithmic client.** Rithmic requires its own conformance testing before a custom R|Protocol app can trade
production accounts. NinjaTrader is already certified, so one CrossTrade connector serves Lucid, DayTraders and FFN.

**Where it runs.** Run everything on your own computer, as Topstep requires (no VPS, VPN or remote server). The other firms allow
bots; check each firm's agreement for its own device and VPS terms before going live.

## One engine per account
Each account gets its own engine process, with its own environment variables and its own journal. All engines on the computer share
**one** hedge-registry file, so no two accounts ever hold opposite directions:
- on the same contract (e.g. Topstep NQ long, Lucid NQ short);
- or across NQ / ES / YM.

```bash
# shared by every engine
export BRIDGE_HEDGE_REGISTRY=C:/trading/hedge.json
```

```bash
# Lucid, NQ
export BRIDGE_BROKER=crosstrade BRIDGE_PRESET="LucidFlex 50K" BRIDGE_MARKET=NQ
export CROSSTRADE_API_KEY=...            # from the environment only, never a file
export CROSSTRADE_ACCOUNT=<NinjaTrader account name>  CROSSTRADE_INSTRUMENT="MNQ 12-26"
uv run python -m bridge.live --journal data/journal_lucid_nq.jsonl
```

```bash
# DayTraders 150K Static, NQ
export BRIDGE_BROKER=crosstrade BRIDGE_PRESET="DayTraders 150K Static" BRIDGE_ACCOUNT_START=150000
export CROSSTRADE_ACCOUNT=<NinjaTrader Rithmic account name>  CROSSTRADE_INSTRUMENT="MNQ 12-26"
uv run python -m bridge.live --journal data/journal_dt150.jsonl
```

Each engine claims its direction before entering, and releases only its own claims when its day ends. An unreadable registry blocks
the entry: unknown is treated as "do not enter".

## Steps (same discipline as `docs/GO_LIVE.md`)
1. **Install:** NinjaTrader 8, the CrossTrade NT8 Add-On, and a CrossTrade subscription (~$49/month, Jx's spend). Connect each firm's
   account in NinjaTrader.
2. **Preflight, offline:** `uv run python -m bridge.live --preflight --offline` with each engine's variables. This checks the preset,
   instrument and account name, and prints the exact order that would be sent.
3. **Preflight, connected:** confirms CrossTrade answers, the account exists and bars arrive.
4. **Practice round trip** on a sim or practice account (`--roundtrip`): one real order that is placed, seen, cancelled or closed. This
   is the first time the connector meets the real server.
5. **Dry run** for a few days with `--journal`, then reconcile against the research engine (`scripts/reconcile.py`).
6. `--live` only after the journals reconcile.

## Rules the guards now know per firm (`bridge/config.py: FIRM_PRESETS`)
- **LucidFlex 50K:** EOD trailing; the floor stops at start + $100 after +$2,100; DLL $1,200 (DLL ON); 40% consistency.
- **DayTraders Static:** the floor never moves. The firm checks breaches on open losses, and the guard watches equity accordingly.
- Guards stay **off** by default in both phases, as in `docs/GO_LIVE.md`. The profit-target stop always applies.

## Known gaps
- The CrossTrade connector is unverified against a live server until step 4.
- Bars: the connector needs 1-minute bars from NinjaTrader via CrossTrade. If CrossTrade's API does not serve bars, the fallback is
  TopstepX bars (needs a Topstep account) or a NinjaTrader-side export. Decided once the API reference is read.
- Contract rolls: `CROSSTRADE_INSTRUMENT` must be updated each quarter, as `BRIDGE_CONTRACT_ID` is for Topstep.

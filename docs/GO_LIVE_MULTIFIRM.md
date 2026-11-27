# Go live beyond Topstep: Lucid and DayTraders (and optionally FFN)

Status 2026-11-27:
- **Built and tested offline (535 tests pass):**
  - broker choice (`BRIDGE_BROKER`), firm presets, static and locked floors;
  - the per-engine anti-hedge check;
  - **the CrossTrade connector, `bridge/crosstrade.py`**, with `tests/test_crosstrade.py` (16 tests).
- **Checked against CrossTrade's API reference only.** The reference was rendered 2026-11-27 (GitHub Actions run 45929437254,
  `data/public/propverify/expand_osstrade_io_docs_api_*.json`). The connector has not met a real server; step 4 is the first time.

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

## How the CrossTrade connector trades (from the API reference)
| Step | Call | Notes |
|---|---|---|
| Entry | `POST /v1/api/accounts/{account}/orders/place` | LIMIT, DAY, our own `orderId` (`lc-…`) |
| Watch the fill | `GET /v1/api/accounts/{account}/orders/{our id}` every 2 s | reads `filled` and `orderState` |
| Protect | `POST …/orders/cancel_and_bracket` on the **first** fill | cancels the rest of the entry, places an OCO stop + target for the position held |
| Cutoff | `POST …/orders/{our id}/cancel` | only if still listed in `GET …/orders?activeOnly=true` |
| 16:00 flat | `POST …/positions/flatten` with `cancelOrders: true` | also sweeps leftover stops and targets |
| Bars | `POST /v1/api/market/bars` (1-minute, closed bars only) | NT8 stamps bars at their close; the connector moves them to the open |

**Differences from Topstep, and what they cost:**
- **The stop and target go on after the fill, not with the entry.** NT8 through CrossTrade has no attached bracket.
  - The position is unprotected for about one fill check (2 s, `CROSSTRADE_PROTECT_POLL_S`) plus request time.
  - If the bracket fails three times, the connector flattens the position.
  - **If the engine process dies while an entry is resting, nothing protects that entry.** Cancel it by hand in NinjaTrader.
- **A partial fill is treated as the whole fill.** The rest of the entry is cancelled when the bracket goes on. The research model
  assumes full fills, so live size can come out smaller than modelled; reconciliation will show how often.
- **Rate limit:** 3 requests per second per CrossTrade user, shared by every engine on the same key. Each engine with a resting
  entry uses about 0.5 per second, so four engines fit. 429s are retried after `Retry-After`.
- **Plan:** the REST API needs CrossTrade **Pro or above** (official, `/docs/api/overview`).
  - Price: Pro is $49/month or $469/year, and Standard is $29/month without API access. Source: Jx's Google search 2026-11-27,
    citing CrossTrade's pricing page, QuantVPS and Copygram. This is third-party; confirm at checkout.
  - **7-day free trial, no credit card.** Per Jx (2026-11-27, third-party), it unlocks all features including the REST API and
    does not convert to a paid plan. So steps 2–5 cost $0; the connected check (step 3) confirms API access on day one.
- **Round-trip proofs:** each engine gets its own proof file (`data/roundtrip_proof_<engine>.json`). Topstep NQ keeps
  `data/roundtrip_proof.json`.

## Steps (same discipline as `docs/GO_LIVE.md`)
On Windows, steps 2–5 are one script: `scripts/crosstrade_test.ps1 -Step check | roundtrip | dryrun` (not yet run on a
Windows machine; the key is asked for each run and never saved).

1. **Install:** NinjaTrader 8 (free for simulation), the CrossTrade NT8 Add-On, and the CrossTrade 7-day trial. Start the trial
   only when steps 2–5 can be done within the 7 days. Pro ($49/month) is needed only after the trial, for live trading. Connect each
   firm's account in NinjaTrader.
2. **Preflight, offline:** `uv run python -m bridge.live --preflight --offline` with each engine's variables. This checks the preset,
   instrument and account name, and prints the exact entry and bracket that would be sent.
3. **Preflight, connected:** `--preflight` without `--offline`. It confirms:
   - CrossTrade answers (HTTP 408 = NinjaTrader closed or the Add-On disconnected);
   - the account is Connected;
   - 1-minute bars arrive and are stamped at the open after conversion.

   Also compare the newest bar's prices with the NT8 chart for that minute once by hand.
4. **Practice round trip** on a sim or practice account (`--roundtrip`): one far-off 1-lot limit is placed, seen, cancelled and seen
   gone. Then place one small sim trade near the market by hand through the engine's path, to watch the stop and target appear after
   the fill.
5. **Dry run** for a few days (no `--live`). This reads real bars, orders and positions through CrossTrade and records orders instead
   of sending them. Then reconcile against the research engine (`scripts/reconcile.py`).
6. `--live` only after the journals reconcile.

## Rules the guards now know per firm (`bridge/config.py: FIRM_PRESETS`)
- **LucidFlex 50K:** EOD trailing; the floor stops at start + $100 after +$2,100; DLL $1,200 (DLL ON); 40% consistency.
- **DayTraders Static:** the floor never moves. The firm checks breaches on open losses, and the guard watches equity accordingly.
- Guards stay **off** by default in both phases, as in `docs/GO_LIVE.md`. The profit-target stop always applies.

## Known gaps
- The CrossTrade connector is unverified against a live server until step 4.
- **Bar timestamps:** NinjaTrader stamps a bar at its close, and this is assumed from NinjaTrader's convention. The doc example does
  not settle it. Step 3's hand comparison settles it.
- **Unprotected seconds after each fill**, and an unprotected resting entry if the engine dies (see above).
- `scripts/export_live_trades.py` reads TopstepX fills only. CrossTrade's executions endpoint covers the last 15 minutes, so export
  fills from NinjaTrader (Account Performance → Executions) for reconciliation.
- **Contract rolls:** `CROSSTRADE_INSTRUMENT` must be updated each quarter, as `BRIDGE_CONTRACT_ID` is for Topstep.

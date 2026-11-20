# Running NQ, ES and YM on separate accounts (from PREREG_MARKETMIX_20261120)

**Not yet.** Keep the live Topstep account NQ-only until `docs/live_report.md` passes its gates
(`docs/PREREG_LIVE_20261120.md`). This file is the setup for when it does.

## What changed in the bot (all off by default; an NQ-only setup behaves as before)
1. **Limit prices on the tick grid (applies to NQ now too).** About half of the strategy's entries are
   gap midpoints between ticks (e.g. 29127.875). The bot now rounds a buy down and a sell up to the
   contract's tick, which fills in exactly the cases the backtest fills, half a tick better. Before this,
   such orders went out off-grid and the broker may have rejected them (not verified either way).
2. **`BRIDGE_MARKET`** = `NQ` (default), `ES` or `YM` sets tick size and $/point for MNQ/MES/MYM.
   ES and YM need `BRIDGE_CONTRACT_ID` set explicitly; find it with
   `uv run python -m bridge.live --find-contract MES` (or `MYM`).
3. **`BRIDGE_HEDGE_REGISTRY`** = a file path shared by every engine on the computer, e.g. `data\hedge.json`.
   Before entering, each engine claims its direction there; an entry opposite to another market's live
   claim is skipped and journaled as `blocked_hedge`. This keeps the accounts inside the firms'
   cross-account hedging bans. An unreadable registry also blocks (an unknown book is never read as flat).
4. Each market writes its own journal: `data/bridge_journal.jsonl` (NQ), `data/bridge_journal_ES.jsonl`,
   `data/bridge_journal_YM.jsonl`.

## Steps, when the time comes (Windows, one terminal per market)
1. `git pull` on the trading computer.
2. For each new account (e.g. the ES account), in its own terminal:
   ```
   set BRIDGE_MARKET=ES
   set BRIDGE_CONTRACT_ID=<id from --find-contract MES>
   set TOPSTEPX_ACCOUNT_ID=<that account's id>
   set BRIDGE_HEDGE_REGISTRY=data\hedge.json
   uv run python -m bridge.live --preflight
   uv run python -m bridge.live --roundtrip
   ```
3. Set `BRIDGE_HEDGE_REGISTRY=data\hedge.json` for the NQ engine too — every engine must use the same file,
   or the check does nothing.
4. Start each engine with `--live` in its own terminal. Practice account first, as in GO_LIVE.md.
5. After trading days, export each market's data for the comparison (scripts/export_live_trades.py).

Planned mix (backtest, with the filter): 5 Topstep = 3 NQ + 1 ES + 1 YM → ~$16K/yr needing ~$4.7K cash,
vs all-NQ ~$21K/yr needing ~$15K. ES's own edge is unconfirmed (86% vs coin flips); YM narrowly (96%).

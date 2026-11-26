# Pre-live audit — before the first ~$850–1,200 goes in (2026-11-26)

Jx asked for every figure behind the first live account to be checked for bugs before money is spent ("don't let it happen like the
memecoin project", where paper returns used an entry price nobody could get). This file lists every check, what it found, and what changed.
Raw output: `docs/jx_runs/audit_pre_live_20261126.txt` (`uv run python -m scripts.audit_pre_live_20261126`, re-run identical).

## Verdict
**One real modelling error was found and fixed. It lowers every prop figure in the repo.** The recycling model judged the loss limit on
*closed* trades only. Topstep checks it on *open* P&L in real time (help.topstep.com 8284204: realized and unrealized, liquidated
immediately). A trade that dips through the floor and then wins still closes the account; the old model let it live. Fixed in
`backtest/engine.py` (worst/best open P&L per trade, `mae_usd` / `mfe_usd`) and `backtest/recycle.py` (`realtime_mll=True` by default),
with tests. `realtime_mll=False` reproduces every figure made before 2026-11-26.

**What it changes for the next step (Topstep 50K, one account, bot):**
| | Before (closed P&L) | After (real-time, corrected) |
|---|---|---|
| Net 2016–26 | $46,492 ($4,293/yr) | **$37,406 ($3,454/yr)** |
| Coin-flip median (does the money come from the rules?) | $18,005 | **$6,384, positive in 76% of runs** — still passes the ≥ $5,000 bar |
| Money needed to start: median / 1 in 10 / worst | −$735 / −$2,583 / −$3,520 | **−$1,181 / −$2,585 / −$3,475** |
| First payout: median amount / days | $1,002 / 126 | **$1,085 / 132** |
| Net after 12 months: median (share of starts losing) | $1,704 (30%) | **$1,327 (39%)** |
Every start date still went positive eventually. **The next step is unchanged: one Topstep account. Budget ~$1,200 to start (not
~$850), with up to ~$2.6K set aside (9 in 10 starts) and ~$3.5K for the worst start.**

**LucidDaily is no longer #1 and no longer qualifies.** Third-party summaries say LucidDaily's *funded* stage trails intraday (open profit
raises the floor) unless the EOD-funded add-on is bought; the repo cannot read Lucid's pages to confirm. Corrected: $85.40 product
$27,301 with a coin-flip median of $218 (52% positive); EOD-funded add-on at $165.20 $16,248 (coin flip −$14,782). TTP Prime ($26,700,
coin flip $3,521) and DayTraders EOD ($33,760, coin flip −$5,937) also fall below the ≥ $5,000 coin-flip bar **if** they check open P&L
the same way (not yet verified for either firm). The 4-firm plan therefore no longer qualifies as approved; Topstep is the only product
that passes on the corrected model.

## Checks and results
| # | Check | Method | Result |
|---|---|---|---|
| 1 | Test suite | `pytest` (no skips) | 503 passed before, 507 after (4 new tests for the fix) |
| 2 | Cached orders are what the current strategy code produces | regenerated all NQ orders from `strategies/ltf_sweep.py` and compared with `ideas_orders_NQ.parquet` | **3,490 of 3,490 identical** |
| 3 | Look-ahead / live parity | rebuilt every order the way the bot does it (that trading day's bars only, closed bars only, before `valid_from`, live config) | **3,484 of 3,490 identical**; 6 differ only in stop/target (the backtest also sees the previous day's bars); entries and directions all match; no look-ahead |
| 4 | Recycling engine logic | independent re-implementation of Topstep and LucidDaily rules, written from the rules text | closed mode: LucidDaily identical ($57,486, 93 payouts); Topstep identical once the $14.50/month API fee is added ($48,377 − $1,885 = $46,492); real-time mode: Topstep identical ($37,406) |
| 5 | **Loss limit on open P&L** | firm rule check | **error found, fixed (above)**. The excursion uses the whole fill bar and exit bar; excluding the fill bar moves Topstep only to $37,663 |
| 6 | Costs | Topstep's page: MNQ $0.74 exchange/NFA + $0.50 commission (since 2026-04-12) = **$1.24 round trip = model** | correct (and conservative before April 2026, when it was $0.74) |
| 7 | Contract caps | engine caps sizing at 200; recycle applies 50 micros (Combine) and the XFA scaling plan 20/30/50; the bot applies the same ladder (`bridge/guards.py`) | correct |
| 8 | Fill realism (Topstep, corrected model) | stress variants | see below |

## How sensitive the corrected Topstep figure is to execution (why the live check matters)
| Variant | Net 2016–26 | Start: median / 1 in 10 / worst |
|---|---|---|
| Baseline (limit fills on touch, stop slips 1 tick, $1.24) | $37,406 | −$1,181 / −$2,585 / −$3,475 |
| Limit entry needs price 1 tick through it | $29,552 | −$1,241 / −$2,744 / −$3,573 |
| Stops slip 2 ticks | $31,050 | −$1,414 / −$3,293 / −$4,466 |
| Orders placed 1 minute late | $26,089 | −$1,209 / −$2,803 / −$3,458 |
| All three together | $14,533 | −$1,673 / −$3,272 / −$4,160 |
Every variant stays positive, but the income is sensitive to execution: the live comparison gates (fill rate, slippage, order timing) are
what decide whether the baseline or a stressed row describes reality. Order timing matters most: the bot must place the order within
seconds of the confirming bar's close, not a minute later.

## What did not change
- The strategy's signals (checks 2 and 3), the cost per trade, the contract caps, the live-comparison gates in
  `docs/PREREG_LIVE_20261120.md` (they compare trades, not account outcomes).
- The Topstep rules themselves (verified 2026-11-22, `docs/PROP_VERIFY_20261122.md`).

## Superseded
All prop-firm dollar figures dated before 2026-11-26 (PROP_VERIFY, PROP_COMPARISON, PREREG_PORTFOLIO_MY, prop ROI PR1, LS1, LS2 and the
radar pricing) used the closed-P&L model and are optimistic. Reproduce any of them with `realtime_mll=False`. The coin-flip helper
(`scripts/radar_price.py: flip`) now swaps a flipped trade's worst and best open P&L; other scripts' own coin-flip loops do not, so re-run
through `flip` before relying on them.

## Still open (not checkable from here)
- Lucid, TTP and DayTraders: whether their loss limits are checked on open P&L and whether LucidDaily funded trails intraday — their pages
  could not be read from this environment (Lucid shows a bot check; a fetch needed approval that was not answered). Until confirmed,
  treat them as not qualifying.
- Queue position on limit fills: only the live fill rate can settle where between "touch" and "1 tick through" reality sits.

## Addendum 1 (2026-11-26): every previously approved product re-priced on the corrected model
`uv run python -m scripts.audit_all_prop_20261126` → `docs/jx_runs/audit_all_prop_20261126.txt` (re-run identical). Same rule as before
(real ≥ 50% of Topstep Standard on the same model and delay, coin flip ≥ $5,000, worst dip no worse than 1.5× Topstep's).
| Product (bot) | Real (closed-P&L model) | Coin flip | Worst dip | Verdict |
|---|---|---|---|---|
| Topstep 50K Standard (benchmark) | $35,124 ($44,359) | $6,205 (75%) | −$4,058 | qualifies |
| **Topstep 50K Consistency** | **$37,406** ($46,492) | $6,384 (76%) | −$3,524 | **qualifies** |
| TTP Futures Prime 50K | $26,700 ($50,495) | $3,521 | −$5,651 | fails (coin flip) |
| DayTraders EOD 50K | $33,760 ($48,856) | −$5,937 | −$7,064 | fails |
| LucidDaily $85.40, funded trails intraday (the default, third-party) | $27,301 ($57,486) | $218 | −$3,814 | fails |
| LucidDaily $85.40 if funded were EOD | $34,124 | $5,723 | −$3,598 | would qualify, but EOD funded is sold at $165.20, which fails (coin flip −$14,782) |
| LucidFlex 50K DLL ON | $29,037 ($40,545) | $4,806 | −$4,508 | fails (coin flip, narrowly) |
| TradeDay 50K $85 | $18,567 ($35,678) | −$1,486 | −$5,855 | fails |
Manual entry (3-minute delay): **nothing qualifies**, not even Topstep (coin flip $4,540); Top One Elite $18,741, coin flip $385.
Products that failed on the old model only get worse on this one. **Result: one firm qualifies — Topstep.** The other firms' verdicts
assume they also check open P&L; if one only checks at the close, its old (closed-P&L) figure applies — confirm on each firm's pages.

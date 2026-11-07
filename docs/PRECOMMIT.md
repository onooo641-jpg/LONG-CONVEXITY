# PRECOMMIT — the rules, fixed before any money is spent

Committed **before** the first Topstep purchase. The commit timestamp is the
proof that these rules came first. Changing anything here after the first
trade needs a new dated section below the line, with the reason. Editing
these rules in place is not allowed.

## What is being tested

Whether the backtested recycling business survives live execution: real
fills, the TopstepX data feed, and the bridge placing orders correctly. The
backtest cannot answer that. One account, small fixed cost, measured monthly.

## Fixed setup

| | |
|---|---|
| Accounts | **one** 50K Trading Combine, Standard path |
| Risk per trade | **$900** |
| Strategy | `strategies/ltf_sweep.py`, `LTFSweepConfig()` defaults. `news_filter` **off**. No 11:00 ET cutoff. |
| Payout policy | **LOCK_FIRST** |
| Guard | `BRIDGE_USE_GUARD=0` (GO_LIVE) |
| Parameters | **None changed once live.** `strategies/registry.py` is pre-registered. Mechanical bug fixes only, each logged in `ARTIFACT_CLASSES.md`. |
| Rules check | On purchase day, re-read Topstep's own pages (`docs/TOPSTEP_RULES.md`). Any mismatch: fix `XFARules`, re-run, **then** trade. |
| Before the Combine | GO_LIVE steps 1-6 on the Practice account, including `--roundtrip` |

## Capital

**Set aside $3,600.** That covers the deepest cumulative loss in 118
backtested start dates (worst −$3,568, Jan 2016 start; typical −$864;
`FIGURES_LEDGER.md` #21). It is a backtest figure. Live results are expected
to be somewhat worse because of fill queueing.

Track one number from your own receipts: **fees paid − payouts received**.

## When to stop

**Binding:** if fees paid − payouts received reaches **−$3,600**, stop buying
resets. That is beyond anything in 11 years of backtest, so either live
execution is worse than modelled or the strategy has changed. Review with the
forward log and reconciliation before deciding anything else.

**Review signals, not exits.** Each of these means pause, run
`scripts/reconcile.py`, read the forward log, and resume unless the review
finds a defect:
- 6 evaluations burned since the last pass (`STOPPING_RULE`)
- 239 days without a payout (`PAYOUT_DROUGHT_DAYS`)
- trailing 100-trade profit factor under 0.70 (`TRAILING_PF_MIN`)

They are review signals because, used as exits, they stop **118 of 118**
backtested start dates, typically before the first payout
(`FIGURES_LEDGER.md` #21).

**Immediate stop, regardless of money:**
- Topstep removes the MLL lock at $0 (net −$61,902 under that change)
- `reconcile.py` shows a `settings` or `logic` difference that the journal
  can't explain
- `cancel_failed` in the journal: check the platform by hand first

## What to expect

From the backtest (`FIGURES_LEDGER.md` #21, #22): about 1 pass in 3
evaluations. Typical wait for the first payout about 5 months; 1 in 4 start
dates got none in the first year. **About 4 months in 5 have no payout** and
cost $60-400. Planning figure about $260/month averaged over a year, not
earned monthly.

## Second account

Only after **both**: one real payout received, and 3 consecutive months of
clean reconciliation (no `settings`/`logic` differences). Maximum 5 (the
Express Funded cap).

---

*Changes after the first trade go below this line, dated, with the reason.*

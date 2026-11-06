# Session notes — checks before spending anything, plus four changes

Written so nothing in this session depends on a chat paste surviving. Repo:
cloned 2026-11-06, `uv run python scripts/ingest.py` run (data through
2026-10-28), full test suite green (336 tests) throughout. No strategy
parameters were changed anywhere in this session — every edit is either a
reproducible measurement, a mechanical bug fix, or a new opt-in flag that
defaults to the old behaviour.

## Check 1 — figure drift between GO_LIVE.md line ~158 and the 5-account table

**Not a parameterisation difference. Two different metrics, both stale.**

The $42,414 figure was never a "withdrawn cash" number — it's `recycle()`'s
**net** field (cash minus cost), hardcoded identically in
`scripts/fade_report.py:307` (`policy=Policy.IMMEDIATE`, confirmed by reading
the call site), and copied into GO_LIVE.md next to a cost figure ($17,314)
that came from a different, older run of `scripts/recycling_report.py`. The
5-account table's $61,984/$44,868 are **cash withdrawn** and **net**,
respectively, from `scripts/account_lifetime.py` (which has always hardcoded
`Policy.IMMEDIATE` too). So the $19,570 gap is net-vs-cash, not
LOCK_FIRST-vs-IMMEDIATE or a payout-cap change — both numbers turned out to
already be the same policy, just different fields, from two scripts that have
never shared one rerun.

Resolved by rerunning everything from the same data, same session, with
each field labelled (see `FIGURES_LEDGER.md` #1 and #4): current 11-year net
is **$48,190** (cash $65,467, cost $17,277), under the new default policy
(see check 5 below). GO_LIVE.md's affected sections were rewritten in place
with a pointer to `FIGURES_LEDGER.md` rather than restating two unlabelled
numbers next to each other again.

## Check 2 — withdrawals by calendar year, 2016-2026

Does the whole business rest on the 2024+ regime change, or does the
account-structure asymmetry (capped bust cost vs. uncapped-ish payout
optionality) carry real weight on its own? Reran the unbroken 2016-2026
chain and attributed each payout to the calendar year it landed in (both
policies, $900/trade):

| Year | LOCK_FIRST withdrawn | IMMEDIATE withdrawn |
|---|---|---|
| 2016 | $0 | $125 |
| 2017 | $0 | $485 |
| 2018 | $0 | $146 |
| 2019 | $4,474 | $6,402 |
| 2020 | $10,617 | $8,927 |
| 2021 | $1,164 | $2,085 |
| 2022 | $3,342 | $2,788 |
| 2023 | $11,444 | $13,423 |
| 2024 | $6,775 | $7,065 |
| 2025 | $9,738 | $8,416 |
| 2026 (partial, to 10-28) | $14,693 | $15,606 |

**Answer: withdrawals are not concentrated in the last two years.** Under
either policy, 2019/2020/2023 — all *inside* the dev-period, pre-2024-regime
window — produced real cash, comparable in size to 2024-2026. The last 3
calendar years (2024-2026, the OOS window per GO_LIVE's own framing) are
roughly half of lifetime withdrawals (50.1% LOCK_FIRST, 47.5% IMMEDIATE), not
nearly all of it. The one flag worth carrying forward: 2026 alone (and it's
not even a complete year yet) is ~24% of the 11-year total under either
policy — a single year that size is a concentration risk worth remembering
even though it doesn't invalidate the earlier years' contribution.

**This does not kill the business case, but it doesn't fully vindicate it
either** — three years (2016-2018) paid nothing at all, which is the real
risk (see "longest dry spell" below), not whether the regime changed.

## Check 3 — pass rate and payout rate vs. Topstep's published numbers

Reconstructed from the same unbroken 2016-2026 chain at $900/trade:

| | LOCK_FIRST | IMMEDIATE | Topstep (2025, published) |
|---|---|---|---|
| Pass rate (combine evaluations → funded) | 34.2% | 33.5% | 16.8% |
| Payout rate (funded accounts → ≥1 payout) | 39.6% | 57.7% | 33.3% |

**3a/3b:** pass rate is ~2x Topstep's reported figure under either policy —
matches the user's own prior ("bootstrap puts it at 30-34%"). Payout rate:
LOCK_FIRST (39.6%) is close to plausible (1.2x reported); **IMMEDIATE
(57.7%) is 1.7x reported** — not the 80%-vs-33% red flag the prompt named as
the trigger, but clearly on the optimistic side.

**3c, where it comes from:** the caveat the prompt itself raised is the right
explanation for most of the gap — Topstep's 16.8%/33.3% are across *all*
participants, overwhelmingly discretionary traders with no mechanical system,
so a one-trade-a-day rule beating that population is not surprising on its
own. What is *not* fully explained by that caveat is IMMEDIATE's extra lift
over LOCK_FIRST (57.7% vs 39.6%) — that's a backtest artifact of the payout
policy itself: IMMEDIATE books a payout the instant eligible, so it credits
"at least one payout" to funded accounts that would have died un-locked (and
un-paid) under LOCK_FIRST. The policy choice directly inflates this specific
metric; it's a reason to read 57.7% skeptically, not a reason to doubt the
policy switch (see check 5 — the switch is justified on 11-year net + the
counterparty-risk argument, not on this metric).

## Check 4 — rule-change stress test

`XFARules` is a frozen dataclass; reran 11 years at $900/trade under
`Policy.LOCK_FIRST` (the policy whose mechanics the lock/reset questions are
actually about) with each change applied alone. Baseline net **$44,823**.

| Change | Net | Delta |
|---|---|---|
| reset $49 → $99 | $43,523 | -$1,300 |
| trailing limit never locks (`mll_locks_at=None`) | **-$17,079** | **-$61,902** |
| `payout_cap` $4,000 → $2,000 | $45,579 | +$756 |
| `winning_days_required` 5 → 10 | $45,444 | +$621 |
| activation charged per attempt, not per XFA earned | $29,625 | -$15,198 |

**Bug found and fixed along the way:** `backtest/recycle.py:298` crashed
(`TypeError`) on `mll_locks_at=None` — `locked = account.peak >= rules.mll_locks_at`
doesn't handle `None`, even though the sibling method `_Account.floor()` 20
lines away already treats `None` as "never locks." Fixed to match that
existing semantics (`locked = rules.mll_locks_at is not None and ...`); this
is a mechanical fix (the dataclass field is documented as accepting `None`,
and one code path just didn't handle it), not a parameter tune. Tests still
pass (332 → still green after the fix).

**Read the no-lock scenario carefully: it's a policy pathology, not a market
result.** Under `LOCK_FIRST`, if the limit never locks, "eligible" requires
`locked or policy is IMMEDIATE` — so `LOCK_FIRST` never pays out, ever, under
this rule change (cash=$0, pure cost = -$17,079). That's correct given the
policy's own definition, but it's really showing "LOCK_FIRST depends
entirely on the lock existing," not "removing the lock loses $61,902 of
trading edge." For comparison, `IMMEDIATE` under the same no-lock change:
net $21,166 (cash $39,678, cost $18,512) — still profitable, because it
never needed the lock to take money out. **How much this business survives
rule-tightening depends heavily on which payout policy is in force**, which
is itself an argument for IMMEDIATE (check 5): it's the policy least exposed
to Topstep changing the one rule (the MLL lock) the whole LOCK_FIRST strategy
depends on.

The other four changes are all single-digit-percent net effects — this
business is not fragile to reset-fee or payout-cap tweaks, it is fragile
specifically to the lock mechanic and to activation-fee timing.

## Check 5 — switched default `Policy` to `IMMEDIATE`

Done in `backtest/recycle.py` (`recycle()`'s default arg and the `Policy`
enum's own docstring), `scripts/recycling_report.py` (`run_row`'s default,
and the policy-comparison code paths re-pointed so the A/B comparison still
compares two *different* policies instead of both silently becoming the new
default). `scripts/account_lifetime.py` and `scripts/fade_report.py` already
hardcoded `Policy.IMMEDIATE` everywhere and needed no change.

Reasoning: `LOCK_FIRST` is optimal against Topstep's *own rules* (waiting for
the lock before withdrawing buys insurance against the trailing limit). It is
not optimal against **counterparty risk**, which the rules don't price at
all. ~80-100 prop firms closed in 2024 (~1 in 7/year); a pending payout at a
firm that fails typically goes unpaid (True Forex Funds: ~300 traders, ~$1.2M
unpaid; Nexgen, Oct 2026: partial payout only). `LOCK_FIRST` maximises how
much of your money sits inside that risk, for as long as possible.

The 11-year data agrees independently: IMMEDIATE wins at every position size
tested (+$3,367 net at $900/trade, more at others — see
`scripts/recycling_report.py`'s policy table). The one-year sample in the
HTML report says LOCK_FIRST is marginally better; 11 years says IMMEDIATE
wins broadly. Both the rules-risk argument and the counterparty-risk argument
point the same way, so this isn't a close call dressed up as one.

All affected GO_LIVE.md tables (the 5-account table, the account-lifetime
table, the two-stage guard comparison, the dry-spell/bust-streak figures)
were rewritten with the regenerated numbers under the new default — see
`FIGURES_LEDGER.md` for the exact commands.

## Check 6 — news filter (F2), ported into `strategies/ltf_sweep.py`

Added `LTFSweepConfig.news_filter: bool = False` (off by default — this is a
new independently-toggled filter, not a retune of the registered params) and
`load_blackout_dates()`, backed by a new `docs/tier1_calendar.csv`: CPI, PPI,
NFP, PCE, Retail Sales (ALFRED/St. Louis Fed real-time release-date vintage
files — primary-sourced, not a "first Friday of the month" heuristic) and
FOMC decision days (federalreserve.gov historical/current calendars), 764
rows, 2016-01-01 to 2026-11-06. Known gap baked into the source data itself:
the Oct-Nov 2025 government shutdown pushed several 2025 releases into
Dec 2025/Jan 2026, visible as irregular gaps in those series — not a scraping
error.

**Cost, measured both ways:**

| | 11-year | OOS (2024-2026) |
|---|---|---|
| Trades removed | 546 / 2,185 (25.0%) | 144 / 574 (25.1%) |
| Net, before → after | -$2,553 → **-$3,342** | $43,064 → **$46,019** |
| Profit factor, before → after | 0.997 → 0.995 | 1.191 → **1.284** |

**Mixed result.** The filter costs money over the full 11-year history
(removes some winning trades along with the news-day noise) but improves
both net and profit factor out-of-sample. Left `news_filter=False` by
default rather than flipping it on — turning it on because the *recent*
window likes it better would be exactly the kind of after-the-fact
cherry-picking GO_LIVE.md's own working rule (the 11:00 ET cutoff, rejected
for being found by scanning a table) warns against. The flag is there,
measured, and available; it is not switched on.

## Check 7 — the stopping rule

It exists: `scripts/reconcile.py`'s `STOPPING_RULE = 6` (commit `e6740f9`,
"Put the stopping rule where it will be read"), surfaced automatically every
time `reconcile.py` runs, reading the live journal's `session_start` records.
**But it only covers the evaluation-burn side of the business** — "how many
combine resets before a funded account" — not the two conditions the prompt
named: a payout drought, or a declining trailing-trade profit factor. Traced
through the code: the streak counter resets to zero the moment an account
*becomes* funded, not when it *pays out* — so a funded account that busts
immediately with zero payouts still resets the streak, which is correct for
measuring combine-burn but blind to a funded account quietly failing to ever
pay.

**Added the missing half**, in the same file, same style (measured
thresholds, not chosen ones):

- `PAYOUT_DROUGHT_DAYS = 213` — the 90th-percentile gap between payouts,
  replaying 2016-2026 at $900/trade under `LOCK_FIRST` (median gap 21 days,
  max 307).
- `TRAILING_PF_MIN = 0.70` over `TRAILING_PF_TRADES = 100` — the 10th
  percentile of rolling 100-trade profit factor over the same history
  (median 0.98).
- `check_business_health(days_since_payout, trailing_pf)` in
  `scripts/reconcile.py`, wired to two new CLI flags (`--days-since-payout`,
  `--trailing-pf`) and printed alongside the existing stopping-rule block.

**Why these are manual inputs, not automatic:** neither is observable from
`data/bridge_journal.jsonl`. A payout is credited on Topstep's dashboard, not
placed by the bridge (no `payout` journal event exists or could exist without
new code on the broker-integration side). A trade's realized win/loss is
decided by the broker's bracket fill, which the bridge places but does not
read back — `bridge/live.py` has no event type carrying P&L. Wiring either
one up automatically would mean teaching the bridge to poll the broker for
account state, which is a real feature, not a stopping-rule fix, and out of
scope here. The honest version ships now: read it off the statement, type it
in, get a measured threshold check against it. 5 new tests in
`tests/test_reconcile.py`; full suite still green.

## Check 8 — concentrate on Topstep, don't build multi-firm support

Recorded, not built. The 2026 futures-firm closures (ProjectX ending
third-party access and reportedly going Topstep-exclusive; Rev One citing
"lacked a top platform option"; FundedSeat citing "limitations from big
trading platforms") were platform gatekeeping, not trading losses — Topstep
is the consolidation's winner, the others are the fragile side. Diversifying
across firms would *increase* exposure to a firm closing, not reduce it, and
`bridge/` is written against TopstepX's specific API — a second firm needs a
second bridge, not a config flag. No code changes; the reasoning is recorded
here and pointed to from `docs/GO_LIVE.md`.

## Items 9-12 (new files, forward log column)

- `docs/FIGURES_LEDGER.md` — one row per standing figure, seeded from checks
  1-7 above plus the pre-existing headline numbers, each with a command,
  computed date, window, and status (`current` / `superseded` / `unsourced`).
  Two figures the prompt asked to seed (`PF 0.876`, the "106-day time to
  pass") could not be reproduced exactly this session — see the ledger for
  what was found instead, including tracing `PF 0.876` to its exact source
  commit (`7fa7f86`).
- `docs/CANDIDATES.md` — the seven registry strategies, LTF Sweep, OR5
  retest, the ORB family search, every session-cutoff candidate from
  GO_LIVE's hourly table, the news filter, and the payout-policy switch, each
  numbered with its formulation and verdict.
- `docs/ARTIFACT_CLASSES.md` — the two existing named classes (confirmation
  one bar early, marketable limit orders) traced to their exact source
  commits with sighting counts, plus the third class the prompt asked to add
  (an API response that can't distinguish failure from empty) — documented
  but **not yet an assertion** in `bridge/preflight.py`; flagged for the next
  session that touches it rather than built speculatively here.
- `scripts/forward_log.py` — added `ambiguous` to `COLUMNS`, backfilled all
  28 existing rows (not 15 — the log has grown since the prompt was written)
  with `False`, confirmed correct because `exit_reason` is "target"/"stop"
  plain on every row and the engine only ever writes `"stop_ambiguous"` /
  `"target_ambiguous"` when the flag is actually `True` (`backtest/engine.py`
  lines 389-390) — so the exit-reason column itself already proves the
  backfill, no need to rerun the original backtests to check.

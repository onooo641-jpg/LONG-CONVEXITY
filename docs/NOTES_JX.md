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

## Check 9 (addendum, same day): an independent concurrent session, and the
## replication it accidentally produced

While this session worked, a second Claude Code session (same account,
`Jx <onooo641@gmail.com>`, 12 commits between 14:19 and 18:15 on 2026-11-06)
independently implemented the same brief against the same repo and pushed
straight to the shared branch this session started from — not a hostile
actor, just no coordination between two sessions. The two branches diverged
without either knowing about the other.

**Provenance was checked before anything else** (author/email/timestamps on
the 12 commits) rather than assumed, per the standing instruction that
unexplained commits in your own repo outrank any other finding.

**This session's own commits were moved to a dedicated branch**
(`jx/rules-recheck-local`) before any merge decision, so the local working
tree stopped being the only copy of either side's work. Neither branch was
merged into the other; this is a documentation-level reconciliation, not a
git merge.

### Replication result: AGREE / DISAGREE / UNIQUE

Comparing this session's `FIGURES_LEDGER.md` / `CANDIDATES.md` /
`ARTIFACT_CLASSES.md` against the independent session's versions on
`origin/claude/ict-trading-resources-ugh07b`:

**AGREE** (same finding, reached independently — the strongest kind of
confirmation available here):
- The `mll_locks_at=None` crash: **both sessions hit it and fixed it with the
  identical line** (`locked = (rules.mll_locks_at is not None and ...)`).
  Confirmed, not a fluke of one session's test fixtures.
- LTF Sweep's raw 11-year P&L direction and the general shape of the
  recycling business case (loses on its own, works inside the account
  structure).
- The confirmation-timing and marketable-limit-order artifact classes
  (classes 1 and 2), independently arrived at before this session started
  and unchanged by either branch.

**DISAGREE, resolved** (at least one side was using stale information, not a
difference of opinion):
- **Payout policy default.** This session's own hazard-sweep argument for
  `IMMEDIATE` and the independent session's `LOCK_FIRST` conclusion were
  both computed correctly for the rule model each was using — the actual
  disagreement was that the independent session had already found two real
  Topstep payout rules (MLL locks on payout; profit-since-last-payout
  required) that this session's rule model was missing. Ported those rules
  in, re-verified the hazard sweep under them (see `FIGURES_LEDGER.md`
  #13/#14), and the two sessions' conclusions now agree exactly: `net`
  figures match to the dollar ($44,590 / $62,065 / $17,475 / 157 accounts /
  53 XFA / 43 payouts / 151 of 161 shared bust days, all identical).
  **Caveat found afterward (same day): that exact match is evidence the port
  was faithful, not evidence the two rules themselves were correct — once
  ported, the two codebases were no longer independent on this point.**
  Checked both rules against Topstep's own help pages directly: both are
  real and confirmed (`docs/TOPSTEP_RULES.md`). But `payout_cap=4000.0` was
  also checked and is wrong — $4,000 is a limited-time promo figure (new
  Combine + Daily Loss Limit at checkout), not the standing $2,000 cap, and
  this account was never bought under that promo. Corrected to `2000.0`;
  conclusion (`LOCK_FIRST` wins) survives, margin narrows from $1,636 to
  $1,051 at $900/trade (`FIGURES_LEDGER.md` #15/#16). The $44,590 figures
  above are real for the rule model they were computed under, now
  superseded — see #15 for the current numbers.
- **ORB family search and OR5 retest results.** The independent session
  found and fixed a genuine look-ahead bug (previous evening's bars breaking
  a range that forms the next morning — `ARTIFACT_CLASSES.md` class 5,
  ported here with its regression test). This was a real correctness bug in
  shared strategy files, not a parameter choice, so porting it is a
  mechanical fix under this project's own working rule, not tuning.
- The "106 days" time-to-first-pass figure, previously marked `unsourced` in
  this session's ledger: the independent session's ledger named
  `scripts/quarterly_report.py` as the source. Verified by running it rather
  than trusting the citation — it reproduces exactly (`FIGURES_LEDGER.md`
  #8).

**UNIQUE** (present on one side only; evaluated, not blindly folded in):
- The independent session implemented `ARTIFACT_CLASSES.md` class 3 (the
  empty-API-response problem this session had only documented) as a real
  assertion in `bridge/roundtrip.py`, touching `bridge/live.py`. **Not
  ported**: it changes the live-trading, real-money execution path, which is
  out of scope for a documentation/ledger reconciliation pass and deserves
  its own review rather than being pulled in as a side effect of this one.
  Flagged in `ARTIFACT_CLASSES.md` for whoever next touches `bridge/live.py`.
- The independent session also started `scripts/jx_capital.py` and
  `scripts/jx_lucid.py`, modelling a second prop firm (LucidFlex) for
  comparison. This runs against this project's own working rule (check 8:
  concentrate on Topstep only, record the reasoning, don't build multi-firm
  support) — not adopted, and worth raising with the other session or the
  user rather than silently overriding it.

**Operational note:** the independent session's commits ran as late as
18:15 on 2026-11-06, the same day. It may still be active. If it keeps
committing to the shared branch, the two histories will diverge again, and
each side will now be building on a different, already-reconciled ledger —
harder to reconcile a second time than this one was. Worth closing or
confirming status before relying on the shared branch again.

## Check 10: the exact match proved the port, not the rules

The AGREE-list match above (check 9) was treated as closing the question.
It didn't — it only proved the port of the other session's rules into this
one was faithful. The two new rules became single-sourced the moment they
were ported; from that point on, matching to the dollar is a port-fidelity
check, not independent replication of the rules themselves.

**Both new rules confirmed against Topstep's own help pages directly**
(not a third session's citation of them): `docs/TOPSTEP_RULES.md`.
`payout_locks_mll` and `profit_since_payout_required` are both real.
**One parameter was wrong**: `payout_cap=4000.0` is the limited-time promo
figure (new Combine + DLL at checkout), not the standing $2,000 cap this
account would actually get. Corrected. `LOCK_FIRST` still wins at $900/trade,
margin narrows from $1,636 to $1,051 (`FIGURES_LEDGER.md` #15/#16).

**Decomposition** (`scripts/payout_rule_decomposition.py`,
`FIGURES_LEDGER.md` #17): isolated the two rules to check a mechanism
prediction pre-registered before running it — `payout_locks_mll` alone
should favour IMMEDIATE (it hands IMMEDIATE the same $0 floor LOCK_FIRST
waits for, for free), `profit_since_payout_required` alone should favour
LOCK_FIRST (it throttles IMMEDIATE's more frequent early payouts). **Both
predictions were wrong about direction.** `payout_locks_mll` alone still
favours LOCK_FIRST — checked against `_Account.floor()`'s own code and
docstring before concluding this, not assumed: the rule is punitive when it
fires on a low-peak account (pins a floor that would otherwise still be
negative up to exactly $0, right when balance is lowest post-payout), not
protective, and IMMEDIATE is the policy that tends to pay out before peak
reaches $2,000. Not a bug — the code matches Topstep's own wording ("set to
$0 regardless of where it was before") and matches its own docstring; the
prediction's mental model was incomplete, not the implementation.
`profit_since_payout_required` alone also favours IMMEDIATE, opposite the
prediction, for reasons not decomposed further this session (it costs
LOCK_FIRST more absolute dollars than IMMEDIATE off each policy's own
baseline — aggregate-level finding only). The combined, actually-shipped
result (c) is unaffected by either wrong prediction and still matches
check 9's conclusion.

**Unresolved, flagged rather than guessed at**: multiple third-party
trackers describe Topstep rule changes during 2026 (an April 2026 payout
change, a "$5K first cap," a "100/90 split") that don't match what
Topstep's own help pages state as of this read. Not reconciled — could not
tell from here whether the third-party pages are stale or Topstep's own
rulebook changed more than once this year. The 11-year backtest assumes a
constant rulebook throughout; 2026 is the one year in the window a rule
change is actually alleged. Re-pull `docs/TOPSTEP_RULES.md`'s sources again
before buying, and re-run the base case if anything else disagrees with the
live page the way `payout_cap` did.

## Check 11: the GitHub Actions workflow the other session added

The other session's last commit on the shared branch, `0742fe9` ("Run the
monthly update on GitHub Actions," 2026-11-06 19:37:41 +0800, authored by
the same account under a different session ID — `session_011kRjSXx5jfPCnRSnoU7MJr`),
adds `.github/workflows/monthly.yml` plus `scripts/monthly_update.py`. This
is the one piece of that session's work that acts on its own rather than
sitting inert in a branch, so it was read in full before anything else in
this check.

What it does: runs on a cron (`17 3 2 * *`, monthly) or manual
`workflow_dispatch`; `permissions: contents: write` only (no
`actions:write`, can't modify workflows or secrets); needs the
`DATABENTO_API_KEY` repo secret, degrades to `--skip-fetch` (re-checks
stored data only, no network call) if the secret is absent; the fetch step
itself aborts before downloading if Databento's quote exceeds $1.00; the
only side effect is a commit (as `github-actions[bot]`, not this account)
of `data/raw`, `docs/forward_log.csv`, and
`docs/jx_runs/monthly_latest.txt`, pushed with the token `actions/checkout`
already holds under `contents: write`. One other change in the same commit,
`scripts/fetch_databento.py`, suppresses an interactive "rotate this key,
it was pasted into a chat" warning specifically when `GITHUB_ACTIONS` is
set — read in full; it's a correct call (a CI secret was never pasted
anywhere, the warning doesn't apply), not a cover for anything.

**Risk read: low, and currently inert.** Scheduled (`schedule:`) workflows
only fire for commits on the repository's *default* branch — this is on
`claude/ict-trading-resources-ugh07b`, not `main`, so the cron will not
fire on its own until/unless this branch is merged. `workflow_dispatch`
could still be triggered manually by anyone with write access from the
Actions tab, but that's a deliberate human action, not something that just
happens. No secret is echoed, no exfiltration path, cost is capped, and the
commit it produces touches only data/log files, not code.

**Before merging this branch to `main`, re-review this workflow** — that's
the point at which it stops being inert. Until then it needs no action.
Does not change the recommendation to close out the other session's
further work on the shared branch; it changes *why* it was safe to still
be looking at this rather than disabling it on sight.

## Check 12: the GO_LIVE drift that wasn't net-vs-cash

Check 1 explained one drift (net mislabeled as cash, $19,570). Asked to check
for a second, separate one: two statements both correctly labelled "net,"
genuinely the same metric, still disagreeing. Could not find it by line
number in the current file (lines move every time this document is edited),
so searched history instead: `git log --all -S"19,570"` led to commit
`d1b8287` ("Run the three pre-purchase checks and write them down"), whose
`docs/GO_LIVE.md` has, at its own lines 158 and 189: a summary net of
**$42,414** (cost $17,314) and a 5-account table's 1-account row of
**$44,868** (cost $17,116, cash $61,984). Diff: $2,454 total, $198 of it
cost-side (cash diff alone is $2,256). Exact match to the numbers given.

Root cause, found by reading `scripts/recycling_report.py` and
`scripts/account_lifetime.py` side by side rather than guessing: the two
scripts can silently run under different policies. `account_lifetime.py`
has always hardcoded `POLICY = Policy.LOCK_FIRST` and passed it explicitly.
`recycling_report.py`'s `compute()` had three places that instead inherited
whatever `recycle()`'s or `run_row()`'s own *default* parameter happened to
be at the time — `bootstrap()`'s inner call, the by-calendar-year table, and
the straight-through "whole" total. At the time of commit `d1b8287`, those
implicit defaults evidently did not match `account_lifetime.py`'s explicit
constant (or the two scripts were reading different cached order sets —
not fully reconstructable this far back). This is `docs/ARTIFACT_CLASSES.md`
class 4 ("one claim, two parameterisations, no label"), and it was not a
one-time historical accident: the same implicit-default pattern was still
in `recycling_report.py` today, and it had already drifted internally a
second time — a comment claiming "the distribution is reported under the
default policy (IMMEDIATE)" went stale the moment `recycle()`'s own default
flipped to `LOCK_FIRST` earlier today, silently making the real/block/
shuffled comparison apples-to-oranges, and the by-year table was quietly on
`IMMEDIATE` while the straight-through total was on `LOCK_FIRST`.

**Fixed, not just ledgered**: every implicit-default call site in
`compute()` now takes an explicit `policy=` (see `FIGURES_LEDGER.md` #19 for
the before/after numbers). Checked today's output again afterward:
`recycling_report.py`'s 1-account net and `account_lifetime.py`'s 1-account
net agree to the dollar ($44,261 both), and they agree *because* both now
pin `Policy.LOCK_FIRST` explicitly rather than because their two separate
defaults happen to coincide this week. That coincidence is exactly what
broke in `d1b8287` and exactly what the fix removes.

## Check 13: does the business survive without 2026

2026 is the one year inside the 11-year window with an open question over
it (partial year, and the one year third-party trackers claim Topstep's own
rules changed). Reran the base case with 2026 excluded entirely
(`FIGURES_LEDGER.md` #18): `LOCK_FIRST` net **$31,404** over 2016-2025 alone,
against $44,261 for the full 11 years. 2026 (roughly 7-8% of elapsed time,
~7.6% of trades) accounts for **$12,857 of net — about 29% of the headline
total**. The business is real on 2016-2025 alone, and the policy conclusion
actually strengthens without 2026 (LOCK_FIRST's margin over IMMEDIATE grows
from $1,051 to $1,650). But the headline number is not representative of a
typical year: one partial, unusually strong year is doing close to a third
of the work. Worth carrying into any go/no-go decision as its own line, not
folded into "the 11-year net is $44,261."

## Check 14: does the stopping rule survive the history it was measured on

`scripts/reconcile.py`'s two stopping rules (`PAYOUT_DROUGHT_DAYS=239`,
`TRAILING_PF_MIN=0.70`) are both percentiles of this same 11-year run
(`FIGURES_LEDGER.md` #11). A percentile is silent about whether someone
actually holding the rule would have stopped trading before the run ever
produced the number the percentile is itself read off. Flagged directly:
the repo's own recorded longest dry spell is 1,184 days (`FIGURES_LEDGER.md`
#6, #15); a 239-day drought trigger and an 1,184-day drought cannot both be
true of someone who traded through the whole thing without stopping.

Pre-registered question: apply the stopping rule retroactively to
2016-2026, find every date it would have fired, and what net would have
been frozen there if trading never resumed. One of two things would have to
be true: (a) the rule is too tight and needs re-registering against the
observed drought distribution, or (b) the rule is right and the 11-year
headline is only achievable by trading through droughts that would not
actually be sat through. Instructed explicitly not to adjust the thresholds
to make (a) go away, and to commit the result either way.

Ran it (`scripts/stopping_rule_retroactive.py`, `FIGURES_LEDGER.md` #20).
Both rules fire for the first time in 2016 — eight months into the whole
project, and well before the first payout anywhere in the 11-year run
(2019-04-02):

| trigger | first fires | frozen net |
|---|---|---|
| `PAYOUT_DROUGHT_DAYS=239` (current) | 2016-08-30 | −$706 |
| `PAYOUT_DROUGHT_DAYS=213` (superseded) | 2016-08-04 | −$657 |
| `TRAILING_PF_MIN=0.70`, 100 trailing trades | 2016-08-17 | −$706 |

All three stop inside the 1,184-day dry spell, before it resolves. The
239-day drought trigger refires four more times later in the window
(2020-11-24 frozen $5,446; 2021-11-17 frozen $7,443; 2022-10-06 frozen
$8,052; 2026-05-09 frozen $30,307) — each is a point where a disciplined
trader following the rule as written, with no carve-out for "no payout has
ever happened yet," would stop and not see what comes after.

**Answer: (b), not (a).** The rule is not mismeasured or too tight; the
11-year headline net (`FIGURES_LEDGER.md` #15, #18) is only reachable by
sitting through a drought the project's own stopping rule says to exit.
Thresholds were not touched to make this disappear. This is the single most
decision-relevant fact to come out of this whole exercise: the backtest's
return depends on a tolerance for drawdown-without-payout that the project
has never actually tested on the person who would be holding the account —
only on the rule that says when to stop holding it.

## Check 15: every start date, every rule, and a stop that doesn't always fire

Check 14 tested one start date (2016-01-01) and two of reconcile.py's three
rules. `scripts/stopping_rule_all_starts.py` (`FIGURES_LEDGER.md` #21) tests
all 118 monthly start dates 2016-01..2025-10 with all three. Together they
stop **118/118**. `STOPPING_RULE=6` alone stops 118/118. Median net when
stopped: $496, 55% positive, against $37,647 and 100% for never stopping.

Why it can't be fixed by tuning: each threshold is a per-event 90th
percentile, checked continuously for years, so it fires almost surely. The
replacement is a **cumulative cash limit** (fees paid − payouts received),
whose false-alarm rate is measured over the whole horizon. −$3,000 fires on 6%
of starts, −$3,600 on none. The three percentile rules stay as review
signals. Recorded as binding in `docs/PRECOMMIT.md` ($3,600 set aside;
reaching it stops resets pending review).

Calendar months (`FIGURES_LEDGER.md` #22): 80% have no payout, median month
−$112, average +$340 (+$262 ex-2026). The strategy alone loses in 47% of
months; October 2026's forward-log 41.7% win rate is matched or worse in 20%
of backtested months.

Test count: **471 passed** on `965743a` (`uv run pytest`, run twice
2026-11-07). The "347" in the 965743a hand-off was wrong; the "336" at the top
of this file is from an earlier point on 2026-11-06.

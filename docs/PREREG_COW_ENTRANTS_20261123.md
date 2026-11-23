# #364 CoW solver rewards: do NEW solvers reach ≥ $15K/yr in their first year? (non-prop) — 2026-11-23

**Why.** #361 was killed by its Stage 1 rule (median recipient outside the top 5: $3,213/yr), but the same output shows a winner-take-most
pattern: the 10th-ranked recipient earned $176K–$345K/yr in every year. The question that matters for a newcomer is how solvers that
*started* during 2024–25 did in their first year. **Disclosure:** written after seeing #361's output (yearly top-15 lists and totals);
the entrant figures below have not been computed. Same data, no new fetch.

**Stage 0 (official onboarding page, fetched 2026-11-23 by run 45207594059).** Joining through the CoW DAO bonding pool needs KYC of a
**company** (incorporation details, shareholders, passports of the main shareholders and developers); path: shadow competition → KYC and
onboarding call → staging → production on BNB Chain → other L2s → mainnet after further evaluation; 25% of weekly rewards locked; 15%
service fee from month 7 (CIP-48). No country exclusion appears in the page text. It is an engineering business, not a deposit.

**Data.** `data/public/solverrelay_cow.parquet` (all 14,353 COW transfers out of the Solver Payouts Safe since 2024-01-01, Blockscout,
complete) priced daily as in #361.

**Rule.** Entrant = recipient whose first payout is on or after 2024-03-01 (not paid in Jan–Feb 2024) and on or before 2025-10-31 (a full
365 days observable to 2026-10-31). First-year earnings = USD received in the 365 days from the first payout, × 0.85 (the 15% fee
applied to the whole year: conservative). Active entrant = paid in ≥ 4 distinct weeks of its first year (filters one-off transfers).
Cohorts: A = first payout 2024-03-01..2024-12-31, B = 2025-01-01..2025-10-31.

**Stage 1 (kill only; cohort A).** KILL if fewer than 25% of active cohort-A entrants earned ≥ $15,000 in their first year.
**Stage 2 (cohorts A and B).** "Worth a no-money shadow-solver build test" only if, in **each** cohort, the **median** active entrant earned
≥ $15,000 in its first year. Otherwise FAIL.

**Honest limits.** Entrants that never won a reward never appear (survivorship: figures are upper bounds). A recipient address is not
always one team. Rewards earned on other chains may be paid from other addresses (not measured). Nothing here measures whether Jx (or the
friend) could build a solver that wins.

**Command.** `uv run python -m scripts.cow_entrants_20261123 | tee docs/jx_runs/cow_entrants_20261123.txt` (re-run once; must be identical).

### Results (2026-11-23; `docs/jx_runs/cow_entrants_20261123.txt`, identical on re-run)
13 incumbents (paid before 2024-03-01); 49 entrants 2024-03-01..2025-10-31.

| Cohort | Active entrants | First-year net (after 15% fee): 25th / median / 75th pct | ≥ $15K |
|---|---|---|---|
| A (2024-03..12) | 17 | $9,166 / $129,087 / $499,045 | 59% |
| B (2025-01..10) | 27 | $4,630 / $25,509 / $72,410 | 59% |

Stage 1: 59% ≥ 25% → survives. **Stage 2 (registered rule): median ≥ $15K in both cohorts → "worth a no-money shadow-solver build test".**

**Unregistered check (`docs/jx_runs/cow_entrants_check_20261123.txt`, identical on re-run).** Many "entrants" are existing solvers that
moved to a new payout address: 10 addresses were first paid on 2025-07-08 (one earned $4.19M in its first year, while two large 2024
recipients stopped being paid at the same time). Flagging addresses that start on a day with 3+ first payouts, or within 21 days after an
established recipient's last payout, leaves 7 unflagged entrants in cohort A (median $95,639; 57% ≥ $15K) and 4 in cohort B (median
$48,411; 75% ≥ $15K). The pass survives the check, but on 11 teams, and teams that tried and never won any reward are invisible, so the
figures are upper bounds on what a new solver earns.

**Reading.** CoW solving is the first non-prop role in the repo where newcomers' measured first-year income exceeds Jx's $15K/yr bar. It
is not a capped-loss ticket like prop: it is an engineering business (company KYC, a solver that out-bids professional teams in weekly
auctions, always-on hosting, starting on BNB Chain / L2s). The registered next step is a no-money shadow-competition test of a solver,
which needs a decision only Jx can make (who builds it — the friend or a hire; a company for KYC later; hosting cost).

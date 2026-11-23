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

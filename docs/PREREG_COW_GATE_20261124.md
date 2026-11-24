# #365 CoW solver gate tests: must pass before anyone builds a solver (non-prop) — 2026-11-24

**Why.** #364 met its registered rule (new solvers' first-year income above $15K/yr), on 11 genuine teams, with survivorship bias. Jx asked
for every required test to be passed before effort or money goes in. This file sets those tests. Written before reading the docs below and
before computing any figure here. **Disclosure:** #361's yearly top-15 lists (including 2026) and #364's entrant lists were already seen.

## Stage 0 — desk check (official CoW docs, read from the `cowprotocol/docs` GitHub repository on 2026-11-24)
Record, with quotes: (1) how solver rewards are computed and who funds them; (2) every cost a solver bears (gas, slippage, penalties,
service fee, locked rewards, bond); (3) KYC, company and country requirements; (4) the onboarding path and chains; (5) whether a no-money
test exists (shadow competition, local test harness, historical auction data).
**KILL** if: residents or companies of Malaysia are excluded; or joining needs Jx to post more than $50K of his own capital as a bond with
no pool option; or the rules forbid what a newcomer would need to do.

## Stage 1 — free data, kill only (any failure kills)
Data: `data/public/solverrelay_cow.parquet` (complete Blockscout listing, as #361/#364) plus a new Actions fetch `cow365`: COW transfers
**into** the Payouts Safe (repayments), and a sample of recent auctions from CoW's public solver-competition API on every network it serves.
- **(a) 2026 newcomers.** Genuine entrants = not flagged by #364's migration check (no same-day cluster of 3+ first payouts; no established
  recipient's last payout in the 21 days before) with first payout 2025-11-01..2026-08-31 and paid in ≥ 4 weeks. Measure = USD received
  from first payout to 2026-10-31, × 0.85, annualised. KILL if at least 3 such entrants exist and their median is < $15,000/yr. (Fewer than
  3: recorded as "not enough 2026 entrants", not a kill by itself.)
- **(b) Do newcomers last?** #364's genuine active entrants from 2024–25 (11): KILL if fewer than 30% earned ≥ $15,000/yr (annualised,
  × 0.85) in 2026-01-01..2026-10-31.
- **(c) Is the reward pool shrinking?** KILL if total USD paid in 2026-05-01..2026-10-31, annualised, is below 50% of 2025's total.
- **(d) Is the door open?** From ~30 days of recent auctions per network: KILL if on **every** network the top 3 solvers (by auctions won)
  win ≥ 95% of auctions that had a winner. Reported per network: auctions sampled, solvers bidding, distinct winners, top-3 and outside-top-5
  win shares.
- **(e) Context:** COW repaid into the Safe by recipients (net vs gross), payouts by quarter in COW and USD, the top recipient's share.

## Stage 2 — the real test (only if Stages 0–1 survive; needs Jx: a builder, and hosting money)
A solver run in CoW's no-money shadow competition (or an offline replay, if Stage 0 finds historical auction data) for 6 weeks. PASS only
if its would-have-won auctions imply ≥ $15,000/yr net after the 15% fee and hosting. A Stage 1 survival is **not** a pass.

**Costs.** Free public data. **Commands.** fetch: Actions job `cow365`; analysis:
`uv run python -m scripts.cow_gate_20261124 | tee docs/jx_runs/cow_gate_20261124.txt` (re-run once; must be identical).
**Honest limits.** As #364 (address ≠ team; migration flag is a heuristic; survivorship). The API sample is recent only. Nothing in Stages
0–1 shows that Jx's side can build a winning solver; only Stage 2 can.

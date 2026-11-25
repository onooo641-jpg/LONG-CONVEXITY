# #417 deBridge DLN takers (permissionless intent filling) — pre-registered 2026-11-25, before any order data are fetched

Why: Jx asked for more roles "like CoW solving (#364) and UniswapX quoting (#371)": a protocol pays a role, and real newcomers' income can
be measured in two independent periods. DLN (deBridge Liquidity Network) takers fill users' cross-chain orders from their own inventory and
keep the spread; the taker software is open source and the role is **permissionless** (no approval), unlike CoW and UniswapX. It was dismissed
at desk "by analogy" with Across (#373) without measurement.

**Data.** deBridge's public order API (`dln-api.debridge.finance` / `stats-api.dln.trade`, `POST /api/Orders/filteredList`), every
fulfilled order 2024-01..2026-10 with: creation and fulfilment time, give amount (USD), take amount (USD), protocol fees, taker address.
Stage 0 checks the fields exist; if the taker address or USD amounts are missing, the test is "not testable" (reported), not killed.
**Measure.** Per order, taker gross margin = give USD − take USD − protocol fees that do not go to the taker (fixed fee and percent fee as
the API reports them). Per taker: monthly volume and gross margin. Cost assumption for a newcomer: $3,000/yr (servers, RPC) + gas as the
API reports it (else 0, stated) — inventory capital is not charged but its size is reported (taker's median daily volume).
**Cohorts (independent periods).** Newcomer = a taker address whose first fill falls in the cohort year and that is not one of the top-5
takers by all-time volume in its first month (likely address migrations of incumbents are flagged and excluded, as in #364). Cohort A =
first fill in 2024, measured over its first 12 months; cohort B = first fill in 2025, first 12 months (2026 entrants reported as context).
**PASS (each cohort must pass — that is the out-of-sample check):** ≥ 3 newcomers, median first-year net ≥ $15,000, and the market shows
room (top-3 takers' share of margin < 90%). **KILL** if both cohorts' median first-year net < $5,000. Anything between = "inconclusive".
**Commands.** `uv run python -m scripts.solvers_20261125` → `docs/jx_runs/solvers_20261125.txt` (re-run identical). Data job `udln`.

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

# #418 UniswapX open fillers on Base (Priority reactor) — pre-registered 2026-11-25, before any per-fill income is computed
Sibling of #371 (same protocol), different access: on Base anyone may fill (priority-gas competition, no approval). Data in the repo:
`uniswapx371_base.parquet` (231,531 Fill events, 81 fillers, 2025-11-01..2026-10-31; ~27% of blocks missed by the scan — reported).
**Newcomers.** Fillers whose first fill is ≥ 14 days after the window start (so incumbents are not mistaken for entrants) and who are not a
top-5 filler by count in their first month. **Cohort A:** first fill 2025-11-15..2026-03-31; **cohort B:** first fill 2026-04-01..2026-07-31.
Each newcomer measured over its first 90 days.
**Income.** For each newcomer, up to 300 fills sampled evenly across its first 90 days: receipts give the swapper's token transfers (input
paid, output received) and the gas the filler paid (gasUsed × effectiveGasPrice); USD from DefiLlama hourly prices. Net per fill = input USD
− output USD − gas USD; scaled to all the filler's fills in the 90 days; annualised × 365/90; minus $3,000/yr infrastructure.
**PASS (both cohorts — the out-of-sample check):** ≥ 3 newcomers each with ≥ 30 sampled fills, median annualised net ≥ $15,000.
**KILL** if both cohorts' median < $5,000. Between = inconclusive. Data job `ubase418`; script `scripts/solvers_20261125.py` (part #418).

---
### #418 result — **KILL** (2026-11-26) — `uv run python -m scripts.solvers_20261125` → `docs/jx_runs/solvers_20261125.txt` (re-run identical)
Data: queue-2 fetch (65 newcomer fillers of 81; 2,237 receipts, 3,978 swapper transfers). 13 newcomers had ≥ 30 priced sampled fills.
Cohort A (first fill 2025-11-15..2026-03-31): 7 newcomers, **median annualised net $798**; cohort B (2026-04-01..07-31): 6 newcomers,
**median −$5,043** → both < $5,000 → KILL. One cohort-A entrant (0xa0e5…) became the largest Base filler (~$950K/yr on this measure), but
most entrants lost money after spread and gas; individual figures are noisy (transfer attribution), the medians are the registered measure.

## #417 addendum (2026-11-26, before any income is computed) — data access change, rule unchanged
Paging the full order history is too slow (60,900 orders = 5 weeks in 2.5 h; back to 2024 ≈ 55 h). The order API has no taker field;
`unlockAuthorityDst` (set by the taker when filling) is used as the taker identity, and USD values are not given. Changes, decided before
seeing any income: (1) **sampling** — blocks of 2,000 consecutive orders at evenly spaced offsets back to 2024-01 (`skip` = 0, 25,000,
50,000, …); per-taker volume and margin are scaled by the sample fraction of each period; a taker's first appearance is its first sampled
block (resolution ≈ the block spacing, reported). (2) **pricing** — orders whose give and take tokens are both in {USDC, USDT, DAI, ETH/WETH,
BNB/WBNB, SOL, BTC/WBTC/cbBTC, POL/MATIC, AVAX} are priced from DefiLlama daily prices; other orders are excluded and their share reported.
Margin per order = give USD − take USD − finalPercentFee − fixFee (USD). Pass/kill bars unchanged. Data job `udln2`.

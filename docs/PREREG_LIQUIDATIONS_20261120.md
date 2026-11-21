# PREREG: lending-liquidation bonuses on smaller venues (candidate #100)

Written 2026-11-20, before any liquidation data was fetched or looked at.
Owner question: is liquidating unhealthy loans on smaller lending venues a Topstep-shaped
opportunity (repeatable, long-lived, one reusable setup, capped downside, scales by copies)?

## Venues
In scope (all use the Aave v2/v3 `LiquidationCall` event, so one decoder covers them):
Aave v3 and Aave-v3 forks on Base, Arbitrum, Optimism, Polygon, Avalanche, BNB Chain, Gnosis,
Scroll, Metis. Method: query each chain's logs by event topic only (no address filter), so forks are
found automatically; a *venue* = (chain, emitting contract). Venues are labelled with a known name
where I know the address, else "unknown fork". Ethereum mainnet is excluded (known crowded, see HANDOFF).
Not in scope, stated up front, not because data was "unreachable" but because they need a different decoder
(per-market underlying/price mapping) and I will not guess: Compound v2 forks (Moonwell, Venus, Sonne),
Compound v3 (profit comes from `buyCollateral`, not the absorb event), and Solana lenders
(Kamino, MarginFi, Save, Drift). For Solana the fetch job only PROBES reachability of keyless
sources; unless a probe returns 24 months of liquidation events they are dropped and reported as
"unmeasured". Conclusions apply only to the measured venues.

## Window
24 full UTC months, 2024-11-01 00:00 to 2026-10-31 24:00. H1 = 2024-11..2025-10, H2 = 2025-11..2026-10.
Month boundaries are exact block numbers (first block with timestamp >= month start, by binary search).

## Data (free, no keys, via GitHub Actions job `liq` in scripts/fetch_public.py)
- Events: `eth_getLogs` on public RPC endpoints (several per chain, fallback), topic0 =
  `LiquidationCall(address,address,address,uint256,uint256,address,bool)`.
- Per event tx: `eth_getTransactionReceipt` -> tx `from`, gasUsed, effectiveGasPrice, L1 fee if present.
  Cap 40,000 receipts per chain; above that, a deterministic every-k-th sample, with gas imputed by the
  sample's per-event mean (flagged).
- Token decimals: `eth_call decimals()`. Prices: DefiLlama coins `chart` daily series (collateral, debt, native gas token).
Raw tables -> `data/public/liq_<chain>.parquet`, `liq_<chain>_prices.parquet`.

## Definitions (fixed now)
- Winner / "bot" = transaction `from` address (the operator). Sensitivity only: the `liquidator` field.
- Gross bonus USD = collateralAmount x price_collateral(day) - debtToCover x price_debt(day).
- Events with a missing price are excluded from value metrics (but counted; coverage reported).
  Events with bonus/collateral value outside [-2%, +30%] are treated as price errors and excluded (counted).
- Gas USD = (gasUsed x effectiveGasPrice + l1Fee) x native price(day); a tx's gas is split equally across the
  LiquidationCall events in it. Net = gross bonus - gas. Flash-loan fees, swap slippage, builder tips/bribes
  and reverted/lost attempts are NOT observable and are NOT subtracted in the primary test (they only lower
  true income; stated as an upward bias). Sensitivity row (no pass/fail): also subtract 0.09% of debt repaid.
- Per venue and month: liquidations, gross bonus USD, gas USD, unique bots, top-3 share and top-10 share of
  gross bonus, median net profit per liquidation. Top-3 / top-10 are chosen within each half by gross bonus.

## Pass criteria
A venue passes only if in BOTH halves:
 (a) top 3 bots win < 60% of gross bonus value in that half;
 (b) at least one liquidation in each of the 12 months;
 (c) net bonus (gross - gas) won by bots outside the top 3 averages >= $500/month in that half.
The idea passes overall if >= 3 venues pass AND their combined outside-top-3 net bonus averages
>= $2,000/month in BOTH halves.
Venues with < 20 liquidations in a half cannot pass (top-3 share is meaningless).

## Then
Apply the five-part filter in HANDOFF_NONPROP.md (repeatable, long-lived, one reusable setup, capped
downside per attempt, scales by adding copies) and give build / drop / unknown. If passing, write a
single-bot design. No spending, no deployment.
Realistic income is NOT the outside-top-3 total: a new bot would be one more competitor; the report will
give a per-bot estimate = outside-top-3 net / (number of outside-top-3 bots + 1) with the caveat that it is an estimate.

## Addendum 1 (2026-11-20, before any results were looked at)
Fetch infrastructure changed (HOW, not WHAT): one GitHub Actions job per chain (`fetch_liq.yml`), resumable from
`data/public/liq_<chain>_state.json`, 150-minute budget per job, progress committed every 20 minutes. Raw amounts
are stored as floats (int64 overflow for 18-decimal wei amounts); decimals/prices unchanged.
Clarification of WHAT is measured, so no result can move it:
- The window stays the full 24 months for every chain. No month sampling, no shortened window, no chain dropped for slowness.
- A chain whose log scan or receipt fetch is not finished after retries is reported as PARTIAL, with the last block
  reached. A partial chain cannot pass (criterion (b) needs all 12 months in each half) and is excluded from the
  overall count, but its partial data may be described, labelled as partial.
- The 40,000-receipt cap per chain is unchanged.
- Run 44739671810 (all chains in one job) was cancelled by Jx's instruction after ~94 minutes: it never left the
  first Base window (every `eth_getLogs` call failed) and its parquet save would have crashed on int64 overflow, so it
  saved no data. Its log is `docs/jx_runs/fetch_public_44739671810_cancelled.txt`. It DID contain the Solana probe:
  public RPC answered for Kamino, MarginFi, Save and Drift, but each program's latest 1,000 signatures cover only
  hours to ~3 months (Kamino 20 min, MarginFi 13 h, Save 1.5 days, Drift ~3 months), i.e. 24 months of history would need
  tens of thousands of paged calls plus per-transaction parsing of liquidation instructions. Solana lenders are therefore
  DROPPED and reported as unmeasured (as pre-registered), not tested.
- The cancelled run's HOW-failure (blocked/failed endpoints) led to a diagnostic job `liq_diag` (prints which
  endpoint answers which getLogs shape) and endpoint health-skipping in the fetcher. Endpoint list for Base lost
  `base.llamarpc.com` (returned HTTP 525). HOW-only changes.

## Addendum 2 (2026-11-20, before any results were looked at; no liquidation data analysed yet)
Endpoint diagnostics (`docs/jx_runs/fetch_public_44754595913.txt`, `_44755511966.txt`, `_44756530502.txt`) found free
public endpoints with full history for: Gnosis, Scroll, Metis, Optimism, Arbitrum (topic-only), and Base, Polygon, Avalanche
(topic-only; Base/Polygon via Pocket + Tenderly, Avalanche via Tenderly). BNB Chain: none (publicnode 403 on old blocks,
the other candidates rate-limited, forbidden or capped). The `ETHERSCAN_API_KEY` secret is NOT set (checked by job
`liq_secretcheck`, `docs/jx_runs/fetch_public_44757024529.txt`), so:
- **BNB Chain: UNMEASURED.** No substitute data. Steps for Jx to enable it are in `docs/NOTES_JX.md` ("Action for Jx").
- No contract-address restriction is used on any chain (topic-only scans, so forks are included automatically). Forks left out: none
  by selection. Venues outside the Aave `LiquidationCall` ABI (Compound v2/v3 forks, Solana lenders) remain unmeasured as in the original.
- Months and window unchanged (24 months). Chains that do not finish are recorded PARTIAL: re-run until finished or until three
  consecutive runs add < 5% more blocks. Partial/unmeasured chains cannot pass and do not count toward the 3-venue requirement.
- Verdict wording: BUILD / DROP / NOT YET DECIDABLE. NOT YET DECIDABLE only if so few chains are measured that the result could
  change with the missing chains (stated explicitly).

## Addendum 3 (2026-11-21; written after one look at the per-chain COVERAGE lines only, before looking at any venue pass/fail result)
First analysis run (`docs/jx_runs/liquidations_20261120.txt` as first generated; it will be overwritten by the final run) showed two data-quality
problems, both unrelated to pass/fail:
1. Token decimals: `eth_call decimals()` failed for some tokens (Scroll: all; Metis, Gnosis: some), so those events had no USD value. Fix (HOW): job
   `liq_decimals` retries the call and falls back to DefiLlama's `decimals` field; analysis merges `liq_<chain>_decimals.parquet`. No change to WHAT is measured.
2. Polygon exceeded the 40,000-receipt cap (49,466 txs), so every 2nd tx got a receipt (pre-registered cap). Unsampled events have no bot identity.
   Handling (fixed now, applies to any capped chain): bot-based metrics (top-3/top-10 share, outside-top-3 net, bot counts) use ONLY events whose tx has a
   receipt (a uniform deterministic half-sample); dollar sums are scaled by (events / events with receipt) for that chain; shares and medians are not scaled;
   bot counts are lower bounds for sampled chains. The earlier code lumped unsampled events into one "unknown_sampled" bot, which would have made the
   top-3 share meaningless; that behaviour is dropped.
Unpriced tokens (no DefiLlama price) stay excluded from value metrics; coverage is reported per chain and unpriced share is listed.

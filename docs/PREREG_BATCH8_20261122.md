# Batch 8: 12 new non-prop mechanisms (#279–#290) — 2026-11-22

Written and committed before any batch-8 data is fetched. Same framework as batches 4–6: Stage 0 desk check (below), **Stage 1 pilot on the last
~4 months only** (fetch job `batch8p`, window 2026-07-01..2026-11-01, judged on 2026-08..10, **KILL if < 4%/yr on capital**, kill-only),
Stage 2 full history (2024-11..2026-10 or venue start; **PASS = both halves ≥ 8%/yr on capital, ≥ 180 days of data**). Stage-1 survivors get a
full-history fetch (job registered by addendum before it runs, rules unchanged). Never spend money; no accounts.
Stage 0 (all 12): permissionless DeFi or public-API venues, no KYC needed to read data; Malaysia: DeFi front-ends not geoblocked for MY (verified
only for HL/dYdX/Aevo in earlier work; Drift, Orderly, Kamino, Aave, Morpho, Boros assumed); **Deribit: Malaysia access assumed, not verified**.

| # | mechanism | data (public API) | exact rule |
|---|---|---|---|
| 279 | funding gaps Drift ↔ HL/dYdX | Drift data API funding records | #208 rule (`scripts/fundgap_20261121.py` run(): entry ≥ 15%/yr gap on prior 24 h, ≤ 5 slots, 3× leverage, 5 bps per leg-side); Drift hourly rate = fundingRate/1e9 ÷ (oraclePriceTwap/1e6) |
| 280 | funding gaps Deribit ↔ HL/dYdX | Deribit get_funding_rate_history (interest_1h) | #208 rule; Deribit pairs BTC, ETH (inverse) and USDC linear perps |
| 289 | funding gaps Orderly ↔ HL/dYdX | Orderly public funding_rate_history | #208 rule; 8-hour rate spread over 8 h |
| 284 | HL HIP-3 builder perps: cross-dex gaps on the same underlying | HL perpDexs + fundingHistory "dex:COIN" | #208 rule over all pairs of dexes listing the same name (incl. main HL for crypto names) |
| 281 | Deribit quarterly futures cash-and-carry | Deribit chart data (futures, perpetual as spot proxy) | each day hold the nearest future with ≥ 30 days left: long spot + short future; return = annualised basis at entry, locked to expiry; costs 0.1% per roll; ÷ 4/3 for margin |
| 282 | Deribit short ATM straddle (volatility risk premium) | Deribit DVOL index + perpetual daily closes | ladder: each day sell a 30-day ATM straddle on 1/30 of capital (BTC and ETH, equal), Black-Scholes price at σ = DVOL; payoff |S_T − K| at expiry; fees 0.06% of underlying; capital = underlying notional (no leverage) |
| 283 | Pendle Boros fixed-vs-floating funding | probe only | if a history endpoint answers: rule registered by addendum before analysis; else not testable |
| 285 | Kamino SOL-LST loops (JitoSOL, mSOL, JupSOL / SOL) | Kamino reserve metrics history; LST/SOL price ratio (DefiLlama coins) | #219 rule: k = min(1/(1 − 0.8·LTV), 6), ROE = s + (k−1)(s − b), s = intrinsic LST yield (trailing 30-day price-ratio growth) + supply APY, b = SOL borrow APY; monthly top-5 by trailing 30-day ROE, TVL ≥ $20M; stress: ratio −5% in 7 days → −10%·k; $20 per change on $2K slot |
| 286 | Aave v3 e-mode loops (wstETH, weETH / WETH; sUSDe / USDT, USDC) | Aave rates-history API; price ratios (DefiLlama coins) | as #285 with Aave reserves (Ethereum, Arbitrum, Base) |
| 287 | Morpho Blue collateral loops (LST/ETH, sUSDe-type/USD) | Morpho GraphQL market historicalState | as #285; collateral earns intrinsic yield only; LTV = lltv |
| 288 | Hyperliquid user vaults, follow the top performers | HL stats-data vault list + vaultDetails | monthly top-5 by trailing-90-day return among vaults with TVL ≥ $1M and age ≥ 180 days (closed vaults included when listed), equal weight; follower keeps 90% of positive monthly P&L (10% leader share) |
| 290 | Morpho curated USDC/USDT vaults by share price | Morpho GraphQL vault historicalState sharePriceUsd | monthly top-5 by trailing-30-day share-price return, TVL ≥ $20M, age ≥ 90 days; return = share-price change; $10 per switch on $2K slot |

Commands: `uv run python scripts/batch8_20261122.py | tee docs/jx_runs/batch8_20261122.txt`. Data: `data/public/batch8_*`.

## Stage 1 results (2026-11-22; `docs/jx_runs/batch8_20261122.txt`, identical on re-run)
| # | Stage 1 (2026-08..10) | outcome |
|---|---|---|
| 280 Deribit ↔ HL/dYdX gaps | 12.72%/yr, 41 positions opened | → Stage 2 |
| 288 HL user vaults top-5 | 27.30%/yr (months +11.7%, +19.2%, −24.0%); current-list survivorship | → Stage 2 (survivorship removed) |
| 284 HIP-3 cross-dex gaps | −2.08% (178 of 247 markets fetched; rest rate-limited) | KILL |
| 281 Deribit cash-and-carry | 2.62% | KILL |
| 282 short straddle ladder | −30.81% | KILL |
| 285 Kamino SOL-LST loops | −4.13% (intrinsic 3.5% < SOL borrow 6.6%) | KILL. A first run used best-of-3 per day (look-ahead, not the registered rule); corrected to the registered monthly top-5 before recording |
| 279, 283, 286, 287, 290 | no data (Drift DNS, Boros no endpoint, Aave API retired, Morpho 400/403); 289 Orderly 0 rows | not testable; one repair probe below |

## Addendum 1: Stage 2 for #280 and #288, written before job `batch8s` runs (rules unchanged)
- **#280:** Deribit funding for the same 10 coins, 2024-11-01..2026-11-01. HL/dYdX from `fundgap_funding.parquet`. `fundgap_20261121.report()` verdict:
  both halves ≥ 8% plus its representativeness check. Context only: the HL–Deribit pair alone (dYdX failed the batch-7 execution check).
  Execution check, same reading as batch 7 C: 6 Deribit order-book snapshots, 10 minutes apart. A median $10K slippage above 2.5 bps per side
  on the coins used means the return is not reachable.
- **#288:** removes survivorship. vaultDetails for every listed vault created before 2026-05-01 that is either closed or has a current TVL
  ≥ $50K (cap 3,000, ≤ 1 request/s). Selection uses each vault's own account value on the selection date (≥ $1M), not today's TVL. Same rule
  as Stage 1 (top 5 by trailing 90 days, 10% leader share). Period 2024-11..2026-10. PASS = both halves ≥ 8%.
- **Repair probe** (fetch only; any test stays registered as above): Drift public S3 historical funding records, Orderly endpoint variants,
  a minimal Morpho GraphQL query.

## Addendum 2: compliance audit (2026-11-22, before the Stage 2 results)
The five-part filter (PREREG_RADAR F1–F5) was not applied idea by idea at Stage 0 of batches 7–8. Applied now, for the two Stage-2 candidates:
| # | F1 repeatable | F2 long-lived | F3 reused setup | F4 capped downside | F5 scales by copies | facts |
|---|---|---|---|---|---|---|
| 280 | yes (funding settles hourly) | yes (Deribit 2016, HL 2023) | yes (10 coins × 2 venue pairs) | partial: delta-neutral, but venue and liquidation risk | **unknown**: depends on Deribit book depth (Stage 2 execution check) | funding data verified (venue APIs); Deribit Malaysia access **assumed** |
| 288 | yes | mixed (vaults 6–24 months old) | yes | **FAIL**: vault returns carry trading losses (−24% in one month) | small (13 eligible vaults ≥ $1M) | data verified (HL API); leader share 10% verified per vault |
**Consequence:** #288 cannot be flagged even if Stage 2 passes; it would stay a near-miss (F4). #280 can be flagged only if its execution
check also passes. Other deviations so far: the fetches use `scripts/fetch_fallback.py` (its own GitHub Actions workflow, same mechanism as
`fetch_public.py`); the first #285 run did not follow the registered rule and was corrected before recording; the #288 Stage-2 universe change
(adding closed vaults) was written after the pilot. It only makes the test harder; the selection rule is unchanged.

## Stage 2 results (2026-11-22; `docs/jx_runs/batch8s_20261122.txt`, identical on re-run)
- **#280 Deribit ↔ HL/dYdX: registered return test PASS (16.28% / 9.86%); execution reading FAILS → not flaggable.** The pooled return
  relies on dYdX (batch 7: $10K costs 23 bps per side) and on six Deribit alt perps whose $10K slippage is 2.5–4.2 bps per side (over budget).
  Only BTC, ETH, SOL and XRP execute within budget on Deribit. HL–Deribit restricted to those four coins earns −1.42% / −0.17%; the HL–Deribit
  pair on all coins earns 7.17% / 5.73%. As with #208, the modelled gap is not reachable at $10K per leg.
- **#288 HL user vaults without survivorship: FAIL** (−5.60% / −4.86%; worst month −35.3%; 11 negative months). 3,000 vaults, 2,923 closed.
  The Stage 1 figure (27.3%) came from survivors.
- Repair probes: Orderly funding history answers without time parameters; the minimal Morpho GraphQL query answers (the batch-8 queries had
  schema errors); Drift S3 404. → #289, #287, #290 become testable in a later fetch; #279 stays not testable.

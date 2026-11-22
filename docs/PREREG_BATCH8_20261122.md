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

# Batch 6: 20 non-prop mechanisms not yet covered (#259–#278) — 2026-11-22

Written and committed before the batch-6 fetch. Staged per CLAUDE.md + PREREG_RADAR addendum 7: **Stage 0** desk check (rules, Malaysia,
five-part filter) → **Stage 0.5** ceiling from current/recent data, most favourable values, kill if < 8%/yr on capital → **Stage 1** last 90 days
realised, kill < 4% → **Stage 2** full history, PASS ≥ 8%/yr both halves (≥ 180 days). Kill-only stages; a high ceiling never counts as a pass.
Data in hand: `llama_pools_now` (2026-11-20), `hl_funding` (to 2026-11-19), `hedged_hlfunding`, `batch5_hlfunding`, `lendborrow_now`. New fetch:
`scripts/fetch_fallback.py batch6` (Paradex market summaries, Lighter funding 90 d, DefiLlama holders-revenue overview + protocol market caps, Drift /
Aave Umbrella / Votium source probes, Yahoo BTC=F and BTC-USD 120 d, coin prices of tranche tokens).

| # | mechanism (who pays) | Stage 0.5 ceiling rule (capital basis) |
|---|---|---|
| 259 | Paradex vs Hyperliquid funding gap; Paradex charges retail 0 fees | 1.5 × max over coins of |Paradex current funding − HL 90-d funding| (annualised; capital 2/3 of notional as #208) |
| 260 | Lighter vs Hyperliquid funding gap; Lighter 0 fees | 1.5 × max over coins of |Lighter 90-d − HL 90-d| |
| 261 | Zero-fee single-venue carry (spot + short perp) on Paradex / Lighter | mean of best 3 coins' 90-d short funding ÷ 1.333 |
| 262 | Real-yield staking, hedged: protocols paying fee revenue to stakers (DefiLlama "holders revenue"), short the token on HL | per token: 365 × 30-d mean holders revenue ÷ (0.3 × market cap) [optimistic: assumes only 30% staked] + HL 90-d short funding, ÷ 1.333; best token |
| 263 | Junior / loss-absorbing tranches (Strata jrUSDe/jrUSDat, Resolv RLP, Reflect) | best current APY (snapshot); Stage 1 uses token price change, not APY |
| 264 | Senior tranches (Strata srUSDe / srUSDat) | best current APY; Stage 1 price-adjusted |
| 265 | Drift insurance-fund staking (USDC; fees + liquidation surplus) | current APY from Drift's API if it answers, else not testable |
| 266 | Aave Umbrella staking (aTokens staked as insurance) | current APY from a public source if it answers, else not testable |
| 267 | Bribe markets: vlCVX votes paid on Votium | current bribe APR (llama.airforce) − 0 (CVX unhedgeable on HL → Stage 1 includes CVX price) |
| 268 | Aerodrome veAERO voting rewards, hedged with HL AERO short | Stage 0: 4-year lock; exit only by selling the veNFT at an unknown discount → F4 unverifiable → KILL unless a price history of veNFT discounts exists (none known) |
| 269 | Tokenised T-bill / RWA yield tokens (USYC, USDY, BUIDL, USTB...) | best snapshot yield |
| 270 | On-chain fixed-rate auctions (TermMax) | best snapshot yield with TVL ≥ $1M |
| 271 | CME Bitcoin futures basis (cash-and-carry through a broker) | 90-d mean annualised (BTC=F − BTC-USD)/BTC-USD × 365/days-to-roll ≈ use front-month basis ÷ 30 d × 365; capital = spot + 40% margin → ÷ 1.4 |
| 272 | Tokenised-stock premium arbitrage (xStocks etc.) | Stage 0: securities access for a Malaysian resident / US-person rules unverified → grey → KILL |
| 273 | Solana LST instant-unstake spreads | Stage 0: instant-unstake pools (Sanctum) arbitrage the discount by design; #41 found LST discounts worth ~$40–50/yr per $10K → KILL unless the snapshot shows an LST > 1% below its stake-pool value (not available) |
| 274 | Hedged volatile LP (Uniswap v3 WETH-USDC fee APR) | Stage 0: concentrated-range impermanent loss / LVR cannot be modelled from daily APY data → not testable faithfully (no verdict) |
| 275 | Bridge / intent relayers (Across etc.) | Stage 0: professional fillers, bonded capital, speed race (as M10) → KILL |
| 276 | Native HYPE staking, hedged with an HL HYPE short | staking APR (assumed 2.5%, Hyperliquid docs third-party) + HYPE 90-d short funding (hedged_hlfunding) ÷ 1.333 |
| 277 | Reverse carry: long perp where funding is negative, short spot by borrowing it | best coin: |HL 90-d funding| (negative side) − current borrow APR of that token (lendborrow_now), ÷ 1.333 |
| 278 | New-chain bootstrapping incentives (stablecoin pools on chains launched ≤ 12 months ago: Monad, Plasma, Stable, MegaETH...) | top-5 mean stable yield (TVL ≥ $5M) on those chains in the snapshot |
Survivors of Stage 0.5 get Stage-1 (90-day) data in a second fetch, then Stage 2 only if they survive. Commands: `uv run python
scripts/batch6_20261122.py | tee docs/jx_runs/batch6_20261122.txt`.

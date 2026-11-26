# Batch A (#419–#421): high-potential, permissionless ideas — pre-registered 2026-11-26, before their data are fetched

Screen applied before testing (Jx, 2026-11-26): permissionless (no approval/onboarding), usable from Malaysia, a structural payer, plausibly
≥ $10K/yr on ~$15K, free data with an out-of-sample period. Stage 1 = in-sample kill-only; Stage 2 = out-of-sample PASS bar. $15,000 pot.

## #419 Crypto variance risk premium: weekly short ATM straddles (Derive on-chain options), BTC and ETH
**Data.** Deribit DVOL (30-day implied vol index) daily for BTC and ETH (public API) 2021-04..2026-10; Binance daily closes
(`uncharted_389_binance_ohlc`). **Rule.** Every Monday close: sell a 7-day ATM straddle on BTC and on ETH (half the pot each); premium =
0.8 × S × DVOL × √(7/365) (Black-Scholes ATM approximation) × 0.90 (a 10% haircut for Derive's spread/fees and for DVOL being a 30-day,
not 7-day, volatility); payoff at expiry = |S₇ − S₀|; no delta hedge (conservative for a small account). Size: notional per leg such that a
5-sigma weekly move (from DVOL) loses at most 25% of that leg's capital. **Stage 1 (2021-04..2023-12):** KILL if annualised < 15% or
worst drawdown < −50%. **Stage 2 (out-of-sample 2024-01..2026-10):** PASS if annualised ≥ 25%, worst drawdown ≥ −35%, t ≥ 2 on weekly
returns. Stage 0: Derive's terms must not exclude Malaysia (checked and reported).

## #420 Perp-DEX reward farming where rewards exceed fees (dYdX v4 trading rewards), hedged on Hyperliquid
**Data.** dYdX indexer public endpoints (trading-reward aggregations, fees) and DYDX price; Stage 0 checks that the protocol-wide reward and
fee totals per period are obtainable without listing addresses. **Rule.** Reward-to-fee ratio per month = total DYDX rewards (USD at that
month's price) ÷ total taker+maker fees. A farmer doing hedged volume (long dYdX, short Hyperliquid, flat price risk) earns, per $1M volume,
ratio × dYdX fee − dYdX fee − Hyperliquid fee (0.045%) − 0.02% spread; cap at the volume a $15K account can carry (5× leverage, 2 round
trips/day = $150K/day). **Stage 1 (2024):** KILL if the median month's net per $1M volume ≤ 0. **Stage 2 (2025-01..2026-10):** PASS if
≥ 70% of months are positive and the annualised net at the capped volume ≥ $10,000. If Stage 0 fails: not testable (reported).

## #421 Withdrawal-queue discounts vs the protocols' real on-chain exchange rates
**Data.** Daily eth_call at historical blocks (block by timestamp from Blockscout; archive RPCs incl. Blockscout's eth-rpc proxy):
weETH `getRate()`, sUSDe `convertToAssets(1e18)`, pufETH `convertToAssets(1e18)`, rsETH LRTOracle `rsETHPrice()`; market prices = hourly
CoinGecko prices already fetched (`distinct_nav_1h`), underlying ETH/USDe. **Rule.** #415 unchanged except NAV = the on-chain rate (daily,
held constant within the day): event = market ≤ NAV × 0.99; buy $5,000; redeem after 7 days at the on-chain rate then; costs 0.10% + lost
yield. **Stage 1 (2024):** KILL if < 4 events or < $3,000/yr. **Stage 2 (2025-01..2026-10):** PASS if ≥ 4 events, ≥ $3,000/yr and ≥ 75%
profitable. (This bar is below $10K: kept because the mechanism is near-riskless if real; reported as "useful, not prop-like" if it passes.)

**Commands.** `uv run python -m scripts.batch_a_20261126` → `docs/jx_runs/batch_a_20261126.txt` (re-run identical). Data job `ubatcha`.

---
## Results (2026-11-26) — `uv run python -m scripts.batch_a_20261126` → `docs/jx_runs/batch_a_20261126.txt`
- **#419 crypto VRP — KILL.** DVOL 2,076 days per coin; mean IV BTC 60%, ETH 74%. Stage 1 (2021-04..2023-12): 144 weeks, +0.19%/week,
  t 0.75, **7.5%/yr** (< 15%), worst drawdown −24.6%. Context Stage 2: −17.0%/yr, drawdown −47.1%. Derive's terms do not name Malaysia.
- **#420 dYdX reward farming — NOT TESTABLE (Stage 0):** the indexer gives trading rewards per address only (no protocol-wide totals);
  DefiLlama gives fees but derivatives volume is now paid (HTTP 402).
- **#421 — the printed "PASS" is INVALID:** the rate fetch stalled after 6 dates (Blockscout block-by-time lookups), so the on-chain rate
  was carried forward from January 2024 for two years and the Stage 2 "+68% mean" is an artefact. Re-fetch (estimated block numbers, no
  per-day lookup) and re-run; rule unchanged.

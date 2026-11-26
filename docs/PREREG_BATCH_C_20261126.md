# Batch C (#429–#438): ten ideas, designed from Batches A–B — pre-registered 2026-11-26, before their data are fetched

Lessons applied: what passed is liquidity to forced/frictional flows (wick family on 4 venues); what failed is behavioural fades out of
sample, carry/yield, concentrated solver roles, vault APYs. So Batch C is weighted to frictions and true-value anchors. All permissionless,
usable from Malaysia, structural payer, out-of-sample split fixed here. $15,000 pot. Data job `ubatchc`; script `scripts/batch_c_20261126.py`.
Stage 1 = in-sample kill-only; Stage 2 = out-of-sample PASS. Event studies: hedged with BTC where stated, 0.045%/side, funding where available.

| # | Idea (payer) | Data | Rule | Stage 1 (kill) | Stage 2 (PASS) |
|---|---|---|---|---|---|
| 429 | Fiat-backed stablecoin depeg buying (panic sellers; redemption at $1 is a true anchor) — USDC, USDT, FDUSD, PYUSD, TUSD, BUSD, USDP | DefiLlama hourly CoinGecko prices 2020–2026 | buy $5,000 when hourly price ≤ 0.98; sell at the first hour ≥ 0.997 or after 30 days; 0.1% costs | 2020-01..2022-12: KILL if < 3 events or mean ≤ 0 | 2023-01..2026-10: PASS if ≥ 3 events, mean ≥ +1%, ≥ 75% profitable |
| 430 | Crypto-backed/synthetic stable depegs (DAI, USDe, FRAX, crvUSD, GHO, LUSD, USDD, USD0, USDS) | same | same rule, buy at ≤ 0.97 | same split | same bar |
| 431 | Binance deposit/withdrawal suspension convergence (arbitrage blocked → prices drift apart) | Binance "wallet maintenance" announcements + Binance and Hyperliquid daily closes | during a suspension of ≥ 1 day, if HL close differs from Binance close by ≥ 2%, trade HL toward Binance; exit at the first close after resumption | 2023–2024: KILL if ≥ 10 events and mean < 0.5% | 2025–2026: PASS if ≥ 10 events, mean ≥ 1%, t ≥ 2 |
| 432 | Funding-sentiment extreme, BTC (crowded shorts market-wide → squeeze) | Binance funding 2020–26; median daily funding across the top-50 perps | when the median falls below its trailing-365-day 5th percentile, long BTC 7 days; above the 95th, short BTC 7 days | 2020–2022: KILL if mean < 0.5% or t < 1 | 2023–2026: PASS if ≥ 10 events, mean ≥ 1.5%, t ≥ 2 |
| 433 | Same signal, ETH | same | same | same | same |
| 434 | BTC CME weekend-gap fill (CME's Friday 21:00–Sunday 22:00 UTC gap) | Binance BTCUSDT 1h archive | at Sunday 22:00 UTC, if price is ≥ 1.5% from Friday 21:00, trade toward the Friday price; exit at the gap fill or Wednesday 22:00 | 2020–2022: KILL if mean < 0.3% or t < 1 | 2023–2026: PASS if ≥ 30 events, mean ≥ 0.5%, t ≥ 2 |
| 435 | Same, ETH (ETHUSDT 1h) | same | same | same | same |
| 436 | HIP-3 commodity perps weekend fade (gold/silver/oil trade on Hyperliquid while CME is shut) | `fivehigh_hip3_1d` | if the Saturday+Sunday move ≥ 2%, fade it from Sunday close to Monday close | first half of history: KILL if mean ≤ 0 | second half: PASS if ≥ 15 events, mean ≥ 0.5%, t ≥ 2 |
| 437 | HIP-3 stock-index perps weekend fade (same rule on index/stock perps) | same | same | same | same |
| 438 | Token-split / redenomination arbitrage (1000x tickers re-based, migrations) | Binance announcements | — | desk: events too few and conversion is exchange-handled; recorded as not testable | — |

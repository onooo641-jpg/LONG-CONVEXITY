# Sweep 4: memecoins, crypto index products, index events and other uncharted mechanisms (#330–#346) — 2026-11-22

Jx: "find 15+ more, same criteria; did you check memecoins, crypto index funds, etc.?" Written and committed before any sweep-4 data is fetched
(job `sweep4`). Same pipeline: Stage 0 desk check (rules, Malaysia, five-part filter, free data) → **Stage 1 kill-only pilot** → Stage 2 full
test. **Event studies:** Stage 1 KILL if the mean net return per event ≤ 0 (≤ 0.2% for the stock-index ones). Stage 2 PASS = mean net > 0.5% per
event AND t-stat > 2 AND both halves positive AND ≥ 8%/yr on capital (one position at a time, overlapping events equal-weighted). **Rotations:**
Stage 1 KILL < 4%/yr; Stage 2 PASS = both halves ≥ 8%/yr. Costs as stated per row. No money spent; no accounts.

| # | mechanism | why it might be structural | data (free) | Stage 1 rule | Stage 0 |
|---|---|---|---|---|---|
| 330 | **Memecoin bonding-curve graduation** (pump.fun tokens migrating to their AMM) | forced liquidity event; curve-to-AMM handover | pump.fun public coin list (complete = true) + GeckoTerminal OHLCV of the migrated pool | buy 1 h after migration, sell 24 h later; 2% round-trip costs (thin pools) | → test (data probe) |
| 331 | Memecoin graduation fade (short) | same event, opposite side | — | — | excluded: graduated memecoins cannot be shorted (no perps) |
| 332 | **Crypto index-token NAV discount** (Index Coop-type tokens, redeemable on-chain) | redemption at NAV caps the discount | DefiLlama coins (token price) + issuer API probe for NAV | buy when price < NAV − 1%, redeem; gain = discount − 0.3% | → test if a NAV source answers |
| 333 | Crypto index rebalancing additions (CoinDesk 20, Coinbase 50, Bitwise 10) | index funds must buy added tokens | constituent-change history | — | parked: no free change history found |
| 334 | **Coinbase spot listing effect** on Hyperliquid perps | new US retail access on the listing day | Coinbase Exchange products + candles (first trading day), HL daily candles | short the HL perp at the listing-day close, cover 7 days later, BTC hedge β = 1; 10 bps | → test |
| 335 | **Token buyback-yield rotation** (protocols buying their own token with revenue) | a mechanical, revenue-funded bid | DefiLlama fees (dailyHoldersRevenue) per protocol + token prices | monthly long the top-5 by trailing-30-day buyback ÷ market cap (mcap ∝ price, supply held at today's), short BTC 1:1; 10 bps per switch; ≥ $50M mcap | → test |
| 336 | **Nasdaq-100 additions** (December reconstitution + replacements) | forced buying by QQQ and peers | Wikipedia Nasdaq-100 article (changes) + Yahoo | as #303: t−5 close → effective close, minus QQQ, 10 bps | → test |
| 337 | **S&P 500 deletions rebound** (forced selling overshoots) | index funds must sell on the effective date | Wikipedia "Historical components of the S&P 500" + Yahoo | buy at the effective-date close, sell 20 trading days later, minus SPY, 10 bps | → test |
| 338 | **Spin-off forced-selling rebound** | parent-index holders dump the spun-off stock | Wikipedia spin-off lists + Yahoo | buy at the close of day 5 after the spin-off, hold 60 trading days, minus SPY, 10 bps | → test if a list parses |
| 339 | **Tokenised-gold premium / discount** (PAXG, XAUT vs gold futures) | mint / redeem at the issuer caps the spread | DefiLlama coins + Yahoo GC=F | days with |premium| > 1% and the size; KILL if < 12 days a year or mean excess < 0.3% | → test (monetising needs issuer KYC: Malaysia not verified) |
| 340 | Liquid-restaking-token depegs (ezETH, rsETH) | withdrawal queue caps the discount | — | — | folded into #273 (tested) |
| 341 | Crypto-treasury company mNAV mean reversion (MSTR-type) | — | — | — | excluded: a valuation pair trade, not structural |
| 342 | **Token-unlock shorts** (#304 retry with a per-protocol schedule source) | scheduled supply | DefiLlama emissions datasets (probe) + HL candles | as #304: short 7 d before an unlock ≥ 1% of supply, cover 7 d after, BTC hedge; 10 bps | → test if schedules parse |
| 343 | **Alt spot-ETF launch events** (SOL, XRP, … ETFs) | first US ETF access | ETF launch dates (Wikipedia) + HL candles | short at the launch-day close, cover 10 days later, BTC hedge; 10 bps | → test (few events) |
| 344 | **Pre-IPO perp → IPO convergence** (HIP-3 pre-IPO perps) | the perp must converge to the listed price | HIP-3 candles + Yahoo first trade | perp premium vs the first listed close; report n and mean gap | → test (few events) |
| 345 | Memecoin creator / launch rewards | — | — | — | excluded: creativity-dependent (launching and promoting tokens) |
| 346 | Memecoin sniping / copy-trading top wallets | — | — | — | excluded: bot race / not structural |
**Count:** 17 mechanisms; 11 go to tests (#330, #332, #334–#339, #342–#344, with #332 / #338 / #342 conditional on data); 1 parked (#333); 4 excluded (#331, #341, #345, #346); #340 folded into #273.
Malaysia: DeFi and US stocks via a broker such as IBKR (assumed); pump.fun front-end access from Malaysia **not verified**.
Command: `uv run python -m scripts.sweep4_20261122 | tee docs/jx_runs/sweep4_20261122.txt`.

## Addendum 1 (2026-11-22, after the first fetch; rules unchanged): data status and follow-up job `sweep4b`
First fetch: 910 graduated pump.fun coins (196 migrated pools with hourly OHLCV), 136 Coinbase USD products listed on HL, 84 buyback protocols,
tokenised-gold prices. **#332 not testable** (no index-token NAV source answered). **#338 not testable** (no spin-off list on Wikipedia).
**#343 not testable** (crypto-ETF article returned no text). **#336 not testable** (the Nasdaq-100 article has no change table). **#344 not
testable** (no pre-IPO HIP-3 name listed on an exchange in the window). The ticker pattern missed the S&P change table's format, and the unlock
schedules were truncated, so job `sweep4b` fetches Yahoo prices for every S&P 500 change since 2024-10 (#337; the table also gives S&P's
announcement dates, which allows a proper look-ahead check of #303) and slimmed unlock schedules with HL candles (#342).
Event-study Stage 1 slice (fixed before any sweep-4 analysis is run): events in 2026-05-01..2026-10-31; Stage 2: all events 2024-11-01..2026-10-31
(halves split 2025-11-01).

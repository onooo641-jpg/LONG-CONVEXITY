# Uncharted batch: tests U-T1 to U-T5 (#383–#387) — pre-registered 2026-11-25, before any data are fetched

Ideas and reasons: `docs/IDEAS_UNCHARTED_20261125.md`. Bar for Jx: about $15K/yr on about $15K (≈ 100%/yr) is "prop-like"; ≥ 20%/yr with
controlled drawdown is "useful". Each test has a Stage 1 (kill-only) and is reported with its data coverage. Free public data only.
**Stage 0 (all):** data availability probe `uprobe` (GeckoTerminal pool OHLCV, Hyperliquid meta/candles, Upbit and Binance announcement
pages, Uniswap CCA contracts). A test whose data are unavailable is recorded "not testable" (with the reason), not killed.

## U-T1 (#383) Launch-phase house vaults
**Data.** Share-price (or token-price) histories of perp-DEX liquidity vaults from their launch: JLP (have), GLP (GMX v1), Gains gDAI/gUSDC
(have), HLP (Hyperliquid vault history), and newer venues where a price series exists (Lighter LLP, Aster ALP, Ostium OLP, Avantis).
**Rule.** For each vault, the return of holding it for its first 12 months (from the first price), hedged as #363 where the vault holds
non-stable assets (weekly non-negative least-squares hedge on SOL/ETH/BTC, Hyperliquid funding), costs 0.3%/yr; compare with months 13–24.
**Stage 1 (kill-only):** KILL if the median first-year return across vaults with data is < 20%/yr. **Pass-ish (forward-trial worthy):**
median first-year ≥ 40%/yr across ≥ 4 vaults **and** first year beats months 13–24 in ≥ 3 of 4.

## U-T2 (#384) Withdrawal-queue discounts (kHYPE, stHYPE, beHYPE, ezETH, rsETH, weETH, pufETH, sUSDe)
**Data.** Daily close of each token's main DEX pool against its underlying (GeckoTerminal OHLCV), 2024-01..2026-10 where available.
**Rule.** NAV proxy = the pool's 30-day rolling maximum price ratio (exchange rates move slowly upward). An **event** = a day the ratio closes
≥ 1.0% below the NAV proxy. Trade: buy at that close (size min($15,000, 2% of the pool's daily volume)), redeem after the token's queue
(HYPE LSTs 9 days, LRTs 7 days as an optimistic floor, sUSDe 7 days) at the NAV proxy of the redemption day, minus 0.10% fees and the
queue's lost staking yield. One position per token at a time.
**Stage 1 (kill-only):** KILL if total net profit over the window is < $3,000/yr on $15,000 (< 20%/yr), or there are fewer than 4 events.

## U-T3 (#385) Hyperliquid pre-launch perps (hyperps)
**Data.** Hyperliquid candles for markets that traded as pre-launch hyperps and later had a token launch (list assembled from Hyperliquid
announcements / meta; every name found is used, none dropped).
**Rule.** Short at the first daily close after the hyperp lists; cover at the close 7 days after the token's launch; 1× notional; funding
from Hyperliquid funding history; 0.045% fees per side.
**Stage 1 (kill-only):** KILL if fewer than 6 events, or the mean return per trade is ≤ 0, or more than a third of trades lose > 50%.

## U-T4 (#386) Exchange risk-tag / delisting announcements → short on Hyperliquid
**Data.** Upbit "investment warning" designations and Binance "monitoring tag" / delisting announcements (public announcement pages), 2024–2026;
Hyperliquid daily prices for tokens with a Hyperliquid perp.
**Rule.** Short at the first Hyperliquid daily close after the announcement time, hold 7 days, hedged with an equal BTC long; 0.045% fees per
side + funding.
**Stage 1 (kill-only):** with ≥ 15 events: KILL if the mean hedged 7-day return of the short is < 1% or its t-statistic < 1. Fewer than 15
events: "not testable".

## U-T5 (#387) Uniswap CCA token auctions
**Data.** CCA auctions on Ethereum, Base, Arbitrum and Unichain (contract events), clearing price, and the token's price 1, 7 and 30 days
after the auction ends (GeckoTerminal pools created by the auction).
**Rule.** Buy at the clearing price; sell after 7 days (primary) — 1 and 30 days reported.
**Stage 1 (kill-only):** with ≥ 5 auctions: KILL if the median 7-day return is ≤ 0. Fewer than 5: "not testable".

**Commands.** probe: Actions job `uprobe`; tests: `scripts/uncharted_*_20261125.py` with outputs in `docs/jx_runs/` (each re-run once;
identical). **Limits.** NAV proxies and announcement times are approximations; small samples are reported as such.

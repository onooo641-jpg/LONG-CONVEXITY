# Post-listing short on new perps — pre-registration, 2026-11-20 (CANDIDATES #44)

**Where the idea came from.** In the N1 run (PREREG_TOP10, 2026-11-20), an
*unhedged* 14-day short on 135 Hyperliquid listings from 2024 onwards averaged
+$171 per $1,000. That was an observation, not a test. The rules below are
fixed before any data on the holdout listings is fetched.

**Holdout:** Hyperliquid perps whose first funding record falls between
2023-05-20 and 2023-12-31. The API's history starts on 2023-05-12, so earlier
"first records" are just the start of the data, not listings. None of these
was in the N1 sample.

**Trade:** short $1,000 at the open of the first 1-hour candle after L+1h.
Close at the last close before L+337h, 14 days later. P&L = price move + funding
(positive rate paid to shorts) − $0.90 perp taker fees. No hedge.

**Market control:** the same 14-day short on BTC over the same hours.
Excess = listing P&L − BTC P&L.

**Pass, all three:**
1. mean P&L > 0 with t > 2;
2. mean excess over BTC > 0 with t > 2;
3. median P&L > 0.

**Also reported:** the share of listings that rose ≥ 50% at any point (a 2×
short would need more margin or be liquidated), and the worst single loss.

If the holdout has fewer than 20 listings, the verdict is "too few to decide".

Command: `uv run python scripts/postlisting_20261120.py`

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

## Result of the hourly version (2026-11-20)

**Too few to decide.** Hyperliquid's API keeps only a limited window of hourly
candles, and **0 of 79** holdout listings from 2023 have hourly candles (run
44583877867). The N1 observation itself rested on the 48 of 135 newer listings
that do have hourly candles.

## Version 2 — daily candles (registered 2026-11-20, before daily data was fetched)

Same holdout (the 79 listings of 2023-05-20..2023-12-31), BTC control and pass
rule, with daily candles:
- entry at the open of the first UTC day starting after L+1h;
- exit at the close of the 14th daily candle;
- funding summed over the same span;
- pump = highest daily high ÷ entry − 1.

## Result of version 2 (2026-11-20, `docs/jx_runs/postlisting_20261120.txt`)

79 of 79 holdout listings had daily data.

| | value | condition met |
|---|---|---|
| mean P&L per $1,000 per 14 days | −$110.86 (t −1.86) | no |
| mean excess over a BTC short | −$70.50 (t −1.20) | no |
| median P&L | +$3.92 | yes |
| share profitable / rose ≥ 50% at some point | 51% / **27%** | |
| worst / best | **−$2,936** / +$811 | |

**Verdict: fail.** The 2024 observation didn't hold on unseen listings. About
a quarter of new coins squeezed 50% or more, and one loss was nearly 3× the
stake.

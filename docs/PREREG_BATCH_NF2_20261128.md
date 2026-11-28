# Batch NF2 (#537–#540): new perps on the smaller DEXes (Aster, dYdX) — pre-registered 2026-11-28, before running

**Theme (niche):** newly listed perps on Aster and dYdX, both usable from Malaysia without KYC. Each idea names its forced or
non-economic payer:
- hype buyers and points farmers who buy listings regardless of price;
- liquidated longs and shorts in thin early books;
- farmers who leave once a listing goes quiet.

**G6:** tiny capacity ($1,500 per trade), unusable by funds. **Not repeats:** #44 tested the post-listing short only on Hyperliquid
(2023); #511/#536 are resting-bid rules; #397 is HL/Binance cascade days.

**Data:** `wickscale_aster_1d` and `wickscale_dydx_1d` daily candles. Markets whose first candle is within 30 days of the file's start
are dropped (unknown true listing). Day 1 = the first candle.

**Costs:** 0.1% round trip (taker both ways). **Funding** is not in the data, so it is not modelled, and that is stated. New listings
usually have positive funding, which pays shorts, so this is roughly neutral to conservative for #537, #538 and #540.

**Size:** $1,500 per trade.

| # | Idea (payer) | Exact rule |
|---|---|---|
| 537 | **Post-listing fade** (early hype buyers overpay, then supply and unlocks arrive) | Short at day 1's close, cover at day 15's close (14 days) |
| 538 | **Pump exhaustion** (squeezed shorts and FOMO buyers overshoot) | Within days 2–60: on any day whose close is ≥ +50% above the previous close, short at that close, cover 3 days later. At most one open trade per market |
| 539 | **Crash bounce** (liquidated longs sell at any price in thin books) | Within days 2–60: on any day whose close is ≤ −30% below the previous close, buy at that close, sell 3 days later. At most one open trade per market |
| 540 | **Dying-listing bleed** (farmers and early holders leave once activity fades) | If day 7's USD volume < 20% of day 1's, short at day 7's close, cover 14 days later |

**Split:** markets listed before 2025-01-01 = Stage 1 (kill-only); listed 2025-01-01 onward = Stage 2.

**Stage 1 KILL:** mean net per trade ≤ 0 (with ≥ 20 trades; fewer → no kill, said so).

**Stage 2 PASS:** all of
- ≥ 30 trades;
- mean net ≥ 1.0% per trade;
- t ≥ 2;
- **net still positive after removing the 3 best trades** (the #536 lesson: no single-pump results).

**$/yr** = mean × $1,500 × Stage-2 trades per year. Also reported: Aster vs dYdX split, median, win rate.

**Families:** #537/#540 are listing-fade; #538 is the squeeze mirror; #539 is the liquidation family (cascade) on a new venue.

**Script/output:** `scripts/batch_nf2_20261128.py` → `docs/jx_runs/batch_nf2_20261128.txt`, re-run identical.

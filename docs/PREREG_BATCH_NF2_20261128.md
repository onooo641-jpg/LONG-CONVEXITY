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

## Results (2026-11-28; `docs/jx_runs/batch_nf2_20261128.txt`, re-run identical): 0 of 4 under the registered rules
| # | Verdict | Stage 1 (listed before 2025) | Stage 2 (listed 2025 onward) |
|---|---|---|---|
| 537 post-listing fade | KILL | −7.70% (t −2.07, 169) | +3.37% (t 0.90, 664); **Aster only +6.61% (t 2.84, median +10.9%)**; dYdX −14.5% |
| 538 pump exhaustion | FAIL | +15.6% (t 3.01, 41) | +0.44% (t 0.08, 165); negative without the 3 best |
| 539 crash bounce | FAIL | +17.0% (t 1.69, 47) | +4.03% (t 1.25, 213); ex-top-3 sum +0.35 |
| 540 dying-listing bleed | KILL | −0.29% (t −0.09, 79) | **+7.18% (t 3.70, 187, 59% win), positive without the 3 best** (Aster +6.5%, dYdX +8.5%) |

The kills stand. #537 (on Aster) and #540 are strong and robust in 2025–26 but not before.
- The likely reason, stated as a hypothesis: Aster before 2025 was ApolloX, a different exchange and listing flow.
- The 2025+ points-farming listing wave may be a new regime that the old history cannot judge.
- The only fair judge is new data, so both are re-registered below as **forward-only** tests. They count as untested, not as passes.

## Addendum 1 (2026-11-28, before 2026-12-01): forward-only tests #541 and #542
- **#541 = #537 on Aster only, forward:** listings first traded on or after 2026-12-01; short at day 1's close, cover at day 15's.
- **#542 = #540, forward, Aster:** same listings; if day 7's quote volume < 20% of day 1's, short at day 7's close, cover at day 21's.
- **Costs:** 0.1% round trip; funding not modelled. Logged by radar N13 (`aster_listing_paper.parquet`) once each exit close is known.
- **PASS, each, by 2027-03-31:** ≥ 30 trades for #541 (≥ 15 for #542); mean net ≥ 1.0%; net positive without the 3 best trades.
- Fewer trades by then → extend to 2027-06-30, then judge.

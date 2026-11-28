# Batch NF22 (#631–#634): weekly signals across Hyperliquid's thin spot tokens, long-only, HYPE-hedged — pre-registered 2026-11-28, before these rules are run on the data

**Why:**
- HL spot lists 300+ permissionless HIP-1 tokens in thin books, traded almost only by HL retail.
- HL spot can't be shorted and few of these tokens have perps, so cross-sectional anomalies are hard for large funds to arbitrage.
- Tested on HL spot so far:
  - wick bids (#510, #524);
  - new listings, days 1–14 (#535).
- Weekly cross-sectional signals are untested here.

**Desk checks:**
- **G5:** HL spot needs no KYC.
- **G6:** the books are thin and retail. Shorting is impossible, which is the friction.

**Data:**
- Existing `fivehigh_hl_spot_1d.parquet`: daily candles, every HL spot pair, to 2026-11-25. USDC-quoted pairs only.
- HL `HYPE` perp daily closes come from `uncharted_385_candles.parquet`.

**Common:**
- **Window:** 2024-12-01 (HYPE perp available as the hedge) .. 2026-11-25.
- **Weekly rebalance** at Monday's daily close (UTC). Hold 7 days to the next Monday's close.
- **Eligible:** median daily USD volume (v × close) over the previous 30 days ≥ $20,000, ≥ 60 days of history, and a traded bar
  (high > low, volume > 0) on both the entry and exit days.
- **Portfolio:** equal weight of the selected tokens. Size per token = min($1,500, 1% of the entry day's USD volume).
- **Hedge:** short HYPE perp, beta 1, same notional.
- **Return** = token return − HYPE return − costs.
- **Costs:** 0.07% taker + an assumed 0.50% spread/impact per side on thin books, so 1.14% per round trip, plus the HYPE leg at 0.09%
  (×1.5 stress reported).

| # | Idea | Selection each Monday |
|---|---|---|
| 631 | **Weekly reversal** | the 10% of eligible tokens with the lowest previous-7-day return (min 3 tokens) |
| 632 | **4-week momentum** | the 10% with the highest previous-28-day return, skipping the last 7 days (min 3) |
| 633 | **Volume shock** | tokens whose last-7-day USD volume ≥ 5 × their previous-30-day weekly average, and whose last-7-day return is ≥ 0 |
| 634 | **Dormant awakening** | tokens with previous-30-day median volume < $5,000 whose last-7-day volume ≥ $50,000 (eligibility uses this rule instead of the $20K median) |

**Split:**
- Stage 1 = weeks starting 2024-12-01..2025-06-30 (kill only);
- Stage 2 = weeks 2025-07-01..2026-11-25, unseen.

**Stage 1 KILL:** ≥ 10 weeks with trades and mean weekly net ≤ 0.

**Stage 2 PASS:** all of
- ≥ 30 weeks with trades;
- mean weekly net ≥ 1% (about 50%+/yr);
- t ≥ 2;
- positive without the 3 best weeks;
- mean > 0 with costs × 1.5;
- the top token is not more than 40% of the profit.

**Multiple testing:** four tests. Only a pass with Stage 2 t ≥ 2.5 goes to the radar forward log.

**Script/output:** `scripts/batch_nf22_20261128.py` → `docs/jx_runs/batch_nf22_20261128.txt`, re-run identical.

# Batch NF8 (#564–#567): Binance leverage signals traded on Hyperliquid — pre-registered 2026-11-28, before running

**Payers:**
- over-levered traders on the largest venue: late longs and shorts that pile in, then get forced out;
- traders who keep paying funding.

**G5:** trades are HL perps. **G6:** event-driven, per-coin, small size.

**Data:**
- Coinalyze Binance daily open interest (`batchj_cz_oi_binance`, in coin units, 110 perps, 2020–26) and daily liquidations
  (`batchj_cz_liq_binance`, l = longs, s = shorts, USD);
- HL hourly funding (`hl_funding`, 155 coins, 2024–26);
- HL daily candles.
- OI value = OI × HL close.

**Not repeats:** #492 (short-squeeze fade, liquidation/price trigger), #495 (retail long/short ratio), #489/#499 (crowded funding
short) use different triggers.

**Rule basics:**
- Entry at HL's close on signal day d; excess = side × (coin − HL BTC) − 0.09%; one open trade per coin per idea.
- **Baselines** (random HL alt vs BTC): short over 3 / 7 days, before 2025 −0.15% / −0.21%, 2025–26 +0.33% / +0.95%. The long
  baseline is the negative of these.

| # | Idea (payer) | Signal | Side, hold |
|---|---|---|---|
| 564 | **Silent leverage build-up** (leverage piles in without price movement; it is usually long-heavy in alts and ends in a flush) | Binance OI up ≥ 50% over 7 days while the HL price changed by less than 5% in absolute terms over the same 7 days | short, 7 days |
| 565 | **Deleveraging complete** (forced long sellers exhausted) | OI down ≥ 30% over 3 days **and** long liquidations over those 3 days ≥ 3% of the starting OI value | long, 7 days |
| 566 | **Funding capitulation** (longs gave up; shorts now crowded and paying) | HL 3-day mean funding was ≥ +30%/yr as of 3 days ago, and the last 24 h mean ≤ −10%/yr | long, 3 days |
| 567 | **Short-squeeze fuel** (shorts pile into a falling coin and pay to stay in) | OI up ≥ 30% over 7 days while the HL price fell ≥ 10% over the same 7 days | long, 7 days |

**Split:** before 2025-01-01 = Stage 1 (KILL if mean ≤ that period's baseline for the side, ≥ 8 trades); 2025 onward = Stage 2.
#566's funding data starts in 2024, so its Stage 1 is 2024.

**Stage 2 PASS:** all of
- ≥ 15 trades;
- mean ≥ 2%;
- t ≥ 2;
- positive without the 3 best;
- mean ≥ the side's baseline + 1 point.

**$/yr:** $3,000 per trade.

**Script/output:** `scripts/batch_nf8_20261128.py` → `docs/jx_runs/batch_nf8_20261128.txt`, re-run identical.

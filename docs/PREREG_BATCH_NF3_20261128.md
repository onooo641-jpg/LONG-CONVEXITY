# Batch NF3 (#543–#546): Binance events traded on Hyperliquid — pre-registered 2026-11-28, before any price is read

**Why.** Batches L and M found real Binance-event effects that failed G5: the coins could only be shorted on venues closed to Malaysia.
This batch keeps only events whose coin already trades on Hyperliquid (usable from Malaysia), so the G5 problem is solved by design.
- Spot delistings and monitoring-tag additions were dropped at the desk: 4 and 0 of their titles name an HL coin.
- Counts below are from titles, made before prices were read.

**G6:** small listings on Hyperliquid, $3,000 per event; too small for funds.

**Rule (all four).**
- A = announcement time (catalog `uncharted_w3_binance_ann.json`); coin = a ticker in the title that is listed on HL
  (`uncharted_385_candles`).
- **Entry:** short the HL perp at the close of the first HL daily candle that starts after A (next UTC day).
- **Exit:** at the close 7 days later.
- **Excess** = −(coin return − HL BTC return) − 0.09% round trip. Funding is not modelled.
- Several coins in one title are averaged.

| # | Event (payer) | Title pattern | Titles / naming an HL coin |
|---|---|---|---|
| 543 | **Seed-tag listing** (Binance lists a risky early token; hype buyers overpay into the listing) | "Will List … Seed Tag" | 62 / 36 |
| 544 | **Earn, loan and margin add** (Binance margin opens shorting and loans; holders put tokens up as collateral and short against them) | "Will Add … on … Earn/VIP Loan/Margin" | 130+ / 67 |
| 545 | **Binance perp launch for a coin already on HL** (short-sale constraint relief: Binance's large short base can now short it) | "Futures Will Launch USDⓈ-M/Margined XUSDT Perpetual", pre-market titles excluded | 121 / 28 |
| 546 | **Binance pre-market perp launch** (pre-market perps price an unlisted token on hype) | the same pattern with "Pre-Market" | subset of the 121 |

**Split:** announcements before 2025-01-01 = Stage 1 (kill-only); 2025-01-01 onward = Stage 2.

**Stage 1 KILL:** mean excess ≤ 0 (≥ 8 events; fewer → no kill, said so).

**Stage 2 PASS:** all of
- ≥ 15 events;
- mean excess ≥ 2%;
- t ≥ 2;
- **sum still positive without the 3 best events**.

**$/yr** = mean × $3,000 × Stage-2 events per year.

**Script/output:** `scripts/batch_nf3_20261128.py` → `docs/jx_runs/batch_nf3_20261128.txt`, re-run identical.

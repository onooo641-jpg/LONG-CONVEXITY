# Batch G (#458–#467): ten individual ideas, calibrated gate — pre-registered 2026-11-26, before any of their data are looked at

**Gate (Jx's calibration).** Each idea has:
- a named structural payer;
- free data;
- a venue usable from Malaysia;
- a time split.

$/yr and event count are not desk filters. Each verdict reports $/yr at a safe size, and only passes ≥ ~$10K/yr count toward Jx's two.
**Lessons used.** The two Batch F passes (#455 mid-month 401(k), #451 Treasury month-end) were *mandated, scheduled flows*. Batch G
looks for more scheduled mandated or price-insensitive flows, and adds crypto versions, where volatility gives more $ per event.
**Costs:**
- crypto 0.045%/side (Hyperliquid/dYdX taker);
- FX 0.3 pip round trip;
- rates 0.5 bp.

**Safe size for $/yr:**
- crypto: $15K × 3 notional;
- FX: $150K notional;
- rates: DV01 $50;
- ETFs: $15K × 2 via IBKR futures equivalents.

| # | Idea (payer) | Exact rule | Data | Stage 1 KILL if | Stage 2 PASS if |
|---|---|---|---|---|---|
| 458 | **Miner margin squeeze** (after a big upward difficulty adjustment, miners must sell BTC to cover costs) | when BTC difficulty rises ≥ 5% at an adjustment, short BTC from the next daily close for 7 days; variant: ≤ −5% → long | blockchain.info difficulty; DefiLlama BTC daily (2014+) | 2014–2020: mean ≤ 0 | 2021–2026-10: ≥ 20 events, mean ≥ 0.5%, t ≥ 2 |
| 459 | **Treasury coupon reinvestment** (index funds must reinvest the large refunding coupons paid on the 15th of Feb/May/Aug/Nov) | long duration (DGS10) from the close 3 FRED trading days before the 15th to the close of the first trading day after the 15th, in Feb/May/Aug/Nov; variant: every month | FRED DGS10 | 1990–2009: mean ≤ 0 | 2010–2026-10: mean ≥ 0.5 bp, t ≥ 2 |
| 460 | **FX month-end hedge rebalancing** (foreign holders of US equities sell USD at the 16:00 London fix after US equities rise, to keep hedge ratios) | last trading day: if SPY month-to-date return to the previous close is > +2%, short USD (long EURUSD) from 2 h before the fix to 5 min after it; if < −2%, long USD. Fix = 16:00 London (15:00 UTC during BST) | Dukascopy EURUSD ticks; Yahoo SPY | 2012–2018: mean ≤ 0 | 2019–2026-10: mean ≥ 0.5 pip, t ≥ 2 |
| 461 | **Crypto funding carry, cross-section** (leveraged longs pay funding on crowded coins) | every Monday 00:00 UTC, rank the 40 Binance perps (`batchd_alts`) by trailing-7-day mean funding; long the 5 lowest, short the 5 highest, equal weight, 7 days; P&L = price + funding; 0.1% per leg per week | `batchd_alts_1h`, `batchd_alts_funding` | 2021–2022: mean weekly ≤ 0 | 2023–2026-10: mean weekly > 0, t ≥ 2, annualised ≥ 15% on gross |
| 462 | **Payday recurring buys** (salaries paid on the 25th in Korea/Japan, and US recurring buys on the 1st/15th, buy crypto price-insensitively) | long BTC from 00:00 UTC on the 24th to 00:00 UTC on the 27th each month (main); variant: the 1st and 15th, day before → day after | DefiLlama BTC daily | 2014–2020: mean ≤ 0 | 2021–2026-10: mean ≥ 0.3%, t ≥ 2 |
| 463 | **Buyback blackout windows** (corporate buyback desks, ~$1T/yr, buy only in open windows) | long SPY from the close of the 3rd trading day after the 25th of Jan/Apr/Jul/Oct (most results out) to the close of the 14th of the last month of the quarter (blackout starts); one event per quarter | Yahoo SPY (adjusted) | 2000–2012: mean excess over the same-length average SPY window ≤ 0 | 2013–2026-10: mean excess > 0, t ≥ 2 |
| 464 | **Fixed-time DCA buying** (exchange recurring-buy plans execute at fixed UTC times; 00:00 UTC is the common default) | long BTC 00:00 → 02:00 UTC daily (Binance 1h closes) | `batchc_btceth_1h` | 2020–2022: mean ≤ 0 | 2023–2026-10: mean ≥ 0.05%, t ≥ 2 |
| 465 | **CME bitcoin-futures expiry** (cash-and-carry funds long spot/ETF and short CME futures unwind into the BRR settlement, 15:00–16:00 London, on the last Friday) | short BTC from 4 h before to the end of the BRR window on the last Friday of each month | `batchc_btceth_1h` | 2020–2023: mean ≤ 0 | 2024–2026-10: ≥ 20 events, mean ≥ 0.2%, t ≥ 2 |
| 466 | **Japanese month-start fund buying** (monthly NISA/investment-trust purchases of foreign assets sell yen at the turn of the month) | long USD/JPY from the last business day's rate to the 3rd business day's (FRED DEXJPUS, noon New York) | FRED DEXJPUS | 2010–2018: mean ≤ 0 | 2019–2026-10: mean ≥ 0.15%, t ≥ 2 |
| 467 | **Large stablecoin mints** (Tether/Circle mint to fill buy orders from OTC desks) — data permitting | hourly: a single USDT mint/issue ≥ $500M seen on Ethereum or Tron → long BTC for 24 h | DefiLlama stablecoin chain data (daily granularity used if hourly is unavailable: day-over-day USDT supply jump ≥ $500M → long next 24 h from 00:00 UTC) | 2020–2022: mean ≤ 0 | 2023–2026-10: ≥ 30 events, mean ≥ 0.3%, t ≥ 2 |

Notes:
- #461 is carry: earlier carry passes were 12–25%/yr. It is included because the cross-section (crowded alts) was never tested.
- #467 overlaps #448 (supply surges): #448 is a weekly aggregate percentile, #467 is single large mints. If both pass they count as one family.
- Data job `ubatchg`: DefiLlama BTC daily, blockchain.info difficulty, Dukascopy EURUSD on month-end days, Yahoo SPY, FRED DEXJPUS,
  DefiLlama USDT chain history.
- Script `scripts/batch_g_20261126.py`; output `docs/jx_runs/batch_g_20261126.txt` (re-run once, identical).

## Results (2026-11-26; `docs/jx_runs/batch_g_20261126.txt`, re-run identical)

| # | Verdict | Key figures | $/yr at safe size |
|---|---|---|---|
| 458 miner margin squeeze | FAIL | S1 +0.25% (t 0.18); S2 −0.85% (n 17); down-variant KILL | −$1.1K |
| 459 Treasury coupon reinvestment | FAIL | Feb/May/Aug/Nov and all-month both below 0.5 bp / t 2 | $22 |
| 460 FX month-end hedge rebalancing | KILL | S1 −18.9 pip (n 11) | — |
| 461 crypto funding carry cross-section | FAIL | S1 82.5%/yr (t 2.74) → S2 16.5%/yr, t 1.49 | ~$5.0K |
| 462 payday recurring buys | KILL (main, 25th) | main S1 −0.10%. **Variant 1st/15th (reported only): S2 +0.87%, t 2.20** | variant ~$7.2K (does not count: variant, < $10K) |
| 463 buyback open windows | KILL | S1 −0.99% excess | — |
| 464 fixed-time DCA | KILL | | — |
| 465 CME bitcoin-futures expiry | KILL | S1 −0.37% | — |
| 466 Japanese month-start buying | FAIL | S1 +0.09%, S2 −0.05% | −$852 |
| 467 large USDT mints | FAIL | S1 +0.54%, S2 −0.05% | −$411 |

**Batch G verdict: 0 of 10 count.** #461 and the #462 variant are the closest. Neither clears both significance and $10K/yr.

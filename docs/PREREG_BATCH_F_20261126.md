# Batch F (#448–#457): ten individual flow ideas — pre-registered 2026-11-26, before any of their data are looked at

**Gate recalibrated (Jx, 2026-11-26): "don't set it too loose or too strict — like how #350–#400 were found."**
Batches D and E rejected ideas at the desk for falling short of $10K/yr or ~100 events/yr, which left Batch E with one idea.
Those two numbers are no longer desk filters. Each idea still needs:
- a structural payer (a forced or paid counterparty);
- free data;
- a venue usable from Malaysia (IBKR futures/FX/stocks; Hyperliquid/dYdX for crypto);
- a genuine time split.

The test decides the rest. A pass is judged as #389 was: out-of-sample sign and t, then $/yr reported against the $15K pot.
Several ideas come from the Batch D/E reject lists.

Futures ideas (#450, #452, #455, #456) use the same data, costs and roll handling as `docs/PREREG_20261120.md` and Batch D:
- markets NQ/ES/YM/RTY, round trip 1.12/0.748/4.48/0.448 points;
- days in the 10 trading days before a quarterly expiry are dropped;
- RTH close = the 15:59 ET bar's close; RTH open = the 09:30 bar's open; "10:00" = the 09:59 bar's close.
- **Futures windows:** Stage 1 2010-07..2015-12 (KILL if mean net ≤ 0 on both NQ and ES). Stage 2 2016-01..2026-10 (PASS if ≥ 3
  of 4 markets have mean net > 0 and the pooled per-event t ≥ 2, where pooled = equal-weight average of each event's net return in % of
  price across the markets trading it).

| # | Idea (payer) | Exact rule | Data | Stage 1 (kill) | Stage 2 (PASS) |
|---|---|---|---|---|---|
| 448 | **Stablecoin supply surges** (new dollars minted to buy crypto) | Every Monday 00:00 UTC: g = 7-day % change in total stablecoin supply (DefiLlama `stablecoincharts/all`, total circulating USD). If g > its trailing-52-week 80th percentile → long BTC 7 days; if < 20th → short 7 days. 0.045%/side | DefiLlama stablecoins; Binance BTC daily (`uncharted_389_binance_ohlc`) | 2020-01..2022-12: mean ≤ 0 | 2023-01..2026-10: ≥ 30 events, mean ≥ 0.5%, t ≥ 2. Variant: ETH |
| 449 | **US spot-ETF net flows** (creations are bought by APs; persistent demand) | daily total BTC-ETF net flow F_d (Farside). If \|F_d\| ≥ $200M, trade BTC sign(F_d) from 00:00 UTC on d+1 to 00:00 on d+2. 0.045%/side | Farside flow table; Binance BTC 1h | 2024-01-11..2024-12-31: mean ≤ 0 | 2025-01..2026-10: ≥ 50 events, mean ≥ 0.2%, t ≥ 2. Variant: ETH ETFs (threshold $50M) |
| 450 | **Month-end pension/balanced-fund rebalancing** | at the close of the 4th-last trading day of each month: equity MTD return R_e (from last month's final RTH close) minus bond MTD return R_b = −7.5 × ΔDGS10 (decimal yield change over the same dates). If R_e − R_b > +2%, short from that close to the RTH close of the last trading day; if < −2%, long | local futures + FRED DGS10 | futures rule | futures rule |
| 451 | **Treasury month-end index extension** (bond indices lengthen duration at month-end; index funds must buy long bonds) | long duration from the close of the 3rd-last trading day to the close of the last trading day of each month. P&L bp = −Δy − 0.5 bp, on DGS10 (main) and DGS30 (variant) | FRED (dates = FRED trading days) | 1990–2009: mean ≤ 0 | 2010–2026-10: mean ≥ 0.5 bp, t ≥ 2 (DGS10) |
| 452 | **OPEX-week dealer hedging** (dealers long gamma pin into expiry; the hedge unwind weakens the week after) | Non-quarterly months only (quarterly OPEX overlaps roll windows): long from the RTH close of the Friday before monthly OPEX (3rd Friday) to the OPEX-Friday close; short from the OPEX-Friday close to the next Friday's close. Main = both legs as one event | local futures | futures rule | futures rule |
| 453 | **USD/JPY gotobi Tokyo fix** (Japanese importers buy dollars at the 09:55 JST fix on 5/10-days) | gotobi = days 5, 10, 15, 20, 25 and the month's last day, moved back to Friday if on a weekend (Japanese holidays ignored). Long USD/JPY from 00:00 UTC to 00:55 UTC (mid, Dukascopy ticks); cost 0.3 pip round trip. Baseline = same window on other weekdays | Dukascopy USDJPY ticks, hours 00–01 UTC, 2012–2026 | 2012–2018: mean ≤ 0 | 2019–2026-10: mean ≥ 0.5 pip, t ≥ 2, beats baseline (Welch t ≥ 1.5). Variant: post-fix short 00:55 → 02:00 |
| 454 | **IPO lock-up expiry** (insiders and VCs sell at the 180-day lock-up end) | US IPOs priced at ≥ $5 with deal size ≥ $50M (Nasdaq IPO calendar). Lock-up date = IPO date + 180 days (standard; assumed). Short from the close 5 trading days before to the close of the first trading day on/after the lock-up date; hedge long IWM; costs 0.1%/side/leg + borrow 30%/yr | Nasdaq calendar API; Yahoo daily | IPOs 2016–2019: mean ≤ 0 | IPOs 2020–2026-04: ≥ 100 events, mean ≥ 0.5%, t ≥ 2 |
| 455 | **Mid-month 401(k) contributions** (payroll contributions invested around the 15th) | long from the RTH close of the last trading day before the 15th to the RTH close of the 2nd trading day on/after the 15th | local futures | futures rule | futures rule |
| 456 | **Quarterly index-rebalance close** (S&P/Nasdaq rebalances executed in the closing auction on the 3rd Friday of Mar/Jun/Sep/Dec) | fade the 15:00 → 16:00 move: from the RTH close to 10:00 on the next trading day, trade −sign(close − 15:00 price) | local futures | futures rule (≥ 10 events) | futures rule |
| 457 | **Vol-spike hedge unwind** (put buyers pay up in panics; dealer delta hedges unwind as vol falls) | Deribit DVOL daily close; if DVOL_d − median(DVOL d−20..d−1) ≥ 10 points → long the coin from the close of d for 7 days (no overlap). 0.045%/side | DVOL (`batcha_raw.json`), Binance daily | 2021-03..2023-12: mean ≤ 0 | 2024-01..2026-10: ≥ 15 events, mean ≥ 1%, t ≥ 2. BTC main, ETH variant |

$/yr for each pass, against the $15K pot:
- futures: notional capped at 10×, as in Batch D;
- #448/#449/#457: $15K × 3× per event;
- #453: $150K notional;
- #454: $5K per event, ≤ 5 open.

Data jobs:
- `ubatchf`: stablecoins, Farside;
- `ubatchf2`: Dukascopy;
- `ubatchf3`: Nasdaq/Yahoo IPOs.

Script `scripts/batch_f_20261126.py`; output `docs/jx_runs/batch_f_20261126.txt` (re-run once, identical).

## Results (2026-11-26; `docs/jx_runs/batch_f_20261126.txt`, re-run identical)

**Mechanical fix:** `part448` used `Series.normalize` (AttributeError), replaced with `.dt.normalize()`; no rule change.

| # | Verdict | Key figures | $/yr at safe size |
|---|---|---|---|
| 448 stablecoin supply surges | FAIL | BTC S1 +0.85% (t 0.74), S2 +0.59%, t 0.81; ETH variant KILL | $5.8K (not significant) |
| 449 US spot-ETF flows | KILL | BTC S1 −0.04%; ETH variant S2 +0.25%, t 1.17 (FAIL) | ETH variant $15.8K, not significant |
| 450 month-end pension rebalancing | FAIL (near miss) | S2 4/4 markets > 0, pooled t 1.99 | ~$4.8K |
| **451 Treasury month-end extension** | **PASS** | DGS10 S2 mean ≥ 0.5 bp, t ≥ 2 | **$716** (DV01 $50) |
| 452 OPEX week | KILL | S1 pooled −0.95% | — |
| 453 USD/JPY gotobi fix | FAIL | S1 +2.0 pip (t 1.10); S2 −2.5 pip. **Caveat:** Dukascopy served only 1,126 of 3,870 days (throttled), so the test has low power | −$292 |
| 454 IPO lock-up expiry short | KILL | S1 −1.04% (n 268); S2 −0.81%, t −2.35 (shorts lose) | — |
| **455 mid-month 401(k)** | **PASS** | S2 4/4 markets > 0, pooled +0.34%, t 2.35 | **$3.2K** (10× notional) |
| 456 index-rebalance close fade | FAIL | S2 0/4 markets > 0 | −$408 |
| 457 DVOL spike | KILL | BTC S1 −0.17% | — |

**Batch F verdict: 2 out-of-sample passes (#451, #455), both far below $10K/yr. None count toward Jx's two.**

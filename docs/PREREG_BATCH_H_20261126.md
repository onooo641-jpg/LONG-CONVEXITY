# Batch H (#468–#477): ten individual ideas, calibrated gate — pre-registered 2026-11-26, before any of their data are looked at

**Gate (Jx's calibration, as Batches F/G).** Each idea needs:
- a named structural payer (a forced, mandated or price-insensitive counterparty);
- free data;
- a venue usable from Malaysia (IBKR futures/ETFs/stocks; Hyperliquid for crypto);
- a genuine time split.

$/yr and event count are not desk filters. Each verdict reports $/yr at a safe size, and only passes ≥ ~$10K/yr on the ~$15K pot
count toward Jx's two.

**Desk rejects (already tested, so not repeated):**
- turn of month (#30, failed);
- Binance perp launches (#396, killed);
- Curve weekly-epoch emission selling (no forced claim time, so no payer at a fixed time);
- mirror-image "asks above short-squeeze wicks" (same liquidation payer as the wick family, so it would not count as a new family).

**Lessons used:**
- The passes were scheduled, mandated flows (#451, #455) and forced liquidity in volatile crypto (wick).
- Batch H looks for more mechanical rebalancing flows, where the payer is forced by its own rules (leveraged and inverse ETPs,
  index-fund dividend reinvestment, hedgers), plus three crypto price-insensitive buyers.

**Costs:**
- crypto: 0.045%/side;
- VX: 0.06 points round trip (1 tick + fees);
- ETFs and US stocks: 0.02%/side for ETFs, 0.05%/side for single stocks;
- Nikkei futures: 0.02%/side;
- rates: 0.5 bp.

**Safe size for $/yr:**
- crypto: $45K notional per signal time (the pot × 3);
- VX: 1 contract ($1,000/pt);
- ETFs and stocks: $30K per signal day (pot × 2);
- Nikkei: $30K;
- rates: DV01 $50.

**Price-at-time convention.** In Binance hourly data the index is the bar's open time, so the price AT time T = the close of the bar that
opens at T−1h (the `_px` fix from Batch C).

| # | Idea (payer) | Exact rule | Data | Stage 1 KILL if | Stage 2 PASS if |
|---|---|---|---|---|---|
| 468 | **Funding-settlement pressure** (traders paying large funding close before the Binance settlement time to avoid paying it) | For each of the 40 `batchd_alts` perps, at each funding time T: signal = the rate settled at that symbol's *previous* funding time (known in advance). If ≥ +0.05% → short from T−2h to T; if ≤ −0.05% → long. Net = side × return − 0.09%. Events at the same T are averaged into one observation for t | `batchd_alts_1h`, `batchd_alts_funding` | 2020–2022: mean ≤ 0 | 2023–2026-10: ≥ 100 timestamps, mean ≥ 0.05%, t ≥ 2. Variant (reported only): re-entry T → T+2h, opposite side |
| 469 | **VIX ETP rebalancing** (leveraged long and inverse VIX ETPs both must buy VX futures into the close after VX rises, and sell after it falls) | Front VX = nearest expiry ≥ 7 calendar days away. Daily price = Settle if > 0, else Close. r_d = price_d / price_{d−1} − 1 (same contract). If r_d ≥ +8% → short from d's price to d+1's price; if ≤ −8% → long. Net points = side × Δ − 0.06 | `batch9_vx.json` (CBOE per-contract daily) | 2013–2018-01: mean ≤ 0 | 2018-03–2026-10: ≥ 30 events, mean net > 0, t ≥ 2 |
| 470 | **Single-stock leveraged-ETF rebalancing** (2× single-stock ETFs — TSLL, NVDL, MSTU/MSTX, CONL, PLTU, SMCX, AMDL — must buy at the close after up days and sell after down days) | Universe: TSLA, NVDA, MSTR, COIN, PLTR, SMCI, AMD. Adjusted open = open × adjclose / close. If the close-to-close adjusted return ≥ +7% → short from that close to the next open; if ≤ −7% → long. Net = side × return − 0.10%. Same-day events are averaged for t | Yahoo daily (job `ubatchh`) | 2023-01–2024-06: pooled mean ≤ 0 | 2024-07–2026-10: ≥ 50 events, mean ≥ 0.2%, t ≥ 2. Variant: close → next close |
| 471 | **BTC spot-ETF NAV window** (in-cash creations are bought in the CF BRRNY window, 15:00–16:00 New York, which sets the ETFs' NAV) | Every weekday: long BTC from 15:00 to 16:00 New York time (UTC offset by date) at hourly prices; net = return − 0.09% | `batchc_btceth_1h` | 2024-01-11–2024-12-31: mean net ≤ 0 | 2025-01–2026-10: mean net ≥ 0.03%, t ≥ 2. Control: the same hour 2021–2023 (pre-ETF) reported |
| 472 | **Mortgage convexity hedging** (MBS holders and servicers must sell duration as rising yields lengthen MBS, and buy it back as falling yields shorten it, extending the move) | FRED trading days. Δ5 = DGS10_d − DGS10_{d−5}. If Δ5 ≥ +20 bp → short duration d → d+5 (P&L bp = +Δy − 0.5); if ≤ −20 bp → long (P&L = −Δy − 0.5). No overlapping events | `batchd_fred_cmt` (DGS10) | 1990–2009: mean ≤ 0 | 2010–2026-10: mean ≥ 1 bp, t ≥ 2. Variants: 10 bp threshold; 2-day hold |
| 473 | **Tether quarter-end BTC buying** (Tether's stated policy since May 2023 is to put up to 15% of quarterly profit into BTC, and its purchases cluster at quarter-ends) | Each quarter from 2023-Q2: long BTC from 00:00 UTC 5 days before the quarter's last day to 00:00 UTC on the next day; net − 0.09%. Excess = net − the mean of all 6-day BTC windows in the same stage | `batchc_btceth_1h` | 2023-Q2–2024-Q4: mean excess ≤ 0 | 2025-Q1–2026-Q3: mean excess ≥ 1%, t ≥ 2 (low power is accepted and stated) |
| 474 | **Quarter-end window dressing** (managers buy the quarter's winners before quarter-end reporting) | Long MTUM, short SPY (adjusted closes) from the close 5 trading days before the quarter's last trading day to the close of the last trading day; net − 0.08% | Yahoo MTUM, SPY (`ubatchh`) | 2013-06–2019-12: mean ≤ 0 | 2020-01–2026-09: mean ≥ 0.3%, t ≥ 2. Variant: the reverse over the first 5 days of the next quarter |
| 475 | **Nikkei dividend reinvestment** (index funds buy futures at the close of the last cum-dividend day in March and September to reinvest expected dividends) | Record date = the last Nikkei trading day of March/September. Last cum day = 2 trading days before it (3 before 2019-07-16, under T+3). Long the Nikkei 225 from the close 5 trading days before the last cum day to the close of the last cum day; net − 0.04% | Yahoo ^N225 (`ubatchh`) | 2000–2012: mean ≤ 0 | 2013–2026-09: mean ≥ 0.5%, t ≥ 2. Variant: all four quarter-ends |
| 476 | **Crypto leveraged-token rebalance** (exchange leveraged tokens rebalance at about 00:00 UTC after big daily moves, buying after up days and selling after down days) | BTC and ETH. r = price(00:00 d) / price(00:00 d−1) − 1. If \|r\| ≥ 5% → trade sign(r) from 00:00 to 01:00 UTC on day d; net − 0.09% | `batchc_btceth_1h` | 2020–2022: mean ≤ 0 | 2023–2026-10: ≥ 30 events, mean ≥ 0.1%, t ≥ 2. Variant: fade 01:00 → 04:00 |
| 477 | **Tax-date selling** (individuals and corporates sell assets to pay taxes due on the 15th of January, April, June, September and December) | D = the last trading day before the 15th. Short SPY from the close of the trading day 5 sessions before D to D's close (adjusted closes); net − 0.04% | Yahoo SPY (`ubatchh`, or `batchg_etf_1d`) | 2000–2012: mean ≤ 0 | 2013–2026-10: mean ≥ 0.2%, t ≥ 2 |

**Families.** If more than one idea in the same family passes, they count as ONE toward Jx's two:
- leveraged-ETP rebalancing: #469, #470, #476 (with #443, killed);
- ETF flows: #471 with #449;
- month/quarter-end rebalancing: #474 with #450 and #451.

Stage 1 can only kill; no stage declares a pass early, and the Stage 2 rules are not changed after Stage 1.

**Data:**
- local files: #468, #469, #471, #472, #473, #476;
- job `ubatchh` (Yahoo: the seven stocks with open/close/adjclose; MTUM, SPY, ^N225), run via `fetch_public.yml` because both fallback
  queues are busy.

**Script and output.** Script: `scripts/batch_h_20261126.py`. Output: `docs/jx_runs/batch_h_20261126.txt` (re-run once; it must be identical).

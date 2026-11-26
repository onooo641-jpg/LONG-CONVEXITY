# Batch I (#478–#487): ten individual ideas, calibrated gate — pre-registered 2026-11-26, before any of their data are looked at

**Gate (Jx's calibration, as Batches F–H).** Each idea needs:
- a named structural payer;
- free data;
- a venue usable from Malaysia;
- a genuine time split.

$/yr and event count are not desk filters. Each verdict reports $/yr at a safe size, and only passes ≥ ~$10K/yr count toward Jx's two.

**Lesson used (from #468).** Many-events-per-year timing around a *mechanical clock* (funding settlement) is the only shape since the
wick to produce $10K+/yr on paper. Batch I tests that shape at other mechanical clocks:
- FX rollover;
- the WM/R 4 pm fix;
- the LBMA gold auction;
- Solana epoch boundaries.

It adds scheduled roll and dividend flows, and an overreaction-to-forced-delisting idea.

**Desk rejects:**
- BITO roll (roll dates not published precisely enough to pre-register);
- Tokyo daily fix (already #453's baseline);
- FX margin-call bids in USD/JPY (same mechanism as the wick family);
- hash-ribbon miner capitulation (same payer as #458, killed).

**Costs:**
- FX: 0.3 bp of price round trip;
- gold: 1 bp;
- crypto perps: 0.09% round trip;
- DEX spot: 0.6% round trip;
- ETFs: 0.02%/side/leg;
- Nikkei: 0.04% round trip.

**Safe size for $/yr:**
- FX: $150K notional;
- gold: $45K;
- crypto: $45K;
- delisted-token buys: $3K per token, at most 5 open;
- ETFs: $30K;
- Nikkei: $30K.

**Clock.** London and New York times are converted to UTC by date (DST-aware). FX and gold prices are Dukascopy BID 1-minute
candle closes. The price "at" HH:MM = the close of the minute candle that ends at HH:MM.

| # | Idea (payer) | Exact rule | Stage 1 KILL if | Stage 2 PASS if |
|---|---|---|---|---|
| 478 | **FX triple-rollover avoidance** (holders short a high-yield currency pay three days of carry at the Wednesday 17:00 NY rollover, so some close before it) | Pairs EURUSD, GBPUSD, USDJPY, AUDUSD. The higher-yield currency each month comes from the OECD 3-month interbank rates (FRED IR3TIB01{US,EZ,GB,JP,AU}M156N, previous month's value). Every Wednesday: long the higher-yield currency vs USD from 15:00 to 16:55 New York. Net bp = side × return − 0.3. Pairs on the same day are averaged | 2012–2018: mean ≤ 0 | 2019–2026-10: mean ≥ 0.3 bp, t ≥ 2. Variant: every weekday |
| 479 | **WM/R 4 pm fix reversal** (fix orders from asset managers are price-insensitive; the pre-fix push reverts after) | Same 4 pairs; every trading day except the month's last (that day belongs to #460). m = price(16:00 London) − price(15:30 London). Trade −sign(m) from 16:00 to 16:30 London. Net bp − 0.3; pairs averaged per day | 2012–2018: mean ≤ 0 | 2019–2026-10: mean ≥ 0.3 bp, t ≥ 2 |
| 480 | **LBMA gold PM auction reversal** (central-bank, ETF and jewellery orders settled at the 15:00 London auction push the price) | XAUUSD. m = price(15:00 London) − price(14:30 London). Trade −sign(m) from 15:05 to 15:35 London. Net − 1 bp | 2012–2018: mean ≤ 0 | 2019–2026-10: mean ≥ 1 bp, t ≥ 2. Variants: AM auction (10:30); silver XAGUSD at 12:00 |
| 481 | **Solana epoch-boundary unstake selling** (deactivated stake becomes liquid only at an epoch boundary, every ~2 days, and unstakers sell) | E = the block time of the first slot of each epoch (public RPC). Short SOL from the first full hour after E for 24 h (Binance SOLUSDT 1h, `batchd_alts_1h`); net − 0.09% | 2021–2022: mean ≤ 0 | 2023–2026-10: ≥ 100 events, mean ≥ 0.1%, t ≥ 2 |
| 482 | **Binance spot-delisting overreaction** (holders who cannot or will not move tokens off Binance must sell before the delisting date) | Binance "Will Delist X, Y on DATE" announcements (catalog 161 as stored, 2022-12..2026-10: 33 announcements, 23 from 2024-07, counted from titles before any price was fetched). For each non-stablecoin token (USDP, TUSD, BUSD, USDC, DAI, FDUSD, PAX excluded) with a Binance `TOKENUSDT` spot 1h archive: buy at the announcement time + 24 h, sell at 00:00 UTC on the delisting date. Excess = return − BTC over the same window − 0.6%. Tokens in the same announcement are averaged | announcements 2022-12..2024-06: mean excess ≤ 0 | 2024-07–2026-10: ≥ 15 announcements, mean excess ≥ 3%, t ≥ 2 (venue: on-chain DEX spot) |
| 483 | **USO monthly roll** (USO rolls its front-month WTI futures on a fixed schedule) | Long USL, short USO from the close of the month's 6th trading day to the close of its 10th (assumed roll window: USO's historical "about two weeks before expiry", four days); net − 0.08% | 2010–2017: mean ≤ 0 | 2018–2026-10: mean ≥ 0.1%, t ≥ 2. Variant: UNG/UNL, same days |
| 484 | **Japanese ETF dividend cash-raising** (big TOPIX and Nikkei ETFs sell to raise cash for dividends settled on July 8–10) | D = the last Nikkei trading day ≤ July 10. Short ^N225 from the close 4 sessions before D to D's close; net − 0.04% | 2000–2012: mean ≤ 0 | 2013–2026: mean ≥ 0.5%, t ≥ 2 (about 14 events; low power stated). Variant: also January 8–10 |
| 485 | **MSCI quarterly review close** (index funds trade the review at the close of the last business day of Feb/May/Aug/Nov) | EEM: trade −sign(review-day close-to-close return) from the review-day close to the next close; net − 0.04% | 2004–2012: mean ≤ 0 | 2013–2026-10: mean ≥ 0.2%, t ≥ 2. Variant: EFA |
| 486 | **Australian super-fund hedge rebalancing** (super funds hedge foreign equities; after a strong month they must sell USD and buy AUD at the month-end fix) | Last trading day: R = average month-to-date return of SPY and EFA to the previous close. If R > +2% → long AUDUSD from 14:00 to 16:05 London; if < −2% → short. Net bp − 0.3 | 2012–2018: mean ≤ 0 | 2019–2026-10: mean ≥ 0.5 bp, t ≥ 2 |
| 487 | **Tax-loss selling rebound in small caps** (US investors sell losers before year-end for tax; the selling stops in January) | Long IWM, short SPY from the close of the last trading day ≤ Dec 15 to the close of the last trading day ≤ Jan 15; net − 0.08% | 2001–2012: mean ≤ 0 | 2013–2026: mean ≥ 0.5%, t ≥ 2 (13 events; low power stated) |

**Families.** If several pass in the same family, they count as one:
- fixings: #479 and #480 (and the month-end fix ideas #460, #486);
- month-end hedge rebalancing: #460 and #486;
- index-rebalance close: #485 and #456.

Stage 1 only kills; no stage passes early, and the Stage 2 rules are fixed now.

**Data (job `ubatchi`, run via `fetch_public.yml`):**
- Dukascopy BID 1-minute candles, one file per day, 2012-01..2026-10, for EURUSD, GBPUSD, USDJPY, AUDUSD, XAUUSD and XAGUSD.
  Only 5-minute closes between 09:00 and 22:00 UTC are kept.
- FRED IR3TIB01*M156N.
- Solana epoch first-slot block times.
- Binance spot 1h archive for the delisted tokens (announcements from `uncharted_w3_binance_ann.json`).
- Yahoo USO, USL, UNG, UNL, EEM, EFA, IWM.

**Script and output.** Script: `scripts/batch_i_20261126.py`. Output: `docs/jx_runs/batch_i_20261126.txt` (re-run once; it must be identical).

## Results (2026-11-26/27; `docs/jx_runs/batch_i_20261126.txt`, re-run identical). PARTIAL DATA for the FX and gold ideas
Dukascopy throttled both GitHub's servers and the session (≈ 8 s per day file). Data coverage:

| Data | Coverage |
|---|---|
| EURUSD | 516 days |
| AUDUSD | month-end days only (170 of 178) |
| XAUUSD | 2012-01..2014-11 only (682 days) |
| GBPUSD, USDJPY, XAGUSD | none |
| Solana epochs | complete (948, 2021-02..2026-11) |

The local fetch (`scripts/fetch_local_batchi.py`, resumable cache) hit the session's background time limit and is not restarted.

| # | Verdict | Key figures | $/yr |
|---|---|---|---|
| 478 FX triple-rollover | KILL | S1 −1.6 bp (EURUSD + AUD only) | — |
| 479 WM/R fix reversal | KILL | S1 −0.1 bp, S2 −0.9 bp (EURUSD only) | — |
| 480 LBMA gold auction | KILL | S1 −0.1 bp (2012–14 only); no Stage 2 data | — |
| 481 Solana epoch unstake selling | FAIL | S1 +0.01%, S2 −0.28% (t −1.69, n 679) | −$22K |
| 482 Binance delisting overreaction | KILL | −35.6% / −42.1% excess (the effect is the opposite: delisted tokens keep falling; shorting them is not possible from Malaysia) | — |
| 483 USO roll | KILL | S1 −0.00% | — |
| 484 Japanese ETF dividend selling | FAIL | S1 +1.15% (t 1.85), S2 +0.28% | $84 |
| 485 MSCI review close | KILL | S1 −0.85% | — |
| 486 AUD super-fund month-end | FAIL | S1 +3.4 bp, S2 +7.4 bp (t 1.84) | $850 |
| 487 tax-loss small-cap rebound | FAIL | S2 +0.56% (t 0.73) | $157 |

**Batch I verdict: 0 of 10.** #478–#480 are underpowered (partial data); none came close to $10K/yr.

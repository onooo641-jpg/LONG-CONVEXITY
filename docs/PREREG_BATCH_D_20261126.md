# Batch D (#443–#446): forced-flow ideas through the quality gate — pre-registered 2026-11-26, before any of their data are looked at

**How this batch was built.** What passed so far (wick family) is liquidity supplied to *forced* flow on a venue a small player can use.
Batch D looks for other forced or contractual flows. Each candidate went through the gate in `docs/NOTES_NONPROP.md`:
(1) a forced or paid counterparty, (2) a reason it persists for a small player, (3) a back-of-envelope ≥ $10K/yr on $15K,
(4) ≥ ~100 events/yr, (5) a venue usable from Malaysia, (6) a genuine out-of-sample.
22 candidates were screened. 4 passed the gate and are registered here. The 18 rejects are listed at the end with the reason.
Jx asked for 10 individual ideas per batch, but also said not to pad. This batch has 4: the other 18 failed the gate.

Common to the futures ideas (#443, #444, #446): own-account IBKR micro futures (IBKR accepts Malaysian residents; Topstep is not involved).
Costs and roll handling are the same as `docs/PREREG_20261120.md`. Round trip in points: NQ 1.12 (MNQ $2/pt), ES 0.748 (MES $5/pt), YM 4.48
(MYM $0.50/pt), RTY 0.448 (M2K $5/pt). Days in the 10 trading days before a quarterly expiry are dropped.
RTH close is the close of the 15:59 ET bar; "15:30 price" is the close of the 15:29 bar.
Days missing either bar are dropped, and so are early-close days.

**$/yr sizing (gate 3):** total notional is capped at 10× the $15,000 pot ($150K), split equally across the markets that signal that day.
Micros are floored, with a minimum of 1.
Stage 1 = 2010-07-01..2015-12-31 (kill-only). Stage 2 = 2016-01-01..2026-10-28 (PASS). This rule has never been run on either window.

| # | Idea (forced/paid counterparty) | Rule (main) | Stage 1 KILL if | Stage 2 PASS if (all) |
|---|---|---|---|---|
| 443 | **Leveraged-ETF close rebalancing** (TQQQ/SQQQ/UPRO/SPXL/SSO/QLD/TNA etc. must buy into up-days and sell into down-days at the close; the daily reset is contractual) | r = 15:30 price ÷ previous RTH close − 1; if \|r\| ≥ 1.0%, trade sign(r) from the 15:30 price to the RTH close | mean net ≤ 0 on both NQ and ES | on ≥ 3 of 4 markets mean net > 0 and t > 2; portfolio ≥ $10K/yr; worst calendar year ≥ −$5K; ≥ 6 of 11 years positive |
| 444 | **Vol-target / risk-control fund de-leveraging** (exposure ∝ 1/realised vol, rebalanced at the close with a lag; variable-annuity hedges) | σ20(d) = stdev of the 20 RTH close-to-close returns ending on day d. Δ = σ20(d−1)/σ20(d−2) − 1 (known at the close of d−1). On day d, if Δ ≥ +5% short, if Δ ≤ −5% long, from the 15:00 price (close of the 14:59 bar) to the RTH close | mean net ≤ 0 on both NQ and ES | same as #443 |
| 445 | **ve-token weekly epoch selling** (emissions/bribes/fees become claimable at the Thursday 00:00 UTC epoch flip; farmers paid in the token sell it). Tokens: CRV, CVX, BAL, PENDLE, AERO, VELODROME, THE (Thursday 00:00 UTC epochs from memory, assumed, not verified) | short token perp + long BTC perp (equal notional) from Thu 00:00 to Fri 00:00 UTC on Binance 1h closes; 0.05%/side × 4 sides; both legs' funding | 2020..2023-12: pooled mean net ≤ 0 | 2024-01..2026-10: pooled mean net ≥ 0.30%, week-clustered t ≥ 2, beats the same trade on the other 6 weekdays (Welch t ≥ 1.5), ≥ 4 tokens with mean > 0, ≥ $10K/yr at $5K per token-leg |
| 446 | **US Treasury auction concession** (dealers must absorb new supply, so yields rise into coupon auctions and fall after; Lou-Yan-Zhang 2013) | each Note/Bond coupon auction (2,3,5,7,10,20,30y; original issues and reopenings; no TIPS/FRN) with its FRED constant-maturity yield. PRE: short duration from the close of A−5 business days to the close of auction day A. POST: long from the close of A to A+5. Net bp = Δy(PRE) − Δy(POST) − 1.0 bp costs | 2009-01..2016-12: mean net ≤ 0 or week-clustered t < 1 | 2017-01..2026-10: mean net ≥ 1.0 bp, week-clustered t ≥ 2, ≥ 6 of 10 years positive, ≥ $10K/yr at DV01 $50 per event (one σ day ≈ 2% of the pot) with at most 3 overlapping, worst year ≥ −$5K |

Execution notes:
- #445 is measured on Binance (data) and would be executed on Hyperliquid/dYdX (Binance is not usable from Malaysia).
  A PASS triggers verification V: the same weeks on Hyperliquid 1h candles for the listed tokens (last ~200 days), same sign and ≥ 50% of
  the magnitude.
- #446 would be traded with CME micro 10-year yield futures or ZN/ZF/ZT micros on IBKR. FRED CMT yields (around the 15:30 close)
  stand in for futures; the auction is at 13:00 ET, so day A's close includes the result.

**Variants (reported; they cannot rescue a failed main rule).**
- #443:
  - thresholds 0.5% / 1.5%;
  - entry at 15:45;
  - Gao-Han-Li-Zhou "first half-hour predicts last half-hour": the sign of the previous close → 10:00 return, traded 15:30 → close on every day;
  - next-morning reversal: fade the signal from the RTH close to the next 10:00.
- #444:
  - thresholds ±2% / ±10%;
  - same-day version, with σ20 including the day's return to 15:00.
- #445: pre-epoch window, Wed 00:00 → Thu 00:00 UTC, short.
- #446: PRE leg alone; POST leg alone; 10-year auctions only.
- **#440 alt-coin variant** (registered here before its data exist; it is a variant of #440, not a new idea):
  - #440's exact rule on 40 Binance USDⓈ-M perps listed by 2021-06 (list in job `ubatchd`), 1h klines and funding archive;
  - Stage 1 2021-01..2022-12; Stage 2 2023-01..2026-10;
  - same thresholds as #440, with t clustered by settlement time.

**Data.** #443/#444 use the local Databento 1m files (NQ processed; ES/YM/RTY in `data/raw/`). #445 and the #440 variant use the Binance
archive (job `ubatchd`). #446 uses the FRED DGS2/3/5/7/10/20/30 CSVs and the fiscaldata.treasury.gov auctions_query API (job `ubatchd`).
Scripts: `scripts/batch_d_20261126.py`. Output: `docs/jx_runs/batch_d_20261126.txt` (re-run once, identical).

## Screened out at the gate (not tested; reason)
| Candidate | Failed gate | Why |
|---|---|---|
| Binance perp-delisting settlement convergence | 5 | forced and contractual, but Binance is not usable from Malaysia; HL/dYdX delistings are too few (gate 4) |
| IPO lock-up expiry shorts (US) | 5 | the anomaly survives because borrow is scarce or costly for small IPOs; a small IBKR account usually can't short them |
| HK / Bursa IPO ballots | 3 | expected value per identity ≈ US$40/IPO × 80/yr; scaling needs extra identities (not allowed) |
| Month-end pension rebalancing (stock-bond) | 4 | 12 events/yr |
| Bond-index month-end extension | 4 | 12 events/yr |
| Quarterly futures expiry TWAP / S&P rebalance close | 4 | 4 events/yr |
| VIX-expiry SOQ hedging | 4 | 12 events/yr |
| USD/JPY gotobi Tokyo fix | 3 | ~0.04% × 72 events at 10× notional ≈ $4K/yr; only clears $10K at ≥ 25× FX leverage |
| Commodity-index (GSCI) roll front-running | 6 | needs per-contract futures data (paid) |
| HK CBBC knock-out cluster reversal | 6 | no free intraday index data |
| Spin-off index selling | 4 | ~40 events/yr, multi-month holds |
| Fixed-ratio token mergers/migrations | 4 | ~5–10 events/yr |
| Court/estate/government coin sales (Mt.Gox etc.) | 4, 2 | few events; front-run by on-chain alert bots |
| Deribit weekly expiry pin (BTC/ETH) | 2 | the most-traded crypto pair, hedged by professionals; the monthly version (#439) already KILLED |
| Tether/USDC mint → BTC drift | 1 | no forced counterparty |
| CEX recurring-buy (DCA) schedule drift | 1, 3 | weak, diffuse flow |
| On-chain liquidation-level clusters | — | wick family (counts as one idea) and workstream B |
| Funding-settlement drift on alts | — | variant of #440 (registered above as a variant) |

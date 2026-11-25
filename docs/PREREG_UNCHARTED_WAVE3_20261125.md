# Uncharted wave 3: ten more testable ideas (#392–#401) — pre-registered 2026-11-25, before their data are fetched

Why: Jx asked for 15+ ideas that are testable with free data, worth testing, and not excluded. Of U1–U22, six such ideas are already
tested (`docs/PREREG_UNCHARTED_20261125.md`: #383, #384, #385, #387, #389, #391). These ten complete the set (16). Ideas and reasons:
`docs/IDEAS_UNCHARTED_20261125.md` (third wave). Stage 1 is kill-only; a survivor gets its own Stage 2 (other venue or forward) before
any claim. Data: GitHub Actions job `uwave3` (+ files already in `data/public/`).

**Event-study template (E)**, used by #393–#397: short the token's Hyperliquid perp at the Hyperliquid daily close of the UTC day that
contains the event; cover at the close H days later; hedge with an equal-notional BTC long; costs 4 × 0.045% plus Hyperliquid funding
(`hl_funding.parquet`, zero where missing — reported). Tokens need Hyperliquid candles on the entry and exit days. **Stage 1 (E):** with
≥ 15 events, KILL if the mean hedged return < 1% or t < 1; fewer than 15 events = not testable. Mean ≥ 2% with t ≥ 2 = Stage 2 worthy.

| # | Idea | Events (fixed now) | H | Extra rule |
|---|---|---|---|---|
| 392 | U9b Binance monitoring-tag additions | Binance announcements whose title contains "Monitoring Tag" and "Add" or "Extend", not "Remove"; tokens parsed from the title | 7 | Hyperliquid perp listed ≥ 7 days before |
| 393 | U23 Binance spot listings (not airdrop programmes) | titles starting "Binance Will List" (Seed Tag included) | 7 | Hyperliquid perp listed ≥ 7 days before |
| 394 | U24 Airdrop-distribution listings (HODLer Airdrops, Launchpool, Megadrop) | titles containing those words; token from the "(TICKER)" | 14 | entry = first Hyperliquid close on/after the announcement day, at most 5 days after it |
| 395 | U25 Korean KRW listings (Upbit, Bithumb) | first daily candle of a KRW market on Upbit or Bithumb (earliest), 2023-06-01..2026-10-24 | 7 | Hyperliquid perp listed ≥ 7 days before; only markets listed today (delisted ones missing: conservative for a short) |
| 396 | U26 Binance perp launches (short-sale constraint relief) | first daily kline of each Binance USDT-M perp (archive), 2023-06..2026-10 | 14 | Hyperliquid perp listed ≥ 14 days before (Binance adds a big shorting venue); note #44 failed on Hyperliquid's own listings |

**#397 U27 Cascade-day reversal.** Cascade day = ≥ 25% of Hyperliquid perps (≥ 30 days old, with a previous close) print a low ≥ 15%
below the previous close. Buy an equal-weight basket of the perps that printed such a low, at that day's close; hold 3 days; unhedged;
costs 2 × 0.045% + funding; a cascade day inside a running hold is skipped. Stage 1: with ≥ 8 events, KILL if the mean basket return
< 2% or fewer than 60% of events are positive. Context only: 10% threshold.

**#398 U28 BNB launchpool demand.** Events: Binance titles containing "Launchpool" or "Megadrop" (HODLer excluded: retroactive
snapshots). Long BNB / short BTC (equal notional, Hyperliquid) from the announcement-day close for 5 days; costs 4 × 0.045% + funding.
Stage 1: with ≥ 10 events, KILL if mean < 0.5% or t < 1.

**#399 U18 Crypto net-nets.** Monthly on the 1st over the last 12 months with CoinGecko market caps (free API limit: 365 days): every
protocol with a DefiLlama treasury and a CoinGecko id; buy (equal weight) tokens whose market cap < liquid treasury (stablecoins + majors,
own token excluded); hold 3 months. Benchmark: equal weight of all protocols with treasury data. Stage 1: KILL if fewer than 10 positions
or mean 3-month excess return < 5%. If the treasury history is not free, the test uses today's treasury only and says so.

**#400 U12 CoW AMM liquidity.** DefiLlama yield pools of the CoW AMM project with ≥ 180 days and max TVL ≥ $1M. LP return vs holding
= base APY − impermanent loss (50/50 constant-product formula, daily DefiLlama token prices, non-overlapping 30-day windows,
annualised). Stage 1: KILL if the median pool's (base APY − IL) < 10%/yr.

**#401 U4 Liquidity-bootstrapping pools (Balancer v2/v3, incl. Fjord).** Pools created by the Balancer LBP factories on Ethereum, Arbitrum
and Base (addresses from `balancer/balancer-deployments`), 2023-06..2026-10. LBP end = last day the pool has a GeckoTerminal candle with
volume; buy at that day's close; sell at the token's price 7 days later (DefiLlama, else its largest GeckoTerminal pool). Only LBPs
with ≥ $50K traded. Stage 1: with ≥ 10 LBPs, KILL if the median 7-day return ≤ 0; fewer = not testable.

**Commands.** `uv run python -m scripts.uncharted_wave3_20261125` (all ten) → `docs/jx_runs/uncharted_wave3_20261125.txt`, re-run once,
identical. Costs, holds and thresholds above do not change after data are seen.

## #397 Stage 2 — pre-registered 2026-11-25 after Stage 1 survived (26 events, mean +3.27%, 62% positive), before running it
Out-of-sample market: the same rule on Binance USD-M perps (`uncharted_389_binance_ohlc.parquet`, every USDT symbol incl. delisted),
2020-01..2026-10, ≥ 25% of eligible perps wicking ≥ 15%, equal-weight basket of the wicked perps bought at that day's close, 3-day hold,
2 × 0.045% costs, no funding (not in that file; reported). PASS if ≥ 8 events, mean ≥ 2%, ≥ 60% positive and t ≥ 2. A pass still needs a
forward check before money (cascade days are rare: a few a year).

## Stage 2 for #393, #394, #395 — pre-registered 2026-11-25 after Stage 1, before Stage 2 data are fetched
Stage 1 (Hyperliquid, 2023-06..2026-10): #395 Korean listings 33 events +9.26% t 5.28; #394 airdrop listings 26 events +12.82% t 2.47;
#393 Binance listings 20 events +6.59% t 1.23. Stage 1's Korean universe was partial (Upbit 161 of 301 markets; Bithumb 0 — fetch time cap;
order = Upbit's market list, not outcome-based).
**Out-of-sample in time and venue:** events from 2020-01-01 to 2023-05-31 (before the Stage 1 window), priced on Binance USD-M perps
(`uncharted_389_binance_ohlc.parquet`; the token's USDT perp must have traded ≥ 7 days before the event for #393/#395; for #394 the first
Binance perp close on/after the event, at most 5 days later). Same rule as Stage 1: short at the event-day close, hold H (7 / 14 / 7),
equal BTCUSDT long hedge, 4 × 0.045% costs, Binance funding (`cryptotrend370_funding.parquet`). Events: Binance announcements
(category 48, fetched back to 2020) and complete Upbit + Bithumb KRW first-candle dates (job `uw3b`).
**PASS** (each idea separately): ≥ 15 events, mean ≥ 2% and t ≥ 2. Also reported: Stage 1 re-run on the complete Korean universe (context).

---
## Stage 1 results (2026-11-25) — `uv run python -m scripts.uncharted_wave3_20261125` → `docs/jx_runs/uncharted_wave3_20261125.txt` (re-run identical)
Data: fetch run 45632635023 (Binance announcements: 1,250 / 2,050 / 400 items in categories 48 / 49 / 161; Upbit 161 of 301 KRW markets and
Bithumb 0 before the time cap; DefiLlama treasuries HTTP 402; no CoW AMM pools under that project name; 791 LBP pools found, 46 priced).
| # | Idea | Events | Mean | t | Verdict |
|---|---|---|---|---|---|
| 392 | Binance monitoring-tag additions | 5 | +5.29% | 0.49 | not testable (< 15) |
| 393 | Binance spot listings, fade (7 d) | 20 | +6.59% | 1.23 | survives (kill-only) |
| 394 | Airdrop-programme listings, short (14 d) | 26 | +12.82% | 2.47 | survives — Stage 2 worthy |
| 395 | Korean KRW listings, fade (7 d) | 33 | +9.26% | 5.28 (82% win, worst −5.8%) | survives — Stage 2 worthy |
| 396 | Binance perp launches | 17 | +8.67% | 0.99 | KILL |
| 397 | Cascade-day reversal | 26 (HL) / 72 (Binance) | +3.27% / +3.73% | 1.95 / 2.69 | survives; **Stage 2 PASS** |
| 398 | Long BNB after Launchpool/Megadrop | 49 | −0.98% | −1.41 | KILL |
| 399 | Crypto net-nets | — | — | — | not testable (DefiLlama treasuries now paid, HTTP 402) |
| 400 | CoW AMM liquidity | — | — | — | not testable (no pools found under the project name) |
| 401 | LBP end-of-sale | 0 usable | — | — | not testable (GeckoTerminal free history too short) |

## Stage 2 results (2026-11-25) — `uv run python -m scripts.uncharted_wave3_20261125` (re-run identical; data fetch run 45656285128)
Binance category-48 announcements 2020-01..2023-05: 886; Korean KRW markets (complete): 489 (Upbit 261, Bithumb 228).
- **#393 Binance listings fade — not testable out-of-sample:** 0 events (in 2020–23 Binance perps almost never existed ≥ 7 days before a
  Binance spot listing).
- **#394 airdrop-programme listings — FAIL:** 2 events (+25.5%, +6.0%); fewer than 15.
- **#395 Korean listings fade — FAIL:** 18 events, mean +3.70%, median +6.15%, **t 0.91** (< 2), win 72%, worst −31.8%; 2020 n 4 −12.1%,
  2021 n 7 +5.8%, 2022 n 3 +9.0%, 2023 n 4 +11.8%. Context: Stage 1 on the complete Korean universe (2023-06..2026-10) 96 events, +8.06%,
  t 6.47. The registered out-of-sample test fails; the only clean check left is forward (radar N12, addendum 5 of the radar pre-registration).

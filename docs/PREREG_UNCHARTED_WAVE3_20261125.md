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

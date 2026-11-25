# #405–#409: five high-ceiling liquidity ideas — pre-registered 2026-11-25, before their data are fetched or analysed

Why: Jx asked for five more ideas that could plausibly reach ≥ $10K/yr on ~$15K, testable with free data, structural, Malaysia-usable
(Hyperliquid / Malaysia-eligible perp DEXes), not excluded. All five sit in the one family with evidence (#389, #397 passed
out-of-sample): paying liquidity to forced or impatient flow. Already-tested look-alikes excluded: #44 post-listing short, #37/#57 funding,
#208/#280 cross-venue funding gaps, #360 points farming (not measurable), #370 momentum. Stage 1 = kill-only; a survivor needs Stage 2
(the second venue named below, then forward paper) before any money. $15,000 pot throughout. Data: Actions job `ufive` + files in repo.

## #405 Oracle-dislocation buying (perp far below its index)
**Data.** Binance USD-M `premiumIndexKlines` 1h + 1h price klines, every USDT perp, 2022-01..2026-10 (trades computed in the job, only trades
saved). Second venue: Hyperliquid hourly funding premium + 1h candles (last ~200 days).
**Rule.** At an hour close where the premium index ≤ −P (P = 1.0% primary; 0.5%, 2% context), buy the perp at that close; exit at the
first hour close with premium ≥ −0.1%, or after 24 h. Size min($1,500, 1% of the previous day's USD volume); $15,000 pot per hour;
costs 2 × 0.045%; funding ignored on Binance (reported), included on Hyperliquid. One open trade per coin.
**Stage 1 (Binance):** KILL if mean net per trade < 0.3%, t < 3, or < $3,000/yr. **Stage 2:** Hyperliquid, same bars.

## #406 Hyperliquid spot (HIP-1) wick bids
**Data.** Hyperliquid spot pairs (spotMeta) daily candles from listing. **Rule.** #389 unchanged except fees: spot maker 0.04%, taker 0.07%
(assumed base tier). **Stage 1:** KILL if mean net per fill < 0.5%, t < 3, or < $3,000/yr. No second venue exists → Stage 2 is forward paper.

## #407 New-listing wick bids (first 30 days after a perp lists — the population #389 excluded)
**Data.** Hyperliquid daily candles (2023-06..2026-10); Binance USD-M daily OHLC (2020-01..2026-10) for Stage 2. **Rule.** #389's rule
(X 15%, 0.5% trade-through, previous-day volume sizing, $15,000 pot) applied only to days 2–30 after each perp's first candle. X 25% context.
**Stage 1 (Hyperliquid):** KILL if mean net per fill < 0.5% or t < 3. **Stage 2 (Binance):** PASS if mean ≥ 0.5%, t ≥ 3, ≥ $3,000/yr,
and ≥ 4 of 6 full years positive.

## #408 Market-neutral 1-day reversal across perps
**Data.** Hyperliquid daily candles + `hl_funding.parquet` (2024–26 funding; 2023 without); Binance daily OHLC + funding
(`cryptotrend370_funding.parquet`) for Stage 2. **Rule.** Each day at the close, universe = perps ≥ 30 days old in the top 100 by the
previous 30 days' USD volume; long the 10% with the lowest day return, short the 10% with the highest, equal weight, equal gross per side;
hold one day; costs 0.045% per side on each leg's traded notional (full daily rebalance) + funding. Returns on capital = long leg + short leg
per $1 per side. **Stage 1 (Hyperliquid):** KILL if mean daily net < 0.05%, t < 3, or annualised < 20% on capital. **Stage 2 (Binance
2020–26):** PASS if annualised ≥ 20%, t ≥ 3, and ≥ 4 of 6 full years positive.

## #409 Cross-venue price gaps (fragmentation)
**Data.** 1h candles for coins listed on Hyperliquid and at least one of Lighter, Aster, Paradex, dYdX v4 (as far back as each API gives,
capped at 120 days). Stage 0: each venue's Malaysia eligibility from its terms (`wickscale_terms.json`); ineligible venues reported, not counted.
**Rule.** At an hour close, if two venues' closes for the same coin differ by ≥ 1.0%, buy the cheap venue, sell the rich one (equal
notional $1,500, at most 5 open pairs); close both at the first hour close with the gap ≤ 0.2%, or after 24 h. Assumed taker fees per side:
Hyperliquid 0.045%, Lighter 0%, Aster 0.04%, Paradex 0.03%, dYdX 0.05%; funding ignored (≤ 24 h, reported as a limit).
**Stage 1:** KILL if mean net per pair < 0.3%, t < 3, or < $3,000/yr. Stage 2: forward paper on live quotes.

**Commands.** `uv run python -m scripts.five_high_20261125` → `docs/jx_runs/five_high_20261125.txt` (re-run once, identical). Thresholds,
costs and universes above do not change after data are seen.

---
## Results

### #407 New-listing wick bids — **KILL** (2026-11-25)
`uv run python -m scripts.five_high_20261125` (part #407). Hyperliquid, days 2–30 after listing, X 15% (primary): 529 fills on 122 coins,
mean +1.48% (median +0.40%), **t 2.47 < 3** → KILL; $3,493/yr; worst peak-to-trough −$3,993. Context only (not used): X 25% +6.06%, t 4.34,
$3,922/yr; Binance X 15% +1.32%, t 3.24, $6,676/yr. Even the best context variant is ~$4–7K/yr: not high-potential.

### #408 Market-neutral 1-day reversal — **KILL** (2026-11-25)
Hyperliquid 2023-06..2026-10: gross reversal +0.070%/day but daily rebalancing costs 0.148%/day → net −0.076%/day, t −0.69, −42.8%/yr.
Binance 2020–26 (context): gross +0.106%/day, net −0.077%/day, −55.8%/yr. The reversal exists but is smaller than taker costs.

## Addendum (2026-11-25, before their data are fetched): #410 and #411
Jx: "killed doesn't count — find five that don't get killed." Nothing can be guaranteed before a test; these two are chosen for a high prior
(same mechanism as #389, which passed out-of-sample) and are judged only on data no rule here has seen. Note for the reader: survivors from
one family are one bet in several forms (they all lose together in crash regimes); this is stated wherever they are summed.

**#410 Deeper wick ladder on unseen venues.** Data: the #403 venues (dYdX v4, Aster, Lighter, Paradex daily candles, `wickscale_*_1d`).
Rule: #389 unchanged except the bid levels: 25% and 35% below the previous close (each level its own size min($1,500, 1% of the previous
day's USD volume); the 15% level belongs to #403 and is excluded here); all fills sold at the close; $15,000 pot. Stage 1, pooled over
venues with ≥ 1 year of data: KILL if mean net per fill < 1.0%, t < 3, or < $2,000/yr in total.

**#411 Wick bids on Hyperliquid HIP-3 markets** (builder-deployed perps: stocks, commodities, indices). Data: every HIP-3 dex's markets
(`perpDexs`, `meta` per dex) daily candles from listing. Rule: #389 unchanged (X 15%, previous-day volume sizing, $15,000 pot, first 30
days excluded). Stage 1: KILL if mean net per fill < 0.5%, t < 3, or < $2,000/yr; fewer than 30 fills = not testable.

### #405, #406, #409, #411 (2026-11-25) — `uv run python -m scripts.five_high_20261125` → `docs/jx_runs/five_high_20261125.txt` (re-run identical)
Data: fetch run 45641135392.
- **#405 oracle dislocations — KILL.** Binance P 1%: 7,842 trades, −0.56%/trade (t −3.21), −$16,243/yr (2022 +$15.0K, 2023 +$1.9K, 2024
  +$2.8K, 2025 −$14.3K, 2026 −$83.9K). Hyperliquid last 120 days (context): −0.79%, −$2,820/yr.
- **#406 Hyperliquid spot wick bids — survives (kill-only)**, but weakly shaped: 7,410 fills on 259 pairs, mean +7.54% (t 4.38), **median
  −1.49%**, win 37%; $27,524/yr of which 2024 $59,340, 2025 $5,295, 2026 $5,420. Belongs to the wick family (one idea with #389).
- **#409 cross-venue gaps — INVALID MEASUREMENT (not a survivor).** The rule printed +1.25%/pair, t 32.9, $105,874/yr, but 80.7% of dYdX
  hours and 28.3% of Aster hours have an unchanged close (no trades): the "gaps" are stale prices. On the 10 most liquid Hyperliquid coins,
  Aster–Hyperliquid gaps ≥ 1% occur in 0.03% of hours. Hourly closes cannot test this; only live order-book quotes can (forward only).
- **#411 HIP-3 wick bids — KILL:** 144 fills, +1.19%, t 1.39, $1,811/yr.
- Check on #403 (dYdX) against the same stale-price problem (context, `wick_scale` data): by previous-day volume, fills on markets with
  $1–10M/day average +7.16% (t 11.39) and > $10M/day +5.48% (t 4.93) — the dYdX result is not a thin-market artefact.

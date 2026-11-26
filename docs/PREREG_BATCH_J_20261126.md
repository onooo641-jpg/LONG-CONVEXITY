# Batch J (#488–#492): leverage-crowding and forced-deleveraging ideas on Coinalyze open-interest and liquidation history — pre-registered 2026-11-26, before any of their data are looked at

**Why this batch is 5 ideas, not 10.**
- Batches C–I (~70 ideas) used up the structural payers that free price, funding and calendar data can test.
- Coinalyze (Jx's free API key, passed in memory and never stored) adds daily open interest (OI) and liquidations back to 2020 on 28
  venues. That opens a small new set of payers.
- Only ideas with a named forced or paying counterparty are included. They are not padded to 10.

**Gate (Jx's calibration).** Each idea needs:
- a structural payer;
- free data;
- Hyperliquid as the Malaysia-usable venue (all coins tested are listed there or traded as perps);
- a time split.

$/yr is reported at a safe size with every verdict.

**New replication rule (lesson from #468).** A crypto idea counts only if it passes Stage 2 (the 40 `batchd_alts` perps, 2023-01..2026-10)
**and** Stage 3 (the 110 unseen perps of `batchh2_unseen`, same period, never used to design anything here). Bybit is reported as a
second-venue check.

**Families.** #491 and #492 are forced-liquidation ideas (family 1, the wick family). If they pass they add capacity to family 1 but are
**not** a new family. #488, #489 and #490 would each be new.

**Data:**
- Prices: Binance 1h archive (`batchd_alts_1h`, `batchh2_unseen_1h`). The daily close at date d = the price at 00:00 UTC of d+1 (`at` convention).
- Funding: Binance archive (`batchd_alts_funding`, `batchh2_unseen_funding`).
- OI (base-asset units) and liquidations (USD, `l` = longs liquidated, `s` = shorts liquidated): Coinalyze daily history for
  `{SYM}USDT_PERP.A` (Binance), and `{SYM}USDT.6` plus Bybit daily OHLCV for the Bybit check.

Fetched from the session by `scripts/fetch_coinalyze_j.py`. The key is read from the environment and is never written to disk or printed.

**Costs and sizing:**
- Cost: 0.09% per round trip per leg.
- Safe size: $45K notional per signal ($15K × 3); for the cross-section, $22.5K per side.

| # | Idea (payer) | Exact rule | Stage 1 KILL if (40 alts, 2020-07..2022-12) | Stage 2 + Stage 3 PASS if (2023-01..2026-10) |
|---|---|---|---|---|
| 488 | **OI-growth crowding** (late leveraged longs who pile in pay funding and get liquidated; coins whose OI in coin units jumps underperform) | Every Monday 00:00 UTC, for coins with ≥ 30 days of OI and OI value ≥ $5M: g = 7-day % change in OI (base units). Short the top quintile, long the bottom quintile, equal weight, hold 7 days. Weekly return = mean(long) − mean(short) − 0.18% | mean weekly ≤ 0 | each stage: ≥ 100 weeks, mean weekly > 0, t ≥ 2 |
| 489 | **Crowded-funding short** (re-test of #423, untestable then on 6 Hyperliquid events): longs paying ≥ 0.05%/8h while OI makes a 30-day high | Per coin, day d: mean Binance funding on d ≥ 0.05% per settlement and OI(d) = max of the last 30 days → short the coin from d's close for 7 days, long BTC as a hedge (equal notional). P&L = −r_coin + r_BTC + coin funding received − BTC funding paid − 0.18%. One open trade per coin; events on the same day are averaged | mean ≤ 0 | each stage: ≥ 30 events, mean ≥ 1%, t ≥ 2 |
| 490 | **Aggregate leverage extreme** (when coin-unit OI across Binance + Bybit is far above its 90-day norm after a rally, the next drop forces deleveraging) | BTC: OI = BTC units, Binance USDT perp + Bybit USDT perp. z = (OI − mean of the prior 90 days) / std. If z ≥ 2 and BTC's 7-day return > 0 → short BTC from d's close for 7 days (no overlap) | mean ≤ 0 | BTC S2: ≥ 10 events, mean ≥ 1%, t ≥ 2; **Stage 3 = ETH, same rule**: mean > 0, t ≥ 1.5 |
| 491 | **OI flush rebound** (family 1: forced deleveraging finished) | Per coin: OI (base) falls ≥ 20% from d−1 to d and the close-to-close return on d ≤ −8% → long from d's close for 3 days; − 0.09% | mean ≤ 0 | each stage: ≥ 30 events, mean ≥ 1%, t ≥ 2 |
| 492 | **Short-squeeze fade** (family 1 mirror: forced short covering overshoots) | Per coin: shorts liquidated on d ≥ 2% of the OI value (OI(d−1) × close(d−1)) and the close-to-close return on d ≥ +10% → short from d's close for 3 days; − 0.09% | mean ≤ 0 | each stage: ≥ 30 events, mean ≥ 1%, t ≥ 2 |

Same-day events across coins are averaged into one observation before the t-test (#489, #491, #492). Stage 1 only kills. No stage passes
early. Stage 3 data are not looked at before Stage 2 is computed: the script prints Stage 3 only after printing Stage 2.

**$/yr.** Computed on the Stage 2 sum at the safe size; for #489, #491 and #492, at most 3 trades open at once.

**Script and output.** Script: `scripts/batch_j_20261126.py`. Output: `docs/jx_runs/batch_j_20261126.txt` (re-run once; it must be identical).

## Results (2026-11-26; `docs/jx_runs/batch_j_20261126.txt`, re-run identical)
Coinalyze covered 110 of the 150 Binance symbols (most of the missing 40 are delisted), so Stage 3 used 73 of the 110 unseen perps.

| # | Verdict | Stage 1 / Stage 2 / Stage 3 | $/yr at safe size |
|---|---|---|---|
| 488 OI-growth crowding | KILL | −0.72% (t −0.67) / +0.38% (t 0.89) / −0.56% | $4.5K (S2, not significant) |
| 489 crowded-funding short | KILL | −2.62% (t −1.64) / +1.35% (t 0.37) / +5.31% (t 2.31) | −$5.8K |
| 490 aggregate leverage (BTC; ETH Stage 3) | FAIL | +0.24% / +2.28% (t 1.39) / ETH −1.51% | $4.5K |
| 491 OI flush rebound (family 1) | FAIL | +3.44% (t 1.79) / +3.23% (t 1.58) / −1.85%; Bybit −1.28% | $25.6K on S2, but does not replicate |
| 492 short-squeeze fade (family 1) | FAIL | +1.28% / −2.64% / +0.17%; Bybit +0.98% | −$65K |

**Batch J verdict: 0 of 5.** No idea held on both the 40 alts and the unseen perps. That is the same failure #468 showed.

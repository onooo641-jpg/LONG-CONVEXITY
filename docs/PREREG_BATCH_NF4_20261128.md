# Batch NF4 (#547–#550): Korean retail flows traded on Hyperliquid — pre-registered 2026-11-28, before running

**Niche and desk checks.**
- **Payer:** Korean retail on Upbit, which is price-insensitive and herd-driven.
- **G6:** Korea's capital controls keep foreign arbitrage out, so coin-level kimchi premia and Upbit frenzies are not arbitraged
  away by funds.
- **G5:** every trade is on the Hyperliquid perp (usable from Malaysia).
- **Data:** `distinct_upbit_1d` (Upbit KRW close and KRW value traded, 301 coins, 2020-05..2026-11); HL daily candles
  (`uncharted_385_candles`; Upbit "PEPE" matches HL "kPEPE"). Upbit KRW listings: `uncharted_w3b_korea`.
- **Not repeats:**
  - #395 is the KRW listing-day fade (its forward log is radar N12);
  - Korea ideas in Batch 10 / DISTINCT used the market-wide premium, not coin-level premia or Upbit volume.

**Rule basics.**
- Signals use day d's Upbit data (KST day ends 15:00 UTC, before the HL daily close at 24:00 UTC, so it is known in time).
- **Entry:** at HL's close of day d. **Exit:** at HL's close of d + h.
- **Excess** = side × (coin − HL BTC) − 0.09%. Funding not modelled.
- At most one open trade per coin; BTC and stablecoins excluded.

| # | Idea | Signal on day d | Side, hold |
|---|---|---|---|
| 547 | **Upbit retail frenzy fade** (Korean retail chases; foreigners cannot arbitrage in, so the frenzy overshoots globally too) | KRW value traded ≥ 10 × its median of the previous 30 days and ≥ ₩50bn | short HL, 3 days |
| 548 | **Coin-level kimchi premium → global catch-up** (Korean demand the capital controls bottle up leaks out through arbitrage and front-running) | relative premium = (KRW close ÷ HL close) ÷ (BTC KRW ÷ BTC HL) − 1 ≥ +8%, after < +8% the day before | long HL, 3 days |
| 549 | **Coin-level kimchi discount → Korean selling spills over** (warnings and delisting fears make Korean holders dump) | relative premium ≤ −5%, after > −5% the day before | short HL, 3 days |
| 550 | **Dying KRW listing** (Korean listing pump fades as retail leaves; #540's Korean twin) | an Upbit KRW market listed on day L (`uncharted_w3b_korea`, Upbit only) whose day-7 KRW value < 20% of day 1's | short HL at day 7's close, 14 days |

**Split:** signals before 2025-01-01 = Stage 1 (kill-only); 2025-01-01 onward = Stage 2.

**Stage 1 KILL:** mean ≤ 0 (≥ 8 trades).

**Stage 2 PASS:** ≥ 15 trades, mean excess ≥ 2%, t ≥ 2, sum still positive without the 3 best trades.

**$/yr:** $3,000 per trade.

**Script/output:** `scripts/batch_nf4_20261128.py` → `docs/jx_runs/batch_nf4_20261128.txt`, re-run identical.

## Results (2026-11-28; `docs/jx_runs/batch_nf4_20261128.txt`, re-run identical): 0 of 4 by rule
| # | Verdict | Stage 1 | Stage 2 |
|---|---|---|---|
| 547 Upbit frenzy fade | KILL | −0.26% (n 274, median +2.4%) | **+2.28% (n 323, t 3.17, win 67%, positive without the top 3)**, $11.7K/yr |
| 548 coin kimchi premium → long | FAIL | n 2 | −1.15% (n 33) |
| 549 coin kimchi discount → short | FAIL | n 0 | n 3 |
| 550 dying Upbit listing short | KILL | −10.3% (n 17) | +5.97% (n 47, t 2.02) |

**Baseline check** (diagnostic after the verdicts): a random short of any HL alt against BTC made +0.33% / +0.95% / +1.99% over
3 / 7 / 14 days in 2025-01..2026-10, and −0.15% / −0.21% / −0.10% in 2023-06..2024-12.
- Part of every "short small coins, works only in 2025–26" result is the market-wide fall of alts against BTC, not an edge.
- #547 (+2.28% vs +0.33%), #540 (+7.18% vs +1.99%) and #544 (+11.1% vs +0.95%) still beat that baseline clearly.

## Addendum 1 (2026-11-28, before 2026-12-01): forward-only #551; baseline bar added to #541/#542
- **#551 = #547 forward:** radar N12 logs Upbit frenzy signals for HL coins from 2026-12-01 (`upbit_frenzy_signals.parquet`).
  - Each is a short of the HL perp from that day's HL close for 3 days, excess vs BTC, − 0.09%.
- **#551 PASS by 2027-03-31:**
  - ≥ 30 signals;
  - mean excess ≥ 1.0% **and** ≥ 1.0 percentage point above the random-short baseline over the same window and hold;
  - sum positive without the 3 best.
- **The same baseline condition is added to #541/#542** (`docs/PREREG_BATCH_NF2_20261128.md`): beat the random-short baseline of HL
  alts over the same window and hold by ≥ 1.0 percentage point. Their other bars are unchanged.

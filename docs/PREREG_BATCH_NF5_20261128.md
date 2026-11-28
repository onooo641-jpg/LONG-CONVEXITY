# Batch NF5 (#552–#555): more Korean retail flows traded on Hyperliquid — pre-registered 2026-11-28, before running

**Data, venue and desk checks** as NF4 (`docs/PREREG_BATCH_NF4_20261128.md`): Upbit daily KRW close and value, HL daily candles,
`uncharted_w3b_korea` listings.
- **Rule basics:** entry at HL's close on the signal day; excess = side × (coin − HL BTC) − 0.09%; one open trade per coin.
- **Alt shorts are judged against the random HL alt-short baseline** for the same hold and period. A short passes only if its Stage-2
  mean beats that baseline by ≥ 1.0 percentage point (baseline 2025–26: 3 d +0.33%, 14 d +1.99%).

| # | Idea (payer) | Signal | Side, hold |
|---|---|---|---|
| 552 | **Korean interest collapse** (once Korean retail leaves an established coin, the bid that held it up is gone) | 30-day average KRW value < 20% of the 30-day average 90 days earlier, coin listed on Upbit ≥ 180 days | short HL, 14 days |
| 553 | **Dying Bithumb listing** (#550's twin on the second Korean exchange) | Bithumb-only KRW listing whose day-7 Upbit-equivalent is unavailable, so instead: HL price at day 7 < day 1, and the listing is on Bithumb (`uncharted_w3b_korea`) | short HL at day 7, 14 days |
| 554 | **Upbit panic dump, long side** (Korean holders dumping at any price; liquidity provision on HL) | KRW value ≥ 10 × the 30-day median **and** Upbit close ≤ −20% versus the previous Upbit close | long HL, 3 days |
| 555 | **Upbit pump day** (the subset of #547 where retail chases a price spike) | KRW value ≥ 10 × the 30-day median **and** Upbit close ≥ +30% versus the previous close | short HL, 3 days |

**Split:** signals before 2025-01-01 = Stage 1 (kill-only); 2025 onward = Stage 2.

**Stage 1 KILL:** mean ≤ 0 (≥ 8 trades). For shorts, mean ≤ the Stage-1 baseline counts as ≤ 0.

**Stage 2 PASS:** all of
- ≥ 15 trades;
- mean ≥ 2%;
- t ≥ 2;
- sum positive without the 3 best;
- shorts: ≥ baseline + 1.0 percentage point.

**$/yr:** $3,000 per trade.

**Script/output:** `scripts/batch_nf5_20261128.py` → `docs/jx_runs/batch_nf5_20261128.txt`, re-run identical.

## Results (2026-11-28; `docs/jx_runs/batch_nf5_20261128.txt`, re-run identical)
| # | Verdict | Stage 1 | Stage 2 | Short baseline (S1 / S2) |
|---|---|---|---|---|
| 552 Korean interest collapse | FAIL | +2.92% (t 2.83, 90) | +2.11% (t 2.46, 223) | −0.10% / +1.99%: beats it by 3.0 points before 2025, only 0.12 points after |
| 553 dying Bithumb listing | FAIL | n 0 | −2.91% (134) | — |
| 554 Upbit panic dump long | FAIL | −7.72% (n 5) | −0.94% (n 16) | — |
| **555 Upbit pump day short** | **PASS** | +3.25% (41, median +7.9%) | **+4.54% (t 2.49, 54, median +8.1%), positive without the 3 best** | −0.15% / +0.33%: beats it by 4.2 points |

#555 is small (~$3.9K/yr at $3,000 per trade, about 30 signals a year).
- It is the one Korean-flow rule that survives both periods and the baseline. When Korean retail pumps a coin +30% on 10× volume,
  the HL perp gives most of it back within 3 days.
- **Forward:** radar N12b's signal log now records the Upbit price change. #555 = signals with chg ≥ +30%.
- **#555 S2c (fixed now), 2026-12-01 → 2027-03-31:** ≥ 10 signals, mean excess ≥ 2% and ≥ baseline + 1 point, positive without the
  best signal. Extended to 2027-06-30 if fewer than 10.

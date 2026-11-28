# Batch NF6 (#556–#559): local-retail frenzies on Turkish and Indonesian exchanges, traded on Hyperliquid — pre-registered 2026-11-28, before data are fetched

**Why.** #555 (shorting HL on Upbit pump days) passed both periods and beat the random-short baseline. The mechanism: local retail
chases a coin, and capital frictions keep foreign arbitrage from absorbing it. Turkey (BtcTurk, TRY pairs) and Indonesia (Indodax,
IDR pairs) have large local retail markets with local-fiat friction.
- **G5:** trades are HL shorts (usable from Malaysia).
- **G6:** local-fiat access barrier; small capacity.
- **Data:** job `ubatchnf6`, daily candles from BtcTurk's and Indodax's public chart APIs, all their local-fiat pairs whose base coin
  is on HL. HL daily candles as NF4/NF5.

**Rule basics:**
- Signal on the local exchange's day d candle; entry at HL's close of day d.
- Excess = −(coin − HL BTC) − 0.09%. One open trade per coin per idea.
- Local volume = base volume × close, in local currency, compared only with the same pair's own history.

| # | Idea | Signal (on the local exchange) | Side, hold |
|---|---|---|---|
| 556 | **BtcTurk pump day** | volume ≥ 10 × its median of the previous 30 days **and** close ≥ +30% versus the previous close | short HL, 3 days |
| 557 | **Indodax pump day** | same on Indodax | short HL, 3 days |
| 558 | **BtcTurk frenzy** (any price move) | volume ≥ 10 × the 30-day median | short HL, 3 days |
| 559 | **Indodax frenzy** | same on Indodax | short HL, 3 days |

**Split:** signals before 2025-01-01 = Stage 1 (kill-only); 2025 onward = Stage 2.

**Stage 1 KILL:** mean ≤ the Stage-1 random-short baseline (≥ 8 trades).

**Stage 2 PASS:** all of
- ≥ 15 trades;
- mean ≥ 2%;
- t ≥ 2;
- sum positive without the 3 best;
- mean ≥ the Stage-2 baseline + 1 point.

The baseline is a random HL alt short against BTC over 3 days: −0.15% before 2025, +0.33% after (NF4).

**If an exchange's history cannot be fetched,** its two ideas are reported as not testable.

**$/yr:** $3,000 per trade.

**Script/output:** `scripts/batch_nf6_20261128.py` → `docs/jx_runs/batch_nf6_20261128.txt`, re-run identical.

## Results (2026-11-28; `docs/jx_runs/batch_nf6_20261128.txt`, re-run identical): 0 of 4
| # | Verdict | Stage 1 | Stage 2 |
|---|---|---|---|
| 556 BtcTurk pump day | KILL | −4.90% (38) | +1.40% (71, t 0.73) |
| 557 Indodax pump day | FAIL | +6.25% (61, t 2.29) | +2.71% (129, t 1.27): only 2.4 points over the baseline, t < 2 |
| 558 BtcTurk frenzy | KILL | −2.27% (402) | +0.74% (1,051) |
| 559 Indodax frenzy | KILL | −0.52% (761) | +0.47% (1,810) |

#555's Korean result does not generalise to Turkey or Indonesia.
- Indodax pump days come closest: positive in both periods, but too noisy.
- Korean retail (Upbit) is the strongest local-retail payer, consistent with its size relative to global volume.

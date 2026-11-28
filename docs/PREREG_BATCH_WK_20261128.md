# Batch WK (#521–#525): refine and stress-test #520 (volatility-scaled wick bids) — pre-registered 2026-11-28, before running

**Why.** Brand-new areas (Batches L–P) found nothing; refining the one working mechanism found #520. This batch follows the refinement
protocol (`docs/REFINEMENT_TRIAGE_20261122.md`):
- at most 5 variants, chosen on development data only;
- each chosen rule is run once on unseen data;
- where a variant was selected, unseen data must also pass with costs × 1.5.

**Family:** all family 1 (forced liquidations); they count once toward the goal. A pass here improves or enlarges #389/#520.

**Base rule (#520).**
- Daily candles; resting buy at previous close × (1 − X), X = k × σ30.
  - σ30 = stdev of the previous 30 daily close-to-close returns; X is clipped to [5%, 30%].
- Fill if the low is ≥ 0.5% through the level; price = the level, or the open if lower.
- Exit at the close.
- Size = min($1,500, 1% of the day's USD volume); one $15,000 pot per day.
- Perps: 0.015% maker + 0.045% taker. Spot: 0.04% + 0.07%.
- First 30 days after listing excluded.

| # | Test | Exact rule | Dev (Stage 1) | Unseen (Stage 2) | PASS if (Stage 2) |
|---|---|---|---|---|---|
| 521 | **Distance multiplier** | k ∈ {2, 3, 5, 6} (k = 4 is #520). Pick the k with the highest Stage-1 $/yr, then run it once on Stage 2 with costs × 1.5 | HL perps 2023-06..2024-12 | 2025-01..2026-10 | ≥ 30 fills, mean ≥ 0.3%, t ≥ 2, **$/yr above #520's $6,374** |
| 522 | **Hold one more day** (the rebound may continue past the first close) | #520, exit at the next day's close instead of the same day's | same | same | mean ≥ 0.3%, t ≥ 2, $/yr above #520's |
| 523 | **#520 on HIP-3 builder perps** (stocks, indices, commodities; fixed X failed in Batch N) | #520 rule, k = 4 | 2025-11-01..2026-04-30 | 2026-05-01..2026-11-25 | ≥ 30 fills, mean ≥ 0.3%, t ≥ 2, ≥ $1,000/yr added |
| 524 | **#520 on Hyperliquid spot tokens** | #520 rule, spot costs | 2024-05-01..2025-06-30 | 2025-07-01..2026-11-25 | same as #523 |
| 525 | **#520 on Binance USDⓈ-M perps** (robustness: is the effect venue-specific? Binance is not usable from Malaysia, so this is evidence only) | #520 rule; size from Binance quote volume | 2023-06..2024-12 | 2025-01..2026-10 | ≥ 30 fills, mean ≥ 0.3%, t ≥ 2 (reported as "mechanism confirmed / not") |

**Stage 1 KILL (all):** mean net per fill ≤ 0.3% with ≥ 30 fills.

**Data (all in the repo):** `uncharted_385_candles`, `fivehigh_hip3_1d`, `fivehigh_hl_spot_1d`, `uncharted_389_binance_ohlc`.

**Script/output:** `scripts/batch_wk_20261128.py` → `docs/jx_runs/batch_wk_20261128.txt`, re-run identical.

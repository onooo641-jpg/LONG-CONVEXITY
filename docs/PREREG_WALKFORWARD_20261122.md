# Walk-forward retest of 16 implementation-sensitive ideas with large configuration grids — 2026-11-22

Written and committed before any grid is run. Jx: 5 configurations is too few. More configurations raise selection luck, so the method changes from
one year-1/year-2 split to a **walk-forward**: every config's daily return series is computed once over 2024-11..2026-10; then **each month, the config
with the best trailing-6-month return is chosen and applied to the next month only**. The concatenated out-of-sample (OOS) months 2025-05..2026-10
(18 months) are the result; no choice ever uses future data, however many configs the grid has.
- **Switching:** when the chosen config changes, one round-trip of that study's trading cost is charged.
- **PASS:** OOS ≥ 8%/yr on capital in both OOS halves (2025-05..2026-01 and 2026-02..2026-10) **and** OOS ≥ 8%/yr over all 18 months with every cost
  ×1.5 (the whole walk-forward re-run). Also printed (never used for the verdict): the best fixed config in hindsight and how often configs switched.
- Data, costs and stress rules as in each original test unless a grid dimension says otherwise.

| grid | idea(s) | dimensions (all combinations) | configs |
|---|---|---|---|
| G1 | #208 funding gaps | entry {5,10,15,20,30}%/yr × exit-below {0,5,10}% × fee {taker 0.05%, maker 0.015% per leg-side} × pairs {all 3, without HL–dYdX, dYdX–Aevo only} × max positions {3,5,8} | 270 |
| G2 | #221 GMX GM (real GM prices) | hedge ratio {0.0 … 1.0 step 0.1} + dynamic-beta | 12 |
| G3 | #201–204 stable-yield selection (fallback universe) | min TVL {5,20,50,100M} × min age {90,180,365 d} × top k {3,5,10} × rank window {30,90 d} × reward-share filter {off, ≤50%} | 144 |
| G3b | #224 stable-pair LPs + #227 savings (batch-4 universes) | universe {224, 227, both} × min TVL {5,20,50M} × k {3,5} × window {30,90} | 36 |
| G3c | #278 new-chain incentives | min TVL {5,20M} × k {3,5,10} × window {30,90} × age {30,90 d} | 24 |
| G4 | #207 new reward programmes | start TVL {1,5,20,50M} × pool age {0,180,365} × min reward {0,3,5,10}% × hold {30,60,90 d} | 144 |
| G5 | #276 hedged HYPE staking | leverage {1.5,2,3} × in-position rule {always, trailing funding >0, >5, >8, >12%} | 15 |
| G6 | #225 Gains vaults | top k {1,2,3,all} × weighting {equal, TVL} × min TVL {0,1M,2M} × rank window {30,90} | 48 |
| G7 | #216/#217/#57 carry family (HL spot+short) | universe {BTC/ETH/SOL, 11 coins incl. HYPE, PAXG} × k {1,2,3,5} × threshold {0,5,10,15,20}% | 40 |
| G8 | #212/#213 hedged staking/farming | coin family {ETH, SOL, HYPE, AVAX, BNB, best-of} × hedge rule {always, only if trailing funding >0, >5} × leverage {2,3} (largest-TVL LST of the family, no churn) | 36 |
| G9 | #211 Pendle PTs | needs expired-market history fetch → registered with that fetch | — |
| G10 | #263/#264 tranches | only 383 days of data (< 6-month warm-up + 18 OOS months) → not testable by walk-forward; reported as such | — |
Command: `uv run python scripts/walkforward_20261122.py | tee docs/jx_runs/walkforward_20261122.txt`

## Results (2026-11-22, `docs/jx_runs/walkforward_20261122.txt`, re-run identical)
| grid | configs | OOS half 1 / half 2 | all 18 months, costs ×1.5 | verdict |
|---|---|---|---|---|
| G1 #208 funding gaps | 270 | 12.80% / 18.22% | 14.45% | **PASS** — picks maker-fee configs; post-hoc taker-only grid (`walkforward_g1_takeronly_20261122.txt`): 8.62% / 12.70% but 5.94% at costs ×1.5 → would FAIL. The pass depends on maker fills |
| G2 #221 GM pools | 12 | 14.18% / 0.08% | 7.07% | FAIL |
| G3 #201–204 stable selection | 144 | 4.91% / −4.27% | −0.32% | FAIL |
| G3b #224 / #227 | 36 | −4.11% / −10.22% | −7.87% | FAIL |
| G3c #278 new chains | 24 | 2.13% / −21.13% | −10.09% | FAIL |
| G4 #207 new rewards | 144 | −6.12% / −13.40% | −4.91% | FAIL |
| G5 #276 hedged HYPE staking | 15 | 14.97% / 8.72% | 11.86% | **PASS** (always picks 3×, always on; staking 2.5% assumed; liquidation risk unmeasured) |
| G6 #225 Gains vaults | 48 | 9.61% / 14.06% | 11.46% | **PASS** (capacity ~$2–3M; APY not yet checked against gToken prices) |
| G7 carry family | 40 | 7.62% / 3.67% | 3.52% | FAIL |
| G8 #212/#213 hedged staking, no churn | 30 | 13.24% / 5.99% | 9.12% | FAIL (half 2 < 8%) |
| G9 #211 Pendle / G10 #263–264 tranches | — | — | — | not run (data fetch needed / history too short) |

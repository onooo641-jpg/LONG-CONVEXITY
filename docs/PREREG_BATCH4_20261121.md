# Batch 4: perp-DEX liquidity vaults, stable-pair LPs, savings rates (#220–#225, #227) — 2026-11-21

Written and committed before any check below is run. Follows CLAUDE.md staged tests + PREREG_RADAR addendum 7:
**Stage 0.5** ceiling from data already in the repo (`data/public/llama_pools_now.parquet` snapshot 2026-11-20, `hl_funding.parquet`)
→ **Stage 1** pilot on the last 90 days only (fetched only for survivors) → **Stage 2** full history only for survivors.
Bar for all: **≥ 8.0%/yr on capital in both halves** (2024-11..2025-10, 2025-11..2026-10). Kill thresholds are kill-only.

| # | mechanism (who pays) | Stage 0.5 ceiling (kill if < 8%) | Stage 1 (90 d) kill | Stage 2 rule |
|---|---|---|---|---|
| 220 | Jupiter JLP (traders' losses + fees), hedged: short JLP's non-stable share on HL | best JLP APY + 0.65 × 90-d HL short funding (SOL/ETH/BTC avg), ÷ (1 + 0.65/3). JLP not in the snapshot → no ceiling possible; goes straight to a pilot fetch | < 4%/yr | hold all window, hedged as in the ceiling |
| 221 | GMX v2 GM pools (traders' losses + fees), hedged: short the index share (assumed 50%) on HL | best GM pool (TVL ≥ $20M, index token on HL) APY + 0.5 × index 90-d funding, ÷ (1 + 0.5/3) | < 4%/yr | monthly top 5 by trailing 30-d hedged yield, #204-style costs and stress |
| 222 | dYdX MegaVault (protocol market making; USDC) | not in snapshot → pilot fetch (dYdX indexer vault PnL) | < 4%/yr | hold all window |
| 223 | Lighter LLP (protocol liquidity pool; USDC) | not in snapshot → pilot fetch if an API answers, else "no data" | < 4%/yr | hold all window |
| 224 | Stable-pair DEX LP fees + rewards (USDC/USDT-type pools: stablecoin, multi exposure, IL risk "no") | best pool (TVL ≥ $5M) apyBase + 0.9 × apyReward; and top-5 average | < 4%/yr | monthly top 5, #204 rules |
| 225 | Trader-counterparty USDC vaults (Gains gUSDC/gDAI, Avantis, Ostium) | best of those in the snapshot; others pilot-fetched if listed by DefiLlama | < 4%/yr | hold the best-ceiling vault all window; plus equal-weight of all |
| 227 | Savings rates not in #210 (Curve scrvUSD, sfrxUSD, sUSDai etc.: stablecoin single pools of savings projects) | best in the snapshot | < 4%/yr | monthly top 5, #204 rules |

Ceilings use the most favourable current values (hindsight); a high ceiling never counts as a pass.
Command (Stage 0.5): `uv run python scripts/batch4_ceiling_20261121.py | tee docs/jx_runs/batch4_ceiling_20261121.txt`

## Results (2026-11-21, `docs/jx_runs/batch4_20261121.txt`, re-run identical)
- #221 GMX GM hedged: Stage 1 8.2%; halves **21.8% / 10.1%** → passes the rule as registered (universe only 2 pools: ETH-USDC, BTC-USDC on Arbitrum).
- #224 stable-pair LPs: Stage 1 −12.0% (7 stress hits) → FAIL.
- #227 other savings rates: 3.7% / −16.8% (5 stress hits) → FAIL.
- #225 trader-counterparty vaults: primary rule (best-ceiling vault, Gains USDC) 9.7% / 4.4% → **FAIL**; secondary (equal weight of 4 Gains vaults)
  10.7% / 13.2%. The primary rule decides: FAIL (near-miss; the largest vault has ~$2.5M TVL, so capacity is tiny anyway).
- #222 dYdX MegaVault: only 67 days of history (< 180) → FAIL (Stage 1 8.2%).
- #220 Jupiter JLP: DefiLlama lists only JLP *lending* markets (not JLP holding); Jupiter's API gives the current APR only → not testable (no history).
- #223 Lighter LLP: API answers with current pool metadata only → not testable (no history).

## Addendum (before fetching): #221 must survive real GM token prices
DefiLlama's GM APY is fee APY; a GM pool also wins/loses against traders and its index exposure is not exactly 50%. Robustness check (decides whether
#221 counts as passed): daily return = Δlog(GM token price) − h × Δlog(index price) + h × (HL short funding)/365, on capital (1 + h/3), with
h = 0.5 as registered, using DefiLlama coin prices for the GM tokens (ETH-USDC 0x70d95587d40A2caf56bd97485aB3Eec10Bee6336, BTC-USDC
0x47c031236e19d024b42f8AE6780E44A573170703 on Arbitrum). Same bar (≥ 8% both halves, equal weight of the two pools, held). If GM prices are not
available, #221 is reported as "passes fee-APY rule, not verified".

## #221 robustness result (2026-11-21, `docs/jx_runs/gm_robust_20261121.txt`, re-run identical): FAIL
With real GM token prices (DefiLlama, ETH-USDC and BTC-USDC GM on Arbitrum) and the registered 50% hedge: Stage 1 −32.9%/yr; halves 3.6% / 3.2%;
worst drawdown −11.0%. The fee APY overstated the pool's return (trader PnL against the pool and imperfect hedge). #221 = FAIL.

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

# Stability pools: Liquity v2 (BOLD) and Felix (feUSD) depositors (#230) — 2026-11-22

Written and committed before any data. Mechanism M7 (docs/IDEAS_SWEEP_20261121.md): borrowers' interest is paid by protocol rule to stability-pool
depositors, who also absorb liquidated debt in exchange for collateral at a discount. DefiLlama reports 0% for these pools (data gap, #210), so
data must come from the protocols' own public API or on-chain state. Malaysia: permissionless contracts (unverified).

## Stages
- **Stage 0 (probe, no values read):** which sources answer from GitHub's runners (Liquity v2 public API/JSON, Felix API, public RPC views).
- **Stage 0.5:** ceiling = current SP APR reported by the source (interest share) — KILL if < 8%.
- **Stage 1:** last 90 days of SP yield (interest + liquidation gains valued at the collateral price at the time, sold with 1% slippage) — KILL < 4%.
- **Stage 2:** from the pool's launch (or 2024-11) to 2026-10, halves by own history: PASS ≥ 8%/yr both halves and ≥ 180 days; loss days
  (collateral gain worth less than the debt absorbed) counted as losses.
Bar ≥ 8%/yr. Command: `uv run python scripts/stabilitypool_20261122.py | tee docs/jx_runs/stabilitypool_20261122.txt`

# Refinement studies: can a different configuration flip a failed idea? (R1–R7) — 2026-11-22

Written and committed before any variant is run. Protocol from `docs/REFINEMENT_TRIAGE_20261122.md`: ≤ 5 variants per idea, all listed here;
**choose the variant with the best year-1 result** (2024-11-01..2025-10-31); run that one variant **once on year 2** (2025-11-01..2026-10-31).
**PASS** only if the chosen variant has ≥ 8%/yr on capital in year 1 **and** year 2, **and** ≥ 8% in year 2 with all trading costs × 1.5.
Year 2 of non-chosen variants is printed for transparency only (never used to choose). Same data, costs and stress rules as the original tests unless
a variant says otherwise. Results get CANDIDATES rows "#<orig>-R".

| study | original | variants (V1 = original configuration) |
|---|---|---|
| R1 | #208 funding gaps HL/dYdX/Aevo | V1 entry 15%, exit on sign flip, taker 0.05%/leg-side · V2 entry 25%, exit when |signal| < 5% · V3 entry 10%, exit sign flip, BTC/ETH/SOL only · V4 as V1 with maker fees 0.015% (assumes maker fills) · V5 as V2 with maker fees |
| R2 | #221 GMX GM pools hedged (real GM prices) | hedge ratio h = 0.3 · 0.5 (V1) · 0.7 · 0.9 · dynamic h = trailing-30-day regression beta of GM on index log returns (past data only, clipped 0–1.2) |
| R3 | #204 stable-yield rotation (and #201–203, #224, #227, #278 family) | V1 #204 (TVL ≥ $5M, age ≥ 90 d, top 5 by 30-d yield, monthly) · V2 TVL ≥ $50M, age ≥ 365 d, top 5 · V3 as V2, top 10, exclude pools whose reward share of yield > 50% · V4 TVL ≥ $100M, age ≥ 365 d, top 5, quarterly rebalance · V5 TVL ≥ $20M, age ≥ 180 d, top 10 ranked by 90-d mean |
| R4 | #207 new reward programmes | V1 #207 · V2 start TVL ≥ $20M · V3 V2 + pool age ≥ 180 d · V4 V3 + reward APR at start ≥ 5% · V5 V4 on a $50,000 portfolio (gas share 1/5) |
| R5 | #276 hedged native HYPE staking (staking 2.5% assumed) | V1 3× always · V2 2× always · V3 3×, in position only when trailing-30-d funding > 8%/yr else Aave-USDC-like 4% · V4 V3 at 2× · V5 3×, exit only when trailing funding < 0 |
| R6 | #225 Gains trader-counterparty vaults | V1 largest-TVL vault · V2 equal weight · V3 TVL-weighted · V4 top 2 by trailing-90-d yield, monthly · V5 equal weight excluding vaults < $1M TVL |
| R7 | #216 gold carry, #217 / #57 carry family (spot + HL short) | universe BTC, ETH, SOL, HYPE, BNB, XRP, DOGE, LINK, SUI, AVAX, PAXG; monthly rank by trailing-30-d funding received by shorts; hold top k if its trailing funding > T, else park at 4%/yr; costs 0.10% spot + 0.045% perp per side; capital ÷ 1.333 — V1 k=3,T=0 · V2 k=3,T=10% · V3 k=5,T=10% · V4 k=1,T=15% · V5 k=3,T=15% |
Pending (needs a fetch): R8 #211 Pendle, blue-chip underlyings only (sUSDe, sUSDS, USDe, USDC-based) — registered later.
Command: `uv run python scripts/refine_20261122.py | tee docs/jx_runs/refine_20261122.txt`

# Were the non-prop ideas only tested at base level? Triage and refinement protocol — 2026-11-22

Jx's point: the base-level test of prop recycling might also have looked weak, and only further work (the friend's strategy, a wide firm search)
showed Topstep's value; killing ideas on one simple implementation can throw away real opportunities.

## What the base level did and did not see
- **Prop firms:** the base-level test is the coin flip (random trade directions). Topstep still scored $18,046 / 98% profitable and ranked top of
  13 products (rank correlation 0.86 with real results, `scripts/radar_backcheck_20261121.py`). The strategy layer then lifted it to $44,359
  (~2.5×). So the base level *found* Topstep, but understates it ~2.5×.
- **Non-prop:** every mechanism got one pre-registered implementation; Stage 1 kills used that one version. Two blind spots:
  1. implementation choices (selection rule, thresholds, hedge ratio, fee tier, rebalancing) may have killed a viable mechanism;
  2. skill/engineering edges (market-making rewards, liquidations, solvers) were screened out at Stage 0 as "bot races" — the non-prop analogue of
     the strategy layer was never built.

## Triage of every non-prop kill
| type | ideas | why | refinement worth it? |
|---|---|---|---|
| **Structural fail** (market-wide fact; no implementation changes it) | #210 stable programmes (yields 3–5% market-wide in 2025–26), #214 CRV wrappers (−40–60% vs CRV), #267 Votium (CVX −52%/yr), #269 RWA (3.9%), #271 CME basis (2.6%), #230 Liquity SP (~$3.6K pool), #277 reverse carry (borrow cost), #212/#213 hedged staking (buy-and-hold also < 8% in year 2), #216 gold carry (funding level) | the number that kills it is a market level, not a rule choice | no |
| **Implementation-sensitive** | #201–#204, #207, #224, #227, #278 (stable-yield selection picks blow-ups → quality filters: protocol age, TVL, stable type), #208 funding gaps (thresholds, exits, maker fees, coin set), #211 Pendle (only blue-chip underlyings), #221 GM pools (dynamic hedge from pool composition), #225 Gains vaults (portfolio rule), #276 HYPE hedged staking (leverage / margin management) | the failure came from a choice I made | **yes — 6 priority studies** |
| **Data-limited** (not a fail) | #209 paid-to-borrow (borrow history paywalled), #219 loops (e-mode LTV missing), #220, #223, #229 INJ, #259 Paradex, #260/#261 Lighter (31 days only), #262 real-yield staking, #265/#266, #222, #228 SKY (re-test 2027-01-08), #274 | missing data, not evidence of failure | when data exists |
| **Skill / engineering edges never built** | Polymarket-style maker rewards (Malaysia grey), perp-DEX maker rebates and liquidity programmes, liquidation bots (workstream B, #100), solvers/relayers | the edge is in execution quality, which a base-level test cannot measure | separate design work, like the friend's strategy for prop |

## Refinement protocol (so a rescue is honest, not data-mined)
1. **Design on year 1 only** (2024-11..2025-10): at most **5 variants per idea**, all written down before touching year 2.
2. **Pick the best variant on year 1**, then run it **once on year 2** (2025-11..2026-10), which no variant was tuned on.
3. **Pass:** year 2 ≥ 8%/yr on capital **and** year 1 ≥ 8% for the chosen variant; because 5 variants are tried, year 2 must also clear 8% with costs
   raised 50% (margin for selection luck).
4. Each study gets its own PREREG committed before running; results go to CANDIDATES as "#2xx-R".
Priority order (most likely to flip): #208 funding gaps (maker fees + adaptive thresholds), #221 GM pools (composition-based hedge),
stable-yield selection with quality filters (#201–#204 family), #211 Pendle blue-chip only, #276 HYPE with 2× and margin rules, #225 Gains portfolio.

# Hedged yield mechanisms: #212 hedged staking, #213 hedged reward farming, #219 correlated-pair loops — 2026-11-21

Written and committed before the data below is fetched. These turn the radar's biggest near-miss group ("F4 price exposure, needs hedge",
~360 rows) into delta-neutral positions: hold the yielding asset, short the same asset's perp on Hyperliquid (HL). The hedge also *earns*
funding when funding is positive (shorts are paid). Malaysia: permissionless contracts + HL: unverified.

## Data (`scripts/fetch_fallback.py hedged lendborrow_corr`, Actions)
DefiLlama daily charts for every single-exposure, non-stablecoin pool with TVL ≥ $20M today whose token maps to an HL perp (ETH family:
stETH, wstETH, rETH, cbETH, weETH, ezETH, rsETH, mETH, sfrxETH, osETH, wBETH, ETHx, WETH, ETH; SOL family: SOL, jitoSOL, mSOL, jupSOL,
bSOL, INF, bnSOL, hSOL; HYPE family: HYPE, kHYPE, stHYPE, wHYPE; BTC family: BTC, WBTC, cbBTC, tBTC, LBTC; AVAX/sAVAX; BNB/slisBNB/BNBx);
HL hourly funding for ETH, SOL, HYPE, BTC, AVAX, BNB; DefiLlama lendBorrow for the same tokens (#219).
Staking projects for #212 = DefiLlama category "Liquid Staking" / "Liquid Restaking" pools; #213 = every mapped pool.

## Common rule
- Hedged daily yield (annualised %) = apyBase + 0.9 × apyReward + F, where F = HL funding received by the short (sum of hourly rates over
  the day × 365 × 100; negative when shorts pay).
- Capital: spot X plus perp margin X/3 (3× short) → return on capital = hedged yield / 1.333.
- Monthly: eligible = TVL ≥ $20M that day, ≥ 90 days of history; rank by trailing 30-day mean hedged yield; hold **top 5** equally for the month.
- Costs per pool entered or exited: 0.05% spot swap + 0.045% perp taker + $10 gas on a $2,000 slot.
- Loss stress: pool TVL −50% within 7 days → −20% of that position (stands in for depegs/exploits the data cannot show).
- Halves 2024-11..2025-10, 2025-11..2026-10. Stage 1 (2026-08..10): KILL < 4.0%/yr. Stage 2: PASS ≥ 8.0%/yr both halves.

## #212 hedged staking — universe: liquid-staking / restaking pools only.
## #213 hedged reward farming — universe: all mapped pools (lending supply with rewards, staking, vaults).
## #219 correlated-pair loops (e-mode style)
Same project and chain: supply a yield-bearing token (LST or yield-bearing stable: sUSDe, sUSDS, sDAI, sfrxUSD) and borrow its base asset
(ETH/WETH for ETH LSTs; SOL; AVAX; HYPE; USDC/USDT for yield-bearing stables). s = supply apyBase + 0.9 × apyReward; b = base-asset
apyBaseBorrow − 0.9 × apyRewardBorrow; k = 1/(1 − 0.8 × LTV of the supplied token), capped at 6; ROE = s + (k − 1)(s − b). No hedge needed
(both legs move together). Monthly top 5, costs $20 per pool in/out on $2,000; loss stress −10% × k of equity on a TVL collapse of either pool.
Same stages and bar.

Commands: `uv run python scripts/hedged_20261121.py | tee docs/jx_runs/hedged_20261121.txt`

## #214 hedged governance-token yields (added 2026-11-21, before any of this batch's data was fetched)
Protocols pay emissions/bribes/fees to holders who stake or vote-lock their governance token. Universe: single-exposure pools whose token
maps to an HL-listed governance perp: CRV (CRV, cvxCRV, sdCRV, yCRV, st-yCRV, asdCRV), AAVE (stkAAVE), ENA (sENA), PENDLE (vePENDLE, sPENDLE,
mPENDLE, Penpie/Equilibria/Stake DAO wrappers), LDO, MORPHO, AERO (veAERO), FXS (cvxFXS, sdFXS); **TVL ≥ $2M** (these pools are smaller).
Same hedged rule, costs, stress, stages and bar as #212/#213, except the TVL eligibility threshold is $2M. Wrapper discounts to the
underlying (e.g. cvxCRV below CRV) are not in the data: stated as a limit; the stress partly covers collapses. #213 keeps its original
families (ETH, SOL, HYPE, BTC, AVAX, BNB) only.

## Results so far (2026-11-21, `docs/jx_runs/hedged_20261121.txt`, re-run identical)
- #212 hedged staking: Stage 1 −2.2%/yr → **FAIL**. #213 hedged farming: Stage 1 −3.6%/yr → **FAIL**. Cause: the monthly top-5 rule churns between
  near-identical staking tokens (9.1% vs 9.4%), and each change costs ~0.6% of a slot. Post-hoc diagnostic (not a verdict,
  `docs/jx_runs/hedged_posthoc_hold_20261121.txt`): even buy-and-hold of the biggest LSTs gives 10.3–12.6% then 4.8–6.6% by half → would fail too.
- #214 hedged governance-token yields: Stage 1 15.5%; halves **8.32% / 15.52%** → passes the rule as registered. Holdings: yCRV, sdCRV, cvxCRV,
  sdPENDLE, AAVE lending. **Not yet a pass of the five-part filter**: F4 (capped downside) is unverified because the hedge is on CRV/PENDLE while
  the position holds wrappers that can trade at a widening discount; F5 capacity is small (pools of a few $M).
- #219: borrow-side history (`chartLendBorrow`) now returns HTTP 402 (paid). Not purchased, not circumvented → no full test.

## Addendum (before fetching): #214 wrapper-discount check, and #209/#219 Stage 0.5 from today's borrow rates
- **#214 robustness (decides whether #214 counts as passed):** add to each wrapper position's daily return the daily change in
  log(wrapper price / underlying price) from DefiLlama coin prices (yCRV/st-yCRV, cvxCRV, sdCRV vs CRV; sdPENDLE vs PENDLE). Same rule and bar
  (≥ 8% both halves). If a wrapper has no price history, its position earns the pool yield minus the largest discount move seen in the other
  wrappers that month (conservative).
- **#209 and #219 Stage 0.5:** ceiling ROE from today's `lendBorrow` snapshot (supply yield, borrow rate after rewards, LTV) with the same
  formulas; KILL if the best pair/pool < 8%. If one survives, the verdict is "survives ceiling; full test not possible (borrow history paywalled)".

## Addendum (2026-11-21): #209 and #219 Stage 0.5 results; #219 mechanical fix
- #209 (`docs/jx_runs/borrow_ceiling_20261121.txt`): ceiling (top-5 mean ROE from today's rates) **11.4%** → survives Stage 0.5 (Dolomite USDC/USD1
  same-asset loops ~16–19% today). Borrow history is paywalled (HTTP 402) → **not testable beyond Stage 0.5**.
- #219 first ceiling printed 0%: the rule's supply yield s used only the lending market's supply APY (≈ 0 for LST collateral) and left out the
  token's own staking/savings yield. Mechanical fix (no threshold changed): s = intrinsic yield of the supplied token (its own DefiLlama
  liquid-staking / savings pool, highest-TVL match by symbol) + market supply APY. Re-run as `scripts/borrow_ceiling_20261121.py`.

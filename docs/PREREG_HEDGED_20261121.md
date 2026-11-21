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

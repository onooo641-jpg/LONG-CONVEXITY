# Batch 2 of the 64 — pre-registration, 2026-11-20 (CANDIDATES #45–47)

Committed before the data for these tests was fetched. Research backtests
only; the legal question for a Malaysian resident still applies.

## M1 — cross-chain lending-rate arbitrage (#45; the 45-list's #3 and #10)

- **Pools:** USDC and USDT supply pools on Aave v3, Compound v3, Spark, Morpho
  and Fluid, on Ethereum, Arbitrum, Base, Optimism, Polygon and Avalanche, from
  DefiLlama's current list, TVL ≥ $10M (survivorship noted). Daily `apyBase`
  from `/chart/{pool}`.
- **Strategy:** every 7 days, move $10,000 to the pool with the highest
  trailing-7-day mean `apyBase` (no look-ahead). Each move costs $20 if
  Ethereum is involved and $5 otherwise, plus a 0.05% bridge fee.
- **Baseline:** hold that symbol's largest Aave v3 Ethereum pool throughout.
- **Pass:** net excess > 1% a year in both halves, for both USDC and USDT.

## M2 — stablecoin depeg buying (#46; the 45-list's #5, as a market trade)

- **Coins**, failures included on purpose: tether, usd-coin, dai, terrausd,
  frax, true-usd, usdd, liquity-usd, paxos-standard, first-digital-usd.
  Daily prices (DefiLlama coins), 2022-01-01 onward.
- **Event:** price ≤ 0.99. Buy; sell when ≥ 0.999 or after 60 days, whichever
  comes first, at that day's price. Cost 0.2%.
- **Pass:** ≥ $300 a year per $10K in both halves, **and** no single event
  losing more than 5%.

## M3 — cross-chain stablecoin dislocations (#47; the 45-list's #9)

- Daily USDC prices on Ethereum, Arbitrum, Base, Optimism, Polygon and
  Avalanche by token address (DefiLlama coins).
- **If** the chains never differ by more than 0.05% on any day, the verdict is
  "no measurable gap at daily resolution". **Otherwise**, count days with a gap
  above 0.3% (more than round-trip costs); pass if ≥ 12 such days a year.
  Caveat: aggregator prices may simply copy one reference price, in which case
  this data can't show a real gap.

Command: `uv run python scripts/batch2_20261120.py`

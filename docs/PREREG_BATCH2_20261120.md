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

## Results (2026-11-20, `docs/jx_runs/batch2_20261120.txt`, data run 44585291434)

| Test | Verdict | Key numbers |
|---|---|---|
| M1 cross-chain lending, weekly rotation | **fail** | USDC −3.46% / −3.88% a year vs holding Aave v3 Ethereum; USDT −0.91% / −1.59% |
| M2 stablecoin depeg buying | **fail** | 66 events. Most recovered for +1–4% within days, but TerraUSD lost 93.9% on the first buy. −$3,148 / −$3,301 a year per $10K, and the worst event breaks the 5% limit |
| M3 cross-chain USDC gaps | **no data** | The coins API rejected the chain-address requests (HTTP 400) |

M2 is the lesson: without the coins that collapsed, depeg buying looks like
free money. One collapse wipes out years of small wins.

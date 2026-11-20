# Handoff: non-prop strategy search (written 2026-11-20)

For a new session continuing the search for non-prop-firm edges. Read `CLAUDE.md` first.

## The bar
Topstep recycling makes about $4,100/yr per account slot with at most ~$3.5K at risk,
which is over 100% a year on capital at risk, and it pays even random trading (98% of coin
flips profit). A non-prop idea is only interesting if it is repeatable and gets near that
return on a few thousand dollars, or scales cleanly with capital.

## Already tested (all failed; details in each PREREG and CANDIDATES row)
| # | idea | why it failed |
|---|---|---|
| 29–33 | overnight drift, turn of month, pre-FOMC, gap fade, day of week (NQ/ES, own account) | no edge out of sample |
| 37, 44 | new-perp funding spikes; post-listing shorts (Hyperliquid) | not above baseline / negative 2nd half |
| 38 | Aave utilisation-threshold arbitrage | −$19.8/event |
| 39 | DEX liquidity-incentive mispricing | sample too small |
| 40 | Polymarket multi-outcome arbitrage | no data: Polymarket blocks US servers (not circumvented) |
| 41 | stETH redemption discounts | ~$40–50/yr per $10K |
| 42 | vault allocation inefficiencies | −0.46%/yr |
| 43 | settlement-resolution inefficiencies | not data-testable |
| 45–47 | cross-chain lending arb; stablecoin depeg buying; cross-chain stablecoin gaps | negative / UST wipeout / no data |
| 49–51 | Bursa IPO ballots; i-Saraan/ASM; MYR crypto price gaps | negative or tiny |
| 57 | funding-rate carry, rotating and BTC+ETH held (2024–26) | 2.9% / 6.4% a year, falling |
| 58 | the friend's NQ trades on own money | −$2,553 over 2016–26; max DD −$73K |
| 59 | offshore broker credit bonuses | credit doesn't absorb losses, or one-time capped |

Screened out by reasoning: maker rebates (need volume), trading competitions (not repeatable),
copy-trading provider fees (need followers), airdrops (no history), betting (illegal in
Malaysia), card/bank bonuses (US-only).

## Lesson so far
Every edge with Topstep-like ROI found so far is a **subsidy built into someone's rules**
(a prop firm pays for failed evaluations with fees from others). Market-pricing edges tested
here were either absent or tiny. The most promising direction is other rule-based subsidies
that repeat, not price patterns.

## Constraints a new session will hit
- The sandbox network allows mainly package registries and GitHub. Use the GitHub Actions
  fetch route (see CLAUDE.md). Actions run on US servers: US-geoblocked sources stay unavailable.
- Bursa and i3investor return 403 to GitHub; Yahoo rate-limits.
- WebFetch on a URL not seen in search results needs Jx's approval.
- Work on the same branch as the main session (the fetch workflow only runs there); `git pull --rebase` before each push.

## Next ideas to test, in priority order (added 2026-11-20 by the prop-firm session)
All are "rule-based subsidies": a protocol, exchange or contest pays by rule, not by mispricing.
ROI figures below are rough estimates, not measured.
1. **Lending-protocol liquidation bonuses.** Aave/Compound forks pay a fixed 5–10% bonus to whoever
   liquidates an unhealthy loan. Test: historical liquidation events per protocol/chain (on-chain or
   indexer data), bonus paid, gas cost, and how concentrated the winners are. Look for smaller chains and
   forks where the top bots do not take everything. Fits Jx's sniper-bot experience.
2. **Points/airdrop farming, delta-neutral.** New perp DEXs and lending markets pay tokens for volume or
   deposits. Test: value paid per $ of volume/deposit in past airdrops vs the cost of farming it hedged
   (fees, funding, capital time). Not backtestable forward; the question is whether the historical
   payout per $ cost is consistently positive.
3. **Cross-venue funding gaps on new listings.** Different from #37/#57: long the perp on the venue with
   low funding, short on the high one. Needs a second venue's funding history that GitHub (US servers)
   can reach.
4. **Polymarket liquidity rewards.** Polymarket pays makers daily rewards for quoting near the midpoint.
   Data is blocked from US servers (#40); check first whether Polymarket is legally available in Malaysia
   before any local run.
5. **SPAC trust-value arbitrage.** Buy SPAC units/shares at or below trust value; the redemption right
   floors the price, warrants are a free option. Low risk, roughly T-bill plus a few %, so capital-heavy.
   Mainly a benchmark for "safe" capital.
6. **Free-entry trading competitions.** Zero cost, positive expected value, small prizes and not repeatable;
   only worth it if entry is free and automatable.

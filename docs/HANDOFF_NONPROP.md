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

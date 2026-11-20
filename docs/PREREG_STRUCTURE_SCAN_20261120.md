# Structure scan: how generous is each bot-allowed prop-firm product? — 2026-11-20 (CANDIDATES #48)

**Question.** Recycling works partly because a firm's rules pay even random
trading. Which products pay random trading most? This finds structural edges
directly, instead of searching for strategy edges.

**Metric.** The **coin-flip net**: the NQ trade sizes of 2016-01..2026-10, with
the direction of every trade randomised (200 runs, seed 1), fees kept, run
through each product's rules, `LOCK_FIRST`. Reported: median net, share of runs
that profit, and the real strategy's net for reference. Risk per trade is 0.45 ×
the product's loss limit, as in the account-size test.

**Products** (automation allowed; end-of-day drawdown, which the model handles):

| product | rules source |
|---|---|
| Topstep 50K / 100K / 150K, Standard and Consistency | Topstep help center (verified); 100K/150K scaling ladder assumed |
| Topstep 50K No-Activation path ($95/month, reset $95, no activation) | Topstep pricing page; reset price third-party |
| LucidFlex 25K / 50K / 100K / 150K | payout rules from Lucid's help center; prices, caps and lock third-party |
| Tradeify Select Flex 50K | payout caps (post-2026-09-01: $2,500 on 50K), winning days and lock as read from Tradeify's help center by third parties; evaluation $159/month, reset $95, no activation (third-party) |

**Excluded:** MyFundedFutures (semi-automated only), Apex, Take Profit Trader,
Alpha Futures (bots banned), FundedNext (80/20, small caps).

**No pass/fail.** This is a ranking. A product that tops it is a candidate for
reading the official rules in full before any purchase.

Command: `uv run python scripts/structure_scan_20261120.py`

## Results (2026-11-20, `docs/jx_runs/structure_scan_20261120.txt`)

| rank | product | coin-flip median net, 2016–26 | coin flips that profit | real strategy net |
|---|---|---|---|---|
| 1 | Topstep 150K Consistency | $34,116 | 94% | $101,828 |
| 2 | Topstep 150K Standard | $30,319 | 94% | $95,324 |
| 3 | Topstep 100K Consistency | $18,967 | 90% | $66,104 |
| 4 | LucidFlex 50K | $18,519 | 97% | $37,523 |
| 5 | Topstep 50K Standard | $18,046 | **98%** | $44,359 |
| 6 | Topstep 50K Consistency | $18,005 | 98% | $46,492 |
| 7 | Topstep 50K No-Activation | $17,410 | 94% | $45,115 |
| 8 | Topstep 100K Standard | $17,148 | 92% | $62,660 |
| 9 | Tradeify Select Flex 50K | $11,110 | 84% | $32,900 |
| 10 | LucidFlex 150K | $5,929 | 62% | $48,184 |
| 11 | LucidFlex 25K | $3,067 | 72% | $14,973 |
| 12 | LucidFlex 100K | $1,126 | 55% | $34,682 |

What it says:
- **Topstep is the most generous structure in the scan.** Its monthly fee
  includes a free reset, its activation is small, and its payout caps grow with
  account size. At 150K a coin flip nets ~$34K per account slot; at 50K
  random play profits in 98% of runs, the most reliable.
- **Lucid is generous at 50K only.** Its payout caps ($2,500/$3,000) barely
  grow with size while losses do, so 100K and 150K are poor structures.
- **Tradeify Select Flex 50K is weaker:** a monthly fee without free resets,
  and a 5-payout limit.
- The ranking rests on verified rules for Topstep, and partly third-party rules
  for Lucid and Tradeify. The Topstep 100K/150K scaling ladder is assumed.

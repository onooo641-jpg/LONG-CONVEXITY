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

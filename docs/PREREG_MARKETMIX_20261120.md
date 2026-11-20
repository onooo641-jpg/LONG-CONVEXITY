# Market mix across accounts: NQ + ES + YM instead of all NQ — 2026-11-20 (CANDIDATES #62)

Written and committed **before** any run. The strategy is unchanged (the "U" unscaled settings, as in
ES_PREREG and PREREG_YM_RTY); only which market each account trades changes.

## Why
PREREG_PORTFOLIO2 showed accounts on identical trades move in lockstep, so their dips stack. Accounts on
different markets get different trades. Earlier single-account results (2016–26, $900 risk, Topstep 50K):
NQ $44,359 (beats 98% of coin flips), ES $20,338 (86%), YM $11,744 (96%). RTY excluded (12%).

## Trades
- NQ: `ideas_orders_NQ.parquet`, MNQ config (as all plan figures).
- ES: `ideas_orders_ES.parquet`, MES config from `scripts/es_test.py`.
- YM: `ideas_orders_YM.parquet`, MYM config from `scripts/ym_rty_test.py` ($0.50/pt, 1-point tick
  slippage), unscaled settings.
If an orders file does not reproduce its earlier single-account figure within 1%, stop and report.

## Portfolios (all start 2016-01-01, platform costs as PREREG_PORTFOLIO2)
- T5-NQ: 5 Topstep accounts, all NQ (reference)
- T5-mix: 5 Topstep accounts: 3 NQ, 1 ES, 1 YM
- C-NQ: 5 Topstep + 5 Lucid + 3 MFFU, all NQ
- C-mix: Topstep 3 NQ/1 ES/1 YM; Lucid 3 NQ/1 ES/1 YM; MFFU 2 NQ/1 ES

## Reading (decided now)
The mix is **worth doing** if its net ÷ cash-on-hand is at least 15% higher than the all-NQ version
AND its net is at least 75% of the all-NQ net. Also reported: monthly P&L correlation NQ–ES–YM.

Command: `uv run python scripts/marketmix_20261120.py`

## Addendum, pre-registered after part 1 ran (2026-11-20 22:05), before part 2 runs
Part 1 found the markets' trades sometimes overlap in time in **opposite** directions (NQ–ES 56,
NQ–YM 98, ES–YM 62 times in 2016–26). Topstep, Lucid and MFFU prohibit hedging across accounts,
including opposite positions in correlated contracts, so part 1's mix is not compliant as tested.
**Part 2 adds a mechanical compliance filter** (not a strategy change): process all trades of all three
markets in entry-time order; skip any trade whose direction is opposite to a position still open in
another market (anywhere in the portfolio, conservatively across firms too). The skipped trade is removed
for every account on that market. Then re-run the four portfolios with the same reading rule.
Part 1 figures stand only as "before compliance" and are not used for planning.

# Paid to borrow: same-asset stablecoin loops on subsidised lending markets (#209) — 2026-11-21

Written and committed before the borrow-side data is fetched. Rule-based subsidy: many lending markets pay token rewards to **borrowers**;
when (supply yield) − (borrow cost after rewards) is positive, supplying a stablecoin and borrowing the same stablecoin against it
("looping") multiplies the subsidy. Same asset on both sides → no price exposure; the position can be unwound at any time (capped downside
apart from protocol hacks / depegs). Different from #204 (no borrowing) and #42/#45 (rate arbitrage across venues).

## Data
DefiLlama `yields.llama.fi/lendBorrow` (current: LTV, borrowable) + `yields.llama.fi/chartLendBorrow/<pool>` (daily apyBaseBorrow,
apyRewardBorrow, totalSupplyUsd, totalBorrowUsd) + `yields.llama.fi/chart/<pool>` (supply apyBase, apyReward), for every borrowable pool
whose symbol is a USD stablecoin with supply TVL ≥ $5M today. Window 2024-11-01 .. 2026-10-31, halves of 12 months.

## Rule
- Supply yield s = apyBase + 0.9 × apyReward; borrow cost b = apyBaseBorrow − 0.9 × apyRewardBorrow (negative = paid to borrow).
- Leverage k = 1 / (1 − 0.8 × LTV), capped at 5 (LTV from today's listing; 20% safety margin). Return on equity = s + (k − 1)(s − b).
- Monthly: rank eligible pools (supply TVL ≥ $5M that day, ≥ 90 days of history, both supply and borrow data present) by trailing 30-day
  mean ROE; hold the **top 5 equally** for the month. Cost: $20 per pool entered and per pool exited (several transactions), on $10,000.
- Loss stress as #204: a held pool whose supply TVL falls > 50% within 7 days → −20% of that position's equity, dropped until month end.
- Baseline reported: Aave v3 USDC Ethereum supply.

## Pass
- Stage 1 (2026-08..10): KILL if ROE < 4.0%/yr.
- Stage 2: PASS if ROE ≥ 8.0%/yr in both halves after costs and stress. Reported: $/yr on $10K/$40K, months negative, how often b < 0.
Bias: survivorship (pools gone before today are missing) → upper bound; leverage uses today's LTV.

Commands: data `scripts/fetch_fallback.py lendborrow` (Actions); test `uv run python scripts/borrowloop_20261121.py | tee docs/jx_runs/borrowloop_20261121.txt`

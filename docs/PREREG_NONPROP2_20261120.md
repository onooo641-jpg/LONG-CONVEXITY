# Non-prop round 2 — 2026-11-20 (CANDIDATES #57–59)

Written and committed **before** any run. Target to compare against: Topstep 50K
recycling, **$4,098/yr** real net (2016–26), worst dip −$3,520 (R1/R3).

## #57 Funding-rate carry, rotating (Hyperliquid funding history)
- Position: short perp + long equal spot (delta-neutral), earns the perp funding rate.
- Data: `data/public/hl_funding.parquet`, hourly, 2024-01-01..2026-11-19, the 20
  baseline majors (`hl_baseline_coins.parquet`, chosen in #37 before any carry look).
- Rule: every Monday 00:00 UTC rank coins by mean funding over the prior 7 days; hold
  the top 3 with positive trailing funding, equal weight; earn the realised funding of
  the next 7 days. Fewer than 3 positive → the rest sits in cash at 0%.
- Costs: 0.25% of notional per coin entered or exited (perp taker 0.045% ×2 + spot
  ~0.07% ×2 + slippage). Capital = 2 × notional (spot leg + perp margin at 1x).
- Control: hold BTC+ETH carry all the time, no rotation, entry/exit cost once.
- **Pass**: net return on capital > 8%/yr, positive in both halves (split at the median date).
- Not modelled: spot–perp price gaps at entry/exit, exchange risk, whether a spot hedge
  exists on the same venue (many Hyperliquid perps have no Hyperliquid spot market).
- Reported: capital needed to match $4,098/yr.

## #58 The friend's NQ strategy on own money (no prop firm)
- Same trades as every prop test ($900 risk, 2016–26, commission kept), on an own
  brokerage account, no firm rules.
- Reported: net/yr, max drawdown, worst year, and the capital needed so that the max
  drawdown is 25% of capital, and the return on that capital.
- **Pass**: return on that capital > 15%/yr and both halves (2016–20, 2021–26) positive.

## #59 Broker credit bonuses as a loss buffer (screen by terms, no backtest)
- Question: do offshore CFD broker bonuses (XM, HFM, FBS, RoboForex) give a
  Topstep-like free option, i.e. does the credit absorb losses after your own money is gone?
- **Pass** needs all three from published terms: the credit absorbs losses beyond the
  deposit; it can be earned again (not a one-time cap); and the broker is accessible
  without breaking its terms.

## Screened out by reasoning (no test)
Maker rebates (need large volume), trading competitions (not repeatable, not testable),
copy-trading provider fees (depend on attracting followers), airdrops (no testable
history), sports/betting promos (illegal in Malaysia), Polymarket (no data from US servers),
card/bank bonuses (US-only).

Command: `uv run python scripts/nonprop2_20261120.py`

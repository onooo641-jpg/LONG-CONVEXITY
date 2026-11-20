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

## Results (2026-11-20, `docs/jx_runs/nonprop2_20261120.txt`)
| # | test | result | verdict |
|---|---|---|---|
| 57 | rotating top-3 funding carry | 2.9%/yr on capital; halves +11.6% / −3.2%; 2024 +12.9%, 2025 −1.8%, 2026 −2.7% | **FAIL** (below 8%, 2nd half negative) |
| 57 | control: BTC+ETH carry held | 6.4%/yr; halves +12.8% / +5.4%; 2024 +11.1%, 2025 +4.7%, 2026 +2.3% | **FAIL** (below 8%; decaying) |
| 58 | friend's strategy on own money, $900 risk | net −$2,553 over 2016–26 (−$236/yr); max drawdown −$73,445; 2016–20 −$60,133, 2021–26 +$57,580 | **FAIL** (no edge over the full period; consistent with R9: lost $45,617 in 2016–23) |
| 59 | broker credit bonuses | see below | **FAIL** on terms |

**#59 terms (third-party summaries of broker terms, 2026):**
- HFM 100% SuperCharged: credit is removed once equity drops below the bonus amount, so it
  does not absorb losses past the deposit; any withdrawal cuts the credit 1:1.
- HFM 30% Rescue: does absorb losses past the deposit, but is non-withdrawable margin credit
  capped at $7,000 total, so at most a one-time option worth a few thousand.
- XM: credit is non-withdrawable and withdrawals remove it (proportionally or entirely,
  depending on the source); bonus abuse leads to account closure.
- None is a repeatable free option like a monthly prop reset. The brokers are offshore
  entities; Malaysian licensing not checked.

**Takeaways:**
- To match Topstep's $4,098/yr, funding carry needs about $64K (held) to $140K (rotating) of capital, and its yield has been falling since 2024.
- #58 confirms the Topstep income is almost all structure: the same trades lose money on own money over 2016–26.
  Any non-prop route therefore needs its own edge; reusing these trades gives none.

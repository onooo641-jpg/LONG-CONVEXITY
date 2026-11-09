# ES unseen-market test — pre-registration

Written and committed **before** any strategy run on ES. Nothing below may be
changed after the first run; if a definition turns out wrong, the run stands as
recorded and a correction goes in a dated addendum.

## Question

The LTF sweep was built and judged on NQ. Is what it shows on NQ a property of
the method, or of NQ? ES (S&P 500 futures) is the closest liquid market, and no
part of the strategy has ever been run on it.

## Data

- ES.v.0 1-minute bars, Databento GLBX.MDP3, three shards in `data/raw/`
  (`ES_v_0_1m_2010-06-06_2018-01-01`, `..._2018-01-01_2023-01-01`,
  `..._2023-01-01_2026-10-29`), fetched in Actions run 42579041681, log in
  `docs/jx_runs/fetch_42579041681.txt`. $20.93 in total.
- Databento flagged some days as degraded. They are **not** excluded; the NQ
  series was never screened that way either.

## Strategy and execution — all unchanged from NQ

- `strategies.ltf_sweep.generate_orders` with `LTFSweepConfig()` defaults,
  one trade per day. **No parameter is rescaled for ES.** The point-valued
  settings (`min_penetration` 0.25, `min_fvg_size` 0.5, `stop_buffer_points` 1.0,
  `min_risk_points` 1, `max_risk_points` 120) were chosen in NQ points. ES moves
  roughly a quarter to a third as many points per day, so the same numbers are
  relatively wider on ES. That is accepted: rescaling would be a choice made for
  ES, and a rescaled run would be a second, separately registered test.
- Contract: MES. Tick 0.25 points, $1.25 per tick ($5 per point). Commission
  $1.24 round trip, the same as the MNQ model. Topstep's actual MES rate is not
  verified.
- `BacktestConfig(risk_per_trade_usd=900)` otherwise default: limit entries,
  1 tick exit slippage, pessimistic ambiguity.
- Recycling: `XFARules()` (rulebook 20261107), `Policy.LOCK_FIRST`, one
  unbroken chain. Contract cap 50 micros in the Combine, as in `recycle.py`.

## Windows

- **Decides — 2016-01-01 .. 2026-10-28**: the same window as the NQ headline
  (ledger R/N rows), so the two are directly comparable.
- **Context — 2010-07-01 .. 2015-12-31**: reported, does not decide. On NQ this
  window lost (holdout, HOLDOUT_PREREG.md), mostly to fees at low prices.

## Baseline and win rule

The NQ claim is that the strategy beats a coin flip with the same trade sizes
(NOTES_JX "Zero-edge baseline"): real recycling net above the 95th percentile of
200 coin-flip runs (seed 1, random sign on gross P&L, commission kept). The same
test is applied to ES in the deciding window.

**ES confirms** the NQ result if, in 2016-01-01 .. 2026-10-28, ES recycling net
is above the 95th percentile of its own coin-flip distribution.

Anything else is **does not confirm**. In that case the NQ result is treated as
possibly specific to NQ, and nothing is tuned on ES to rescue it.

Also reported, not decisive: trades, win rate, profit factor, raw net by year,
pass rate, payouts, and the same figures for the context window.

## What either outcome changes

- Confirms: stronger evidence the edge is the method's. It also makes a second
  account on MES a candidate. That still needs its own forward log before money
  goes in.
- Does not confirm: the NQ plan is unchanged, but the evidence behind it is
  weaker than the NQ backtest alone suggests. This is recorded in FIGURES_LEDGER
  and NOTES_JX.

Command: `uv run python scripts/es_test.py`

## Results (2026-11-09, run once, `scripts/es_test.py`)

Raw output: `docs/jx_runs/es_test_ES.txt`. The same script on NQ
(`--market NQ`, `docs/jx_runs/es_test_NQ_check.txt`) reproduces the ledger:
$44,359 net, coin flip median $18,046, holdout −$2,505.

| 2016-01-01 .. 2026-10-28 (decides) | NQ (MNQ) | ES (MES) |
|---|---|---|
| trades / win rate / PF | 2,185 / 53.1% / 0.994 | 1,754 / 53.1% / 0.977 |
| raw net / fees | see ledger S1b | −$18,363 / $84,972 |
| recycling net | **$44,359** | **$20,338** |
| coin flip median / 95th pct | $18,046 / $36,711 | $11,002 / $24,180 |
| real beats … of flips | 98% | 86% |
| pass rate (real / flip median) | 34.4% / 26.7% | 32.3% / 26.6% |

| 2010-07-01 .. 2015-12-31 (context) | NQ | ES |
|---|---|---|
| PF / recycling net | 0.784 / −$2,505 | 0.873 / $2,478 |
| real beats … of flips | 83% | 95% |

**Verdict: DOES NOT CONFIRM.** ES recycling net $20,338 is below its coin-flip
95th percentile, $24,180. Per the rule above, the NQ result is treated as
possibly NQ-specific, and nothing is tuned on ES.

What the numbers show, without changing the verdict:
- ES points the same way as NQ: a higher pass rate than a coin flip and more
  money than 86% of flips. The margin is too small to clear the bar set in
  advance.
- On both markets, the raw strategy loses (PF below 1) and the recycling
  structure turns that into profit. Part of that profit is what a coin flip
  also earns.
- Fees are the largest cost on ES: $85K against a −$18K raw result, because
  the unscaled 1-point stop buffer gives a median 5-point stop and 35 micros.
  A lower commission or a rescaled ES config would change this. Either one is
  a new test that would need its own pre-registration; neither was run here.

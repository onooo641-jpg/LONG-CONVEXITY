# New reward programmes in their first 30 days (#207) — 2026-11-21

Written and committed before running. Tests the radar's core thesis ("catch new incentives early, before capital crowds in") on stablecoin
pools, as a repeatable rule. Data already fetched for #204 (`data/public/fallback_stable_charts.parquet`: 727 stablecoin, single-exposure
pools with TVL ≥ $1M today, full DefiLlama daily history). Only the #204 rotation has been run on it; reward-start events have not been looked at.

## Rule
- **Event:** day d where a pool's apyReward > 0 and either (a) the previous 14 days had apyReward = 0 / missing, or (b) d is the pool's first
  day of history; TVL on d ≥ $1M; apyReward on d ≤ 1000% (data errors excluded).
- **Trade:** enter on d+1 (one day to notice), hold 30 days, then exit. Daily return = (apyBase + 0.9 × apyReward) / 365.
- **Portfolio:** $10,000 split equally across active events, at most 5 at a time (new events skipped while 5 are held); idle money earns the
  baseline (Aave v3 USDC Ethereum, same days). Cost $5 per entry and per exit.
- **Loss stress:** a held pool whose TVL falls > 50% within 7 days → −20% of that position, position closed (as #204).
- Window 2024-11-01 .. 2026-10-31, halves of 12 months.

## Pass
- **Stage 1 (2026-08..10):** KILL if portfolio net < 4.0%/yr.
- **Stage 2:** PASS if portfolio net ≥ 8.0%/yr in both halves AND ≥ 30 events taken in each half (repeatable). Also reported: mean
  excess yield per event over the baseline, share of events hitting the stress, $ per year on $10K / $40K.
Bias: pools that died before today are missing (survivorship) → results are an upper bound.

Command: `uv run python scripts/newrewards_20261121.py | tee docs/jx_runs/newrewards_20261121.txt`

## Result (2026-11-21, `docs/jx_runs/newrewards_20261121.txt`)
242 reward-start events in the window; 100 taken (37 / 63 by half). **Stage 1: −61.7%/yr → KILL. FAIL.** 26% of taken positions hit the
loss-stress (TVL −50% in a week). Post-hoc diagnostic, not a verdict (`docs/jx_runs/newrewards_posthoc_nostress_20261121.txt`): with the stress
set to zero the rule earns 4.3% / −0.5% by half (1.9%/yr), below plain Aave USDC (5.2% / 3.5%): the median new reward on a stablecoin pool
is only 2.1% APR and $5 transactions on $10K eat it. "Catch new stablecoin rewards early" has no edge in this data.

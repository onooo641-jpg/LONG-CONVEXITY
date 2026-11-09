# Idea batch, 2026-11-09 — pre-registration (CANDIDATES rows 17–28)

Committed before any of these ideas is run. Results go in a dated section at the
end; nothing above it changes. None of these touches the live config. An idea
that passes goes to the forward log as a shadow next to the baseline, not live.

## Datasets and baseline

Five datasets, each with its own baseline: unchanged `LTFSweepConfig()`, one
trade per day, $900, `XFARules()` (20261107), `Policy.LOCK_FIRST`, $1.24
commission. Contract specs are as in ES_PREREG / PREREG_YM_RTY.

| id | market | window |
|---|---|---|
| NQ-S | NQ | 2016-01-01..2026-10-28 (screen, already seen) |
| NQ-O | NQ | 2010-07-01..2015-12-31 |
| ES | ES | 2016-01-01..2026-10-28 |
| YM | YM | 2016-01-01..2026-10-28 |
| RTY | RTY | 2017-08-01..2026-10-28 |

**Metric: margin = recycling net − median recycling net of 100 coin flips**
(same trade sizes, random sign on gross P&L, commission kept, seed 1; any
funded_scale is applied to the flips too). This removes what the account
structure pays regardless of the signal, so an idea can't pass just by trading
more or bigger.

## Pass rule

An idea **passes** if its margin beats its baseline's margin on **NQ-S and NQ-O
and at least 2 of ES / YM / RTY**. Twelve ideas are tested at once, so a
single-dataset improvement means nothing; this rule is set to make a lucky pass
unlikely.

## The ideas (each is one row in CANDIDATES)

17. **Long only.** Drop short trades. Index futures drift up.
18. **Short only.** Drop long trades. The mirror of 17, so the two are judged
    together.
19. **Scale out, runner to 2R.** Half off at the 1R target. The rest runs to 2R
    with its stop moved to entry (`scale_out_fraction` 0.5,
    `runner_stop_offset` 0, `runner_target` = entry + 2R).
20. **Scale out, runner to 3R.** Same as 19 with the runner to 3R.
21. **Smaller funded size, ×0.5.** Combine at $900; funded trades at half size
    (`recycle(funded_scale=0.5)`).
22. **Smaller funded size, ×0.75.**
23. **Loss-streak pause.** After 3 losing trades in a row, skip the next 5
    trades. The streak counts every baseline trade's outcome, taken or skipped,
    so it is knowable live.
24. **Equity filter.** Take a trade only if the previous 20 baseline trades net
    above zero. Needs 20 prior trades.
25. **Fee cap 5%.** Skip a trade if its round-trip commission (contracts ×
    $1.24) is more than 5% of the $900 risk (more than 36 micros).
26. **Fee cap 3%.** The same at 3% (more than 21 micros).
27. **Wider stop buffer.** `stop_buffer_points` 2.0 instead of 1.0, orders
    regenerated.
28. **Time stop.** Exit at market 120 minutes after the order goes live if
    neither stop nor target was hit (`time_exit_ts` = min(original,
    valid_from + 120 min)).

Command: `uv run python scripts/idea_batch_20261109.py`

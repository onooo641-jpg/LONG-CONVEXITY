# YM and RTY unseen-market tests — pre-registration (2026-11-09)

Committed before the YM/RTY data reached this repo and before any run on them.
Results go in a dated section at the end; nothing above it changes.

## Why two versions

ES unchanged did not confirm (docs/ES_PREREG.md). ES with its point settings
scaled to ES prices (PREREG_20261109 test 2b, k = 0.31) beat 100% of its coin
flips, but that was run after the ES failure, so it is a hypothesis, not
evidence. YM and RTY have never been run, so they can test it cleanly:

- **U (unchanged)** — `LTFSweepConfig()` exactly as on NQ.
- **S (scaled)** — the 2b rule, unchanged: k = median over 2016-01-01..2026-10-28
  of (daily RTH close of the market ÷ daily RTH close of NQ), rounded to 2
  decimals; `stop_buffer_points`, `min_fvg_size`, `min_risk_points`,
  `max_risk_points` each × k; `min_penetration` = one tick of that market
  (YM 1.0, RTY 0.1), as it is one tick on NQ and ES.

## Data and contracts

- YM.v.0 and RTY.v.0 1-minute bars from Databento GLBX.MDP3, fetched by the
  push-triggered workflow (`.github/fetch_request.txt`, commit 25c3bad).
- MYM: tick 1.0 point, $0.50 per point. M2K: tick 0.1 point, $5 per point.
  (Contract specs from general knowledge, not checked against CME today.)
- The engine works in 0.25-point ticks, so tick_value is $ per 0.25 point
  (MYM 0.125, M2K 1.25), and exit slippage is one real tick
  (MYM 4 engine ticks, M2K 0.4).
- Commission $1.24 round trip, the MNQ/MES model. Not verified for MYM/M2K.
- $900 a trade, `XFARules()` rulebook 20261107, `Policy.LOCK_FIRST`, one chain.

## Windows and rule

Decides: 2016-01-01 .. 2026-10-28. If a market's data starts later, the window
starts at its first full month and that is stated. Context: 2010-07-01 ..
2015-12-31 where data exists.

Same rule as ES: a version **confirms** on a market if its recycling net is
above the 95th percentile of 200 coin flips (same trade sizes, random sign on
gross P&L, commission kept, seed 1).

**Reading:**
- The "scaled" hypothesis is supported only if **S confirms on both YM and
  RTY**. One of two counts as mixed, none as not supported.
- U is reported for each market under the same rule. It extends the ES result
  and decides nothing about S.

## What changes either way

Nothing in the live NQ plan changes on this result alone. If S is supported,
the next step is a forward log of S on a second market before any money goes
in. If it is not supported, the ES 2b result is treated as chance.

Command: `uv run python scripts/ym_rty_test.py`

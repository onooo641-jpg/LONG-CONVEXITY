# Holdout pre-registration — NQ 2010-07-01 to 2015-12-31

Written and committed **before** any strategy result on this window was
looked at. The commit hash of this file is the proof. Nothing below may be
edited after the run. Corrections go in a dated section at the end, with the
reason.

## Why this window is a holdout

Every LTF Sweep result in the repo starts at 2016-01-01. The data from
2010-06-07 exists (`data/raw/NQ_v_0_1m_2010_2017.parquet`), but was excluded
because the Asian session is thin before 2016, which matters for the seven
session strategies. LTF Sweep trades 09:30–16:00 ET, where coverage is
94.5% (2010), 94.6% (2011), 96.6% (2012), 98–99% (2013–2015). That was
measured by counting RTH 1-minute bars, the only thing looked at on this
window before this file.

Usable once. After the run below it is in-sample like everything else.

## Common setup (all variants)

- Strategy: `strategies/ltf_sweep.py`, `LTFSweepConfig()` defaults, one trade
  per day. Orders from `generate_orders()` on bars from 2010-06-07, so pools
  and swings have history.
- Execution: `BacktestConfig(risk_per_trade_usd=900.0)`, all other defaults.
- Window: trades with `entry_ts` in [2010-07-01, 2016-01-01) UTC.
- Account model: `recycle()` with `XFARules()` as of commit `c43f477` ($2,000
  cap, payout resets MLL, profit-since-payout, Combine MLL lock), and
  `Policy.LOCK_FIRST`. One unbroken chain from the first trade.
- Filters remove **orders** before simulation. Nothing else changes.

## Variants

**Baseline.** No filter.

**V1 — news days.** Skip any order whose `trading_date` (CME trading date)
is a release day for CPI, PPI, Employment Situation (NFP), PCE (Personal
Income and Outlays), Retail Sales, or an FOMC decision day. These are the
same six series as `docs/tier1_calendar.csv` on `jx/rules-recheck-local`.
Dates from primary sources (BLS, BEA, Census, federalreserve.gov) for
2010-06..2015-12. **Status: pending.** Only PPI (BLS historical file) and
2012 CPI/NFP were fetched before this commit. V1 is run when the calendar is
complete, without changing this definition.

**V2 — with the daily trend.** For each order, take daily closes = the last
1-minute close at or before 16:00 ET on each New York date. Let `c1` = the
close of the last date before the order's `trading_date`, and `sma` = the
mean of the 20 closes ending at `c1` inclusive. Keep a long only if
`c1 >= sma`; keep a short only if `c1 < sma`. Fewer than 20 prior closes:
skip the order.

**V3 — wide stops.** `risk_points` as `generate_orders()` reports it. Skip the
order if `risk_points > 2.0 ×` the median `risk_points` of the previous 60
orders (all orders, before any filtering, by `valid_from`). Fewer than 20
previous orders: keep.

**V4 — big overnight gaps.** For each New York date: RTH open = open of the
first 1-minute bar at or after 09:30 ET; RTH close = last close at or before
16:00 ET; RTH range = high − low over 09:30–16:00. Gap on date D =
|open(D) − close(previous date)|. Skip orders on D if gap > 0.5 × the mean RTH
range of the 20 dates before D. Fewer than 20 prior dates: skip the order.

## What counts as a win (decided now)

A variant wins only if **all three** hold on the holdout, against the
baseline:

1. Recycling net (one chain, as above) is higher.
2. Raw profit factor (`net_pnl` > 0 summed ÷ `net_pnl` < 0 summed, absolute)
   is higher.
3. Raw net P&L is higher in at least 4 of the 6 calendar years 2010 (from
   07-01) to 2015.

A winner is **not adopted**. It goes into a shadow forward log and needs to
hold up there before any `PRECOMMIT.md` change.

Also reported, decision-free: the baseline's raw stats and recycling result
on the holdout (the main thesis check), and every variant on 2016-01-01 to
2026-10-28 (seen data, context only).

## Command

`uv run python scripts/holdout_test.py` (written after this file, committed
with the results).

---

## Result (2026-11-07, run once, commit after 633a258)

`uv run python scripts/holdout_test.py` → `docs/jx_runs/holdout_test_2010_2015.txt`.

**Baseline on the holdout** ($900, current Topstep rules, LOCK_FIRST):
625 trades, win 52.3%, **PF 0.784**, raw −$67,633. Recycling: **net
−$2,505** (withdrawn $2,431, spent $4,936), pass rate 16.7%, 3 payouts,
longest dry spell 1,739 days.

**Verdict by the pre-registered rule:**
- V2 trend: no (recycling net lower)
- **V3 wide stop: WIN** by the rule, but by a hair (recycling net +$373,
  PF 0.784 → 0.788). It goes to a shadow log only, as registered.
- V4 gap: no (recycling net lower)
- V1 news: not run (calendar pending)

## Post-hoc explanation (not pre-registered, does not change the verdict)

`scripts/holdout_fee_check.py` → `docs/jx_runs/holdout_fee_check.txt`.
Before fees the holdout is slightly positive: **gross PF 1.037** (+$10,204).
Fees were $77,837. NQ traded around 2,000–4,500, stops were 3.5–6.6 points,
so $900 of risk meant 70–127 micros, and fees ran **10–18% of risk per
trade**. They are ~2% today. The same drag explains much of 2016–2018
(12–13% of risk, all losing years). It fell steadily as the index rose.

Re-run with fees at today's ratio (1.8% of risk): raw PF 1.000, raw +$79,
**recycling net +$164** over 5.5 years, pass rate 24.0%. At 2.4%:
−$281. So on unseen years, at today's costs, the business **breaks even**.
It does not reproduce the 2016–2025 figure ($31,404 over 10 years). The pass
rate (24%) is below the zero-edge coin-flip baseline (26.7%,
`jx_zero_edge.py`).

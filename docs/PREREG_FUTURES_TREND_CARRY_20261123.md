# #350 Cross-asset futures trend and carry on own capital (non-prop; Databento daily bars) — 2026-11-23

Jx (2026-11-23): find a non-prop strategy with prop-like profits; Databento credits are available. A documented strategy edge (not a loophole):
time-series momentum and curve carry across CME futures. Written before any data is fetched.
**Data.** Databento GLBX.MDP3, ohlcv-1d, continuous `.v.0` (front by volume) and `.v.1` (second), 2010-06..2026-10, 26 roots: ES NQ YM RTY ZT ZF ZN
ZB 6E 6J 6B 6A 6C 6S GC SI HG CL NG RB HO ZC ZS ZW LE HE. **Cost control:** quote first (free); download only if the total quote ≤ $2.00
(small against the free credits; otherwise stop and report the quote to Jx).
**Signals.** TSMOM: sign of the trailing L-month return of `.v.0` (skipping the last week). Carry: annualised log(F0 / F1), with contract spacing
of 3 months for index / rates / FX, 1 month for CL NG RB HO, 2 months for GC SI HG LE HE ZC ZS ZW (an approximation). Combo: average of the two
signs. Positions sized to a target annual volatility per market (60-day realised), scaled so the whole book hits the portfolio vol target.
Monthly rebalance; cost 2 bps of traded notional per side; cash earns T-bills (FRED DTB3).
**Grid (36).** L {3, 6, 12} × vol target {10%, 15%} × universe {all 26, ex-ags (drop ZC ZS ZW LE HE)} × signal {TSMOM, carry, combo}.
**Test (same as batch 9).** Walk-forward: monthly pick of the best config on the trailing 36 months; OOS 2016-01..2026-10, halves split 2021-05.
PASS = both halves ≥ 10%/yr AND all-OOS with costs × 1.5 ≥ 10%/yr AND worst OOS drawdown no worse than SPY's over the same months. Stage 1
(kill-only): OOS 2025-11..2026-10 < 4%/yr.
**Capital note.** Futures need margin; to earn about $18K/yr (the Malaysia-eligible prop portfolio) at 10–15%/yr takes about $120–180K.
Command: `uv run python -m scripts.futures_trend_20261123 | tee docs/jx_runs/futures_trend_20261123.txt`.

## Addendum 1 (2026-11-23): cost approval
The quote was $2.4282 (52 continuous symbols, ohlcv-1d), above the $2.00 cap, so the first download aborted. **Jx approved $2.43** (from his Databento
credits) on 2026-11-23. The cap is raised to $2.50 for this one pull. No rule changes.

## Addendum 2 (2026-11-23, before any data has arrived): #351–#354 on the same Databento daily bars
Same universe, costs, vol scaling, walk-forward and PASS rule as #350 (both OOS halves ≥ 10%/yr, costs × 1.5 ≥ 10%, drawdown no worse than
SPY's). Cross-sectional legs are dollar-neutral (long top third, short bottom third, equal risk per market).
| # | factor | signal (monthly) | grid |
|---|---|---|---|
| 351 | cross-sectional momentum | trailing L-month return (skip last week) | L {3, 6, 12} × vt {10, 15%} × universe {all, ex-ags} = 12 |
| 352 | value (long-horizon reversal) | minus the trailing 5-year return (L {36, 48, 60} months) | 12 |
| 353 | skewness | minus the trailing 12-month skewness of daily returns (window {6, 12, 24} months) | 12 |
| 354 | multi-factor | equal-risk sum of the TSMOM, carry, cross-sectional momentum and value signals (each from its own L) | L {3, 6, 12} × vt × universe = 12 |
Literature basis (third-party, recorded as motivation only, not as evidence): time-series momentum and carry across futures (Moskowitz–Ooi–
Pedersen 2012; Koijen et al. 2018), value and momentum everywhere (Asness–Moskowitz–Pedersen 2013), commodity skewness (Fernandez-Perez et al.).

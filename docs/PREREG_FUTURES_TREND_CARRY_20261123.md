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

## Addendum 3 (2026-11-23, after the first #350–#354 run; written before any whole-contract sizing is computed)
First run: #351 cross-sectional momentum met the registered PASS (walk-forward CAGR 20.72%, halves 26.94% / 14.97%, costs × 1.5 20.20%, worst
drawdown −22.3% vs SPY −23.9%). #352 and part of #354 were broken: the 5-year window sliced to `-0` (empty), so value never traded. This is a
mechanical bug; fixed and all five re-run (results below once identical on re-run).
**#351b implementability (new, stricter test; the #351 rule is unchanged).** The registered backtest uses fractional notional. A real account trades
whole contracts. Universe for a small account: markets with a CME micro or small contract (multipliers to be verified against CME pages
before any live use; assumed here): MES ($5 × index), MNQ ($2), MYM ($0.50), M2K ($5), M6E (€12,500), M6A (A$10,000), M6B (£6,250), MGC
(10 oz), SIL (1,000 oz), MHG (2,500 lb), MCL (100 bbl), plus full-size ZN ($1,000 × price) and ZT ($2,000 × price) to test whether rates can
be held at all. Each month, target notional = the #351 weight × capital, rounded to the nearest whole contract; cost $1.50 per micro contract
per side (assumed) + 1 tick. Capital levels: $15K, $50K, $100K, $250K. **PASS at a capital level** = the fixed most-picked config
(xsmom / L12 / vt15 / ex-ags) on 2016-01..2026-10 earns ≥ 10%/yr in both halves after whole-contract rounding and costs, with a worst drawdown no
worse than SPY's. Report the smallest capital that passes and its dollar profit per year, compared with the prop portfolio's $18K/yr.

### Results (2026-11-23; both outputs identical on re-run)
**#350–#354 after the bug fix** (`docs/jx_runs/futures_trend_20261123.txt`; walk-forward OOS 2016-01..2026-10, 130 months):
| # | factor | CAGR | halves | costs × 1.5 | worst DD (SPY −23.9%) | verdict |
|---|---|---|---|---|---|---|
| 350 | trend / carry | 11.72% | 4.00% / 19.75% | 12.73% | −34.6% | FAIL (first half, drawdown) |
| 351 | cross-sectional momentum | **20.72%** | **26.94% / 14.97%** | **20.20%** | **−22.3%** | **PASS** (most-picked xsmom / L12 / vt15 / ex-ags, 81 of 130 months) |
| 352 | value (5-year reversal) | 0.46% | 8.56% / −6.82% | −0.39% | −46.0% | FAIL |
| 353 | skewness | 8.75% | 6.12% / 11.35% | 8.24% | −27.9% | FAIL |
| 354 | multi-factor | 1.09% | 0.39% / 1.76% | 0.77% | −29.3% | FAIL |
#351 is unchanged by the fix (it never used the 5-year window) and is the first non-prop idea in the repo to pass a registered full test.

**#351b implementability** (`docs/jx_runs/futures_xsmom_small_20261123.txt`; fixed config xsmom / L12 / vt15, 13 markets with micro or
small contracts, whole contracts, assumed costs):
| account | CAGR | halves | worst DD | verdict | avg $/yr |
|---|---|---|---|---|---|
| fractional reference (13 markets) | 16.15% | 22.97% / 9.81% | −24.4% | FAIL (second half) | — |
| $15,000 | 10.00% | 17.51% / 3.08% | −34.0% | FAIL | $2,537 |
| $50,000 | 15.19% | 23.12% / 7.89% | −27.2% | FAIL | $17,008 |
| $100,000 | 17.06% | 23.71% / 10.87% | −23.0% | PASS (marginal) | $42,316 |
| $250,000 | 15.94% | 23.16% / 9.23% | −24.1% | FAIL | $92,887 |
**Reading.** The 13-market universe a small account can trade fails even before rounding (second half 9.81%); the $100K pass sits inside the
fractional reference's own failure, so it is rounding luck, not a property of the strategy. The edge needs the full 21–26-market universe,
including full-size rates and FX contracts (ZN ≈ $110K notional each), i.e. roughly $250K–$1M of capital, and then pays ~15–20%/yr. That is a
normal managed-futures risk premium, not a prop-like return on small capital. **Verdict for Jx: real but not usable at his size.** Margin not
modelled; multipliers and costs assumed.

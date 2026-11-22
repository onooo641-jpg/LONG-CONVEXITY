# Batch 9: fallback benchmark in MYR + four risk-premium families aimed at ≥ 10%/yr (#292–#295) — 2026-11-22

Written and committed before any batch-9 data is fetched (job `batch9`). Jx asked (2026-11-22) for (a) S&P 500 vs Malaysian fixed deposits in
ringgit, and (b) at least two ideas at 10%+/yr, with many configurations. **Honest label:** #292–#295 are *economic risk premia* (paid for bearing
crash, currency or volatility risk), not loopholes. They are allowed under "data/economics-driven" but carry tail risk, so a drawdown check is
added to the pass rule.

## A. Benchmark (ranking, no pass/fail)
SPY total return (adjusted close; Yahoo chart API, else stooq price + 1.8%/yr dividends, labelled) converted to MYR with FRED DEXMAUS, vs
Malaysian deposit rate (FRED INTDSRMYM193N; where missing: 2.5%/yr, labelled assumed), vs USD T-bills (FRED DTB3) converted to MYR.
Report per year 2006–2026, CAGR, worst drawdown, worst year, for 100% FD, 100% S&P, 50/50 and 70/30 S&P/FD (annual rebalance).

## B. Walk-forward families (all: monthly pick of the best config on the trailing 36 months; OOS 2016-01..2026-10, halves split 2021-05;
## costs as stated; PASS = both OOS halves ≥ 10%/yr AND all-OOS with costs ×1.5 ≥ 10%/yr AND worst OOS drawdown no worse than SPY's
## worst drawdown over the same OOS months)
| # | family | data | grid |
|---|---|---|---|
| 292 | VIX futures roll-down (short front or second VX future) | Cboe CFE per-contract daily settlements 2013+, Cboe VIX / VIX3M indices | exposure {0.1, 0.2, 0.3, 0.5} of capital (notional/capital) × contract {VX1, VX2} × entry filter {always, VIX3M/VIX > 1.0, > 1.1} × exit {none, flat when VIX > 30} = 48; daily roll by weights (constant-maturity 30 days), cost 0.05 vol pts per roll per contract notional fraction; T-bill on cash |
| 293 | FX carry (G10 + EM vs USD) | FRED daily FX (DEX*) + FRED 3-month rates (IR3TIB01*M156N) | k {1, 2, 3} highest-carry longs × funding {USD, lowest-carry} × leverage {1, 2} × filter {none, VIX < 25, 60-day vol target 10%} = 36; monthly rebalance; cost 0.05% per trade side + 0.5%/yr financing spread |
| 294 | Cboe option-strategy indices (put-writing, buy-writes, collars, condors) | Cboe index history CSVs (PUT, WPUT, BXM, BXMD, BXY, CLL, CNDR, PPUT, …) + DTB3 | index {each available} × leverage {1.0, 1.5} = 2 × #indices; cost 0.5%/yr implementation drag, leverage financed at DTB3 + 0.5% |
| 295 | levered stock–bond risk parity | SPY total return + 10-year Treasury total return from FRED DGS10 (duration approximation) + DTB3 | stock weight {40, 50, 60}% × leverage {1, 1.5, 2} × rebalance {monthly} × vol target {none, 10%} = 18; financing DTB3 + 0.5% |
Malaysia access (Stage 0): all four via a broker such as Interactive Brokers, which serves Malaysian residents (**assumed, not verified**).
Command: `uv run python -m scripts.batch9_20261122 | tee docs/jx_runs/batch9_20261122.txt`.

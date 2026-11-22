# #291 Buy the prop firm's "free option" in the options market (non-prop) — 2026-11-22

**Question.** On own money the friend's NQ trades lose (−$2,553 over 2016–26, #58). At Topstep they earn $44,359 because losses are capped at
fees while profits are paid out. Can the same capped-loss shape be bought from the listed options market, with no prop firm?
**Data.** Friend's trades (`ideas_orders_NQ.parquet`, `simulate`, $900 risk, the same trades as the Topstep benchmark, 2016-01..2026-10).
VXN (Cboe Nasdaq-100 volatility index, daily close, FRED series VXNCLS; fetch job `vxn`).
**Rule.** For each trade, at the entry fill buy an ATM Nasdaq-100 option in the trade's direction (call for long, put for short), expiring at
16:00 ET that day (0DTE; NQ/MNQ options list daily expiries; the model applies them to all years, which is **optimistic for years before daily
expiries existed**). Price: Black-Scholes, r = 0, σ = prior-day VXN close / 100, T = time to 16:00 ET (minimum 30 minutes). Spend **$900 of
premium per trade** (Micro options, multiplier $2, fractional size allowed as an approximation). Exit at the trade's exit time, valued with
the same σ. The most a trade can lose is $900, the same as the $900 risk budget per trade in the futures backtest.
**Costs (assumed, not verified).** Half-spread 2% of premium per side, $0.50 commission per micro option per side.
**Pass (same flag rule as prop products, vs Topstep 50K no delay).** Real net ≥ $22,180 (50% of Topstep) AND coin-flip median ≥ $5,000
(random trade directions, costs kept, 200 runs, seed 1) AND worst drawdown of cumulative P&L ≥ −$5,280 (1.5× Topstep's −$3,520).
Context only: σ ×0.8 and ×1.2 (0DTE implied vol differs from 30-day VXN); results per half (2016–20, 2021–26).
Command: `uv run python -m scripts.optionwrap_20261122 | tee docs/jx_runs/optionwrap_20261122.txt`.

# #370 Crypto perp trend-following and cross-sectional momentum, with a configuration grid and walk-forward selection (non-prop) — 2026-11-24

**Why.** Jx asked for a last in-depth audit across all areas. General trading was tested heavily (prop-side NQ, futures factors #350–#354,
carry, options, index events) but **crypto trend / momentum was never tested**, although crypto is where these effects are reputed to be
strongest and Hyperliquid (usable from Malaysia, used in earlier tests) offers the markets. Written before any data are fetched.

**Data (free).** Binance USDⓈ-M perpetual daily klines and funding-rate files from the public archive `data.binance.vision`, **every symbol
ever listed** (including delisted — no survivorship), 2020-01..2026-10; symbol list from the archive's S3 listing. Binance prices and
funding are a proxy for Hyperliquid (prices are arbitraged across venues; funding levels differ — Hyperliquid funding from
`data/public/hl_funding.parquet` is shown as a 2024–26 sensitivity). BTC buy-and-hold is the benchmark.

**Universe.** Each month: USDT perps ranked by trailing 30-day quote volume at the previous month end (no look-ahead); top **N**.
A coin drops out if it has no price that day (delisting = position closed at the last price).

**Configuration grid (52 configs, fixed).**
- **TS trend** (per coin, equal risk): signal = sign of the L-day return, L ∈ {20, 50, 100, 200}; mode ∈ {long/flat, long/short};
  N ∈ {20, 50}; rebalance ∈ {daily, weekly}. Weights ∝ 1/(60-day volatility), gross exposure 1× capital. (32 configs)
- **XS momentum**: rank by L-day return skipping the last day, L ∈ {7, 14, 30, 60, 90}; long top q, short bottom q, q ∈ {10%, 20%};
  N ∈ {20, 50}; weekly rebalance; 0.5× long + 0.5× short, equal weight. (20 configs)
- Costs: 4.5 bps taker fee + 5 bps slippage per side on traded notional (sensitivity: × 1.5); funding: longs pay, shorts receive the
  symbol's funding (8-hourly sums per day). No leverage beyond 1× gross.

**Walk-forward.** Each month, pick the configuration with the best trailing-12-month return (ties: lower drawdown); hold it next month.
Out-of-sample 2021-01..2026-10; halves split at the midpoint. The best fixed configuration in hindsight is printed as **context only**.

**Stages.**
- **Stage 1 (kill only, cheapest slice 2024-01..2026-10, two base configs: TS L=100 long/short N=20 daily; XS L=30 q=20% N=50):** KILL if
  both base configs lose money (CAGR < 0%).
- **Stage 2 (walk-forward):** **Prop-like PASS** = CAGR ≥ 100%/yr in both halves and with costs × 1.5, worst drawdown no worse than −30%.
  **Useful** = CAGR ≥ 20%/yr in both halves and with costs × 1.5, and worst drawdown no worse than BTC buy-and-hold's over the same window.
  Otherwise FAIL. Implementability at $15K on Hyperliquid (minimum order ~$10) is checked for the chosen configs (count of positions).

**Commands.** fetch: Actions job `cryptotrend370`; analysis: `uv run python -m scripts.crypto_trend_20261124 | tee
docs/jx_runs/crypto_trend_20261124.txt` (re-run once; must be identical).
**Limits.** Binance funding ≠ Hyperliquid funding; daily closes ignore intraday stops/liquidations (1× gross limits this); slippage for
smaller coins may exceed 5 bps; 52 configs create selection risk (handled by walk-forward + cost stress, not removed).

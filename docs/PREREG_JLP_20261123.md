# #363 Hedged Jupiter JLP ("be the house" for perp traders who lose): does it reach prop-like money? (non-prop) — 2026-11-23

**Why.** Jx asked whether the prop-firm factor (payouts funded by the ~90% of customers who fail) was ever tested outside prop firms. The
"house" side of that factor in open markets is a perp-DEX liquidity pool: it is every trader's counterparty, so it keeps traders' net losses
plus most trading fees. Tested so far: Hyperliquid HLP, Gains gUSDC (#225, fail 6.9%/yr), GMX GM (#221, fail 3.6%/yr) and liquidation bonuses
(#100). **Jupiter JLP** (Solana; the largest such pool, with the highest published yields) was marked "not testable" in batch 4 (#220) because
only the current APR was fetched. Its daily **price** history is free (DefiLlama coins API, CoinGecko id), and a price series captures the
whole return (fees + traders' losses − traders' wins + the basket's moves). So the test can be done with a hedge estimated from prices,
without the pool's historical weights. Written before any JLP data is fetched.

## Stage 0 (desk check)
- Access: Jupiter is a permissionless Solana app; Hyperliquid (hedge venue) is used from Malaysia in earlier tests (assumed). The fetch job
  downloads Jupiter's terms page(s) and prints any mention of Malaysia / restricted jurisdictions. An explicit Malaysia exclusion kills #363.
- Not a rule-evasion or bot-detection issue: holding a pool token and a short perp is ordinary use.

## Data
DefiLlama `coins.llama.fi/chart` daily prices, all fetched with the same start timestamp (so the daily points line up):
JLP (`coingecko:jupiter-perpetuals-liquidity-provider-token`; also the Solana mint `solana:27G8MtK7VtTcCHkpASjSDdkWWYfoqT6ggEuKidVJidD4`, the
series with more days is used and both lengths are printed), `coingecko:solana`, `coingecko:ethereum`, `coingecko:bitcoin`, from 2023-10-01.
Hyperliquid hourly funding for SOL / ETH / BTC (`data/public/hl_funding.parquet`, already in the repo; 2024-01-01..2026-11-19).

## Exact rule
- Daily simple returns. Every Monday, hedge ratios β (SOL, ETH, BTC) = non-negative least squares of JLP's daily returns on the three coins'
  daily returns over the trailing 60 days (both sides demeaned, i.e. with an intercept; NNLS solved exactly by trying every subset of the
  three coins). Held for the week.
- Hedged daily return per $1 of JLP = r_JLP − Σ β_i r_i + Σ β_i × (that UTC day's summed Hyperliquid hourly funding of coin i) (a short
  receives positive funding).
- Costs: Hyperliquid taker 0.045% on hedge notional traded (the first hedge and every weekly |Δβ|); JLP mint + burn 0.30% per year held
  (one round trip a year, charged daily pro rata). Sensitivity: all costs × 1.5.
- Capital per $1 of JLP = 1 + Σβ / 3 (short margin at 3× leverage, in USDC, earning nothing). Daily return on capital = hedged return ÷ that.
- Out-of-sample window: first Monday with 60 days of history and funding data (not before 2024-01-01) .. 2026-10-31. Halves split at the
  midpoint date. Reported: CAGR on capital, worst drawdown, daily volatility, average β, average capital per $1 JLP, and the unhedged JLP and
  basket returns as context.

## Stages and verdicts
- **Stage 1 (kill only; 2026-05-01..2026-10-31):** KILL the prop-like question if the annualised (CAGR) hedged return on capital is < 20%/yr.
  (A true 100%/yr would fall below 20% over six months only with a residual volatility far above any perp-pool token's.)
- **Stage 2 (full window):**
  - **Prop-like PASS** (Jx's target, about $15K/yr on about $15K): CAGR on capital ≥ 100%/yr in **both** halves, ≥ 100% with costs × 1.5,
    and worst drawdown no worse than −25%.
  - **Useful but not prop-like:** CAGR ≥ 15%/yr in both halves, ≥ 15% with costs × 1.5, worst drawdown no worse than −25%.
  - Otherwise **FAIL**.
  If Stage 1 kills, Stage 2 is printed as context only (the data are the same fetch, no extra cost) and the verdict stays KILL.

**Costs.** Free public data only. **Commands.** fetch: Actions `fallback_fetch.yml` job `jlp363`; analysis:
`uv run python -m scripts.jlp_20261123 | tee docs/jx_runs/jlp_20261123.txt` (re-run once; must be identical).

**Honest limits.** A price-based hedge leaves basket-tracking error in the result (it is counted, not removed). DefiLlama daily points are
single snapshots, not closes. JLP deposits are sometimes capped by the pool's AUM limit, so entry is not always possible. Smart-contract and
oracle risk (Solana, Jupiter) and Hyperliquid venue risk are not priced.

# Pendle fixed-rate stablecoin PTs held to maturity, expired markets included (#211) — 2026-11-21

Written and committed before any Pendle market history is fetched (a structure probe of the API runs first; it prints field names only).
Mechanism M25 (docs/IDEAS_SWEEP_20261121.md): buying a principal token (PT) locks a fixed yield until maturity; the counterparty is the
yield-token speculator. Capped downside only if the underlying stablecoin holds its peg — 2025 had depegs inside Pendle markets (e.g. Stream
xUSD, Elixir deUSD), so expired markets must be included.

## Data
Pendle public API (`api-v2.pendle.finance`), all chains it lists: every market whose underlying asset symbol is a USD stablecoin or a
yield-bearing USD stablecoin (symbol list in the script), active and expired, with daily implied APY, TVL/liquidity and maturity; underlying
price at maturity from the Pendle API or DefiLlama coins (`coins.llama.fi`).

## Rule
- First day of each month 2024-11..2026-10: eligible = stable markets with liquidity ≥ $5M that day and ≥ 30 days to maturity. Buy the
  top 3 by implied APY, equal weight, a third of the month's new capital each; hold to maturity (rolling ladder: each month 1/6 of capital is
  deployed, so ~6 monthly cohorts overlap; idle cash earns 0).
- Return of a position = (1 + implied APY)^(days/365) − 1 − 0.1% swap cost − $10 gas on $10,000/6 per cohort leg;
  if the underlying's price at maturity < $0.98, return = underlying price − 1 (loss) instead.
- Annualised return per cohort-month, reported by entry month; halves by entry month.

## Pass
- Stage 1: cohorts entered 2026-05..2026-07 (the latest ones fully matured or marked at current PT value): KILL if mean < 4.0%/yr.
- Stage 2: PASS if mean annualised return ≥ 8.0%/yr for entries in both halves (2024-11..2025-10, 2025-11..2026-10; open positions marked at
  latest PT price), AND no single month below −20%.
Reported: depeg losses hit, $/yr on $10K/$40K, share of entries in markets that later depegged.

Command: `uv run python scripts/pendle_20261121.py | tee docs/jx_runs/pendle_20261121.txt`

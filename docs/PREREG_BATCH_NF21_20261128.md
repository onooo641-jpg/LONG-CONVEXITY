# Batch NF21 (#627–#630): price signals in thin Bittensor subnet pools — pre-registered 2026-11-28, before any NF20 subnet data is analysed

**Why:**
- Subnet "alpha" tokens trade in about 100+ thin constant-product pools that only on-chain retail and subnet teams use.
- No CEX lists most of them, so cross-sectional anomalies (momentum, reversal, flow-chasing, dilution) may survive. That is far less
  likely on large venues.
- Same data as NF20 (`batchnf20_subnets_1d.parquet`, weekly snapshots, addendum 1). The NF20 return model is unchanged:
  - staker yield accrues;
  - constant-product slippage for $1,500 in and out;
  - TAO hedged on HL with funding (NF20 addendum 2);
  - netuid re-use and deregistration count as −100%.

**Desk checks:** as NF20 (G5: buying TAO from Malaysia not verified; staking is a wallet extrinsic).

**Common:**
- **Universe** at each monthly rebalance: subnets with tao_in ≥ 1,000 TAO and ≥ 4 weekly snapshots of history.
- **Holds** run from the first snapshot on or after the 1st of the month to the first snapshot on or after the next 1st.
- Equal weight, 10 subnets per portfolio.
- **Lookback signals** use snapshots up to and including the rebalance snapshot. No future data.

| # | Idea | Rule |
|---|---|---|
| 627 | **Alpha momentum** | the 10 subnets with the highest 4-week alpha price change (in TAO) |
| 628 | **Alpha reversal** | the 10 with the lowest 4-week alpha price change |
| 629 | **TAO inflow chase** | the 10 with the largest 4-week growth in tao_in (net TAO staked into the pool) |
| 630 | **Low dilution** | the 10 with the lowest alpha supply growth (alpha_in + alpha_out) over 4 weeks |

**Split:**
- Stage 1 = holds starting 2025-04..2025-12 (kill only); the first month is lost to the lookback;
- Stage 2 = holds starting 2026-01..2026-10, unseen.

**Stage 1 KILL:** ≥ 6 holds and mean net ≤ 0.

**Stage 2 PASS:** all of
- ≥ 10 monthly holds;
- mean net ≥ 3% per month;
- t ≥ 2;
- positive without the best 3 months;
- positive with slippage × 1.5;
- NF20's yield-model sanity check passes.

**If NF20's Stage 0 data bar is not met, NF21 is not testable.**

**Multiple testing:** four tests on the same data as NF20's four. Only a pass with Stage 2 t ≥ 2.5 goes to the radar forward log.

**Script/output:** `scripts/batch_nf21_20261128.py` → `docs/jx_runs/batch_nf21_20261128.txt`, re-run identical.

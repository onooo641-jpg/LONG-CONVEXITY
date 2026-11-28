# Wick family additions (#519–#520): resting asks above squeeze spikes; volatility-scaled bids — pre-registered 2026-11-28, before running

**Why.** #389 (resting bids under liquidation wicks, Hyperliquid perps) is the only large non-prop survivor, but:
- it loses in crash regimes;
- its per-fill edge fell in 2025;
- its fixed 15% distance almost never fills on calmer coins.

Two untested variants could improve it rather than only enlarge it:
- #492 faded squeezes at the daily close, using liquidation data; no resting-order mirror was ever run.
- No volatility-scaled distance was ever registered.

**Family:** both are family 1 (forced liquidations) and count once toward the goal. Their value is as additions to #389.

**Common rule (as #389).**
- **Data:** daily candles of every Hyperliquid perp (`uncharted_385_candles`); first 30 days after listing excluded.
- **Fill:** only if the day trades ≥ 0.5% through the level. Fill price = the level, or the open if the day opened beyond it.
- **Exit:** at that day's close.
- **Size per fill:** min($1,500, 1% of the day's USD volume); one $15,000 pot per day.
- **Costs:** 0.015% maker in, 0.045% taker out.

| # | Idea | Exact rule | Stage 1 (2023-06..2024-12) KILL if | Stage 2 (2025-01..2026-10) PASS if |
|---|---|---|---|---|
| 519 | **Resting asks above short-squeeze spikes** (forced short covering overshoots, the mirror of #389's payer) | Each day, per perp, a resting limit **sell** at previous close × (1 + X), X = 15% primary (10%, 20%, 30% context). Fill if the day's high ≥ level × 1.005; fill price = the level, or the open if it opened above. Buy back at the close | mean net per fill ≤ 0.3% (≥ 30 fills) | ≥ 30 fills, mean net ≥ 0.3%, t ≥ 2, net ≥ $3,000/yr |
| 520 | **Volatility-scaled bids** (the same forced sellers, on coins too calm for a fixed 15%) | Resting buy at previous close × (1 − X_c). X_c = 4 × σ30, where σ30 is the stdev of the coin's previous 30 daily close-to-close returns, clipped to [5%, 30%]. Otherwise #389 | same | same |

**Also reported:**
- correlation of monthly P&L with #389's (same windows);
- #389 + #519 combined: worst month and $/yr, i.e. whether the mirror offsets #389's crash months;
- profit without the best day.

**Script/output:** `scripts/wick_family_20261128.py` → `docs/jx_runs/wick_family_20261128.txt`, re-run identical.

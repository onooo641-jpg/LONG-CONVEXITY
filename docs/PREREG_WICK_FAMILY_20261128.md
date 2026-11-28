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

## Results (2026-11-28; `docs/jx_runs/wick_family_20261128.txt`, re-run identical)
| | Stage 1 2023-06..2024-12 | Stage 2 2025-01..2026-10 | Verdict |
|---|---|---|---|
| #389 reference (X 15%) | +4.32%/fill (t 18.4, 1,866 fills), $25.6K/yr | +1.33%/fill (t 5.67, 2,484), $14.4K/yr | (reference) |
| **#519 asks above squeeze spikes** (X 15%) | −1.15%/fill (t −5.68) | −0.34%/fill | **KILL**: squeezes keep running; no X level works in Stage 1 |
| **#520 volatility-scaled bids** | +7.64%/fill (t 20.8, 930 fills, 85% win), $15.8K/yr | **+3.92%/fill (t 6.60, 753 fills, 60% win), $6.4K/yr** ($3.8K without the best day) | **PASS** |

- **#520** is a better-quality version of #389 out of sample: about 3× the edge per fill, but fewer fills, so fewer dollars ($6.4K vs
  $14.4K/yr).
  - It is family 1 and below $10K/yr, so it does not count as a new family.
  - It suggests that sizing the bid distance to each coin's volatility holds up better than the fixed 15%.
  - Combining the two (union, or #520's distances replacing #389's) was not tested and needs its own pre-registration.
- **#519** offers no hedge: its monthly P&L correlation with #389 is −0.32 (Stage 1) / +0.25 (Stage 2), and adding it worsens the
  worst month.

## Addendum 1 (2026-11-28, before 2026-12-01): #520 joins the forward paper test
- Radar N10 now also logs #520's paper fills (`wick520_paper.parquet`) alongside #389's (`wick_paper.parquet`).
- It uses the same candles and costs. Size uses the previous day's volume, as N10 does, because the day's own volume is unknown
  until it closes.
- **#520 S2c PASS (fixed now):** 2026-12-01 → 2027-01-26, ≥ 40 fills and mean net per fill ≥ 1.0%. The bar is set above #389's 0.5%,
  because #520's out-of-sample edge was ~3.9%.

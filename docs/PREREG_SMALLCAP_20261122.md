# #320 Small-capacity high-reward pools (non-prop, Topstep-shaped: high %, capped dollars) — 2026-11-22

**Question (Jx, 2026-11-22: can a non-prop mechanism reach ≥ 50%/yr?).** Large capital cannot enter pools of $100K–$2M without diluting the
reward, so high incentive yields may survive there for small positions. Earlier radar filters required TVL ≥ $1–20M, so this region is untested.
**Data.** DefiLlama /pools (current list) + /chart/{pool} daily history; reward-token and pool-token prices from DefiLlama coins
(per-coin requests). Job `smallcap`.
**Universe.** Pools with TVL between $100K and $2M on the selection day and (apyBase + apyReward) ≥ 50%, any chain and asset.
**Rule.** Monthly (from 2025-11): hold the 10 pools with the highest trailing-30-day mean APY, $1,500 each ($15K total, ≤ 1.5% of any pool's TVL).
Return per pool per day = apyBase/365 + apyReward/365 × (reward-token price change factor since entry, i.e. rewards valued at the current price)
− impermanent-loss proxy for non-stable pools (|daily pool-token price change| × 0.5) + pool-token price change for single-asset non-stable pools.
Collapse: TVL falls > 70% within 7 days → −50% on that slot. Costs $15 per entry and exit (gas + swap) per slot.
**Survivorship.** The current list misses dead pools. Correction: any pool whose chart stops before the month ends is booked at −50% at its last date.
**Stage 1 (kill-only).** 2026-08..10: **KILL if < 25%/yr** on capital.
**Stage 2.** 2025-11..2026-10 split at 2026-05: **PASS = both halves ≥ 50%/yr and ≥ 30%/yr with costs ×2**. Also reported: dollars per year on
$15K (the capacity is the point: high %, small dollars).
**Stage 0.** DeFi front-ends (no KYC); Malaysia access assumed (not geoblocked as far as known). F4 (capped downside) fails for non-stable pools,
so a pass on non-stable pools would be reported as a near-miss. Stable-only results are reported separately and can pass.
Command: `uv run python -m scripts.smallcap_20261122 | tee docs/jx_runs/smallcap_20261122.txt`.

## Addendum 1 (2026-11-22, written before any #320 data exists in the repo): monthly consistency + #321
Jx asked for ≥ 50%/yr **consistently by month**. Added to the Stage 2 PASS rule (stricter only; nothing loosened):
**every month of 2025-11..2026-10 ≥ 0%, and at least 10 of 12 months ≥ 3.4%** (3.4%/month compounds to ≈ 50%/yr).
**#321 small-budget reward campaigns (Merkl).** Same rule and pass criteria as #320, applied to Merkl opportunities with TVL $100K–$2M:
APR = daily reward value × 365 / TVL, rewards valued at the current reward-token price. Data: Merkl public API (job `merkl`). If no daily
history is available, Stage 1 uses whatever history the API returns. With under 90 days of history it is not testable.

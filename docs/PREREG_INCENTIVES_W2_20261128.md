# Radar week 2: Ember USDC concentrated-liquidity vault (Sui), CANDIDATES #588. Pre-registered 2026-11-28, before its chart history is looked at

**Selection:** taken mechanically from the radar test queue, which ranks by 90-day realised yield
(`data/radar/latest_summary.md`, 2026-11-28, addendum 3).
- **Queue:**
  1. Ember (Sui) USDC, 15.85%/yr over 90 days, TVL $1.31M, pool `0a3c5663-73bd-4d8a-bdcc-5e529a8b741d`;
  2. Bluefin USDSUI-USDC (already tested as #203, skipped);
  3. Dolomite USD1 (already tested as #202, skipped).
- **Only #588 is new.** The queue's 90-day figure is the only number seen before this pre-registration.

**Template:** identical to `docs/PREREG_INCENTIVES_W1_20261121.md`.
- **Same question:** net yield more than T-bill (4.0%, assumed) + 8 = **12.0%/yr**, in both halves, with no loss event.
- **Same data:** DefiLlama `yields.llama.fi/chart/<pool>` via `data/radar/charts.parquet`, last 730 days at most.
- **Same rule:**
  - apyBase + apyReward × 0.90 × TVL / (TVL + $10K) − 26 tx/yr × $0.10 (Sui);
  - loss-event proxy: a 7-day TVL fall > 50%.
- **Same stages:**
  - Stage 0, desk check;
  - Stage 1: last 60 days, KILL if < 8.0%/yr;
  - Stage 2: PASS only if history ≥ 180 days, both halves ≥ 12.0%/yr, and no loss event.

**Stage 0 (desk, before data):**
- Ember is a Sui vault protocol that runs concentrated-liquidity positions for USDC depositors. The reward is a protocol programme
  (DefiLlama lists reward tokens).
- The deposit is a permissionless contract (assumed from the protocol type, not verified on-chain).
- Malaysia: unverified-onchain.
- **Price exposure:** DefiLlama marks the pool as stable. A concentrated-liquidity vault can still hold a non-USD asset if its range
  pairs USDC with something else. The pair is not visible in the radar row, so this is recorded as **unverified F4**. A PASS would go to
  Jx only once the vault's strategy page is read.
- **Capacity context:** $15K × 15.85% ≈ $2.4K/yr at best, below one Topstep slot (~$3.7K/yr). A PASS would still not be flagged unless it
  also beats that.

**Command:**
- `uv run python scripts/incentives_w2_20261128.py | tee docs/jx_runs/incentives_w2_20261128.txt`;
- the script is the W1 script with this setup only.

## Results (2026-11-28, `docs/jx_runs/incentives_w2_20261128.txt`, re-run identical): FAIL
- **History:** 202 days from 2026-05-11. Mean base yield 7.48%, mean reward 6.37%. Worst 7-day TVL ratio 0.74 (no loss event).
- **Stage 1** (last 60 days): 16.31%/yr, so the test continued.
- **Stage 2: half 1 10.94%/yr, below the 12.0% bar; half 2 15.32%/yr.** Verdict FAIL.
- **Context:** $1,313/yr on $10K, against $4,097/yr for one Topstep slot. Even a pass would not have been flagged.

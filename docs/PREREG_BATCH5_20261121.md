# Batch 5: hedged resource/revenue staking (#228) and hedged native L1 staking (#229) — 2026-11-21

Written and committed before the data below is fetched. Staged per CLAUDE.md + PREREG_RADAR addendum 7. Bar ≥ 8.0%/yr on capital in both halves.
- **#228 hedged resource / revenue staking.** Tron energy rental (TRX staked to rent "energy" that every USDT transfer on Tron needs; DefiLlama
  `tr-energy`) and SKY staking rewards (`sky-lending` SKY pools), each hedged with a 3× short of TRX / SKY on Hyperliquid.
  Hedged yield = pool yield (apyBase + 0.9 × apyReward) + HL funding received by the short, ÷ 1.333.
- **#229 hedged native L1 staking.** Stake ATOM, TIA, INJ, SEI, DYDX (Cosmos-SDK chains; APR = inflation × (1 − community tax) / bonded ratio
  × (1 − 5% validator commission), from each chain's public LCD) or APT/NEAR/DOT (no free history → only if an API answers), hedged with an HL
  short. Unbonding periods (≈ 21 days) are kept hedged; slashing not modelled.
- **Stage 0.5** (needs a small fetch: last 90 days of HL funding for TRX, SKY, ATOM, TIA, INJ, DOT, NEAR, APT, SEI, DYDX; current staking APR;
  current DefiLlama pool yields): ceiling = current yield + 90-day funding, ÷ 1.333 → KILL any coin < 8%; mechanism killed if no coin ≥ 8%.
- **Stage 1** (survivors only): last 90 days realised hedged yield < 4%/yr → KILL. **Stage 2**: full history from 2024-11 if available;
  PASS ≥ 8%/yr both halves (for #229 only if historical staking APR is available; otherwise the verdict is "not testable beyond Stage 1").
Malaysia: native staking / permissionless; HL unverified. Command: `uv run python scripts/batch5_20261121.py | tee docs/jx_runs/batch5_20261121.txt`

## Results (2026-11-21; `docs/jx_runs/batch5_20261121.txt`, `docs/jx_runs/sky_stage2_20261121.txt`; re-runs identical)
- #228 TRX energy rental hedged: Stage 0.5 ceiling −1.4% (HL TRX shorts pay 13.2%/yr) → KILL. SKY staking hedged: one pool survived Stage 1
  (15.4%); Stage 2: only **112 days** of history (from 2026-07-11) → FAIL on the ≥ 180-day rule, halves 12.9% / 16.9% (pool yield 5.4% + SKY short
  funding 14.4%). Near-miss: re-test when 180 days exist (≈ 2027-01-07). The other SKY pool had no overlapping data.
- #229 hedged native staking: ATOM ceiling 4.9% (shorts pay 8.1%) → KILL; INJ ceiling 12.1% (APR 8.7% + 7.4%) but no free APR history →
  not testable beyond Stage 0.5; TIA/SEI/DYDX inflation not exposed by the standard endpoint; APT/NEAR/DOT no APR source → not testable.

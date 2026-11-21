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

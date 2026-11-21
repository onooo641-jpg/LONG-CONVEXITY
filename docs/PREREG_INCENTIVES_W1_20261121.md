# Radar week 1: three stablecoin incentive setups — 2026-11-21 (CANDIDATES #201, #202, #203)

Written and committed **before** any chart history for these pools was fetched or looked at. Chosen mechanically by the radar
(`docs/PREREG_RADAR_20261121.md` test queue): the top three venue-level setups by reward APR among rows with all five filter parts
verified (baseline run 44885195094). Malaysia status for all three: `unverified-onchain` (Stage 0 below).

| # | setup | pools (DefiLlama pool id) | reward APR at selection |
|---|---|---|---|
| 201 | Lista Lending, stablecoin supply, Ethereum | USDC `005bdeab-17c3-4561-961d-fef74f4ca6f9`, USDT `5e953c59-150a-4e1a-a117-3db74c7c8591` | 10.6%, 4.7% |
| 202 | Dolomite, stablecoin supply, Ethereum | USDC `20e45c3e-7de7-4d34-89e7-20858ecdf252`, USD1 `86e18974-35ca-4948-9c82-694facf9d082` | 7.7%, 6.0% |
| 203 | Bluefin Spot, USDSUI-USDC 0.01% LP, Sui | `e3887972-24e6-45a9-8ef5-bcc22b6b5739` | 6.6% |

## Question
Does a $10,000 stablecoin position in the setup earn **more than T-bill + 8%/yr** after costs, in both halves of its history, without a
loss event? (The bar is the template in the radar pre-registration. T-bill is taken as **4.0%/yr: assumed**, not looked up, so the bar is
**12.0%/yr net**.)

## Data
DefiLlama `yields.llama.fi/chart/<pool>` daily history (apy, apyBase, apyReward, tvlUsd), collected by the radar into
`data/radar/charts.parquet` (pools listed in `docs/radar/test_pools.csv`). Window: all available history, capped at the last 730 days.

## Exact rule
Per pool and day: net yield (annualised) = apyBase + apyReward × 0.90 × TVL / (TVL + $10,000) − cost.
- 0.90 = haircut for selling the reward token (slippage and price fall between accrual and sale): **assumed**.
- TVL / (TVL + $10,000) = dilution of the reward by our own deposit.
- cost: 26 transactions a year (enter, exit, claim + swap twice a month) × $5 on Ethereum ($130/yr = 1.3%/yr on $10K), × $0.10 on Sui
  (≈0.03%/yr): **assumed**.
- Setup daily yield = equal-weight mean of its pools on days they have data.
- Loss-event proxy: any 7-day TVL fall > 50% in any of the setup's pools.

## Stages (kill early, never pass early)
- **Stage 0, desk check (minutes):** protocol still live; the reward is a protocol/foundation programme, not a one-off; deposit is
  permissionless (no KYC/geofence on the contract); Malaysia: no known prohibition on supplying stablecoins to a DeFi contract
  (front-end geoblock not checkable from here; recorded as unverified). Kill if the programme has ended or the deposit is not permissionless.
- **Stage 1, pilot (last 60 days only): KILL if the setup's mean net yield < 8.0%/yr** (4 points below the bar, so noise cannot kill a
  setup that really earns 12%).
- **Stage 2, full test:** PASS only if (a) history ≥ 180 days, (b) mean net yield ≥ 12.0%/yr in **both** halves of the window, and
  (c) no loss-event proxy hit. Otherwise FAIL (reason recorded).
Also reported, not used for pass/fail: the same at $50,000; mean apyReward share of total yield; $ per year on $10K vs Topstep 50K
recycling ($4,097/yr per slot, at most ~$3.5K at risk).

## Not measured (stated now)
Smart-contract hack and stablecoin depeg risk are not in the APY data (a depeg can wipe out years of yield: #46 UST). A PASS here is
therefore necessary, not sufficient; it would go to Jx only together with that caveat.

Command: `uv run python scripts/incentives_w1_20261121.py | tee docs/jx_runs/incentives_w1_20261121.txt`

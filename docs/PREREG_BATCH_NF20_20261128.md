# Batch NF20 (#623–#626): Bittensor subnet staking (dTAO), protocol emissions as the subsidy — pre-registered 2026-11-28, before any data is fetched

**Why:**
- **New family: someone else pays.** Since dTAO (2025-02), each Bittensor subnet has a thin AMM pool (TAO ↔ subnet "alpha").
  - Holders who stake TAO into a subnet receive part of that subnet's block emissions in alpha.
  - The payer is protocol inflation, through subnet owners and miners selling emissions.
  - The pools are thin, retail and permissionless.
- **Question:** is the TAO-hedged total return (alpha price change + emissions received) large after slippage? Or does emission selling
  push alpha down as fast as it accrues?
- **Untested here.** HYPE/LST hedged staking (R5) is the nearest family; it was 9–23%/yr.

**Stage 0 (desk + data probe, this batch's first step):**
- **G5:**
  - TAO is self-custodial. Staking is a wallet extrinsic with no KYC.
  - Buying TAO from Malaysia is **not verified** (Malaysian SC-registered exchanges may not list it; a DEX route via wrapped TAO is
    possible).
  - The TAO hedge is the HL `TAO` perp.
- **G6:** the yields are published on dashboards, so crowding is likely. What is unknown is the net of alpha dilution.
- **Data probe (job `ubatchnf20`):**
  - Query the public Bittensor archive node for the runtime API `SubnetInfoRuntimeApi.get_all_dynamic_info` once a day at 00:00 UTC,
    from 2025-03-01 to 2026-11-25. Blocks are found by timestamp, about 7,200 per day.
  - Store per subnet: netuid, block, tao_in, alpha_in, alpha_out, alpha_out_emission (per block), price (= tao_in / alpha_in),
    registration block.
  - Decoding uses `substrate-interface`, installed at job runtime, not added to the project.
  - HL `TAO` daily candles and funding come from existing files or are refetched.
- **If the probe cannot return decoded history for ≥ 200 days and ≥ 30 subnets, NF20 stops as "not testable"** and the next batch moves
  on. A parse or unit fix may be added by addendum **before** any return is computed.

**Return model (if data exists):**
- **Staker yield per day (assumption, stated before data):** alpha_out_emission × 7,200 × 0.41 (the validator/staker share) × 0.82
  (after an 18% validator take), divided by alpha_out.
  - Sanity check: the median yield for SN1 and SN64 is compared with a published APY snapshot.
  - If off by > 2× the model is reported as unreliable and no PASS is possible.
- **Holding-period return in TAO** = (alpha held × (1 + accrued yield) × price_end) / (alpha bought × price_start) − 1.
- **Slippage:** constant-product price impact for a $1,500 position in, and again out, against that day's pool reserves.
- **USD return** = the TAO return, since the TAO price is hedged with an HL short, minus HL funding paid over the hold.

| # | Idea | Rule |
|---|---|---|
| 623 | **Top-10 subnets by emission, monthly** | on the 1st of each month, stake equally into the 10 subnets with the largest alpha_out_emission × price; hold 1 month; TAO hedged |
| 624 | **New subnets, first 90 days** | stake into each subnet 7 days after registration (with tao_in ≥ 1,000 TAO); hold 90 days or until deregistration (a deregistered subnet's value counts as what the pool paid out, otherwise 0) |
| 625 | **Highest model yield decile, monthly** | on the 1st of each month, the decile of subnets (tao_in ≥ 1,000 TAO) with the highest model staker yield; hold 1 month |
| 626 | **Root / largest-pool control** | the 5 subnets with the largest tao_in; hold 1 month (low-subsidy control) |

**Split:**
- Stage 1 = holds starting 2025-03..2025-12 (kill only);
- Stage 2 = holds starting 2026-01..2026-10, unseen.

**Stage 1 KILL:** ≥ 10 holds and mean net ≤ 0.

**Stage 2 PASS:** all of
- ≥ 10 monthly holds (#623, #625, #626) or ≥ 20 subnet holds (#624);
- mean net ≥ 3% per month (about 40%+/yr; the bar is set for >100%/yr on small capital);
- t ≥ 2;
- positive without the best 3 holds;
- positive with slippage × 1.5;
- the yield-model sanity check passes.

**Multiple testing:** four tests. Only a pass with Stage 2 t ≥ 2.5 goes to the radar forward log.

**Script/output:** `scripts/batch_nf20_20261128.py` → `docs/jx_runs/batch_nf20_20261128.txt`, re-run identical.

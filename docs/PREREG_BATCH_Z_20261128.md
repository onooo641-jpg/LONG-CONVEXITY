# Batch Z (#534): points-farming funding subsidies — #208's rule on Aster and Lighter — pre-registered 2026-11-28, before data are fetched

**Desk checks:**
- **G5:** funding is paid to whoever holds the other side; a small account shorting the high-funding venue receives it directly.
- **G6:** the payer is non-economic (airdrop-points farmers who keep leaning long regardless of funding), and per-venue capacity is too
  small for large funds.
- #208 (HL/dYdX/Aevo, passed after the fee fix: 20.3% / 11.9% on capital) never included the points venues. This is the same family
  (#208 / R1); a pass adds capacity, not a new family.

**Venues:** Hyperliquid (HL), Aster, Lighter; all permissionless DEX perps.

**Rule: #208's exactly** (`docs/PREREG_FUNDGAP_20261121.md` with the fee fix).
- Daily signal = mean hourly funding over the last 24 h on venue A minus venue B, annualised.
- **Open** at |signal| ≥ 15%/yr: short the higher-funding venue, long the lower. **Close** when the signal changes sign.
- **Costs:** 0.05% per leg per side.
- **Capital:** 3× per leg; at most 5 positions.
- **Coins:** #208's 12 (BTC ETH SOL XRP DOGE AVAX LINK SUI ARB OP LTC BNB) where both venues list them.
- **Pairs:** HL–Aster, HL–Lighter, Aster–Lighter, pooled in one portfolio (as #208 pooled its three).
- **Funding normalisation:**
  - Aster's per-interval rate is spread over its interval, as #208 did for Gate.
  - Lighter's API rate is taken as per hour if the API returns hourly points.
- **Window:** from the first hour all of a pair's venues have data to 2026-10-31.
  - **Halves** = split at the midpoint of the pooled window, computed by the script.
  - **Stage 1** = the last 3 months.

**Pass (as #208):**
- Stage 1 KILL if < 4%/yr on capital.
- Stage 2 PASS if ≥ 8%/yr on capital in **both halves**, and ≥ 20 positions opened per half or invested ≥ 50% of days per half.
- **Also, because there are 5 variants of this family now:** the second half must still clear 8% with fees × 1.5.

**If Lighter's history cannot be fetched**, the test runs HL–Aster alone with the same rule, and says so.

**Not modelled** (as #208): price gaps between venues at entry and exit, both legs filling together, moving collateral, venue risk.

**Data job:** `ubatchz`, Aster `fapi/v1/fundingRate` and Lighter funding history, coins above.

**Script/output:** `scripts/batch_z_20261128.py` → `docs/jx_runs/batch_z_20261128.txt`, re-run identical.

## Addendum 1 (2026-11-28, after the first fetch, before any position or P&L was computed)
- **Lighter units:** the first fetch stored Lighter rates with a size-dependent heuristic. A unit check (BTC median raw value 0.0012,
  against Hyperliquid's 1.25e-5 per hour as a fraction) shows the API reports **percent per hour**.
- Lighter is re-fetched raw (`batchz_lighter_raw.parquet`, with the API's `direction` field), with HTTP 429 backoff. Three coins
  (ARB, LTC, BNB) were refused on the first run.
- **Rule for the analysis:** Lighter rate = raw / 100 per hour; the sign follows `direction` (short = shorts pay longs = negative).
- Aster: per-8-hour fraction (median 0.0001, the usual 0.01%), spread over its interval as registered.
- Nothing else changes.

## Result (2026-11-28; `docs/jx_runs/batch_z_20261128.txt`, re-run identical): **FAIL**
- **Pooled HL/Aster/Lighter (window 2024-10-30..2026-10-31):**
  - Stage 1 (last 3 months): 3.75%/yr, below the 4% kill line.
  - Halves: 14.60% / **4.12%** on capital.
  - Second half with fees × 1.5: −0.61%.
  - About $3.7K/yr on $40K.
- **Pairs, second half:** HL–Aster 1.52%, HL–Lighter −0.57%, Aster–Lighter 0.63%.
- **Units check** as in addendum 1: Lighter BTC median 1.20e-05 per hour, against HL 1.25e-05.
- **Conclusion:** the points-farming venues did not carry a lasting funding subsidy. Gaps were wide in 2024–25 and closed in 2025–26,
  the same decay as #208's original pairs.

**Process note:** a mis-scoped edit to `scripts/fetch_uncharted.py` (commit dede428f) deleted 1,576 lines. It was caught when the
Actions job failed to import, restored from the previous commit in c634b1bd, and the change was re-applied inside `job_ubatchz` only.
No other job ran in between.

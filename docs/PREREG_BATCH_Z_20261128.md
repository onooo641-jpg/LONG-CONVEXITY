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

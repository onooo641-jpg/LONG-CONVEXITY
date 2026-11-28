# Batch NF27 (#651–#654): funding snapshot timing on Aster — hold the receiving side across settlement only — pre-registered 2026-11-28, before any minute data is fetched

**Why:**
- Jx asked for loopholes. This one is allowed by the venue's own rules.
- **Aster** (Binance-style perps) charges funding to positions held **at the settlement time** (within 15 seconds, per Aster's docs),
  over 4- or 8-hour intervals.
- A position opened just before settlement and closed just after collects **the full interval's funding** while carrying price risk for
  only minutes.
- The question is whether the price moves against the receiving side around settlement, because everyone knows the rate in advance.
- **GRVT** accrues funding into a per-minute index (its help centre), so it has no snapshot effect and is excluded.

**Desk checks:**
- **G5:** Aster is a DEX; no KYC.
- **Bot policy:** API trading is allowed.
- **Fees:** taker about 0.035% per side (Aster docs; third-party). Slippage on thin alts is added as one extra 0.05% per side.
- **No manipulation:** the trade only holds through settlement; it does not try to move the rate.

**Data (job `ubatchnf27`):**
- Aster `exchangeInfo` (all perps); `fundingRate` history per symbol from 2025-01-01 (paged).
- For each settlement with \|rate\| ≥ 0.10% per interval: **1-minute klines** from 35 minutes before to 35 minutes after.
- **Files:** `batchnf27_funding.parquet`, `batchnf27_minutes.parquet`.

**Rule:**
- **Settlement** t = the funding timestamp, floored to the minute. **Receiving side** = short if rate > 0, long if rate < 0.
- **Entry** at the close of the 1-minute bar ending W minutes before t. **Exit** at the close of the bar ending W minutes after t.
- Both bars must have volume > 0, otherwise the trade is dropped.
- **Return** = \|rate\| + side × (exit/entry − 1) − 2 × (0.035% + 0.05%).
- **Size** = min($1,500, 1% of the USD volume of the 2W minutes around t).
- Unhedged, because the window is minutes; HL 1-minute history is not available that far back.

| # | Rule |
|---|---|
| 651 | \|rate\| ≥ 0.10%, W = 1 minute |
| 652 | \|rate\| ≥ 0.25%, W = 1 minute |
| 653 | \|rate\| ≥ 0.10%, W = 5 minutes |
| 654 | \|rate\| ≥ 0.10%, W = 30 minutes (does the price drift into or out of settlement?) |

**Split:** Stage 1 = settlements 2025-01-01..2025-12-31 (kill only); Stage 2 = 2026-01-01..2026-11-25, unseen.

**Stage 1 KILL:** ≥ 30 trades and mean ≤ 0.

**Stage 2 PASS:** all of
- ≥ 30 trades;
- mean ≥ 0.10% per trade (one trade is minutes of exposure, so a smaller per-trade bar is used, with ≥ $3,000/yr at the registered
  size);
- t ≥ 2;
- sum positive without the 3 best trades;
- mean > 0 with costs × 1.5;
- no single symbol > 40% of the profit.

**Multiple testing:** four tests. Only a pass with Stage 2 t ≥ 2.5 goes to the radar forward log.

**Script/output:** `scripts/batch_nf27_20261128.py` → `docs/jx_runs/batch_nf27_20261128.txt`, re-run identical.

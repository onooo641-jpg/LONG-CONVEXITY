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

## Result (2026-11-28; `docs/jx_runs/batch_nf27_20261128.txt`, re-run identical): **0 of 4**
- **Data:**
  - Aster funding: 2,219,680 rows on 636 perps. One symbol with a non-ASCII name failed (UnicodeEncodeError).
  - 25,323 settlements with \|rate\| ≥ 0.10%. 1-minute bars cover 8,790 of them; the job's time budget ended first. That is enough for
    kill decisions.

| # | Rule | Stage 1 (2025) | Stage 2 (2026) | Funding / price leg (Stage 2) | Verdict |
|---|---|---|---|---|---|
| 651 | ≥ 0.10%, ±1 min | n 2,483, −0.20% (t −7.37) | n 9,303, −0.09% | +0.34% / −0.25% | KILL (Stage 1) |
| 652 | ≥ 0.25%, ±1 min | n 1,015, −0.21% | n 3,793, −0.12% | +0.60% / −0.54% | KILL (Stage 1) |
| 653 | ≥ 0.10%, ±5 min | n 2,341, −0.25% | n 8,400, −0.44% | +0.34% / −0.61% | KILL (Stage 1) |
| 654 | ≥ 0.10%, ±30 min | n 2,088, +0.13% (t 0.69) | n 6,783, −0.24% | +0.36% / −0.43% | FAIL |

**Reading:**
- The snapshot is priced. In the minutes around settlement the price moves against the receiving side by about the funding paid (it
  scales with the rate: about −0.25% at 0.10%, about −0.54% at 0.25%).
- After fees, every window loses. The loophole exists in the rules, but the market has already closed it.

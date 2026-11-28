# Batch NF15 (#598–#602): hourly forced selling on thin perp venues — pre-registered 2026-11-28, before any hourly venue data is fetched

**Why:**
- #569 (hourly cascade reversal) passed on Hyperliquid out of sample.
- NF14 showed that thin venues' daily edges fade as the venues mature, and that their stale no-trade prints fake signals.
- This batch tests the hourly mechanism where local liquidations hit thin books: Backpack, Extended, Pacifica and Apex Omni (the
  venues that answered in NF14).
- Idea #602 isolates the **venue-local** cascade, the one an HL trader cannot see, with HL as the hedge.

**Desk checks:** G5/G6 as in NF14 (Backpack needs KYC, country list unverified). Hourly holds, small size.

**Data (job `ubatchnf15`, GitHub Actions):**
- Hourly candles, 2026-03-01..2026-11-25, for every perp on Backpack, Extended and Pacifica, and Apex's 40 markets with the highest
  NF14 daily volume.
- HL hourly: `wickscale_hl_1h.parquet` (from 2026-04-24).
- Bluefin is skipped: 8 markets only.

**Executable-bar filter (from NF14; applies to every idea):**
- An entry needs that hour to be a traded bar: high > low, and USD volume ≥ $20,000.
- The exit hour must have USD volume > 0, otherwise the next traded hour's close is used, up to 4 more hours. If none, the trade is
  dropped.

**Rules:**
- **σh** = stdev of the market's previous 168 hourly close-to-close returns (≥ 100 non-missing).
- **Size** = min($1,500, 1% of the hour's USD volume).
- One open trade per market per idea.
- **Costs:** 0.02% + 0.05% per round trip (×1.5 stress reported). #602 pays two round trips.

| # | Idea | Rule |
|---|---|---|
| 598 | #569 on **Backpack** | hour return ≤ −5σh → buy at that hour's close, sell 4 hours later |
| 599 | #569 on **Extended** | same |
| 600 | #569 on **Pacifica** | same |
| 601 | #569 on **Apex Omni** (40 largest) | same |
| 602 | **Venue-local cascade, hedged** (all four venues) | venue hour return ≤ −5σh **and** HL same coin, same hour > −1.5σh(HL) → buy venue + short HL at the hour's close; exit both 4 hours later. Coins matched by NF14's name rule and unit check (0.95..1.05 median price ratio) |

**Split** (as NF9): Stage 1 = to 2026-08-15 (kill only); Stage 2 = 2026-08-16..2026-11-25, unseen.
- For #598–#601, Stage 1 also uses March–April data. For #602 it starts 2026-04-24, when HL hourly data begins.

**Stage 1 KILL:** ≥ 30 trades and mean net ≤ 0.

**Stage 2 PASS:** all of
- ≥ 30 trades;
- mean net ≥ 0.3%;
- t ≥ 2;
- sum positive without the 3 best trades;
- mean > 0 with costs × 1.5.

**Multiple testing:** five tests of one family. Only a pass with Stage 2 t ≥ 2.5 goes to the radar forward log.

**Script/output:** `scripts/batch_nf15_20261128.py` → `docs/jx_runs/batch_nf15_20261128.txt`, re-run identical.

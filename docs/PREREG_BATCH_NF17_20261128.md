# Batch NF17 (#610–#613): thin-venue dislocations against Hyperliquid, hourly, hedged — pre-registered 2026-11-28, before any NF15 hourly venue data or NF17 funding data has been looked at

**Why:**
- Thin perp venues (Backpack, Extended, Pacifica, Apex Omni) have shallow books and their own retail flow.
- When their price or funding moves away from Hyperliquid's, a small trader can take the other side **with HL as the hedge**. The
  market risk then cancels and only the local gap is kept.
- #597 (daily venue discount) printed a PASS made of stale prints. This batch uses hourly traded bars only (the NF14 lesson) and four
  distinct triggers.
- Jx (2026-11-28): stay in thin, retail, permissionless venues.

**Desk checks:**
- **G5:** as NF14/NF15; Backpack needs KYC, the others are wallet-based, country lists unverified.
- **G6:** the venues are small. Large arbitrage desks may already link them to HL, and that is what the test measures.

**Data:**
- **Hourly candles:** NF15's `batchnf15_{backpack,extended,pacifica,apex}_1h.parquet` (2026-03-01..2026-11-25), and HL
  `wickscale_hl_1h.parquet` (from 2026-04-24).
- **Funding (job `ubatchnf17`):** hourly-or-interval funding history, 2026-03-01..2026-11-26, for every perp on Backpack, Extended and
  Pacifica, and HL `fundingHistory` for every HL coin that one of them also lists.
  - The endpoints are unverified from this sandbox; raw first replies go to `batchnf17_probe.json`.
  - **Units:** each venue's rate is divided by its settlement interval (from timestamp gaps, as Batch Z did for Aster) to get a rate
    per hour. A unit check (BTC median per hour against HL's) may correct a scale or sign by addendum **before** the analysis.

**Common rules:**
- **Matching:** venue markets are matched to HL coins by NF14's `norm()` and kept only if the median venue/HL price ratio is in
  0.95..1.05 (NF14 addendum 1).
- **Traded bar:** the entry hour needs high > low and venue USD volume ≥ $20,000, and an HL bar in the same hour.
- **Exit:** as NF15, the venue close 4 hours later (next traded hour up to +8h). The HL leg exits at its close in the same hour as the
  venue exit.
- **Size** = min($1,500, 1% of the venue hour's USD volume).
- **Costs:** two legs × 0.07% per round trip (×1.5 stress reported). One open trade per venue market per idea.
- **Hedged return** = direction × (venue leg − HL leg) − costs.

| # | Idea | Rule |
|---|---|---|
| 610 | **New-listing dislocation** | a venue market whose first candle is ≥ 2026-04-25 (so HL data exists, and it is not a market that predates the data) and whose coin HL already lists. During its first 72 hours: when \|venue close / HL close − 1\| ≥ 2% on a traded bar, trade toward HL (long venue / short HL if the venue is cheap, the reverse if rich) and exit after 4 hours |
| 611 | **Hourly gap convergence** (all other hours) | same trigger at ≥ 1.5%, any market outside its first 72 hours; trade toward HL; exit after 4 hours |
| 612 | **Venue-local pump fade** | venue hour return ≥ +5σh (NF15's σh) **and** HL same coin, same hour < +1.5σh(HL) → short venue / long HL at the closes; exit after 4 hours (the mirror of #602) |
| 613 | **Venue-local funding spike** | at an hour's close: the venue's per-hour funding, annualised, has \|rate\| ≥ 100%/yr, and the venue rate minus HL's same-hour rate is ≥ 100%/yr in the same direction → take the receiving side on the venue and hedge on HL. Hold 24 hours. Return = funding gap received over the 24 hours + both price legs − 2 legs × 0.07% |

**Split** (as NF15): Stage 1 = data start..2026-08-15 (kill only); Stage 2 = 2026-08-16..2026-11-25, unseen.

**Stage 1 KILL:** ≥ 30 trades and mean net ≤ 0.

**Stage 2 PASS:** all of
- ≥ 30 trades;
- mean net ≥ 0.3%;
- t ≥ 2;
- sum positive without the 3 best trades;
- mean > 0 with costs × 1.5;
- the stale-print check: passing trades inspected for flat or near-zero-volume bars on **either** leg, and for one market
  dominating. If that is what drives the PASS, it is recorded as invalid.

**Multiple testing:** four tests; NF14–NF16 already ran many venue tests. Only a pass with Stage 2 t ≥ 2.5 goes to the radar forward
log.

**Not modelled:**
- the two legs filling together;
- moving collateral between venues;
- venue failure.

**Script/output:** `scripts/batch_nf17_20261128.py` → `docs/jx_runs/batch_nf17_20261128.txt`, re-run identical.

## Result (2026-11-28; `docs/jx_runs/batch_nf17_20261128.txt`, re-run identical): **0 of 4 valid**
- **Data:**
  - Funding: 3,332,485 rows. Backpack, Extended and Pacifica settle hourly, and their base rate is 0.0000125 per hour, the same as HL.
  - Unit check, BTC median per hour: HL 1.15e-5, Backpack 1.25e-5, Extended 1.30e-5, Pacifica 1.25e-5. No addendum was needed.
  - HL: 142 coins; a few HTTP 502s.

| # | Idea | Stage 1 | Stage 2 | Verdict |
|---|---|---|---|---|
| 610 | new-listing dislocation | no trades | n 1 | FAIL (too few) |
| 611 | hourly gap convergence | n 39, +2.18% | n 131, **+1.67% (t 12.09)**, $4,619/yr | printed PASS → **invalid** (below) |
| 612 | venue-local pump fade | n 6, +0.05% | n 9, +0.44% | FAIL (too few) |
| 613 | venue-local funding spike | n 473, +0.04% | n 323, +0.04% | FAIL (gap received +0.12%; costs eat it) |

**#611 stale-print check** (`scripts/batch_nf17_diag_20261128.py` → `docs/jx_runs/batch_nf17_diag_20261128.txt`, re-run identical):
- **Entering one hour later** (the venue traded at h+1): +1.67% → **−0.07% (t −0.57)**, n 122 of 131. Every venue is about 0:
  Apex +0.04%, Backpack −0.02%, Extended −0.24%.
- **The gap closes within the hour:** median |gap| 2.11% → 0.57%; only 42% are still ≥ 0.5% the same way.
- **Entry-hour volume:** median $34K, so these are traded bars, but the venue's hourly close is a stale last trade relative to HL's.
- **Recorded invalid**, the same as NF16 #603 and NF19. These gaps cannot be captured with hourly data.

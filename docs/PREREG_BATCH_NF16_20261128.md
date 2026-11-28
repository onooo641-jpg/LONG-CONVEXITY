# Batch NF16 (#603–#609): duplicate thin books on Hyperliquid spot, and four untested thin perp venues — pre-registered 2026-11-28, before any of this data is fetched

**Why:**
- Jx (2026-11-28): stay in thin, retail, permissionless venues; no national equity markets.
- **Hyperliquid spot** now lists the same token in several thin books: HYPE, UBTC, UETH, UXPL, FXRP, KHYPE and others are quoted in
  USDC and also in USDH, USDT0 or USDE. That is 13 bases with ≥ 2 books (counted from pair labels only; no prices were looked at).
  - A seller who dumps into the thin second book cannot be followed there by large market makers at size. The question is whether
    that gap pays after spot fees. Not tested before: #426 was spot vs perp carry, and #429 was stablecoin depegs on large venues.
- The **stablecoin books** on HL spot (USDH, USDT0, USDE, USDXL and others against USDC) are thin. Buying a dip and waiting for par
  is the retail version of a peg-keeper.
- **GRVT, Nado, Ethereal and Hibachi** are perp DEXes launched in 2025 and never tested here. The #520 wick rule and the #536
  first-30-days rule are applied to them unchanged.

**Desk checks (Stage 0):**
- **G5:** HL spot needs no KYC. GRVT and Hibachi are self-custodial with a wallet sign-in; Nado (Ink chain) and Ethereal likewise.
  Country lists are not verified; this is a data test first.
- **G6:** the HL spot second books are new, from 2025. None of the four perp venues has a published edge study we know of.
- Bot policy: all four venues publish trading APIs, and HL allows API trading.

**Data (job `ubatchnf16`, GitHub Actions):**
- **HL spot:** `spotMeta`, then hourly candles for the last 5,000 hours (about 2026-05-05..2026-11-28) of:
  - every book whose base token has ≥ 2 books;
  - every book with a USD stablecoin as base, i.e. a base name containing "USD", plus USDT0.
  - File: `batchnf16_hlspot_1h.parquet` (pair, base, quote, t, o, h, l, c, v in base units).
- **GRVT, Nado, Ethereal, Hibachi:** daily candles, full history, every perp, in NF14's format (`batchnf16_{venue}_1d.parquet`).
- The endpoints are not verified from this sandbox (the network is blocked). The first raw reply of each is kept in
  `batchnf16_probe.json`. A parse fix (units, fields) may be added as an addendum **before** any analysis is run. A venue that returns
  nothing is reported as not testable.

**HL spot conventions (#603–#604):**
- **USDC value of a book's price** = price × the hourly close of the quote token's USDC book; USDC = 1.
- **USD volume** = v × close × that rate.
- **Executable bar:** high > low, and USD volume ≥ $5,000 in the entry hour.
- **Exit** at the close 4 hours later if that hour traded; otherwise the next traded hour, up to +8h; otherwise the trade is dropped.
- **Size** = min($1,500, 1% of the entry hour's USD volume).
- **Costs:** HL spot base-tier taker fee 0.07% per side (×1.5 stress reported).
- One open trade per book.

| # | Idea | Rule |
|---|---|---|
| 603 | **Duplicate-book discount (HL spot)** | for a base with ≥ 2 books: reference = the USDC book, or, if the cheap book is the USDC book, the median of the other books. When a book's USDC-valued close is ≤ 0.99 × the reference close in the same hour (both books traded that hour, executable-bar filter on the cheap book), **buy the cheap book and sell the reference book** at those closes (held inventory). Exit both 4 hours later. Return = cheap leg − reference leg − 4 × 0.07% |
| 604 | **Stablecoin-book dip (HL spot)** | for a USD-stablecoin base quoted in USDC: hourly close ≤ 0.997 with the executable-bar filter → buy at that close. Exit at the first later hourly close ≥ 0.9995, or at the close 168 hours after entry. Return − 2 × 0.07%. Size min($1,500, 1% of the hour's USD volume) |
| 605 | #520 wick bids on **GRVT** | NF14's rule unchanged: resting bid at prev close × (1 − clip(4σ30, 5%, 30%)), filled if the low trades 0.5% through; sell at the close; maker 0.02% + taker 0.05% |
| 606 | #520 on **Nado** | same |
| 607 | #520 on **Ethereal** | same |
| 608 | #520 on **Hibachi** | same |
| 609 | #536 first-30-days rule (X 15%) pooled on the four venues | NF14 #596's rule unchanged; markets listed in each venue's first 30 days of data are excluded |

**Splits:**
- **#603–#604 (hourly):**
  - Stage 1 = data start..2026-08-15 (kill only);
  - Stage 2 = 2026-08-16..2026-11-25, unseen.
- **#605–#609 (daily):**
  - Stage 1 = venue start..2026-04-30 (kill only);
  - Stage 2 = 2026-05-01..2026-11-25, unseen.
  - These venues are young, so the split is set at 2026-05-01 instead of NF14's 2025-07-01.

**Stage 1 KILL:**
- #603–#604: ≥ 30 trades and mean net ≤ 0.
- #605–#609: NF14's rule, ≥ 30 fills and mean net ≤ 0.3%.

**Stage 2 PASS:** all of
- ≥ 30 trades, or ≥ 15 for #604, since depegs are rare;
- mean net ≥ 0.3%;
- t ≥ 2;
- sum positive without the 3 best trades, or the 3 best days for #605–#609;
- mean > 0 with costs × 1.5;
- for #605–#609, also NF14's ≥ $1,000/yr.

**Stale-print check (NF14 lesson):** before any PASS is accepted, the passing trades are checked for flat or near-zero-volume bars and
for one market dominating. A PASS driven by such bars is recorded as invalid.

**Multiple testing:** seven tests. Only a pass with Stage 2 t ≥ 2.5 goes to the radar forward log.

**Script/output:** `scripts/batch_nf16_20261128.py` → `docs/jx_runs/batch_nf16_20261128.txt`, re-run identical.

## Data note (2026-11-28, before the analysis was run)
- **HL spot:** 32 books, 116,745 hours, 2026-05-03..2026-11-28.
- **GRVT:** 184 perps, from 2024-12; prices plain, volume_q in USDT.
- **Hibachi:** 15 perps, from 2024-10.
- **Nado:** gateway and archive answered HTTP 403 to GitHub Actions. **Ethereal:** HTTP 503. Both are **not testable**, as registered.
- Nothing was changed. One observation, from last closes only and not from returns: the USDUC book (@302) had collapsed to $0.0015.
  #604 ran as registered, so that depeg counts.

## Result (2026-11-28; `docs/jx_runs/batch_nf16_20261128.txt`, re-run identical): **0 of 5 testable valid**

| # | Idea | Stage 1 | Stage 2 | Verdict |
|---|---|---|---|---|
| 603 | HL spot duplicate-book discount | n 51, +1.59% | n 40, **+1.83% (t 5.24)**, $1,815/yr | printed PASS → **invalid** (stale-print check below) |
| 604 | HL spot stablecoin-book dip | n 41, −0.36% (USDUC −58.8%) | n 37, +1.12%, $275/yr | **KILL (Stage 1)** |
| 605 | #520 wick bids, GRVT | n 150, +1.56% | n 185, −1.43% | FAIL |
| 606 | #520, Nado | — | — | not testable (HTTP 403) |
| 607 | #520, Ethereal | — | — | not testable (HTTP 503) |
| 608 | #520, Hibachi | n 25, +1.69% | n 16, +0.91% | FAIL |
| 609 | #536 pooled (GRVT, Hibachi) | n 130, +2.66% | n 21, −4.17% | FAIL |

**#603 stale-print check** (`scripts/batch_nf16_diag_20261128.py` → `docs/jx_runs/batch_nf16_diag_20261128.txt`, re-run identical):
- **41 of 93 trades:** the cheap leg was the deep USDC book. The "reference" was a thin book with a median $2,016 traded that hour, so
  its close is a stale last trade, not an executable price.
- **Entering one hour later** (both legs traded): +2.01% → **+0.08% (t 0.16)**. The gap is gone by the next hour's closes (median
  −0.23%; 22% still ≤ −1%).
- So the hourly-close result is not executable. Even if a live bot caught some of these gaps, capacity is about $1.2–1.8K/yr. Not
  forward-logged.

**Post-hoc sensitivity, not a verdict:** #604 without the collapsed USDUC book would have a Stage 1 mean of about +1.1%. That is still
only about $275/yr in Stage 2, and the −58.8% trade is exactly the risk the rule carries.

**Lessons:**
- GRVT repeats NF14: the first months were good and the edge reversed once the venue matured.
- Hourly closes in thin books are last trades. A cross-book gap must survive a one-hour delay before it counts.

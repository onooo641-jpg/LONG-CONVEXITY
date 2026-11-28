# Batch NF23 (#635–#638): zero-fee retail venues (Lighter, Paradex): #520 wick bids and #569 hourly cascades — pre-registered 2026-11-28, before any Lighter/Paradex candles exist in the repo

**Why:**
- Several thin-venue rules died on costs:
  - #520 wick bids, after NF14 and NF16;
  - #569 cascades, after NF15, where the Stage 2 means were about −0.1% to +0.0% net of 0.07%.
- **Lighter** charges standard retail accounts zero trading fees; the trade-off is slower order processing. **Paradex** advertises zero
  fees for retail.
- On a zero-fee venue, a rule whose gross edge is about +0.1% could pay.
- Both venues had empty candle files before (`wickscale_lighter_1d`, `wickscale_paradex_1d`). The cause was never diagnosed, because
  no raw replies were kept.

**Desk checks:**
- **G5:** both are wallet-based.
- **Fees (third-party/marketing, not verified for API orders):**
  - Lighter: zero for standard accounts.
  - Paradex: zero for retail.
  - The test runs at zero fees and is stressed at NF14's 0.02% + 0.05%.
- **Geoblock:** if a venue's API refuses GitHub's US servers, the venue is not testable. **No workaround is used.**

**Data (job `ubatchnf23`):**
- **Lighter:** `orderBooks` → `candlesticks` for every perp. Daily, full history; hourly 2026-03-01..2026-11-26. Several parameter
  variants are tried (seconds vs ms; resolution `1d`/`1h` vs `1440`/`60`); the first that returns rows wins.
- **Paradex:** `markets` → `markets/klines` (resolution 1440 and 60, ms timestamps; seconds tried if empty).
- **Files:** `batchnf23_{lighter,paradex}_{1d,1h}.parquet` (coin, t, o, h, l, c, v_usd). Raw first replies go to
  `batchnf23_probe.json`. A parse or unit fix may be added by addendum before analysis.

| # | Idea | Rule (unchanged from the source test) |
|---|---|---|
| 635 | #520 wick bids on **Lighter** | NF14's `wick(d, "vol")`; split 2025-07-01, or 2026-05-01 if the data starts after 2025-03-01 |
| 636 | #520 on **Paradex** | same |
| 637 | #569 hourly cascade on **Lighter** | NF15's rule (r ≤ −5σh, traded bar ≥ $20K, exit +4h); Stage 1 to 2026-08-15, Stage 2 2026-08-16..2026-11-25 |
| 638 | #569 on **Paradex** | same |

**Costs:** 0 (registered), stressed at 0.02% + 0.05% per round trip.

**Pass criteria:**
- **#635–#636:** NF14's judge, which already requires a pass with costs × 1.5; here the stress uses NF14's full costs instead.
- **#637–#638:** NF15's verdict, with the stress at 0.07%.
- **Both:** a PASS also needs the stress mean > 0, and the stale-print check (traded bars, no single market dominating).

**Multiple testing:** this family has now been tested on 11+ venues. Only a pass with Stage 2 t ≥ 2.5 **and** a positive stress mean
goes to the radar forward log.

**Script/output:** `scripts/batch_nf23_20261128.py` → `docs/jx_runs/batch_nf23_20261128.txt`, re-run identical.

**Output note:** the #637–#638 line labelled "costs x1.5" is NF15's printout. In this batch it is the 0.07% stress, because the script
sets the base cost to 0.

## Addendum 1 (2026-11-28, after the fetch, before any return was computed)
- **Lighter:** `orderBooks` answers (200; fees listed as 0.0000), but `candlesticks` answers **HTTP 403** to GitHub's US servers on
  every variant (s/ms, `1d`/`1440`/`1h`/`60`). This may be a regional block. No workaround is used. **#635 and #637 are not testable.**
- **Paradex:**
  - Hourly klines work: 66 perps, 2026-03-01..2026-11-25. Daily resolution 1440 is refused (HTTP 400); the API serves up to 60-minute
    bars.
  - **Volume unit fix:** the kline volume field is already USD. The job multiplied it by close: BTC came out at $280B/day; as USD it is
    about $4.6M/day. So v_usd = stored value / close.
  - **Bar convention:** a bar's open is the previous close; high/low/close come from trades. Bars exist only in hours with trades.
  - **#636** uses daily bars built from the hourly ones: open = first open, high = max, low = min, close = last, v_usd = sum. Its
    window is therefore 2026-03..2026-11, so the split is 2026-05-01, as registered for late-starting data.
- Nothing else changes.

## Result (2026-11-28; `docs/jx_runs/batch_nf23_20261128.txt`, re-run identical): **#636 PASS (small); #638 FAIL; #635/#637 not testable**

| # | Venue / rule | Stage 1 | Stage 2 | Verdict |
|---|---|---|---|---|
| 635 | Lighter wick bids | — | — | not testable (HTTP 403) |
| 636 | Paradex wick bids (daily from hourly) | n 3, +8.87% | n 69, **+5.25% (t 4.87)**, $1,581/yr; stress +5.18% | **PASS** |
| 637 | Lighter #569 | — | — | not testable (HTTP 403) |
| 638 | Paradex #569 | n 47, +0.74% (t 2.34) | n 22, −0.20% | FAIL |

**#636 stale-print check** (`scripts/batch_nf23_diag_20261128.py` → `docs/jx_runs/batch_nf23_diag_20261128.txt`, re-run identical):
- **Not executable at size:** in 61% of fills, the hour that made the low traded less than $1,500 (median $531). Those fills were too
  thin to fill at the registered size.
- **Executable at size:** the 27 fills whose low hour traded ≥ $1,500 average **+5.72%**.
- **Against HL:** fills on days HL also fell ≥ 5% average +3.50% (n 32). Paradex-only wicks average +7.71% (n 23).
- **Concentration:** TRX has 13 of 69 fills. No market dominates.
- **Verdict stands:** the PASS is **not** driven by unexecutable prints. Capacity is tiny, though: about $1.6K/yr at the registered
  size, less after capping each fill at the low hour's volume.
- **Forward log:** radar **N15** from 2026-12-01 (`scripts/radar_nonprop.py: n15_paradex_wick`). Fills are capped at
  min($1,500, 1% of day volume, USD volume of the low hour), and the zero-fee and 0.07% stress returns are both logged.
- **Judged with the other forward tests on 2027-01-26 and 2027-03-31.** It needs positive mean and positive sum without the 3 best
  fills, on the capped sizes.
- **Not verified:** whether Paradex charges API orders zero fees.

# Batch NF (#535–#536): niche new markets, liquidity for forced sellers in their first days — pre-registered 2026-11-28, before running

**Why niche, and the desk checks.** Jx asked for nicher areas. Candidates were checked against the radar's existing logs and earlier
tests, which already cover: depeg buying (#46, Batch C), new HL perp listings (#511, #385 + radar N11), and HL spot after 30 days
(#510). What was never tested:
- **#535, new HL spot tokens in their first 14 days.** Airdrop recipients and early unlockers dump into very thin books.
- **#536, new markets on smaller perp DEXes (Aster, dYdX) in their first 30 days.** Thin books plus points farmers; #511 tested only
  Hyperliquid.

**G5:** a resting limit buy on these venues is the direct receiver of a forced seller's discount (all are usable from Malaysia, no
KYC). **G6:** tiny capacity (1% of volume, $1,500 per fill) that funds cannot use. Lighter and Paradex candle files are empty, so they
are not tested.

**Rule (#389 mechanics).**
- Each day in the market's window, a resting buy at previous close × (1 − X).
- **Fill** if the low is ≥ 0.5% through the level; price = the level, or the open if lower. **Exit** at the close.
- **Size** = min($1,500, 1% of the day's USD volume); one $15,000 pot per day.

| # | Universe and window | X primary (context) | Costs | Dev (Stage 1) | Unseen (Stage 2) |
|---|---|---|---|---|---|
| 535 | HL spot pairs (`fivehigh_hl_spot_1d`), days 1–14 after each pair's first candle (day 1 has no previous close, so fills start day 2) | 20% (10%, 30%) | 0.04% + 0.07% | pairs first traded before 2025-07-01 | 2025-07-01 onward |
| 536 | Aster (`wickscale_aster_1d`) and dYdX v4 (`wickscale_dydx_1d`) perps, days 1–30 after each market's first candle; markets whose first candle is within 30 days of the file's start are dropped (unknown true listing) | 15% (10%, 20%) | 0.02% maker + 0.05% taker | listed before 2025-01-01 | 2025-01-01 onward |

**Stage 1 KILL:** mean net per fill ≤ 0.3% (≥ 30 fills).

**Stage 2 PASS:** ≥ 30 fills, mean ≥ 0.3%, t ≥ 2, ≥ $1,000/yr.

**Also reported:** profit without the best day, median per fill, win rate, and per-venue split for #536.

**If either passes,** it is added to radar N10's forward paper log with a bar fixed before 2026-12-01.

**Script/output:** `scripts/batch_nf_20261128.py` → `docs/jx_runs/batch_nf_20261128.txt`, re-run identical.

## Results (2026-11-28; `docs/jx_runs/batch_nf_20261128.txt`, re-run identical)
| # | Verdict | Stage 1 | Stage 2 | Note |
|---|---|---|---|---|
| 535 new HL spot tokens, days 1–14 (X 20%) | FAIL | +4.79%/fill (t 2.50, median −1.84%) | +32.7% (t 1.23, 139 fills), $5.3K/yr, **$710/yr without the best day** | One-off pumps; the typical fill loses |
| **536 new Aster/dYdX perps, days 1–30 (X 15%)** | **PASS (fragile)** | +15.9% (t 2.33, 297 fills) | **+1.74%/fill (t 2.29, 1,737 fills), $15.4K/yr**; Aster +1.38% (t 2.03), dYdX +4.80% (t 1.11) | Median fill −0.60%, win 46%. Context rows: X 10% t 1.24, X 20% t 1.97 |

**#536 diagnostics** (after the verdict, not part of the rule):
- Only 2% of fills are spike-only bars, so these are not bad prints.
- 53% of fills are at the $1,500 cap.
- **The top 10 of 1,737 fills produce 109% of the profit:** new memecoin perps that dipped 15% and then exploded (BLESS +640% in a
  day, LIGHT +299%). Without them the rule loses.
- It is a tail bet on new-listing pumps more than a dependable dip rebound. Treat it as unproven until the forward log says otherwise.

## Addendum 1 (2026-11-28, before 2026-12-01): #536 in the forward paper test
- Radar N13 logs #536 paper fills on Aster perps in their first 30 days (`aster_new_paper.parquet`). dYdX is not logged; it supplied
  10% of Stage-2 fills.
- **S2c PASS (fixed now), 2026-12-01 → 2027-01-26:** ≥ 40 fills, mean net ≥ 1.0%, **and** net profit still positive after removing the
  3 best fills. That last condition is the robustness check the backtest failed.

# Batch WK2 (#526–#529): last wick refinements (capped at 4), then pause for the forward test — pre-registered 2026-11-28, before running

**Rules as Batch WK** (refinement protocol). Base = #522: #520's volatility-scaled bids, exit at the next day's close.
Stage 1 = HL perps 2023-06..2024-12; Stage 2 = 2025-01..2026-10. Reference Stage 2 figures:
- #522: $8,269/yr, +3.97%/fill;
- #389: $14,372/yr.

**Caution, stated before running:** 2025–26 has now judged #520, #521–#525 and these four. Passes here are provisional until the
forward paper test (2026-12-01 → 2027-01-26).

| # | Test | Exact rule | PASS if (Stage 2) |
|---|---|---|---|
| 526 | **Hold length** | Hold h ∈ {2, 3, 5} days (exit at the close h days after the fill day). Pick h by Stage-1 $/yr; run once on Stage 2 with costs × 1.5 | ≥ 30 fills, mean ≥ 0.3%, t ≥ 2, $/yr above #522's $8,269 |
| 527 | **Equal-risk sizing** | #522, but size = min($1,500 × clip(0.10 / X_c, 0.5, 2), 1% of volume): bigger when the bid is close (calm coin), smaller when far | same, $/yr above #522's |
| 528 | **Skip systemic crash days** (#389's losses cluster in market-wide crashes) | #522, but no fills on days when BTC's low is ≥ 5% below its previous close | $/yr ≥ #522's **and** worst month no worse than #522's |
| 529 | **#389 + #522 combined** | Both rules on one $15,000 pot. On a coin-day where both fill, count it once as #522. Each keeps its own exit | mean ≥ 0.3%, t ≥ 2, $/yr above both #389's $14,372 and #522's $8,269 |

**Stage 1 KILL (all):** mean net per fill ≤ 0.3% with ≥ 30 fills.

**Script/output:** `scripts/batch_wk2_20261128.py` → `docs/jx_runs/batch_wk2_20261128.txt`, re-run identical.

After this batch, no more wick refinements until the forward test reports.

## Results (2026-11-28; `docs/jx_runs/batch_wk2_20261128.txt`, re-run identical)
| # | Verdict | Stage 2 (2025-01..2026-10) | Note |
|---|---|---|---|
| 526 hold length (h 3 chosen) | FAIL | +5.17%/fill with costs × 1.5, $6,524/yr | More per fill, fewer dollars than #522 |
| 527 equal-risk sizing | FAIL | $6,625/yr | Shifting size to calmer coins costs money |
| 528 skip BTC crash days | FAIL | $6,172/yr, worst month −$918 | Smaller worst month, but crash days are where much of the profit is |
| **529 #389 + #522 on one pot** | **PASS** | **+2.66%/fill (t 10.6, 2,642 fills), $26,680/yr, worst month −$417** | Beats #389 ($13.8K) and #522 ($8.3K) alone |

**Why #529 beats the sum (checked by decomposition):**
- On the 1,480 coin-days where both rules fill, #389's same-day exit tends to lose, while #522's next-day exit wins. Taking those
  fills as #522 lifts the #389 part from $13.8K to $23.3K/yr.
- Its worst month (−$417) is better than either rule alone (−$1,455 and −$1,884).
- The $15,000 pot binds on 35 of 412 fill days.
- **Caveat:** 2025–26 has now judged many wick variants, so the forward paper test decides.

## Addendum 1 (before 2026-12-01): #529 in the forward paper test
- #529 is computed from radar N10's two logs:
  - #522 = the `ret522` column of `wick520_paper.parquet`;
  - #389 = `wick_paper.parquet`, minus coin-days present in the #520 log.
- **#529 S2c PASS (fixed now):** 2026-12-01 → 2027-01-26, ≥ 60 combined fills and mean ≥ 1.0%.

No more wick refinements until the forward test reports (2027-01-26).

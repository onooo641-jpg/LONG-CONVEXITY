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

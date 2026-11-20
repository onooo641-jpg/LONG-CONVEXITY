# Multi-firm portfolio: Topstep + Lucid + MFFU + Breakout on the same trades — 2026-11-20 (CANDIDATES #60)

Written and committed **before** any run.

## Question
What income, worst dip and cash on hand result from running the friend's NQ trades on
several firms at once, and how much does adding firms/slots add over Topstep alone?

## Components (rules exactly as already tested; no new rule choices)
| firm | rules | trades | single-slot result so far |
|---|---|---|---|
| Topstep 50K | `XFARules()` | $900 risk | $44,359 (C2) |
| LucidFlex 50K | `lucidflex(50)` from `scripts/structure_scan_20261120.py` | $900 | $37,523 (#36) |
| MFFU Rapid EOD 50K | `MFFU` from `scripts/round3_20261120.py` | $900 | $34,481 (R1) |
| Breakout Classic 50K | `breakout()` static model, $950 risk, 10x notional cap, no fee refund | $950 | $38,263 (G3) |

## Slot limits (per person/household)
- Topstep: up to 5 Express Funded Accounts at once (Topstep help centre).
- Lucid: up to 5 funded accounts per household (third-party summaries of Lucid rules).
- MFFU: up to 3 Rapid EOD sim-funded accounts per size (third-party).
- Breakout: one evaluation at a time; modelled as 1 slot.

All slots get the **same trades**, so N slots at one firm are N identical copies of one
pipeline: income and dips scale by exactly N. Diversification only comes across firms.

## Portfolios
- A: Topstep ×1 (reference)
- B: one slot at each of the four firms
- B−: B without Breakout (its bot connection is unconfirmed)
- C: maximum slots: Topstep ×5 + Lucid ×5 + MFFU ×3 + Breakout ×1
- C−: C without Breakout

## Metrics (daily combined net = withdrawals × split − all costs, costs accrued monthly)
Total net 2016–26 and per year; 2016–20 vs 2021–26; worst dip from a previous peak;
most cash ever out of pocket (lowest combined net); longest time below a previous peak;
losing calendar years. Coin flip for portfolio B (200 runs, seed 1, same sign flip applied
to every firm on the same trade): median net, share profitable, 5th-percentile worst dip.

**Cash on hand** = the larger of worst dip and most out of pocket. No pass/fail: this
sizes the plan. Firm-level caveats from each component's pre-registration still apply.

Command: `uv run python scripts/portfolio_20261120.py`

## Addendum, pre-registered after part 1 ran but before part 2 ran: start-date test
Part 1 starts every firm on 2016-01-01, the worst stretch for this strategy. Part 2
restarts each firm from scratch on the 1st of every month from 2016-01 to 2025-10 (118
starts) and records, for portfolios A and B−, the first 12 months: net income, worst dip
and most out of pocket. Reported: median, 10th percentile and share of starts that lose
money in year one. B− is used because Breakout's bot connection is unconfirmed.
Command: `uv run python scripts/portfolio_starts_20261120.py`

## Results part 1 (2026-11-20, `docs/jx_runs/portfolio_20261120.txt`)
Single-slot totals reproduce earlier runs exactly (Topstep $44,359, Lucid $37,523, MFFU $34,481, Breakout $38,263).

| portfolio | net 2016–26 (/yr) | 2016–20 / 2021–26 | worst dip = cash on hand | longest below peak | losing years |
|---|---|---|---|---|---|
| A Topstep ×1 | $44,359 ($4,097) | $7,671 / $36,687 | $3,520 | 44.7 mo | 4 |
| B one slot at each of 4 firms | $154,625 ($14,280) | $20,037 / $134,588 | $22,853 | 50.2 mo | 5 |
| B− same without Breakout | $116,362 ($10,746) | $17,970 / $98,392 | $13,829 | 50.1 mo | 4 |
| C max slots (5/5/3/1) | $551,113 ($50,896) | $83,758 / $467,355 | $66,990 | 50.2 mo | 4 |
| C− max slots without Breakout | $512,850 ($47,362) | $81,691 / $431,159 | $57,966 | 50.1 mo | 4 |

- Monthly P&L correlation between firms is 0.80–0.88: adding firms adds income almost
  linearly but also adds the dips, which line up in time (2016–18, 2021–22).
- Coin flip, portfolio B: median $51,287, 94% profitable, 5th percentile −$5,713; median
  worst dip −$20,217, 5th percentile −$36,350. The structure still pays without an edge.
- Income is back-loaded: 2016–18 lose every year at every scale; 2023–26 make most of it.

## Results part 2: start-date test (`docs/jx_runs/portfolio_starts_20261120.txt`)
First 12 months after starting on the 1st of each month, 2016-01..2025-10 (118 starts):

| portfolio | year-one net median (10th / 90th pct) | starts that lose in year one | worst out of pocket in year one |
|---|---|---|---|
| A Topstep ×1 | $1,704 (−$1,320 / $9,624) | 32% | −$1,906 |
| B− Topstep + Lucid + MFFU | $5,127 (−$5,552 / $25,071) | 35% | −$6,722 |

Median year-one net by start year (B−): 2016 −$3,546, 2017 −$5,274, 2018 $1,045,
2019 $18,537, 2020 $5,356, 2021 $2,004, 2022 $12,140, 2023 $22,817, 2024 $22,060, 2025 $2,690.

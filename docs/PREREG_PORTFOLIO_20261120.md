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

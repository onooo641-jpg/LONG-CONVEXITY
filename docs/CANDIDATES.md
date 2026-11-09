# CANDIDATES

One numbered row per idea tried. The point is that nothing gets retested blind,
and the count of things tried is visible in one place instead of spread across
the README and commit messages.

Rules:
- Next number = last number + 1. Numbers are never reused or renumbered.
- Write the formulation down **before** the run, in enough detail to rerun it.
  Code path plus the parameter values that differ from defaults.
- The verdict cites where it came from. Figures in a verdict are not standing
  figures until they're in `docs/FIGURES_LEDGER.md`.
- A variant found by looking at results gets its own row, marked
  **selected-on-data**.

**Tried so far: 28 rows, and row 12 alone is a 900-combination search.** So the
real count of configurations looked at is about 914, plus the 0.5–3.0 target
sweep in row 9.

Rows 1–15 were numbered retroactively on 2026-11-06. Their verdicts are
copied from the README and commit messages, which pre-date the ledger; I
didn't re-run them. Defaults shared by rows 1–7 (`strategies/base.py`
`BaseConfig`): stop buffer 2 pt, target 2R, swing_n 2, min FVG 1 pt, risk
2–250 pt, entries expire 15:00 ET, flat 16:00 ET, one trade per day, $500
risk, 5m signals and 1m fills.

## Pre-registered (strategies/registry.py — frozen, never tune)

| # | name | formulation | verdict | source |
|---|---|---|---|---|
| 1 | po3_judas | Asian-session range (accumulation). Raid between 09:30–11:00 ET, market-structure break by 12:00, FVG limit entry, entry expires 15:00, flat 16:00. `PO3Config` defaults. | Dev +$6,064 (PF 1.44), OOS −$521 (PF 0.93). **Fail.** | README table, post 2026-09-09 fix |
| 2 | silver_bullet | First FVG aligned with structure in 10:00–11:00 ET. `SilverBulletConfig` defaults. | Dev +$15,421 (1.03), OOS +$814 (1.01): $1.92/trade. **Fail** (not a business). | same |
| 3 | turtle_soup | Raid on prior-day high/low 07:00–12:00 ET, structure break by 13:00, target at the opposite level. | Dev −$13,563 (0.91), OOS −$8,287 (0.87). **Fail.** | same |
| 4 | ob_retest | Retest of an order block left by ≥15 pt displacement, 07:00–14:00 ET, entry at block midpoint. | Dev −$21,027 (0.96), OOS −$31,676 (0.86). **Fail.** | same |
| 5 | breaker_retest | Retest of a failed order block (polarity flipped), ≥15 pt displacement, breaks within 60 bars, 07:00–14:00 ET. | Dev +$20,730 (1.04), OOS −$14,631 (0.93). **Fail.** | same |
| 6 | ote_retracement | 0.705 retracement of a post-break leg of 20–400 pt, extreme set over 6 bars, 07:00–14:00 ET. | Dev −$26,131 (0.92), OOS +$8,605 (1.07). **Fail** (inconsistent). | same |
| 7 | sfp_reversal | Swing-failure pattern, ≥1 pt penetration, entry at 0.5 between close and extreme, 07:00–12:00 ET. | Dev −$175,903 (0.75), OOS −$33,101 (0.86). **Fail.** | same |
| — | combined account of 1–7 | Earliest signal of the day wins. | Dev −$134,031 (0.81), OOS −$21,840 (0.91). Rows 4–7 share 97–100% of signal days, so 1–7 are really two or three ideas. | README |

## Not pre-registered

| # | name | formulation | verdict | source |
|---|---|---|---|---|
| 8 | **LTF sweep** (the live candidate) | `strategies/ltf_sweep.py`, `LTFSweepConfig()`. 15m pool = prior 4 candles. Sweep ≥0.25 pt beyond it, 09:30–15:00 ET. 1m CHoCH within 30 bars (CHoCH required, not BOS). 1m FVG ≥0.5 pt limit entry, stop buffer 1 pt, target 1.0R, risk 1–120 pt, entries to 15:30, flat 16:00. One per day. Marketable entries refused (`skip_marketable_entries=True`). | Full 2016–2026 $500: −$3,044, WR 53.2% vs BE 53.3%, PF 0.994 (ledger S1–S5). Dev −$25,001, OOS +$21,957. **Open.** The forward log since 2026-08-29 is the only clean test. | ledger; README |
| 9 | LTF sweep, target-R sweep | Row 8 with `target_r` across 0.5–3.0 (reported points 1:1, 1:1.5, 1:2). `scripts/sweep_target_r.py`. | OOS PF 1.150 / 1.026 / 0.987. Monotone down over the whole range, same shape in dev. **1:1 kept** (the specified value, not selected). | README §LTF |
| 10 | LTF sweep, unrestricted | Row 8 with `one_per_day=False`. | Dev "+$84,346" flips to −$136,451 when a fill needs one tick through. **Fail** (fill-model artefact). | README |
| 11 | OR5 retest | `strategies/or5_retest.py` per `docs/or5_retest_spec.md` (rules committed before the run, 653e2ee). 09:30–09:35 range, body ≥40%, trade body direction. 1m close break, close retest within ±5 pt, re-close beyond before 10:00 ET, stop entry +2 pt. Stop = retest extreme ±3 pt clamped to 12–35 pt. Half off at 1R, runner to the range height, BE+2, flat 10:45. News filter **not** applied (no calendar). | Dev 868 fills, PF 0.62, −$88,041. OOS 291, PF 0.59, −$33,503. Every first-target setting 0.5R–2.0R loses. Mirrored direction loses too. **Fail.** Re-run after the same look-ahead fix: dev PF 0.71, OOS PF 0.68 (pessimistic). Still fails. | 97b54d6; `docs/jx_runs/or5_retest_after_fix_*` |
| 12 | ORB family search | `scripts/search_orb.py`. Grid: entry ∈ {break_retest, break_first, fail_fade} × side ∈ {body, either} × stop ∈ {pullback 3, fixed 15, fixed 25, height 0.5, height 1.0} × min body ∈ {0, 0.4} × exit ∈ {10:45, 12:00, 16:00} × target ∈ {0.25, 0.4, 0.5, 0.75, 1.0}R. 900 combinations, $500, stop entries, 1 tick slippage. **Search, selected-on-data.** | Breakouts: 0 of 600 profitable in both periods. fail_fade: 14% of 300 profitable in both, dev/OOS rank correlation +0.784, best cell PF 1.17, 2026 negative in every variant. ~~Hypothesis~~ → **Fail after look-ahead fix (2026-11-06):** `detect()` let the previous evening's bars break a range that only forms at 09:35 (ARTIFACT_CLASSES 5). Fixed: **0 of 900** profitable in both periods, best dev PF 1.06, fail_fade OOS PF 0.74. | c280e2a; fix 2026-11-06, `docs/jx_runs/search_orb_after_fix_*` |
| 13 | LTF session cutoff 11:00 ET | Row 8, but stop taking setups at 11:00 ET (GO_LIVE hourly table). **Selected-on-data.** | OOS +$12,200, dev −$2,232, 11y +$9,968. The only positive one, because it was picked off the by-hour table. **Rejected.** | GO_LIVE §收工; 859ad92 |
| 14 | LTF session cutoff 13:00 ET | Same, 13:00. | OOS +$15,217, dev −$18,843, 11y −$3,626. **Rejected.** | same |
| 15 | LTF session cutoff 15:30 ET (spec) | Same as the spec: sweeps to 15:00, entries to 15:30, flat 16:00. Exits once the day is resolved. | OOS +$13,274, dev −$17,668, 11y −$4,394 (confirming-bar fills excluded; ledger S7, unsourced). **Kept as the spec, not selected.** | same |

| 16 | failed-breakout fade, unselected member (to forward-log) | Row 12's `fail_fade`, `side_rule=either`, stop = 1.0× range height, exit 10:45, 1R, `min_body_frac=0.0` (the variant `fade_report.py` plots because nothing selected it). Formulated 2026-11-06 for a forward log starting 2026-09-08 05:27 UTC. | Before the fix: 53% of its trades were impossible and carried all the profit. After: 1,855 trades, PF 0.95, dev 1.01, **OOS 0.80, −$26,959**. **Fail. Not forward-logged.** | `docs/jx_runs/fade_after_fix_*` |
| 17 | LTF, long only | Batch 2026-11-09 (`docs/PREREG_BATCH_20261109.md`). Drop shorts. | fail (margin worse on NQ-S, NQ-O) | PREREG_BATCH_20261109 results |
| 18 | LTF, short only | Drop longs. | fail | PREREG_BATCH_20261109 results |
| 19 | LTF, scale out, runner 2R | Half off at 1R, runner to 2R, stop to entry. | fail (worse on every set) | PREREG_BATCH_20261109 results |
| 20 | LTF, scale out, runner 3R | Same, runner to 3R. | fail (worse on every set) | PREREG_BATCH_20261109 results |
| 21 | funded size ×0.5 | `recycle(funded_scale=0.5)`. | fail | PREREG_BATCH_20261109 results |
| 22 | funded size ×0.75 | `recycle(funded_scale=0.75)`. | fail (NQ-S only) | PREREG_BATCH_20261109 results |
| 23 | loss-streak pause | 3 losses in a row → skip next 5 trades (streak counts shadow outcomes). | fail (ES, YM… not NQ) | PREREG_BATCH_20261109 results |
| 24 | equity filter | Trade only if prior 20 baseline trades net > 0. | fail | PREREG_BATCH_20261109 results |
| 25 | fee cap 5% | Skip if contracts × $1.24 > 5% of risk. | fail | PREREG_BATCH_20261109 results |
| 26 | fee cap 3% | Same at 3%. | fail | PREREG_BATCH_20261109 results |
| 27 | stop buffer 2.0 | `stop_buffer_points=2.0`. | fail (NQ-S only) | PREREG_BATCH_20261109 results |
| 28 | 120-min time stop | `time_exit_ts = min(orig, valid_from + 120 min)`. | **PASS** by rule; real net gain small (NQ +$1.2K); NQ-O +$187. Forward-log shadow only | PREREG_BATCH_20261109 results |

Earlier, superseded version of 13 (c21f67c): "11:00, cancel unfilled" 350 /
+$16,409 OOS, 908 / −$10,150 dev, before confirming-bar fills were excluded.
Not a separate idea, so not numbered.

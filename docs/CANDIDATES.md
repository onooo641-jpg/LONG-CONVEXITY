# Candidates

One row per idea actually tried, numbered retroactively, formulation stated in
full, verdict stated. Exists so nothing gets retested blind — check here
before re-running an idea that already has a number.

Figures below at $500/trade unless noted; see `FIGURES_LEDGER.md` for the
commands behind the recycling-specific numbers.

| # | Candidate | Formulation | Verdict |
|---|---|---|---|
| 1 | `po3_judas` | PO3 / Judas swing: Asian-range raid, MSB, FVG entry. Pre-registered, ICT's published parameters. | 11yr net +$7,985 (116 trades), OOS net +$406 (35 trades). Thin sample both windows; weakly positive, not load-bearing. |
| 2 | `silver_bullet` | First aligned FVG in the 10:00-11:00 ET window. Pre-registered. | 11yr net +$45,179 (1,751 trades), OOS net **-$22,081** (452 trades). Profitable in development, loses out-of-sample — the selection-bias case the registry's pre-registration exists to surface. |
| 3 | `turtle_soup` | Raid on prior day high/low, then structure break. Pre-registered. | 11yr net **-$24,784** (625 trades), OOS net **-$9,841** (196 trades). Loses in both windows. |
| 4 | `ob_retest` | Retest of an order block left by displacement. Pre-registered. | 11yr net +$55,504 (2,056 trades), OOS net +$12,031 (648 trades). Profitable in both windows — the registry's best-behaved member. |
| 5 | `breaker_retest` | Retest of a failed order block, polarity flipped. Pre-registered. | 11yr net +$23,232 (2,007 trades), OOS net **-$18,539** (669 trades). Same shape as #2: development-positive, OOS-negative. |
| 6 | `ote_retracement` | 0.705 retracement of a post-break expansion leg. Pre-registered. | 11yr net +$15,910 (1,396 trades), OOS net +$19,727 (418 trades). Profitable in both windows, OOS actually stronger than development. |
| 7 | `sfp_reversal` | Swing failure pattern inside the NY morning. Pre-registered. | 11yr net **-$200,242** (2,444 trades), OOS net **-$39,153** (685 trades). The worst of the seven by a wide margin, loses in both windows. |
| 8 | `ltf_sweep` (LTF Sweep) | 15m liquidity pool, 1m sweep + CHoCH, 1m FVG entry, fixed 1:1 target. Not pre-registered against OOS the way 1-7 were — invented after the data had already been looked at, so its spec (`strategies/ltf_sweep.py`) is committed and frozen instead, same discipline applied after the fact. | Full history (2016-2026) net **-$2,553** (2,185 trades, see `FIGURES_LEDGER.md` #1), OOS net +$43,064. Loses on its own over the full history; the recycling business case (see `backtest/recycle.py`) depends on the account structure's asymmetry, not on this being a positive-expectancy strategy. This is the model everything else in this project is built on top of. |
| 9 | `or5_retest` (OR5 retest) | Opening-range (09:30-09:35) break and retest, stop order on confirmed retest, spec in `docs/or5_retest_spec.md`. Rules came from outside the project; pre-registered before the first backtest ran (same discipline as 1-7, applied to a model invented from an external source instead of ICT's own publications). | Spec rules F2 (news blackout) and the retest/target parameter sweep (window 5/8/10pt, TP1 0.5R/0.8R/1.0R) are specified but not yet reported run — `strategies/or5_retest.py` implements the base rules; the parameter-sweep comparison in the spec's section on pre-registered vs. swept variants has not been executed this session. Open. |
| 10 | ORB family search (`scripts/search_orb.py`) | Hundreds of opening-range-break rule combinations (entry kind, side rule, stop, min body fraction, exit minute) swept on development data only, scored out-of-sample for every combination but never selected on it. Explicitly labelled a search, not a pre-registered test. | Not re-run this session; the script's own three honesty checks (dev-only selection, combination count reported, dev/OOS rank correlation reported) are the right lens for reading its output — a high OOS number from this script is not comparable to the pre-registered strategies above without also reading the rank-correlation figure. |
| 11 | LTF Sweep exit cutoff: 11:00 ET | Flatten the session at 11:00 instead of 15:30. Found by scanning an hourly table of candidate cutoffs against the full 11-year result. | 11yr **+$9,968** (dev -$2,232, OOS +$12,200) — the only hourly cutoff that turns the full history positive, and it is positive *because* it was picked by searching for the best one. GO_LIVE.md's working rule: do not reinstate this or anything found the same way. Rejected on methodology, not on the number. |
| 12 | LTF Sweep exit cutoff: 13:00 ET | Flatten at 13:00. | 11yr -$3,626 (dev -$18,843, OOS +$15,217). Still negative over 11 years; OOS number alone would look attractive, same objection as #11. Rejected. |
| 13 | LTF Sweep exit cutoff: 15:30 ET (shipped) | Flatten at 15:30 — the strategy's originally specified session end, run start-to-finish without searching for a better exit. | 11yr -$4,394 (dev -$17,668, OOS +$13,274). This is the number the engine actually trades, specifically *because* it was not chosen by comparison with #11/#12. |
| 14 | News filter (F2): no entries on a tier-1 US data release or FOMC day | Ported from `docs/or5_retest_spec.md` rule F2 into `strategies/ltf_sweep.py` as an opt-in `news_filter` config flag (off by default), backed by `docs/tier1_calendar.csv` (CPI/PPI/NFP/PCE/Retail/FOMC, 2016-2026). | Removes 25% of trades in both windows. 11-year net gets **worse** (-$2,553 → -$3,342); OOS net and profit factor both improve (net +$43,064 → +$46,019, PF 1.191 → 1.284). Mixed result over the full history, so left off by default rather than flipped on — see `docs/NOTES_JX.md` check 6. |
| 15 | Payout policy: `LOCK_FIRST` vs `IMMEDIATE` | Whether a funded account waits for its trailing loss limit to lock at $0 before taking a payout (`LOCK_FIRST`), or pays out the moment it is eligible regardless (`IMMEDIATE`). | 11yr: IMMEDIATE wins at every position size tested (+$3,367 net at $900/trade; see `FIGURES_LEDGER.md` #4/#6). One-year sample says LOCK_FIRST is slightly better, 11-year sample says IMMEDIATE wins broadly — resolved in favour of the 11-year sample. Also preferred independently for counterparty-risk reasons (see `docs/GO_LIVE.md`, "先領錢，不等鎖死"). **Switched the default** in `backtest/recycle.py` 2026-11-06. |

## Rule-change stress test (not separate candidates — one baseline, five perturbations)

Run against the shipped LTF Sweep at $900/trade, 11 years, `Policy.LOCK_FIRST`
(the policy whose mechanics the lock/reset changes are actually about).
Baseline net $44,823.

| Change | Net | Delta |
|---|---|---|
| reset $49 → $99 | $43,523 | -$1,300 |
| trailing limit never locks (`mll_locks_at=None`) | -$17,079 | -$61,902 (degenerate under LOCK_FIRST — see `docs/NOTES_JX.md` check 4) |
| `payout_cap` $4,000 → $2,000 | $45,579 | +$756 |
| `winning_days_required` 5 → 10 | $45,444 | +$621 |
| activation charged per attempt, not per XFA earned | $29,625 | -$15,198 |

This is not a new strategy candidate; it is a sensitivity check on the account
rules the recycling business depends on. Kept here rather than in
`FIGURES_LEDGER.md` because the comparison *is* the result, not a single
standing number.

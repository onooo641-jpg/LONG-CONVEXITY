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
| 9 | `or5_retest` (OR5 retest) | Opening-range (09:30-09:35) break and retest, stop order on confirmed retest, spec in `docs/or5_retest_spec.md`. Rules came from outside the project; pre-registered before the first backtest ran (same discipline as 1-7, applied to a model invented from an external source instead of ICT's own publications). | Spec rules F2 (news blackout) and the retest/target parameter sweep (window 5/8/10pt, TP1 0.5R/0.8R/1.0R) are specified but not yet reported run — `strategies/or5_retest.py` implements the base rules; the parameter-sweep comparison in the spec's section on pre-registered vs. swept variants has not been executed this session. **Fails regardless**: an independent concurrent session found and fixed a look-ahead in this file (`ARTIFACT_CLASSES.md` class 5, ported here) — dev PF 0.62→0.71, OOS PF 0.59→0.68 after the fix. Still loses both periods. Open on the parameter sweep; closed on "does the base rule work." |
| 10 | ORB family search (`scripts/search_orb.py`) | Hundreds of opening-range-break rule combinations (entry kind, side rule, stop, min body fraction, exit minute) swept on development data only, scored out-of-sample for every combination but never selected on it. Explicitly labelled a search, not a pre-registered test. | Not re-run this session for the search itself; the script's own three honesty checks (dev-only selection, combination count reported, dev/OOS rank correlation reported) are the right lens for reading its output. **The look-ahead fix (`ARTIFACT_CLASSES.md` class 5) changes the answer anyway**: before the fix, `fail_fade` had 14% of 300 combinations profitable in both periods; after porting the fix, 0 of 900 combinations are profitable in both periods (best dev PF 1.06). The 14% was entirely the previous-evening-breaks-tomorrow's-range bug. |
| 11 | LTF Sweep exit cutoff: 11:00 ET | Flatten the session at 11:00 instead of 15:30. Found by scanning an hourly table of candidate cutoffs against the full 11-year result. | 11yr **+$9,968** (dev -$2,232, OOS +$12,200) — the only hourly cutoff that turns the full history positive, and it is positive *because* it was picked by searching for the best one. GO_LIVE.md's working rule: do not reinstate this or anything found the same way. Rejected on methodology, not on the number. |
| 12 | LTF Sweep exit cutoff: 13:00 ET | Flatten at 13:00. | 11yr -$3,626 (dev -$18,843, OOS +$15,217). Still negative over 11 years; OOS number alone would look attractive, same objection as #11. Rejected. |
| 13 | LTF Sweep exit cutoff: 15:30 ET (shipped) | Flatten at 15:30 — the strategy's originally specified session end, run start-to-finish without searching for a better exit. | 11yr -$4,394 (dev -$17,668, OOS +$13,274). This is the number the engine actually trades, specifically *because* it was not chosen by comparison with #11/#12. |
| 14 | News filter (F2): no entries on a tier-1 US data release or FOMC day | Ported from `docs/or5_retest_spec.md` rule F2 into `strategies/ltf_sweep.py` as an opt-in `news_filter` config flag (off by default), backed by `docs/tier1_calendar.csv` (CPI/PPI/NFP/PCE/Retail/FOMC, 2016-2026). | Removes 25% of trades in both windows. 11-year net gets **worse** (-$2,553 → -$3,342); OOS net and profit factor both improve (net +$43,064 → +$46,019, PF 1.191 → 1.284). Mixed result over the full history, so left off by default rather than flipped on — see `docs/NOTES_JX.md` check 6. |
| 15 | Payout policy: `LOCK_FIRST` vs `IMMEDIATE` | Whether a funded account waits for its trailing loss limit to lock at $0 before taking a payout (`LOCK_FIRST`), or pays out the moment it is eligible regardless (`IMMEDIATE`). | **Flipped twice in one day (2026-11-06), both times for real reasons, and the second flip is where it stands.** First: under the rule model read 2026-09-14, IMMEDIATE won every size tested (+$3,367 net at $900/trade) because a payout taken before the natural lock left the account's floor exposed below $0 — reasonable on the rules, and independently backed by a firm-failure hazard sweep (`FIGURES_LEDGER.md` #12) showing IMMEDIATE still ahead at every hazard from 0% to 25%/yr, so the switch did not even depend on resolving the counterparty-risk debate. **Then an independent concurrent session (and this session, re-deriving it) re-read Topstep's payout page and found two rules neither rule model had:** a payout permanently locks the MLL to $0 (removing most of IMMEDIATE's structural advantage — the thing LOCK_FIRST was "paying" to get, IMMEDIATE now gets for free on its first payout too), and every payout after the first requires positive profit since the last one (which throttles IMMEDIATE's more frequent early payouts). Re-run under the corrected rules: **LOCK_FIRST wins at $500/$900/$1,000** (+$1,636 net at $900/trade; `FIGURES_LEDGER.md` #13), and the hazard sweep re-run under the same corrected rules shows LOCK_FIRST still ahead at every hazard 0-25%, not just at h=0. Only $250/trade (where both lose) still favours IMMEDIATE. **Switched the default back to `LOCK_FIRST`** in `backtest/recycle.py`, matching the independent session's own conclusion exactly. |

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

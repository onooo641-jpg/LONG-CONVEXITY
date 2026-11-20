# FIGURES_LEDGER

**Standing rule: a figure that isn't in this ledger isn't a standing figure,
however it appears in prose.** README, GO_LIVE, reports and commit messages
may quote figures. Only figures here, with a command that reproduces them,
can be relied on. Add the row before quoting the number anywhere else.

Status:
- **current** — reproduces from the command on the stated window, and is the
  parameterisation the plan uses.
- **superseded** — reproduces, but another row replaces it (named).
- **unsourced** — quoted in prose, no command in this ledger reproduces it yet.

Windows:
- **W0908** — data to 2026-09-08 05:27 UTC (the last shard before the
  September pull). Most figures in the docs were computed on this.
- **W1028** — all data in the repo as of 2026-11-06 (to 2026-10-28 23:59 UTC).

Command shorthand:
- `CHK0908` = `uv run python scripts/jx_checks.py --end 2026-09-08T05:27Z`
- `CHK1028` = `uv run python scripts/jx_checks.py`
- `ASOF` = `uv run python scripts/asof.py 2026-09-08T05:27Z`
- `ORD0908` / `ORDALL` = `data/processed/jx_orders_20260908T0527.parquet` /
  `jx_orders_all.parquet`, written by the first `jx_checks.py` run on that window

Rulebooks: **RB0914** = Topstep rules as read 2026-09-14
(`jx_checks.py --rules 20260914`). **RB1106** = plus the two payout rules read
2026-11-06 (payout resets the MLL to $0; profit since last payout). RB1106 is
`XFARules()`'s default and the current rulebook.

Recycling figures are $900/trade, one unbroken chain from 2016-01-01. Rows
R1–R13 and A1–A4 are **RB0914** unless they say otherwise. Rows tagged N
(below) are RB1106 and supersede them.

## Current headline — rulebook 20261107, the figures README.md quotes

All $900 a trade, NQ (MNQ), `Policy.LOCK_FIRST`, payout cap $2,000, one
unbroken chain from 2016-01-01, data to 2026-10-28. Commands use the default
rulebook (`20261107`).

| # | figure | value | command | window | computed | status |
|---|---|---|---|---|---|---|
| C1 | chain: evaluations / funded / payouts | 152 / 52 / 44 | `uv run python scripts/jx_checks.py --skip-strategy` (§1, "cap 2,000, LOCK_FIRST") | W1028 | 2026-11-07 | **current** |
| C2 | chain: withdrawn / spent / **net** | $61,440 / $17,081 / **$44,359** | same | W1028 | 2026-11-07 | **current** |
| C3 | evaluation pass rate | 34.4% (52 of 151 that ended) | `uv run python scripts/jx_capital.py` | W1028 | 2026-11-07 | current |
| C4 | deepest cash dip over 118 monthly start dates: median / worst | −$863 / −$3,520 | same | W1028 | 2026-11-07 | current |
| C5 | days to first payout: median / p90 | 144 / 826 | same | W1028 | 2026-11-07 | current |
| C6 | coin-flip baseline (same sizes, random sign, fees kept), median of 200 | $18,046; pass 26.7% | `uv run python scripts/jx_zero_edge.py` | W1028 | 2026-11-07 | current |
| C7 | raw strategy, no recycling, $900 | −$2,553 net (S6) | `uv run python scripts/jx_checks.py` §1 last line | W1028 | 2026-11-06 | current |
| C8 | unseen holdout 2010-07..2015-12, recycling net | −$2,505 (PF 0.784) | `uv run python scripts/holdout_test.py` | 2010–2015 | 2026-11-07 | current |
| C9 | withdrawals by year, LOCK_FIRST cap $2,000 | 2016–18 $0 each; 2019 $4,474; 2020 $9,734; 2021 $1,164; 2022 $3,342; 2023 $11,586; 2024 $6,596; 2025 $10,221; 2026 $14,322 | `uv run python scripts/jx_checks.py --skip-strategy` §2, "policy LOCK_FIRST" | W1028 | 2026-11-07 | current |
| C10 | rule stress, net: baseline / reset $99 / activation per attempt / MLL never locks / 10 winning days / all five | $44,359 / $43,259 / $29,459 / −$17,130 / $46,775 / −$33,329 | same, §3 "policy LOCK_FIRST" | W1028 | 2026-11-07 | current |
| C11 | per evaluation bought: spent / withdrawn (C2 ÷ C1) | $112 / $404 | arithmetic on C1, C2 | W1028 | 2026-11-19 | current |
| C12 | commission $0.74 instead of $1.24, 2016–26 / holdout | net $50,961 / −$2,475 | `uv run python scripts/commission_sensitivity.py` | W1028 | 2026-11-08 | current |

## Strategy alone

| # | figure | value | command | window | computed | status |
|---|---|---|---|---|---|---|
| S1 | full-history net, $500, one/day | −$3,044 (2,161 trades) | `ASOF scripts/simulator_inputs.py` (or `CHK0908` §0) | W0908 | 2026-11-06 | current for W0908 |
| S1b | same | −$3,357 (2,185 trades) | `CHK1028` §0 | W1028 | 2026-11-06 | current |
| S2 | win rate | 53.2% (W1028: 53.1%) | same as S1 / S1b | | 2026-11-06 | current |
| S3 | break-even win rate | 53.3% (both) | same as S1 / S1b | | 2026-11-06 | current |
| S4 | **payoff ratio** (avg win R / avg loss R) | 0.876 (both) | same as S1 / S1b | | 2026-11-06 | current. **README calls this "PF". It isn't.** |
| S5 | **profit factor** | **0.994** (both) | `CHK0908` / `CHK1028` §0 | | 2026-11-06 | current |
| S6 | strategy alone, $900, report slice | −$2,135 (W1028: −$2,553) | `CHK0908` / `CHK1028` §1 last line | | 2026-11-06 | current. GO_LIVE 158 doesn't say it's $900, not $500. |
| S7 | "11 years −$4,394" (GO_LIVE 32) | −$4,394 | none | | | unsourced (per 859ad92: full session, confirming-bar fills excluded) |
| S8 | "PF 0.856 dev / 0.876 full" (README 158–160) | | | | | unsourced as PF. These are the payoff ratios. See S4/S5. |

## Recycling, 11 years

| # | figure | value | command | window | computed | status |
|---|---|---|---|---|---|---|
| R1 | chain, **IMMEDIATE**: withdrawn / spent / net | $61,984 / $17,116 / **$44,868** | `CHK0908` §1 | W0908 | 2026-11-06 | current for W0908 |
| R1b | same | $65,467 / $17,277 / **$48,190** | `CHK1028` §1 | W1028 | 2026-11-06 | **current** |
| R2 | chain, LOCK_FIRST (GO_LIVE 158, recycling_report headline) | $59,728 / $17,314 / $42,414 | `CHK0908` §1; `ASOF scripts/recycling_report.py --orders ORD0908 --out /tmp/r.html` | W0908 | 2026-11-06 | superseded by R1 |
| R3 | **drift resolution** | GO_LIVE 158 = LOCK_FIRST, 189 = IMMEDIATE. Gap $2,454 net / $2,256 withdrawn. The quoted "$19,570" compares withdrawn with net. payout_cap is not the cause. | `CHK0908` §1 | W0908 | 2026-11-06 | current |
| R4 | longest stretch with no payout, IMMEDIATE | 479 days | `CHK0908` / `CHK1028` §1 | both | 2026-11-06 | current |
| R5 | longest no-payout, LOCK_FIRST (GO_LIVE 166) | 1,184 days | same | both | 2026-11-06 | superseded by R4 |
| R6 | longest bust streak, IMMEDIATE / LOCK_FIRST | 17 / 39 | same | both | 2026-11-06 | 17 current; 39 (GO_LIVE 165) superseded |
| R7 | withdrawals by calendar year, IMMEDIATE | table in NOTES_JX §2 | `CHK0908` §2 | W0908 | 2026-11-06 | current |
| R8 | share of withdrawals in 2024–2026 | 44.5% (W1028: 47.5%) | `CHK0908` / `CHK1028` §2 | | 2026-11-06 | current |
| R9 | net 2016–2023 while strategy lost $45,617 | +$22,336 | same | both | 2026-11-06 | current |
| R10 | net in the 5 years the strategy lost | −$1,351 | same | both | 2026-11-06 | current |
| R11 | stress test, one change at a time | NOTES_JX §3 | `CHK0908` / `CHK1028` §3 | both | 2026-11-06 | current |
| R12 | all five changes together | −$12,352 (W1028: −$11,910) | same | | 2026-11-06 | current |
| R13 | "7/11 profitable years, first three lose" (GO_LIVE 167) | 7/11 | `ASOF scripts/recycling_report.py ...` "by calendar year" | W0908 | 2026-11-06 | superseded: LOCK_FIRST. IMMEDIATE version not computed. |

## Recycling under current rules (RB1106) — supersedes R1–R13 where they overlap

`CHKN` = `uv run python scripts/jx_checks.py --skip-strategy`;
`CHKN0908` = the same with `--end 2026-09-08T05:27Z`.

| # | figure | value | command | window | computed | status |
|---|---|---|---|---|---|---|
| N1 | **current policy** | **LOCK_FIRST** (beats IMMEDIATE at $500/$900/$1,000) | `CHKN` §1, plus the per-size comparison in NOTES_JX | W1028 | 2026-11-06 | **current**. Supersedes R3's "IMMEDIATE is current". |
| N2 | chain, LOCK_FIRST: withdrawn / spent / net | $62,065 / $17,475 / **$44,590** | `CHKN` §1 | W1028 | 2026-11-06 | **current** |
| N2b | same | $58,450 / $17,314 / $41,136 | `CHKN0908` §1 | W0908 | 2026-11-06 | current for W0908 |
| N3 | chain, IMMEDIATE | $61,264 / $18,310 / $42,954 | `CHKN` §1 | W1028 | 2026-11-06 | current (not the policy) |
| N4 | longest no-payout / bust streak, LOCK_FIRST | 1,184 days / 39 | `CHKN` §1 | both | 2026-11-06 | current. R5/R6's 1,184 and 39 are current again. |
| N5 | 2024–2026 share of withdrawals | 50.0% | `CHKN` §2 | W1028 | 2026-11-06 | current |
| N6 | 2016–2023 net / 5 losing years net | +$18,602 / −$2,473 | `CHKN` §2 | W1028 | 2026-11-06 | current |
| N7 | stress, LOCK_FIRST: no lock / all five | −$17,079 / −$33,825 (no payouts at all) | `CHKN` §3 | W1028 | 2026-11-06 | current. Policy artefact, see NOTES_JX. |
| N8 | stress, IMMEDIATE: no lock / all five / worst pair | $21,166 / −$11,875 / $4,925 | `CHKN` §3 | W1028 | 2026-11-06 | current |
| N9 | 5-account table, $900, n=1/3/5/8/10 net | $44,590 / $137,539 / **$230,488** / $183,718 / $152,538 | `uv run python scripts/account_lifetime.py --orders ORDALL` | W1028 | 2026-11-06 | **current**. Supersedes A1/A1b. |
| N10 | funded mortality, $900 | 100% of 53 XFA; median life 11 trades / 20 days | same | W1028 | 2026-11-06 | current. Supersedes A2/A3. |
| N11 | staggered 5 chains, bust days shared | 151/161 (93.8%) | same | W1028 | 2026-11-06 | current. Supersedes A4. |

## Accounts (scripts/account_lifetime.py, IMMEDIATE, RB0914) — superseded by N9–N11

| # | figure | value | command | window | computed | status |
|---|---|---|---|---|---|---|
| A1 | 5-account table, $900: n=1/3/5/8/10 net | $44,868 / $138,345 / **$231,823** / $186,088 / $155,598 | `ASOF scripts/account_lifetime.py --orders ORD0908` | W0908 | 2026-11-06 | current for W0908 |
| A1b | same | $48,190 / $148,340 / **$248,489** / $202,313 / $171,529 | `uv run python scripts/account_lifetime.py --orders ORDALL` | W1028 | 2026-11-06 | current |
| A2 | funded mortality, $900 | **98%** of 52 XFA | `ASOF scripts/account_lifetime.py --orders ORD0908` | W0908 | 2026-11-06 | current for W0908 |
| A2b | same | 100% of 52 | `... --orders ORDALL` | W1028 | 2026-11-06 | current |
| A3 | funded median life, $900 | 12 trades / 20 days | same | both | 2026-11-06 | current |
| A4 | staggered 5 chains, bust days shared | 147/156 (94.2%) (W1028: 150/159, 94.3%) | same | | 2026-11-06 | current |

## Single-pass replay (scripts/quarterly_report.py, $900, from 2025-10-01)

| # | figure | value | command | window | computed | status |
|---|---|---|---|---|---|---|
| Q1 | time to first pass | **106 days**, 9 accounts | `ASOF scripts/quarterly_report.py --out /tmp/q.html` | W0908 | 2026-11-06 | current |
| Q1b | same | 106 days, 9 accounts | `uv run python scripts/quarterly_report.py --out /tmp/q.html` | W1028 | 2026-11-06 | current |
| Q2 | Standard vs No-Activation, first pass | $648 vs $823 | same | both | 2026-11-06 | current |

## ES unseen-market test (docs/ES_PREREG.md, pre-registered e24926e)

| # | figure | value | command | window | computed | status |
|---|---|---|---|---|---|---|
| E1 | ES recycling net, $900, 2016→2026-10-28 | **$20,338** (1,754 trades, PF 0.977, pass 32.3%) | `uv run python scripts/es_test.py` | ES 2016-01-01..2026-10-28 | 2026-11-09 | current |
| E2 | ES coin-flip median / 95th pct | $11,002 / $24,180 (real beats 86%) | same | same | 2026-11-09 | current |
| E3 | **ES verdict** | **does not confirm** (E1 < E2 95th pct) | same | same | 2026-11-09 | current |
| E4 | ES 2010-07..2015 (context) | net $2,478, PF 0.873, beats 95% of flips | same | ES 2010-07-01..2015-12-31 | 2026-11-09 | current |
| E5 | NQ reproduction via es_test.py | $44,359 / flip 95th pct $36,711 → confirms | `uv run python scripts/es_test.py --market NQ` | W1028 | 2026-11-09 | current; matches N rows |

## Risk size, ES sensitivities, two accounts (docs/PREREG_20261109.md, pre-registered ab112d1)

| # | figure | value | command | window | computed | status |
|---|---|---|---|---|---|---|
| K1 | risk-size verdict | **$900 stays** ($1,200/$1,500 higher in 3/4 datasets, not ES 2010–15) | `uv run python scripts/jx_ideas_20261109.py` | NQ/ES, both windows | 2026-11-09 | current |
| K2 | NQ 2016–26 net at $500/700/900/1200/1500 | $15,800 / $31,137 / $44,359 / $73,960 / $69,240 | same | W1028 | 2026-11-09 | current |
| K3 | ES 2016–26, $0.74 commission (post-hoc) | $27,587, beats 90% of flips | same | ES SEEN | 2026-11-09 | current, exploratory |
| K4 | ES 2016–26, settings × 0.31 (post-hoc) | $31,672, beats **100%** of flips (95th pct $23,998) | same | ES SEEN | 2026-11-09 | current, exploratory; tested on YM/RTY next |
| K5 | NQ + ES side by side | net $64,697; deepest −$4,444; payout months 32% (NQ alone 20%); flow corr 0.14 | same | SEEN | 2026-11-09 | current, descriptive |

## YM / RTY unseen-market tests (docs/PREREG_YM_RTY.md, pre-registered 23b0c8a)

| # | figure | value | command | window | computed | status |
|---|---|---|---|---|---|---|
| Y1 | YM unchanged: net / flip 95th pct | $11,744 / $10,714 → confirms (narrowly; beats 96%) | `uv run python scripts/ym_rty_test.py` | YM 2016-01..2026-10 | 2026-11-09 | current |
| Y2 | YM scaled ×2.55 | $11,593 / $14,671 → does not confirm | same | same | 2026-11-09 | current |
| Y3 | RTY unchanged | −$2,293 / $17,352 → does not confirm (beats 12%) | same | RTY 2017-08..2026-10 | 2026-11-09 | current |
| Y4 | RTY scaled ×0.14 | $8,928 / $11,849 → does not confirm | same | same | 2026-11-09 | current |
| Y5 | **scaled hypothesis** | **not supported** (0 of 2) | same | | 2026-11-09 | current; K4 treated as chance |
| Y6 | unchanged, beats coin flips | NQ 98%, YM 96%, ES 86%, RTY 12% | es_test.py, ym_rty_test.py | 2016→ | 2026-11-09 | current |

## Idea batch (docs/PREREG_BATCH_20261109.md, pre-registered fb76f72)

| # | figure | value | command | window | computed | status |
|---|---|---|---|---|---|---|
| B1 | batch verdict | 1 pass of 12: **#28 120-min time stop** | `uv run python scripts/idea_batch_20261109.py` | 5 datasets | 2026-11-09 | current |
| B2 | #28 recycling net vs baseline | NQ $45,554 vs $44,359; ES $24,638 vs $20,338; YM $2,020 vs $11,744; RTY −$1,745 vs −$2,293 | same | | 2026-11-09 | current |
| B3 | #28 margin over coin flip vs baseline | NQ-S 29,172 vs 25,548; NQ-O 1,866 vs 1,679 | same | | 2026-11-09 | current |

## Account size and payout path (scripts/account_size_test.py, NQ, risk = 0.45 × MLL)

Not pre-registered; describes account choice, not the strategy. The 100K/150K
funded scaling ladders are assumed (50K × 2 / × 3), and so is a $150 winning
day at every size.

| # | figure | value | command | window | computed | status |
|---|---|---|---|---|---|---|
| Z1 | net per account, 2016–26: 50K / 100K / 150K, Standard | $44,359 / $62,660 / $95,324 | `uv run python scripts/account_size_test.py` | W1028 | 2026-11-09 | current |
| Z2 | deepest cash, same | −$3,520 / −$7,152 / −$9,952 | same | same | 2026-11-09 | current |
| Z3 | net per account, 2010–15, Standard | −$2,505 / −$5,144 / −$9,484 | same | 2010-07..2015 | 2026-11-09 | current |
| Z4 | Consistency path vs Standard, 2016–26 | 50K +$2,133; 100K +$3,444; 150K +$6,504. 2010–15: worse or equal | same | | 2026-11-09 | current |

## Timing patterns and Topstep cost structure (docs/PREREG_20261120.md, pre-registered 005220e)

| # | figure | value | command | window | computed | status |
|---|---|---|---|---|---|---|
| T1 | timing patterns (overnight, turn of month, pre-FOMC, gap fade, day of week) | **all fail**; NQ overnight SEEN +4.3 pts/night, t 1.66 | `uv run python scripts/patterns_20261120.py` | OLD / SEEN, 4 markets | 2026-11-20 | current |
| T2 | Back2Funded always / once vs never, NQ 2016–26 net | $55,663 / $53,764 vs $44,359 | `uv run python scripts/topstep_costs_20261120.py` | W1028 | 2026-11-20 | current |
| T3 | same, 2010–15 net | −$6,549 / −$4,737 vs −$2,505 → **fail** | same | 2010–15 | 2026-11-20 | current |
| T4 | doubled payout caps, change in 2016–26 net: 50K / 100K / 150K | +$329 / −$6,580 / −$9,287 | same | W1028 | 2026-11-20 | current |

## Lucid comparison (docs/PREREG_LUCID_20261120.md, pre-registered ddce1b3)

| # | figure | value | command | window | computed | status |
|---|---|---|---|---|---|---|
| L1 | LucidFlex 50K net / withdrawn / spent, $900 | $37,523 / $55,723 / $18,200 | `uv run python scripts/lucid_test_20261120.py` | W1028 | 2026-11-20 | current; prices and lock rule third-party |
| L2 | LucidFlex worst cash dip over 118 starts / beats coin flips | −$4,720 / 98% | same | W1028 | 2026-11-20 | current |
| L3 | LucidFlex 2010–15 net | −$701 | same | 2010–15 | 2026-11-20 | current |

## Crypto and prediction-market top-10 (PREREG_TOP10_20261120, bb5f06e; PREREG_POSTLISTING_20261120, 616bb9c)

| # | figure | value | command | window | computed | status |
|---|---|---|---|---|---|---|
| X1 | top-10 verdicts N1–N7 | N1–N3, N5, N6 fail; N4 no data; N7 not testable | `uv run python scripts/top10_20261120.py` | per test | 2026-11-20 | current |
| X2 | N5 stETH discount capture | ~$40–50 a year per $10K | same | 2023-04..2026-11 | 2026-11-20 | current |
| X3 | post-listing short, 2023 holdout (daily) | mean −$110.86 per $1,000 per 14d; 27% squeezed ≥ 50%; worst −$2,936 → **fail** | `uv run python scripts/postlisting_20261120.py --daily` | 79 listings 2023 | 2026-11-20 | current |

## Structure scan (docs/PREREG_STRUCTURE_SCAN_20261120.md, 3a29e05)

| # | figure | value | command | window | computed | status |
|---|---|---|---|---|---|---|
| G1 | coin-flip median net: Topstep 150K Cons / 150K Std / 50K Std / LucidFlex 50K / Tradeify Flex 50K | $34,116 / $30,319 / $18,046 / $18,519 / $11,110 | `uv run python scripts/structure_scan_20261120.py` | 2016–26 | 2026-11-20 | current; Lucid/Tradeify rules partly third-party |
| G2 | share of coin flips that profit, Topstep 50K Standard | 98% | same | 2016–26 | 2026-11-20 | current |

## Non-prop loophole hunt (docs/PREREG_LOOPHOLES_20261120.md)

| # | figure | value | command | window | computed | status |
|---|---|---|---|---|---|---|
| H1 | IPO value per RM applied r/(1+X), mean (halves) | 0.40% (1.69% / −0.76%) → FAIL | `uv run python scripts/ipo_test_20261120.py` | 19 IPOs 2024-05..2026-11 | 2026-11-20 | current; hand-collected sample |
| H2 | IPO avg profit per application, mean / median; RM/yr at 55 IPOs | RM311 / RM201; RM17.1K (mean), 90% range RM5.2K–31.1K | same | same | 2026-11-20 | post-hoc metric |
| H3 | FTMO 100K coin-flip median net at 1% / 2% / 3% risk | −$2,570 / $32,683 / $93,174 | `uv run python scripts/static_dd_20261120.py` | 2016–26 | 2026-11-20 | rules third-party; 2–3% risk may breach FTMO practices |
| H4 | FTMO 100K real strategy net at 1% / 2% risk | $38,694 / $142,746 | same | 2016–26 | 2026-11-20 | same caveats |

Raw output for every command above is in `docs/jx_runs/`.

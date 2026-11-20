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
| H5 | Luno premium over Kraken × USD/MYR (BTC/ETH/SOL/XRP), 6 snapshots | +0.38% to +0.55% | `uv run python scripts/myx_gap_20261120.py` | 2026-11-20 02:31–03:23 UTC | 2026-11-20 | FX ref rate is daily |
| H4 | FTMO 100K real strategy net at 1% / 2% risk | $38,694 / $142,746 | same | 2016–26 | 2026-11-20 | same caveats |

## FTMO Futures vs Topstep (docs/PREREG_FTMO_FUTURES_20261120.md)

| # | figure | value | command | window | computed | status |
|---|---|---|---|---|---|---|
| F1 | real net: Topstep 50K / FTMO Fut Growth 50K / Pro 50K (100%) / Pro (50%) | $44,359 / $34,236 / $28,452 / $27,671 | `uv run python scripts/ftmo_futures_20261120.py` | 2016–26 | 2026-11-20 | FTMO rules third-party; reset price & ladder assumed |
| F2 | coin-flip median: same order | $18,046 / $1,906 / $1,523 / −$4,836 | same | 2016–26 | 2026-11-20 | same |
| F3 | worst dip: same order | −$3,520 / −$9,675 / −$9,310 / −$10,825 | same | 2016–26 | 2026-11-20 | same |
| F4 | FTMO Fut Growth / Pro net if renewal includes a free reset | $48,297 / $41,352 | sensitivity lines in the same output file | 2016–26 | 2026-11-20 | renewal-reset rule unverified |

## TradeDay / Bulenox vs Topstep (docs/PREREG_FIRMS2_20261120.md)

| # | figure | value | command | window | computed | status |
|---|---|---|---|---|---|---|
| F5 | real net: TradeDay FP 50K $85/mo / $189/mo / Bulenox Momentum 50K | $35,678 / $22,158 / −$4,139 | `uv run python scripts/firms2_20261120.py` | 2016–26 | 2026-11-20 | rules third-party; some assumed |
| F6 | coin-flip median: same order | $14,035 / −$4,213 / −$14,622 | same | 2016–26 | 2026-11-20 | same |
| F7 | worst dip: same order | −$4,835 / −$10,035 / −$10,840 | same | 2016–26 | 2026-11-20 | same |

## Global round 1 (docs/PREREG_GLOBAL_20261120.md)

| # | figure | value | command | window | computed | status |
|---|---|---|---|---|---|---|
| G3 | Breakout Classic 50K, 10x cap: real net (risk ≤$950 refund/no; ≤$1,250 refund/no) | $44,663 / $38,263; $57,215 / $49,215 | `uv run python scripts/global_round1_20261120.py` | 2016–26 | 2026-11-20 | rules third-party; bot policy unpublished |
| G4 | same, coin-flip median | $15,203 / $10,679; $24,507 / $17,863 | same | 2016–26 | 2026-11-20 | same |
| G5 | NQ trade leverage on 50K at $950 risk: median / p10 / p90 | 13.3x / 5.5x / 29.4x | inline check in session (micros × entry × $2 / 50K) | 2016–26 | 2026-11-20 | current |
| G6 | Tradeify Lightning 50K real net, cap $2,000 / $1,500 | $40,998 / $20,196 | same as G3 | 2016–26 | 2026-11-20 | cap unverified |

## Round 3 futures firms (docs/PREREG_ROUND3_20261120.md, pre-registered 486c51f)

| # | figure | value | command | window | computed | status |
|---|---|---|---|---|---|---|
| R1 | real net: Topstep 50K / MFFU Rapid EOD 50K / TFD Static Core / TFD Static Pro | $44,359 / $34,481 / $10,680 / $20,248 | `uv run python scripts/round3_20261120.py` | 2016–26 | 2026-11-20 | MFFU funded rules official; prices third-party; TFD from its own plans page |
| R2 | coin-flip median, same order (share profitable) | $18,046 (98%) / $7,358 (74%) / −$1,163 (38%) / $3,274 (71%) | same | 2016–26 | 2026-11-20 | same |
| R3 | worst dip, same order | −$3,520 / −$5,590 / −$3,226 / −$3,667 | same | 2016–26 | 2026-11-20 | same |
| R4 | TFD Core if payouts may go down to the floor (unconfirmed reading) | $18,253 real / $3,068 coin flip | same | 2016–26 | 2026-11-20 | upper bound only |

## Non-prop round 2 (docs/PREREG_NONPROP2_20261120.md, pre-registered f1eef1e)

| # | figure | value | command | window | computed | status |
|---|---|---|---|---|---|---|
| P1 | funding carry return on capital: rotating top-3 / BTC+ETH held | 2.9%/yr / 6.4%/yr | `uv run python scripts/nonprop2_20261120.py` | HL 2024-01..2026-11 | 2026-11-20 | basis and venue risk not modelled |
| P2 | capital to make $4,098/yr: rotating / held | $139,858 / $64,293 | same | same | 2026-11-20 | same |
| P3 | friend's NQ trades on own money, $900 risk: net / max DD | −$2,553 / −$73,445 | same | 2016–26 | 2026-11-20 | current |
| P4 | same, 2016–20 / 2021–26 | −$60,133 / +$57,580 | same | same | 2026-11-20 | current |

## Multi-firm portfolio (docs/PREREG_PORTFOLIO_20261120.md, pre-registered 0922084; addendum before part 2)

| # | figure | value | command | window | computed | status |
|---|---|---|---|---|---|---|
| M1 | net 2016–26: A Topstep×1 / B 4 firms ×1 / B− no Breakout / C max slots / C− | $44,359 / $154,625 / $116,362 / $551,113 / $512,850 | `uv run python scripts/portfolio_20261120.py` | 2016–26 | 2026-11-20 | firm caveats as per component prereg |
| M2 | worst dip (= cash on hand), same order | $3,520 / $22,853 / $13,829 / $66,990 / $57,966 | same | same | 2026-11-20 | same |
| M3 | monthly P&L correlation between firms | 0.80–0.88 | same | same | 2026-11-20 | same |
| M4 | coin flip, B: median net / profitable / 5th-pct worst dip | $51,287 / 94% / −$36,350 | same | same | 2026-11-20 | same |
| M5 | year-one net median, A / B− (share of starts losing) | $1,704 (32%) / $5,127 (35%) | `uv run python scripts/portfolio_starts_20261120.py` | starts 2016-01..2025-10 | 2026-11-20 | same |
| M6 | worst year-one out of pocket, A / B− | −$1,906 / −$6,722 | same | same | 2026-11-20 | same |

## Live-account predictions (docs/PREREG_LIVE_20261120.md)

| # | figure | value | command | window | computed | status |
|---|---|---|---|---|---|---|
| L1 | trades/month; fill rate; win rate; mean net R (full / recent) | 16.8 / 16.9; 80% / 79%; 53.1% / 55.6%; −0.001 / +0.083 | `uv run python scripts/live_predictions_20261120.py` | 2016-01..2026-10 / 2024-01..2026-10 | 2026-11-20 | prediction |
| L2 | cumulative net R after 40 trades, 5/50/95% (full / recent) | −10.8/+0.2/+11.9 / −8.7/+3.4/+14.6 | same | same | 2026-11-20 | prediction |
| L3 | Topstep 50K days to first pass, median (full / recent) | 36 / 26 | same | monthly starts | 2026-11-20 | prediction |
| L4 | Topstep 50K net after 3 / 6 / 12 months, median (full) | −$338 / $96 / $1,704 | same | monthly starts | 2026-11-20 | prediction |
| L5 | same, recent | −$244 / $713 / $8,354 | same | monthly starts 2024-01..2025-10 | 2026-11-20 | prediction |

## Portfolio 2: staggered starts, corrected costs (docs/PREREG_PORTFOLIO2_20261120.md, 5fe8339)

| # | figure | value | command | window | computed | status |
|---|---|---|---|---|---|---|
| Q1 | net 2016–26: B−c / C−sync / C−stag | $113,827 / $532,382 / $531,867 | `uv run python scripts/portfolio2_20261120.py` | 2016–26 | 2026-11-20 | current; supersedes M1 B−/C− for planning |
| Q2 | cash on hand: B−c / C−sync / C−stag | $14,590 / $49,792 / $50,502 | same | same | 2026-11-20 | same |
| Q3 | stagger vs sync: net / cash | −0.1% / +1.4% (not worth it) | same | same | 2026-11-20 | current |

## Market mix across accounts (docs/PREREG_MARKETMIX_20261120.md, 871e435; addendum before part 2)

| # | figure | value | command | window | computed | status |
|---|---|---|---|---|---|---|
| X1 | monthly correlation NQ–ES / NQ–YM / ES–YM (compliant) | 0.25 / −0.05 / −0.10 | `uv run python scripts/marketmix_20261120.py --compliant` | 2016–26 | 2026-11-20 | current |
| X2 | 5 Topstep all NQ vs 3NQ/1ES/1YM: net / cash on hand | $229,334 / $15,336 vs $176,902 / $4,741 | same | same | 2026-11-20 | current |
| X3 | 5T/5L/3M all NQ vs mixed: net / cash on hand | $529,425 / $52,994 vs $415,303 / $21,097 | same | same | 2026-11-20 | current; planning figure |
| X4 | trades skipped by anti-hedge filter: NQ / ES / YM | 69 / 54 / 85 | same | same | 2026-11-20 | current |

## Account size inside the market mix (docs/PREREG_SIZEMIX_20261120.md)

| # | figure | value | command | window | computed | status |
|---|---|---|---|---|---|---|
| S1 | 5 Topstep mixed, net: 50K / 100K / 150K | $176,902 / $254,379 / $383,019 | `uv run python scripts/sizemix_20261120.py` | 2016–26 | 2026-11-20 | 100K/150K ladders assumed |
| S2 | same, cash on hand | $4,741 / $22,578 / $33,749 | same | same | 2026-11-20 | same |

Raw output for every command above is in `docs/jx_runs/`.

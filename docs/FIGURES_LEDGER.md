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

## FundedNext Futures addition (docs/PREREG_FUNDEDNEXT_20261120.md)

| # | figure | value | command | window | computed | status |
|---|---|---|---|---|---|---|
| F8 | FundedNext Rapid Pro 50K single NQ account, real net cap $1,000 / $1,250 | $14,482 / $21,416 | `uv run python scripts/fundednext_20261120.py` | 2016–26 | 2026-11-20 | payout share, cap, lock third-party |
| F9 | C-mix vs C-mix + 5 FundedNext: net / cash on hand | $415,303 / $21,097 vs $461,630 / $39,424 | same | same | 2026-11-20 | same |

## Manual entry delay (docs/PREREG_DELAY_20261121.md)

| # | figure | value | command | window | computed | status |
|---|---|---|---|---|---|---|
| D1 | Topstep 50K net at 0/1/2/3/5-min entry delay, 2016–26 | $44,359 / $43,516 / $43,986 / $37,348 / $27,080 | `uv run python scripts/delay_20261121.py` | 2016–26 | 2026-11-21 | current |
| D2 | same, 2024–26 | $25,172 / $20,401 / $22,720 / $21,028 / $15,077 | same | 2024–26 | 2026-11-21 | current |

Raw output for every command above is in `docs/jx_runs/`.

## Liquidation bonuses (docs/PREREG_LIQUIDATIONS_20261120.md)

| # | figure | value | command | window | computed | status |
|---|---|---|---|---|---|---|
| LQ1 | Registered test: venues passing / overall | 7 pass; OVERALL PASS = True | `uv run python -I scripts/liquidations_20261120.py` | 2024-11..2026-10, 8 chains | 2026-11-21 | measured (net = bonus − gas only; BNB, Solana, Compound forks unmeasured) |
| LQ2 | Combined outside-top-3 net bonus, passing venues, H1 / H2 | $1.70M / $1.09M per month | same | halves | 2026-11-21 | measured; sum over all other winners, not one bot |
| LQ3 | Top-3 share (tx from) H1 / H2: Arbitrum v3, Base v3, Avalanche v3, Polygon v3, Optimism v3 | 0.30/0.09, 0.36/0.11, 0.41/0.26, 0.17/0.09, 0.19/0.38 | same | halves | 2026-11-21 | measured |
| LQ4 | Same with winner = liquidator field: venues passing | 5 (Arbitrum v3 fails, H2 top-3 0.62) | same | halves | 2026-11-21 | measured sensitivity |
| LQ5 | Median active (>= 12 wins) bot outside top 3, net $/month H2: Arbitrum / Base / Avalanche / Optimism / Polygon (Aave v3) | $226 / $31 / $729 / $0 / $83 | same | H2 | 2026-11-21 | measured, gas-only, survivor-biased |
| LQ6 | Same, 75th percentile H2 | $839 / $473 / $1,892 / $56 / $516 | same | H2 | 2026-11-21 | measured, same caveats |
| LQ7 | Debt repaid in passing Aave v3 pools, H1 → H2 | roughly halved ($70M → $41M Arbitrum; $42M → $32M Base) | same | halves | 2026-11-21 | measured; income depends on volatility |
| LQ8 | Chains complete / unmeasured | 8 complete; BNB unmeasured | `data/public/liq_*_state.json`; `docs/jx_runs/fetch_liq_*` | | 2026-11-21 | measured |

## Liquidation monthly lumpiness (docs/PREREG_LIQ_MONTHLY_20261121.md)

| # | figure | value | command | window | computed | status |
|---|---|---|---|---|---|---|
| M1 | 24-month gross bonus, five main pools; share from top 3 / top 5 months | $44.95M; 54.2% / 70.3% | `uv run python -I scripts/liq_monthly_20261121.py` (output `docs/jx_runs/liq_monthly_20261121.txt`, re-run identical) | 2024-11..2026-10 | 2026-11-21 | measured |
| M2 | Months with gross bonus under $200K | 10 of 24 | same | same | 2026-11-21 | measured (Jx quoted 11) |
| M3 | Biggest months, gross bonus | 2025-02 $12.0M, 2025-10 $6.9M, 2026-02 $5.4M, 2025-11 $4.2M, 2025-04 $3.1M | same | same | 2026-11-21 | measured (Jx quoted $11.2M / $6.6M / $5.1M / $4.0M) |
| M4 | Months above $3M / above $1M gross | 6 of 24 / 9 of 24 (counted from the month table) | same | same | 2026-11-21 | measured |
| M5 | Median active non-top-3 bot (zeros included): months under $200 / $200–1,000 / over $1,000 | 23 / 1 / 0 of 24 | same | same | 2026-11-21 | measured, gas only |
| M6 | Median bot that won at least once: months under $200 / $200–1,000 / over $1,000 | 17 / 6 / 1 of 24 | same | same | 2026-11-21 | measured, gas only |
| M7 | Outside-top-3 net, 24 months pooled; share from top 3 / top 5 months | $10.0M; 52.4% / 73.7% | same | same | 2026-11-21 | measured, gas only |
| M8 | Months since the March 2026 SVR switch with gross bonus above $1M | 1 of 8 (June 2026, $1.94M); the other 7 were $18K–$130K | same | 2026-03..2026-10 | 2026-11-21 | measured |

## Radar, workstream C (docs/PREREG_RADAR_20261121.md)

| # | figure | value | command | window | computed | status |
|---|---|---|---|---|---|---|
| RD1 | Radar baseline sweep counts (run 44885195094) | 9,086 protocols; 14,884 pools, 1,295 paying rewards; 714 live Merkl campaigns; 67 incentive-related Snapshot proposals (of 373 in 45 days); 1,287 of 1,317 pages fetched | Actions `radar.yml` → `scripts/radar.py`; log `docs/jx_runs/radar_44885195094.txt` | snapshot 2026-11-21 | 2026-11-21 | measured (live sources; not reproducible later by design) |
| RD2 | Candidates surviving screening / all five filter parts verified / near-miss rows | 93 / 12 / 1,963 | same | same | 2026-11-21 | measured |
| RP1 | Alpha Futures Standard 50K, manual entry 3 min late: real net / coin-flip median (profitable) / worst dip | $40,155 / $8,998 (81%) / −$4,773 (flag needs ≥ −$4,641: not flagged) | `uv run python scripts/radar_price.py` → `docs/jx_runs/radar_price_20261121.txt` | 2016-01..2026-10 | 2026-11-21 | current, re-run identical |
| RP2 | Topstep 50K reference at 3-min delay: real / coin flip / dip | $37,348 / $14,701 / −$3,094 | same | same | 2026-11-21 | current |
| RP3 | Blue Guardian Elite 50K, 3-min delay, purchase price bracket $141 / $350 (sensitivity only; price not readable) | real $43,877 / $37,398; coin flip $6,442 / −$1,457 | same | same | 2026-11-21 | sensitivity, not ranked |
| RP4 | Existing models re-priced by the radar (no delay) match the ledger: Topstep, Lucid, MFFU, TradeDay, Bulenox, FTMO Growth, TFD | identical to G1/F1/R1/F5/F6/F8/R2 values; except FTMO Pro: $27,428 / $1,810 vs ledger F1 $28,452, because this script scales the $900 trades to $800 instead of re-simulating at $800 (contract rounding) | same | same | 2026-11-21 | current |
| RT1 | #201 Lista stables: Stage 1 net (last 60 d) | 4.61%/yr (kill < 8%) | `uv run python scripts/incentives_w1_20261121.py` → `docs/jx_runs/incentives_w1_20261121.txt` | 2026-09-22..2026-11-21 | 2026-11-21 | current, re-run identical (data `data/radar/charts.parquet`, radar run 5) |
| RT2 | #202 Dolomite stables: Stage 1 net | 6.38%/yr (kill) | same | same | 2026-11-21 | current |
| RT3 | #203 Bluefin USDSUI-USDC: Stage 1 / half 1 / half 2 net; worst 7-day TVL ratio; $ on $10K | 13.75% / 22.92% / 16.26%; 0.32 (loss proxy hit); $1,962/yr | same | 2026-03-04..2026-11-21 | 2026-11-21 | current; assumptions: T-bill 4%, 10% reward haircut, $5/tx Ethereum |

## Liquidation replay: price-update gap, gas bidding, competition by size (docs/PREREG_LIQ_REPLAY_20261121.md, addenda 1–5)

| # | figure | value | command | window | computed | status |
|---|---|---|---|---|---|---|
| RP1 | Registered screen (ideal arm, 4 feed-ok chains: Arbitrum, Base, Avalanche, Polygon): pooled reachable share by count / by value; verdict | 13.1% / 10.1%; PLAUSIBLE (4 of 4 venues >= 10% by count) | `uv run python -I scripts/liq_replay_20261121.py 2` (output `docs/jx_runs/liq_replay_20261121.txt`, re-run identical; data `data/public/liq_replay_gaps_s2_*`, fetch logs `docs/jx_runs/liq_replay_s2_*`) | liquidations > $50 bonus, 2026-04-01..2026-10-31, 1,204 resolved events | 2026-11-21 | measured; UPPER BOUND (assumes instant detection); Base uses latest oracle source and a 1,000-block window (addendum 4) |
| RP2 | Share of liquidations landing in the SAME block as a price update of their feed: Arbitrum / Base / Avalanche / Polygon | 63.8% / 77.9% / 65.7% / 76.1% (random blocks: ~0) | same | same | 2026-11-21 | measured |
| RP3 | Reachable share by count / by value per venue (ideal arm, delay 2–3 blocks): Arbitrum, Base, Avalanche, Polygon | 15.0%/10.0%, 10.4%/12.5%, 10.4%/10.3%, 15.8%/8.2% | same | same | 2026-11-21 | measured |
| RP4 | Post-hoc: reachable share by count / by value if our delay is 5 blocks: Arbitrum, Base, Avalanche, Polygon | 12.3%/9.3%, 8.6%/10.1%, 6.7%/9.5%, 7.9%/4.0% | same | same | 2026-11-21 | measured, post-hoc descriptive |
| RP5 | Post-hoc month split, pooled ideal arm: June 2026 vs other window months, by count / by value | 13.7%/10.9% (953 events) vs 10.8%/6.5% (251 events) | same | same | 2026-11-21 | measured, post-hoc descriptive |
| RP6 | Optimism excluded by the feed check | 93% of resolved events show no update of the resolved feed in the window; its 96% reachable share is not credible | same | same | 2026-11-21 | measured data-quality failure (feed not resolved) |
| RP7 | Winner gas / bonus, median, by bonus size ($50–200 / $200–1K / $1K–5K / > $5K): Arbitrum, Base | 0.11%/0.04%/0.01%/0.00%; 0.97%/0.34%/0.05%/0.01% | same | last 12 months, 5 pools | 2026-11-21 | measured, gas only |
| RP8 | Winner gas / bonus, 90th percentile, $50–200: Base / Avalanche / Optimism | 8.1% / 9.3% / 37.9% | same | same | 2026-11-21 | measured |
| RP9 | Share of bonus won by addresses with >= 50 wins, events above $200 (range over size buckets): Arbitrum / Avalanche / Polygon / Base / Optimism | 72–90% / 92–97% / 89–91% / 41–61% / 36–50% | same | same | 2026-11-21 | measured |
| RP5 | FuturesElite Elite 50K (manual entry, 3-min delay; rules own FAQ, price $128 third-party): real / coin flip (profitable) / dip | $31,071 / $5,903 (79%) / −$2,560 → meets the pre-registered "extra slot" flag | `uv run python scripts/radar_price.py` | 2016-01..2026-10 | 2026-11-21 | current, re-run identical; corrected per addendum 6 (first run with assumed lock: $44,000, superseded) |
| RP6 | same at price $160 / $200 (sensitivity) | real $27,999, coin flip $2,383 (63%), dip −$3,200; real $24,159, coin flip −$2,160 (38%), dip −$4,525 → flag fails above ~$128–150 | command in `docs/jx_runs/radar_fe_corrected_20261121.txt` header | same | 2026-11-21 | sensitivity |
| RP7 | Goat Flex 50K / Blueberry Ascent 50K (bots): real / coin flip / dip | $23,784 / −$3,419 / −$6,322; $23,397 / −$4,016 / −$10,982 | `uv run python scripts/radar_price.py` | same | 2026-11-21 | current; prices third-party |
| FB1 | #204 stable yield rotation: Stage 1 / half 1 / half 2 net; loss-stress events | 13.23% / −6.53% / 4.79%; 7 | `uv run python scripts/fallback_20261121.py` → `docs/jx_runs/fallback_20261121.txt` | 2024-11..2026-10 | 2026-11-21 | current, re-run identical; data `data/public/fallback_*` (fallback fetch run 44898113814) |
| FB2 | #205 HLP vault: Stage 1 / half 1 / half 2 annualised; worst drawdown | 4.89% / 27.65% / 7.88%; −0.80% (sparse points) | same | same | 2026-11-21 | current |
| NR1 | #207 new stable rewards: events / taken / stress share; Stage 1; post-hoc no-stress halves | 242 / 100 / 26%; −61.7%/yr; 4.32% / −0.46% | `uv run python scripts/newrewards_20261121.py` | 2024-11..2026-10 | 2026-11-21 | current |
| PG1 | #210 programme halves: sUSDe / bUSD0 / sUSDf / Sky | 9.09%/4.30%; 13.02%/2.99%; 7.10%/4.87%; 5.48%/3.18% | `uv run python scripts/programmes_20261121.py` | 2024-11..2026-10 | 2026-11-21 | current |
| PM1 | Prop products, avg $/month 2016–26 (real): Topstep 50K / Alpha Std (3-min) / Lucid / TradeDay $85 / MFFU / FuturesElite (3-min) | $341 / $309 / $289 / $274 / $265 / $239; last-24-month avg $1,006 / $979 / $644 / $588 / $819 / $1,022 | `uv run python scripts/radar_monthly_20261121.py` | 2016-01..2026-10 | 2026-11-21 | current |
| CE1 | Stage 0.5 ceilings: #217 best-venue carry (HL leg, hindsight top 3 of 12 coins, 90 d) / #214 yCRV + CRV short funding / ETH, SOL, BTC hedged | 7.8% (kill) / 25.0% / 9.6%, 9.3%, 9.6% | `uv run python scripts/ceiling_20261121.py` → `docs/jx_runs/ceiling_20261121.txt` | HL funding to 2026-11-19; pools snapshot 2026-11-20 | 2026-11-21 | current, re-run identical |
| FG1 | #208 funding gaps pooled (SUPERSEDED: fees double-counted) | 7.58% / 13.79% / 4.43%; 111 / 124 | `uv run python scripts/fundgap_20261121.py` | 2024-11..2026-10 | 2026-11-21 | current, re-run identical |
| HG1 | #212 / #213 hedged staking / farming Stage 1 | −2.23% / −3.63% (KILL) | `uv run python scripts/hedged_20261121.py` | 2026-08..10 | 2026-11-21 | current, re-run identical |
| HG2 | #214 rule halves; with wrapper discount Stage 1; yCRV/CRV and cvxCRV/CRV ratio start→end | 8.32% / 15.52%; −162.5%; 0.977→0.555, 0.949→0.419 | `scripts/hedged_20261121.py`, `scripts/hedged_wrappers_20261121.py` | 2024-11..2026-10 | 2026-11-21 | current |
| HG3 | #216 gold carry halves | 7.07% / 5.12% | `uv run python scripts/goldcarry_20261121.py` | 2025-04..2026-10 | 2026-11-21 | current |
| B4a | #221 GM hedged: fee-APY halves; real GM prices halves | 21.82% / 10.10%; 3.62% / 3.18% | `scripts/batch4_20261121.py`, `scripts/gm_robust_20261121.py` | 2024-11..2026-10 | 2026-11-21 | current |
| B4b | #224 / #227 Stage 1; #225 primary / equal-weight halves; #222 days | −12.03% / 5.79%→halves 3.65% / −16.81%; 9.69%/4.39% vs 10.74%/13.22%; 67 days | `uv run python scripts/batch4_20261121.py` | same | 2026-11-21 | current |
| B5 | #228 SKY hedged halves (112 days); #229 ceilings ATOM / INJ | 12.85% / 16.86%; 4.93% / 12.06% | `scripts/sky_stage2_20261121.py`, `scripts/batch5_20261121.py` | 2026-07..10 | 2026-11-21 | current |
| BC | #209 ceiling; #219 corrected ceiling | 11.44%; 6.79% | `uv run python scripts/borrow_ceiling_20261121.py` | snapshot 2026-11-21 | 2026-11-21 | current |
| PD | #211 Pendle Stage 1 mean annualised | −7.04% (1 depeg in 9) | `uv run python scripts/pendle_20261121.py` | cohorts 2026-05..07 | 2026-11-21 | current |
| SP1 | #230 Liquity v2 SP deposits / total interest per year / max SP APY | $3,648 / ~$1,040 / 48.2% | Actions `fetch_fallback.py sp_data` → `data/public/sp_liquity_api.json` | snapshot 2026-11-22 | 2026-11-22 | measured (live API, not reproducible later) |
| RP8 | MFFU Builder 50K: $153 list / $107 code — real, coin flip (profitable), dip | $25,323, $2,022 (62%), −$6,732 / $32,453, $9,759 (85%), −$4,708 | `uv run python scripts/radar_price.py` | 2016-01..2026-10 | 2026-11-22 | current |
| RP9 | MFFU Studio #001 / #002 / #003: real; coin flip (profitable) | $7,551, −$2,528 (16%) / $15,602, −$3,770 (21%) / $3,249, −$1,775 (14%) | `uv run python scripts/radar_price_one.py mffu_studio` | 2016-01..2026-10 | 2026-11-22 | current, re-run identical |
| RP10 | TTP Futures Prime 50K ($99, third-party price): real / coin flip (profitable) / dip | $46,597 / $14,016 (95%) / −$4,884 | `uv run python scripts/radar_price_one.py ttp_prime50` | 2016-01..2026-10 | 2026-11-22 | current, re-run identical |
| RP11 | TTP sensitivity: $59.40 / $149 / $199 / 3-min delay — real, coin flip | $53,527, $21,704 / $37,847, $4,249 / $29,097, −$5,709 / $33,434, $10,732 | `uv run python scripts/ttp_sens_20261122.py` | same | 2026-11-22 | sensitivity |
| RP12 | Traders Launch 100K / 200K: real, coin flip | $722, −$13,645 / $4,371, −$24,351 | `uv run python scripts/radar_price_one.py traders_launch` | same | 2026-11-22 | current |
| RP13 | TTP Futures Prime 150K ($289): real / coin flip / dip | $43,662 / −$6,562 (38%) / −$19,074 | `uv run python scripts/radar_price_one.py ttp_prime150` | 2016-01..2026-10 | 2026-11-22 | current, re-run identical |
| RP14 | DayTraders EOD 50K at $99 / $199 (sensitivity; price unread): real, coin flip, dip | $48,602, $13,511 (89%), −$3,079 / $36,802, −$4,406 (29%), −$6,989 | `uv run python scripts/radar_price_one.py dt_eod50` | 2016-01..2026-10 | 2026-11-22 | sensitivity, re-run identical |
| RP15 | FuturesElite Elite 50K, 3-min delay, reset $89 (own page): real / coin flip / dip | $33,645 / $9,121 (91%) / −$2,014 | `uv run python scripts/radar_price_one.py fe_elite50 --delay` | same | 2026-11-22 | current (supersedes RP5) |

## Liquidation: Morpho Blue on Base (docs/PREREG_LIQ_MORPHO_20261121.md)

| # | figure | value | command | window | computed | status |
|---|---|---|---|---|---|---|
| MO1 | Stage-1 pilot gross bonus / events / winners / top-3 share | $2.39M / 6,600 / 848 / 0.28 | `uv run python -I scripts/liq_morpho_20261121.py pilot` (`docs/jx_runs/liq_morpho_20261121_pilot.txt`) | 2026-08-01..10-31 | 2026-11-21 | measured; not killed (line $3,750) |
| MO2 | Registered venue test (top-3 < 60%, events every month, outside-top-3 net >= $500/month), both halves | PASS: top-3 14.9% / 3.7%; 12/12 months both halves; outside-top-3 net $459K / $3.79M per month pooled | `uv run python -I scripts/liq_morpho_20261121.py full` (`docs/jx_runs/liq_morpho_20261121.txt`, re-run identical; data `data/public/liq_morphobase*`) | 2024-11..2026-10 | 2026-11-22 | measured, gas only, upper bound |
| MO3 | 24-month gross bonus; share of top 5 months; months under $200K | $54.1M; 89.1%; 12 of 24 | same | same | 2026-11-22 | measured |
| MO4 | Gross bonus since March 2026: Morpho Base vs five Aave pools | $12.1M vs $2.3M | same + `liq_monthly_20261121.txt` | 2026-03..2026-10 | 2026-11-22 | measured |
| MO5 | Share of value won by addresses with >= 50 wins (liquidator field), by size bucket | 81–86%; top 10 hold 48–52% | same | last 12 months | 2026-11-22 | measured |
| MO6 | Median active non-top-3 bot: months under $200 / over $1,000 (zeros included); winners only under 200 / 200–1,000 / over 1,000 | 23 / 1 of 24; 16 / 4 / 4 of 24 | same | same | 2026-11-22 | measured, gas only |
| B14 | Addendum 14 batch (#237–#258): flagged on verified/registered prices — TTP Prime 50K reset $79 $49,057 / $16,960 / −$3,884; FE Nitro 50K (3-min) $48,463 / $15,373 / −$4,331. Would flag at a bracket price only: TTP Instant $299, LucidDaily $99, MFFU Pro $127, DayTraders S2F $199, FE Prime $129/$229, FE Instant $199/$349, BG Reserve $150 | see `docs/jx_runs/radar_batch14_20261122.txt` | `uv run python scripts/radar_batch14_20261122.py` | 2016-01..2026-10 | 2026-11-22 | current, re-run identical |
| B6 | Batch 6 (#259–#278): #276 HYPE hedged staking halves 24.90% / 9.16% (Stage 1 9.93%), robustness year 2: 7.29% no staking, 8.15% at 2×, 6.48% both; #260 / #261 Stage 1 −0.25% / −5.67%; #263 / #278 Stage 1 −26.25% / −41.33%; #264 halves −37.93% / 6.47%; #267 Stage 1 −83.45%; ceilings #269 3.89%, #271 2.64%, #277 6.32%, #259 33.18%, #262 19.99% | see the PREREG final-results table | `scripts/batch6a/b/c/s_20261122.py`, `votium_20261122.py`, `hype_robust_20261122.py` | 2024-11..2026-11 | 2026-11-22 | current, re-runs identical |
| FG2 | #208 corrected (fee bug fixed): Stage 1 / halves; fees ×1.5 / ×2 halves | 13.30% / 20.30% / 11.87%; 17.05% / 8.15%; 13.79% / 4.43% | `uv run python scripts/fundgap_20261121.py`; `scripts/fundgap_sens_20261122.py` | 2024-11..2026-10 | 2026-11-22 | current, re-run identical |
| RF | Refinement R1–R7 chosen variants: year 1 / year 2 / year 2 costs ×1.5 | R1 24.86/17.08/15.96; R2 18.43/−10.20/−10.20; R3 −1.31/−31.76/−33.81; R4 0.65/−27.17/−29.14; R5 23.39/9.26/9.26; R6 11.62/9.79/9.79; R7 17.36/6.36/5.63 | `uv run python scripts/refine_20261122.py` | 2024-11..2026-10 | 2026-11-22 | current |
| WF1 | Walk-forward OOS halves / all-months costs ×1.5: G1 funding gaps; G5 HYPE; G6 Gains; G1 taker-only (post-hoc) | 12.80 / 18.22 / 14.45; 14.97 / 8.72 / 11.86; 9.61 / 14.06 / 11.46; 8.62 / 12.70 / 5.94 | `uv run python scripts/walkforward_20261122.py` | OOS 2025-05..2026-10 | 2026-11-22 | current, re-run identical |

| # | figure | value | command | window | computed | status |
|---|---|---|---|---|---|---|
| MR1 | Morpho Base: share of liquidations in the same block as an oracle price update / within 1 block | 93.8% / 97.9% (random blocks 0.3%) | `uv run python -I scripts/liq_morpho_replay_20261121.py 2` (`docs/jx_runs/liq_morpho_replay_20261121.txt`, identical on re-run; data `data/public/liq_replay_gaps_s2_morphobase.parquet`) | 397 sampled events, 2026-04..10 | 2026-11-22 | measured |
| MR2 | Reachable share for a watcher 2 blocks after the update: events / bonus value; registered verdict | 2.1% / 0.8%; DROP (< 5% and < 5%) | same | same | 2026-11-22 | measured upper bound at block-level latency |
| MR3 | Reachable share in stress months June 2026 / October 2026 / other months | 0.0% / 0.0% / 12.5% (value 10.5%) | same | same | 2026-11-22 | measured, descriptive |
| B7a | #225 gUSDC price-based vs APY-based return (549 days); OOS halves; costs ×1.5; verdict | 6.94% vs 10.67%/yr; 16.11% / −19.94%; 3.96%; FAIL | `uv run python -m scripts.batch7_20261122` (`docs/jx_runs/batch7_20261122.txt`, identical on re-run) | `data/public/batch7_gains_prices.parquet` (DefiLlama coins) | 2026-11-22 | measured (price feed noisy) |
| B7b | G9 Pendle walk-forward, 344 stable markets incl. expired: OOS halves; costs ×1.5; verdict | 0.82% / 7.85%; 2.86%; FAIL | same | `data/public/batch7_pendle_*.parquet` (Pendle API) | 2026-11-22 | measured |
| B7c | $10K market-order cost per side, median (Aevo / dYdX / HL); top-of-book median | 55.0 / 23.2 / 1.85 bps; $2,888 / $8,334 / $400 | same | `data/public/batch7_orderbooks.json` (647 books, 3 h, 2026-11-22) | 2026-11-22 | measured, one window |
| B7d | #276 with liquidations: count (1.5× / 2× / 3×); walk-forward halves; costs ×1.5; verdict | 2 / 3 / 12; 13.62% / −8.85%; 2.67%; FAIL | `uv run python -m scripts.batch8_20261122` part D (`docs/jx_runs/batch8_20261122.txt`, identical on re-run) | `data/public/batch7_hype4h.parquet` (HL candles) | 2026-11-22 | measured; 5% maintenance margin assumed |
| B8a | Batch 8 Stage 1 (2026-08..10): #280 / #288 / #284 / #281 / #282 / #285 | 12.72 / 27.30 / −2.08 / 2.62 / −30.81 / −4.13 %/yr | same | `data/public/batch8_raw.json` (Deribit, HL, Kamino, DefiLlama coins) | 2026-11-22 | measured; kill-only stage |
| B10a | #298 rows meeting the flag rule at 0 / 40 / 60 / 80% off (all 62; verified-price 35) | 18 / 39 / 52 / 55; 7 / 16 / 25 / 28 | `uv run python -m scripts.salewindow_20261122` (`docs/jx_runs/salewindow_20261122.txt`, identical on re-run) | friend's NQ trades 2016-01..2026-10 | 2026-11-22 | measured; resets discounted (optimistic) |
| B10b | #300 share-hedged stock-perp carry, Stage 1; #314 index perps | −13.28% / −2.21%/yr | `uv run python -m scripts.batch10_20261122` | `data/public/batch8_raw.json` HIP-3 funding 2026-08..10 | 2026-11-22 | measured |

## Liquidation best-case check (docs/PREREG_LIQ_BESTCASE_20261122.md)

| # | figure | value | command | window | computed | status |
|---|---|---|---|---|---|---|
| BC1 | Mean income per active non-top-3 bot-month, Aave five pools / Morpho Base: 24 months | $1,022 / $2,143 (median $0 for both) | `uv run python -I scripts/liq_bestcase_20261122.py` (`docs/jx_runs/liq_bestcase_20261122.txt`, re-run identical) | 2024-11..2026-10 | 2026-11-22 | measured, gas only |
| BC2 | Same, last 8 months (Mar–Oct 2026) | $587 / $881 (median $0) | same | 2026-03..10 | 2026-11-22 | measured, gas only |
| BC3 | Same, quiet months (venue gross < $200K) vs the 5 biggest months | $98 / $84 vs $3,127 / $5,351 | same | 24 months | 2026-11-22 | measured, gas only |
| BC4 | Parity case (one Aave-pool-sized plus one Morpho-sized entry): mean per month, 24 months / last 8 months | $3,165 / $1,468; "USD 500–1,500 best case" SUPPORTED as a parity case; new-bot parity unproven | same | same | 2026-11-22 | measured, gas only, upper bound |
| BC5 | Who wins same-block events (gap <= 1): distinct winners, top-3 / top-10 share, repeat-winner (>= 50 wins) share: Aave sample / Morpho sample | 109 winners, 0.38 / 0.71, 77% / 114 winners, 0.26 / 0.59, 75% | same | replay samples | 2026-11-22 | measured |
| BC6 | Fair share of the same-block pool per active bot, last 8 months: Aave five pools / Morpho Base | $815 / $4,322 a month, before costs (24-month figures $4,127 / $11,177) | same | same | 2026-11-22 | measured model, upper bound |
| S3a | #323 hedged extreme-funding harvest, Stage 1; coins/day above 100%/yr funding 2024 / 2025 / 2026 | −1.36%/yr; 1.3 / 0.1 / 0.1 | `uv run python -m scripts.sweep3_20261122` (`docs/jx_runs/sweep3_20261122.txt`, identical on re-run) | `data/public/hl_funding.parquet` | 2026-11-22 | measured |
| M300 | Months >= $300 / rolling-12m averaging >= $300/mo: Topstep 50K; Topstep+Lucid+TTP (1 each) | 20% / 39%; 27% / 61% (avg $341 and $1,007/mo; last 36 months $751 and $2,085/mo) | `uv run python -W ignore -m scripts.monthly300_20261122` (`docs/jx_runs/monthly300_20261122.txt`, identical on re-run) | friend's NQ trades 2016-01..2026-10 | 2026-11-22 | measured |
| B8s | #280 halves (registered); tradeable slice HL–Deribit BTC/ETH/SOL/XRP; #288 halves without survivorship | 16.28% / 9.86%; −1.42% / −0.17%; −5.60% / −4.86% | `uv run python -m scripts.batch8s_20261122` (`docs/jx_runs/batch8s_20261122.txt`, identical on re-run) | `data/public/batch8s_raw.json` | 2026-11-22 | measured |
| PV1 | Re-priced with official rules: Topstep Consistency path; TTP Instant at $499; LucidDaily corrected at $99/$199; FE Instant corrected | $46,492; $43,076 (no flag); $55,283 / $39,083; $39,117 | `uv run python -m scripts.prop_reprice_verified_20261122` (`docs/jx_runs/prop_reprice_verified_20261122.txt`, identical on re-run) | friend's NQ trades 2016-01..2026-10; rules from official pages (`data/public/propverify`) | 2026-11-22 | measured; rules verified per docs/PROP_VERIFY_20261122.md |
| PJ1 | Priced at Jx-supplied checkout prices: DayTraders EOD 50K $105; LucidDaily EOD eval $85.40 promo; LucidFlex DLL ON $80.50 promo | $47,894 / $12,461 / −$3,265; $57,486 / $24,093 / −$3,758; $39,455 / $20,175 / −$4,478 | `uv run python -m scripts.prop_price_jx_20261122` (`docs/jx_runs/prop_price_jx_20261122.txt`, identical on re-run) | friend's NQ trades 2016-01..2026-10; prices from Jx | 2026-11-22 | measured; prices third-party (Jx) |
| OW1 | #291 option wrap: real net; coin-flip median; worst dip | −$28,411; −$74,810 (0%); −$55,103 | `uv run python -m scripts.optionwrap_20261122` (`docs/jx_runs/optionwrap_20261122.txt`, identical on re-run) | friend's NQ trades 2016-01..2026-10; VXN (FRED) | 2026-11-22 | modelled (Black-Scholes at VXN; 0DTE assumed for all years) |

## Liquidation: newer chains and Compound v3 (PREREG_LIQ_NEWCHAINS_20261122.md, PREREG_LIQ_COMET_20261122.md)

| # | figure | value | command | window | computed | status |
|---|---|---|---|---|---|---|
| NC1 | Stage-1 pilot gross, best venue: Sonic / Linea / Ink / zkSync / Soneium (kill line $3,750) | $1,874 / $755 / $257 / $84 / $482: all killed | `uv run python -I scripts/liq_newchains_20261122.py pilot` (`docs/jx_runs/liq_newchains_20261122_pilot.txt`) | 2026-08..10 | 2026-11-22 | measured |
| NC2 | Mantle pool 0xcfa5ae7c2c: registered test; 24-month gross; share under $50 | PASS (top-3 0.51/0.45; outside-top-3 net $4,586/$2,079 a month pooled); $161,853; 10,789 of 11,146 events | `uv run python -I scripts/liq_newchains_20261122.py full` (`docs/jx_runs/liq_newchains_20261122.txt`) | 2024-11..2026-10 | 2026-11-22 | measured, gas only |
| NC3 | Mantle pool: mean / median income per active non-top-3 bot-month, H1 / H2 | $147 / $64; median $0 | inline analysis of the same data (script `liq_newchains_20261122.py` output plus `liq_bestcase` method) | same | 2026-11-22 | measured, gas only |
| CM1 | Compound v3 stage-1 pilot gross: Base / Arbitrum / Optimism / Polygon | $9.1K / $102.6K / $3.6K (killed) / $0 (killed) | `uv run python -I scripts/liq_comet_20261122.py pilot` | 2026-08..10 | 2026-11-22 | measured |
| CM2 | Compound v3 stage 2: venues passing | 0 (Base USDC Comet misses by one month in H2; Arbitrum USDC Comet misses H1 top-3 0.602 and one month) | `uv run python -I scripts/liq_comet_20261122.py full` | 2024-11..2026-10 | 2026-11-22 | measured |
| CM3 | Compound v3 main USDC Comets, 24-month gross: Base / Arbitrum; last 8 months | $2.45M / $1.83M; $45K / $59K | same | same | 2026-11-22 | measured |
| CM4 | Mean income per active non-top-3 bot-month, Base / Arbitrum USDC Comet: 24 months vs last 8 months | $1,558 / $723 vs $2 / $11 (median $0) | same data, bestcase method | same | 2026-11-22 | measured, gas only |
| CM5 | Buy transactions that also absorb in the same transaction: Base / Arbitrum USDC Comet | 66.9% (139 sampled) / 46.1% (269 sampled): MIXED | job `liq_comet_timing`, `docs/jx_runs/fetch_public_*` | all | 2026-11-22 | measured sample |
| PB1 | Frozen 50K baseline: LucidFlex DLL ON; LucidFlex DLL OFF; DayTraders EOD; Blueberry Ascent (expiry = reset) | $40,545; $34,770; $47,894; $30,747 | `uv run python -m scripts.prop_baseline_20261122` (`docs/jx_runs/prop_baseline_20261122.txt`, identical on re-run) | friend's NQ trades 2016-01..2026-10; inputs docs/radar/prop_assumptions_20261122.csv | 2026-11-22 | measured; inputs from Jx + official pages |
| B9 | MYR benchmark 2006–26 CAGR: S&P 500 / 70-30 / FD (assumed 2.5%); #292–#295 walk-forward CAGR | 11.42% / 9.06% / 2.53%; 6.05% / 13.57% / 8.36% / 13.46% (all FAIL) | `uv run python -m scripts.batch9_20261122` (`docs/jx_runs/batch9_20261122.txt`, identical on re-run) | FRED, Yahoo SPY, Cboe | 2026-11-22 | measured |
| B10c | #303 additions: mean excess per event, t-stat, halves; quarterly-only subset | +3.90%, 2.97, +4.19% / +3.72%; +3.49% (t 2.36, n 22) | `uv run python -m scripts.batch10_20261122` (`docs/jx_runs/batch10_20261122.txt`, identical on re-run) | Wikipedia constituents, Yahoo | 2026-11-22 | measured; subset is context |
| SC1 | #320 stablecoin pools Stage 1 | 21.27%/yr (KILL) | `uv run python -m scripts.smallcap_20261122` (`docs/jx_runs/smallcap_20261122.txt`, identical on re-run) | DefiLlama | 2026-11-22 | measured |
| S3b | #322 flow-weighted edge; #324 APY-based Stage 1; #325 Stage 1 | −6.95 bps; 94.78%/yr; −23.41%/yr | `uv run python -m scripts.sweep3_20261122` (`docs/jx_runs/sweep3_20261122.txt`, identical on re-run) | dYdX, HL, DefiLlama | 2026-11-22 | measured |
| S4 | #334 mean / t; #335 halves; #337 Stage 1; #303 tradeable check (post-announcement entry) mean / t / n | +0.28% / 0.03; −30.87% / +24.21%; −1.08%; +0.17% / 0.15 / 20 | `uv run python -m scripts.sweep4_20261122` (`docs/jx_runs/sweep4_20261122.txt`, identical on re-run) | Coinbase, HL, DefiLlama, Wikipedia, Yahoo | 2026-11-22 | measured; #303 check withdraws the batch-10 pass |
| CF1 | #296 FTMO 2-Step: 50K $300 / 100K $500 [sens] real, coin flip, dip | $71,038 / −$2,259 / −$44,881; $85,665 / −$85 / −$53,925 | `uv run python -m scripts.cfdprop_20261122` (`docs/jx_runs/cfdprop_20261122.txt`, identical on re-run) | friend's NQ trades 2016-01..2026-10; rules from ftmo.com | 2026-11-23 | measured; price unverified |
| PMY1 | Malaysia-eligible portfolio (Topstep Consistency + TTP Prime + DayTraders EOD + LucidDaily list), 1 each / x5: net, per year, worst dip | $195,000, $18,006, −$13,858 / $974,999, $90,028, −$69,291 | `uv run python -m scripts.portfolio_my_20261123` (`docs/jx_runs/portfolio_my_20261123.txt`, identical on re-run) | friend's NQ trades 2016-01..2026-10; frozen inputs + verified rules | 2026-11-23 | measured; same trades on every account |
| MAN1 | Manual entry (3-min): Top One Elite ACCESS 50K $189 / $39 promo; LucidDaily $85.40 manual | $15,459 / $21,566; $48,761 | `uv run python -m scripts.manual_my_20261123` (`docs/jx_runs/manual_my_20261123.txt`, identical on re-run) | friend's NQ trades 2016-01..2026-10, 3-min delay; Top One rules from its help centre | 2026-11-23 | measured |
| FT1 | #350 / #351 / #352 / #353 / #354 walk-forward CAGR (OOS 2016-01..2026-10); #351 halves, costs ×1.5, worst DD | 11.72% / 20.72% / 0.46% / 8.75% / 1.09%; 26.94% / 14.97%, 20.20%, −22.3% (SPY −23.9%) | `uv run python -m scripts.futures_trend_20261123` (`docs/jx_runs/futures_trend_20261123.txt`, identical on re-run) | Databento GLBX ohlcv-1d continuous, 2010-06..2026-10; FRED DTB3 | 2026-11-23 | measured; fractional notional |
| FT2 | #351b whole-contract CAGR, second half: fractional 13-market / $15K / $50K / $100K / $250K | 16.15%, 9.81% / 10.00%, 3.08% / 15.19%, 7.89% / 17.06%, 10.87% / 15.94%, 9.23% | `uv run python -m scripts.futures_xsmom_small_20261123` (`docs/jx_runs/futures_xsmom_small_20261123.txt`, identical on re-run) | same; micro multipliers and costs assumed | 2026-11-23 | measured; margin not modelled |
| JLP1 | #363 hedged Jupiter JLP, CAGR on capital: Stage 1 (2026-05..10) / full / half 1 / half 2 / costs ×1.5; by year 2024 / 2025 / 2026; worst DD | 9.7% / 32.0% / 56.6% / 11.3% / 31.8%; 70.8% / 23.0% / 8.0%; −7.1% | `uv run python -m scripts.jlp_20261123` (`docs/jx_runs/jlp_20261123.txt`, identical on re-run) | DefiLlama coins (CoinGecko JLP, SOL, ETH, BTC), Hyperliquid funding | 2026-11-23 | measured; price-based hedge (tracking error included) |
| SR1 | #361 CoW: Stage 1 recipients / total / median outside top 5; 10th-ranked 2024 / 2025 / 2026 (gross) | 54 / $7,213,683 / $3,213/yr; $221,205 / $345,363 / $176,033 per yr | `uv run python -m scripts.solver_relay_20261123` (`docs/jx_runs/solver_relay_20261123.txt`, identical on re-run) | Blockscout listing of COW transfers from the Solver Payouts Safe; DefiLlama COW price | 2026-11-23 | measured |
| SR2 | #362 Across Oct 2026: priced fills / volume / spread / bps; 6th-ranked relayer; median bps fills ≤ $15K | 276,218 / $256,961,271 / $69,784 / 2.72; $8,790/yr; 3.32 bps | same command | Base + Arbitrum SpokePool FilledRelay logs (public RPCs, 0 missed); DefiLlama ETH/BTC | 2026-11-23 | measured (upper bound) |
| COWE1 | #364 CoW entrants: active A / B; median first-year net after fee A / B; share ≥ $15K; unregistered check medians (n) | 17 / 27; $129,087 / $25,509; 59% / 59%; $95,639 (7) / $48,411 (4) | `uv run python -m scripts.cow_entrants_20261123`, `uv run python -m scripts.cow_entrants_check_20261123` (`docs/jx_runs/cow_entrants_20261123.txt`, `cow_entrants_check_20261123.txt`, identical on re-run) | same data as SR1 | 2026-11-23 | measured; survivorship upper bound |
| COWG1 | #365 Stage 1: genuine 2026 entrants; 2024–25 entrants ≥ $15K in 2026; pool 2026-05..10 annualised vs 2025; top-1 share 2024/25/26; outside-top-5 win share mainnet / BNB; top-3 value share mainnet / BNB | 1; 5 of 11 (45%); $6,414,563 vs $10,637,374 (60%); 12% / 18% / 50%; 43.7% / 34.3%; 78% / 99% | `uv run python -m scripts.cow_gate_20261124`, `uv run python -m scripts.cow_gate_value_20261124` (`docs/jx_runs/cow_gate_20261124.txt`, `cow_gate_value_20261124.txt`, identical on re-run) | Blockscout payouts; CoW solver-competition API sample (Actions run 45313480778) | 2026-11-24 | measured; API window ~30 days approximate |
| COWS1 | #366 pilot: auctions received / baseline solutions; production auction endpoints answering 403; staging endpoints answering 200 (orders) | 0 / 0; 11 of 11; 11 of 11 (0–3 orders) | Actions `cow_shadow.yml` run 45329600886 (`docs/jx_runs/cow_shadow_run_45329600886.txt`); fallback job `cowauction` run 45332265118 (`docs/jx_runs/fetch_fallback_45332265118.txt`) | api.cow.fi / barn.api.cow.fi | 2026-11-24 | measured (live endpoints; a re-run reflects the endpoint state at that time) |
| COWW1 | #367: registry solvers / payout addresses; recipients examined / matched; 2026 ≥ $15K recipients by class (Established / Small / Unknown) with $/yr and share; small-team range | 89 / 112; 29 / 28; 10 $2,487,206 29% / 6 $810,935 9% / 7 $5,302,086 61%; $23,405–$385,541 | `uv run python -m scripts.cow_who_20261124` (`docs/jx_runs/cow_who_20261124.txt`, identical on re-run) | cms.cow.fi solver registry (Actions run 45344455035); Blockscout payouts | 2026-11-24 | measured; identity from named sources |
| CT1 | #370 walk-forward CAGR / worst DD / Sharpe; halves; costs ×1.5; BTC CAGR / DD; HL-listed-only hindsight config 2023–26 | 30.8% / −90.6% / 0.73; −5.2%, 80.3%; 28.5%; 18.4% / −76.7%; 0.3%, 61.2%, 58.8%, −6.9% | `uv run python -m scripts.crypto_trend_20261124` (`docs/jx_runs/crypto_trend_20261124.txt`, identical on re-run) | data.binance.vision archive (Actions run 45378975452), HL funding | 2026-11-24 | measured |
| CT2 | #382 HL-listed walk-forward CAGR / DD; years 2021–26; end value by start 2021/22/23/24/25 | 28.9% / −90.6%; +1,284%, −60.7%, −42.1%, +46.8%, +21.0%, −21.5%; ×4.39 / ×0.32 / ×0.81 / ×1.39 / ×0.95 | `uv run python -m scripts.crypto_trend_hl_20261124` (`docs/jx_runs/crypto_trend_hl_20261124.txt`, identical on re-run) | as CT1 | 2026-11-24 | measured |
| UX1 | #371 Arbitrum UniswapX Aug–Oct 2026: fills; volume / annualised; top-3 share (count); newcomer monthly shares; measured fills; volume-weighted gross spread; newcomer A / B gross per yr | 10,957; $191,936,273 / $761M; 89.0%; 9.9% / 9.7% / 5.2%; 5,051; 8.62 bps; $85,116 / $51,884 | `uv run python -m scripts.uniswapx_20261124`, `scripts.uniswapx_vol_20261124`, `scripts.uniswapx_margin_20261124` (`docs/jx_runs/uniswapx_*.txt`, identical on re-run) | Arbitrum public RPC logs + receipts (Actions runs 45379364066, 45401284013, 45406058307); DefiLlama daily/hourly prices | 2026-11-24 | measured; gross spread vs hourly mid |
| FB1 | Base flashblocks probe, free public endpoint | pending==latest+1 in 0/339 polls, 0 errors => NOT SUPPORTED | `uv run python scripts/fetch_public.py liq_flashblocks` (Actions) | docs/jx_runs/liq_flashblocks_20261124.txt |
| FB2 | Base docs: Denim 200 ms blocks 2026-11-05, Flashblocks retired | third-party (docs read via Actions) | `uv run python scripts/fetch_public.py liq_basedocs` | docs/jx_runs/fetch_public_45377543121.txt |
| UC1 | #391 HK IPO one-lot (AASTOCKS, 2024-01..2026-10): IPOs with fields; mean / median day-one; Rule A EV per yr; zero-fee EV per yr | 301; +35.6% / +8.2%; −US$277; +US$1,092 | `uv run python -m scripts.uncharted_hkipo_20261125` | docs/jx_runs/uncharted_hkipo_20261125.txt |
| UC2 | #385 short HL pre-launch perps (mapping-checked): n; mean / median; t; liquidated at 1× isolated; mean then | 27; +18.3% / +24.2%; 1.65; 11; −14.3% | `uv run python -m scripts.uncharted_hyperp_20261125` | docs/jx_runs/uncharted_hyperp_20261125.txt |
| UC3 | #389 Stage 1 HL X 15%: fills; mean per fill; t; $/yr on $15K; X 10/20/30% mean | 4,350; +2.61%; 15.45; $19,606; +0.91% / +6.24% / +13.21% | `uv run python -m scripts.uncharted_wick_20261125` | docs/jx_runs/uncharted_wick_20261125.txt |
| UC4 | #389 Stage 2: HL worst drawdown / day; sizing-fix $/yr; margin-reserved $/yr; Binance fills, mean, t, $/yr, years positive; Binance path drawdown | −$2,480 / −$2,307; $18,839; $6,423; 17,286, +1.48%, 14.98, $15,776, 6/6; −$22,260 | `uv run python -m scripts.uncharted_wick_s2_20261125` | docs/jx_runs/uncharted_wick_s2_20261125.txt |
| UC5 | #383 launch vaults: series; median first-year hedged; JLP / HLP / ZLP year 1 | 5; 32.1%; 82.6% / 86.8% / 32.1% | `uv run python -m scripts.uncharted_vaults_20261125` | docs/jx_runs/uncharted_vaults_20261125.txt |
| UC6 | #384 LST discounts (GeckoTerminal, 6 months): net per yr; #387 CCA: auctions / real / with 7-day price; median 7-day | $3; 1,152 / 16 / 8; −39.3% | `uv run python -m scripts.uncharted_lst_20261125`; `uv run python -m scripts.uncharted_cca_20261125` | docs/jx_runs/uncharted_lst_20261125.txt, uncharted_cca_20261125.txt |
| UC7 | #396 Binance perp launch short: n, mean, t; #397 cascade reversal HL: n, mean, t, positive; Binance: n, mean, t, positive | 17, +8.67%, 0.99; 26, +3.27%, 1.95, 62%; 72, +3.73%, 2.69, 62% | `uv run python -m scripts.uncharted_wave3_20261125` | docs/jx_runs/uncharted_wave3_20261125.txt (after uwave3) |
| FH1 | #407 new-listing wick bids HL X15%: fills, mean, t, $/yr; #408 1-day reversal HL: gross / cost / net per day, annualised; Binance net per day, annualised | 529, +1.48%, 2.47, $3,493; +0.070% / 0.148% / −0.076%, −42.8%; −0.077%, −55.8% | `uv run python -m scripts.five_high_20261125` | docs/jx_runs/five_high_20261125.txt |

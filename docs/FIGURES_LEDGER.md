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

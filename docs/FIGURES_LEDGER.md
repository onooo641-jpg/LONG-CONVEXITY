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

Raw output for every command above is in `docs/jx_runs/`.

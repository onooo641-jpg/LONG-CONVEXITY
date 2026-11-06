# NOTES_JX — three checks before buying anything

Run 2026-11-06. No strategy parameter was changed. One mechanical fix was
needed (commit `e7d6950`: `XFARules(mll_locks_at=None)` raised `TypeError`).

Every figure below comes from one of these commands. Raw output is committed
in `docs/jx_runs/` so nothing depends on a chat paste.

```bash
uv run python scripts/ingest.py
# as the docs saw it (last shard before the September pull):
uv run python scripts/jx_checks.py --end 2026-09-08T05:27Z   # -> docs/jx_runs/checks_asof_20260908.txt
# with all data now in the repo (to 2026-10-28):
uv run python scripts/jx_checks.py                           # -> docs/jx_runs/checks_data_to_20261028.txt
```

`scripts/asof.py` runs any existing script on truncated data, e.g.
`uv run python scripts/asof.py 2026-09-08T05:27Z scripts/account_lifetime.py --orders <cached orders>`.

Two data windows matter. The GO_LIVE figures were computed on data ending
**2026-09-08 05:27 UTC**. Re-running on today's data (to 2026-10-28) moves
every figure a little; both are given. All recycling figures are $900/trade,
one unbroken chain from 2016, XFARules as of 2026-09-14.

---

## 1. Figure drift — resolved: it's the payout Policy, not payout_cap

**Correction to the premise first.** The two lines are not comparing the same
thing. Line 158's +$42,414 is **net**; line 189's $61,984 is **withdrawn**
(入袋). $61,984 − $42,414 = $19,570 is withdrawn-vs-net. Like for like:

| GO_LIVE | Policy | withdrawn | spent | net |
|---|---|---|---|---|
| line 158 | `LOCK_FIRST` | $59,728 | $17,314 | **$42,414** |
| line 189 | `IMMEDIATE` | $61,984 | $17,116 | **$44,868** |
| real gap | | $2,256 | $198 | **$2,454** |

Both reproduce exactly on the 2026-09-08 window. `payout_cap` is not it: cap
$2,000 gives $42,823 (LOCK_FIRST) and $46,251 (IMMEDIATE), matching neither.
The slicing difference between the two scripts (entry_ts vs exit_ts, bars from
2015-11-17 vs 2015-12-01) changes nothing — same 2,161 trades, same results.

Where each comes from:
- Line 158 = `scripts/recycling_report.py`, `"whole": recycle(history)` —
  `recycle()` defaults to `Policy.LOCK_FIRST`.
- Line 189 = `scripts/account_lifetime.py`, `recycle(trades, policy=Policy.IMMEDIATE)`.

**Current: IMMEDIATE.** Every GO_LIVE table from line 184 down (accounts,
lifetimes, 98% mortality, staggered chains) uses it, and the recycling report's
own policy table says IMMEDIATE beats LOCK_FIRST at every size over 11 years.
The report headline quotes the policy its own table rejects.

Superseded along with line 158 (all LOCK_FIRST):
- 1,184-day drought → **479 days** under IMMEDIATE
- 39 dead accounts in a row → **17** under IMMEDIATE
- "7/11 profitable years, first three all lose" — fresh-start-per-year table,
  LOCK_FIRST. Not recomputed under IMMEDIATE.

Same figures on data to 2026-10-28: LOCK_FIRST $62,249 / $17,426 / $44,823;
IMMEDIATE **$65,467 / $17,277 / $48,190**.

Other drift found on the way (in `docs/FIGURES_LEDGER.md`):
- **"PF 0.876" is the payoff ratio, not the profit factor.** True PF over
  2016–2026 at $500 is **0.994** (both windows). README lines 101 and 158–160
  label the payoff ratio as PF; the OOS 1.190 in the same table is a real PF.
- "−$3,044" (strategy alone, $500) and "−$2,135" (strategy alone, line 158) are
  the same 2,161 trades at $500 and $900. Neither line says which size.
- GO_LIVE line 32 "11 years −$4,394" is a third 11-year figure (full session,
  confirming-bar fills excluded, per commit 859ad92). Not reproduced here.

## 2. Withdrawals by calendar year — not concentrated in 2024–2026

IMMEDIATE, data to 2026-09-08. "raw" = the same trades with no account
structure, $900.

| year | payouts | withdrawn | spent | net | raw strategy |
|---|---|---|---|---|---|
| 2016 | 1 | $125 | $1,009 | −$884 | −$30,055 |
| 2017 | 3 | $485 | $962 | −$477 | −$9,479 |
| 2018 | 2 | $146 | $1,207 | −$1,061 | −$28,955 |
| 2019 | 9 | $6,402 | $1,458 | $4,944 | $6,987 |
| 2020 | 7 | $8,927 | $1,950 | $6,977 | $1,369 |
| 2021 | 4 | $2,085 | $1,754 | $331 | −$1,873 |
| 2022 | 3 | $2,788 | $2,048 | $740 | −$6,581 |
| 2023 | 11 | $13,423 | $1,656 | $11,767 | $22,970 |
| 2024 | 7 | $7,065 | $1,903 | $5,162 | $13,496 |
| 2025 | 6 | $8,416 | $1,801 | $6,615 | $1,897 |
| 2026* | 9 | $12,122 | $1,353 | $10,769 | $28,089 |

*2026 to 09-08. "spent" is booked at each account event, so it lags the
calendar a little; it sums to the $17,116 total.

| split | withdrawn | net | raw strategy |
|---|---|---|---|
| 2016–2023 | $34,380 (55.5%) | **+$22,336** | −$45,617 |
| 2024–2026 | $27,604 (44.5%) | +$22,547 | +$43,482 |
| the 5 years the strategy lost | $5,629 (9.1%) | **−$1,351** | −$76,943 |
| the 6 years it made money | $56,355 (90.9%) | +$46,234 | +$74,808 |

On data to 2026-10-28: 2024–2026 = 47.5% of withdrawals; 2016–2023 net
unchanged at +$22,336.

**How to read it:**
- The test you set doesn't trigger. 2016–2023, when the strategy lost $45,617,
  the chain still netted **+$22,336**. The result isn't just the 2024+ regime.
- But the asymmetry doesn't turn losing years into profit. It turns them into
  roughly **break-even** ones: five losing years (−$76,943 raw) cost −$1,351
  net. All the profit comes from years when the strategy was flat or better.
- It does amplify near-flat years: 2020 (+$1,369 raw → +$6,977 net) and 2025
  (+$1,897 → +$6,615).
- So the bet is "the strategy has some years at or above flat". That's weaker
  than needing a real edge, but it's still a bet. 2016–2018 is what a run
  without one looks like: three years, $3,178 spent, $756 withdrawn.

Verdict: check 2 does **not** rule out buying.

## 3. Rule-change stress test — survives any single change and any pair; dies on all five

IMMEDIATE, data to 2026-09-08. One change at a time:

| change | net | vs baseline |
|---|---|---|
| baseline | **$44,868** | — |
| reset $49 → $99 | $43,668 | −3% |
| activation charged per attempt (153 × $149) | $29,819 | −34% |
| **MLL never locks** (`mll_locks_at=None`) | **$20,442** | **−54%** |
| payout_cap 4,000 → 2,000 | $46,251 | +3% (see below) |
| winning_days_required 5 → 10 | $43,185 | −4% |
| **all five at once** | **−$12,352** | negative |

Worst pairs: activation-per-attempt + no lock **$4,648**; no lock + 10 winning
days $8,281. Every pair stays positive. Data to 2026-10-28: baseline $48,190,
no lock $21,166, all five −$11,910, worst pair $4,925. Same shape.

- **The MLL lock is the one rule that matters.** Lose it and half the profit
  goes. Lose it together with per-attempt activation and nothing is left.
- Reset price, payout cap and winning-days count barely move it. The reset fee
  could double and you'd hardly notice.
- `payout_cap 2,000` comes out slightly *higher*. Mechanically: smaller payouts
  leave more balance in the XFA, so slightly fewer funded accounts die. The cap
  rarely binds anyway; 50% of the balance is usually under $2,000.
- Under LOCK_FIRST, "no lock" means zero payouts ever (−$16,918), because the
  policy waits for a lock that never comes. One more reason IMMEDIATE is the
  current policy.

## What this doesn't cover

- **Rules not re-checked.** XFARules are Topstep's as of 2026-09-14. I didn't
  check today's rulebook. Check the MLL lock first; it's the 54% one.
- Every caveat in GO_LIVE still applies: backtest only, optimistic limit fills,
  Databento not TopstepX data, the 20-micro funded cap not modelled
  (`scaling_tier` is modelled; queue position isn't).
- One unbroken chain is one path. Starting the chain a month later gives a
  different year table.

## Next steps

1. Look up today's Topstep 50K XFA rules: MLL lock, activation timing, payout
   cap, winning days, reset price. Update `XFARules` and rerun
   `scripts/jx_checks.py`.
2. Fix the recycling report headline to IMMEDIATE (or pass `policy=` explicitly
   in `compute()`), then regenerate the report and GO_LIVE line 158.
3. Before going live: the empty-response class in `docs/ARTIFACT_CLASSES.md`
   (class 3) has unguarded sites in the shutdown path. Read that first.

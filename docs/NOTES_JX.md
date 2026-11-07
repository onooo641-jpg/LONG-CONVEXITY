# NOTES_JX — three checks before buying anything

> **Update, later on 2026-11-06: Topstep's rules re-checked, and the policy
> verdict in §1 flipped.** Read "Rules re-checked" at the end first. Sections
> 1–3 below are as first written, using the 2026-09-14 rulebook
> (`jx_checks.py --rules 20260914`).

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

---

## Rules re-checked against Topstep (2026-11-06, later)

Read from Topstep's own pages that day (help.topstep.com payout policy,
topstep.com/express-funded-account-rules, help.topstep.com MLL article).

| rule | model had | Topstep says | effect |
|---|---|---|---|
| MLL after a payout | unchanged (could stay below $0) | **"resets to $0 permanently"** | **new, modelled** (`payout_locks_mll`) |
| 2nd+ payout | 5 winning days | + **positive net profit since last payout** | new, modelled (`profit_since_payout_required`) |
| MLL lock at +$2,000, $2,000 trailing, EOD | yes | yes | matches |
| 5 winning days of $150+, 50% of balance, 90/10 | yes | yes | matches |
| 50K payout cap | $4,000 | **$2,000**; $4,000 only for new Combines with the DLL added at checkout, as a limited-time offer from "June 2nd" | unclear if the offer is still on. Cap barely moves the result (below). |
| Back2Funded window | 30 days (GO_LIVE) | **7 calendar days**, $599 | GO_LIVE corrected. Not in the model. |
| Standard reset $49, activation $149 per XFA earned | yes | yes | matches |

Not verified: No-Activation path pricing. Third-party sites disagree
($85–$109 a month and per reset). Check your dashboard.

### What changed (data to 2026-10-28, $900, one chain from 2016)

| | old rules | **current rules** |
|---|---|---|
| IMMEDIATE net | $48,190 | $42,954 |
| **LOCK_FIRST net** | $44,823 | **$44,590** |
| winner | IMMEDIATE | **LOCK_FIRST** |

The payout-resets-MLL rule makes an early payout throw away the buffer below
$0. LOCK_FIRST now wins at $500 (+$3,883), $900 (+$1,636) and $1,000
(+$10,982). IMMEDIATE wins only at $250, where both lose money.
**The current policy is LOCK_FIRST.** `account_lifetime.py`, `fade_report.py`
and the recycling report now use it explicitly.

So the §1 call ("IMMEDIATE is current") was right under the old model and is
now superseded. GO_LIVE line 158 (+$42,414, LOCK_FIRST) had the right policy
by default. Its 1,184-day drought and 39-account streak are LOCK_FIRST
figures, so they're current again.

### Check 2 under current rules (LOCK_FIRST, data to 2026-10-28)

- 2024–2026 = **50.0%** of withdrawals ($31,023 of $62,065).
- 2016–2023 net **+$18,602** while the strategy alone lost $45,617.
- The 5 losing years net **−$2,473**. The 6 others +$47,063.
- Verdict unchanged: **not concentrated in the recent regime. Doesn't rule
  out buying.**

### Check 3 under current rules (LOCK_FIRST, data to 2026-10-28)

| change | net |
|---|---|
| baseline | $44,590 |
| reset $49 → $99 | $43,240 |
| activation per attempt | $29,094 |
| payout cap $4,000 → $2,000 | $44,261 |
| 10 winning days | $43,035 |
| **MLL never locks** (trailing never locks, payouts don't lock either) | **−$17,079** |
| all five | −$33,825 |

Pairs without the lock change all stay above +$27,000. Any pair *with* it is
negative.

Read this carefully. Under LOCK_FIRST, "no lock" means **no payouts ever**,
because the policy waits for a lock that doesn't exist. That's a policy
artefact: a trader would switch to IMMEDIATE. Under IMMEDIATE the same change
gives **+$21,166** (worst pair +$4,925, all five −$11,875). So:

- **If the lock rule ever changes, switch policy.** The business survives at
  roughly half the profit.
- Everything else Topstep could plausibly tighten costs 0–35%.

Commands: `uv run python scripts/jx_checks.py --skip-strategy` (current rules
are the default) and `--rules 20260914` for the old ones. Output is in
`docs/jx_runs/checks_rules20261106_*.txt`.

### Step 3 done: empty-book proof

`python -m bridge.live --roundtrip`, GO_LIVE step 4b. Without it, `--live`
never exits 0 (no auto-shutdown) and the deadline sweep cancels everything
sent. See ARTIFACT_CLASSES class 3.

### Still open

- Which payout cap applies to the Combine you actually buy ($2,000 or $4,000).
  Check at checkout.
- `docs/recycling_report.pdf` and `docs/fade_report.html` weren't regenerated.
- GO_LIVE's $900 → $250 / guard table was not recomputed (flagged in place).

---

## Capital, pass rate, other firms (2026-11-06, evening)

All backtest, $900/trade, LOCK_FIRST, current Topstep rules, data to
2026-10-28. `uv run python scripts/jx_capital.py`; output in
`docs/jx_runs/capital_*`.

**Pass rate per evaluation: 34%** (53 passes in 156 finished attempts). About
1 in 3. Median evaluation life is 7 trades, about 10 days.

**Money needed, starting a fresh chain on each of 118 monthly start dates
(2016–2025):**

| | median | 1 in 4 starts worse than | 1 in 10 worse than | worst |
|---|---|---|---|---|
| deepest cumulative loss before recovering | −$863 | −$1,628 | −$2,613 | −$3,568 (Jan 2016 start) |
| days to first payout | 144 | 318 | 826 | 1,183 |
| fees paid before first payout | $746 | $1,602 | $2,628 | $3,568 |

Every start date eventually went positive. Starts from 2023 on: median
deepest loss −$457, median 64 days to first payout. That's the good regime,
not a promise.

**Other firms — automation policy** (from third-party summaries found by
search; official pages **not** read, except Tradeify's guidelines page):

| firm | bots on funded accounts | note |
|---|---|---|
| Topstep | **yes**, in writing (2026-09-10) | the only one verified by us |
| Lucid Trading | reportedly yes, evaluation and funded | best alternative on paper. Official page not read (needed approval). |
| Tradeify | yes, **but** the bot must be used only at Tradeify, with ownership proof and a live video | can't run the same bot at Topstep too |
| MyFundedFutures | sources conflict (semi-auto only vs allowed) | unclear |
| Apex | reportedly semi-auto only on funded accounts | likely no |
| Take Profit Trader, TradeDay, Funded Futures Family, Blue Guardian | no | ruled out |

**LucidFlex 50K, rough model** (`scripts/jx_lucid.py`; one-time ~$95–140
eval, ~$95 reset, no monthly or activation fee, other rules close to
Topstep's). All third-party numbers. Payout cap unknown.

| | net, 11 years |
|---|---|
| Topstep (current rules) | $44,590 |
| LucidFlex estimate | $46,765–$47,150 |

About +$2,500 (≈5%). That's within the uncertainty of the inputs. Switching
would also mean writing a new broker client (Lucid isn't TopstepX/ProjectX as
far as I found) and getting automation confirmed in writing. **Not worth
switching now.** Worth a second account later if Topstep is working.

---

## Zero-edge baseline (2026-11-07)

`uv run python scripts/jx_zero_edge.py`. The same 2,185 trade sizes at $900,
signs randomised 200 times, fees kept, current rules, LOCK_FIRST.

| | pass rate | net, 11 years |
|---|---|---|
| real strategy | **34.0%** | $44,590 |
| coin flip, fees kept | 26.3% (90% range 21.2–32.1%) | median $18,561, positive in 98% of runs |
| coin flip, no fees | 31.0% | median $28,712 |

- The "zero-edge ceiling = 2000/5000 = 40%" argument assumes a fixed floor.
  Topstep's floor trails the peak, which lowers everyone's pass rate. Under
  the real mechanics a no-edge trader passes about 26%. The strategy's 34% is
  above the 95th percentile of that, so it beats a coin flip on this
  structure.
- In this model, **most of the profit comes from the account structure, not
  from the signal**: a coin flip still nets about $18.6K. The strategy adds
  about $26K on top. That's a model result. Real fills are worse (queueing)
  and Topstep's rules can change.
- Model detail found here: the Combine floor is modelled as trailing with no
  lock. Topstep's MLL article says it locks at the starting balance in the
  Combine too. So the model is slightly conservative on passing. Not fixed
  yet.

---

## Model and doc fixes (2026-11-07)

- `XFARules.payout_cap` 4000 → **2000**, the standing 50K Standard cap per
  Topstep's payout page. The $4,000 figure needs the limited-time DLL offer at
  checkout.
- New `XFARules.combine_mll_locks = True`. Topstep's MLL article says the
  Combine's trailing limit also locks at the starting balance. The model had
  it trailing forever. Effect is small: +$98 over 11 years, pass rate
  34.0% → 34.4%.
- `jx_checks.py` rulebook **20261107** (default) = both changes.
  20261106 / 20260914 reproduce the earlier runs.
- Current headline (data to 2026-10-28, $900, LOCK_FIRST): **net $44,359**
  (withdrawn $61,440, spent $17,081). IMMEDIATE $43,433. No lock: −$17,130
  (LOCK_FIRST) / $21,000 (IMMEDIATE).
- Capital (`jx_capital.py`): deepest cumulative loss median −$863, 1 in 10
  −$2,564, worst **−$3,520**. Days to back-to-even median 144, 1 in 10 1,000,
  worst 1,357. **Essentially unchanged** from the $4,000-cap run.
- Zero-edge (`jx_zero_edge.py`): coin flip passes 26.7% and nets $18,046
  median against the strategy's 34.4% / $44,359.
- GO_LIVE wake time corrected for US daylight saving: **22:25 MYT now**
  (US winter), 21:25 in US summer, or 21:25 all year if you'd rather wait an
  hour in winter than miss trades.
- Not changed: `scripts/quarterly_report.py` has its own first-pass replay,
  which still trails without the Combine lock.

---

## Holdout result, 2010-2015 (2026-11-07)

Pre-registered in `docs/HOLDOUT_PREREG.md` (633a258) before running; full
result and post-hoc analysis there.

- **The recycling business did not work on 5.5 unseen years.** Net −$2,505
  at the fees of the time. At today's fee ratio it breaks even (+$164).
  Pass rate 24% at today's fees, below a coin flip's 26.7%.
- The strategy's edge **before fees** is thin everywhere: gross PF 1.04 on
  the holdout, 1.12 on 2016-2026. Much of the "it got better after 2019"
  pattern tracks fees falling from ~13–18% of risk to ~2% as NQ's price
  rose. It is not only a regime change.
- Filters: V3 (skip stops wider than 2× the recent median) wins by the
  registered rule by a negligible margin. Shadow-log candidate only. V2 and
  V4 fail. V1 is pending the 2010-2015 news calendar.
- **Planning range, honestly stated:** 2016–2025 backtest ≈ $3,140/yr; unseen
  2010–2015 at today's costs ≈ $0/yr. Downside in both is capped at fees.

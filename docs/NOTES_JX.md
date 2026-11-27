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

## Commission sensitivity (2026-11-08)

The engine charges MNQ $1.24 round trip. Topstep's pages disagree: $1.22 on
the Combine/XFA commissions article, **$0.74** on the TopstepX commissions
article (both found 2026-11-08). Not changed in the model until the actual
fee shows on a statement. `scripts/commission_sensitivity.py`:

| | $1.24 | $0.74 |
|---|---|---|
| 2016–2026 recycling net | $44,359 | **$50,961** |
| 2016–2026 raw PF | 0.997 | 1.043 |
| Holdout 2010–2015 recycling net (fees of the time) | −$2,505 | −$2,475 |

Lower fees help the recent period about 15%, but they don't rescue the
holdout. Check the real per-contract fee on your friend's first statement.

Topstep's product list (help.topstep.com, 2026-11-08) includes ES/MES,
NQ/MNQ, RTY/M2K and YM/MYM in the Combine and the funded accounts.

## ES unseen-market test (2026-11-09)

Pre-registered in `docs/ES_PREREG.md` before running. The strategy was
unchanged, run on MES for 2016–2026 and judged against a coin flip with the
same trade sizes. **Result: does not confirm.** ES nets $20,338 against a
coin-flip 95th percentile of $24,180; NQ nets $44,359 against $36,711. ES
points the same way (it beats 86% of flips) but not by enough. Treat the NQ
edge as possibly NQ-specific. The NQ plan is unchanged; the evidence for it is
weaker than the NQ backtest alone suggests.

Data cost: ES $20.93 (bought). Quotes for the full window: YM $20.15 and RTY
$11.24, not bought.

## Risk size, ES sensitivities, two accounts (2026-11-09)

Full results: `docs/PREREG_20261109.md`. In short:
- **$900 stays.** Bigger risk earns more on paper, mostly from the account
  structure: a coin flip's profit rises almost as fast. It also fails the
  pre-registered rule on ES 2010–2015.
- **ES with settings scaled to its price beats 100% of coin flips**, against
  86% unscaled. This is post-hoc, so it is a hypothesis being tested on YM/RTY
  (`docs/PREREG_YM_RTY.md`).
- **Two markets smooth cash flow:** payout months go from 20% to 32%, and the
  two chains barely move together (correlation 0.14).

## YM and RTY (2026-11-09)

Pre-registered in `docs/PREREG_YM_RTY.md` before the data arrived. Across four
markets, the unchanged strategy beats a coin flip on NQ (98%) and narrowly on
YM (96%), but not on ES (86%) or RTY (12%). Price-scaled settings help on
neither YM nor RTY, so the ES scaled result was chance. The raw strategy loses
on all four; the money comes from the recycling structure plus, on NQ, an edge
that does not clearly carry over to other markets.

**Conclusion:** keep trading NQ only. There's no good case for a second market.
The NQ edge is better treated as NQ-specific, possibly partly luck, which is
why the forward log and the cash-reserve stop matter.

Databento spend 2026-11-09: ES $20.93, YM+RTY $31.39 twice (the first purchase
was lost, my error), about $84 in total.

## 12-idea batch (2026-11-09)

Pre-registered in `docs/PREREG_BATCH_20261109.md`. To pass, an idea had to
beat the baseline's margin over a coin flip on NQ 2016–26, NQ 2010–15, and 2
of ES/YM/RTY.
- These made things worse or were mixed: long-only, short-only, scaling out
  with a runner (2R/3R), smaller funded size, a loss-streak pause, an equity
  filter, fee caps, and a wider stop.
- **The 120-minute time stop passed,** but weakly. The real money barely
  changes on NQ (+$1.2K over 11 years), and one pass in twelve is about what
  luck gives. It goes into the forward log as a shadow; live stays unchanged.

## Account size and payout path (2026-11-09)

Topstep caps funded accounts at 5, so the money each account earns sets the
ceiling. `scripts/account_size_test.py` (NQ, risk scaled to each loss limit):

| per account | 50K | 100K | 150K |
|---|---|---|---|
| net 2016–26 | $44,359 | $62,660 | $95,324 |
| deepest cash | −$3,520 | −$7,152 | −$9,952 |
| net 2010–15 | −$2,505 | −$5,144 | −$9,484 |

- 150K earns about 2.1× per slot but needs about 2.8× the reserve and loses
  about 3.8× as much in a bad period. 50K returns the most per dollar of
  reserve.
- The Consistency path adds 5–7% in 2016–26 and nothing in 2010–15.
- The 100K/150K scaling ladder is assumed, not read from Topstep.
- The model now supports `consistency_target` and `scaling_mult`. Defaults
  are unchanged, and the baseline still reproduces $44,359.

## Timing patterns and Topstep cost options (2026-11-20)

Pre-registered in `docs/PREREG_20261120.md`.
- **Futures timing patterns all fail:** overnight drift, turn of month,
  pre-FOMC drift, gap fade and day of week, on 4 markets after micro costs. The
  well-known patterns aren't strong enough here to trade.
- **Back2Funded fails:** it adds about $11K in 2016–26 but loses more in
  2010–15 and nearly doubles the cash dip. Don't reactivate blown accounts.
- **Don't take the doubled payout cap at 100K/150K:** bigger payouts leave less
  cushion and the accounts die sooner (−$6.6K and −$9.3K). At 50K it barely
  matters.

## Lucid and Malaysia access (2026-11-20)

- **Lucid (LucidFlex 50K):** automation allowed per its help center. Same
  trades: $37,523 vs Topstep's $44,359, worst dip −$4,720 vs −$3,520. It fails
  as a replacement but works as a second firm. Needs a Tradovate or Rithmic
  connection; ProjectX is reportedly not supported since December 2025.
- **Malaysia access for the crypto and prediction-market ideas:**
  - The SC regulates crypto exchanges, and only a handful are registered.
    Bybit and Huobi were ordered out.
  - Offshore and DeFi venues sit in a legal grey area, with no investor
    protection.
  - Polymarket's status for Malaysia is conflicting: a June 2026 source says
    accessible, a November 2026 source lists it as restricted.
  - So those ideas are on hold until the legal question is answered properly.

## Crypto and prediction-market top-10 (2026-11-20)

Pre-registered, backtested on free public data fetched through GitHub Actions
(`.github/workflows/fetch_public.yml`).
- **Fail:** new-perp funding, utilisation threshold (fallback data, because
  the history is paywalled), liquidity incentives (too few with IL data),
  stETH discounts (~$45 a year per $10K), vault switching.
- **No data:** Polymarket, which refuses US servers. Not circumvented.
- **Not testable:** settlement resolution.
- **Tested and failed:** shorting new listings. It looked like +$171 per
  $1,000 on 2024 listings, then lost $111 on unseen 2023 listings, with 27% of
  coins squeezing 50% or more.

## Non-prop loophole hunt (2026-11-20, docs/PREREG_LOOPHOLES_20261120.md)
- IPO ballot: fails the pre-registered test; average applicant makes ~RM140–310 per IPO but needs ~RM30K+ per application and late-2026 IPOs turned weak.
- i-Saraan: the one guaranteed freebie found: RM500/yr (20% on RM2,500), RM5,000 lifetime; 90% locked in EPF.
- ASM funds: 5% liquid, ~1% above best FDs; good for idle cash.
- Luno vs global: uniform ~0.45% premium = MYR conversion cost; not exploitable.
- Static-drawdown prop firms (FTMO 2-Step): structure pays random play at ≥2% risk; FTMO polices risk per trade; prop-related; verify rules before any test.

## FTMO checked, FTMO Futures tested (2026-11-20, docs/PREREG_FTMO_FUTURES_20261120.md)
- FTMO accepts Malaysia (18+). But FTMO recommends ≤1% risk per trade, where the CFD "structure" is worth nothing; Topstep's edge comes from allowing ~45% of the loss buffer per trade.
- FTMO Futures: $28–34K vs Topstep $44K over 2016–26 ($48K best case if renewal resets are free); dips ~3× deeper. Not better; a possible second firm only.
- Bulenox (bots explicitly allowed, Malaysia not listed as restricted) not modelled: rules changed recently.

## Firms round 2 + global round 1 (2026-11-20)
- TradeDay Fast Pass at $85/mo (discount code): $35.7K vs Topstep $44.4K — closest futures match; bot must live inside NinjaTrader/Tradovate/TradingView. Elite Trader Funding and FXIFY Futures don't allow bots. Bulenox Momentum loses money (30-day eval limit).
- Breakout / Kraken Prop Classic 50K: Topstep-level ($38–57K) once its 10x leverage cap is applied; uncapped numbers were a model artefact. Malaysia not restricted. Bot policy unpublished — must ask.
- Non-prop classes screened out by reasoning (betting illegal in MY, bank bonuses US-only, airdrops untestable/grey).

## Conclusion of the 2026-11-20 search (CANDIDATES #48–60)
**Answer:** the only thing that makes Topstep-level money is prop-firm structure, and the
way to scale it is more firm slots running the same trades, not a different strategy.
- 60 pre-registered tests. Every non-prop idea failed (#29–33, #37–47, #49–51, #57–59).
  The friend's trades lose money on own money over 2016–26 (#58), so the income is the
  firms' rules, which pay even random trading (coin flips profit in 94–98% of runs).
- No single firm beats Topstep 50K (#48, #53–56). Lucid, MFFU and Breakout come close
  and run alongside it.
- Plan figures (#60): Topstep + Lucid + MFFU = $10.7K/yr over 2016–26, cash on hand
  $13.8K; at max slots (5 Topstep, 5 Lucid, 3 MFFU) $47K/yr and $58K cash on hand.
  Firms move together (correlation 0.80–0.88), so dips stack. Year one: median $5.1K,
  35% of start months lose money, worst $6.7K out of pocket.
- Scale in steps: Topstep alone until the live account confirms the backtest, then add
  Lucid and MFFU, then more slots. Breakout only once a bot can connect.

**What the backtest cannot settle (needs live data or the firms):**
1. Live Topstep results vs the model (the friend's live account).
2. Breakout/Kraken Prop: bot connection and the "heightened risk" clause.
3. Whether copying one strategy across 5 accounts per firm stays allowed in practice
   (Topstep's help centre permits multiple XFAs; firms may deny them at their discretion).
4. MFFU Rapid EOD still on sale; TradeDay discount recurrence; Lucid/MFFU prices.
5. Household rules: Lucid and Breakout count per household.

## Firm questions verified from public pages (2026-11-20 13:15)
- **Breakout / Kraken Prop: ruled out for the bot.** Kraken's own Prop page: "Kraken Prop
  does not currently offer API access ... evaluation and funded accounts. All orders on a
  Prop account are placed manually." Third-party reviews add that copy trading across
  accounts is prohibited. Breakout's help centre allows multiple funded accounts up to
  $200K total, which no longer matters. Plan figures to use: B− and C− in
  PREREG_PORTFOLIO (Topstep + Lucid + MFFU): $10,746/yr, $13,829 cash; max slots $47,362/yr, $57,966 cash.
- **Topstep: confirmed.** Bots via TopstepX API (powered by ProjectX, billed separately);
  built-in TopstepX Trade Copier for Combines and XFAs (not Live); up to 5 XFAs and $750K
  buying power through a copier (help-centre text quoted by third parties).
- **Lucid: automation confirmed.** Lucid help centre "Permitted Activities": automated trading
  systems and trade copiers are permitted; HFT banned. Max 5 funded per household.
  CORRECTION (13:45): Lucid is **not** on ProjectX any more. ProjectX ended third-party
  service on 2026-02-28 and now runs only as TopstepX; Lucid lists CQG (Tradovate,
  NinjaTrader, TradingView) and Rithmic platforms. The TopstepX bot does not connect as is.
- **MFFU: confirmed with one porting cost.** Fair Play page allows automated strategies;
  copying between your own accounts allowed (third-party). Platforms: Tradovate,
  NinjaTrader, TradingView, Quantower; no ProjectX (HyperProp "coming soon" as of Aug 2026),
  so the bot needs a Tradovate-API version. Rapid EOD is still sold on MFFU's plan page
  (read 2026-11-20): one-time fee, $162 shown, $97 with current promotion; no end date.

## How the bot can reach Lucid and MFFU (2026-11-20 13:45)
Both firms run on Tradovate. Tradovate's own API is closed to prop and evaluation accounts
(Tradovate API Access article, as summarised by CrossTrade), so the bot cannot log in directly.
Routes, cheapest change first:
1. **CrossTrade Pro ($49/mo, unlimited accounts):** partner-level OAuth link to Tradovate with a
   REST trading API that reaches linked prop accounts. Keep the Python engine; replace only the
   order adapter (`bridge/topstepx.py` → a CrossTrade adapter). Bars can keep coming from TopstepX.
2. TradingView strategy alerts → webhook router (PickMyTrade $50/mo or TradersPost $49+), using the
   repo's Pine strategy. Needs TradingView Essential ($14.95/mo; alerts expire after 2 months)
   or Premium ($69.95/mo, open-ended). Pine-vs-Python signal parity is untested.
3. NinjaTrader strategy (C# port) on the friend's PC: no monthly router, biggest rewrite.
Cost effect on PREREG_PORTFOLIO B− (Topstep + Lucid + MFFU): the model charged $30/mo for
API access; route 1 at $49/mo lowers 2016–26 net by ~$2.5K (to ~$113.9K, ~$10.5K/yr).
C− (max slots) is unchanged or slightly better (model charged $120/mo across 8 accounts).
Topstep's rule that trading must originate from the trader's personal device applies to Topstep;
Lucid/MFFU cloud routing is their own call, so check each firm's device/VPS rule before going live.

## Live comparison set up (2026-11-20 15:40)
- `docs/PREREG_LIVE_20261120.md`: what gets compared (signal parity → execution → same-day R →
  outcome bands → account milestones), predictions from history, and decision gates.
- `scripts/export_live_trades.py` (run on the trading computer) pulls fills via ProjectX
  `Trade/search` (new `TopstepXBroker.trades`) and the bot's order decisions into `data/live/`.
- `scripts/live_compare.py --backtest` writes `docs/live_report.md`. Tested with synthetic fills
  (`tests/test_live_compare.py`). Waiting on the first live data.

## Plan figures corrected (2026-11-20 21:40, PREREG_PORTFOLIO2)
- One API subscription per platform (ProjectX for Topstep, CrossTrade $49/mo for Lucid + MFFU).
- One account at each of Topstep, Lucid, MFFU: ~$10.5K/yr (2016–26), ~$14.6K cash on hand.
- Max accounts (5/5/3): ~$49K/yr, ~$50K cash on hand.
- Staggering account start dates does not reduce risk: identical trades put the accounts back in step.

## Market mix: the cheapest way to scale (2026-11-20 22:30, PREREG_MARKETMIX)
- Same strategy on NQ, ES and YM in different accounts; markets' monthly results barely move together.
- With an anti-hedge filter (never hold opposite directions in two index markets at once — required by
  the firms' cross-account hedging bans):
  - 5 Topstep accounts: all NQ $21.2K/yr needing $15.3K cash → 3 NQ/1 ES/1 YM $16.3K/yr needing **$4.7K**.
  - Full plan (5 Topstep, 5 Lucid, 3 MFFU): all NQ $48.9K/yr, $53K cash → mixed **$38.4K/yr, $21K cash**.
- Before trading a second market live, the bot needs: per-market contract ids (MES, MYM), one engine per
  market, and a shared check of open positions across all accounts that blocks opposite-direction entries.
- ES's own edge is unconfirmed (86% vs coin flips); YM narrowly confirmed (96%).

## Bot changes for the market mix (2026-11-20 22:55) — see docs/MULTI_MARKET.md
- Tick-grid fix (live NQ too): limit prices are rounded to the tick, buys down and sells up, which fills in
  exactly the backtest's cases. ~46.5% of NQ entries were between ticks before. Two live tests updated to
  expect the rounded price (29128.0 instead of 29127.875).
- New, off by default: `BRIDGE_MARKET` (NQ/ES/YM presets), `BRIDGE_HEDGE_REGISTRY` (shared anti-hedge
  check across engines), `--find-contract`, per-market journals. Tests: tests/test_hedge_multimarket.py.

## Can profitability still be raised? (2026-11-20 23:30) — answer: not without more cash per dollar earned
Tested tonight, all pre-registered (#61–#64):
- Staggered start dates: no effect.
- Market mix NQ/ES/YM with anti-hedge filter: **yes** — the plan's best change; cash needed falls 60–69%.
- Bigger accounts (100K/150K) in the mix: more income, but 5–7× the cash; 50K stays most efficient.
- FundedNext Futures as a fourth firm: weak structure (single account $14.5K vs Topstep $44.4K); adding it
  nearly doubles cash for +11% income. Tradeify excluded by its own rule (bot can't run at other firms).
**Current best plan (2016–26 backtest):** 5 Topstep + 5 Lucid + 3 MFFU, 50K, mixed markets ≈ **$38K/yr with
~$21K cash**; Topstep-only mixed ≈ $16K/yr with ~$4.7K cash. All-NQ max ≈ $49K/yr but needs ~$53K cash.
Remaining income upside depends on live results, not on more backtest changes.


## Action for Jx: Etherscan API key (only needed to measure BNB Chain liquidations)
Why: no free public node serves BNB Chain's old logs; Etherscan's V2 API can, with a free key. Free plans may exclude
some chains (BNB is reported to need a paid plan on some tiers: unverified). Do not pay without deciding it is worth it.
1. Go to etherscan.io, create an account, then API Dashboard -> Add -> copy the key. (One key works for all chains via V2.)
2. In GitHub: repo onooo641-jpg/LONG-CONVEXITY -> Settings -> Secrets and variables -> Actions -> New repository secret.
3. Name it exactly `ETHERSCAN_API_KEY`, paste the key, save. Never paste the key in chat or commit it.
4. Tell the next session to run the `bnb_es` job (the code is ready: `liq_bnb_es` in `scripts/fetch_public.py`).

## Liquidation test #100: verdict (2026-11-21) — BUILD, in simulate-only mode first
Pre-registered in `docs/PREREG_LIQUIDATIONS_20261120.md` (four addenda, all committed before the numbers they affect). Raw output:
`docs/jx_runs/liquidations_20261120.txt` (re-run once, identical). Figures: `docs/FIGURES_LEDGER.md` LQ1–LQ8. Candidate row: #100.

**What was measured (24 months, Nov 2024 – Oct 2026).** Every liquidation on 8 chains using the Aave liquidation event (229,691 events, 67 venues, free public
nodes). Complete: Base, Arbitrum, Optimism, Polygon, Avalanche, Gnosis, Scroll, Metis. **Not measured:** BNB Chain (no free source; needs the Etherscan key in
"Action for Jx" above), Solana lenders (Kamino, MarginFi, Save, Drift: public RPC can't return 24 months), Compound-style lenders (different event; not decoded).
Bonus = collateral value − debt repaid, using daily DefiLlama prices; minus gas paid by the winner. Flash-loan fees, swap slippage, bribes and failed attempts are
NOT in the numbers, so every net figure is an upper bound.

**Which venues pass (registered test).** 7 of the 67 venues, and the idea passes overall (needed 3 venues and $2,000/month; got 7 and $1.1–1.7 million/month
paid to everyone outside the top 3). The five that matter are the main Aave v3 pools:
| venue | top-3 share (H1 / H2) | winning addresses per half | what the non-top-3 winners earned together per month (H1 / H2) |
|---|---|---|---|
| Arbitrum Aave v3 | 0.30 / 0.09 | ~1,400 | $697K / $433K |
| Base Aave v3 | 0.36 / 0.11 | 823 / 1,611 | $324K / $317K |
| Avalanche Aave v3 | 0.41 / 0.26 | 283 / 236 | $288K / $158K |
| Polygon Aave v3 (half-sample of receipts) | 0.17 / 0.09 | 1,450 / 1,653 (lower bounds) | $263K / $132K |
| Optimism Aave v3 | 0.19 / 0.38 | 487 / 598 | $106K / $41K |
Two small forks also pass (Polygon 0x8dff…, Avalanche 0x4f01…) but pay a median bot about $0–$17/month: ignore them. Gnosis, Metis and Scroll fail (top bots take 80–98%, or
too little left). Dollar amounts are before the costs listed above and are the whole pool, not one bot's share.

**How crowded.** Not crowded by the registered measure (top-3 share 9–41%), but winners are many and mostly occasional: on Arbitrum/Base/Polygon, 36–64% of value in H2 went
to addresses that won three times or fewer. Caution: if the same operator uses many addresses, "tx sender" understates concentration. Using the `liquidator` field instead,
Arbitrum's H2 top-3 share is 0.62 (fails the 60% rule); the other four still pass and 5 venues in total still pass, but combined outside-top-3 income falls to $854K / $458K a month.
The top 10 liquidator addresses hold 58–94% of the value, so a small bot competes with a small group of professionals for the big events.

**Realistic monthly income for a small bot (ESTIMATE, built from measured bots).** Look at bots that were active (12+ wins in the half) and not in the top 3. Median net per month in H2 (gas only):
Arbitrum $226, Base $31, Avalanche $729, Optimism $0, Polygon $83; 75th percentile $839 / $473 / $1,892 / $56 / $516; 90th percentile $2.8K / $2.0K / $6.1K / $0.2K / $0.9K.
Run on all five venues at once, a median bot made roughly $2.3K a month in H1 and $1.1K in H2; a 75th-percentile bot about $3.8K in H2. Expect less: those figures skip flash-loan fees (the
0.09% sensitivity only takes 1–3% off), swap slippage, reverted attempts and bribes, and they exclude bots that quit. The pool also shrank: debt liquidated in H2 was
roughly half of H1 (Arbitrum $70M → $41M; Base $42M → $32M), because liquidations follow market stress. Gas per winning liquidation: Arbitrum $0.8, Polygon $0.6,
Base $4.6, Avalanche $5.8, Optimism $7.8 (the last three show bidding for priority). **A new bot's real capture rate is unknown and unmeasurable without running one.** For scale
against the benchmark: Topstep recycling is $4,097/yr per slot; a liquidation bot in the middle of the pack on these five venues would be roughly $13–28K/yr before costs and variance, with no capital at risk if it uses flash loans. Treat that as a hypothesis, not a forecast.

**Five-part filter (HANDOFF_NONPROP).**
1. Repeatable: PASS (measured). about 6,000–29,000 events per year on each main pool; every month had liquidations in both halves.
2. Long-lived: PASS (measured 24 months; Aave v3 has existed since 2022, third-party knowledge). Risk: the bonus is a governance parameter and could be cut.
3. One reusable setup: PASS. The same event and functions on all measured chains: one codebase, one config entry per chain.
4. Capped downside per attempt: PASS by design if the bot uses a flash loan and reverts unless profit exceeds a threshold: loss per failed attempt = gas (cents on Arbitrum/Polygon, a few dollars on Base/Optimism/Avalanche when bidding). Not yet tested live: contract bugs and key theft are the real risks.
5. Scales by adding copies: PARTIAL. Adding chains/venues adds income without adding capital; adding capital does not raise income, and extra bots on one venue split the same pool.

**Verdict: BUILD, but only simulate-only first.** The structural test passes and survives the stricter identity check. What is still unknown, and only a shadow-mode bot can measure: how many liquidations a new bot wins against the professionals, and the real after-slippage profit. Nothing here authorises spending or deployment.

**Design: one reusable bot for the passing venues (Arbitrum, Base, Avalanche, Polygon, Optimism; skip the two small forks and all failing venues).**
- Watcher (per chain): follow new blocks via a public RPC; keep the set of open borrowers from Borrow/Repay/Supply events; each block re-score only accounts with health factor < 1.05 via the pool's `getUserAccountData`; re-score all when an oracle price moves.
- Executor contract (one Solidity contract per chain, identical code): `flashLoanSimple(debtAsset, amount)` → `liquidationCall(collateral, debt, user, amount, false)` → swap collateral to debt asset on the best DEX route → repay loan + premium → send the remainder to the owner wallet; **revert unless profit ≥ min_profit**. This is the downside cap.
- Before sending: `eth_call` simulation; only send if simulated profit > gas cost × margin; priority fee capped at a fixed share of expected profit.
- Per-chain config: pool address, flash-loan source, DEX router, gas cap, daily gas budget, max debt per attempt, kill switch.
- Shadow mode (stage 0, no money): run the watcher and simulations only; log for each on-chain liquidation the simulated profit we could have made and whether our trigger would have fired before the winner's block. Output: would-win rate and simulated profit per venue per month. Pre-register the go/no-go thresholds before starting.
- Stage 1 (needs Jx's explicit approval, not part of this verdict): tiny live budget (gas only, no capital) on the best venue, with a hard daily loss cap.
- Risks to price: smart-contract bug, key management (hot wallet holds only gas money), governance cutting bonuses, volatile income, and competition from professionals on the largest events.

**Next step (no spending).** Write the shadow-mode watcher and the executor contract with a local fork test; pre-register the stage-0 pass criteria (for example: simulated net ≥ $X per venue per month over 4 weeks and a would-win rate ≥ Y%) before it runs.

## Action for Jx: running the liquidation shadow bot faster / always-on (decision only, nothing is bought)
Current setup (free): GitHub Actions on a public repo, chained ~6-hour jobs, public RPCs. It runs 24/7 with short gaps at restarts and is slower than a real bot (public RPCs, one cycle every ~1-2 seconds at best).
If the shadow result is "latency-limited", the cheapest upgrade is, in order (all prices are third-party estimates, unverified, check before buying):
1. A small VPS, about US$4–10/month (Hetzner, DigitalOcean, Vultr class), running the same `scripts/liq_shadow.py`. Still public RPCs; removes the restart gaps.
2. A paid or free-tier private RPC (Alchemy/QuickNode/Chainstack class). Free tiers may be enough for the watcher; websocket/low-latency tiers are roughly US$50–100+/month per the vendors' public pricing.
3. For a later LIVE pilot (needs your explicit approval, not part of this test): a fresh hot wallet funded with only gas money (assumed US$50–100 per chain, loss capped by design), executor deployment gas (assumed under US$5 per L2 chain, more on Polygon/Avalanche spikes), plus items 1–2. Rough total: US$300–500 one-off + US$10–110/month. Risks: contract bug, key theft, governance cutting bonuses, competition.
Nothing above is purchased or started.

## Liquidation shadow test: progress (2026-11-21)
Pre-registered: `docs/PREREG_LIQ_SHADOW_20261121.md` (3 addenda). Executor contract (`contracts/src/LiqExecutor.sol`) passed all four fork tests on all five venues (Arbitrum, Base, Optimism, Polygon, Avalanche); logs `docs/jx_runs/liq_forktest_*`.
Watcher v2 (`scripts/liq_shadow.py`) runs on GitHub Actions (cron every 6 h, one job per chain, free on this public repo): ~0.6–2 s per cycle on Arbitrum/Optimism/Avalanche, Polygon and Base slower; positions cached with `actions/cache`; logs committed to `data/shadow/`.
The 4-week clock started about 2026-11-21 06:10 UTC (when all five venues were watching). Scheduled checks: 2026-11-22 (health), 2026-11-28 (week 1, includes the pre-registered early-kill rule), 2026-12-05, 2026-12-12, and the final verdict 2026-12-19; each fires a fresh session that runs `scripts/liq_shadow_summary.py` and commits the result.
Honest expectation: the public-RPC watcher is slower than a VPS with a private node, so a poor fire-first rate may be latency-limited; the final report separates that from "no opportunity" using the near-miss counts.
Nothing is bought, deployed or sent on-chain; no keys with funds exist.

## Liquidations: crash months (2026-11-21) — for Jx, plain language
Source for every number below: `docs/jx_runs/liq_monthly_20261121.txt` (command `uv run python -I scripts/liq_monthly_20261121.py`, pre-registered in `docs/PREREG_LIQ_MONTHLY_20261121.md`); five main Aave v3 pools, Nov 2024 – Oct 2026. **M** = measured from on-chain data, **E** = my estimate.
- **How often crashes happen (M).** Income is lumpy. The 5 biggest months paid 70.3% of all bonus ($45M over 24 months; 2025-02 $12.0M, 2025-10 $6.9M, 2026-02 $5.4M, 2025-11 $4.2M, 2025-04 $3.1M; your figures were $11.2M / $6.6M / $5.1M / $4.0M, within about 7%, the difference is probably the price source). 10 of 24 months paid under $200K. Months above $3M: 6 of 24 (one in four), above $1M: 9 of 24. Since the SVR switch on Arbitrum/Base (March 2026) only one month (June 2026, $1.9M) was above $1M; the other seven were $18K–$130K. So a crash like 2025-02 or 2025-10 has not been tested against the post-SVR world (M); whether the next one pays a public bot is unknown (E).
- **Quiet month vs crash month for a median bot (M, gas only).** In a quiet month the typical active bot outside the top 3 made $0 (most active bots simply win nothing that month); the median bot that did win made $0–$40. In the 5 big months the median bot that won made $196–$1,677 (2025-02 $1,677; 2025-04 $943; 2026-02 $807; 2025-10 $351; 2025-11 $196), and the 75th percentile of all active bots reached $1.2–2.0K in three of them (2025-02, 2025-04, 2026-02). Counting every active bot (zeros included) the median was under $200 in 23 of 24 months (zero in most) and $248 only in 2025-04. By month: the median winning bot made under $200 in 17 of 24 months, $200–$1,000 in 6, over $1,000 in 1.
- **Against Topstep (M for liquidations, repo figure for Topstep).** Topstep recycling pays in 20% (one market) to 32% (two markets) of months (`docs/NOTES_JX.md` above, `docs/PREREG_20261109.md`). A liquidation bot beats $1,000 in a month for the median winner in 4% of months and earns $200 or more in 29% of months: similar lumpiness, but much smaller median payouts, and the big months go mostly to the top bots (top 3 months = 52% of all outside-top-3 net).
- **Crashes can't be predicted, but they can be detected as they start (E).** Prices move first, then positions near the liquidation line fall over together. The shadow watcher now logs, once an hour per chain, how much debt sits within 2%, 5% and 10% above the line (debt near the line) and sets a "stress" flag when 10 or more eligible liquidations happen in an hour or the chain's main token moves 5% inside the hour. That tells us a crash is starting in minutes, not in hindsight. Nothing in these logs has been analysed yet (data only started at the 08:50 UTC restart); the first readings are in `data/shadow/<chain>/near_line.jsonl`.
- **New alert (design, tested).** If a chain has gone more than 60 minutes without a committed heartbeat, a GitHub issue "liq watcher down: <chain>" is opened (one per chain, closed when it recovers). Heartbeats reach the repo every 20 minutes, so an alert can lag about 25 minutes. Missing a crash is the costliest failure, so a quiet repo with open issues is the signal to check.
- **CRASH WINDOW report (design; nothing to report yet).** After the registered shadow verdict, the watcher keeps logging until the first rolling 30 days with more than $1,000,000 gross bonus across the five venues finishes, or until 2027-06-30. For that window only, a separate line reports fire-first rate and simulated net (CRASH-WORTHWHILE if fire-first is at least 10% and net at least $2,000, otherwise CRASH-NOT-WORTHWHILE, "latency-limited" if more than half the misses were within 3 blocks). It never overrides the registered verdict. Status: no verdict published yet, so no window. A monthly scheduled session (12th of each month) updates this line here.
- **Honest limits (E).** The monthly table counts gas only, not flash-loan fees, swap slippage, bribes or failed attempts, so every dollar figure is an upper bound. Bot identity is the transaction sender (an operator with many addresses looks like many bots). The median-bot numbers describe bots that were already active in each half, not what a newcomer would make.

## Liquidation replay: can a public bot be first? (2026-11-21)
Pre-registered in `docs/PREREG_LIQ_REPLAY_20261121.md` (5 addenda); output `docs/jx_runs/liq_replay_20261121.txt` (re-run identical); ledger RP1–RP9. **M** measured, **E** estimate.
- **Same block as the price update (M).** For 1,204 liquidations (above $50 bonus, April–October 2026) on Arbitrum, Base, Avalanche and Polygon, 64–78% landed in the same block as a price update of their price feed; for random blocks it is about 0%. Those are won by whoever lands with the price update. On Arbitrum and Base that is the Chainlink SVR auction (web research, third-party: Aave adopted it in March 2026), which a public-RPC bot cannot beat.
- **What is left to reach (M, upper bound).** Even a watcher that detects instantly could reach only about 13% of events (10% of the dollar value) pooled; per venue 10–16% of events, 8–12.5% by value. If our delay is 5 blocks it falls to 7–12% by count and 4–10% by value. Optimism is excluded: the price feed I resolved shows no updates, so its 96% is a data failure, not an opportunity.
- **Registered screen: PLAUSIBLE, but marginal (M).** Pooled reachable share is above the 10% line only by 3 points by count and by 0.1 points by value, on a sample of 1,204 events, so it could sit on either side of the line.
- **What this means for the shadow GO bar (E, my judgment).** GO needs fire-first on at least 10% of eligible liquidations. The reachable ceiling is about 13%, so a bot would have to win nearly every reachable event, against professionals. I think GO is unlikely (roughly one chance in eight or ten), but the shadow test, not this replay, decides.
- **Gas bidding (M).** Winner gas is under 1% of the bonus at the median and about 0.01% on events above $5,000; on small events the 90th percentile is 8–9% on Base/Avalanche and 38% on Optimism. So gas is not what eats the profit on big events.
- **Competition by size (M).** Addresses with 50 or more wins take 72–97% of the value on Arbitrum, Avalanche and Polygon; Base (41–61%) and Optimism (36–50%) are the least locked up.
- **June 2026 vs the other months (post-hoc, M).** June 2026 ($1.9M bonus, the only post-SVR month above $1M) shows 13.7% reachable by count / 10.9% by value against 10.8% / 6.5% for the other six months. A bigger month does not obviously change who can be first.
- **Limits (M/E).** Base uses the oracle's latest source and a 33-minute window (the only endpoint that worked); the replay assumes instant detection (a ceiling); the "actions-arm" latency in the output is polluted by restart cycles and is not used.

## Liquidation levers swept: recommendation and monthly profit (2026-11-22)
Evidence: `docs/jx_runs/liquidations_20261120.txt`, `liq_replay_20261121.txt`, `liq_monthly_20261121.txt`, `liq_morpho_20261121.txt`, `liq_morpho_replay_20261121.txt`; ledger LQ, RP, M, MO, MR rows. **M** measured, **E** my estimate.
- **Venues measured.** Aave v3 main pools on Arbitrum/Base/Avalanche/Polygon/Optimism ($45M bonus in 24 months) and Morpho Blue on Base ($54M). Both pass the "is there money outside the top 3" test (M). Unmeasured: BNB (no free data), Solana lenders, Compound/Euler/Fluid (no decoder; same oracle-update structure expected, E).
- **Who gets it (M).** Aave: 64–78% of liquidations land in the same block as a price update; reachable for a perfectly fast block-level watcher 13% of events / 10% of value. Morpho Base: 93.8% same block, 97.9% within 1 block; reachable 2.1% / 0.8% (registered verdict DROP at block-level latency). In the stress months that carry the money (Morpho June and October 2026) 0% was reachable.
- **Lumpiness (M).** Aave top 5 months = 70% of the bonus, Morpho 89%. Since March 2026 Morpho Base paid $12.1M (June $9.0M, October $1.9M, other six months $0.07–0.5M) and the five Aave pools $2.3M.
- **Typical existing bot (M, gas only).** Median active non-top-3 bot that won in a month: Aave pools about $255 a month averaged over 24 months (about $105 over the last 8); Morpho Base about $899 a month over 24 months, driven by 4 big months (Oct 2025 $9,905, Feb 2025 $4,616, Feb 2026 $2,221, Jan 2025 $1,343) and about $85 a month over the last 8 months.
- **Remaining speed lever (not tested, needs money).** Bots reading Base's 200 ms pre-confirmed "flashblocks" could still race for same-block events. Base's docs say the raw flashblocks WebSocket is not for applications and there is no free public WebSocket RPC, so this needs a paid node provider (Base docs, third-party). Same for joining the Chainlink SVR auction on Arbitrum/Base (bond about 0.1 ETH recommended, onboarding via Chainlink, economics unverified). Both need Jx's approval; neither is bought.
- **Recommendation (E).** Do not build or spend on a liquidation bot now. Let the free shadow test (verdict 2026-12-19, week-1 kill check 2026-11-28) and the log-only crash-window watcher run; they cost nothing. Reopen only if the shadow shows fire-first near 10% or a crash window shows a public bot capturing value. Put time and money into Topstep/Lucid/MFFU instead.
- **Potential profit per month for a NEW small bot (E, built from the measured typical-bot figures above, before slippage, bribes and failed attempts, which I could not observe).** Right now (quiet regime): about $0–$100 a month. Averaged over a full cycle that includes crash months: about $150–$600 a month (roughly a fifth to a half of the typical existing bot's $1,150 a month, Aave $255 plus Morpho $899), which is $1.8K–$7K a year, but about two thirds of that arrives in 4–5 months and most months are near zero. A crash month for a bot that already wins its share might be $1K–$5K (E). Best case with paid speed infrastructure and SVR access: $500–$1,500 a month averaged (E, unproven). For scale: one Topstep slot is $4,097 a year, about $340 a month (backtest, repo figure) and scales to about $38K a year with the multi-firm plan.

## Liquidations: best case checked (2026-11-22)
Pre-registered `docs/PREREG_LIQ_BESTCASE_20261122.md`; output `docs/jx_runs/liq_bestcase_20261122.txt` (identical on re-run); ledger BC1–BC6. **M** measured, **E** estimate. This SUPERSEDES the "best case $500–1,500 a month, unproven" line above, which was an estimate; the data say the following.
- **A typical incumbent bot makes a lot on average and nothing in the middle (M, gas only).** Active non-top-3 bots (12+ wins in a half-year): mean income per bot-month $1,022 on the Aave pools and $2,143 on Morpho Base over 24 months ($587 and $881 over the last 8 months), but the median bot-month is $0. The mean comes from crash months (5 biggest months: mean $3,127 and $5,351; quiet months: $98 and $84).
- **So "USD 500–1,500 a month" is supported only as parity with incumbents (M).** A bot present at one Aave-pool-sized and one Morpho-sized slot would have averaged $3,165 a month over 24 months and $1,468 over the last 8 (gas only). Reaching parity with incumbents is the unproven part: nothing in this data says a new bot wins its share, and it cannot be tested without paying for speed.
- **Who wins same-block events (M).** Not one or two firms: 109 distinct winners over 980 sampled Aave events and 114 over 378 Morpho events; top 3 hold 38% and 26%, top 10 hold 71% and 59%, and addresses with 50+ wins hold 75–77% of the value. It is a field of professionals, not a monopoly.
- **Your RM 1,200 (about USD 300) a month question (E).** As an average over a full cycle it is inside my range: roughly a 10–20% chance of reaching incumbent parity times a parity income of $1.5–3K a month gives an expectation of about $150–600 a month. But it is NOT passive and NOT steady: most months pay near zero, about two thirds of the year's income arrives in 4–5 months, the typical bot-month is $0, and it needs a build, infrastructure, a gas wallet and monitoring. Costs not in any figure: swap slippage, bribes, failed attempts, the Chainlink auction's share (reported recapture about 53% of the available value goes to the protocol side, third-party), infrastructure.
- **Paid-speed route cost (third-party, unverified).** Providers document Base flashblocks (200 ms pre-confirmations) on their normal Base endpoints, with free tiers (Chainstack Developer plan 3M requests a month, Alchemy 30M compute units a month) and paid plans from about $199 a month (Chainstack Pro) to $999 (QuickNode Business). A free tier is enough only for short measurement windows (a continuous 10 requests per second would use about 26M requests a month). Nothing is purchased.

## Action for Jx: Base flashblocks-latency test (optional, free tier first; nothing is bought)
Only you can do this because it needs an account. Why: the one remaining speed question is whether a bot reading Base's 200 ms pre-confirmed blocks can win same-block liquidations; the block-level tests cannot see inside a block.
1. Create a free account at a Base RPC provider that documents flashblocks (for example Chainstack or Alchemy; free tiers exist, third-party).
2. Create a Base mainnet WebSocket/HTTPS endpoint URL that includes the API key.
3. GitHub: repo Settings → Secrets and variables → Actions → New repository secret named `BASE_FLASHBLOCKS_URL`, paste the URL, save. Never paste it in chat or commit it.
4. Tell the next session; it will pre-register and run a short-window flashblocks measurement on the free tier (the code path will be written then). Spending beyond the free tier needs your explicit approval.

Update 2026-11-22: the watcher now accepts a private RPC URL per chain through the environment variable `LIQ_RPC_<CHAIN>` (tried first, never printed), and `docs/LIQ_VPS_SETUP.md` explains how to run it log-only on a VPS. Renting the VPS is for Jx; nothing is rented.

## 2026-11-22 — official-page verification: four firms do not accept Malaysian residents
Read directly from each firm's own pages (rendered on GitHub Actions; details and URLs in `docs/PROP_VERIFY_20261122.md`):
**MyFundedFutures** (restricted-countries policy, 2026-10-14), **FuturesElite** (terms), **Alpha Futures** (countries with limitations), **Blue
Guardian Futures** (2026-11-13) list Malaysia as restricted. MFFU is one of the three firms in the multi-firm plan (`PREREG_PORTFOLIO2_20261120`),
so that plan needs a replacement firm for a Malaysian account holder (whether it matters depends on whose name the accounts are in).
Topstep 50K rules match the model; its XFA **Consistency path** prices at $46,492 vs $44,359 for Standard (same trades, same costs).
TTP Futures Prime 50K rules match the model ($49,057). Verification of the remaining firms continues.

## Liquidation levers: final table after the full sweep (2026-11-22)
Supersedes the lever lines above. **M** measured (gas only, before slippage, bribes, failed attempts), **E** estimate for a NEW small bot per month. Evidence: ledger LQ, RP, M, MO, MR, BC, NC, CM rows.
| Lever | Measured result | New-bot profit per month (E) | Verdict |
|---|---|---|---|
| Free setup, Aave five pools (block-level) | 64–78% same-block; reachable 13% of events, 10% of value | $0–$100 | shadow test decides (28 Nov kill check, 19 Dec) |
| Morpho Base (block-level) | 93.8% same-block; reachable 2.1% / 0.8% | $0–$20 | DROP (registered) |
| Paid speed (VPS plus flashblocks provider) | incumbent mean $1,022 (Aave) + $2,143 (Morpho) per bot-month over 24 months, $587 + $881 over the last 8; median $0 | $100–$500 net; best case $1,500–$3,000 if parity | needs your money; parity unproven |
| Chainlink auction (Aave Arbitrum/Base) | about 93 bidders; protocol side about 53% (third-party) | $0–$200 | unverified economics, small post-March pool |
| Newer Aave chains | Sonic, Linea, Ink, zkSync, Soneium killed (best venue $1.9K in 3 months); Celo unmeasured; Mantle passes but tiny ($162K in 24 months, mean $64–147 per active bot-month) | $0–$50 | not worth building |
| Compound v3 (collateral buys) | no venue passes (near misses); $4.3M gross in 24 months on the two big USDC Comets but only $104K in the last 8; 47–67% of buys are atomic absorb-and-buy | $0–$20 now; crash months only | dead since March 2026 |
| Not measured | BNB, Solana lenders, Euler, Fluid, Silo | unknown | no free data or decoder |
**Total for a typical month: about $0–$100 now; about $100–$600 averaged over a cycle with crash months (E).** Reasons not to build now: every free lever failed or was killed; the only levers with real money (same-block races) need paid speed or auction access and parity with professionals, who hold 75–77% of the value; the median incumbent earns $0; about two thirds of a year's income arrives in 4–5 months; one Topstep slot is about $340 a month and the multi-firm plan about $3,170 (backtests, repo figures). What would change this: shadow fire-first near 10%, a crash window showing a public bot capturing value, or a decision by Jx to fund the paid-speed test.

## 2026-11-23 — Malaysia-eligible multi-firm portfolio (replaces the Topstep + Lucid + MFFU plan for a Malaysian account holder)
`docs/PREREG_PORTFOLIO_MY_20261123.md`: Topstep (Consistency path) + TTP Futures Prime + DayTraders EOD + LucidDaily, one 50K account each, same
trades: **$195,000 over 2016–26 ($18,006/yr; $1,500/month on average, $3,136/month over the last 36 months), worst dip −$13,858.** At each
firm's account cap (5 each): $975K / $90K per year, worst dip −$69,291 (the swings add up because every account takes the same trades).
FTMO 2-Step (CFD) fails the flag rule (coin flip ≈ 0, deep dips), so the CFD route adds nothing structurally.

### Flashblocks probe (2026-11-24)
Free public Base endpoint does NOT expose sub-block (pending) state (0/339 polls). Speed lever needs a provider endpoint with flashblocks: Jx step = create a free-tier account at a Base RPC provider that lists flashblocks, add the URL as GitHub secret `BASE_FLASHBLOCKS_URL`; I then run the same probe against it. Shadow watcher was down ~2 h on 2026-11-24 (cron dropped); restarted and now self-chains. Watched uptime so far ~57% of wall time per chain (≈43 h each), a coverage risk for the 75% inconclusive rule.

### Base changed (2026-11-24): flashblocks retired, 200 ms blocks
Per Base docs (read via Actions run 45377543121): 200 ms canonical blocks since 2026-11-05; Flashblocks and `pending` state gone. So "paid flashblocks" is dead as a speed lever on Base; the Action for Jx item about `BASE_FLASHBLOCKS_URL` is CANCELLED (do not register for it). Base replay/shadow numbers reflect the old 2 s era or a slow 8 s cycle: Base is unmeasured for the new regime. Speed on Base now means WebSocket `newHeads` on a low-latency VPS/provider, untested. Arbitrum (250 ms), Polygon, Avalanche, Optimism are unaffected by this change. Shadow Addendum 5 records it.

## 2026-11-26 — pre-live audit: one modelling error, all prop figures lowered
`docs/AUDIT_PRE_LIVE_20261126.md`. Signals, look-ahead, live parity, costs and contract caps checked and correct. Error: the loss limit
was judged on closed trades; Topstep checks open P&L in real time (help.topstep.com 8284204). Fixed (`realtime_mll=True` default).
Topstep 50K Consistency: $46,492 -> **$37,406** ($3,454/yr), coin flip $18,005 -> $6,384 (still qualifies). Start money: median
-$1,181, 1 in 10 -$2,585, worst -$3,475. LucidDaily, TTP Prime and DayTraders EOD fail the coin-flip bar if they check open P&L the same
way (unconfirmed): the 4-firm plan is on hold; Topstep only. Next step unchanged: one live Topstep account, ~$1,200 to start.

## 2026-11-26 — prop search 2 (more firms that pass on the corrected model)
`docs/PREREG_PROP_SEARCH2_20261126.md`. Re-priced every other modelled product (TTP Instant/Prime 100K/150K, LucidDirect, Tradeify, FTMO
Futures, TFD, Blueberry, FundedNext, Bulenox, Traders Launch, DayTraders S2F) on the corrected model.

**Result:** no new qualifier at real prices; the count stays at 3 (LucidFlex 50K, Topstep 50K Consistency, LucidDaily $85.40).

**Near misses:**
- **DayTraders S2F 50K:** qualifies at $199. At the reported $342 it fails only on the dip under EOD ($45.7K, dip −$6.8K vs −$6.1K bar).
- **LucidDirect 50K at $360:** EOD $38.1K, but dip −$7.6K.

Firm pages say Lucid ignores unrealized P&L, and FundedNext and Blueberry breach on live equity. The others don't say.

**Jx can settle two facts only he can see:**
1. the DayTraders S2F 50K checkout price;
2. whether DayTraders' S2F loss limit counts open P&L.

### 2026-11-26 — Topstep Labs (static drawdown) priced from the official page
13 Labs products: static combines 25K–150K, Daily Payouts+, $1.5K/$3K/$6K Challenges. None qualifies under the registered bar.

Strong near-misses that fail only on the worst dip:
- **150K Static Consistency ($279):** $74.8K over 2016–26, coin flip $29.5K (91% positive), worst dip −$9.5K.
- **100K Static Consistency ($199):** $42.5K, coin flip $17.3K (89%), dip −$6.9K vs −$6.1K bar.

The dip bar is scaled to 50K accounts. If Jx accepts a ~$7–10K buffer, these are the best rule-driven products found.

**$3K Challenge ($49):** $15.1K, coin flip $7.0K (85%), dip −$2.2K. It misses on real net, and two at once would clear it.

`docs/PREREG_PROP_SEARCH2_20261126.md` Stage C2.

## 2026-11-26 — prop search 3: Jx's three levers (`docs/PREREG_PROP_SEARCH3_20261126.md`)
**Engine.** Audit addendum 3, from the other session, now measures exit-bar open loss only up to the fill. Topstep 50K Standard is
$38,034; bar: real ≥ $19,017, dip ≥ −$5,794.

**Results:**
- **Different markets:** LucidFlex 50K on **ES qualifies** ($26.5K, flip $14.9K, dip −$2.2K). **5 LucidFlex 3 NQ / 1 ES / 1 YM: net
  $163K vs $206K, worst cash $10.0K vs $19.5K → worth doing.** On Topstep the mix does not help.
- **Bigger accounts:** the same $900 risk makes them worse. With scaled risk, the Topstep 150K Static Consistency makes $110K (flip $33K)
  but its dip is −$8.9K, so it is an option only.
- **Open-loss-ignoring firms:** **Funded Futures Network (new, qualifies when bought ≤ $96 / $154 / $149 for 50K / 100K / 150K with
  the activation waived)**. City Traders Imperium is CFD; the bot would need an MT5 port.
- **DayTraders 100K / 150K Static qualify if priced ≤ $90 / $93.**

**Jx to supply:**
1. the DayTraders 100K/150K Static checkout prices;
2. FFN's non-promo discount level, and whether the waived activation applies on the bot's platform;
3. a decision on porting the bot to MT5 for CTI.
- **Overnight (prop search 3 part 2):**
  - The **Topstep $3K Challenge ($49) qualifies** on the corrected engine: $24.8K, flip $7.7K, dip −$1.2K; break-even $68.
  - Start money:
    - FFN 50K/100K/150K at the promo: median −$0.7K to −$1.0K, worst −$4.1K to −$5.6K;
    - LucidFlex ES: worst −$2.4K;
    - DayTraders Static pays slowly (first payout after ~1 year).
  - ES and YM work only at LucidFlex.
- **2026-11-27, with Jx's prices:**
  - **DayTraders 100K Static ($80) and 150K Static ($95) qualify**: $22.0K / $48.4K over 2016–26, flip $7.5K / $5.4K, dip −$4.0K / −$3.1K.
    Slow: first payout after about a year, and about half of the starts are still down at 12 months.
  - **FFN 50K is borderline**: it passes only if resets are also bought at the ≥ 50% promo price. FFN 100K/150K at 50% off fail on the dip.
  - City Traders Imperium is parked.
  - **Qualifying set now:** LucidFlex 50K (NQ, ES), Topstep 50K Consistency, LucidDaily, Topstep $3K Challenge, DayTraders 100K/150K
    Static. New firm: DayTraders.
  - Connectors needed before going live: Lucid (CrossTrade), DayTraders and FFN (Rithmic); the bot today speaks only ProjectX.

## 2026-11-27 — go-live: CrossTrade connector for Lucid and DayTraders (`docs/GO_LIVE_MULTIFIRM.md`)
- **Built:**
  - `bridge/crosstrade.py`: NinjaTrader 8 via the CrossTrade NT8 Add-On. It covers Lucid, DayTraders and FFN, so no custom Rithmic
    client is needed.
  - `BRIDGE_BROKER=crosstrade` is wired into `bridge.live` (preflight, roundtrip, dry run, live).
  - One round-trip proof per engine.
  - Engine-scoped anti-hedge claims across accounts and markets.
  - 535 tests pass (16 new in `tests/test_crosstrade.py`).
- **Verified:** against CrossTrade's rendered API reference only (run 45929437254). No real server yet.
- **Differences from Topstep:**
  - The stop and target go on after the first fill (cancel_and_bracket), so there are about 2 s unprotected per trade.
  - A partial fill is treated as the whole fill.
  - A resting entry is unprotected if the engine dies.
  - Bars are assumed stamped at their close (NinjaTrader convention), to be confirmed on the chart.
- **Mechanical fix:** `search_contracts` and `trades` had been placed on `DryRunBroker` instead of `TopstepXBroker`, so
  `--find-contract` and `scripts/export_live_trades.py` would have crashed. Moved.
- **Needs Jx:**
  - a CrossTrade **Pro** plan (the REST API needs Pro or above; the price was not captured);
  - NinjaTrader 8;
  - a sim account for steps 3–4;
  - which computer and accounts run the new firms.
- **Status and checklist from here on:** `docs/HANDOFF_GO_LIVE_CROSSTRADE.md`.
  - Pricing: CrossTrade Pro is $49/month, with a 7-day free trial that includes the API (third-party).
  - Jx's NinjaTrader sim account exists (trial ends ≈ 2026-12-10).
  - The setup was handed to a local session on Jx's PC, because Remote Control could not share the PC's folders with a cloud session.

## 2026-11-27 — CrossTrade practice test: prepared for Jx's PC (`docs/CROSSTRADE_PRACTICE_JX.md`)
- **Ran from a cloud container, not Jx's PC** (his computer offered no folder to the session), so NT8, the Add-On and the real
  CrossTrade server were not reachable; crosstrade.io itself is also blocked here. Steps 2–6 of the practice test still need the PC.
- **Step 1 (tests):** `uv run --with pytest python -m pytest -q tests/test_crosstrade.py tests/test_multifirm.py` PASS (25 tests);
  full suite 423 passed, 117 skipped (data-dependent skips in this checkout).
- **Re-checked against the saved CrossTrade reference:** bar time format (`2026-03-18T20:00:00.0000000Z`, 7-digit fractions) parses;
  cancel_and_bracket fields/semantics, GET order by our own id, flatten `cancelOrders`, and the Bearer key location
  (My Account → Security → Reveal) match the connector. Bar stamping (close vs open) is still not settled by the docs.
- **Mechanical fix:** the connected check never printed the newest bar, so the by-hand chart comparison could not be done.
  `bridge/preflight.py: newest_bar_line` now prints its PC-time and New York minute, OHLCV, and the NT8 chart label to find
  (test added in `tests/test_crosstrade.py`).
- **New:** `scripts/crosstrade_collect.py` (copies a New York day's journal rows to `docs/jx_runs/crosstrade_test_journal_<YYYYMMDD>.jsonl`,
  refuses rows that look like secrets, logs PASS/FAIL below; 4 tests), `-Collect` on `scripts/crosstrade_test.ps1` (collect,
  `git pull --rebase`, commit, push), `scripts/crosstrade_schedule.ps1` (Task Scheduler, Mon–Fri 09:25 New York = 22:25 Malaysia
  until US clocks change on 2027-03-14, wakes the PC). The .ps1 files were not executed (no PowerShell here); first real run is on the PC.
- **Needs Jx:** NT8 desktop + live 1-minute MNQ bars; CrossTrade trial started Sun 29 / Mon 30 Nov; the user variable
  `CROSSTRADE_API_KEY`; then the three commands in the guide.

### 2026-11-27 (local session on Jx's PC)
- Cloned the branch to `C:\trading\LONG-CONVEXITY`. `uv` was already installed.
- `uv run --with pytest python -m pytest -q tests/test_crosstrade.py tests/test_multifirm.py tests/test_crosstrade_collect.py`:
  PASS (29 tests).
- Both `.ps1` scripts parse without errors in Windows PowerShell (parse check only; no step run through to CrossTrade yet).
- NinjaTrader 8.1.9.1 was already installed and running. Its log shows price feed Connected (`Simulation` connection, 12:59 PC
  time). MNQ 12-26 minute files for 23-27 Nov are cached. Live new bars: not yet confirmed.
- CrossTrade Add-On 1.14.2 is installed and loaded by NinjaTrader. Its Connected status and the trial's start date: not confirmed.
- This PC already had: wake timers enabled, and no sleep on mains power (sleeps after 10 min on battery, so keep it plugged in).
- Set a repo-local git identity (it was empty, so the unattended collect commit would have failed). `git push --dry-run` passes
  without a prompt.
- Opened the `-Step savekey` window. Waiting for Jx to paste the key.

## 2026-12 — CrossTrade practice test: run log (written by `scripts/crosstrade_collect.py`)
- 2026-11-27 check: **FAIL** (exit 1; 0 rows: no journal rows). Journal: `docs/jx_runs/crosstrade_test_journal_20261127.jsonl`.
- 2026-11-27 check: **FAIL** (exit 1; 0 rows: no journal rows). Journal: `docs/jx_runs/crosstrade_test_journal_20261127.jsonl`.
- 2026-11-27 check: **PASS** (exit 0; 0 rows: no journal rows). Journal: `docs/jx_runs/crosstrade_test_journal_20261127.jsonl`.

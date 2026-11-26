# Prop search 3: Jx's three levers + the remaining search — pre-registered 2026-11-26, before any of these runs

**Jx (2026-11-26):** "investigate these, incorporate both".

His three levers:
- (A) trade different markets in different accounts;
- (B) bigger accounts, which have more room under the corrected model;
- (C) more firms whose loss limit ignores open losses.

My three:
- (D) Funded Futures Network and the never-priced firms;
- (E) break-even promo prices for the near misses;
- (F) a dip bar scaled to account size, as a second reading.

**Bars (both reported for every row):**
- **Registered bar** (unchanged from the audit), all three must hold:
  - real ≥ 50% of Topstep 50K Standard (bot, real-time model; $17,562);
  - coin-flip median ≥ $5,000 (200 flips, seed 1, `radar_price.flip`);
  - worst dip ≥ 1.5 × Topstep's (−$6,088).
- **(F) size-scaled reading (Jx's call, reported beside the registered verdict, never replacing it):** the same, except the dip limit is
  −$6,088 × (the account's max loss ÷ $2,000).

Strategy unchanged: the friend's orders from `strategies/ltf_sweep.py`. Topstep is on the real-time model; Lucid EOD (its own page);
other firms real-time unless their own page states unrealized P&L does not count.

## (A) Market mix on the corrected model
**Trades.** ES and YM orders were regenerated from the unchanged strategy (`generate_orders`; the cached files are git-ignored), with
the configs of `scripts/marketmix_20261120.py`. Check: with `realtime_mll=False`, single-account Topstep must reproduce the earlier
figures (NQ $44,359, ES $20,338, YM $11,744) within 1%, or stop.

**A1, single accounts.** ES and YM alone on each qualifying product (Topstep 50K Consistency, LucidFlex 50K DLL ON, LucidDaily $85.40),
corrected model, same bars.

**A2, portfolios.** `marketmix_20261120.py --compliant` (anti-hedge filter) re-run on the corrected model:
- T5-NQ vs T5-mix (5 Topstep: 3 NQ / 1 ES / 1 YM);
- the same on Lucid (5 LucidFlex).

Reading (registered 2026-11-20, unchanged): the mix is worth doing if net ÷ cash on hand is ≥ 15% higher than all-NQ and net is ≥ 75%
of all-NQ.

## (B) Bigger accounts with the SAME $900 risk per trade
On a bigger account the bot keeps the 50K risk, so the account has more room.

Products, corrected model:
- Topstep 100K/150K Standard, Consistency and Static (both paths);
- LucidFlex 100K/150K (EOD);
- TTP Prime 100K/150K;
- DayTraders Trail 150K (official rules, Stage D form);
- DayTraders Static 100K/150K (official rules; price not known: shown at the 50K Static's $55 as a floor and flagged).

Risk $900. Also reported: risk 0.45 × MLL (as in search 2) for comparison.

## (C) Firms whose loss limit ignores open (unrealized) losses
Search the stored official pages (`data/public/propverify/`, including the new FFN/BluSky/IQ/Finotive renders) and the web for explicit
statements that unrealized P&L does not count toward the max loss or drawdown.
- A firm counts as EOD-ignoring only on an official-page quote.
- Every firm found is modelled with `realtime_mll=False` (as Lucid) and priced.

## (D) Funded Futures Network and the never-priced firms
FFN Standard MAX (EOD evaluation; funded "EOD + Static +$100"; 40% consistency; payout caps $1,000 (payouts 1–3), then $1,250; 80/20;
$500 minimum) at:
- the list price ($178 + $120 activation unless waived);
- this week's promo ($53.40 with the activation waived).

These parameters are from the rendered rules articles. Malaysia eligibility is checked on FFN's country-restriction article. BluSky, IQ
Capital and Finotive are priced if their renders give readable rules; otherwise they are recorded as unreadable.

## (E) Break-even promo prices
For each near miss, the highest one-time price at which it meets the registered bar (bisection on `one_time_price` = `reset`, $1
steps), or "no price works". Near misses:
- DayTraders S2F 50K;
- LucidDirect 50K;
- TTP Instant 50K;
- DayTraders Trail 50K;
- Tradeify Select Flex 50K;
- LucidFlex 25K;
- the $3K Challenge (here the fee scales the payout race).

**Outputs.**
- Script: `scripts/prop_search3_20261126.py`, output `docs/jx_runs/prop_search3_20261126.txt`.
- Script: `scripts/marketmix_20261120.py --compliant --corrected`, output `docs/jx_runs/marketmix_corrected_20261126.txt`.
- Both re-run once; output must be identical.
- Recorded in this file, `docs/NOTES_JX.md` and `docs/FIGURES_LEDGER.md`.

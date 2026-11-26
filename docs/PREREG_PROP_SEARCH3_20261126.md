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

## Addendum E2 (registered 2026-11-26, after part 1 printed, before this runs)
**Engine note.** Another session pushed audit addendum 3 (`backtest/engine.py`): the open loss on the exit bar now counts only up to the
stop or target fill. Every corrected-model figure rose. Topstep 50K Standard went from $35,124 to $38,034, so the bar is now real
≥ $19,017 and dip ≥ −$5,794. This search ran entirely on the new engine. Prop search 2's figures predate it and are slightly too strict.

**E2.** The same break-even method (highest one-time price meeting the registered bar), applied to the leads part 1 found:
- FFN Standard MAX 50K / 100K / 150K: risk $900 at 50K, 0.45 × MLL for the larger sizes; activation $0 (promo) and $120 (list);
  reset $100;
- DayTraders 100K / 150K Static, whose prices are unknown: risk $900 and 0.45 × MLL.

Script: `scripts/prop_search3_e2_20261126.py`.

## Results (2026-11-26; corrected engine incl. audit addendum 3; all outputs re-run identical)
Bar: real ≥ $19,017, coin flip ≥ $5,000, dip ≥ −$5,794 (Topstep 50K Standard, bot, real-time: $38,034, dip −$3,862).

### (A) Market mix (`docs/jx_runs/marketmix_corrected_20261126.txt`)
The regenerated ES/YM trades reproduce the earlier figures exactly on the closed-P&L model (NQ $44,359, ES $20,338, YM $11,744).

**Single accounts:**

| Product | NQ | ES | YM |
|---|---|---|---|
| Topstep 50K Consistency | $39,949 / flip $7,699 — qualifies | $6,023 — fails | $3,997 — fails |
| **LucidFlex 50K DLL ON (EOD)** | $40,545 / $21,522 — qualifies | **$26,480 / flip $14,926 (94%) / dip −$2,230 — QUALIFIES** | $12,359 — fails |
| LucidDaily $85.40 | $35,798 / $8,115 — qualifies | $9,413 — fails | $7,699 — fails |

**Portfolios (anti-hedge filter; MFFU dropped):**

| Comparison | Net | Cash on hand | Net per $ of cash | Verdict |
|---|---|---|---|---|
| 5 Topstep: 3 NQ / 1 ES / 1 YM vs all NQ | −30% | −36% | +8% | not worth it |
| **5 LucidFlex: 3 NQ / 1 ES / 1 YM vs all NQ** | **$163K vs $206K (−21%)** | **$10.0K vs $19.5K (−49%)** | **+55%** | **WORTH DOING** |
| 5 Topstep + 5 Lucid, mixed vs all NQ | −25.5% (limit −25%) | −47% | +40% | not worth it (misses the net rule by 0.5 pt) |

Monthly correlation: NQ–ES 0.12, NQ–YM 0.02, ES–YM −0.08. The live bot needs the cross-account anti-hedge check before a second
market is traded.

### (B) Bigger accounts with the same $900 risk (`docs/jx_runs/prop_search3_20261126.txt`)
**Same risk makes bigger accounts worse**, not better. The targets grow while the trades do not, so the coin flips turn negative:
- Topstep 100K Standard: $24.1K, flip −$5.7K;
- Topstep 150K Standard: $4.0K;
- LucidFlex 150K: $6.2K.

With risk scaled to 0.45 × MLL, the Topstep 100K/150K Static (Consistency) are strong, but fail the registered dip limit:
- 150K Static Consistency: $110.4K, flip $33.2K (92%), dip −$8.9K;
- 100K Static Consistency: $73.1K, flip $18.3K, dip −$6.5K.

They qualify only on the size-scaled reading (F), as do Topstep 100K/150K Static Standard and Topstep 150K Consistency.

**DayTraders 100K/150K Static qualify on the registered bar at a $55 placeholder price:** 100K $25.0K, flip $11.1K, dip −$2.9K;
150K $52.3K, flip $10.0K, dip −$1.9K. Their real prices are unknown; see E2.

### (C) Firms whose loss limit ignores open losses
Official-page quotes:
- **Lucid** (known);
- **Funded Futures Network Standard MAX**: EOD drawdown; "intraday losses beyond the DLL are managed by the soft breach lockout, not
  the drawdown"; open dips "NOT caught by the system";
- **City Traders Imperium**: "drawdown is calculated from account balance, not equity"; "No equity-based drawdown on any program".
  CTI is a CFD firm (MT5 / Match-Trader), so the bot would need porting. It is not priced here.

Count open losses (real-time): BluSky ("falls... at any point"), DayTraders (all plans), FundedNext, Blueberry. Tradeify, Purdia and
Goat only state that open *profits* do not raise the floor.

### (D) Funded Futures Network Standard MAX
Malaysia is not on FFN's restricted list. Bots are allowed at FFN's discretion. Modelled with `realtime_mll=False`.

| Price | 50K | 100K (risk $1,620) | 150K (risk $2,250) |
|---|---|---|---|
| List ($178/$348/$408 + $120 activation) | fails | fails | fails |
| **Promo $53.40/$104.40/$122.40, activation waived** | **$24.0K, flip $6.1K (81%), dip −$4.1K — QUALIFIES** | **$38.6K, flip $12.9K (91%), dip −$5.3K — QUALIFIES** | **$43.3K, flip $16.3K (92%), dip −$5.6K — QUALIFIES** |

### (E) Break-even prices (registered bar)

| Product | Break-even | Price now |
|---|---|---|
| DayTraders S2F 50K | $251 | $342 |
| LucidDirect 50K (EOD) | $303 | $360.50 |
| TTP Instant 50K | $321 | $499 |
| DayTraders 50K Trail | $55 | $70 |
| LucidFlex 25K | $80 | $100 |
| Topstep $3K Challenge | qualifies at $0 (break-even not computed) | $49 |

**E2** (`docs/jx_runs/prop_search3_e2_20261126.txt`, re-run identical):
- **FFN 50K: $96 with the activation waived**, $65 with the $120 activation (list $178);
- **FFN 100K (risk $1,620): $154 waived**, $88 with activation (list $348);
- **FFN 150K (risk $2,250): $149 waived**, $89 with activation (list $408);
- **DayTraders 100K Static: up to $90** (risk $900);
- **DayTraders 150K Static: up to $93** (risk $900).

### Verdict
New qualifiers, conditional:
1. **LucidFlex 50K on ES**: unconditional; Lucid's own rule, no price assumption. **The 5-LucidFlex 3/1/1 mix is worth doing.**
2. **Funded Futures Network** (a new firm), all sizes, **when bought at or below the break-even with the activation waived**. FFN's
   50%-off deals clear it at 50K ($89 ≤ $96).
3. **DayTraders 100K / 150K Static**, if the checkout price is ≤ $90 / $93 (unknown).

Options outside the registered bar: Topstep 100K/150K Static (size-scaled reading), City Traders Imperium (needs an MT5 bot port).

## Part 2, overnight (registered 2026-11-26, before running; Jx answers prices tomorrow)
Bar, models and engine as in part 1.
1. **Money needed to start** for each new qualifier and option, using the audit's method (`starts()` in
   `scripts/audit_pre_live_20261126.py`): a fresh chain started each month 2016-01..2025-10 (118 starts). Reported per product: the
   median, 1-in-10 and worst cash out of pocket; the first payout's amount and days; the 12-month net median and the share of starts
   still losing. Products:
   - LucidFlex 50K DLL ON on ES;
   - FFN Standard MAX 50K / 100K / 150K at the promo prices with the activation waived;
   - DayTraders 100K / 150K Static at their break-even prices ($90 / $93), as placeholders;
   - Topstep 150K Static Consistency (risk 0.45 × MLL, option);
   - LucidFlex 50K DLL ON on NQ (reference).
2. **ES and YM on the new firms:** the same single-account test as (A1) for FFN 50K (promo), DayTraders 100K / 150K Static
   ($90 / $93) and Topstep 150K Static Consistency.
3. **The $3K Challenge break-even price** (bisection, as in E).
4. **Prop search 2 re-run on the corrected engine** (audit addendum 3): `prop_search2_20261126`, `_c2_`, `_d_`. Outputs are saved as
   `*_engine3.txt` so the originals stay as the record of what was reported at the time.

Script: `scripts/prop_search3_p2_20261126.py` → `docs/jx_runs/prop_search3_p2_20261126.txt` (re-run once; it must be identical).

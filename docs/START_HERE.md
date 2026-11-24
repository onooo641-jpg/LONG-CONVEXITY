# START HERE — every result in one place (updated 2026-11-23)

Plain-language guide for readers. Sorted from "what makes money" to "what failed". Every number links to the file that explains it; every
file in `docs/jx_runs/` is the raw output of a script you can re-run. Rules for how tests are run: `CLAUDE.md`.

---

## 1. Bottom line
| What | Status | Money (backtest 2016–26, friend's NQ trades) |
|---|---|---|
| **Prop-firm recycling, Malaysia-eligible portfolio** (Topstep + TTP Prime + DayTraders EOD + LucidDaily, 1 account each) | **Works (backtest)** | $195,000 total = **$18,006/yr**, ~$1,500/month avg ($3,136 last 3 years); cash needed for worst dip ~$13,858 |
| Single prop firm (Topstep 50K) | Works (backtest) | $44,359 = $4,097/yr |
| Liquidation bot (workstream B) | Not built; shadow test running | est. $0–$100/month now, $100–$600 averaged over crash cycles |
| Any non-prop strategy usable at Jx's size | **None** (~105 tested) | — |
| Futures cross-sectional momentum #351 | **Passed the full test on paper, but needs ~$250K+** (whole-contract test fails at $15K and $50K) | ~15–20%/yr on capital, not prop-like |
| **CoW Protocol solving #364** (a business, not a deposit) | **Only non-prop role where newcomers measurably earned > $15K/yr**: genuine new solvers' first-year net median ~$48K–$96K (11 teams; upper bound, failed teams invisible). Needs a company + KYC and a solver that beats professional teams | **Gate tests #365: Stage 0 + Stage 1 passed** (no kill), with warnings: rewards shrinking ($6.4M/yr vs $10.6M in 2025), top solver takes 50%, top 3 take 78–99% of winning value. Only pass route left: a real solver tested on live auctions with no money (Stage 2) |
| #361 / #362 / #363 (2026-11-23) | CoW median solver KILL ($3,213/yr), Across relaying KILL ($8,790/yr for 6th), hedged JLP KILL (71% in 2024 → 8% in 2026) | — |

**If prop income stops (fallback plan, 2026-11-23).**
- *What would stop it:* firm rule changes or closures, not the friend's strategy losing its edge (every approved firm's coin-flip median is
  positive, $12K–$24K, so the income comes from the rules). An industry-wide change (all firms ban bots, or a regulator steps in) cannot be
  diversified inside prop.
- *Early warning already running:* the daily radar diffs ~120 prop-firm rule/pricing pages (`docs/radar/watchlist.csv`, output
  `data/radar/changes.parquet`); any new rule set can be re-modelled the same day with `backtest/recycle.py`; the live gates in
  `docs/PREREG_LIVE_20261120.md` stop adding accounts if live results fall below the model's 5th percentile.
- *Loss if it stops:* the income, not savings: only fees already paid are at risk (worst dip ~$13,858 for the 4-firm portfolio).
- *The real fallback is the capital prop builds:* save a fixed share of every payout. At ~$100K the money itself can earn prop-sized
  dollars at normal returns: #351b futures momentum backtests at 17.06%/yr at $100K (marginal pass, ledger FT2) ≈ $17K/yr; an index fund
  ~$7–10K/yr. Arithmetic: saving all of $18K/yr reaches $100K in ~5–6 years; 5 accounts per firm (backtest $90K/yr, worst dip −$69K)
  in ~1–2 years.

---

## 2. Prop firms
Benchmark Topstep 50K: $44,359 real net, coin-flip median $18,046, worst dip −$3,520. "Qualifies" = real ≥ 50% of Topstep, coin flip ≥ $5,000,
worst dip no worse than 1.5× Topstep's (manual-entry products judged with a 3-minute entry delay).

### 2a. APPROVED — Malaysia-eligible, rules verified on the firms' own pages, qualifies
| Rank | Product (price) | Entry | Real net 2016–26 | Per year | Coin flip | Worst dip | Source |
|---|---|---|---|---|---|---|---|
| 1 | LucidDaily 50K EOD ($85.40 promo) | bot | $57,486 | $5,308 | $24,093 | −$3,758 | `docs/PROP_VERIFY_20261122.md` §6 |
| 2 | TTP Futures Prime 50K ($99, reset $79) | bot | $49,057 | $4,530 | $16,960 | −$3,884 | §2, §4 |
| 3 | DayTraders EOD 50K ($105 + $5) | bot | $47,894 | $4,422 | $12,461 | −$3,265 | §7 |
| 4 | Topstep 50K, **Consistency payout path** ($49/mo) | bot | $46,492 | $4,293 | $18,005 | −$3,520 | §4 |
| 5 | Topstep 50K, Standard path | bot | $44,359 | $4,096 | $18,046 | −$3,520 | benchmark |
| 6 | LucidFlex 50K DLL ON ($80.50) | bot | $40,545 | $3,744 | $21,522 | −$4,108 | §7 |
| 7 | TradeDay 50K ($85 code) | bot (no API: platform rewrite) | $35,678 | $3,294 | $14,035 | −$4,835 | `docs/RADAR_RESULTS_SUMMARY.md` |
**All of them together:** `docs/PREREG_PORTFOLIO_MY_20261123.md` ($195K with 1 account each; $975K with 5 each, worst dip −$69K).

### 2b. DISAPPROVED — firm does not accept Malaysian residents (their own restricted-country lists)
| Firm | Best product and figure (would have qualified) | Source |
|---|---|---|
| FuturesElite | Prime 50K $52,176, Nitro $48,463, Elite $33,645 (manual) | `docs/PROP_VERIFY_20261122.md` §1 |
| Blue Guardian Futures | Elite 50K $43,877, Reserve $41,251 (manual) | §1 |
| Alpha Futures | Standard 50K $40,155 (manual; dip misses by $132) | §1 |
| MyFundedFutures | Rapid EOD, Pro, Builder (was in the old 3-firm plan) | §1 |
| Goat Funded Futures | GOAT Daily | §1 |
| Tradeify | Select Flex (restricted per Jx) | §7 |
| FundedNext Futures | Rapid / Flex / Direct | §8 |
| The Futures Desk | unverified → kept out | §7 |

### 2c. DISAPPROVED — eligible but does not qualify
| Product | Real net | Why it fails | Source |
|---|---|---|---|
| LucidDaily 50K EOD at $122 list | $51,557 | worst dip −$5,368 (by $88) | §6 |
| LucidFlex 50K DLL OFF | $34,770 | worst dip −$5,648 | §7 |
| DayTraders S2F 50K ($342 promo / $570) | $44,692 / $27,820 | dip −$7,524 / coin flip negative | §6 |
| TTP Futures Instant 50K ($499) | $43,076 | dip −$11,214 | §4 |
| FTMO Futures Growth 50K | $34,236 | coin flip $1,906 | `docs/RADAR_RESULTS_SUMMARY.md` |
| FTMO 2-Step CFD 50K / 100K | $49–86K | coin flip ≈ 0, dips −$45K to −$70K | `docs/PREREG_BATCH10_20261122.md` (#296) |
| Blueberry Ascent 50K ($98/mo) | $30,747 | coin flip $3,395 (30-day expiry rule decides) | §7 |
| Traders Launch 100K / 200K; Bulenox | $722 / $4,371; −$4,139 | lose or near zero | summary |
| Take Profit Trader | not priced | bots banned (manual only); rules being read | pending |

### 2d. Manual entry (you place trades from alerts; 3-minute delay; compare with Topstep at 3 minutes $37,348)
| Product | Real net | Coin flip | Worst dip | Qualifies | Note |
|---|---|---|---|---|---|
| LucidDaily 50K EOD $85.40 | $48,761 | $18,582 | −$2,818 | yes | bots also allowed |
| DayTraders EOD 50K $105 | $41,112 | $9,250 | −$3,083 | yes | bots also allowed |
| LucidFlex 50K DLL ON $80.50 | $40,494 | $16,365 | −$3,228 | yes | bots also allowed |
| Topstep 50K Consistency | $39,978 | $13,795 | −$3,094 | yes | bots also allowed |
| TTP Futures Prime 50K | $35,554 | $13,397 | −$4,070 | yes | bots also allowed |
| **Top One Elite ACCESS 50K ($39 promo)** | $21,566 | $5,436 | −$3,427 | yes (barely) | **manual only** (bots banned); fails at $189 list ($15,459) |
Not priced (help centres did not render): Take Profit Trader, Purdia, Phidias, Hola Prime, The5ers Futures; YLOS (rules incomplete).
AquaFunded: Malaysia allowed on Instant Funding only (max $50K). Source: `docs/PROP_VERIFY_20261122.md` §8.

---

## 3. Liquidation strategy (workstream B, separate session)
| Question | Answer | Source |
|---|---|---|
| Is there money? | Yes: $45M (Aave, 5 chains) + $54M (Morpho Base) of bonuses in 24 months | `docs/NOTES_JX.md` "Liquidation test #100" |
| Can a new free bot get it? | Mostly no: 64–98% of liquidations happen in the same block as the price update; professionals hold 75–77% | "Liquidation levers: final table" |
| Expected profit for a new small bot | $0–$100/month now; $100–$600 averaged over a cycle with crash months (estimate) | same |
| Decision | Don't build yet; free shadow test (kill check 2026-11-28, verdict 2026-12-19) | `docs/PREREG_LIQ_SHADOW_20261121.md` |

---

## 4. Non-prop strategies (own capital) — sorted by verdict
Bar: ≥ 8%/yr on capital in both halves (risk-premium families: ≥ 10% and drawdown no worse than the S&P). Full list with numbers:
`docs/CANDIDATES.md`; batch files `docs/PREREG_*`.

### 4a. Passed a full test
| # | Idea | Result | Can Jx use it? |
|---|---|---|---|
| 351 | Futures cross-sectional momentum (long the 12-month winners, short the losers, across 21–26 CME futures; monthly) | 20.72%/yr 2016–26 walk-forward, halves 26.94% / 14.97%, worst drawdown −22.3% (S&P −23.9%) | **No, not at $10–50K.** Whole-contract version fails at $15K (second half 3.08%) and $50K (7.89%); needs full-size rates/FX contracts, so ~$250K+, earning ~15–20%/yr. `PREREG_FUTURES_TREND_CARRY_20261123.md` addendum 3 |

(#303 S&P 500 additions passed on paper but was withdrawn: it bought before S&P's announcements; tradeable version +0.17%/event.)

### 4b. In progress / open
| # | Idea | Why it has potential | Status |
|---|---|---|---|
| 364 | CoW Protocol solving: new solvers' first-year income | registered rule met: median entrant $129K (2024) / $25.5K (2025) after fee; after removing likely address migrations $96K (7 teams) / $48K (4 teams) | next: no-money shadow-competition solver; needs a builder, later a company for KYC (`docs/PREREG_COW_ENTRANTS_20261123.md`) |
| 324 | Newer perp / options vaults | 95% on advertised APY | needs real share prices |
| 339 | Tokenised gold premium | redemption floor | not credible as measured (futures vs spot) |

### 4c. Failed — closest misses first
| # | Idea | Best result | Why it failed | File |
|---|---|---|---|---|
| 363 | Hedged Jupiter JLP (house side of perp traders' losses) | 70.8% in 2024, 23.0% 2025, 8.0% 2026 | Stage 1 9.7% < 20%: yield competed away as capital poured in | `PREREG_JLP_20261123` |
| 361 | CoW solving, median solver | $3,213/yr (top 10 earn $176K+) | winner-take-most; see #364 | `PREREG_SOLVER_RELAY_20261123` |
| 362 | Across relaying | 6th relayer $8,790/yr | top 5 take 95% of a $0.8M/yr market | `PREREG_SOLVER_RELAY_20261123` |
| 350 / 352–354 | Futures trend+carry, value, skew, multi-factor | 11.7% / 0.5% / 8.8% / 1.1% | a half below 10% or drawdown worse than S&P | `PREREG_FUTURES_TREND_CARRY` |
| 208 / 280 | Cross-venue funding gaps | 20.3% / 11.9% on paper | execution: $10K orders cost 23–55 bps per side | `PREREG_BATCH7`, `PREREG_BATCH8` |
| 276 | Hedged HYPE staking | 23.4% / 9.3% | short gets liquidated (12×) | `PREREG_BATCH7` |
| 293 / 295 | FX carry; levered stock–bond | 13.6%; 13.5%/yr | one half below 10%, drawdown −43% | `PREREG_BATCH9` |
| 225 | Gains vaults | 9.6% / 14.1% on APY | real token price fell | `PREREG_BATCH7` |
| 288 | Hyperliquid user vaults | 27% pilot | −5.6% / −4.9% with closed vaults | `PREREG_BATCH8` |
| 303 | S&P 500 additions | +3.9%/event | look-ahead | `PREREG_BATCH10` addendum 2 |
| 291 | Friend's trades as options | — | options fairly priced (coin flip −$75K) | `PREREG_OPTIONWRAP` |
| … | ~90 more (stable yields, loops, LPs, VIX, memecoin-adjacent, listings, unlocks …) | | each row in `docs/CANDIDATES.md` (#200–#346) | |

### 4d. Not testable (no free data) or excluded by the repo's rules
Memecoin history beyond 2 days (pump.fun), index-token NAV, spin-off lists, BNB / Solana liquidations, prediction markets (Malaysia), launchpools
(Malaysia), creator / marketing ventures (rule). See `docs/PREREG_SWEEP4_20261122.md`, `docs/IDEAS_SWEEP2_20261122.md`.

---

## 5. Where everything lives
| You want | Open |
|---|---|
| Prop firm rules checked against official pages | `docs/PROP_VERIFY_20261122.md` |
| All prop products compared (62 rows) | `docs/PROP_COMPARISON_20261122.md` |
| Frozen prop inputs (edit prices here) | `docs/radar/prop_assumptions_20261122.csv` |
| Every non-prop idea and verdict | `docs/CANDIDATES.md`, `docs/RADAR_RESULTS_SUMMARY.md`, `docs/NOTES_NONPROP.md` |
| Every number and the command that produced it | `docs/FIGURES_LEDGER.md` |
| Map by workstream | `docs/INDEX.md` |

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
| Any non-prop strategy | **None passed a full test yet** (~100 tested) | — |
| Non-prop tests in progress | #350 futures trend/carry + #351–#354 (same data) | results pending |

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

### 2d. Not priced yet (manual-entry firms that accept Malaysia)
Take Profit Trader, Top One, Purdia, Phidias, AquaFunded, Hola Prime, YLOS, The5ers Futures — help-centre crawl running; prices at 3-minute delay
to follow. FundedNext Futures: rules changed, re-price pending.

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
None. (#303 S&P 500 additions passed on paper but was withdrawn: it bought before S&P's announcements; tradeable version +0.17%/event.)

### 4b. In progress / open
| # | Idea | Why it has potential | Status |
|---|---|---|---|
| 350 | Cross-asset futures trend + carry (26 CME futures) | decades of published evidence; diversifies across rates, FX, metals, energy, indices | Databento data downloading |
| 351–354 | Cross-sectional momentum, value (5-year reversal), skew, combined multi-factor (same 26 futures) | published "factor" premia on futures; same data, no extra cost | registered; run with #350 |
| 324 | Newer perp / options vaults | 95% on advertised APY | needs real share prices |
| 339 | Tokenised gold premium | redemption floor | not credible as measured (futures vs spot) |

### 4c. Failed — closest misses first
| # | Idea | Best result | Why it failed | File |
|---|---|---|---|---|
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

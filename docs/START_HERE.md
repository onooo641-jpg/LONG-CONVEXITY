# START HERE — every result in one place (updated 2026-11-25)

Plain-language guide. Sorted from "what makes money" to "what failed". Every number points to the file that explains it; every file in
`docs/jx_runs/` is raw output of a script you can re-run; every standing figure has a row in `docs/FIGURES_LEDGER.md`. Test rules:
`CLAUDE.md` and section 10.

**Contents:** 1 Bottom line · 2 What only Jx can do · **2b Next step and money needed** · 3 Calendar · 4 Prop firms · 5 Liquidation bot · 6 Own-capital strategies ·
7 Approval-gated roles (CoW, UniswapX) · 8 Uncharted search (U1–U28) · 9 Radar and monitoring · 10 How tests are run · 11 Where everything lives

---

## 1. Bottom line
| What | Status | Money |
|---|---|---|
| **Prop-firm recycling, Malaysia-eligible portfolio** (Topstep + TTP Prime + DayTraders EOD + LucidDaily, 1 account each) | **Works (backtest 2016–26)** | $195,000 total = **$18,006/yr**; cash for worst dip ~$13,858 |
| Single prop firm (Topstep 50K) | Works (backtest) | $44,359 = $4,097/yr |
| **#389 Resting bids under liquidation wicks** (Hyperliquid perps, own capital) | **Best non-prop result so far.** Stage 1 + out-of-sample on Binance (S2a) + risk (S2b) passed; forward paper (S2c) 2026-12-01 → 2027-01-26 and a margin check (S2d) still open | backtest ~$18.8K/yr on $15K (Hyperliquid 2023–26), or ~$6.4K/yr if resting orders lock margin; **loses in crash regimes** (Binance path −$22K, 2025-09 → 2026-07) |
| **#397 Cascade-day reversal** (buy the perps that wicked, hold 3 days) | Stage 1 + Binance Stage 2 passed | ~7–8 events/yr, +3.3–3.7% per event ≈ $3.7K/yr unlevered on $15K; overlaps #389's crash days |
| #385 Short Hyperliquid pre-launch perps | Survives Stage 1; small sizes only | ~$4K/yr; forward watch running |
| **UniswapX quoting #371** (Arbitrum RFQ: quoters approved by Uniswap Labs) | Passed the four volume/margin checks; live paper run (Stage 5b) shows the money is reachable **only as an approved quoter** | newly approved quoters kept ≈ $52K–$85K/yr gross; verdict 2026-11-26 |
| **CoW Protocol solving #364–#368** (a business) | New small teams measurably earn ($23K–$386K/yr); onboarding **paused** by CoW | follow-up 2026-12-15 |
| Futures cross-sectional momentum #351 | Passed on paper, needs ~$250K+ | ~15–20%/yr on capital |
| Liquidation bot (workstream B) | Shadow test running | est. $0–$100/month now |
| Everything else (~140 non-prop ideas) | Failed, not testable, or excluded | sections 6–8 |

**Next step and how much money:** section 2b — one live prop account, ~$700–850 to start, up to ~$2.7K set aside (9 in 10 starts), ~$3.8K worst case.

**If prop income stops (fallback plan, 2026-11-23).**
- *What would stop it:* firm rule changes or closures, not the friend's strategy losing its edge (every approved firm's coin-flip median is
  positive, $12K–$24K, so the income comes from the rules). An industry-wide change cannot be diversified inside prop.
- *Early warning already running:* the daily radar diffs ~120 prop-firm rule/pricing pages (section 9); any new rule set can be re-modelled
  the same day with `backtest/recycle.py`; live gates in `docs/PREREG_LIVE_20261120.md` stop adding accounts below the model's 5th percentile.
- *Loss if it stops:* the income, not savings (only fees already paid are at risk; worst dip ~$13,858).
- *The real fallback is the capital prop builds:* at ~$100K, #351b futures momentum backtests 17.06%/yr ≈ $17K/yr; an index fund ~$7–10K/yr.
  Non-prop add-ons being validated now: #389, #397 (section 6b).

---

## 2. What only Jx can do (everything else runs without him)
| Item | Why it needs Jx | Effort |
|---|---|---|
| **#389 margin check** | Does a resting limit order on Hyperliquid reduce "available margin"? Decides ~$18.8K vs ~$6.4K/yr | 1 minute, ~$20 in his Hyperliquid account; place a small bid far below the price, read "available", cancel |
| UniswapX quoter application (#371) | Uniswap Labs approves quoters (intake form); a company/KYC may be asked | decide after the 2026-11-26 verdict |
| CoW solver onboarding (#364) | CoW paused onboarding; Jx is the contact | reply when they reopen (reminder 2026-12-15) |
| Prop accounts, payments, live trades | money/KYC | per `docs/GO_LIVE*.md` |

## 2b. Next step and money needed (2026-11-25)
Plain answer first: **the next step is one prop account run live by the friend, and it needs about $700–850 to start, with up to ~$2.7K
set aside (covers 9 in 10 historical starts) and ~$3.8K for the worst start ever seen.** That money pays evaluation fees and resets; it is not
trading capital (the firm's money absorbs trading losses). Labels: **M** = measured in the backtest (2016-01..2026-10, friend's NQ trades at
$900 risk), **V** = verified on the firm's own page, **J** = supplied by Jx (not verified by the repo), **E** = estimate.

### Status on 2026-11-25
- **Live Topstep data: none in the repo yet** (`data/live/` does not exist). The friend's export (`scripts/export_live_trades.py`, then push
  `data/live/`) is what every later step waits on. He should `git pull` first so he has the tick-grid fix in `bridge/topstepx.py`.
- The bot (`bridge/`) connects **only to TopstepX** today. LucidDaily, TTP Prime and DayTraders need a different order route (below).

### Order of steps (each step starts only after the gate before it)
| Step | What | Gate to move on | Who | Money |
|---|---|---|---|---|
| 1 | **One live prop account.** Topstep 50K with the bot (works today), or LucidDaily 50K EOD (manual now, bot after step 3) | — | friend (account, PC); Jx pays if agreed | start ~$700–850; reserve up to ~$2.7K (M) |
| 2 | **Live check after 40 trades** (≈ 2.5 months at 16.8 trades/month, M) using `scripts/live_compare.py` | `docs/PREREG_LIVE_20261120.md`: order parity ≥ 95%; fill rate of limit orders 80% ± 10 points; mean stop slippage ≤ 2 ticks; cumulative net R vs the bands (5% / 50% / 95%: −10.8 / +0.2 / +11.9 full history; −8.7 / +3.4 / +14.6 since 2024). Above the recent median → add accounts; inside the bands → hold; below the 5th percentile of both → stop adding | Claude reads the pushed data | $0 |
| 3 | **Build the second order route** (no cost to build): CrossTrade adapter for Tradovate-based firms (Lucid). TTP Prime and DayTraders: platform not yet confirmed in the repo (**unverified**) | adapter passes the same round-trip test as TopstepX (`--roundtrip`) on a practice account | Claude Code; Jx/friend subscribes to CrossTrade only when ready | $49/month once subscribed |
| 4 | **Add accounts**: Topstep + LucidDaily, then the 4-firm plan (section 4a) | step 2 passed; one firm per month so each new route is checked live | friend | reserve ~$7–7.5K for 2 firms (E), ~$12–14K for 4 (M) |
| 5 | **#389 wick bids live** (own capital, section 6b) | S2c forward paper ends 2027-01-26 and holds; S2d margin check done; guard G2 (daily fill cap $5,000) and a pre-registered loss limit | Jx | $15,000 pot as modelled; lost money in crash periods |
| — | Liquidation bot (section 5) | not building | — | $0 |

### Money needed to start one account (M; ledger LS1, `docs/PREREG_LUCID_START_20261125.md`)
A fresh chain was started on the first of every month 2016-01..2025-10 (118 starts). "Deepest loss" = most money out of pocket (fees minus
payouts) before payouts paid it back. Every start on all three products eventually went positive.
| | **LucidDaily 50K EOD, $85.40 promo** | LucidDaily 50K EOD, $122 list | Topstep 50K (Consistency path) |
|---|---|---|---|
| Typical start (median) | **−$683** | −$1,054 | −$735 |
| 1 in 4 starts worse than | −$1,687 | −$2,410 | −$1,248 |
| 1 in 10 starts worse than | −$2,673 | −$3,819 | −$2,583 |
| Worst start | −$3,758 | −$5,368 | −$3,520 |
| Days to first payout: median / 90th percentile | 158 / 826 | 158 / 826 | 126 / 827 |
| Net after 12 months: median (share of starts losing) | **$3,971** (30%) | $3,239 (32%) | $1,704 (30%) |
| Starts from 2023 on: median deepest / days to payout | −$342 / 78 | −$488 / 78 | −$418 / 63 |
Not in these figures: CrossTrade $49/month (needed for a bot on Lucid; ≈ $250 more in a typical start, E) and TopstepX API $14.50/month.
The older Topstep Standard figures (NOTES_JX, `scripts/jx_capital.py`: median −$863, 1 in 10 −$2,613, worst −$3,568, 144 days) used an
earlier trade set and the Standard path; LS1 supersedes them for comparisons.

### Running costs per account (what you pay while it runs)
| Product | Evaluation | Reset | Monthly | Other | Source |
|---|---|---|---|---|---|
| Topstep 50K | $49/month | $49 | — | activation $149 per funded account; TopstepX API $14.50/month (code `topstep`), shared by all Topstep accounts | V (`PROP_VERIFY_20261122.md` §4, `GO_LIVE.md`) |
| LucidDaily 50K EOD | $85.40 promo / $122 list, one-time | assumed = purchase price | none | CrossTrade Pro $49/month if bot-run (unlimited accounts) | price J, rules V, reset assumed |
| TTP Futures Prime 50K | $99 | $79 | — | order route unverified | V |
| DayTraders EOD 50K | $105 | $105 (assumed) | — | $5 activation; bots, copiers and a VPS allowed | V |

### Money by stage (cash to have ready, not all spent)
| Stage | When (earliest) | Cash to have ready | Monthly |
|---|---|---|---|
| 1 account (Topstep or LucidDaily) | now | start ~$700–850; top up to ~$2.7K; worst ~$3.5–3.8K (M) | $63.50 Topstep / $0–49 Lucid |
| Topstep + LucidDaily | after the 40-trade check (~Feb 2027) | ~$7–7.5K (E: same trades, so the two dips roughly add) | ~$113 + resets |
| 4-firm plan (section 4a) | after both routes run live | ~$12.2–13.9K (M, `PREREG_PORTFOLIO_MY_20261123.md`) | evals + resets + $49 CrossTrade |
| + #389 | after 2027-01-26 | + $15K own capital (M model pot; can lose a meaningful share in a crash period) | trading fees |
| Everything | mid-2027 at the earliest | ~$27–29K (E) | — |

### Why LucidDaily is #1 — and its catches
- **Best product in the backtest:** $57,486 real net 2016–26 ($5,308/yr), coin flip $24,093, worst dip −$3,758, ROI on fees 416% (section 4a,
  ledger PR1). Topstep: $44–46K.
- **Price.** $85.40 is the promo you saw at checkout (J). The repo cannot read Lucid's checkout (it shows a bot-check page to automated
  browsers; not circumvented), so the price and the promo's end date are unverified. At the $122 list price it falls to $51,557 and the worst
  dip (−$5,368) misses the repo's rule by $88. Buying the evaluation while the promo runs locks the price for that attempt only; resets are
  assumed to cost the same as the purchase (not supplied).
- **Order route.** Lucid runs on Tradovate, whose API is closed to prop and evaluation accounts. Route: CrossTrade Pro ($49/month, partner
  OAuth; NOTES_JX "How the bot can reach Lucid and MFFU"). CrossTrade is not in the backtest: about $6.4K over 10.8 years, so roughly
  **$51K** after it (E) — still above Topstep.
- **Manual entry works too:** placing each trade from an alert within 3 minutes backtests at **$48,761** (section 4d), above bot-run Topstep;
  the cost is being awake for the US session (Malaysian night).
- The LucidDaily **Intraday** variant ($65.80 promo) shows $60,661, but the model cannot tell intraday from end-of-day drawdown, so that
  figure is optimistic; do not rely on it.

### Which to start with
- **If the friend has not started live yet:** start with LucidDaily (manual now, or bot once the CrossTrade adapter passes), or Topstep +
  LucidDaily together (~$7–7.5K reserve, E). Lucid ranks higher and the promo is time-limited.
- **If Topstep is already live:** keep it running; it is the live test of the strategy. The pre-registered plan adds accounts only after 40
  live trades; adding Lucid earlier risks only evaluation fees (~$85 each), not the strategy. Build the CrossTrade adapter now either way.
- Same signals run on every account (copying between your own accounts is allowed); the anti-hedge filter and hedge registry
  (`bridge/hedge.py`) block opposite positions across accounts, which firms prohibit.

## 3. Calendar of scheduled verdicts
| Date | What | Where |
|---|---|---|
| 2026-11-26 | #371 UniswapX Stage 5b verdict (36 h paper run on GitHub) | `docs/PREREG_UNISWAPX_20261124.md` |
| 2026-11-28 / 2026-12-19 | Liquidation shadow kill check / verdict (workstream B) | `docs/PREREG_LIQ_SHADOW_20261121.md` |
| 2026-12-01 → 2027-01-26 | #389 S2c forward paper log (radar N10) | `data/radar/wick_paper.parquet` |
| 2026-12-15 | CoW follow-up reminder | `docs/NOTES_NONPROP.md` |
| 2027-01-08 | #228 SKY re-test | `docs/CANDIDATES.md` |
| weekly | radar review (dismiss or test leads) | `docs/RADAR_REVIEW_*.md` |

---

## 4. Prop firms
Benchmark Topstep 50K: $44,359 real net, coin-flip median $18,046, worst dip −$3,520. "Qualifies" = real ≥ 50% of Topstep, coin flip ≥ $5,000,
worst dip no worse than 1.5× Topstep's (manual-entry products judged with a 3-minute entry delay).

### 4a. APPROVED — Malaysia-eligible, rules verified on the firms' own pages, qualifies
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

**ROI** (`uv run python -m scripts.prop_roi_20261125`, ledger PR1). *ROI on fees* = net ÷ all fees paid 2016–26. *Return on cash* = net per
year ÷ worst dip (the cash you must be able to lose).
| Product | Fees paid 2016–26 | ROI on fees | Return on cash / yr |
|---|---|---|---|
| LucidDaily 50K EOD ($85.40) | $13,835 | 416% | 141% |
| TTP Futures Prime 50K | $14,865 | 330% | 117% |
| DayTraders EOD 50K | $12,530 | 382% | 135% |
| Topstep 50K Consistency | $17,081 | 272% | 122% |
| Topstep 50K Standard | $17,081 | 260% | 116% |
| LucidFlex 50K DLL ON | $15,178 | 267% | 91% |
| TradeDay 50K ($85) | $13,000 | 274% | 68% |
| **4-firm portfolio** (LucidDaily promo + TTP + DayTraders + Topstep Consistency) | $58,311 | **345%** | **151%** ($18,553/yr on $12,248) |

### 4b. DISAPPROVED — firm does not accept Malaysian residents (their own restricted-country lists)
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

### 4c. DISAPPROVED — eligible but does not qualify
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

### 4d. Manual entry (you place trades from alerts; 3-minute delay; compare with Topstep at 3 minutes $37,348)
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

## 5. Liquidation strategy (workstream B, separate session)
| Question | Answer | Source |
|---|---|---|
| Is there money? | Yes: $45M (Aave, 5 chains) + $54M (Morpho Base) of bonuses in 24 months | `docs/NOTES_JX.md` "Liquidation test #100" |
| Can a new free bot get it? | Mostly no: 64–98% of liquidations happen in the same block as the price update; professionals hold 75–77% | "Liquidation levers: final table" |
| Expected profit for a new small bot | $0–$100/month now; $100–$600 averaged over a cycle with crash months (estimate) | same |
| Decision | Don't build yet; free shadow test (kill check 2026-11-28, verdict 2026-12-19) | `docs/PREREG_LIQ_SHADOW_20261121.md` |
| How lumpy is it? | Very: the 5 biggest of 24 months paid 70% of Aave bonuses (Morpho 89%); a typical non-top-3 bot beats $1,000 in only 4% of months and makes $200+ in 29% (M). Big crash months came about every 6 months in the data (Feb 2025, Oct–Nov 2025, Feb 2026) | `docs/NOTES_JX.md` "Liquidations: crash months" |
| Can crash months be predicted? | No. They can be detected as they start (fast price drops, health factors falling toward 1.0); the watcher logs debt near the liquidation line hourly (`data/shadow/<chain>/near_line.jsonl`) and opens a GitHub issue if a chain goes unwatched > 60 min | `docs/PREREG_LIQ_SHADOW_20261121.md` addendum 4 |
| What about crashes after the test? | Log-only extension: the watcher keeps running after the verdict until the first 30-day window with > $1M of bonus (or 2027-06-30) and reports it separately (CRASH-WORTHWHILE needs fire-first ≥ 10% and simulated net ≥ $2,000) | same |
| Risk to the verdict | Watcher uptime ~57% of wall time per chain so far; below 75% the registered rules make the verdict INCONCLUSIVE and extend 2 weeks | `docs/NOTES_JX.md` (2026-11-24) |

---

---

## 6. Own-capital strategies (non-prop) — sorted by verdict
Bar for the older batches: ≥ 8%/yr on capital in both halves (risk-premium families ≥ 10% and drawdown no worse than the S&P). The
uncharted batch uses staged kill-only tests (section 10) with dollar bars on a $15K pot. Full list: `docs/CANDIDATES.md`.

### 6a. Passed a full test
| # | Idea | Result | Can Jx use it? |
|---|---|---|---|
| 351 | Futures cross-sectional momentum (21–26 CME futures, monthly) | 20.72%/yr 2016–26 walk-forward, halves 26.94% / 14.97%, worst drawdown −22.3% (S&P −23.9%) | **No, not at $10–50K** (whole-contract version fails at $15K and $50K); ~$250K+. `PREREG_FUTURES_TREND_CARRY_20261123.md` add. 3 |

(#303 S&P 500 additions passed on paper but was withdrawn: it bought before S&P's announcements; tradeable version +0.17%/event.)

### 6b. Passing so far — not yet usable (stages left)
| # | Idea | Results so far | What is left | File |
|---|---|---|---|---|
| **389** | Resting bids 15% under the previous close on every Hyperliquid perp, sold at the day's close (liquidity to forced liquidations) | Hyperliquid 2023–26: 4,350 fills, +2.61%/fill (t 15.5), $19.6K/yr ($18.8K with no look-ahead sizing), every year positive; **Binance 2020–26 out-of-sample: +1.48%/fill, t 15.0, $15.8K/yr, 6/6 years positive**; worst HL drawdown −$2,480 | S2c forward paper to 2027-01-26; S2d margin check (Jx). **Warning:** loses in crash regimes (Binance −$22K over 2025-09 → 2026-07; 2022H2 and 2025H2 negative on both venues) — any live version needs a pre-registered loss limit | `PREREG_UNCHARTED_20261125.md` |
| **397** | Cascade-day reversal: on days when ≥ 25% of perps wick ≥ 15%, buy those perps at the close, hold 3 days | Hyperliquid: 26 events, +3.27%, 62% positive (t 1.95); **Binance 2020–26: 72 events, +3.73%, t 2.69, 62% positive** | forward check (rare: ~7–8 a year); small dollars | `PREREG_UNCHARTED_WAVE3_20261125.md` |
| 385 | Short Hyperliquid pre-launch perps from listing to token launch + 7 days | 27 events, +18.3% mean, +24% median; 2024–25 ≈ +30% | 11 of 27 would be liquidated at 1× isolated margin → small sizes only (~$4K/yr); forward watch (radar N11) | `PREREG_UNCHARTED_20261125.md` |
| 383 | Launch-phase perp-DEX house vaults (first 12 months) | median first-year hedged 32% (JLP 83%, HLP 87%, ZLP 32%); year 1 beat year 2 in 4/4 | below the 40% bar; only 3 true perp vaults with prices; parked | same |
| 384 | Withdrawal-queue discounts (HYPE LSTs, LRTs, sUSDe) | KILL on the registered data (6 months only) | inconclusive: needs on-chain swap history (Stage 1b) | same |
| 324 / 339 | Newer perp/options vaults; tokenised gold premium | 95% advertised APY; redemption floor | need real share prices / not credible as measured | older batches |

### 6c. Failed — closest misses first
| # | Idea | Best result | Why it failed | File |
|---|---|---|---|---|
| 396 | Short when Binance launches a perp on a token already on Hyperliquid | 17 events, +8.7% mean | t 0.99 < 1; one −92% loss | `PREREG_UNCHARTED_WAVE3_20261125` |
| 391 | Hong Kong IPO one-lot applications | day-one +35.6% average | allocation odds priced: −US$277/yr (+$1,092 with zero fees) | `PREREG_UNCHARTED_20261125` |
| 387 | Uniswap token auctions (CCA) | 16 real of 1,152 | median 7-day −39% | same |
| 370 | Crypto perp trend / momentum (918 coins, 52 settings, walk-forward) | 30.8%/yr | −90.6% drawdown, losing first half; 2026 windfall only on Binance-only meme coins | `PREREG_CRYPTO_TREND_20261124` |
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

### 6d. Not testable (no free data) or excluded by the repo's rules
Memecoin history beyond 2 days (pump.fun), index-token NAV, spin-off lists, BNB / Solana liquidations, prediction markets (Malaysia),
launchpools (Malaysia), creator / marketing ventures (rule), #386 delisting shorts (2 events; Upbit blocks US servers), token-sale platforms
(no free per-sale data), incentivised testnets and pre-IPO perps (forward only). See `docs/PREREG_SWEEP4_20261122.md`,
`docs/IDEAS_SWEEP2_20261122.md`, `docs/IDEAS_UNCHARTED_20261125.md`.

---

## 7. Approval-gated roles (a business, not a deposit)
These pay a role (solver, quoter) out of protocol fees or spreads. Newcomers can earn, but only after the protocol approves them.

| # | Role | What was measured | Verdict / status | File |
|---|---|---|---|---|
| 371 | **UniswapX quoter (Arbitrum, RFQ since 2026-06)** | Stage 1: top-3 fillers 89% of fills (Aug–Oct 2026). Stage 2: newly approved quoters took 9.9% / 9.7% / 5.2% of monthly fills. Stage 3: $191.9M in 92 days = **$761M/yr**. Stage 4: 5,051 fills, volume-weighted gross spread 8.62 bps; newcomer A **$85,116/yr**, B **$51,884/yr** gross (gross ≠ net). Stage 5: open-competition plan dropped (orders go to an exclusive quoter). **Stage 5b (live paper, interim at 22 h):** a public KyberSwap route matched or beat the winning quoter on 61% of 80 orders (median gap 0.9 bps), but only 1 of 153 fills (0.7%) went to a non-exclusive filler | passes every volume/margin check; **reachable only as an approved quoter** (outsider route: KILL). Approval rate unpublished; aimed at experienced teams. Verdict 2026-11-26 | `PREREG_UNISWAPX_20261124.md`, `data/uniswapx_paper/` |
| 364 | CoW Protocol solver | genuine new solvers' first-year net median ~$48K–$96K (11 teams; upper bound) | registered rule met | `PREREG_COW_ENTRANTS_20261123.md` |
| 365 | CoW gate tests | rewards $6.4M/yr (2026) vs $10.6M (2025); top solver 50%, top 3 78–99% | Stage 0 + 1 passed with warnings | `PREREG_COW_GATE_20261124.md` |
| 366 / 368 | CoW live shadow / staging | production auction feed HTTP 403; staging 2,072 auctions, 0 usable | not runnable without CoW | `PREREG_COW_SHADOW_*`, `PREREG_COW_BARN_*` |
| 367 | Who CoW's solvers are | 6 small teams made $23K–$386K/yr in 2026 (9% of rewards); big firms take most | small teams can earn | `PREREG_COW_WHO_20261124.md` |
| — | CoW onboarding | CoW (Telegram): onboarding paused for some weeks | reminder 2026-12-15 | `NOTES_NONPROP.md` |
| 361 / 362 | CoW median solver; Across relayer | $3,213/yr; 6th relayer $8,790/yr | KILL (winner-take-most) | `PREREG_SOLVER_RELAY_20261123.md` |
| 372–376, 377–381 | 1inch, deBridge, Drift, RFQ market makers, ZK provers, UMA, redemption bots | desk | dismissed or approval-gated | `docs/NICHE_SWEEP_20261124.md` |

---

## 8. Uncharted search (2026-11-25): 28 ideas, 16 testable and worth testing
Ideas and reasons: `docs/IDEAS_UNCHARTED_20261125.md`. Tests: `docs/PREREG_UNCHARTED_20261125.md` (#383–#391),
`docs/PREREG_UNCHARTED_WAVE3_20261125.md` (#392–#401).

| # | Idea | Verdict |
|---|---|---|
| 389 (U17) | Resting bids under wicks | **passing** (S1, S2a, S2b); S2c/S2d open |
| 397 (U27) | Cascade-day reversal | **passing** (S1 + Binance S2) |
| 385 (U8) | Short pre-launch perps | survives S1, small |
| 383 (U1) | Launch-phase vaults | survives S1, below bar |
| 384 (U5–U7) | Withdrawal-queue discounts | KILL on registered data, inconclusive |
| 387 (U2) | Uniswap token auctions | KILL |
| 391 (U21) | Hong Kong IPOs | KILL |
| 396 (U26) | Binance perp launches | KILL |
| 392–395, 398–401 | Binance monitoring tags, Binance listings fade, airdrop-listing dumps, Korean listings fade, BNB launchpool demand, crypto net-nets, CoW AMM, LBPs | running (data fetch `uwave3`, 2026-11-25) |
| 386 (U9) | Upbit/Binance delisting shorts | not testable (2 events) |
| U3, U10, U11, U13–U16, U19, U20, U22 | token sales, testnets, pre-IPO perps, RFQ desks, Timeboost, DRIPs, builder codes, treasury-company premiums, locked-token OTC, Japan perks | not testable, dismissed at desk, or excluded |

---

## 9. Radar and monitoring (runs daily on GitHub, 02:41 UTC)
| Watch | What it does | Output |
|---|---|---|
| Prop-firm pages (~120) | diffs rules and prices | `data/radar/changes.parquet` |
| N1–N9 non-prop leads | stablecoin depegs, extreme funding, new CoW solver payouts, audit-contest prizes, governance posts about incentives/bot roles (23 forums), perp-venue volume surges, Malaysia access pages | `data/radar/leads.parquet` |
| **N10 (new)** | #389 rule applied to every live Hyperliquid perp from 2026-12-01 (paper) | `data/radar/wick_paper.parquet` |
| **N11 (new)** | perps newly listed on Hyperliquid (pre-launch candidates for #385) | leads |
| #371 paper filler | UniswapX orders vs public routes (chained 5.5 h sessions) | `data/uniswapx_paper/` |
Rules: `docs/PREREG_RADAR_NONPROP_20261124.md` (addenda 1–4).

---

## 10. How tests are run (so a result can be trusted)
- **Pre-registered:** question, data, exact rule, costs and pass/kill bars are committed before data are fetched (`docs/PREREG_*`).
- **Staged:** Stage 0 desk check → Stage 1 cheap kill-only test → Stage 2 full / out-of-sample test. A stage may kill early, never pass early;
  rules never change after data are seen (mechanical bug fixes are allowed and recorded).
- **Reproducible:** every figure comes from a command; raw output in `docs/jx_runs/`; each script is re-run once and must print identical
  output; figures go in `docs/FIGURES_LEDGER.md`.
- **Honest labels:** verified (official pages, on-chain) vs third-party vs assumed; survivorship and look-ahead are checked and reported.
- **Data:** the sandbox blocks most sites, so fetches run on GitHub Actions (`scripts/fetch_fallback.py`, `scripts/fetch_uncharted.py`).

---

## 11. Where everything lives
| You want | Open |
|---|---|
| Prop firm rules checked against official pages | `docs/PROP_VERIFY_20261122.md` |
| All prop products compared (62 rows) | `docs/PROP_COMPARISON_20261122.md` |
| Frozen prop inputs (edit prices here) | `docs/radar/prop_assumptions_20261122.csv` |
| Every non-prop idea and verdict | `docs/CANDIDATES.md`, `docs/RADAR_RESULTS_SUMMARY.md`, `docs/NOTES_NONPROP.md` |
| Every number and the command that produced it | `docs/FIGURES_LEDGER.md` |
| Map by workstream | `docs/INDEX.md` |
| Uncharted ideas and their tests | `docs/IDEAS_UNCHARTED_20261125.md`, `docs/PREREG_UNCHARTED_20261125.md`, `docs/PREREG_UNCHARTED_WAVE3_20261125.md` |
| Approval-gated roles (CoW, UniswapX) | `docs/PREREG_COW_*`, `docs/PREREG_UNISWAPX_20261124.md`, `docs/UNISWAPX_PAPER_FILLER_GUIDE.md` |
| Radar rules and reviews | `docs/PREREG_RADAR_NONPROP_20261124.md`, `docs/RADAR_REVIEW_20261124.md`, `docs/AUDIT_ALL_AREAS_20261124.md`, `docs/NICHE_SWEEP_20261124.md` |
| Data fetch jobs (GitHub Actions) | `scripts/fetch_fallback.py`, `scripts/fetch_uncharted.py`, `.github/fallback_request.txt` |


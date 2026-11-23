# Non-prop notes (liquidations, radar, other non-prop ideas)

Prop-firm work is logged in `docs/NOTES_JX.md`. Map of everything: `docs/INDEX.md`.
Earlier non-prop entries (before 2026-11-21) are in `docs/NOTES_JX.md`; the liquidation test's pre-registered
verdict sections ("Liquidation test #100: verdict", "Liquidation shadow test: …") stay there as registered.
New non-prop write-ups start below.

## Radar week 1 (2026-11-21)
**Built** (`docs/PREREG_RADAR_20261121.md`, CANDIDATES #200): daily GitHub Actions job (`.github/workflows/radar.yml`, 02:41 UTC) running
`scripts/radar.py`. The sandbox cannot reach any source; Actions (US servers) collects. Sources: DefiLlama pools + protocols, Merkl live
campaigns, Snapshot proposals (45 days), 53 prop-firm sites crawled two levels into their help centres (1,317 pages), 3 directories
(+ sitemaps: propfirmmatch 18,771 URLs, saveonpropfirms 527), 16 venue docs pages, 8 SDK release feeds. Pages are diffed day to day
(31 pages already changed between today's runs, e.g. E8 Markets). Everything is in one candidate table; every removal is in the near-miss table.

**Baseline sweep (latest run):** 1,295 reward pools + 714 Merkl campaigns + 67 incentive votes → 92 pass threshold, quality, F3–F5 and
Malaysia → 17 with all five filter parts verified; 2,147 near-misses with reasons (1,377 below threshold, 260 DefiLlama outliers,
~360 price exposure (F4), ~70 TVL < $1M (F5), 24 reward not persistent, 18 not long-lived). Known gaps: Polymarket (US geoblock), Tally
(needs key), JS-only pages (Apex/Lucid/Tradeify/ETF/Aqua return 403 to the runner; Phidias/Top One/Blue Guardian prices load by script).

**Week-1 tests (#201–#203, `docs/PREREG_INCENTIVES_W1_20261121.md`): all FAIL.** Lista stables killed at Stage 1 (4.6%/yr net; today's
10.6% reward was a spike), Dolomite killed at Stage 1 (6.4%/yr), Bluefin USDSUI-USDC earned 22.9% / 16.3% net by half but hit the
pre-registered loss-event proxy (TVL fell to 32% of its 7-day high) → near-miss. Lesson, pre-registered as addendum 3: rank the queue by
90-day realised yield, not today's APR. Even the best case was ~$2K/yr per $10K, under one Topstep slot.

**Prop-firm sweep** (`docs/radar/prop_firms.csv`, pricing `scripts/radar_price.py`, raw `docs/jx_runs/radar_price_20261121.txt`):
- Full bots allowed (own pages): Topstep, Lucid, MFFU, TradeDay (inside platforms), Bulenox, TFD, Tradeify (conditional), HyroTrader (crypto);
  CFD: Audacity, Alpha Capital, Goat (NQ strategy not portable).
- **Alert-assisted (bots banned, manual / semi-automated allowed): Blue Guardian, Phidias** (both explicitly allow semi-automated with active
  management), **Alpha Futures, Top One Futures** (ban automation only). Banned outright on CFD: Maven, Lux.
- **FundedNext: its crawled terms now say bots "not expressly authorised" and "systematic execution ... based on external signals" may be
  prohibited** — conflicts with the help-page reading in PREREG_FUNDEDNEXT; moved to `unclear` (matters for workstream A, which had already
  dropped it).
- Pricing, 3-min manual delay: **Alpha Futures Standard 50K $40,155 real / $8,998 coin flip (81% profitable) / dip −$4,773**; Topstep at the
  same delay $37,348 / $14,701 / −$3,094. Not flagged: the pre-registered dip limit is −$4,641 (missed by $132). Blue Guardian Elite 50K
  priced only as a sensitivity (price unreadable): $43.9K / $37.4K real at $141 / $350. Phidias, Top One: rules incomplete in crawled pages.
- All existing models re-priced identically to the ledger (FTMO Pro differs only by $900→$800 scaling vs re-simulation).

**Flag to Jx: none.** Nothing passed the filter and a full pre-registered test.

**Week-2 queue (first run on/after 2026-11-28, addendum 3 ranking):** current top verified row after the protocol-family age fix is Curve
BOLD-USDC (39.9% reward APR, $8.6M TVL); it will be queued only if its 90-day realised yield ranks it top-3.
For workstream A (not acted on here): Alpha Futures Standard 50K could be a manual-entry slot (real net above Topstep at the same delay),
needs a person at the screen 22:30–00:30 MYT and the copy/third-party-signal clauses read by hand.

## Radar update (2026-11-21, afternoon): new firms priced, non-prop fallback tests
**New firms.** Sitemaps of propfirmmatch and saveonpropfirms gave 20 futures firms not on the watch list; their own help centres were
crawled. Priced (rules from own pages, prices from directories = third-party):
- **FuturesElite Elite 50K, manual entry 3 min late: $31,071 real / $5,903 coin flip (79%) / dip −$2,560 → meets the pre-registered
  "extra slot" flag** (Topstep at the same delay: $37,348 / $14,701 / −$3,094). Fragile: at $160 → $28.0K / $2.4K; at $200 → $24.2K / −$2.2K.
  The first run ($44,000) used an assumed funded lock and was corrected from FuturesElite's own page before reporting (addendum 6).
- Goat Flex 50K (bots): $23,784 / −$3,419; Blueberry Ascent 50K (bots, self-built only): $23,397 / −$4,016. Both below Topstep.
- Bot policy (directory text, third-party) for the rest: bots allowed at BluSky, DayTraders, Funded Futures Network, Finotive, The Trading Pit,
  IQ Capital / Traders Launch (conditions); manual only at Purdia, AquaFunded, Hola Prime, YLOS, The5ers Futures. Their 50K rules or prices
  were not readable, so not priced. Several firms allow only bots running "your own strategy": usable only while the friend holds the accounts.
**Non-prop fallback tests (`docs/PREREG_FALLBACK_20261121.md`): both FAIL.** Stablecoin yield rotation −6.5% / 4.8% by half after loss stress
(the highest yields are the pools that collapse); Hyperliquid HLP 27.7% / 7.9% by half (near-miss, yield falling).
**Flag to Jx:** FuturesElite passes the prop-firm pricing flag (not a non-prop opportunity); it needs the price confirmed and a person placing
trades by hand within 3 minutes. No non-prop flag.

## Radar update (2026-11-21, evening): more mechanisms, a process mistake, prop-firm monthly view
**Process mistake (mine), now fixed.** CLAUDE.md says Stage 1 runs "on the cheapest small slice of data". I fetched full two-year histories
before piloting, so ideas killed at Stage 1 still cost the whole GitHub Actions fetch (up to 1.5 h). Fixed in PREREG_RADAR addendum 7:
Stage 0.5 ceiling check from data already in the repo (`scripts/ceiling_20261121.py`), pilot-first fetches, batched jobs.
**Mechanism sweep** (`docs/IDEAS_SWEEP_20261121.md`): 40 mechanisms listed with Stage-0 checks; 9 fail Malaysia/filter at desk check.
**Results since the afternoon:**
- #207 new stablecoin reward programmes, first 30 days: FAIL at Stage 1 (−61.7%/yr with loss stress; 1.9%/yr even without, below Aave).
- #210 ten named stablecoin programmes held (sUSDe, bUSD0, sUSDf, Sky, Spark, Maple, Pendle, Liquity, Felix, HL Earn): all FAIL; 8–13% in
  2024–25, 3–5% in 2025–26.
- #217 best-venue DeFi funding carry: Stage 0.5 KILL (ceiling 7.8%).
- Queued (data fetching): #208 funding gaps, #209 paid-to-borrow loops, #211 Pendle PTs incl. expired, #212 hedged staking, #213 hedged farming,
  #214 hedged governance-token yields (ceiling 25%: yCRV), #216 gold carry, #219 correlated-pair loops.
**Prop-firm monthly view** (`docs/jx_runs/radar_monthly_20261121.txt`): average $/month 2016–26 Topstep $341, Alpha Std (3-min manual) $309,
Lucid $289, TradeDay $85 $274, MFFU $265, FuturesElite (3-min) $239; payouts land in only ~1 month in 5; last 24 months ~3× the 10-year average.

## Radar update (2026-11-21, night): verdicts for the 16 queued tests — no pass, no flag
| # | idea | verdict |
|---|---|---|
| 209 | paid-to-borrow stable loops | survives ceiling (11.4%); not testable further (borrow history paywalled, HTTP 402) |
| 211 | Pendle PTs to maturity | FAIL Stage 1 (−7.0%; apxUSD depeg) |
| 212 | hedged liquid staking | FAIL Stage 1 (churn costs; buy-and-hold also < 8% in year 2) |
| 213 | hedged reward farming | FAIL Stage 1 |
| 214 | hedged governance-token yields | FAIL: passed the fee-APY rule, but wrappers lost 40–60% vs CRV |
| 216 | gold carry (PAXG) | FAIL (7.1% / 5.1%) |
| 219 | correlated-pair loops | KILL at ceiling (6.8%) |
| 220 | hedged JLP | not testable (no history) |
| 221 | hedged GMX GM | FAIL: passed fee-APY rule, real GM prices 3.6% / 3.2% |
| 222 | dYdX MegaVault | FAIL (67 days of history) |
| 223 | Lighter LLP | not testable (no history) |
| 224 | stable-pair DEX LPs | FAIL Stage 1 (−12%) |
| 225 | Gains/trader-counterparty vaults | FAIL on primary rule (equal-weight 10.7% / 13.2%, ~$2.5M capacity) |
| 227 | other savings rates | FAIL |
| 228 | hedged TRX energy / SKY staking | TRX KILL; SKY 12.9% / 16.9% but only 112 days → FAIL, re-test ≈ 2027-01-07 |
| 229 | hedged native staking | ATOM KILL; INJ ceiling 12.1% but no APR history → not testable |
Lesson: two apparent passes (#214, #221) came from DefiLlama "APY" fields that leave out the price of the token earning the yield; the robustness
checks (real token prices) removed both. Watch list: #228 SKY (re-test at 180 days), #209 Dolomite loops, #229 INJ, #205 HLP, #225 Gains.

## Radar update (2026-11-22): new prop-firm structures found and priced
| # | product | bots / manual | result vs Topstep 50K ($44,359 real / $18,046 coin flip) |
|---|---|---|---|
| **233** | **The Trading Pit Futures Prime 50K** | bots (own T&C), Malaysia OK, Level 1 data free | **$46,597 real / $14,016 coin flip (95%) / dip −$4,884 at $99 (price verified on TTP's own page) → FLAG** (fails at ≥ $149) |
| 236 | DayTraders EOD 50K | bots (own help centre), 100% split, 5 accounts | price unreadable: at $99 $48,602 / $13,511; at $199 $36,802 / −$4,406 → confirm price |
| 206 | FuturesElite Elite 50K | manual (3-min) | $33,645 / $9,121 (91%) with its own $89 reset → flagged (purchase price $128 third-party) |
| 231 | MFFU Builder 50K (new plan, caught by the radar diff) | bots, 1 account | $153: $25,323 / $2,022; with the 30% code $107: $32,453 / $9,759 |
| 232 | MFFU Studio (static MLL, withdraw any time) | bots | not flagged (coin flip negative: 2:1 target-to-loss evaluation) |
| 234 | Traders Launch 100K / 200K | bots (pre-approval) | not flagged (1% drawdown too tight) |
| 235 | TTP Futures Prime 150K | bots | not flagged ($43.7K / −$6.6K) |
**Flag to Jx (passes the prop-firm sweep rule on verified rules and price): The Trading Pit Futures Prime 50K** — an additional automated slot
alongside Topstep. Before buying: confirm one account per person limits, the 30-day challenge window (modelled), and that the friend's bot runs
on the friend's own TTP account (TTP bans the same EA used by multiple traders).

## Radar update (2026-11-22, later): 22 more prop products (#237–#258, PREREG_RADAR addendum 14; re-run identical)
**Flagged on registered prices:** TTP Futures Prime 50K with its own $79 reset — **$49,057 real / $16,960 coin flip (97%) / dip −$3,884**
(Topstep 50K: $44,359 / $18,046 / −$3,520); FuturesElite Nitro 50K, manual entry 3 min late, $152 (directory price) — $48,463 / $15,373 / −$4,331
(its funded drawdown is intraday, modelled end-of-day → optimistic).
**Would flag if the unread price is near the low bracket (sensitivity, not flagged):** TTP Futures Instant 50K ($299), LucidDaily 50K ($99),
MFFU Pro 50K ($127), DayTraders S2F 50K ($199), FuturesElite Prime 50K ($129 and $229), FuturesElite Instant 50K ($199 and $349: $102–115K real,
looks too good → verify first), Blue Guardian Reserve 50K ($150). Blue Guardian Direct 50K misses only on the dip rule.
**Not flagged:** TTP Prime 100K, Goat 1-Day 50K/100K, Goat EOD, all Alpha Zero/Advanced/Direct/Standard-100K, MFFU Pro One-Day, LucidDirect.
**Pattern:** instant (no-evaluation) accounts with one-time fees and 90–100% splits score very high in the model: each is a cheap ticket whose
payout chance is high for this bot. Their real prices (mostly script-loaded) decide everything — confirming 6 prices would settle 8 products.

## Radar update (2026-11-22, evening): batch 6 — 20 more non-prop mechanisms (#259–#278)
One narrow pass, not robust: **#276 hedged native HYPE staking** (24.9% / 9.2% by half on the registered rule; 6.5–8.2% in year 2 without the
assumed staking yield or at 2× leverage; essentially HYPE funding carry, which fell from 117% to ~10%). Everything else failed or is not testable:
zero-fee-venue funding gaps and carry (Lighter) lost money in the 31-day pilot; junior/senior tranches and new-chain incentives collapsed; Votium
bribes are swamped by CVX's −52%/yr; RWA (3.9%), CME basis (2.6%) and reverse carry (6.3%) die at the ceiling; Drift/Umbrella/Paradex lack data.
No flag to Jx (#276 is reported as marginal; a 3× short on HYPE also carries unmeasured liquidation risk).

## Refinement results (2026-11-22): configuration changes, year-1 design / year-2 test
**Found a bug in my own #208 script: fees were charged twice.** Corrected, the original cross-venue funding-gap rule PASSES (20.3% / 11.9% by half,
no losing month, ~$6.4K/yr on $40K) — but it is fragile: it fails at 2× fees, needs the Aevo pairs (HL–dYdX alone fails), and entry/exit price
differences, slippage and collateral moves are not modelled. Refinement passes: R1 funding gaps with maker fees (24.9% / 17.1%), R5 hedged HYPE staking
(23.4% / 9.3%, marginal), R6 Gains vaults equal-weight (11.6% / 9.8%, ~$2–3M capacity; price check pending). Failures with every configuration:
GM pools (best hedge ratio flips sign between years — classic overfitting the protocol caught), stable-yield selection, new-reward programmes,
conditional carry. **First non-prop candidates worth a small live pilot: #208 funding gaps (needs an execution-cost pilot on Aevo), then #225 Gains.**

## Walk-forward retest (2026-11-22): 16 ideas, 12–270 configurations each
Method: every month, use whichever configuration did best over the previous 6 months; 18 out-of-sample months. Three survive:
**funding gaps (#208)** 12.8% / 18.2% (but only with maker fees; taker-only fails the 1.5× cost check), **hedged HYPE staking (#276)** 15.0% / 8.7%,
**Gains vaults (#225)** 9.6% / 14.1% (tiny capacity). Everything else fails with every configuration: stablecoin-yield selection, stable LPs,
savings rates, new-chain and new-reward programmes, GM pools, carry, hedged staking. These three are the only non-prop ideas worth a live pilot;
each pilot costs money → Jx decides.

## 2026-11-22 — batch 7: three of the four survivors fail their checks
- **Funding gaps (#208)**: the free paper execution test (647 order books, 3 hours) shows a $10K market order costs 55 bps per side on Aevo and
  23 on dYdX, vs a 2.5-bps budget; the top of book holds ~$2.9K on Aevo. The modelled return is not reachable at useful size. A live pilot would
  only confirm this → **no longer recommended for a paid pilot.**
- **Gains vaults (#225)**: the real gUSDC price fell 1.180 → 1.119 over the test period; DefiLlama's APY overstated it (6.9% vs 10.7%/yr). FAIL.
- **Pendle (#211)** with all 344 expired markets: FAIL (0.8% / 7.9%).
- **Hedged HYPE (#276)**: liquidation check pending (HYPE candles in the batch-8 run).
- Batch 8 (12 new mechanisms #279–#290) pre-registered; Stage 1 pilot data being fetched.
- **#276 hedged HYPE fails with liquidations** (HYPE rose up to 124% in a week; the 3× short is liquidated 12 times; walk-forward 13.6% / −8.9%).
  All four walk-forward survivors have now failed their follow-up checks.
- **Batch 8 Stage 1:** 2 of 12 continue: #280 Deribit↔HL funding gaps (12.7% in the pilot) and #288 Hyperliquid user vaults (27.3%, but −24% in
  October, survivorship). 4 killed (#281 cash-and-carry 2.6%, #282 short straddles −31%, #284 HIP-3 gaps −2%, #285 Kamino loops −4%).
  6 not testable (Drift, Boros, Aave, Morpho ×2, Orderly: no data). Stage 2 + repair probes fetching (`batch8s`).

## 2026-11-22 — sweep 2 (24 Topstep-shaped mechanisms, #296–#319)
List and desk checks: `docs/IDEAS_SWEEP2_20261122.md`; tests: `docs/PREREG_BATCH10_20261122.md`. So far: #300 stock-perp carry and #314
index-perp carry KILL; #298 sale-window buying (prop side) roughly doubles the number of products meeting the flag rule at 40% off (optimistic:
resets discounted too). recycle.py gained an optional two-phase evaluation and fee refund (for the CFD firms in #296); tests pass.

## 2026-11-22 — the 22 queued ideas: verdicts
Failed: #280 (execution), #288, #291, #292, #293, #294, #295, #301, #302, #305 (artefact), #320, #322, #325. **Passed the registered test: #303
S&P 500 additions** (+3.90% per event, t 2.97; quarterly-only +3.49%, t 2.36), but F4 fails (stock risk, not capped), so it is a near-miss under
the five-part filter. Open: #324 (needs share prices). Not tested / not testable / not completed: #296, #297, #304, #306, #307, #308, #321.

## 2026-11-22 — correction: #303 fails (look-ahead); sweep 4 verdicts
S&P's own announcement dates show the registered #303 entry (5 trading days before inclusion) was before the announcement for 13 of 20 dated
additions. Buying after the announcement earns +0.17% per event (t 0.15). **No non-prop idea has passed a full test.** Sweep 4: #334 Coinbase
listing short FAIL, #335 buyback rotation FAIL, #337 deletions KILL, #339 tokenised gold open but not credible as measured, 7 not testable
(memecoin history limited to about 2 days by pump.fun's API; no index-token NAV, spin-off list, Nasdaq-100 change table or ETF list; 2 unlocks).

## 2026-11-23 — futures factors (#350–#354, Databento) and the research report
- **#351 futures cross-sectional momentum passes the registered full test** (20.72%/yr walk-forward 2016–26, halves 26.94% / 14.97%, costs ×1.5
  20.20%, worst drawdown −22.3% vs SPY −23.9%). First non-prop pass in the repo. #350 trend/carry, #352 value, #353 skew, #354 multi-factor FAIL.
  A mechanical bug (5-year window sliced to empty) was fixed before the final run; #351 was unaffected.
- **#351b: not usable at Jx's size.** With whole micro contracts on the 13 markets a small account can trade, $15K and $50K fail (second half
  3.08% / 7.89%); even fractional sizing on those 13 markets fails. The edge needs the full universe (full-size rates and FX), so ~$250K+, for
  ~15–20%/yr. That is a standard managed-futures premium, not a prop-like return.
- **Research report** `reports/Non prop high return alternatives.md` (notes in `research_notes/Non prop high return alternatives/`): across
  crypto, TradFi, protocol-paid roles, Malaysian promotions and DePIN, nothing shows repeatable > 100%/yr on small capital. Closest: liquidation
  bonuses (workstream B shadow test), hedged points farming (one-off episodes, #360 not measurable), CoW solving and Across relaying (measurable
  from on-chain data: registered next as #361 / #362).


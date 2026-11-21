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

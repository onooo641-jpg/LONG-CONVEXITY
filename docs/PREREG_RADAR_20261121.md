# Radar (workstream C): design, thresholds and test queue — 2026-11-21 (CANDIDATES #200 upward)

Written and committed **before** the radar's first run. Implements HANDOFF_NONPROP "Change of approach",
"Radar sources, reworked", "Baseline sweep first", "Wider but not looser", "Staged testing".
The radar is a scanner, not a test: it produces a ranked candidate table. Nothing it prints is a pass/fail
result for an idea; ideas only pass through a separate pre-registered test (`docs/PREREG_<NAME>_*.md`).

Candidate numbers: **#200** = the radar itself (baseline sweep + prop-firm sweep). Each tested idea gets the next
number (#201, #202, ...).

## Runs
- **Baseline sweep**: first run, a full snapshot, no diffing. Then **daily** (GitHub Actions, 02:41 UTC) diff mode.
- Code `scripts/radar.py`; workflow `.github/workflows/radar.yml`; outputs `data/radar/` (tables) and
  `docs/jx_runs/radar_<run_id>.txt` (raw log). Sandbox cannot reach these hosts, so only Actions (US servers) collects.
  US-geoblocked sources are not circumvented: they are logged in the near-miss table as "no data".

## Sources (all public, primary; no keys, no spending)
| id | source | what is collected |
|---|---|---|
| S1 | DefiLlama `yields.llama.fi/pools` (all pools) | pools with `apyReward` > 0: TVL, reward APY, stablecoin, IL risk |
| S2 | DefiLlama `api.llama.fi/protocols` (all protocols) | listing date, TVL, chains, category; new-listing flag |
| S3 | Merkl `api.merkl.xyz/v4/opportunities` (all pages) | live campaigns: daily rewards, TVL, APR, start |
| S4 | Snapshot GraphQL (last 45 days of proposals) | proposals whose title mentions incentives / emissions / rewards / grants / liquidity mining |
| S5 | Rule/pricing/FAQ/changelog pages, `docs/radar/watchlist.csv` | page text snapshot, daily diff, automation and Malaysia sentences |
| S6 | Prop-firm directories (propfirmmatch, propvator, saveonpropfirms), same file | outbound firm domains not yet in the registry ("discovered firms") |
| S7 | GitHub releases feeds of venue SDKs/bots, same file | new releases (builder signal) |
Not collectable (logged as near-miss "no data"): Polymarket (US geoblock), Tally (needs a key).

## Candidate table (`data/radar/candidates.parquet`, one row per source item)
`item_id, source, venue, chain, what_pays, budget_usd_day, competing_capital_usd, reward_apr_pct, start_date,
first_seen, last_seen, url, stablecoin, il_risk, rank_score, filter_f1..f5, malaysia, status`.
- **budget/day**: S1 = TVL × apyReward / 100 / 365; S3 = `dailyRewards`; S4 = USD amount parsed from the title if any, else blank.
- **competing capital** = TVL (S1, S3). **Money per competitor = reward APR % = budget/day ÷ capital × 365.**
- **Rank** by money per competitor, descending, among rows that reach the ranking stage.

## Screening, in order (all thresholds fixed now)
1. **First-pass threshold (deliberately low)**: S1 apyReward ≥ 3% and TVL ≥ $50,000 and budget/day ≥ $20;
   S3 live, daily rewards ≥ $20 and TVL ≥ $50,000; S4 keyword match; S2 listed ≤ 30 days and TVL ≥ $1M (new venue flag).
   Below threshold → near-miss "below threshold: <metric>". Pools with no reward at all are not candidates (counted only).
2. **Data quality**: DefiLlama `outlier` true, or APR > 1000%, or TVL < $50K → near-miss ("outlier", "implausible").
3. **Five-part filter** (automated proxies; "unverified" is allowed to pass to the deep check but never to a test):
   - F1 repeatable: the reward exists in ≥ 70% of daily points over the last 180 days (S1 chart history, deep check).
     S3: campaign belongs to a protocol with ≥ 3 distinct campaigns seen (unverified until history accumulates).
   - F2 long-lived: protocol listed ≥ 365 days ago (S2) AND pool reward history ≥ 180 days (S1 deep check).
   - F3 reused setup: the venue has ≥ 2 reward-paying candidates, or is deployed on ≥ 2 chains.
   - F4 capped downside: stablecoin = true AND ilRisk = "no" (no price exposure). Non-stable rows fail F4
     with reason "price exposure, needs hedge" (re-reviewable; not dropped silently).
   - F5 scales by copies: TVL ≥ $1M (a $10K position is ≤ 1% of the pool).
4. **Malaysia access check** (before any test): venue category table `docs/radar/malaysia.csv` and, for firms, the
   restricted-countries sentence on the fetched pages. Status ∈ {blocked, grey-area, unverified-onchain, ok}.
   `blocked` or `grey-area` → near-miss (not a pass). `unverified-onchain` (permissionless contracts, frontend not
   checked) proceeds to the desk check, where I check it by hand.
5. **Deep check** runs only on the top 60 by rank that survive 1–3 and 4, to save requests (S1 chart history).
6. **Near-miss table** `data/radar/nearmiss.parquet`: `item_id, source, venue, stage, reason, metrics, first_seen, last_seen`.
   Nothing is removed without a row. Reviewed monthly in NOTES_NONPROP.

## Test queue (testing capacity is the bottleneck)
- At most **3 candidates a week** go to a test, chosen by rank among rows that pass the filter (all five parts verified,
  Malaysia status not blocked/grey) and have not been tested. A candidate is a *venue-level setup* (e.g. "stable pools of
  protocol X paying token Y"), not a single pool.
- Each gets a **Stage 0 desk check** (rules, bot policy, Malaysia access, five-part filter by hand, minutes), then a
  pre-registered **Stage 1 pilot** with a kill-only threshold set loose, then **Stage 2** the full test. A stage may
  kill; none may pass early; full-test rules never change after pilot data. Each test is its own PREREG file,
  committed before running.
- Test question template for incentive setups: *does the realised reward per $ deployed (after dilution from own
  deposit, gas, hedge cost, token sell-off) exceed T-bill + 8%/yr, in both halves of the available history, with
  capped downside?* The exact numbers are set in that test's own PREREG.

## Prop-firm sweep (inside the radar)
Registry `docs/radar/prop_firms.csv`: firm, product, rules URL, **automation status** ∈ {`full_bots`, `alert_assisted`,
`banned`, `unclear`}, evidence label ∈ {verified (firm's own page read), third-party, assumed}, quoted sentence, Malaysia status.
- `full_bots`: firm's written rules allow automated/API order entry by the account holder.
- `alert_assisted`: full bots are banned but the written rules allow a person placing orders from alerts/signals
  (no auto-execution, no copy-trading of purchased signals unless allowed).
- The radar collects the automation sentences from each firm's pages daily; I classify by reading them. A firm whose
  status is not read from its own page stays `unclear` and is **not priced**.
- **Pricing** (`scripts/radar_price.py`, `backtest/recycle.py`, `XFARules`, `Policy.LOCK_FIRST`, friend's NQ orders,
  2016-01..2026-10, $900 base risk scaled as in PREREG_ROUND3: risk = min(0.45 × loss limit, 0.875 × daily loss limit)):
  - `full_bots`: real trades and the coin-flip test (random sign, commission kept, 200 runs, seed 1).
  - `alert_assisted`: the same two, with every entry **3 minutes late** (PREREG_DELAY_20261121: largest viable delay).
  - Rules not yet modelled in the repo are written from the firm's own page; if a rule is unreadable the product is not priced.
- **Reading (ranking, no pass/fail)**: a firm product is flagged **"extra slot candidate"** if real net ≥ 50% of Topstep 50K
  ($44,359 → ≥ $22,180; for delayed products compare with Topstep at 3 min delay, $37,348 → ≥ $18,674) AND coin-flip median ≥ $5,000
  AND worst dip no deeper than 1.5× Topstep's (−$3,520 → ≥ −$5,280). Malaysia access and the live-account cost of an
  extra slot are checked in the desk check, not here.

## Reporting
Weekly "Radar" section in `docs/NOTES_NONPROP.md`: counts by stage, top-10 ranked, new this week, near-miss changes,
rule-page diffs, prop-firm table, tests started/killed/passed. Jx is flagged only for something that passes the
five-part filter **and** a full pre-registered test.

## Not in scope
Anything private or insider; paid data; geoblock circumvention; workstream B (liquidations).

## Addendum 1 (2026-11-21, after the first baseline run, scanner fixes only; thresholds unchanged)
The first Actions run showed: (a) DefiLlama's JSON was cut off by a 5 MB read cap in `scripts/radar.py` (mechanical bug;
S1/S2 had 0 rows, so no S1 results exist yet); (b) every Merkl "BORROW" and "collateral/looping" campaign passed F4 only because
its tokens were stablecoins. Borrow/collateral positions carry liquidation risk, so for S3 **F4 now also requires action ≠ BORROW and
no "collateral/looping/leverage" in the name** (this applies the existing F4 "no price exposure" rule; it does not loosen anything).
(c) Firm help centres hide the bot policy in articles, so page following is now two levels deep (≤30 + ≤15 links per firm),
and directory sitemaps are fetched to enumerate firms.

## Addendum 2 (2026-11-21, before pricing the newly classified firms)
From the crawled pages (own help centres): Blue Guardian and Phidias allow semi-automated trading with active human management;
Alpha Futures and Top One Futures ban automation but not manual entry → classified `alert_assisted` (priced with the 3-minute delay).
New models in `scripts/radar_models.py`: **Alpha Futures Standard 50K** (all rules readable) and **Blue Guardian Elite 50K** (all rules
readable except the purchase price, which the static pages do not contain). Blue Guardian is therefore run at two bracket prices ($141 = its
fixed reset fee, $350) as **sensitivity only, not ranked or flagged**, consistent with "if a rule is unreadable the product is not priced".
Phidias and Top One: plan target/price not in crawled pages → not priced. FundedNext's crawled terms now prohibit bots "not expressly
authorised" → `unclear`, no longer priced as full_bots (reported for the prop-firm workstream).

## Addendum 3 (2026-11-21, after week 1; applies from week 2, does not change week-1 results)
Week 1 showed the snapshot reward APR picks spikes (#201: 10.6% today, 5.6% average). From week 2 the test queue ranks fully verified
rows by the **90-day mean of (apyBase + apyReward × 0.9) from the deep-check chart history**, not by today's reward APR; rows with
< 90 days of history are not queued. The daily table keeps today's APR as `rank_score` for display. Max 3 tests a week, unchanged.
Week-2 queue is chosen this way from the first run on or after 2026-11-28.

## Addendum 4 (2026-11-21): new futures firms from the directory sitemaps
Parsing the sitemaps collected in the baseline (`data/radar/directory_urls.parquet`) found 20 futures firms not on the watch list:
BluSky Trading Company, DayTraders, Funded Futures Network, IQ Capital, NexGen ProTrader Funding, Purdia Capital, Legends (rules page),
Blueberry Futures, Finotive Futures, FuturesElite, Goat Funded Futures, Hola Prime Futures, Trade The Pool, Traders Launch, YLOS Trading,
E8 Futures, BrightFunded Futures, The5ers Futures, The Trading Pit Futures, AquaFunded Futures. Their directory pages (third-party) are
added as `directory_firm` rows so their automation sentences are collected; a firm is classified only from its own pages, so each
needs its own site added once its domain is known. Scanner change only; no thresholds changed.

## Addendum 5 (2026-11-21): pricing the directory-found firms (before running)
Own help centres crawled (radar run 9). Priced where the 50K plan's rules are readable on the firm's own pages; the purchase price comes from
the directory listing (third-party, the higher/list figure where two are shown) because the firms load prices by script. Same procedure as
the main sweep (coin flip 200 runs seed 1; real trades; 3-min delay for alert-assisted; flag rule unchanged). Products:
- **Goat Funded Futures Flex 50K** (full bots, own strategy): target 6% $3,000, EOD trailing $2,000 locking at start (both phases), eval
  consistency 50%, funded none, no DLL, 30 micros, payouts after 5 winning days ≥ $250, 50% of profit up to $2,000, min $500, split 80%;
  $218 one-time, resets priced as a rebuy.
- **Blueberry Futures Ascent 50K** (full bots only if self-built and disclosed; "systems obtained from a friend" banned → usable only if the
  friend holds the account): target $3,000, EOD $2,000, **2 minis / 20 micros**, 30-day limit, reset $125; funded buffer $2,100, cap $2,500,
  min $500, 5 days ≥ $200, 35% consistency; $245; split and funded lock not stated → assumed 90% and start + $100.
- **FuturesElite Elite 50K, with DLL** (alert-assisted: "Fully automated trading using AI or bots is not permitted"): target $3,000, EOD
  trailing $2,000 (funded lock not stated → assumed at start), 50% eval consistency, DLL $1,200, 40 micros, no time limit; funded: 6 days ≥ $150,
  50% of profit, min $500, cap $2,000, 90%, no consistency or buffer; $128 (only figure shown).
Not priced (rules or prices not readable): The Trading Pit Futures, E8 Futures, Traders Launch, DayTraders, Funded Futures Network, BluSky,
Finotive, AquaFunded, Purdia, YLOS, Hola Prime, The5ers Futures, IQ Capital, Trade The Pool, NexGen, Legends.

## Addendum 6 (2026-11-21): FuturesElite rules now read, before re-pricing
The first FuturesElite run (flagged, $44,000) used two assumptions. A post-hoc sensitivity (`scripts/radar_fe_sens_20261121.py`) showed the
result depends on them (never-locking floor → −$4,480; $200 price → $35,504). FuturesElite's own article "Elite drawdown, daily loss limit and
contracts" (2026-10-18) states the 50K floor **locks at start + $100** and funded contracts **scale 20 / 30 / 40 micros** (below $2,500 / from
$2,500 / from $3,499). The model is corrected to those rules (scaling applied in both phases: conservative) and re-priced; the corrected run
replaces the first. The $128 price stays third-party (directory, "With DLL" plan).

## Addendum 7 (2026-11-21): Stage 0.5 ceiling check and pilot-first fetches (process, applies to every new test)
The slow step is fetching data through GitHub Actions (10 min – 2 h). Until now the full history was fetched before the Stage-1 pilot could
kill an idea, so failing ideas still cost the whole fetch. From now on:
1. **Stage 0.5 ceiling check (minutes, data already in the repo):** compute the idea's best case from current/recent data (today's pool
   yields, last-90-day funding, etc., choosing the most favourable values). If even that best case is below the test's bar → KILL without
   fetching anything. Kill-only: a high ceiling never counts as a pass.
2. **Pilot-first fetch:** the first fetch pulls only the Stage-1 window (last ~90 days). The full history is fetched only for ideas that
   survive Stage 1.
3. Run several ideas' fetches in one Actions job.
First application (`docs/jx_runs/ceiling_20261121.txt`): #217 best-venue carry ceiling 7.8%/yr (HL leg, best 3 of its 12 coins over the last 90 days,
chosen with hindsight) < 8% → **Stage 0.5 KILL**. #212/#213 majors: ceilings 6.6–9.6% (marginal, data already queued). #214: yCRV 20.7% +
CRV short funding 12.7% → ceiling 25% (highest of the batch).

## Addendum 8 (2026-11-22): new product caught by the rule-change watcher — MFFU Builder 50K (priced before running)
Rules from MFFU's own help centre ("Builder Plan 50k - A Comprehensive Guide", 2026-10-21): eval target $3,000, EOD trailing MLL $2,000,
soft DLL $1,000 (pause), 40 micros, no eval consistency, 1 day minimum; sim funded starts at $0, MLL $2,000 EOD trailing (locks at $0 when the
peak reaches +$2,000, assumed from "trails up to breakeven"), payouts above a $2,100 buffer, first needs $500 above buffer, later $500 since the
last payout, 2 qualifying days per cycle, 50% consistency, min $500, cap $2,000, 80/20, 5 sim payouts then live (modelled as the account ending,
as Lucid); one-time price $153 list ($107 with the 30% code: sensitivity), no activation; one sim-funded account per user. MFFU allows bots
(PREREG_ROUND3). Same pricing procedure and flag rule as the sweep (no delay; risk $875 under the $1,000 soft DLL).

## Addendum 9 (2026-11-22): MFFU Studio plans (#232), priced before running
MFFU's own help centre ("Studio Plans - A Comprehensive Guide", effective 2026-10-14): #001 $10K ($140, static MLL $500, target $1,000, 10 micros),
#002 $20K ($280, $1,000, $2,000, 20 micros), #003 $5K ($75, $250, $500, 5 micros); no DLL, no consistency, no minimum days; sim funded starts at
$0 with the same **static** MLL; **all net profit above $0 can be withdrawn any time** (min $250, #003 $100), 80/20; one Studio account per user;
daily purchase cap. Modelled with a static floor that never moves and withdrawals as soon as ≥ the minimum (`Policy.IMMEDIATE`, needed because
there is no lock); risk = 0.45 × MLL. Same coin-flip test and flag rule as the sweep. The daily profit cap ($2.5K–$10K) never binds at this risk.
Limits: the daily purchase cap and "availability is limited" may make a recycling plan impossible in practice.

## Addendum 10 (2026-11-22): The Trading Pit Futures Prime 50K and Traders Launch 100K/200K (#233), priced before running
- **TTP Futures Prime 50K** (support.thetradingpit.com "How it works", "Rules", "Rewards"): target $3,000, EOD trailing $2,000 locking at the
  starting balance in both phases, daily pause $1,000 (soft, risk $875), 50 micros, 30-day challenge, 40% eval consistency (modelled as
  combine_consistency 0.40), funded: 5 profitable days ≥ $150 per reward, up to 50% of profit, cap $2,500, 80%; price $99 (directory list,
  third-party), resets priced as rebuys, $0 activation. Bots: own EAs allowed (directory text). Market-data fee not stated → not modelled.
- **Traders Launch 100K / 200K** (traderslaunch.com pricing + rules + payout rules, 2026-07-16): one-time $159 / $299; target $2,000 / $4,000;
  EOD drawdown $1,000 / $2,000 locking at the starting balance (assumed the same once funded); fixed 20 / 40 micros; 40% session-profit limit in
  the evaluation (modelled as combine_consistency 0.40); 60-day limit; funded: payouts daily once above +1% (modelled as a buffer of 1% = $1,000 /
  $2,000), no cap, no consistency, 80%; up to 5 accounts per user; EAs allowed after pre-approval. Risk = 0.45 × drawdown.
Same procedure and flag rule as the sweep.

### Addendum 10 results (2026-11-22; `docs/jx_runs/radar_price_ttp_prime50.txt`, `radar_price_traders_launch.txt`, re-run identical)
- **TTP Futures Prime 50K: real $46,597 / coin flip $14,016 (95% profitable) / worst dip −$4,884 → EXTRA SLOT CANDIDATE** (Topstep 50K $44,359 /
  $18,046 / −$3,520). Checked on TTP's own pages: Level 1 market data included free (no data fee); EAs/automation allowed except listed abuse
  functions and the same EA run by multiple traders; Malaysia not on either restricted list (eligibility FAQ). Price $99 is third-party
  (directory; own page loads by script). Sensitivity (`docs/jx_runs/ttp_sens_20261122.txt`, labelled): $59.40 → $53.5K / $21.7K (100%);
  $149 → $37.8K / $4.2K (67%, flag fails); $199 → $29.1K / −$5.7K; 3-min manual entry → $33.4K / $10.7K. The flag depends on the price being ≤ ~$120.
- Traders Launch 100K / 200K: $722 / $4,371 real, coin flip −$13.6K / −$24.4K → not flagged (1%-of-account drawdown is too tight for this strategy).

## Addendum 11 (2026-11-22): TTP Futures Prime 150K (before running)
Same TTP rules as addendum 10 at the 150K size (own support pages): target $9,000, EOD trailing $4,500 locking at start, daily pause $3,000,
150 micros, reward cap $5,000 (50% of profit), 5 profitable days ≥ $150, 30-day challenge, 40% eval consistency; price **$289** (directory list;
third-party). Risk = min(0.45 × 4,500, 0.875 × 3,000) = $2,025. Same flag rule (reference Topstep 50K, as in the sweep).

## Addendum 12 (2026-11-22): DayTraders EOD 50K (#236) and TTP price verified
- TTP's own futures page (thetradingpit.com/futures, crawled 2026-11-22) lists the $50,000 Futures Prime at **"Price $99"** → #233's price is now
  verified, not third-party.
- **DayTraders EOD 50K** (daytraders.com help centre, 2026-10-22): bots allowed ("scripts, bots and strategy automation that trade at normal
  execution speeds", VPS allowed). Eval: target $3,000, EOD trailing $2,000 stopping at start (both phases), DLL $1,250 soft (risk $875), 100 micros,
  2 qualifying days ≥ $200, 50% consistency, no time limit, no resets (failed eval = new purchase); funded: $5 activation, 8 qualifying days ≥ $200
  between payouts, 30% consistency, request $500–$2,000, balance must stay ≥ start + $2,000 after the payout (buffer $2,000; request needs
  ≥ $2,600), **100% split**, up to 5 EOD accounts. Evaluation price not readable (loads by script) → **bracket $99 / $199, sensitivity only, not
  ranked or flagged** (as Blue Guardian).

## Addendum 13 (2026-11-22): FuturesElite Elite 50K evaluation reset read from its own page
FuturesElite "Reset fees" (crawled 2026-11-22): Elite 50K evaluation reset **$89** (the model used a $128 rebuy). Model updated (`reset=89`);
purchase price stays the $128 directory figure (own page does not show it). Re-priced with the same procedure.

## Addendum 14 (2026-11-22): 22 more prop-firm products (#237–#258), registered before any run
Source: each firm's own help centre in the radar crawl (2026-11-21/22), quoted in `data/radar/snapshots/`. Same procedure as the sweep: friend's
NQ orders 2016-01..2026-10, coin flip 200 runs seed 1, `Policy.LOCK_FIRST`, risk = min(0.45 × max loss, 0.875 × daily limit), 3-minute entry
delay for alert-assisted firms, same "extra slot" flag rule (vs Topstep 50K; delayed products vs Topstep at 3 min). **Products whose purchase price
is not readable on the firm's own page are run at two bracket prices as sensitivity only (marked [sens]) and are never ranked or flagged.**
Model limits stated now: intraday-trailing funded drawdowns are modelled as end-of-day (optimistic) and marked; unstated payout caps are assumed
and marked; "N payouts then live" is modelled as the account ending.

| # | product | bots/manual | price used | key rules (own pages) | assumptions |
|---|---|---|---|---|---|
| 237 | TTP Futures Prime 50K re-priced (reset $79, activation $0 now, own page) | bots | $99 | as #233 | — |
| 238 | TTP Futures Prime 100K | bots | $189 (own page) | target $6,000, EOD $3,000 locking at start, pause $2,000 (challenge only), 100 micros, cap $3,500 | reset priced at $189 rebuy |
| 239 | TTP Futures Instant 50K | bots | [sens] $299 / $499 (directory) | instant; EOD $2,000 trailing to start; pause from $1,200; per-cycle target $3,000; 20% consistency; 5 days; min $500; caps $2,000→$2,500→$3,000; 90% | cap modelled $2,500 |
| 240 | Lucid LucidDaily 50K (EOD add-on) | bots | [sens] $99 / $199 | target $3,000, MLL $2,000, 50% eval consistency, 40 micros; funded buffer $2,100, lock +$100, profit since last payout > 0, no consistency, 90% | cap assumed $2,000 |
| 241 | Lucid LucidDirect 50K | bots | [sens] $299 / $499 | instant; EOD MLL $2,000 lock +$100; DLL $1,200; goals $3,000 then $2,500; 20% consistency; min $500; 90% | cap assumed $2,000 |
| 242 | MFFU Pro 50K | bots | [sens] $127 / $227 | target $3,000, EOD $2,000, 50% eval consistency, 30 micros; funded buffer $2,100, min $1,000, no cap, MLL to start+$100 static after the 1st payout, 80% | 14-day first-payout wait not modelled |
| 243 | MFFU Pro 50K One-Day | bots | [sens] $127 / $227 | as #242 but target $4,000, no eval consistency | same |
| 244 | DayTraders S2F 50K | bots | [sens] $199 / $399 | instant; EOD $2,500 stopping at start; DLL $1,250; 10 qualifying days ≥ $200; 20% consistency; max $2,000; 100% | buffer $2,500, min $500 |
| 245 | Goat 1-Day Pass 50K | bots | $218 (directory list) | target $3,000, EOD $2,000 lock at start, no eval consistency, 40 micros; funded 35% consistency, 5 winning days ≥ $100, 50% of profit, min $500, 80% | cap modelled $1,750 (caps 1,500→2,500) |
| 246 | Goat EOD 50K | bots | [sens] $150 / $250 | target $3,000, EOD $2,000 lock at start, 50% eval consistency, 50 micros; funded 30% consistency, 7 winning days ≥ $100, DLL $1,250, 50% of profit, min $500, 80% | cap $2,000 |
| 247 | Alpha Futures Zero 50K | manual | $169/month, reset $149 (own) | target $3,000, EOD $2,000 lock at start, DLL $1,000, 30 micros; qualified ladder 10/20/30 micros, 40% consistency, 50% of profit, min $200, max $1,500, 5 winning days ≥ $200, 90% | ladder also in eval (conservative) |
| 248 | Alpha Futures Advanced 50K | manual | $209/month, reset $189 (own) | target $4,000, EOD $1,750 lock at start, no DLL, 50 micros, 40% eval consistency; 50% of profit, min $1,000, max $15,000, 5 winning days ≥ $200, 90% | — |
| 249 | Alpha Futures Direct 50K | manual | $519 one-time (own) | instant; EOD $2,000 lock at start; DLL $1,000; goals $3,000 then $2,000; 20% consistency; max $2,000; min $500; 90% | — |
| 250 | FuturesElite Prime 50K | manual | [sens] $129 / $229 (reset $109 own) | target $3,000, EOD $2,000 lock +$100, DLL $1,200, 40 micros, no eval consistency; funded goal $500, buffer $2,100, 40% consistency, min $500, caps $2,000→$2,500→$2,800, 90% | cap $2,500 |
| 251 | FuturesElite Nitro 50K | manual | $152 (directory), reset $99 (own) | target $3,000, EOD $2,000, 50% eval consistency, 50 micros; funded lock +$100, buffer $2,100, first payout at +$2,600, min $500, cap $2,000, 90% | funded drawdown is intraday → modelled EOD (optimistic) |
| 252 | FuturesElite Instant 50K (no DLL) | manual | [sens] $199 / $349 | instant; EOD $2,500; ladder 20/30/40 micros at $0/$1,500/$2,500; 6 days ≥ $250; cushion $1,500; caps $2,500 then $3,000; min $500; 100% | — |
| 253 | Blue Guardian Reserve 50K (no DLL) | manual | [sens] $150 / $250 | target $3,000, EOD $2,000 trailing (eval, no lock), 50% eval consistency, 40 micros; funded lock +$100; 50% of profit, cap $2,000, 5 winning days ≥ $150, later payouts need $750 net; 5 payouts then live; 90% | funded scaling ladder not readable → full 40 micros (optimistic) |
| 254 | Blue Guardian Direct 50K | manual | [sens] $299 / $499 | instant; EOD $2,000 lock +$100; DLL $1,250; goals $3,000 then $2,000; 30% consistency (checkout option); no buffer; caps $2,000 then $2,500; 90% | cap $2,000 |
| 255 | Alpha Futures Standard 100K | manual | $239/month, reset $199 (own) | target $6,000, EOD $3,000, DLL $2,000 (qualified), 100 micros, 50% eval / 40% qualified consistency; 50% of profit, min $500, max $4,000 | Topstep 100K ladder used |
| 256 | Alpha Futures Zero 100K | manual | $279/month, reset $249 (own) | target $6,000, EOD $3,000, DLL $2,000, 60 micros; qualified ladder 20→60 micros; 40% consistency; 50% of profit, max $2,500 | ladder also in eval |
| 257 | Alpha Futures Direct 25K | manual | $349 one-time (own) | instant; MLL $1,000; DLL $500; goals $1,500 then $1,000; 20% consistency; max $1,000; min $500; 90% | — |
| 258 | Goat 1-Day Pass 100K | bots | $358 (directory list) | target $6,000, EOD $3,000 lock at start, 60 micros; funded as #245 with caps scaled (modelled $2,500) | caps assumed |
Commands: `uv run python scripts/radar_price_one.py <key> [--delay]`, outputs `docs/jx_runs/radar_price_<key>.txt`.

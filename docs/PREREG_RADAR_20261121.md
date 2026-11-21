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

# PREREG: liquidation shadow test (candidate #100, stage 2) — written 2026-11-21, before any shadow data exists

Question: could a small bot, running our watcher and executor, have fired BEFORE the actual winner on enough Aave v3 liquidations to earn real money after the costs
the earlier test could not see (flash-loan premium, DEX slippage, gas)? Follows `docs/PREREG_LIQUIDATIONS_20261120.md` (registered pass, verdict BUILD in simulate-only mode).
Simulate-only: nothing is sent on-chain, no private key with funds exists, nothing is paid for. The executor contract runs only on local forks inside CI.

## Stage 0: desk check (done now, no data)
- Protocol rules: Aave v3 `liquidationCall` is permissionless; anyone may call it. No platform rule is being evaded. (Verified: public Aave docs/ABI, third-party knowledge; contract behaviour is re-verified by the fork tests.)
- Bot policy: liquidation bots are an intended protocol role (the bonus exists to pay them). No detection or geoblock circumvention is used: only public RPC endpoints and GitHub Actions, as already used for data.
- Malaysia: no check done on legality of operating a liquidation bot from Malaysia; the Aave web front end may restrict some regions but this bot never uses it. Treat as UNVERIFIED legal risk; Jx must decide before any live use.
- Five-part filter: already passed in the #100 verdict (repeatable, long-lived, one setup, capped downside by design, scales by adding chains).

## Stage 1: gate before shadow starts
Fork tests (Foundry, GitHub Actions, one local fork per chain) must pass on each venue before that venue enters the shadow test:
(i) liquidates an artificially unhealthy position (oracle mocked) and leaves profit > 0 in the executor; (ii) reverts when profit < min_profit; (iii) flash loan is repaid
(premium paid) in the success case; (iv) reverts on a healthy position and on an unusable swap route, losing nothing but simulated gas. A venue whose tests cannot be made to pass
is dropped by an addendum (committed before any shadow results) and the GO rules below then apply to the remaining venues; they are not loosened.

## Stage 2: shadow test
- Venues: the Aave v3 main pool on Arbitrum (0x794a…14ad), Base (0xa238…d1c5), Avalanche (0x794a…14ad), Polygon (0x794a…14ad), Optimism (0x794a…14ad). Forks excluded.
- Duration: 4 consecutive weeks (week k = hours 168(k-1) to 168k after `data/shadow/start.json` `start_ts`, set when the first run starts watching all venues). Watching runs in GitHub Actions
  (chained ~5.9-hour jobs, free on a public repo). Watcher uptime per chain is logged; events while a chain was not being watched are EXCLUDED from every denominator and reported as a gap.
- Watcher: tracked borrower set per chain = borrowers from Borrow events in the 180 days before start, plus users liquidated in the 24-month dataset, plus new Borrow events live.
  Each cycle (as fast as the public RPC allows; measured and logged): head block, `getUserAccountData` for the tracked set via Multicall3 (risky tier HF < 1.05 every cycle, all others at least every 60 s).
  First time a user's health factor < 1 is seen, the watcher builds the simulated transaction immediately: debt = largest variable-debt reserve, collateral = largest usable collateral reserve,
  debtToCover = min(close factor x debt, USD 250,000), close factor 50% (100% if HF < 0.95); seized collateral = debtToCover x price_debt / price_collateral x liquidationBonus (capped at the user's collateral balance);
  DEX proceeds from Uniswap v3 QuoterV2 `quoteExactInputSingle` at the current head (best of fee tiers 100/500/3000/10000, direct pair, else via the chain's wrapped native token). Record `N_ready` = head block number read
  right after the simulation finished, and wall time.
- Every actual liquidation on the venue (LiquidationCall logs, scanned continuously) is logged with block B_w, user, assets, amounts, tx sender, and the winner's receipt (gasUsed x effectiveGasPrice + L1 fee).
  Actual bonus USD = collateral amount x oracle price - debt amount x oracle price (Aave oracle, read within seconds of the event).
- Definitions (fixed now):
  * ELIGIBLE liquidation: on one of the five venues, inside watcher uptime, actual bonus > USD 50.
  * FIRE-FIRST: an eligible liquidation whose user has a simulated record with N_ready + 1 < B_w (our transaction could have been included in a block strictly before the winner's), record created after the user's previous liquidation or healthy observation, and simulated net > 0.
    Records are matched to the first liquidation of that user after them; later liquidations of the same user need a new record.
  * SIMULATED NET (USD) for a fire-first event = proceeds from the quote (at the oracle price of the debt asset) - debtToCover x (1 + flash premium) - the winner's actual gas cost (USD, native token at oracle price).
    Flash premium = pool `FLASHLOAN_PREMIUM_TOTAL()`. The winner's gas is deliberately used as our cost (we would have had to outbid it). Events with simulated net <= 0 are not fired (count in neither numerator nor net).
  * Miss reasons are logged: not in tracked set; in set but not seen unhealthy 2+ blocks earlier; simulated net <= 0.
- GO, evaluated after week 4 (all must hold):
  (a) fire-first on >= 10% of eligible liquidations, all venues pooled;
  (b) simulated net >= USD 500 per month across all venues (4-week sum x 30/28);
  (c) simulated net sum positive in at least 3 of the 4 weeks.
- KILLED EARLY: after week 1, if fire-first < 2% of eligible liquidations AND week-1 simulated net < USD 50. Stop and write the verdict. A stage may stop the test early; nothing may declare GO early.
- NO-GO: week 4 completed and GO not met.
- INCONCLUSIVE: fewer than 200 eligible liquidations over the 4 weeks, or any single venue unwatched more than 25% of the time; then extend once by 2 weeks, re-evaluating the same rules on the extended window.
- Latency caveat (stated now, not a rule change): the watcher runs from GitHub Actions with public RPCs, which is slower than a VPS with a paid node. A NO-GO or KILL caused by latency is reported as "latency-limited" together with
  the share of misses where our detection came within 3 blocks of the winner, and the cost of the cheaper faster setup goes under "Action for Jx" in NOTES_JX. The GO rules above are not relaxed by this.
- Weekly: `docs/jx_runs/liq_shadow_week<k>.txt` (from `scripts/liq_shadow_summary.py`) committed with the logs under `data/shadow/`. The final verdict goes in `docs/NOTES_JX.md` "Liquidation shadow test: verdict".
- Costs: none. No keys with funds, no deployment. Any live pilot needs Jx's explicit approval.

## Addendum 1 (2026-11-21, before any shadow data exists): refresh tiers (HOW the watcher polls; no GO/KILL rule changes)
Refreshing every tracked user every 60 s is not feasible on public RPCs (thousands of tracked users). Tiers instead, by last seen health factor: HF < 1.05 every cycle;
1.05–1.2 every 10 s; 1.2–1.5 every 60 s; >= 1.5 every 300 s; users with no debt only after a new Borrow event. A position that falls from HF >= 1.5 to < 1 inside 5 minutes
can be seen late: that is counted as a miss ("in set but not seen unhealthy 2+ blocks earlier"), not excluded. Multicall batches are 60 users, max 600 users per cycle.
The tracked set bootstraps from 180 days of Borrow events; coverage (share of actual liquidated users that were in the set) is reported.

## Addendum 2 (2026-11-21, before any shadow data): Stage 1 fork-test gate result
`contracts/test/LiqExecutor.t.sol` run by `.github/workflows/liq_forktest.yml` (Foundry, local fork per chain, logs `docs/jx_runs/liq_forktest_<chain>_<run>.txt`).
All five venues passed all four tests (profitable liquidation repays the flash loan and leaves profit; reverts below min profit; reverts on a healthy position; reverts on an unusable route)
with one representative collateral/debt pair each: Arbitrum WETH/USDC, Base WETH/USDC, Optimism WETH/USDC, Polygon WETH/native USDC, Avalanche BTC.b/USDC (run 44864998186 for Polygon,
44864424865 for Avalanche, 44863668981 for the others). Pairs that failed for reasons unrelated to the executor logic were swapped for these: Avalanche WAVAX (supply cap full), WETH.e (thin pool),
WBTC.e (frozen reserve); Polygon WMATIC/native USDC (no usable pool), USDC.e debt (frozen), WBTC (thin pool).
What this proves: the executor mechanism on each chain. What it does not prove: that every collateral/debt pair has a usable swap route; the shadow simulation uses the live quote for the actual pair
and a pair with no quote is logged as "sim_no_quote" (a miss). Aave v3.3+ dust rules (full liquidation if debt or collateral < USD 2,000 or HF < 0.95; no leftover < USD 1,000) were found by the tests
(`MustNotLeaveDust`) and are now applied in the simulation (assumed to hold on all five pools; unverified for older pool versions).
All five venues enter the shadow test. No keys with funds, nothing deployed.

## Addendum 3 (2026-11-21 05:30 UTC; no shadow outcome has been looked at; v1 logs were never even committed): watcher v2 (HOW; GO/KILL rules and all definitions unchanged)
The first 40 minutes of the v1 watcher (poll `getUserAccountData` for tiers of ~12,000–38,000 tracked users through public RPCs) showed cycle times of 15–250 seconds (public RPCs throttle and
return errors), which makes "fire first" impossible regardless of the opportunity. Only run statistics were read (cycle time, error counts), no liquidation or detection results. v2 does what a real bot does:
positions (collateral/debt balances per user) are snapshotted once (via `getUserConfiguration` + `getUserReserveData`) and refreshed on that user's Supply/Withdraw/Borrow/Repay/collateral-toggle/liquidation events and a slow
background refresh; every cycle ONE multicall reads all reserve prices and interest indexes, health factors are recomputed locally for every debtor, and only users with local HF < 1.03 are confirmed with
the exact `getUserAccountData` (local HF ignores eMode, which can only make it lower, never higher: no missed liquidations from that approximation). The simulation, matching, definitions and GO/KILL tests are unchanged.
The shadow clock starts when v2 has built the positions for a venue and logs `uptime start ver=2`; v1 uptime, records and events are ignored by `liq_shadow_summary.py`. Positions are cached between runs with
`actions/cache` (not committed). Logs under `data/shadow/` are now actually committed (v1 only committed run logs under `docs/jx_runs/`).

## Addendum 4 (2026-11-21 08:50 UTC; Jx's "addendum 2" request, numbered 4 here because addenda 2 and 3 already exist): crash-month logging, alert, log-only extension
Status of the shadow data at commit time: watching (ver 2) since 05:06–06:10 UTC, so about 2–3 hours per chain (hours watched from `uptime.jsonl`: Arbitrum 3.2, Avalanche 2.2, Polygon 3.1, Optimism 3.1, Base 1.8). Honest disclosure of what has been looked at: no weekly summary and no result beyond the first hours.
`liq_shadow_summary.py` was opened twice during setup, at roughly 1 hour and 2 hours of data, and I quoted the second reading to Jx ("19 eligible, 0 fire-first", explicitly called noise, no decision taken). Nothing else (no fire-first rate for any period longer than those hours) has been seen.
This addendum changes NO existing GO / KILL / NO-GO / INCONCLUSIVE rule, definition, venue, sample or threshold. It only adds logging, an alert and a log-only extension:
- (a) DEBT NEAR THE LINE: once per hour per chain the watcher appends to `data/shadow/<chain>/near_line.jsonl` the number of tracked users and their total debt (USD, at the oracle prices the watcher already reads) with local health factor in [1.00,1.02), [1.02,1.05), [1.05,1.10). Uses the health factors computed every cycle: no extra RPC calls.
- (b) STRESS FLAG, same hourly record: `stress = true` if eligible liquidations (bonus > USD 50) logged in that hour >= 10, OR the chain's wrapped-native oracle price moved >= 5% within the hour ((max − min)/min of the cycle samples).
- (c) UPTIME ALERT: `.github/workflows/liq_alert.yml` runs every 30 minutes; if any enabled chain has had no heartbeat for more than 60 minutes it opens a GitHub issue titled `liq watcher down: <chain>` (GITHUB_TOKEN, issues: write); at most one open issue per chain (deduped by title), closed automatically when the chain is watching again. Heartbeats reach the repo with the 20-minute commits, so an alert can lag up to ~25 minutes; the rule is on the committed heartbeat age.
- (d) LOG-ONLY EXTENSION: after the registered verdict (including any 2-week extension, and also after KILLED EARLY) the watcher keeps running with the same definitions, until a CRASH WINDOW completes or 2027-06-30, whichever is first. CRASH WINDOW = the first rolling 30 days after the verdict date in which gross bonus across the five venues (LiquidationCall logs at Aave oracle prices, all events, field `bonus_usd`) exceeds USD 1,000,000. `scripts/liq_crash_window.py` reports for that window, separately from the registered test: fire-first rate (eligible events, same matching), simulated net (same formula), miss reasons, and the share of misses where a record had `n_ready` within 3 blocks of the winner's block (`B_w − n_ready <= 3`).
  Fixed now for this report only: CRASH-WORTHWHILE if fire-first >= 10% AND simulated net >= USD 2,000 over the window; otherwise CRASH-NOT-WORTHWHILE, annotated "latency-limited" if more than 50% of misses were near-misses. It never overrides the registered verdict and is reported as a separate line in `docs/NOTES_JX.md`.
Why: the 24-month data show income is lumpy (the 5 biggest months paid about 71% of all bonus) and no major crash has happened since SVR went live on Arbitrum/Base in March 2026, so a quiet 4-week test cannot show how a public bot does in the months that pay. The scheduled follow-up sessions are updated so the final verdict does not switch the watcher off.

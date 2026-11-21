# PREREG: liquidation replay, gas bidding and competition by size (candidate #100, follow-up to the shadow test) — written 2026-11-21 before any replay data

Questions (Jx, 2026-11-21): (1) does gas bidding eat the profit; (2) is speed/latency the real limit; (3) who wins big events; (4) do winners act in the same block as the price update (then a bot without co-location can never be first).
The shadow test (`PREREG_LIQ_SHADOW_20261121.md`) answers the fire-first rate live over 4 weeks. This replay answers (2) and (4) from history in hours, and (1) and (3) from data already in the repo. Nothing here changes the shadow GO/KILL rules.

## Stage 0: desk check (web research 2026-11-21; all third-party, unverified unless noted)
- Aave v3 on Arbitrum and Base uses Chainlink SVR (Smart Value Recapture): price updates are first offered in a private Atlas auction so the winning searcher backruns the update with the liquidation; SVR on Ethereum since 2025; Base/Arbitrum adopted March 2026 (LlamaRisk: ~93 unique searchers; recapture ~53% of available value; Aave governance forum, Chainlink docs). Searchers bond ~0.1 ETH (Chainlink docs) and onboard via Chainlink; whether it is permissionless is unverified.
- Avalanche/Polygon/BNB SVR expansion was proposed (outcome not found); Optimism: nothing found.
- Arbitrum replaced Timeboost (200 ms express lane) with priority gas auctions; sources disagree on the date (June vote vs 24 Sep 2026 start): unverified.
- Base orders transactions by priority fee in ~200 ms windows (Base docs).
Implication to test: on SVR chains, liquidations triggered by a price update are won inside the auction (same block as the update), so a public-RPC bot can only compete for slow-trigger events (interest accrual, delayed liquidations).

## Data (free, existing + one Actions fetch)
- Events: `data/public/liq_<chain>.parquet` rows on the five main pools (Arbitrum 0x794a…14ad, Base 0xa238…d1c5, Avalanche/Polygon/Optimism 0x794a…14ad) with bonus > USD 50 (bonus = collateral value − debt value, DefiLlama daily prices, as in `scripts/liquidations_20261120.py`), block time 2026-08-01 .. 2026-10-31 (months 21–23 of the window).
- Replay sample (deterministic): per chain, sort eligible events by (block, tx, user), take every k-th for n = 400 (stage 2) and every 4th of those for n = 100 (stage 1); `scripts/liq_replay_sample_20261121.py` writes `data/public/liq_replay_sample.parquet`.
- Price-update logs: for each sampled event, resolve the collateral and debt asset's Chainlink source from the Aave oracle (`getSourceOfAsset`, read at latest and assumed unchanged since 2026-08-01; assets with an `AssetSourceUpdated` log on the oracle in the window are excluded) then the source's `aggregator()`. An UPDATE = any log emitted by that aggregator address. Fetch `eth_getLogs` on those addresses for [B_w − 10,000, B_w]. Unresolvable feeds (adapters, composite feeds) are excluded and counted.

## Definitions (fixed now)
- GAP G of an event = B_w − (last block <= B_w with an update log from the collateral OR the debt feed), searched in the 10,000 blocks before; none found = G = infinity ("slow trigger"). Using the closer of the two feeds is the conservative choice (smaller G = less reachable).
- NULL: for each sampled event also draw one random block uniformly in the same window (seeded, `numpy.random.default_rng(1)`) and compute G for the same two feeds; this is the share of "gaps <= L" expected by chance.
- Latency L (blocks) for our bot: L_s = median(detect_ms of ver-2 records in `data/shadow/<chain>/unhealthy.jsonl`)/1000 + 1.0 s (assumed network and inclusion delay); L = ceil((L_s + block_time)/block_time). Block times: Arbitrum 0.25 s, others 2 s. IDEAL arm (VPS and private RPC, assumed): L_s = 0.3 s.
- REACHABLE: G > L (including G = infinity). R = reachable share of resolved sampled events; R_value = same weighted by bonus. Also reported: share with G = 0 (same block as an update) and G <= 1.
- Pass logic for this screen (necessary condition, not a sufficient one: it assumes instant detection): 
  * DROP the fast price-triggered-bot hypothesis if, at stage 2, pooled R < 5% AND pooled R_value < 5% in the IDEAL arm (even a perfect watcher cannot reach the shadow GO bar of 10% fire-first).
  * PLAUSIBLE if pooled R >= 10% and R >= 10% on at least 3 of the 5 venues in the IDEAL arm.
  * Otherwise MARGINAL (report which venues have room).
- Stage 1 (pilot, n = 100 per chain): KILL-ONLY at pooled R < 3% (IDEAL arm) AND R_value < 3%: stop, no stage 2. Otherwise run stage 2 with the same rules; the stage-2 rules above are not changed by pilot data.

## Gas bidding and competition by size (existing data, descriptive, no pass/fail)
Eligible events as above but the whole last 12 months (months 12–23), by bonus bucket (50–200, 200–1,000, 1,000–5,000, > 5,000 USD):
- gas share = winner gas USD / bonus USD (median, 90th percentile); share of events whose effective gas price is more than 2x that chain's month-10th-percentile gas price (a bidding proxy);
- unique winners (tx from), top-3 and top-10 shares of bonus by `liquidator` field, share of bonus won by addresses with >= 50 wins on that chain in the 12 months.

## Output
`scripts/liq_replay_20261121.py` → `docs/jx_runs/liq_replay_20261121.txt` (run twice, identical), FIGURES_LEDGER rows, update CANDIDATES #100 row and NOTES_JX.

## Addendum 1 (2026-11-21, before any gap data; only event counts were looked at)
Counting eligible events (bonus > USD 50) per chain showed the last 3 months are quiet: 101 / 109 / 45 / 85 / 7 events (Arbitrum / Base / Avalanche / Polygon / Optimism) in Aug–Oct 2026 versus 4,327 / 2,951 / 2,018 / 2,979 / 762 over the last 12 months,
so a 3-month window cannot give a usable sample. Changes (WHAT is measured; made before seeing any gap result):
- Window is now 2026-04-01 .. 2026-10-31 (months 17–23): 7 months, entirely after the March 2026 SVR adoption votes. Eligible events there: about 900 / 600 / 540 / 700 / 140; the sample is every k-th for n = 400 per chain (all events where fewer than 400 exist).
- Feed source per event: the Aave oracle source IN FORCE at the event block, from `AssetSourceUpdated` logs on the oracle over the window; if an asset has no source update in the window, its latest source is used; if the event precedes the first in-window update for that asset, the event is unresolved (excluded, counted).
Everything else (gap definition, L formula, DROP/PLAUSIBLE/MARGINAL and stage-1 kill rules, descriptive tables) is unchanged. Side finding recorded now: liquidation activity in Aug–Oct 2026 was roughly a tenth of the 12-month average, which matters for income estimates.

## Addendum 2 (2026-11-21, after the stage-1 pilot on 4 of 5 chains; stage-2 rules unchanged except as stated)
Pilot (`docs/jx_runs/liq_replay_20261121_stage1.txt`): pooled ideal-arm R was above the 3% kill line, so stage 2 runs. Two data-quality findings, handled before any stage-2 data:
1. Optimism feed resolution is not credible: for WETH collateral 16 of 19 sampled events show NO update of the resolved ETH feed within the 10,000-block (5.5 h) window, which a liquid price feed does not do. Rule added: a chain is excluded as "feed unresolved" if more than 50% of its resolved events (at least 10) show no update of the collateral feed in the window. Optimism is therefore excluded from the pooled verdict unless a stage-2 re-run passes this check; it is still reported separately. The PLAUSIBLE rule's "3 of 5 venues" becomes "3 of the venues that pass the check" and stays at least 3.
2. The ACTIONS-arm latency L uses the median `detect_ms` of unhealthy records, which is polluted by position-rebuild cycles right after restarts (Avalanche median 574 s). That arm is for information only and has no effect on any verdict, as already stated (verdict rules use the IDEAL arm).
Also recorded: most events resolve only the collateral feed (stablecoin debt feeds usually do not resolve); events are kept when at least one feed resolves, using the closest update of the resolved feed(s). This matches the definition (closer of the two feeds) and is the conservative reading for volatile-collateral events.

## Addendum 3 (2026-11-21 08:50 UTC; stage-2 gap data NOT looked at; only the stage-1 pilot was): descriptive month split
Added before reading any stage-2 result: report R and R_value (IDEAL arm, resolved events, chains passing the feed check) separately for June 2026 (month 19 of the window) and for the other window months (Apr, May, Jul–Oct 2026), per chain and pooled. Descriptive only: it changes no rule, threshold, sample or verdict logic. Reason: Jx's observation that income is concentrated in a few big months, so the replay window's mix of months matters for interpretation.

## Addendum 4 (2026-11-21; stage-2 gap data for Arbitrum, Avalanche, Optimism exists but was NOT opened; Base produced no data): Base endpoint limit
The Base replay job cannot finish: the only Base endpoint with deep history that accepts address-filtered `eth_getLogs` over the needed ranges (Pocket) now rejects ranges above 500 blocks, which makes the oracle-source scan (about 17,000 calls) and every per-event log query fail or crawl. Changes for Base ONLY, made before any Base gap data exists:
- endpoint: Tenderly's Base gateway (accepted 1,000-block spans in the earlier diagnostics);
- the in-force oracle source is NOT scanned over the window: Base uses the oracle's latest source for every event (assumption stated; the SVR feed swap on Base in March 2026 precedes the window start of 2026-04-01, to be checked later if possible);
- the update-log window is 1,000 blocks (about 33 minutes) instead of 10,000. A gap beyond 1,000 blocks is recorded as "no update in window" (counts as reachable, as for every chain); the feed check (more than 50% no-update means exclusion) applies to Base as to the others, so a 33-minute window on a slow feed can exclude Base.
All other chains, definitions and decision rules are unchanged.

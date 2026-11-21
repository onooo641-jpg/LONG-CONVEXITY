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

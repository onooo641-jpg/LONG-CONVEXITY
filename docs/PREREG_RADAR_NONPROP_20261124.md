# Radar expansion: non-prop sources N1–N9 (workstream C) — 2026-11-24

**Why.** Jx asked for the daily radar to cover more areas outside prop firms. Until now its non-prop coverage was DeFi reward pools
(S1), new DeFi protocols (S2), Merkl campaigns (S3), Snapshot governance titles (S4) and ~15 DeFi docs pages. The search so far (≈ 115
tests) says money for small players comes from (i) someone else paying a subsidy, (ii) capped or skill-gated roles, (iii) one-off
dislocations. The new sources watch for exactly those. **A lead is not a verdict**: every lead goes to a desk check, then a staged,
pre-registered test (CLAUDE.md rules). Thresholds below are fixed before the first run and are not tuned after seeing leads.

Code: `scripts/radar_nonprop.py`, called from `scripts/radar.py` (daily Actions job `radar.yml`). Output: `data/radar/leads.parquet`
(history, `first_seen` kept), summary section "Non-prop leads" in `data/radar/latest_summary.md`. Free public sources only, no keys.
Each source runs inside its own error guard; a failed source is reported, never silently skipped.

| Id | Watches | Source (free) | Lead rule (fixed) | Why it can matter |
|---|---|---|---|---|
| N1 | Stablecoin depegs | DefiLlama stablecoins API (prices) | USD-pegged, circulating ≥ $10M, price < 0.985 or > 1.015 | redemption / repeg trades (one-off dislocations) |
| N2 | Extreme perp funding | Hyperliquid `metaAndAssetCtxs` | \|funding\| ≥ 100%/yr annualised and open interest ≥ $2M | hedged carry when it is extreme (most gone since 2024, #323) |
| N3 | Paid-bot role entry: CoW solver payouts | Blockscout: COW sent from the Solver Payouts Safe, last 21 days; DefiLlama COW price | any recipient never paid before (history seeded from #361 data) receiving ≥ $1,000 in the window; plus weekly totals | are newcomers still getting in (#364/#365)? |
| N4 | Security audit contests (protocol-paid prize pools) | Code4rena, Sherlock, Cantina, CodeHawks, Immunefi pages (page watch) | a changed page whose added text shows a prize ≥ $50,000 | skill-gated, protocol-paid income |
| N5 | Governance forums | Discourse RSS: Aave, Compound, Morpho, CoW, Uniswap, Arbitrum, Optimism, Lido, Sky, Balancer, GMX, dYdX | topic first seen in the window whose title matches incentive / reward / liquidation / solver / keeper / relayer / filler / market maker / LP programme / grant / points / competition / subsidy / rebate / bounty / airdrop / retro | new subsidies and bot programmes before they are crowded |
| N6 | New funding rounds | DefiLlama raises API | round in the last 14 days, ≥ $5M, category DEX / derivatives / lending / yield / CDP / liquid staking / bridge / RWA / launchpad | new venues usually launch points / incentives |
| N7 | Perp-venue volume surges | DefiLlama derivatives overview | 24h volume ≥ $20M and 7-day change ≥ +100%, or a venue not seen before with 24h volume ≥ $20M | incentive-driven volume (points seasons) |
| N8 | Malaysia-accessible promotions | page watch: moomoo MY, Webull MY, Rakuten Trade, Luno MY, Tokenize, MX Global | a changed page whose added text mentions RM / $ amounts with bonus / reward / cash / free / promo / campaign | capped per-person subsidies open to a Malaysian resident |
| N9 | Malaysia access changes + paid-bot docs | page watch: SC Malaysia investor alert list, BNM consumer alert list; CoW rewards/onboarding docs, UniswapX, 1inch Fusion, Across relayers, Chainlink Automation, Gelato, Bebop docs; CoW services releases | any change (diff shown) | access/legality changes; rule changes for bot roles |

**What happens to a lead.** The weekly review reads the new leads; each one either gets a one-line dismissal (with reason) in
`docs/NOTES_NONPROP.md` or a Stage 0 desk check and a pre-registered test with a new candidate number (#300+ series continues).
**Limits.** Page-watch sources depend on pages rendering without JavaScript; failures are listed in the summary and fixed by replacing
URLs (a mechanical change). Nothing here is a backtest.

### Addendum 1 (2026-11-24, after the first run; mechanical source repairs, lead thresholds unchanged)
First run (Actions 45330403375): N1, N2, N3, N5 worked (459 stablecoins, 235 perps, 658 CoW payouts to 53 recipients, 12/12 forums).
DefiLlama's raises and derivatives-overview endpoints now return **HTTP 402** (paid). A URL probe (fetch run 45331221932,
`docs/jx_runs/fetch_fallback_45331221932.txt`) found replacements:
- **N6 dropped**: no free source for funding rounds; the radar's S2 flag (new protocols ≤ 30 days, TVL ≥ $1M) still covers new venues.
- **N7**: now CoinGecko `derivatives/exchanges` (free): 24h volume (BTC × DefiLlama BTC price) ≥ $20M and ≥ 2× the level stored 7+ days
  earlier (history builds from today), or a venue new to the list with ≥ $20M. Same thresholds.
- **N4**: Sherlock and Cantina pages are script-rendered (169 / 821 characters), but both have public JSON lists
  (`audits.sherlock.xyz/api/contests`, `cantina.xyz/api/v0/competitions`); a lead is a contest not seen before with prize ≥ $50,000 that
  is not finished. Code4rena and Immunefi stay as page watches. CodeHawks dropped (HTTP 429 to automated requests).
- **N8**: Luno (404 on every candidate URL) and Tokenize (unreachable from GitHub's servers) dropped; HATA and Sinegy (Malaysian exchanges)
  added (unverified until the next run). **N9**: Gelato docs unreachable; homepage watched instead.
- (2026-11-24, second run 45331504230) Sinegy returns HTTP 403 to automated requests: dropped; HATA works. "Not finished" for N4 now
  also excludes judging / escalation / review / results statuses (submissions closed), and the summary prints contest statuses.

### Addendum 2 (2026-11-24, coverage gaps; thresholds unchanged)
Jx asked whether every area is covered. It is not; gaps recorded in `docs/NOTES_NONPROP.md`. Two cheap gaps closed: **N5** adds 11 more
governance forums (Curve, Jupiter, Gnosis, Frax, Across, Ethena, Polygon, zkSync, Scroll, Mantle, Celo; same keyword rule); **N9** adds a
page watch of market-maker / maker-rebate programmes on perp venues (Hyperliquid fees, Aster, Paradex, Orderly, Drift fees, edgeX), any
change reported. Unreachable URLs are reported in source health and fixed or dropped later.

### Addendum 3 (2026-11-24, niche sweep `docs/NICHE_SWEEP_20261124.md`)
N8 (Malaysian broker/exchange promo pages) removed at Jx's request (well known, small). N5 keyword list extended with: prover, operator
program, rebalancer, searcher, OEV. Regulator alert lists (N9) kept as a legality guard.

## Addendum 4 (2026-11-25): N10 and N11, forward logs for the uncharted batch
- **N10, #389 S2c paper log:** each daily run applies the #389 rule unchanged (bid at previous close −15%, fill only on a print ≥ 0.5%
  below, sell at the close, size min($1,500, 1% of the previous day's USD volume), Hyperliquid fees, perps ≥ 30 days old) to every
  live Hyperliquid perp for completed UTC days from **2026-12-01**, appending to `data/radar/wick_paper.parquet`. Running totals print
  under "Source health". The S2c verdict (≥ 60 fills and mean net ≥ 0.5% after 8 weeks, i.e. on 2027-01-26) is read from this file.
- **N11, #385 forward watch:** perps first listed on Hyperliquid in the last 3 days become leads, to be checked by hand for pre-launch
  status and logged as paper shorts per the #385 rule.

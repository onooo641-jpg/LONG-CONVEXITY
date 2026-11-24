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

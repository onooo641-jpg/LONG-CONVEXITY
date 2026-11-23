# #360 Hedged airdrop / points farming, measured after the fact (non-prop; "someone else pays") — 2026-11-23

**Why.** Jx: a non-prop strategy with prop-like profit (prop portfolio ≈ $18K/yr on ≈ $14K of cash at risk, > 100%/yr on cash at risk). Prop
pays because failed customers fund the option; open-market strategies pay 5–15%. The one untested category where a third party (token issuers)
pays early users is airdrop / points farming. Earlier excluded as "no measurable payout schedule" (#319); re-opened here as a retrospective
measurement of what a hedged small farmer actually received. Written before any data is collected.
**Universe.** Token airdrops / points-to-token conversions from 2023-01 to 2026-10 where the issuer published the allocation basis (points per
activity) and the token traded on a liquid venue at the claim date. Sources: the issuers' own docs / blog posts (official pages, fetched by
GitHub Actions), DefiLlama coins for claim-date prices, Hyperliquid / DefiLlama for funding or borrow costs of the hedge.
**Measure per campaign (a "typical small farmer").** Capital C = $10,000; activity = the issuer's main qualifying action at the median documented
level for wallets with allocations ≤ the 90th percentile (no whales, no sybils). Return = (tokens received × claim-date price × 0.9 haircut for
selling) − fees (gas, trading, bridging at documented rates) − hedge cost (perp funding or borrow) over the farming window. Report ROI on C,
annualised over the farming window, and $ per campaign.
**Pass (structural, like the prop flag rule).** Across campaigns, median annualised ROI ≥ 50% AND ≥ 60% of campaigns profitable AND the result
holds when the largest single campaign is removed (no single-airdrop dependence). Stage 1 (kill-only): the first 5 campaigns with complete
data; KILL if the median ROI < 10%.
**Honest limits recorded in advance.** Survivorship: campaigns that paid nothing or rugged must be included (search issuers' docs for programmes
that ended without a token); allocation formulas are often opaque, and when the basis is not published the campaign is "not measurable", not
dropped silently. Malaysia: DeFi front-ends assumed; some airdrops geo-excluded the US only (recorded per campaign). Sybil / multi-wallet farming
is excluded (rule violation at most issuers).
Command: `uv run python -m scripts.airdrop_20261123 | tee docs/jx_runs/airdrop_20261123.txt`.

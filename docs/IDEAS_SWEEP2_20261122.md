# Structural sweep 2: Topstep-shaped and niche mechanisms (#296–#319) — 2026-11-22

Jx: "Topstep isn't just a prop-firm strategy, it's prop-firm *capital recycling*, so find 20+ niche structural mechanisms, each different, with
sub-variations." What makes Topstep work: (1) small fixed cost, losses capped, profits paid out (a cheap option on the strategy); (2) repeatable
(reset and buy again); (3) other people's capital; (4) written rules that can be priced exactly. Each idea below names which of these it has.
Already tested or screened ideas are excluded (CANDIDATES #1–#295, IDEAS_SWEEP_20261121 M1–M40, HANDOFF_NONPROP).
Stage 0 = desk check: rules, bot policy, Malaysia access, five-part filter, free data. **Only "→ test" rows go to a pre-registered test**
(`docs/PREREG_BATCH10_20261122.md`).

| # | mechanism | Topstep traits | sub-variations | Stage 0 |
|---|---|---|---|---|
| 296 | **CFD prop-firm recycling** (friend's NQ trades on US100 CFD accounts) | 1, 2, 3, 4 | FTMO 2-step (fee refunded with first payout), FundedNext Stellar 1-/2-step, The5ers High Stakes, Alpha Capital, Goat Funded Trader CFD, Audacity; static vs trailing loss | → test (official rules being read; recycle.py extended with 2 phases + fee refund) |
| 297 | **Free prop-firm competitions that award funded accounts** | 1 (zero cost), 2 (monthly), 3 | FundedNext monthly competition, others if listed | → test (desk value model: P(top-N) × value of a funded account from #296 pricing) |
| 298 | **Buy evaluations only in sale windows** (40–90% codes) | cost side of 1 | Black Friday / monthly codes for each flagged product | → test (reprice flagged and near-miss products at sale prices; ranking) |
| 299 | Crypto prop recycling (HyroTrader: bots allowed) | 1–4 | 1-/2-step | parked: needs a crypto strategy; the friend's is NQ only |
| 300 | **Stock-perp funding carry** (HL HIP-3 stock perps vs real shares at a broker) | 2, 4 | short perp + long shares when funding > 0; reverse when < 0; per-stock vs basket | → test (funding data in hand; Stage 1) |
| 301 | **Dividend gap on stock perps** (perp tracks price through ex-date; no dividend paid) | 4 | long shares + short perp over ex-dates; 30% US withholding for Malaysians | → test (needs HIP-3 candles + dividend dates) |
| 302 | **Weekend gap on stock perps** (perps trade 24/7, shares do not) | 4 | fade or follow weekend perp moves into Monday open | → test |
| 303 | **Index-addition effect** (forced buying by index funds) | 2, 4 | S&P 500 adds, Nasdaq-100 annual reconstitution, S&P 400/600 promotions | → test (Wikipedia change lists + prices; Stage 1 last 2 years) |
| 304 | **Token-unlock shorts** (scheduled supply, hedged with BTC) | 2, 4 | cliff vs linear, ≥ 1% / ≥ 2% of supply | → test if a free unlock calendar answers (DefiLlama emissions probe); else not testable |
| 305 | **Redemption-floor arbitrage** (permissionless redeemable stablecoins) | 1 (floor), 2 | Liquity LUSD, BOLD, Felix feUSD, others found | → test (DEX price history: discounts below $1 − fee, frequency and size) |
| 306 | **Cooldown discount on yield stables** (sUSDe 7-day unstake etc.) | 1 (floor at redemption value), 2 | sUSDe, others with a cooldown | → test (DEX price vs redemption value) |
| 307 | **Listing-announcement drift with a 1-hour delay** (no speed race) | 2 | Upbit / Bithumb KRW listings; traded on HL perps | → test if Upbit notices answer |
| 308 | **Delisting / warning-designation shorts** (forced selling during notice period) | 2 | Upbit warning designations, delist notices | → test (same data as #307) |
| 309 | SPAC trust-value floor | 1 | units vs shares, pre-deal vs vote | parked: ≈ T-bill + 2–4% (M37), EDGAR data needs a contact e-mail in the user agent (privacy rule) |
| 310 | Closed-end fund / trust discount mean-reversion | 1 | US CEFs, remaining crypto trusts | parked: no free NAV history found |
| 311 | On-chain T-bill tokens trading below NAV (USDY, BUIDL-type) | 1 | redeem at NAV | parked: redemption needs KYC/whitelisting |
| 312 | Hyperliquid spot-ticker deployment auctions | 2 | buy cheap tickers, resell | parked: resale market illiquid, no price history |
| 313 | Prop-firm "pay after you pass" / free-reset promos | cost side of 1 | per firm | folded into #298 (pricing variants) |
| 314 | Index perp vs CME futures basis (HIP-3 US500 vs ES) | 2, 4 | US500, USTECH vs NQ | → test with #300 data (subvariant: index names only) |
| 315 | Prediction-market near-certain outcomes (97–99¢) | 1, 2 | Polymarket | excluded: gambling-law grey in Malaysia; Polymarket blocked from US data runners |
| 316 | Lead-trader / vault-leader fees (others' capital; 10% of profits) | 3 | HL vault leader, eToro Popular Investor | excluded: depends on marketing (creativity rule); friend's trades lose on own money (#58) |
| 317 | CEX launchpools / earn promos | 1, 2 | Binance, Bybit, OKX | excluded: Malaysia gate (SC orders), as M16 |
| 318 | Options expiry pinning / CME roll dislocation | 4 | NQ/ES rolls | parked: per-contract futures/options data paid |
| 319 | Restaking / points-to-token conversions | 1 | various | excluded: no measurable payout schedule |

**Count:** 24 mechanisms; 14 go to a test (#296, #297, #298, #300–#308, #314, with #304/#307/#308 conditional on data); 6 parked with
a reason; 4 excluded by standing rules.

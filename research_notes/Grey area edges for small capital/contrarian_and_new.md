# Grey-area edges for small capital (USD 10–15K): contrarian evidence and a 2025–2026 mechanism sweep

Scope note for the report writer: the target is ">100%/yr on USD 10–15K", i.e. at least USD 10–15K/yr net, legally and within written terms, from Malaysia. Searches ran on 2026-11-28. Direct page fetches to arxiv.org, financemagnates.com, tradingview.com and coingape.com were blocked by this session's network, so several figures below come from search-result summaries of those pages, not from reading the full text. Each such item is marked "(snippet)". Figures from snippets should be re-checked before they go into a final number.

Cross-reference with the repo (verified by grep of `docs/CANDIDATES.md`): HIP-3 ideas already tested and failed: #284 (cross-dex funding gaps), #300 (stock-perp funding carry), #314 (index-perp carry), #510 (wick bids on HIP-3), #614 (pre-IPO perp gaps), #655 (oracle lag). Crypto prop firms and exchange trading competitions were dismissed at desk in #377–#381 (`docs/NICHE_SWEEP_20261124.md`: manual-only or Bybit geoblock; prizes $10–50K).

## Key Question 1: What does rigorous evidence say about profit concentration (MEV, airdrops, prop payouts, retail trading) and survivorship bias?

### Takeaway
Every venue with good data shows the same thing: a small number of vertically integrated or specialised players take most of the profit, and the median retail participant loses or earns little. MEV goes mostly to validators and builder-linked searchers. Airdrop tokens mostly fall after launch. About 2–7% of prop-challenge buyers ever get a payout, with average payouts around USD 1–2K. "I made $X" stories come from the small group of winners, and nobody counts the people who lost.

### Cited Findings
**MEV (2023–2025 data)**
- CEX-DEX arbitrage on Ethereum, Aug 2023–Mar 2025: an estimated USD 233.8M extracted by **19 major searchers** across 7,203,560 arbitrages. Searchers tied exclusively to one builder keep low margins and pass most revenue to that builder, "sometimes even operating at negative net profit". Searchers spread across many builders keep more. (snippet) — [Wu, Sui, Thiery, Pai, AFT 2025 / arXiv 2507.13023](https://drops.dagstuhl.de/storage/00lipics/lipics-vol354-aft2025/html/LIPIcs.AFT.2025.26/LIPIcs.AFT.2025.26.html)
- Over USD 233.8M / 19 months ≈ USD 148M/yr shared among 19 searchers, and the main cost is the builder's cut. (Arithmetic on the figure above.) — [arXiv 2507.13023](https://arxiv.org/html/2507.13023v3)
- Theory with empirical checks: the validator's share of MEV rises as searcher competition rises, and "the majority of the total observable MEV is captured by validators". (snippet) — [Mamageishvili, Schlegel, Sudakov, Sui, arXiv 2407.07474](https://arxiv.org/html/2407.07474v2)
- Builder concentration: three builders produced about 80% of Ethereum blocks between Oct 2023 and Mar 2024. Of the dominant builders (beaverbuild, Titan, rsync), two run their own CEX-DEX searchers. (snippet; older evidence, 2023–24) — [arXiv 2507.13023](https://arxiv.org/pdf/2507.13023)
- BNB Smart Chain, May–Nov 2025: within months two builders (48Club, Blockrazor) produced over 96% of blocks and took about 92% of MEV profits. (snippet) — [arXiv 2602.15395](https://www.arxiv.org/pdf/2602.15395)
- At the contract level, a small group of top-tier contracts earns over 60% of realised MEV profit. One tier of nine contracts holds about 62%. (snippet; study date and method not confirmed) — [arXiv 2608.05011](https://arxiv.org/pdf/2608.05011)

**Airdrops / points (2023–2025 data)**
- In nine major airdrops, recipients sold most of their tokens on exchanges soon after receiving them, up to 95%. One Sybil-farmed campaign (Gemstone) gave 99.53% of supply to Sybils. (snippet; paper revised July 2025) — [Messias, Yaish, Livshits, arXiv 2312.02752](https://arxiv.org/html/2312.02752v4)
- Hunter-group economics on Hop and LayerZero: many groups made positive net profits and others did not cover their costs. (snippet) — [arXiv 2503.14316](https://ar5iv.labs.arxiv.org/html/2503.14316)
- Of 118 token launches (TGEs) in 2025, 84.7% traded below their launch valuation (Memento Research, as reported). (snippet) — [Cointelegraph](https://cointelegraph.com/news/crypto-airdrops-token-failure-utility-distribution)
- 88% of airdropped tokens lose value within 3 months. (headline; older, 2024) — [DappRadar](https://dappradar.com/blog/88-of-airdropped-tokens-lose-value-within-3-month)
- PANews's 2025 year-end review says airdrop-farming returns in 2025 were "far from ideal". Insider allocations rose, with some projects keeping 40%+ for team and VCs. (snippet) — [PANews via HTX](https://www.htx.com/news/panews-crypto-year-end-review-did-your-2025-airdrop-harvesti-3MBKp1do/)

**Prop firms (2024–2026 data)**
- FPFX Tech analysis of 300,000+ accounts: 14% pass a challenge and 7% ever reach a payout. (snippet) — [Finance Magnates via TradingView](https://www.tradingview.com/news/financemagnates%3A3a251e333094b%3A0-exclusive-only-7-of-300-000-prop-trading-accounts-achieved-payouts/)
- The Funded Trader's internal data implied about 20% of those who pass get any payout, so about 1% of all clients make money. This is a single firm. (snippet) — [Finance Magnates](https://www.financemagnates.com/forex/prop-firm-the-funded-trader-paid-traders-386k-in-march-could-have-earned-3x-more/)
- Goat Funded Trader: USD 26M paid to 22,279 of 1.2M traders. That is 1.9% of traders, averaging about USD 1,167 per paid trader. (headline + arithmetic) — [Finance Magnates](https://www.financemagnates.com/forex/prop-firm-goat-funded-trader-says-it-paid-26-million-to-22279-of-12-million-traders/)
- FundedNext: USD 15.19M paid to 8,340 traders in February, about USD 1,821 each. (headline + arithmetic) — [Finance Magnates](https://www.financemagnates.com/forex/analysis/prop-firm-fundednext-says-it-paid-1519m-to-8340-traders-in-february/amp)
- Prop Firm Match tracked about USD 325M in payouts across the industry in 2025. FTMO and The5ers are not included, and the figures are self-reported by firms. (snippet) — [Finance Magnates](https://financemagnates.com/forex/prop-firm-match-tracked-about-325-million-in-payouts-to-traders-in-2025)
- Crypto-settled prop payouts doubled to USD 115M in Q1 2026, but growth has stalled since December 2025. (headline) — [Finance Magnates](https://www.financemagnates.com/forex/analysis/prop-firm-crypto-payouts-doubled-to-115-million-in-q1-2026-but-growth-has-stalled-since-december/)

**Retail trading outcomes (older baselines)**
- 74–89% of EU retail CFD accounts typically lose money (national regulators' analysis; this is the basis for the mandatory risk warning). (2018, older) — [ESMA decision, via CONSOB](https://www.consob.it/documents/1912911/1970971/esma35_43_1000.pdf/6dc9bc30-c528-09dc-9430-398c8df4c3af)
- Broker-level loss rates such as 82% at Plus500 and 62% at Interactive Brokers come from a third-party compilation and are not verified against broker disclosures. — [Hyperdash](https://hyperdash.com/learn/why-cfd-traders-lose-money-is-the-game-rigged)
- BIS: an estimated 73–81% of retail crypto-app users in 95 countries likely lost money on their initial bitcoin investment. The median investor lost USD 431 of USD 900 invested by Dec 2022. The estimate assumes USD 100/month purchases from the month of app download. (2022–23, older) — [BIS WP 1049](https://www.bis.org/publ/work1049.pdf); [BIS Bulletin 69](https://www.bis.org/publ/bisbull69.htm)

**Limits to arbitrage (theory)**
- Arbitrage is done by a small number of specialists using other people's capital, and arbitrage capacity can fail exactly when mispricing is largest. (1997, older) — [Shleifer & Vishny, NBER w5167](https://nber.org/papers/w5167)
- "Statistical limits of arbitrage": alphas have to be estimated from limited history, so even real anomalies are hard to exploit with confidence. — [Da, Nagel, Xiu, BFI WP 2024-135](https://bfi.uchicago.edu/wp-content/uploads/2024/10/BFI_WP_2024-135.pdf)

### Inferences
- Over 2023–2025 the profit pool in MEV has moved toward validators and builders. The independent small searcher sits at the bottom of the pecking order, and even builder-linked searchers sometimes run at a loss. A USD 10–15K newcomer does not have the order flow or the builder relationship that the profit depends on.
- Prop-firm economics: if 2–7% of buyers get paid and the average payout is about USD 1.2–1.8K, then the funded traders who make more than USD 15K/yr are a small fraction of that 2–7%. Public "payout certificate" posts come from this tail. This matches the repo's own finding that Topstep recycling works only because of a specific tested strategy, not because of the business model.
- Survivorship bias, structurally: every dataset above (airdrops, prop, CFD, BIS) has a loss-making majority, and the winners are the only ones who post. No source gives a per-participant distribution, such as a Gini or top-1% share, for airdrops or prop payouts. Concentration has to be inferred from pass and payout rates.
- Limits-to-arbitrage theory explains why small-capacity anomalies can exist: large funds cannot be bothered with them. But the repo's 600+ tests (CANDIDATES.md) show that in practice the crypto small-capacity niches are already taken by bots, and the remaining edge is too small to matter.

### Gaps
- No rigorous source found giving the top-1%/top-10% share of airdrop value or of prop-firm payout dollars. Only pass and payout rates are public.
- The full text of arXiv 2507.13023 was not readable, because arxiv.org is blocked in this session. A per-searcher profit split is not confirmed.
- No 2025–2026 regulator update of the ESMA 74–89% figure was found. ASIC REP 828 (Jan 2026) appeared in the results but was not read.

## Key Question 2: Which new 2025–2026 mechanisms have published numbers suggesting a small player could earn >USD 15K/yr legally? Who pays, and is it repeatable?

### Takeaway
None found. Every 2025–2026 subsidy mechanism with published numbers pays either a fixed percentage on balance (USDC rewards about 4–5%, Kraken xStocks up to 1%, government paper about 3.5%), or a one-off capped bonus, or rewards concentrated on one deployer or one early cohort (HIP-3, Virtuals Genesis). On USD 15K, the balance-based programs pay roughly USD 150–750/yr. The only items with headline figures above 100% (Virtuals Genesis x4–x128, Bybit 200% APR) are peak or best-case numbers from promotional sources, and both decayed or ended.

### Cited Findings
**Stablecoin issuer/distributor rewards**
- Late 2025: Coinbase paid about 4% and Kraken about 5% annual rewards on USDC. Coinbase calls it a loyalty program it funds itself, and says it may change or end it. (snippet) — [Decrypt](https://decrypt.co/333472/coinbase-paypal-stablecoin-rewards-genius-prohibitions-how?amp=1)
- Who pays: the GENIUS Act bars issuers from paying yield, but exchanges and distributors pay "rewards" funded by their revenue share from Circle's reserve interest. PayPal pays rewards on PYUSD through a third-party issuer arrangement (rate not found). — [Decrypt](https://decrypt.co/333472/coinbase-paypal-stablecoin-rewards-genius-prohibitions-how?amp=1)
- Regulatory risk: an OCC proposal on 25 Feb 2026 would restrict third-party yield arrangements. A May 2026 CLARITY Act deal would ban paying stablecoin interest to US customers but keep activity-based rewards. One later (Sept 2026) report says CLARITY failed to advance over rewards disputes. Status is unresolved. — [Decrypt (OCC)](https://decrypt.co/359506/banking-occ-new-stablecoin-yield-rules-coinbase); [The Block (May 2026 deal)](https://www.theblock.co/news/regulation/2026-05-02-coinbase-says-deal-reached-on-clarity-act-stablecoin-yield-clearing-path-to-long-stalled-senate-markup-399780)

**Tokenized stocks / RWA promotions**
- Bybit xStocks campaign (July–15 Aug 2025): 150,000 USDT prize pool (100K Token Splash) and "up to 200% APR" Easy Earn staking. Ended. 200% is the headline maximum on a capped promotional tier. — [Bybit press release](https://www.bybit.com/en/press/post/bybit-amplifies-xstocks-offerings-with-150-000-usdt-prize-pool-campaign-blt777be30c71be06c9)
- Kraken xStocks First Trade Bonus (23 Jul–31 Aug 2025): one-off USDG reward for a first trade of USD 100 or more, Tier 3 KYC required. Kraken Meta xStocks incentive from 1 Dec 2025 needs at least USD 50 of xStock trades. — [Kraken rules](https://www.kraken.com/xstocks-first-trade-bonus-rules); [Kraken Meta incentive](https://www.kraken.com/legal/meta-xstocks-incentive)
- Kraken Opt-In Rewards: up to 1% on xStocks held (ongoing). — [Kraken blog](https://blog.kraken.com/product/xstocks/introducing-opt-in-rewards)

**New exchange types: Hyperliquid HIP-3 (Oct 2025 onward)**
- Deploying a market requires staking 500,000 HYPE. HIP-3 markets charge twice the validator-perp fee, and the deployer keeps 50%. Deployers can set an extra fee share of 0–300%. — [Hyperliquid docs](https://hyperliquid.gitbook.io/Hyperliquid-docs/hyperliquid-improvement-proposals-hips/hip-3-builder-deployed-perpetuals); [Sacra](https://sacra.com/chat/h/ece0f836-9f12-400d-b703-5ff30572e80f/)
- "Growth mode" (Nov 2025) cuts all-in taker fees on new markets by over 90%, with settings locked for 30 days. — [FXStreet](https://www.fxstreet.com/cryptocurrencies/news/hyperliquid-unveils-hip-3-growth-mode-slashing-fees-by-90-to-boost-new-markets-202511191148); [The Defiant](https://thedefiant.io/news/blockchains/hyperliquid-to-roll-out-growth-mode-to-supercharge-new-markets)
- Concentration: one deployer (trade.xyz) reportedly has about 98% of HIP-3 volume (92 markets in 8 months). Builder markets reached over USD 62B in monthly volume, about 51.8% of exchange volume on one measured day (dates unclear). — [KuCoin flash](https://www.kucoin.com/news/flash/trade-xyz-builds-92-markets-and-98-hip-3-volume-on-hyperliquid-in-8-months); [The Defiant](https://thedefiant.io/news/defi/builder-deployed-markets-overtake-crypto-on-hyperliquid)

**AI-agent token launchpads (Virtuals Genesis, 2025)**
- May 2025: about 24 Genesis launches showed peak returns of x4–x128, average x32. These are peak multiples, not realised returns, and the source is promotional in tone. — [TechFlow](https://techflowpost.com/en-US/article/25779)
- Rules: taking profit triggers a points cooldown. Since May 2025, moving assets between wallets to dodge the cooldown triggers cooldowns on linked wallets. — [TechFlow](https://techflowpost.com/en-US/article/25885); [DWF Labs analysis](https://www.dwf-labs.com/research/552-virtuals-protocol-genesis-mechanism-analysis)
- No audited dataset of per-participant net returns after cooldowns. Returns rise with oversubscription, which is a sign of crowding. — [Alea Research](https://alearesearch.substack.com/p/virtual-genesis-virtuals-agent-launchpad)

**Government / central-bank programs (Malaysia)**
- Primary Malaysian government sukuk issuance is institutional-only. Retail can buy only through secondary or exchange-traded routes. Government yields are about 3.5% in 2026 versus 1.85–2.10% for 12-month fixed deposits. The BNM OPR is 2.75% (cut July 2025). (secondary guide) — [malaysia4u guide](https://malaysia4u.com/bonds-sukuk-guide)
- Budget 2027 announced a tokenised retail savings sukuk. No rate or launch date has been published. — [The Edge Malaysia](https://theedgemalaysia.com/node/821203); [Bernama](https://www.bernama.com/en/news.php/?id=2629701)

### Inferences
- Balance-based rewards (USDC rewards, xStocks opt-in, sukuk) are capped near the risk-free rate because the payer funds them from reserve interest. On USD 15K they pay about USD 150–750/yr, 30–100× short of the target. Being "grey" adds nothing here: the subsidy is simply a share of T-bill interest.
- Who pays for venue launch incentives: the venue's marketing budget or its token holders. Rewards end once volume targets are met (the Bybit and Kraken campaigns lasted about 5–6 weeks). They are repeatable only by moving from one new campaign to the next, which the repo already tested as "broker bonuses / incentive rotation" (small or failed).
- HIP-3 growth mode subsidises traders through lower fees. It does not pay passive capital. The economic rent goes to the deployer, who needs 500K HYPE staked (far above USD 15K), and one deployer has about 98% of volume. The trading angles a small player could use were already tested in the repo and failed (#284, #300, #314, #510, #614, #655).
- Virtuals Genesis is the only 2025 item with published returns far above 100%, but those are peak multiples on early launches in a hot AI-agent market. The setup selects for crowding (returns track oversubscription), the cooldown rules penalise taking profit, and the repo's tests of "token sales / LBPs / memecoin graduation / points farming" already found this class decayed. There is no new evidence that it survives into 2026.
- Overall: no 2025–2026 mechanism found where a single, rules-compliant USD 10–15K participant has published, verified evidence of earning more than USD 15K/yr repeatably. The prop-firm route (already in the repo) remains the only one with a tested positive figure: USD 3,689/yr corrected Topstep, per CLAUDE.md.

### Gaps
- Current (Nov 2026) Coinbase/Kraken USDC reward rates were not confirmed. The PYUSD reward rate was not found.
- No 2025–2026 data was found on new-exchange liquidity-provider/maker rebate programs open to small accounts. Maker rebates usually need top VIP tiers, but this is assumed, not sourced.
- No 2025–2026 data was found on restaking "points 2.0" or new instant-funding/crypto-prop payout distributions beyond the aggregate figures in Q1.
- No numbers found on copy-trading lead-trader profit share for traders who do no marketing.

## Key Question 3: Per candidate — Malaysia legality, within written terms, realistic profit (verified vs anecdotal), capital/time, risks, free data

### Takeaway
No candidate meets the bar. The closest thing to "grey but legal" is stacking the USDC/xStock rewards and launch promotions on exchanges that serve Malaysia, but these add up to hundreds, not tens of thousands, of USD per year. The rest are either excluded (geoblock, Sybil, gambling) or already tested in the repo.

### Cited Findings
| Candidate | Malaysia access / legality | Within terms? | Realistic profit on USD 15K | Evidence grade | Capital / time | Main risks | Free data |
|---|---|---|---|---|---|---|---|
| USDC rewards (Coinbase ~4%, Kraken ~5%, late 2025) | Not confirmed whether Malaysian residents are eligible (gap). Coinbase/Kraken status on the Securities Commission Malaysia registered-exchange list not checked | Yes. Program terms let the firm change or end it — [Decrypt](https://decrypt.co/333472/coinbase-paypal-stablecoin-rewards-genius-prohibitions-how?amp=1) | ~USD 600–750/yr | Rates from press (snippet), not from the program page | USD 15K, near-zero time | Rule change (OCC Feb 2026 proposal), exchange counterparty risk | Exchange rate pages only |
| Kraken xStocks opt-in rewards / first-trade bonus | xStocks are restricted in some regions; Malaysia availability not confirmed (gap) | Yes, but one bonus per client (Sybil excluded) — [Kraken rules](https://www.kraken.com/xstocks-first-trade-bonus-rules) | ≤1% on holdings (~USD 150) + one-off bonus | Official terms (verified) | Small | Tokenised-stock custody/issuer risk | Kraken legal pages |
| Bybit xStocks campaigns (up to 200% APR, 2025) | Bybit is geoblocked for Malaysia per the repo's #377 desk check. Using it would mean geoblock evasion → **excluded** | n/a | n/a | Press release (verified as headline) — [Bybit](https://www.bybit.com/en/press/post/bybit-amplifies-xstocks-offerings-with-150-000-usdt-prize-pool-campaign-blt777be30c71be06c9) | — | — | — |
| HIP-3 growth-mode markets | Hyperliquid is permissionless; the repo already trades its data | Yes | Repo tests: negative or faded (#284, #300, #314, #510, #614) | Repo-verified | Deployer role needs 500K HYPE → out of reach — [HL docs](https://hyperliquid.gitbook.io/Hyperliquid-docs/hyperliquid-improvement-proposals-hips/hip-3-builder-deployed-perpetuals) | Deployer-set oracles, 98% single-deployer concentration | Hyperliquid API (already in `data/public`) |
| Virtuals Genesis points | Crypto launchpad; no Malaysia-specific ruling found | Yes if one wallet. Linked-wallet cooldowns enforced — [TechFlow](https://techflowpost.com/en-US/article/25885) | Unknown. Peak x4–x128 (May 2025) is anecdotal and not realised | Promotional / anecdotal | Points accrue from holding/staking VIRTUAL, so capital is at token-price risk | Token crash (84.7% of 2025 TGEs below launch value — [Cointelegraph](https://cointelegraph.com/news/crypto-airdrops-token-failure-utility-distribution)) | On-chain (Base) data, no API checked |
| Malaysian govt sukuk / tokenised retail sukuk | Legal, onshore | Yes | ~3.5% ≈ USD 525/yr | Secondary guide — [malaysia4u](https://malaysia4u.com/bonds-sukuk-guide) | Low | Rate cuts | BNM / Bond Info Hub |
| Prop-firm recycling (benchmark) | Already used by Jx | Yes (repo audited) | USD 3,689/yr corrected Topstep | Repo-verified (CLAUDE.md) | Fees only | Strategy decay | Repo |

**Excluded categories (with reason)**
- Sybil / multiple accounts, fake identities, prohibited self-referral: breaches platform terms. Linked-wallet detection is now explicit, e.g. Virtuals' May 2025 rule — [TechFlow](https://techflowpost.com/en-US/article/25885).
- KYC / geoblock / VPN evasion: forbidden by the repo rules. Bybit is excluded for Malaysia on this basis.
- Bot-detection evasion, wash trading, spoofing, pump groups, sandwich attacks, oracle pushing: market manipulation, and the repo rules forbid it.
- Gambling and prediction markets: illegal in Malaysia (repo standing rule). Prediction-like perps are excluded by the brief.
- Copy-trading lead-trader share that needs follower marketing, and other creative/marketing businesses: excluded by the brief.

### Inferences
- The contrarian reading holds: where good data exists, profits go to a concentrated set of capitalised or vertically integrated players. New 2025–2026 subsidies are funded from reserve interest or marketing budgets, which caps them near the risk-free rate or makes them one-off. No legal, within-terms mechanism found turns USD 10–15K into USD 15K/yr with verified evidence.
- The only mechanism with tested positive economics is still prop-firm recycling with a tested strategy, because the firm's fee-funded payout pool is the "subsidy" and the strategy, not the rules gap, is the edge.
- If any new 2025–2026 item deserves a cheap Stage 0/1 check, the best candidate is a desk check of which USDC/xStock reward programs Malaysian residents can legally use. Expected value is about USD 0.5–1K/yr, so it is a cash-management upgrade, not an edge.

### Gaps
- Malaysian eligibility for Coinbase/Kraken rewards and xStocks was not verified. This needs the SC Malaysia registered DAX operator list and each firm's regional terms.
- Virtuals Genesis realised-return data for late 2025–2026 was not found. Measuring it would need on-chain Base data, and a free API was not checked.
- Network blocks (arxiv.org, financemagnates.com, tradingview.com, coingape.com) stopped the full-text checks of the MEV and prop-firm figures. Re-fetch these via the repo's GitHub Actions fetch workflow if exact numbers are needed.

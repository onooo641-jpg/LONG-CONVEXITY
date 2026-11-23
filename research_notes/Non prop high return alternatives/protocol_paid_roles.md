# Protocol-paid automation roles in DeFi (solvers, fillers, relayers, keepers, oracle publishers, MEV on small chains), 2024–2026

*Research date 2026-11-23. Method and verification level: direct page fetches to docs.cow.fi, forum.cow.fi,
business.1inch.com and docs.uma.xyz failed (hosts are outside this sandbox's network allowlist), so every finding
below comes from web-search result snippets that quote or summarise the linked page. Treat all figures as
"third-party summary of the cited page", not as page-read verified. Where sources disagree it is noted.
Target being tested: a small operator with USD 10–15K capital earning USD 15–20K/yr (>100%/yr). Repo benchmark:
Topstep recycling USD 4,097/yr. Prior repo verdict: `docs/IDEAS_SWEEP_20261121.md` rows M9–M11 (solvers "Stage 0 FAIL
F4/F5", oracle push "parked") were marked unverified; this note supplies the evidence.*

## 1. For each role: who pays, reward formula/budget, operator count, concentration, barriers, capital, realistic income for a new small operator

### Takeaway
No role found has evidence that a new small operator with USD 10–15K earns USD 15–20K/yr. The roles that are
open (Across relaying, UniswapX open-auction filling, deBridge DLN taking, Keep3r, MEV backrunning) are races that a
few professional firms win, or they pay very little (UMA proposals, Keep3r). The role with the most protocol money
and no inventory need, CoW Protocol solving, needs either a large bond (about USD 85K or more even on the reduced
route) or KYC plus core-team approval through the CoW DAO pool. Its reward pool is about USD 3.7M/yr at 2026 COW
prices, and about half goes to one team. Pyth publishing, Chainlink Automation, 1inch Fusion resolving, UniswapX
quoting and Polymarket UMA proposing are permissioned or whitelisted.

### Cited Findings

**CoW Protocol solvers (intent/batch-auction solvers; paid by CoW DAO in COW from protocol fees)**
- Rewards are paid weekly in COW (currently every Tuesday). The rules come from CIPs 20, 36, 38, 48, 57, 67, 74, 85 and 87 — [CoW docs: Solver rewards](https://docs.cow.fi/cow-protocol/reference/core/auctions/rewards)
- Current formula (CIP-74): performance reward = total score − reference score − missing score, clipped by cap(x)=max(−c_l, min(c_u, x)). The upper cap c_u is a chain-specific fraction β of the protocol fee (excluding partner fees) on the solver's executed trades in that auction. The lower cap comes from penalty caps on orders won but not settled — [CoW docs: Solver rewards](https://docs.cow.fi/cow-protocol/reference/core/auctions/rewards); [CIP-74 forum thread](https://forum.cow.fi/t/cip-74-align-solver-rewards-with-protocol-revenue-and-introduce-a-volume-based-fee/3234)
- CIP-74 took effect around 2025-12-08. It replaced the fixed per-auction cap (about 0.01–0.012 ETH; sources differ) with a cap tied to revenue, and added an unconditional volume fee of about 2 bps — [arXiv 2607.21955](https://arxiv.org/abs/2607.21955); [CIP-Draft: Align Solver Rewards with Protocol Revenue](https://forum.cow.fi/t/cip-draft-align-solver-rewards-with-protocol-revenue/3174)
- An earlier draft proposed a cap of 150,000 COW per solver per week. Its simulation put total weekly solver rewards at about 502k COW under the old system and about 863k COW under a capped hybrid. Whether that weekly cap is in force now is unconfirmed — [CIP-Draft: Align Solver Rewards](https://forum.cow.fi/t/cip-draft-align-solver-rewards-with-protocol-revenue/3174)
- A forum thread is titled "Second price auction is broken for small orders since CIP-74", which suggests problems with how rewards work on small orders — [CoW forum](https://forum.cow.fi/t/second-price-auction-is-broken-for-small-orders-since-cip-74/3317)
- Total budget (third party, on-chain): from 2026-01-01 to 2026-09-14 the CoW rewards safe paid solvers about 36.8M COW (≈ USD 2.6M) on USD 23.3B of settled volume. The count includes COW transfers and ETH gas refunds but not trading surplus, and solver names are Bitquery's attribution — [Bitquery investigation](https://bitquery.io/investigations/cow-swap-solver-auctions)
- A search summary of the same Bitquery piece said 52% of COW paid for winning went to one team. A second search could not confirm this figure — [Bitquery](https://bitquery.io/investigations/cow-swap-solver-auctions) (unconfirmed)
- Blockworks reported "Barter buys rival solver codebase to expand CoW Swap dominance", i.e. consolidation among top solvers (headline only; date not seen) — [Blockworks](https://blockworks.co/news/barter-buys-rival-solver-codebase)
- Bonding. CIP-44 (May 2024) allows a reduced "sub-bond" of USD 50K in yield-bearing stables or ETH plus 500K COW, ramping to a target of USD 100K plus 1M COW. A solver in a reduced pool is still vouched for by the CoW DAO pool, and the core team can reject it — [CIP-44](https://forum.cow.fi/t/cip-44-reduced-bonding-requirements/2424); [CoW docs: bonding pools](https://docs.cow.fi/cow-protocol/reference/core/auctions/bonding-pools)
- A full own bonding pool is USD 500K (cUSDC) plus 1.5M COW. This comes from a third-party summary, so it may be outdated — [BRRR DAO via search summary](https://brrrdao.substack.com/p/cow-protocol-part-2-cow-solver-economy)
- A draft dated 2026-05-16 proposes reduced pools of USD 200K in stables or ETH, or USD 100K plus 0.5M COW. It also proposes a 15% service fee on COW rewards after six months in the DAO pool. It is a draft; the outcome is not confirmed — [CIP-Draft: Simplifying the CoW DAO bonding pool](https://forum.cow.fi/t/cip-draft-simplifying-the-operations-of-the-cow-dao-bonding-pool/3455)
- CIP-48 (2024) added a service fee for pool solvers, waived for the first three months in a reduced pool — [Goverland CIP-48](https://gl.app/dao/cow.eth/proposals/0x563ab9a66265ad72c47a8e55f620f927685dd07d4d49f6d1812905c683f05805)
- Onboarding: "no prerequisites (other than KYC if joining the CoW DAO bonding pool)". Solvers first run in a "shadow" competition on live order flow without settling (Arbitrum and mainnet), then staging, then an onboarding call — [CoW docs: onboard](https://cowswap.mintlify.app/cow-protocol/howto/solvers/onboard)
- Operator count and concentration: 28 solvers were active in Jan–Apr 2025. Only 12 had more than 1% of volume, and 3 had more than 50% (industry blog) — [Sprinter blog](http://blog.sprinter.tech/building-economic-trust-in-solver-based-networks-part-2/)
- Academic (Aug 2023–Feb 2025): CoW was the least concentrated of three intent DEXs, with the top solver at about 25% share — [arXiv 2503.00738 "Execution Welfare Across Solver-based DEXes"](https://arxiv.org/html/2503.00738v2)
- After CIP-74, volume-weighted HHI rose from 0.176 to 0.241, mainly because of the incumbent top solver. Concentration fell for small orders and rose for large ones, and count-based HHI fell (about −0.060). The sample is 395 days of daily solver shares, 2025-03-01 to 2026-03-30 (preprint) — [arXiv 2607.21955](https://arxiv.org/abs/2607.21955)
- Cost side: some solvers say rewards on small trades sometimes fall below operating overhead (secondary source) — [Blockchain Dose](https://blockchaindose.com/cow-protocol-and-anoma/)

**UniswapX fillers (paid by order flow: the spread between user limit and execution; no protocol subsidy found)**
- There is one permissioned role, the quoter (vetted by Uniswap Labs), and one permissionless role, the filler. The RFQ winner gets about 24 s (2 blocks) of exclusivity on mainnet, then the order goes to an open Dutch auction. Non-exclusive fillers can override exclusivity by paying a premium — [Uniswap docs: auction types](https://developers.uniswap.org/docs/liquidity/uniswapx/concepts/auction-types); [Uniswap docs: fillers overview](https://developers.uniswap.org/docs/liquidity/uniswapx/filling/overview)
- Distinct filler addresses fell from over 2,000 in mid-2023 to 12 in January 2024. The top 3 handled about 79% of daily volume — [Chitra/Gauntlet, arXiv 2403.02525](https://arxiv.org/html/2403.02525v1)
- Over Aug 2023–Feb 2025, SCP and Wintermute had more than 90% of UniswapX volume — [arXiv 2503.00738](https://arxiv.org/html/2503.00738v2)
- A third-party blog claims the top 3 fillers take 70–85% of weekly volume through exclusive arrangements. It cites no dataset — [Chainscore blog](https://chainscorelabs.com/blog/comparisons/intent-based-architecture/uniswapx-exclusive-filler-deals-undermine-decentralization)

**1inch Fusion resolvers (paid by order flow; resolvers must stake 1INCH)**
- Resolvers stake 1INCH (lock of one month to two years) to get Unicorn Power, agree to the resolver terms of use, register on the whitelist, set up a worker address and deposit 1INCH into the FeeBank — [1inch Fusion FAQ](https://help.1inch.com/en/articles/6800254-1inch-fusion-faq)
- Current docs require at least 5% of total Unicorn Power among whitelisted resolvers. Older sources and 1IP-33 (2023) said 10%. The whitelist holds only 10 resolvers at a time — [1inch business docs](https://business.1inch.com/portal/assets/docs-v2/resolvers/introduction.md); [1IP-33](https://gl.app/dao/1inch.eth/proposals/0x99a7314a9344be93995abec23ecc7a42f885f864b7ef74efc3a2ac9f19d392d7); [1inch docs (older)](https://1inch-docs.vercel.app/docs/fusion-swap/becoming-a-resolver/how-to-become-resolver)
- 1IP-89, which removes the 5% Unicorn Power requirement for access to Fusion exclusive orders, shows status "Succeeded". Whether it has been implemented is unconfirmed — [1IP-89 on Goverland](https://gl.app/dao/1inch.eth/proposals/0x67998a68bb09a7db6d0e8dcf3412086000f90213a22ee884c4c72996d341df07)
- The top 3 resolvers control about 80% of Fusion volume (Aug 2023–Feb 2025) — [arXiv 2503.00738](https://arxiv.org/html/2503.00738v2)
- The resolver terms of use have been re-issued several times (2025-11-24, 2026-07-27, 2026-08-14). The content, including any KYC/KYB clause, could not be read here — [1inch resolver ToU 2026-08-14](https://business.1inch.com/portal/assets/legal-docs/resolvers/terms-of_use_resolvers_20260814.pdf)

**Across relayers (paid by user relayer fee plus LP-fee structure; relayers front their own capital and are repaid from the HubPool)**
- Relayers fill bridge deposits on the destination chain with their own capital and are repaid later. The relayer fee is meant to cover gas, the opportunity cost of capital and risk. LPs are the "capital of last resort" (slow fill) — [Across docs: actors](https://docs.across.to/reference/actors-in-the-system); [Across docs: fees](https://docs.across.to/reference/fees-in-the-system)
- Capital is locked until bundle settlement, about 1.5 hours by Across's docs. A competitor comparison cites 4 hours — [Across docs: speed](https://docs.across.to/user-docs/how-across-works/speed); [search summary of Chainscore comparison](https://www.chainscorelabs.com/comparisons/bridges-trustless-vs-trusted-architectures/fee-models/connext-vs-across-relayer-costs)
- Competition is first-to-fill on the destination chain, plus an exclusivity layer. Relayers opt in by opening a pull request to a configuration repository. The Across API picks the exclusive relayer using relayer preferences, destination-chain balances and possibly recent performance. The fill contract rejects other fillers until the deadline. The docs said the rollout was incremental — [Across docs: relayer exclusivity](https://docs.across.to/relayers/relayer-exclusivity); [Across docs: relayer nomination](https://docs.across.to/relayers/relayer-nomination); [exclusive-relayer-configs repo (mirror)](https://gh.r-mj.com/sprintertech/exclusive-relayer-configs)
- Operator count: 32 active relayers each cleared more than USD 10K volume per week in Q2 2025 (official post) — [Across on X, Q2 2025 recap](https://x.com/AcrossProtocol/status/1949926734389784953)
- Across separately claims "52+ independent operators" (promotional, period not stated) — [Across blog](https://across.to/blog/across-jumper-exchange)
- Across does not publish a relayer roster or a concentration breakdown; volume is top-5 concentrated, with no figure given — [Eco article](https://eco.com/support/en/articles/14799839-across-protocol-solver-architecture-deep-dive)

**deBridge DLN takers and Mayan Swift solvers (paid by order spread; capital fronted)**
- DLN solvers track orders off-chain and fill when their own criteria are met (profitability, margin, token whitelist, finality) — [deBridge docs](https://docs.debridge.finance/dln-the-debridge-liquidity-network-protocol/market-and-limit-orders)
- An open-source `dln-taker` daemon exists and needs a funded reserve wallet — [npm @debridge-finance/dln-taker](https://www.npmjs.com/package/%40debridge-finance%2Fdln-taker)
- One third party calls the taker network permissionless; another describes "deBridge's approved solver set". The two conflict — [Eco deBridge explainer](https://eco.com/support/en/articles/14800733-debridge-cross-chain-liquidity-network-explained)
- A study of 3.5M cross-chain intents (USD 9.24B, Jun–Nov 2025, Mayan Swift, Across and deBridge) finds deBridge has "higher solver profitability". The same study found 210 historical liquidity-exhaustion attack instances on deBridge with a mean net profit of about USD 286. Mayan Swift is described as an English auction with a "relatively distributed solver setup" — [arXiv 2602.17805](https://arxiv.org/html/2602.17805)

**Keepers (Chainlink Automation, Gelato, Keep3r)**
- Chainlink Automation runs on Chainlink's professional node-operator pool (the same operators as Data Feeds), with rotating node selection. A 2026 source says Automation is moving into the Chainlink Runtime Environment (CRE). Sources disagree on whether the operator set is "permissionless" or "pre-approved, bonded" — [Chainlink docs](https://docs.chain.link/chainlink-automation); [Spark glossary](https://www.spark.money/glossary/keeper-network)
- Gelato was described as running on a whitelisted set of node operators, with a plan to go permissionless by mid-2023. No current confirmation was found — [Hackernoon overview](https://hackernoon.com/an-overview-of-smart-contract-automation-solutions)
- Keep3r is an open market: any bonded keeper can execute any registered job, and pay is gas plus a premium. An undated DappRadar listing shows USD 653 of 24h volume, which suggests negligible activity — [Spark glossary](https://www.spark.money/glossary/keeper-network); [DappRadar](https://dappradar.com/?p=32467)

**Oracle roles (Pyth publishers, UMA proposers and disputers)**
- Pyth publishers apply through a Data Publisher Application, and the publisher insights page has a "permissioned" column — [Pyth insights: publishers](https://insights.pyth.network/publishers)
- Oracle Integrity Staking (OIS) launched in Sep 2024 to reward publishers and their delegators. Pyth now says the DAO is winding down OIS rewards, and the OIS docs show "OIS rewards are paused" — [Pyth blog: next chapter](https://www.pyth.network/blog/pyth-s-next-chapter-infrastructure-upgrade-and-a-revenue-based-economic-model); [Pyth OIS docs](https://docs.pyth.network/oracle-integrity-staking); [Pyth OIS launch blog](https://pyth.network/blog/oracle-integrity-staking-incentivizing-safer-price-feeds-for-a-more-secure-defi)
- UMA/Polymarket: UMIP-189 passed on 2025-08-06 and moved Polymarket to the Managed Optimistic Oracle V2 (MOOV2), limiting proposals to a whitelist. The initial list had 37 addresses: Risk Labs and Polymarket staff, plus users with 20+ proposals at more than 95% accuracy in the past 3 months — [The Block](https://www.theblock.co/post/366507/polymarket-uma-oracle-update)
- Eligibility was broadened in Nov 2025 to at least 5 proposals at 95% or better accuracy. Current docs use two criteria over 6 months "subject to Risk Labs' discretion". Disputes remain open to anyone — [UMA blog: managed proposers update](https://blog.uma.xyz/articles/managed-proposers-update); [UMA docs: default proposer whitelist](https://docs.uma.xyz/using-uma/default-proposer-whitelist)
- Economics: proposer bond is typically USD 750 and the reward is USD 2, raised to USD 5 on many markets. A wrong, disputed proposal loses the whole bond, so break-even accuracy at a USD 5 reward is about 99.3% — [Polymarket docs: resolution](https://docs.polymarket.com/concepts/resolution); [Polymarket guide: why you probably shouldn't propose](https://polymarketguide.gitbook.io/polymarketguide/basics/why-you-probably-shouldnt-propose)
- Operational risk: one UMA forum thread asks for a refund of 37,875 USDC.e burned by self-disputing 86 "poisoned" requests — [UMA discourse](https://discourse.uma.xyz/t/request-to-refund-37-875-usdc-e-burned-by-self-disputing-86-poisoned-requests/2283)

**MEV backrunning and arbitrage on smaller chains/L2s (paid by price dislocations, not by a protocol)**
- Arbitrum Timeboost (from Apr 2025): Selini Capital and Wintermute won more than 90% of express-lane auction rounds, Apr–Jul 2025 (11.5M express-lane transactions, 151K auctions). Auction competition and DAO revenue declined over time, and secondary resale markets collapsed — [arXiv 2509.22143](https://arxiv.org/abs/2509.22143)
- An AFT 2026 paper says two searchers kept dominating through Mar 2026 — [AFT 2026, LIPIcs vol. 395 paper 20](https://drops.dagstuhl.de/storage/00lipics/lipics-vol395-aft2026/LIPIcs.AFT.2026.20/LIPIcs.AFT.2026.20.pdf)
- Timeboost revenue was about USD 2M in its first three months — [The Block, 2025-07-04](https://www.theblock.co/post/361058/arbitrum-timeboost-fees)
- An Arbitrum docs page says the express lane will be decommissioned when a PGA (priority gas auction) activates after an on-chain vote. Current status unverified — [Arbitrum docs](https://docs.arbitrum.io/how-arbitrum-works/timeboost/how-to-use-timeboost)
- Base: two entities produce more than 80% of spam MEV (Flashbots analysis) — [Flashbots: MEV and the limits of scaling](https://writings.flashbots.net/mev-and-the-limits-of-scaling)
- Spam's share of Base gas peaked near 50% in early 2025. After the gas-target cut (Jun 2025) and a minimum gas price (Dec 2025) it fell below 15% through Jun 2026 — [arXiv 2604.00234](https://arxiv.org/html/2604.00234)
- 82% of MEV bots on Base and 60% on Optimism are "profitable" under the paper's metric. A reviewer flags inconsistencies between its abstract and tables — [arXiv 2607.24172 "There Will Be Spam"](https://arxiv.org/html/2607.24172v1); [Pith review](https://pith.science/paper/2607.24172)
- Profits on rollups are significantly lower than on Ethereum, and cyclic-arbitrage contracts used more than 50% of gas on Base and Optimism in Q1 2025 — [Optimistic MEV in L2s, AFT 2025](https://drops.dagstuhl.de/storage/00lipics/lipics-vol354-aft2025/html/LIPIcs.AFT.2025.28/LIPIcs.AFT.2025.28.html)
- Ethereum arbitrage profits "are captured by a select few"; Solana is described as a high-frequency trading floor — [Extropy arbitrage analysis 2024–25](https://hackmd.io/@Extropy/ArbAnalysis)

### Inferences
- **CoW, money available:** USD 2.6M over 257 days annualises to about USD 3.7M/yr of solver rewards at 2026 COW prices. The implied price is about USD 0.071 per COW (2.6M / 36.8M). If about 50% goes to one team and the rest is split Pareto-style among roughly 15–25 others, a new entrant would win only the residual small-order and long-tail share. That share is exactly where rewards are capped by protocol fees and where solvers say rewards can be below overhead.
- **CoW, capital barrier:** at that COW price, the CIP-44 reduced bond is about USD 50K + USD 35K ≈ USD 85K, rising to about USD 171K at target. That is far above the USD 10–15K budget. The only route within budget is the CoW DAO pool (no own bond, but KYC, core-team approval and a service fee). So the binding constraint is solver quality and approval, not capital.
- **UniswapX and 1inch Fusion:** inside the 10–15K budget the only path is the open Dutch-auction tail on UniswapX after the exclusivity window. That is a latency race against SCP and Wintermute. 1inch needs a top-10 stake of Unicorn Power, plausibly far beyond budget (the 1INCH amount needed was not found).
- **Across, sensitivity (illustrative, margin assumed, not sourced):** USD 15K/yr from relaying needs volume × net margin = USD 15K. At 1 bp net that is USD 150M/yr (about USD 410K/day). At 3 bps it is USD 50M/yr (about USD 137K/day), which means turning USD 12K of inventory about 11 times a day with locks of 1.5–4 h. That is near the physical limit and assumes winning fills against the exclusivity layer, which weights destination-chain balances. I judge this implausible for a USD 12K operator.
- **UMA:** USD 15K/yr at USD 5/proposal is 3,000 undisputed proposals a year (about 8 a day), each tying up USD 750, and every loss wipes out 150 rewards. Polymarket proposing is also whitelisted since Aug 2025. Not viable as an income source.
- **Pyth and Chainlink:** institution- or operator-permissioned; Pyth's reward programme is paused. Not accessible.
- **Small-chain MEV:** the "82% of bots profitable" figure means profitable at all, not profitable at scale. Concentration (two entities, more than 80% of Base spam; two firms, more than 90% of Timeboost) and Base's Dec 2025 minimum gas price both argue against USD 15–20K/yr for a newcomer. That makes this the same kind of bot race as the liquidation work already studied in workstream B.
- **Overall:** this supports the earlier Stage 0 FAIL on solver/filler rewards (M10), with one refinement. Capital is not the binding barrier for CoW (the DAO pool route); quality, approval and concentration are.

### Gaps
- Exact current CoW reward parameters (β per chain, whether a weekly cap applies, current DAO-pool service fee) could not be read: docs.cow.fi and forum.cow.fi were unreachable from this sandbox.
- Per-solver CoW payouts, and therefore median solver income, were not obtained; the 52% single-team figure is unconfirmed.
- No sourced figure for Across relayer net margin (bps) or realised per-relayer income; no public relayer concentration figure.
- Mayan Swift solver onboarding requirements: not found. deBridge taker permissioning: sources conflict.
- 1inch: amount of 1INCH equal to 5% of whitelisted Unicorn Power, and whether the terms of use require KYC/KYB, were not found.
- Sky/Maker non-liquidation keepers (e.g. flap/flop, oracle poke, spell execution) and protocol-paid vault strategists/rebalancers (Yearn, Arrakis, Gamma, Morpho curators): no evidence collected in this pass.
- Gelato's current executor permissioning and Keep3r 2025–26 activity: not found.
- One search summary said L2 arbitrage is about 0.03–0.05% of trading volume on Arbitrum, Base and Optimism, but the exact paper could not be confirmed, so the figure is not used.

## 2. Is there free, machine-readable, per-operator payout data to compute income distributions and median operator income (2024–2026)?

### Takeaway
Yes for CoW (official Dune dashboard, a GitHub accounting repo, a per-auction solver competition API and an academic
replication repo) and, from on-chain events, for Across, UniswapX, deBridge, UMA and Timeboost. Payout data alone
overstates profit because operator costs (gas, infrastructure, inventory) are not published anywhere.

### Cited Findings
- CoW's docs name a Dune dashboard as the source of truth for weekly solver payments. The accounting reference points to dune.com/cowprotocol/cow-solver-rewards, used to verify accounting every week — [CoW docs: rewards](https://docs.cow.fi/cow-protocol/reference/core/auctions/rewards); [CoW docs: accounting](https://docs.cow.fi/cow-protocol/reference/core/auctions/accounting)
- The dashboard data comes from scripts in the `cowprotocol/solver-rewards` GitHub repo. CoW uploads internal data to Dune and joins it with on-chain data — [Dune case study](https://community.dune.com/case-studies/cow-protocols-journey-into-automated-payments-and-understanding-user-behavior); [solver-rewards issues index](https://issues.ecosyste.ms/hosts/GitHub/repositories/cowprotocol%2Fsolver-rewards/issues)
- There is a separate repo for Gnosis Chain payouts — [gnosis_chain_solver_payouts](https://awesome.ecosyste.ms/projects/github.com%2Fcowprotocol%2Fgnosis_chain_solver_payouts)
- The CoW API has a "get information about a solver competition" endpoint, giving per-auction solver bids and rankings — [CoW API reference](https://cowswap.mintlify.app/api-reference/get-information-about-a-solver-competition)
- Weekly aggregate solver rewards also appear on DefiLlama's COW token page (for example USD 2.92M, USD 611.61K and USD 876.06K entries; periods unclear) — [DefiLlama COW](https://defillama.com/token/cow)
- The Core Team has a DAO mandate to buy back all solver rewards emitted each week, and buybacks are reviewable on Dune — [Blockworks token transparency: CoW H1 2026](https://blockworks.com/token-transparency/filing/cow-protocol)
- An academic dataset of daily CoW solver shares (2025-03-01 to 2026-03-30) has code in GitHub repo `ryonzhang/solver-reward-market-structure` — [arXiv 2607.21955](https://arxiv.org/abs/2607.21955)
- Bitquery's 2026 solver-pay table is built from COW transfers out of the rewards safe plus ETH gas refunds — [Bitquery](https://bitquery.io/investigations/cow-swap-solver-auctions)
- Across: exclusivity opt-ins are public pull requests to a config repo. Repayments run through HubPool bundles that pass a challenge period and then pay out on the relayer's chosen chain, so fills and refunds are on-chain events — [Across docs: relayer exclusivity](https://docs.across.to/relayers/relayer-exclusivity); [exclusive-relayer-configs (mirror)](https://gh.r-mj.com/sprintertech/exclusive-relayer-configs)
- No Dune dashboard for Across relayer fills was found — [Eco article: no published relayer roster](https://eco.com/support/en/articles/14799839-across-protocol-solver-architecture-deep-dive)
- Cross-chain intents (Mayan, Across, deBridge) can be reconstructed at scale from public chain data: 3.5M intents, Jun–Nov 2025 — [arXiv 2602.17805](https://arxiv.org/html/2602.17805)
- Timeboost auction results (bids and winners) were studied from public data: 151K auctions, 11.5M transactions — [arXiv 2509.22143](https://arxiv.org/abs/2509.22143)
- Pyth publisher list with a permission flag — [Pyth insights](https://insights.pyth.network/publishers)

### Inferences
- The cheapest Stage 1 measurement in repo style would be CoW: pull the weekly per-solver COW payouts (solver-rewards repo or the Dune query results), convert at the weekly COW price, and compute the median and the share of solvers below USD 15K/yr for 2024–2026. The sandbox blocks docs.cow.fi and forum.cow.fi, so this would go through the existing GitHub Actions `scripts/fetch_public.py` route, or through GitHub (api.github.com via `gh`) for the solver-rewards repo.
- For Across, the comparable measure is per-relayer fee income = Σ(input amount − output amount − gas) over fills from SpokePool events, which can be built from free RPC or explorer data. No ready-made per-relayer income table was found.
- For UniswapX and 1inch Fusion, filler and resolver addresses appear in fill events on the reactor and settlement contracts, so volume shares can be computed. Margins need price reconstruction.

### Gaps
- Not verified whether the Dune dashboard exposes per-solver weekly USD (vs COW) and whether the free Dune tier allows exporting it.
- Exact Across, UniswapX and deBridge event names and contract addresses were not collected in this pass.
- No public dataset of operator costs exists for any role, so "net income per operator" cannot be computed from public data alone.

## 3. Which roles are permissionless today and accessible from Malaysia without KYC evasion?

### Takeaway
Open without permission: Across relaying (exclusivity is an opt-in by PR), UniswapX non-exclusive filling,
Keep3r keeping, UMA disputing and non-Polymarket UMA proposing, MEV backrunning; deBridge DLN taking is probably open
(sources conflict). Gated: CoW solving (bond, or KYC plus approval; KYC is a normal legitimate step, not evasion),
1inch Fusion (top-10 stake whitelist plus terms of use), UniswapX quoting (Uniswap Labs vetting), Polymarket UMA
proposing (whitelist since Aug 2025), Pyth publishing (application/permissioned), Chainlink Automation (node operators).
No source mentions a Malaysia-specific restriction for any of these roles. That is unverified, not confirmed safe.

### Cited Findings
- UniswapX: quoter is permissioned (vetted by Uniswap Labs); filler is permissionless — [Uniswap docs](https://developers.uniswap.org/docs/liquidity/uniswapx/concepts/auction-types)
- CoW: no prerequisites other than KYC when joining the CoW DAO bonding pool; otherwise a bond (CIP-44 reduced or full) — [CoW onboarding docs](https://cowswap.mintlify.app/cow-protocol/howto/solvers/onboard); [CIP-44](https://forum.cow.fi/t/cip-44-reduced-bonding-requirements/2424)
- 1inch Fusion: whitelist of 10 resolvers, at least 5% of Unicorn Power, terms of use required — [1inch FAQ](https://help.1inch.com/en/articles/6800254-1inch-fusion-faq); [1inch business docs](https://business.1inch.com/portal/assets/docs-v2/resolvers/introduction.md)
- Across: relayer exclusivity is opt-in through a config pull request; the base relayer role is open and first-to-fill — [Across docs: relayer exclusivity](https://docs.across.to/relayers/relayer-exclusivity); [Across docs: actors](https://docs.across.to/reference/actors-in-the-system)
- UMA/Polymarket: proposals are whitelist-only since Aug 2025 on markets Polymarket chooses; disputes stay open, with the DVM as final arbiter — [The Block](https://www.theblock.co/post/366507/polymarket-uma-oracle-update); [UMA blog](https://blog.uma.xyz/articles/managed-proposers-update)
- Critics say the whitelist turns the oracle from permissionless into permissioned and excludes skilled proposers — [Polymarket guide: criticisms](https://polymarketguide.gitbook.io/polymarketguide/case-studies/securing-the-oracle/criticisms)
- Pyth publishers: application form and "permissioned" status per publisher — [Pyth insights](https://insights.pyth.network/publishers)
- Keep3r: any bonded keeper can execute any registered job — [Spark glossary](https://www.spark.money/glossary/keeper-network)
- deBridge taker: "permissionless" per one third party, "approved solver set" per another — [Eco deBridge explainer](https://eco.com/support/en/articles/14800733-debridge-cross-chain-liquidity-network-explained)

### Inferences
- From Malaysia, the open roles are reachable on-chain with no KYC step, so no evasion question arises. The CoW DAO-pool KYC is a legitimate disclosure step and is acceptable under the repo rules, provided Jx himself completes it.
- Polymarket-linked UMA work is doubly constrained: the whitelist since Aug 2025, and Polymarket's own geoblock list (the repo already records Polymarket as blocked from US servers; Malaysia's status was not checked here).

### Gaps
- No source checked whether CoW's KYC, 1inch's terms of use or Across's API terms exclude Malaysia-resident operators; this needs reading the actual terms (blocked hosts in this sandbox).
- Whether deBridge and Mayan require approval for new solvers is unresolved.

## 4. Evidence of small independent operators earning meaningful returns vs professional dominance

### Takeaway
No case study, forum post or governance report was found showing a small, independent operator earning
USD 15K+/yr net in any of these roles in 2024–2026. Every concentration measure found points to professional
dominance: top 3 CoW solvers above 50% of volume, UniswapX top 2 above 90%, 1inch top 3 about 80%, Timeboost top 2
above 90% of rounds, Base spam top 2 above 80%. Long tails exist (28 CoW solvers; 32 Across relayers above USD 10K/week),
but none of these sources reports their income.

### Cited Findings
- CoW: 28 solvers active, 12 above 1% of volume, top 3 above 50% (Jan–Apr 2025) — [Sprinter blog](http://blog.sprinter.tech/building-economic-trust-in-solver-based-networks-part-2/)
- CoW: about 52% of 2026 reward COW to one team (unconfirmed) — [Bitquery](https://bitquery.io/investigations/cow-swap-solver-auctions)
- CoW: the top solver bought a rival solver's codebase (Barter) — [Blockworks](https://blockworks.co/news/barter-buys-rival-solver-codebase)
- CoW after CIP-74: HHI up (0.176 → 0.241) by volume, down by trade count, and concentration fell in small orders — i.e. small orders became more contestable, but they carry small, fee-capped rewards — [arXiv 2607.21955](https://arxiv.org/abs/2607.21955)
- Some solvers say small-trade rewards sometimes fall below overhead — [Blockchain Dose](https://blockchaindose.com/cow-protocol-and-anoma/)
- UniswapX: from more than 2,000 filler addresses (mid-2023) to 12 (Jan 2024), with the top 3 at about 79% — [arXiv 2403.02525](https://arxiv.org/html/2403.02525v1)
- UniswapX: SCP plus Wintermute above 90% — [arXiv 2503.00738](https://arxiv.org/html/2503.00738v2)
- 1inch Fusion: top 3 about 80% — [arXiv 2503.00738](https://arxiv.org/html/2503.00738v2)
- Across: 32 relayers above USD 10K/week in Q2 2025; volume top-5 concentrated (no figure) — [Across on X](https://x.com/AcrossProtocol/status/1949926734389784953); [Eco article](https://eco.com/support/en/articles/14799839-across-protocol-solver-architecture-deep-dive)
- Timeboost: Selini plus Wintermute above 90% of rounds; resale markets collapsed — [arXiv 2509.22143](https://arxiv.org/abs/2509.22143)
- Base: two entities above 80% of spam MEV; "extreme concentration… suggests significant barriers to entry" — [Flashbots](https://writings.flashbots.net/mev-and-the-limits-of-scaling)
- UMA: proposer guides advise most users not to propose, because USD 2–5 rewards do not justify USD 750 bond risk — [Polymarket guide](https://polymarketguide.gitbook.io/polymarketguide/basics/why-you-probably-shouldnt-propose)
- Pyth OIS rewards paused/wound down — [Pyth OIS docs](https://docs.pyth.network/oracle-integrity-staking)

### Inferences
- The structural pattern matches the repo's earlier finding for liquidation bots (workstream B): protocol-paid automation becomes a winner-take-most race once a role is profitable. The tail exists, but nobody publishes evidence that the tail clears USD 15–20K/yr after costs.
- If any of these is worth a Stage 1 kill-test, the order by cost of measurement would be: (1) CoW per-solver payout distribution (data is official and weekly, and answers "does the 10th-best solver earn more than USD 15K/yr in rewards?"); (2) Across per-relayer fee income from SpokePool fill events; (3) deBridge DLN per-taker spread from on-chain fills, since one paper flags deBridge as having higher solver profitability. A suggested kill rule: if the median non-top-5 operator's gross rewards or fees are below USD 15K/yr in 2025–26, the role cannot meet the target net of costs. This should be pre-registered first, per CLAUDE.md.

### Gaps
- No source found with realised income for any specific small operator (CoW forum posts by small solvers, Across relayer write-ups, deBridge taker reports). The BRRR DAO article "How much do solvers really earn?" was found by title only; its estimates use Dec 2024 COW prices (about USD 1.61) and could not be read.
- No 2026 UniswapX or 1inch concentration data; the latest academic figures end in Feb 2025.

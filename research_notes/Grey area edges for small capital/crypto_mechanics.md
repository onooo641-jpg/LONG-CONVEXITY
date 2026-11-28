# Crypto "grey-area" profit mechanisms for a small player (USD 10–15K, Malaysia resident), 2025–2026

Scope note (read first). Research date 2026-11-28. In this session the network blocked direct fetches of arxiv.org, bitquery.io and github.io, so every external finding below comes from **search-result excerpts, not full texts**. Numbers should be re-checked against the primary page before they are used in a ledger row. "Repo" sources are this repository's own earlier tests (local paths), which are verified by Jx's own runs. Labels used: **[official]** = venue docs / regulator; **[peer-review/preprint]** = academic; **[third-party]** = research firm or media; **[promo/anecdote]** = influencer, marketing or single-team self-report.

## Q1. How each mechanism works, why it is considered unethical, whether it is within written terms, and Malaysian legality

### Takeaway
Every mechanism in scope is technically open and mostly within written venue rules, but the ones that are clearly within rules (maker rebates, JIT, backrunning, migration timing, points OTC run by the venue itself) are either professional-only races or pay too little. The ones that pay well (sniping, launch-points, Binance Alpha) are rug-heavy or sit on platforms not registered in Malaysia. For Malaysia, the Securities Commission (SC) regulates exchange **operators**, warns that investors on unregistered platforms have no protection, and is acting against unregistered exchanges. I found no SC rule that addresses a resident's own use of a DEX.

### Cited Findings

**Malaysia (SC) – legal frame**
- [official] The SC revised its Guidelines on Recognized Markets on 20 May 2026 (tighter investor protection and governance for registered digital asset exchange (DAX) operators) and issued a practice note on digital asset broking. DAX operators join the Financial Markets Ombudsman Service in 2026 — [SC media release](https://www.sc.com.my/resources/media/media-release/sc-issues-revised-guidelines-on-recognized-markets-for-digital-asset-exchange); [The Star, 2026-05-20](https://www.thestar.com.my/business/business-news/2026/05/20/sc-revises-guidelines-to--strengthen-malaysia039s-digital-asset-market); [Baker McKenzie, 2026-02](https://www.bakermckenzie.com/en/insight/publications/2026/02/malaysia-securities-commission-clarifies-requirements-digital-asset-broking)
- [official/third-party] From 14 April 2026 the SC worked with Google and other tech firms to stop unregistered DAX operators promoting to Malaysians on social media, and took administrative action against four unregistered DAX operators — [Business Today, 2026-05-20](https://www.businesstoday.com.my/2026/05/20/sc-tightens-digital-asset-exchange-rules-speeds-up-product-approvals/); [BIX Malaysia](https://www.bixmalaysia.com/learning-center/articles-tutorials/securities-commission-tightens-digital-asset-rules,-targets-unregistered-exchanges)
- [official] The SC says people who invest through unlicensed or unregistered entities "are not protected under the Malaysian securities laws" — [SC caution notice](https://www.sc.com.my/resources/media/media-release/sc-cautions-investors-against-unauthorised-initial-coin-offerings-and-digital-asset-exchanges)
- [official] In December 2024 the SC reprimanded Bybit and its CEO for running a DAX in Malaysia without registration — [SC](https://www.sc.com.my/resources/media/media-release/sc-takes-enforcement-action-against-bybit-for-illegally-operating-dax-in-malaysia); [FMT](https://www.freemalaysiatoday.com/category/business/2024/12/27/sc-reprimands-bybit-for-operating-illegal-digital-asset-exchange)
- [official] Consultation Paper 3/2025 (30 June – 11 August 2025) proposed DAX framework changes, including listing some assets without prior SC approval. It covers centralised operators, not DEXs — [SC](https://www.sc.com.my/resources/media/media-release/sc-seeks-public-feedback-on-proposed-enhancements-to-the-framework-for-digital-asset-exchange); [Lexology](https://www.lexology.com/library/detail.aspx?g=c71461c7-7945-4b23-b8b0-b240143e3321)
- [third-party] A law-firm summary says the SC has issued "periodic updates and press statements" on DeFi, NFTs and stablecoins. I could not find their text — [Mondaq](https://www.mondaq.com/fin-tech/1620168/everything-you-need-to-know-about-the-securities-commissions-guidelines-on-digital-assets)

**MEV backrunning (Base, Solana, HyperEVM)**
- How it works: a bot places its transaction right after a price-moving trade (or after a cross-venue gap opens) to capture the arbitrage. Unlike a sandwich, it does not worsen the victim's price. Critics object to the spam it creates and the fees it pulls from users. On Base and Optimism, spam MEV transactions used **over 50% of block gas in Q1 2025**, and only **6–12%** of these speculative probes led to a trade — [arXiv 2604.00234 "Blockspace Under Pressure"](https://arxiv.org/html/2604.00234) [preprint]
- On Base, the EVAge paper (2025 data) reports the high-frequency variant of a backrun strategy (SBA-HFT) earned **1,682.92 ETH** against **16.13 ETH** for the plain version, so the speed tier captures roughly 99% — [arXiv 2609.27424](https://arxiv.org/html/2609.27424v1) [preprint; the authors' claim that their tooling "empowers smaller searchers" is untested]
- On Solana, Jito bundles are the main ordering channel. Helius counted >3 billion bundles and **3.75M SOL in tips** over a year, from transfers to eight Jito tip accounts. Jito data misses activity routed through alternative mempools — [Helius Solana MEV report](https://www.helius.dev/blog/solana-mev-report) [third-party]. A single blog claims searchers tip 50–60% of expected profit — [cryptomevbot](https://cryptomevbot.com/blog/jito-mev-solana-bot) [promo, unsourced]
- On HyperEVM, one bot team reported about **$5M profit over ~8 months** arbitraging HYPE between HyperEVM pools (HyperSwap HYPE/USDT0, PRJX) and Hyperliquid's order book. The edge came from HYPE prices updating every 2 seconds. The 2M per-block gas limit against ~130K gas per arbitrage capped a block at ~7–8 arbitrages, and it got tight as more DEXs launched — [TechFlow](https://www.techflowpost.com/en-US/article/28622); [Odaily, 2025-10-20](https://www.odaily.news/en/post/5206943); [ChainCatcher](https://www.chaincatcher.com/en/article/2214261) [self-report by one team, republished]
- Terms: backrunning and atomic arbitrage are allowed by public chains and by Jito's block engine (an open auction by tip per compute unit) — [cryptomevbot](https://cryptomevbot.com/blog/jito-mev-solana-bot) [promo]; Helius (above). Sandwiching specific users is excluded under this brief's constraints. For scale, Helius put the average Solana sandwich profit at 0.0425 SOL ($8.67) — [Helius](https://www.helius.dev/blog/solana-mev-report)

**JIT (just-in-time) liquidity**
- How it works: liquidity is added to a concentrated-liquidity pool right before a large swap and removed right after, so the JIT provider collects the fee instead of passive LPs. It is seen as unethical because it dilutes passive LPs. A 2023 Imperial College study (Uniswap v3) found an average JIT **ROI of 0.007%** per attack and said sandwiching was more profitable with lower barriers — [IACR eprint 2023/973](https://eprint.iacr.org/2023/973.pdf) [peer-review, older]
- A 2025 AFT paper models optimal JIT and finds a "significant gap between observed and optimal JIT behavior", especially in risky-asset pools, and expects JIT to grow with Uniswap v4 hooks — [AFT 2025, LIPIcs](https://drops.dagstuhl.de/storage/00lipics/lipics-vol354-aft2025/html/LIPIcs.AFT.2025.8/LIPIcs.AFT.2025.8.html) [peer-review, model]. A 2025 preprint simulates optimised JIT against 6,829 observed JIT swaps — [arXiv 2509.16157](https://arxiv.org/pdf/2509.16157) (headline profit not seen). A 2026 FC paper studies Ethereum JIT, Jan 2024 – Sep 2025, and how JIT profit flows to block builders — [FC'26 DeFi](https://ifca.ai/fc26/defi/papers/jit-liquidity-ethereum-builders.pdf) (results not seen)
- Uniswap v4 hooks can let a pool capture JIT itself, which may shrink outside JIT — [dev.to commentary](https://dev.to/frb_research/uniswap-v4-hooks-mev-2026-searcher-opportunities-and-risks-1kkk) [opinion, unmeasured]

**Token-launch sniping (pump.fun, Virtuals Genesis, HIP-1)**
- pump.fun: Bitquery found sniper bots among the first buyers on **28%** of coins. They made **$31.5M on what they sold, or $15.2M counting unsold holdings**. Devs and their bundled wallets made **$579M+** — [Bitquery investigation](https://bitquery.io/investigations/pump-fun-snipers-bundles) [third-party; period not seen]
- For tokens bought by ≥20 other wallets in their creation block, **74.6% ended in a rug** (defined as a ≥50% drop with no recovery), against 0.9% when no one else bought (Oct 26 – Nov 25, 2026) — [dev.to/quantbloc](https://dev.to/quantbloc/pumpfun-bundles-in-2026-what-happens-to-first-block-buyers-5ci9) [blog analysis]
- Ethics: much early-block buying is by the deployer's own bundles or coordinated "wallet rings" (1,012 persistent rings detected) — [arXiv 2607.02795](https://arxiv.org/pdf/2607.02795); [arXiv 2609.10246 "Meme Coin Factories"](https://arxiv.org/pdf/2609.10246); [arXiv 2610.41597 serial rug exits](https://arxiv.org/html/2610.41597) [preprints]. A small sniper is mostly the counterparty of these teams
- Virtuals Genesis: allocation depends on points. Selling a Genesis allocation temporarily cuts the seller's points — [Bankless](https://www.bankless.com/nonstop-virtuals-gains). Virtuals restricts the first buys at launch to itself as an anti-sniping defence — [Nethermind on ethresear.ch](https://ethresear.ch/t/anti-sniper-defenses-token-launches-beyond/22882) [third-party]
- HIP-1 (Hyperliquid spot token deploy) uses a 31-hour Dutch auction for the ticker/deploy gas. I found no evidence tying HIP-1 to sniping profits — [QuillAudits](https://www.quillaudits.com/blog/blockchain/guide-to-hyperevm)

**Points / pre-market OTC (Whales Market, Pendle YT)**
- Whales Market lists points off-chain under prior agreements with participating projects. The project's own database updates ownership, and buyers claim tokens afterwards — [Tiger Research](https://reports.tiger-research.com/p/point-market-airdrop-trading-eng) [third-party]. The platform reports $330M+ cumulative volume. Collateral reduces counterparty/settlement risk but does not remove it — [pm.wiki](https://pm.wiki/projects/whales-market) [aggregator]
- Pendle YT holders receive the underlying protocol's points. Buying YT is a bet that the airdrop exceeds its cost — [Crypto.com Research, May 2025](https://crypto.com/en/research/interest-rate-derivatives-pendle-may-2025) [third-party]. Within terms: YT is the protocol's own sanctioned way to trade points
- Whether selling points through a third-party OTC desk breaks a given project's airdrop terms: not found (see Gaps)

**Binance Alpha points (new 2025 mechanism)**
- Users earn "Alpha Points" from balance and trading volume on Binance Wallet/Alpha tokens and spend them (~15 points per claim) on airdrops and TGEs. Most 2025 airdrops required **190–256 points** to be eligible. 2025 summary: 221 tokens launched, average airdrop value **$1,076 per user** (gross) — [CoinMarketCap Academy 2025 recap](https://coinmarketcap.com/academy/uk/article/binance-alpha-2025-crypto-airdrops-token-launches) [third-party]
- Critics call it a volume-farming treadmill: earning 15 volume points needs about **$32,768** of swaps at roughly $10–20 slippage and fees. Typical single-TGE take was $50–80, and some campaigns needed up to 3 BNB locked — [Forklog](https://forklog.com/en/the-race-for-alpha-points-a-trap-for-airdrop-hunters-or-binances-gold-mine/) [third-party]
- Legality for Malaysia: Binance is not on the SC's registered list. Bybit, a comparable unregistered exchange, was reprimanded (above). Whether Binance Wallet's self-custody "Alpha" layer counts as using an unregistered DAX was not verified (Gaps)

**Maker rebate / MM incentive programs on perp DEXs**
- Hyperliquid [community docs, secondary]: maker rebates of −0.001% / −0.002% / −0.003% for >0.5% / >1.5% / >3.0% share of 14-day weighted maker volume (perps + 2× spot). Base perps fees are 0.045% taker / 0.015% maker — [Hyperliquid community docs](https://hyperliquid-co.gitbook.io/community-docs/architecture/hypercore/dex/clearinghouse/fees); official page [hyperliquid.gitbook.io fees](https://hyperliquid.gitbook.io/hyperliquid-docs/trading/fees) (not readable in this session). Sources disagree on which tier reaches 0% maker fees (tier 4 vs tier 5 at $2B+) — [Datawallet](https://www.datawallet.com/crypto/hyperliquid-fees-explained)
- Extended [official]: 0% maker / 0.025% taker. Rebates run from **0.002% at 0.5%** of 30-day maker volume share up to **0.010% at 5%**, paid daily only if ≥$10 accrued — [Extended docs](https://docs.extended.exchange/extended-resources/trading/trading-fees-and-rebates)
- Lighter: Standard accounts pay 0/0 with lower priority and rate limits, and Plus accounts pay 0.005%. No maker rebate found — [thundermessage](https://thundermessage.com/priced-against-lighter) [third-party]. Paradex: retail web orders reportedly zero-fee since 15 June 2026 — [coincodecap](https://signals.coincodecap.com/hyperliquid-vs-paradex-vs-aden-vs-pacifica-vs-extended) [third-party]. Pacifica: 1.5 bp maker / 4 bp taker base tier — [perpfinder](https://perpfinder.com/perps/pacifica) [third-party]
- Ethics/terms: legitimate posting is fine; wash or self-matching to reach a share threshold is manipulation (excluded)

**Delisting / migration / forced conversion**
- FTM→S migration at a fixed 1:1. Kraken delisted FTM on 2 May 2025, listed S on 5 May and credited S by 9 May. The redemption contract is run by Sonic Labs — [Kraken support](https://support.kraken.com/gb/articles/migration-of-ftm-to-s) [official exchange]. OKX expected 1–5 days and excluded holdings under 1 FTM — [OKX](https://www.okx.com/cs/help/okx-to-support-ftm-token-migration) [official exchange]
- MKR→SKY terms (deadlines, delayed-upgrade penalty) were not found in this session

**Stablecoin redemption / depeg, trading competitions, liquidation keepers (already tested by repo)**
- Liquity-fork redemption bots: anyone may redeem 1 stable for $1 of collateral minus a fee, but feUSD traded at ~$0.998 (May 2026), so it is rarely profitable after the fee and an atomic bot race → dismissed — [repo docs/NICHE_SWEEP_20261124.md #379](../../docs/NICHE_SWEEP_20261124.md)
- Stablecoin depeg buying failed (UST −94% on one buy); fiat/synthetic variants (#429/#430) were downgraded after verification — [repo docs/CANDIDATES.md #46, #429–438](../../docs/CANDIDATES.md)
- Exchange/perp-DEX trading competitions: pools of $10K–$50K split among ~50 winners (Orderly, Sai, Gate, Kodiak), often ranked by volume → dismissed as too small — [repo NICHE_SWEEP #378](../../docs/NICHE_SWEEP_20261124.md)
- Liquidation keepers on small Aave-style venues: professionals take 75%+; a new bot makes ~$0–600/month — [repo CANDIDATES #100](../../docs/CANDIDATES.md) (brief's stated prior)

**Excluded by the brief's constraints (listed with reason)**
- Sandwiching specific users (Solana Jito sandwiches; Helius avg $8.67 each): market manipulation / harms named users
- pump.fun dev bundling and "wallet rings" ($579M+ to devs per Bitquery): coordinated self-dealing, close to pump-and-dump
- Multiple wallets to clear Binance Alpha / points thresholds, or to farm Whales Market points: sybil
- Wash or self-matched maker volume to reach Extended/Hyperliquid share tiers: wash trading
- Pushing thin-pool prices to trigger liquidations on small lenders: oracle manipulation
- Polymarket and Whales Market "binary pre-market contracts" (Yes/No paying $1): prediction markets / gambling, illegal in Malaysia

### Inferences
- The clean, within-terms mechanisms (backrun, JIT, maker rebates, migration timing) are all latency races or share-threshold programs. The 2025–26 data shows winners take most of the pie (Base 1,683 vs 16 ETH; 6–12% probe success; rebate floors at 0.5% venue share).
- The mechanisms that look lucrative on paper (Virtuals Genesis multiples, Binance Alpha averages, pump.fun snipers) depend on hype-cycle survivorship, or most of the value goes to insiders.
- Malaysia: DEX and self-custody use by a resident is not addressed by any SC text I found. Centralised venues not on the SC register (Binance, Bybit) give no investor protection and are under active SC enforcement. A Malaysian should assume these grey programs are lawful to use but unprotected. This is an inference, not legal advice.

### Gaps
- SC text on DeFi/DEX use by residents (the Mondaq-referenced statements) was not retrieved. The SC Guidelines on Digital Assets FAQs should be read directly.
- Whether Binance Wallet/Alpha is treated as an "unregistered DAX" for Malaysian users is unverified.
- Whales Market's own terms of service and default procedure, and individual projects' rules on points transfer (many projects bar point sales), were not found.
- MKR→SKY delayed-upgrade penalty terms were not found.
- Hyperliquid's official fee table could not be read. Figures are from community docs.

## Q2. Realistic annual profit for a small player (verified/official vs anecdote)

### Takeaway
None of the mechanisms has verified evidence that a USD 10–15K player reliably earns USD 15–20K/yr. The only large verified-ish numbers belong to professional teams (HyperEVM arb ~$5M/8 months, one team) or to aggregates (Jito tips, Bitquery sniper totals). Per-small-player figures are either tiny (rebates, JIT, competitions, redemption bots) or promotional averages with heavy survivorship (Virtuals, Binance Alpha).

### Cited Findings
- Backrunning on Base: the speed tier earns ~100× the plain strategy (1,682.92 vs 16.13 ETH) — [arXiv 2609.27424](https://arxiv.org/html/2609.27424v1) [preprint]. Probe success is 6–12% — [arXiv 2604.00234](https://arxiv.org/html/2604.00234) [preprint]. Total MEV profit grows about linearly with non-MEV volume on Base — same source
- Solana MEV: annual MEV revenue is estimated at ~$720M (2025), and searcher profits through Jito are put at ">$480M cumulative by Q2 2026". The sources disagree and are secondary — [rpcfast](https://rpcfast.com/blog/solana-mev); [businessmodelanalyst](https://businessmodelanalyst.com/the-400-million-mev-problem-how-solanas-block-production-became-a-competitive-sport/) [third-party/promo]. I found no per-searcher distribution
- HyperEVM arb: ~$5M over ~8 months for one team [self-report, unaudited] — [TechFlow](https://www.techflowpost.com/en-US/article/28622)
- JIT: 0.007% average ROI per attack (v3, 2023 data) — [IACR 2023/973](https://eprint.iacr.org/2023/973.pdf)
- pump.fun sniping: $31.5M realised, or **$15.2M after counting unsold bags**, across all snipers. Unsold holdings halve the realised take — [Bitquery](https://bitquery.io/investigations/pump-fun-snipers-bundles). An idealised call-channel strategy (buy at the call, sell 30 s later) had a **mean of +552.2% but a median of −4.0%** — [moneyleavesclues substack](https://moneyleavesclues.substack.com/p/inside-the-economics-of-pumpfun-call) [third-party]. Solidus Labs claims ~98.7% of pump.fun tokens showed pump-and-dump or rug traits — [Solidus Labs](https://www.soliduslabs.com/reports/solana-rug-pulls-pump-dumps-crypto-compliance) [third-party, method unverified]. One multi-agent study finds sniper bots have "minimal observable performance effect" and mostly redistribute profits among participants — [arXiv 2601.08641](https://arxiv.org/pdf/2601.08641)
- Virtuals Genesis: reported 4×–128× (avg 32×) over ~24 launches to May 2025 — [TechFlow](https://techflowpost.com/en-US/article/25779) [promo]. Every fully subscribed launch printed 2.2×–28× to April 2025 (Sim0.eth, via the same coverage). Later, about 6 of 23 launches "pulled ahead" — [AltcoinBuzz](https://www.altcoinbuzz.io/cryptocurrency-news/top-15-virtuals-protocol-genesis-launches-by-point-value/). These are multiples on small point-capped allocations, measured at peak or listing prices. Sources conflict on the minimum raise (42,425 vs 112,000 VIRTUAL)
- Binance Alpha: average gross airdrop value $1,076 per user in 2025 — [CMC](https://coinmarketcap.com/academy/uk/article/binance-alpha-2025-crypto-airdrops-token-launches). Typical single TGE $50–80; ~$10–20 cost per 15 volume points — [Forklog](https://forklog.com/en/the-race-for-alpha-points-a-trap-for-airdrop-hunters-or-binances-gold-mine/). Best cases: up to 859 USDT over 11 projects (April 2025) and ~$2,000 in 20 days at peak prices — [TechFlow 25392](https://www.techflowpost.com/en-US/article/25392); [TechFlow 25699](https://www.techflowpost.com/en-US/article/25699) [anecdote]
- Maker rebates: Extended pays 0.002% at the minimum 0.5% share — [Extended docs](https://docs.extended.exchange/extended-resources/trading/trading-fees-and-rebates). Hyperliquid pays 0.001% at >0.5% share — [community docs](https://hyperliquid-co.gitbook.io/community-docs/architecture/hypercore/dex/clearinghouse/fees)
- Earlier repo results for comparison: competitions too small; redemption bots rare; liquidation bots ~$0–600/month; Hyperliquid points ~$3–7K per $1M volume — [repo CANDIDATES/NICHE_SWEEP](../../docs/CANDIDATES.md)

### Inferences
- Maker rebate arithmetic: $15,000/yr at 0.002% needs **$750M/yr of maker volume** (~$2M/day), **and** that volume must be ≥0.5% of Extended's total maker volume. At 0.001% on Hyperliquid it needs $1.5B/yr plus a 0.5% venue share. Neither is realistic on $10–15K without inventory losses swamping the rebate. The rebate is a tie-breaker for professional MMs, not a standalone edge.
- Binance Alpha: at ~$1,076 gross per user per year, minus volume costs (Forklog's $10–20 per 15 points, repeated daily), a single honest account nets low hundreds to ~$1K/yr. That is far below target, and more accounts would be sybil (excluded).
- pump.fun sniping: the all-sniper net of $15.2M is shared across many bots, and the call-channel median is −4%. A new small bot's expected value is near zero or negative after rugs and fees. This matches the repo's earlier "memecoin graduation – no data" status.
- Virtuals Genesis is the only item with large reported per-allocation multiples. But allocations are point-capped (points come from holding/staking VIRTUAL, which carries price risk), returns are at peak prices, and the sample is a 2025 hype window. It does not support a forward >100%/yr claim.
- HyperEVM HYPE arbitrage is the clearest 2025 example of a small team (not a firm) earning seven figures. It is a capacity-capped (7–8 arbs/block) race that tightened as more DEXs launched. The repo's earlier cross-venue-gap failure probably applies to late entrants. That is an inference: there is no 2026 data.

### Gaps
- No public per-searcher profit distribution for Base, Sonic, Berachain or HyperEVM (e.g. "median searcher P&L") was found.
- No wallet-level study gives "X% of pump.fun snipers are net profitable after rugs".
- No independent (non-promotional) dataset of Virtuals Genesis returns across all launches, including failed or undersubscribed ones, was found.
- Sonic FeeM, Berachain and HIP-1-specific small-player results: no sources found.

## Q3. Capital, time, technical skill, capacity and key risks

### Takeaway
Capital is rarely the binding constraint. Latency, infrastructure and competition are. Mechanisms a non-engineer can do (Alpha points, Genesis points, points OTC) carry platform, rug and clawback risk. Mechanisms that need engineering (backrun, JIT, arb) are capacity-capped races where incumbents already hold the latency edge.

### Cited Findings
- HyperEVM arb capacity: 2M gas per block ÷ ~130K gas per arb ≈ 7–8 arbs per block. It got tight once more pools and DEXs launched — [TechFlow](https://www.techflowpost.com/en-US/article/28622)
- Base: over half of block gas is spam probes, and only 6–12% trade — [arXiv 2604.00234](https://arxiv.org/html/2604.00234). Losing probes still pay gas, so small searchers bleed fees
- Jito: the block engine ranks bundles by tip per compute unit, and losing bundles are dropped — [cryptomevbot](https://cryptomevbot.com/blog/jito-mev-solana-bot) [promo]
- Extended rebates are paid only if ≥$10 accrues in 24h, which alone requires ≥$50M/day of maker volume at 0.002% (arithmetic from [Extended docs](https://docs.extended.exchange/extended-resources/trading/trading-fees-and-rebates))
- Lighter Standard accounts have lower execution priority and rate limits than paid tiers, so zero fees come with worse queue position — [thundermessage](https://thundermessage.com/priced-against-lighter)
- Binance Alpha: some campaigns need up to 3 BNB, which is exposed to BNB price — [Forklog](https://forklog.com/en/the-race-for-alpha-points-a-trap-for-airdrop-hunters-or-binances-gold-mine/)
- Virtuals: selling allocations temporarily cuts points (a recurring-access penalty) — [Bankless](https://www.bankless.com/nonstop-virtuals-gains)
- Points OTC: settlement depends on the project's off-chain database and its cooperation — [Tiger Research](https://reports.tiger-research.com/p/point-market-airdrop-trading-eng). Deal-failure risk remains despite collateral — [pm.wiki](https://pm.wiki/projects/whales-market)
- Migrations: exchanges may skip dust (OKX excluded <1 FTM) and suspend trading for days (Kraken: 2–9 May 2025) — [Kraken](https://support.kraken.com/gb/articles/migration-of-ftm-to-s); [OKX](https://www.okx.com/cs/help/okx-to-support-ftm-token-migration)
- Crowded launches: 74.6% rug rate when ≥20 wallets buy in the creation block — [dev.to/quantbloc](https://dev.to/quantbloc/pumpfun-bundles-in-2026-what-happens-to-first-block-buyers-5ci9)

### Inferences (rough requirement table; built from the sources above plus judgement)
| Mechanism | Capital | Skill / time | Capacity for one small player | Main risks |
|---|---|---|---|---|
| Backrun / atomic arb (Base, HyperEVM, Sonic, Berachain) | $1–10K (gas + inventory; flash loans can replace inventory) | Solidity/Rust, own node or low-latency RPC, months of build | Tiny; winner-take-most per block | Gas bleed on failed probes, being outbid |
| JIT on v3/v4 | Pool-size inventory (often >$100K per big swap) | Builder/bundle integration | Very small; v4 hooks may internalise it | Inventory/IL, builder fees |
| pump.fun / launch sniping | $1–5K | Bot plus fast Solana RPC/Jito | Large but negative-median | Rugs, dev bundles, unsold bags |
| Virtuals Genesis points | VIRTUAL holdings (price risk) | Low | Point-capped allocations | Hype-cycle dependence, token drawdown |
| Binance Alpha | ~$1–3K + up to 3 BNB | Low, daily grind | One account ≈ $1K/yr gross | Unregistered in Malaysia, rule changes, volume costs |
| Points OTC / Pendle YT | Any | Low–medium | Market-limited | Project disqualification, airdrop below YT cost |
| Maker rebates | Margin for quoting | MM bot, risk engine | Needs ≥0.5% venue share | Adverse selection > rebate |
| Migration timing | Any | Low | Event-driven, rare | Deposit freezes, dust exclusion |

### Gaps
- No source gives measured infrastructure costs (RPC, colocation, Jito tip share) for a solo searcher in 2025–26.
- Clawback histories (airdrops revoked for "sybil" flags on honest single accounts) were not researched in this session.

## Q4. Free public data to backtest or measure each mechanism

### Takeaway
Most of these mechanisms can be measured for free on-chain. The repo's GitHub Actions fetch route (US servers) is needed because this sandbox blocks most hosts, including arxiv.org, bitquery.io and github.io in this session. The cheapest decisive Stage-1 measurements would be (a) the HyperEVM HYPE pool-vs-HyperCore gap and gas-competition profile, and (b) Virtuals Genesis full-population returns including failures.

### Cited Findings
- Jito tips can be measured from transfers to the eight public Jito tip accounts (the method Helius used) — [Helius](https://www.helius.dev/blog/solana-mev-report)
- Base/Optimism spam-MEV share and probe success were measured from public block data — [arXiv 2604.00234](https://arxiv.org/html/2604.00234)
- pump.fun sniper/bundle attribution was done by Bitquery from Solana on-chain data — [Bitquery](https://bitquery.io/investigations/pump-fun-snipers-bundles). Funding-network team detection uses public wallet funding graphs — [arXiv 2611.11436](https://arxiv.org/html/2611.11436)
- HyperEVM arbitrage targets public pools (HyperSwap HYPE/USDT0, PRJX). Hyperliquid's order-book prices are public — [TechFlow](https://www.techflowpost.com/en-US/article/28622). The repo already fetches Hyperliquid candles and funding (CLAUDE.md, "Existing data")
- Extended's rebate schedule and payout thresholds are public — [Extended docs](https://docs.extended.exchange/extended-resources/trading/trading-fees-and-rebates)
- Binance Alpha launch lists and per-airdrop thresholds are compiled publicly — [CMC 2025 recap](https://coinmarketcap.com/academy/uk/article/binance-alpha-2025-crypto-airdrops-token-launches)
- FTM→S migration timelines are on exchange support pages — [Kraken](https://support.kraken.com/gb/articles/migration-of-ftm-to-s)

### Inferences
- Candidate free measurements: (1) HyperEVM blocks (public RPC) for arb transactions per block, gas price paid and searcher-address concentration over 2025–26, i.e. a top-3 share test like the repo's #100; (2) Virtuals Genesis contracts on Base for each launch's raise, oversubscription and 7/30-day price versus allocation cost, all launches included; (3) a Solana RPC or Dune query on pump.fun creation-block buyers' 24h realised P&L by bot address; (4) Jito tip-account flows by searcher address for concentration; (5) Binance Alpha airdrop value per claim from public price data against points cost. Each should be pre-registered per CLAUDE.md before it runs.
- Expected verdicts (prior, untested): (1) concentrated, fails the small-entrant gate; (2) the only one with a plausible pass, but it depends on the hype cycle; (3) negative median; (4) concentrated; (5) below target on a single account.

### Gaps
- Whether Dune public dashboards exist for Virtuals Genesis, HyperEVM MEV or Sonic/Berachain searchers was not checked.
- EigenPhi and libmev coverage of Base, HyperEVM, Sonic and Berachain was not checked (both sites may need a GitHub Actions fetch).
- Full texts of the 2026 arXiv pump.fun papers (2607.02795, 2609.10246, 2610.39458, 2610.41597, 2611.11436) were not readable here. Their headline profit numbers for early-buyer and team-following strategies are unknown and worth fetching.

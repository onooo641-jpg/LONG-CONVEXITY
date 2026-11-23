# Capacity-limited trading edges for small capital (USD 10–15K), 2024–2026

Research date: 2026-11-23. Method: web search only. WebFetch could not reach arxiv.org, drops.dagstuhl.de or helius.dev from this
session (DNS blocked), so every paper figure below comes from search-engine summaries of abstracts and result pages,
not from reading the full text. Each figure is tagged by how it is known:
- **[paper]**: peer-reviewed or arXiv paper, abstract-level figure
- **[data-report]**: on-chain analytics or industry data report
- **[vendor]**: exchange, vendor or promotional blog (treat as anecdotal)
- **[repo]**: already measured in this repo (see `docs/HANDOFF_NONPROP.md`, `docs/CANDIDATES.md`)

Bottom line up front: I found **no measured, documented case of a small, non-colocated automated trader earning >100%/yr
net of costs in 2024–2026** in any of the suggested categories. The measured literature shows the opposite pattern: the
"capacity-limited" pies exist, but they are taken by a handful of small, very fast specialist bots. Most of the profit is
paid to block builders or validators, or burned on failed transactions. A USD 10K trader does not compete with large
funds. It competes with other small bots that are faster.

---

## Q1. Which capacity-limited edges have published evidence of high returns for small capital in 2024–2026, and how fast did they decay?

### Takeaway
None of the categories has published evidence that a small automated trader earned >100%/yr net. The best-measured
categories (CEX-DEX arbitrage, cross-chain arbitrage, L2/Solana atomic arbitrage) are highly concentrated. Profit per
trade is tiny. Most of the gross value goes to builders or validators. Cross-exchange CEX price gaps mostly disappeared after
April 2018. New-listing and memecoin "edges" with high reported win rates are insider schemes, not arbitrage.

### Cited Findings

**CEX-DEX arbitrage (Ethereum L1): highly concentrated, margins go to builders**
- [paper] Wu, Sui, Thiery and Pai, "Measuring CEX-DEX Extracted Value and Searcher Profitability" (AFT 2025, arXiv:2507.13023). Data: Aug 2023–Mar 2025 (19 months). 19 major CEX-DEX searchers extracted an estimated USD 233.8M from 7,203,560 identified CEX-DEX arbitrages. Three searchers took about three-quarters of both volume and extracted value. The authors list a dataset on Dune. — [arXiv abs](https://arxiv.org/abs/2507.13023v2); [AFT 2025 LIPIcs](https://drops.dagstuhl.de/storage/00lipics/lipics-vol354-aft2025/html/LIPIcs.AFT.2025.26/LIPIcs.AFT.2025.26.html)
- [paper] Same paper: searcher profitability is tied to integration with block builders. "Exclusive searchers maintain lower margins, sharing most of their extracted value with affiliated builders, sometimes even operating at negative net profit." — [arXiv html v3](https://arxiv.org/html/2507.13023v3)
- [paper] An AFT 2026 paper reports that eleven searchers account for >80% of identified CEX-DEX arbitrage volume, and the two largest alone for 49.2%. (Attributed by the search summary to LIPIcs.AFT.2026.21; the PDF was not opened.) — [AFT 2026 PDF](https://drops.dagstuhl.de/storage/00lipics/lipics-vol395-aft2026/LIPIcs.AFT.2026.21/LIPIcs.AFT.2026.21.pdf)
- [vendor/analysis] Ethereum arbitrage has a high bid-to-profit ratio. Illustrative example: on a USD 100 arbitrage the searcher bids USD 90 to the builder and keeps USD 10. Hundreds of addresses attempt arbitrage, but the core group that wins bids "often does not exceed 20 in any given week". Most others are "peripheral participants who capture sporadic, lower-value opportunities". (Illustrative, not measured.) — [Extropy HackMD](https://hackmd.io/@Extropy/ArbAnalysis)
- [paper] Builder concentration: MEV-Boost produces about 90% of Ethereum blocks. Three builders (beaverbuild, rsync, Titan) produced about 80% of MEV-Boost blocks in Oct 2023–Mar 2024. (From a search summary; the exact source paper is uncertain. It appeared alongside arXiv:2407.07474 "Searcher Competition in Block Building".) — [arXiv 2407.07474](https://arxiv.org/html/2407.07474v1)

**Cross-chain arbitrage: real and growing, but inventory-based, fast and centralised**
- [paper] Öz et al., "Cross-Chain Arbitrage: The Next Frontier of MEV in DeFi" (arXiv:2501.17335 v2, Jun 2025; ACM DOI 10.1145/3771566, Dec 2025). Data: 242,535 trades, USD 868.64M volume, nine chains, Sep 2023–Aug 2024. 66.96% of trades use pre-positioned inventory and settle in about 9 s. Bridge-based arbitrages take about 242 s. Activity clusters on Ethereum-centric L1–L2 pairs, grew 5.5x over the period and surged after the Dencun upgrade. — [arXiv html v2](https://arxiv.org/html/2501.17335v2)
- [paper] v1 of the same work ("Pandora's Box", Jan 2025): 260,808 cross-chain arbitrages, 32.37% involving bridges. It flags centralisation among arbitrageurs, congestion from failed transactions and growing private-mempool use. — [arXiv abs v1](https://arxiv.org/abs/2501.17335v1); [Flashbots summary page](https://www.flashbots.net/cross-chain-arbitrage)
- [paper] Mancino et al., "Bunny Hops and Blockchain Stops" (arXiv:2511.17527, BRAINS 2025). 2.4B transactions, 12 chains, 45 bridges, Sep 2023–Aug 2024. Multi-hop cross-chain arbitrage opportunities are "exceedingly infrequent". — [arXiv abs](https://arxiv.org/abs/2511.17527v2)
- Note: all three cross-chain studies use the same Sep 2023–Aug 2024 window. I found no measurement for 2025–2026.

**L2 / rollup atomic arbitrage: low cost, low profit, spam-heavy**
- [paper] Torres et al., "Rolling in the Shadows" (arXiv:2405.00138, v3 Sep 2025). Arbitrum, Optimism and zkSync over 32 months. MEV trading volume on rollups is comparable to Ethereum's. Costs are lower, but profits are "significantly lower" than on Ethereum. No sandwiching was detected on popular rollups. — [arXiv abs](https://arxiv.org/abs/2405.00138)
- [paper] arXiv:2406.02172: arbitrage on Arbitrum, Base and Optimism pools is 0.03%–0.05% of trading volume. On zkSync Era it is about 0.25%. — [arXiv html](https://arxiv.org/html/2406.02172v2)
- [paper] Wu and Öz (Flashbots), "To Wait or To Probe: Arbitrage Competition on High-Throughput Blockchains" (AFT 2026, arXiv:2606.00720). Base, 1 Jun 2025–28 Feb 2026. "Probabilistic" searchers (who submit transactions that check on-chain state) are 23% of arbitrage activity but produce 95% of spam and use 20% of Base gas. After Base's configuration changes, fee revenue shifted toward successful arbitrages, probabilistic bots paid higher priority fees and spam used less blockspace. — [Flashbots Collective post](https://collective.flashbots.net/t/to-wait-or-to-probe-arbitrage-competition-on-high-throughput-blockchains/5759); [AFT 2026 record](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.AFT.2026.24)
- [paper] "There Will Be Spam: Characterizing State-Invariant Transactions and Speculative MEV" (arXiv:2607.24172) exists but could not be read. Content unknown. — [arXiv PDF](https://arxiv.org/pdf/2607.24172)

**Solana atomic arbitrage: huge count, tiny average, shrinking pie**
- [data-report] Jito's detector found 90,445,905 successful Solana arbitrage transactions over one year. Average profit was USD 1.58 per arbitrage and the largest single one was USD 3.7M. Jito's data excludes searcher-side profit and activity in alternative mempools. — [Helius Solana MEV report](https://www.helius.dev/blog/solana-mev-report)
- [data-report] Decay: Jito protocol revenue fell for a fifth straight quarter in Q2 2026, down 45% quarter on quarter, from a peak of USD 26.1M in Q1 2025. The search summary gives Q2 2026 revenue as USD 1.28M; the URL slug reads "128m", so verify. Jito tips fell about 50% to about USD 9.9M in Q2 2026. Jito BAM reached 33% of Solana stake (launched Sep 2025). — [Solana Compass](https://solanacompass.com/news/jito-q2-2026-protocol-revenue-falls-45-to-128m-as-bam-reaches-33-of-solana-stake)
- [vendor] 2025 Solana MEV totals conflict: one source says over USD 720M and another over USD 400M, under different definitions. — [Coinmonks/Medium](https://medium.com/coinmonks/solana-mev-enters-a-new-phase-how-firedancer-and-alpenglow-change-the-game-6eba6bd0efb3); [Business Model Analyst](https://businessmodelanalyst.com/the-400-million-mev-problem-how-solanas-block-production-became-a-competitive-sport/)

**Solana memecoin / pump.fun sniping: the high win rates are insider schemes**
- [data-report] Pine Analytics, "Exit Liquidity Machines": 4,600+ deployer-funded sniper wallets tied to 10,400+ deployers (about 1.75% of launch activity) had an 87% profitability rate. This applies only to wallets funded by the token's deployer before launch that bought in the same block. 85% sold within 5 minutes. — [Pine Analytics](https://pineanalytics.substack.com/p/exit-liquidity-machines); [BeInCrypto summary](https://beincrypto.com/pump-fun-meme-coin-snipers-systematic-problem)
- [data-report] Bitquery: 74% of pump.fun gains cannot be replicated by copy traders. — [KuCoin flash](https://www.kucoin.com/news/flash/bitquery-study-reveals-74-of-pump-fun-gains-cannot-be-replicated-by-copy-traders)
- [paper] arXiv:2607.02795 (Jul 2026) describes 1,012 persistent wallet rings among coordinated sniper cohorts. Not opened. — [arXiv abs](https://arxiv.org/abs/2607.02795)
- [vendor] Bots generate 60–80% of trading volume on some pump.fun tokens (May 2025). — [BeInCrypto](https://beincrypto.com/trading-bots-pump-fun-solana-meme-coins)

**New-token listing effects (CEX/DEX): directional drift, not arbitrage, and already priced in**
- [data-report] RockawayX, Binance/Bybit/MEXC listings: prices run up in the week before listing, rise at +7 days, and fall at 30 and 60 days. — [RockawayX](https://rockawayx.com/insights/bullish-or-bearish-what-really-happens-when-tokens-list-on-a-cex)
- [data-report] BitMEX Q1 2025 derivatives report: 70.83% of tokens perp-listed on OKX hit their all-time high on listing day; on Binance 50%. — [BitMEX blog](https://www.bitmex.com/blog/2025q1-derivatives-report)
- [data-report] The Tie (2026): after adjusting for BTC, most of the listing move happens before the token goes live. The announcement, not the listing, is the catalyst. — [The Tie](https://www.thetie.io/insights/what-does-an-exchange-listing-actually-deliver-in-2026)
- I found **no study that measures DEX-vs-CEX price gaps around listing time**.
- [repo] Hyperliquid post-listing shorts (#44) and new-perp funding spikes (#37) were already tested and failed. — `docs/HANDOFF_NONPROP.md`

**Cross-exchange CEX arbitrage (including small/regional venues): decayed after 2018**
- [paper] Crépellière, Pelster and Zeisberger, "Arbitrage in the Market for Cryptocurrencies" (J. Financial Markets 2023, DOI 10.1016/j.finmar.2023.100817). Price deviations "hardly exist since April 2018". The remaining gaps do not give meaningful returns after costs. A related study cited in coverage estimated more than USD 377M of opportunities in 2017 and USD 384M in Q1 2018 alone. — [Paderborn working paper](https://wiwi.uni-paderborn.de/fileadmin-wiwi/cetar/TAF_Working_Paper_Series/TAF_WP_067_CrepellierePelsterZeisberger2022_rev.pdf); [Decrypt summary](https://decrypt.co/245963/professor-coin-free-lunch-cryptocurrency-markets)
- [paper] Finance Research Letters vol. 71 (2025) art. 106364: minute data, 16 exchanges, Apr 2013–Apr 2024. Arbitrage opportunities last longer when higher-risk exchanges are involved. High fees and blockchain congestion slow capital transfers. — [Cardiff ORCA PDF](https://orca.cardiff.ac.uk/173664/1/1-s2.0-S154461232401393X-main.pdf)
- [paper] Hautsch, Scheuch and Voigt, "Building Trust Takes Time": cross-exchange BTC gaps track settlement latency and are smaller between low-default-risk exchanges. Most gaps are too small to trade once transaction costs and settlement risk are counted. — [arXiv 1812.00595](https://arxiv.org/abs/1812.00595)
- [paper] Barbon and Ranaldo, "On the Quality of Cryptocurrency Markets" (Sep 2024 version): deviations from no-arbitrage are much larger on DEXs than CEXs, and they rise with gas fees. — [arXiv html v7](https://arxiv.org/html/2112.07386v7)
- [paper] Borri and Shakhnov: sizable, persistent BTC dollar-price discounts across 165 exchanges, explained by capital controls and venue frictions. (Cited in arXiv:2510.14435.) — [arXiv 2510.14435](https://arxiv.org/pdf/2510.14435)
- [repo] MYR crypto price gaps (#51) were already tested here: negative or tiny. — `docs/HANDOFF_NONPROP.md`

**Hyperliquid HIP-3 / pre-launch "hyperps": new markets, no measured returns**
- [data-report] HIP-3 open interest went from about USD 280M at the start of 2026 to a record USD 2.38B in April 2026. — [The Block, 2026-04-15](https://www.theblock.co/news/web3/2026-04-15-hip-3-open-interest-2-billion-demand-24-7-tokenized-equity-exposure-397276)
- [data-report] One deployer (Trade.xyz) holds more than 90% of HIP-3 open interest. An October 2026 count found 315 markets with USD 4.08B OI, with six of ten HIP-3 exchanges at zero OI on every market. Sources disagree on peak OI figures. — [CoinStats news](https://coinstats.app/news/26ccbcd2cb983c0b84bb401326151b5912586ecf434934c607df0543fc7977a2_315-perpetual-markets-on-stocks-gold-and-oil-what-to-watch-on-Hyperliquids-HIP3-exchanges/); [BlockEden](https://blockeden.xyz/blog/2026/04/29/hyperliquid-hip3-builder-markets-1b-oi-commodities/)
- [vendor] HIP-3 fees are about double standard Hyperliquid fees: about 3 bp maker and 9 bp taker before discounts. (Single source; verify against HL docs.) — [BlockEden](https://blockeden.xyz/blog/2026/04/29/hyperliquid-hip3-builder-markets-1b-oi-commodities/)
- [data-report] Coin Metrics: since Jan 2026, HL BTC-perp funding has been 1.95x more volatile than Binance BTC-perp and 3.32x more volatile than Deribit BTC-perp. — [Coin Metrics SOTN 368](https://coinmetrics.substack.com/p/state-of-the-network-issue-368)
- [data-report] Messari studied price discovery in Hyperliquid weekend markets (HIP-3 equity/commodity perps trade while CME and the NYSE are closed). Returns to arbitrageurs were not shown in the snippet. — [Messari](https://messari.io/report/weekend-trading-evidence-of-price-discovery-in-hyperliquid-s-weekend-markets)
- [official docs] Hyperps (pre-launch perps) have no spot or index oracle. Funding is set relative to a moving average of the hyperp's own mark price. The docs warn that heavy one-way momentum makes funding strongly favour the opposite side for the next 8 hours. — [Hyperliquid docs: hyperps](https://hyperliquid.gitbook.io/hyperliquid-docs/trading/hyperps)
- [data-report] Examples of hyperp volatility: the MON hyperp priced Monad at about USD 15B FDV. The PUMP hyperp peaked at USD 0.015 and fell to USD 0.0055. — [The Block](https://www.theblock.co/news/markets/2025-10-08-hyperliquid-lists-hyperps-monad-token-373750); [Coinfomania](https://coinfomania.com/hyperliquid-pump-usd-hyperp-launch/)

**Options market-making on small venues (Derive, Aevo): no return data for small makers**
- [data-report] Derive's share of on-chain options premiums (Derive + Aevo + Paradex) rose from 78% to 96%, and Aevo's share shrank. — [CryptoRank](https://cryptorank.io/insights/research/onchain-options-premiums-more-than-tripled-in-2026-as-derive-pulled-ahead)
- [vendor] FalconX has quoted on Derive since Oct 2025, and Derive runs a market-maker incentive programme. Derive-linked material has conflicts of interest. — [Derive insights (FalconX repost)](https://insights.derive.xyz/exploring-derives-record-options-surge/); [Alea Research](https://alearesearch.substack.com/p/derive-onchain-options-built-for)
- [data-report] Retail options-vault AUM is small (Ribbon about USD 4M, Typus about USD 1.7M on DefiLlama). — [DefiLlama dashboard](https://defillama.com/pro/onchain-options-bkus9n)
- I found no realised-return figures for small or retail options market makers on Derive, Aevo or Deribit alt options.

**AMM liquidity provision / JIT: only the fastest LPs profit**
- [data-report] Uniswap Labs: the only group that consistently beat holding was "flash" (JIT) LPs who provide liquidity for one block. JIT filled about 0.3% of liquidity demand (2022 data). — [Uniswap blog](https://blog.uniswap.org/jit-liquidity)
- [paper] A 2025 markout analysis of the ETH–USDC 5 bp pool found that both mean and median LP returns are negative. — [AFT 2025 LIPIcs.AFT.2025.8](https://drops.dagstuhl.de/storage/00lipics/lipics-vol354-aft2025/html/LIPIcs.AFT.2025.8/LIPIcs.AFT.2025.8.html)
- [paper] An earlier study found about 50% of Uniswap v3 positions lose money. — [arXiv 2205.08904](https://arxiv.org/pdf/2205.08904)

**Funding-rate arbitrage (CEX vs DEX)**
- [paper] An MDPI 2026 study of funding rates across 26 exchanges and 812 symbols (Nov 2025–Jan 2026) finds CEXs dominate price discovery with 61% higher integration than DEXs. Its delta-neutral return figures were not in the snippet. — [MDPI Mathematics 14(2):346](https://www.mdpi.com/2227-7390/14/2/346)
- [vendor] DEX–CEX funding divergence "can sometimes exceed 0.1% per hour" in extreme conditions (anecdotal). — [OneKey blog](https://onekey.so/blog/ecosystem/funding-rate-divergence-dex-cex/)
- [repo] Already tested here: cross-venue funding gaps on HL/dYdX/Aevo/Deribit failed on execution costs. Extreme-funding harvest on HL small caps vanished after 2024. Rotating carry in 2024–26 gave 2.9–6.4%/yr and was falling (#57). — `docs/HANDOFF_NONPROP.md`

### Inferences
- **The capacity limit protects small bots from large funds, not from other small bots.** CEX-DEX (top 3 = 75%), Ethereum
  arbitrage (≤20 weekly winners), Base (probabilistic spam = 20% of gas) and Solana (USD 1.58 average arbitrage) all point
  the same way: whoever has the lowest latency and the best builder or validator access takes the pie, whatever their capital.
  A USD 10–15K trader has no capital advantage here, because these strategies use flash loans or tiny inventory.
- **Decay is fast and visible.** CEX cross-exchange gaps were gone by April 2018. Solana MEV revenue (Jito) fell five
  quarters in a row from Q1 2025 to Q2 2026. Builder and validator auctions push searcher margins toward zero. This repo already saw
  HL extreme-funding harvest vanish after 2024. I would assume a half-life of months, not years, for any newly found
  on-chain arbitrage.
- **The one structural niche with some support is inventory-based cross-chain arbitrage.** 67% of cross-chain arbitrages
  use pre-positioned inventory, so capital spread across chains is the barrier, not flash-loan atomicity. That favours
  mid-size inventory holders. A USD 10–15K trader can hold only small inventory per chain, which caps trade size. It is
  "capacity-limited" in the wrong direction for a small trader. Centralisation was already reported in 2023–24.
- **High-win-rate memecoin sniping is mostly insider coordination** (deployer-funded wallets). Copying it means copying
  manipulation. It is not a legitimate structural edge and should stay out of scope.
- **Listing effects are directional drift, not arbitrage.** They are already tested (#37, #44) or announced before listing.
- **HIP-3 is the newest market structure (2026).** Its builder-deployed markets are thin (6 of 10 deployers had zero OI by Oct 2026)
  and fees are double. The likely edges are passive market making on thin builder markets, which resembles the failed thin-dYdX
  MM result (~USD 15/day), and weekend basis versus the CME/NYSE reopen, which is directional risk. No returns are documented.
- **The repo's existing lesson holds.** Rule-based subsidies (prop-firm evaluations, liquidation bonuses) beat market-pricing
  edges. Even liquidation bonuses, the best "capacity-limited" candidate here, came out as "pie exists, median new bot USD 0".

### Gaps
- No public, verifiable P&L found for any small or retail automated trader earning >100%/yr net in 2024–2026 (no Dune
  dashboard, no audited open-source bot with reported results). Claims of this kind found in passing were promotional.
- Searcher-level profit distribution for Solana and for Base probabilistic bots: I found no paper with the full
  distribution (the share of small or new searchers that are net profitable).
- Cross-chain arbitrage measurements stop in Aug 2024. No 2025–2026 update found.
- Full texts of arXiv:2606.00720, 2607.24172, 2607.02795 and the AFT 2026 papers could not be read (arxiv.org and
  drops.dagstuhl.de were blocked for WebFetch in this session). Figures beyond the abstracts are unknown.
- No measured realised returns for small options makers on Derive or Aevo, or for HIP-3 market makers.
- No study of DEX vs small-CEX price gaps at token launch.

---

## Q2. For each edge: required capital, latency/infrastructure, main costs, and the share a non-colocated bot can capture

### Takeaway
For atomic or near-atomic on-chain arbitrage, capital is not the constraint: flash loans make it close to zero. Latency and
inclusion access are the constraint, and the measured capture share for a slow newcomer is probably near zero. The repo's
own liquidation replay found that 64–94% of events land in the same block as the price update. For inventory strategies
(cross-chain, market making), capital is the constraint, and USD 10–15K caps both size and absolute income.

### Cited Findings
- Latency and settlement: inventory-based cross-chain arbitrage settles in about 9 s, versus about 242 s for bridge-based arbitrage. [paper] — [arXiv 2501.17335v2](https://arxiv.org/html/2501.17335v2)
- Inclusion cost on Ethereum: profit goes largely to builders. Exclusive searchers share "most of their extracted value" with builders and sometimes run at a net loss. [paper] — [arXiv 2507.13023v3](https://arxiv.org/html/2507.13023v3)
- Illustrative bid-to-profit: a USD 90 bid on USD 100 of profit. [vendor/analysis] — [Extropy HackMD](https://hackmd.io/@Extropy/ArbAnalysis)
- Failed-transaction and spam cost on L2: probabilistic bots produce 95% of spam and use 20% of Base gas. After the configuration change they pay higher priority fees. [paper] — [Flashbots Collective](https://collective.flashbots.net/t/to-wait-or-to-probe-arbitrage-competition-on-high-throughput-blockchains/5759)
- Rollup economics: lower costs but "significantly lower" profits than Ethereum. [paper] — [arXiv 2405.00138](https://arxiv.org/abs/2405.00138)
- Size of the L2 arbitrage pie: 0.03–0.05% of pool volume on Arbitrum, Base and Optimism; about 0.25% on zkSync Era. [paper] — [arXiv 2406.02172](https://arxiv.org/html/2406.02172v2)
- Solana: average arbitrage profit USD 1.58 across about 90M arbitrages a year. [data-report] — [Helius](https://www.helius.dev/blog/solana-mev-report)
- CEX cross-exchange: high fees and blockchain congestion slow capital transfers, and gaps persist only around higher-risk exchanges. [paper] — [Cardiff ORCA](https://orca.cardiff.ac.uk/173664/1/1-s2.0-S154461232401393X-main.pdf)
- HIP-3 trading costs: about 3 bp maker and 9 bp taker before discounts (single source). [vendor] — [BlockEden](https://blockeden.xyz/blog/2026/04/29/hyperliquid-hip3-builder-markets-1b-oi-commodities/)
- Hyperps: no spot to hedge before launch, and funding swings against momentum over 8 h windows. [official docs] — [Hyperliquid docs](https://hyperliquid.gitbook.io/hyperliquid-docs/trading/hyperps)
- LP adverse selection: mean and median LP markouts are negative in the ETH–USDC 5 bp pool. Only one-block JIT LPs beat holding. [paper/data-report] — [AFT 2025.8](https://drops.dagstuhl.de/storage/00lipics/lipics-vol354-aft2025/html/LIPIcs.AFT.2025.8/LIPIcs.AFT.2025.8.html); [Uniswap blog](https://blog.uniswap.org/jit-liquidity)
- [repo] Liquidation replay (closest in-repo analogue): 64–78% of Aave-fork liquidations land in the same block as a price update. Reachable share for a perfectly fast watcher: 13% by count / 10% by value. On Morpho Base, 93.8% land in the oracle-update block, so the reachable share is 2.1% of events / 0.8% of value. — `docs/CANDIDATES.md` row #100

### Per-strategy summary table (my synthesis from the findings above; the capture estimates are inferences, not measurements)

| Strategy | Capital needed | Latency / infra | Main costs | Plausible capture share for a non-colocated hobby bot | Evidence of >100%/yr for small capital |
|---|---|---|---|---|---|
| ETH L1 CEX-DEX arbitrage | Large CEX inventory + hedging account | Builder integration, sub-block CEX execution | Builder bids (most of the profit), CEX fees | ~0 (top 3 = 75%) | None |
| L2 (Base/Arb/OP) atomic DEX arbitrage | ~0 (flash loans) + gas float | Sequencer proximity; on Base, flashblocks-level speed | Priority fees, failed-tx gas (spam = 20% of Base gas) | Very low; same-block competition | None |
| Solana atomic arbitrage | ~0 + SOL for tips | Staked RPC / Jito / BAM, co-located | Tips, failed transactions | Very low; USD 1.58 average arbitrage | None |
| Cross-chain inventory arbitrage | Inventory on each chain (USD 10K spread thin) | ~9 s settlement; multi-chain nodes | Gas on both sides, inventory rebalancing, bridge fees | Unknown; centralisation reported | None |
| Long-tail DEX arbitrage on new or small chains | ~0–5K | Block-level watcher | Gas; rug/honeypot tokens | Unknown; pie small | None |
| Pump.fun sniping | 1–5K | Same-block | Fees, rugs | Profitable subset is insider-funded | Insider subset only (87% win rate); not legitimate |
| Listing drift (CEX/HL) | 5–15K | Low | Fees, funding | Already tested (#37, #44): fails | None |
| HIP-3 thin-market MM / weekend basis | 10–15K | Low–medium | 2x fees, adverse selection, gap risk | Unknown | None |
| Derive/Aevo options MM | 15K+ margin | Medium; vol-surface model | Adverse selection, hedging | Unknown; FalconX and pro makers quote there | None |
| Regional CEX price gaps | Accounts on both venues | Low | Withdrawal fees, transfer time, KYC | Tested (#51 MYR): tiny | None |

### Inferences
- For flash-loan strategies, capital is irrelevant. "Capacity-limited" there means "latency-limited", and that favours specialists, not small traders.
- For inventory strategies, a USD 10–15K bankroll means absolute income is capped. Even 1% of the 2023–24 cross-chain volume
  (USD 868.64M/yr) at plausible margins would be small, and a newcomer would capture a fraction of that.
- To reach >100%/yr on USD 10–15K (USD 10–15K/yr of profit), a bot would need to win roughly 6,300–9,500 Solana arbitrages
  a year at the USD 1.58 average, net of tips and failures. That implies a sustained win rate against Jito-integrated searchers.
  No evidence supports this for a non-colocated bot.

### Gaps
- No public measurement of the share of DEX arbitrage opportunities that stay open for more than 1 block, or more than 2 s, on
  Base, Arbitrum or Solana. This is the key quantity for a non-colocated bot. It could be measured with the repo's existing
  RPC replay code (see Q4).
- No figure for the net profitability of probabilistic (spam) searchers on Base after the 2025–26 fee changes.

---

## Q3. Which venues and data sources are reachable from Malaysia and from US-hosted GitHub Actions runners?

### Takeaway
Binance and Bybit are off-limits for a Malaysia resident: Binance lists Malaysia as a Restricted Location, and the SC ordered
Bybit out in Dec 2024. Binance futures APIs return HTTP 451 from US cloud IPs. Hyperliquid's public info API (funding and
candles), public EVM RPCs, GeckoTerminal's keyless API and Dune are the usable free data routes. Hyperliquid's own S3
archive is requester-pays, which needs an AWS bill, so it needs Jx's approval.

### Cited Findings
- Binance's terms list the United States and **Malaysia** (and Ontario) as Restricted Locations. — [Binance API FAQ / terms via search summary](https://www.binance.com/en/support/articles/360004492232)
- Binance APIs return HTTP 451 "Unavailable For Legal Reasons" to restricted-region IPs. `fapi.binance.com` (futures) returns 451 from the US. Many cloud and datacenter IP ranges are blocked. Forum users cite `data-api.binance.vision` / `data.binance.vision` for public spot market data. Whether these work from GitHub Actions is unverified. — [Binance dev forum: 451 from US](https://dev.binance.vision/t/error-451-when-accessing-the-futures-api-from-us/16725); [Vercel community](https://community.vercel.com/t/binance-api-calls-on-vercel/29895); [QuotaGuard](https://quotaguard.com/blog/binance-futures-api-static-ip)
- Securities Commission Malaysia ordered Bybit Technology Ltd (order dated 11 Dec 2024, announced 27 Dec 2024) to disable its website and apps for Malaysia within 14 business days and to stop promotion to Malaysian investors. Bybit had been on the SC Investor Alert List since July 2021. — [SC media release](https://www.sc.com.my/resources/media/media-release/sc-takes-enforcement-action-against-bybit-for-illegally-operating-dax-in-malaysia); [The Block](https://www.theblock.co/news/business/2024-12-29-malaysia-orders-bybit-to-halt-local-operations-over-registration-failure-332552)
- The SC ordered Huobi Global to cease in May 2023 (single secondary source). — [The Block](https://www.theblock.co/post/332552/malaysia-orders-bybit-to-halt-local-operations-over-registration-failure)
- SC-registered digital asset exchanges (RMOs) include Luno Malaysia. Counts differ by source (5–6 as of late 2025 / Sep 2026), so check the SC list. — [SC list](https://www.sc.com.my/regulation/guidelines/recognizedmarkets/list-of-registered-digital-asset-exchanges); [FinTech News MY](https://fintechnews.my/regulated-crypto-exchanges-malaysia/)
- Hyperliquid info API: `POST https://api.hyperliquid.xyz/info` with `type: "fundingHistory"` needs no key, account or signature. A third party documents about 500 entries per call. — [Chainstack docs](https://docs.chainstack.com/reference/hyperliquid-info-funding-history); [GoldRush docs](https://goldrush.dev/docs/api-reference/hyperliquid-info/funding-history)
- Hyperliquid S3: the `hyperliquid-archive` bucket holds l2Book snapshots and asset contexts and is updated about monthly. Trades and fills are in `hl-mainnet-node-data`. Both are **requester-pays**: anonymous access is refused, and an AWS account with billing is needed. Data can be missing. — [Hyperliquid docs: historical data](https://hyperliquid.gitbook.io/hyperliquid-docs/historical-data); [Dwellir guide](https://www.dwellir.com/blog/how-to-get-historical-hyperliquid-data)
- GeckoTerminal public API: free, no authentication, 30 calls/min. Pool OHLCV endpoint `api.geckoterminal.com/api/v2/networks/{net}/pools/{addr}/ohlcv/{tf}`. I found no official free history depth; a third-party page implies about 6 months, so verify. CoinGecko has an "extended historical data for onchain OHLCV" changelog item, probably for paid plans. — [GeckoTerminal API guide](https://apiguide.geckoterminal.com/faq); [CoinGecko keyless API](https://docs.coingecko.com/docs/keyless-public-api); [CoinGecko changelog](https://docs.coingecko.com/changelog/extended-historical-data-for-onchain-ohlcv-endpoint)
- The CEX-DEX paper publishes its dataset on Dune. — [arXiv 2507.13023](https://arxiv.org/abs/2507.13023v2)
- [repo] `scripts/fetch_public.py` already has public-RPC helpers (`rpc()`, block-timestamp bisection, log scans used for the liquidation replays) and Hyperliquid funding/candle jobs. GitHub Actions already reaches HL, DefiLlama and public EVM RPCs (publicnode, llamarpc). Polymarket is blocked from US servers (#40). — `scripts/fetch_public.py`, `docs/HANDOFF_NONPROP.md`

### Inferences
- Any edge that needs execution on Binance, Bybit, OKX or Huobi is out of scope for Jx: these are restricted or ordered out in Malaysia. Using them would be the kind of geoblock and rule evasion the repo excludes. Their public data can at most serve as a reference price, and only through endpoints that answer US runners normally, with no proxy.
- Execution venues plausibly open to a Malaysia resident without evasion are permissionless on-chain venues (DEXs on L2s or Solana, Hyperliquid, Derive) and SC-registered MY exchanges. Check each venue's terms for its own restricted-country list before live use. I did not verify Hyperliquid's or Derive's terms for Malaysia in this pass.
- For backtests, the reachable free stack is: public EVM/Solana RPC logs (swap events), HL info API (funding, candles), GeckoTerminal OHLCV (coarse, minute bars at best), and Dune (SQL over decoded DEX trades; free tier has query-credit limits).

### Gaps
- Whether `data.binance.vision` and `data-api.binance.vision` answer GitHub Actions runners normally: not verified.
- Hyperliquid's and Derive's own restricted-jurisdiction lists for Malaysia: not checked here.
- GeckoTerminal free OHLCV history depth and trades-endpoint window: no official figure found.
- Dune free-tier limits for 2026: not checked.

---

## Q4. Academic and empirical evidence on returns to small or "retail-sized" arbitrageurs and the decay of such edges

### Takeaway
The literature measures concentration and decay, not small-trader success. Every 2024–2026 measurement found shows a few
dominant searchers, profit leaking to infrastructure owners (builders, validators, sequencers), and shrinking pies. Classic
CEX arbitrage decayed after early 2018. Remaining gaps survive only where settlement risk, counterparty risk or capital
controls make them unsafe or unreachable.

### Cited Findings
- Concentration: 3 searchers ≈ 75% of CEX-DEX value (Aug 2023–Mar 2025) — [arXiv 2507.13023](https://arxiv.org/abs/2507.13023v2). 11 searchers >80% and the top 2 at 49.2% (AFT 2026) — [LIPIcs AFT 2026.21](https://drops.dagstuhl.de/storage/00lipics/lipics-vol395-aft2026/LIPIcs.AFT.2026.21/LIPIcs.AFT.2026.21.pdf)
- Margin capture by infrastructure: exclusive searchers sometimes have negative net profit after sharing with builders — [arXiv 2507.13023v3](https://arxiv.org/html/2507.13023v3)
- CEX gap decay: "price deviations hardly exist since April 2018" — [Crépellière et al. WP](https://wiwi.uni-paderborn.de/fileadmin-wiwi/cetar/TAF_Working_Paper_Series/TAF_WP_067_CrepellierePelsterZeisberger2022_rev.pdf)
- Persistence only with risk: longer-lasting gaps involve higher-risk exchanges — [FRL 2025](https://orca.cardiff.ac.uk/173664/1/1-s2.0-S154461232401393X-main.pdf). Gaps track settlement latency and default risk — [Hautsch et al.](https://arxiv.org/abs/1812.00595)
- Solana pie shrinking: Jito revenue down five quarters in a row from a Q1 2025 peak; tips down about 50% in Q2 2026 — [Solana Compass](https://solanacompass.com/news/jito-q2-2026-protocol-revenue-falls-45-to-128m-as-bam-reaches-33-of-solana-stake)
- Rollups: lower profit than L1 despite lower costs — [arXiv 2405.00138](https://arxiv.org/abs/2405.00138)
- Copy-trading of memecoin winners fails: 74% of gains are not replicable — [KuCoin/Bitquery](https://www.kucoin.com/news/flash/bitquery-study-reveals-74-of-pump-fun-gains-cannot-be-replicated-by-copy-traders)
- LPs: the median LP loses versus markout, and only JIT LPs profit — [AFT 2025.8](https://drops.dagstuhl.de/storage/00lipics/lipics-vol354-aft2025/html/LIPIcs.AFT.2025.8/LIPIcs.AFT.2025.8.html); [Uniswap](https://blog.uniswap.org/jit-liquidity)

### Inferences
- "Small capital earns >100%/yr because big capital can't scale" is real as a mechanism (pies of USD 1–100K/month on
  long-tail venues). The beneficiaries, though, are a few low-latency specialists. A non-professional should expect
  the median outcome of the repo's liquidation work: pie exists, median new bot ≈ USD 0.
- The only small-capital edges with Topstep-like ROI that this repo has confirmed are rule-based subsidies, not
  pricing inefficiencies. The literature found here does not contradict that.

### Candidate tests with free data (new angles, not repeats of tested items). These are suggestions for pre-registration, not results.
1. **"Slow-bot reachable share" for L2 DEX arbitrage (Base, Arbitrum).** Reuse the liquidation-replay method: from public-RPC
   swap logs (Uniswap v2/v3/Aerodrome pools of long-tail tokens), find cross-pool price gaps above fees+gas, and measure what
   share stays open for at least 1 block (or at least 2 s). Stage 1: one chain, 2 weeks, 20 pools. Kill if the reachable net
   value is below about USD 300/month. Data: public RPC `eth_getLogs` (already used in `fetch_public.py`).
2. **Inventory cross-chain gap persistence (Base ↔ Arbitrum ↔ Optimism, same token).** Use block-aligned DEX prices from
   swap logs. Measure gaps above fees+gas+rebalancing that last at least 9 s, the median inventory-arbitrage settlement time in
   arXiv 2501.17335. Kill if, after a 50% haircut for competition, net is below USD 1,000/month on USD 10K of inventory.
3. **HIP-3 weekend basis to Monday open.** HL candles for HIP-3 equity/commodity perps vs Friday close / Monday open. This is
   a directional or basis test, not arbitrage, and HL candles are free. Only worth running if Stage 0 confirms Malaysian
   access to the relevant HIP-3 deployer and 2x fees are included.
- Not recommended: Solana atomic arbitrage (needs Jito/BAM co-location; USD 1.58 average), pump.fun sniping (the profitable
  subset is insider-funded), CEX listing drift (tested #37/#44), regional CEX gaps (tested #51), cross-venue funding (tested),
  options MM on Derive (no free historical order-book data found; pro makers present).

### Gaps
- No academic paper found that directly estimates the net returns of a small or newly entering searcher cohort. Papers measure the top of the distribution.
- No published half-life estimates for 2024–2026 DEX arbitrage edges. Decay evidence is indirect (revenue series, concentration).
- Derive/Aevo historical order-book or trade data availability (free) was not established.

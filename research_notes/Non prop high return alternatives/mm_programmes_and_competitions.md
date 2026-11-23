# Exchange-funded income for a small automated trader: maker rebates, MM / liquidity reward programmes and trading competitions (2025–2026)

Research date: 2026-11-23. Method: web search only. WebFetch could not reach the official docs hosts (`hyperliquid.gitbook.io` and `docs.dydx.xyz` failed DNS in this sandbox because they are outside the allowed network domains), so no official page was opened in full. Figures marked **[official, snippet]** come from search-result excerpts of the venue's own pages. Figures marked **[third-party]** come from aggregators, guides or news. Figures marked **[inference]** are my own arithmetic. Every fee figure should be checked against the live page before a pre-registration uses it.

## Bottom line: can USD 10–15K earn USD 15–20K/yr (>100%/yr) from exchange subsidies?

### Takeaway
No, not on the evidence found. On the large perp DEXs, maker rebates go only to accounts that already hold a big share of exchange-wide maker volume, or that do tens of millions of dollars a day. At a size a USD 10–15K account can plausibly fill, the rebates are 0.01–0.25 bp, or the maker pays a positive fee. Reward programmes with published budgets have gone mostly to the top one or two firms. Competition prizes are top-heavy ROI lotteries, mostly on CEXs that the Securities Commission Malaysia (SC) has listed or acted against. No source showed a small market maker earning >100%/yr net of adverse selection.

### Cited Findings
- Hyperliquid maker rebates depend on an account's share of total 14-day weighted maker volume, not on its own dollar volume: −0.001% above 0.5% share, −0.002% above 1.5%, −0.003% above 3.0%. The base perps fee is 0.045% taker / 0.015% maker **[third-party, consistent across several guides]** — [Dwellir](https://www.dwellir.com/blog/hyperliquid-fees-explained); [Hypebasis](https://hypebasis.io/blog/hyperliquid-maker-rebate-explained); [Hyperliquid docs (official, not opened)](https://hyperliquid.gitbook.io/hyperliquid-docs/trading/fees)
- One guide says Hyperliquid's API reported about USD 77B of volume in the 14 days to 2026-10-28, which puts the first rebate tier at about USD 385M of maker volume per 14 days **[third-party, single source]** — [Hyperliquid market-making guide](https://hyperliquidguide.com/guides/trading/hyperliquid-market-making-guide)
- Worked example from the same family of guides: USD 20M of maker fills in a month at −0.001% earns about USD 200 in rebates. "The rebate is tiny per dollar, so it matters only to high-volume market makers" **[third-party]** — [Hyperliquid market-making guide](https://hyperliquidguide.com/guides/trading/hyperliquid-market-making-guide)
- dYdX v4's best maker rebate is −0.011% (−1.1 bp). It needs Tier 9: more than USD 125M of 30-day volume **and** at least 4% market share. The base-tier maker fee is +1.0 bp **[official docs per snippet; third-party for the tier conditions]** — [dYdX docs: Rewards, Fees and Parameters](https://docs.dydx.xyz/concepts/trading/rewards); [eco.com Hyperliquid vs dYdX](https://eco.com/support/en/articles/15039717-hyperliquid-vs-dydx-fees-liquidity-ux-compared)
- Paradex: retail (UI) traders pay zero maker and zero taker fees. API orders default to the "Pro" profile, which a third party reports at about 0.3 bp maker / 2 bp taker, so the API gets no rebate. Market makers' quotes for the zero-fee retail flow are "visible only in the Paradex UI, hidden from APIs" (Retail Price Improvement) **[official docs for retail zero fee and API default; third-party for Pro fee levels]** — [Paradex trading fees](https://docs.paradex.trade/trading/trading-fees); [Paradex trader profiles](https://docs.paradex.trade/trading/trader-profiles); [FalconX on Paradex](https://www.falconx.io/newsroom/paradex-dime-the-zero-fee-privacy-first-perps-dex)
- Lighter: standard accounts pay no maker fee and earn no rebate. Premium accounts pay a small **positive** maker fee (0.0028%–0.0040%) **[third-party]** — [perps.info lowest-fee DEX guide](https://perps.info/guides/lowest-fee-dex); [finbold maker-fee guide](https://finbold.com/guide/maker-fees-are-going-negative-a-guide-to-how-trading-venues-compare/)

### Inferences
- **[inference]** Hyperliquid tier-1 rebate: USD 385M per 14 days is about USD 27.5M a day of maker fills, roughly 2,200× a USD 12.5K account's capital every day. Below that share the account pays +0.8 to +1.5 bp as a maker, so the rebate is out of reach.
- **[inference]** dYdX Tier 9: USD 125M per 30 days is about USD 4.2M a day (about 330× capital per day), plus 4% of all dYdX volume. If both could be met, 1.1 bp × USD 125M is about USD 13.75K a month. That is why only professional firms qualify.
- **[inference]** Breakeven for USD 15K/yr from the rebate alone, ignoring adverse selection: at −0.25 bp (Drift-type rate) you need about USD 600M a year of maker fills (USD 1.6M a day, about 130× capital per day). At −0.1 bp (Hyperliquid tier 1) you need USD 1.5B a year, but you only get that rate above the 0.5% share threshold. At −0.01 bp (GRVT bottom tier) you need USD 15B a year. A USD 10–15K account cannot keep up that turnover with controlled inventory, and adverse selection on passive fills would have to be below the rebate (unmeasured here).
- **[inference]** This agrees with the repo's earlier reasoning screen ("maker rebates (need volume), trading competitions (not repeatable)", `docs/HANDOFF_NONPROP.md` line 28) and with the #322 thin-venue market-making FAIL (`docs/PREREG_SWEEP3_20261122.md`).

### Gaps
- Official Hyperliquid and dYdX fee pages could not be opened (sandbox network). The thresholds above are snippet- or guide-level and must be checked live, e.g. through the Hyperliquid `userFees` info endpoint (see the data section).
- No published dYdX 30-day exchange volume for 2026 was found, so the size of a 4% share in dollars is unknown.

## Which venues accessible from Malaysia pay negative maker fees, at what volume, and what would rebate income be?

### Takeaway
Real negative maker fees exist at dYdX (up to −1.1 bp, top tier only), Hyperliquid (−0.1 to −0.3 bp, share-based), Drift (about −0.25 bp in a docs example), GRVT (−0.01 to −0.3 bp) and some Kraken Futures new-listing schedules. Paradex and Lighter pay none to API makers. On the DEXs, none of the rebates is large enough at small-account volume to fund USD 15–20K a year. Malaysia is not on the third-party restricted lists found for Hyperliquid or dYdX, but the official terms were not checked.

### Cited Findings
- **Hyperliquid fee tiers:** fees use 14-day weighted volume (perps + 2× spot). The base tier is 0.045% / 0.015%. Above USD 5M: 0.040% / 0.012%. Above USD 25M: 0.035% / 0.008%. One guide says maker becomes 0% at Tier 4 (above USD 500M). Sources disagree on the top-tier thresholds **[third-party]** — [Dwellir](https://www.dwellir.com/blog/hyperliquid-fees-explained); [hiperwire](https://hiperwire.io/explainers/hyperliquid-trading-fees-explained); [datawallet](https://www.datawallet.com/crypto/hyperliquid-fees-explained)
- **Hyperliquid extras:** aligned quote assets get 20% lower taker fees, 50% better maker rebates and 20% more volume credit. HIP-3 "growth mode" markets cut maker rebates, volume credit and rate-limit credit by 90%. Sub-account volume counts toward the master's tier **[third-party]** — [Hyperliquid market-making guide](https://hyperliquidguide.com/guides/trading/hyperliquid-market-making-guide); [datawallet](https://www.datawallet.com/crypto/hyperliquid-fees-explained)
- **Hyperliquid has no designated market maker programme** and no special latency privileges; rebates come purely from volume share **[third-party]** — [Hyperliquid market-making guide](https://hyperliquidguide.com/guides/trading/hyperliquid-market-making-guide)
- **dYdX:** fee tiers are set by governance and can be queried on chain at `/dydxprotocol/v4/feetiers/perpetual_fee_params` **[official docs, snippet]** — [dYdX docs](https://docs.dydx.xyz/concepts/trading/rewards). Surge Season 7 (October 2025) brought a 7-tier schedule with a −1.1 bp maker rebate and a 50% rebate on positive fees for API traders "through the end of 2025". This was a time-limited promotion **[official blog]** — [dYdX blog: Surge Season 7](https://www.dydx.xyz/blog/fee-free-trading-1m-rewards-surge-season-7-launches-on-dydx)
- **dYdX market-making fee programme:** a 2023 governance proposal created a 5-tier programme keyed to maker volume as a percentage of 30-day exchange volume. It passed with about 99.7% in favour **[governance record]** — [Goverland dYdX proposal](https://gl.app/dao/dydxgov.eth/proposals/0x8d7b06b21e50756479a4738924039adf74705d66d8c92554cff74dbab52a9a73)
- **Drift (Solana):** the official docs conflict. The older v2 docs gave a flat 2 bp maker rebate, with fills against the AMM ineligible. Current docs describe volume tiers with a worked example "maker (−0.0025% rebate) with 20% staking gets −0.003%". An August 2025 update introduced a unified tier model, maker-rebate boosts of up to 40% for DRIFT stakers, and a temporary zero-fee BTC/ETH campaign **[official docs/blog, snippets]** — [Drift trading fees](https://docs.drift.trade/trading/trading-fees); [Drift maker rebate fees](https://docs.drift.trade/market-makers/maker-rebate-fees); [Drift old v2 docs](https://drift-labs.github.io/documentation-v2/docs/Trading/3F0d-trading-fees); [Drift new fee structure](https://www.drift.trade/updates/new-trading-fee-structure)
- **GRVT:** a rebate at every tier, from −0.0001% at the lowest to −0.003% at Level 9 **[third-party aggregator]** — [finbold](https://finbold.com/guide/maker-fees-are-going-negative-a-guide-to-how-trading-venues-compare/); [perps.info](https://perps.info/guides/lowest-fee-dex)
- **DESK:** −1 bp maker rebate listed **[third-party]** — [perpfinder DESK review](https://perpfinder.com/perps/desk)
- **Kraken Futures:** a "New Listings & Incentive Rebate Fee Schedule" (April 2026) exists **[official, title only; terms not read]** — [Kraken support](https://support.kraken.com/articles/futures-maker-rebate-april-2026)
- A September 2026 piece argues the perp-DEX fee war has largely ended ("The fee war nobody's really fighting anymore") **[third-party, headline only]** — [Invezz](https://invezz.com/news/2026/09/16/the-fee-war-nobodys-really-fighting-anymore/)
- **Malaysia access:** third-party restricted-country lists for Hyperliquid name the US, Ontario and sanctioned regions (Russia, North Korea, Iran, Cuba, Syria, Crimea/Donetsk/Luhansk). One guide says dYdX restricts the USA, Canada, the UK and sanctioned jurisdictions. **Malaysia is not mentioned** for either. The restrictions cover residence and citizenship, not just IP **[third-party]** — [coinperps](https://www.coinperps.com/learn/hyperliquid-restricted-countries); [datawallet Hyperliquid](https://www.datawallet.com/crypto/hyperliquid-supported-and-restricted-countries); [datawallet dYdX](https://datawallet.com/crypto/dydx-restricted-countries); [dYdX integration compliance (official, list not seen)](https://docs.dydx.xyz/interaction/integration/integration-compliance)

### Inferences
- **[inference]** The only rebate large enough to matter (dYdX −1.1 bp) is gated by a 4% market-share condition. The only one with no share gate (Drift-type −0.25 bp, if it applies at the base tier) needs about USD 1.6M a day of maker fills for USD 15K a year. These programmes subsidise firms that are already large.
- **[inference]** Using Paradex's `INTERACTIVE` / retail flag to get zero fees on bot orders would misrepresent automated flow as retail. That is the kind of policy evasion this repo excludes, so Paradex is a zero-rebate venue for a bot.
- **[inference]** Vertex, Aevo, Orderly, Extended, edgeX, Bluefin, Apex Omni and GMX did not come up with any sourced negative maker fee. GMX is pool-based with no order-book maker side, so it has no maker rebate by design. Treat all of these as "no evidence of a rebate".

### Gaps
- No sourced fee tables for Aevo, Orderly, Extended, edgeX, Bluefin, Apex Omni or Vertex. Vertex's 2025 status (reported wind-down) was not verified in this session.
- Malaysia status was not checked in the official Terms of Use of any DEX. The SC's position on residents using offshore DEXs (as distinct from operators) was not found.
- The Kraken Futures rebate schedule terms and Kraken's Malaysia availability are unknown.
- Drift's base-tier maker rate in late 2026, and Drift's current operating status, were not verified.

## Which liquidity-provider / market-maker reward programmes have published budgets and formulas, and what share goes to small participants?

### Takeaway
The best-documented programme, dYdX v3 liquidity-provider rewards (USD 75M of DYDX over 5 years), was strongly concentrated: one 2022 distribution analysis found 80.5% going to the top two accounts. Current 2025–2026 programmes are mostly taker-volume "seasons" or points/airdrops (dYdX Surge, Aster, Lighter LLP) rather than retainers open to small makers. Hyperliquid runs no DMM programme.

### Cited Findings
- The dYdX LP rewards allocation was 7.5% of the initial token supply (described as USD 75M of DYDX over 5 years), distributed per 28-day epoch by a maker-volume/uptime/spread formula **[official foundation blog]** — [dYdX Foundation: liquidity provider rewards](https://www.dydx.foundation/blog/liquidity-provider-rewards)
- A May 2022 distribution report (Goldberg and Haimowitz) found rewards heavily skewed: 80.5% to the top two accounts under one uncapped scoring variant **[third-party analysis via search summary]** — [dYdX Foundation blog](https://www.dydx.foundation/blog/liquidity-provider-rewards); [Chaos Labs dYdX MM rewards optimisation](https://chaoslabs.xyz/posts/chaos-labs-dydx-market-maker-liquidity-rewards-optimization)
- Community concern recorded in the academic review: LPs with lower maker volumes received the majority of LP rewards, "which contradicted the purpose of this programme" **[academic]** — [Chan, "dYdX: Liquidity Providers' Incentive Programme Review", arXiv 2307.03935 (2023)](https://arxiv.org/abs/2307.03935v1)
- dYdX Surge Season 7 (October 2025): "Fee-Free Trading & $1M Rewards", a trading-volume rewards season, not a maker retainer **[official blog]** — [dYdX blog](https://www.dydx.xyz/blog/fee-free-trading-1m-rewards-surge-season-7-launches-on-dydx)
- Aster season 2 distributed 320M ASTER (about USD 600M) and ended on 2025-10-05. Lighter's rewards ran through its Lighter Liquidity Pool (LLP). Perp-DEX volumes are described as still heavily incentive-driven **[third-party]** — [Hotcoin Research via HTX](https://www.htx.com/en-in/news/hotcoin-research-review-of-top-perp-dexs-cold-reflection-ami-FVIhJ0pj/); [The Block](https://www.theblock.co/post/373210/perp-dex-monthly-trading-volume-1-trillion-usd-hyperliquid-aster-lighter)
- Hyperliquid's builder-code programme pays fee shares to frontends (wallets, bots, Telegram apps), not to makers. Phantom leads with USD 20.63M in revenue, and one builder (trade.xyz) facilitated about 30% of Hyperliquid volume since January 2026 **[third-party]** — [CoinGecko top Hyperliquid builders](https://www.coingecko.com/research/publications/top-hyperliquid-builders); [Talos on trade.xyz](https://www.talos.com/insights/trade-xyzs-role-in-hyperliquid)
- Derive (formerly Lyra) runs an "Institutional Trading Rewards Program" **[official title only; terms not read]** — [Derive docs](https://docs.derive.xyz/docs/institutional-trading-rewards-program)

### Inferences
- **[inference]** Score-based MM reward pools (maker volume × uptime × spread, normalised by share) give most of the money to whoever already has the most maker volume and uptime. A USD 10–15K bot quoting small size gets a pro-rata share that is close to zero.
- **[inference]** Points/airdrop seasons (Aster, Lighter, dYdX Surge) reward volume. They are taker- or wash-prone, the token value is speculative, and the payout is unknown in advance. This is the "new rewards" family the repo already tested and failed (R4 / walk-forward "new rewards" FAIL in `docs/CANDIDATES.md`).
- Prediction-market liquidity rewards (Polymarket, Gemini prediction markets) are excluded as gambling under the brief.

### Gaps
- I found no published 2025–2026 per-account distribution for any perp-DEX MM programme (Drift, Paradex, Aevo, dYdX v4 MM fee programme). Small-participant share is therefore unmeasured for current programmes.
- The Chan (2023) paper's own concentration tables were not read (the PDF was not opened).

## Trading competitions: Malaysia access and legality, prize pools, entrants, and expected value

### Takeaway
The big recurring competitions are on CEXs (Gate WCTC up to USD 5–6M "maximum" pools, Bitget KCGI USD 6M with about 120K participants, Bitget King of Trading 1.7M USDT, KuCoin weekly USD 30K). Bitget, MEXC and KuCoin are on the SC Investor Alert List, so a Malaysian resident should treat them as off-limits. Gate's status is unconfirmed. DEX competitions are small (thousands of dollars) and ranked by ROI, so the expected value per entrant is low and unrepeatable, far below USD 15–20K a year.

### Cited Findings
- **Gate WCTC S7 (2025):** a dynamic pool capped at USD 5M, set by the number of active participants. Team competition USD 1.8M (first half) + USD 2.2M (second half); individual competition USD 1M. The team phase ran 2025-04-21 to 2025-06-08 **[official page + news]** — [Gate WCTC S7](https://www.gate.com/competition/wctc/s7); [Bitcoinist](https://bitcoinist.com/gate-io-kicks-off-wctc-s7-race-for-a-5-million-prize-pool-and-a-ford-mustang-gt/)
- An aggregator lists Gate WCTC S9 with a pool "up to 6,000,000 USDT" and quotes the rules: "the maximum prize pool does not represent the amount actually paid out" **[third-party]** — [buycrypt trading-competition calendar](https://buycrypt.com/trading-competitions/)
- **Bitget KCGI 2025:** USD 6M pool, 120,197 participants, 1,620 teams, 2025-07-24 to 2025-08-12 **[third-party aggregator; not confirmed against Bitget]** — [buycrypt](https://buycrypt.com/trading-competitions/)
- **Bitget King of Trading 2025:** 1.7M USDT pool for futures traders **[third-party news]** — [CryptoRank](https://cryptorank.io/news/feed/ee6ff-bitget-king-of-trading-2025-competition)
- **KuCoin weekly futures competition (2025-12-15 to 2025-12-21):** USD 30K pool paid in BEST/WET tokens and futures deduction coupons; entry from 1 USDT of cumulative futures volume **[official]** — [KuCoin announcement](https://www.kucoin.com/announcement/tr-$30000-Prize-Pool-Lock-In-Your-Spot-in-the-Futures-Competition-with-a-1-USDT-Trade)
- **dYdX × Crypto.com Onchain Season 2:** the page conflicts (USD 20,000 USDC vs a fixed 3,000 USDC split across the top 20 by ROI%). Minimum 100 USDC starting equity and USD 10,000 volume **[official partner page]** — [Crypto.com event](https://crypto.com/events/dydx-trading-competition-season-two)
- **BitMEX ROI competitions (2025):** the top 100 (April Anarchy) or top 50 (Slither to Success) by ROI% share the pool. Some prizes need USD 200,000 minimum volume; the top-ROI trader gets 2.2% (April) or 15% (Jan–Feb) of the pool **[official]** — [BitMEX April Anarchy](https://bitmex.com/app/competition/april-anarchy); [BitMEX Slither to Success](https://bitmex.com/app/competition/slither-to-success-competition)
- **Gemini ROI Rumble:** USD 250/100/50 GUSD daily to the top 3 derivatives traders by ROI, no minimum size **[official]** — [Gemini support](https://support.gemini.com/hc/en-gb/articles/17603167633179-ROI-Rumble-Trading-Competition)
- **Kraken** runs monthly spot trading challenges (2026) **[official, titles only]** — [Kraken competitions](https://www.kraken.com/competitions/chutes-spot-trading-challenge-08-26)
- **Aster AI trading competition** (run by MoneySharks, not Aster): USD 50,000 pool in ASTER **[third-party]** — [TechFlow](https://www.techflowpost.com/en-US/article/28844)
- **Alpha Arena (nof1.ai):** six LLMs traded USD 10K each on Hyperliquid (Season 1 ended 2025-11-03; four of six ended in loss). It is a benchmark with no cash prize for entrants **[news]** — [SCMP](https://www.scmp.com/tech/tech-trends/article/3329784/deepseek-outperforms-ai-rivals-real-money-real-market-crypto-showdown); [Decrypt](https://decrypt.co/345006/ai-crypto-trading-showdown-deepseek-grok-winning-gemini-implodes); [datawallet explainer](https://www.datawallet.com/crypto/alpha-arena-nof1-ai-explained)
- **SC status of competition hosts:** MEXC Global was added to the SC Investor Alert List on 2022-09-05 **[official SC update]** — [SC Investor Alert List as at 5/9/2022](https://www.sc.com.my/resources/media/investor-alert-updates/investor-alert-list-as-at-592022). KuCoin has a 2021 entry for "operating a DAX without registration" **[SC list, cached]** — [SC Investor Alert List](https://www.sc.com.my/regulation/enforcement/investor-alerts/sc-investor-alerts/investor-alert-list). Bitget is reported to be on the list **[third-party, undated]** — [CryptoSlate](https://cryptoslate.com/bybit-shut-down-in-malaysia-over-unlicensed-operations/). Gate.com: no SC listing or enforcement found (not confirmed either way).

### Inferences
- **[inference]** Expected value: the KCGI 2025 headline (USD 6M ÷ 120,197 participants) averages about USD 50 per participant, and most of it goes to team or volume ranks and the top few ROI ranks. ROI-ranked contests with top-heavy payouts reward the highest-variance (most leveraged) entrants, so a capped-loss bot either takes lottery-style risk or wins nothing. A USD 15–20K yearly income from competitions would mean repeatedly placing in the top handful of contests with tens of thousands of entrants. There is no evidence that this can be done, and nothing found suggests it can be repeated.
- **[inference]** Prizes paid in exchange tokens or "deduction coupons" (KuCoin) are worth less than face value, and coupons only have value if you keep trading there.
- **[inference]** Accessing Bitget, MEXC, KuCoin, Bybit or Binance from Malaysia would conflict with SC listings/orders and the repo's "no geoblock circumvention" rule. The legal-access shortlist reduces to DEX competitions (small pools) and possibly Gate (unverified).

### Gaps
- No official final payout totals or winner distributions were found for WCTC S7/S9, KCGI 2025 or King of Trading 2025. Entrant counts are aggregator-only.
- Gate.com's and OKX's Malaysia status was not confirmed from SC primary sources.
- No DEX-native recurring competition (Hyperliquid, Lighter, edgeX, Paradex) with a published 2025–2026 cash pool was found.

## Is there evidence of small market makers earning >100%/yr on capital net of adverse selection?

### Takeaway
No. I found no case study, leaderboard analysis or blog showing a small (≤ USD 15K) market maker earning >100%/yr net of adverse selection on rebates or MM programmes. The evidence found points the other way: rewards are concentrated, and rebate income per dollar is tiny.

### Cited Findings
- Hyperliquid guide: about USD 200 of rebates on USD 20M of monthly maker fills at tier 1. Rebates matter "only to high-volume market makers" **[third-party]** — [Hyperliquid market-making guide](https://hyperliquidguide.com/guides/trading/hyperliquid-market-making-guide)
- dYdX v3 LP rewards: 80.5% to the top two accounts under one scoring variant (2022 report) **[third-party analysis]** — [dYdX Foundation blog](https://www.dydx.foundation/blog/liquidity-provider-rewards)
- Searches for 2025 analyses of Hyperliquid maker-volume concentration (top firms' share) returned only fee guides. No concentration study was found **[search result, negative]** — [Hyperliquid for market makers (guide)](https://hyperliquidguide.com/pro)
- Repo context (internal, verified by this repo's own tests): idea #322 "thin-venue market making" FAILED (`docs/PREREG_SWEEP3_20261122.md`). The funding-gap idea #208 passes walk-forward only with maker fills and fails taker-only under the 1.5× cost check (`docs/CANDIDATES.md`, WF row).

### Inferences
- **[inference]** Maker rebates help an edge that is already positive (they lower execution cost for strategies like #208 funding gaps). They are not an income source on their own at USD 10–15K scale.

### Gaps
- No published P&L of small makers, and no measurement of adverse selection per fill on these venues, was found. This would need our own order-book/trade replay (see data below).

## Malaysia: which CEXs are restricted and which are registered?

### Takeaway
The SC has taken enforcement action against Binance (2021), Huobi, and Bybit (Dec 2024, ordered to disable its platforms). Binance was re-added to the Investor Alert List on 2026-10-08. MEXC, KuCoin and (per a third party) Bitget are on the alert list. I found **no** SC order against OKX, contrary to the brief's premise. As of September 2026 the registered DAX operators are reported as HATA Digital, Luno Malaysia, MX Global, SINEGY DAX and Kinetic DAX (Tokenize was registered in 2022 but is absent from 2026 lists). Coinbase is not registered.

### Cited Findings
- **Bybit:** the SC reprimanded Bybit and its CEO and ordered it to disable its website and apps within 14 business days from 2024-12-11, stop advertising to Malaysians and close its Malaysian Telegram group. The SC confirmed compliance on 2024-12-27. Bybit had been on the Investor Alert List since July 2021. The SC says operating an unregistered DAX is an offence under s.7(1) of the Capital Markets and Services Act 2007 and that it has acted against four illegal DAX operators, the latest being Bybit in November 2024 **[official SC + news]** — [SC media release](https://www.sc.com.my/resources/media/media-release/sc-takes-enforcement-action-against-bybit-for-illegally-operating-dax-in-malaysia); [The Block](https://www.theblock.co/post/332552/malaysia-orders-bybit-to-halt-local-operations-over-registration-failure); [Cointelegraph](https://cointelegraph.com/news/malaysia-securities-regulator-bybit-halt-operations)
- **Binance:** an SC order to disable its website and mobile apps in Malaysia (2021) **[news]** — [The Block](https://www.theblock.co/amp/post/113076/malaysia-binance-disable-crypto-exchange-website-mobile-apps). Added to the Investor Alert List **[news]** — [The Edge Malaysia](https://theedgemalaysia.com/article/sc-adds-largest-cryptocurrency-exchange-platform-binance-investor-alert-list). Re-added in the SC update "as at 8/10/2026" (the only entity added that day). A secondary source says it had been removed in 2024 **[official SC update + third-party]** — [SC Investor Alert List as at 8/10/2026](https://www.sc.com.my/resources/media/investor-alert-updates/investor-alert-list-as-at-8102026); [Layer7 SEA Daily Brief 2026-10-19](https://www.layer7ventures.com/reports/sea-daily-brief-oct19-2026)
- **Huobi:** ordered to cease operating in Malaysia **[news]** — [IBTimes](https://www.ibtimes.com/malaysia-securities-commission-orders-huobi-cease-illegal-digital-asset-exchange-operations-3694809); [Blockworks](https://blockworks.co/news/huobi-crypto-exchange-malaysia)
- **MEXC:** Investor Alert List from 2022-09-05 **[official]** — [SC update 5/9/2022](https://www.sc.com.my/resources/media/investor-alert-updates/investor-alert-list-as-at-592022). **KuCoin:** 2021 entry **[SC list, cached]** — [SC Investor Alert List](https://www.sc.com.my/regulation/enforcement/investor-alerts/sc-investor-alerts/investor-alert-list). **Bitget:** reported on the list **[third-party, undated]** — [CryptoSlate](https://cryptoslate.com/bybit-shut-down-in-malaysia-over-unlicensed-operations/)
- **OKX, Gate.com:** no SC listing or enforcement found in these searches **[negative result]**.
- **Registered DAX operators:** HATA Digital, Luno Malaysia, MX Global, SINEGY DAX and Kinetic DAX as of 2026-09-09 **[third-party, citing the SC register]** — [Fintech News Malaysia](https://fintechnews.my/regulated-crypto-exchanges-malaysia/); [crypto.news](https://crypto.news/malaysia-crypto-trading-tops-4b-fitch-says/). The SC register page shows an update dated 2025-12-03 **[official, not opened]** — [SC list of registered DAX](https://www.sc.com.my/regulation/guidelines/recognizedmarkets/list-of-registered-digital-asset-exchanges). In 2022 the four registered operators were MX Global, SINEGY DAX, Luno Malaysia and Tokenize Technology **[news]** — [The Star 2022-12-01](https://www.thestar.com.my/business/business-news/2022/12/01/malaysia039s-digital-assets-market-regulated-to-protect-investors-sc). Bybit's local investment is via HATA **[third-party]** — [crypto.news](https://crypto.news/malaysia-crypto-trading-tops-4b-fitch-says/)
- **Rules:** the SC revised its Guidelines on Recognized Markets for DAX on 2026-05-20 (tighter rules, faster product approvals) **[official + news]** — [SC media release](https://www.sc.com.my/resources/media/media-release/sc-issues-revised-guidelines-on-recognized-markets-for-digital-asset-exchange); [Business Today](https://www.businesstoday.com.my/2026/05/20/sc-tightens-digital-asset-exchange-rules-speeds-up-product-approvals/). The SC clarified digital-asset broking requirements in February 2026 **[law-firm note, title only]** — [Baker McKenzie](https://www.bakermckenzie.com/en/insight/publications/2026/02/malaysia-securities-commission-clarifies-requirements-digital-asset-broking)

### Inferences
- **[inference]** The registered Malaysian DAXs are spot venues with small volume. No maker-rebate or competition programme was found for them, so they offer no exchange-subsidy route at this scale.
- **[inference]** Coinbase (and Coinbase International) does not appear on the registered list, so it should be treated as not available to Malaysian residents unless Coinbase's own country list says otherwise (not checked).

### Gaps
- The Bitget, OKX and Gate entries on the live SC Investor Alert List could not be confirmed (the page was not opened).
- Whether the SC treats a resident's use of a non-custodial DEX as a regulated activity was not found. Only operator-side offences are documented.

## Which free, machine-readable data could measure this?

### Takeaway
Hyperliquid and dYdX expose fee tiers, per-user fee rates, trades and order books free through public APIs. These are enough to measure required maker share, rebate income and adverse selection by replay. Competition data mostly exists only as web leaderboards and aggregator calendars, not as APIs.

### Cited Findings
- Hyperliquid info API `userFees` returns a user's fee schedule and rates (including the maker-rebate tier) **[third-party API docs]** — [Chainstack: hyperliquid info userFees](https://docs.chainstack.com/reference/hyperliquid-info-userfees.md)
- dYdX fee tiers can be queried from any full node at `/dydxprotocol/v4/feetiers/perpetual_fee_params` **[official docs, snippet]** — [dYdX docs](https://docs.dydx.xyz/concepts/trading/rewards)
- Hyperliquid builder-code volume and revenue dashboards **[third-party, free web]** — [Blockworks Research builder codes](https://blockworks.com/analytics/hyperliquid/hyperliquid-builder-codes); [CoinMarketMan builder-codes API guide](https://coinmarketman.com/blog/hyperliquid-builder-codes-api-tracking-volume-and-revenue-per-builder--en/); [DefiLlama Hyperliquid builders](https://defillama.com/pro/hyperliquid-builders-mhbg6p)
- Perp-DEX volume, OI and fee comparison tables **[third-party, free web]** — [perpdexwars](https://perpdexwars.com/); [perps.info](https://perps.info/guides/lowest-fee-dex)
- Competition calendar with prize-pool history (web, not API) **[third-party]** — [buycrypt trading competitions](https://buycrypt.com/trading-competitions/)
- Drift market-maker rebate docs (fee parameters) **[official]** — [Drift maker rebate fees](https://docs.drift.trade/market-makers/maker-rebate-fees)

### Inferences
- **[inference]** The cheapest Stage 1 measurement for this repo: use the existing GitHub Actions fetch path (`scripts/fetch_public.py`) to pull Hyperliquid `l2Book` snapshots and trades for 2–3 coins. Then compute (a) the 14-day exchange maker volume, giving the dollar size of the 0.5% rebate threshold, and (b) the 1-, 5- and 30-second mid-price markout after passive fills at the touch, which measures adverse selection per fill against the 0.1–0.3 bp rebate. That tells us whether any rebate tier can be profitable before building anything. The repo already fetches Hyperliquid candles and funding.
- **[inference]** Hyperliquid's public leaderboard and per-address `userFills`/`userFees` could show how many addresses sit in rebate tiers (the concentration evidence missing above). This is my assumption about available endpoints and was not verified in this session.

### Gaps
- Endpoints for the Hyperliquid leaderboard, the dYdX indexer (`indexer.dydx.trade/v4`) and a Drift data API are known from memory but were not verified in this session. The sandbox also blocked direct fetches of the official docs, so availability needs checking through the GitHub Actions fetch job.
- No free API found for CEX competition leaderboards or final payouts.

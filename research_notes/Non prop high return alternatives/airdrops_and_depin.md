# Third-party-subsidised crypto income for small players (2025–2026): hedged airdrop / points farming and DePIN / node incentives

Research date: 2026-11-23. Scope: can USD 10,000–15,000 plus modest time earn about USD 15,000–20,000 a year (>100%/yr on capital at
risk) for a Malaysian resident, repeatably, through (a) hedged points / airdrop farming or (b) DePIN / node-operator rewards, and how
could that be measured with free public data?

**How to read these notes.** In this sandbox, WebFetch could not reach keyrock.com, arxiv.org or substack.com (DNS blocked), and DefiLlama's API
(api.llama.fi) was also unreachable. Every figure below therefore comes from search-engine result summaries of the cited pages, not from a
full read of each page. Treat exact numbers as "reported by the cited source" and re-check against the primary page before putting them
in `docs/FIGURES_LEDGER.md`. Where a search summary drew on several pages without tying a claim to one of them, all candidate pages are
cited (most often the 2026 perp-DEX guides: Dropstab, TechFlow, Exchange-compare, OneKey). Labels used: **[official]** = the protocol's own docs or tokenomics post; **[research]** = a named research
firm or academic paper; **[third-party]** = media, aggregator or blog; **[anecdote]** = single-user report; **[my arithmetic]** = my calculation from
cited inputs. The repo already holds a pre-registration for this question (`docs/PREREG_AIRDROP_20261123.md`, #360) whose Stage 0 verdict
was "not measurable as registered"; these notes add sources and a measurement method but do not change that test's rules.

## Q1. Is there a systematic, survivorship-aware dataset of airdrop returns per dollar of capital or per wallet? What do median vs mean and the 2023–2026 trend show?

### Takeaway
No public dataset measures airdrop farming return **per dollar of capital** across a survivorship-complete set of programmes (including
points programmes that paid little or nothing). What exists covers (i) gross income of wallets that *did* receive airdrops (a survivor-only
sample, with means well above medians), or (ii) post-TGE token prices (they mostly fall). The trend from 2023 to 2026 is clearly downward: a
few 2023–2024 drops paid thousands per wallet, while 85–93% of 2024–2026 launches trade below their TGE price.

### Cited Findings
**Per-wallet / per-address income (survivor samples)**
- X-explore with Colin Wu (June 2023) [research]: across 5 airdrops (Uniswap, ENS, Optimism, Blur, Arbitrum), 34,547 "standard hunter" addresses
  (received 3–4 of the 5) had a **median of $6,497** and a **mean of $9,384**; 932 "premium" addresses (all 5) had a median of $14,288 and a mean of
  $18,935. These are gross token income, not net of costs, and the authors note one entity could control several of these addresses —
  [Forklog summary](https://forklog.com/en/experts-assess-incomes-of-airdrop-hunters/); [Wu Blockchain](https://wublock.substack.com/p/in-depth-analysis-of-airdrop-hunters).
- Dragonfly, "State of Airdrops 2025" (11 Mar 2025, also SSRN 5176403 and an SEC Crypto Task Force submission) [research]: 12 airdrops
  (11 that geoblocked the US plus 1 control) totalling $7.16B, with a **median claim of $4,600 per eligible wallet**. The report's purpose is a
  policy argument (US users lost an estimated $1.84B–$2.64B) —
  [Dragonfly microsite](https://airdropreport2025.dragonfly.xyz/Dragonfly-s-State-of-Airdrops-Report-2025-1b1af13b644180c8aff9c2bd0d222e14);
  [SEC PDF](https://www.sec.gov/files/dragonflys-state-airdrops-report-2025.pdf); [SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5176403).
- Luo, Kang, Zheng and Liu, "Toward Resilient Airdrop Mechanisms" (arXiv 2503.14316, Mar 2025) [research]: on Hop Protocol, 3,551 sybil
  addresses in 150 groups; **expected reward per address mostly under ~$200**, highest $341.12 (at June 2022 Hop prices); clusters reached ~$40,000 in
  aggregate; LayerZero sample 7,681 addresses in 198 groups averaging ~129 transactions each; some groups profitable, others not —
  [arXiv](https://arxiv.org/html/2503.14316); [token-research summary](https://token-research.com/research/tr-1128).
- Messias et al., "Airdrops: Giving Money Away Is Harder Than It Seems" (arXiv 2312.02752) [research]: 9 airdrops; in some cases up to 66% of tokens
  were sold quickly, largely by farmers; protocols without airdrops grew users about as much —
  [arXiv abstract](https://arxiv.org/abs/2312.02752).
- Nansen [research]: 41.1% of the top 10,000 ZKsync airdrop addresses sold their full allocation within 24 hours —
  [The Block](https://www.theblock.co/amp/post/300608/zksync-token-airdrop-sales-nansen). Nansen's "Airdrop Pro" ranks top wallets by total income
  across 15 airdrops; it publishes leaderboards, not medians — [Nansen Research](https://research.nansen.ai/article/47).
- CoinGecko (via media) [third-party]: top 50 airdrops 2020–2023 worth $26.6B; 2024 had 36 notable airdrops; secondary sites cite ~$4.5B of airdrops in 2025
  vs ~$19B in 2024 (peak-price methods; not a CoinGecko per-wallet study) — [crypto.news](https://crypto.news/coingecko-details-the-largest-crypto-airdrops-of-all-time/);
  [AirdropAlert statistics](https://airdropalert.com/crypto-airdrop-statistics/); [Decrypt, biggest airdrops of 2025](https://decrypt.co/352376/5-biggest-crypto-airdrops-2025).

**Post-TGE price performance (what a farmer who did not sell at once received)**
- Keyrock, "Airdrops in the Barren Desert" (2024 airdrops) [research]: 62 airdrops on 6 chains; **only 8 had positive returns after 90 days (~88%
  down)**; most of the move happens in the first ~15 days; worst ZEND (−95%), best DRIFT —
  [Keyrock](https://keyrock.com/airdrops-in-the-barren-desert/); [DL News](https://dlnews.com/articles/snapshot/keyrock-study-says-most-token-airdrops-crash-after-launch/);
  [BeInCrypto](https://beincrypto.com/majority-airdrop-tokens-crash-within-15-days/).
- Memento Research, "State of 2025 Token Launches" (data to 20 Dec 2025) [research]: 118 TGEs; **84.7% (100/118) below TGE valuation; median FDV
  down ~71%**; none of 28 launches with ≥$1B FDV were above launch — [Memento Research](https://mementoresearch.com/state-of-2025-token-launches-year-in-review);
  [Crypto Times](https://www.cryptotimes.io/2025/12/21/2025-token-launches-struggle-as-most-trade-below-tge-prices/).
- Arrakis Finance [research]: 125 TGEs, ~85% below initial price; about two-thirds were down within 7 days, and only 9.4% of first-week decliners ever
  recovered to launch price in 2025 — [The Defiant](https://thedefiant.io/news/research-and-opinion/only-1-in-10-weak-token-launches-recovered-in-2025-arrakis).
- CryptoRank [research, via media]: 93% of 113 tokens launched 2024–2026 that reached $100M market cap were below TGE price —
  [BeInCrypto analysis](https://beincrypto.com/airdrop-analysis-token-decline-strategy/) (cited there; primary not read).
- An on-chain analysis of over 2 million airdrop addresses found 64% of recipients sold immediately at TGE [third-party; primary author not identified
  in the summary] — [BeInCrypto](https://beincrypto.com/airdrop-analysis-token-decline-strategy/).
- [anecdote] One trader's log: of 30 airdrops received since Dec 2024, only one (Avantis, +30.4%) traded above its TGE price — same BeInCrypto article.

### Inferences
- Survivorship: the per-wallet medians ($4,600 Dragonfly; $6,497 X-explore) are conditioned on the wallet being eligible and on the programme
  having launched a valuable token. Neither counts (a) wallets that farmed and were excluded or sybil-filtered, (b) programmes that ended with no
  token, (c) costs, or (d) capital deployed. They cannot be divided into "return per dollar".
- Mean > median in every sample (X-explore: $9,384 vs $6,497; $18,935 vs $14,288), so income is right-skewed and a few drops dominate.
- Trend: the 2023 sample (UNI/ENS/OP/ARB/Blur) and the late-2024 Hyperliquid drop paid thousands per wallet; 2024–2025 launches mostly fell
  85–90% of the time. For a farmer who sells at claim, the post-TGE decline matters less than the claim-day price; but the decline means a
  farmer who cannot sell (vesting, illiquid, thin order books) or is paid in a later season gets far less.
- The repo's earlier note (`docs/HANDOFF_NONPROP.md`) cites "one Nansen analysis of 10 L2 airdrops: median net profit per address $47, mean
  $1,850". I could **not** find that study in this session; treat it as unverified until its source is located.

### Gaps
- Full text of Keyrock, Memento, Dragonfly and the two arXiv papers was not readable from this sandbox (blocked hosts); medians/means by year
  and methodology details are from summaries.
- No study found that includes points programmes that paid nothing. No study reports ROI on capital for hedged farmers.
- No 2026-specific aggregate (e.g. "2026 airdrops below TGE") from a named research firm was found beyond the CryptoRank 2024–2026 figure.

## Q2. Campaigns with a published (or derivable) allocation basis: reconstructed return for a hedged USD 10K farmer

### Takeaway
Only a handful of campaigns let an outsider compute "tokens per point" (fixed weekly point pools + a published token pool), and almost none
publish "points per dollar of activity" for volume programmes. Where both sides can be pieced together (Ethena Season 1, a stablecoin
programme with no hedge needed), a $10K day-one farmer earned roughly **+26% (simple holding) to ~+100% (best boosted lock) in six weeks**,
before slippage, at a conservative launch price. For the perp-DEX programmes (Hyperliquid, Lighter, Extended) the value **per point** can be
estimated, but value **per dollar of volume** requires the protocol's total eligible volume, which is not published per season; it can be
approximated from free volume data (see Q6). No reconstruction is official.

### Cited Findings
**Ethena Season 1 ("Shards", ~6 weeks to 1 Apr 2024; stablecoin USDe, so no price hedge needed)**
- 750M ENA (5% of supply) distributed linearly by shards over a six-week campaign; 122.1k users accumulated 360.7B shards [third-party recap of
  official data; the search summary did not tie the recap to one page, candidates cited] —
  [AirdropAlert Ethena](https://airdropalert.com/airdrops/ethena/); [DL News](https://dlnews.com/articles/defi/ethena-500m-airdrop-leads-defi-project-to-plan-the-next-one/);
  the same 360.7B total is in the repo's Stage 0 note (`docs/PREREG_AIRDROP_20261123.md`).
- Shard rates changed during the campaign: holding USDe 5/day per $ (later cut to 2), staking 1/day, locking 10/day, locked Curve LP 20/day (later 15)
  [third-party, sources disagree; summarised across these guides] — [Bitpinas guide](https://bitpinas.com/learn-how-to-guides/ethena-airdrop-protocol/);
  [Coincu](https://coincu.com/249716-how-to-get-ethena-airdrop/); [CoinLaunch](https://coinlaunch.space/events-contests/ethena-airdrop/).
- Reported outcomes [third-party; summarised across the same guides and a case study]: $10,000 locked on day one → ~9,000 ENA; 1K USDe on day one →
  ~640 ENA — [OneClick case study](https://www.oneclick.fi/blog/ethena-season-1-airdrop-case-study); [Bitpinas](https://bitpinas.com/learn-how-to-guides/ethena-airdrop-protocol/).
  A Medium analysis puts the simplest buy-and-hold USDe strategy at **23.75% ROI** for Season 1 (ex-yield, from day one) —
  [Medium "Shards out Sats in"](https://medium.com/@stephenoresco/shards-out-sats-in-farming-ethenas-season-2-sats-campaign-e094bfa690f9).
- ENA launched at about a $1B market cap on 2 Apr 2024 [third-party] — [The Defiant](https://thedefiant.io/news/defi/ethena-labs-ena-launches-at-usd1-billion-post-airdrop-as-sats-campaign-kicks-off).
  The repo's Stage 0 note recorded a $0.59 launch price (third-party; `docs/PREREG_AIRDROP_20261123.md`).
- Later seasons: Season 2 "Sats" ran to ~2 Sep 2024 (start date disputed); no final sats total or ENA-per-sat ratio published in sources found —
  [AirdropAlert Ethena S2](https://airdropalert.com/airdrops/ethena/ethena-season-2/). Season 5 was reported as 2% of ENA supply —
  [KuCoin blog](https://www.kucoin.com/blog/how-to-claim-ethena-season-5-airdrop).
- An investigator alleged anomalies in Ethena's Season 1–2 farming events that hurt users — [Cointelegraph](https://cointelegraph.com/news/ethena-labs-accused-farming-ethena-tokens).

**Hyperliquid (genesis airdrop 29 Nov 2024; perp DEX volume farming)**
- Points schedule [official docs, via summaries]: Season 1 from 1 Nov 2023, **1M points/week for 6 months**; Season 1.5 (May 2024) 8M points;
  Season 2 from 29 May 2024 at **700k/week** to ~29 Sep 2024; Season 2.5 8.4M points; the docs publish **no points-to-HYPE formula** and Hyperliquid
  reserved the right to modify past point distributions — [Hyperliquid docs, points](https://hyperliquid.gitbook.io/hyperliquid-docs/points);
  [Eco summary](https://eco.com/support/en/articles/15039718-hyperliquid-airdrop-hype-genesis-facts-and-season-2-status).
- 310M HYPE (31% of supply) to points holders; ~94,000 wallets; $3.90 launch price → ~$1.2B [third-party] —
  [Eco](https://eco.com/support/en/articles/15039718-hyperliquid-airdrop-hype-genesis-facts-and-season-2-status);
  [CoinGecko biggest airdrops](https://www.coingecko.com/learn/biggest-crypto-airdrops). Community ratio ~5.35 HYPE/point (unverified) —
  [hackmd strategy note](https://hackmd.io/@DeFiRadar-Hub/airdrop-hyperliquid-strategy-farming-points).

**Lighter (LIT TGE ~30 Dec 2025; perp DEX volume farming)**
- 25% of LIT supply (250M LIT) to points from Seasons 1–2 (Jan–Dec 2025); ~12.5M points → **~20 LIT per point** (20–20.8 depending on the points total
  used) [third-party; Lighter published no conversion] — [Cipher on X](https://x.com/cipher_airdrop/status/2005881405948191066);
  [Lighterpedia](https://lighterpedia.com/ecosystem/lighter-points-program); [MEXC](https://blog.mexc.com/news/lighter-lit-token-crashes-30-launch-price-2-45-airdrop-dump/).
- Season 2 paid **250,000 points/week** (200,000 retail, 50,000 market making) [third-party; matches the official retail docs page title] —
  [Lighterpedia](https://lighterpedia.com/ecosystem/lighter-points-program); [Lighter docs, retail points](https://docs.lighter.xyz/points-program/retail).
- LIT fell ~30% on day one to a low of $2.45 [third-party] — [MEXC](https://blog.mexc.com/news/lighter-lit-token-crashes-30-launch-price-2-45-airdrop-dump/).
  Total airdrop ~$675M, CoinGecko's 10th-largest ever —
  [CoinMarketCap Academy](https://coinmarketcap.com/academy/article/lighter-LIT-675m-tenth-largest-crypto-airdrop).
- Pre-TGE OTC points prices reached $75–80/point [third-party] — [AirdropAlert](https://airdropalert.com/?p=328436). Jump Crypto received ~9.6M LIT
  (>$24M at launch), partly as a market-making fee; one cluster held ~$26M of LIT — [MEXC](https://www.mexc.com/news/386269); [MEXC](https://www.mexc.com/news/386270).

**Extended (XTEN; perp DEX volume farming; snapshot 6 Nov 2026)**
- **300M XTEN (30% of 1B) to points holders, fully unlocked at TGE** [official tokenomics post] — [Extended on X](https://x.com/extendedapp/status/2117309226423108056);
  [KuCoin news](https://www.kucoin.com/news/flash/extended-reveals-xten-tokenomics-30-airdrop-fully-unlocked-at-tge-staking-offers-up-to-5x-yield-boost).
- ~70M points (community estimate) → ~4.29 XTEN/point; Hyperliquid pre-market ~$0.27; 17,384,355 XTEN belong to points earned by Extended's internal
  market-making team; holders must sign terms by 31 Dec (snapshot 6 Nov) [third-party] — [AirdropAlert](https://airdropalert.com/blogs/xten-tokenomics/);
  [airdrops.io](https://airdrops.io/extended/). Season 1 paid 1.2M points weekly [third-party] — [Dropstab](https://news.dropstab.com/research/top-perpetual-dex-platforms-for-point-farming).

**Older published-criteria drops (tiers, not $-based):** Hop and LayerZero were analysed per address (see Q1, Luo et al.); expected rewards per Hop
address mostly <$200 — [arXiv 2503.14316](https://arxiv.org/html/2503.14316).

### Inferences
**[my arithmetic] Ethena Season 1, $10K farmer, 42 days, ENA valued at $0.59 (conservative launch figure):**
- ENA per shard = 750M / 360.7B = **0.00208**.
- Hold USDe at 5 shards/$/day: 10,000 × 5 × 42 = 2.1M shards → 4,366 ENA → **$2,576 (+25.8% in 6 weeks)**. Consistent with the Medium 23.75% estimate.
- Locked Curve LP at 20 shards/$/day for all 42 days: 8.4M shards → 17,466 ENA → **$10,305 (~+103% in 6 weeks)** — an upper bound, since the rate
  was later cut to 15 and LP carries pool risk.
- The "$10K locked → ~9,000 ENA" report implies ~$5,300 (+53%) at $0.59.
- No price hedge was needed (USDe is a dollar-pegged synthetic); costs were gas, forgone sUSDe yield for non-staked positions, depeg and
  smart-contract risk. Ethena's own launch at ~$1B market cap would make these figures higher if ENA's price was above $0.59 at claim.
- Annualised, +26% in 6 weeks looks like >200%/yr, but this was a single six-week window that only existed once; later Ethena seasons were smaller
  shares of supply (Season 5: 2%) at lower ENA prices, and no per-sat ratio for Season 2 is published, so repeatability cannot be shown.

**[my arithmetic] Hyperliquid value per point:** points ≈ 26M (S1: 1M × ~26 weeks) + 8M (S1.5) + ~12.3M (S2: 0.7M × ~17.6 weeks) + 8.4M (S2.5)
≈ **54.7M** → 310M / 54.7M ≈ **5.7 HYPE/point** (the community's 5.35 would imply ~58M points, e.g. if closed-alpha points are included). At $3.90
→ **~$21–22 per point**; mean ~3,300 HYPE (~$12.9K) per wallet across ~94K wallets (mean, heavily skewed). Because the weekly pool was fixed,
value per $ of volume = weekly pool value ÷ weekly eligible volume, which needs Hyperliquid's weekly volume (free on DefiLlama, not fetched
here). Points were also awarded for market making and referrals, so a volume-only rate overstates what a taker earns.

**[my arithmetic] Lighter:** 20 LIT/point × $2.45–$3.00 ≈ **$49–$60 per point at TGE**, below the $75–80 pre-TGE OTC prices. Season 2's weekly pool
≈ 250,000 × 20 LIT × ~$2.7 ≈ **$13.5M per week** (about $10.8M for retail). Value per $ of volume again needs weekly volume.

**[my arithmetic] Extended:** ~4.29 XTEN × $0.27 ≈ **~$1.16 per point (pre-market)**; at 1.2M points/week the weekly pool is ≈ $1.4M; the internal
market-making team holds ~5.8% of the airdrop (17.38M/300M).

**Hedged-farmer economics, general form.** For a fixed weekly pool worth P dollars, the rebate on volume is r = P / V (V = all eligible weekly
volume). A hedged farmer trading two offsetting legs pays c per dollar of volume (fees on both venues + spread + funding difference). Profit
per week = (r − c) × v, where v is capped by margin and time. The farmer does not know P (token price at claim) or V (others' volume) until the
end, and pools that fill up push r down (the "cost per point rises as a farm gets popular" observation in
[AirdropAlert's method note](https://airdropalert.com/?p=328436)). Professional market makers (Jump at Lighter, Extended's own MM team) compete
for the same pool with lower c.

### Gaps
- No campaign found that publishes **points per dollar of volume** (perp DEXs) together with a final token-per-point rate; all perp DEX
  reconstructions rely on third-party points totals.
- Ethena Seasons 2–4: no final sats/shard totals found, so per-dollar returns cannot be computed.
- Hedge cost data (fee tiers per venue, realised spreads) were not collected in this session; official fee pages should be fetched via the
  repo's GitHub Actions workflow.
- Exact ENA price at the claim moment (vs the $0.59 recorded earlier and the ~$1B market-cap report) not verified.

## Q3. Which points / airdrop programmes are live now (late 2026), can a Malaysian resident join them without geoblock evasion, and what are their budgets?

### Takeaway
The live pipeline in late 2026 is dominated by perp DEX points programmes (Variational, Pacifica, Paradex, Lighter's ongoing seasons,
Ostium, StandX, N1, Nado), plus wallet/L2 programmes with no published terms (Ink/Kraken, Jumper). Several publish a token budget (Extended 30%,
Variational 32%, Paradex 20% of DIME for the genesis airdrop, Lighter 25% reserved for future seasons) but none publishes a points-to-token rate
before TGE. Malaysia is not on Hyperliquid's restricted list per third-party summaries; Malaysia **is** excluded from KuCoin HODLer airdrops and
from BTSE. Per-programme Malaysia terms must be read one by one.

### Cited Findings
**Programmes reported live or pending (all third-party unless marked; dates as of the source)**
- **Variational (VAR):** points programme pushed from Q3 to Q4 2026; TGE targeted Q4 2026; **32% of supply** to the genesis airdrop, fully unlocked;
  3,000,000 points at launch plus 150,000 weekly — [The Blockverse](https://theblockverse.co/variational-airdrop/);
  [Exchange-compare tier list](https://exchange-compare.com/best/perp-dex-airdrops/). One guide calls Variational and Extended "already late" for
  new entrants — [Dropstab](https://news.dropstab.com/research/top-perpetual-dex-platforms-for-point-farming).
- **Extended (XTEN):** snapshot taken 6 Nov 2026; terms must be signed by 31 Dec; TGE date not set → effectively closed to new farmers —
  [AirdropAlert](https://airdropalert.com/blogs/xten-tokenomics/).
- **Pacifica (Solana perp DEX):** 10,000,000 points a week, snapshot every Thursday; no token, TGE or claim date confirmed —
  [The Blockverse](https://theblockverse.co/pacifica-airdrop/).
- **Paradex (DIME):** Season 2 with 4M XP weekly; **20% of DIME for the genesis airdrop**, 57.6% community supply; season extended by six months in
  late 2025 (current status in Nov 2026 not confirmed) — [TechFlow perp DEX guide](https://www.techflowpost.com/en-US/article/30136);
  [Dropstab](https://news.dropstab.com/research/top-perpetual-dex-platforms-for-point-farming).
- **Lighter:** token live; 25% of LIT supply reserved for future points seasons; a Robinhood-wallet campaign converts points from a fixed 11M LIT pool
  (2× points via Robinhood Wallet) — perp-DEX guides (claim not tied to one page): [Dropstab](https://news.dropstab.com/research/top-perpetual-dex-platforms-for-point-farming); [TechFlow](https://www.techflowpost.com/en-US/article/30136); [Exchange-compare](https://exchange-compare.com/best/perp-dex-airdrops/); [OneKey](https://onekey.so/blog/ecosystem/perp-dex-point-farming-practical-guide-from-beginner-to-advanced-20260123120930/);
  [AirdropAlert](https://airdropalert.com/?p=328436); [airdrops.io on X](https://x.com/airdrops_io/status/2099447351978983529).
- **edgeX:** TGE 31 Mar 2026 (pre-TGE window closed); **Aster:** staged airdrops; **Hyperliquid:** official docs describe no second airdrop and no later points
  season (aggregators that list "Season 3" conflict with the docs) — perp-DEX guides (claim not tied to one page): [Dropstab](https://news.dropstab.com/research/top-perpetual-dex-platforms-for-point-farming); [TechFlow](https://www.techflowpost.com/en-US/article/30136); [Exchange-compare](https://exchange-compare.com/best/perp-dex-airdrops/); [OneKey](https://onekey.so/blog/ecosystem/perp-dex-point-farming-practical-guide-from-beginner-to-advanced-20260123120930/);
  [search summary of Hyperliquid docs](https://eco.com/support/en/articles/15039718-hyperliquid-airdrop-hype-genesis-facts-and-season-2-status).
- **Ink (Kraken):** Ink points do not guarantee tokens; no conversion formula, eligibility rules or TGE date; **Jumper (JUMP):** TGE guided Q4 2026, no
  terms published; **Flint:** points start with a devnet competition 13–20 Nov 2026 — [Datawallet](https://www.datawallet.com/crypto/top-crypto-airdrops);
  [Airdrop calendar](https://orbitperpscreener.com/airdrop-calendar); [Airdropmeta Jumper](https://www.airdropmeta.com/projects/jumper).
- **Others named as live:** Ostium (Season 2), StandX, N1, Nado — perp-DEX guides (claim not tied to one page): [Dropstab](https://news.dropstab.com/research/top-perpetual-dex-platforms-for-point-farming); [TechFlow](https://www.techflowpost.com/en-US/article/30136); [Exchange-compare](https://exchange-compare.com/best/perp-dex-airdrops/); [OneKey](https://onekey.so/blog/ecosystem/perp-dex-point-farming-practical-guide-from-beginner-to-advanced-20260123120930/);
  [OneKey guide, Jan 2026](https://onekey.so/blog/ecosystem/perp-dex-point-farming-practical-guide-from-beginner-to-advanced-20260123120930/).
- **Excluded by the user's constraints:** predict.fun (PREDICT TGE and claim 18 Nov 2026) is a prediction market (gambling exclusion) —
  [Bitrue TGE calendar Nov 2026](https://www.bitrue.com/blog/upcoming-crypto-tge-november-2026).
- Anti-sybil systems at several perp DEXs can slash points retroactively for wash trading —
  perp-DEX guides (claim not tied to one page): [Dropstab](https://news.dropstab.com/research/top-perpetual-dex-platforms-for-point-farming); [TechFlow](https://www.techflowpost.com/en-US/article/30136); [Exchange-compare](https://exchange-compare.com/best/perp-dex-airdrops/); [OneKey](https://onekey.so/blog/ecosystem/perp-dex-point-farming-practical-guide-from-beginner-to-advanced-20260123120930/).

**Malaysia access**
- Hyperliquid's Terms (updated 26 Jan 2025) restrict the US, Ontario and sanctioned regions; Malaysia is not listed in third-party summaries;
  using a VPN to get around restrictions breaches the terms — [CoinPerps](https://www.coinperps.com/learn/hyperliquid-restricted-countries);
  [Datawallet](https://www.datawallet.com/crypto/hyperliquid-supported-and-restricted-countries).
- KuCoin HODLer Airdrops exclude Malaysia (with Singapore, Canada, the Netherlands, France and others) —
  [KuCoin support](https://www.kucoin.com/support/48142946141378).
- BTSE bars use from Malaysia — [BTSE support](https://support.btse.com/en/support/solutions/articles/43000781560).
- Dragonfly's 2025 report: 11 of its 12 sampled airdrops geoblocked the US (Malaysia not discussed in the summary) —
  [Dragonfly](https://medium.com/dragonfly-research/the-2025-state-of-airdrops-report-how-the-u-s-got-sidelined-and-what-comes-next-70aaedf4e9b2).

### Inferences
- Budgets are large in token terms (20–32% of supply), but the dollar value depends on an unknown launch FDV and on the 2025 evidence that
  ~85% of launches fall below TGE (Q1).
- By late 2026 the market is crowded: many perp DEXs run simultaneous points programmes, professional market makers farm them, and guides
  already describe some as "late". The early-entry window the repo's radar notes identified (first months of a programme) is the only part with a
  plausibly high rebate rate.
- Malaysia: DeFi front-ends that only geoblock the US/Ontario/sanctioned regions appear joinable; CEX-run airdrops (KuCoin) and some venues
  (BTSE) are not. This must be checked per programme at sign-up, from the official terms.

### Gaps
- Lighter, Variational, Pacifica, Paradex terms were not read for Malaysia-specific exclusions.
- No reliable source gives these programmes' expected FDV; pre-market prices (e.g. XTEN ~$0.27) are thin and unofficial.
- Paradex DIME TGE status and Ethena's current season status in Nov 2026 were not confirmed.

## Q4. DePIN / node-operator incentives: realistic monthly earnings per node vs hardware cost, reward schedules, explorers/APIs, Malaysia availability

### Takeaway
Token subsidies in DePIN have shrunk sharply: Solana DePIN rewards fell from ~$7.6M/month (Jul 2025) to below network revenue (<$2M vs $2.4–2.8M
per month in Feb–Apr 2026). Realistic small-operator earnings are **a few dollars per month per Helium hotspot, ~$36–40/month at the cap per GEODNET
station ($500–1,000 hardware), and ~$50–85/month net per consumer GPU**. None of these reaches 100%/yr on capital reliably, several (Hivemapper
Bee, Helium Mobile carrier offload) are US/LatAm-centric, and infrastructure-oracle roles (Pyth, Chainlink) are not open to small players in
the sources found.

### Cited Findings
**Sector level**
- Messari & Escape Velocity, "State of DePIN 2025" (28 Jan 2026) [research, via media]: ~$10B circulating market cap, **~$72M on-chain revenue in
  2025**; leaders trade at ~10–25× revenue (vs >1,000× in 2021) — [Cointelegraph](https://cointelegraph.com/news/depin-revenues-grow-despite-token-losses);
  [Crypto News AU](https://cryptonews.com.au/news/depin-isnt-dead-its-a-10b-revenue-driven-market-messari-says-132708/).
- Syndica monthly "Deep Dive: Solana DePIN" [research]: July 2025, 10 protocols paid **$7.6M** of rewards to deployers while 7 protocols earned ~$0.9M a
  month; Feb 2026 revenue $2.4M with rewards **< $2M** for the first time; Apr 2026 rewards **$1.8M** vs revenue **$2.8M** (protocol sets differ, so not
  like-for-like) — [Syndica Jul 2025](https://blog.syndica.io/deep-dive-solana-depin-july-2025);
  [Syndica Feb 2026](https://blog.syndica.io/deep-dive-solana-depin-february-2026); [Syndica Apr 2026](https://blog.syndica.io/deep-dive-solana-depin-april-2026/).

**Helium (IoT and Mobile)**
- IoT hotspots: well-placed units ~0.07–0.30 HNT/day, about **$1–5/month** at HNT ≈ $0.51; top dense sites ~$8–15/month [third-party] —
  [MillionMiner, 2026 guide](https://millionminer.com/news/helium-mining-2026-complete-operator-guide).
- Helium Mobile: residential/low-footfall deployments earn **under $1/month or near zero** without real carrier offload; Mobile rewards concentrated in
  the USA, Mexico and Brazil [third-party] — [DePIN Run](https://www.depinrun.com/guides/helium-hotspot-operator-guide).
- Since July 2026 HNT rewards follow delivered data rather than coverage; Helium on-chain revenue fell from $3.35M (Q2 2026) to $718,000 (Q3 2026)
  after a carrier price cut [third-party, very recent] — [CoinPaprika](https://coinpaprika.com/education/helium-hnt).

**GEODNET (GNSS reference stations)**
- Cap 6 GEOD/day ≈ **$36–40/month** at 2026 prices; hardware **$500–1,000** (MobileCM base ~$695); payback 13–42 months; the daily cap is set to halve
  to 3 GEOD from 1 Jul 2027 [third-party, sources conflict] — [CoinPaprika earn-DePIN](https://coinpaprika.com/education/earn-depin);
  [DePIN research release, 21 Nov 2026](https://github.com/Ricosworks1/depin-research-reports/releases/tag/depin-dispatch-geodnet-deflationary-20261121);
  [Solana Report, Mar 2026](https://solanareport.com/2026/03/23/solana-depin-revenue-surge-2026-helium-hits-3-5m-users-while-io-net-and-geodnet-lead-earnings).

**Hivemapper / Bee Maps (dashcam mapping)**
- Bee costs $19/month on a 24-month plan ($456), **sold only in the US and Puerto Rico**; the USDC rate paid to drivers is not published —
  [CoinPaprika](https://coinpaprika.com/education/hivemapper-bee-maps); [DePIN Run](https://depinrun.com/guides/hivemapper-node-operator-guide).

**Grass (bandwidth sharing)**
- Season 1 (28 Oct 2024): 100M GRASS (10% of supply) to ~1.5M claiming addresses (2.8M eligible reported); ~35–40 GRASS per user average
  (blog estimate) — [The Block](https://www.theblock.co/news/defi/2024-10-30-grass-becomes-most-distributed-solana-airdrop-as-nearly-1-5-million-addresses-claim-tokens-323805);
  [MEXC blog](https://blog.mexc.com/news/missed-grass-airdrop-season-1-heres-how-to-position-for-grasss-massive-14m-season-2/).
- Season 2: a USDC payout for bandwidth shared 14 Oct 2024–8 Jun 2026, funded from network revenue ($17M H1 2026 reported), claim 22 Jul 2026–
  22 Jan 2027; community reports "tiny payouts" [third-party; one anecdote: 543 days → $0.49] —
  [CoinStats](https://coinstats.app/news/7b48731b158dd9f5899ba04c044076af0c204c6d5d81686c0fe2975985e513e3_Grass-Airdrop-Season-2-Claim-Is-Live-Community-Reacts-to-Tiny-Payouts);
  [Binance Square](https://www.binance.com/square/hashtag/GRASSAirdrop).

**GPU compute (io.net, Akash, Nosana)**
- io.net lists RTX 4090 rental at **$0.18/hour** (customer price) [official] — [io.net FAQ](https://io.net/p/faq-can-i-run-ai-workloads-on-consumer-gpus-like-rtx-4090).
- Third-party net estimates for one 4090: **~$50–85/month** after electricity, depreciation and fees; another blog claims $340–580/month on io.net
  (unclear gross/net) — [TerabyteTriangle](https://terabytetriangle.com/en/tutorial/depin-gpu-rental-economics-2026.html);
  [Endless Mining](https://endlessmining.com/renting-your-gpu-for-ai-2026/).
- Akash: network GPU utilisation **33.7% in Q1 2026** [research]; the Homenode path takes a 30% fee [third-party] —
  [Messari, State of Akash Q1 2026](https://messari.io/report/state-of-akash-q1-2026-final); [ownyourmind.ai](https://ownyourmind.ai/use/how-to-run-an-akash-provider/).
- Nosana ran a Sept 2026 campaign for RTX 4090/5090 hosts (bonus = 20% of daily use for ≥85% uptime); no monthly earnings figure found —
  [depin.builders](https://depin.builders/projects/nosana).

**Explorers / APIs (free and machine-readable status)**
- Helium's legacy api.helium.io is deprecated since the 2023 Solana migration; reward data now come from Helium oracle **public S3 data exports**
  and Solana RPC; HeliumGeek offers a REST API with Mobile/IoT reward history (pricing not stated) —
  [freeapihub Helium API page](https://freeapihub.com/apis/helium-blockchain-api); [HeliumGeek API](https://heliumgeek.com/api).
- Syndica's monthly Solana DePIN reports (free PDFs) give network-level rewards and revenue —
  [Syndica Dec 2025 PDF](https://blog.syndica.io/content/files/2026/01/Deep-Dive---Solana-DePIN-December-2025-2.pdf).

### Inferences
- [my arithmetic] io.net's own price caps a 4090's gross at 0.18 × 730 h ≈ **$131/month at 100% utilisation**, before the platform share and
  electricity; at Akash-like ~34% utilisation, ≈ $45/month gross. That brackets the $50–85/month net estimates and rules out the $340–580 claims for
  a single card at io.net's listed price.
- [my arithmetic] GEODNET at the cap: $432–480/yr on $500–1,000 of hardware ≈ **43–96%/yr gross** (token-price dependent), falling by half after
  the July 2027 cap cut. With $15K one might buy ~15–25 stations, but each needs a distinct qualifying site (an assumption, not verified here),
  so a single person cannot simply stack them at home; the ~$15–20K/yr target would need every station at the cap and a stable GEOD price.
- DePIN subsidies now look smaller than network revenue on Solana (Syndica), so "someone else pays" is fading: operator income increasingly
  tracks real demand, which is concentrated in the US/LatAm for Helium Mobile and Hivemapper.
- Hardware DePIN is closer to a small capex business with token risk than to a subsidised yield; returns are tens of percent at best, not >100%.

### Gaps
- Malaysia availability not verified for GEODNET, io.net, Akash or Nosana hosting (likely global, unverified); Helium IoT coverage in Malaysia not
  checked.
- Pyth / Chainlink operator rewards: no sources found in this session describing open participation for small players (background
  knowledge says publishers/node operators are vetted institutions; unverified here).
- Filecoin storage-provider economics, Render node economics, and incentivised testnets (2026 lists) were not covered for lack of tool budget.
- Many DePIN sources found (CoinPaprika "education", Solana Report, DePIN Run, MillionMiner) are low-profile and possibly AI-generated; their
  numbers conflict. Official explorer data should replace them before any figure is ledgered.
- No consumer GPU purchase price or Malaysian electricity tariff was collected, so net GPU ROI on capital is not computed.

## Q5. Sybil rules: what is allowed, and what must be excluded

### Takeaway
One wallet per person, farmed with real activity, is allowed everywhere surveyed. Multi-wallet (sybil) farming is the main thing issuers
filter, slash or claw back, and it is excluded by the user's constraints; so is wash trading, which several perp DEX programmes slash
retroactively. Issuers also keep discretion to change allocations after the fact.

### Cited Findings
- Hyperliquid reserves the right to modify previous point distributions at its sole discretion — [Eco summary of Hyperliquid docs](https://eco.com/support/en/articles/15039718-hyperliquid-airdrop-hype-genesis-facts-and-season-2-status).
- Perp DEX anti-sybil systems can slash points retroactively for wash traders — perp-DEX guides (claim not tied to one page): [Dropstab](https://news.dropstab.com/research/top-perpetual-dex-platforms-for-point-farming); [TechFlow](https://www.techflowpost.com/en-US/article/30136); [Exchange-compare](https://exchange-compare.com/best/perp-dex-airdrops/); [OneKey](https://onekey.so/blog/ecosystem/perp-dex-point-farming-practical-guide-from-beginner-to-advanced-20260123120930/).
- Somnia's airdrop policy: eligibility and amount at the company's sole discretion — [Somnia docs](https://docs.somnia.network/concepts/miscellaneous/legal/airdrop-policy).
- LayerZero ran a sybil self-report inquiry before its airdrop — [BlockBeats](https://en.theblockbeats.news/news/53914).
- Academic work finds airdrop farming dominated by multi-address clusters (Hop: 3,551 sybil addresses in 150 groups; LayerZero 7,681 in 198 groups) —
  [arXiv 2503.14316](https://arxiv.org/html/2503.14316); earlier work found about half of Arbitrum recipients appeared to be same-person addresses —
  [arXiv 2407.01176](https://arxiv.org/html/2407.01176v1).
- Hyperliquid's terms treat VPN circumvention of restrictions as a breach — [CoinPerps](https://www.coinperps.com/learn/hyperliquid-restricted-countries).

### Inferences
- A compliant single-wallet farmer competes in the same fixed pools as sybil clusters and professional market makers (Q2: Jump at Lighter,
  Extended's internal MM team), so the per-dollar rebate available to an honest small player is diluted by these participants.
- The published per-wallet medians (Q1) partly reflect multi-wallet operators; an honest single wallet should expect less than "median per
  hunter" figures imply if those hunters are clusters.

### Gaps
- Per-programme sybil rules for Variational, Pacifica, Paradex and Lighter were not read in full.

## Q6. Bottom line on the objective and how to MEASURE it with free public data

### Takeaway
On the evidence found, neither category shows a **repeatable** path from $10–15K to $15–20K/yr. Airdrops paid >100% annualised in a few
early, one-off windows (Ethena S1 ≈ +26–100% in six weeks; Hyperliquid's ~$13K mean per wallet), but the systematic data show those were
outliers: 85–93% of 2024–2026 launches fell below TGE, no study counts programmes that paid nothing, and allocation rates per dollar are
unpublished. DePIN pays tens of percent at best on hardware, with subsidies shrinking. A measurement is possible for **fixed-pool perp DEX
programmes** using free data: weekly point pool (docs) × token per point (claim data) × claim price (DefiLlama) ÷ weekly volume (DefiLlama).

### Cited Findings
- Fixed weekly point pools are published (or reported) for Hyperliquid (1M then 700k/week), Lighter (250k/week in S2), Extended (1.2M/week), Variational
  (150k/week), Pacifica (10M/week), Paradex (4M XP/week) — sources in Q2–Q3 above.
- Post-TGE outcome base rates: Keyrock 2024 (only 8 of 62 airdrops positive at 90 days); Memento 2025 (84.7% of 118 TGEs below TGE valuation, median
  FDV −71%) — [Keyrock](https://keyrock.com/airdrops-in-the-barren-desert/); [Memento Research](https://mementoresearch.com/state-of-2025-token-launches-year-in-review).
- Helium reward data are in public S3 oracle exports and on Solana — [freeapihub](https://freeapihub.com/apis/helium-blockchain-api); Syndica publishes
  monthly Solana DePIN rewards vs revenue — [Syndica](https://blog.syndica.io/deep-dive-solana-depin-april-2026/).

### Inferences
**Proposed survivorship-aware measurement (free data; fits the repo's GitHub Actions fetch workflow):**
1. *Universe fixed in advance:* snapshot, on a fixed date, every perp DEX / stablecoin points programme listed on two or more trackers (e.g.
   Dropstab, airdrop calendars) and in the repo's incentive radar; keep programmes that later pay nothing (value 0) or never launch.
2. *Pool value:* weekly points pool (official docs, archived via the rule-change watcher) × tokens per point (claim-contract totals from Dune or the
   token's own explorer; or published pool ÷ points total) × claim-day price (DefiLlama coins API, free).
3. *Denominator:* weekly protocol volume or TVL (DefiLlama derivatives / TVL APIs, free) → rebate per $ of volume (perps) or per $·day (deposits).
4. *Cost:* official fee schedules on both venues + funding difference (Hyperliquid/Lighter funding already in `data/public/`) → net rebate r − c.
5. *Capital map:* convert to ROI on $10K given a margin/leverage cap and realistic weekly volume for one person; report median across programmes and
   re-run without the largest programme (as `docs/PREREG_AIRDROP_20261123.md` requires).
- Expected result from what is known now: the early weeks of Hyperliquid/Lighter-type pools probably show r ≫ c ex post, while the median
  programme (including zeros and the ~85% that fall) probably does not; the prereg's "drop the largest campaign" rule is likely to fail. This
  is an expectation, not a measured result.
- DePIN measurement: per-node reward history is free for Helium (S3 exports/Solana) and network-level for Solana DePINs (Syndica); GEODNET,
  io.net, Akash and Nosana per-node data access was not established.
- Against the repo benchmark (Topstep recycling ≈ $4,097/yr real net; multi-firm plan ≈ $18K/yr on ≈ $14K cash at risk), no DePIN option found
  reaches the target; airdrop farming could only reach it in an unusually good year, and that cannot be shown to be repeatable from public data.

### Gaps
- DefiLlama volume series for Hyperliquid and Lighter were not fetched (API blocked from this sandbox), so the per-$-volume rebate was not computed;
  this is the next concrete step (add a fetch job to `scripts/fetch_public.py`).
- No free source found for per-wallet allocation distributions (medians) for Lighter or Hyperliquid other than claim-contract data on Dune (needs a
  free account/API key).
- Malaysian tax treatment of airdrop or DePIN income was not researched.

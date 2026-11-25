# Radar summary 2026-11-25

Baseline date: 2026-11-21

## Counts
- S2 protocols: 9110
- S1 reward pools: 1301
- S3 Merkl live: 703
- S4 governance hits: 58
- pages fetched ok: 1787
- pages total: 1834
- candidates surviving to ranking: 84
- of which all five filter parts verified: 18
- near-miss rows total: 10933

## Near-miss by stage/reason (top)

- first_pass / below threshold: 10043
- quality / DefiLlama outlier flag: 276
- filter / F4 price exposure, needs hedge; F5 TVL < $1,000,000: 241
- filter / F4 price exposure, needs hedge: 157
- filter / F5 TVL < $1,000,000: 88
- deep / F2 not long-lived: 41
- deep / F1 reward not persistent: 35
- quality / implausible APR > 1000%: 18
- filter / F3 single pool/venue on one chain (no reused setup); F4 price exposure: 11
- gone / disappeared from source (last seen 2026-11-23): 6
- gone / disappeared from source (last seen 2026-11-22): 5
- filter / F3 single pool/venue on one chain (no reused setup): 4
- filter / F3 single pool/venue on one chain (no reused setup); F5 TVL < $1,000,0: 4
- gone / disappeared from source (last seen 2026-11-21): 2
- collect / no data (request failed): 1

## Top 25 by money per competitor (reward APR on competing capital)

| venue | chain | what pays | $/day | capital | reward APR % | F1 | F2 | stable | new | Malaysia |
|---|---|---|---|---|---|---|---|---|---|---|
| curve-dex | Ethereum | BOLD-LUSD nan reward tokens ['0x6440f144b7e50D6a84 | 1,216 | 1,303,268 | 34.1 | fail | pass | True | True | unverified-onchain |
| stake-dao-yield | Ethereum | BOLD-USDC Curve reward tokens ['0x6440f144b7e50D6a | 1,238 | 1,510,441 | 29.9 | pass | fail | True | True | unverified-onchain |
| curve-dex | Ethereum | BOLD-USDC nan reward tokens ['0x6440f144b7e50D6a84 | 9,321 | 11,502,739 | 29.6 | pass | pass | True | False | unverified-onchain |
| stake-dao-yield | Ethereum | PYUSD-CRVUSD Curve reward tokens ['0x5D29949F8e64f | 8,234 | 17,821,529 | 16.9 | pass | fail | True | False | unverified-onchain |
| stake-dao-yield | Ethereum | EVAUSDT-EVAUSDC Curve reward tokens ['0xD533a94974 | 1,553 | 3,736,478 | 15.2 | pass | fail | True | False | unverified-onchain |
| mento-v3 | Monad | AUSD-USDM nan reward tokens ['0xBC69212B8E4d445b23 | 831 | 2,090,131 | 14.5 | fail | fail | True | False | unverified-onchain |
| convex-finance | Ethereum | FRXUSD-MSUSD nan reward tokens ['0xd533a949740bb33 | 832 | 3,030,978 | 10.0 | pass | unverified | True | False | unverified-onchain |
| stake-dao-yield | Ethereum | FRXUSD-DUSD Curve reward tokens ['0xD533a949740bb3 | 284 | 1,082,890 | 9.6 | fail | fail | True | False | unverified-onchain |
| morpho-blue | Ethereum | RE7COUSDC nan reward tokens ['0xa12cc123ba206d4031 | 2,084 | 8,104,557 | 9.4 | fail | fail | True | False | unverified-onchain |
| lista-lending | BSC | USDT nan reward tokens ['0xFceB31A79F71AC9CBDCF853 | 446 | 1,744,882 | 9.3 | fail | fail | True | False | unverified-onchain |
| morpho-blue | Base | RE7VENICEUSDC nan reward tokens ['0xacfe6019ed1a7d | 767 | 3,006,425 | 9.3 | fail | fail | True | False | unverified-onchain |
| convex-finance | Ethereum | FRXUSD-DUSD nan reward tokens ['0xd533a949740bb330 | 670 | 2,640,485 | 9.3 | fail | unverified | True | False | unverified-onchain |
| morpho-blue | Base | BITMXNBP nan reward tokens ['0xF197FFC28c23E0309B5 | 387 | 1,537,810 | 9.2 | fail | fail | True | True | unverified-onchain |
| flying-tulip-ftusd | Ethereum | SFTUSD staked ftUSD (FT rewards bought on open mar | 338 | 1,468,821 | 8.4 | fail | fail | True | False | unverified-onchain |
| morpho-blue | Ethereum | FRAXELERATOR nan reward tokens ['0xcacd6fd266af91b | 231 | 1,033,633 | 8.1 | fail | fail | True | True | unverified-onchain |
| upshift | Stellar | HOLD Supply USDC in Upshift sentUSDC | 13,503 | 61,608,167 | 8.0 | unverified | pass | True | False | unverified-onchain |
| reflect-tranches | Solana | SYRUPUSDC Senior reward tokens ['AvZZF1YaZDziPY2RC | 363 | 1,782,661 | 7.4 | fail | fail | True | True | unverified-onchain |
| sky-lending | Ethereum | USDS GROVE Farming Pool reward tokens ['0xb30FE1CF | 16,843 | 84,301,852 | 7.3 | fail | fail | True | False | unverified-onchain |
| stake-dao-yield | Ethereum | FRXUSD-MSUSD Curve reward tokens ['0xD533a949740bb | 783 | 3,939,412 | 7.3 | pass | fail | True | False | unverified-onchain |
| morpho-blue | Stable | GPYUSDSE nan reward tokens ['0x28f1f38a9f7db1f769a | 11,962 | 61,125,216 | 7.1 | fail | fail | True | False | unverified-onchain |
| aave | Ethereum | LEND Supply RLUSD to the Aave V4 Sentora Hub | 14,493 | 75,571,065 | 7.0 | unverified | unverified | True | False | unverified-onchain |
| bluefin-spot | Sui | USDSUI-USDC 0.01% reward tokens ['0x00000000000000 | 248 | 1,311,671 | 6.9 | pass | pass | True | False | unverified-onchain |
| convex-finance | Ethereum | EVAUSDT-EVAUSDC nan reward tokens ['0xd533a949740b | 468 | 2,487,699 | 6.9 | pass | unverified | True | False | unverified-onchain |
| curve-dex | Ethereum | PMUSD-CRVUSD nan reward tokens ['0xD533a949740bb33 | 267 | 1,451,101 | 6.7 | pass | pass | True | False | unverified-onchain |
| curve-dex | Ethereum | PMUSD-FRXUSD nan reward tokens ['0xD533a949740bb33 | 242 | 1,355,124 | 6.5 | pass | pass | True | False | unverified-onchain |

## Test queue (addendum 3: top 3 venues by 90-day mean of base + 0.9 x reward APR)

- bluefin-spot (Sui) USDSUI-USDC 0.01% reward tokens ['0x000000000000000000000000: 14.86%/yr over 90 d, TVL $1,311,671, pool e3887972-24e6-45a9-8ef5-bcc22b6b5739
- ember (Sui) USDC R25 Treasury reward tokens ['0xdba34672e30cb065b1f93e3a: 11.59%/yr over 90 d, TVL $8,168,499, pool 0ce62070-5201-47d1-84d5-f76d7e0cf5c0
- dolomite (Ethereum) USD1 nan reward tokens ['0xdA5e1988097297dCdc1f90D4dFE7909e8: 7.82%/yr over 90 d, TVL $42,119,660, pool 86e18974-35ca-4948-9c82-694facf9d082

## Governance proposals mentioning incentives (last 45d, newest 25)

- sdcrv-gov.eth: [active] Add a gauge for the following pool: MET/WETH on Mainnet (Metronome DAO) REPUSH https://snapshot.org/#/sdcrv-gov.eth/proposal/0xc96d84e7a7a9c2ea4ea8659b4ce7b509d3b271577734665dbd6f8aa2fca1e2fd
- sdcrv-gov.eth: [active] Add a gauge for the following stableswapNG pool: bdUSD/MUSD on Mainnet (Bitcoin Dollar  REPUSH https://snapshot.org/#/sdcrv-gov.eth/proposal/0x531139312e5b87db43061bbcea2b66cb060b7dcae076a35289d26a475373725c
- cowgrants.eth: [active] Grant Application: CoW BYOS Security Audit https://snapshot.org/#/cowgrants.eth/proposal/0x3357a1a4f928a337883e7fbbe01d2235067c3e7a2a2e4a2696bb9aaebfce9038
- sdcrv-gov.eth: [active] Add a gauge for the following stableswap-NG pool: DOLA/sinvUSD [ https://snapshot.org/#/sdcrv-gov.eth/proposal/0xb6192d05068cf9ebecb2c52057c267e3f3817a1dda8f89e2db623122c68de76e
- sdcrv-gov.eth: [closed] Update gauge implementations on the stableswap-ng, twocrypto-ng and tricrypto-ng factories and on the https://snapshot.org/#/sdcrv-gov.eth/proposal/0x3c0e84ef6ae492abe2b54aede41e4555ca7907f364aad46f0f613540ecfe7410
- sd-yieldbasis.eth: [closed] 63# Move 2.5M YB to a multisig managing incentives for the YB/crvUSD pair https://snapshot.org/#/sd-yieldbasis.eth/proposal/0xefe4c53029244c091751001b65b884cefc6199cb0ec6a7a2dddb64c5a9f0f97f
- assangedao.eth: [closed] AIP-22: Perpetual Fund grants, paid in $JUSTICE https://snapshot.org/#/assangedao.eth/proposal/0x08acb047d8f67bdfd35ba35df1b501238f8440f2cf2b72a76be2d2d3b42a8fa5
- sdfxn.eth: [closed] Gauge vote FXN - 26/11/2026 - 9/12/2026 https://snapshot.org/#/sdfxn.eth/proposal/0xe7837bf1209b388558d4e2beed0160f73cde4fad79a7fe4012849c93195614b3
- sd-yieldbasis.eth: [closed] Gauge vote YB - 26/11/2026 - 9/12/2026 https://snapshot.org/#/sd-yieldbasis.eth/proposal/0x679ea0bfa594140cce624fc024d59bee527a490cc127fbb5f4f7716c8f69079d
- sdfxs.eth: [closed] Gauge vote FXS - 26/11/2026 - 9/12/2026 https://snapshot.org/#/sdfxs.eth/proposal/0x0d32c129ceea51c12bacf857463bffd1156e01b90d5a42e1e6348c98744ee92c
- sdcrv.eth: [closed] Gauge vote CRV - 26/11/2026 - 9/12/2026 https://snapshot.org/#/sdcrv.eth/proposal/0x7e22fd01421f9e4f05cb7ba6242486c1cb236aafa613fddf1cce3c3b7e4e3212
- beets-gauges.eth: [closed] Beets Sonic gauge vote (Round 49) https://snapshot.org/#/beets-gauges.eth/proposal/0xced87b2fc253636be39f3e2fc71e1324fd9b78ee4cb69f833cbc1cc6cd53342f
- sdcrv-gov.eth: [closed] Add a gauge for the following stableswapNG pool: bdUSD/MUSD on Mainnet (Bitcoin Dollar https://snapshot.org/#/sdcrv-gov.eth/proposal/0x778b833a3ff714352912879d80f4b31fc23dcb97bf60aee042621bbdede1b36a
- 1inch.eth: [closed] 1INCH Governance Proposal: Restore Staking Rewards or Eliminate Early Withdrawal Penalties https://snapshot.org/#/1inch.eth/proposal/0x605afa47aecb562f3139738e674f4017ed1ab795c5eac4cadd5ac3376a2dd507
- sdcrv-gov.eth: [closed] Add the MET/WETH pool on Ethereum to the Curve Gauge Controller https://snapshot.org/#/sdcrv-gov.eth/proposal/0xf4b5267569df45f46d2155cea7809cfc27da508d44081fd327cca91c3d01a756
- cratos.eth: [active] CIP-47 With respect to the current reward standard, should we consider extending the deadline to Dece https://snapshot.org/#/cratos.eth/proposal/0xa78ac3f3390dc64a559a5a4e3b6f2ea0879173e3478bd8763f4f0f1ef3111536
- puffer-gauge.eth: [active] Gauge Proposal [22 Gauges] 2026-11-14 01:00 GMT+1 to 2026-11-28 01:00 GMT+1 https://snapshot.org/#/puffer-gauge.eth/proposal/0xf2c95bb4273eb66ccf7fb5a57beaac3608e4624d7659869c660adfdd00a51104
- sdcrv-gov.eth: [closed] Add yscvxCRV/CRV (factory-stable-ng-888) gauge 0x3a1EdF12445b3329485C486467Fa0789dd3C01bC to the Gaug https://snapshot.org/#/sdcrv-gov.eth/proposal/0x2887e0c342a8984e6648af42ec2737ceca725f7fddc9c47842c35bb7f9cdbe49
- 1inch.eth: [closed] [1IP-107] Aqua LP Incentive Program — Season 2 https://snapshot.org/#/1inch.eth/proposal/0x6910f1e7fafaa4f1dd003503fd025752d0de4fbcc9a46c69cad59941bfd35b4d
- stakedao.eth: [closed] (REPUSH) SDGP-69: Claim Deadline for sdPENDLE and sdBAL Voting-Power Rewards https://snapshot.org/#/stakedao.eth/proposal/0xe84f20a814602ed82a81a7d9365e4765930774595a69fc7d248f971f72b201a4
- sdcrv-gov.eth: [closed] Activate wstGBP/crvUSD LlamaLend V2 on Ethereum: set a 80,000 crvUSD borrow cap and 10% admin fee, an https://snapshot.org/#/sdcrv-gov.eth/proposal/0xe047aae704fe64d20f617ffd656e8f6717834f0f8738071e6ada4b969521c1e5
- ideation.shapeshiftdao.eth: [closed] [Ideation] SCP-228: Accept and distribute the Zcash retroactive grant for ShapeShift's Zcash work https://snapshot.org/#/ideation.shapeshiftdao.eth/proposal/0x6b605a315c8e86b79e3ea804d79a668a01e9bc5ca6f76f814a0ff38f2b1813c8
- sdcrv-gov.eth: [closed] Activate wOUSD/crvUSD LlamaLend V2 on Ethereum: set a 950,000 crvUSD borrow cap and 10% admin fee, an https://snapshot.org/#/sdcrv-gov.eth/proposal/0x24100d70b5b57ca622e53bbd8776c68f83888bf4c0a589dc51e831f5984543cf
- sdcrv-gov.eth: [closed] Add a gauge for the following stableswap-NG pool: DOLA/SwanUSD https://snapshot.org/#/sdcrv-gov.eth/proposal/0x3baa878c1450739af8428dacbd0e6e5ccfadaf385e41be51cb2861caf988fe53
- sdcrv-gov.eth: [closed] Activate wOUSD/crvUSD LlamaLend V2 on Ethereum: set a 950,000 crvUSD borrow cap and 10% admin fee, at https://snapshot.org/#/sdcrv-gov.eth/proposal/0xae6c512df20e105b73daa1af8d2dc6bb71759fe0441aad664b707e17d6a7c2fc

## Prop-firm rule/price changes today: 174 pages

- **Topstep** https://www.topstep.com/: $6,000 / Proof of Payout / $1,500
- **Bulenox** https://bulenox.com/: The Ecosystem of Trader Development Get funded up to $750,000
- **E8 Markets** https://e8markets.com/: Average First Payout $5,799 / $81M+ in payouts processed since 2021, verified independently on PropFirmMatch, and PayoutJunction. Our Discord community of 42,495+ traders
- **trade-the-pool (via propfirmmatch)** https://propfirmmatch.com/futures/prop-firms/trade-the-pool: 15% off all accounts + free account of the same size if reaching payout (first order only) excluding $100K and $200K Buying Power - Flex acc / 15% off all accounts + free account of the same size if reaching payout (first order only) excluding $100K and $200K Buying Power - Flex acc / Trade The Pool - Edge - 1-Step - 100K $226.10
- **brightfunded-futures (via propfirmmatch)** https://propfirmmatch.com/futures/prop-firms/brightfunded-futures: BrightFunded Futures - BrightCore - 1 Step 150K $230.00 / $460.00 / BrightFunded Futures - BrightCore - 1 Step 100K $170.00
- **the5ers-futures (via propfirmmatch)** https://propfirmmatch.com/futures/prop-firms/the5ers-futures: Both programs must close all positions before the weekend / Maximum amount per payout request: / $25K: Payout 1 $750 | Payout 2 $875 | Payout 3 $1,000 | Payout 4+ $1,000
- **the-trading-pit-futures (via propfirmmatch)** https://propfirmmatch.com/futures/prop-firms/the-trading-pit-futures: The Trading Pit Futures, established in February 2022 and based in Liechtenstein, offers futures trading through 1-step and 2-step evaluatio
- **aquafunded-futures (via propfirmmatch)** https://propfirmmatch.com/futures/prop-firms/aquafunded-futures: AquaFunded Futures - Instant - Instant 150K $436.20 / AquaFunded Futures - Instant - Instant 25K $172.20 / AquaFunded Futures - Instant - Instant 100K $360.00
- **Goat Funded Futures** https://goatfundedfutures.com/: Goat Funded Futures is a prop firm that gives futures traders access to evaluation and instant funding plans, with up to $750K in simulated  / Goat Funded Futures is a prop firm that gives futures traders access to evaluation and instant funding plans, with up to $750K in simulated  / Daily Payout
- **AquaFunded Futures** https://aquafunded.com/: INSTANT PRO 100K $560 $336 ▼$224 INSTANT PRO 200K $905 $543 ▼$362 INSTANT STANDARD 100K $505 $303 ▼$202 CFDS +200% FEE BACK INSTANT FLEX 100 / Mega Sale fees. INSTANT PRO 100K: $560, now $336. INSTANT PRO 200K: $905, now $543. INSTANT STANDARD 100K: $505, now $303. CFDS: +200% FEE B
- **Traders Launch** https://traderslaunch.com/: Premium $100K–$300K Static #1 on PropScore TL Drops On Sale Now / Example Account $25,000 / Profit Target $1,500
- **The5ers Futures** https://the5ers.com/futures/: for a prop account of up to $500K. / Profit split / $500K
- **Topstep** https://www.topstep.com/live-funded-account-rules: The average is rounded up to the next tier of 25k, $50k, $100k, $150k, or $250k
- **MyFundedFutures** https://myfundedfutures.com/plans/signature: 3 C. B. · Signature 20K 8 payouts
- **MyFundedFutures** https://myfundedfutures.com/plans/builder: $1,600.00
- **MyFundedFutures** https://myfundedfutures.com/plans/rapid: $1,020.60 / $844.20 / $543.60
- **MyFundedFutures** https://myfundedfutures.com/plans/rapid-eod: $1,020.60 / $844.20 / $543.60
- **MyFundedFutures** https://myfundedfutures.com/plans/pro: $1,939.38 / $1,632.16 / $2,480.80
- **Blue Guardian** https://www.blueguardian.com/payouts: $261.03 / $145.26 / $523.80
- **FundedNext Futures** https://fundednext.com/cookie-policy: FundedNext Labs - Limited Slots. Real Experiments. / or get $1,000 extra / $ 306.9 $ 0.0 M+
- **FundedNext Futures** https://fundednext.com/aml-policy: FundedNext Labs - Limited Slots. Real Experiments. / or get $1,000 extra / $ 306.9 $ 0.0 M+
- **The5ers** https://the5ers.com/futures-faqs/: BlackArrow Demo Account 4 Articles Consistency Rule 7 Articles Day Trading new 16 Articles FAQs 22 Articles Payments 4 Articles Payouts 5 Ar
- **E8 Markets** https://e8markets.com/e8-traders-stories: E8 Markets maintains one of the highest average payouts at $3,212 per payout. We provide top-notch support and superb trading conditions. Tr / 32m ago $50,000 Perpetual +$104 / 51m ago $100,000 Classic Markets +$5,653
- **E8 Markets** https://e8markets.com/legal/affiliate: This Agreement supersedes and replaces all prior affiliate program agreements, including but not limited to the previous Forex Affiliate Pro / (n) Qualification Threshold: At least USD $5,000 in revenue and at least five (5) Unique Users generated by the Affiliate’s Discount Codes o / Article IV: Commissions, Attribution and Payout Conditions
- **E8 Markets** https://e8markets.com/compare-simfi-funded-accounts: Average First Payout $5,799
- **Audacity Capital** https://audacitycapital.co.uk/funded-trader-program/: $1,000 / $1,120 / $1,385
- **HyroTrader** https://hyrotrader.com/transparency/: $9,710,050 / $1,737,650 / $1,527
- **Crypto Fund Trader** https://cryptofundtrader.com/faq: If you selected a 1-Phase Evaluation (Classic, Pro or Turbo), there is only one phase: once you reach the profit target of your modality, yo / The trailing drawdown applies only to the former 1-Phase Evaluation (existing accounts) and Break Evaluations. It does not apply to 1-Phase  / Swap fees are not charged on the CFT Terminal. Instead, open positions may be subject to funding fees, which vary in both timing and amount 
- **Crypto Fund Trader** https://cryptofundtrader.com/terms-and-conditions/: 48h Payout: Costs 20% of the evaluation price and allows participants to become eligible for scholarship consideration every 2 ac
- **Goat Funded Futures** https://goatfundedfutures.com/refund-policy: Goat Funded Futures is a prop firm that gives futures traders access to evaluation and instant funding plans, with up to $750K in simulated  / Goat Funded Futures is a prop firm that gives futures traders access to evaluation and instant funding plans, with up to $750K in simulated  / Daily Payout
- **Goat Funded Futures** https://goatfundedfutures.com/terms-and-condition: Goat Funded Futures is a prop firm that gives futures traders access to evaluation and instant funding plans, with up to $750K in simulated  / Goat Funded Futures is a prop firm that gives futures traders access to evaluation and instant funding plans, with up to $750K in simulated  / Daily Payout
- **Goat Funded Futures** https://goatfundedfutures.com/privacy-policy: Goat Funded Futures is a prop firm that gives futures traders access to evaluation and instant funding plans, with up to $750K in simulated  / Goat Funded Futures is a prop firm that gives futures traders access to evaluation and instant funding plans, with up to $750K in simulated  / Daily Payout
- **Goat Funded Futures** https://goatfundedfutures.com/daily-payout-futures-prop-firm: Goat Funded Futures is a prop firm that gives futures traders access to evaluation and instant funding plans, with up to $750K in simulated  / Goat Funded Futures is a prop firm that gives futures traders access to evaluation and instant funding plans, with up to $750K in simulated  / Daily Payout
- **The Trading Pit Futures** https://support.thetradingpit.com/en/articles/835084-cfd-prime-swing-rules: Applies only to 1-Phase $100K and $200K accounts, in both phases. How it's calculated depends on when your account was created: / • Day 1: +$6,000, Day 2: −$2,000, Day 3: +$4,000, Day 4: +$2,000. / • Total Profit is $10,000. Your Best Day (Day 1) is 60% of it, so the rule isn't met yet.
- **Funded Futures Network** https://fundedfuturesnetwork.com/payouts: $5,334,973 / Nov 26 $5,334,973 paid to date / Requested $1,364
- **Traders Launch** https://traderslaunch.com/payout-rules: Payout Rules | Traders Launch
- **MyFundedFutures** https://myfundedfutures.com/coupons: $1,939.38 / $1,632.16 / $2,480.80
- **MyFundedFutures** https://help.myfundedfutures.com/en/articles/13523548-instant-sim-funded-upgrade: Consistency Rule at My FundedFutures
- **MyFundedFutures** https://help.myfundedfutures.com/en/articles/12879226-pro-plan-1day-addon: Flex Plan - $25,000 / A Comprehensive Guide
- **Goat Funded Trader** https://help.goatfundedtrader.com/rewards.html: Minimum Profit & Profitable Days: Traders must have a minimum profit of 3% in their account and complete the same number of minimum profitab
- **Audacity Capital** https://audacitycapital.co.uk/tr/funded-trader-program/: $1,000 / $1,000 / $1.940
- **Audacity Capital** https://audacitycapital.co.uk/pt/funded-trader-program/: $1.000 / $1.120 / $1.385
- **Audacity Capital** https://audacitycapital.co.uk/tl/funded-trader-program/: $1,000 / $1,120 / $1,385
- **Audacity Capital** https://audacitycapital.co.uk/ar/funded-trader-program/: $1,120 / $1,120
- **Audacity Capital** https://audacitycapital.co.uk/hi/funded-trader-program/: $1,000 / $1,120 / $1,560
- **AquaFunded Futures** https://www.aquafunded.com: INSTANT PRO 100K $560 $336 ▼$224 INSTANT PRO 200K $905 $543 ▼$362 INSTANT STANDARD 100K $505 $303 ▼$202 CFDS +200% FEE BACK INSTANT FLEX 100 / Mega Sale fees. INSTANT PRO 100K: $560, now $336. INSTANT PRO 200K: $905, now $543. INSTANT STANDARD 100K: $505, now $303. CFDS: +200% FEE B
- **AquaFunded Futures** https://www.aquafunded.com/: INSTANT PRO 100K $560 $336 ▼$224 INSTANT PRO 200K $905 $543 ▼$362 INSTANT STANDARD 100K $505 $303 ▼$202 CFDS +200% FEE BACK INSTANT FLEX 100 / Mega Sale fees. INSTANT PRO 100K: $560, now $336. INSTANT PRO 200K: $905, now $543. INSTANT STANDARD 100K: $505, now $303. CFDS: +200% FEE B
- **DayTraders** https://daytraders.com/help/articles/17684753-s2f-consistency: S2L Consistency
- **DayTraders** https://daytraders.com/help/articles/17704121-how-to-request-a-payout: Static Payouts
- **DayTraders** https://daytraders.com/help/articles/17697907-s2l-consistency: EOD Consistency
- **DayTraders** https://daytraders.com/help/articles/17697925-moving-from-pro-or-s2f-to-live: EOD Payouts
- **DayTraders** https://daytraders.com/help/articles/17704079-supported-platforms: ArcTrader is fully supported by DayTraders. For other third-party platforms we offer limited support. For platform issues, contact the platf

## Page changes today: 186

- Topstep (firm) https://www.topstep.com/: +223 / -185 lines
- MyFundedFutures (firm) https://help.myfundedfutures.com/: +3 / -2 lines
- Bulenox (firm) https://bulenox.com/: +1 / -1 lines
- FXIFY (firm) https://fxify.com/: +6 / -6 lines
- The5ers (firm) https://the5ers.com/: +4 / -4 lines
- E8 Markets (firm) https://e8markets.com/: +44 / -44 lines
- Crypto Fund Trader (firm) https://cryptofundtrader.com/: +45 / -46 lines
- QT Funded (firm) https://qtfunded.com/: +1 / -1 lines
- propfirmmatch (directory) https://propfirmmatch.com/: +28 / -28 lines
- saveonpropfirms (directory) https://saveonpropfirms.com/: +1 / -1 lines
- Polymarket (docs) https://docs.polymarket.com/changelog: +4 / -1 lines
- Kalshi (docs) https://docs.kalshi.com/changelog: +21 / -1 lines
- Morpho (docs) https://docs.morpho.org/: +2 / -1 lines
- Kamino (docs) https://docs.kamino.finance/: +1 / -2 lines
- Jupiter (docs) https://station.jup.ag/docs: +1 / -1 lines
- dYdX v4 (release) https://github.com/dydxprotocol/v4-chain/releases.atom: +1 / -1 lines
- blueberry-futures (via propfirmmatch) (directory_firm) https://propfirmmatch.com/futures/prop-firms/blueberry-futures: +2 / -2 lines
- finotive-futures (via propfirmmatch) (directory_firm) https://propfirmmatch.com/futures/prop-firms/finotive-futures: +2 / -2 lines
- futureselite (via propfirmmatch) (directory_firm) https://propfirmmatch.com/futures/prop-firms/futureselite: +7 / -7 lines
- goat-funded-futures (via propfirmmatch) (directory_firm) https://propfirmmatch.com/futures/prop-firms/goat-funded-futures: +4 / -4 lines
- hola-prime-futures (via propfirmmatch) (directory_firm) https://propfirmmatch.com/futures/prop-firms/hola-prime-futures: +2 / -2 lines
- trade-the-pool (via propfirmmatch) (directory_firm) https://propfirmmatch.com/futures/prop-firms/trade-the-pool: +16 / -16 lines
- traders-launch (via propfirmmatch) (directory_firm) https://propfirmmatch.com/futures/prop-firms/traders-launch: +7 / -6 lines
- ylos-trading (via propfirmmatch) (directory_firm) https://propfirmmatch.com/futures/prop-firms/ylos-trading: +2 / -2 lines
- e8-futures (via propfirmmatch) (directory_firm) https://propfirmmatch.com/futures/prop-firms/e8-futures: +4 / -4 lines
- brightfunded-futures (via propfirmmatch) (directory_firm) https://propfirmmatch.com/futures/prop-firms/brightfunded-futures: +22 / -14 lines
- the5ers-futures (via propfirmmatch) (directory_firm) https://propfirmmatch.com/futures/prop-firms/the5ers-futures: +21 / -19 lines
- the-trading-pit-futures (via propfirmmatch) (directory_firm) https://propfirmmatch.com/futures/prop-firms/the-trading-pit-futures: +5 / -5 lines
- aquafunded-futures (via propfirmmatch) (directory_firm) https://propfirmmatch.com/futures/prop-firms/aquafunded-futures: +17 / -17 lines
- Goat Funded Futures (firm) https://goatfundedfutures.com/: +16 / -6 lines
- AquaFunded Futures (firm) https://aquafunded.com/: +7 / -3 lines
- Traders Launch (firm) https://traderslaunch.com/: +23 / -5 lines
- The5ers Futures (firm) https://the5ers.com/futures/: +160 / -162 lines
- Immunefi (contest) https://immunefi.com/bug-bounty/: +6 / -6 lines
- Bebop (bot_docs) https://docs.bebop.xyz/: +1 / -1 lines
- CoW services (release) https://github.com/cowprotocol/services/releases.atom: +5 / -5 lines
- Orderly docs (mm_program) https://orderly.network/docs/home: +1 / -1 lines
- Topstep (firm_sub) https://www.topstep.com/live-funded-account-rules: +3 / -3 lines
- Topstep (firm_sub) https://help.topstep.com/en/articles/8284117-topstep-refund-policies: +1 / -1 lines
- Topstep (firm_sub) https://help.topstep.com/en/articles/8284215-express-funded-account-parameters: +1 / -1 lines

## Non-prop leads (docs/PREREG_RADAR_NONPROP_20261124.md): new today 5

### Extreme funding (1)
- BIGTIME: funding -4380%/yr, open interest $2,112,462 https://app.hyperliquid.xyz/trade/BIGTIME

### Audit contest prizes (1)
- Immunefi: page changed; largest amount in added text $500,000 https://immunefi.com/bug-bounty/

### Governance: incentives / bot programmes (1)
- lido: LEGO Grant Proposal: eth-hw-signer https://research.lido.fi/t/lego-grant-proposal-eth-hw-signer/12227

### Malaysia access / bot-role docs / market-maker programme changes (2)
- Bebop: changed: {"docsConfig":{"theme":"mint","$schema":"https://mintlify.com/docs.json","name":"Bebop API Docs","colors":{"primary":"#0 https://docs.bebop.xyz/
- Orderly docs: changed: {"docsConfig":{"theme":"mint","$schema":"https://mintlify.com/docs.json","name":"Orderly","colors":{"primary":"#aa5cf8", https://orderly.network/docs/home

### Source health
- N1 stablecoins: 459
- N2 Hyperliquid perps: 235
- N3 CoW payouts (21d): 604 transfers, COW price 0.09383068350000001, $650,998 to 53 recipients
- N5 forums answering: 22/23
- N4 Cantina item keys: allowedSeverities,cantinaTriaged,company,createdAt,currencyCode,entryFee,id,instructions,joined,kind,kycRequired,name,status,timeframe,totalFindings,totalRewardPot,url
- N4 statuses: {'cantina:complete': 144, 'sherlock:FINISHED': 30, 'cantina:live': 1, 'cantina:escalations': 1}
- N4 contests listed: 30 Sherlock, 146 Cantina
- N7 derivatives venues (CoinGecko): 100; BTC $58552.99

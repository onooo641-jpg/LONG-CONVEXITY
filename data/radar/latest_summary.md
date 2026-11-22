# Radar summary 2026-11-22

Baseline date: 2026-11-21

## Counts
- S2 protocols: 9088
- S1 reward pools: 1292
- S3 Merkl live: 713
- S4 governance hits: 60
- pages fetched ok: 1766
- pages total: 1814
- candidates surviving to ranking: 91
- of which all five filter parts verified: 20
- near-miss rows total: 6104

## Near-miss by stage/reason (top)

- first_pass / below threshold: 5285
- quality / DefiLlama outlier flag: 269
- filter / F4 price exposure, needs hedge; F5 TVL < $1,000,000: 224
- filter / F4 price exposure, needs hedge: 145
- filter / F5 TVL < $1,000,000: 83
- deep / F2 not long-lived: 34
- deep / F1 reward not persistent: 30
- quality / implausible APR > 1000%: 13
- filter / F3 single pool/venue on one chain (no reused setup); F4 price exposure: 10
- filter / F3 single pool/venue on one chain (no reused setup); F5 TVL < $1,000,0: 4
- filter / F3 single pool/venue on one chain (no reused setup): 4
- gone / disappeared from source (last seen 2026-11-21): 2
- collect / no data (request failed): 1

## Top 25 by money per competitor (reward APR on competing capital)

| venue | chain | what pays | $/day | capital | reward APR % | F1 | F2 | stable | new | Malaysia |
|---|---|---|---|---|---|---|---|---|---|---|
| curve-dex | Ethereum | BOLD-USDC nan reward tokens ['0x6440f144b7e50D6a84 | 9,387 | 9,346,848 | 36.7 | pass | pass | True | False | unverified-onchain |
| curve-dex | Ethereum | BOLD-LUSD nan reward tokens ['0x6440f144b7e50D6a84 | 1,217 | 1,226,625 | 36.2 | fail | pass | True | True | unverified-onchain |
| stake-dao-yield | Ethereum | PYUSD-CRVUSD Curve reward tokens ['0x5D29949F8e64f | 15,446 | 17,871,859 | 31.5 | pass | fail | True | False | unverified-onchain |
| mento-v3 | Monad | AUSD-USDM nan reward tokens ['0xBC69212B8E4d445b23 | 835 | 2,098,473 | 14.5 | fail | fail | True | False | unverified-onchain |
| morpho-blue | Ethereum | RE7COUSDC nan reward tokens ['0xa12cc123ba206d4031 | 2,241 | 6,140,822 | 13.3 | fail | fail | True | False | unverified-onchain |
| convex-finance | Ethereum | PMUSD-CRVUSD nan reward tokens ['0xd533a949740bb33 | 334 | 1,078,624 | 11.3 | pass | unverified | True | False | unverified-onchain |
| stake-dao-yield | Ethereum | PMUSD-CRVUSD Curve reward tokens ['0xD533a949740bb | 332 | 1,088,412 | 11.1 | pass | fail | True | False | unverified-onchain |
| lista-lending | BSC | USDT nan reward tokens ['0xFceB31A79F71AC9CBDCF853 | 304 | 1,039,914 | 10.7 | fail | fail | True | False | unverified-onchain |
| morpho-blue | Base | RE7VENICEUSDC nan reward tokens ['0xacfe6019ed1a7d | 769 | 2,710,998 | 10.4 | fail | fail | True | False | unverified-onchain |
| curve-dex | Ethereum | USDT-USDTE nan reward tokens ['0xD533a949740bb3306 | 282 | 1,011,014 | 10.2 | fail | fail | True | False | unverified-onchain |
| stake-dao-yield | Ethereum | FRXUSD-DUSD Curve reward tokens ['0xD533a949740bb3 | 293 | 1,084,430 | 9.8 | fail | fail | True | False | unverified-onchain |
| convex-finance | Ethereum | FRXUSD-DUSD nan reward tokens ['0xd533a949740bb330 | 693 | 2,640,727 | 9.6 | fail | unverified | True | False | unverified-onchain |
| sky-lending | Ethereum | USDS GROVE Farming Pool reward tokens ['0xb30FE1CF | 16,801 | 64,380,008 | 9.5 | fail | fail | True | False | unverified-onchain |
| convex-finance | Ethereum | FRXUSD-MSUSD nan reward tokens ['0xd533a949740bb33 | 744 | 2,989,861 | 9.1 | pass | unverified | True | False | unverified-onchain |
| upshift | Stellar | HOLD Supply USDC in Upshift sentUSDC | 10,064 | 45,916,498 | 8.0 | unverified | pass | True | False | unverified-onchain |
| lista-lending | Ethereum | USDC nan reward tokens ['coingecko:lista'] | 550 | 2,531,227 | 7.9 | pass | pass | True | False | unverified-onchain |
| morpho-blue | Stable | GPYUSDSE nan reward tokens ['0x28f1f38a9f7db1f769a | 8,449 | 39,942,408 | 7.7 | fail | fail | True | False | unverified-onchain |
| stake-dao-yield | Ethereum | FRXUSD-MSUSD Curve reward tokens ['0xD533a949740bb | 811 | 3,935,296 | 7.5 | pass | fail | True | False | unverified-onchain |
| convex-finance | Ethereum | EVAUSDT-EVAUSDC nan reward tokens ['0xd533a949740b | 484 | 2,376,997 | 7.4 | fail | unverified | True | False | unverified-onchain |
| yearn-finance | Katana | VBUSDC nan reward tokens ['0x7F1f4b4b29f5058fA32CC | 1,245 | 6,219,649 | 7.3 | pass | pass | True | False | unverified-onchain |
| flying-tulip-ftusd | Ethereum | SFTUSD staked ftUSD (FT rewards bought on open mar | 333 | 1,707,488 | 7.1 | fail | fail | True | False | unverified-onchain |
| aave | Ethereum | LEND Supply RLUSD to the Aave V4 Sentora Hub | 14,853 | 77,450,056 | 7.0 | unverified | unverified | True | False | unverified-onchain |
| stake-dao-yield | Ethereum | FRXUSD-CRVUSD Curve reward tokens ['0xD533a949740b | 197 | 1,070,795 | 6.7 | pass | fail | True | False | unverified-onchain |
| stake-dao-yield | Ethereum | EVAUSDT-EVAUSDC Curve reward tokens ['0xD533a94974 | 682 | 3,763,660 | 6.6 | pass | fail | True | False | unverified-onchain |
| bluefin-spot | Sui | USDSUI-USDC 0.01% reward tokens ['0x00000000000000 | 242 | 1,358,472 | 6.5 | pass | pass | True | False | unverified-onchain |

## Test queue (addendum 3: top 3 venues by 90-day mean of base + 0.9 x reward APR)

- ember (Sui) USDC Ember Concentrated Liquidity reward tokens ['0x00000000: 15.71%/yr over 90 d, TVL $1,564,683, pool 0a3c5663-73bd-4d8a-bdcc-5e529a8b741d
- bluefin-spot (Sui) USDSUI-USDC 0.01% reward tokens ['0x000000000000000000000000: 15.20%/yr over 90 d, TVL $1,358,472, pool e3887972-24e6-45a9-8ef5-bcc22b6b5739
- dolomite (Ethereum) USD1 nan reward tokens ['0xdA5e1988097297dCdc1f90D4dFE7909e8: 7.81%/yr over 90 d, TVL $44,923,480, pool 86e18974-35ca-4948-9c82-694facf9d082

## Governance proposals mentioning incentives (last 45d, newest 25)

- sdcrv-gov.eth: [active] Update gauge implementations on the stableswap-ng, twocrypto-ng and tricrypto-ng factories and on the https://snapshot.org/#/sdcrv-gov.eth/proposal/0x3c0e84ef6ae492abe2b54aede41e4555ca7907f364aad46f0f613540ecfe7410
- sd-yieldbasis.eth: [active] 63# Move 2.5M YB to a multisig managing incentives for the YB/crvUSD pair https://snapshot.org/#/sd-yieldbasis.eth/proposal/0xefe4c53029244c091751001b65b884cefc6199cb0ec6a7a2dddb64c5a9f0f97f
- assangedao.eth: [closed] AIP-22: Perpetual Fund grants, paid in $JUSTICE https://snapshot.org/#/assangedao.eth/proposal/0x08acb047d8f67bdfd35ba35df1b501238f8440f2cf2b72a76be2d2d3b42a8fa5
- sdfxn.eth: [active] Gauge vote FXN - 26/11/2026 - 9/12/2026 https://snapshot.org/#/sdfxn.eth/proposal/0xe7837bf1209b388558d4e2beed0160f73cde4fad79a7fe4012849c93195614b3
- sd-yieldbasis.eth: [active] Gauge vote YB - 26/11/2026 - 9/12/2026 https://snapshot.org/#/sd-yieldbasis.eth/proposal/0x679ea0bfa594140cce624fc024d59bee527a490cc127fbb5f4f7716c8f69079d
- sdfxs.eth: [active] Gauge vote FXS - 26/11/2026 - 9/12/2026 https://snapshot.org/#/sdfxs.eth/proposal/0x0d32c129ceea51c12bacf857463bffd1156e01b90d5a42e1e6348c98744ee92c
- sdcrv.eth: [active] Gauge vote CRV - 26/11/2026 - 9/12/2026 https://snapshot.org/#/sdcrv.eth/proposal/0x7e22fd01421f9e4f05cb7ba6242486c1cb236aafa613fddf1cce3c3b7e4e3212
- beets-gauges.eth: [active] Beets Sonic gauge vote (Round 49) https://snapshot.org/#/beets-gauges.eth/proposal/0xced87b2fc253636be39f3e2fc71e1324fd9b78ee4cb69f833cbc1cc6cd53342f
- sdcrv-gov.eth: [closed] Add a gauge for the following stableswapNG pool: bdUSD/MUSD on Mainnet (Bitcoin Dollar https://snapshot.org/#/sdcrv-gov.eth/proposal/0x778b833a3ff714352912879d80f4b31fc23dcb97bf60aee042621bbdede1b36a
- 1inch.eth: [active] 1INCH Governance Proposal: Restore Staking Rewards or Eliminate Early Withdrawal Penalties https://snapshot.org/#/1inch.eth/proposal/0x605afa47aecb562f3139738e674f4017ed1ab795c5eac4cadd5ac3376a2dd507
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
- magpiexyz.eth: [closed] MIP #102 – Cease MGP Emissions to the mWOM Pools https://snapshot.org/#/magpiexyz.eth/proposal/0x4dcea4bbe438757d0fad375ea473b8f221730e6a4622e98e158a29fe4c9ac6f7
- qbio-phase2.eth: [closed] DP37 - Three-Month Continuation Grant Agreement https://snapshot.org/#/qbio-phase2.eth/proposal/0x9e8dbe408a08debd37a4b8ab66f6b61382cc59e4dc7fd9db90e597dec6a8d2a5
- fusedao.eth: [closed] FIP14: Zero Inflation, 400M Cap Enforced On-Chain, 30M FUSE for Validator Rewards Through the Transit https://snapshot.org/#/fusedao.eth/proposal/0x2cba3ecb0f952ebb2d82583bb9279cc836e36c18ce2ed540299ab254dcdc5e94
- sdfxn.eth: [closed] Gauge vote FXN - 12/11/2026 - 25/11/2026 https://snapshot.org/#/sdfxn.eth/proposal/0x6214cbfb2dd2fcd86ba05d14fd8a5297622c9ec18b1fc7447e7e3304743eb31a

## Prop-firm rule/price changes today: 182 pages

- **E8 Markets** https://e8markets.com/: $81M+ in payouts processed since 2021, verified independently on PropFirmMatch, and PayoutJunction. Our Discord community of 42,359+ traders
- **DayTraders** https://daytraders.com/: You need $0 and today / Payouts Automated approval / Payout certificates
- **MyFundedFutures** https://myfundedfutures.com/plans/builder: ² Payouts are based on simulated account profits and are subject to rules compliance, trading day requirements, and firm review. See program / Permitted Instruments: Participants may trade, within the simulated environment only, standardized futures contracts listed on regulated U.S / 39.2% of participants who reached the simulated Funded Stage earned at least one payout²;
- **MyFundedFutures** https://myfundedfutures.com/plans/rapid: $1,492.67 / $2,790.00 / $1,961.30
- **MyFundedFutures** https://myfundedfutures.com/plans/rapid-eod: $1,492.67 / $2,790.00 / $1,961.30
- **MyFundedFutures** https://myfundedfutures.com/plans/pro: ² Payouts are based on simulated account profits and are subject to rules compliance, trading day requirements, and firm review. See program / Permitted Instruments: Participants may trade, within the simulated environment only, standardized futures contracts listed on regulated U.S / 39.2% of participants who reached the simulated Funded Stage earned at least one payout²;
- **Blue Guardian** https://www.blueguardian.com/payouts: $227.85
- **FundedNext Futures** https://fundednext.com/cfds: $ 100K / $549.99 / $ 200K
- **FundedNext Futures** https://fundednext.com/cookie-policy: FundedNext Labs - Limited Slots. Real Experiments. / or get $1,000 extra / $ 306.9 $ 0.0 M+
- **FundedNext Futures** https://fundednext.com/aml-policy: FundedNext Labs - Limited Slots. Real Experiments. / or get $1,000 extra / $ 306.9 $ 0.0 M+
- **E8 Markets** https://e8markets.com/e8-traders-stories: 12h ago $5,000 Perpetual +$128 / 18h ago $5,000 Perpetual +$310 / 21h ago $25,000 Classic Markets +$487
- **HyroTrader** https://hyrotrader.com/transparency/: $9,657,277 / $1,534 / $456,529
- **Funded Futures Network** https://fundedfuturesnetwork.com/payouts: $5,321,605 / Nov 26 $5,321,605 paid to date / Requested $500
- **Traders Launch** https://traderslaunch.com/results: Results & Payouts | Traders Launch
- **FuturesElite** https://faq.futureselite.com/en/articles/17584271-elite-payouts: Nitro payouts
- **FuturesElite** https://faq.futureselite.com/en/articles/17585527-the-live-trading-program: Elite payouts
- **MyFundedFutures** https://myfundedfutures.com/studio: ² Payouts are based on simulated account profits and are subject to rules compliance, trading day requirements, and firm review. See program / Permitted Instruments: Participants may trade, within the simulated environment only, standardized futures contracts listed on regulated U.S / 39.2% of participants who reached the simulated Funded Stage earned at least one payout²;
- **MyFundedFutures** https://myfundedfutures.com/plans/builder: ² Payouts are based on simulated account profits and are subject to rules compliance, trading day requirements, and firm review. See program / Permitted Instruments: Participants may trade, within the simulated environment only, standardized futures contracts listed on regulated U.S / 39.2% of participants who reached the simulated Funded Stage earned at least one payout²;
- **MyFundedFutures** https://myfundedfutures.com/plans/rapid-eod: ² Payouts are based on simulated account profits and are subject to rules compliance, trading day requirements, and firm review. See program / Permitted Instruments: Participants may trade, within the simulated environment only, standardized futures contracts listed on regulated U.S / 39.2% of participants who reached the simulated Funded Stage earned at least one payout²;
- **MyFundedFutures** https://myfundedfutures.com/plans/pro: ² Payouts are based on simulated account profits and are subject to rules compliance, trading day requirements, and firm review. See program / Permitted Instruments: Participants may trade, within the simulated environment only, standardized futures contracts listed on regulated U.S / 39.2% of participants who reached the simulated Funded Stage earned at least one payout²;
- **FundedNext Futures** https://fundednext.com/terms-of-service: FundedNext Labs - Limited Slots. Real Experiments. / or get $1,000 extra / $ 306.9 $ 0.0 M+
- **MyFundedFutures** https://myfundedfutures.com/plans/rapid: ² Payouts are based on simulated account profits and are subject to rules compliance, trading day requirements, and firm review. See program / Permitted Instruments: Participants may trade, within the simulated environment only, standardized futures contracts listed on regulated U.S / 39.2% of participants who reached the simulated Funded Stage earned at least one payout²;
- **MyFundedFutures** https://myfundedfutures.com/plans/rapid-eod: ² Payouts are based on simulated account profits and are subject to rules compliance, trading day requirements, and firm review. See program / Permitted Instruments: Participants may trade, within the simulated environment only, standardized futures contracts listed on regulated U.S / 39.2% of participants who reached the simulated Funded Stage earned at least one payout²;
- **MyFundedFutures** https://myfundedfutures.com/plans/pro: ² Payouts are based on simulated account profits and are subject to rules compliance, trading day requirements, and firm review. See program / Permitted Instruments: Participants may trade, within the simulated environment only, standardized futures contracts listed on regulated U.S / 39.2% of participants who reached the simulated Funded Stage earned at least one payout²;
- **HyroTrader** https://hyrotrader.com/transparency/: 16 hours ago Solana zMiJcT…HBJ2BW $28.00 Solscan / 16 hours ago Solana 41rGic…p3Ah8c $51.00 Solscan / 16 hours ago Solana 4NA6vD…LmY9y1 $2,000.00 Solscan
- **Traders Launch** https://traderslaunch.com/results: Results & Payouts | Traders Launch
- **Traders Launch** https://traderslaunch.com/payout-rules: Payout Rules | Traders Launch
- **FundedNext Futures** https://fundednext.com/terms-of-service: 1.6. In the event of any conflict, discrepancy or inconsistency between (i) these Terms (main text) and (ii) any Policies, Rules, Annexes, F
- **Traders Launch** https://traderslaunch.com/payout-rules: Payout Rules | Traders Launch
- **The5ers** https://the5ers.com/: But l’m here to say i followed all rules and got my first payout within 6 hrs requesting 👍🏽 and also their support team is great shout out t
- **Traders Launch** https://traderslaunch.com/: Premium $100K–$300K Static #1 on PropScore TL Drops Limited Drops / TL Drops are how we launch new account types: numbered drops, each on sale for a limited time at a launch price. Get an email the moment the
- **The5ers Futures** https://the5ers.com/futures/: But l’m here to say i followed all rules and got my first payout within 6 hrs requesting 👍🏽 and also their support team is great shout out t
- **MyFundedFutures** https://myfundedfutures.com/studio: ² Payouts are based on simulated account profits and are subject to rules compliance, trading day requirements, and firm review. See program / Permitted Instruments: Participants may trade, within the simulated environment only, standardized futures contracts listed on regulated U.S / 39.2% of participants who reached the simulated Funded Stage earned at least one payout²;
- **MyFundedFutures** https://myfundedfutures.com/plans/builder: $800.00 / Payout auto-approved / $800.00
- **MyFundedFutures** https://myfundedfutures.com/plans/rapid: $706.50 / $456.30 / $1,964.70
- **MyFundedFutures** https://myfundedfutures.com/plans/rapid-eod: $706.50 / $456.30 / $1,964.70
- **MyFundedFutures** https://myfundedfutures.com/plans/pro: ² Payouts are based on simulated account profits and are subject to rules compliance, trading day requirements, and firm review. See program / Permitted Instruments: Participants may trade, within the simulated environment only, standardized futures contracts listed on regulated U.S / 39.2% of participants who reached the simulated Funded Stage earned at least one payout²;
- **E8 Markets** https://e8markets.com/e8-traders-stories: 4h ago $50,000 Classic Markets +$1,800 / 9h ago $50,000 Classic Markets +$4,500 / 10h ago $25,000 Classic Markets +$441
- **HyroTrader** https://hyrotrader.com/transparency/: 22 hours ago Solana 4mTQ8g…UXmMXD $400.00 Solscan / 22 hours ago Solana 4wt3Cn…MCXPdk $241.02 Solscan / 22 hours ago Solana 5YSkBq…zjFyJU $78.17 Solscan
- **Traders Launch** https://traderslaunch.com/results: Results & Payouts | Traders Launch
- **Traders Launch** https://traderslaunch.com/payout-rules: Payout Rules | Traders Launch
- **Topstep** https://help.topstep.com/en/articles/11748475-dynamic-live-risk-expansion: Topstep Payout Policy
- **Topstep** https://help.topstep.com/en/articles/12578731-how-identity-verification-works: Topstep Payout Policy
- **Blueberry Futures** http://help.blueberryfutures.com/en/articles/12891015-drawdown-types-eod-vs-trailing-explained: How much does an Account Reset cost? (Evaluation & Funded)
- **Blueberry Futures** http://help.blueberryfutures.com/en/articles/11196022-do-you-have-payout-caps: What Is the Profit Split at Blueberry Futures?
- **Traders Launch** https://traderslaunch.com/: Premium $100K–$300K Static #1 on PropScore TL Drops On Sale Now / Example Account $25,000 / Profit Target $1,500
- **The5ers Futures** https://the5ers.com/futures/: Profit Target / $1,500 / $1,000
- **MyFundedFutures** https://myfundedfutures.com/plans/rapid: ² Payouts are based on simulated account profits and are subject to rules compliance, trading day requirements, and firm review. See program / Permitted Instruments: Participants may trade, within the simulated environment only, standardized futures contracts listed on regulated U.S / 39.2% of participants who reached the simulated Funded Stage earned at least one payout²;
- **MyFundedFutures** https://myfundedfutures.com/plans/rapid-eod: $1,229.00 / $1,807.00 / $866.00
- **FundedNext Futures** https://fundednext.com/cookie-policy: Cookies are small files that are stored on your device and that help us collect information about your activities. In particular, cookies al / Most browsers automatically accept cookies by default. You can get more information about setting up cookies for the most common browsers he / These cookies allow you to browse the Website and use its functionalities. Through these cookies, we also ensure the security and administra
- **The5ers** https://the5ers.com/futures-faqs/: BlackArrow Demo Account 4 Articles Consistency Rule 7 Articles Day Trading new 15 Articles FAQs 22 Articles Payments 4 Articles Payouts 5 Ar
- **E8 Markets** https://e8markets.com/e8-traders-stories: 6h ago $50,000 Classic Markets +$1,800 / 11h ago $50,000 Classic Markets +$4,500 / 12h ago $25,000 Classic Markets +$441
- **HyroTrader** https://hyrotrader.com/transparency/: 24 hours ago Solana 4mTQ8g…UXmMXD $400.00 Solscan / 24 hours ago Solana 4wt3Cn…MCXPdk $241.02 Solscan / 24 hours ago Solana 5YSkBq…zjFyJU $78.17 Solscan
- **Traders Launch** https://traderslaunch.com/payout-rules: Payout Rules | Traders Launch

## Page changes today: 190

- E8 Markets (firm) https://e8markets.com/: +15 / -15 lines
- Crypto Fund Trader (firm) https://cryptofundtrader.com/: +7 / -7 lines
- propfirmmatch (directory) https://propfirmmatch.com/: +16 / -16 lines
- Kalshi (docs) https://docs.kalshi.com/changelog: +28 / -1 lines
- Lighter (docs) https://docs.lighter.xyz/: +1 / -1 lines
- goat-funded-futures (via propfirmmatch) (directory_firm) https://propfirmmatch.com/futures/prop-firms/goat-funded-futures: +2 / -2 lines
- hola-prime-futures (via propfirmmatch) (directory_firm) https://propfirmmatch.com/futures/prop-firms/hola-prime-futures: +2 / -2 lines
- traders-launch (via propfirmmatch) (directory_firm) https://propfirmmatch.com/futures/prop-firms/traders-launch: +2 / -2 lines
- ylos-trading (via propfirmmatch) (directory_firm) https://propfirmmatch.com/futures/prop-firms/ylos-trading: +2 / -2 lines
- the5ers-futures (via propfirmmatch) (directory_firm) https://propfirmmatch.com/futures/prop-firms/the5ers-futures: +2 / -2 lines
- the-trading-pit-futures (via propfirmmatch) (directory_firm) https://propfirmmatch.com/futures/prop-firms/the-trading-pit-futures: +2 / -2 lines
- BluSky Trading Company (firm) https://bluskytrading.com/: +1 / -1 lines
- DayTraders (firm) https://daytraders.com/: +81 / -88 lines
- Topstep (firm_sub) https://help.topstep.com/en/articles/10657969-live-funded-account-parameters: +1 / -1 lines
- Topstep (firm_sub) https://help.topstep.com/en/articles/8284233-topstep-payout-policy: +1 / -1 lines
- Topstep (firm_sub) https://help.topstep.com/en/articles/8284208-consistency-at-topstep: +1 / -1 lines
- Topstep (firm_sub) https://help.topstep.com/en/articles/8284197-trading-combine-parameters: +1 / -1 lines
- MyFundedFutures (firm_sub) https://myfundedfutures.com/studio: +22 / -22 lines
- MyFundedFutures (firm_sub) https://myfundedfutures.com/plans/builder: +36 / -21 lines
- MyFundedFutures (firm_sub) https://myfundedfutures.com/plans/rapid: +6 / -6 lines
- MyFundedFutures (firm_sub) https://myfundedfutures.com/plans/rapid-eod: +21 / -15 lines
- MyFundedFutures (firm_sub) https://myfundedfutures.com/plans/pro: +15 / -15 lines
- Blue Guardian (firm_sub) https://www.blueguardian.com/payouts: +18 / -18 lines
- Top One Futures (firm_sub) https://help.toponefutures.com/en/articles/10907463-what-is-the-maximum-number-of-accounts-i-can-trade: +1 / -1 lines
- FundedNext Futures (firm_sub) https://fundednext.com/cfds: +6 / -0 lines
- FundedNext Futures (firm_sub) https://fundednext.com/cookie-policy: +89 / -44 lines
- FundedNext Futures (firm_sub) https://fundednext.com/aml-policy: +89 / -44 lines
- E8 Markets (firm_sub) https://e8markets.com/e8-traders-stories: +30 / -30 lines
- Audacity Capital (firm_sub) https://audacitycapital.co.uk/funded-trader-program/: +20 / -20 lines
- HyroTrader (firm_sub) https://hyrotrader.com/transparency/: +15 / -15 lines
- BluSky Trading Company (firm_sub) https://bluskytrading.com/faq/: +1 / -1 lines
- BluSky Trading Company (firm_sub) https://bluskytrading.com/terms-and-conditions/: +1 / -1 lines
- BluSky Trading Company (firm_sub) https://bluskytrading.com/privacy-policy/: +1 / -1 lines
- BluSky Trading Company (firm_sub) https://bluskytrading.com/cookie-policy/: +1 / -1 lines
- Funded Futures Network (firm_sub) https://fundedfuturesnetwork.com/payouts: +56 / -56 lines
- Traders Launch (firm_sub) https://traderslaunch.com/results: +1 / -1 lines
- Traders Launch (firm_sub) https://traderslaunch.com/crypto/rules: +1 / -1 lines
- Traders Launch (firm_sub) https://traderslaunch.com/terms: +1 / -1 lines
- Topstep (firm_sub) https://help.topstep.com/en/articles/8284204-what-is-the-maximum-loss-limit: +1 / -1 lines
- Topstep (firm_sub) https://help.topstep.com/en/articles/10296582-prohibited-conduct: +1 / -1 lines

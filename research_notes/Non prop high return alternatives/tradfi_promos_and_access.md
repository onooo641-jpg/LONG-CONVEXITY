# Traditional-finance / fintech "someone else pays" offers and access-barrier arbitrages for a Malaysian resident (2025–2026)

Research date: 2026-11-23. Method: web search only. **Important limitation:** this sandbox could not open
ringgitplus.com or moomoo.com (DNS blocked, `getaddrinfo ENOTFOUND`), so figures from those sites come from
search-result extracts, not full-page reads. Every figure below is labelled:
**[official]** = bank/regulator/broker's own page or T&C; **[news]** = mainstream news report;
**[3rd-party]** = comparison/affiliate/review site or user-generated post; **[repo]** = measured earlier in this
repository (pre-registered test, reproducible); **[inference]** = my own arithmetic or judgement.
Currency: USD:MYR ≈ 3.97 is the fixed rate Moomoo MY used in its January 2026 promotion terms (no current spot rate
was checked), so USD 15,000–20,000/yr ≈ RM 60,000–80,000/yr, and the capital (USD 10–15K) ≈ RM 40,000–60,000.

## Objective: can any combination turn RM 45–70K into RM 60–80K/yr (>100%/yr) legally and repeatably? Which offers pay most per ringgit?

### Takeaway
No. Every offer found is either (a) a one-time, per-person, capped sign-up reward worth RM 200–2,000, (b) a ~4–6%
rate product, or (c) a risk-bearing yield (P2P ~9–10% net, IPO ballots with a wide, recently negative range). A
realistic all-in total for one person on RM 45–70K is roughly RM 5,000–25,000 in year 1 (≈ USD 1.3–6K, i.e. ~10–40%),
falling in later years once sign-up promos are used up; the upper end depends almost entirely on Bursa IPO ballots,
which already **failed** this repo's pre-registered test (#49). Nothing approaches 100%/yr.

### Cited Findings
- Policy rate context: Bank Negara held the OPR at 2.75% at its final 2026 MPC meeting (5 Nov 2026), the eighth hold in a row since the July 2025 cut from 3.00%; analysts expect a possible hike to 3.00% in Q1 2027 **[official/news]** — [BNM MPS 05112026](https://www.bnm.gov.my/-/monetary-policy-statement-05112026); [The Star](https://www.thestar.com.my/business/business-news/2026/11/05/bank-negara-keeps-opr-steady-at-275); [NST](https://www.nst.com.my/amp/business/corporate/2026/11/1571412/bank-negara-leaves-opr-unchanged-final-2026-mpc-meeting-watch)
- Best fixed-deposit promotions in November 2026: headline 3.90% (8 months) / 4.00% (12 months), RM 5,000 minimum, 4–30 Nov 2026 (bank name not legible in the extract); RHB 3.90% 12-month, RM 1,000 minimum, to 30 Nov; Public Bank eFD up to 3.75% (9 months), 2 Oct–30 Nov **[3rd-party, RinggitPlus updated 13 Nov 2026, via search extract]** — [RinggitPlus FD list](https://ringgitplus.com/en/blog/fixed-deposits/best-fixed-deposit-accounts-in-malaysia.html)
- Alliance Bank Privilege FD promotion up to 4.00% p.a., 1 Oct 2026–31 Mar 2027 **[3rd-party, Loanstreet updated 14 Oct]** — [Loanstreet](https://loanstreet.com.my/learning-centre/best-fixed-deposit); MBSB TD-i/TIA-i up to 3.85% **[3rd-party, date unclear]** — [RinggitPlus](https://ringgitplus.com/en/blog/bank-news/earn-up-to-3-85-p-a-with-mbsb-banks-latest-td-i-and-tia-i-campaign.html)
- The Association of Banks in Malaysia publishes a periodic FD-rate table (e.g. "FD Rates as at 15 November 2025") **[official]** — [ABM PDF](https://www.abm.org.my/wp-content/uploads/2025/11/FD-Rates-as-at-15-November-2025-1.pdf)
- EPF declared 6.15% for 2025 (both conventional and Shariah; 2024 was 6.30%), paid 1 Mar 2026 **[news]** — [Malay Mail](https://www.malaymail.com/news/malaysia/2026/02/28/epf-announces-615pc-dividend-for-both-conventional-shariah-savings-for-2025/210707); [The Star](https://www.thestar.com.my/news/nation/2026/02/28/epf-declares-615-dividend-for-conventional-savings-for-2025)
- ASB (Bumiputera unit trust) declared 5.75 sen/unit for FY2025 (5.20 sen dividend + 0.55 sen bonus), unchanged from 2024 **[news]** — [The Star](https://www.thestar.com.my/business/business-news/2025/12/19/amanah-saham-nasional-declares-575-senunit-dividend-for-asb-fund); [Business Today](https://www.businesstoday.com.my/2025/12/19/pnb-declares-5-75-asb-dividend-for-2025-payout-hits-record-rm10-4-billion/)
- ASM / ASM2 / ASM3 fixed-price funds (open to all Malaysians): 5.00%, redeemable at RM 1 — the best liquid MYR parking found; i-Saraan first-year return ~26% but tiny (RM 500/yr) and 90% locked **[repo #50]** — [docs/PREREG_LOOPHOLES_20261120.md](../../docs/PREREG_LOOPHOLES_20261120.md)
- Bursa IPO ballots: pre-registered value per RM applied = 0.40% per IPO (halves +1.69% / −0.76%), 37% of IPOs closed below issue → FAIL; post-hoc average applicant profit RM 266–311 per IPO (median RM 139–201) → RM 7.7K–17K/yr at 55 IPOs/yr, bootstrap 90% range RM 2K–31K **[repo #49]** — [docs/PREREG_LOOPHOLES_20261120.md](../../docs/PREREG_LOOPHOLES_20261120.md)
- P2P financing: Funding Societies headline yields ~13–14% reportedly net ~9–10% after defaults **[3rd-party, low reliability]** — [malaysia4u](https://malaysia4u.com/review/funding-societies)

### Inferences
- **Ranking by return per ringgit of own capital [inference]:**
  1. Broker sign-up rewards (e.g. Webull RM 200 of NVDA shares for RM 1,000 held 60 days ≈ 20% in two months) — highest
     percentage, but one per person per broker and RM 200–2,000 in absolute terms.
  2. i-Saraan 20% government match (RM 500/yr cap; i-Saraan Plus RM 600/yr for gig workers) — instant 20%, locked.
  3. PRS tax relief — the "return" equals Jx's marginal Malaysian tax rate on up to RM 3,000/yr; worth nothing if he has
     little Malaysian taxable income.
  4. Credit-card 0% balance transfer / instalment cash — needs no own capital; earns only the deposit rate (~4%) on the
     borrowed sum, one time per new card (≈ RM 1,200 on RM 30,000 for 12 months).
  5. Bursa IPO ballots — reusable capital, ~55–60 IPOs/yr; expected value small to modest and recently negative.
  6. P2P notes ~9–10% net (risk-bearing, not a subsidy); ASM ~5%; FD/digital-bank promos ~4%.
- **Realistic annual total for one person with RM 60K [inference]:** base parking (ASM/FD) RM 2.4–3K + one-time broker
  rewards RM 0.5–2K + one-time 0% card float RM 0.6–2.4K (1–2 new cards) + i-Saraan RM 0.5K (if eligible) + PRS tax
  saving RM 0–0.9K + cashback RM 0.6–2.4K (needs real spending, not capital) + IPO ballots RM −2K to +17K
  (wide) ≈ **RM 5K–25K in year 1**, dropping to roughly RM 4K–20K in later years. This is the same order as one
  Topstep slot ($4,097/yr ≈ RM 16K) only if the IPO ballot result lands at the top of its range, which recent data
  (second half negative, late-2026 weak listings) does not support.
- The "someone else pays" mechanism in Malaysia is mostly customer-acquisition spending by brokers, banks and digital
  banks; it is capped per person and one-off, so it does not compound or scale with capital — the opposite of what a
  >100%/yr target needs.

### Gaps
- No live USD/MYR spot rate was checked; conversions use the 3.97 rate in Moomoo's January 2026 terms.
- Exact per-person caps on FD and digital-bank campaign balances were not readable (RinggitPlus blocked).
- Jx's Malaysian taxable income (which sets the PRS/EPF tax-relief value) is unknown.

## Which current or recurring promotions pay the most per ringgit, how often can they be repeated, and what is the realistic annual total for one person?

### Takeaway
Brokers (Moomoo, Webull) paid the richest sign-up rewards in 2026 (RM 200–2,000+ headline per new user), but each is
once per person and most 2026 campaigns have already ended. Banks offer 0% balance-transfer and 0% instalment-cash
plans that can be parked in ~4% deposits, worth ~RM 1,000–1,200 per new card per year. Deposit and digital-bank
promos top out at ~4%. Cashback cards are capped at roughly RM 20–100 per card per month.

### Cited Findings
**Brokers (one per person, new users)**
- Moomoo MY: new-user welcome pack "worth up to RM 1,800+" for deposit tasks completed by 30 Jun 2026 (an earlier pack, "up to RM 2,000+", ended 19 Mar 2026); deposit-based free stock for users who had never deposited before 8 Jul 2026, based on cumulative net deposits (withdrawals reduce it); keeping ≥ RM 10,000 for 60 days unlocks 90-day commission-free cards for US and Bursa stocks; stock-transfer tiers from RM 50,000 pay NVIDIA shares; free shares valued at a fixed USD:MYR 3.97 (26 Jan 2026) **[official, Moomoo MY support pages, via search extract; the page-to-item mapping could not be verified because moomoo.com is blocked here]** — [Moomoo MY support topic9_545](https://www.moomoo.com/my/support/topic9_545); [topic9_565](https://www.moomoo.com/my/support/topic9_565); [topic9_594](https://www.moomoo.com/my/support/topic9_594)
- Moomoo's Malaysia launch promo included free Apple shares **[3rd-party]** — [RinggitPlus](https://ringgitplus.com/en/blog/investment/moomoo-goes-live-in-malaysia-with-exclusive-new-user-promos-including-free-apple-shares.html)
- Webull MY (March 2026): "up to 6% p.a. returns" (cash-management promo) and RM 200 of NVIDIA shares for new users depositing ≥ RM 1,000 and keeping it 60 days, ending 31 Mar 2026; one year of commission-free trading from activation **[news]** — [Free Malaysia Today, 26 Mar 2026](https://www.freemalaysiatoday.com/category/leisure/2026/03/26/webull-malaysia-offering-up-to-6-p-a-returns-and-free-nvidia-shares)
- Webull MY 31 Mar–31 Jul 2026: RM 300 as three RM 100 trading vouchers for a net RM 5,000 deposit held 60 days; reward attached via invite link **[3rd-party]** — [malaysia4u Webull review](https://malaysia4u.com/review/webull)
- Earlier Webull MY campaign: US$100 of welcome rewards **[3rd-party, older]** — [RinggitPlus](https://ringgitplus.com/en/blog/investment/webull-malaysia-offers-us100-worth-of-welcome-rewards-in-latest-campaign.html)

**Deposits / digital banks / e-wallets**
- Ryt Bank cut its base savings rate from 3% to 2.05% p.a.; a campaign rate of up to 4% p.a. was reported as extended to 1 Feb 2027 **[3rd-party/news via search extract; specific article not confirmed]** — [TechARP Ryt Bank tag page](https://www.techarp.com/tag/ryt-bank/?amp=1)
- Boost Bank basic savings ~2.50% (June 2026 comparison); GXBank savings revised to 2.00% p.a. from 1 Oct 2024; AEON Bank basic savings-i 0.25% with higher promotional "pots" **[3rd-party/news]** — [fintechnews.my comparison](https://fintechnews.my/59187/digital-banking-news-malaysia/digital-bank-malaysia-savings-interest-rate/); [SoyaCincau (GXBank 2024)](https://soyacincau.com/2024/09/08/gxbank-new-revised-daily-interest-rate-cashback-revision/); [iMoney "where 3%+ lives in 2026"](https://www.imoney.my/articles/?p=70938)
- Touch 'n Go GO+ (money-market fund inside the e-wallet): historical ~1.30–1.47% p.a., promotional +4% bonus in 2021; not PIDM-protected; no current 2026 rate found **[news, old]** — [SoyaCincau 2021](https://soyacincau.com/2021/03/29/touch-n-go-ewallet-go-plus-5-things-you-need-to-know/); [TNG T&C (updated 5 Jun 2026)](https://www.tngdigital.com.my/assets/images/user-tnc.pdf)

**Credit-card float (0% balance transfer / instalment cash)**
- RHB: 0% for 12 months, no processing fee, transfer RM 1,000–30,000, new RHB credit-card applicants only, campaign to 31 Dec 2026 **[3rd-party, RinggitPlus via search extract]** — [RinggitPlus balance-transfer list](https://ringgitplus.com/cards/credit-cards/balance-transfer)
- Maybank: 0% balance transfer for 12 months with no upfront fee ran 23 Jun 2025–31 Mar 2026 (approval by 15 Apr 2026, quota-limited) **[official T&C / 3rd-party]** — [Maybank BT T&C PDF](https://www.maybank2u.com.my/iwov-resources/pdf/personal/promotions/2025/bal-trans-tnc.pdf); [RinggitPlus](https://ringgitplus.com/en/blog/bank-news/maybank-0-balance-transfer-i-plan-with-no-upfront-fee.html). Maybank's balance-transfer page reportedly lists crediting to a current/savings account as an option **[official, via search extract, not read in full]** — [Maybank BT page](https://www.maybank2u.com.my/maybank2u/malaysia/en/personal/cards/features_services/balance-transfer.page?)
- Alliance Bank Visa Platinum: 0% for 6 months, no upfront fee; Hong Leong WISE: 0% up to 12 months with a 5% one-time upfront fee **[3rd-party]** — [iMoney](https://www.imoney.my/credit-card/balance-transfer?src=footer)
- Normal card finance charge 15–18% p.a. **[3rd-party]** — [RinggitPlus BT explainer](https://ringgitplus.com/en/blog/balance-transfer/everything-you-need-to-know-about-balance-transfer-plans.html)
- Maybank EzyCash/-i: standard upfront fee 3.88% or RM 100; fee waived for applications 1 Feb–31 Mar 2026; 0% only on the 6-month tenure (longer tenures 8.88% p.a.); repaid in equal monthly instalments **[official T&C]** — [Maybank EzyCash Feb-26 T&C](https://www.maybank2u.com.my/iwov-resources/pdf/personal/promotions/2026/ezycash-feb26-tnc.pdf)
- Standard Chartered Cash-On-Call Plus: one-time fee 2% or RM 25 (whichever higher) for RM 1,000–9,999; no such fee from RM 10,000 **[official, via search extract; interest rate not captured]** — [SC Cash-On-Call Plus](https://sc.com/my/credit-cards/cash-on-call-plus)

**Cashback cards (spend-based, not capital-based)**
- Typical caps: Affin Duo Visa 5% weekend spend, RM 50/month; AEON BiG Visa Gold 5% at AEON BiG on the 28th, RM 100/month cap; Public Bank Petron Visa Gold RM 50/month per tier; AmBank Cash Rebate Visa Platinum up to 8% with spend-dependent cap **[3rd-party]** — [RinggitPlus cashback](https://ringgitplus.com/cards/credit-cards/cashback); [CompareHero](https://www.comparehero.my/credit-card/cashback/); [Bright Side of News](https://brightsideofnews.com/fintech/best-cashback-credit-card-in-malaysia-2026/)

**Government incentives (recurring, capped)**
- i-Saraan: matching up to RM 500/yr (RM 5,000 lifetime) for self-employed; Budget 2026 added i-Saraan Plus for gig/ride-hailing workers, up to RM 600/yr (RM 6,000 lifetime) **[news]** — [Malay Mail Budget 2026](https://www.malaymail.com/news/malaysia/2025/10/11/budget-2026-simplified-what-malaysians-can-expect-in-tax-reliefs-cash-aids-and-other-benefits/194177); [Bernama](https://www.bernama.com/en/general/news.php?id=2477134)
- PRS tax relief: RM 3,000/yr (shared with deferred annuity), extended to YA 2026–2030 in Budget 2025; relief reduces taxable income, based on gross contribution incl. upfront charges **[news / 3rd-party]** — [The Star, Budget 2025 reliefs](https://www.thestar.com.my/news/nation/2024/10/19/changes-to-the-scope-of-existing-personal-tax-reliefs-under-budget-2025); [StashAway PRS guide](https://www.stashaway.my/r/guide-private-retirement-scheme-prs-malaysia)
- ASB financing (Bumiputera-only fund): Maybank ASB Financing-i RM 10K–200K at SBR + 1.50% = 4.25% effective (≥ RM 30K, 5–20 yr online) or 4.55% below RM 30K; SBR 2.75% since 11 Jul 2025 **[official]** — [Maybank ASB Financing-i](https://www.maybank2u.com.my/maybank2u/malaysia/en/personal/loans/investment/asb_financing_i.page). CIMB's ASB-secured financing example uses 4.4% p.a. with a 10.75% ceiling rate **[official]** — [CIMB](https://www.cimb.com.my/en/personal/day-to-day-banking/financing/personal-financing/term-financing-i-secured-by-asb-certificate.html)

**Other fixed-income / P2P**
- SC Annual Report 2025 (via Fintech News): P2P platforms raised RM 2.83bn in 2025 (+13% from RM 2.51bn), 33,913 campaigns; cumulative RM 11.32bn over 154,283 campaigns **[official via news]** — [fintechnews.my](https://fintechnews.my/58007/wealthtech-malaysia/sc-malaysia-annual-report-2025-fintech/)
- microLEAP reported a 0.40% default rate vs a "market average of 4.18%" (Q2 2025; methodology unstated) **[3rd-party press]** — [Newswav](https://newswav.com/article/microleap-drives-msme-financing-growth-with-139-yoy-increase-as-mycif-expan-A2507_pEmCam)
- P2P default-rate denominators are "ballooned by rollovers", flattering reported default rates **[3rd-party]** — [BIX Malaysia](https://www.bixmalaysia.com/learning-center/articles-tutorials/p2p-allure-with-a-catch)
- The Edge (23 Oct 2026): Funding Societies Malaysia "could see single largest default since its debut"; a motor-oil company raised RM 3.5M at 4.17% over four months with a disclosed default probability as high as 15.47% **[news]** — [The Edge](https://theedgemalaysia.com/article/tech-funding-societies-malaysia-could-see-single-largest-default-its-debut)
- Funding Societies reported ~2% annualised default and claims >10% returns (company claim, older); CGC covers 50% of outstanding repayment on certain products **[news / company]** — [The Edge 2024](https://theedgemalaysia.com/article/cover-story-p2p-financing-industry-growing)

### Inferences
- **Repeatability [inference]:** broker and card promos are "new customer only", so each is usable once per person per
  institution. Malaysia has perhaps 5–8 retail brokers with app promos and ~10 card issuers, so the one-off pool is
  roughly RM 2,000–6,000 in total over 1–2 years, then dries up. FD/digital-bank campaigns recur but pay only
  ~0.3–1.5 points above the board/ASM rate.
- **0% card float arithmetic [inference]:** RM 30,000 × 4.0% FD × 1 yr ≈ RM 1,200 gross (RHB-type, no fee); minus any
  card fees. HLB WISE's 5% upfront fee makes it negative. Maybank-type 6-month 0% EzyCash with a waived fee ≈ RM 30,000 ×
  3.8% × 0.5 ≈ RM 570, but instalments start immediately, so the average balance is about half (≈ RM 300). A normal
  balance transfer must pay off an existing balance on another card, so it only creates float if Jx already carries
  (or deliberately creates through ordinary spending) a balance elsewhere; crediting to a savings account, if still
  offered, removes this limit.
- **ASB financing [inference]:** 5.75% distribution − 4.25% financing ≈ 1.5%/yr on borrowed money, e.g. ≈ RM 3,000/yr on
  RM 200K, before insurance/fees and only for Bumiputera investors; distributions are not guaranteed.
- **P2P [inference]:** ~9–10% net is a credit-risk yield, not a subsidy; at RM 60K it is ~RM 5–6K/yr with tail risk of
  single large defaults (Oct 2026 Edge report).

### Gaps
- No currently active (late Nov 2026) Moomoo or Webull MY promotion could be confirmed; Tiger Brokers MY and
  Interactive Brokers MY promotions were not found at all.
- The UOB "0% instant cash" item in search results appears to be a Singapore page; Malaysian UOB terms were not found.
- The interest rate on SC Cash-On-Call Plus and whether proceeds go to a savings account were not captured.
- Per-person caps on digital-bank campaign balances (Ryt 4%, Boost jars, AEON pots) and current GO+ rate not found.
- The annual government service tax on credit cards and BNM credit-card eligibility/limit rules were not verified this
  session (see the legal section).

## Do MYR crypto prices on Malaysian SC-registered exchanges show persistent premiums/discounts vs global USD prices large enough to arbitrage after fees and transfer times? Is arbitrage permitted?

### Takeaway
No exploitable gap. This repo measured Luno trading +0.38% to +0.55% above Kraken × USD/MYR on BTC, ETH, SOL and XRP
alike, with one-tick spreads; the gap is the same for every coin, so it is the cost of moving money into/out of MYR,
and it is smaller than Luno's own taker fee plus a USD↔MYR conversion (~0.6%). No exchange terms on arbitrage were
found.

### Cited Findings
- Luno +0.38% to +0.55% above Kraken × USD/MYR, uniform across coins, one-tick spreads (professional market makers) → FAIL **[repo #51]** — [docs/PREREG_LOOPHOLES_20261120.md](../../docs/PREREG_LOOPHOLES_20261120.md); [docs/CANDIDATES.md](../../docs/CANDIDATES.md)
- SC's registered digital-asset exchanges in 2026 (secondary sources): HATA Digital, Luno Malaysia, MX Global, SINEGY DAX and Kinetic DAX; Tokenize appeared on a 2022 list but not on 2026 lists found **[3rd-party; the SC register page itself was not loaded]** — [fintechnews.my DAX list](https://fintechnews.my/regulated-crypto-exchanges-malaysia/); [SC register](https://www.sc.com.my/regulation/guidelines/recognizedmarkets/list-of-registered-digital-asset-exchanges); [The Star 2022](https://www.thestar.com.my/business/business-news/2022/12/01/malaysia039s-digital-assets-market-regulated-to-protect-investors-sc)
- SC revised its Guidelines on Recognized Markets for DAX in May 2026 (tighter operator rules, faster product approvals) **[official/news]** — [SC media release](https://www.sc.com.my/resources/media/media-release/sc-issues-revised-guidelines-on-recognized-markets-for-digital-asset-exchange); [The Star 20 May 2026](https://www.thestar.com.my/business/business-news/2026/05/20/sc-revises-guidelines-to--strengthen-malaysia039s-digital-asset-market)
- Luno MY fees (secondary, conflicting): FPX deposits free from RM 100 (RM 1 below); MYR withdrawal free or RM 0.10; exchange maker from 0.25% / taker from 0.50% (another source: taker 0.25–0.50%); Instant Buy/Sell ~2% **[3rd-party]** — [malaysia4u Luno review](https://malaysia4u.com/review/luno); [FXEmpire](https://www.fxempire.com/crypto/exchange/luno/review)
- Wise MYR→USD: RM 7.17 + 0.57% of the amount converted; a comparison site puts Wise's rate markup at ~0.05% vs mid-market, Xe +1.24%, WorldRemit +1.41% **[official / 3rd-party, updated 27 Jun 2026]** — [Wise pricing](https://wise.com/my/pricing/); [MoneyTransfers](https://moneytransfers.com/send-money/usa/malaysia)

### Inferences
- **Round-trip arithmetic [inference]:** sell on Luno at +0.45% premium − Luno taker 0.25–0.50% − USD↔MYR conversion to
  recycle the MYR (~0.6% via Wise) − network fees ≈ **−0.4% to −0.7% per cycle**. The premium is the price of the
  MYR rail, not a mispricing.
- Remittance/FX rails (Wise vs banks vs remitters) are a cost comparison, not an arbitrage: the cheapest rail is
  ~0.6%, and there is no published case of an MYR rail paying more than the mid-market rate.
- HATA, MX Global, SINEGY and Kinetic DAX were not measured; given one-tick spreads at Luno, a large persistent gap at
  smaller venues would most likely reflect thin liquidity rather than free money.

### Gaps
- No Luno/HATA/MX/SINEGY terms of service text on arbitrage, multiple-account or withdrawal limits was found.
- Public MYR order-book APIs for HATA, MX Global, SINEGY and Kinetic DAX were not confirmed (Luno's public ticker was
  used in this repo's #51 test).
- BNM foreign-exchange policy limits on residents moving MYR offshore (relevant to recycling the leg) were not
  verified this session.

## Bursa Malaysia IPO public balloting: historical oversubscription, first-day returns and expected value per application

### Takeaway
2025 had about 60 IPOs (RM 5.96bn raised); popular ACE Market deals were 12–54× oversubscribed and some more than doubled
on day one, but losers exist (SumiSaujana −25% on day one). This repo's pre-registered test on 19 IPOs (2024-05 to
2026-11) gave a mean value of only 0.40% per RM applied, with the recent half negative and 37% of IPOs closing below
issue → FAIL. Post-hoc, an average applicant made RM 266–311 per IPO (RM 7.7K–17K/yr at ~55 IPOs), with a very wide
range.

### Cited Findings
- 2025: 60 IPOs (vs 55 in 2024; PwC counts 59), RM 5.96bn raised (−20% vs RM 7.42bn in 2024); 11 Main Market IPOs **[news]** — [NST, Dec 2025](https://www.nst.com.my/amp/business/corporate/2025/12/1346105/malaysia-ipos-add-nearly-rm33bil-market-cap-2025-closes); [WargaBiz](https://ipv4.wargabiz.com.my/2025/12/22/despite-global-shocks-bursa-malaysia-delivers-60-ipos-in-2025/); [PwC ECM Watch 2025](https://www.pwc.com/sg/en/publications/assets/page/equity-capital-markets-watch-2025.pdf)
- THMY Holdings: public portion 35.57× oversubscribed; opened +158% over its 31-sen IPO price (Oct 2025); reports differ on the close (73.5 sen vs ~91 sen) **[news]** — [The Star](https://www.thestar.com.my/business/business-news/2025/10/13/thmy-ipo-oversubscribed-3557-times-ahead-of-ace-market-debut); [NST](https://www.nst.com.my/amp/business/corporate/2025/10/1300185/thmy-logs-years-biggest-ipo-premium-158pct)
- Insights Analytics public portion 53.6× oversubscribed **[news]** — [The Star](https://www.thestar.com.my/business/business-news/2025/10/15/insights-analytics-ipo-public-portion-oversubscribed-536-times); Express Powerr 13.55× **[news]** — [The Star](https://www.thestar.com.my/business/business-news/2025/09/10/express-powerr039s-ipo-oversubscribed-by-1355-times); Farmiera 16.69× **[news]** — [The Star](https://www.thestar.com.my/business/business-news/2025/11/03/farmiera-ipo-oversubscribed-by-1669-times); LAC Med (Main Market) 12.6× **[news]** — [The Star](https://www.thestar.com.my/business/business-news/2025/12/01/lac-med039s-main-market-ipo-126-times-oversubscribed); One Gasmaster 25.24× (Jan 2026) **[news]** — [The Star](https://www.thestar.com.my/business/business-news/2026/01/20/one-gasmaster-ipo-oversubscribed-2524-times-ahead-of-ace-market-debut)
- First-day results: Foodie Media +18.3% **[news]** — [The Star](https://www.thestar.com.my/business/business-news/2025/11/28/foodie-media-makes-strong-ace-market-debut-at-183-above-ipo-price); Aquawalk +22% **[news]** — [The Star](https://www.thestar.com.my/business/business-news/2025/11/20/aquawalk-ends-maiden-trading-day-22-higher); SumiSaujana −25% on day one **[news]** — [NST "IPO market rides highs and lows"](https://www.nst.com.my/amp/business/corporate/2025/10/1302682/ipo-market-rides-highs-and-lows)
- A user-generated Moomoo column: average first-day gain 37.06% for the 14 stocks listed since July 2025, 11 of 14 up **[3rd-party, user-generated]** — [Moomoo community](https://www.moomoo.com/community/feed/193-day-one-surge-bursa-ipo-frenzy-rolls-on-115462463553542)
- Deloitte: Malaysia led Southeast Asia in IPO performance in 1H25 **[news]** — [The Star](https://www.thestar.com.my/business/business-news/2025/07/11/deloitte-malaysia-leads-southeast-asia-in-ipo-performance-for-1h25); Bursa targets RM 28bn of IPOs in 2026 **[news]** — [The Star, 30 Jan 2026](https://www.thestar.com.my/business/business-news/2026/01/30/bursa-aims-for-rm28bil-worth-of-ipos-this-year)
- Repo test (19 IPOs, 2024-05..2026-11, hand-collected): first-day mean +45.8%, median +28.0%, 37% closed below issue; value per RM applied r/(1+X) mean 0.40% (halves +1.69% / −0.76%) → FAIL; RM 10,000 pro-rata ≈ RM 40 per IPO; post-hoc mean RM 266–311 (median RM 139–201) per application → RM 7.7K–17K/yr, bootstrap 90% RM 2K–31K; average applicant applies ~RM 31–35K; one application per person per IPO; losers had low oversubscription (3.6×, 5.9×, 8.1×) but X is only published after applications close; 4 of the last 7 in late 2026 closed at or below issue **[repo #49]** — [docs/PREREG_LOOPHOLES_20261120.md](../../docs/PREREG_LOOPHOLES_20261120.md); run output `docs/jx_runs/ipo_test_20261120.txt`

### Inferences
- **Expected value [inference]:** the only defensible number is the pre-registered 0.40% per RM applied per IPO
  (≈ RM 240 per IPO on RM 60K applied pro-rata, if allocation were pro-rata, which it is not: Malaysian ballots favour
  small applications). The post-hoc RM 7.7K–17K/yr (≈ USD 1.9–4.3K) is the most valuable recurring item in this whole
  note, but it is (a) not pre-registered, (b) negative in the recent half, and (c) based on 19 IPOs. Treat it as a
  candidate for a fresh pre-registered forward test, not as an income estimate.
- Capital is locked only from application to refund (~1–3 weeks), so RM 45–70K can back most of ~55–60 IPOs/yr; the
  binding limit is one application per person per IPO, not capital.

### Gaps
- No official full-year 2025 average first-day return or oversubscription series (Bursa's IPO pages block automated
  access from this workspace and from GitHub, per `docs/HANDOFF_NONPROP.md`).
- Exact Bursa balloting/allocation rule (how lots are distributed by application size) was not found.

## Are there structural "free option" retail products (capital-protected notes, equity-linked deposits) with asymmetric payoffs?

### Takeaway
None found. Malaysian retail structured products seen (dual-currency investments, structured investments) are not
principal-protected, not PIDM-covered, carry the issuing bank's credit risk, and DCIs are effectively a sold currency
option (yield in exchange for conversion risk) — the opposite of a free option. Bank gold accounts carry a ~3.8%
buy/sell spread, so no gold-vs-spot arbitrage.

### Cited Findings
- CIMB DCI is NOT protected by PIDM; investor takes the bank's credit risk; at maturity the bank may repay in the alternate currency at the pre-agreed rate **[official]** — [CIMB DCI](https://cimb.com.my/en/personal/wealth-management/investments/investment-products/dual-currency-investment.html)
- Alliance Bank DCI is "non-principal-protected", with possible loss of principal **[official]** — [Alliance Bank DCI](https://www.alliancebank.com.my/personal/Investment/Wealth-Management/Dual-Currency-Investment); Hong Leong DCI minimum RM 50,000, not covered by the CMSA s.152 compensation fund **[official]** — [HLB DCI](https://www.hlb.com.my/en/personal-banking/investments/structured-investment/dual-currency-investments.html)
- CIMB issued a notice (8 Oct 2026) changing documentation for several structured products incl. DCI (contents not retrieved) **[official]** — [CIMB notice](https://www.cimb.com.my/en/personal/important-notices/2026/notice-of-changes-to-the-product-documentation-governing-structured-product.html)
- Maybank Gold Investment Account, 13 Feb 2026: sell RM 633.28/g, buy back RM 609.29/g (≈3.8% spread, my calculation from the quoted prices) **[official via search extract]** — [Maybank gold & silver rates](https://www.maybank2u.com.my/maybank2u/malaysia/en/personal/rates/gold_and_silver.page); Public Bank GIA, 20 May 2026: sell RM 584.97/g, buy RM 562.52/g (≈3.8%) **[official]** — [Public Bank GIA rates](https://www.pbebank.com/en/rates-charges/gold-investment-account/)
- Conflict: Maybank Islamic MIGA-i is described as having a narrower spread, yet its quoted sell/buy for ≥100 g (RM 653.07 / RM 612.18) implies ~6.3%; a Wise guide quotes a ~9% Maybank spread (undated) **[official / 3rd-party]** — [Maybank MIGA-i](https://www.maybank2u.com.my/maybank2u/malaysia/en/personal/wealth/gold_silver/maybank-islamic-gold-account-i.page?); [Wise gold guide](https://wise.com/my/blog/how-to-invest-in-gold-malaysia)

### Inferences
- A product only gives a "free option" if the issuer under-prices the option it sells to the customer; DCIs do the
  reverse (customer sells the option). No equity-linked FD with guaranteed principal and uncapped upside was found
  in 2025–2026 retail offerings [inference].
- Gold accounts: a ~4% round trip means the account only pays if gold moves >4%; it is a gold position, not an
  arbitrage [inference].

### Gaps
- Current Malaysian capital-protected structured notes (if any are offered to retail in 2026) and their participation
  rates were not found.
- Live gold-account prices vs spot XAU/MYR were not compared (BNM Kijang Emas/spot data not fetched).

## Legal / regulatory constraints and terms-of-service limits

### Takeaway
All items above are legal for a Malaysian resident, but every subsidy is limited to one person, often "new customer
only", and capped (broker first-deposit rewards, RHB new cardholders, RM 30K BT cap, one IPO application per person,
i-Saraan RM 500/yr, PRS RM 3K relief). Crypto must stay on SC-registered DAXs to stay inside Malaysian rules; ASB and
its financing are restricted to Bumiputera investors. Scaling by using other people's identities is excluded by the
brief and by the terms.

### Cited Findings
- Moomoo deposit-based free stock limited to users who had never deposited before 8 Jul 2026; rewards based on cumulative net deposits **[official via search extract]** — [Moomoo MY support](https://www.moomoo.com/my/support/topic9_545)
- RHB 0% BT limited to new RHB card applicants, RM 1,000–30,000 **[3rd-party]** — [RinggitPlus](https://ringgitplus.com/cards/credit-cards/balance-transfer); Maybank 0% BT "subject to available quota" **[official T&C]** — [Maybank T&C](https://www.maybank2u.com.my/iwov-resources/pdf/personal/promotions/2025/bal-trans-tnc.pdf)
- One application per person per IPO **[repo]** — [docs/PREREG_LOOPHOLES_20261120.md](../../docs/PREREG_LOOPHOLES_20261120.md)
- i-Saraan RM 500/yr (RM 5,000 lifetime); i-Saraan Plus RM 600/yr (RM 6,000 lifetime) **[news]** — [Malay Mail](https://www.malaymail.com/news/malaysia/2025/10/11/budget-2026-simplified-what-malaysians-can-expect-in-tax-reliefs-cash-aids-and-other-benefits/194177)
- SC registers five DAX operators; May 2026 revised DAX guidelines **[official/3rd-party]** — [SC media release](https://www.sc.com.my/resources/media/media-release/sc-issues-revised-guidelines-on-recognized-markets-for-digital-asset-exchange); [fintechnews.my](https://fintechnews.my/regulated-crypto-exchanges-malaysia/)
- SC requires P2P platforms to disclose default information, methodology and statistics **[3rd-party]** — [BIX Malaysia](https://www.bixmalaysia.com/learning-center/articles-tutorials/p2p-allure-with-a-catch)
- GO+ balances are neither e-money, deposits, capital-guaranteed nor PIDM-protected **[news]** — [SoyaCincau](https://soyacincau.com/2021/03/29/touch-n-go-ewallet-go-plus-5-things-you-need-to-know/)

### Inferences
- The binding constraint is "one person", not legality: because each subsidy is per identity and capped, the total
  does not scale with capital — the structural reason no stack reaches 100%/yr on RM 45–70K [inference].
- Any further quantitative check (e.g. a forward IPO-ballot test) must be pre-registered per this repo's CLAUDE.md
  before running [inference/repo rule].

### Gaps (not verified this session; from general knowledge, so not relied on above)
- BNM credit-card rules (minimum income, number of issuers and credit-limit multiples for lower incomes).
- SC retail-investor caps on ECF/P2P investment per issuer and per year.
- BNM foreign-exchange policy on resident individuals' offshore investment.
- EPF voluntary self-contribution annual limit and the EPF/PRS tax-relief interaction.
- Whether any DAX's terms prohibit cross-exchange arbitrage or rapid in/out flows.

## Free public data to measure each item

### Takeaway
Rates and promo terms are measurable from official pages (BNM, ABM, bank rate pages, broker T&Cs) plus aggregators;
crypto via Luno's public API (already used here); IPO stats only via news because Bursa blocks automated access;
P2P only via SC annual reports and platform self-disclosures.

### Cited Findings
- OPR decisions: BNM monetary policy statements **[official]** — [BNM MPS](https://www.bnm.gov.my/-/monetary-policy-statement-05112026)
- FD board rates by bank (periodic PDF tables) **[official, ABM]** — [ABM FD rates](https://www.abm.org.my/wp-content/uploads/2025/11/FD-Rates-as-at-15-November-2025-1.pdf); FD promos aggregated (third-party) — [RinggitPlus](https://ringgitplus.com/en/blog/fixed-deposits/best-fixed-deposit-accounts-in-malaysia.html); [StashAway FD table](https://www.stashaway.my/r/malaysia-fixed-deposit-rates)
- Gold account prices: [Maybank rates page](https://www.maybank2u.com.my/maybank2u/malaysia/en/personal/rates/gold_and_silver.page); [Public Bank GIA](https://www.pbebank.com/en/rates-charges/gold-investment-account/) **[official]**
- DAX register and P2P/ECF statistics: [SC DAX list](https://www.sc.com.my/regulation/guidelines/recognizedmarkets/list-of-registered-digital-asset-exchanges); [SC Annual Report 2024 ECF/P2P chapter](https://www.sc.com.my/annual-report-2024/strengthening-the-sustainability-and-competitiveness-of-the-capital-market/ecf-and-p2p-financing-fuelling-msme-growth-in-advancing-ekonomi-madani) **[official]**
- MYR crypto prices: Luno public ticker vs Kraken × USD/MYR, as in repo #51 **[repo]** — [docs/PREREG_LOOPHOLES_20261120.md](../../docs/PREREG_LOOPHOLES_20261120.md)
- IPO oversubscription/first-day data: news reports (The Star, NST, Bernama), hand-collected in `data/public/ipo_sample_20261120.csv` **[repo]** — [docs/PREREG_LOOPHOLES_20261120.md](../../docs/PREREG_LOOPHOLES_20261120.md)
- FX rail costs: [Wise pricing](https://wise.com/my/pricing/) **[official]**
- Dividends: EPF and ASNB announcements (news) — [Malay Mail EPF](https://www.malaymail.com/news/malaysia/2026/02/28/epf-announces-615pc-dividend-for-both-conventional-shariah-savings-for-2025/210707); [The Star ASB](https://www.thestar.com.my/business/business-news/2025/12/19/amanah-saham-nasional-declares-575-senunit-dividend-for-asb-fund)

### Inferences
- The only items worth further data work are (1) IPO ballots (a forward, pre-registered test logging every 2027 IPO's
  oversubscription and first-day close from news) and (2) a one-off list of currently open broker/card sign-up offers
  checked on the issuers' own pages; everything else is a known ~4–6% rate [inference].

### Gaps
- ringgitplus.com and moomoo.com were unreachable from this sandbox; they need to be allowed in network settings (or
  fetched via the GitHub Actions route) to read full promo tables and T&Cs.
- BNM's open data API and Kijang Emas gold prices were not checked this session.
- Bursa's own IPO statistics pages block automated access (per `docs/HANDOFF_NONPROP.md`).

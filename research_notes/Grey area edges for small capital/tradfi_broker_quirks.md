# TradFi and retail-broker structural "grey-area" edges for a Malaysia resident with USD 10–15K (2025–2026)

Researched 2026-11-28. Web budget: about 20 searches and fetches. sifma.org, zhuanlan.zhihu.com and newmoonspecialsituations.substack.com
were blocked by the sandbox network (DNS fail), so the SIFMA letter and two deal write-ups are cited only through search-result
summaries. Repo-internal evidence (this repo's own tests) is cited with relative paths and counts as **verified** (reproducible
command and raw output in the repo). Everything else is labelled: official/primary (SEC filings, HKEX/BNM/LHDN, law-firm and Big-4
summaries of the rules), third-party (news), or anecdotal (blogs, newsletters, forum posts).

Benchmark to beat (from the brief and CLAUDE.md): Topstep recycling, about USD 18K/yr on about USD 14K at risk (old closed-P&L
figure; corrected realtime-MLL path is USD 3,689/yr real net per CLAUDE.md).

## Q1. Mechanism, why some see it as unethical, within written terms, legal in Malaysia, who pays

### Takeaway
Most of these edges are within written terms and legal for a Malaysian resident (BNM lets residents without domestic ringgit borrowing
invest any amount abroad). Who pays is usually an issuer or a structure (IPO underpricing, tender premiums, round-up shares, DRP
discounts, broker marketing budgets). The "unethical" label mostly comes from incumbents (brokers, fund managers, SIFMA) whose costs rise.
CFD latency arbitrage and swap-free abuse are the exception: broker terms ban them and void the profits, so they are excluded.

### Cited Findings

**Malaysian legal and FX baseline (official)**
- A resident without domestic ringgit borrowing (DRB) "is free to invest any amount in foreign currency (FC) assets onshore and abroad." — [BNM FEP: investing in FC assets](https://www.bnm.gov.my/fep/policies/rules-by-residency/resident/investing-in-fca)
- Residents with DRB (for example a housing loan) are capped at RM1 million per calendar year of ringgit converted into foreign-currency assets. Above that, BNM approval is needed, and financial institutions must see it before processing. The cap is aggregated across the person's sole proprietorship and partnerships. — [BNM consolidated FEP notices, Oct 2025](https://www.bnm.gov.my/documents/20124/60360/Consolidated+Foreign+Exchange+Policy+Notices_Oct+2025.pdf); [BNM statement](https://www.bnm.gov.my/-/eapn062026); the limit resets each 1 January per [HSBC MY FAQ (older, 2016-era)](https://sp.hsbc.com.my/liquid/6399.html)
- Foreign-sourced dividends received in Malaysia by individuals (not through a partnership business) are tax-exempt from 1 Jan 2022 to 31 Dec 2036 (Budget 2026 edition). — [PwC Tax in Motion Budget 2026](https://www.pwc.com/my/en/assets/publications/tax-in-motion/2025/pwc-tax-in-motion-budget2026-edition.pdf); [RSM Budget 2026 highlights](https://www.rsm.global/malaysia/sites/default/files/media/05%20Tax/Newsletter/PDF/Budget%202026%20Highlights.pdf). A separate 2026 exemption order, for dividends received through a partnership business, runs only to 31 Dec 2030; it was gazetted 22 Oct 2026. — [KPMG MY Nov 2026](https://assets.kpmg.com/content/dam/kpmgsites/my/pdf/2026/11/monthly-tax-developments-nov-2026.pdf.coredownload.inline.pdf); [Orbitax](https://orbitax.com/news/country/article/Malaysia-Extends-and-Expands-E-63400)
- LHDN guidance on income received from abroad (June 2024 amendment) is the primary text. — [LHDN guidelines](https://www.hasil.gov.my/wp-content/uploads/20240620-guidelines-tax-treatment-in-relation-to-income-received-from-abroad-amendment-june-2024.pdf)

**A. Hong Kong IPO subscriptions (one-lot, margin)**
- Mechanism: the public tranche is balloted by tier. Pool A covers applications up to HK$5M and Pool B covers larger ones; each is balloted separately, so a one-lot ("red shoe" / 一手) application gets a lottery-style allocation. — [bayase.com explainer](https://bayase.com/post/hong-kong-ipo-retail-allocation-group-a-b/); [Sohu 2025 guide](https://www.sohu.com/a/927602618_121478176) (anecdotal)
- 2025 rule change (effective 4 Aug 2025): at least 40% of offer shares must go to the bookbuilding placing tranche. Issuers pick Mechanism A (a small initial public allocation plus a tiered clawback) or Mechanism B (a fixed 10% minimum public allocation, no clawback). Sources disagree on the Mechanism A tiers; check the HKEX text. — [Charltons](https://www.charltonslaw.com/hkex-listing-rule-changes-effective-4-august-2025-further-consultation-on-ongoing-public-float/); [Morgan Lewis](https://www.morganlewis.com/pubs/2025/08/hkex-issues-conclusions-on-optimizing-ipo-price-discovery-and-open-market-requirements); [Norton Rose Fulbright](https://www.nortonrosefulbright.com/-/media/files/client-alert--ipo-price-discovery-and-open-market-20250922-and-30-exe-typesetted.pdf?revision=adc5cb6c-2391-4df9-ac54-36c9b3f2bc67&revision=5250636106307387904)
- After the reform, most new IPOs chose the fixed 10% Mechanism B, the "red shoe" one-lot priority mostly lapsed, and one-lot success rates fell mostly to single digits. — [Sohu 2025 guide](https://www.sohu.com/a/927602618_121478176); a Zhihu analysis of 114 IPOs from 2025 (zhuanlan.zhihu.com/p/2013566794770694726, blocked here; summary via search) (anecdotal)
- Critics say the new rules shift allocation to institutions: "bad news for both retail investors and small brokers" (broker association chair). — [SCMP](https://www.scmp.com/business/markets/article/3321247/hong-kong-ipo-allocation-rules-shift-focus-institutions-limit-retail-access)
- First IPO under the new rules (Guangzhou Innogen): public tranche 5,342x oversubscribed; only 18,279 of 256,072 applications got shares (7.1%). — [China Daily HK](https://www.chinadailyhk.com/hk/article/617926)
- Who pays: the issuer and its selling shareholders, through underpricing. Grey part: IPO margin loans of up to 100–200x the deposit inflate demand. Mixue drew about HK$1.84 trillion in retail margin. In March 2025 the SFC brought back a minimum 10% deposit on IPO margin loans. — [The Standard: Mixue margin](https://www.thestandard.com.hk/finance/article/70503/Retail-investors-pump-record-184tn-into-IPO); [The Standard: margin cap revived](https://thestandard.com.hk/section-news/section/11/271136/Cap-on-IPO-margin-loans-revived-to-ease-demand). A 2026 article says current SFC guidance allows only 10x margin on new-share subscriptions. — [yolkinsight.hk](https://yolkinsight.hk/ipo-allotment/) (anecdotal)
- Legality: no Malaysian rule against it found. Broker access is the binding constraint. — repo desk note [docs/IDEAS_UNCHARTED_20261125.md](../../docs/IDEAS_UNCHARTED_20261125.md) (U21: "IPO access unverified" for IBKR (needs IBHK), moomoo, M+ and Webull MY)

**B. Bursa Malaysia IPO balloting**
- Mechanism: the public portion is balloted, with a separate Bumiputera tranche. In 2025 Bursa had 60 IPOs raising RM5.96bn. — [WargaBiz](https://wargabiz.com.my/2025/12/22/despite-global-shocks-bursa-malaysia-delivers-60-ipos-in-2025/)
- Example debuts, which are mixed:
  - Foodie Media: retail 24.6x oversubscribed, opened +18.3%.
  - Saliran Group: closed −22.2% on debut (13 Mar 2025).
  - BMS Holdings: public 1.4x, Bumiputera tranche 0.19x.
  - PSP Energy: public 5.87x (Dec 2025).
  - Impact Capital (24 Nov 2026): public 139.69x, opened at 32 sen against a 22 sen IPO price, then fell to 24.5 sen by 11:05.
  — [The Star PSP](https://www.thestar.com.my/business/business-news/2025/11/25/psp-energy039s-ipo-oversubscribed-by-587-times); [The Edge IPO watch](https://theedgemalaysia.com/node/785350); [rates.my Impact Capital](https://rates.my/insights/impact-capital-ipo); [scanx Impact Capital](https://scanx.trade/stock-market-news/ipo/impact-capital-shares-open-45-45-above-ipo-price-ace-market-debut/57059561)
- RichTech Digital: 245.42x oversubscribed. — [minichart](https://www.minichart.com.sg/2025/02/09/richtech-digital-berhads-ipo-sees-phenomenal-245-42x-oversubscription-a-testament-to-malaysias-booming-digital-payment-sector/) (anecdotal)

**C. US IPO access via retail brokers (Moomoo, Webull, Tiger)**
- Moomoo says every Bullish subscriber received shares, and that the BitGo (Jan 2026) and Figure (Feb 2026) IPOs reached all requesters, with moomoo taking just under 10% of BitGo. A user reply says they asked for 500 BitGo shares and got 10, so "100%" means at least one share per requester, not a full fill. — [moomoo Bullish](https://www.moomoo.com/us/newsroom/bullish-ipo-subscription); [moomoo community BitGo](https://www.moomoo.com/community/feed/bitgo-surges-36-1-on-debut-moomoo-achieves-100-allocation-115943809548294); [Nasdaq PR Figure](https://www.nasdaq.com/press-release/moomoo-serves-first-brokerage-platform-retail-access-figure-technology-solutions-incs) (broker PR = interested party)
- Bullish: priced US$37, opened at $90, closed day one at $68. BitGo: $18 offer, $24.50 intraday high (+36.1%). — [Webull news](https://www.webull.com/news/13476156341900288); [moomoo community](https://www.moomoo.com/community/feed/bitgo-surges-36-1-on-debut-moomoo-achieves-100-allocation-115943809548294)
- These are moomoo **US** pages. Whether moomoo MY / Webull MY customers can join US IPO books was not verified (see Gaps).

**D. Odd-lot tender offers (US)**
- Mechanism: in an issuer tender (often a modified Dutch auction), the issuer may first buy in full from holders of fewer than 100 shares who tender everything, then prorate the rest. Buy 99 shares below the expected purchase price and tender them. SEC Rule 13e-4 / Reg 14E: the offer must stay open at least 20 business days, holders keep withdrawal rights, and every holder gets the same price. — [dombey.capital guide](https://www.dombey.capital/blog/what-is-a-dutch-auction-tender-offer-the-complete-guide); [cummings.law](https://www.cummings.law/legal-requirements-for-conducting-a-dutch-auction-tender-offer/)
- Odd-lot priority is optional. Each Schedule TO / Offer to Purchase must be read: INVE's ~US$20M Dutch auction (2026) had none. — [toosmalltofund](https://toosmalltofund.substack.com/p/inves-20m-dutch-auction-6-to-the) (anecdotal)
- Examples:
  - WEX modified Dutch auction, up to US$750M at $148–$170, closed 25 Mar 2025; odd lots bought in full. — [dombey.capital](https://www.dombey.capital/blog/what-is-a-dutch-auction-tender-offer-the-complete-guide)
  - Expensify (EXFY): US$25M at $0.98–$1.20 with odd-lot priority, expiring 10 Jun 2026. — [smallstvalue](https://smallstvalue.com/blog/expensify-exfy-25m-dutch-auction-tender-offer-098-to-120)
  - MiniLuxe (MNLX): C$0.40–0.48 range with odd-lot priority. Billed as "up to 14.3%", it closed with **no shares purchased**. — newmoonspecialsituations substack (blocked; via search summary)
- Who pays: the issuer, by paying a premium to all tendering holders. Odd-lot priority exists to cut the issuer's shareholder-servicing costs.
- Why some call it aggressive: you become a holder only to harvest the premium, against the spirit of the "small legacy holder" carve-out. It is within the written offer terms.

**E. Reverse-split round-up**
- Mechanism: some issuers round any fractional post-split entitlement up to a whole share. Holding 1 share before a 1-for-N split gives you 1 share worth N times as much. Under DTC, participants request round-up shares; after about 4 business days DTC asks the transfer agent for the total and receives one deposit to Cede. Brokers must answer DTC's election requests on time for beneficial holders to benefit. — [American Rebel release (SEC exhibit, 2025)](https://www.sec.gov/Archives/edgar/data/1648087/000149315225021519/ex99-18.htm); [GlobeNewswire, American Rebel, Mar 2025](https://www.globenewswire.com/news-release/2025/03/27/3050642/0/en/AMERICAN-REBEL-UPDATE-1-FOR-25-REVERSE-STOCK-SPLIT-UPDATED-EFFECTIVE-DATE-IS-MARCH-31-2025-AS-PER-NASDAQ-PROCESSING-ROUND-LOT-100-SHARE-SHAREHOLDER-PROTECTION-FRACTIONAL-SHARE-ROUN.html) (primary)
- Industry pushback: in a 25 Mar 2025 letter to the exchanges, SIFMA describes "a novel trading practice designed to profit from the 'round-up'" and proposes cash in lieu instead of round-ups. — [SIFMA letter](https://www.sifma.org/wp-content/uploads/2025/03/SIFMA-Reverse-Split-and-Fractional-Shares-Letter-to-Exchanges-03.25.25.pdf) (primary; fetch blocked, read via search summary)
- 2025–2026 status, from filings:
  - Round-up is still used in some 2025–26 filings: Applied DNA (1:50, Mar 2025), Kaival Brands (2025), and Healthcare Triangle (2026: "round up at the participant level", no cash for fractions). — [Applied DNA exhibit](https://www.sec.gov/Archives/edgar/data/744452/000110465925022883/tm258867d1_ex99-1.htm); [Kaival DEF 14C](https://www.sec.gov/Archives/edgar/data/1762239/000173112225000319/e6391_def14c.htm); [Healthcare Triangle DEF 14A](https://www.sec.gov/Archives/edgar/data/1839285/000121390026005400/ea0273071-def14a_health.htm)
  - Many 2026 filings pay cash in lieu instead (Surf Air, Cardlytics). — [Surf Air PRE 14A](https://www.sec.gov/Archives/edgar/data/0001936224/000114036126023346/ny20063944x1_pre14a.htm); [Cardlytics DEF 14A](https://www.sec.gov/Archives/edgar/data/1666071/000162828026024446/cdlx-20260409.htm)
  - Some filings round up only holders who already own at least one whole post-split share, which kills the "1 share" trick.
  - Some leave it to DTC "at the participant level", so brokers may not pass the round-up through. Impact Biomedical (2026): "The 1,162% Paper Round-Up That May Vanish at Your Broker." — [newmoonspecialsituations](https://newmoonspecialsituations.substack.com/p/impact-biomedical-the-1162-paper) (title only; fetch blocked)
- The January 2025 Nasdaq rule change concerns bid-price compliance after reverse splits: a company that did a reverse split in the past year gets no new compliance period. It does not ban round-ups. — [Beyond Air DEF 14A](https://www.sec.gov/Archives/edgar/data/1641631/000164117225008699/formdef14a.htm)
- Who pays: other shareholders (dilution, usually tiny) and the issuer or broker who funds the extra shares. Why some call it unethical: SIFMA calls it a practice that exploits a shareholder-friendly rounding convention. It is legal and within issuer terms where round-up is written.

**F. Rights issues and scrip / DRP discounts (Malaysia)**
- Bursa DRP examples:
  - UOA Development: DRS price RM1.54, about 9.42% below the adjusted 5-day VWAP (2026).
  - KSL Holdings: up to 10% discount to the 5-day VWAP.
  - Yinson: DRP price fixed May 2025.
  — [EdgeProp UOA](https://www.edgeprop.my/content/1916370/uoa-development-fixes-drs-share-price-rm154-final-dividend); [EdgeProp KSL](https://api.edgeprop.my/content/1916740/ksl-offers-dividend-reinvestment-option-10-sen-final-payout); [The Star Yinson](https://www.thestar.com.my/business/business-news/2025/05/15/yinson-fixes-drp-share-price)
- Bursa Anywhere has offered e-DRP elections to individual CDS holders since 2022. — [The Star](https://www.thestar.com.my/business/business-news/2022/03/21/bursa-malaysia-launches-new-feature-on-bursa-anywhere)
- The discount applies only to the dividend amount reinvested. A 10 sen dividend at a 9.4% discount earns about 0.94 sen per share, and the shares go ex-dividend in the meantime. Who pays: non-electing shareholders, through dilution.

**G. Closed-end fund discount and tender events**
- Saba's model: buy closed-end funds at wide discounts to NAV (it cites a 30–40% discount for its BPRE stake), then press for tenders or liquidations near NAV. In the BlackRock fight, a tender at NAV would have given Saba about 14%. Settlements include a 42% tender at European Smaller Companies Trust and a full-exit tender at Schroder UK Mid Cap. About US$121bn of CEFs trade 15% or more below NAV. — [Risk.net](https://www.risk.net/node/7957003); [Hedgeweek](https://www.hedgeweek.com/saba-secures-full-exit-tender-for-schroder-uk-mid-cap-fund/); [WealthManagement](https://www.wealthmanagement.com/alternative-investments/wall-street-managers-pile-into-closed-end-funds-on-discounts); [Saba news](https://www.sabacapital.com/news)
- BlackRock calls arbitrageurs short-term opportunists, which is the source of the "unethical" framing. That view comes from a party to the dispute. — [BlackRock CEF proxy page](https://blackrock.com/us/individual/cef-proxy/truth)
- A small player can free-ride after a tender is announced. Pro-rated tenders (for example 42%) leave the rest exposed to the discount.

**H. Merger arbitrage on small deals**
- High merger spreads correlate with higher deal-cancellation rates, so wide spreads on small deals are partly pay for failure risk. — [Alpha Architect / Verdad summary, 2023](https://alphaarchitect.com/merger-spread/)
- An older US cash-deal study argues some opportunities suit small investors better than hedge funds; its figures were not visible. — [USI paper](https://wwwold.usi.edu/media/3651437/Merger-Arbitrage-Investment.pdf)

**I. Broker sign-up promotions (Malaysia)**
- Moomoo MY:
  - Apr–Jun 2026: free Apple fractional shares by deposit tier (RM1,000 and up) plus 180 days commission-free; ended 30 Jun 2026.
  - 31 Jul–31 Oct 2026: free NVIDIA shares for transfers of RM10,000 or more, plus 180–360 days zero commission; ended.
  - Feb–Apr 2026: up to 10 g of gold for stock transfers.
  - Older: "up to 360 days 0-commission and RM5,000 rewards".
  — [moomoo MY Apr–Jun 2026](https://www.moomoo.com/my/support/topic9_565); [moomoo MY Feb–Apr 2026](https://www.moomoo.com/my/support/topic9_553); [moomoo MY RM5,000](https://www.moomoo.com/my/support/topic9_205) (official T&Cs)
- Webull MY: RM200 of NVIDIA shares for new users who deposit RM1,000 and hold it 60 days (ended 31 Mar 2026). "Up to RM500" in free shares and coupons is also advertised. — [dividendmagic](https://dividendmagic.com.my/webull-malaysia-review-and-how-you-can-get-rm500-in-nvidia-shares/); [malaysia4u](https://malaysia4u.com/review/webull) (anecdotal or referral pages)
- Tiger MY, IBKR, Rakuten Trade: no current promotion found.
- Who pays: the broker's customer-acquisition budget. It is legitimate for one identity per broker. Multiple accounts are excluded.

**J. Retail CFD/FX pricing quirks (excluded)**
- Broker terms explicitly ban latency arbitrage and let the broker revoke trades:
  - FXCM clause 27 bans "gaming and/or use of abusive trading practices"; latency-reliant trades "may be revoked, without prior notice".
  - FXDD calls it "strictly forbidden… a material breach".
  - Fusion Markets has an FAQ on arbitrage.
  - UK case law: a FOREX.com UK dispute over voided profits, [EWHC 2133 (QB) 2017](https://caselaw.nationalarchives.gov.uk/ewhc/qb/2017/2133).
  — [Collyer Bristow](https://collyerbristow.com/?p=5752); [Forex Peace Army FXDD thread](https://www.forexpeacearmy.com/community/goto/post?id=250713); [Fusion Markets FAQ](https://fusionmarkets.freshdesk.com/support/solutions/articles/51000308112-do-you-allow-arbitrage-); [Deriv trading terms](https://deriv.com/terms-and-conditions/trading-terms)
- The UK Financial Ombudsman applies a "manifest error" test when a broker cancels trades over latency. — [FOS technical note](https://www.financial-ombudsman.org.uk/publications/technical_notes/spread-betting.htm)
- Focus Malaysia: "Arbitrage: a system abuse that doesn't pay off". — [Focus Malaysia](https://focusmalaysia.my/?p=203261)

**Exclusions (with reason)**
- Multiple accounts, family-member or nominee identities to multiply IPO ballots, odd-lot tenders, round-ups or sign-up bonuses: identity tricks. They break broker or one-per-person terms and, for IPO ballots, HK/Bursa multiple-application rules. Brief and CLAUDE.md exclude them.
- KYC or geoblock evasion (for example US-only promotions, Polymarket): excluded by CLAUDE.md.
- CFD latency arbitrage, stale-quote sniping, and swap-free (Islamic) account carry abuse: banned in broker terms, with profits voidable (sources above). No swap-free-specific clause was found in this search, but brokers' "abusive trading" clauses are generic.
- Buying a stock to push it through a round-up or tender, wash trades, spoofing: market manipulation.
- IPO "grey market" pre-listing trading in HK (Futu/Phillip dark pools): legal, but just a trading venue, not an edge. Not researched.

### Inferences
- The legal path for a no-loan Malaysian individual looks clear (BNM "any amount"). With a housing loan, USD 15K is far under the RM1M yearly cap. Foreign dividends are tax-exempt in Malaysia until 2036.
- The "unethical" critiques come from parties whose costs rise: SIFMA members (round-up processing), fund sponsors (CEF tenders), and HK brokers and institutions (retail IPO margin). Issuer-written terms are what count; all of A–I are within them when the specific offer documents allow it.

### Gaps
- US withholding on dividends for Malaysian residents: I believe there is no US–Malaysia income tax treaty, so the 30% default applies. No source was retrieved in this session; verify on IRS treaty tables or W-8BEN instructions.
- Whether a Malaysian resident can subscribe to HK IPOs through moomoo MY, Webull MY, Tiger or IBKR (IBHK entity), and US IPOs through moomoo MY: not verified. Needs broker help pages or an account login (Jx only).
- No Securities Commission Malaysia guidance found specifically on residents using foreign brokers (licensing applies to brokers, not investors). Not verified.
- Swap-free account abuse clauses were not found.

## Q2. Realistic annual profit for a small player, capacity and repeatability

### Takeaway
None of these is near USD 18K/yr on USD 14K; most are USD 0–2K/yr per identity. The repo's own test of HK one-lot IPO applications
(2024-01 to 2026-10, 301 IPOs) gives −US$277/yr with HK$100 fees and +US$1,092/yr with a zero-fee broker. Allocation odds are priced in.
Odd-lot tenders, round-ups and promotions are a few hundred to low thousands of USD a year, rationed by the 99-share and 1-share caps.

### Cited Findings
- **HK IPO, verified in this repo (#391, KILL):**
  - 317 IPOs parsed (AASTOCKS); 301 in the window with all fields.
  - Mean first-day return +35.6%, median +8.2%, 67% up.
  - Median lot value HK$3,932; median one-lot success rate 7%.
  - Rule A (one lot in every IPO, HK$100 fee): **−US$277/yr per identity**. By year: 2024 −$773, 2025 +$214, 2026 −$222.
  - Zero fee: **+US$1,092/yr**.
  - Hot IPOs (final oversubscription ≥ 100x, 199 of 301): +53% on day one, but a median one-lot success rate of 3%.
  - The other 102 IPOs averaged +0.7% on day one.
  - The best single IPO EV was DualityBio (Apr 2025): one-lot rate 80%, +116.7% on day one, about HK$8,732.
  - The per-year medians show the reform effect: 32% (2024) → 8% (2025) → 3% (2026).
  — [docs/PREREG_UNCHARTED_20261125.md](../../docs/PREREG_UNCHARTED_20261125.md); raw output [docs/jx_runs/uncharted_hkipo_20261125.txt](../../docs/jx_runs/uncharted_hkipo_20261125.txt); [docs/CANDIDATES.md](../../docs/CANDIDATES.md) row 391
- Third-party HK figures (consistent with the repo's):
  - First three quarters of 2025: 66.67% of IPOs rose on day one, average +37.63%; about 30% of up-days were +100% or more.
  - Another tally: 2025 average one-lot win rate 31.97%, average first-day +19.33%.
  - Long-run HK day-one average +38.1% (Ritter, Jan 2026), cited in the repo pre-registration.
  — [The Standard: Biren](https://www.thestandard.com.hk/finance/article/320338/Birens-Hong-Kong-IPO-retail-tranche-oversubscribed-nearly-1900-times); [Sohu](https://www.sohu.com/a/927602618_121478176) (anecdotal); [docs/PREREG_UNCHARTED_20261125.md](../../docs/PREREG_UNCHARTED_20261125.md)
- HK oversubscription extremes:
  - Mixue: about 5,319x.
  - Bloks: about 5,724x.
  - Golden Empire: more than 11,500x (single outlet, unverified).
  - Biren: about 1,900x.
  - Xizang Zhihui Mining: about 1,317x.
  — [The Standard: Biren](https://www.thestandard.com.hk/finance/article/320338/Birens-Hong-Kong-IPO-retail-tranche-oversubscribed-nearly-1900-times); [Longbridge](https://longbridge.com/en/news/270544744)
- HK capacity: 113 IPOs in 2025 and 118 in 2026 to date, per the repo AASTOCKS data. — [docs/jx_runs/uncharted_hkipo_20261125.txt](../../docs/jx_runs/uncharted_hkipo_20261125.txt)
- Margin applications scale pool size, not odds. Pro-rata within a tier means 10x margin buys about 10x the expected shares at a cost of 10x interest. IPO margin interest rates were not found (see Gaps).
- **Bursa IPO:** 60 IPOs in 2025, but no market-wide first-day average found. Debuts are mixed: some +18% to +45% opens, some −22% closes. Lots are RM-hundreds in size. — sources in Q1 B
- **Odd-lot tenders:**
  - Profit per event is (purchase price − buy price) × at most 99 shares, minus commissions. Commissions "can swamp the odd-lot return on 99 shares". — [helpyourfinances FDX experience](https://helpyourfinances.com/risk-behind-odd-lot-tender-offers-my-fdx-experience-explained/); [toosmalltofund](https://toosmalltofund.substack.com/p/inves-20m-dutch-auction-6-to-the) (anecdotal)
  - Example at WEX's range: buying at about $150 with a $170 top gives up to about $2K on 99 shares if it clears at the top. Real clearing prices are often at or near the bottom of the range. This is arithmetic, not evidence.
  - Prior repo estimate: "typical returns 5–10%/yr, not prop-like" for merger arb, CEF discounts and odd-lot tenders together. — [docs/AUDIT_ALL_AREAS_20261124.md](../../docs/AUDIT_ALL_AREAS_20261124.md)
- **Reverse-split round-up:**
  - Impact Biomedical's paper round-up return was 1,162%, but "may vanish at your broker". — [newmoon substack](https://newmoonspecialsituations.substack.com/p/impact-biomedical-the-1162-paper) (anecdotal; blocked)
  - Per event, profit is about (split ratio − 1) × the post-split price of one share, minus commission, often USD 5–200 per account. This is arithmetic on typical microcap splits and is not verified.
  - Event count per year: not found (see Gaps).
- **DRP:** about 9–10% of the dividend reinvested. On USD 15K with a 4% yield that is roughly USD 50–60/yr (arithmetic from the [UOA](https://www.edgeprop.my/content/1916370/uoa-development-fixes-drs-share-price-rm154-final-dividend) and [KSL](https://api.edgeprop.my/content/1916740/ksl-offers-dividend-reinvestment-option-10-sen-final-payout) discounts).
- **CEF tender:** about 14% per Saba-style event at full NAV tender, before proration. Proration (for example 42%) cuts the realised gain. — [Risk.net](https://www.risk.net/node/7957003)
- **Broker promotions:**
  - About RM200–500 (USD 45–110) per broker per campaign, plus commission-free periods and stock-transfer rewards (gold, NVDA) at the RM10K+ tiers.
  - Repeatable only through new brokers, since most rewards are for new customers. Some moomoo campaigns reward transfers for existing customers.
  — [moomoo MY](https://www.moomoo.com/my/support/topic9_565); [dividendmagic](https://dividendmagic.com.my/webull-malaysia-review-and-how-you-can-get-rm500-in-nvidia-shares/)

### Inferences
- Stacked optimistically per identity: HK IPO zero-fee (~US$1.1K), odd-lot tenders (~US$0.5–2K), round-ups (~US$0.2–1K if the broker passes them through), and promotions (~US$0.2–0.5K, one-off) come to roughly **US$2–4K/yr**. That is well below the US$18K benchmark and labour-heavy (reading every Schedule TO and 8-K).
- The edges are capped by identity, not capital, which is the defining feature. More capital does not help, and the cap cannot be lifted legitimately (multiple identities are excluded). That is why they cannot match prop recycling ROI in absolute dollars.
- CEF tender and merger arb scale with capital but return about 5–15% on capital. On USD 15K that is roughly USD 0.75–2K/yr, with deal-break tail risk.

### Gaps
- IPO margin interest rates at HK brokers (one-week financing) were not found.
- A Bursa IPO first-day average for 2023–2025 and per-tranche ballot success rates were not found.
- Reverse-split round-up events per year, and how often moomoo, IBKR or Tiger actually credit round-up shares (2025–26), were not found. Key data is behind the blocked substack.
- Count of US issuer tenders per year with odd-lot priority, and realised clearing versus range, were not found. The repo's #326 is parked on the EDGAR contact-email issue.
- No 2024–25 study isolating small-deal merger-arb returns was found. The [NYU Shanghai 2026 thesis](https://cdn.shanghai.nyu.edu/sites/default/files/xiya_wang_thesis_nyush_honors_2026.pdf) covers 2016–2024 deals, but its results were not retrieved.

## Q3. Capital, time, risks (allocation odds, financing, broker bans, rule changes)

### Takeaway
Capital is trivial for all of them (a few hundred to a few thousand USD per event). The constraints are rule changes and broker
handling, plus time spent reading filings. Each edge has already been squeezed:
- HK Aug 2025 reform: one-lot odds down to single digits.
- SFC 10% deposit rule (Mar 2025) and 10x margin guidance.
- SIFMA's 2025 push for cash in lieu, and the drift of many issuers to it.
- Optional odd-lot priority, with tenders that can fail (MiniLuxe).

### Cited Findings
- HK one-lot odds fell after the August 2025 reform (32% → 8% → 3% median by year in the repo data). Mechanism B (fixed 10%, no clawback) is the common choice. — [docs/jx_runs/uncharted_hkipo_20261125.txt](../../docs/jx_runs/uncharted_hkipo_20261125.txt); [Sohu](https://www.sohu.com/a/927602618_121478176)
- Margin: SFC minimum 10% deposit reinstated in March 2025. 2026 guidance said to limit IPO margin to 10x, with a Pool B threshold of at least HK$500K of own funds. — [The Standard](https://thestandard.com.hk/section-news/section/11/271136/Cap-on-IPO-margin-loans-revived-to-ease-demand); [yolkinsight](https://yolkinsight.hk/ipo-allotment/) (anecdotal)
- Broker margin-book figures understate final demand: one analysis multiplies margin cover by 2–3x to estimate final oversubscription, so odds cannot be judged well before applying. — [yolkinsight](https://yolkinsight.hk/ipo-allotment/) (anecdotal)
- Debut risk: Bullish closed day one at $68 after a $118 high, so selling timing matters. Bursa's Saliran closed −22% on debut and Impact Capital fell from 32 to 24.5 sen within hours. — [Webull news](https://www.webull.com/news/13476156341900288); [rates.my](https://rates.my/insights/impact-capital-ipo)
- Round-up risk:
  - SIFMA (Mar 2025) proposes cash in lieu.
  - Issuers increasingly pay cash (Surf Air, Cardlytics 2026) or round up only holders who own at least one whole post-split share.
  - "Determined by DTC at the participant level" wording lets brokers decline to pass on the round-up.
  — [SIFMA letter](https://www.sifma.org/wp-content/uploads/2025/03/SIFMA-Reverse-Split-and-Fractional-Shares-Letter-to-Exchanges-03.25.25.pdf); [Surf Air](https://www.sec.gov/Archives/edgar/data/0001936224/000114036126023346/ny20063944x1_pre14a.htm); [Cardlytics](https://www.sec.gov/Archives/edgar/data/1666071/000162828026024446/cdlx-20260409.htm)
- Underlying risk: reverse-split stocks are distressed microcaps, so the price often falls through the split window. The split date can also move (American Rebel changed its effective date to 31 Mar 2025 "per Nasdaq processing"). — [GlobeNewswire](https://www.globenewswire.com/news-release/2025/03/27/3050642/0/en/AMERICAN-REBEL-UPDATE-1-FOR-25-REVERSE-STOCK-SPLIT-UPDATED-EFFECTIVE-DATE-IS-MARCH-31-2025-AS-PER-NASDAQ-PROCESSING-ROUND-LOT-100-SHARE-SHAREHOLDER-PROTECTION-FRACTIONAL-SHARE-ROUN.html)
- Odd-lot risk: the clearing price may sit at the bottom of the range, the tender can lapse (MiniLuxe closed with no purchase), and some offers have no odd-lot priority (INVE). You hold the stock from purchase until payment, roughly 20+ business days. — [toosmalltofund](https://toosmalltofund.substack.com/p/inves-20m-dutch-auction-6-to-the); [cummings.law](https://www.cummings.law/legal-requirements-for-conducting-a-dutch-auction-tender-offer/)
- Merger-arb risk: wide spreads signal higher break risk. — [Alpha Architect](https://alphaarchitect.com/merger-spread/)
- CEF risk: proration (42% at European Smaller Companies) and standstills. BlackRock's settlement keeps Saba away from 50 funds until 2027, which removes catalysts. — [Risk.net](https://www.risk.net/node/7957003)
- CFD latency: profits revocable without notice; account closure. — [Collyer Bristow](https://collyerbristow.com/?p=5752)

### Inferences
- Time cost dominates. An odd-lot, round-up and tender watchlist needs daily EDGAR scanning (8-K, DEF 14A/14C, SC TO-I). That can be automated, but EDGAR requires a contact e-mail in the user agent, which is why repo #326 is parked and needs Jx's approval.
- Withholding is a hidden cost on dividend-type plays (assumed 30% US withholding, unverified). A dividend-capture or ADR approach for a Malaysian resident is worse than for treaty residents, so it was not pursued further.

### Gaps
- Moomoo MY / Webull MY corporate-action policy on fractional round-ups, and odd-lot tender elections through Malaysian-entity brokers (some brokers charge voluntary corporate-action fees), were not found.
- HK broker IPO handling fees for Malaysian clients were not found. The repo assumed HK$100; the result flips sign at zero fees.

## Q4. Free public data to backtest each

### Takeaway
Free data exists for every mechanism. HK IPO was already backtested in this repo from AASTOCKS tables. US odd-lot tenders and
reverse splits need SEC EDGAR full-text search or the daily index, and are blocked only by the EDGAR user-agent contact-email
requirement. Bursa IPO and DRP data are in Bursa announcements.

### Cited Findings
- HK IPO: the AASTOCKS listed-IPO table (fetched via GitHub Actions run 45600030401) has offer price, lot size, oversubscription, one-lot rate and first-day return from 2024-01. HKEXnews allotment-results announcements give per-tier odds (PDF). — [docs/PREREG_UNCHARTED_20261125.md](../../docs/PREREG_UNCHARTED_20261125.md)
- US odd-lot tenders: Schedule TO-I filings on EDGAR (Offer to Purchase states odd-lot priority, range and expiry; the final results come in an SC TO-I/A). Reg 14E / Rule 13e-4 set the timing. — [cummings.law](https://www.cummings.law/legal-requirements-for-conducting-a-dutch-auction-tender-offer/); repo #326 parked: [docs/PREREG_SWEEP3_20261122.md](../../docs/PREREG_SWEEP3_20261122.md)
- Reverse splits: EDGAR 8-K and proxy (PRE/DEF 14A, 14C) text contains "round up" or "cash in lieu" wording. Examples: [Healthcare Triangle](https://www.sec.gov/Archives/edgar/data/1839285/000121390026005400/ea0273071-def14a_health.htm), [Kaival](https://www.sec.gov/Archives/edgar/data/1762239/000173112225000278/e6379_pre-14c.htm), [Applied DNA](https://www.sec.gov/Archives/edgar/data/744452/000110465925022883/tm258867d1_ex99-1.htm). Nasdaq and NYSE daily corporate-action lists give effective dates (not fetched).
- Bursa IPO, DRP and rights: Bursa company announcements (prospectus, ballot results, DRP price-fixing). Examples: [The Star PSP](https://www.thestar.com.my/business/business-news/2025/11/25/psp-energy039s-ipo-oversubscribed-by-587-times), [EdgeProp UOA DRS](https://www.edgeprop.my/content/1916370/uoa-development-fixes-drs-share-price-rm154-final-dividend).
- CEF discounts: Saba press releases list positions and tender outcomes. — [Saba news](https://www.sabacapital.com/news)

### Inferences
- The cheapest next test is a Stage 1 on reverse-split round-ups. Use EDGAR full-text search for "rounded up to the nearest whole share" in 8-K filings from 2025-01 to 2026-10, then for each event compute (ratio − 1) × the post-split close minus a 1-share commission. A KILL-only threshold would be under US$1,000/yr. It needs the EDGAR contact e-mail decision first (Jx), or GitHub Actions with a generic contact. Per CLAUDE.md privacy rules, Jx decides that.
- Odd-lot tenders can share the same EDGAR pipeline (SC TO-I filings). Both are expected to land in the low thousands of USD a year at best.

### Gaps
- Whether the GitHub Actions fetch path can use a generic EDGAR contact without breaching the repo privacy rule: an open decision for Jx.
- No free source of broker-level round-up crediting outcomes; only anecdotal posts.

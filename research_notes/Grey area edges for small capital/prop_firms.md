# Prop-firm rule asymmetries and promotions a small, rule-abiding, automated player can use (2025–2026)

Scope note for the report writer. Researched 2026-11-28. **WebFetch could not reach any site from this sandbox** (DNS blocked: propfirmbriefing.com,
velotrade.com, hyrotrader.com all failed), so evidence comes from two places:
1. **Official firm pages, verbatim text**, rendered in November 2026 by the repo's own GitHub Actions job (`scripts/prop_verify_fetch.py`) and stored in
   `data/public/propverify/*.json` (last commit 2026-11-28). These are cited by their official URL and are marked **[official]**.
2. **Web-search summaries** (titles and URLs real; text summarised by the search tool, pages not opened). Marked **[search]**; most are affiliate or
   review sites, so treat them as third-party.
Repo facts already verified in earlier sessions (`docs/PROP_VERIFY_20261122.md`, `docs/NOTES_JX.md`) are marked **[repo]**.

## 1. Which firms allow bots, accept Malaysia residents, and have recycle-friendly rules?

### Takeaway
Among futures firms, the ones confirmed in their own writing to allow full automation and not to restrict Malaysia are Topstep (no VPS allowed), Lucid,
DayTraders and Funded Futures Network (FFN). DayTraders is the only one that says in writing that you may copy trades into accounts at other
firms. FundedNext Futures and The Trading Pit also allow EAs. MyFundedFutures, Alpha Futures, FuturesElite, Goat Funded Futures and Blue Guardian
Futures exclude Malaysia, and Top One Futures bans automation outright. On the CFD and crypto side, FTMO, The5ers, FXIFY, City Traders Imperium and
HyroTrader allow EAs or bots and do not list Malaysia, but most forbid running **someone else's** strategy. That clause is decisive for an account in
Jx's name running the friend's bot.

### Cited Findings
**Malaysia access (official restricted lists)**
- **Restricted: MyFundedFutures.** Malaysia is on its "Restricted Countries List" (updated 2026-10-14). [official] — [MFFU restricted-countries policy](https://help.myfundedfutures.com/en/articles/8229993-restricted-countries-policy)
- **Restricted: Alpha Futures.** Malaysia is listed under "countries with limitations" (2026-08-12). [official] — [Alpha Futures](https://help.alpha-futures.com/en/articles/9523389-countries-with-limitations)
- **Restricted: FuturesElite.** "FuturesElite does not provide Services to users residing in … Malaysia". [official] — [FuturesElite T&C](https://futureselite.com/terms-and-conditions)
- **Restricted: Goat Funded Futures.** Malaysia is on its restricted list. [official] — [GFF](https://help.goatfundedfutures.com/en/articles/14094470-which-countries-are-restricted)
- **Restricted: Blue Guardian.** Malaysia is on its list (2026-11-13). Earlier repo work recorded this as futures-only, with CFD allowed. [official] — [Blue Guardian](https://help.blueguardian.com/en/articles/18426607-who-can-sign-up-age-and-restricted-countries)
- **Partly restricted: AquaFunded.** Malaysia "can trade with restrictions (Instant Funding models only, max $50K funded per trader)". [official] — [AquaFunded](https://help.aquafunded.com/en/articles/9251052-are-there-any-countries-we-cannot-trade-from)
- **Payout method only: FundedNext.** Malaysia appears only on its card-payout restriction list, not the sign-up list. FundedNext says it operates partly from Malaysia (HQ Ajman, UAE; article dated 2026-09-30). [official] — [FundedNext withdrawals](https://help.fundednext.com/en/articles/8020084-how-can-i-withdraw-my-profits), [FundedNext location](https://helpfutures.fundednext.com/en/articles/17225702-where-is-fundednext-located-and-registered)
- **Not restricted: Lucid.** Its list includes Indonesia, Cambodia and Myanmar but not Malaysia. [official] — [Lucid restricted countries](https://support.lucidtrading.com/en/articles/11404636-restricted-countries)
- **Not restricted: The5ers.** Its "Forbidden Territories" list (Afghanistan … Yemen) does not include Malaysia. [official] — [The5ers](https://the5ers.com/)
- **Not restricted: Topstep, DayTraders, FTMO.** None lists Malaysia. [repo/official] — [Topstep](https://help.topstep.com/en/articles/8284116), [DayTraders](https://daytraders.com/help/articles/17704103-who-can-sign-up), [FTMO](https://ftmo.com/en/faq/who-can-join-ftmo/)
- **Not restricted: FFN.** Its country list excludes Cuba, Iran and others; Malaysia is not on it and is selectable at checkout. [official] — [FFN rules 12.1](https://app.fundedfuturesnetwork.com/nexus/rules/article-12-1-country-restrictions-and-product-list), [FFN checkout](https://fundedfuturesnetwork.com/checkout?plan=50SM&feed=cqg&coupon=NEXUS)
- **Not verified: Crypto Fund Trader and Breakout.** I found no official list naming Malaysia. Third-party trackers do not settle it. [search] — [TSB on CFT](https://traderssecondbrain.com/prop-firm/crypto-fund-trader/available-countries), [Breakout ineligible-countries article](https://intercom.help/breakoutprop/en/articles/10340733-which-countries-are-ineligible-for-breakout-services)
- **Restricted (third-party): CK Capital and FXIFY Futures.** Search summaries say both list Malaysia; FXIFY Futures calls it "prohibited". Funded Daily reportedly caps Malaysian traders at $50K. [search] — [CK Capital](https://intercom.help/ck-capital/en/articles/13586032-are-there-any-prohibited-countries), [FXIFY Futures](https://intercom.help/fxify-futures/en/articles/10235705-prohibited-country-and-restrictions), [Funded Daily](https://intercom.help/funded-daily/en/articles/14368157-are-there-restricted-countries)
- **Free filters exist.** Prop Firm Match publishes Malaysia-filtered lists, including EA-allowed challenges for futures and crypto. [search] — [PFM futures EA list, Malaysia](https://propfirmmatch.com/futures/prop-firm-lists/countries/malaysia/challenges/allow-ea-trading), [PFM crypto EA list, Malaysia](https://propfirmmatch.com/crypto/prop-firm-lists/countries/malaysia/challenges/allow-ea-trading)

**Automation policies (official wording)**
- **Topstep: allowed, own device only.** "Can I use automated trading strategies? Yes, with conditions… no exceptions are made for errant trades or malfunctions." Bots run through the TopstepX API (ProjectX, billed separately). "The use of VPS, VPNs, and remote servers is prohibited… Running automation on a VPS can result in account suspension." [official] — [Topstep Combine parameters](https://help.topstep.com/en/articles/8284197-trading-combine-parameters), [TopstepX API access](https://help.topstep.com/en/articles/11187768-topstepx-api-access)
- **Lucid: allowed.** "Automated trading systems and trade copiers are permitted… Traders are fully responsible for any software errors". HFT is banned (article 2026-08-26). Microscalping is flagged if more than 50% of profits come from trades held 5 seconds or less. [official] — [Lucid other activities](https://support.lucidtrading.com/en/articles/11404728-other-trading-activities), [Lucid HFT](https://support.lucidtrading.com/en/articles/11404736-prohibited-high-frequency-trading), [Lucid microscalping](https://support.lucidtrading.com/en/articles/11404742-prohibited-microscalping)
- **DayTraders: allowed, including copying to other firms (2026-10-22).** "Trade copiers that copy trades across your own accounts, including accounts at other firms. Running your platform or tools on a VPS." Not allowed: millisecond order placement or changes, latency reliance, "Trading for other people", and "Using a copier or automation to hedge or to exceed your max contracts". [official] — [DayTraders automation](https://daytraders.com/help/articles/17704087-automation-ai-and-trade-copiers)
- **FFN: allowed, but identical bots count as copy trading.** FFN treats "Automated trading systems/bots running identical strategies across accounts" as copy trading. Copy-traded accounts are capped (FFN advertises copying across 5 funded accounts, "up to $1.25 million in sim capital"). It uses an EOD drawdown that is "basically static" once sim funded. [official] — [FFN 7.1 copy trading](https://app.fundedfuturesnetwork.com/nexus/rules/article-7-1-copy-trading-limits-and-rules), [FFN why](https://fundedfuturesnetwork.com/why)
- **FundedNext Futures: allowed.** It "allows VPN/VPS, news trading, and EAs/bots", with a one-time fee, no overnight or weekend holding and no refunds. Its terms say the limit is recalculated "from the highest recorded End Of Day Balance". Cross-account hedging, inside FundedNext or with other firms, is not allowed. [official] — [FundedNext Futures FAQ](https://helpfutures.fundednext.com/en/articles/17225788-fundednext-futures-most-frequently-asked-questions), [FundedNext futures terms](https://fundednext.com/futures-challenge-terms)
- **The Trading Pit: allowed with limits.** On CFD Prime Swing, EAs are allowed if they don't copy signals that aren't yours, run "latency/reverse/hedge/arbitrage or HFT", use emulators, or trade within 2 minutes of high-impact news on $100K/$200K accounts. A VPS is allowed. On futures, NinjaTrader copying works only via "Replikanto FlowBots – Compliance Edition". [official] — [TTP CFD Prime Swing](https://support.thetradingpit.com/en/articles/835084-cfd-prime-swing-rules), [TTP futures platforms](https://support.thetradingpit.com/en/articles/836080-futures-prime-platforms-conditions)
- **Blueberry Futures: only self-built bots (2026-10-01).** A bot is allowed only if "It is proprietary. You built it yourself. Not bought, rented, shared, or commissioned from someone else", it runs your own strategy, and it is disclosed in advance with consent. [official] — [Blueberry](http://help.blueberryfutures.com/en/articles/12921692-can-i-use-eas-bots-or-copy-trading)
- **Blue Guardian Futures: limited (and Malaysia-restricted for futures anyway).** "Systems that place more than 200 trades a day are not allowed. Hands-off, round-the-clock automated trading is not allowed." [official] — [Blue Guardian prohibited strategies](https://help.blueguardian.com/en/articles/18426719-prohibited-trading-strategies)
- **Top One Futures: banned.** "Use of any automated trading system, script, bot, Expert Advisor (EA)… is strictly forbidden." It also bans trading on "trades executed elsewhere (for example… at another firm)". [official] — [Top One Futures](https://help.toponefutures.com/en/articles/11021584-prohibited-trading-practices)
- **Tradeify: allowed only at Tradeify.** Earlier repo work recorded that its bot must be used only at Tradeify, with ownership proof and a live video, so the same bot cannot also run at Topstep. [repo] — `docs/NOTES_JX.md`
- **Apex 4.0: conflicting reports.** One rules card says automation is allowed in evaluations but fully automated systems are banned on funded and live accounts (semi-automated only). I could not get an official page through Cloudflare. [search] — [puravidaedge Apex card](https://puravidaedge.com/firms/apex/)
- **Breakout / Kraken Prop: no API.** Kraken's prop page says "does not currently offer API access… All orders on a Prop account are placed manually." [repo] — `docs/NOTES_JX.md` 2026-11-20
- **FTMO (CFD and Futures): allowed, own decisions only.** "Automated trading is permitted. You must not, however, use software… that manipulate, abuse, or provide an unfair advantage… including high-frequency strategies and latency arbitrage." Futures accounts must not "replicate, follow, or otherwise incorporate the trading decisions of any third party… via signal services, master accounts, trade copiers". FTMO also warns that a third-party EA risks denial because others may run the same strategy. [official] — [FTMO Futures forbidden practices](https://ftmo.com/en/futures/forbidden-trading-practices/), [FTMO strategies FAQ](https://ftmo.com/en/faq/which-instruments-can-i-trade-and-what-strategies-am-i-allowed-to-use/)
- **The5ers: EA bans.** It bans EAs that scalp the rollover and third-party EAs "where other traders have the same trades open". [official] — [The5ers prohibited practices](https://the5ers.com/faqs/prohibited-trading-practices/)
- **FXIFY (CFD): EAs allowed, but Malaysia unclear.** It advertises EAs, news trading, weekend holds and static drawdown, and "Martingale & Grid Allowed" with a "100% Refund" on its three-phase program. It lists Malaysia in its checkout country picker, but a search hit says FXIFY **Futures** prohibits Malaysia. Check the CFD and futures products separately. [official/search] — [FXIFY](https://fxify.com/), [FXIFY 3-phase](https://fxify.com/programs/three-phase-challenge/)
- **City Traders Imperium (CFD): most permissive found.** The 1-Step allows "Martingale and third-party EAs", has no daily drawdown, a 5% trailing balance-based drawdown, a first payout at 7 days, and an 80–100% split. Malaysia status not checked. [official] — [CTI 1-Step](https://citytradersimperium.com/1-step-challenge/), [CTI EA rules](https://citytradersimperium.com/ea-trading-rules/)
- **HyroTrader (crypto): own strategies only, via exchange API.** Challenges run through Bybit or BloFin demo accounts connected by API, or its own platform. Rules: 4% daily, 8% max loss, 10% target, a 40%-per-day profit-distribution rule, and an 80–90% split. Banned: Martingale, "Hedging across multiple accounts", more than 5% of balance in low-cap coins, and "Strategies that only profit from news-driven pricing errors". Third-party summaries of its terms say automation of your own strategy is permitted but not purchased systems, copy trading or signals. Its Tealstreet and Tiger terminals are unavailable where Bybit is restricted, "and you must not use a VPN". [official/search] — [HyroTrader trading rules](https://www.hyrotrader.com/trading-rules/), [HyroTrader terms](https://www.hyrotrader.com/terms-and-conditions/), [propfirmpal summary](https://propfirmpal.com/firms/unverified/hyrotrader)
- **Crypto Fund Trader: bots allowed with bans, Malaysia unverified.** Third-party reviews say EAs and bots are allowed, but HFT, tick scalping, arbitrage EAs and multi-account reverse-trading EAs are not. Reports on copy trading conflict. The firm describes itself as "all demo" and a Bybit partner. [search/official] — [LuxAlgo CFT](https://www.luxalgo.com/prop-firms/crypto-fund-trader/), [CFT home](https://cryptofundtrader.com/)

### Inferences
- **Third-party strategy clauses decide which firms work.** The repo's bot is the friend's strategy (CLAUDE.md: the friend trades on the friend's own computer and account). FTMO, HyroTrader, Blueberry, Goat Funded Trader and The5ers forbid running another person's strategy or decisions. They would exclude the bot on accounts in Jx's name. They do not affect accounts in the friend's own name.
- **DayTraders is the cleanest fit for running one bot at several firms.** It explicitly allows copying into accounts at other firms and allows a VPS. Topstep is the binding constraint: no VPS, own device only.
- **FFN would cap the multi-account bot.** It counts identical bots across accounts as copy trading, so the bot would fall under its account-count caps.

### Gaps
- **Unread official pages.** I could not read Apex, Tradeify, Bulenox, Take Profit Trader or Earn2Trade help pages; they returned Cloudflare pages or link indexes only. Bulenox's FAQ shows the question "Can I use bots, algos or trade copiers?" but not the answer.
- **Malaysia unverified for some firms.** No official list was found for Crypto Fund Trader, Breakout, HyroTrader (its terms refer to a separate "Restricted Jurisdictions List" that did not render), FXIFY CFD (versus Futures) or CTI.

## 2. Rule asymmetries that change expected value

### Takeaway
The biggest lever is **how the loss limit is measured**. "End-of-day" on paper often still breaches in real time on open P&L (Topstep, Apex), and only
some firms (Lucid) ignore unrealized P&L. Next come a trailing drawdown that locks at the start balance, consistency caps and payout caps, and the
fee refunded on first payout (CFD/forex). Firms add or tighten these with little notice; Topstep, Apex and FundingTicks all made major mid-life
changes in 2025–2026.

### Cited Findings
- **Topstep checks the loss limit on open P&L in real time.** The repo found this on 2026-11-26 and corrected its model. Topstep 50K Consistency fell from $46.5K to about $37–40K over 2016–26. [repo] — [help.topstep.com 8284204](https://help.topstep.com/en/articles/8284204), `docs/AUDIT_PRE_LIVE_20261126.md`
- **Lucid ignores unrealized P&L; FundedNext and Blueberry breach on live equity.** Under the real-time check, LucidDaily, TTP Prime and DayTraders EOD fail the repo's coin-flip bar unless they also ignore open P&L. Whether they do is unconfirmed. [repo] — `docs/NOTES_JX.md` 2026-11-26
- **Apex "EOD" is also enforced intraday.** Since 2026-03-01 Apex offers EOD or intraday trailing drawdown. The EOD floor is reset at 4:59:59 PM ET but "still enforce[d]… in real time during the next session, open profit and loss included". Consistency is 50% on new funded accounts (30% on legacy) and none in evaluations. The MAE and 5:1 risk-reward rules are reported removed, and there is a 30-day evaluation limit. [search] — [SpicyFutures Apex 4.0](https://spicyfutures.com/apex-trader-funding-4-0-review-2026/), [tradedupe](https://tradedupe.com/apex-consistency-rule), [dealpropfirm](https://dealpropfirm.com/articles/apex-trader-funding-march-2026-new-rules)
- **FFN: EOD drawdown that becomes static once funded.** [official] — [FFN why](https://fundedfuturesnetwork.com/why)
- **Topstep XFA changes in 2026.** These are third-party reports and some conflict:
  - two XFA paths from about 2026-02-05: Standard needs 5 winning days of $150 or more; Consistency needs 3 days and a 40% best-day target;
  - per-cycle payout caps on new No-Activation-Fee 50K/100K Combines cut to $2,000 (Standard) or $3,000 (Consistency) on about 2026-04-28, from $5,000 and $6,000;
  - per-trade commissions added on TopstepX from about 2026-04-12.
  Topstep's rules page says it may change rules "with or without prior notice". [search] — [curvedtrading](https://curvedtrading.com/articles/en/reviews/topstep-review/), [tradecovex](https://tradecovex.com/guides/topstep-rule-changes-2026), [nexusfi](https://nexusfi.com/showthread.php?p=911770), [Topstep XFA rules](https://topstep.com/express-funded-account-rules)
- **Topstep moves traders to Live accounts.** The Live account starts at 20% of cumulative XFA balance, capped at account size, with a $10,000 minimum. [official] — [Topstep call-up](https://help.topstep.com/en/articles/13747178-live-funded-account-call-up-and-call-down-process)
- **Some firms refund the fee with the first payout:**
  - FTMO: "One-time refundable fee… Refund Yes 100%";
  - FXIFY: "Refundable Fee 100%";
  - AquaFunded: "One-time fee • 100% refundable";
  - BrightFunded: "100% Account Fee Refund" as an add-on;
  - The Trading Pit Prime: fee "returned to you with a payout";
  - FundedNext Stellar 1-Step: a 150% Reward add-on returns 150% of the fee at the first or third reward.
  Instant-funding products generally do **not** refund: TTP CFD Instant, CTI Instant. [official] — [FTMO](https://ftmo.com/en/), [FXIFY](https://fxify.com/programs/three-phase-challenge/), [AquaFunded](https://aquafunded.com/), [BrightFunded](https://brightfunded.com/), [TTP CFD Instant](https://support.thetradingpit.com/en/articles/835378-cfd-instant-how-it-works), [FundedNext Stellar 1-Step](https://help.fundednext.com/en/articles/17252927-stellar-1-step-account), [CTI VIP](https://citytradersimperium.com/vip-program-payout/)
- **Goat Funded Futures refunds unpaid sim accounts at the move to live.** Sim accounts that have not had a payout "are simply closed and its account fee refunded" when they transition to live (e.g. 3×50K → 150K Live with a $4,500 EOD trailing drawdown). [official] — [GFF transition](https://help.goatfundedfutures.com/en/articles/15563248-transition-what-happens-when-i-transition-from-sim-to-live) (Malaysia restricted)
- **FTMO Futures limits on holding and price limits.** No positions or resting orders past session end (auto-liquidated), and no new positions within 2% of a CME daily price limit. [official] — [FTMO Futures forbidden practices](https://ftmo.com/en/futures/forbidden-trading-practices/)
- **TTP Futures Prime 50K.** Rules: $1,000 daily pause, force-close at 14:55 CT (Topstep 15:10), 40% consistency in the challenge, and copy trading allowed "manually or automatically" across up to 5 own accounts. [repo/official] — [TTP Futures Prime rules](https://support.thetradingpit.com/en/articles/836071-futures-prime-rules)
- **CFD static drawdowns favour higher risk per trade, but firms police it.** FTMO 2-Step failed the repo's coin-flip test; FTMO recommends ≤1% risk per trade, where the structure adds nothing. [repo] — `docs/NOTES_JX.md` 2026-11-20/23

### Inferences
- **Funded-account value depends on several rules together.** These are the real-time vs end-of-day check, the payout cap per cycle, the minimum winning days, and the consistency ratio. Evaluation price is usually second-order unless a monthly subscription runs for many months.
- **A refund on first payout effectively makes the evaluation free conditional on success.** Break-even pass probability then depends only on the expected payout, not the fee. This helps a strategy with a low pass rate but a high payout when it passes. For automated futures it exists mainly at CFD-style firms.

### Gaps
- **Open-P&L checks unconfirmed.** I found no official statement on whether DayTraders, TTP Prime, FFN or Bulenox check the loss limit on open P&L. This matters most for the repo's model.
- **Topstep's current payout policy unread.** I could not read the official XFA payout policy page from here, and third-party figures conflict ($150 vs $200 winning days).

## 3. Promotions: frequency, depth, and effect on break-even

### Takeaway
Deep discounts are routine. Apex ran a 90%-off code about every one to two months through 2025–2026. In late November 2026 (Black Friday) firms
showed 25–85% off, BOGO deals and bundle tiers. Discount-only buying sharply lowers break-even for **one-time-fee** products. For monthly-subscription
firms the discount usually covers only the first month and not resets or activation fees, so the gain is smaller.

### Cited Findings
- **Apex ran 90%-off sales about every one to two months.** These are mostly sponsored press releases or affiliate reports:
  - December 2025: Christmas code KPQQCFDP; SAVENOW at about $19.60 per account;
  - to January 6, 2026: code FUTURE;
  - to March 9, 2026: up to 90% off intraday and 85% off EOD at the 4.0 relaunch;
  - May 28 – June 3, 2026: code FUTURE with 5-packs and zero-activation options;
  - to October 13, 2026: Legacy accounts at 90% off the first month.
  A guide says Apex issues codes "roughly once a month… 50–90% off list" and that the discount "doesn't touch the monthly subscription, the reset fee, or the Performance Account activation". [search] — [invezz Jan 2026](https://invezz.com/news/2026/01/07/apex-trader-funding-brings-back-massive-90-discount-with-code-future/), [invezz May 2026](https://invezz.com/news/2026/05/28/apex-trader-funding-launches-90-off-promotion-5-pack-bundles-zero-fee-options/), [spacecoastdaily Dec 2025](https://spacecoastdaily.com/2025/12/apex-trader-funding-christmas-sale-2025-get-90-off-with-code-kpqqcfdp/), [skool restructure sale](https://www.skool.com/investceo/apex-trader-funding-website-product-restructure-plus-up-to-90-off-sale-through-march-9), [eltraderfinanciado legacy 90%](https://www.eltraderfinanciado.com/en/news/apex-trader-funding/apex-riporta-i-conti-legacy-al-90-di-sconto), [fortraders coupon analysis](https://fortraders.com/blog/apex-trader-funding-coupon-codes)
- **Offers on official pages, late November 2026** [official]:
  - FFN: "70% OFF on Nexus or 50% OFF + Buy 1, Get 1 Free on Max Accounts", with a coupon NEXUS checkout link — [FFN accounts](https://fundedfuturesnetwork.com/accounts)
  - Alpha Futures: "EARLYBOGO40 25K Zero BOGO + 40% off" (Malaysia restricted) — [Alpha Futures](https://alpha-futures.com/)
  - Phidias: "Up to 85% Off OTP & Up to 60% Off Evals" — [Phidias](https://phidiaspropfirm.com/faq)
  - Finotive Futures: "60% off Instant · 40% off One Step" — [Finotive](https://finotivefutures.com/)
  - Funded Futures Family: "50% off your first account, plus a $250 payout bonus" — [FFF](https://www.fundedfuturesfamily.com/)
  - Blue Guardian: "30% OFF All accounts" plus bundle tiers of 25%/30%/35%/40% for 1–4+ accounts in one order — [Blue Guardian](https://www.blueguardian.com/), [bundle discounts](https://help.blueguardian.com/en/articles/18426642-futures-bundle-discounts)
  - AquaFunded: 35% off, rising to −40%/−45% for a 2nd and 3rd account — [AquaFunded](https://aquafunded.com/)
  - BrightFunded: "30% Off + Free Account Upon Payout" — [BrightFunded](https://brightfunded.com/)
  - Audacity: 50%/30% off — [Audacity](https://audacitycapital.co.uk/)
  - E8: 15% off — [E8](https://e8markets.com/)
  - DayTraders: a free demo account — [DayTraders](https://daytraders.com/)
- **Topstep discounts are smaller.** A referral gives 15% off the first purchase. Promo codes apply "to a new Trading Combine® or a Reset — not both". The ProjectX API has a 50% code "topstep". A $3K Challenge at $49 was a past Labs Drop and is no longer on sale ($199 now, which fails the repo model). [official/repo] — [Topstep dashboard](https://help.topstep.com/en/articles/10513413-getting-started-with-the-topstep-dashboard), [Topstep API](https://help.topstep.com/en/articles/11187768-topstepx-api-access), `docs/GO_LIVE_MULTIFIRM.md`
- **Coupons renew at the discounted price at one firm.** "If you used a discount coupon, it renews at the same price." [official] — [Blusky billing](https://help.blusky.pro/en/articles/12434108-billing)
- **MFFU's rewards can't stack with promo codes.** Rewards "cannot be combined with promotional codes" unless stated. [official] — [MFFU club](https://help.myfundedfutures.com/en/articles/16130843-myfundedclub-membership-perks-and-rewards)
- **One firm calls constant sales a red flag.** City Traders Imperium writes: "If every week is '90% off for 24 hours only,' the pricing is designed to pressure you". [official] — [CTI](https://citytradersimperium.com/no-evaluation-prop-firms/)

### Inferences
- **Break-even formula.** Per attempt: EV = p_pass × E[net payouts | funded] − (eval fee + resets + activation + data/platform fees).
  - At 90% off a one-time $150 fee, cost drops to about $15. The break-even pass rate falls tenfold, provided activation and other fees are not also charged.
  - For monthly products, the saving is (1 − d) × first month only. A strategy that takes M months to pass saves d × fee / (M × fee), about d/M.
- **Buy only during sales.** A recycler buying only at sales (Apex-style 90% roughly monthly; Black Friday and holiday sales elsewhere) can lower acquisition cost substantially. This is legitimate, but the next sale date is not guaranteed. Bundle and BOGO deals are worth most where the firm allows the same bot on several accounts (DayTraders, Lucid, TTP; FFN up to its copy cap).

### Gaps
- **No price history.** There is no free systematic price/discount history for futures firms. The repo's earlier third-party prices need confirming at checkout (`docs/GO_LIVE_MULTIFIRM.md`).

## 4. Practices firms explicitly ban (excluded from any plan)

### Takeaway
All of these are excluded because they break written rules:
- hedging between accounts or firms;
- copying another person's trades or signals;
- HFT, latency arbitrage, emulators and microscalping;
- rollover and news-error scalping;
- Martingale (at most firms);
- holding past the session at FTMO Futures;
- going over position limits through copiers;
- VPS use at Topstep;
- VPN use to get around geoblocks;
- third-party or purchased EAs at several firms.
Firms detect these automatically, by matching identical trades across accounts and by IP or device.

### Cited Findings
- **Hedging across accounts, users or firms.** Banned in writing at:
  - Lucid ("between different firms or funded platforms"; flagged accounts are reset to the prior day's balance) — [Lucid hedging](https://support.lucidtrading.com/en/articles/11404734-prohibited-hedging)
  - FundedNext futures and CFD (including "accounts maintained at other firms") — [FN futures terms](https://fundednext.com/futures-challenge-terms), [FN CFD terms](https://fundednext.com/cfd-challenge-terms)
  - Top One Futures — [Top One](https://help.toponefutures.com/en/articles/11021584-prohibited-trading-practices)
  - Blue Guardian ("in one account or across several") — [Blue Guardian](https://help.blueguardian.com/en/articles/18426719-prohibited-trading-strategies)
  - HyroTrader — [HyroTrader rules](https://www.hyrotrader.com/trading-rules/)
  - DayTraders ("Using a copier or automation to hedge") — [DayTraders](https://daytraders.com/help/articles/17704087-automation-ai-and-trade-copiers)
- **Copying other people's trades or signals, or third-party strategies.** Banned at:
  - FTMO Futures ("regardless of whether the service is paid or free") — [FTMO](https://ftmo.com/en/futures/forbidden-trading-practices/)
  - FundedNext: no copying between any FundedNext accounts, "whether it belongs to the same individual or another entity", detected by identical entry/exit/lot/time. First breach brings a warning and no reward for the cycle. — [FundedNext copy rule](https://help.fundednext.com/en/articles/8019805-what-is-the-copy-trading-rule-at-fundednext)
  - Goat Funded Trader ("any third-party strategy, off-the-shelf strategy or one marketed to pass challenge accounts"; also bans switching between EA in the assessment and manual in funded) — [GFT T&C](https://www.goatfundedtrader.com/legal/terms-and-conditions)
  - Blueberry — [Blueberry](http://help.blueberryfutures.com/en/articles/12921692-can-i-use-eas-bots-or-copy-trading)
  - The5ers — [The5ers](https://the5ers.com/faqs/prohibited-trading-practices/)
  - DayTraders ("Trading for other people") — [DayTraders](https://daytraders.com/help/articles/17704087-automation-ai-and-trade-copiers)
- **Copying between your own accounts at other firms is allowed at some firms.** DayTraders, AquaFunded ("between AquaFunded account and external accounts") and Blue Guardian ("your own external accounts") allow it. Top One Futures bans trading on trades executed at another firm, and so does Tradeify (bot exclusivity, per the repo). [official] — [AquaFunded copy](https://help.aquafunded.com/en/articles/11877755-is-copy-trading-allowed), [Blue Guardian Instant](https://help.blueguardian.com/en/articles/18426779-instant-standard-account-rules)
- **HFT, latency, reverse or arbitrage EAs, and emulators.** Banned at:
  - FTMO — [FTMO](https://ftmo.com/en/futures/forbidden-trading-practices/)
  - The Trading Pit — [TTP](https://support.thetradingpit.com/en/articles/835084-cfd-prime-swing-rules)
  - Lucid — [Lucid HFT](https://support.lucidtrading.com/en/articles/11404736-prohibited-high-frequency-trading)
  - Goat Funded Trader ("Gold Arbitrage EA") — [GFT](https://www.goatfundedtrader.com/legal/terms-and-conditions)
  - DayTraders (milliseconds, order spam) — [DayTraders](https://daytraders.com/help/articles/17704087-automation-ai-and-trade-copiers)
  - Crypto Fund Trader (HFT, tick scalping, arbitrage EAs) [search] — [LuxAlgo](https://www.luxalgo.com/prop-firms/crypto-fund-trader/)
  At TTP, accounts using banned EAs are "denied any upgrade or payout, and the Challenge is not refunded".
- **Rollover and news-error scalping.** The5ers bans EAs that scalp the rollover; HyroTrader bans "strategies that only profit from news-driven pricing errors"; TTP blocks trades 2 minutes either side of high-impact news on large accounts. [official] — sources above
- **Microscalping.** Lucid flags accounts where more than 50% of profit comes from trades held 5 seconds or less. [official] — [Lucid](https://support.lucidtrading.com/en/articles/11404742-prohibited-microscalping)
- **Martingale.** Banned at HyroTrader; allowed at FXIFY and CTI 1-Step. [official]
- **Gambling patterns.** Top One Futures cites "trial-and-error 'gambling' style": buying many accounts and breaching all within 24 hours. [official] — [Top One](https://help.toponefutures.com/en/articles/11021584-prohibited-trading-practices)
- **VPS/VPN.** Topstep prohibits VPS, VPN and remote servers for order flow. HyroTrader forbids a VPN to get around Bybit geo-restrictions. [official] — [Topstep](https://help.topstep.com/en/articles/11187768-topstepx-api-access), [HyroTrader](https://www.hyrotrader.com/trading-rules/)
- **A disputed VPN/VPS denial.** A $2,000 instant-funding payout was reportedly denied in April 2025 over alleged VPN/VPS use; the trader blamed corporate security software. [search] — [fundedtrading.com](https://fundedtrading.com/are-prop-firms-legit/)

### Inferences
- **What is out.** The only "grey" levers that stay inside the rules are structural: choosing firms whose measurement rules suit the strategy, buying during sales, using fee refunds, and running one's own bot on the allowed number of own accounts at firms that permit it. Anything that profits from the firm's simulator itself is out, as is anything involving other people's accounts or opposite positions across accounts. Simulator exploits include latency, rollover, news-error scalping and emulators.

### Gaps
- **Household and IP limits.** Rules vary (Lucid and Breakout count per household, per the repo). I did not compile a full table of household or IP limits.

## 5. Payout reliability and firm failures (2024–2026)

### Takeaway
The industry kept losing firms through 2025–2026. Trackers count about 80–100 closures in 2024–25. Recent closures more often came with refunds:
FundingTicks (January 2026) and Propel Capital (August 2025) refunded, while True Forex Funds (2024) and The Funded Trader's denials left traders
unpaid. The CFTC's case against My Forex Funds was dismissed with sanctions against the CFTC in May 2025, so there is no US enforcement precedent.
Rule changes applied to existing accounts are the main payout risk, even at large firms: a pro se suit against Topstep in April 2026 alleges exactly
this.

### Cited Findings
- **My Forex Funds: CFTC case dismissed, CFTC sanctioned.** A New Jersey federal judge dismissed the CFTC's complaint against Traders Global Group with prejudice and awarded fees for sanctions (order signed 2025-05-13). The CFTC put four lawyers and one investigator on leave, and MFF signalled a comeback. [search: Willkie, Finance Magnates, Quinn Emanuel] — [Willkie](https://complianceconcourse.willkie.com/articles/new-jersey-federal-judge-dismisses-forex-case-with-prejudice-and-awards-attorney-fees/), [Finance Magnates](https://www.financemagnates.com/forex/my-forex-funds-parent-defeats-cftc-in-court-as-judge-imposes-sanctions/), [MFF comeback](https://www.financemagnates.com/forex/myforexfunds-hints-at-comeback-after-winning-legal-battle-against-cftc/)
- **FundingTicks (owned by FundingPips): wound down mid-January 2026.** This followed stricter rules in December 2025 that traders said were applied retroactively, cancelling earned profits and completed stages. Reports say full refunds of evaluation and master-account fees and payouts to funded traders, made "as an act of goodwill". [search] — [Finance Magnates](https://www.financemagnates.com/forex/following-profit-cuts-and-trading-limits-prop-firm-fundingticks-begins-winding-down/), [Tradeinformer](https://tradeinformer.com/broker-news/fundingpips-shuts-futures-prop-firm-fundingticks), [Prop Firm Match news](https://propfirmmatch.com/industry-news/fundingticks-announces-full-wind-down-of-operations)
- **Other closures and denials:**
  - True Forex Funds reportedly left about 300 traders with about $1.2M unpaid (figure traced to a competitor's reporting);
  - The Funded Trader's CEO disclosed more than $2M in denied withdrawals in January–February 2024, against $17M+ paid;
  - Propel Capital closed on 2025-08-19 with promised refunds, fulfilment unconfirmed;
  - Pro Traders Fund reportedly went silent in October 2025.
  [search; trackers] — [propnavi history](https://propnavi.io/en/blog/prop-firm-shutdowns-history/), [propfirmverifier tracker](https://www.propfirmverifier.com/prop-firm-shutdowns), [thepropfirmguide](https://thepropfirmguide.com/prop-firms-that-shut-down/), [propfirmtrading graveyard](https://propfirmtrading.net/graveyard)
- **FundedFirm: unverified allegations.** It had a 2.5 Trustpilot score and 212+ reviews in February 2026, alleging systematic denials, fabricated payouts and a cloned site. [search] — [dealpropfirm](https://dealpropfirm.com/articles/fundedfirm-85m-scandal)
- **Topstep lawsuit (pro se, April 2026).** Vincent McCrudden filed case 3:26-cv-00816-WWB-LLL on 2026-04-09, alleging a scheme to collect fees and use rule changes to block payouts, plus a bait-and-switch to Live accounts. It is a single-plaintiff suit, not a class action, and early stage; Topstep's terms likely require arbitration. Separately, Topstep had a data breach in December 2025. [search: forum only] — [NexusFi thread](https://nexusfi.com/funded-trading-evaluation-firms/61682-trader-files-federal-lawsuit-against-topstep-alleging-deceptive-practices-claims-rule-change.html), [ClaimDepot breach](https://www.claimdepot.com/investigations/topstep-data-breach-2025)
- **Platform risk.** In early 2024 MetaQuotes cut off grey-label MT4/MT5 for US-facing prop firms, and many firms closed or migrated. FTMO and The5ers later returned to the US, FTMO via OANDA on MT5, and Funding Pips got a direct MetaQuotes licence. Finance Magnates (2026-07-01) reports cTrader restricting US prop-firm access after an "internal regulatory assessment". Separately, ProjectX ended third-party service on 2026-02-28, so Lucid left ProjectX [repo]. [search] — [Finance Magnates MT5 back](https://www.financemagnates.com/forex/prop-trading-on-metatrader-5-is-back-in-the-us/amp), [cTrader restricts](https://www.financemagnates.com/forex/ctrader-restricts-us-prop-firm-access-following-internal-regulatory-assessment/), [Funding Pips MT5](https://www.financemagnates.com/forex/funding-pips-becomes-latest-prop-firm-to-bring-metatrader-5-back-after-year-long-hiatus)
- **Payout volumes (firm-reported).** Prop Firm Match tracked about $325M (exactly $324,963,316) in 2025, sourced from firms and excluding FTMO and The5ers. FundedNext topped it at about $108M. Crypto prop payouts doubled to $115M in Q1 2026 but had stalled since December, and two firms held 71% of volume. [search] — [Finance Magnates PFM 2025](https://financemagnates.com/forex/prop-firm-match-tracked-about-325-million-in-payouts-to-traders-in-2025), [FM crypto Q1 2026](https://www.financemagnates.com/forex/analysis/prop-firm-crypto-payouts-doubled-to-115-million-in-q1-2026-but-growth-has-stalled-since-december/)
- **Breakout's own payout claims.** It claims "$80M+ paid to traders" and "160+ countries served", with a lifetime leaderboard of top traders at $0.5–0.7M (updated monthly from February 2025). These are self-reported. [official] — [Breakout](https://breakoutprop.com/)
- **Complaint clusters on Trustpilot.** A review aggregator counted 37 one- or two-star reviews (2026-09-18 to 10-05) mentioning denied payouts, with firms citing coordinated trading, VPS or news rules. It is unverified, and the firm is not named in the snippet. [search] — [edge-ledger tracker](https://edge-ledger.io/prop-firm-payout-tracker)

### Inferences
- **The risk is rule changes, not outright default.** For a rules-following bot at an established firm, the main payout risk is retroactive or forward rule changes that cut caps or add costs (Topstep 2026 caps and commissions; FundingTicks). Spreading across 3–4 firms limits the damage from any single change.
- **Expect enforcement to look at patterns.** Denials cluster around coordinated or identical trading across accounts and VPS use. These are exactly the patterns a one-bot, multi-account plan produces, so it is safe only at firms that allow it in writing (DayTraders, Lucid, TTP; FFN up to its copy cap).

### Gaps
- **No audited data.** I found no audited, independent payout-denial rate per firm. All payout totals are firm-reported, and complaint counts are anecdotal.

## 6. What free data can measure this

### Takeaway
Free, repeatable sources exist:
- official rule and help pages, already scraped into `data/public/propverify` by the repo's GitHub Actions job, which can be re-run to diff rule changes over time;
- Prop Firm Match payout listings and country/EA filters;
- shutdown trackers;
- Trustpilot review pages;
- court dockets (CourtListener).
No free systematic discount-price history was found.

### Cited Findings
- **Rule-page text.** The repo's `.github/workflows/prop_verify.yml` and `scripts/prop_verify_fetch.py` render official pages (444 JSON files as of 2026-11-28), including deep help-centre crawls of Lucid, DayTraders, FTMO, FundedNext, The5ers, TTP, Blueberry and Blue Guardian. [repo] — `docs/PROP_VERIFY_20261122.md`
- **Prop Firm Match.** Payout listings by asset class (futures, crypto, perpetuals) and Malaysia-filtered firm lists. The data are firm-supplied. [search] — [PFM payouts](https://propfirmmatch.com/futures/payouts/leveraged?page=10), [PFM Malaysia restricted](https://propfirmmatch.com/futures/prop-firm-lists/restricted-countries/malaysia)
- **Shutdown trackers (third-party).** [search] — [propfirmverifier](https://www.propfirmverifier.com/prop-firm-shutdowns), [propfirmtrading graveyard](https://propfirmtrading.net/graveyard), [edge-ledger](https://edge-ledger.io/prop-firm-payout-tracker)
- **Court records.** [search] — [CourtListener](https://storage.courtlistener.com/), Topstep case 3:26-cv-00816
- **Self-reported payouts.** Breakout's monthly leaderboard and Crypto Fund Trader's "Payouts live on Propfirmmatch.com" are firm self-reports. [official] — [Breakout](https://breakoutprop.com/), [CFT](https://cryptofundtrader.com/)

### Inferences
- **Track rule and price changes cheaply.** Re-running prop_verify weekly and diffing the text would give a dated rule-change log and a promotion log. The promotion banners are captured in the page text: FFN 70%, Phidias 85%, Alpha BOGO and so on.

### Gaps
- **Prop Firm Match not fetched.** Its pages and the shutdown trackers could not be fetched from this sandbox; they need adding to `scripts/fetch_public.py` for the GitHub Actions runner.
- **Unrendered help centres.** Apex, Tradeify and Bulenox help centres sit behind Cloudflare and did not render, even on GitHub Actions.

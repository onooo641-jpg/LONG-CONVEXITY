# Prop-firm fact verification from official pages — 2026-11-22 (in progress)

Jx asked (2026-11-22) for every prop-firm fact to be verified directly. Method: official sites rendered with a headless browser on GitHub Actions
(`.github/workflows/prop_verify.yml`, `scripts/prop_verify_fetch.py`; pass 2 clicks pricing tabs, `scripts/prop_verify_click.py`; pass 3 crawls
help centres deeply). Raw text: `data/public/propverify/*.json`. Public pages only, no logins, no evasion. Each fact: **verified** (official text
matches the model), **differs** (official text differs → model corrected and re-priced), **not found** (not on the pages read).

## 1. Malaysia access (decisive; official restricted-country lists)
| firm | status | source (official) |
|---|---|---|
| **MyFundedFutures** (all plans: Rapid EOD, Pro, Builder, Studio) | **RESTRICTED: Malaysia is on its list** | help.myfundedfutures.com/en/articles/8229993-restricted-countries-policy (updated 2026-10-14) |
| **FuturesElite** (Nitro, Elite, Prime, Instant) | **RESTRICTED** ("does not provide services to users residing in … Malaysia") | futureselite.com/terms-and-conditions |
| **Alpha Futures** (all plans) | **RESTRICTED** (even visiting: trading not permitted) | help.alpha-futures.com/en/articles/9523389-countries-with-limitations (2026-08-12) |
| **Blue Guardian Futures** | **RESTRICTED for Futures** (CFD allowed) | help.blueguardian.com/en/articles/18426607 (2026-11-13) |
| Alpha Capital Group (CFD) | available (Malaysia in its checkout list) | alphacapitalgroup.uk/resources/alpha-capital-country-availability-2026 |
| Funded Futures Network, Traders Launch, Top One Futures, FXIFY | Malaysia selectable in the checkout country list (available, unless a separate list says otherwise) | their checkout pages |
| Topstep, Lucid, TTP, DayTraders, Tradeify, TradeDay, Goat, Blueberry, FundedNext, TFD, Bulenox, FTMO | no restriction found yet; deep help-centre crawl (pass 3) pending | — |
**Consequence:** the multi-firm plan (Topstep + Lucid + MFFU, `docs/PREREG_PORTFOLIO2_20261120.md`) includes a firm that does not accept
Malaysian residents. The flagged FuturesElite Nitro / Elite and the near-miss Alpha Standard and Blue Guardian products are not available to a
Malaysian resident either. (The friend's own account, on the friend's computer, depends on the friend's residence, not Jx's.)

## 2. Product rules
### Topstep 50K (benchmark) — verified, with one better option found
Official checkout (dashboard.topstep.com/guest/checkout/7/account) and help centre: $49/month ✔, reset $49 ✔, activation $149 ✔, target $3,000 ✔,
MLL $2,000 EOD trailing, locks at start ✔, 5 minis / 50 micros ✔, XFA payout 50% up to $2,000 (Standard) ✔, 5 winning days of $150 ✔, 90/10 ✔,
up to 5 XFAs ✔. Not in the model: a **55% consistency target** in the Combine (repriced: no effect, $44,359 unchanged, as `docs/GO_LIVE.md` said);
**XFA Consistency path** (3 days, 40%, cap $3,000) → **$46,492** (+$2,133); No-Activation path ($95/mo, reset $85) → $45,335; optional $1,000
DLL doubles payout caps (limited-time offer from June 2; not priced: a $1,000 DLL is about one losing trade at $900 risk).
### The Trading Pit Futures Prime 50K — verified
thetradingpit.com/futures and support.thetradingpit.com/en/articles/836071-futures-prime-rules: $99 one-time ✔, reset $79 ✔, target $3,000 ✔,
max drawdown $2,000 trailing EOD ✔, 5 / 50 contracts ✔, 30-day challenge ✔, 40% consistency in the Challenge (raises the target) ✔, activation
$129 shown struck through to $0 (promotion) ✔ (model $0), 80% split ✔, reward 50% of profit up to $2,500 ✔, 5 days of $150 ✔, every 7 days
(not modelled), $1,000 daily pause (auto-close for the day; not modelled), force-close 14:55 CT (Topstep 15:10), copy trading "manually or
automatically" across up to 5 own accounts allowed; HFT / grid / martingale / gap prohibited. No explicit EA sentence for futures.
### FuturesElite — resets verified; Instant model **differs**; firm restricted for Malaysia
Evaluation resets (faq.futureselite.com/en/articles/17585246-reset-fees): Elite 50K $89 ✔, Prime $109 ✔, Nitro $99 ✔. Instant 50K
(futureselite.com/instant-account): drawdown 5% = $2,500 ✔, **20% consistency rule (model: none)**, payouts after earning 5% = $2,500 (**model
buffer $1,500**). The "too good" Instant figure ($102–115K) came from these two errors.
### Lucid — LucidFlex verified; LucidDaily **differs**
LucidFlex 50K (support.lucidtrading.com 12945790, 12945796): target $3,000 ✔, MLL $2,000 ✔, 40% consistency ✔, 4 / 40 contracts, 5 days of $150 ✔,
min payout $500, 50% up to $2,000 ✔, 5 payouts then live ✔, 90/10 ✔, no activation fee ✔. LucidDaily 50K (15996664, 15997266): target $3,000 ✔,
MLL $2,000 ✔, 50% consistency ✔, buffer $52,100 ✔, **no per-request cap (model $2,000)**, **min payout $500 (model none)**, an $8,000 day moves
the account live. Prices: pricing page 404 → pass 2.
### MyFundedFutures (restricted for Malaysia) — rules recorded for completeness
Rapid EOD 50K (myfundedfutures.com/plans/rapid-eod): target $3,000, EOD MLL $2,000 locking at +$100, 30% consistency (eval only), min 4 days, no
activation fee, funded buffer $2,100, min payout $500, $500 net profit since last payout, daily payouts, 90/10. Pro 50K: $159 promo / $265 list,
80/20, bi-weekly, up to $100K per payout. Builder 50K: $92 promo / $153 list, 1-day pass, $1K soft daily pause, payouts every 48 h, 80/20, one
account per user.

## 3. Prices read from official pricing pages / public checkouts (pass 2, 2026-11-22; list price / current promotion)
| product | official price | model | status |
|---|---|---|---|
| Topstep 50K Standard | $49/mo, reset $49, activation $149 | same | verified |
| Topstep 50K No-Activation | $95/mo ($85 sale), reset $85 | — | new option, priced $45,335 |
| TTP Futures Prime 50K | $99 one-time, reset $79 | same | verified |
| **TTP Futures Instant 50K** | **$499** (client-area quick checkout) | [sens] $299 / $499 | **resolved: $499 → $43,076 / $8,750 / −$11,214, not flagged** |
| Goat Funded Futures "GOAT Daily" 50K | $198 list / $89 promo, reset $90, target $3,000, EOD $2,000, 40%/50% consistency, no activation | Goat EOD [sens] $150/$250 | product renamed; re-price pending rules |
| FundedNext Futures 50K | $141.99 list / $74.99 promo, target $2,500, EOD MLL $1,500, 40% consistency, reset $82.99 | Rapid Pro 50K (other rules) | differs → re-price pending |
| Blueberry Ascent 50K | $139/mo list / $55.60 promo | check | pending |
| Funded Futures Network MAX Standard 50K | $178 list / $53.40 promo, target $3,000, EOD $2,000, 5 days | not modelled | new |
| Tradeify 50K Evaluation | $376 list / $263 promo, target $3,500, static $1,500, soft DLL $900, split 80/10/10 | Select Flex 50K (other rules) | differs → re-price pending |
| Bulenox 50K | $175 one-time, target $3,000, drawdown $2,500, no DLL | Momentum (loses) | pending |
| Top One Futures 50K | $189 list / $39 promo, EOD static, reset $35, activation $189 → $142 | not modelled (alert-assisted) | new |
| Purdia EOD 50K | $179 list / $107.40, activation $130 → $1, copy trading allowed | not modelled | new |
| Take Profit Trader 50K | $170/month; page states "No trading bots" | — | bots banned (confirms registry) |
| MFFU Builder / Rapid / Rapid EOD / Pro 50K | $153 / $209 / $275 / $265 list ($92 / $125 / $165 / $159 promo) | various | firm restricted for Malaysia |
| Alpha Standard 50K | $129/mo ($64.50 promo), reset $109 | same | firm restricted for Malaysia |
| Blue Guardian futures 50K | $209 ($146 with code) | various | firm restricted for Malaysia |
| Lucid (Flex / Daily / Direct) | **not readable**: site shows a bot-verification page to automated browsers (not circumvented) | — | only Jx can read the checkout |
| DayTraders EOD / S2F 50K | **not readable**: only the 25K EOD tab renders ($80 promo); list range EOD 25K $309 … 300K $1,599, S2F $370–$825 | [sens] | pending (product checkout pages) |

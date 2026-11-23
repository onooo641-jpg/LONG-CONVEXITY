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
| **Goat Funded Futures** | **RESTRICTED** | help.goatfundedfutures.com/en/articles/14094470-which-countries-are-restricted |
| Topstep | not on its ineligible list (list updated 2026-11-17; no Malaysia mention in 81 help articles) | help.topstep.com/en/articles/8284116 |
| Lucid Trading | not on its restricted list (2026-10-08) | support.lucidtrading.com/en/articles/11404636-restricted-countries |
| DayTraders | not on its restricted list | daytraders.com/help/articles/17704103-who-can-sign-up |
| FTMO | not on its residency-restricted list | ftmo.com/en/faq/who-can-join-ftmo/ |
| The Trading Pit, Blueberry | no Malaysia mention in 45 / 160 help articles | support.thetradingpit.com, help.blueberryfutures.com |
| FundedNext | sign-up not restricted; Malaysia is on its card-payout restriction list only | help.fundednext.com/en/articles/8020084 |
| TradeDay, Tradeify, TFD, Bulenox, Traders Launch, The5ers | help centres did not render (0–1 pages) → **not verified** | — |
**Consequence:** the multi-firm plan (Topstep + Lucid + MFFU, `docs/PREREG_PORTFOLIO2_20261120.md`) includes a firm that does not accept
Malaysian residents. The flagged FuturesElite Nitro / Elite and the near-miss Alpha Standard and Blue Guardian products are not available to a
Malaysian resident either, nor is Goat Funded Futures. (The friend's own account, on the friend's computer, depends on the friend's residence, not Jx's.)

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

### DayTraders — rules verified; bots explicitly allowed; S2F payout targets differ (no effect)
daytraders.com/help (2026-10-22): "You can use AI, scripts, bots, trade copiers and a VPS, as long as you don't trade in an HFT style".
EOD 50K: target $3,000 ✔, EOD MLL $2,000 stopping at start ✔, $1,250 daily pause (not modelled; a pause, not a breach), 10 minis / 100 micros ✔,
50% consistency in the evaluation ✔, 30% per payout cycle ✔, 8 qualifying days of $200 ✔, max $2,000 per request ✔, min balance after payout
$52,000 ✔ (buffer $2,000), 100% split ✔, $5 activation ✔. S2F 50K: MLL $2,500 ✔, 20% consistency ✔, 10 qualifying days of $200 ✔, max $2,000 ✔,
**per-cycle profit targets $3,500 / $3,000 / $2,500 (model $500)** → re-priced: unchanged ($55,274 at $199), because the 20% consistency rule
already forces larger cycles. Prices for the 50K EOD / S2F are still unreadable (only the 25K tab renders).
### Blueberry Ascent 50K — rules verified; billing differs
help.blueberryfutures.com/en/articles/12916577: target $3,000 ✔, EOD MLL $2,000 ✔, 2 minis / 20 micros ✔, reset $125 ✔, $200 qualifying days ✔,
30-day limit. **The official card shows Ascent billed per month** (25K: $139/mo, $55.60 promo); the model used a one-time $245. 50K monthly
price not rendered → not priced.

## 4. Re-pricing with official rules (`docs/jx_runs/prop_reprice_verified_20261122.txt`)
| product | before | official rules | flag rule |
|---|---|---|---|
| Topstep 50K Standard | $44,359 | $44,359 (55% combine rule has no effect) | yes |
| **Topstep 50K Consistency path** | — | **$46,492** / $18,005 / −$3,520 | yes (best Topstep option) |
| Topstep 50K No-Activation | — | $45,335 / $17,715 / −$4,270 | yes |
| TTP Futures Instant 50K | [sens] $299: $58,276 | **official $499: $43,076 / $8,750 / −$11,214** | no |
| LucidDaily 50K (no cap, min $500) | [sens] $56,774 / $40,574 | $99: $55,283 / $21,726 / −$4,356; $199: $39,083 / $4,227 / −$8,756 | only if the price is ≈ $99 |
| DayTraders S2F 50K (official targets) | [sens] $55,274 / $40,474 | unchanged | only if ≈ $199 |
| FuturesElite Instant 50K (20% consistency, $2,500 buffer) | [sens] $114,682 | $39,117 / $24,832 / −$2,786 | yes, but firm restricted for Malaysia |

## 5. Bottom line for a Malaysian account holder (so far)
Available, bots allowed, rules verified and meeting the flag rule: **Topstep 50K** (best on the Consistency path, $46,492) and **TTP Futures
Prime 50K** ($49,057). LucidFlex 50K (rules verified; price behind a bot check) and DayTraders EOD / S2F and LucidDaily (rules verified; price
unreadable) depend on prices only Jx can read at checkout. MFFU, FuturesElite, Alpha Futures, Blue Guardian Futures and Goat Funded Futures are
not available to Malaysian residents.

## 6. Products priced at checkout prices supplied by Jx (2026-11-22; source: Jx, not read by the radar)
`docs/jx_runs/prop_price_jx_20261122.txt` (identical on re-run). Rules as verified above. Resets: LucidFlex keeps the model's $90; others assume
reset = purchase price (not supplied). LucidFlex DLL is a soft pause with no published 50K amount → modelled as none (optimistic for DLL ON).
recycle.py uses closed-trade P&L, so intraday vs EOD drawdown variants of LucidDaily are not distinguished (intraday optimistic).
| product, price | real | coin flip | worst dip | flag rule |
|---|---|---|---|---|
| LucidFlex 50K DLL OFF $165 / $115.50 promo | $34,723 / $37,495 | $16,119 / $18,495 | −$5,070 / −$4,724 | yes / yes |
| LucidFlex 50K DLL ON $115 / $80.50 promo | $37,523 / $39,455 | $18,519 / $20,175 | −$4,720 / −$4,478 | yes / yes |
| LucidDaily 50K EOD eval $122 / $85.40 promo | $51,557 / $57,486 | $17,739 / $24,093 | −$5,368 / −$3,758 | no (dip by $88) / **yes** |
| LucidDaily 50K Intraday eval $94 / $65.80 promo | $56,093 / $60,661 | $22,594 / $27,487 | −$4,136 / −$2,895 | yes / yes (optimistic) |
| LucidDaily 50K EOD funded $236 / $165.20 promo | $33,089 / $44,558 | −$2,140 / $10,241 | −$10,384 / −$7,269 | no / no |
| **DayTraders EOD 50K $105 + $5 activation** | **$47,894** | $12,461 | −$3,265 | **yes** |
| DayTraders S2F 50K $570 / $342 promo | $27,820 / $44,692 | −$8,565 / $15,893 | −$17,360 / −$7,524 | no / no |
| Blueberry Prime 2-Step / Classic / Flex / Instant Lite | — | — | — | not priced: these plans are not on the futures help centre (they look like Blueberry's CFD plans); rules needed |

## 7. Frozen 50K baseline (Jx, 2026-11-22)
Inputs live in **`docs/radar/prop_assumptions_20261122.csv`** (promotions and rule changes go there; the script does not change):
`scripts/prop_baseline_20261122.py` → `docs/jx_runs/prop_baseline_20261122.txt` (identical on re-run). Modelling choices preserved from Jx:
LucidFlex 40% evaluation consistency, no time limit, reset separate from purchase (50% add-on not assumed to survive a reset); DayTraders failed
evaluation = replacement purchase at $105, $5 activation only on a pass; Blueberry subscription months, evaluation resets and funded resets
kept separate, with the 30-day expiry run as variants. Soft DLLs stop the day at the limit (one trade per day in this data).
| product | real net | per year | coin flip | worst dip | flag rule |
|---|---|---|---|---|---|
| LucidFlex 50K DLL ON ($80.50, reset $80, soft DLL $1,200) | $40,545 | $3,744 | $21,522 (99%) | −$4,108 | yes |
| LucidFlex 50K DLL OFF ($115.50, reset $115) | $34,770 | $3,211 | $15,201 (94%) | −$5,648 | no (dip by $368) |
| DayTraders EOD 50K ($105 + $5 on pass, replacement $105, soft DLL $1,250) | $47,894 | $4,422 | $12,461 (88%) | −$3,265 | yes |
| Blueberry Ascent 50K ($98/mo; expiry → $125 reset; no funded reset) | $30,747 | $2,839 | $3,395 (62%) | −$6,086 | no |
| Blueberry Ascent 50K (… $500 funded resets used) | $51,229 | $4,730 | $9,707 (72%) | −$10,666 | no (dip) |
| Blueberry Ascent 50K (context: no 30-day limit) | $30,099 | $2,779 | $8,791 (82%) | −$4,410 | yes |
Caveat (repo convention, as for Topstep): monthly subscriptions are charged for every month of the 2016–26 span, including while funded.
Malaysia eligibility per Jx: TradeDay, Traders Launch, Take Profit Trader (bots banned) eligible; Bulenox provisional; **Tradeify restricted**;
The Futures Desk unverified (excluded until support confirms). Registry updated.

## 8. Manual-entry firms that accept Malaysia (pass 4 crawl, 2026-11-23; `docs/jx_runs/manual_my_20261123.txt`, identical on re-run)
Malaysia: **FundedNext Futures RESTRICTED** (helpfutures.fundednext.com/en/articles/17228971); **AquaFunded**: Instant Funding only, max $50K
per trader (help.aquafunded.com/en/articles/9251052); **Top One**: not on its restricted list (11021644), bots banned (10907920); YLOS: no
restriction found (help centre mostly Portuguese, rules incomplete); Take Profit Trader, Purdia, Phidias, Hola Prime, The5ers help centres did
not render → not priced.
**Top One Elite ACCESS 50K** (official): $189 ($39 promo), target $3,000 in 30 days, no evaluation consistency, EOD trailing $2,000 locking at
+$100, activation $189 ($142 promo), evaluation reset $35, funded reset $499, funded: 5 days ≥ $250, 40% consistency per cycle, $2,000 buffer,
$2,500 profit before a payout, $500–$1,500 per request, 90% split, 50% of each later payout from new profit.
| Manual entry, 3-minute delay (vs Topstep 3-min $37,348) | real | coin flip | worst dip | qualifies |
|---|---|---|---|---|
| Top One Elite ACCESS 50K at $189 list | $15,459 | −$61 | −$4,609 | no |
| Top One Elite ACCESS 50K at $39 promo | $21,566 | $5,436 | −$3,427 | yes (barely) |
| LucidDaily 50K EOD $85.40 (manual) | $48,761 | $18,582 | −$2,818 | yes |
| DayTraders EOD 50K $105 (manual) | $41,112 | $9,250 | −$3,083 | yes |
| LucidFlex 50K DLL ON $80.50 (manual) | $40,494 | $16,365 | −$3,228 | yes |
| Topstep 50K Consistency (manual) | $39,978 | $13,795 | −$3,094 | yes |
| TTP Futures Prime 50K (manual) | $35,554 | $13,397 | −$4,070 | yes |

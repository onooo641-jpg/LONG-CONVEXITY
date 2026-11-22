# Prop-firm products compared with Topstep 50K — 2026-11-22

Friend's NQ trades 2016-01..2026-10 through `backtest/recycle.py`. Source: `docs/jx_runs/salewindow_20261122.txt` (0% column; identical on re-run).
Benchmark Topstep 50K: real $44,359 ($4,097/yr, $341/month), coin flip $18,046, worst dip −$3,520. Manual-entry products (delay 3) carry a
3-minute entry delay and are compared with Topstep at 3 minutes ($37,348). **Flag** = real ≥ 50% of Topstep, coin flip ≥ $5,000, worst dip no
worse than 1.5× Topstep's. `[sens]` = price unreadable (script-loaded checkout), shown at a low and a high bracket; never flagged on its own.
"Flags at 40% off" = meets the flag rule if bought with a 40% code (resets discounted too: optimistic).

| # | product | entry | real net 2016–26 | per year | per month | vs Topstep | coin flip | worst dip | meets flag rule at this price | at 40% off |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | FuturesElite Instant 50K $199 [sens] | manual (3-min) | $114,682 | $10,589 | $882 | 307% | $82,570 | $-1,393 | **yes** | yes |
| 2 | FuturesElite Instant 50K $349 [sens] | manual (3-min) | $102,382 | $9,454 | $788 | 274% | $67,295 | $-2,443 | **yes** | yes |
| 3 | Blue Guardian Direct 50K $299 [sens] | manual (3-min) | $62,773 | $5,796 | $483 | 168% | $51,438 | $-4,772 | – | yes |
| 4 | TTP Instant 50K $299 [sens] | bot | $58,276 | $5,381 | $448 | 131% | $32,076 | $-4,485 | **yes** | yes |
| 5 | LucidDaily 50K $99 [sens] | bot | $56,774 | $5,242 | $437 | 128% | $23,037 | $-4,356 | **yes** | yes |
| 6 | DayTraders S2F 50K $199 [sens] | bot | $55,274 | $5,104 | $425 | 125% | $31,518 | $-4,378 | **yes** | yes |
| 7 | FuturesElite Prime 50K $129 [sens] | manual (3-min) | $52,176 | $4,818 | $401 | 140% | $11,247 | $-3,697 | **yes** | yes |
| 8 | FuturesElite Prime 50K $229 [sens] | manual (3-min) | $49,076 | $4,531 | $378 | 131% | $7,623 | $-4,197 | **yes** | yes |
| 9 | TTP Prime 50K, reset $79 | bot | $49,057 | $4,530 | $377 | 111% | $16,960 | $-3,884 | **yes** | yes |
| 10 | DayTraders EOD 50K, $99 [sens] | bot | $48,602 | $4,488 | $374 | 110% | $13,511 | $-3,079 | **yes** | yes |
| 11 | FuturesElite Nitro 50K ($152) | manual (3-min) | $48,463 | $4,475 | $373 | 130% | $15,373 | $-4,331 | **yes** | yes |
| 12 | Blue Guardian Direct 50K $499 [sens] | manual (3-min) | $48,173 | $4,448 | $371 | 129% | $26,832 | $-10,568 | – | – |
| 13 | TTP Futures Prime 50K ($99) | bot | $46,597 | $4,303 | $358 | 105% | $14,016 | $-4,884 | **yes** | yes |
| 14 | Topstep 50K | bot | $44,359 | $4,096 | $341 | 100% | $18,046 | $-3,520 | **yes** | yes |
| 15 | Blue Guardian Elite 50K, price $141 [sens] | manual (3-min) | $43,877 | $4,051 | $338 | 117% | $6,442 | $-4,653 | – | yes |
| 16 | TTP Futures Prime 150K ($289) | bot | $43,662 | $4,032 | $336 | 98% | $-6,562 | $-19,074 | – | – |
| 17 | TTP Instant 50K $499 [sens] | bot | $43,076 | $3,977 | $331 | 97% | $8,750 | $-11,214 | – | yes |
| 18 | LucidDirect 50K $299 [sens] | bot | $42,064 | $3,884 | $324 | 95% | $17,660 | $-5,669 | – | yes |
| 19 | Blue Guardian Reserve 50K $150 [sens] | manual (3-min) | $41,251 | $3,809 | $317 | 110% | $9,206 | $-4,515 | **yes** | yes |
| 20 | LucidDaily 50K $199 [sens] | bot | $40,574 | $3,746 | $312 | 91% | $5,432 | $-8,756 | – | yes |
| 21 | DayTraders S2F 50K $399 [sens] | bot | $40,474 | $3,737 | $311 | 91% | $9,708 | $-9,556 | – | yes |
| 22 | Alpha Futures Standard 50K | manual (3-min) | $40,155 | $3,708 | $309 | 108% | $8,998 | $-4,773 | – | yes |
| 23 | Alpha Standard 100K ($239/mo) | manual (3-min) | $38,038 | $3,512 | $293 | 102% | $-998 | $-9,918 | – | – |
| 24 | LucidFlex 50K | bot | $37,523 | $3,465 | $289 | 85% | $18,519 | $-4,720 | **yes** | yes |
| 25 | Blue Guardian Elite 50K, price $350 [sens] | manual (3-min) | $37,398 | $3,453 | $288 | 100% | $-1,457 | $-5,698 | – | yes |
| 26 | DayTraders EOD 50K, $199 [sens] | bot | $36,802 | $3,398 | $283 | 83% | $-4,406 | $-6,989 | – | yes |
| 27 | MFFU Pro 50K $127 [sens] | bot | $35,980 | $3,322 | $277 | 81% | $9,016 | $-4,064 | **yes** | yes |
| 28 | TradeDay $85 (code) | bot | $35,678 | $3,294 | $274 | 80% | $14,035 | $-4,835 | **yes** | yes |
| 29 | MFFU Rapid EOD 50K | bot | $34,481 | $3,184 | $265 | 78% | $7,358 | $-5,590 | – | yes |
| 30 | FTMO Futures Growth 50K | bot | $34,236 | $3,161 | $263 | 77% | $1,906 | $-9,675 | – | – |
| 31 | FuturesElite Elite 50K | manual (3-min) | $33,645 | $3,107 | $259 | 90% | $9,121 | $-2,014 | **yes** | yes |
| 32 | Tradeify Select Flex 50K | bot | $32,900 | $3,038 | $253 | 74% | $11,110 | $-7,261 | – | yes |
| 33 | MFFU Builder 50K ($107 code) [sens] | bot | $32,453 | $2,997 | $250 | 73% | $9,759 | $-4,708 | **yes** | yes |
| 34 | TTP Prime 100K ($189) | bot | $30,418 | $2,809 | $234 | 69% | $-3,408 | $-12,474 | – | – |
| 35 | Blue Guardian Reserve 50K $250 [sens] | manual (3-min) | $29,651 | $2,738 | $228 | 79% | $-4,756 | $-7,525 | – | yes |
| 36 | LucidDirect 50K $499 [sens] | bot | $29,264 | $2,702 | $225 | 66% | $-2,806 | $-11,869 | – | – |
| 37 | Goat EOD 50K $150 [sens] | bot | $27,838 | $2,570 | $214 | 63% | $737 | $-7,500 | – | yes |
| 38 | FTMO Futures Pro 50K | bot | $27,428 | $2,533 | $211 | 62% | $1,810 | $-9,181 | – | – |
| 39 | Goat 1-Day Pass 100K ($358) | bot | $26,342 | $2,432 | $203 | 59% | $-26,251 | $-19,366 | – | – |
| 40 | MFFU Builder 50K ($153) | bot | $25,323 | $2,338 | $195 | 57% | $2,022 | $-6,732 | – | yes |
| 41 | Goat Flex 50K | bot | $23,784 | $2,196 | $183 | 54% | $-3,419 | $-6,322 | – | yes |
| 42 | MFFU Pro 50K One-Day $127 [sens] | bot | $23,584 | $2,178 | $181 | 53% | $1,811 | $-4,191 | – | yes |
| 43 | Blueberry Ascent 50K | bot | $23,397 | $2,160 | $180 | 53% | $-4,016 | $-10,982 | – | yes |
| 44 | Goat 1-Day Pass 50K ($218) | bot | $22,227 | $2,052 | $171 | 50% | $-7,651 | $-10,338 | – | – |
| 45 | Alpha Direct 50K ($519) | manual (3-min) | $22,197 | $2,050 | $171 | 59% | $-4,548 | $-12,732 | – | – |
| 46 | TradeDay $189 | bot | $22,158 | $2,046 | $170 | 50% | $-4,213 | $-10,035 | – | – |
| 47 | MFFU Pro 50K $227 [sens] | bot | $21,680 | $2,002 | $167 | 49% | $-6,593 | $-7,272 | – | yes |
| 48 | TFD Static Pro | bot | $20,248 | $1,870 | $156 | 46% | $3,274 | $-3,667 | – | yes |
| 49 | Alpha Advanced 50K ($209/mo) | manual (3-min) | $17,903 | $1,653 | $138 | 48% | $-11,782 | $-8,907 | – | – |
| 50 | Goat EOD 50K $250 [sens] | bot | $16,838 | $1,555 | $130 | 38% | $-15,553 | $-13,216 | – | – |
| 51 | MFFU Studio #002 $20K ($280) | bot | $15,602 | $1,441 | $120 | 35% | $-3,770 | $-7,098 | – | yes |
| 52 | FundedNext Rapid Pro 50K | bot | $14,482 | $1,337 | $111 | 33% | $-608 | $-7,040 | – | yes |
| 53 | TFD Static Core | bot | $10,680 | $986 | $82 | 24% | $-1,163 | $-3,226 | – | – |
| 54 | MFFU Pro 50K One-Day $227 [sens] | bot | $10,284 | $950 | $79 | 23% | $-12,840 | $-9,781 | – | – |
| 55 | MFFU Studio #001 $10K ($140) | bot | $7,551 | $697 | $58 | 17% | $-2,528 | $-3,696 | – | – |
| 56 | Alpha Direct 25K ($349) | manual (3-min) | $7,034 | $649 | $54 | 19% | $-10,058 | $-8,872 | – | – |
| 57 | Alpha Zero 100K ($279/mo) | manual (3-min) | $6,022 | $556 | $46 | 16% | $-20,223 | $-14,155 | – | – |
| 58 | Traders Launch 200K ($299) | bot | $4,371 | $404 | $34 | 10% | $-24,351 | $-15,606 | – | – |
| 59 | MFFU Studio #003 $5K ($75) | bot | $3,249 | $300 | $25 | 7% | $-1,775 | $-1,980 | – | – |
| 60 | Traders Launch 100K ($159) | bot | $722 | $67 | $6 | 2% | $-13,645 | $-8,817 | – | – |
| 61 | Alpha Zero 50K ($169/mo) | manual (3-min) | $-440 | $-41 | $-3 | -1% | $-12,032 | $-12,080 | – | – |
| 62 | Bulenox Momentum 50K | bot | $-4,139 | $-382 | $-32 | -9% | $-14,622 | $-10,840 | – | – |

## Not priced (and why)

| firm | automation (written rules) | reason |
|---|---|---|
| Apex Trader Funding  | unclear | bot policy or rules unreadable |
| Phidias  | alert_assisted | manual entry allowed; rules unreadable (script-loaded pages) |
| Take Profit Trader  | banned_full_bots | bots banned by its rules → would need manual entry; rules not modelled |
| Earn2Trade  | banned_full_bots | bots banned by its rules → would need manual entry; rules not modelled |
| Top One Futures  | alert_assisted | manual entry allowed; rules unreadable (script-loaded pages) |
| Funded Futures Family  | banned_full_bots | bots banned by its rules → would need manual entry; rules not modelled |
| Elite Trader Funding  | banned_full_bots | bots banned by its rules → would need manual entry; rules not modelled |
| FXIFY Futures  | banned_full_bots | bots banned by its rules → would need manual entry; rules not modelled |
| HyroTrader (crypto only) | full_bots | crypto-only: needs a crypto strategy (parked #299) |
| Maven Trading (CFD) | banned_full_bots | bots banned by its rules → would need manual entry; rules not modelled |
| Lux Trading Firm (CFD) | banned_full_bots | bots banned by its rules → would need manual entry; rules not modelled |
| Audacity Capital (CFD) | full_bots | CFD firm: being priced in #296 (official pages fetching) |
| Alpha Capital Group (CFD) | full_bots | CFD firm: being priced in #296 (official pages fetching) |
| Goat Funded Trader (CFD) | full_bots | CFD firm: being priced in #296 (official pages fetching) |
| BluSky Trading Company  | full_bots | bots allowed; rules unreadable so far |
| DayTraders  | full_bots | priced above under its products (EOD, S2F) |
| Funded Futures Network  | full_bots | bots allowed; rules unreadable so far |
| IQ Capital  | full_bots_conditional | bots allowed with conditions; rules unreadable |
| Finotive Futures  | full_bots | bots allowed; rules unreadable so far |
| Purdia Capital  | alert_assisted | manual entry allowed; rules unreadable (script-loaded pages) |
| AquaFunded Futures  | alert_assisted | manual entry allowed; rules unreadable (script-loaded pages) |
| Hola Prime Futures  | alert_assisted | manual entry allowed; rules unreadable (script-loaded pages) |
| YLOS Trading  | alert_assisted | manual entry allowed; rules unreadable (script-loaded pages) |
| The5ers Futures  | alert_assisted | manual entry allowed; rules unreadable (script-loaded pages) |
| Trade The Pool  | unclear | bot policy or rules unreadable |
| NexGen ProTrader Funding  | unclear | bot policy or rules unreadable |
| Legends Trading  | unclear | bot policy or rules unreadable |
| E8 Futures  | unclear | bot policy or rules unreadable |
| BrightFunded Futures  | unclear | bot policy or rules unreadable |

Also being priced in #296 (CFD accounts with bots allowed): FTMO, FundedNext, The5ers, Alpha Capital, Goat Funded Trader, Audacity.

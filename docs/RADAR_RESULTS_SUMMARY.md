# Radar results summary (workstream C), as of 2026-11-22

One place for every structural idea tested by the radar workstream and every prop-firm product priced. Details, rules and raw outputs: the
PREREG file named in each row, `docs/CANDIDATES.md` (#200–#278), `docs/FIGURES_LEDGER.md`, `docs/jx_runs/`. All tests were pre-registered;
re-runs identical. Bars: non-prop ≥ 8%/yr on capital in both halves (week-1 incentive tests 12%); prop "extra slot" = real net ≥ 50% of
Topstep 50K, coin-flip median ≥ $5,000, worst dip no worse than 1.5× Topstep's (3-min-delay products compared with Topstep at 3 min).
Benchmark: Topstep 50K $44,359 real / $18,046 coin flip (98%) / −$3,520 dip (2016-01..2026-10).

## A. Prop-firm products (friend's NQ trades, recycle.py)
**Flagged on registered rules and price**
| # | product | entry | real net | coin flip (profitable) | worst dip | notes |
|---|---|---|---|---|---|---|
| 237 | **The Trading Pit Futures Prime 50K** ($99, reset $79 — own page) | bot | **$49,057** | $16,960 (97%) | −$3,884 | bots allowed, Malaysia OK, free L1 data; fails if price ≥ ~$149 |
| 251 | FuturesElite Nitro 50K ($152 directory) | manual 3-min | $48,463 | $15,373 (94%) | −$4,331 | funded drawdown intraday, modelled EOD (optimistic) |
| 206 | FuturesElite Elite 50K ($128 directory, reset $89 own) | manual 3-min | $33,645 | $9,121 (91%) | −$2,014 | purchase price unconfirmed |
| — | LucidFlex 50K / TradeDay $85 (from earlier work) | bot | $37,523 / $35,678 | $18,519 / $14,035 | −$4,720 / −$4,835 | already in the plan / TradeDay needs a platform rewrite |

**Would flag only if the unreadable price is near the low bracket (sensitivity, not ranked)**
| # | product | low price → real / coin flip | high price → real / coin flip |
|---|---|---|---|
| 236 | DayTraders EOD 50K (bots) | $99 → $48,602 / $13,511 | $199 → $36,802 / −$4,406 |
| 244 | DayTraders S2F 50K (bots) | $199 → $55,274 / $31,518 | $399 → $40,474 / $9,708 |
| 240 | LucidDaily 50K EOD (bots) | $99 → $56,774 / $23,037 | $199 → $40,574 / $5,432 |
| 239 | TTP Futures Instant 50K (bots) | $299 → $58,276 / $32,076 | $499 → $43,076 / $8,750 |
| 242 | MFFU Pro 50K (bots) | $127 → $35,980 / $9,016 | $227 → fails |
| 231 | MFFU Builder 50K (bots, new plan) | $107 code → $32,453 / $9,759 | $153 list → $25,323 / $2,022 |
| 250 | FuturesElite Prime 50K (manual) | $129 → $52,176 / $11,247 | $229 → $49,076 / $7,623 |
| 252 | FuturesElite Instant 50K (manual) | $199 → $114,682 / $82,570 | $349 → $102,382 / $67,295 (looks too good: verify) |
| 253 | Blue Guardian Reserve 50K (manual) | $150 → $41,251 / $9,206 | $250 → fails |
| — | Blue Guardian Elite 50K (manual) | $141 → $43,877 / $6,442 | $350 → fails |
| 254 | Blue Guardian Direct 50K (manual) | $299 → $62,773 / $51,438 (dip misses by $131) | $499 → $48,173 / $26,832 |

**Not flagged:** Alpha Futures Standard 50K (manual, $40,155 / $8,998, dip misses by $132), MFFU Rapid EOD ($34,481 / $7,358), FTMO Growth / Pro,
TFD Static Core / Pro, TradeDay $189, Bulenox (loses), Goat Flex / 1-Day 50K & 100K / EOD, Blueberry Ascent, MFFU Studio #001–#003, MFFU Pro One-Day,
Traders Launch 100K / 200K, TTP Prime 100K / 150K, Alpha Zero / Advanced / Direct / Standard 100K / Zero 100K / Direct 25K, LucidDirect.
**Not priced (rules or bot policy unreadable):** Apex, Take Profit Trader, Phidias, Top One, E8 (no bot policy), Earn2Trade, FFF, ETF, FXIFY, FundedNext
(terms now restrict bots), BluSky, Funded Futures Network, Finotive, AquaFunded, Purdia, YLOS, Hola Prime, The5ers Futures, IQ Capital, Trade The Pool.
Per-month view (`docs/jx_runs/radar_monthly_20261121.txt`): Topstep $341/month average 2016–26, payouts in ~1 month in 5.

## B. Non-prop structural mechanisms (47 tested) — no robust pass
| # | mechanism | verdict |
|---|---|---|
| 201–203 | stablecoin incentive pools (Lista, Dolomite, Bluefin) | FAIL (Bluefin near-miss: loss proxy) |
| 204 | monthly rotation into top stable yields | FAIL (collapses) |
| 205 | Hyperliquid HLP vault | FAIL near-miss (27.7% → 7.9%) |
| 207 | new reward programmes, first 30 days | FAIL |
| 208 | cross-venue funding gaps (HL/dYdX/Aevo) | **PASS after fee-bug fix: 20.3% / 11.9%** (fragile: fails at 2× fees, needs Aevo; execution costs not modelled) |
| 209 | paid-to-borrow stable loops | ceiling 11.4%; not testable (borrow history paywalled) |
| 210 | ten named stable programmes (sUSDe, bUSD0, sUSDf, Sky, Spark, Maple, Pendle, Liquity, Felix, HL Earn) | FAIL (3–5% now) |
| 211 | Pendle PTs to maturity incl. expired | FAIL (depegs) |
| 212–213 | hedged staking / hedged farming | FAIL |
| 214 | hedged governance-token yields (CRV wrappers) | FAIL (wrappers −40–60% vs CRV) |
| 216 | gold carry (PAXG + short) | FAIL |
| 217 | best-venue funding carry | KILL at ceiling |
| 219 | correlated-pair loops (LST/ETH, sUSDe/USDC) | KILL at ceiling (6.8%) |
| 220, 223 | JLP, Lighter LLP | not testable |
| 221 | hedged GMX GM pools | FAIL with real token prices |
| 222 | dYdX MegaVault | FAIL (history too short) |
| 224, 227 | stable-pair LPs, other savings rates | FAIL |
| 225 | Gains trader-counterparty vaults | FAIL on primary rule (equal weight 10.7% / 13.2%, tiny capacity) |
| 228 | hedged TRX energy / SKY staking | TRX KILL; SKY 12.9% / 16.9% on 112 days → re-test ≈ 2027-01-07 |
| 229 | hedged native L1 staking | ATOM KILL; INJ ceiling 12.1%, not testable |
| 230 | stability pools (Liquity v2) | FAIL (pool ~$3.6K) |
| 259–278 | batch 6 (zero-fee venues, real-yield staking, tranches, insurance funds, bribes, veAERO, RWA, fixed-rate auctions, CME basis, tokenised stocks, LST unstake, hedged LP, relayers, HYPE staking, reverse carry, new-chain incentives) | #276 hedged HYPE staking narrow pass, not robust; rest FAIL / KILL / not testable |
Earlier non-prop tests (#29–#59, #100) are in `docs/HANDOFF_NONPROP.md`. Mechanism list with desk checks: `docs/IDEAS_SWEEP_20261121.md`.

## B2. Refinement (configuration changes; year-1 design, year-2 test; `docs/PREREG_REFINE_20261122.md`)
PASS: R1 funding gaps with maker fees (24.9% / 17.1%), R5 hedged HYPE staking (23.4% / 9.3%, marginal), R6 Gains vaults equal weight (11.6% / 9.8%,
small capacity, gToken price check pending). FAIL with every configuration: R2 GM pools, R3 stable-yield selection, R4 new rewards, R7 conditional carry.

## C. Open items
1. Confirm prices (script-loaded, unreadable by the crawler): DayTraders EOD / S2F 50K, LucidDaily 50K, TTP Futures Instant 50K, FuturesElite
   Prime / Instant / Nitro / Elite 50K, MFFU Pro 50K, Blue Guardian Reserve / Direct 50K.
2. Scheduled: weekly radar review (Saturdays 12:23 MYT); near-miss re-test #228 SKY (2027-01-08).

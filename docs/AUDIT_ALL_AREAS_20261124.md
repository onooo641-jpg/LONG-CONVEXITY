# Coverage audit: every area for a small player, what was done, what is left — 2026-11-24

Jx asked for a last, in-depth audit across all areas "in case you miss them", then to actually try what is left. Method: list every
mechanism family by **who pays** (the only sources of > 10%/yr returns found so far: someone else's subsidy, a skill/engineering edge, a
capped or one-off dislocation, or risk premia), map every test in `docs/CANDIDATES.md`, every radar source, every exclusion, and mark gaps.
"Configs" = whether variants were tried beyond one base implementation (refinement studies R1–R7 and the 16-idea walk-forward retest with
12–270 configurations each, `docs/PREREG_REFINE_20261122.md`, NOTES_NONPROP 2026-11-22).

## A. Someone else's subsidy, customer side (the prop-firm shape: capped loss, others pay)
| Family | Tests | Configs | Radar | Verdict |
|---|---|---|---|---|
| Futures/CFD prop evaluations | #1–#65, firm scans (Topstep, Lucid, MFFU, TTP, DayTraders, TradeDay, FTMO, FundedNext, Breakout…), #296 CFD, #298 sale windows | yes (strategy layer, firm rules, sizes, mixes, staggering, manual entry) | ~120 firm pages daily | **WORKS (backtest): ~$18K/yr Malaysia portfolio** |
| Prop competitions | #297 | — | firm pages | not testable (winners' returns unpublished) |
| Broker deposit/credit bonuses | early loophole tests | — | — | FAIL |
| CEX launchpools / exchange competitions | — | — | — | excluded (Binance/Bybit/OKX not allowed in Malaysia) |
| Malaysian broker/exchange sign-up promos | radar review #1 | — | N8 (moomoo, Webull, Rakuten Trade, HATA) | small one-offs (RM60-class) |
| Government matches, fixed-price funds | #50 i-Saraan / ASM | — | — | PASS but tiny (RM500/yr, 90% locked) |
| Tax reliefs (PRS RM3,000; SSPN RM8,000 with children) | this audit (desk) | — | — | worth ~RM570–750/yr in tax for PRS: personal finance, not a strategy |
| Bursa IPO ballots | #49 | post-hoc variants shown | — | FAIL |

## B. Someone else's subsidy, protocol side (incentives / emissions)
| Family | Tests | Configs | Radar | Verdict |
|---|---|---|---|---|
| Stablecoin yields, reward programmes, Merkl | #201–#207, #210, #224, #227, #278, Merkl | yes (R3/R4, walk-forward) | S1, S3, N5 (23 forums) | FAIL (3–5% market-wide; selection picks blow-ups) |
| Pendle, wrappers, bribes, tranches, new chains | #211, #214, #267, sweep 3/4 | yes (#211 all 344 markets) | S1–S4 | FAIL |
| Points / airdrops | #360 | — | indirect (forums, volume surges) | not measurable (allocation bases unpublished); sybil farming excluded |
| New protocols | radar S2 | — | S2 daily | leads only |

## C. The "house" side of losing traders
| Family | Tests | Configs | Radar | Verdict |
|---|---|---|---|---|
| Perp-DEX LP vaults (HLP, Gains, GMX, JLP, user vaults) | HLP, #225, #221, #363, #288 | yes (R6, walk-forward, hedge variants) | S1 | FAIL (open to unlimited capital → 4–10%; JLP 71% in 2024 → 8% in 2026) |
| Option / counterparty vaults | #324 | — | — | open (needs share prices) |
| Liquidation bonuses | #100 (workstream B) | shadow test | B's own jobs | pros take 75%+; shadow verdict 2026-12-19 |

## D. Skill / engineering roles paid by protocols ("bot roles")
| Family | Tests | Radar | Verdict |
|---|---|---|---|
| CoW solving | #361, #364–#368 | N3 newcomers, N9 docs, CoW forum | passes all free checks; small teams earn $23K–$386K/yr (#367); test access paused by CoW; parked as a startup-sized project |
| Across relaying | #362 | N9 docs | KILL (6th relayer $8.8K/yr) |
| UniswapX filling | **#371 (this audit)** | N9 docs | measuring |
| 1inch Fusion resolving | desk (this audit) | N9 docs | FAIL Stage 0: max 10 whitelisted, ranked by large 1INCH stakes, KYC |
| deBridge DLN takers | desk (this audit) | — | dismissed: ~4 bps taker incentive, same economics as Across (#362) |
| Drift keepers / fillers | desk (this audit) | N9 maker page | dismissed: reward = lesser of 10% of fee and a time-based amount (cents per fill), speed race; liquidations are workstream B |
| MEV backrunning / atomic arbitrage | #36 desk | — | dismissed: latency race won by specialist searchers |
| Market-making programmes / maker rebates | #322, radar review #1 | N9 (6 perp venues) | FAIL (thin-venue MM lost; rebates 0.25 bps or volume-share tiers) |
| Audit contests | #369 | N4 (Sherlock, Cantina APIs; Code4rena, Immunefi pages) | KILL (AI-crowded: ~$85 prize per submission in 2026) |
| Oracle / validator / DePIN node operation | research report | — | permissioned or low-yield (research report) |

## E. Arbitrage and dislocations
| Family | Tests | Configs | Radar | Verdict |
|---|---|---|---|---|
| Cross-venue funding gaps | #208, #280, #323 | yes (R1, walk-forward) | N2 extreme funding | FAIL at execution (23–55 bps per side vs 2.5-bps budget) |
| Basis / cash-and-carry | #271, #281 | — | — | FAIL (2.6%) |
| Stablecoin depegs | radar review #1 | — | N1 daily | no retail 1:1 redemption on current depegs |
| Index adds/deletes, listings, buybacks, unlocks, tokenised gold | #303, #334, #335, #337, #339 | variants | — | FAIL (#303 look-ahead) |
| MYR crypto price gaps | #51 | — | — | negative/tiny |
| Merger arb, closed-end discounts, odd-lot tenders | #326 parked | — | — | parked (SEC data needs a contact e-mail per request); typical returns 5–10%/yr, not prop-like |
| Leveraged-ETF decay (short pairs) | desk (this audit) | — | — | dismissed: gross profit, borrowing fees remove most of it (academic and practitioner sources) |

## F. Risk premia and general trading
| Family | Tests | Configs | Verdict |
|---|---|---|---|
| Friend's NQ strategy and variants | #1–#65 | many | loses on own capital; profit comes from prop rules |
| Calendar drifts (overnight, pre-FOMC) | #29–#31 | — | FAIL |
| Futures trend, carry, value, skew, momentum | #350–#354, #351b | grid + walk-forward | #351 passes on paper (20.7%/yr) but needs ~$250K+ |
| VIX roll, FX carry, option selling, risk parity | early batches, #282 | some | 5–15%/yr or worse |
| Stock-perp and index-perp carry, hedged staking | #300, #314, #276 | walk-forward | FAIL |
| **Crypto perp trend + cross-sectional momentum** | **#370 (this audit)** | 52 configs + walk-forward | testing — the one big trading family never tested |

## G. Excluded by Jx's rules or the law (not gaps)
Prediction markets and betting (Malaysian gambling law); multi-account / sybil farming and rule or bot-detection evasion; geoblock
circumvention; creativity/marketing businesses (YouTube, homestay, e-commerce, running a prop firm — the last is where the "90% fail"
money lands in bulk, Jx's decision); Malaysian bank / e-wallet sign-up promos (one-off, small).

## Gaps found by this audit and what was done
1. **Crypto trend / momentum** — #370 pre-registered and fetched (every Binance USDT perp ever listed, 2020–26; 52 configs; walk-forward).
2. **UniswapX fillers** — #371 pre-registered and fetched (Arbitrum + Base fills, 12 months).
3. 1inch resolvers, deBridge takers, Drift keepers, leveraged-ETF decay, tax reliefs — desk-checked above (all dismissed with reasons).
4. Still open by data: points/airdrops (no free allocation data), option vaults #324 (share prices), merger arb / odd-lot (SEC contact
   requirement), prop competitions #297 (winners unpublished).

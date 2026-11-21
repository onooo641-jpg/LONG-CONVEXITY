# Mechanism sweep: every structural edge type I could list, Stage-0 desk check (2026-11-21, workstream C)

Why a mechanism list: the radar screened ~16,000 pools/campaigns/protocols, but they reduce to a handful of **mechanisms** (a deposit
earning a reward is one mechanism whether there are 10 or 10,000 pools). New strategies come from new mechanisms, so this lists every
mechanism I could find and desk-checks each (CLAUDE.md "Stage 0": rules, Malaysia, five-part filter, data — minutes each).
Filter: F1 repeatable, F2 long-lived, F3 one reusable setup, F4 capped downside, F5 scales by copies. MY = Malaysia access.

| # | mechanism (who pays) | F1–F5 | MY | data from US runners | status |
|---|---|---|---|---|---|
| M1 | Prop-firm evaluation recycling (failed-fee pool) | pass | ok (Topstep in use) | yes | **the benchmark; FuturesElite/Alpha added as manual-entry slots (#206, #200)** |
| M2 | Stablecoin deposit incentives (protocol emissions) | pass | unverified-onchain | yes | tested #201–#204, #207, #210: FAIL (3–5%/yr now; high APRs precede collapses) |
| M3 | Paid to borrow (borrow rewards > interest), same-asset loop | pass | unverified-onchain | yes | **#209 data fetching** |
| M4 | Cross-venue funding difference, delta-neutral | pass | DeFi only | yes (dYdX, Aevo) | **#208 data fetching** |
| M5 | Single-venue funding carry (spot long, perp short) | pass | DeFi ok | yes | #57 FAIL (2.9–6.4%) |
| M6 | Protocol market-making vault (Hyperliquid HLP) | pass | unverified | yes | #205 FAIL near-miss (27.7% → 7.9%, falling) |
| M7 | Stability pools (liquidation gains to depositors) | pass | unverified | partial (DefiLlama shows 0%) | #210: data gap; needs on-chain liquidation-gain data → queued |
| M8 | Lending liquidation bonus (bots) | pass | unverified | yes | #100 workstream B (shadow test; GO unlikely per replay) |
| M9 | Keeper / auction / redemption bounties (bots) | pass | unverified | on-chain only | mostly liquidation variants (B); non-liquidation bounties (e.g. redemption arbitrage) queued as on-chain scan |
| M10 | Solver/filler rewards (CoW, UniswapX, 1inch Fusion) | pass | unverified | partial | Stage 0 FAIL F4/F5: needs bonded capital + professional infra; winners concentrated |
| M11 | Oracle-update / price-push incentives (Pyth Express Relay etc.) | pass | unverified | no | Stage 0: auction among searchers = M8-like competition; parked |
| M12 | Dated-futures cash-and-carry basis (Deribit, CME) | pass | **grey** (Deribit not SC-registered); CME via broker ok but capital-heavy | Deribit yes | Malaysia gate fails for Deribit; CME micro basis ≈ T-bill + 1–3% (capital-heavy) → not tested |
| M13 | New-perp funding spikes | pass | DeFi ok | yes | #37 FAIL |
| M14 | Post-listing shorts | — | — | yes | #44 FAIL |
| M15 | Airdrop / points farming | F1/F2 fail | varies | no history | screened out (Jx filter) |
| M16 | CEX launchpools / earn promos (Binance, Bybit, OKX) | pass | **grey** (SC orders vs Binance/Bybit) | blocked (451/403) | Malaysia gate fails |
| M17 | Malaysian-licensed exchange promos (Luno, Tokenize, MX Global, Hata) | F1 weak | ok | manual | small one-off promos; not structural |
| M18 | Prediction-market liquidity rewards (Polymarket, Limitless, Opinion) | pass | **grey** (betting law) | Polymarket blocked | Malaysia gate fails |
| M19 | Sports-betting arbitrage / matched betting | pass | **illegal** | — | excluded |
| M20 | Maker rebates on exchanges | needs volume | — | — | screened out (needs volume tiers) |
| M21 | Exchange referral / builder-code revenue | needs users | — | — | screened out (audience-dependent) |
| M22 | Copy-trading provider fees | needs followers | — | — | screened out |
| M23 | Trading competitions | F1/F2 fail | varies | — | screened out (not repeatable) |
| M24 | Bug bounties | skill | ok | — | out of scope (skill, not structure) |
| M25 | Pendle fixed-rate PT to maturity | pass | unverified-onchain | only live markets (expired ones missing) | #210 (live markets): FAIL; full test needs expired-market history (Pendle API) → queued |
| M26 | Staking / restaking yield | pass | ok | yes | ≈ 3–5%; below bar (not separately tested) |
| M27 | Tokenised T-bills | pass | ok | yes | baseline ≈ 4% |
| M28 | Peg-stability-module / mint-redeem arbitrage | pass | unverified | on-chain | competitive bots (M8-like); parked |
| M29 | Stablecoin depeg buying | — | — | yes | #46 FAIL (UST) |
| M30 | stETH / LST redemption discounts | pass | — | yes | #41 FAIL (tiny) |
| M31 | Cross-chain lending-rate / stablecoin gaps | — | — | yes | #45/#47 FAIL / no data |
| M32 | Vault allocation inefficiency | — | — | yes | #42 FAIL |
| M33 | Offshore broker deposit bonuses | F4 fail | grey | — | #59 FAIL |
| M34 | Bursa IPO ballots | pass | ok | yes | #49 FAIL |
| M35 | Government matches / fixed-price funds (i-Saraan, ASB/ASM) | pass | ok | yes | #50: PASS but tiny (RM500/yr) |
| M36 | MYR crypto price gaps | — | ok | yes | #51 FAIL |
| M37 | SPAC trust-value floor (US, via IBKR) | pass | ok | SEC EDGAR (heavy) | ≈ T-bill + 2–4%, capital-heavy; benchmark only, not tested |
| M38 | Merger arbitrage / closed-end-fund discounts | market risk | ok | hard | not a rule-based subsidy; parked |
| M39 | Index-put / variance premium selling | F4 weak | ok via broker | no free options history | market-risk premium, not a subsidy; parked |
| M40 | Malaysian bank/e-wallet promos, cashback | F1 weak | ok | manual | tiny, manual |

## Reading
- 40 mechanisms → 19 tested or being tested; 9 fail the Malaysia gate or the five-part filter at Stage 0; the rest need data that is not free
  from US servers or are skill/audience-based.
- Every mechanism that pays a **small player** a Topstep-like return either needs a rule written by someone who loses money on purpose
  (prop firms: failed-fee pool; protocols: token emissions while bootstrapping), or is a bot race (liquidations, solvers, keepers).
  Emissions decay as capital arrives (seen directly in #201–#210), bot races concentrate in a few winners (#100 replay).
- Open/queued: M3 (#209), M4 (#208), M7 stability pools from on-chain gains, M25 Pendle with expired markets, M9 non-liquidation bounties.

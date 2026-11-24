# Radar review #1 — every new non-prop lead, 2026-11-24 (radar runs 45330403375, 45331504230 and the addendum-2 run)

Rule (`docs/PREREG_RADAR_NONPROP_20261124.md`): each lead is dismissed with a reason or desk-checked and pre-registered.
Third-party facts below are labelled; none of them is a backtest.

## N1 stablecoin depegs (7) — all dismissed
| Coin | Price / size | Disposition | Reason |
|---|---|---|---|
| apxUSD (Apyx) | $0.9665 / $250M | dismiss | backed by Strategy STRC preferred shares; mint/redeem only for authorised institutions (KuCoin/CryptoSlate/Invezz reports, June 2026) → no retail redemption arbitrage; buying is a recovery bet |
| AP USDA | $0.8786 / $76M | dismiss | claims 1:1 redemption but no audits (DefiLlama); retail redemption not verifiable |
| MSUSD (Metronome synth) | $0.7985 / $41M | dismiss | synthetic debt token; no verified 1:1 retail redemption |
| pmUSD | $0.4067 / $33M | dismiss | collapsed, not a temporary dislocation |
| USDR (Real USD) | $0.3976 / $18M | dismiss | collapsed in 2023 (long dead) |
| satUSD (River) | $0.9767 / $17M | dismiss | 2.3% discount, one-off at best; not prop-like |
| alUSD (Alchemix) | $0.9620 / $10M | dismiss | long-standing discount; 1:1 only via the slow transmuter (months) → a few % over months, not prop-like |

## N4 audit contests (2) → desk check #369: KILL at Stage 0
Leads: Cantina Morpho Midnight Adapter ($400,000, live), Revert v4lend ($50,000, escalations). Audit contests are protocol-paid and
skill-based (work Claude could do), so the whole route was desk-checked (third-party sources, not verified against platform docs):
prize money per submission fell from **$451 (2024) to $85 (2026 H1)**; public contests on Sherlock/Cantina **−83%** from early 2024 to early
2026 while submissions **+24%**; in one Cantina contest (Mar 2026) 8 of 59 paid researchers took 82.7% of $50K and 46 got $154 each;
Sherlock requires a **$250 USDC stake per report** (refunded if valid) and withholds payouts below validity thresholds; Cantina allows
AI findings only if validated, with per-submission deposits and Persona KYC; Code4rena runs its own AI auditor and reportedly wound down
in May 2026; industry-wide, AI-generated reports flood bug bounties. **Verdict: KILL** — AI has made this crowded; an AI-assisted newcomer's
expected value per report (~$85 average, highly skewed) is below Sherlock's stake and far below prop-like income. Re-check only if
the radar shows prize pools recovering.

## N5 governance forums (15 unique leads) — none is an opportunity for Jx; three are relevant to the parked CoW plan
- **CoW: "Proposal for consistency rewards v2.2"** — changes pay for good losing bids (matters for a new solver's income): *watch*.
- **CoW: "A public mirror of the solver auction archive (past 30 days)"** — would make an offline replay test of our solver possible: *watch*.
- **CoW: "[CIP-82] NOC Engine … BYOS track"** and CoW's registry entry "BYOS lets teams integrate with CoW Protocol without the operational
  overhead of running a full solver" — a possibly lighter entry route for us: *check when onboarding resumes*.
- CoW: "Migrate the TSolver bonding pool" (Tokka Labs moving to its own pool — an established firm), grant applications (building
  grants: excluded) — dismiss.
- Aave Umbrella reward renewal (staking yield, single-digit-% class, tested family), Aave bounty payout, Compound COMP rewards problem, Morpho
  and Lido grant requests (building grants: excluded), Sky stUSDS liquidation ratio (parameter) — dismiss.
- The 11 forums added in addendum 2 produced no matching topics in the last 14 days.

## N8 Malaysian promotions — dismissed (too small), pocket money only
Rakuten Trade: 1,000 RT points + up to RM60 Touch 'n Go credit on activation; moomoo MY and Webull MY: "Welcome Rewards" (amounts not in
page text); HATA: 10% referral rebate, staking rewards. One-off, capped, legal — worth taking only as small change, not a strategy.
MX Global row pointed to an unrelated payroll company (mxglobal.com): removed.

## N9 market-maker / maker-rebate programmes — dismissed for small accounts
Drift pays a flat **0.25 bps** maker rebate (on $1M monthly volume ≈ $25); Hyperliquid maker rebates require a share of total exchange
maker volume (≥ 0.5% tiers) — reachable only by large market makers; Aster, Paradex, Orderly and edgeX pages returned no fee text
(script-rendered) — URLs to be replaced. Thin-venue market making already failed (#322).

## N2, N3, N7 — no leads
No extreme funding (235 perps checked); no new CoW solver recipients (53 paid in 21 days); perp volume surges need 7 days of history.

## General trading (Jx asked)
Not a radar area: trading strategies are found by backtests, not feeds. Tested so far: prop-side NQ variants #1–#65, overnight/pre-FOMC
drift, futures trend/carry/value/skew/momentum #350–#354, VIX roll, FX carry, option selling, risk parity, index events, crypto listing /
unlock trades. Best: #351 futures momentum 20.7%/yr on paper, needs ~$250K+. No trading edge near 100%/yr on small capital.

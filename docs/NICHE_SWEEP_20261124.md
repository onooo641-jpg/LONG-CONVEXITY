# Niche sweep — mechanisms shaped like the two real finds (prop recycling, CoW solving) — 2026-11-24

Jx: Malaysian areas are too well known; dive into niches, as that is how prop recycling and CoW were found. The two finds share a shape:
**someone else pays** (failed customers; a protocol's fee budget), the role or product is **open to a disciplined bot**, and it is **niche**
enough not to be crowded by big money (a per-person cap, or an engineering barrier). Each niche below was desk-checked against that shape
(third-party sources; none is a backtest). Measured tests from this sweep: #370 crypto trend/momentum, #371 UniswapX fillers.

| # | Niche | Shape | Desk finding (source class) | Disposition |
|---|---|---|---|---|
| 377 | Crypto prop firms (structural coin-flip test like Topstep's) | prop | HyroTrader: own-strategy bots allowed but accounts ≥ $50K manual-only (Sept 2026 terms per Velotrade), trades on Bybit (barred from serving Malaysians by SC → using it = geoblock issue); Bitfunded, Kraken Prop manual-only; Crypto Fund Trader bans HFT and possibly API bots (vendor blogs) | excluded / not bot-usable; recheck if a bot-friendly crypto prop on a Malaysia-legal venue appears (radar prop pages) |
| 378 | Exchange / perp-DEX trading competitions | prop | prize pools $10K–$50K split among ~50 winners (Orderly, Sai, Gate, Kodiak); many rank by volume (favours big accounts); Polymarket perps excluded | dismissed: too small |
| 379 | Liquity-fork redemption bots (feUSD, BOLD, others) | CoW | anyone may redeem 1 stable for $1 of collateral minus fee; feUSD ~$75M at ~$0.998 (May 2026) → rarely profitable after fee, atomic bot race | dismissed (MEV race, rare); #305 already showed "redemption-floor" lows were data artefacts |
| 380 | ZK proving markets (Boundless, Succinct) | CoW | Boundless reportedly pausing core protocol (2026-11-05) and ending emissions in Q4 2026; job fees "near zero", 1,500+ provers; Succinct needs PROVE stake, "designed for experienced operators" | dismissed: ending / hardware race with stake |
| 381 | UMA optimistic-oracle proposer / disputer bots | CoW | Polymarket proposals now whitelisted (managed oracle); 98.6% of requests settle undisputed → little dispute income | dismissed |
| 372 | 1inch Fusion resolvers | CoW | max 10 whitelisted by staked 1INCH, KYC | dismissed (capital-gated) |
| 373 | deBridge DLN takers | CoW | open-source taker; ~4 bps taker incentive; same economics as Across (#362 KILL) | dismissed by analogy |
| 374 | Drift keepers / fillers | CoW | reward = lesser of 10% of fee and a time-based amount (cents), speed race | dismissed |
| 371 | UniswapX fillers (Arbitrum, Base) | CoW | permissionless contract calls; concentration unknown | **measuring** |
| 365–368 | CoW solving (incl. small β=100% chains, BYOS track) | CoW | passes all free checks; onboarding paused by CoW | parked, watched |
| 370 | Crypto perp trend / momentum | trading | never tested | **measuring** |

**Radar changes from this sweep.** Malaysian broker/exchange promo pages (N8) removed — small and well known. Malaysian regulator alert
lists kept as a legality guard. N5 forum keywords extended to new paid-operator programmes: prover, operator programme, rebalancer,
searcher, OEV (oracle-extractable value), "solver incentive".

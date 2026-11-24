# #366 CoW Stage 2a: how far behind the real winners is CoW's open-source example solver? (no money) — 2026-11-24

**Why.** #365 passed every free check; the only pass route left is a real solver bidding on live auctions. Jx chose GitHub Actions to run
the first step: CoW's own open-source example ("baseline") solver in local shadow mode, compared with the actual winners on the same
auctions. This measures the head start (or not) that the free code gives; it is **not** an income test and cannot pass #365 Stage 2.

**Setup (fixed before any run).** Docker image `ghcr.io/cowprotocol/services:main` (digest printed in the run log), three programs on one
GitHub runner: `solvers baseline` (config as CoW's playground: max-hops 2, 8 base tokens), `driver` (Uniswap V2 liquidity preset, as the
playground; app data from api.cow.fi), `autopilot` in shadow mode against `https://api.cow.fi/mainnet/` (pulls each live auction, sends it
to the local driver, logs the local solver's reward and win; nothing is settled). RPC: free public Ethereum endpoint
(`ethereum-rpc.publicnode.com`). Network: Ethereum mainnet (largest API sample in #365). After the run, each auction id is looked up in
CoW's solver-competition API (`/api/v2/solver_competition/{id}`) for the production solutions.

**Runs.** Pilot ≥ 20 minutes (does it run at all; kill-only: if the stack cannot receive auctions or produce any solution after one repair
attempt, record "not runnable on Actions with a free RPC"). Main run: 180 minutes.

**Measures (main run).** Auctions received; share with a valid baseline solution ("bid rate"); for those, ratio = baseline score /
best production score in the same auction; would-have-won share (baseline score ≥ best production score); median ratio.
**Verdict for the "start from the free baseline" route (kill-only).** KILL the route if would-have-won share < 1% **and** median ratio
< 0.5 → a competitive solver must be built on different foundations (more liquidity sources, aggregator APIs, private inventory); the free
code gives no real head start. Otherwise: "baseline is a usable starting point" (still not a pass).

**Costs.** Free (GitHub Actions minutes; Jx chose this). **Commands.** run: push `.github/cow_shadow_request.txt` (workflow
`cow_shadow.yml`); analysis: `uv run python -m scripts.cow_shadow_20261124 | tee docs/jx_runs/cow_shadow_20261124.txt` (re-run once;
must be identical).
**Honest limits.** Uniswap V2 liquidity only (production solvers use many sources and private liquidity), so the gap is an upper bound on
how far *a minimal* solver is behind; a free public RPC can throttle and drop auctions (counted, reported); shadow scores use the same
scoring code as production but are not settled, so execution risk is ignored.

### Results (2026-11-24)
**Pilot (Actions run 45329600886, `docs/jx_runs/cow_shadow_run_45329600886.txt`).** Image `ghcr.io/cowprotocol/services@sha256:05078ac1…`
(version main@8b4bb6a2). All three programs started and stayed up for 20 minutes (solver engine, driver serving on port 11088, autopilot
in shadow mode). Every request for the live auction failed: `HTTP 403 Forbidden for https://api.cow.fi/mainnet/api/v1/auction` (~100
attempts). Auctions received: 0; baseline solutions: 0.
**Repair attempt (fetch run 45332265118, `docs/jx_runs/fetch_fallback_45332265118.txt`).** The production live-auction endpoint returns
403 on all 11 networks; the staging (barn) endpoints answer 200 but hold 0–3 orders (0 on mainnet), so a staging run cannot be compared
with production winners.

**Verdict (pre-registered pilot rule): NOT RUNNABLE on GitHub Actions with free access.** CoW's production auction feed is restricted;
its FAQ says order-book access is whitelisted, generally once a solver is live. So the no-money test of a real solver (#365 Stage 2)
needs CoW's cooperation: the official route is the "CoW Swap Solvers" Telegram group (shadow competition, currently on Plasma).
This does not kill CoW solving; it moves the next step to a human contact, which only Jx (or the friend) can make. An unregistered
alternative — rebuilding past auctions from public data (solver-competition order lists + the public orders API) and feeding them to the
local stack — is possible but needs substantial engineering and would use today's chain state for past auctions (lower fidelity).

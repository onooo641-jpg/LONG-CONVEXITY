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

# #368 CoW solver readiness + mini-benchmark on CoW's open staging feed (Gnosis Chain, no money) — 2026-11-24

**Why.** CoW paused new-solver onboarding "for the next weeks" (reply to Jx, 2026-11-24) and its production auction feed is closed
(#366, HTTP 403). Its **staging ("barn") feed is open** (#366 repair probe: HTTP 200 on all 11 networks; Gnosis had the most orders). Real
users trade on staging and CoW's staging solvers compete there, so the same shadow stack can (1) prove our pipeline works end to end on
CoW's real auction format, ready for when onboarding resumes, and (2) compare CoW's open-source baseline solver with the staging winners
on the same auctions. A near-live rebuild of production auctions was rejected: rebuilt auctions arrive after the winners have settled,
so their orders would already be filled when our solver simulates.

**Setup (fixed).** Same image and workflow as #366 (`cow_shadow.yml`), network Gnosis Chain (chain id 100): autopilot shadow =
`https://barn.api.cow.fi/xdai/`; driver liquidity presets Honeyswap + SushiSwap; base tokens WXDAI, USDC, USDT, WETH, GNO, sDAI, COW;
free RPC `https://rpc.gnosischain.com`. Comparison: `https://barn.api.cow.fi/xdai/api/v2/solver_competition/{auction id}`.
Run: 180 minutes (one repair attempt allowed if the stack does not start).

**Measures.** Auctions with ≥ 1 order received; baseline solutions; staging competition found for the same id; baseline score / best
staging score; would-have-won share. **Verdict.** "Pipeline ready" if ≥ 1 valid baseline solution is produced on a real auction.
Benchmark (only if ≥ 30 auctions have both a baseline bid and staging competition data): same rule as #366 — KILL the "start from the
free baseline" route if would-have-won < 1% and median ratio < 0.5. Fewer than 30: "sample too small", descriptive only.

**Commands.** run: push `.github/cow_shadow_request.txt` with `net=xdai`; analysis:
`uv run python -m scripts.cow_shadow_20261124 | tee docs/jx_runs/cow_shadow_20261124.txt`.
**Limits.** Staging volume is tiny and staging solvers may be configured differently from production; a staging result says little about
production income. Free Gnosis RPC may throttle. Configs moved from `cow_shadow/*.toml` to `cow_shadow/mainnet/*.toml` (same content)
to add `cow_shadow/xdai/`.

### Results (2026-11-24; Actions run 45370955833, `docs/jx_runs/cow_shadow_run_45370955833.txt`; `docs/jx_runs/cow_shadow_20261124.txt`)
The stack ran the full 180 minutes on Gnosis staging. The autopilot received **2,072 auctions with orders**; the baseline produced
**0 solutions**; CoW's staging competition API had solver data for **1** of those 2,072 auctions (CoW's own staging solvers also bid
almost never), i.e. the staging feed is nearly all unfillable resting orders. One transient HTTP 503 from the staging feed; no driver or
solver errors at the logged level.
**Verdict (registered):** "pipeline ready" **not demonstrated** (0 valid solutions) — but this cannot be told apart from "no solvable
orders on staging", since staging solvers were equally silent. Benchmark: sample too small (1 auction). Conclusion: CoW's open staging feed
cannot test a solver; a real test needs CoW's production shadow access (paused by CoW, reminder set for 2026-12-15).

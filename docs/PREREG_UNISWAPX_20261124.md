# #371 UniswapX fillers on Arbitrum and Base: is filling open to newcomers or locked by a few pros? (non-prop) — 2026-11-24

**Why.** Coverage audit gap: UniswapX filling (a paid-bot role like CoW solving and Across relaying) was only desk-checked in 2026-11-21
("needs bonded capital + pros", sweep M10) and never measured. Written before any data are fetched.

**Stage 0 (official repo `Uniswap/UniswapX` README, read 2026-11-24).** Reactors: Arbitrum V3 Dutch Order Reactor
`0xB274d5F4b833b61B340b654d600A864fB604a87c`; Base Priority Order Reactor `0x000000001Ec5656dcdB24D90DFa42742738De729`. Every reactor emits
`Fill(bytes32 indexed orderHash, address indexed filler, address indexed swapper, uint256 nonce)` with `filler = msg.sender`. Filling is a
permissionless contract call on these chains (Dutch decay on Arbitrum; priority-gas auction on Base); Ethereum mainnet is left out
(quotes come through Uniswap-approved quoters, and free mainnet log scans failed in #361).

**Data.** Fill logs from public RPCs (as #362), plus 64 sampled block timestamps per chain for dating.
**Measures.** Fills per filler address per month; distinct fillers; top-3 share of fills; newcomers = fillers whose first fill falls in
the window's last six months; each newcomer's best monthly share.
**Stage 1 (kill only; 2026-08-01..2026-10-31, both chains).** KILL if the top 3 fillers make ≥ 90% of fills on **both** chains.
**Stage 2 (2025-11-01..2026-10-31).** "Door open" (only route to a further profit study) if on at least one chain a newcomer (first fill
2026-05-01 or later) reached ≥ 5% of that chain's fills in some month. Otherwise FAIL. Profit per fill is **not** measured here (fills carry
no amounts; a later study would need transfer-level data).

**Commands.** fetch: Actions job `uniswapx371`; analysis: `uv run python -m scripts.uniswapx_20261124 | tee docs/jx_runs/uniswapx_20261124.txt`.
**Limits.** A filler address is not a team (teams can use several); counts are not profits.

### Results Stages 1–2 (2026-11-24; `docs/jx_runs/uniswapx_20261124.txt`, identical on re-run)
Arbitrum: complete (0 blocks missed), 43,825 fills in 12 months by 55 fillers. Base: 231,531 fills, but the public-RPC time budget stopped
at 2026-07-23 (4.24M of 15.77M blocks missed), so Base's Stage 1 window is **not measured** (coverage handling made explicit in the script
before the verdict: an unmeasured chain cannot count towards a kill).
Stage 1 Arbitrum 2026-08..10: 10,957 fills, 28 fillers, **top-3 share 89.0%** (one filler 77%) → survives (kill needs ≥ 90% on both chains).
Stage 2: newcomers on Arbitrum reached **9.9% / 9.7% / 5.2%** monthly share (first fills Aug 2026) → **"door open"** (registered rule).
Base newcomers since May 2026: best 3.8%. Volumes are falling: Arbitrum 11.5K fills (Nov 2025) → ~4K/month; Base 74K → 6K/month.

### Stage 3 (registered 2026-11-24, after Stages 1–2, before any volume data): is there enough money?
Fill events carry no amounts. Data: transaction receipts of all Arbitrum fills 2026-08-01..2026-10-31; per fill, the swapper's input
transfer (token, amount) priced with DefiLlama daily prices (stables $1; other tokens via `coins.llama.fi`). **Ceiling** = annualised
priced input volume × **10 bps** (a generous filler margin before gas and hedging). **KILL** if 10% of the ceiling (a strong newcomer's
share) is below $15,000/yr. Command: fetch job `uniswapx371b`; analysis `uv run python -m scripts.uniswapx_vol_20261124 | tee
docs/jx_runs/uniswapx_vol_20261124.txt`.

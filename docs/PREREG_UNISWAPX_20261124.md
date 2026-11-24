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

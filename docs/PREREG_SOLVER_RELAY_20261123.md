# #361 CoW Protocol solver rewards and #362 Across relayer fees: can a small newcomer earn ≥ $15K/yr? (non-prop) — 2026-11-23

**Why.** Jx wants a non-prop source with prop-like money: about $15–18K/yr from about $10–15K of capital (or time plus a small amount of
capital). The research report (`reports/Non prop high return alternatives.md`, ranks 3 and 4) found two protocol-paid roles whose payouts
are fully on-chain and free to measure: CoW Protocol solving (the CoW DAO pays weekly COW rewards to the solvers who win batch auctions) and
Across relaying (bridge users pay a fee to whoever fronts their funds on the destination chain). Both are open by design, so the question is
not access but whether anyone outside the top few players earns enough. Written before any data is fetched.

## Stage 0 (desk check; done on GitHub Actions because docs.cow.fi and docs.across.to are blocked from this sandbox)
- Addresses used (from a search-engine summary of docs.cow.fi and from memory; **assumed until the run confirms them**): CoW Solver Payouts
  Safe `0xA03be496e67Ec29bC62F01a428683D7F9c204930` (Ethereum); COW token `0xDEf1CA1fb7FBcDC777520aa7f396b4E015F497aB`; Across SpokePool on
  Base `0x09aea4b2242abC8bb4BB78D537A67a245A7bEC64`, Arbitrum `0xe35e9842fceaCA96570B734083f4a58e8F7C5f2A`. The fetch job downloads the
  official pages (docs.cow.fi/governance/multisigs, the solver onboarding page, the rewards page; docs.across.to contract addresses) and prints
  whether each address appears, plus on-chain checks (contract code present; fill events found).
- Fill events (verbatim from `across-protocol/contracts` `V3SpokePoolInterface.sol`, read 2026-11-23): `FilledRelay(bytes32 inputToken,
  bytes32 outputToken, uint256 inputAmount, uint256 outputAmount, uint256 repaymentChainId, uint256 indexed originChainId, uint256 indexed
  depositId, uint32 fillDeadline, uint32 exclusivityDeadline, bytes32 exclusiveRelayer, bytes32 indexed relayer, bytes32 depositor,
  bytes32 recipient, bytes32 messageHash, V3RelayExecutionEventInfo relayExecutionInfo)` with struct `(bytes32 updatedRecipient, bytes32
  updatedMessageHash, uint256 updatedOutputAmount, FillType fillType)`; legacy `FilledV3Relay` (address / bytes variants). FillType 0 fast,
  1 replaced slow fill, 2 slow fill (paid by the protocol, not a relayer: excluded).
- Access: both roles are permissionless contract calls except that a CoW solver must be allow-listed, normally through the CoW DAO bonding
  pool after KYC (terms, service fee and any country limits recorded from the onboarding page). A Malaysian exclusion in the official text
  would end #361 at Stage 0. Running either is a business (servers, engineering months), not a deposit.

## #361 CoW solver rewards
**Data.** Ethereum `eth_getLogs` (public RPCs): COW `Transfer` events sent **from** the Solver Payouts Safe, 2024-01-01..2026-10-31; block
timestamps; COW daily price from DefiLlama (`coingecko:cow-protocol`). ETH transfers (gas / slippage reimbursements) are ignored: they repay
costs. A recipient counts as a solver if it was paid in ≥ 4 distinct weeks of the measured period (filters one-off transfers).
**Measure.** Gross USD per recipient per period = Σ (COW × that day's price); annualised by days in the period. Before server costs, before
the bonding pool's service fee (15% after six months per the docs summary; shown as a sensitivity).
**Stage 1 (kill only; 2026-01-01..2026-10-31).** KILL if the median recipient outside the top 5 earns < $15,000/yr gross.
**Stage 2 (2024-01-01..2026-10-31).** "Worth building a shadow solver" (the only possible pass here) if, in each of 2024, 2025 and 2026
(annualised), the **10th-ranked** recipient earns ≥ $15,000/yr gross and still ≥ $15,000 after the 15% service fee. A pass does **not** mean Jx
can earn it: a new solver must beat incumbents in CoW's shadow competition first (a separate, later test, no money).

## #362 Across relaying
**Data.** `FilledRelay` and `FilledV3Relay` logs on the Base and Arbitrum SpokePools (public RPCs); output-token `symbol()` / `decimals()` via
`eth_call`; ETH and BTC daily prices from DefiLlama for WETH / WBTC fills; 64 sampled block timestamps per chain for dating fills.
**Measure per fill.** Spread = inputAmount − updatedOutputAmount, in the asset's units (input decimals = output decimals, except USDC/USDT from
BNB Chain, 18 decimals), × USD price. Fills whose implied input/output ratio is outside 0.9–1.1 are excluded and counted (token mismatch).
The spread is an **upper bound** on relayer income: it still contains the Across LP fee and must pay destination gas.
**Stage 1 (kill only; fills on 2026-10-01..2026-10-31, annualised × 365/31).** KILL if (a) the 6th-ranked relayer by total spread (Base +
Arbitrum) earns < $15,000/yr upper bound, OR (b) the median spread on fills ≤ $15,000 is < 2 bps (at ≤ 2 bps, even $15K of inventory turned
3,500 times a year — once every 2.5 hours, optimistic — earns < $10,500/yr before LP fee and gas).
**Stage 2 (only if Stage 1 survives; 2025-11-01..2026-10-31, Base + Arbitrum + Optimism).** Entrant estimate = (median bps on fills ≤ $15K won
by relayers outside the top 5, minus 1 bp assumed LP fee) × min(average volume of fills ≤ $15K handled by relayers ranked 6–10, $15K × 3,500)
− median destination gas per fill × the implied number of fills. PASS if ≥ $15,000/yr in both 6-month halves.

**Costs.** Free public data only. **Commands.** fetch: Actions `fallback_fetch.yml` jobs `cow361`, `across362`; analysis:
`uv run python -m scripts.solver_relay_20261123 | tee docs/jx_runs/solver_relay_20261123.txt` (re-run once; must be identical).
**Honest limits.** Recipient address ≠ solver team in every case (a team can use several addresses, or a shared one); public RPCs can miss
ranges (coverage printed and reported); relayer identities are addresses only; neither test measures whether Jx could build a competitive bot.

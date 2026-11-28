# Batch NF28: oracle-lag trading on oracle-priced perps — Stage 0 desk result (2026-11-28): **KILL, not testable**

**Idea (Jx, "grey areas"):**
- Oracle-priced perps (Gains/gTrade, Ostium, Avantis, HIP-3 deployer oracles) fill at an oracle price. If the oracle lags the real
  market, a trader who sees the real price first can trade against the stale one.
- It is legal. Some call it toxic flow.

**Stage 0 findings (third-party and vendor sources; not verified on-chain):**
1. **Execution design closes it.** These venues use pull-based low-latency oracles (e.g. Chainlink Data Streams, Pyth pull). An order
   is filled at a price fetched **after** it is submitted (two-step execution), so a visible lag cannot be traded at the stale price.
   Builders also add buffers or TWAPs (Chainlink and Chainscore articles).
2. **No free history:** Pyth's historical endpoints require an API key since the 2026-08-26 Pyth Core upgrade. The free TradingView
   shim endpoints were retired (Pyth docs and dev forum). Obtaining a key needs a sign-up by Jx.
3. HIP-3 deployer oracles are set by deployers, so each market is different. Trading a known deployer bug would be exploit territory,
   not a structural edge.

**Verdict:** KILL at Stage 0. No data was fetched and no rule was run.
- **Re-open only if:** a venue is found that fills at the pre-order oracle price, its terms allow it, and Jx obtains a Pyth API key for
  the history.

**Sources:**
- docs.pyth.network/price-feeds/use-historical-price-data
- dev-forum.pyth.network (Benchmarks TradingView sunset)
- chain.link/article/price-feed-architecture-perpetuals
- chain.link/blog/low-latency-oracle-solution

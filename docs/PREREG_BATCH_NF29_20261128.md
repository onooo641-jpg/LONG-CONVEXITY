# Batch NF29 (#656–#659): HyperEVM DEX pools vs Hyperliquid's order book — what a newcomer arbitrageur can still reach — pre-registered 2026-11-28, before any pool data is fetched

**Why:**
- One team self-reports about $5M over roughly 8 months from arbitraging HYPE between HyperEVM pools and Hyperliquid (unaudited,
  `reports/Grey area edges for small capital.md`). This is the #3-ranked candidate in that report.
- It is ordinary arbitrage: it restores prices after other people's swaps. There is no front-running of specific users and no
  manipulation.
- The question is whether gaps big enough to pay costs **stay open for at least one block** often enough for a newcomer, rather than
  being taken instantly by the incumbents.

**Desk checks:**
- **G5:** HyperEVM and Hyperliquid need no KYC.
- **G6:** crowded, since the incumbents are known. This pilot measures how crowded.
- Capital: about $1,500 per leg is enough at pilot scale.

**Data (job `ubatchnf29`, GitHub Actions):**
- **Pools:** the top HyperEVM pools by liquidity from GeckoTerminal (`networks/hyperevm/pools`), for pairs whose base token has an HL
  market (WHYPE, UBTC, UETH, USOL and others). Quote tokens USDT0, USDC, USDe, USDH. Kept: fee tier, DEX name, token addresses and
  decimals.
- **Swaps:** `eth_getLogs` on the public HyperEVM RPC for Uniswap-v3 `Swap` and v2 `Sync` events of those pools, over **the last
  5,000 minutes** (≈ 3.5 days, the HL 1-minute candle limit).
- **Timing and identity:** block timestamps from a sample of blocks, interpolated. The swap's `sender`/`recipient` topics identify the
  bot contract.
- **HL prices:** 1-minute candles (perp and spot) for the same bases, last 5,000 minutes.
- **Files:** `batchnf29_pools.json`, `batchnf29_swaps.parquet`, `batchnf29_hl_1m.parquet`.
- Endpoints are not verified from this sandbox. Raw first replies go to `batchnf29_probe.json`, and a parse or unit fix may be added
  by addendum before analysis.

**Measures:**
- **Pool price after each swap:** v3 = (sqrtPriceX96 / 2^96)² × 10^(dec0 − dec1), oriented to quote per base; v2 = reserve ratio.
- **Gap** = pool price / HL perp 1-minute close (same minute) − 1.
- **Cost of one arbitrage round trip:** the pool fee tier + 0.045% HL taker + 0.05% buffer. Gas is about 0 and is ignored; the value is
  printed.
- **Reachable gap:** |gap| > cost after a swap, **and** the pool's next event is in a **later block** with the gap still > cost (so no
  one closed it in the same block).
- **Reachable value** = (|gap| − cost) × min($1,500, notional of the swap that opened the gap) × 0.5, a capture haircut.
- **Concentration:** among swaps that **close** a gap (the next event after a gap, moving the pool price at least halfway back to HL),
  the share done by the top 3 sender contracts.

| # | Measure (pilot window, extrapolated to a year by × 365 / days covered) |
|---|---|
| 656 | Reachable value per year, **all pools pooled** |
| 657 | Same, **WHYPE pools only** (the reported incumbent trade) |
| 658 | Same, **non-HYPE bases** (UBTC, UETH, USOL and others) |
| 659 | **Concentration:** top-3 share of gap-closing swaps, all pools |

**Stage 1 (this pilot, kill only):**
- **KILL** the family if #656 < **$3,600/yr** ($300/month), or if #659's top-3 share > **95%** with #656 < $15,000/yr.
- **No PASS can be declared from this pilot.** Surviving leads to **Stage 2**: a forward log of live gaps through the radar (a
  2–4-week pre-registered window). That is the only way to see block-level persistence over a longer period with free data.

**Not modelled:**
- the speed race inside a block;
- inventory rebalancing between HyperEVM and HyperCore;
- bridge timing;
- MEV ordering on HyperEVM.

**Script/output:** `scripts/batch_nf29_20261128.py` → `docs/jx_runs/batch_nf29_20261128.txt`, re-run identical.

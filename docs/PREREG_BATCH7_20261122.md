# Batch 7: Gains price check (#225), Pendle walk-forward (#211, G9), free execution pilot for funding gaps (#208) — 2026-11-22

Written and committed before the batch-7 fetch (`scripts/fetch_fallback.py batch7`).

## A. #225 Gains vaults against real vault-token prices
DefiLlama APY may leave out losses to traders (the #214/#221 lesson). Data: daily USD price of the Gains vault tokens (gUSDC on Arbitrum
`0xd3443ee1e91aF28e5FB858Fbd0D72A63bA8046E0`; other chains if a source answers) from DefiLlama coins, plus Gains' own API if it answers.
Rule: realised daily return = Δ price / price. **PASS** if the price-based return of the vault(s) the G6 walk-forward used is ≥ 8%/yr in both OOS
halves (2025-05..2026-01, 2026-02..2026-10) and ≥ 8% with costs ×1.5; if only the Arbitrum vault has prices, it is tested alone (fixed hold).
Also reported: price-based vs APY-based return over the same days.

## B. G9 Pendle PTs walk-forward, expired markets included
Universe: every Pendle market (all chains the API lists) whose name matches the stablecoin pattern of #211, expiring 2024-11-01 or later; daily
implied APY / TVL history; underlying price at expiry (DefiLlama coins). Causal accounting: an open position accrues its entry implied APY daily;
a depeg loss (underlying < $0.98 at expiry) is booked on the expiry day. Monthly ladder: each month 1/6 of capital buys the top-k markets.
Grid: k {1,3,5} × min TVL {1M, 5M, 20M} × min days to maturity {30, 60, 90} × underlying {all, blue-chip (name contains USDE, SUSDE, USDS, SUSDS,
USDC, USDT, DAI, GHO, FRAX, CRVUSD)} = 54 configs. Costs 0.1% swap + $10 gas per leg on $10,000/6/k. Walk-forward and PASS rule as
PREREG_WALKFORWARD (monthly pick on trailing 6 months, OOS halves ≥ 8%, costs ×1.5 ≥ 8%).

## C. #208 free execution pilot (paper, no money)
Every 10 minutes for 3 hours: L2 order books for BTC, ETH, SOL, XRP, DOGE, AVAX, LINK, SUI, ARB, OP, LTC, BNB on Hyperliquid, dYdX v4, Aevo.
Measures per venue/coin: (1) **slippage of a $10,000 market order** (walk the book, vs mid) per side; (2) **top-of-book size** at best bid/ask
(maker-fill capacity proxy); (3) quoted spread. The funding-gap test assumed 5 bps taker per leg-side and still passed with costs ×1.5 → the budget
for slippage is ~2.5 bps per leg-side. **Reading:** taker execution viable if the median $10K slippage ≤ 2.5 bps per leg-side on the venues/coins
used; maker execution plausible if median top-of-book size ≥ $10,000. Per venue and per coin reported; Aevo decides (the pass needs Aevo pairs).
Commands: `uv run python scripts/batch7_20261122.py | tee docs/jx_runs/batch7_20261122.txt`

## D. #276 hedged HYPE staking: liquidation check (addendum, written before the HYPE price fetch, 2026-11-22)
The walk-forward pass (G5, lev3/always, 14.97% / 8.72%) ignored liquidation of the short. Data: Hyperliquid HYPE perp 4-hour candles
(candleSnapshot, latest 5,000 bars ≈ 2024-11 onward), fetched by job `hype4h`.
Position per $1 of capital at leverage L: staked spot HYPE and a short perp of equal notional L/(L+1); margin 1/(L+1) in USDC.
Staked HYPE cannot be moved quickly (7-day unstaking), so the hedge is **rebalanced only every 7 days** (reset at the close of the 4h bar).
Between rebalances the short's margin equity = 1/(L+1) − notional × (P/P0 − 1); **liquidated** when equity < 5% × notional × P/P0 (maintenance
margin assumed 5%; uncertain), checked against each bar's high. On liquidation: the remaining equity plus a 0.5% fee is lost and the spot leg
is **unhedged until the next weekly rebalance** (its P&L from the liquidation price to the rebalance close is booked). Losses are booked on the
day they happen, added to the G5 daily series, and the G5 walk-forward is re-run with the same 15 configs.
**PASS** = same as G5: OOS halves ≥ 8% and costs ×1.5 ≥ 8%. Also reported (context, not the verdict): liquidation count per leverage, and a
variant that re-hedges at the next 4h bar (loss = remaining equity + 0.5% only).

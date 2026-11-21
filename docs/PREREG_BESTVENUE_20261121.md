# Best-venue funding carry on DeFi perps (#217) — 2026-11-21

Written before the funding data (#208 fetch) is seen. Extends #57 (Hyperliquid only, 2.9–6.4%/yr): hold the coin spot and short its perp on
whichever DeFi venue — Hyperliquid, dYdX v4 or Aevo — has paid shorts the most over the trailing 30 days.
- Coins BTC, ETH, SOL, XRP, DOGE, AVAX, LINK, SUI, ARB, OP, LTC, BNB. Monthly: rank every (coin, venue) by trailing-30-day mean funding received
  by a short; hold the **top 3** (distinct coins) equally for the month. Daily return per position = funding received that day on its venue.
- Capital: spot + 1/3 margin (3× short) → return / 1.333. Costs: 0.10% spot + 0.05% perp per side on each change of position.
- Halves 2024-11..2025-10, 2025-11..2026-10. Stage 1 (2026-08..10) KILL < 4%/yr; PASS ≥ 8%/yr both halves.
Limits: spot custody on-chain (wrapped tokens for non-native coins), liquidation at 3× on a ~30% move before rebalancing.
Command: `uv run python scripts/bestvenue_20261121.py | tee docs/jx_runs/bestvenue_20261121.txt`


## Result: Stage 0.5 KILL (2026-11-21)
Ceiling from data in hand: best 3 coins' last-90-day Hyperliquid short funding (chosen with hindsight) = 7.8%/yr on capital (LTC, SUI, LINK; first inline calculation said 7.5% because it used the wrong coin list, corrected by `scripts/ceiling_20261121.py`),
below the 8% bar; dYdX/Aevo would have to pay shorts more than HL on the same coins to lift it. Not run (`docs/jx_runs/ceiling_20261121.txt`).

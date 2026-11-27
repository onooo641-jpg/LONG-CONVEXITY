# Batch N (#509–#511): the wick rule (#389) on Hyperliquid markets it never covered — pre-registered 2026-11-27, before running

**Why.** Everything that has worked outside prop firms is liquidity for forced sellers on Hyperliquid (#389 wick bids, #397 cascade
reversal, #385 pre-launch shorts). #389 tested only standard Hyperliquid perps after their first 30 days. Hyperliquid is usable from
Malaysia, so the cheapest way to add income is more markets for the proven rule.

**Family:** all three are family 1 (#389). They add capacity; they are not new families. Gate as Batches F–M; a pass counts toward
Jx's goal only at ≥ ~$10K/yr of added profit.

**Rule (identical to #389 except where noted).**
- Each day, for every market: a resting limit buy at the previous close × (1 − X).
- **Fill** only if the day's low is ≥ 0.5% below the level. Fill price = the level, or the open if the day opened below it.
- **Sell** at that day's close.
- **Size per fill** = min($1,500, 1% of the day's USD volume). Fills of one day share one $15,000 pot (scaled down if exceeded).
- **Costs:** perps 0.015% maker in, 0.045% taker out; **spot (#510) 0.04% maker + 0.07% taker**.

| # | Universe (data already in the repo) | X primary (context) | Dev (Stage 1, kill-only) | Unseen (Stage 2) |
|---|---|---|---|---|
| 509 | **HIP-3 builder perps** (stocks, indices, commodities, FX on Hyperliquid's builder DEXes; they trade 24/7 while the underlying is closed, so weekend liquidations meet thin books). `fivehigh_hip3_1d`, 271 markets, 2025-10..2026-11; first 30 days of each market excluded | **5%** (10%, 15%). Set below #389's 15% because a 5% daily drop is already about 2σ for an index or large stock; chosen now, before any fill is computed | 2025-11-01..2026-04-30 | 2026-05-01..2026-11-25 |
| 510 | **Hyperliquid spot tokens** (HIP-1). `fivehigh_hl_spot_1d`, 342 pairs, 2024-04..2026-11; first 30 days excluded | 15% (10%, 20%) | 2024-05-01..2025-06-30 | 2025-07-01..2026-11-25 |
| 511 | **Perps in their first 30 days after listing** (the window #389 excluded; new listings are where over-levered early longs get liquidated). `uncharted_385_candles` | 15% (10%, 20%) | listings before 2025-01-01 | listings 2025-01-01 onward |

**Stage 1 KILL:** mean net per fill ≤ 0.3% (with ≥ 30 fills; fewer → no kill, said so).

**Stage 2 PASS:** ≥ 30 fills, mean net per fill ≥ 0.3%, t ≥ 2, and net ≥ $1,000/yr. A pass counts toward the goal only if net
≥ $10K/yr.

**Also reported:**
- net $/yr;
- profit without the single best day (wick profits concentrate);
- overlap of fill days with #389's fill days. Shared days compete for the same $15,000 pot.

**Script/output:** `scripts/batch_n_20261127.py` → `docs/jx_runs/batch_n_20261127.txt`, re-run identical.

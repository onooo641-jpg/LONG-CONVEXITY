# Cross-venue funding gaps (#208) — 2026-11-21

Written and committed before the funding histories are fetched (only a reachability probe was run: `docs/jx_runs/fetch_fallback_*.txt`).
HANDOFF_NONPROP idea 3. Different from #57 (single-venue carry): here the position is delta-neutral **across two perp venues**, short where
funding is high and long where it is low, so it earns the funding difference.

## Venues (Malaysia filter applied first)
- **Tested (permissionless DeFi perps, Malaysia not known to be blocked: unverified):** Hyperliquid (HL) vs dYdX v4, HL vs Aevo, dYdX vs Aevo.
- **Reported only, not eligible:** HL vs Gate.io (centralised exchange not registered with Malaysia's Securities Commission → grey; listed so the
  size of the CEX gap is known). Binance, Bybit, BitMEX refuse US servers; OKX gives only ~3 months; Paradex's funding feed is a high-frequency
  index (not fetched); Drift's data host did not resolve.
- Coins: BTC, ETH, SOL, XRP, DOGE, AVAX, LINK, SUI, ARB, OP, LTC, BNB (those a venue lacks are skipped).

## Data
Hourly funding rates 2024-11-01 .. 2026-10-31 from each venue's public API (`scripts/fetch_fallback.py funding`), normalised to a rate per hour
(Gate's 8-hour rate ÷ 8, assigned to each hour of its interval).

## Rule (decided now)
- Daily, for every coin and venue pair: signal = mean hourly funding over the past 24 h on venue A minus venue B, annualised.
- **Open** when |signal| ≥ 15%/yr: short the higher-funding venue, long the lower, notional $N each leg. **Close** when the signal changes
  sign (or the coin's data stops). Earned P&L per hour = (funding_high − funding_low) × N while open (funding paid by longs to shorts).
- **Costs:** 0.05% taker fee per leg per side (open 2 legs + close 2 legs = 0.20% of N per round trip). Price difference between venues at
  entry/exit is not modelled (assumed mean zero; stated as a limit).
- **Capital:** 3× leverage on each leg → capital = 2N/3 per position. Portfolio: at most 5 positions open at once (first signals first),
  capital split in 5 slots; idle slots earn 0.
- **Window halves:** 2024-11..2025-10 and 2025-11..2026-10.

## Pass (tested set = the three DeFi pairs pooled in one portfolio)
- Stage 1 (2026-08..10): KILL if return on capital < 4.0%/yr.
- Stage 2: PASS if return on capital ≥ 8.0%/yr in both halves after fees, AND ≥ 20 round trips per half.
Reported: per-pair results, HL–Gate (not eligible), $ per year on $10K/$40K, worst month, share of time invested.
Limits: execution (both legs fill at the same time), venue risk (exchange failure, dYdX/Aevo liquidity on alts), liquidation at 3× on a
~30% move against one leg before rebalancing; none are in the P&L.

Command: `uv run python scripts/fundgap_20261121.py | tee docs/jx_runs/fundgap_20261121.txt`

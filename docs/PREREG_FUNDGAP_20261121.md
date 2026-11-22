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

## Addendum 1 (2026-11-21, before the funding data arrived; found with synthetic data only)
A synthetic check showed that a gap that stays open for months never completes a "round trip", so the repeatability condition would fail a
strategy that earns continuously. Condition (b) is replaced by: **≥ 20 positions opened in each half, OR invested on ≥ 50% of days in each
half**. Thresholds, costs and the 8%/yr bar are unchanged. No real funding data had been fetched when this was written.

## Result (2026-11-21, `docs/jx_runs/fundgap_20261121.txt`, re-run identical): FAIL
Pooled HL/dYdX/Aevo: 111 / 124 positions opened by half, invested all the time; **13.8% / 4.4%/yr on capital** (Stage 1 7.6%); worst month −1.0%.
Pairs alone: HL–dYdX −2.7% / −8.9% (fees exceed the gap), HL–Aevo 3.6% / 1.5%, dYdX–Aevo 4.9% / −0.8%. The gaps that paid in 2024–25 closed in
2025–26. HL–Gate (report only) not measured: Gate refused the history request (HTTP 4xx). Second half below 8% → FAIL.

## Addendum 2 (2026-11-22): fee bug found and fixed — corrected result PASSES the original rule
The refinement study (R1) re-implemented the rule and got a different number for the original configuration. Cause: the script set FEE_SIDE = 0.001
and charged FEE_SIDE × 2 on every open and every close = 0.40% of notional per round trip, twice the registered 0.20% (0.05% per leg per side).
Fixed (FEE_SIDE = 0.0005); no other change. **Corrected result (`docs/jx_runs/fundgap_20261121_feefix.txt`, re-run identical):** 111 / 124 positions
opened by half; Stage 1 13.30%; **halves 20.30% / 11.87% on capital → PASS**; worst month +0.04%; ~$6.4K/yr on $40K. Per pair: HL–dYdX 8.6% / 2.2%,
HL–Aevo 10.8% / 6.0%, dYdX–Aevo 13.0% / 7.2% (the pass needs the Aevo pairs). Sensitivity (labelled, `docs/jx_runs/fundgap_sens_20261122.txt`):
fees ×1.5 → 17.1% / 8.2% (still passes), ×2 → 13.8% / 4.4% (fails), ×3 → fails. **Not modelled and decisive in practice:** price difference between
venues at entry and exit, slippage on Aevo's thinner order books, simultaneous execution of both legs, moving collateral between venues, liquidation
of a 3× leg on a large move, venue risk. The earlier FAIL in NOTES/CANDIDATES was caused by the bug and is superseded.

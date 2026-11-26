# Batch E (#447): Pendle PT dislocation buying — pre-registered 2026-11-26, before its data are fetched

**Why only one idea.** Batches C and D (16 ideas plus variants) produced 0 passes. Every published flow or calendar anomaly failed out
of sample, and wave 3 (#392–#401) is fully resolved. This time I screened the remaining untested space by "who pays":
forced sellers, issuers, protocols, funding payers, impatient traders, lottery buyers, brokers and governments.
Only one candidate cleared the quality gate (`docs/NOTES_NONPROP.md`). Rejected candidates are listed at the end. Jx said not to pad.

| # | Idea | Gate |
|---|---|---|
| 447 | **Buy Pendle PTs when their implied yield spikes** | (1) **Forced seller:** leveraged PT loops (PT used as collateral on Morpho/Aave/Euler) unwind or are liquidated when borrow rates jump, which dumps PT into thin Pendle AMMs. (2) **Persistence:** PT pools are small; big money can't use them; the convergence is contractual (a PT redeems 1:1 for the underlying at maturity, with no permission needed). (3) A 5-point yield spike on a 3–6-month PT is a ~1.5–3% price dislocation; hundreds of markets give 100+ events/yr. (5) Pendle is usable from Malaysia. (6) Split by time. Different from #211 (#211 held every stable PT to maturity as carry and failed on depegs). This one buys only after forced selling and sells on reversion. |

## Rule (#447)
- **Data:** Pendle API, every market on every chain, active and expired, expiring ≥ 2024-03-01.
  Daily history (implied APY, TVL), plus the underlying's daily USD price from DefiLlama. Job `upendle`.
- **Universe (main):** markets whose name matches the stablecoin pattern of #211 (`usd|dai|gho|frax|usr|usx|ausd|usde|usdai|usdf|usdg|usd0|eusd|deusd|reusd|syrup`).
- **Signal on day t:** implied_t − median(implied over days t−14..t−1, ≥ 10 points) ≥ 0.05 (5 points), time to expiry ≥ 14 days,
  and TVL_t ≥ $1M.
- **Entry:** at the **next** daily point (t+1), so the signal is never traded on its own snapshot.
- **PT price in underlying units:** P = (1 + implied)^(−years to expiry). It equals 1 at expiry.
- **Exit:** at the first daily point after entry where implied ≤ (median at signal + 0.01), or after 30 days, or at expiry
  (redeemed at 1.0).
- **Return (USD):** (P_exit × U_exit) ÷ (P_entry × U_entry) − 1 − 0.4%. U is the underlying's USD price, so depegs are charged.
  The 0.4% covers AMM impact and gas, 0.2% per side. One open position per market.
- **Stage 1 (kill-only):** signals 2024-03-01..2024-12-31. KILL if fewer than 10 events or mean ≤ 0.
- **Stage 2 (PASS):** signals 2025-01-01..2026-10-31. PASS only if all of these hold:
  - ≥ 30 events;
  - mean ≥ +1.0%;
  - t ≥ 2;
  - ≥ 65% profitable;
  - ≥ $10K/yr at $5,000 per event, with at most 3 open at once (first come, first served).
- **Variants (reported only, cannot rescue a fail):**
  - threshold 3 points or 8 points;
  - same-day entry;
  - non-stable PTs (ETH/BTC/HYPE derivatives), judged in underlying units.

## Screened out at the gate this round (not tested; reason)
| Candidate | Gate | Why |
|---|---|---|
| Curve LLAMMA soft-liquidation arbitrage | 2 | atomic MEV race |
| Liquity v2 redemption arbitrage | 2 | atomic bots |
| Perp-DEX liquidation takeovers (Orderly etc.) | — | liquidation-bonus family = workstream B (not touched) |
| Volume-prize trading competitions on zero-fee DEXes | 6 | prize allocation unknown in advance (points family, not measurable) |
| Reverse-split round-up | 3 | ~$1–3K/yr per identity; scaling needs more identities |
| Exchange rebate capture (IBKR tiered) | 2 | HFT-dominated |
| Bond / CEF NAV-discount reversion | 3 | published alpha 5–10%/yr unlevered; the stale-NAV artefact risk is the same as #429 |
| HL / dYdX delist settlements | 5 | reduce-only mode prevents opening the convergence trade |
| OI-crowding "front-run the cascade" | 1, 6 | close kin of #432/#433/#427, all killed |
| Dual-investment strike pinning (08:00 UTC) | 2 | BTC/ETH, professionally hedged |
| Emission-inflation cross-section | 6 | free supply history limited to 365 days; kin of failed unlock shorts |
| Odd-lot tenders | 4, 3 | ~20 events/yr, $3–8K/yr; SEC access needs a contact e-mail (parked as #326) |
| Spectra / Napier / Exponent PTs | — | same mechanism as #447. Only used as a second venue if #447 passes. |

Script `scripts/batch_e_20261126.py`; output `docs/jx_runs/batch_e_20261126.txt` (re-run once, identical).

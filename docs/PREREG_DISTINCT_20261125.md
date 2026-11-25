# #412–#413: two more distinct mechanisms — pre-registered 2026-11-25, before their data are fetched

Why: Jx counts variants of one mechanism as one idea (the wick family #389/#397/#403/#410 = one). By the same rule the listing-event
shorts #393/#394/#395 are one family. Families not killed so far: wick buying; listing-event shorts (Stage 2 pending); pre-launch perp
shorts (#385); launch-phase vaults (#383, below bar). #409 (cross-venue gaps, `docs/PREREG_FIVE_HIGH_20261125.md`) and these two are
different mechanisms. Stage 1 kill-only; Stage 2 before any claim.

## #412 Korean-premium spikes (relative mispricing Upbit KRW vs Hyperliquid)
**Data.** Upbit daily candles for every listed KRW market + KRW-USDT (Upbit public quotation API, days start 00:00 UTC); Hyperliquid daily
closes; Binance USD-M daily closes for Stage 2. **Signal.** premium = Upbit KRW close ÷ KRW-USDT close ÷ Hyperliquid close − 1; spike =
premium − its own trailing 30-day median ≥ 5 percentage points, the token listed on Upbit ≥ 30 days earlier (so #395's listing events are
excluded). **Rule.** Short the Hyperliquid perp at that day's close, hold 7 days, equal BTC long hedge, 4 × 0.045% + funding; one position
per token at a time. **Stage 1 (Hyperliquid 2023-06..2026-10):** with ≥ 15 events KILL if mean < 1% or t < 1; < 15 not testable.
**Stage 2 (Binance 2020-01..2023-05, premium vs Binance close):** PASS if ≥ 15 events, mean ≥ 2%, t ≥ 2.

## #413 Withdrawal-queue discounts, Stage 1b of #384 (hourly prices)
**Data.** DefiLlama hourly prices (`period=1h`, same timestamps for token and underlying) 2024-01..2026-11 for kHYPE, stHYPE, beHYPE, ezETH,
rsETH, weETH, pufETH, sUSDe and HYPE / ETH / USDe. **Rule.** #384 unchanged except: hourly ratio; NAV proxy = trailing 720-hour max;
event = ratio ≥ 1.0% below it; size $5,000 per event (no volume data: deliberately small); redeem after the queue at the NAV proxy of
that hour, minus 0.10% and lost staking yield; one position per token at a time; one $15,000 pot. **Stage 1:** KILL if < 4 events or
< $3,000/yr. A survivor needs a forward paper check of the actual DEX quote for $5,000 before money.

**Commands.** `uv run python -m scripts.distinct_20261125` → `docs/jx_runs/distinct_20261125.txt` (re-run identical). Data job `udistinct`.

---
## Stage 1 results (2026-11-25) — `uv run python -m scripts.distinct_20261125` (data: fetch run 45650013333)
- **#412 Korean-premium spikes — survives Stage 1 (kill-only):** 54 events on 41 tokens, mean +2.53% (median +4.26%), t 2.10, win 69%,
  worst −29.6%; 2024 n 2 −16.7%, 2025 n 40 +3.24%, 2026 n 12 +3.40%. **Stage 2 as registered could not run:** Upbit's KRW-USDT market (the
  registered exchange rate) has no history before 2023, so 2020–23 has no events. Not a pass.
- **#413 withdrawal discounts (hourly) — printed "survives" ($19,168/yr, 372 events, 0 losing) but the measurement is not credible:**
  the redemption value is the token's own trailing 30-day maximum price, so any discount is assumed to close by construction (zero losers is
  the symptom), and a real NAV drop (e.g. rsETH 2026-04, beHYPE 2026-06) is booked as profit. Needs the protocols' on-chain exchange rates
  (Stage 1c) before it counts either way. Recorded as **invalid measurement**, not a survivor.

## #412 Stage 2b — pre-registered 2026-11-25 before running it
Same rule and bars as Stage 2, but the KRW→USD rate = Upbit KRW-BTC close ÷ Binance BTCUSDT close (a BTC-implied rate that exists back to
2020; it carries BTC's own Korean premium, so a spike now means the token's premium rising ≥ 5 points relative to BTC's, against its own
30-day median). Window 2020-05..2023-05 on Binance USD-M perps. PASS if ≥ 15 events, mean ≥ 2%, t ≥ 2. Also reported for context: Stage 1
re-run with this rate on Hyperliquid.
- **#412 Stage 2b — FAIL** (`docs/jx_runs/distinct_20261125.txt`, re-run identical): Binance 2020-05..2023-05 with the BTC-implied rate,
  112 events on 23 tokens, mean −1.20%, median −0.62%, t −1.07 (2020 +0.43%, 2021 −4.04%, 2022 +1.85%, 2023 −1.79%). Context: Stage 1 with
  the same rate on Hyperliquid 60 events +1.22%, t 1.03. The 2025–26 effect did not exist before → #412 is dead.

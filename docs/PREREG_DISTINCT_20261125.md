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

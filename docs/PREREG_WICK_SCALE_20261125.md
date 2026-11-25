# #402–#404: scaling and hardening #389 (resting bids under wicks) — pre-registered 2026-11-25, before their data are fetched

Why: Jx asked that the list be high-potential. Of everything tested, only #389 reached ~$15–19K/yr on $15K and passed out-of-sample
(Binance 2020–26). Its limits are capital turnover (one fill per coin per day), one venue's capacity, and losses in crash regimes.
These three tests attack exactly those limits. #389's own rule and verdict are unchanged.

## #402 Hourly wick bids (capital turnover)
**Data.** Binance USD-M 1h klines, every USDT perp in the archive (delisted included), 2022-01..2026-10 — the fills are computed inside the
Actions job and only fills are saved; Hyperliquid 1h candles for every perp (API limit ≈ last 200 days) as a second venue.
**Rule.** Each hour, a resting bid at the previous hour's close × (1 − X); filled only on a print ≥ 0.5% below the bid; fill at the bid (or
the open if it opened below); sold at that hour's close. X = 8% primary; 5% and 12% context. Size min($1,500, 1% of the previous UTC day's
USD volume / 24 × 24) = min($1,500, 1% of the previous day's USD volume) per fill; a $15,000 pot per hour (capital returns at the hour's
close). Costs 0.015% + 0.045%. Perps ≥ 30 days old.
**Stage 1 (kill-only), Binance 1h:** KILL if mean net per fill < 0.3%, t < 3, or < $3,000/yr. Context: per-year, half-years, worst
peak-to-trough on the pot. Hyperliquid 1h (last ~200 days) is reported as a second-venue check, not a verdict.

## #403 Same daily rule on other perp venues (capacity + a third out-of-sample market)
**Data.** Daily candles from the public APIs of dYdX v4 (indexer), Aster (Binance-style futures API), Lighter, Paradex — every market each
returns, as far back as each allows. Stage 0: each venue's access for a Malaysian resident (terms / restricted-country list) is checked and
reported; a venue that excludes Malaysia is reported but does not count.
**Rule.** #389 unchanged (X 15%, 0.5% trade-through, first 30 days excluded, size min($1,500, 1% of the previous day's USD volume — the
look-ahead-free version), $15,000 pot, Hyperliquid fee levels as a stand-in).
**Stage 1 (kill-only), per venue with ≥ 1 year of data:** KILL the venue if mean net per fill < 0.5% or t < 3. Report $/yr per venue and
the combined $/yr if bids run on every surviving, Malaysia-eligible venue with separate $15,000 pots.

## #404 Crash-regime guard (judged only on the #403 venues, which #389 has not seen)
Two guards, fixed now: **G1** — post no bids on day d if on day d−1 at least 25% of the venue's eligible perps wicked ≥ 15% (the #397
cascade definition); **G2** — cap the day's total fill notional at $5,000 instead of $15,000. Measured on each #403 venue against the
unguarded rule: worst peak-to-trough, worst day, $/yr. A guard is **adopted** only if, pooled over the #403 venues, it improves the worst
drawdown by ≥ 30% while keeping ≥ 70% of the unguarded $/yr. Hyperliquid/Binance results for the guards are printed as context only
(they were seen when the guards were designed).

**Commands.** `uv run python -m scripts.wick_scale_20261125` → `docs/jx_runs/wick_scale_20261125.txt`; re-run once, identical. Data: Actions
job `uscale`.

# #468 confirmation on unseen perps — pre-registered 2026-11-26, before the data are fetched

**Why.** #468 (funding-settlement pressure, `docs/PREREG_BATCH_H_20261126.md`) passed its pre-registered Stage 2 on the 40
`batchd_alts` perps:
- result: mean 0.128% per settlement timestamp, t 2.29, n 1,585, about $23.9K/yr at $45K;
- the PASS stands as recorded.

The diagnostics (in `docs/jx_runs/batch_h_20261126.txt`) make it fragile:
- the median timestamp is −0.055%;
- dropping the 10 best timestamps leaves mean 0.049%, t 0.97;
- all of the profit is on the long side (negative funding → long into settlement); the short side lost −0.09% per event;
- AXS and ZEC give about 45% of the sum.

Before #468 counts toward Jx's two, it must replicate on coins it has never seen and show it can be traded on Hyperliquid.

**Data (job `ubatchh2`, via `fetch_public.yml`):**
- **Unseen universe.** Every Binance USDⓈ-M perp ending in USDT that:
  - is listed in the data.binance.vision archive and has a 1h kline file for 2022-12 (so it was listed before the test window);
  - is not among the 40 `batchd_alts`;
  - is not an index contract (names containing DOM, DEFI, BLUEBIRD or FOOTBALL);
  - is not a stablecoin base (USDC, BUSD, TUSD, FDUSD, USDP).

  Delisted symbols are included (no survivorship filter). For each: 1h klines and funding for 2023-01..2026-10.
- **Hyperliquid 1h candles.** `candleSnapshot` (last 5,000 hours, about 2026-04..2026-11) for every coin in either universe that
  Hyperliquid lists.

**Rule.** Identical to #468:
- signal = the rate settled at the symbol's previous funding time; if it is ≥ +0.05% → short from T−2h to T; if ≤ −0.05% → long;
- net = side × return − 0.09%;
- events at the same T are averaged into one observation.

**Pass criteria.** C1 counts toward the verdict; C2 is reported only:
- **C1, replication (unseen universe, 2023-01..2026-10).** All four must hold:
  - ≥ 300 timestamps;
  - mean ≥ 0.05% per timestamp;
  - t ≥ 2;
  - the mean stays > 0 after dropping the 10 best timestamps.
- **C2, venue check (reported, low power).** The same signals (Binance funding), priced with Hyperliquid 1h closes for coins on both
  venues, over the Hyperliquid window. Report n, mean and t.

**Verdict.**
- **#468 confirmed** if C1 holds. It then counts as a new family, with $/yr reported at $45K per timestamp from the combined
  universe and C2 as the venue caveat.
- **#468 fails confirmation** if C1 fails. It is then recorded as "PASS on its own sample, failed confirmation" and does not count.

**Script and output.** Script: `scripts/batch_h_20261126.py` (`part468c`). Output: `docs/jx_runs/batch_h_20261126.txt` (re-run once; it must be identical).

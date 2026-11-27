# Batch L (#501–#504): exchange risk-parameter forced closes — pre-registered 2026-11-27, before any of their prices are fetched

**Gate (Jx's calibration, as Batches F–K):** a named structural payer; free data; a venue usable from Malaysia; a genuine time split.
$/yr is reported at a safe size, and only passes ≥ ~$10K/yr count toward Jx's goal.

**New family (none of the ~500 earlier ideas used it; checked by keyword search of every PREREG file).** When Binance changes a risk
parameter on a coin, holders are forced to cut or close positions on Binance's timetable, not on price:
- cutting maximum leverage forces de-leveraging;
- delisting a perp or a margin pair forces every open position closed;
- lowering a coin's collateral ratio forces margin calls on holders using it as collateral.

Holders of these coins are mostly long, so the forced side is selling. **Payer:** over-leveraged holders forced out on a schedule.
All four ideas are one family and count as one.

**Events.** Binance announcement catalog `data/public/uncharted_w3_binance_ann.json` (3,700 titles, 2022-10..2026-11, stored before
this batch). Titles are selected by pattern; article bodies are fetched once (Binance CMS detail API, via GitHub Actions) only to read
the symbols, dates and ratios they name. Counts from titles, before any price was seen:
| # | Idea | Title pattern | Titles (2022 / 23 / 24 / 25 / 26) |
|---|---|---|---|
| 501 | **Leverage-tier cuts** | "Leverage & Margin Tiers" | 7 / 30 / 53 / 59 / 25 |
| 502 | **Perp delistings** (USDⓈ-M) | "Futures Will Delist" with a USDT symbol in title or body | 23 titles with USDT symbols named in the title |
| 503 | **Margin-pair delistings** | "Margin Will Delist" | 6 / 20 / 1 / 0 / 3 |
| 504 | **Collateral-ratio cuts** | "Collateral Ratio" | 0 / 1 / 8 / 49 / 38 |

**Exact rule (all four).**
- A = announcement time. Prices are Binance USDⓈ-M perpetual 1-hour closes (data.binance.vision archive).
- **Entry:** the close at T_e = A rounded up to the hour + 1 h.
- **Short the coin** and hold to T_x. **Excess** = −(coin return − BTCUSDT return over the same window) − 0.09% round trip.
- Coins in one announcement are averaged, so one announcement is one event. If the perp stops trading before T_x, exit at its last close.
- **Exit time T_x:**
  - #501: T_e + 72 h.
  - #502: the delist date in the title (or else the body), 09:00 UTC, capped at T_e + 14 days; otherwise T_e + 72 h.
  - #503: the date in the title, 06:00 UTC, same cap.
  - #504: T_e + 72 h, only for coins whose collateral ratio is *lowered*. Read from body lines that carry the coin and two percentages
    (old, new). If no body yields readable rows, #504 is reported as not testable.
- **Symbols:**
  - #501/#502: any `<COIN>USDT` named in the title or body that has a USDⓈ-M archive.
  - #503: the title's coin + USDT.
  - BTCUSDT and the stablecoins are excluded as shorts.
- **Variant (reported only):** #501 restricted to bodies containing "reduce", "lower" or "decrease".

**Stages.**
- **Stage 1 (dev): announcements before 2025-01-01.** KILL if mean excess ≤ 0. With fewer than 8 events, no kill, and say so.
- **Stage 2 (out of sample): announcements 2025-01-01 → 2026-11-27.** PASS if ≥ 15 events, mean excess ≥ 1.0% and t ≥ 2.
  - Also report Stage 2 restricted to coins with a Hyperliquid perp (`data/public/hl_coins`). Hyperliquid is the Malaysia-usable
    venue to short; a pass must hold there too.
- **$/yr** = mean excess × $5,000 per event × Stage-2 events per year (at most 5 open at once).

Stage 1 only kills; nothing passes early; Stage 2 rules are fixed now.

**Data job:** `ubatchl` (`scripts/fetch_uncharted.py`), run through `fetch_public.yml`.
- Outputs: `data/public/batchl_bodies.json`, `data/public/batchl_events.json`, `data/public/batchl_1h.parquet`.
- Months fetched: each event's month and the next, for each symbol; BTCUSDT for all months 2022-10..2026-11.

**Script/output:** `scripts/batch_l_20261127.py` → `docs/jx_runs/batch_l_20261127.txt` (re-run once; identical).

## Addendum 1 (2026-11-27, before any #504 price was seen): parser fix for #504, rule unchanged
- Binance's collateral tables arrive flattened one cell per line (coin / before % / after %). The registered reader looked for all
  three on one line, so it found no rows, and the fetch job pulled no prices for those coins.
- `collateral_cuts()` in `scripts/fetch_uncharted.py` now reads both layouts and is shared by the fetch and the analysis. It finds
  cuts in 73 of 96 #504 announcements.
- The rule (short coins whose ratio is lowered, 72 h, excess vs BTC − 0.09%) and every threshold are unchanged. The fetch is re-run
  for the new symbols. #501–#503 use the same data and must reproduce their first-run figures exactly.

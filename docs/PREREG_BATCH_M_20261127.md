# Batch M (#505–#508): Malaysia-tradable forced and seasonal flows — pre-registered 2026-11-27, before any of their outcomes are computed

**Gate (as Batches F–L):** a named structural payer; free data; a venue usable from Malaysia; a genuine time split.
$/yr is reported at a safe size; only passes ≥ ~$10K/yr count.

**Lesson from Batch L:** the strongest forced-flow effects (#482, #502) sit on coins only shortable on exchanges closed to Malaysia.
Batch M keeps to trades Malaysia can place: buying spot on a DEX, FX, US ETFs.

Each idea was checked against every earlier PREREG file by keyword search (repatriation, tax day, post-delisting, Diwali/festival);
none was tested before. Two ideas first drafted for this batch had been tested and were dropped: CME bitcoin expiry (#465) and
Japanese month-start buying (#466).

| # | Idea (payer) | Exact rule | Stage 1 (dev) KILL if | Stage 2 (unseen) PASS if |
|---|---|---|---|---|
| 505 | **Rebound after a perp delisting** (forced closers are gone once the perp settles; #502 showed the selling runs up to the settlement) | Events: #502's Stage-2-style perp delistings with the `<COIN>USDT` symbol in the title (`batchl_events.json`), exit time T_x as #502. Long Binance **spot** `<COIN>USDT` from the close at T_x + 1 h for 7 days. Excess = coin − BTCUSDT − **0.6%** (DEX round trip). Coins in one announcement averaged | delistings announced before 2025: mean ≤ 0 (< 8 events: no kill) | 2025–2026-11: ≥ 12 events, mean ≥ 2%, t ≥ 2 |
| 506 | **Japanese fiscal-year-end repatriation** (Japanese companies and institutions bring foreign earnings home before the 31 March year-end; price-insensitive yen buying) | Long JPY (short USD/JPY, FRED DEXJPUS) from the last business day ≤ end of February to the last ≤ 31 March. Return = −(USDJPY_end / USDJPY_start − 1) − carry − 0.003%. Carry = (US − JP 3-month rate, OECD IR3TIB01, February value) / 12 | 2002–2013 (JP rate starts 2002-04, so the first event is 2003): mean ≤ 0 | 2014–2026: mean ≥ 0.5%, t ≥ 2 (13 events; low power stated). Variant (reported only): half-year end, last business day ≤ 31 Aug → last ≤ 30 Sep |
| 507 | **US tax-payment selling** (individuals sell assets to pay capital-gains tax by the federal filing deadline) | Short SPY from the close 10 trading days before the deadline to the close on the deadline (last trading day ≤ it). Deadlines: 15 April rolled to the next business day, except 2007-04-17, 2011-04-18, 2012-04-17, 2016-04-18, 2017-04-18, 2018-04-17, 2020-07-15, 2021-05-17, 2022-04-18, 2023-04-18. Return − 0.04% | 2001–2012: mean ≤ 0 | 2013–2026: mean ≥ 0.5%, t ≥ 2 (14 events; low power stated). Variants (reported only): long SPY deadline → +10 trading days (rebound); BTC (daily) same windows 2015–2026 |
| 508 | **Gold before Diwali** (Indian festival jewellery and bar buying is price-insensitive and concentrated in the weeks before Diwali; India is the second-largest consumer) | Long GLD from the close 15 trading days before Diwali (Lakshmi Puja) to the last close ≤ Diwali. Return − 0.04%. Dates (from public calendars, ±1 day): 2004-11-12, 2005-11-01, 2006-10-21, 2007-11-09, 2008-10-28, 2009-10-17, 2010-11-05, 2011-10-26, 2012-11-13, 2013-11-03, 2014-10-23, 2015-11-11, 2016-10-30, 2017-10-19, 2018-11-07, 2019-10-27, 2020-11-14, 2021-11-04, 2022-10-24, 2023-11-12, 2024-11-01, 2025-10-20, 2026-11-08 | 2004–2014: mean ≤ 0 | 2015–2026: mean ≥ 1%, t ≥ 2 (12 events; low power stated) |

**Safe size for $/yr:** #505 $3K per event (illiquid DEX tokens, at most 5 open); #506 $150K notional; #507 $30K; #508 $45K.

**Families:** #505 belongs to the Batch L forced-close family; #506–#508 are each separate calendar-flow families.

Stage 1 only kills; nothing passes early; Stage 2 rules are fixed now.

**Data:**
- Existing: `batchl_events.json`, `batchl_1h`, `batchg_dexjpus`, `batchi_ir3m`, `batchg_etf_1d` (SPY), `batchg_btc_1d`.
- New job `ubatchm`: Yahoo GLD daily 2004–2026, and Binance spot 1h for #505 symbols (event month and the next) plus BTCUSDT spot.

**Script/output:** `scripts/batch_m_20261127.py` → `docs/jx_runs/batch_m_20261127.txt`, re-run identical.

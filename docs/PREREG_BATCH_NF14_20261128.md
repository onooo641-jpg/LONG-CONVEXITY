# Batch NF14 (#589–#597): thin permissionless perp venues never tested — pre-registered 2026-11-28, before any data is fetched

**Why:**
- Jx, 2026-11-28: national markets are "too general and popular".
- Every pass so far (#389, #520, #536) came from thin crypto venues with few professional market makers. Forced sellers there
  (liquidations, points farmers dumping) hit empty books.
- Venues already tested: Hyperliquid, Aster, dYdX, Orderly (Batch B), Binance (evidence only). Lighter and Paradex had no candles.
- **New here:** Drift (Solana), Bluefin (Sui), Apex Omni, edgeX, Extended, Pacifica, Backpack.

**Desk checks:**
- **G5:** resting limit buys on the venue are filled by the forced seller directly.
  - Drift, Bluefin, Apex Omni, edgeX, Extended and Pacifica are wallet-connected, with no KYC. Malaysia is not on their restricted
    lists as far as known (**unverified; checked before any live use**).
  - Backpack needs KYC, and its country list is unverified. It is tested for evidence and flagged unless access is confirmed.
- **G6:** capacity is tiny ($1,500 or 1% of volume per fill), too small for funds.
- Venues whose candle API returns nothing are reported "not testable". Nothing is substituted for them.

**Data (job `ubatchnf14`, GitHub Actions):**
- Each venue's public candle endpoint, daily bars, full history, every perp market, saved as `batchnf14_<venue>_1d.parquet`
  (coin, t ms, o, h, l, c, v_usd).
- **Hyperliquid daily bars:** `uncharted_385_candles.parquet`, through 2026-11-25.
- **Coin names** are normalised (upper case; -PERP, USDT, USD, _USDC_PERP and 1000/k prefixes removed) only to match HL for #597.

**Costs:** 0.02% maker + 0.05% taker per round trip on every venue (most charge less maker; Backpack and Apex charge more taker).
×1.5 is reported as a stress.

**Shared wick rule (#520):**
- Each day: resting buy at previous close × (1 − X), with X = 4·σ30 (30-day stdev of daily close returns, previous days only),
  clipped 5%..30%.
- **Fill** if low ≤ level × (1 − 0.5%); price = min(level, open). **Exit** at the close.
- A market needs ≥ 30 days of history before its first bid.
- **Size:** min($1,500, 1% of the day's USD volume); $15,000 pot per day, pro rata.

| # | Idea | Universe / rule |
|---|---|---|
| 589 | #520 on **Drift** | shared wick rule |
| 590 | #520 on **Bluefin** | shared wick rule |
| 591 | #520 on **Apex Omni** | shared wick rule |
| 592 | #520 on **edgeX** | shared wick rule |
| 593 | #520 on **Extended** | shared wick rule |
| 594 | #520 on **Pacifica** | shared wick rule |
| 595 | #520 on **Backpack** perps | shared wick rule |
| 596 | **#536 on all seven, pooled** (new listings) | Days 1–30 after a market's first candle; markets whose first candle is within 30 days of the venue's first candle are dropped (true listing unknown). Fixed X = 15%, no 30-day history requirement; otherwise as the shared rule |
| 597 | **Venue discount to Hyperliquid** (cross-venue convergence, hedged) | Daily close on the venue ≥ 3% below HL's daily close for the same coin: buy on the venue, short on HL at the closes; exit both at the next daily close. Return = venue leg − HL leg − 4 × 0.035% (two round trips). $1,500 per event, $15,000 pot per day |

**Split:** Stage 1 = days before 2025-07-01, Stage 2 = 2025-07-01..2026-11-25 (unseen). Per-venue windows start at the venue's
first data.

**Stage 1 KILL:** ≥ 30 fills and mean net ≤ 0.3%. With < 30 Stage 1 fills there is no kill, and Stage 2 decides.

**Stage 2 PASS:** all of
- ≥ 30 fills;
- mean net ≥ 0.3%;
- t ≥ 2;
- ≥ $1,000/yr (thin venues; the radar forward log, not the size, decides go-live);
- sum positive without the 3 best days;
- mean > 0 with costs × 1.5.

**Multiple testing:** seven venue tests of one rule. A single venue passing is reported as "PASS, 1 of 7". It goes to the forward
paper log only if its Stage 2 t ≥ 2.5. With t ≥ 2 alone, about 1 in 3 runs of seven null tests would produce one pass by luck.

**Also reported:** fills, median, win rate, $/yr without the best day, and a per-venue table for #596/#597.

**Script/output:** `scripts/batch_nf14_20261128.py` → `docs/jx_runs/batch_nf14_20261128.txt`, re-run identical.

## Addendum 1 (2026-11-28, before any data arrived): #597 unit check
A coin matched by name to HL counts only if the median of its daily close ratio (venue / HL) over all common days is between 0.95 and
1.05. This drops wrong matches (same ticker, different asset) and unit mismatches (kPEPE vs 1000PEPE vs PEPE), which would otherwise
show up as a permanent "discount". It is a data-validity rule written before any venue data was seen.

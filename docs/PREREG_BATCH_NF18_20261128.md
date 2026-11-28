# Batch NF18 (#614–#618): the same equity, pre-IPO or commodity perp on several thin venues — pre-registered 2026-11-28, before any hourly data for these markets is fetched

**Why:**
- Hyperliquid's builder-deployed (HIP-3) dexes and GRVT list the **same assets** several times over: NVDA on xyz, km, flx, cash, io
  and GRVT; ANTHROPIC on vntl, io, para, xyz and GRVT; gold on five books.
- Each book is thin and retail, and nothing forces the copies together outside US cash hours:
  - pre-IPO names have no underlying at all;
  - stocks have none at night and on weekends.
- Untested here:
  - #284 tested HIP-3 cross-dex **funding** gaps, not prices;
  - #300 found pre-IPO carry unhedgeable;
  - the weekend fades in Batch C covered commodities and indices, not single stocks.
- **NF16 lesson built in:** every gap trade enters **one hour after** the signal, at the next hour's closes. A gap made of stale
  last prints in a thin book cannot pay that way.

**Desk checks:**
- **G5:** HL needs no KYC. GRVT is self-custodial (wallet). Equity perps are synthetic; no securities are bought.
- **G6:** the books are new (2025–26) and small.
- Fees: HIP-3 charges about 2× HL's base taker fee. A conservative 0.10% per side per leg is used.

**Data (job `ubatchnf18`, GitHub Actions):**
- **HL HIP-3:** `perpDexs` → `meta` per dex; hourly candles, last 5,000 hours (about 2026-05..2026-11-28), for every HIP-3 market
  whose normalised name (rule below) appears on at least two venues, or on HIP-3 and GRVT.
- **GRVT:** hourly klines (`CI_1_H`, TRADE) over the same window for every GRVT perp whose name matches such a market.
- Files: `batchnf18_hip3_1h.parquet`, `batchnf18_grvt_1h.parquet` (venue, market, key, t, o, h, l, c, v_usd).

**Name rule:**
- Key = upper-case name without the dex prefix (`xyz:`) and without `_USDT_Perp`, then mapped by this alias table:

| Key | Aliases |
|---|---|
| ANTHROPIC | ANTHROPIC, ANTH, ANT |
| OPENAI | OPENAI, OAI |
| GOLD | GOLD, XAU, XAUT |
| SILVER | SILVER, XAG |
| WTI | WTI, CL, OIL, USOIL |
| BRENT | BRENTOIL, BZ |
| SP500 | US500, USA500 |
| NDX | USTECH, USA100 |
| R2000 | SMALL2000 |
| NATGAS | GAS, NATGAS |
| PLATINUM | PLATINUM, XPT |
| PALLADIUM | PALLADIUM, XPD |
| TENCENT | TENCENT, TCNT |
| SKHYNIX | SKHYNIX, SKHX |

- **Classes:**
  - pre-IPO = ANTHROPIC, OPENAI, SPACEX;
  - commodity/index = the other keys in the table, plus COPPER;
  - equity = any other key, except crypto: keys that are Hyperliquid main-dex perps, keys listed on the crypto-only `hyna` dex, and
    keys whose GRVT `asset_class` is CRYPTO (saved in `batchnf18_grvt_classes.json`).
- **Unit check:** for each pair of markets with one key, the median price ratio over hours where both traded must be in 0.95..1.05,
  otherwise the pair is dropped (e.g. SPY vs US500).

**Common gap rule (#614–#617):**
- **Traded hour** = high > low and USD volume ≥ $5,000 (HIP-3 volume = v × close).
- **Signal** at hour h: both markets of a pair traded, and cheap close ≤ (1 − X) × rich close.
- **Entry** at the hour h+1 closes: both must trade at h+1; no condition on the gap at h+1. Long the cheap market, short the rich one.
- **Exit** at the first hour ≥ h+5 where both trade, up to h+9; otherwise the trade is dropped.
- **Return** = cheap leg − rich leg − 2 legs × 0.20% round trip (×1.5 stress reported).
- **Size** = min($1,500, 1% of the smaller leg's h+1 USD volume).
- One open trade per pair.
- Where a key has several pairs at once, only the widest gap that hour is taken.
- **US cash hours** = Monday–Friday, hours starting 14:00..20:00 UTC (DST ignored). Everything else is off-hours.

| # | Idea | Rule |
|---|---|---|
| 614 | **Pre-IPO cross-venue gap** | class pre-IPO, X = 3%, any hour |
| 615 | **Equity gap, off-hours** | class equity, X = 1%, signal hour off-hours |
| 616 | **Equity gap, cash hours** | class equity, X = 1%, signal hour in cash hours (oracle-anchored control) |
| 617 | **Commodity/index gap** | class commodity/index, X = 1%, any hour |
| 618 | **Single-stock weekend fade** | per equity key, the market with the highest median hourly USD volume. Weekend move m = close of Sunday's 21:00 UTC hour / close of Friday's 19:00 UTC hour − 1 (both traded hours). If \|m\| ≥ 3%, trade against m at the Sunday close and exit at the close of Monday's 15:00 UTC hour (after the cash open); that hour must trade. Return − 0.20% |

**Split:** Stage 1 = data start..2026-08-15 (kill only); Stage 2 = 2026-08-16..2026-11-25, unseen.

**Stage 1 KILL:** ≥ 20 trades (#614, #618) or ≥ 30 (others), and mean net ≤ 0.

**Stage 2 PASS:** all of
- ≥ 20 trades (#614, #618) or ≥ 30 (others);
- mean net ≥ 0.3%;
- t ≥ 2;
- sum positive without the 3 best trades;
- mean > 0 with costs × 1.5;
- the stale-print check: one key or one pair must not dominate, and both legs' bars at entry and exit must have real volume.

**Multiple testing:** five tests. Only a pass with Stage 2 t ≥ 2.5 goes to the radar forward log.

**Not modelled:**
- legs filling together;
- separate margin on each venue;
- GRVT–HL transfers;
- HIP-3 deployer risk (a deployer can halt a market).

**Script/output:** `scripts/batch_nf18_20261128.py` → `docs/jx_runs/batch_nf18_20261128.txt`, re-run identical.

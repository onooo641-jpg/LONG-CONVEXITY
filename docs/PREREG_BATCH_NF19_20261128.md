# Batch NF19 (#619–#622): gaps between thin crypto copies of the same coin, entered one hour late — pre-registered 2026-11-28, before any of this data is fetched or looked at

**Why:**
- **Jx (2026-11-28):** stocks are too public. NF19 stays crypto-native and thin.
- These are coins that trade as several thin copies:
  - on thin venues that HL does not list;
  - on HL's crypto HIP-3 dex `hyna` next to HL main;
  - on HL spot next to the HL perp;
  - on GRVT next to HL.
- **NF16 lesson:** every trade enters **one hour after** the signal, so a stale last print cannot pay.
- NF17's #610/#611 are the undelayed version against HL for four venues. NF19 covers different copies and adds the delay.

**Desk checks:**
- **G5:** wallet venues; Backpack needs KYC.
- **G6:** the copies are new and thin. The test measures whether arbitrage bots already close the gaps within an hour.
- Holding inventory is needed for the short spot leg (#621), as in #603.

**Data:**
- **#619:** NF15 hourly candles (Backpack, Extended, Pacifica, Apex; 2026-03..2026-11-25).
- **#620–#622 (job `ubatchnf19`):** hourly candles, last 5,000 hours, for:
  - every `hyna` market;
  - the HL main perp of every coin used in #620–#622;
  - every HL spot USDC book whose token maps to an HL main perp;
  - every GRVT perp with `asset_class` CRYPTO whose base is an HL main perp.
  - Also saved: the HL main-perp list (`batchnf19_main_perps.json`).
- **Files:** `batchnf19_{hyna,hlmain,hlspot,grvt}_1h.parquet` (venue, market, key, t, o, h, l, c, v_usd).

**Keys:**
- **NF14's `norm()`**, applied to the name without a dex prefix.
- **HL spot tokens:** key = name, or name without a leading "U" if that is a main perp (UBTC → BTC, UETH → ETH).
- **GRVT:** key = base.
- **Unit check** as NF18: median price ratio of each pair, over hours both traded, in 0.95..1.05.

**Gap engine (NF18's, unchanged):**
- **Traded hour:** high > low and USD volume ≥ $5,000.
- **Signal** at hour h: cheap close ≤ (1 − X) × rich close, both traded.
- **Entry** at the h+1 closes (both traded); long cheap / short rich.
- **Exit** at the first hour ≥ h+5 where both trade, up to h+9.
- **Size** = min($1,500, 1% of the smaller leg's h+1 volume).
- One open trade per pair; the widest gap per key and hour.
- **Costs per leg, round trip** (×1.5 stress reported):
  - HL main 0.09%;
  - HL spot 0.14%;
  - `hyna` 0.18% (HIP-3 2× fee);
  - GRVT, Backpack, Extended, Pacifica, Apex 0.10%.

| # | Idea | Pairs | X |
|---|---|---|---|
| 619 | **Thin-venue-only coins** | any two of Backpack/Extended/Pacifica/Apex, for keys **not** listed on HL main | 2% |
| 620 | **hyna vs HL main** | `hyna:COIN` vs main `COIN` | 1% |
| 621 | **HL spot vs HL perp** | spot USDC book vs main perp of the same token | 1% |
| 622 | **GRVT crypto vs HL main** | GRVT crypto perp vs main perp | 1% |

**Split:** Stage 1 = data start..2026-08-15 (kill only); Stage 2 = 2026-08-16..2026-11-25, unseen.

**Stage 1 KILL:** ≥ 30 trades and mean net ≤ 0.

**Stage 2 PASS:** all of
- ≥ 30 trades;
- mean net ≥ 0.3%;
- t ≥ 2;
- sum positive without the 3 best trades;
- mean > 0 with costs × 1.5;
- the stale-print check: no single key or pair dominates, and real volume on both legs at entry and exit.

**Multiple testing:** four tests, plus #614 in NF18. Only a pass with Stage 2 t ≥ 2.5 goes to the radar forward log.

**Not modelled:**
- legs filling together;
- margin on two venues;
- transfers.

**Script/output:** `scripts/batch_nf19_20261128.py` → `docs/jx_runs/batch_nf19_20261128.txt`, re-run identical.

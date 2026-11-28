# Batch NF26 (#647–#650): capped / extreme funding on thin venues, received hedged — pre-registered 2026-11-28, before these thresholds are run

**Why:**
- **Jx (2026-11-28):** look at funding caps.
- When a crowd pushes funding to a venue's cap (or near it), the side receiving funding is paid the capped rate for as long as the crowd
  stays. Taking the other side and hedging on another venue is legitimate: it is ordinary trading against a crowded position, with no
  price manipulation.
- #613 (NF17) tested spikes ≥ 100%/yr and failed (+0.04%/24h net). #423 (funding-cap crowding) was not testable.
- NF26 tests **cap-level** extremes, and persistence.

**Data:** NF17's `batchnf17_funding.parquet` (per-hour rates, NF17 units check passed) and NF15 hourly candles, with HL hourly.

**Engine:** NF17 #613's, unchanged.
- **Entry** at the hour's close; hold 24 hours.
- **Return** = funding gap received + both price legs − 2 legs × 0.07%.
- Traded bar ≥ $20K; unit check 0.95..1.05; one open trade per market.

| # | Idea | Trigger (rates per hour, annualised) |
|---|---|---|
| 647 | **Extreme venue funding** | venue \|rate\| ≥ 300%/yr and venue − HL gap ≥ 300%/yr, same direction → receive on venue, hedge HL |
| 648 | **Cap-level venue funding** | the same at ≥ 1,000%/yr |
| 649 | **Extreme HL funding, hedged on a thin venue** | HL \|rate\| ≥ 300%/yr and HL − venue gap ≥ 300%/yr → receive on HL, hedge on the thin venue (the hedge venue with the largest gap) |
| 650 | **Persistent spike** | #613's trigger (≥ 100%/yr both conditions) has held for ≥ 6 consecutive hours → enter at the 6th hour's close |

**Split:** Stage 1 = to 2026-08-15 (kill only); Stage 2 = 2026-08-16..2026-11-25, unseen.

**Stage 1 KILL:** ≥ 30 trades and mean ≤ 0.

**Stage 2 PASS:** all of
- ≥ 30 trades;
- mean ≥ 0.3%;
- t ≥ 2;
- sum positive without the 3 best trades;
- costs × 1.5 mean > 0.

**Multiple testing:** four tests plus #613. Only a pass with t ≥ 2.5 goes to the radar forward log.

**Script/output:** `scripts/batch_nf26_20261128.py` → `docs/jx_runs/batch_nf26_20261128.txt`, re-run identical.

## Result (2026-11-28; `docs/jx_runs/batch_nf26_20261128.txt`, re-run identical): **0 of 4 robust**

| # | Trigger | Stage 1 | Stage 2 | Verdict |
|---|---|---|---|---|
| 647 | venue ≥ 300%/yr | n 59, +0.11% | n 28, +0.04% | FAIL |
| 648 | venue ≥ 1,000%/yr | n 4 | n 3 | FAIL (too few) |
| 649 | HL ≥ 300%/yr, hedged on a thin venue | n 21, +0.17% | n 31, **+0.43% (t 2.77)**, $487/yr | printed PASS → **fragile, not forward-logged** |
| 650 | 6-hour persistent spike | n 72, +0.09% | n 49, +0.16% | FAIL |

**#649 check** (`scripts/batch_nf26_diag_20261128.py` → `docs/jx_runs/batch_nf26_diag_20261128.txt`, re-run identical):
- **Entering 1 hour after the signal:** Stage 2 −0.02% (t −0.09). **After 2 hours:** −0.11%.
- Funding received stays about +0.39%, but the price legs turn against the trade as the crowd unwinds.
- **Concentration:** one market (AITO) supplies 238% of the summed return.
- So the edge sits in the first hour and in one market. It is too fragile to log, and about $490/yr even as printed.

**Reading:**
- Funding caps do pay the receiving side (+0.4–0.5% per 24 hours at extremes), but the crowd's unwind moves prices by about as much.
- Funding received as a hedged carry is no edge on these venues. This matches #613 and #323.

**Not done, on purpose:**
- Self-referral and sybil wallets are rule violations. Avoiding detection is outside the standing rules.
- Exchange trial funds are not legally available here.
- Pushing an oracle or liquidation price is manipulation.
- Jx asked for these; they were declined, and the legitimate funding-cap version was tested instead.

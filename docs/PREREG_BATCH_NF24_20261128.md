# Batch NF24 (#639–#642): small reversal edges on a zero-fee thin venue (Paradex, hourly) — pre-registered 2026-11-28, before these rules are run on the data

**Why:**
- Paradex charges retail zero fees (NF23; not verified for API orders). #636 wick bids passed there, though small.
- On other venues, hourly reversal edges smaller than about 0.1% died on fees.
- This batch tests reversal triggers that #569 (−5σ, tested in NF23 #638) does not cover.

**Data:** NF23's `batchnf23_paradex_1h.parquet`, with NF23 addendum 1 (volume field = USD; bars only in traded hours).
- 66 perps, 2026-03-01..2026-11-25.

**Common (NF15's engine, unchanged):**
- **σh** = stdev of the previous 168 hourly returns (≥ 100).
- **Traded bar:** high > low and USD volume ≥ $20,000.
- **Exit** at the close 4 hours later (next traded hour up to +8h).
- **Size** = min($1,500, 1% of the hour's USD volume).
- One open trade per market.
- **Costs** 0; stress at 0.07% per round trip.

| # | Idea | Rule |
|---|---|---|
| 639 | **−3σ bounce** | hour return ≤ −3σh and > −5σh → buy at the close, exit +4h |
| 640 | **+5σ pump fade** | hour return ≥ +5σh → short at the close, exit +4h |
| 641 | **+3σ fade** | +3σh ≤ hour return < +5σh → short, exit +4h |
| 642 | **24-hour loser bounce** | at 00:00 UTC each day, among markets with ≥ $500K USD volume in the previous 24 hours, buy the 3 with the lowest 24-hour return and exit at the close 24 hours later (the exit hour must trade, otherwise the next traded hour up to +6h) |

**Split:** Stage 1 = to 2026-08-15 (kill only); Stage 2 = 2026-08-16..2026-11-25, unseen.

**Stage 1 KILL:** ≥ 30 trades and mean net ≤ 0.

**Stage 2 PASS:** all of
- ≥ 30 trades;
- mean ≥ 0.3%;
- t ≥ 2;
- sum positive without the 3 best trades;
- stress mean > 0;
- the stale-print check: a one-hour-delayed entry stays positive (NF16/NF17 lesson).

**Multiple testing:** four tests on one venue's data. Only a pass with Stage 2 t ≥ 2.5 goes to the radar forward log.

**Script/output:** `scripts/batch_nf24_20261128.py` → `docs/jx_runs/batch_nf24_20261128.txt`, re-run identical.

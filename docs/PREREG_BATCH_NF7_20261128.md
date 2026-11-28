# Batch NF7 (#560–#563): Korean retail follow-ups traded on Hyperliquid — pre-registered 2026-11-28, before running

Data, venue, entry and excess as NF5 (`docs/PREREG_BATCH_NF5_20261128.md`):
- signal on Upbit day d, entry at HL's close of d;
- excess = side × (coin − HL BTC) − 0.09%; one open trade per coin per idea.

**All four are alt shorts**, judged against the random HL alt-short baseline. 2025–26: +0.33% over 3 days, +0.95% over 7 days.
Before 2025: −0.15% / −0.21%.

| # | Idea (payer) | Signal on Upbit | Hold |
|---|---|---|---|
| 560 | **Pump day, longer hold** (#555's payer: Korean chasers; does the give-back continue past 3 days?) | KRW value ≥ 10 × the 30-day median and close ≥ +30% | 7 days |
| 561 | **Post-frenzy dry-up** (retail leaves after a frenzy, and the bid that held the price goes with it) | a frenzy day (KRW value ≥ 10 × median) within the previous 30 days, and today's KRW value < 20% of that frenzy day's | 7 days |
| 562 | **Dump-day continuation** (#554's long lost, so Korean panic dumps may keep going) | KRW value ≥ 10 × median and close ≤ −20% | 3 days |
| 563 | **Persistent Korean overvaluation** (a coin-level kimchi premium held for days reverts by price falling) | relative premium (as #548) ≥ +3% on 5 consecutive Upbit days | 7 days |

**Split:** before 2025-01-01 = Stage 1 (kill if mean ≤ that period's baseline, ≥ 8 trades); 2025 onward = Stage 2.

**Stage 2 PASS:** all of
- ≥ 15 trades;
- mean ≥ 2%;
- t ≥ 2;
- positive without the 3 best;
- mean ≥ baseline + 1 point.

**Note:** #560 is #555's family, a hold-length variant.

**$/yr:** $3,000 per trade.

**Script/output:** `scripts/batch_nf7_20261128.py` → `docs/jx_runs/batch_nf7_20261128.txt`, re-run identical.

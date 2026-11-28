# Batch W (#530–#531): energy hedging-pressure seasonals — pre-registered 2026-11-28, before data are fetched

Area plan: `docs/PLAN_BATCHES_O_Z.md` (Batch W). Keyword check: no earlier PREREG tested refinery maintenance or the natural-gas
winter premium. #483 tested the USO roll window, a different mechanism.
- **Venue:** US ETFs or NYMEX futures via a broker such as IBKR (usable from Malaysia).
- **Data:** Yahoo daily adjusted UGA, USO, UNG (job `ubatchw`).
- About 1 event a year, so power is low, and that is stated.

| # | Idea (payer) | Exact rule | Stage 1 KILL if | Stage 2 PASS if |
|---|---|---|---|---|
| 530 | **Spring refinery maintenance** (refiners take capacity offline Feb–Apr ahead of summer; gasoline gets scarcer relative to crude, and refiners and blenders must buy) | Long UGA, short USO, equal dollars, from the last close of January to the last close of April. Return = UGA − USO − 0.2% | 2009–2016: mean ≤ 0 | 2017–2026: mean ≥ 2%, t ≥ 2 (10 events) |
| 531 | **Natural-gas winter hedging premium** (utilities and distributors pay up to lock winter supply; the premium decays as winter passes without the feared shortage) | Short UNG from the last close of November to the last close of March. Return = −(UNG change) − 0.1% | winters starting 2008–2015: mean ≤ 0 | winters 2016–2025: mean ≥ 3%, t ≥ 2 (10 events). Reported alongside: short UNG April→October (the rest of the year, as a check that it is the winter premium and not UNG's all-year roll decay) |

**$/yr:** $45K per event.

**Families:** #530 and #531 are separate (refining margins; gas hedging premium).

Stage 1 only kills; nothing passes early.

**Script/output:** `scripts/batch_w_20261128.py` → `docs/jx_runs/batch_w_20261128.txt`, re-run identical.

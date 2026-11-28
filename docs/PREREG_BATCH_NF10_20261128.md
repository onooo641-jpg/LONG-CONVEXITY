# Batch NF10 (#572–#575): hourly structure — the Korean morning, intraday frenzies, #569 on Binance — pre-registered 2026-11-28, before running

**Data:**
- HL hourly OHLCV (`wickscale_hl_1h`, 196 coins, 2026-04-24..11-25): Stage 1 = to 2026-08-15, Stage 2 = after.
- Binance hourly closes (`batchh2_unseen_1h`, 110 perps, 2023-01..2026-10): Stage 1 = 2023–2024, Stage 2 = 2025–2026-10.
- Upbit coin list (`distinct_upbit_1d`) marks Korea-listed coins.

**Desk checks:**
- **G5:** HL trades (#574 is evidence only; Binance is not usable from Malaysia).
- **G6:** intraday, small size, tied to a local-retail payer.

**Costs:** 0.09% round trip, excess vs HL BTC over the same hours where stated.

| # | Idea (payer) | Rule |
|---|---|---|
| 572 | **Korean morning buying** (Upbit retail is most active in the first KST hours, 09:00 KST = 00:00 UTC) | Every day: long an equal-weight basket of HL coins that are also on Upbit, from the 23:00 UTC hourly close to the 03:00 UTC close. Excess vs HL BTC over the same 4 hours, − 0.09% |
| 573 | **Korean morning give-back** (that buying reverts once Korean retail activity fades) | Every day: short the same basket from the 03:00 UTC close to the 09:00 UTC close. Excess vs BTC, − 0.09% |
| 574 | **#569 on Binance** (is the hourly cascade reversal venue-specific?) | Binance hourly closes. Hour return ≤ −5σh (σh = stdev of the previous 168 hourly returns) → buy at that close, sell 4 hours later, − 0.09% |
| 575 | **Intraday frenzy pump** (#555's give-back at an hourly scale on HL itself) | HL hour with USD volume ≥ 10 × its previous-168-hour median **and** return ≥ +3σh → short at that close, cover 4 hours later, − 0.09% |

One open trade per coin per idea (#572/#573: one basket trade per day).

**Stage 1 KILL:** mean ≤ 0 (≥ 30 trades).

**Stage 2 PASS:** all of
- ≥ 30 trades;
- mean ≥ 0.2% (#572/#573: baskets, daily) or ≥ 0.3% (#574/#575);
- t ≥ 2;
- positive without the 3 best.

#574 is reported as "mechanism confirmed / not", not as a tradeable pass.

**Script/output:** `scripts/batch_nf10_20261128.py` → `docs/jx_runs/batch_nf10_20261128.txt`, re-run identical.

## Results (2026-11-28; `docs/jx_runs/batch_nf10_20261128.txt`, re-run identical): 0 of 3 tradeable; #574 invalid as run
| # | Verdict | Stage 1 | Stage 2 |
|---|---|---|---|
| 572 Korean morning buying | KILL | −0.09% (107 days) | −0.11% (101) |
| 573 Korean morning give-back | KILL | −0.11% | −0.10% |
| 574 #569 on Binance | **invalid as run** | 16 of the 110 Binance symbols in `batchh2_unseen_1h` have > 50% flat (zero-return) hours, so σh ≈ 0 and they fire 80,000+ false signals (win 2–7%, median = −cost) | — |
| 575 intraday frenzy pump | FAIL | +0.23% (t 1.14) | −0.05% |

**#574, post-hoc data-quality re-run** (evidence only, labelled as post-hoc; `docs/jx_runs/batch_nf10_574_posthoc_20261128.txt`):
- Only symbols with ≤ 10% flat hours are kept.
- 2023–24: +0.35% (t 5.44, 2,548). 2025–26: **−0.32% (t −3.46, 2,072)**.
- The hourly cascade reversal does **not** carry over to Binance in 2025–26. That is a warning sign for #569: its HL edge also shrank,
  from +1.37% to +0.34%. The forward test (N14) decides.
- #569's own HL data has 0% flat hours, so it is unaffected by the data problem.

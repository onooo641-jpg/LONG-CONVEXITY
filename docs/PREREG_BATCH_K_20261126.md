# Batch K (#493–#495): last full-effort batch before the switch back to prop firms — pre-registered 2026-11-26, before any of their data are looked at

**Context.** Jx: Batch K is the last batch for now. After it, effort moves to finding more prop firms that pass. The audit
(`docs/AUDIT_PRE_LIVE_20261126.md`) left 3 passing prop setups.

**Selection.** Batch K takes the three hypotheses with the best remaining odds. Each has:
- a named payer;
- a large event count;
- a **confirmation stage on data the idea was not designed on**. The lesson of #468 and Batch J is that single-universe passes do not
  replicate.

Not padded to 10: about 75 ideas since Batch C have used up the free-data structural payers (see `docs/NOTES_NONPROP.md`).

**Gate (Jx's calibration).** Payer, free data, a Malaysia-usable venue (Hyperliquid for crypto, IBKR for ETFs), and a time split. $/yr is
reported at a safe size; only passes of ≥ ~$10K/yr count toward Jx's two.

| # | Idea (payer) | Exact rule | Stage 1 KILL if | Stage 2 PASS if | Stage 3 (confirmation, required) |
|---|---|---|---|---|---|
| 493 | **Recurring-buy calendar** (US recurring-buy plans and semi-monthly payroll buy crypto price-insensitively on the 1st and 15th; #462's BTC variant hinted at it: +0.87%, t 2.20, report-only) | Two windows a month, from Binance 1h prices: 00:00 UTC on the last day of the previous month → 00:00 UTC on the 2nd; and 00:00 UTC on the 14th → 00:00 UTC on the 16th. Long an equal-weight basket; net − 0.09% | 40 `batchd_alts` (ex BTC) 2020-07..2022-12: mean ≤ 0 | 40 alts 2023-01..2026-10: mean ≥ 0.3%, t ≥ 2 | 110 unseen perps (`batchh2_unseen`) 2023-01..2026-10: mean > 0, t ≥ 2 |
| 494 | **Pension month-end rebalancing, bond leg** (#450: 4/4 index futures positive, pooled t 1.99. If pensions sell equities after equities beat bonds, they must buy bonds: an untested, independent leg) | #450's signal on SPY: at the close of the 4th-last trading day, R_e = SPY month-to-date return (adjusted, from last month's final close); R_b = −7.5 × ΔDGS10 over the same dates. If R_e − R_b > +2%: short SPY and long TLT to the last trading day's close; if < −2%: the reverse. Net − 0.04% per leg | SPY leg 2003–2015: mean ≤ 0 | SPY leg 2016..2026-10: mean ≥ 0.2%, t ≥ 2 | **TLT leg** 2016..2026-10 (the bond side, never tested): mean > 0, t ≥ 2. Reported: EFA as equity leg |
| 495 | **Retail positioning crowding** (when retail accounts are lopsidedly long a perp, those longs pay funding and are the forced sellers in the next drop) | Every Monday 00:00 UTC: Coinalyze Binance daily long/short *account* ratio of the previous day. Coins with ≥ 30 days of history: short the top quintile of long-account share, long the bottom quintile, equal weight, 7 days. Weekly = mean(long) − mean(short) − 0.18% | 40 alts 2020-10..2022-12: mean ≤ 0 | 40 alts 2023-01..2026-10: ≥ 100 weeks, mean > 0, t ≥ 2 | 110 unseen 2023..2026-10: mean > 0, t ≥ 2 |

**Rules for running the stages:**
- Stage 1 only kills. No stage passes early.
- Stage 3 is computed and printed only after Stage 2.
- An idea counts only if both Stage 2 and Stage 3 hold.

**$/yr at safe size:**
- #493: $45K per window, about 24 windows/yr;
- #494: $30K per leg;
- #495: $22.5K per side.

**Data:**
- Local: Binance 1h prices for #493 and #495; `batchg_etf_1d` (SPY, EFA) and `batchd_fred_cmt` (DGS10).
- New:
  - TLT and IEF from Yahoo (job `ubatchk`, `fetch_public.yml`);
  - Coinalyze daily long/short ratio for the Binance symbols (`scripts/fetch_coinalyze_j.py --k`; the key comes from the environment
    and is never stored).

**Script and output.** Script: `scripts/batch_k_20261126.py`. Output: `docs/jx_runs/batch_k_20261126.txt` (re-run once; it must be identical).

## Results (2026-11-26; `docs/jx_runs/batch_k_20261126.txt`, re-run identical)

| # | Verdict | Stage 1 / Stage 2 / Stage 3 | $/yr at safe size |
|---|---|---|---|
| 493 recurring-buy calendar | FAIL | +2.42% (t 3.36) / −0.08% / −0.18% (unseen) | −$839 |
| 494 pension month-end, bond leg | FAIL | SPY +0.35% (t 1.79) / SPY +0.18% (t 0.95) / TLT +0.11% (t 0.77); EFA +0.31% (t 1.86) | $683 |
| 495 retail positioning crowding | FAIL | +2.29%/wk (t 2.28) / +0.78% (t 1.80) / **−0.93% (t −2.62) on unseen perps** | $9.2K on S2, but it reverses out of sample |

**Batch K verdict: 0 of 3.** Each idea worked in 2020–22, then weakened or reversed in 2023–26 on unseen data. This is the pattern
seen across Batches C–K.

**Search summary C–K:** ~78 ideas.
- **$10K+ passes:** only the wick family (#389/#403).
- **Small out-of-sample passes:** #455 (~$3.2K/yr) and #451 (~$0.7K/yr).

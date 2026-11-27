# Batch P (#515–#518): government bonds outside the US — pre-registered 2026-11-27, before the yields and auction file are read

Area plan: `docs/PLAN_BATCHES_O_Z.md` (Batch P). The US versions were tested: #446 auction concession (Stage 1 strong, gone after
2017) and #451 month-end index extension (Batch F). Japan, Germany and the UK were never tested.
- **Venue:** JGB, Bund and Gilt futures through a broker such as IBKR (usable from Malaysia).
- **Data (probed 2026-11-27, Actions):** MOF daily JGB yields 1974–2026; MOF `Auction_Results_for_JGBs.xls`; BoE 10-year nominal
  zero-coupon yield (IUDMNZC) daily; Bundesbank 10-year Bund yield daily. The UK DMO auction calendar is behind a captcha, so there is
  no Gilt auction test.

| # | Idea (payer) | Exact rule | Stage 1 KILL if | Stage 2 PASS if |
|---|---|---|---|---|
| 515 | **JGB auction concession** (primary dealers must absorb each auction, so yields rise into it and fall after) | #446's rule on Japan. Every JGB coupon auction in the MOF file (2, 5, 10, 20, 30, 40-year; JGBi, CMT and liquidity-enhancement auctions excluded), with the MOF yield of the same tenor. PRE: short duration from the close of A−5 business days to the close of A. POST: long from A to A+5. Net bp = Δy(PRE) − Δy(POST) − 1.0 bp | 2009–2016: mean net ≤ 0 | 2017–2026: mean net ≥ 1.0 bp, t ≥ 2 on weekly-clustered means, ≥ 6 of 10 years positive, $/yr ≥ $10K at DV01 $50 per event |
| 516 | **JGB month-end index extension** (bond index funds must lengthen duration at month-end) | #451's rule: long the 10-year from the close of the 3rd-last business day to the last business day of each month. P&L = −Δy − 0.5 bp. MOF 10Y | 1990–2009: mean ≤ 0 | 2010–2026: mean ≥ 0.5 bp, t ≥ 2 |
| 517 | **Bund month-end index extension** | same rule, Bundesbank 10-year | 1990–2009: mean ≤ 0 (data permitting) | 2010–2026: mean ≥ 0.5 bp, t ≥ 2 |
| 518 | **Gilt month-end index extension** | same rule, BoE 10-year zero-coupon | earliest data–2009: mean ≤ 0 | 2010–2026: mean ≥ 0.5 bp, t ≥ 2 |

**$/yr:** #515 = net bp × $50 × events per year. #516–#518 = mean bp × $50 DV01 (≈ $55K of 10-year futures notional per bp
sensitivity) × 12.

**Families:** #515 is the auction-concession family (with #446). #516–#518 are one family (index extension, with #451) and count once.

Stage 1 only kills; nothing passes early.

**Data job:** `ubatchp`. **Script/output:** `scripts/batch_p_20261127.py` → `docs/jx_runs/batch_p_20261127.txt`, re-run identical.

## Results (2026-11-27; `docs/jx_runs/batch_p_20261127.txt`, re-run identical)
| # | Verdict | Stage 1 | Stage 2 | $/yr |
|---|---|---|---|---|
| 515 JGB auction concession (1,925 auctions, 6 tenors) | FAIL | +0.35 bp (week t 1.29, 5/8 years) | −0.25 bp (t −0.60, 2/10 years) | −$826 |
| 516 JGB month-end extension | KILL | −0.01 bp | −0.53 bp (t −2.56) | −$317 |
| 517 Bund month-end extension | KILL | −0.43 bp | −0.18 bp | −$111 |
| 518 Gilt month-end extension | FAIL | +0.94 bp (t 1.85) | +0.06 bp (t 0.13) | $35 |

**Batch P verdict: 0 of 4.** Sovereign-bond supply and index-extension flows are priced away in Japan, Germany and the UK, as in the
US (#446, #451).

# Batch K, part 2 (#496–#499): more and stronger ideas (Jx: "I meant more also stronger ideas") — pre-registered 2026-11-26, before their data are looked at

**Selection bar (stronger than Batches C–K).** Each idea needs:
- (1) a payer whose flow is mechanical, large and current (2024–26);
- (2) enough events and volatility to reach ≥ $10K/yr at a safe size if the effect is real;
- (3) a confirmation stage on an independent asset, venue or coin set.

Every candidate was checked against `docs/CANDIDATES.md` and all PREREG files first (hyphen and space spellings). Not tested before:
- Ethena hedge flows;
- the CME basis *unwind* (#271 tested holding the basis, not the unwind's price impact);
- Hyperliquid funding premium over Binance.

#499 is a declared **re-test**: the same mechanism as #489 (killed), on a venue not used before. It is labelled so; its result does not
overturn #489's verdict.

**Costs and safe size.** Crypto: 0.09% round trip per leg; $45K notional per signal ($15K × 3); for the cross-section, $22.5K per side.
Venue: Hyperliquid.

| # | Idea (payer) | Exact rule | Stage 1 KILL if | Stage 2 PASS if | Stage 3 (required) |
|---|---|---|---|---|---|
| 496 | **Ethena hedge flows** (USDe is backed by short perps. Mints force Ethena to *sell* perps; redemptions force it to *buy them back*; size ~$5–15B) | Daily USDe circulating supply (DefiLlama). Δ = day-over-day % change. If Δ ≤ −1.5% (redemptions) → long ETH from 00:00 UTC of the next day for 2 days; if Δ ≥ +1.5% (mints) → short. Net − 0.09%. No overlap | ETH 2024-03..2024-12: mean ≤ 0 | ETH 2025-01..2026-10: ≥ 20 events, mean ≥ 0.5%, t ≥ 2 | BTC, same rule and period: mean > 0, t ≥ 1.5 |
| 497 | **CME basis-trade unwind** (cash-and-carry funds hold spot or ETF and short CME futures; when the basis collapses they sell spot) | Daily annualised basis b = (BTC=F / BTC-USD − 1) × 365 / days to the last Friday of the month (expiry). Days within 3 calendar days of expiry are excluded. If b falls ≥ 5 points over 5 days → short BTC from that close for 5 days; net − 0.09%. No overlap | BTC 2021-01..2023-12: mean ≤ 0 | BTC 2024-01..2026-10 (ETF era): ≥ 15 events, mean ≥ 0.5%, t ≥ 2 | ETH (ETH=F vs ETH-USD), same rule, 2024..2026-10: mean > 0, t ≥ 1.5 |
| 498 | **Hyperliquid retail funding premium** (Hyperliquid's retail longs pay more than Binance's for the same coin; that crowding unwinds) | Every Monday 00:00 UTC, for coins on both venues: p = mean of HL daily funding − mean of Binance daily funding, over the last 7 days (Coinalyze daily, same units). Short the top quintile of p, long the bottom quintile; prices = Hyperliquid daily closes (Coinalyze OHLCV); 7 days; − 0.18%. Coins: those in `batchd_alts` (the 40) | 2024-10..2025-06: mean ≤ 0 | 2025-07..2026-10: ≥ 50 weeks, mean > 0, t ≥ 2 | the same rule on the coins from the 110 unseen set listed on both venues, 2025-07..2026-10: mean > 0, t ≥ 2 |
| 499 | **Crowded-funding short, re-test on Bybit** (#489's mechanism) | #489's rule exactly, with Bybit data only: Bybit daily funding (Coinalyze) ≥ 0.05% per settlement (Coinalyze reports the funding rate in %) and Bybit OI at a 30-day high → short the coin from the Bybit daily close for 7 days, long BTC on Bybit; funding approximated by 3 × the daily rate per day held; − 0.18% | Bybit 2021-01..2022-12: mean ≤ 0 | Bybit 2023-01..2026-10: ≥ 30 events, mean ≥ 1%, t ≥ 2 | none extra: #489's unseen-perp Stage 3 (+5.3%, t 2.31) already exists; this is a venue confirmation |
| 500 | **Hedger-paid carry on Hyperliquid** (holders of locked or airdropped tokens hedge by shorting Hyperliquid perps and pay deeply negative funding to longs; #468's profit sat on this side) | Per coin (Hyperliquid coins also on Binance), day d: HL daily funding (per-8h basis, same unit check as #498) ≤ −0.03% → long the coin on HL from d's close for 7 days, short BTC as a hedge (equal notional). P&L = r_coin − r_BTC + funding received (3 × the daily per-8h rate per day held) − BTC funding paid − 0.18%. One open trade per coin; same-day events averaged | 2024-10..2025-06: mean ≤ 0 | 2025-07..2026-10: ≥ 20 events, mean ≥ 1%, t ≥ 2 | the same rule on **Binance** funding and prices (1h archive) for the 110 unseen perps, 2023-01..2026-10: mean > 0, t ≥ 2 |

(#500 added 2026-11-26, before any Hyperliquid funding data were opened.)

**Rules for running the stages:**
- Stage 1 only kills. No stage passes early.
- Stage 3 is printed after Stage 2.
- An idea counts toward Jx's two only if Stage 2 and Stage 3 both hold and its $/yr at the safe size is ≥ ~$10K.

**Data:**
- Job `ubatchk2` (GitHub Actions, `fetch_public.yml`):
  - DefiLlama USDe supply history;
  - Yahoo BTC=F, ETH=F, BTC-USD, ETH-USD daily.
- `scripts/fetch_coinalyze_j.py --k2` (session; the key comes from the environment and is never stored):
  - Hyperliquid daily funding and OHLCV for coins also on Binance;
  - Binance daily funding (same source, so the units match);
  - Bybit daily funding.

**Script and output.** Script: `scripts/batch_k2_20261126.py`. Output: `docs/jx_runs/batch_k2_20261126.txt` (re-run once; it must be identical).

## Results (2026-11-26; `docs/jx_runs/batch_k2_20261126.txt`, re-run identical)

| # | Verdict | Stage 1 / Stage 2 / Stage 3 | $/yr at safe size |
|---|---|---|---|
| 496 Ethena hedge flows | FAIL | ETH +0.02% / −0.12% / BTC −0.21% | −$1.7K |
| 497 CME basis-trade unwind | KILL | −0.32% / **−1.08% (t −2.30)** / ETH −1.20%: after the basis collapses, BTC rebounds (the opposite sign) | −$19.8K |
| 498 Hyperliquid funding premium | FAIL | +0.47% / **−1.78% (t −2.52)** / −1.26% (t −1.86): coins where Hyperliquid pays more funding *outperformed* in 2025–26 | −$20.7K |
| 499 #489 re-test on Bybit | KILL | −1.10% / +0.70% (t 0.52) | $2.6K |
| 500 hedger-paid carry on Hyperliquid | KILL | −1.64% / +0.24% / Binance unseen −0.46% | −$26.9K |

**Batch K part 2: 0 of 5.**

**Observation (not a pass and not tradable as registered):** #498 points the opposite way, consistently on both coin sets in 2025–26. It
would need its own pre-registration with a new kill window; the 2024–25 window here (+0.47%) would kill the reversed rule. This was a
units check on data already opened, so it is not a fresh test.

**Batch K total (#493–#500): 0 of 8.** Batch search paused per Jx. Next: prop firms.

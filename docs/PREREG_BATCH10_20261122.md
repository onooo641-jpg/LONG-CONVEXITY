# Batch 10: tests for sweep 2 (#296–#308, #314) — 2026-11-22

Written and committed before the batch-10 fetch (job `batch10`). Ideas and Stage 0 in `docs/IDEAS_SWEEP2_20261122.md`. Stage 1 = cheapest slice,
**kill-only**; survivors get Stage 2 by addendum (rules unchanged). Prop pricing uses the radar flag rule (real ≥ $22,180, coin flip ≥ $5,000,
worst dip ≥ −$5,280, vs Topstep 50K).

| # | data | Stage 1 rule (kill-only) |
|---|---|---|
| 296 CFD prop recycling | firm pages (official, fetched by Actions); friend's NQ trades | Price each firm's ~$50K 2-phase/1-phase product with recycle.py (extended: `phase2_target`, `refund_fee_on_first_payout`; defaults off, so existing results do not change; tests must pass). Risk = min(0.45 × max loss, 0.875 × daily loss). CFD cost: 1.5 index points per round trip per NQ-equivalent contract ($30), replacing the futures commission (assumed). Not priced if the rules or the EA policy cannot be read. Full flag rule applies (no separate Stage 1). |
| 297 competitions → funded account | firm competition pages | value = P(top-N) × value of the prize account (its #296 real-net figure ÷ years). P(top-N) from published winners' returns vs the friend's monthly return distribution at the competition's max risk. Not testable if winners' figures are unpublished. |
| 298 sale-window buying | flagged + near-miss products (radar_price models) | ranking: real / coin flip / dip at 40%, 60%, 80% off; no pass/fail |
| 300 stock-perp funding carry | HIP-3 funding (batch8_raw.json, 2026-07..11) | daily: hold the 5 stock perps with the highest trailing-7-day absolute funding, on the receiving side, hedged 1:1 with shares; 5 bps per leg-side; capital 4/3 of notional. KILL if 2026-08..10 < 4%/yr |
| 314 index perps vs futures | same, index names only (US500, USA500, USTECH, SMALL2000, XYZ100, JP225, KR200) | same rule; KILL < 4%/yr |
| 301 dividend gap | HIP-3 funding premium + Yahoo dividends | per ex-date in 2026-07..11: long shares + short perp from the prior close to the ex-date close: +0.7·D (30% US withholding) − 4 × 5 bps − funding paid − change in perp premium. KILL if the mean net per event ≤ 0 |
| 302 weekend gap | HIP-3 1h candles + Yahoo opens | if the perp moved > 1% between Friday 16:00 ET and Monday 09:00 ET, fade it in the perp from 09:00 to 10:00 ET; 10 bps round trip. KILL if the mean per trade ≤ 0 |
| 303 index additions | Wikipedia S&P 500 change list + Yahoo prices | buy each added stock at the close 5 trading days before the effective date, sell at the effective-date close, minus SPY; 10 bps. KILL if the mean excess ≤ 0.2% per event (2024-11..2026-10) |
| 304 token-unlock shorts | DefiLlama emissions (probe) + HL candles | short the HL perp 7 days before an unlock ≥ 1% of supply, cover 7 days after, BTC hedge β = 1; 10 bps. KILL if mean ≤ 0; not testable without a calendar |
| 305 redemption floor | GeckoTerminal daily OHLCV (LUSD, BOLD, feUSD pools) | capital parked at 4%/yr, deployed on days whose low < $1 − 0.5% fee; gain = half of (1 − fee − low) per event (half-capture). KILL if total < 6%/yr |
| 306 cooldown discount | GeckoTerminal sUSDe pools + DefiLlama sUSDe value | as #305, gain = half of the discount beyond 0.3% (7-day cooldown carry). KILL if total < 6%/yr |
| 307 listing drift | Upbit notices (probe) + HL 1h candles | long the HL perp 1 h after a KRW listing notice, exit 24 h later; 10 bps. KILL if mean ≤ 0 (2026-07..11) |
| 308 warning / delist shorts | same | short 1 h after notice, exit 72 h later; 10 bps. KILL if mean ≤ 0 |
Command: `uv run python -m scripts.batch10_20261122 | tee docs/jx_runs/batch10_20261122.txt` (+ `scripts/cfdprop_20261122.py` for #296–#298).

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

## Results so far (2026-11-22)
- **#298 sale windows (ranking; `docs/jx_runs/salewindow_20261122.txt`, identical on re-run).** Of 62 price rows (35 with a verified price), the
  flag rule is met by 18 / 39 / 52 / 55 rows at 0 / 40 / 60 / 80% off (verified-price rows: 7 / 16 / 25 / 28). Newly flagging at 40% off
  (verified price): MFFU Rapid EOD 50K ($43,775 / $17,429 / −$3,580), Tradeify Select Flex, FundedNext Rapid Pro, TFD Static Pro,
  MFFU Builder 50K ($153), Goat Flex 50K, Blueberry Ascent 50K, Alpha Futures Standard 50K (manual). Topstep itself: $44,359 → $47,338.
  TTP Prime 50K (reset $79): $49,057 → $55,003. **Caveats:** resets are discounted too, which is optimistic (many codes exclude resets).
  The availability and frequency of 40%+ codes are not verified (checkout prices are behind logins). Ranking only, no pass/fail.
- **#300 stock-perp funding carry: KILL** (US-listed shares only, as the registered 1:1 share hedge requires): −13.28%/yr in 2026-08..10.
  Context: all single-name perps, including pre-IPO / private / non-US names that cannot be hedged with shares (UNITREE, TREAD, ANTH…),
  show 49.89%/yr. That figure is not tradeable as registered. An unhedged position would be a directional bet on illiquid perps.
  The hedgeable list was written into the script during this run, after a first context run had wrongly included ANTH.
- **#314 index-perp funding carry: KILL** (−2.21%/yr).

## Addendum 1 (2026-11-22): batch-10 Stage 1 so far, and the #303 Stage 2 rule (written before the full price fetch)
Stage 1 results (`docs/jx_runs/batch10_20261122.txt`): **#301 dividend gap KILL** (22 ex-dates, mean −0.053% per event). **#302 weekend gap
KILL** (348 trades, −0.332% per trade, 41% hits). **#303 index additions continue** (7 events with prices, mean excess +6.90%, median +5.98%).
The Wikipedia wikitext has no change table, so additions are read from the constituents table's "Date added" column (current members only).
Only 7 of the window's additions had Yahoo prices: the fetch took the alphabetically last 200 tickers, a mechanical error.
**#303 Stage 2 (rule unchanged: buy the close 5 trading days before the effective date, sell at the effective-date close, minus SPY, 10 bps).**
Universe: every constituent with "Date added" in 2024-11-01..2026-10-31 (prices fetched by job `addprice`). PASS = mean excess > 0.5% per event
AND t-stat > 2 AND both halves (split 2025-11-01) positive AND annualised return ≥ 8%/yr on capital (one position at a time, overlapping events
equal-weighted within the capital). Caveat recorded in advance: S&P announces additions about 5 trading days before the effective date, so t−5 is
often after the announcement. This tests the post-announcement drift only. Removed-again members are missing (survivorship, small over 2 years).
#304: the unlock list answered; the parser and rule will be registered by addendum 2 before any analysis. #305–#308 wait for job `batch10b`.

## Results (2026-11-22; `docs/jx_runs/batch10_20261122.txt`)
- **#303 S&P 500 additions: registered Stage 2 PASS.** 36 of 39 additions priced; mean excess +3.90% per event (median +3.55%), t-stat 2.97,
  halves +4.19% / +3.72%, 64% hits; the registered one-position-at-a-time figure is 47.9%/yr. That figure compounds concentrated event windows, so
  it overstates a realistic capital return. **Look-ahead check (context, done after the verdict):** quarterly-rebalance additions (announced
  about a week ahead, so t−5 is after the news) n = 22, +3.49%, t = 2.36. Off-cycle additions (often announced 2–5 days ahead, possible
  look-ahead) n = 14, +4.55%, t = 1.81. Equal-weighting each quarter's additions for 5 days gives roughly 3.5% per quarter ≈ 14–15%/yr before
  idle-cash interest (rough, not a registered figure). **Five-part filter: F4 (capped downside) fails** (single-stock risk is hedged against
  SPY, not capped) → not flaggable as a structural pass; reported to Jx as the first non-prop idea to pass a full test, with these caveats.
  Other caveats: 22–36 events, one regime (2024–26 momentum additions), removed-again members missing, effect historically crowded.
- **#305 redemption floor: Stage 1 "continue" is a data artefact → not tradeable.** The sub-$1 values are single-trade wicks in daily lows on
  pools trading $268–$35K a day (closes ≈ $0.998). No further test.
- #304 not tested (the unlock-list parser was never registered); #306 no reference value; #307/#308 Upbit blocks automated requests (403);
  #296 not completed (FTMO FAQ answers and the other CFD firms' rule pages did not render fully); #297 not testable (winners' returns unpublished).

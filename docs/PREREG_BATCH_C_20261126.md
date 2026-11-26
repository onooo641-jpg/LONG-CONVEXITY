# Batch C (#429–#438): ten ideas, designed from Batches A–B — pre-registered 2026-11-26, before their data are fetched

Lessons applied: what passed is liquidity to forced/frictional flows (wick family on 4 venues); what failed is behavioural fades out of
sample, carry/yield, concentrated solver roles, vault APYs. So Batch C is weighted to frictions and true-value anchors. All permissionless,
usable from Malaysia, structural payer, out-of-sample split fixed here. $15,000 pot. Data job `ubatchc`; script `scripts/batch_c_20261126.py`.
Stage 1 = in-sample kill-only; Stage 2 = out-of-sample PASS. Event studies: hedged with BTC where stated, 0.045%/side, funding where available.

| # | Idea (payer) | Data | Rule | Stage 1 (kill) | Stage 2 (PASS) |
|---|---|---|---|---|---|
| 429 | Fiat-backed stablecoin depeg buying (panic sellers; redemption at $1 is a true anchor) — USDC, USDT, FDUSD, PYUSD, TUSD, BUSD, USDP | DefiLlama hourly CoinGecko prices 2020–2026 | buy $5,000 when hourly price ≤ 0.98; sell at the first hour ≥ 0.997 or after 30 days; 0.1% costs | 2020-01..2022-12: KILL if < 3 events or mean ≤ 0 | 2023-01..2026-10: PASS if ≥ 3 events, mean ≥ +1%, ≥ 75% profitable |
| 430 | Crypto-backed/synthetic stable depegs (DAI, USDe, FRAX, crvUSD, GHO, LUSD, USDD, USD0, USDS) | same | same rule, buy at ≤ 0.97 | same split | same bar |
| 431 | Binance deposit/withdrawal suspension convergence (arbitrage blocked → prices drift apart) | Binance "wallet maintenance" announcements + Binance and Hyperliquid daily closes | during a suspension of ≥ 1 day, if HL close differs from Binance close by ≥ 2%, trade HL toward Binance; exit at the first close after resumption | 2023–2024: KILL if ≥ 10 events and mean < 0.5% | 2025–2026: PASS if ≥ 10 events, mean ≥ 1%, t ≥ 2 |
| 432 | Funding-sentiment extreme, BTC (crowded shorts market-wide → squeeze) | Binance funding 2020–26; median daily funding across the top-50 perps | when the median falls below its trailing-365-day 5th percentile, long BTC 7 days; above the 95th, short BTC 7 days | 2020–2022: KILL if mean < 0.5% or t < 1 | 2023–2026: PASS if ≥ 10 events, mean ≥ 1.5%, t ≥ 2 |
| 433 | Same signal, ETH | same | same | same | same |
| 434 | BTC CME weekend-gap fill (CME's Friday 21:00–Sunday 22:00 UTC gap) | Binance BTCUSDT 1h archive | at Sunday 22:00 UTC, if price is ≥ 1.5% from Friday 21:00, trade toward the Friday price; exit at the gap fill or Wednesday 22:00 | 2020–2022: KILL if mean < 0.3% or t < 1 | 2023–2026: PASS if ≥ 30 events, mean ≥ 0.5%, t ≥ 2 |
| 435 | Same, ETH (ETHUSDT 1h) | same | same | same | same |
| 436 | HIP-3 commodity perps weekend fade (gold/silver/oil trade on Hyperliquid while CME is shut) | `fivehigh_hip3_1d` | if the Saturday+Sunday move ≥ 2%, fade it from Sunday close to Monday close | first half of history: KILL if mean ≤ 0 | second half: PASS if ≥ 15 events, mean ≥ 0.5%, t ≥ 2 |
| 437 | HIP-3 stock-index perps weekend fade (same rule on index/stock perps) | same | same | same | same |
| 438 | Token-split / redenomination arbitrage (1000x tickers re-based, migrations) | Binance announcements | — | desk: events too few and conversion is exchange-handled; recorded as not testable | — |

## Batch C extension (#439–#442) — pre-registered 2026-11-26 before their data are fetched (Jx: 10 individual ideas, variants on top)
Each idea has a BTC and an ETH variant (judged separately). Data: Binance 1h klines (`batchc_btceth_1h`), Binance 8-hourly funding events
for BTCUSDT/ETHUSDT and Coinbase daily candles (job `ubatchc2`). Costs 0.045% per side. Stage 1 = 2020-01..2022-12 (2024 for #441),
Stage 2 out-of-sample = 2023-01..2026-10 (2025-01..2026-10 for #441).

| # | Idea (payer) | Rule | Stage 1 (kill) | Stage 2 (PASS) |
|---|---|---|---|---|
| 439 | Options-expiry unwind (dealer hedges released at Deribit's 08:00 UTC Friday expiry; last Friday of the month) | long from Friday 08:00 to Monday 08:00 if price fell over the expiry week (Fri 08:00 → Fri 08:00), else short | mean < 0.3% or t < 1 | ≥ 30 events, mean ≥ 0.5%, t ≥ 2 |
| 440 | Funding-settlement drift (longs/shorts close just before paying funding) | at 2 h before each 8-hourly settlement, if the last funding rate ≥ 0.03% short until 1 h after settlement; if ≤ −0.03% long | mean < 0.05% or t < 1 | ≥ 100 events, mean ≥ 0.08%, t ≥ 2 |
| 441 | US spot-ETF fix window (creations struck at 16:00 New York = 20:00/21:00 UTC) | long BTC/ETH 18:00→21:00 UTC on US trading days when the previous day's 13:30→21:00 UTC return > 0 (inflow persistence), else short | 2024: mean < 0.05% or t < 1 | ≥ 150 events, mean ≥ 0.08%, t ≥ 2 |
| 442 | Coinbase premium (US buyers pay above offshore price) | daily: premium = Coinbase close ÷ Binance USDT close − 1; if premium > its trailing-90-day 95th percentile, long 3 days; < 5th, short 3 days | mean < 0.5% or t < 1 | ≥ 20 events, mean ≥ 1%, t ≥ 2 |

## Verification stage V for #429, #430 (and #421) — pre-registered 2026-11-26 after their Stage 2 printed PASS, before any check is run
The Stage 2 passes rest on CoinGecko hourly prices (aggregated, can include dead venues: BUSD trades down to $0.14 in that feed after its
wind-down). A pass counts only if the events were tradeable on an independent venue:
- **Stablecoins (#429, #430):** Binance spot 1h klines (archive) for the token against USDT (FDUSD, USDC, TUSD, BUSD, USDP, DAI where
  listed). An event is **confirmed** if, in its entry hour, the Binance low ≤ the CoinGecko entry price + 0.5% and the Binance pair later
  reaches ≥ 0.997 (the exit rule) within 30 days; it is **unverifiable** if the token has no Binance pair at that time.
- **#421:** events from 2026-05-01 on are checked against GeckoTerminal pool closes (`uncharted_384_ohlcv`, the main DEX pool): confirmed if
  the pool's daily close or low on the event day is ≥ 0.5% below the on-chain NAV.
- **Rule:** an idea keeps its PASS only if ≥ 70% of its verifiable events are confirmed **and** the confirmed events alone still meet the
  Stage 2 bar (≥ 3 events, mean ≥ +1%, ≥ 75% profitable for #429/#430; ≥ $3,000/yr scaled for #421). Otherwise it is downgraded to
  "data artefact / not confirmed". Data: job `uverify`.

---
## Results so far (2026-11-26 check-in) — `uv run python -m scripts.batch_c_20261126`, `uv run python -m scripts.verify_v_20261126`
| # | Result |
|---|---|
| 429 | Stage 1 survives (35 events, +3.39%), Stage 2 printed PASS (220 events, +4.18%, 100% profitable) — **pending verification V** (CoinGecko feed includes dead venues, e.g. BUSD down to $0.14 after its wind-down) |
| 430 | Stage 1 survives (10 events), Stage 2 printed PASS (19 events, +4.07%, 95%) — **pending verification V** |
| 431 | Not testable: only 4 suspension titles, without token/window detail |
| 432 / 433 | KILL (t 0.33 / 0.33 in 2020–22) |
| 434 / 435 | KILL (2020–22 mean −0.78% / −1.65%) |
| 436 / 437 | KILL / FAIL (1 event per half) |
| 438 | Not testable |
| 439 | KILL (BTC mean 0.00%, ETH −0.53%) |
| 440 | pending data (`ubatchc2`) |
| 441 | KILL (BTC −0.09%, ETH −0.17% per event in 2024) |
| 442 | pending data (`ubatchc2`) |

**#421 (Batch A) re-run with real on-chain rates (4,181 rate rows):** Stage 1 2024 108 events +1.60% (survives); Stage 2 printed PASS
(89 events, +5.47%, 100% profitable, $13,308/yr). **Verification V:** 85% of verifiable event days "confirmed" — but every confirmed day is
pufETH on a pool trading $0.0001–$2 a day (no executable size), and none of the liquid tokens' (weETH, sUSDe, rsETH) discounts appear on
their DEX pools. **Not counted: the CoinGecko discounts are not tradeable.**

### Verification V results (2026-11-26) — `uv run python -m scripts.verify_v_20261126` → `docs/jx_runs/verify_v_20261126.txt` (re-run identical)
Mechanical fix before the verdict: CoinGecko points are seconds off the hour, so event times are floored to the hour to match Binance bars.
- **#429 — DOWNGRADED (data artefact):** 219 Stage 2 events, of which 200 are BUSD after Binance's BUSDUSDT pair ended (2023-12-15: the
  CoinGecko price comes from dead venues, down to $0.14). 17 events verifiable on Binance spot; **2 confirmed (12%)**, below the 70% rule.
- **#430 — DOWNGRADED (not confirmed):** 19 events, none verifiable on an independent venue (DEX-only tokens or no Binance pair then).
- **#421 — not counted** (see above: confirmations only on a pufETH pool trading <$2/day).

**Mechanical fix (2026-11-26, before #440's data arrived):** #439–#441 read hourly closes by bar *open* time, so every window sat 1 h late.
`_px()` now reads the price at T as the close of the bar opening at T−1h. #439 and #441 re-run: still KILL (BTC −0.59% / +0.05%, t −0.82 / 0.64;
ETH −1.07% / −0.11%). #440 has been run only with the fix.

### Final (2026-11-26)
- #440 (with the timing fix; funding from the same Binance archive files via job `ubatchd`, since `ubatchc2` hung twice): **KILL**. BTC 552 events −0.15% t −1.95; ETH −0.30% t −3.45. Price moves *with* the paying side, not against it.
- #442 (Coinbase daily via job `ucb442`): **KILL**. BTC 73 events +0.05% t 0.06; ETH +0.95% t 0.98.
- **Batch C: 0 of 12 pass.** Output `docs/jx_runs/batch_c_20261126.txt` (re-run identical).

# Batch NF12 (#580–#583): Tokyo Stock Exchange daily price limits and retail margin calls — pre-registered 2026-11-28, before data are fetched

**Area (new):** Japanese single stocks. No earlier PREREG tests TSE price limits (keyword check: "limit-down", "stop-low", "TSE",
"margin call" give only #485 Japanese ETF dividends and #466 month-start buying, both different mechanisms).

**Payer (forced, non-economic):**
- Japanese retail margin traders (about ¥4–5 trillion of margin longs) must post extra margin (oishō) by day +2 or be liquidated at
  any price.
- A stock that closes at its daily limit-down (stop-low) has unfilled sellers queued at the limit. A buy order at the limit price
  fills against them.
- **G5 (assumed, to verify before any live use):** IBKR offers TSE stocks and accepts Malaysian residents. 100-share lots, so trades
  needing more than $3,000 for one lot (price > ¥4,500 at ¥150/$) are skipped.
- **G6:** price-limit studies exist (e.g. Kim & Rhee 1997 on the TSE). Retail-dominated small caps are too small for funds.

**Data (job `ubatchnf12`, GitHub Actions):**
- Yahoo daily OHLCV and split events for every 4-digit code 1300–9999 that Yahoo serves as `NNNN.T`, instrument type EQUITY,
  2015-01-01..2026-11-27; plus 1306.T (TOPIX ETF) as the benchmark.
- Prices are made raw (un-split-adjusted) with the split events, because limits depend on the raw price.
- **Limitations:**
  - Delisted stocks are missing (survivorship bias in favour of longs).
  - Codes with letters (new since 2024) are missing.

**Limit table (JPX, by previous raw close, yen):**
- <100: 30; <200: 50; <500: 80; <700: 100; <1,000: 150; <1,500: 300; <2,000: 400; <3,000: 500; <5,000: 700; <7,000: 1,000;
- <10,000: 1,500; <15,000: 3,000; <20,000: 4,000; <30,000: 5,000; <50,000: 7,000; <70,000: 10,000; <100,000: 15,000; else 30,000.

A **limit-down close** is:
- close = day low;
- close ≤ previous close − 0.95 × limit (tolerance for any table revision; expanded limits are larger and still qualify);
- volume > 0.

**Sizing:**
- Per trade: min($1,500, 1% of the day's turnover), $15,000 pot per day, scaled down pro rata.
- ¥150/$ fixed. Trades needing more than $3,000 for a 100-share lot are skipped.
- 20-day median turnover ≥ ¥20M (about $130K), so the stock is liquid enough.

**Costs:** 0.25% per side (commission, half-spread, slippage on small caps), 0.5% per round trip. The return is the raw stock
return, not the excess over TOPIX (holds are 1–2 days; the TOPIX excess is printed as context).

| # | Idea | Rule |
|---|---|---|
| 580 | **First limit-down close** (forced sellers queued at the limit) | Buy at the limit-down close on day 0 (previous day not a limit-down close); sell at the next day's close |
| 581 | **Second consecutive limit-down close** (margin calls escalate) | Buy at the close of the second consecutive limit-down close; sell at the next day's close |
| 582 | **TSE wick bids** (#520 rule on TSE stocks) | Resting bid at previous close × (1 − 4·σ30), clipped 5%..30%. Fills if the low ≤ bid × (1 − 0.5%); fill price min(bid, open); sell at that day's close |
| 583 | **Margin-call day** (TOPIX ETF closes ≥ 3% below its previous close on day 0) | At the close of day +1 (when unmet margin calls are liquidated), buy the 10 liquid stocks with the worst day −1→+1 two-day return; sell at the close of day +3 |

**Split:** Stage 1 = 2015-01-01..2020-12-31 (kill only: ≥ 30 trades and mean net ≤ 0); Stage 2 = 2021-01-01..2026-11-27, unseen.

**Stage 2 PASS:** all of
- ≥ 30 trades;
- mean net ≥ 0.3%;
- t ≥ 2;
- ≥ $3,000/yr;
- sum positive without the 3 best trading days;
- mean still > 0 with costs × 1.5.

**Context only (not verdicts):** #580 with exit at the next open; by-year means; share of events skipped for lot size.

**Script/output:** `scripts/batch_nf12_20261128.py` → `docs/jx_runs/batch_nf12_20261128.txt`, re-run identical.

## Withdrawn before any data was seen (2026-11-28, Jx)
Jx: "trying out other countries ... way too general and popular". Fails G6 on reflection: deep, professional markets where the
mechanism is published, unlike the thin crypto venues where #389/#520/#536 passed. Withdrawn with no data looked at (the NF12 Actions
fetch was cancelled mid-run; NF13 was never fetched). No result; candidate numbers stay reserved and are not reused.

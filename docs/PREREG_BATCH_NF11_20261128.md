# Batch NF11 (#576–#579): Reg SHO threshold-list forced buy-ins — pre-registered 2026-11-28, before data are fetched

**Payer (regulatory, non-economic).** Under SEC Reg SHO Rule 203(b)(3), a clearing firm with a fail-to-deliver in a threshold security
that persists for 13 consecutive settlement days must close it out by buying shares, at any price.
- **G5:** any brokerage account (IBKR, usable from Malaysia) can hold the stock and be the seller to those forced buyers.
- **G6:** mostly small caps, too small for most funds.
- Keyword check: no earlier PREREG mentions Reg SHO, threshold lists or fails-to-deliver.

**Data:**
- Nasdaq Trader daily threshold files (`nasdaqthYYYYMMDD.txt`, the threshold list of Nasdaq-listed securities), 2018-01..2026-11;
- Yahoo daily adjusted closes for every ticker that appears (job `ubatchnf11`).
- **Limitation:** tickers Yahoo no longer serves (many delisted) are missing. That survivorship bias favours longs, so results are
  reported with the share of events that had prices.

**Days on list:** consecutive trading days a ticker appears; day 1 = the first file listing it.

| # | Idea | Rule |
|---|---|---|
| 576 | **Close-out deadline** (forced buy-ins cluster around day 13) | Buy at the close of day 11 on the list, sell at the close of day 16 |
| 577 | **Addition** (new persistent fails mean future forced buying) | Buy at the close of day 1, sell at the close of day 13 |
| 578 | **Removal** (fails resolved, the forced buying ends) | Short at the close of the first day off the list after ≥ 13 days on it, cover 5 days later |
| 579 | **Long stay** (fails that persist past 13 days mean buy-ins keep coming) | On day 20 still listed: buy at the close, sell 5 days later |

**Excess** = side × (stock − SPY) − 0.2% round trip (small caps, wider spreads). Stocks under $1 at entry are excluded (not
practical, and the worst bad-print risk).

**Split:** events before 2023-01-01 = Stage 1 (kill if mean ≤ 0, ≥ 20 events); 2023 onward = Stage 2.

**Stage 2 PASS:** all of
- ≥ 30 events;
- mean ≥ 1%;
- t ≥ 2;
- sum positive without the 3 best;
- prices found for ≥ 60% of events (otherwise reported as survivorship-limited).

**$/yr:** $3,000 per event.

**Script/output:** `scripts/batch_nf11_20261128.py` → `docs/jx_runs/batch_nf11_20261128.txt`, re-run identical.

## Results (2026-11-28; `docs/jx_runs/batch_nf11_20261128.txt`, re-run identical): 0 of 4
2,322 daily files (all business days 2018–2026), 2,362 tickers, 1,412 with Yahoo prices (62–70% of events priced).

| # | Verdict | Stage 1 (2018–22) | Stage 2 (2023–26) |
|---|---|---|---|
| 576 close-out deadline long | KILL | −1.17% (366) | −4.61% (956, t −6.09) |
| 577 addition long | KILL | −3.10% (1,405) | −7.52% (3,162, t −5.68) |
| 578 removal short | FAIL | +2.13% (264, t 2.70) | +0.98% (705, t 0.81) |
| 579 long-stay long | FAIL | +0.43% (95) | −4.74% (300) |

**The forced buy-ins do not lift these stocks.** Threshold-list stocks underperform SPY strongly, even with survivorship bias
favouring the longs, since delisted names are missing.
- The obvious mirror, shorting at addition, fails G5 by construction. A security is on the list because shares cannot be delivered,
  so borrow is scarce or unavailable. It is not registered as a test.

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

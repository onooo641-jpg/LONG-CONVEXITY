# Batch NF13 (#584–#587): Hong Kong equities (crashes, Stock Connect closures, H-share dividend tax) — pre-registered 2026-11-28, before data are fetched

**Area (new):** Hong Kong single stocks and index ETFs.
- **Keyword check:** no earlier PREREG mentions Stock Connect, southbound, or HK dividends. #391 (HK IPO lots) is a different mechanism.
- **G5 (assumed, verify before any live use):** IBKR offers HKEX stocks to Malaysian residents. Long-only, so no borrow is needed.
- **G6:** HK penny-stock crashes and Connect holiday gaps are known to locals but too small or too irregular for funds. The dividend
  tax clientele is published.

**Payers:**
- **#584, #585:** forced sellers in HK small caps (broker margin calls; collapsing pump schemes). HK has no daily price limit.
- **#586:** absent mainland buyers. Southbound Stock Connect closes on mainland holidays while HKEX trades. Mainland flow
  (often HK$10–20bn a day) returns on reopening.
- **#587:** tax-driven sellers. Southbound mainland investors pay 20% tax on H-share dividends, foreign holders 10%, so they sell
  before ex-dates. A 10% payer keeps more of each dividend than the price drop takes, if the drop reflects the 20% clientele.

**Data (job `ubatchnf13`, GitHub Actions):**
- Yahoo daily OHLCV, split and dividend events for 4-digit codes 0001–9999 as `NNNN.HK` (instrument type EQUITY), plus 2800.HK
  (Tracker Fund) and 000001.SS (Shanghai Composite; its trading calendar marks mainland closures). 2015-01-01..2026-11-27.
- **Limitation:** delisted stocks are missing (survivorship bias in favour of longs).

**Common rules:**
- Prices are split-adjusted, not dividend-adjusted.
- **Costs:** 0.3% per side for small caps (#584/#585: commission, stamp duty 0.1–0.13%, spread); 0.2% per side for #587
  (larger stocks); 0.05% per side for 2800.HK (#586; ETFs are exempt from stamp duty).
- **Liquidity:** 20-day median turnover ≥ HK$5M; close ≥ HK$0.20 (no sub-tick penny stocks).
- **Size:** min($1,500, 1% of the day's turnover); $15,000 pot per day, pro rata; HK$7.8/$.

| # | Idea | Rule |
|---|---|---|
| 584 | **HK wick bids** (#520 rule) | Resting bid at previous close × (1 − 4·σ30), clipped 5%..30%. Fills if the low ≤ bid × (1 − 0.5%); fill price min(bid, open); sell at that day's close |
| 585 | **HK crash-day close** | A stock closes ≥ 40% below its previous close: buy at that close, sell at the next day's close |
| 586 | **Stock Connect reopening** | For every gap of ≥ 1 HK trading day on which Shanghai was closed: buy 2800.HK at the close of the last HK day before Shanghai reopens, sell at the close of the first day both trade. $15,000 per event |
| 587 | **H-share dividend tax clientele** | For each dividend with D / close(ex−1) ≥ 2%: buy at the close the day before ex-date, sell at the ex-date open. Return = (open_ex + 0.9·D) / close(ex−1) − 1 − costs. The 10% withholding is assumed for all stocks (conservative for HK-incorporated firms, which pay no withholding). $1,500 per event |

**Split:** Stage 1 = 2015-01-01..2020-12-31 (kill only: ≥ 30 trades, or ≥ 15 events for #586, and mean net ≤ 0); Stage 2 =
2021-01-01..2026-11-27, unseen.

**Stage 2 PASS:** all of
- ≥ 30 trades (#586: ≥ 15 events);
- mean net ≥ 0.3%;
- t ≥ 2;
- ≥ $3,000/yr;
- sum positive without the 3 best days;
- mean > 0 with costs × 1.5.

**Context only:** by-year means; #586 return of the same window when Shanghai was open (placebo: random HK days).

**Script/output:** `scripts/batch_nf13_20261128.py` → `docs/jx_runs/batch_nf13_20261128.txt`, re-run identical.

## Withdrawn before any data was seen (2026-11-28, Jx)
Jx: "trying out other countries ... way too general and popular". Fails G6 on reflection: deep, professional markets where the
mechanism is published, unlike the thin crypto venues where #389/#520/#536 passed. Withdrawn with no data looked at (the NF12 Actions
fetch was cancelled mid-run; NF13 was never fetched). No result; candidate numbers stay reserved and are not reused.

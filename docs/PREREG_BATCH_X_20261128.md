# Batch X (#532–#533): the wick mechanism outside crypto (US ETFs, FX) — pre-registered 2026-11-28, before data are fetched

**Why this area.** It passes the new desk checks (`docs/HANDOFF_NONPROP.md`, 2026-11-28):
- **G5:** a resting limit order at any broker can be the receiver of a forced seller's discount (margin calls, stop cascades, flash
  crashes such as 24 Aug 2015 in ETFs and the Jan 2019 JPY flash crash).
- **G6:** the crowded published effect is close-to-close short-term reversal; resting orders at volatility-scaled distances that
  fill only on intraday wicks are not that.
- **Independence:** no wick variant was ever judged on these markets or years, so this is an independent test of the #520 mechanism.
  It does not reuse the crypto 2025–26 window that #520–#529 leaned on.

**Venue:** US ETFs and spot FX via a broker such as IBKR (usable from Malaysia; GTC limit orders). FX "JPY margin-call bids" was
desk-rejected in Batch I only as "same family as the wick"; family 1 still counts once toward the goal.

**Rule (#520 adapted to markets that move less).**
- Each trading day, per instrument: a resting limit buy at previous close × (1 − X), X = 4 × σ30.
  - σ30 = stdev of the previous 30 daily close-to-close returns; X is clipped to [1%, 30%].
- **Fill** only if the day's low ≤ level × (1 − 0.1 X): it must trade through by a tenth of the distance. Bad prints in free daily
  data are a known risk, and the through-margin guards against them.
- Fill price = the level, or the open if the day opened below it. **Exit at that day's close.**
- Context (reported only): exit at the next day's close.
- **Costs:** ETFs 0.02% per side; FX 0.005% per side.
- **Size:** $5,000 per fill, one $15,000 pot per day, scaled down if exceeded.

| # | Universe (Yahoo daily OHLC, adjusted) | Dev (Stage 1, kill-only) | Unseen (Stage 2) |
|---|---|---|---|
| 532 | 34 liquid US ETFs: SPY QQQ IWM DIA XLE XLF XLK XLV XLY XLP XLI XLB XLU EEM EFA EWJ EWZ FXI GLD SLV USO UNG TLT HYG LQD VNQ SMH XBI KRE GDX ARKK TQQQ SOXL IBB | 2006–2015 | 2016–2026-11 |
| 533 | 14 FX pairs: USDJPY AUDJPY EURJPY GBPJPY NZDJPY CADJPY CHFJPY EURUSD GBPUSD AUDUSD NZDUSD USDCAD USDCHF USDMXN | 2006–2015 | 2016–2026-11 |

**Stage 1 KILL:** mean net per fill ≤ 0 (≥ 30 fills).

**Stage 2 PASS:** ≥ 30 fills, mean net per fill ≥ 0.2%, t ≥ 2, and $/yr ≥ $3,000.

**Also reported:**
- fills by year;
- profit without the best day;
- the next-day-exit context row.

**Script/output:** `scripts/batch_x_20261128.py` → `docs/jx_runs/batch_x_20261128.txt`, re-run identical.

**Data job:** `ubatchx` (Yahoo chart API, daily OHLC + adjusted close; OHLC is scaled by adjclose/close for ETFs).

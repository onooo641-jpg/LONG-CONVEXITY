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

## Results (2026-11-28; `docs/jx_runs/batch_x_20261128.txt`, re-run identical)
| # | Verdict | Stage 1 2006–15 | Stage 2 2016–26 | Note |
|---|---|---|---|---|
| 532 US ETFs | FAIL | +0.64%/fill (t 3.87, 293 fills) | **−0.53%/fill** (t −4.92, 360), win 30% | ETF dips at 4σ keep falling into the close; next-day exit +0.21% (t 0.88) |
| 533 FX pairs | FAIL (and **data artifact**) | +0.57% (t 8.1) | +0.87% (t 19.3, 83% win), $1.4K/yr at $5K/fill | See below |

**#533 is not real.** Diagnostic run after the verdict, not part of the rule:
- 97% of its 2016–26 fills are spike-only bars (open-to-close move < 0.2% with the low ≥ 4σ below). That is the signature of bad
  prints in Yahoo's free FX daily data.
- Examples fall on 2020-01-01 and 2024-01-01, when FX was closed.
- The spikes coincide across JPY pairs because the feed glitches hit all of them at once (97% "corroborated", by the glitch itself).
- **Lesson:** free daily FX lows cannot test resting-order ideas; tick or minute data is needed (Dukascopy is throttled, Batch I).

**Batch X verdict: 0 of 2.** The wick mechanism does not carry over to liquid US ETFs. Its forced sellers sit in crypto's 24/7,
highly leveraged perps.

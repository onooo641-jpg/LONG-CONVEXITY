# Batch NF9 (#568–#571): forced flows within hours on Hyperliquid — pre-registered 2026-11-28, before running

**Why.** All earlier forced-flow tests used daily candles. Hyperliquid's hourly candles (`wickscale_hl_1h`, 196 coins,
2026-04-24..2026-11-25) were never used to judge any rule.
- **Payers:** liquidated and stop-hit traders inside an hour (dips); chasers squeezing shorts inside an hour (spikes).
- **G5:** resting or market orders on HL. **G6:** intraday, small size, too small for funds.
- Family 1 (liquidations), and the squeeze mirror for #570.

**Split:** Stage 1 (kill-only) = 2026-04-24..2026-08-15; Stage 2 (unseen) = 2026-08-16..2026-11-25.

**σh** = stdev of the coin's previous 168 hourly close-to-close returns. Size = min($1,500, 1% of the hour's USD volume).

| # | Idea | Rule | Costs |
|---|---|---|---|
| 568 | **Hourly wick bids** | resting buy at previous hour's close × (1 − X), X = 4σh clipped to [1%, 20%]; fill if the hour's low ≤ level × (1 − 0.1 X); fill price = the level or the hour's open if lower; exit at the **next** hour's close | 0.015% + 0.045% |
| 569 | **Hourly cascade reversal** | hour return ≤ −5σh → buy at that hour's close, sell 4 hours later | 0.09% |
| 570 | **Hourly squeeze give-back** | hour return ≥ +5σh → short at that hour's close, cover 4 hours later | 0.09% |
| 571 | **Market-wide hourly flush** | BTC hour return ≤ −2% → buy an equal-weight basket of the 20 HL alts with the highest previous-30-day volume at that hour's close, sell 6 hours later (one event) | 0.09% |

One open trade per coin per idea.

**Stage 1 KILL:** mean net ≤ 0 (≥ 30 trades; #571 ≥ 8 events).

**Stage 2 PASS:** all of
- ≥ 30 trades (#571: ≥ 10 events);
- mean net ≥ 0.3%;
- t ≥ 2;
- sum positive without the 3 best.

**$/yr** = mean × size × trades scaled to a year.

**Script/output:** `scripts/batch_nf9_20261128.py` → `docs/jx_runs/batch_nf9_20261128.txt`, re-run identical.

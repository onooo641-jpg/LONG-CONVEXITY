# Live Topstep account vs the model: what to compare, predictions, gates — 2026-11-20

Written and committed **before** any live trade data exists in the repo. The predictions
come only from historical data (`scripts/live_predictions_20261120.py`,
output `docs/jx_runs/live_predictions_20261120.txt`, machine-readable `docs/live_predictions.json`).

## How live data gets here
On the trading computer, after trading days:
```
uv run python scripts/export_live_trades.py --start <first live day>
git add data/live && git commit -m "live data" && git push
```
This writes `data/live/fills.csv` (every fill, from ProjectX `Trade/search`) and
`data/live/decisions.csv` (the bot's placed/blocked/skipped orders from its journal).
No credentials are written. Then anyone runs `uv run python scripts/live_compare.py --backtest`,
which writes `docs/live_report.md`.

## What is compared, in order (each layer only matters if the one before it passes)
1. **Signal parity (does the bot do what the backtest does?).** Re-run the engine on the live
   days. For each backtest signal: did the bot place an order with the same direction and
   entry/stop/target within 1 tick? Any live order with no backtest signal is listed.
   **Gate: ≥ 95% match.** A miss is a bug or data difference to fix before anything else.
2. **Execution (do fills match the model's assumptions?).**
   - Fill rate of placed limit orders vs model **80%** (gate: within ±10 points).
   - Entry slippage vs model **0 ticks**; stop-exit slippage vs model **1 tick** (gate: mean ≤ 2);
     target exits vs **0 ticks**.
   - Costs per micro round turn vs model **$1.24**.
   - Contracts filled = contracts planned.
3. **Same-day outcome.** Live net R minus backtest net R on the same trade (should be ~0;
   a steady gap means costs or fills differ from the model).
4. **Outcome vs bands (is the edge behaving like the backtest?).** Cumulative net R of the
   last 20/40/60/100 live trades vs every run of that many consecutive historical trades.
   **Judged from 40 trades (~2.5 months).** Below the 5th percentile of both windows ⇒ the
   backtest does not describe live trading: stop scaling.
5. **Account milestones** vs the Topstep path predictions below (passes, busts, first payout).

## Predictions (from historical data; R = $900 risk, net of commission)
| | full 2016-01..2026-10 | recent 2024-01..2026-10 |
|---|---|---|
| trades per month | 16.8 | 16.9 |
| limit-order fill rate | 80% | 79% |
| win rate | 53.1% | 55.6% |
| mean net R per trade (sd) | −0.001 (0.98) | +0.083 (0.96) |
| exits at the stop | 46% | 43% |
| cumulative net R after 40 trades: 5% / 50% / 95% | −10.8 / +0.2 / +11.9 | −8.7 / +3.4 / +14.6 |
| after 100 trades: 5% / 50% / 95% | −20.4 / −1.0 / +20.8 | −8.1 / +5.8 / +23.5 |

Topstep 50K, starting on the 1st of each month (full: 118 starts; recent: 22 starts):
| | full | recent |
|---|---|---|
| days to first pass, median (5–95%) | 36 (6–293) | 26 (8–67) |
| evaluations bought before first pass, median (95%) | 3 (12) | 2 (5) |
| days to first payout, median | 145 | 88 |
| first payout within 90 / 180 days | 35% / 57% | 50% / 77% |
| net after 3 months, median (5–95%) | −$338 (−$636 to $3,205) | −$244 (−$631 to $4,472) |
| net after 6 months, median (5–95%) | $96 (−$1,072 to $6,603) | $713 (−$1,259 to $10,591) |
| net after 12 months, median (5–95%) | $1,704 (−$1,497 to $10,228) | $8,354 (−$807 to $12,469) |
| starts losing money over 12 months | 32% | 18% |

**Point predictions for the first 3 months live (one account, $900 risk):** about 50 trades;
win rate 50–58%; 2–3 evaluations bought before the first pass; first payout more likely
than not after month 3; net after 3 months most likely a small loss (−$250 to −$650), with a
~25% chance of being up. A loss in month 1–3 is the normal case and is not evidence against the model.
The recent window is the more optimistic reading and assumes the post-2024 behaviour continues;
the full window is the cautious one.

## Decision gates (no strategy-parameter changes either way)
- Parity < 95% or stop slippage > 2 ticks ⇒ fix the bot/execution first; numbers after that point
  are not comparable.
- After 40 trades: inside both bands ⇒ model holds so far; above the recent median ⇒ consider the
  second Topstep account; below the 5th percentile of both ⇒ stop adding accounts.
- After 100 trades and a first payout inside bands ⇒ proceed to the multi-firm plan
  (`docs/PREREG_PORTFOLIO_20261120.md`, B− then C−).

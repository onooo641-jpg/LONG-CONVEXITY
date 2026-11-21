# Manual entry delay: can a person place the bot's trades by hand? — 2026-11-21 (CANDIDATES #65)

Written and committed **before** any run. Stage 1-style quick test (data already in the repo).

## Why
Many prop firms ban full bots but allow alert-assisted manual entry (HANDOFF_NONPROP "semi-automated").
A person needs time to see the alert and place the bracket order. The model places the limit order at the
confirmation instant; 14.3% of trades fill inside the confirming bar (bridge/live.py notes).

## Test
Same NQ orders, same engine, $900 risk. Each order's resting window starts **d minutes later**
(valid_from + d); if the window would start after the order's expiry, the trade is missed. Everything else
unchanged. d = 0 (reference), 1, 2, 3, 5 minutes.
Reported per d: filled trades, win rate, net P&L, Topstep 50K recycling net and worst dip (2016-01..2026-10),
and the same for 2024-01..2026-10.

## Reading (decided now)
Manual entry is **viable** at delay d if Topstep 50K recycling net (2016–26) at d is at least 80% of d = 0
AND the 2024–26 recycling net at d is at least 80% of its d = 0 value. The largest viable d is the
maximum reaction time a person may take. If even d = 1 fails, the semi-automated category is dropped.

Command: `uv run python scripts/delay_20261121.py`

## Results (2026-11-21, `docs/jx_runs/delay_20261121.txt`)
| entry delay | Topstep 50K net 2016–26 (% of d=0) | 2024–26 (% of d=0) | verdict |
|---|---|---|---|
| 0 min | $44,359 (100%) | $25,172 (100%) | reference |
| 1 min | $43,516 (98%) | $20,401 (81%) | viable |
| 2 min | $43,986 (99%) | $22,720 (90%) | viable |
| 3 min | $37,348 (84%) | $21,028 (84%) | viable |
| 5 min | $27,080 (61%) | $15,077 (60%) | not viable |

**Largest viable delay: 3 minutes.** A person placing the bot's alert by hand within 3 minutes keeps ≥80% of the
recycling result. Note the raw trade edge falls faster (2024–26 raw P&L $43.1K → $30.6K at 1 minute): the prop-firm
structure, not the trade edge, carries most of the result. Next: the prop-firm sweep must list which firms' written
rules allow alert-assisted manual entry, then price each with the coin-flip test using the delayed trades.

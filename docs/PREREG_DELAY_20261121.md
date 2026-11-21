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

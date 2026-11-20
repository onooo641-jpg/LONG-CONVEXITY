# Futures firms with bots + renewal resets vs Topstep — pre-registration, 2026-11-20 (CANDIDATES #54)

Screened (third-party summaries of each firm's help centre unless marked):
- **Elite Trader Funding: excluded.** Terms prohibit automated systems unless authorised in writing; semi-automated only.
- **FXIFY Futures: excluded.** Expert Advisors / automated systems not permitted.
- **TradeDay: included.** Personal bots allowed inside NinjaTrader/Tradovate/TradingView (no external API, no purchased bots). Free reset at renewal (TradeDay help centre). Malaysia not on third-party restricted list.
- **Bulenox: included.** Bots explicitly allowed. Since 2026-08-17 no subscriptions, so no renewal reset; evaluations are one-time with a 30-day limit. Malaysia not on third-party restricted list.

Rules modelled (50K, risk $900/trade, 200 coin flips, seed 1, 2016-01..2026-10, LOCK_FIRST):

| | TradeDay Fast Pass 50K (opened after 2026-07-26) | Bulenox Momentum 50K, Option 2 EOD |
|---|---|---|
| price | $189/month list; $85 with the common 55% code (both run) | $143 one-time per attempt; reset price unannounced → rebuy |
| evaluation | $3,000 target, $2,000 EOD trailing, best day ≤45% | $3,000 target, EOD trailing **$2,000 assumed** (Legacy is $2,500), pass within 30 days |
| contracts | 5 minis = 50 micros, no ladder | 2/4/7 minis = 20/40/70 micros at <$1.5K / <$4K / above |
| funded | $2,000 EOD trailing, lock at start assumed | locks at start + $100 |
| payout | 5 days of ≥$150 AND best day ≤45%; 50% of balance, cap $1,500, min $250 | 5 days of ≥$150 AND best day ≤35%; amount above a $3,000 buffer, cap $1,500; account ends after 3 payouts (assumed) |
| split / activation | 80% (Funded Sim) / none | 90% / none |
| renewal reset | free (help centre) | n/a |
| other | $15/month platform/automation assumed | $15/month assumed |

Ranking against Topstep 50K on real net, coin-flip net and worst dip. No pass/fail.
Command: `uv run python scripts/firms2_20261120.py`

## Results (2026-11-20, `docs/jx_runs/firms2_20261120.txt`)

| product | real net 2016–26 | spent | worst dip | coin-flip median (profitable) |
|---|---|---|---|---|
| **Topstep 50K** (reference) | **$44,359** | $17,081 | −$3,520 | **$18,046 (98%)** |
| TradeDay Fast Pass 50K at $85/mo (code) | $35,678 | $13,000 | −$4,835 | $14,035 (96%) |
| TradeDay Fast Pass 50K at $189/mo (list) | $22,158 | $26,520 | −$10,035 | −$4,213 (31%) |
| Bulenox Momentum 50K Opt 2 | −$4,139 | $22,399 | −$10,840 | −$14,622 (0%) |

- **TradeDay with the discount code is the closest Topstep-like structure found so far**
  (80% of Topstep's real net, 78% of its coin-flip value), driven by the free renewal
  reset. It depends on the discount recurring every month (unverified) and on the bot
  running inside NinjaTrader/Tradovate/TradingView (TopstepX API code would need porting).
  At list price it is half of Topstep.
- **Bulenox Momentum loses money**: the 30-day evaluation limit expires many attempts,
  and payouts above a $3,000 buffer capped at $1,500 for 3 payouts return little.
- Low-confidence inputs: TradeDay funded lock level, Bulenox Momentum drawdown size
  ($2,000 assumed) and what follows the third Momentum payout.

## Verification, 2026-11-20 12:00
- TradeDay automation: no API exposed; bots must run inside NinjaTrader/Tradovate/
  TradingView (TradeDay help centre via TradersPost). The TopstepX bot would need a rewrite.
- Discount recurrence: **not settled.** Third-party pages conflict: one says renewals bill
  at the discounted price; another says affiliate codes cover the first month only;
  vendor norm is first month only. TradeDay's billing FAQ does not say. Treat the $189 list
  result ($22.2K) as the base case until confirmed at checkout or by support.

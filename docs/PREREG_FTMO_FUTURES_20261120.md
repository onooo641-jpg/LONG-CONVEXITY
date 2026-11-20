# FTMO verification + FTMO Futures vs Topstep — pre-registration, 2026-11-20 (CANDIDATES #53)

## Verified before running (FTMO's own pages unless marked)
- Malaysia is not on FTMO's restricted list; clients must be 18+ (ftmo.com/en/faq/who-can-join-ftmo).
- FTMO CFD rewards: claimable from day 14 after the first trade, account in profit, no
  open positions; profit can be rolled over (ftmo.com FAQ).
- FTMO's own trading-tips article recommends not risking more than 1% per trade idea, and
  its Forbidden Trading Practices bar "repeated simulated trading activity that results in
  higher Risk per Trade Idea". At 1% the CFD coin-flip result is negative (H3), so FTMO
  CFD's structural value at compliant risk is ~zero. **This retires #52 as an edge.**
- Why Topstep differs: no risk-per-trade rule; the model risks $900 against a $2,000
  limit (45% of the buffer), versus 10% of the buffer at FTMO CFD 1%.

## Test: FTMO Futures (launched 2026-08-31) vs Topstep 50K
FTMO Futures rules (third-party summaries of FTMO's Futures Trading Objectives page;
automation allowed per FTMO's futures Forbidden Trading Practices as cited by CrossTrade):

| | Growth 50K | Pro 50K |
|---|---|---|
| price | $119/month | $139/month |
| target | $3,000 | $3,000 |
| end-of-day trailing limit (locks at start) | $2,000 | $3,000 |
| daily loss | none in evaluation; soft $1,000 funded (no effect at 1 trade/day) | hard $1,000 |
| evaluation consistency | best day ≤ 40% | best day ≤ 50% |
| payout | every 4 days of ≥$150; 50% of profit, cap $2,500 | every 5 days of ≥$200; 100% of profit, cap $5,000 |
| split / activation | 90% / none | 90% / none |

Assumptions (unverified): reset $109 (Growth) / $129 (Pro), no free reset per rebill;
funded contract ladder same as Topstep's (2 → 5 minis on 50K, thresholds assumed);
$15/month automation/API cost; evaluation cap 10 minis. Pro is run withdrawing 100% and
50%. Risk per trade: $900 (Topstep, Growth), $800 for Pro (must stay under the $1,000
hard daily limit). 200 coin flips, seed 1, 2016-01..2026-10, LOCK_FIRST.

No pass/fail: a ranking against Topstep 50K on real-strategy net, coin-flip net, and
worst dip (largest fall in cumulative net).

Command: `uv run python scripts/ftmo_futures_20261120.py`

## Results (2026-11-20, `docs/jx_runs/ftmo_futures_20261120.txt`)

| product | real net 2016–26 | per year | spent | worst dip | coin-flip median (profitable) |
|---|---|---|---|---|---|
| **Topstep 50K** (reference, reproduces C2/C6) | **$44,359** | $4,098 | $17,081 | −$3,520 | **$18,046 (98%)** |
| FTMO Futures Growth 50K | $34,236 | $3,163 | $35,514 | −$9,675 | $1,906 (56%) |
| FTMO Futures Pro 50K, withdraw 100% | $28,452 | $2,628 | $32,920 | −$9,310 | $1,523 (56%) |
| FTMO Futures Pro 50K, withdraw 50% | $27,671 | $2,556 | $30,985 | −$10,825 | −$4,836 (30%) |

Sensitivity to the one assumption that matters, a free reset at each monthly renewal
(FTMO's futures FAQ only describes paid resets; Alpha, TradeDay, Elite, FXIFY Futures give
one): Growth $48,297, Pro (100%) $41,352 with it.

Verdict: **FTMO Futures is at best about Topstep's level (+9% if renewal resets are
free) and otherwise ~25–35% worse, with a dip 2.7× deeper**. Price ($119–139/month vs
$49) and paid resets are the difference; no structural advantage. Not a new loophole;
at most a second firm for diversification once the renewal-reset rule is confirmed.
FTMO Futures also allows 3 Sim-Funded accounts (CrossTrade summary) vs Topstep's 5.

#52 (FTMO CFD) is retired as an edge: at FTMO's recommended ≤1% risk the coin-flip
result is −$2,570 (H3). The real strategy still nets $38,694 there (H4), which is
strategy edge, not structure, and it would need porting to MT5/cTrader index CFDs.

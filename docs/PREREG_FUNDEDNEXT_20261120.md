# Adding FundedNext Futures (Rapid Pro 50K) to the mixed plan — 2026-11-20 (CANDIDATES #64)

Written and committed **before** any run.

## Firm screen
- FundedNext Futures: bots allowed in Challenge and funded accounts, through any integration that connects
  to Tradovate (fundednext.com general rules; helpfutures.fundednext.com article 14298560). Reachable
  with the same CrossTrade route as Lucid/MFFU.
- Tradeify: bots allowed only if the strategy is **not used at other prop firms** (Tradeify guidelines as
  summarised by TradersPost/Phidias) — excluded, since this strategy runs at Topstep.

## Rules modelled (Rapid Pro 50K; official help pages unless noted)
- Challenge: target $3,000; EOD trailing MLL $2,000; no consistency, no daily limit; 40 micros.
- Funded: EOD trailing $2,000, locks at +$100 (third-party: lock point $50,100); 40% consistency, minimum
  3 days; $500 profit per cycle (third-party); payout 50% of profit up to the cap (third-party);
  cap **$1,000** (official page shows 50K "$1,000 → $1,250"; $1,250 run as sensitivity); minimum $250;
  90% split; account ends after 5 payouts.
- Price $159.99 one-time with a code (third-party), same price to rebuy; no activation fee.
- Platform: CrossTrade already paid for Lucid/MFFU, so no extra cost.

## Tests
1. Single account, NQ: real net and coin flip (200 runs, seed 1) vs Topstep 50K.
2. Add 5 FundedNext accounts (3 NQ / 1 ES / 1 YM, anti-hedge filter) to C-mix (PREREG_MARKETMIX part 2).

## Reading (decided now)
FundedNext is **worth adding** if it raises C-mix net by at least 10% while net per $ of cash on hand
falls by no more than 10%.

Command: `uv run python scripts/fundednext_20261120.py`

## Results (2026-11-20, `docs/jx_runs/fundednext_20261120.txt`)
- Single NQ account: real net **$14,482** (cap $1,000) / $21,416 (cap $1,250); coin-flip median −$608 (46%
  profitable) / $4,818 (69%). Topstep 50K: $44,359 / $18,046 (98%). Low payout caps, a 50% payout share and
  the 5-payout limit make it a weak structure.
- Added to C-mix (5 accounts, mixed markets): net +11.2% but cash on hand +86.9% ($21,097 → $39,424);
  net per $ of cash −40.5%. **Not worth adding.**

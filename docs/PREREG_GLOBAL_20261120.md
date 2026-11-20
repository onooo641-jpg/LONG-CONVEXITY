# Global structural-edge search, round 1 — pre-registration, 2026-11-20 (CANDIDATES #55)

Search principle (unchanged): products whose own rules pay even random trading. Not
Malaysia-specific; still must be usable by an 18-year-old Malaysian resident.

## Why the search stays inside "evaluation-style" products
Classes screened and set aside (reasoning, no test):
- Matched betting / sportsbook promos: real structural edge elsewhere, but online
  betting is illegal for Malaysian residents and accounts get limited.
- Bank / broker sign-up bonuses: US/UK-resident only; small.
- CFD broker deposit bonuses: credit usually adds margin, not loss absorption; offshore
  CFD brokers are unlicensed for Malaysian residents.
- Airdrop / points farming: positive on average historically for some programs, but
  survivorship-biased, sybil rules, offshore-DeFi grey area; not testable with
  rules-based data. Logged as idea, not tested.
- Funding/basis carry, post-listing shorts, depeg buying: already tested and failed (#29-#47).

## Test A — Breakout (Kraken) 1-Step, 50K, static drawdown, on-demand payouts
Rules (third-party summaries of Breakout's help centre): one-time fee, no time limit,
no min days, no consistency rule; daily loss 3% of the day's opening balance incl.
floating P&L; max loss static from the starting balance, also when funded, never moves
after payouts; payouts on demand, $50 minimum, no cap; split 80%; evaluation fee
refunded with the first payout (one source; run with and without).

| plan | fee | target | static max loss |
|---|---|---|---|
| Classic 50K | $400 | $5,000 | $3,000 |
| Pro 50K | $280 | $6,000 | $2,500 |
| Turbo 50K | $180 | $4,500 | $1,500 |

Model: withdraw every positive balance at day end (on demand); one account slot,
sequential; NQ trade stream as proxy for the Nasdaq perp (perp funding not modelled);
risk per trade 25% / 33% / 43% of the max loss, capped below the $1,500 daily limit.
Malaysia not on Breakout's ineligible list (Breakout help centre). Bot policy unclear.

## Test B — Tradeify Lightning 50K (no evaluation)
$492 one-time; EOD trailing $2,000 locking at start + $100; 40 micros max; payout needs
fresh profit of $3,000 (first) / $2,000 (later) and consistency 20%/25%/30% (25% used);
withdrawal cap $1,500 assumed ($2,000 sensitivity); 90% split; a breach is a repurchase.

Both: 200 coin flips, seed 1, 2016-01..2026-10, compared with Topstep 50K. No pass/fail.
Commands: `uv run python scripts/global_round1_20261120.py`

## Results (2026-11-20, `docs/jx_runs/global_round1_20261120.txt`)

Leverage matters: the NQ trades need a median 13x notional on a 50K account (p10 5.5x,
p90 29x). Kraken Prop (Breakout's current brand) raised Nasdaq 100 / S&P 500 leverage
to 10x (Kraken blog), so the realistic rows are the 10x ones. Each trade is shrunk to
fit 10x notional.

| product (50K) | real net 2016–26 | coin-flip median (profitable) | worst dip |
|---|---|---|---|
| **Topstep** (reference) | **$44,359** | **$18,046 (98%)** | −$3,520 |
| Breakout/Kraken Prop Classic, risk ≤$950, 10x, fee refund | $44,663 | $15,203 (94%) | −$8,224 |
| same, no refund | $38,263 | $10,679 (88%) | −$9,024 |
| Breakout Classic, risk ≤$1,250, 10x, refund | $57,215 | $24,507 (96%) | −$6,235 |
| same, no refund | $49,215 | $17,863 (93%) | −$7,035 |
| Breakout Pro, risk ≤$1,050, 10x, refund | $34,381 | $10,857 (90%) | −$5,160 |
| Breakout Turbo (any risk) | ≤$17,843 uncapped | ≤$2,635 | — |
| Tradeify Lightning, cap $2,000 / $1,500 | $40,998 / $20,196 | $10,776 / −$4,089 | −$11,007 / −$12,837 |

Without any leverage cap Breakout Classic looked far better ($67–105K); that was the
model ignoring the cap, not the firm.

Verdict: **Breakout/Kraken Prop Classic is Topstep-level, up to ~1.3x with the fee
refund and ~$1,250 nominal risk** (actual risk mostly set by the 10x cap). It is the
first non-Topstep structure that matches it, from an exchange-owned firm, Malaysia not
restricted. Open items before any purchase: bot/API policy (unpublished), Breakout's
prohibited-practices text on risk per trade, whether Kraken Prop rules match the
Breakout rules used here, the fee refund, and perp funding/fees vs NQ commissions.
Tradeify Lightning depends on its unverified withdrawal cap.

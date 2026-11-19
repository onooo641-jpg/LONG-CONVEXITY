# Lucid Trading (LucidFlex 50K) — pre-registration, 2026-11-20 (CANDIDATES #36)

Committed before the run. Results go in a dated section at the end.

## Why Lucid

Of the futures prop firms checked, Lucid's own help center says outright that
"automated trading systems and trade copiers are permitted" (Permitted
Activities article). Third-party surveys in September 2026 found unattended
automation allowed only at Lucid, MyFundedFutures, FundedNext Futures and
Tradeify. Apex, Take Profit Trader, Alpha Futures and others ban bots.
MyFundedFutures' policy is described inconsistently ("semi-automated with
oversight"), and FundedNext pays 80/20 with small caps, so Lucid is tested
first.

## Rules modelled

**From Lucid's help center** (LucidFlex Payouts article, dated 2026-07-28):
- A payout needs 5 days of at least $150 profit (50K) in the cycle, plus
  positive net profit for the cycle.
- Minimum payout $500. Maximum 50% of profit, up to **$2,000** on a 50K; the
  caps don't scale.
- **5 payouts per account**, after which the account "moves live".
- 90/10 split.

**From third-party pages** (not read on Lucid's own site):
- Evaluation: +$3,000 target, $2,000 end-of-day trailing loss limit, 50%
  consistency (not binding at one ~$900 trade a day), 40 micros.
- The loss limit locks at starting balance **+$100** once the balance passes
  $2,100, or at the first payout.
- Funded: the same trailing limit and lock, no scaling plan assumed (40
  micros), no daily loss limit.
- Prices: evaluation **$115** one-time, reset **$90**, no activation fee, no
  monthly fee. A blown funded account can't be reset, so the replacement is a
  new $115 evaluation.
- Data/platform cost assumed **$15/month** (non-professional CME data, quoted at
  $5–15).

**Conservative assumption:** after the 5th payout the account is treated as
finished. LucidLive (real capital) rules aren't modelled; whatever it pays
would come on top of these figures.

**Not modelled:** Lucid no longer supports ProjectX (third-party, December
2025), so live trading would need a new Tradovate or Rithmic connection. That's
engineering work, not part of this test.

## Test

The same NQ trades as the Topstep headline ($900, `LTFSweepConfig()`, one a
day, 2016-01-01..2026-10-28 and 2010-07-01..2015-12-31), `Policy.LOCK_FIRST`.

**Passes** if, in 2016–2026, (a) Lucid's net is above the 95th percentile of
its own 200 coin flips, and (b) net per dollar of worst cash dip is at least
Topstep's (C2 ÷ |C4 worst| = 44,359 / 3,520 = 12.6). 2010–2015 is reported.

Command: `uv run python scripts/lucid_test_20261120.py`

## Results (2026-11-20, run once, `docs/jx_runs/lucid_test_20261120.txt`)

The Topstep side reproduces the ledger exactly (C2, C4, C6), so the extended
model is consistent.

| 2016–2026, $900, same trades | Topstep 50K | LucidFlex 50K |
|---|---|---|
| net | $44,359 | **$37,523** |
| withdrawn / spent | $61,440 / $17,081 | $55,723 / $18,200 |
| pass rate / payouts | 34.4% / 44 | 33.5% / 40 |
| beats coin flips | 98% | 98% |
| deepest cash dip, worst of 118 starts | −$3,520 | **−$4,720** |
| net per $ of worst dip | 12.6 | 7.9 |
| 2010–2015 net | −$2,505 | −$701 |

**Verdict: fail.** (a) is met: Lucid's edge over a coin flip is the same as
Topstep's. (b) is not: Lucid needs a deeper cash reserve for less money. The
cost lines show why. Topstep's monthly subscription includes a free reset
credit; Lucid charges $90 for every evaluation bust ($9,810 in resets in
total).

What it means: Lucid isn't a better first choice than Topstep. As a second
firm, after Topstep's 5 accounts, it still adds about $37K per account slot
over 11 years in the backtest, at about $4,700 of reserve per slot. It also
needs a new Tradovate or Rithmic connection, and LucidLive after 5 payouts
isn't modelled.

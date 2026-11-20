# Non-prop-firm loophole hunt — pre-registration, 2026-11-20 (CANDIDATES #49–#52)

Same search principle as the prop-firm finding: look for places where **a
product's own rules pay the customer more than the risk**, not for price
patterns in free data. Malaysia-legal, available to an 18-year-old resident,
no geoblock workarounds. Written before any data below was collected.

## #49 Bursa IPO public ballot
Hypothesis: Bursa IPOs are priced below where they trade on day one, and the
public tranche is allotted by ballot with refunds, so applying to every IPO is
a lottery with positive value.
- Data: every Main/ACE Market IPO with a public tranche, 2024-01 to latest,
  with issue price, first-day close, and public-tranche oversubscription X.
  Sources: news reports (The Star, The Edge, NST, Bernama, Moomoo recaps).
- Per IPO: first-day return r = close/issue − 1; expected fill fraction
  f = 1/(1+X); value per RM applied e = f × r.
- Pass if: mean e > 0.5% per application, mean e > 0 in each half of the
  sample (by listing date), and the share of IPOs with r < 0 is under 35%.
- Then: expected RM per year for a RM10,000 application each time, after
  application fee (RM1–2) and selling costs (~0.25% incl. stamp duty, min fee).
- Known model gap: Malaysian ballots favour small applications ("equitable
  distribution"), so fill on a large application can be below 1/(1+X). Bounds
  given, not hidden.

## #50 Guaranteed government matches and fixed-price funds
Hypothesis: some schemes pay a fixed bonus above any market rate.
- i-Saraan (EPF, self-employed): 20% match, capped RM500/yr, RM5,000 lifetime.
- EPF voluntary dividend, ASM fixed-price fund distributions, best FD rates.
- Pass if a scheme pays > 2× the best risk-free deposit rate for its
  first year. Report liquidity locks.

## #51 Price gaps between Malaysian crypto exchanges and global prices
Hypothesis: MYR crypto venues are small and niche, so their prices drift
from global prices by more than fees.
- Test now: snapshot Luno (MYR) vs a global USD price × USD/MYR; snapshot
  any other registered Malaysian exchange with a public price feed.
- Pass to stage 2 (a week of 15-minute logging) only if a snapshot gap
  exceeds round-trip fees + 0.3%.

## #52 Static-drawdown prop firms (control: not a new idea class)
Only if time allows: coin-flip test of a static max-loss firm, since
random walks are worth more under static floors than under trailing ones.

## Results (2026-11-20)

### #49 Bursa IPO ballot: FAIL (pre-registered rule); small positive on average, not reliable
Data deviation: Bursa's and i3investor's pages block automated access, from this
workspace and from GitHub, so "every IPO" was not reachable. Used 19 IPOs
(2024-05..2026-11) hand-collected from news search results, one source per row
(`data/public/ipo_sample_20261120.csv`), deliberately including the flops found.
Skewed to 2026 (14 of 19).
Run: `uv run python scripts/ipo_test_20261120.py` → `docs/jx_runs/ipo_test_20261120.txt`.

- First-day close vs issue: mean +45.8%, median +28.0%, but **37% closed below issue**.
- Pre-registered value per RM applied, r/(1+X): mean 0.40% (halves +1.69% / −0.76%),
  r<0 share 37% > 35% → **FAIL**. RM10,000 pro-rata ≈ RM40 per IPO.
- Post-hoc (not pre-registered): average profit per application, from tranche
  shares × price × r ÷ applications, which needs no allotment-rule assumption:
  mean RM266–311, median RM139–201 per IPO → RM7.7K–17K/yr at 55 IPOs/yr,
  bootstrap 90% range RM2K–31K. But the average applicant applies ~RM31–35K per
  IPO, and one person gets one application per IPO.
- The losers had low oversubscription (Evocom 3.6×, PSP 5.9×, Eckem 8.1×), but X
  is only published after applications close, so it can't be used to choose.
- Late 2026 turned weak: 4 of the last 7 in the sample closed at or below issue.

### #50 Guaranteed schemes
- **i-Saraan (EPF, self-employed): PASS, tiny.** 20% government match on up to
  RM2,500/yr (RM500/yr, RM5,000 lifetime), plus EPF dividend (6.15% for 2025).
  First-year return ~26% vs best 12-month FD promo ~4.0%. But 75% is locked to
  age 55 and 15% is purpose-restricted; only 10% (Akaun Fleksibel) is withdrawable.
- **ASM / ASM2 / ASM3 fixed-price funds: FAIL rule (5.00% vs 4.0% FD, not 2×),**
  but the best liquid parking for idle MYR cash found (redeemable at RM1).

### #52 Static-drawdown prop firm (FTMO 2-Step 100K, third-party rule summaries)
Run: `uv run python scripts/static_dd_20261120.py` → `docs/jx_runs/static_dd_20261120.txt`.

| risk per trade | coin-flip median net 2016–26 | coin flips profitable | real strategy net |
|---|---|---|---|
| $1,000 (1%) | −$2,570 | 40% | $38,694 |
| $2,000 (2%) | $32,683 | 91% | $142,746 |
| $3,000 (3%) | $93,174 | 100% | $224,198 |

The structure pays random play once risk per trade is ≥2% of the account: with a
fixed floor, expected withdrawals per funded account ≈ split × buffer
($8K on 100K). But FTMO's own Forbidden Trading Practices bar trading that raises
"Risk per Trade Idea" and require risk management "replicable in real markets";
3% is likely to be treated as gambling, 2% is borderline, 1% is safe.
Malaysia is not on third-party restriction maps (not verified on FTMO's site).
The model assumes the balance resets to the start after each payout, and checks
the daily loss only on realised P&L. Both are unverified/optimistic.

### #51 MYR crypto exchange gap: FAIL (no stage 2)
Run: `uv run python scripts/myx_gap_20261120.py` → `docs/jx_runs/myx_gap_20261120.txt`
(six GitHub-runner snapshots, 02:31–03:23 UTC). Other registered Malaysian
exchanges had no reachable public price feed (Tokenize/SINEGY DNS failures,
Hata/MX Global 404).
- Luno trades **+0.38% to +0.55% above** Kraken × USD/MYR on BTC, ETH, SOL and
  XRP alike, with one-tick spreads (professional market makers present).
- The gap is the same for every coin, so it reflects the cost of moving money
  into/out of MYR (and a daily FX reference rate), not a coin mispricing.
  Capturing it means buying offshore in USD and converting MYR back, and bank/
  Wise FX spreads (~0.4–1%) plus fees exceed the gap + 0.3% bar → FAIL.

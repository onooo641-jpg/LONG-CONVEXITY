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

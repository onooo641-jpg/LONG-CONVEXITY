# Portfolio 2: staggered account starts and corrected platform costs — 2026-11-20 (CANDIDATES #61)

Written and committed **before** any run. Deployment choices only; no strategy parameter changes.

## Changes from PREREG_PORTFOLIO_20261120
1. **Costs.** One ProjectX/TopstepX API subscription ($14.50/mo) covers every Topstep account
   (ProjectX: one subscription regardless of where you trade); the old model charged it per account.
   Lucid and MFFU need a Tradovate route: CrossTrade Pro **$49/mo once** for all their accounts,
   replacing the $15/mo-per-account placeholder. Breakout dropped (Kraken Prop has no API).
2. **Staggered starts.** N slots at one firm start on consecutive months instead of the same day.
   Same trades, same rules; each slot is an independent pipeline from its own start date.

## Portfolios (2016-01-01 .. 2026-10-28)
- A: Topstep ×1
- B−c: Topstep ×1 + Lucid ×1 + MFFU ×1, corrected costs
- C−sync: Topstep ×5, Lucid ×5, MFFU ×3, all slots of a firm start together on the firm's mean
  stagger month (Topstep/Lucid 2016-03-01, MFFU 2016-02-01), corrected costs
- C−stag: same slots, starts staggered monthly (Topstep/Lucid 2016-01..05, MFFU 2016-01..03),
  corrected costs. Same total slot-months as C−sync.

## Metrics
Total net and per year; worst dip from a previous peak; most out of pocket; cash on hand = larger
of the two; longest time below a previous peak; losing calendar years.

## Reading (decided now)
Staggering is **worth doing** if C−stag's cash on hand is at least 15% below C−sync's with net within
5%. Otherwise synchronized and staggered are equivalent and the simpler one (buy as cash allows) stands.

Command: `uv run python scripts/portfolio2_20261120.py`

## Results (2026-11-20, `docs/jx_runs/portfolio2_20261120.txt`)
| portfolio | net 2016–26 (/yr) | cash on hand | longest below peak | losing years |
|---|---|---|---|---|
| A Topstep ×1 | $44,359 ($4,097) | $3,520 | 44.8 mo | 4 |
| B−c Topstep + Lucid + MFFU, corrected costs | $113,827 ($10,512) | $14,590 | 50.2 mo | 4 |
| C−sync max slots, same start | $532,382 ($49,166) | $49,792 | 44.9 mo | 4 |
| C−stag max slots, monthly stagger | $531,867 ($49,119) | $50,502 | 46.2 mo | 3 |

- **Staggering does nothing** (net −0.1%, cash +1.4%): with the same trades, staggered accounts fall back
  into step after their first bust, so losses still land together. Buy accounts as cash allows; timing
  them does not reduce risk.
- **Corrected plan figures:** one slot per firm ≈ **$10.5K/yr, ~$14.6K cash on hand**; max slots ≈
  **$49K/yr, ~$50K cash on hand** (one API subscription per platform instead of per account).
- 2016–18 still lose at every scale; most income is 2023–26.

# Money needed to start: LucidDaily 50K EOD vs Topstep 50K (descriptive, 2026-11-25)
**Status: descriptive, no pass/fail.** Jx asked how much cash a LucidDaily start needs, the same question `scripts/jx_capital.py` answered for
Topstep (NOTES_JX "Money needed, starting a fresh chain"). Written together with the first run (an exploratory run was looked at first), so it
decides nothing; it only reports. No rule or strategy parameter is changed.

**Method.** Rules, prices and trades exactly as `scripts/portfolio_my_20261123.py` (friend's NQ trades 2016-01..2026-10, $900 risk;
LucidDaily 50K EOD at $85.40 promo and $122 list, reset = purchase price (assumed); Topstep 50K Consistency path). A fresh chain starts on the
first of each month 2016-01..2025-10 (118 starts). Per start: deepest cumulative cash (fees minus payouts), days to first payout, net after
12 months. Not included: CrossTrade ($49/month, needed for a bot on Lucid) and TopstepX API ($14.50/month).

**Command.** `uv run python -m scripts.lucid_start_capital_20261125` → `docs/jx_runs/lucid_start_capital_20261125.txt` (re-run identical).

## Results (2026-11-25)
| | LucidDaily $85.40 | LucidDaily $122 | Topstep Consistency |
|---|---|---|---|
| deepest loss, median | −$683 | −$1,054 | −$735 |
| 1 in 4 starts worse than | −$1,687 | −$2,410 | −$1,248 |
| 1 in 10 worse than | −$2,673 | −$3,819 | −$2,583 |
| worst start | −$3,758 | −$5,368 | −$3,520 |
| days to first payout, median / 90th pct | 158 / 826 | 158 / 826 | 126 / 827 |
| net after 12 months, median (share losing) | $3,971 (30%) | $3,239 (32%) | $1,704 (30%) |
| starts 2023+: median deepest / days to payout | −$342 / 78 | −$488 / 78 | −$418 / 63 |
Every start eventually went positive on all three.

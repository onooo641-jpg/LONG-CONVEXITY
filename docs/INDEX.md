# Map of this repo, by workstream (start here)

The repo holds three separate things. They share tools (backtest engine, pre-registration rules, figures
ledger) but **not** results: a number from one workstream says nothing about another.

---

## A. Prop-firm account recycling (the main business)
Automated NQ strategy run on Topstep (and later Lucid / MyFundedFutures) evaluations; income comes from the
firms' rules. Status: backtest + paper forward log; first live Topstep account being set up.

| What | Where |
|---|---|
| What the business is and how it works | `README.md` |
| How to go live (Chinese) and the live-account checklist | `docs/GO_LIVE.md`, `docs/WINDOWS_SETUP.md`, `bridge/README.md` |
| Running NQ + ES + YM on separate accounts (later) | `docs/MULTI_MARKET.md` |
| Live account vs model: what is compared, predictions, gates | `docs/PREREG_LIVE_20261120.md`, report in `docs/live_report.md` once data exists |
| Current plan figures | `docs/PREREG_PORTFOLIO2_20261120.md`, `docs/PREREG_MARKETMIX_20261120.md` |
| Firms compared (Topstep, Lucid, MFFU, FTMO, TradeDay, Bulenox, Breakout, TFD, FundedNext…) | `docs/PREREG_STRUCTURE_SCAN_20261120.md`, `PREREG_FTMO_FUTURES_*`, `PREREG_FIRMS2_*`, `PREREG_GLOBAL_*`, `PREREG_ROUND3_*`, `PREREG_FUNDEDNEXT_*` |
| Account size, market mix, staggering, manual-entry delay | `PREREG_SIZEMIX_*`, `PREREG_MARKETMIX_*`, `PREREG_PORTFOLIO2_*`, `PREREG_DELAY_20261121.md` |
| Running log, prop-firm sections | `docs/NOTES_JX.md`: sections up to "Liquidation test #100" (except the liquidation/BNB "Action for Jx" items) |
| Candidate numbers | `docs/CANDIDATES.md` rows **#1–#65** |

## B. Non-prop opportunities: liquidation bonuses (#100)
Bot that liquidates unhealthy Aave loans on smaller chains for the protocol's bonus. Separate code, separate data.

| What | Where |
|---|---|
| 24-month test and verdict (BUILD, simulate-only) | `docs/PREREG_LIQUIDATIONS_20261120.md`; `docs/NOTES_JX.md` "Liquidation test #100: verdict" |
| 4-week shadow test (no money) | `docs/PREREG_LIQ_SHADOW_20261121.md`; progress in `docs/NOTES_JX.md` "Liquidation shadow test: progress"; logs `data/shadow/` |
| Replay test (gas bidding, latency, Chainlink SVR) | `docs/PREREG_LIQ_REPLAY_20261121.md` |
| Code | `scripts/liquidations_20261120.py`, `scripts/liq_*.py`, `contracts/` |
| Decisions/costs for Jx | `docs/NOTES_JX.md` "Action for Jx" (Etherscan key; always-on hosting) |
| Candidate number | `docs/CANDIDATES.md` row **#100** (non-prop numbering starts at #100) |

## C. Non-prop search and radar
Everything else tried outside prop firms, and the plan for finding new opportunities.

| What | Where |
|---|---|
| What was tried, why it failed, rules for new ideas (five-part filter, staged tests, radar design) | `docs/HANDOFF_NONPROP.md` |
| Earlier non-prop tests | `PREREG_LOOPHOLES_*`, `PREREG_TOP10_*`, `PREREG_BATCH2_*`, `PREREG_POSTLISTING_*`, `PREREG_NONPROP2_*` |
| **Radar** (daily Actions job): design, thresholds, test queue | `docs/PREREG_RADAR_20261121.md`; code `scripts/radar.py`, `.github/workflows/radar.yml`; watch lists `docs/radar/` |
| Radar outputs: candidate table, near-miss table, page diffs, latest summary | `data/radar/candidates.parquet`, `nearmiss.parquet`, `changes.parquet`, `latest_summary.md`, `propfirm_snippets.md` |
| Prop-firm sweep (bot / alert-assisted policy per firm, pricing) | `docs/radar/prop_firms.csv`; `scripts/radar_price.py`, `scripts/radar_models.py` |
| Weekly radar tests | `docs/PREREG_INCENTIVES_W1_20261121.md` (#201–#203) |
| Weekly "Radar" summaries | `docs/NOTES_NONPROP.md` |
| Candidate numbers | `docs/CANDIDATES.md` rows **#200 upward** |

---

**Shared:** `CLAUDE.md` (rules for every session), `docs/FIGURES_LEDGER.md` (every figure with its command;
section titles name the workstream), `docs/jx_runs/` (raw outputs).
From 2026-11-21, new non-prop write-ups go to `docs/NOTES_NONPROP.md`; prop-firm write-ups stay in `docs/NOTES_JX.md`.

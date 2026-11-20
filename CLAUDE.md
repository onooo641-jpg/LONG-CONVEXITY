# Working in this repo (read first)

Owner: Jx. Project: prop-firm account recycling (Topstep 50K) with a friend's automated NQ
strategy, plus a search for other structural edges. README.md explains the business.

## Standing rules
- Branch: all work goes on `claude/ict-trading-resources-ugh07b` (the fetch workflow only
  runs on it). Two sessions may work at once: run `git pull --rebase` before every commit
  and push, and never force-push. Do not merge other branches unless Jx asks.
- No strategy-parameter changes (mechanical fixes are fine). Do not reinstate the 11:00 cutoff.
- **Pre-register every test before running it**: write `docs/PREREG_<NAME>_<YYYYMMDD>.md`
  (question, data, exact rule, costs, pass criteria), commit and push it, then run.
- Every reported figure needs a reproducible command and a row in `docs/FIGURES_LEDGER.md`;
  raw output goes to `docs/jx_runs/<script>.txt`; re-run once and confirm identical output.
- Each tested idea gets a row in `docs/CANDIDATES.md`. Numbering: main branch continues
  from #60; the non-prop branch uses #100 upward to avoid collisions.
- Be honest about uncertainty; say which facts are verified vs third-party vs assumed.
- Never commit API keys or secrets. Spending money needs Jx's explicit approval.
- The friend's live trading runs on the friend's own computer and account.
- No help evading prop-firm rules or bot detection; no geoblock circumvention.
- Opportunity lists: structural, data/economics-driven edges only. Leave out Jx's YouTube,
  homestay or other creativity-dependent ventures. Prefer non-Malaysia-focused ideas with
  ROI comparable to Topstep recycling.
- Jx wants work carried through to a conclusive answer without asking permission at each step.

## Benchmark every idea against
Topstep 50K recycling, 2016–26: **$44,359 real net ($4,097/yr)**, coin-flip median $18,046
(98% profitable), worst dip −$3,520. Multi-firm plan figures: `docs/PREREG_PORTFOLIO2_20261120.md` (Topstep + Lucid + MFFU,
Breakout dropped: no API) and `docs/PREREG_MARKETMIX_20261120.md` (NQ/ES/YM mix with anti-hedge filter).

## Tools in the repo
- `backtest/recycle.py`: `XFARules` + `recycle()` model any prop-firm rule set
  (trailing/static drawdown, buffers, caps, ladders, consistency, one-time pricing, instant funding).
- Friend's trades: `simulate(pd.read_parquet(D.PROCESSED_DIR / "ideas_orders_NQ.parquet"), D.load("1m"),
  BacktestConfig(risk_per_trade_usd=900))`, see any `scripts/*_20261120.py` for the pattern.
- Coin-flip structural test: same trade sizes, random sign, commission kept, 200 runs, seed 1.
- Free public data: the sandbox network blocks most sites. Add a job to `scripts/fetch_public.py`,
  put its name in `.github/fetch_public_request.txt` and push; GitHub Actions (US servers) runs it
  and commits `data/public/*.parquet`. Existing data: Hyperliquid candles/funding, DefiLlama
  lending/pools/prices, Polymarket (blocked from US), MYX snapshots.
- Tests: `uv run pytest -q`.

## Where results live
- `docs/NOTES_JX.md`: running log and conclusions (latest: "Conclusion of the 2026-11-20 search").
- `docs/IDEAS_64_STATUS.md`: status of the original 64 ideas.
- `docs/HANDOFF_NONPROP.md`: what non-prop ideas were tried, why they failed, what is left.

# #382 #370 restricted to coins tradeable on Hyperliquid (the Malaysia-usable venue) — 2026-11-24

**Why.** Jx: "this still looks pretty good" about #370 (walk-forward 30.8%/yr). #370's 2026 gains came mostly from Binance-only coins,
which a Malaysian resident cannot trade. The relevant number is the same procedure on the coins Hyperliquid lists. **Disclosure:** written
after #370's output, including a hindsight-config context line for Hyperliquid-listed coins (0.3% / 61.2% / 58.8% / −6.9% in 2023–26).
To limit bias, **nothing is changed** except the universe.

**Rule.** Identical to `docs/PREREG_CRYPTO_TREND_20261124.md` (same 52 configs, costs, funding, walk-forward, halves, bars), with the
universe limited to Binance USDT perps whose coin is listed on Hyperliquid (mapping: strip "USDT"; "1000X"/"1000000X" → "kX"; Hyperliquid
coin list = coins in `data/public/hl_funding.parquet`, 2024-01..2026-11). Binance prices/funding remain the data source.
**Verdicts.** Prop-like PASS / Useful / FAIL with the #370 bars. Also reported: outcome by start year (Jan 2021…Jan 2025) and worst
drawdown from each start.
**Command.** `uv run python -m scripts.crypto_trend_hl_20261124 | tee docs/jx_runs/crypto_trend_hl_20261124.txt` (re-run once; identical).
**Limits.** As #370; plus coins listed on Hyperliquid today may not have been listed throughout 2021–23 (survivorship towards today's list).

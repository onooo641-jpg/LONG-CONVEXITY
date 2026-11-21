# Named structural stablecoin programmes, buy-and-hold (#210) — 2026-11-21

Written and committed before running. Each programme pays by protocol rule (stability-pool liquidation gains and interest, funding-backed
staking yield, savings rates, protocol lending): **Liquity v2 BOLD, Felix feUSD, Ethena sUSDe, Falcon sUSDf, Sky (sUSDS/stUSDS/sDAI),
Spark Savings, Usual bUSD0, Hyperliquid Earn, Maple, Pendle v2 stable pools**. Data: `data/public/fallback_stable_charts.parquet` (DefiLlama
daily apyBase/apyReward/TVL; already fetched for #204, per-programme results not looked at).

## Rule (per programme)
- For each programme, take its pools in the file; programme daily yield = equal-weight mean over its pools with data that day of
  (apyBase + 0.9 × apyReward), capped at 1000%. Hold all window. Cost: $10 in and $10 out on $10,000 (≈0.1%/yr, ignored below 1 bp).
- Loss stress as #204: a pool whose TVL falls > 50% within 7 days → −20% on that pool's share, the pool dropped.
- Window 2024-11-01 .. 2026-10-31 (or the programme's first day of data if later), halves split at the midpoint of its own history.

## Pass (per programme)
≥ 8.0%/yr in both halves, no loss-stress hit, ≥ 180 days of history. Stage 1 per programme: last 3 months < 4.0%/yr → KILL.
Multiple programmes are tested at once; each is judged on its own rule, and a pass is still subject to the unmeasured hack/depeg risk
(stated in the result). Survivorship: programmes that failed before today are missing.

Command: `uv run python scripts/programmes_20261121.py | tee docs/jx_runs/programmes_20261121.txt`

## Result (2026-11-21, `docs/jx_runs/programmes_20261121.txt`): all 10 FAIL
Best: Ethena sUSDe 9.1% / 4.3% by half (last 3 months 4.7%); Usual bUSD0 13.0% / 3.0%; Falcon sUSDf 7.1% / 4.9%; Sky 5.5% / 3.2%.
Liquity v2 BOLD and Felix show 0% yield in DefiLlama (their stability-pool yield is probably not reported there: data gap, not a result);
Spark, Hyperliquid Earn, Maple, Pendle show TVL-collapse stress hits that may partly be pool-id changes in DefiLlama. Conclusion: passive
stablecoin programmes paid 8–13% in 2024–25 and 3–5% in 2025–26; none is a fallback at the 8% bar now.

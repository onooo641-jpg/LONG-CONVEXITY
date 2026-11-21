# Non-prop fallback: stablecoin yield rotation (#204) and Hyperliquid HLP vault (#205) — 2026-11-21

Written and committed **before** any of the data below is fetched. Jx asked for a non-prop fallback that need not match Topstep but should
be in the same range. Both ideas are capital-based (return scales with money deposited), long-lived, repeatable monthly, run on one setup,
and have no position sizing decisions. Malaysia: permissionless contracts / Hyperliquid (blocks US, Malaysia not known to be blocked):
**unverified**, checked by hand before any use.

Bar for a fallback (lower than the incentive-test bar, as Jx asked): **net ≥ 8.0%/yr in both halves** (T-bill 4.0% assumed + 4), which on
$40K is ~$3.2K/yr, in the range of one Topstep slot ($4,097/yr). Window: 2024-11-01 .. 2026-10-31 (24 months), halves 12 months each.

## #204 Stablecoin yield rotation (DefiLlama)
- **Universe:** every pool in today's `yields.llama.fi/pools` with stablecoin = true, ilRisk = "no", exposure = "single", TVL ≥ $1M; full
  daily history from `yields.llama.fi/chart/<pool>`. (Survivorship bias: pools that died before today are missing, so results are an
  upper bound; the stress below partly offsets it.)
- **Rule:** on the first day of each month, eligible pools = TVL ≥ $5M on that day and ≥ 90 days of history. Rank by the trailing 30-day mean
  of (apyBase + 0.9 × apyReward). Hold the **top 5 equally** for the month. Daily return = (apyBase + 0.9 × apyReward)/365 of each held pool.
- **Costs:** $5 per pool entered or exited (one transaction each), on a $10,000 portfolio.
- **Loss stress:** if a held pool's TVL falls more than 50% within 7 days while held, assume a **20% loss of that pool's allocation** (assumed;
  stands in for exploits/depegs the APY data cannot show), and it is dropped until month end.
- **Baseline reported (not a criterion):** holding Aave v3 USDC on Ethereum.
- **Stage 1 (pilot, last 3 months):** KILL if net < 4.0%/yr. **Stage 2:** PASS if net ≥ 8.0%/yr in both halves after costs and stress.

## #205 Hyperliquid HLP vault
- **Data:** `api.hyperliquid.xyz/info` `{"type":"vaultDetails","vaultAddress":"0xdfc24b077bc1425ad1dea75bcb6f8158e10df303"}`, all-time
  account-value and PnL history. Daily return = ΔPnL / previous account value.
- **Stage 1 (last 3 months):** KILL if annualised return < 4.0%. **Stage 2:** PASS if annualised return ≥ 8.0% in both halves AND worst
  peak-to-trough drawdown of the return index > −15%. Deposit/withdraw lockup (4 days, per Hyperliquid docs: third-party/assumed) noted, not modelled.

## Reported for both
$/yr on $10K and $40K; worst month; months negative; comparison with Topstep 50K recycling ($4,097/yr per slot, ~$3.5K at risk,
98% of coin flips profitable).

## Not measured
Smart-contract hacks and depegs beyond the stress proxy; HLP tail events beyond the window (e.g. a market-manipulation loss larger than any
seen). A PASS is a fallback candidate, not a recommendation to deposit; any deposit needs Jx's explicit approval.

Commands: data via `.github/workflows/fallback_fetch.yml` (`scripts/fetch_fallback.py`); test
`uv run python scripts/fallback_20261121.py | tee docs/jx_runs/fallback_20261121.txt`.

# CANDIDATES

One numbered row per idea tried. The point is that nothing gets retested blind,
and the count of things tried is visible in one place instead of spread across
the README and commit messages.

Rules:
- Next number = last number + 1. Numbers are never reused or renumbered.
- Write the formulation down **before** the run, in enough detail to rerun it.
  Code path plus the parameter values that differ from defaults.
- The verdict cites where it came from. Figures in a verdict are not standing
  figures until they're in `docs/FIGURES_LEDGER.md`.
- A variant found by looking at results gets its own row, marked
  **selected-on-data**.

**Tried so far: 55 rows, and row 12 alone is a 900-combination search.** So the
real count of configurations looked at is about 914, plus the 0.5–3.0 target
sweep in row 9.

Rows 1–15 were numbered retroactively on 2026-11-06. Their verdicts are
copied from the README and commit messages, which pre-date the ledger; I
didn't re-run them. Defaults shared by rows 1–7 (`strategies/base.py`
`BaseConfig`): stop buffer 2 pt, target 2R, swing_n 2, min FVG 1 pt, risk
2–250 pt, entries expire 15:00 ET, flat 16:00 ET, one trade per day, $500
risk, 5m signals and 1m fills.

## Pre-registered (strategies/registry.py — frozen, never tune)

| # | name | formulation | verdict | source |
|---|---|---|---|---|
| 1 | po3_judas | Asian-session range (accumulation). Raid between 09:30–11:00 ET, market-structure break by 12:00, FVG limit entry, entry expires 15:00, flat 16:00. `PO3Config` defaults. | Dev +$6,064 (PF 1.44), OOS −$521 (PF 0.93). **Fail.** | README table, post 2026-09-09 fix |
| 2 | silver_bullet | First FVG aligned with structure in 10:00–11:00 ET. `SilverBulletConfig` defaults. | Dev +$15,421 (1.03), OOS +$814 (1.01): $1.92/trade. **Fail** (not a business). | same |
| 3 | turtle_soup | Raid on prior-day high/low 07:00–12:00 ET, structure break by 13:00, target at the opposite level. | Dev −$13,563 (0.91), OOS −$8,287 (0.87). **Fail.** | same |
| 4 | ob_retest | Retest of an order block left by ≥15 pt displacement, 07:00–14:00 ET, entry at block midpoint. | Dev −$21,027 (0.96), OOS −$31,676 (0.86). **Fail.** | same |
| 5 | breaker_retest | Retest of a failed order block (polarity flipped), ≥15 pt displacement, breaks within 60 bars, 07:00–14:00 ET. | Dev +$20,730 (1.04), OOS −$14,631 (0.93). **Fail.** | same |
| 6 | ote_retracement | 0.705 retracement of a post-break leg of 20–400 pt, extreme set over 6 bars, 07:00–14:00 ET. | Dev −$26,131 (0.92), OOS +$8,605 (1.07). **Fail** (inconsistent). | same |
| 7 | sfp_reversal | Swing-failure pattern, ≥1 pt penetration, entry at 0.5 between close and extreme, 07:00–12:00 ET. | Dev −$175,903 (0.75), OOS −$33,101 (0.86). **Fail.** | same |
| — | combined account of 1–7 | Earliest signal of the day wins. | Dev −$134,031 (0.81), OOS −$21,840 (0.91). Rows 4–7 share 97–100% of signal days, so 1–7 are really two or three ideas. | README |

## Not pre-registered

| # | name | formulation | verdict | source |
|---|---|---|---|---|
| 8 | **LTF sweep** (the live candidate) | `strategies/ltf_sweep.py`, `LTFSweepConfig()`. 15m pool = prior 4 candles. Sweep ≥0.25 pt beyond it, 09:30–15:00 ET. 1m CHoCH within 30 bars (CHoCH required, not BOS). 1m FVG ≥0.5 pt limit entry, stop buffer 1 pt, target 1.0R, risk 1–120 pt, entries to 15:30, flat 16:00. One per day. Marketable entries refused (`skip_marketable_entries=True`). | Full 2016–2026 $500: −$3,044, WR 53.2% vs BE 53.3%, PF 0.994 (ledger S1–S5). Dev −$25,001, OOS +$21,957. **Open.** The forward log since 2026-08-29 is the only clean test. | ledger; README |
| 9 | LTF sweep, target-R sweep | Row 8 with `target_r` across 0.5–3.0 (reported points 1:1, 1:1.5, 1:2). `scripts/sweep_target_r.py`. | OOS PF 1.150 / 1.026 / 0.987. Monotone down over the whole range, same shape in dev. **1:1 kept** (the specified value, not selected). | README §LTF |
| 10 | LTF sweep, unrestricted | Row 8 with `one_per_day=False`. | Dev "+$84,346" flips to −$136,451 when a fill needs one tick through. **Fail** (fill-model artefact). | README |
| 11 | OR5 retest | `strategies/or5_retest.py` per `docs/or5_retest_spec.md` (rules committed before the run, 653e2ee). 09:30–09:35 range, body ≥40%, trade body direction. 1m close break, close retest within ±5 pt, re-close beyond before 10:00 ET, stop entry +2 pt. Stop = retest extreme ±3 pt clamped to 12–35 pt. Half off at 1R, runner to the range height, BE+2, flat 10:45. News filter **not** applied (no calendar). | Dev 868 fills, PF 0.62, −$88,041. OOS 291, PF 0.59, −$33,503. Every first-target setting 0.5R–2.0R loses. Mirrored direction loses too. **Fail.** Re-run after the same look-ahead fix: dev PF 0.71, OOS PF 0.68 (pessimistic). Still fails. | 97b54d6; `docs/jx_runs/or5_retest_after_fix_*` |
| 12 | ORB family search | `scripts/search_orb.py`. Grid: entry ∈ {break_retest, break_first, fail_fade} × side ∈ {body, either} × stop ∈ {pullback 3, fixed 15, fixed 25, height 0.5, height 1.0} × min body ∈ {0, 0.4} × exit ∈ {10:45, 12:00, 16:00} × target ∈ {0.25, 0.4, 0.5, 0.75, 1.0}R. 900 combinations, $500, stop entries, 1 tick slippage. **Search, selected-on-data.** | Breakouts: 0 of 600 profitable in both periods. fail_fade: 14% of 300 profitable in both, dev/OOS rank correlation +0.784, best cell PF 1.17, 2026 negative in every variant. ~~Hypothesis~~ → **Fail after look-ahead fix (2026-11-06):** `detect()` let the previous evening's bars break a range that only forms at 09:35 (ARTIFACT_CLASSES 5). Fixed: **0 of 900** profitable in both periods, best dev PF 1.06, fail_fade OOS PF 0.74. | c280e2a; fix 2026-11-06, `docs/jx_runs/search_orb_after_fix_*` |
| 13 | LTF session cutoff 11:00 ET | Row 8, but stop taking setups at 11:00 ET (GO_LIVE hourly table). **Selected-on-data.** | OOS +$12,200, dev −$2,232, 11y +$9,968. The only positive one, because it was picked off the by-hour table. **Rejected.** | GO_LIVE §收工; 859ad92 |
| 14 | LTF session cutoff 13:00 ET | Same, 13:00. | OOS +$15,217, dev −$18,843, 11y −$3,626. **Rejected.** | same |
| 15 | LTF session cutoff 15:30 ET (spec) | Same as the spec: sweeps to 15:00, entries to 15:30, flat 16:00. Exits once the day is resolved. | OOS +$13,274, dev −$17,668, 11y −$4,394 (confirming-bar fills excluded; ledger S7, unsourced). **Kept as the spec, not selected.** | same |

| 16 | failed-breakout fade, unselected member (to forward-log) | Row 12's `fail_fade`, `side_rule=either`, stop = 1.0× range height, exit 10:45, 1R, `min_body_frac=0.0` (the variant `fade_report.py` plots because nothing selected it). Formulated 2026-11-06 for a forward log starting 2026-09-08 05:27 UTC. | Before the fix: 53% of its trades were impossible and carried all the profit. After: 1,855 trades, PF 0.95, dev 1.01, **OOS 0.80, −$26,959**. **Fail. Not forward-logged.** | `docs/jx_runs/fade_after_fix_*` |
| 17 | LTF, long only | Batch 2026-11-09 (`docs/PREREG_BATCH_20261109.md`). Drop shorts. | fail (margin worse on NQ-S, NQ-O) | PREREG_BATCH_20261109 results |
| 18 | LTF, short only | Drop longs. | fail | PREREG_BATCH_20261109 results |
| 19 | LTF, scale out, runner 2R | Half off at 1R, runner to 2R, stop to entry. | fail (worse on every set) | PREREG_BATCH_20261109 results |
| 20 | LTF, scale out, runner 3R | Same, runner to 3R. | fail (worse on every set) | PREREG_BATCH_20261109 results |
| 21 | funded size ×0.5 | `recycle(funded_scale=0.5)`. | fail | PREREG_BATCH_20261109 results |
| 22 | funded size ×0.75 | `recycle(funded_scale=0.75)`. | fail (NQ-S only) | PREREG_BATCH_20261109 results |
| 23 | loss-streak pause | 3 losses in a row → skip next 5 trades (streak counts shadow outcomes). | fail (ES, YM… not NQ) | PREREG_BATCH_20261109 results |
| 24 | equity filter | Trade only if prior 20 baseline trades net > 0. | fail | PREREG_BATCH_20261109 results |
| 25 | fee cap 5% | Skip if contracts × $1.24 > 5% of risk. | fail | PREREG_BATCH_20261109 results |
| 26 | fee cap 3% | Same at 3%. | fail | PREREG_BATCH_20261109 results |
| 27 | stop buffer 2.0 | `stop_buffer_points=2.0`. | fail (NQ-S only) | PREREG_BATCH_20261109 results |
| 28 | 120-min time stop | `time_exit_ts = min(orig, valid_from + 120 min)`. | **PASS** by rule; real net gain small (NQ +$1.2K); NQ-O +$187. Forward-log shadow only | PREREG_BATCH_20261109 results |
| 29 | overnight drift (own account) | `docs/PREREG_20261120.md` H1. Long RTH close → next open, micros, roll windows dropped. | fail (0/3 OLD, 0/4 SEEN; best NQ t 1.66) | PREREG_20261120 |
| 30 | turn of month (own account) | H2. Close of day −2 → close of day +3. | fail | PREREG_20261120 |
| 31 | pre-FOMC drift (own account) | H3. 14:00 day before → 13:59 statement day. | fail | PREREG_20261120 |
| 32 | gap fade (own account) | H5. Gaps ≥ 0.25%, fade to prior close or RTH close. | fail (negative everywhere) | PREREG_20261120 |
| 33 | day of week (own account) | H6. Open → close per weekday, t > 2.6. | fail (NQ Monday SEEN alone passes, 1 of 20 cells) | PREREG_20261120 |
| 34 | Back2Funded always | P1. Reactivate a lost XFA up to 2×, $599. | fail (+$11.3K 2016–26, −$4.0K 2010–15, dip −$6,660) | PREREG_20261120 |
| 35 | Back2Funded once | P2. At most 1 reactivation per XFA. | fail (+$9.4K / −$2.2K) | PREREG_20261120 |
| 36 | Lucid (LucidFlex 50K) instead of Topstep | `docs/PREREG_LUCID_20261120.md`. Same trades, Lucid rules in the model. | fail as a replacement ($37,523 vs $44,359; worst dip −$4,720 vs −$3,520); beats coin flips 98%, so usable as a second firm | PREREG_LUCID_20261120 |
| 37 | new-perp funding spikes (Hyperliquid) | `docs/PREREG_TOP10_20261120.md` N1. | fail (1st half not above baseline; 2nd half negative) | PREREG_TOP10 |
| 38 | utilisation-threshold arbitrage (Aave) | `docs/PREREG_TOP10_20261120.md` N2. | fail (fallback mode; −$19.8/event) | PREREG_TOP10 |
| 39 | liquidity incentive mispricing (DEX LPs) | `docs/PREREG_TOP10_20261120.md` N3. | fail (n too small: 4+4) | PREREG_TOP10 |
| 40 | multi-outcome probability arbitrage (Polymarket) | `docs/PREREG_TOP10_20261120.md` N4. | no data (Polymarket refuses US servers; not circumvented) | PREREG_TOP10 |
| 41 | stETH redemption discounts | `docs/PREREG_TOP10_20261120.md` N5. | fail (~$40–50/yr per $10K) | PREREG_TOP10 |
| 42 | vault allocation inefficiencies | `docs/PREREG_TOP10_20261120.md` N6. | fail (3% of vaults; −0.46%/yr before costs) | PREREG_TOP10 |
| 43 | settlement-resolution inefficiencies | `docs/PREREG_TOP10_20261120.md` N7. | not data-testable (manual review) | PREREG_TOP10 |
| 44 | post-listing short on new perps (Hyperliquid, unhedged) | `docs/PREREG_POSTLISTING_20261120.md`. Selected from the N1 observation; tested on unseen 2023 listings. **Selected-on-data.** | fail on unseen 2023 listings (−$111 mean, 27% squeezed ≥50%, worst −$2,936 per $1,000) | PREREG_POSTLISTING |
| 45 | cross-chain lending-rate arbitrage (weekly) | `docs/PREREG_BATCH2_20261120.md` M1. | fail (−0.9% to −3.9%/yr vs holding Aave Ethereum) | PREREG_BATCH2 |
| 46 | stablecoin depeg buying (failures included) | M2. | fail (UST −94% on one buy; −$3.1K/yr per $10K) | PREREG_BATCH2 |
| 47 | cross-chain stablecoin dislocations | M3. | no data (chain-address prices rejected) | PREREG_BATCH2 |
| 48 | structure scan of bot-allowed prop-firm products (coin-flip net) | `docs/PREREG_STRUCTURE_SCAN_20261120.md`. Ranking, no pass/fail. | ranking done: Topstep 150K most generous ($34K coin flip); 50K most reliable (98%); Lucid only at 50K; Tradeify weaker | PREREG_STRUCTURE_SCAN |
| 49 | Bursa IPO public ballot | `docs/PREREG_LOOPHOLES_20261120.md`. | FAIL pre-registered (0.40%/RM applied, 2nd half negative, 37% below issue); post-hoc avg applicant RM7.7K-17K/yr, wide | PREREG_LOOPHOLES |
| 50 | guaranteed government matches / fixed-price funds | `docs/PREREG_LOOPHOLES_20261120.md`. | i-Saraan PASS but tiny (RM500/yr, 90% locked); ASM 5% vs FD 4% fails 2x rule | PREREG_LOOPHOLES |
| 51 | MYR crypto exchange price gaps | `docs/PREREG_LOOPHOLES_20261120.md`. | FAIL: uniform +0.4-0.55% Luno premium on all coins = MYR conversion cost; 1-tick spreads | PREREG_LOOPHOLES |
| 52 | static-drawdown prop firm coin-flip (control) | `docs/PREREG_LOOPHOLES_20261120.md`. | RETIRED: FTMO recommends <=1% risk, where coin flip is -$2.6K; structure pays random play at >=2% risk ($33K coin flip at 2%); FTMO bans high risk-per-idea; prop-related | PREREG_LOOPHOLES |
| 53 | FTMO verification + FTMO Futures Growth/Pro vs Topstep 50K | `docs/PREREG_FTMO_FUTURES_20261120.md`. Ranking. | FTMO Futures Growth $34K / Pro $28K vs Topstep $44K (Growth $48K if renewal resets are free); coin flip ~$0-2K vs $18K; no structural edge | PREREG_FTMO_FUTURES |
| 54 | TradeDay Fast Pass / Bulenox Momentum vs Topstep (ETF, FXIFY Futures excluded: no bots) | `docs/PREREG_FIRMS2_20261120.md`. Ranking. | TradeDay $85/mo: $35.7K real, $14.0K coin flip (closest to Topstep $44.4K/$18.0K); list price $22K; Bulenox Momentum -$4K | PREREG_FIRMS2 |
| 55 | global round 1: Breakout static 1-Step 50K; Tradeify Lightning 50K | `docs/PREREG_GLOBAL_20261120.md`. Ranking. | Breakout/Kraken Prop Classic 50K at 10x: $38-57K real, $11-25K coin flip = Topstep-level; Lightning $20-41K (cap-dependent) | PREREG_GLOBAL |
| 56 | round 3: MFFU Rapid EOD 50K; TFD Static Core/Pro (Apex unresolved; Phidias, E2T, TPT, Top One, Blue Guardian, Alpha, FFF banned; HyroTrader crypto-only) | `docs/PREREG_ROUND3_20261120.md`. Ranking. | none beats Topstep: MFFU $34.5K real / $7.4K coin flip; TFD Pro $20.2K / $3.3K; TFD Core $10.7K / −$1.2K. MFFU usable only as an extra slot alongside Topstep | PREREG_ROUND3 results |
| 57 | funding-rate carry (Hyperliquid majors), rotating top-3 and BTC+ETH held | `docs/PREREG_NONPROP2_20261120.md`. Pass > 8%/yr on capital, both halves positive. | fail (2.9% / 6.4%; yields falling since 2024) | PREREG_NONPROP2 results |
| 58 | friend's NQ strategy on own money | same. Pass > 15%/yr at 25% max-DD sizing, both halves positive. | fail (−$2,553 over 2016–26; max DD −$73K) | PREREG_NONPROP2 results |
| 59 | offshore broker credit bonuses as a loss buffer | same. Terms screen. | fail (credit does not absorb losses, or one-time capped) | PREREG_NONPROP2 results |
| 60 | multi-firm portfolio, same trades (Topstep, Lucid, MFFU, Breakout; 1 slot each and max slots) | `docs/PREREG_PORTFOLIO_20261120.md`. Sizing, no pass/fail. | B− (Topstep+Lucid+MFFU) $116K / $10.7K/yr, cash on hand $13.8K; max slots $513K, cash $58K; firms correlate 0.80–0.88; year one median $5.1K, 35% of starts lose | PREREG_PORTFOLIO results |
| 61 | staggered account starts; one API subscription per platform | `docs/PREREG_PORTFOLIO2_20261120.md`. Worth doing if cash on hand ≥15% lower at ≤5% net change. | not worth it (net −0.1%, cash +1.4%); corrected plan: 1 slot/firm $10.5K/yr, $14.6K cash; max slots $49K/yr, $50K cash | PREREG_PORTFOLIO2 results |
| 62 | market mix across accounts (NQ/ES/YM) with anti-hedge filter | `docs/PREREG_MARKETMIX_20261120.md`. Worth doing if net per $ of cash ≥ +15% and net ≥ 75% of all-NQ. | **WORTH DOING**: 5 Topstep cash $15.3K→$4.7K for −23% net; full plan cash $53K→$21K for −22% net ($38.4K/yr) | PREREG_MARKETMIX results |
| 63 | bigger Topstep accounts (100K/150K) inside the market mix | `docs/PREREG_SIZEMIX_20261120.md`. Worth switching if net ≥ +30% and cash ≤ $15,336. | not worth switching: +44% / +117% net but cash $22.6K / $33.7K vs $4.7K; 50K mix is 3× more cash-efficient | PREREG_SIZEMIX results |
| 64 | add FundedNext Futures Rapid Pro 50K (Tradeify excluded: bots only if not used at other firms) | `docs/PREREG_FUNDEDNEXT_20261120.md`. Worth adding if net ≥ +10% and net per $ cash falls ≤ 10%. | not worth adding: +11% net for +87% cash (net per $ cash −40%); single account $14.5K vs Topstep $44.4K | PREREG_FUNDEDNEXT results |
| 65 | manual entry delay (semi-automated firms) | `docs/PREREG_DELAY_20261121.md`. Viable if recycling net ≥ 80% of no-delay in both windows. | viable up to 3 minutes (84%/84%); 5 minutes fails (61%/60%) | PREREG_DELAY results |
| 100 | lending-liquidation bonuses on smaller Aave-style venues (Base, Arbitrum, Optimism, Polygon, Avalanche, Gnosis, Scroll, Metis; BNB unmeasured) | `docs/PREREG_LIQUIDATIONS_20261120.md`. A venue passes if in both halves top-3 < 60% of bonus value, liquidations every month, outside-top-3 net >= $500/month; idea passes at >= 3 venues and >= $2,000/month combined. | PASS: 7 venues pass; combined outside-top-3 net $1.70M / $1.09M per month (all other winners together); 5 still pass with winner = liquidator field. Median active small bot $30–$800/month per venue, gas-only. Verdict BUILD in shadow mode first | PREREG_LIQUIDATIONS results; NOTES_JX "Liquidation test #100: verdict" | Update 2026-11-21: 4-week shadow test running since 06:10 UTC (`PREREG_LIQ_SHADOW_20261121.md`, verdict 2026-12-19, week-1 kill check 2026-11-28, log-only crash-window extension to 2027-06-30); replay screen PLAUSIBLE but marginal (`PREREG_LIQ_REPLAY_20261121.md`: 64–78% of liquidations land in the same block as a price update; reachable share for a perfectly fast watcher 13% by count / 10% by value); income lumpy (`PREREG_LIQ_MONTHLY_20261121.md`: top 5 months = 70% of bonus). Update 2026-11-22: Morpho Blue on Base (`PREREG_LIQ_MORPHO_20261121.md`): 35,192 liquidations, $54.1M bonus in 24 months, registered venue test PASS (top-3 share 4–15%, outside-top-3 net $0.46M/$3.8M a month pooled), but 89% of the bonus came in 5 months and speed/competition is untested; replay and shadow arms next. Update 2026-11-22: Morpho Base replay (`PREREG_LIQ_MORPHO_REPLAY_20261121.md`): 93.8% of liquidations land in the same block as an oracle update; reachable share 2.1% of events / 0.8% of value at block-level latency: registered verdict DROP for a fast block-level bot (only a flashblocks-latency arm remains untested). |

| 200 | Radar (workstream C): daily scan of DefiLlama pools/protocols, Merkl campaigns, Snapshot incentive votes, prop-firm rule pages, docs changelogs, SDK releases; five-part filter, Malaysia check, near-miss log; prop-firm sweep with recycle.py pricing | `docs/PREREG_RADAR_20261121.md` (+ addenda 1–2). Scanner, no pass/fail. | built; baseline 2026-11-21: 1,295 reward pools + 714 Merkl campaigns → 93 screened → 12 fully verified; 1,963 near-misses logged. Prop-firm sweep: Blue Guardian, Phidias, Alpha Futures, Top One = alert-assisted; Alpha Futures Standard 50K at 3-min delay $40.2K real / $9.0K coin flip, not flagged (dip −$4,773 vs −$4,641 limit); FundedNext terms now restrict bots (unclear) | PREREG_RADAR; NOTES_NONPROP "Radar week 1" |
| 201 | Lista Lending stablecoin supply (Ethereum), radar week 1 | `docs/PREREG_INCENTIVES_W1_20261121.md`. Pass: net ≥ 12%/yr both halves, no loss event. | FAIL at Stage 1 (4.6%/yr net last 60 d) | PREREG_INCENTIVES_W1 results |
| 202 | Dolomite stablecoin supply (Ethereum), radar week 1 | same | FAIL at Stage 1 (6.4%/yr) | same |
| 203 | Bluefin USDSUI-USDC LP (Sui), radar week 1 | same | FAIL: 22.9% / 16.3% net by half but loss-event proxy hit (TVL to 32% of 7-day high); near-miss | same |

| 204 | stablecoin yield rotation (DefiLlama, top 5 monthly) — non-prop fallback | `docs/PREREG_FALLBACK_20261121.md`. Pass ≥ 8%/yr net both halves. | FAIL: −6.5% / 4.8% by half after loss stress (7 pool collapses) | PREREG_FALLBACK results |
| 205 | Hyperliquid HLP vault — non-prop fallback | same. Pass ≥ 8%/yr both halves, drawdown > −15%. | FAIL (near-miss): 27.7% / 7.9% by half; last 3 months 4.9%; falling | PREREG_FALLBACK results |
| 206 | FuturesElite Elite 50K, manual entry (alert-assisted), extra prop slot | PREREG_RADAR addenda 5–6. Flag rule as #200. | **flagged at $128** (third-party price): $31,071 real / $5,903 coin flip (79%) / dip −$2,560 vs Topstep at same delay $37,348 / $14,701; fails above ~$150. Needs: price confirmed, a person at the screen, signal clause read | PREREG_RADAR addendum 6; ledger RP5–RP6 |

| 207 | new stablecoin reward programmes, first 30 days | `docs/PREREG_NEWREWARDS_20261121.md`. Pass ≥ 8%/yr both halves, ≥ 30 events/half. | FAIL at Stage 1 (−61.7%/yr with loss stress; 1.9%/yr even without it, below Aave) | PREREG_NEWREWARDS result |
| 210 | named structural stablecoin programmes held (Liquity BOLD, Felix, sUSDe, sUSDf, Sky, Spark, bUSD0, HL Earn, Maple, Pendle) | `docs/PREREG_PROGRAMMES_20261121.md`. Each ≥ 8%/yr both halves. | all FAIL (best sUSDe 9.1%/4.3%, bUSD0 13.0%/3.0%); yields fell to 3–5% in 2025–26 | PREREG_PROGRAMMES result |
| 217 | best-venue DeFi funding carry (HL/dYdX/Aevo) | `docs/PREREG_BESTVENUE_20261121.md` | Stage 0.5 KILL: hindsight ceiling 7.8%/yr < 8% | ceiling_20261121.txt |
| 208 | cross-venue funding gaps, delta-neutral (HL/dYdX/Aevo) | `docs/PREREG_FUNDGAP_20261121.md` (+ addenda 1–2). Pass ≥ 8%/yr both halves. | **PASS after a fee-bug fix: 20.3% / 11.9%** (earlier 13.8% / 4.4% FAIL had fees double-counted); fragile: fails at 2× fees, needs the Aevo pairs; execution basis/slippage not modelled | PREREG_FUNDGAP addendum 2  **Batch 7 execution pilot: FAIL** — $10K taker cost 55 bps/side on Aevo, 23 on dYdX vs 2.5 budget (PREREG_BATCH7 C) |
| 209 | paid-to-borrow same-asset stable loops | `docs/PREREG_BORROWLOOP_20261121.md`; PREREG_HEDGED addendum | survives Stage 0.5 (ceiling 11.4%, Dolomite loops ~16–19% today); NOT TESTABLE further: borrow history paywalled (HTTP 402) | borrow_ceiling_20261121.txt |
| 211 | Pendle stable PTs to maturity, expired markets included | `docs/PREREG_PENDLE_20261121.md` | FAIL at Stage 1 (−7.0%/yr; apxUSD depeg) | PREREG_PENDLE result  G9 walk-forward incl. 344 markets: FAIL (0.8% / 7.9%) |
| 212 | hedged liquid staking (LST + HL short) | `docs/PREREG_HEDGED_20261121.md` | FAIL at Stage 1 (−2.2%; churn costs); post-hoc buy-and-hold also < 8% in year 2 | PREREG_HEDGED results |
| 213 | hedged reward farming (ETH/SOL/HYPE/BTC/AVAX/BNB pools) | same | FAIL at Stage 1 (−3.6%) | same |
| 216 | gold carry (PAXG + HL short) | `docs/PREREG_GOLDCARRY_20261121.md` | FAIL: 7.1% / 5.1% | goldcarry_20261121.txt |
| 219 | correlated-pair loops (LST/ETH, sUSDe/USDC) | PREREG_HEDGED | Stage 0.5 KILL (corrected ceiling 6.8%; e-mode LTV not in data) | borrow_ceiling_20261121.txt |
| 220 | hedged Jupiter JLP | `docs/PREREG_BATCH4_20261121.md` | not testable (no history: DefiLlama lists only JLP lending; Jupiter API current APR only) | batch4_20261121.txt |
| 221 | hedged GMX GM pools | same | FAIL: fee-APY rule 21.8% / 10.1% but with real GM token prices 3.6% / 3.2% (Stage 1 −32.9%) | batch4 + gm_robust_20261121.txt |
| 222 | dYdX MegaVault | same | FAIL (only 67 days of history; Stage 1 8.2%) | same |
| 223 | Lighter LLP | same | not testable (no history) | same |
| 224 | stable-pair DEX LPs | same | FAIL at Stage 1 (−12.0%) | same |
| 225 | trader-counterparty USDC vaults (Gains) | same | FAIL on the primary rule (9.7% / 4.4%); equal-weight 10.7% / 13.2% (near-miss; ~$2.5M capacity) | same  Real gUSDC price: FAIL (6.9%/yr price vs 10.7% APY; OOS 16.1% / −19.9%) |
| 227 | other savings rates (sUSDu, savUSD, sUSDai, sDOLA, sfrxUSD...) | same | FAIL (3.7% / −16.8%) | same |
| 229 | hedged native L1 staking | `docs/PREREG_BATCH5_20261121.md` | ATOM Stage 0.5 KILL (4.9%); INJ ceiling 12.1% but no free APR history → not testable beyond Stage 0.5; TIA/SEI/DYDX/APT/NEAR/DOT no APR data | batch5_20261121.txt |

| 214 | hedged governance-token yields (yCRV, cvxCRV, sdCRV, sdPENDLE, AAVE) | PREREG_HEDGED (+ wrapper addendum) | FAIL: rule 8.3% / 15.5% but wrappers lost 40–60% vs CRV (yCRV 0.98→0.56); with discount Stage 1 −162% | hedged_wrappers_20261121.txt |
| 228 | hedged resource/revenue staking (TRX energy, SKY staking) | `docs/PREREG_BATCH5_20261121.md` | TRX KILL (shorts pay 13%); SKY FAIL on history (112 d < 180) at 12.9% / 16.9% — near-miss, re-test ≈ 2027-01-07 | batch5 + sky_stage2_20261121.txt |

| 230 | stability pools (Liquity v2 BOLD, Felix feUSD) | `docs/PREREG_STABILITYPOOL_20261122.md` | FAIL on capacity: Liquity v2 SP holds ~$3.6K, total interest ~$1K/yr (48% APY on nothing); Felix no data | sp_liquity_api.json |
| 231 | MFFU Builder 50K (new plan caught by the radar's rule-change watcher) | PREREG_RADAR addendum 8 | list $153: $25,323 real / $2,022 coin flip (62%) / dip −$6,732 → not flagged; with the advertised 30% code ($107, sensitivity): $32,453 / $9,759 (85%) / −$4,708 → would flag. One account per user | radar_price_20261121.txt |
| 232 | MFFU Studio static-MLL plans (#001–#003; payouts of all profit any time) | PREREG_RADAR addendum 9 | not flagged: #002 $15,602 real / −$3,770 coin flip (21%); #001 $7,551 / −$2,528; #003 $3,249 / −$1,775 — the 2:1 target-to-loss evaluation costs ~3 purchases per funded account | radar_price_mffu_studio.txt |
| 233 | The Trading Pit Futures Prime 50K (bots allowed, Malaysia OK) | PREREG_RADAR addendum 10 (+12) | **EXTRA SLOT CANDIDATE: $46,597 real (> Topstep $44,359) / $14,016 coin flip (95%) / dip −$4,884** at **$99, verified on TTP's own futures page**; holds at ≤ ~$120, fails at $149 | radar_price_ttp_prime50.txt; ttp_sens_20261122.txt |
| 234 | Traders Launch 100K / 200K | same | not flagged ($722 / $4,371 real; coin flip deeply negative) | radar_price_traders_launch.txt |

| 235 | TTP Futures Prime 150K ($289) | PREREG_RADAR addendum 11 | not flagged: $43,662 real / −$6,562 coin flip (38%) / dip −$19,074; the 50K is the size that works | radar_price_ttp_prime150.txt |
| 236 | DayTraders EOD 50K (bots allowed; 100% split; up to 5 accounts) | PREREG_RADAR addendum 12 | price unreadable → sensitivity only: at $99 **$48,602 real / $13,511 coin flip (89%) / dip −$3,079**; at $199 $36,802 / −$4,406. Confirm the price: at ≤ ~$120 it would beat Topstep | radar_price_dt_eod50.txt |
| 206b | FuturesElite Elite 50K re-priced with its own $89 reset (addendum 13) | same flag rule (3-min delay) | still flagged: $33,645 / $9,121 (91%) / −$2,014 | radar_price_fe_elite50.txt |

| 237 | TTP Futures Prime 50K with its own $79 reset | addendum 14 | **EXTRA SLOT CANDIDATE: $49,057 / $16,960 (97%) / −$3,884** (supersedes #233's $46.6K) | radar_batch14_20261122.txt |
| 238 | TTP Futures Prime 100K ($189) | same | not flagged ($30,418 / −$3,408) | same |
| 239 | TTP Futures Instant 50K | same | [sens] $299: $58,276 / $32,076 (98%) / −$4,485 (would flag); $499: $43,076 / $8,750 / −$11,214 | same |
| 240 | LucidDaily 50K (EOD) | same | [sens] $99: $56,774 / $23,037 (98%) / −$4,356 (would flag); $199: $40,574 / $5,432 / −$8,756 | same |
| 241 | LucidDirect 50K | same | [sens] $299: $42,064 / $17,660 / −$5,669 (dip just fails); $499: not | same |
| 242 | MFFU Pro 50K | same | [sens] $127: $35,980 / $9,016 (80%) (would flag); $227: not | same |
| 243 | MFFU Pro 50K One-Day | same | [sens] not flagged at either price | same |
| 244 | DayTraders S2F 50K | same | [sens] $199: $55,274 / $31,518 (100%) / −$4,378 (would flag); $399: $40,474 / $9,708 / −$9,556 | same |
| 245 | Goat 1-Day Pass 50K ($218) | same | not flagged ($22,227 / −$7,651) | same |
| 246 | Goat EOD 50K | same | [sens] not flagged | same |
| 247 | Alpha Zero 50K ($169/mo) | same | not flagged (−$440 real) | same |
| 248 | Alpha Advanced 50K ($209/mo) | same | not flagged | same |
| 249 | Alpha Direct 50K ($519) | same | not flagged | same |
| 250 | FuturesElite Prime 50K (manual) | same | [sens] $129: $52,176 / $11,247 (86%) / −$3,697; $229: $49,076 / $7,623 / −$4,197 — would flag at both | same |
| 251 | FuturesElite Nitro 50K (manual, $152 directory) | same | **EXTRA SLOT CANDIDATE: $48,463 / $15,373 (94%) / −$4,331** (funded drawdown is intraday, modelled EOD → optimistic) | same |
| 252 | FuturesElite Instant 50K (manual) | same | [sens] $199: $114,682 / $82,570 (100%) / −$1,393; $349: $102,382 / $67,295 — would flag at both; result looks too good, verify rules/price before trusting | same |
| 253 | Blue Guardian Reserve 50K (manual) | same | [sens] $150: $41,251 / $9,206 (would flag); $250: not | same |
| 254 | Blue Guardian Direct 50K (manual) | same | [sens] $299: $62,773 / $51,438 (100%) / −$4,772 (dip fails by $131); $499: $48,173 / $26,832 / −$10,568 | same |
| 255 | Alpha Standard 100K | same | not flagged | same |
| 256 | Alpha Zero 100K | same | not flagged | same |
| 257 | Alpha Direct 25K | same | not flagged | same |
| 258 | Goat 1-Day Pass 100K | same | not flagged | same |

| 259–278 | Batch 6: 20 non-prop mechanisms (zero-fee venue funding gaps/carry, hedged real-yield staking, tranches, insurance funds, bribes, veAERO, RWA, fixed-rate auctions, CME basis, tokenised stocks, LST unstake, hedged LP, relayers, HYPE staking, reverse carry, new-chain incentives) | `docs/PREREG_BATCH6_20261122.md` | 1 narrow pass (#276 hedged native HYPE staking 24.9% / 9.2%, not robust: 6.5–8.2% in year 2 under conservative assumptions); 11 killed at Stage 0/0.5; 5 failed Stage 1/2; 5 not testable (incl. #259 surviving the ceiling at 33%) | PREREG_BATCH6 final results  #276 liquidation check: FAIL (3× short liquidated 12 times; walk-forward 13.6% / −8.9%) |

| R1–R7 | refinement studies (year-1 design, year-2 test, costs ×1.5) on #208, #221, #204 family, #207, #276, #225, carry family | `docs/PREREG_REFINE_20261122.md` | PASS: R1 funding gaps (maker 24.9% / 17.1%), R5 HYPE hedged staking (23.4% / 9.3%, marginal), R6 Gains vaults (11.6% / 9.8%, small, price check pending); FAIL: R2 GM (best hedge flips), R3 stable selection, R4 new rewards, R7 conditional carry | refine_20261122.txt |

| WF | walk-forward retest of 16 ideas with grids of 12–270 configs (monthly pick on trailing 6 months; OOS 2025-05..2026-10) | `docs/PREREG_WALKFORWARD_20261122.md` | PASS: G1 funding gaps (12.8% / 18.2%, needs maker fills — taker-only fails the ×1.5 cost check), G5 HYPE hedged staking (15.0% / 8.7%), G6 Gains vaults (9.6% / 14.1%); FAIL: GM pools, stable selection, stable-pair LPs/savings, new chains, new rewards, carry family, hedged staking | walkforward_20261122.txt |
| 280 | funding gaps Deribit ↔ HL/dYdX | `docs/PREREG_BATCH8_20261122.md` | return test PASS (16.3% / 9.9%) but execution FAIL: tradeable slice (HL–Deribit, BTC/ETH/SOL/XRP) −1.4% / −0.2% → not flaggable | batch8s_20261122.txt |
| 288 | Hyperliquid user vaults, top-5 trailing 90 days | same | FAIL Stage 2 without survivorship (−5.6% / −4.9%; worst month −35%) | batch8s_20261122.txt |
| 291 | friend's NQ trades wrapped in 0DTE options (non-prop copy of the prop free option) | `docs/PREREG_OPTIONWRAP_20261122.md` | FAIL (−$28,411; coin flip −$74,810) | optionwrap_20261122.txt |
| 284 | HL HIP-3 cross-dex funding gaps | same | FAIL Stage 1 (−2.08%) | same |
| 281 | Deribit futures cash-and-carry | same | FAIL Stage 1 (2.62%) | same |
| 282 | Deribit short ATM straddle ladder | same | FAIL Stage 1 (−30.81%) | same |
| 285 | Kamino SOL-LST loops | same | FAIL Stage 1 (−4.13%; SOL borrow 6.6% > intrinsic 3.5%) | same |
| 279, 283, 286, 287, 289, 290 | Drift gaps, Boros, Aave loops, Morpho loops, Orderly gaps, Morpho vaults | same | not testable (no data); repair probes running | same |
| 296–319 | Sweep 2: 24 Topstep-shaped / niche mechanisms | `docs/IDEAS_SWEEP2_20261122.md`, `docs/PREREG_BATCH10_20261122.md` | 14 to test, 6 parked, 4 excluded; results below | batch10 |
| 298 | buy prop evaluations only in sale windows | PREREG_BATCH10 | ranking: flag-rule rows 18 → 39 at 40% off (verified-price rows 7 → 16); resets discounted too (optimistic) | salewindow_20261122.txt |
| 300 | HIP-3 stock-perp funding carry (share-hedged) | same | FAIL Stage 1 (−13.28%; unhedgeable pre-IPO names show 49.9%, not tradeable as registered) | batch10_20261122.txt |
| 314 | HIP-3 index-perp funding carry | same | FAIL Stage 1 (−2.21%) | same |
| 320–321 | small-capacity high-reward pools; small Merkl campaigns (50% bar) | `docs/PREREG_SMALLCAP_20261122.md` (+ addenda 1–3) | fetch queued | — |
| 322–326 | sweep 3: thin-venue market making, hedged extreme funding, counterparty/option vaults, small stable lending, odd-lot tenders | `docs/PREREG_SWEEP3_20261122.md` | #323 FAIL Stage 1 (−1.36%; extreme funding nearly gone since 2024); #326 parked (EDGAR contact e-mail); rest queued | sweep3_20261122.txt |
Earlier, superseded version of 13 (c21f67c): "11:00, cancel unfilled" 350 /
+$16,409 OOS, 908 / −$10,150 dev, before confirming-bar fills were excluded.
Not a separate idea, so not numbered.

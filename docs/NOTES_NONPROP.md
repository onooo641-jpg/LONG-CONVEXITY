# Non-prop notes (liquidations, radar, other non-prop ideas)

Prop-firm work is logged in `docs/NOTES_JX.md`. Map of everything: `docs/INDEX.md`.
Earlier non-prop entries (before 2026-11-21) are in `docs/NOTES_JX.md`; the liquidation test's pre-registered
verdict sections ("Liquidation test #100: verdict", "Liquidation shadow test: …") stay there as registered.
New non-prop write-ups start below.

## Radar week 1 (2026-11-21)
**Built** (`docs/PREREG_RADAR_20261121.md`, CANDIDATES #200): daily GitHub Actions job (`.github/workflows/radar.yml`, 02:41 UTC) running
`scripts/radar.py`. The sandbox cannot reach any source; Actions (US servers) collects. Sources: DefiLlama pools + protocols, Merkl live
campaigns, Snapshot proposals (45 days), 53 prop-firm sites crawled two levels into their help centres (1,317 pages), 3 directories
(+ sitemaps: propfirmmatch 18,771 URLs, saveonpropfirms 527), 16 venue docs pages, 8 SDK release feeds. Pages are diffed day to day
(31 pages already changed between today's runs, e.g. E8 Markets). Everything is in one candidate table; every removal is in the near-miss table.

**Baseline sweep (latest run):** 1,295 reward pools + 714 Merkl campaigns + 67 incentive votes → 92 pass threshold, quality, F3–F5 and
Malaysia → 17 with all five filter parts verified; 2,147 near-misses with reasons (1,377 below threshold, 260 DefiLlama outliers,
~360 price exposure (F4), ~70 TVL < $1M (F5), 24 reward not persistent, 18 not long-lived). Known gaps: Polymarket (US geoblock), Tally
(needs key), JS-only pages (Apex/Lucid/Tradeify/ETF/Aqua return 403 to the runner; Phidias/Top One/Blue Guardian prices load by script).

**Week-1 tests (#201–#203, `docs/PREREG_INCENTIVES_W1_20261121.md`): all FAIL.** Lista stables killed at Stage 1 (4.6%/yr net; today's
10.6% reward was a spike), Dolomite killed at Stage 1 (6.4%/yr), Bluefin USDSUI-USDC earned 22.9% / 16.3% net by half but hit the
pre-registered loss-event proxy (TVL fell to 32% of its 7-day high) → near-miss. Lesson, pre-registered as addendum 3: rank the queue by
90-day realised yield, not today's APR. Even the best case was ~$2K/yr per $10K, under one Topstep slot.

**Prop-firm sweep** (`docs/radar/prop_firms.csv`, pricing `scripts/radar_price.py`, raw `docs/jx_runs/radar_price_20261121.txt`):
- Full bots allowed (own pages): Topstep, Lucid, MFFU, TradeDay (inside platforms), Bulenox, TFD, Tradeify (conditional), HyroTrader (crypto);
  CFD: Audacity, Alpha Capital, Goat (NQ strategy not portable).
- **Alert-assisted (bots banned, manual / semi-automated allowed): Blue Guardian, Phidias** (both explicitly allow semi-automated with active
  management), **Alpha Futures, Top One Futures** (ban automation only). Banned outright on CFD: Maven, Lux.
- **FundedNext: its crawled terms now say bots "not expressly authorised" and "systematic execution ... based on external signals" may be
  prohibited** — conflicts with the help-page reading in PREREG_FUNDEDNEXT; moved to `unclear` (matters for workstream A, which had already
  dropped it).
- Pricing, 3-min manual delay: **Alpha Futures Standard 50K $40,155 real / $8,998 coin flip (81% profitable) / dip −$4,773**; Topstep at the
  same delay $37,348 / $14,701 / −$3,094. Not flagged: the pre-registered dip limit is −$4,641 (missed by $132). Blue Guardian Elite 50K
  priced only as a sensitivity (price unreadable): $43.9K / $37.4K real at $141 / $350. Phidias, Top One: rules incomplete in crawled pages.
- All existing models re-priced identically to the ledger (FTMO Pro differs only by $900→$800 scaling vs re-simulation).

**Flag to Jx: none.** Nothing passed the filter and a full pre-registered test.

**Week-2 queue (first run on/after 2026-11-28, addendum 3 ranking):** current top verified row after the protocol-family age fix is Curve
BOLD-USDC (39.9% reward APR, $8.6M TVL); it will be queued only if its 90-day realised yield ranks it top-3.
For workstream A (not acted on here): Alpha Futures Standard 50K could be a manual-entry slot (real net above Topstep at the same delay),
needs a person at the screen 22:30–00:30 MYT and the copy/third-party-signal clauses read by hand.

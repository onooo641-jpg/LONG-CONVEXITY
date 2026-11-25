# Uncharted batch: tests U-T1 to U-T5 (#383–#387) — pre-registered 2026-11-25, before any data are fetched

Ideas and reasons: `docs/IDEAS_UNCHARTED_20261125.md`. Bar for Jx: about $15K/yr on about $15K (≈ 100%/yr) is "prop-like"; ≥ 20%/yr with
controlled drawdown is "useful". Each test has a Stage 1 (kill-only) and is reported with its data coverage. Free public data only.
**Stage 0 (all):** data availability probe `uprobe` (GeckoTerminal pool OHLCV, Hyperliquid meta/candles, Upbit and Binance announcement
pages, Uniswap CCA contracts). A test whose data are unavailable is recorded "not testable" (with the reason), not killed.

## U-T1 (#383) Launch-phase house vaults
**Data.** Share-price (or token-price) histories of perp-DEX liquidity vaults from their launch: JLP (have), GLP (GMX v1), Gains gDAI/gUSDC
(have), HLP (Hyperliquid vault history), and newer venues where a price series exists (Lighter LLP, Aster ALP, Ostium OLP, Avantis).
**Rule.** For each vault, the return of holding it for its first 12 months (from the first price), hedged as #363 where the vault holds
non-stable assets (weekly non-negative least-squares hedge on SOL/ETH/BTC, Hyperliquid funding), costs 0.3%/yr; compare with months 13–24.
**Stage 1 (kill-only):** KILL if the median first-year return across vaults with data is < 20%/yr. **Pass-ish (forward-trial worthy):**
median first-year ≥ 40%/yr across ≥ 4 vaults **and** first year beats months 13–24 in ≥ 3 of 4.

## U-T2 (#384) Withdrawal-queue discounts (kHYPE, stHYPE, beHYPE, ezETH, rsETH, weETH, pufETH, sUSDe)
**Data.** Daily close of each token's main DEX pool against its underlying (GeckoTerminal OHLCV), 2024-01..2026-10 where available.
**Rule.** NAV proxy = the pool's 30-day rolling maximum price ratio (exchange rates move slowly upward). An **event** = a day the ratio closes
≥ 1.0% below the NAV proxy. Trade: buy at that close (size min($15,000, 2% of the pool's daily volume)), redeem after the token's queue
(HYPE LSTs 9 days, LRTs 7 days as an optimistic floor, sUSDe 7 days) at the NAV proxy of the redemption day, minus 0.10% fees and the
queue's lost staking yield. One position per token at a time.
**Stage 1 (kill-only):** KILL if total net profit over the window is < $3,000/yr on $15,000 (< 20%/yr), or there are fewer than 4 events.

## U-T3 (#385) Hyperliquid pre-launch perps (hyperps)
**Data.** Hyperliquid candles for markets that traded as pre-launch hyperps and later had a token launch (list assembled from Hyperliquid
announcements / meta; every name found is used, none dropped).
**Rule.** Short at the first daily close after the hyperp lists; cover at the close 7 days after the token's launch; 1× notional; funding
from Hyperliquid funding history; 0.045% fees per side.
**Stage 1 (kill-only):** KILL if fewer than 6 events, or the mean return per trade is ≤ 0, or more than a third of trades lose > 50%.

## U-T4 (#386) Exchange risk-tag / delisting announcements → short on Hyperliquid
**Data.** Upbit "investment warning" designations and Binance "monitoring tag" / delisting announcements (public announcement pages), 2024–2026;
Hyperliquid daily prices for tokens with a Hyperliquid perp.
**Rule.** Short at the first Hyperliquid daily close after the announcement time, hold 7 days, hedged with an equal BTC long; 0.045% fees per
side + funding.
**Stage 1 (kill-only):** with ≥ 15 events: KILL if the mean hedged 7-day return of the short is < 1% or its t-statistic < 1. Fewer than 15
events: "not testable".

## U-T5 (#387) Uniswap CCA token auctions
**Data.** CCA auctions on Ethereum, Base, Arbitrum and Unichain (contract events), clearing price, and the token's price 1, 7 and 30 days
after the auction ends (GeckoTerminal pools created by the auction).
**Rule.** Buy at the clearing price; sell after 7 days (primary) — 1 and 30 days reported.
**Stage 1 (kill-only):** with ≥ 5 auctions: KILL if the median 7-day return is ≤ 0. Fewer than 5: "not testable".

## U-T6 (#389) Resting bids under liquidation wicks — added 2026-11-25 before its data were examined
**Data.** Daily candles of every Hyperliquid perp (`uncharted_385_candles.parquet`, fetched for U-T3), first 30 days after each listing
excluded, 2023-06..2026-10.
**Rule.** Each day, for every perp, a resting limit buy at the previous close × (1 − X). Filled only if the day's low is ≥ 0.5% below the
level (trade-through; queue priority is unknown). Fill price = the level, or the open if the day opened below it. Sell at that day's
close. Size per fill = min($1,500, 1% of the day's USD volume). Costs: 0.015% maker in, 0.045% taker out. X = 15% primary; 10%, 20%, 30%
reported as context (no selection among them).
**Stage 1 (kill-only), X = 15%:** KILL if mean net return per fill ≤ 0.3%, or net profit < $3,000/yr (fills of one day share one $15,000
pot: if a day's fills exceed $15,000 they are scaled down).

## U-T7 (#391) Hong Kong IPO one-lot applications — added 2026-11-25 before its data were fetched
**Why.** Issuers underprice IPOs (long-run Hong Kong day-one average +38.1%, Ritter Jan 2026; ~40% in 2025 per HKEX via Reuters).
The public tranche gives small "one-lot" applications a lottery-style share, capped per identity, so big money cannot take it all.
**Stage 0 (desk, open).** A broker that lets a Malaysian resident apply for Hong Kong IPOs (IBKR needs an IBHK account; moomoo/M+/Webull MY
trade HK shares, IPO access unverified). Until confirmed, a pass here only makes this "worth asking a broker".
**Data.** Public IPO result tables (AASTOCKS listed-IPO table and/or etnet IPO pages): listing date, offer price, lot size,
public-offer oversubscription, one-lot success rate, first-day performance. 2023-01..2026-10, every IPO with those fields; none dropped.
**Rule A (primary).** Apply for one lot in every IPO with cash. Expected value per IPO = one-lot success rate × lot value × first-day
return − HK$100 application cost (conservative; many brokers charge HK$0–100). Annual EV = sum over IPOs in the year, in USD at 7.8.
**Rule B (context only, look-ahead).** Only IPOs whose final public oversubscription ≥ 100× (final figures are known only after
applications close; broker margin-book figures approximate them before) — reported, not used for the verdict.
**Stage 1 (kill-only).** KILL if Rule A's mean annual EV over 2023-01..2026-10 < US$1,000 per identity, or if fewer than 30 IPOs have
the needed fields. Surviving means only "a small capped add-on worth a broker-access check"; scaling via larger tiers and IPO margin
loans needs per-tier allotment data and its own pre-registration (Stage 2).

**Commands.** probe: Actions job `uprobe`; tests: `scripts/uncharted_*_20261125.py` with outputs in `docs/jx_runs/` (each re-run once;
identical). **Limits.** NAV proxies and announcement times are approximations; small samples are reported as such.

## U-T6 (#389) Stage 2 — pre-registered 2026-11-25 after Stage 1 survived, before any Stage 2 data were fetched
Stage 1 used every Hyperliquid perp, so Stage 2 must add evidence the rule has not seen. All four parts are required for
"prop-like candidate"; any failure stops it. Nothing in the rule changes (X = 15%, 0.5% trade-through, first 30 days excluded, size
min($1,500, 1% of USD volume), $15,000 pot, Hyperliquid fees 0.015% / 0.045%).
- **S2a, out-of-sample market:** Binance USD-M perps, every USDT symbol in the data.binance.vision archive (delisted included),
  daily OHLC 2020-01..2026-10. PASS if mean net per fill ≥ 0.5% with t ≥ 3, net ≥ $3,000/yr, and the year is positive in ≥ 4 of the
  6 full years 2020–2025. X = 10/20/30% reported as context only.
- **S2b, risk on Hyperliquid (Stage 1 data):** daily P&L path on the $15,000 pot: PASS if the worst peak-to-trough drawdown is no
  worse than −$3,750 (−25%) and the worst single day no worse than −$3,000.
- **S2c, out-of-sample time:** forward paper run on Hyperliquid daily candles from 2026-12-01 for 8 weeks (radar logs each day's
  fills). PASS if ≥ 60 fills and mean net per fill ≥ 0.5%.
- **S2d, desk:** Hyperliquid rules for resting orders (margin reserved by open orders, open-order limits, API rate limits) must allow
  the rule's resting bids on a $15,000 account; if not, the size/coin count that fits is fixed before S2c and reported.

---
## Results

### U-T7 (#391) Hong Kong IPO one-lot applications — **KILL** (2026-11-25)
`uv run python -m scripts.uncharted_hkipo_20261125` → `docs/jx_runs/uncharted_hkipo_20261125.txt` (re-run identical).
Data: AASTOCKS listed-IPO table (17 pages, fetch run 45600030401): 317 IPOs, but the table only reaches back to **2024-01-05**, so the
window is 2024-01..2026-10 (not 2023 as registered); 301 of 309 in-window IPOs have every field.
- Mean first-day return +35.6% (median +8.2%; 67% up), median lot value HK$3,932, median one-lot success rate 7%.
- **Rule A (one lot in every IPO): EV −HK$6,090 over 2.82 years = −US$277/yr per identity** (2024 −US$773, 2025 +US$214,
  2026 −US$222). With a zero-fee broker: +HK$24,010 = **+US$1,092/yr** — still a rounding error against the $15K bar.
- Why: allocation odds are priced. Hot IPOs (final oversubscription ≥ 100×; 199 of 301) averaged +53% on day one but a median one-lot
  success rate of 3%; the other 102 averaged +0.7% with high odds. Rule B (look-ahead) on the hot ones: +US$402/yr.
- Verdict: KILL (Rule A < US$1,000/yr). Stage 0 broker access not needed. Scaling via margin applications was not tested; with
  allocation this rationed it would need per-tier data and is unlikely to change the conclusion.

### U-T3 (#385) Short Hyperliquid pre-launch perps — **survives Stage 1 (kill-only)**, small and tail-heavy (2026-11-25)
`uv run python -m scripts.uncharted_hyperp_20261125` → `docs/jx_runs/uncharted_hyperp_20261125.txt` (re-run identical). Data: fetch run
45609648643 (235 Hyperliquid perps incl. 56 delisted; CoinGecko ids by symbol; DefiLlama first spot price; Hyperliquid funding).
- 34 perps listed > 2 days before their first spot price; 29 tradeable to TGE + 7 days; **27 pass the price-mapping check (primary)**.
- Primary: **mean short return +18.3%, median +24.2%, t 1.65, win 63%**, 3 of 27 lose > 50% (worst −127%); price −11.0% on average,
  funding to the short +7.4%. By listing year: 2023 −22.6% (n 6), 2024 +29.6% (n 6), 2025 +30.1% (n 15). 2026: one live hyperp, no TGE yet.
- Kill rules (n ≥ 6, mean > 0, ≤ 1/3 lose > 50%): none triggered → survives.
- **Caveats (decisive for sizing):** the average worst run-up after entry is +152%; with isolated 1× margin 11 of 27 would have been
  liquidated (mean −14.3%). It only works as small positions inside a cross-margined account. Excluding three doubtful names
  (AERO is a DefiLlama first-price artefact; OX, SHIA) gives n 24, mean +17.7%. At ~15 events a year, ~$1.5K notional each (sized to
  survive an 8× run-up), that is roughly **$4K/yr**: useful, not prop-like. Next: forward paper log of new Hyperliquid pre-launch
  listings (radar) before any money; no Stage 2 registered yet.

### U-T6 (#389) Resting bids under liquidation wicks — **survives Stage 1 (kill-only)**; S2b **PASS**; S2a/S2c/S2d pending (2026-11-25)
`uv run python -m scripts.uncharted_wick_20261125` → `docs/jx_runs/uncharted_wick_20261125.txt` (re-run identical).
- X 15% (primary): **4,350 fills on 706 days, mean net +2.61% per fill (median +1.73%, t 15.45, win 60%), $67,089 = $19,606/yr on the
  $15,000 pot**; every year positive (2023 $9,819; 2024 $30,927; 2025 $16,070; 2026 to Oct $10,272); without the best day $18,504/yr.
  X 10%: +0.91%/fill, $27,133/yr. X 20%: +6.24%, $12,794/yr. X 30%: +13.21%, $12,536/yr.
- Checks: delisted coins included (56 of 235; their 1,088 fills average +2.7%); P&L spread over many coins (largest +$3.1K WIF, worst
  −$1.7K OM). Fill logic: a print ≥ 0.5% below the bid means the bid was consumed (price priority), so fills are not assumed.
- Mechanical fix found after Stage 1: size used the fill day's own volume (look-ahead). With the previous day's volume: 4,068 fills,
  +2.41%/fill, **$18,839/yr** — conclusion unchanged.
- **S2b (risk) PASS:** worst peak-to-trough −$2,480, worst day −$2,307 (2025-10-10), 6 losing months of 41
  (`uv run python -m scripts.uncharted_wick_s2_20261125`).
- **Capacity warning for S2d:** resting bids total ~$218K notional a day (median). If Hyperliquid reserves initial margin for open
  orders (third-party sources say yes; official docs not yet read), that is ~$52K of margin at each coin's maximum leverage, and a
  $15,000 account could post ~23% of the bids → **~$6.4K/yr**. Docs fetch `u389docs` queued.

### U-T1 (#383) Launch-phase perp-DEX house vaults — **survives Stage 1 (kill-only); forward-trial bar not met** (2026-11-25)
`uv run python -m scripts.uncharted_vaults_20261125` → `docs/jx_runs/uncharted_vaults_20261125.txt` (re-run identical).
- Vault series passing the pre-fixed name filter with ≥ 400 days: 5 (JLP, Resolv RLP, Origin stETH ARM LP, ZO ZLP, HLP).
  First-year hedged return on capital: JLP 82.6%, HLP 86.8%, ZLP 32.1%, RLP 15.0%, ARM −4.0% → **median 32.1%** (≥ 20%: survives).
- Forward-trial bar (median ≥ 40% across ≥ 4, year 1 beats year 2 in ≥ 3): median fails; year 1 beat year 2 in 4 of 4
  (JLP 83→31%, HLP 87→21%, ZLP 32→−38%, RLP 15→−93%). Context: DefiLlama fee APY of 92 Derivatives pools, year 1 > year 2 in 63.
- Limits: only 3 true perp-house vaults have price histories; vaults that died (exploits) have none → survivorship bias toward pass.
  Parked; would need share-price histories for Lighter LLP, Aster ALP, Ostium, Avantis, edgeX, Paradex to go further.

### U-T4 (#386) Delisting announcements → hedged short — **not testable** (2026-11-25)
`uv run python -m scripts.uncharted_tags_20261125` → `docs/jx_runs/uncharted_tags_20261125.txt` (re-run identical). Upbit's notice API
returns HTTP 403 to US servers. Binance "Delisting" category: 360 announcements (2023-04..2026-11), but only **2** spot token delistings
involved a token with a Hyperliquid perp (XMR −6.5%, LOOM +3.5% hedged) — below the 15 needed. Futures-contract delistings: 3 events.
- **S2d (desk), from Hyperliquid's docs** (fetched via Actions run 45617056553, `data/public/uncharted_389_hldocs.json`): open orders
  1,000 per user (+1 per $5M volume, max 5,000) — enough for one bid per perp; address action limit = 1 request per $1 traded plus a
  10,000 starting buffer — ~200 bid updates a day fit; maximum limit order value ≥ $5M — no constraint. **Not stated in the docs:**
  whether resting orders reserve margin. Two cases until checked: no reservation → ~$18.8K/yr (prior-day sizing); reservation at
  each coin's maximum leverage → ~$6.4K/yr. A one-minute test (place a small resting bid, see whether "available margin" drops)
  settles it; that needs Jx's Hyperliquid account.
- **S2a (out-of-sample market) PASS** (`uv run python -m scripts.uncharted_wick_s2_20261125` → `docs/jx_runs/uncharted_wick_s2_20261125.txt`,
  re-run identical; Binance archive, fetch run 45627417590): 918 USDT perps (delisted included), 2020-01..2026-10, X 15%: **17,286 fills,
  mean net +1.48% (t 14.98, win 59%), $15,776/yr, all 6 full years positive** (2020 $15.8K, 2021 $43.6K, 2022 $8.5K, 2023 $10.6K,
  2024 $24.7K, 2025 $1.5K). X 10/20/30%: +0.57/+3.44/+7.05% per fill.
- **Red flag (context, not a registered criterion):** the Binance $15,000-pot path had a **−$22,260 peak-to-trough drawdown
  (2025-09-13 → 2026-07-16)** — larger than the pot. Half-years with a negative mean per fill are crash regimes: Binance 2022H2 −2.79%
  (FTX), 2025H2 −2.17% (2025-10-10 cascade); Hyperliquid 2025H2 −2.69%. Hyperliquid's dollar P&L stayed positive in that window
  (+$5.1K) only through sizing; its mean per fill there was −1.09%. 2026H2 is positive again on both venues (HL +3.98%, Binance +1.61%).
  So the rule has a real long-run edge but loses in crash regimes, and the HL S2b pass rests on a shorter, kinder history.
- **Status:** S2a PASS, S2b PASS, S2c forward paper (radar N10) 2026-12-01 → 2027-01-26, S2d margin test needs Jx. No money until all
  pass; any live version would need a crash-regime limit (e.g. a daily loss stop), which is a new rule and needs its own
  pre-registration and forward test.

### U-T2 (#384) Withdrawal-queue discounts — **KILL on the registered data, but inconclusive** (2026-11-25)
`uv run python -m scripts.uncharted_lst_20261125` → `docs/jx_runs/uncharted_lst_20261125.txt` (re-run identical).
GeckoTerminal's free API returned only ~6 months of daily pool history (2026-05..2026-11), not 2024-01..2026-10. In that window the main
pools (kHYPE $4.0M, weETH $8.5M, rsETH $3.5M, sUSDe $1.3M reserve) never closed ≥ 1% below the 30-day-max NAV proxy; beHYPE/ezETH hits
were dust-sized → $3/yr → KILL by rule. Context only (not the registered source): DefiLlama/CoinGecko daily ratios 2024–2026 show
discount days (rsETH 149, pufETH 566, ezETH 75, sUSDe 42); the rule on those, with no volume cap, gives an optimistic ceiling of
$8.7K/yr (excluding beHYPE's feed artefacts), mostly pufETH (pool volume ≈ $0/day) and rsETH. That ceiling is unreliable: token and ETH
prices are snapshotted at different moments, which alone produces ~1% fake discounts. A fair test needs pool-level on-chain swap history
(Curve/Uniswap rsETH/ETH, ezETH/WETH, pufETH/WETH) — Stage 1b, to be pre-registered before fetching.

### U-T5 (#387) Uniswap CCA auctions — **KILL** (2026-11-25)
`uv run python -m scripts.uncharted_cca_20261125` → `docs/jx_runs/uncharted_cca_20261125.txt` (re-run identical). 1,152 auctions from the
four canonical factories (Base 528, Ethereum 407, Unichain 131, Arbitrum 86); 289 graduated; **16 real** (graduated, ended, real
USDC/USDT/ETH, ≥ $10K raised; most others are tests with fake "USDC"). 8 have a 7-day price: **median 7-day return −39.3%** (mean +2.1%;
FOLD +284%, BALANCE −93%, BFX −99%, RNBW −73%). 1-day median −32%, 30-day −21%. Aztec (VAZT, 19,390 ETH) has no tradeable price yet.

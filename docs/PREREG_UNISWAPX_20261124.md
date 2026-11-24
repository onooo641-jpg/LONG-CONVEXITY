# #371 UniswapX fillers on Arbitrum and Base: is filling open to newcomers or locked by a few pros? (non-prop) — 2026-11-24

**Why.** Coverage audit gap: UniswapX filling (a paid-bot role like CoW solving and Across relaying) was only desk-checked in 2026-11-21
("needs bonded capital + pros", sweep M10) and never measured. Written before any data are fetched.

**Stage 0 (official repo `Uniswap/UniswapX` README, read 2026-11-24).** Reactors: Arbitrum V3 Dutch Order Reactor
`0xB274d5F4b833b61B340b654d600A864fB604a87c`; Base Priority Order Reactor `0x000000001Ec5656dcdB24D90DFa42742738De729`. Every reactor emits
`Fill(bytes32 indexed orderHash, address indexed filler, address indexed swapper, uint256 nonce)` with `filler = msg.sender`. Filling is a
permissionless contract call on these chains (Dutch decay on Arbitrum; priority-gas auction on Base); Ethereum mainnet is left out
(quotes come through Uniswap-approved quoters, and free mainnet log scans failed in #361).

**Data.** Fill logs from public RPCs (as #362), plus 64 sampled block timestamps per chain for dating.
**Measures.** Fills per filler address per month; distinct fillers; top-3 share of fills; newcomers = fillers whose first fill falls in
the window's last six months; each newcomer's best monthly share.
**Stage 1 (kill only; 2026-08-01..2026-10-31, both chains).** KILL if the top 3 fillers make ≥ 90% of fills on **both** chains.
**Stage 2 (2025-11-01..2026-10-31).** "Door open" (only route to a further profit study) if on at least one chain a newcomer (first fill
2026-05-01 or later) reached ≥ 5% of that chain's fills in some month. Otherwise FAIL. Profit per fill is **not** measured here (fills carry
no amounts; a later study would need transfer-level data).

**Commands.** fetch: Actions job `uniswapx371`; analysis: `uv run python -m scripts.uniswapx_20261124 | tee docs/jx_runs/uniswapx_20261124.txt`.
**Limits.** A filler address is not a team (teams can use several); counts are not profits.

### Results Stages 1–2 (2026-11-24; `docs/jx_runs/uniswapx_20261124.txt`, identical on re-run)
Arbitrum: complete (0 blocks missed), 43,825 fills in 12 months by 55 fillers. Base: 231,531 fills, but the public-RPC time budget stopped
at 2026-07-23 (4.24M of 15.77M blocks missed), so Base's Stage 1 window is **not measured** (coverage handling made explicit in the script
before the verdict: an unmeasured chain cannot count towards a kill).
Stage 1 Arbitrum 2026-08..10: 10,957 fills, 28 fillers, **top-3 share 89.0%** (one filler 77%) → survives (kill needs ≥ 90% on both chains).
Stage 2: newcomers on Arbitrum reached **9.9% / 9.7% / 5.2%** monthly share (first fills Aug 2026) → **"door open"** (registered rule).
Base newcomers since May 2026: best 3.8%. Volumes are falling: Arbitrum 11.5K fills (Nov 2025) → ~4K/month; Base 74K → 6K/month.

### Stage 3 (registered 2026-11-24, after Stages 1–2, before any volume data): is there enough money?
Fill events carry no amounts. Data: transaction receipts of all Arbitrum fills 2026-08-01..2026-10-31; per fill, the swapper's input
transfer (token, amount) priced with DefiLlama daily prices (stables $1; other tokens via `coins.llama.fi`). **Ceiling** = annualised
priced input volume × **10 bps** (a generous filler margin before gas and hedging). **KILL** if 10% of the ceiling (a strong newcomer's
share) is below $15,000/yr. Command: fetch job `uniswapx371b`; analysis `uv run python -m scripts.uniswapx_vol_20261124 | tee
docs/jx_runs/uniswapx_vol_20261124.txt`.

### Stage 3 results (2026-11-24; `docs/jx_runs/uniswapx_vol_20261124.txt`, identical on re-run; fetch run 45401284013)
10,957 Arbitrum fills (Aug–Oct 2026), 10,597 priced (125 tokens; 342 unpriced transfers): **$191.9M in 92 days → $761M/yr**; median fill
$3,999. Volume share: top filler 84.0%; the August newcomers 7.3% and 5.2%. Ceiling at 10 bps: $761K/yr for all fillers; 10% share →
**$76K/yr → survives**. (A first fetch ran but its files were not saved because of an output-name mismatch; fixed and re-run.)

### Stage 4 (registered 2026-11-24, after Stage 3, before any output-side data): the margin fillers actually earn
Data: the same 10,957 Arbitrum fills; per fill the swapper's **input** (transfers from the swapper) and **output** (transfers to the swapper,
excluding refunds of the input token), each valued at the **hourly** DefiLlama price of the fill hour, for the tokens that make up the top
95% of Stage-3 input volume plus their output tokens (others dropped and counted). Gross filler spread per fill = USD(in) − USD(out)
(what the filler keeps before hedging cost and gas). Report: volume-weighted spread (bps), median, per filler (the two newcomers named).
**KILL** if the volume-weighted gross spread is < 2 bps, **or** either August newcomer's annualised gross (spread × its volume × 365/92)
is < $15,000/yr. Otherwise "worth a no-money filler prototype" (still not a pass). Hourly prices add noise of tens of bps per fill; it
averages out over ~10,000 fills but per-filler figures for small fillers are noisy (reported with fill counts).
Command: fetch `uniswapx371c`; analysis `uv run python -m scripts.uniswapx_margin_20261124 | tee docs/jx_runs/uniswapx_margin_20261124.txt`.

### Stage 4 results (2026-11-24; `docs/jx_runs/uniswapx_margin_20261124.txt`, identical on re-run; fetch run 45406058307)
16,750 swapper transfers from 10,957 fills; hourly prices for 37 of the 40 most-used tokens. **Measured 5,051 fills ($102.6M)**; dropped
5,797 (unpriced token, or no ERC-20 output to the swapper — e.g. native-ETH payouts, which emit no Transfer event) and 109 with |spread| >
500 bps. **Volume-weighted gross spread 8.62 bps** (median 2.62 bps); gross $88,459 in 92 days (≈ $351K/yr on the measured half).
Dominant filler: 4,148 fills, $92.9M, 4.25 bps, ≈ $157K/yr gross. **Newcomer A** (first fill 2026-08-13): 250 fills, $3.35M, 64.1 bps,
**≈ $85K/yr gross**; **newcomer B** (2026-08-21): 106 fills, $2.68M, 48.8 bps, **≈ $52K/yr gross**.
**Verdict (registered): survives → "worth a no-money filler prototype" (not a pass).**
**Limits.** Gross ≠ net: the spread is measured against hourly mid prices and still contains the filler's DEX/hedging execution cost and
gas; only 46% of fills are measured (native-ETH payouts are invisible to Transfer logs); newcomer figures rest on 250 and 106 fills and may
reflect long-tail tokens with wider spreads and higher hedging risk. Filler addresses are not teams.

### Stage 5 design notes (2026-11-24, probes `docs/jx_runs/fetch_fallback_45411276620.txt` and the uxorders run)
- UniswapX's order API is public (open and filled orders; fields include input/outputs with start/end amounts, cosignerData, fillBlock,
  fillTimestamp, settledAmounts); KyberSwap's aggregator quotes work without a key on Arbitrum; 0x needs a key; Odos returned an error.
- Open orders were empty at probe time (orders live seconds); the filled-order endpoint returned only the latest 50 (~9.5 hours) without a
  pagination cursor, so a months-long retrospective paper test is not possible from this API without further work (decoding V3 block-based
  decay curves from `encodedOrder`, paging by time).
- The sandbox cannot reach these hosts; GitHub Actions can. A live paper filler needs ~36 runtime hours for ~200 Arbitrum orders
  (~5.5 per hour), which would compete for the same Actions minutes as workstream B's live liquidation shadow test.
**Next step needs Jx:** where the live paper filler runs (GitHub Actions minutes / a PC / a small server, ~$5–20/month, needs approval).

### Stage 5 (registered 2026-11-24, Jx chose to run it on his PC): live paper filler, no money
**Program.** `tools/uniswapx_paper_filler.py` (Python standard library only, read-only public APIs, no wallet or keys). Every 2 s it reads
open UniswapX orders on Arbitrum (`api.uniswap.org/v2/orders`); for each open order it asks KyberSwap's free aggregator
(`aggregator-api.kyberswap.com`) how much output the order's input would buy right now, including KyberSwap's gas estimate; it logs every
quote until the order disappears, then reads the order's fill record (settled output, fill time) from the same API.
**Measure per filled order.** Paper profit = our last pre-fill quote − the output the real winner delivered − gas (KyberSwap gas estimate
+ $0.10 fill overhead), in USD. "Competitive" = paper profit > 0 (we could have paid the swapper what the winner paid, from a public DEX
route, at about the same moment). Exact-output orders use the maximum input (conservative).
**Run.** ≥ 36 hours (target ~200 filled orders). **Verdicts** (on filled orders with a pre-fill quote):
- **KILL** if competitive share < 5% of orders **or** annualised paper profit (Σ positive paper profit × 365 × 24 / hours run) < $5,000.
- **Worth building a real filler** (still not income: speed is untested — the metric assumes we fill at the winner's moment) if
  competitive share ≥ 10% **and** annualised paper profit ≥ $15,000. In between: inconclusive (extend the run).
Command on Jx's PC: `python uniswapx_paper_filler.py --hours 36`; the program writes `uniswapx_paper_log.jsonl` and
`uniswapx_paper_summary.txt`, which Jx sends back; analysis re-computed from the log by `--summarize`.
**Runtime change (2026-11-24, Jx):** run on GitHub Actions instead of Jx's PC — workflow `uniswapx_paper.yml`, chained 5.5-hour
sessions until 36 hours, log and summary committed to `data/uniswapx_paper/` after each session. Rules and verdict bars unchanged.
Cost noted to Jx: ~2,160 Actions minutes, shared with workstream B's shadow test and the daily radar.

### Stage 5 outcome (2026-11-24): stopped — the open race the paper filler was meant to measure does not exist on Arbitrum any more
- 10-minute live smoke test (fallback run 45420214269, `docs/jx_runs/fetch_fallback_45420214269.txt`, log in `data/public/uxsmoke_run/`):
  the program ran against the live APIs; 1 order appeared and was **filled 1 second after creation**; the order parser failed on the V3
  format (fields `curve`, `maxAmount`, `minAmount`), so no quote was taken.
- The 50 most recent filled Arbitrum orders (`data/public/uniswapx371_orders_sample.json`): **50 of 50 carry an `exclusiveFiller`** set by
  the cosigner (top: the dominant filler 26, then 12, 6, 4, 2 — the same "newcomers" as Stage 2), and **all were filled 1–3 seconds after
  creation** (median 1 s).
- Uniswap's docs (developers.uniswap.org, "UniswapX RFQ auctions on Base and Arbitrum", 2026-06-13; "Become a quoter"): Arbitrum and Base
  moved from open Dutch auctions to **RFQ**; the winning quoter gets an exclusivity window; the **quoter role is permissioned and vetted by
  Uniswap Labs** (intake form / waitlist), with ≥ 5 successful exclusive fills in beta before production and "fade" penalties; filling is
  permissionless only after the exclusivity window.
- So Stage 2's "newcomers" are **newly approved quoters**, and the paper filler (an outside filler) could almost never fill. The 36-hour
  chained run (workflow `uniswapx_paper.yml`, run 45420156616) was **cancelled** after ~30 minutes to save Actions minutes.
**Reading.** UniswapX filling has CoW's shape: protocol-level order flow with approved newcomers earning ≈ $50–85K/yr gross, but entry
requires Uniswap Labs' approval as an RFQ quoter (a firm-quote service answering within ~500 ms, then filling). Next step only Jx can take:
submit Uniswap's quoter intake form (or keep it parked with CoW). Stage 5 verdict: **not run (premise invalid)**.

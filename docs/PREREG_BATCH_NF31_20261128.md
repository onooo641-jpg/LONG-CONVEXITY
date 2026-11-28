# Batch NF31 (#664–#667): Clanker tokens on Base — the same four rules as NF30, a third thin AMM ecosystem — pre-registered 2026-11-28, before any Clanker data is fetched

**Why:**
- This is an independent out-of-sample check of the NF21 #627 / NF30 #660 family (momentum and launch dynamics in thin, closed AMM
  token ecosystems).
- Clanker deploys permissionless ERC-20s with Uniswap pools on Base, mostly against WETH, traded by on-chain retail.
- Earlier evidence: Bittensor momentum was positive (t 1.77); HL spot weekly momentum (#632) was negative.

**Data (job `ubatchnf31`):**
- Clanker public API token list (all pages; every token ever deployed, so dead tokens are included).
- GeckoTerminal daily OHLCV per pool (`currency=token`, so prices are in the quote token).
- Only WETH-quoted pools are used. The hedge is an HL ETH short.
- HL ETH funding: `fundgap_funding.parquet` (HL, to 2026-11-01), mean-filled after that.
- **Order and coverage:** tokens are ranked by Clanker's listed market cap (or deploy order if none is given), and the fetch takes as
  many pools as the 150-minute budget allows, oldest first. The coverage achieved is printed.
- Raw first replies go to `batchnf31_probe.json`. A fix may be added by addendum before analysis.

**Rules: NF30's exactly** (#660 → #664 momentum, #661 → #665 reversal, #662 → #666 new tokens days 8–37, #663 → #667 first-week
drift).
- Prices are in WETH, hedged with ETH.
- Costs: 1% swap fee per side (Clanker pools, third-party) plus NF30's impact model, plus HL 0.09%.
- Eligible: ≥ $20K median daily volume.
- Same split, kill and pass rules; −100% if the last price is below 1% of entry.

**Script/output:** `scripts/batch_nf31_20261128.py` → `docs/jx_runs/batch_nf31_20261128.txt`, re-run identical.

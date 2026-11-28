# Batch NF25 (#643–#646): zero-fee points farming, hedged across venues — Stage 0 desk result and measurement plan (2026-11-28)

**Jx (2026-11-28):** "Find what other loopholes to exploit."

**Mechanism:**
- Perp DEXes run points programmes that convert into token airdrops. The token issuer pays.
- On zero-fee venues (Lighter, Paradex), volume costs only the spread. The idea is to keep a long on one venue and a short on another,
  with no market exposure, and earn points on both.
- **Rule boundary:** only ordinary trading is in scope. Wash trading, self-trading and sybil accounts are excluded. These are rule
  violations; Lighter slashed such points.
- #360 was "not measurable" because per-wallet formulas are unpublished. The **aggregate** yield (airdrop value ÷ volume during the
  programme) is measurable, and it is what an average farmer earned per dollar of volume.

**Honesty note:** rough figures for Lighter and Paradex were seen during desk research, before this file was written. So NF25 is a
**descriptive measurement**, not a blind pre-registered test, and no PASS is claimed from it.

## Stage 0 desk figures (third-party sources; none verified on-chain)

| # | Programme | Airdrop | Qualifying window | Volume | ≈ $ per $1M volume |
|---|---|---|---|---|---|
| 643 | Hyperliquid | 310M HYPE (31%), ~$1.2B at TGE 2024-11-29 (The Block) | points 2023-11-01..2024-05-01 (1M points/week, per docs summaries) | DefiLlama, job `ubatchnf25` | to be measured |
| 644 | Aster | 704M ASTER (8.8% of supply) unlocked at TGE, claims from 2025-09-17 (Aster docs) | Stages 1–2 | "$37B+" in the earlier campaign (press release) | to be measured |
| 645 | Lighter | 250M LIT (25%), ~$675M at TGE 2025-12-30 (Bubblemaps via Cointelegraph); 12.5M points → 20 LIT/point | S1 2025-01-23..09-30 (~$550B), S2 Oct–Dec | about $1.1T in total | **~$590** |
| 646 | Paradex (zero fee) | 25% of DIME supply; FDV snapshots about $10–19M (CoinGecko, DropsTab), all-time high $0.10 (~$100M FDV) | pre-season..S2 end 2026-01-31 | "$250B+" cumulative | **~$25–100** |

**Reading:**
- The later and more crowded the programme, the lower the yield. Hyperliquid paid in the thousands of dollars per $1M (likely); Lighter
  about $590; Paradex below a typical spread cost of $100–200 per $1M of hedged volume.
- With zero fees, everyone farms, and the yield falls to about the cost. That is the same decay as every other edge in this repo.

**What would make it repeatable (forward only):**
- Live programmes, according to an affiliate guide as of 2026-08: Paradex S3, Extended, Pacifica, and Lighter's reserved 25%.
- Points trade OTC before TGE (Lighter points about $100: The Defiant). The weekly points issued, the OTC price and the weekly volume
  give the **current** $ per $1M before the airdrop.
- Selling points forward is often against venue terms. It is noted as a measurement source only, not as a strategy.
- **Radar addition:** add a points-yield lead when OTC price × weekly points ÷ weekly volume ≥ 3 × the hedged cost. Not yet built,
  because no free OTC price API was found.

**Data job `ubatchnf25`:** DefiLlama daily derivatives volume for Hyperliquid, Aster, Lighter and Paradex, to fill the volume column.
Output goes to `docs/jx_runs/batch_nf25_20261128.txt`.

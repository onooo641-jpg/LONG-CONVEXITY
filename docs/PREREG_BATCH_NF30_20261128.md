# Batch NF30 (#660–#663): Virtuals agent-token ecosystem on Base — momentum, reversal, new launches — pre-registered 2026-11-28, before any of this data is fetched

**Why:**
- NF21 #627 (subnet momentum) is the strongest near-miss so far: +6.9%/month hedged, t 1.77.
- The cleanest out-of-sample check of "momentum in a thin, closed AMM token ecosystem" is a **different** ecosystem of the same kind.
  Virtuals agent tokens are hundreds of thin tokens, almost all paired against VIRTUAL in AMM pools on Base, traded by on-chain retail.
- VIRTUAL has an HL perp, so the ecosystem's market exposure can be hedged.
- Genesis launches were candidate #7 in `reports/Grey area edges for small capital.md`; only promotional peak multiples exist.

**Desk checks:**
- **G5:** Base DEX use needs no KYC (SC Malaysia does not protect it; lawful but unprotected, unverified).
- **G6:** thin and retail.
- **Survivorship:** the agent list comes from the Virtuals API, all statuses, **including dead agents**. A token whose pool stops
  trading counts at its last price, and at −100% if its last price is below 1% of entry.

**Data (job `ubatchnf30`):**
- **Virtuals API:** every agent with a token and LP address (paged; all statuses), with created date and status.
- **GeckoTerminal:** daily OHLCV per LP pool on Base (`networks/base/pools/{lp}/ohlcv/day`, up to 1,000 days). Prices are taken in
  VIRTUAL where the pool quotes VIRTUAL, otherwise in USD.
- **HL:** VIRTUAL daily closes and funding (existing daily candles; funding from `fivehigh_hl_premium` where available, else its mean).
- **Endpoints are not verified** from this sandbox. Raw first replies go to `batchnf30_probe.json`. A fix may be added by addendum
  before analysis.

**Common:**
- **Returns** are in VIRTUAL terms (the agent token's return in VIRTUAL), hedged with an HL VIRTUAL short to remove the ecosystem's USD
  exposure.
- **Costs:** 1% swap fee per side (the Virtuals bonding/LP fee; third-party), plus constant-product impact for $1,000 against the
  pool's USD liquidity, approximated by daily volume where reserves are unknown: impact = $1,000 / (0.5 × daily volume), capped at 10%.
  Plus HL 0.09% for the hedge.
- **Eligible:** ≥ $20,000 median daily volume over the previous 30 days.

| # | Idea | Rule |
|---|---|---|
| 660 | **4-week momentum** | on the 1st of each month, the 10 eligible tokens with the highest 28-day return; hold 1 month (NF21 #627's rule) |
| 661 | **4-week reversal** | the 10 with the lowest 28-day return; hold 1 month |
| 662 | **New agents, days 8–37** | buy each agent 7 days after its first pool candle (if eligible that day); hold 30 days |
| 663 | **Genesis/launch first week** | buy at the close of the first full day of trading; hold 7 days (measures the post-launch drift that Genesis allocations ride) |

**Split:**
- Stage 1 = holds starting before 2025-07-01 (kill only);
- Stage 2 = 2025-07-01..2026-10-31, unseen.

**Stage 1 KILL:** ≥ 6 holds (monthly) or ≥ 30 trades (#662–#663), and mean ≤ 0.

**Stage 2 PASS:** all of
- ≥ 10 monthly holds or ≥ 30 trades;
- mean ≥ 3%/month (#660–#661) or ≥ 3% per trade (#662–#663);
- t ≥ 2;
- positive without the 3 best;
- positive with costs × 1.5;
- no single token > 40% of profit.

**Multiple testing:** four tests. Only a pass with t ≥ 2.5 goes to the forward log. If #660 passes **and** #627 is positive forward,
the momentum family is treated as confirmed.

**Script/output:** `scripts/batch_nf30_20261128.py` → `docs/jx_runs/batch_nf30_20261128.txt`, re-run identical.

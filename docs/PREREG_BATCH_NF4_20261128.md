# Batch NF4 (#547–#550): Korean retail flows traded on Hyperliquid — pre-registered 2026-11-28, before running

**Niche and desk checks.**
- **Payer:** Korean retail on Upbit, which is price-insensitive and herd-driven.
- **G6:** Korea's capital controls keep foreign arbitrage out, so coin-level kimchi premia and Upbit frenzies are not arbitraged
  away by funds.
- **G5:** every trade is on the Hyperliquid perp (usable from Malaysia).
- **Data:** `distinct_upbit_1d` (Upbit KRW close and KRW value traded, 301 coins, 2020-05..2026-11); HL daily candles
  (`uncharted_385_candles`; Upbit "PEPE" matches HL "kPEPE"). Upbit KRW listings: `uncharted_w3b_korea`.
- **Not repeats:**
  - #395 is the KRW listing-day fade (its forward log is radar N12);
  - Korea ideas in Batch 10 / DISTINCT used the market-wide premium, not coin-level premia or Upbit volume.

**Rule basics.**
- Signals use day d's Upbit data (KST day ends 15:00 UTC, before the HL daily close at 24:00 UTC, so it is known in time).
- **Entry:** at HL's close of day d. **Exit:** at HL's close of d + h.
- **Excess** = side × (coin − HL BTC) − 0.09%. Funding not modelled.
- At most one open trade per coin; BTC and stablecoins excluded.

| # | Idea | Signal on day d | Side, hold |
|---|---|---|---|
| 547 | **Upbit retail frenzy fade** (Korean retail chases; foreigners cannot arbitrage in, so the frenzy overshoots globally too) | KRW value traded ≥ 10 × its median of the previous 30 days and ≥ ₩50bn | short HL, 3 days |
| 548 | **Coin-level kimchi premium → global catch-up** (Korean demand the capital controls bottle up leaks out through arbitrage and front-running) | relative premium = (KRW close ÷ HL close) ÷ (BTC KRW ÷ BTC HL) − 1 ≥ +8%, after < +8% the day before | long HL, 3 days |
| 549 | **Coin-level kimchi discount → Korean selling spills over** (warnings and delisting fears make Korean holders dump) | relative premium ≤ −5%, after > −5% the day before | short HL, 3 days |
| 550 | **Dying KRW listing** (Korean listing pump fades as retail leaves; #540's Korean twin) | an Upbit KRW market listed on day L (`uncharted_w3b_korea`, Upbit only) whose day-7 KRW value < 20% of day 1's | short HL at day 7's close, 14 days |

**Split:** signals before 2025-01-01 = Stage 1 (kill-only); 2025-01-01 onward = Stage 2.

**Stage 1 KILL:** mean ≤ 0 (≥ 8 trades).

**Stage 2 PASS:** ≥ 15 trades, mean excess ≥ 2%, t ≥ 2, sum still positive without the 3 best trades.

**$/yr:** $3,000 per trade.

**Script/output:** `scripts/batch_nf4_20261128.py` → `docs/jx_runs/batch_nf4_20261128.txt`, re-run identical.

# Re-price the Topstep $3K Challenge at what is actually on sale — pre-registered 2026-11-27

**Why.** The planning chat (2026-11-27) read Topstep's official pages:
- help.topstep.com article 18466040 now lists the $3K Challenge at **$199 one-time, 5 minis / 50 micros, $1,000 static MLL**.
- The $49 version (10 micros / 1 mini) was **Labs Drop #003**, a limited past drop.
- Current Labs versions: **Undead $199** (50 micros, $1,000 MLL) and **Slasher $65** (20 micros, $500 MLL).
- The repo's qualifying figure (PS3b: $24,757, flip $7,674, dip −$1,176, break-even $68) priced the past $49 / 10-micro drop.

**Model (unchanged).** `scripts/prop_search2_c2_20261126.challenge`:
- two rounds from $0, each must reach +target before worst open P&L touches −MLL (static);
- passing both pays a fixed payout and the account closes, then buy another;
- the $900 risk is scaled down to the contract cap;
- friend's NQ trades 2016–26, `radar_price.trades(orders, bars, 0)`, corrected engine.

**Assumed, not on the pages read:** target $3,000 and payout $3,000 for every version, as in the original Labs reading. Slasher's
target and payout were not stated; it is priced with the same $3,000 / $3,000, and its row is labelled assumed.

**Rows:**
1. Past drop $49 / 10 micros / $1,000 (must reproduce PS3b: $24,757 / $7,674 / −$1,176).
2. **$3K Challenge $199 / 50 micros / $1,000** (Undead has identical parameters).
3. Slasher $65 / 20 micros / $500 (assumed target/payout).
- For each: real net, coin-flip median (200 flips, seed 1, `flip`), worst dip, verdict, and break-even price (bisection on 0–2,000).

**Bar (registered, corrected engine):** real ≥ $19,017, coin flip ≥ $5,000, dip ≥ −$5,794.

**Script/output:** `scripts/challenge_reprice_20261127.py` → `docs/jx_runs/challenge_reprice_20261127.txt`, re-run identical.
Docs to update with the result: PS2C/PS3b ledger rows (mark as past drop), `GO_LIVE_MULTIFIRM.md`, `NOTES_JX.md`, `START_HERE.md`.

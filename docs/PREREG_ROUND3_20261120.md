# Round 3: remaining bot-allowed futures firms vs Topstep 50K — 2026-11-20 (CANDIDATES #56)

Written and committed **before** any run.

## Screen (automation policy, read 2026-11-20)
| firm | bots? | source | in this test? |
|---|---|---|---|
| MyFundedFutures (MFFU) | **Allowed**: "Traders may make use of automated trading strategies tailored to their own specific settings", no HFT, no exploiting sim fills | MFFU help centre, Fair Play page (read directly) | yes, Rapid EOD 50K |
| The Futures Desk (TFD) | **Allowed**: "algorithmic trading are allowed" (FAQ), "Scalping + Algos" | TFD members site, static plans page (read directly) | yes, Static Core and Static Pro |
| Apex | conflicting third-party reports; official page not readable this session (approval needed) | — | no, unresolved |
| Phidias, Earn2Trade, Take Profit Trader, Top One Futures, Blue Guardian, Alpha Futures, Funded Futures Family | banned | firm help centres as quoted by third parties; Top One's own help centre | no |
| HyroTrader | allowed (own bots, API), but **crypto only**, 3% max risk per trade | HyroTrader FAQ | no: the strategy is NQ |

The structure scan (#48) excluded MFFU as "semi-automated only". That came from a
third-party page; MFFU's own Fair Play page allows automated strategies. Corrected here.

## Products and rules
Common: friend's NQ trades 2016-01..2026-10, `Policy.LOCK_FIRST`, coin flip = 200 runs,
seed 1, signs randomised, commission kept. Contract caps in micros.
**Risk per trade = min(0.45 × loss limit, 0.875 × daily loss limit)**: a firm with a
daily loss limit forces smaller risk so a full stop cannot hit it. Trades are scaled
from the $900 base by that ratio.

**Topstep 50K** — reference, `XFARules()` unchanged.

**MFFU Rapid EOD 50K** (risk $900)
- Evaluation: target $3,000; EOD trailing $2,000; 30% consistency; 3 minis / 30 micros;
  no daily limit; $157 one-time, 365 days access (modelled as 365-day expiry); bust = new $157.
- Funded (official help page "Rapid EOD 50k"): starts $0, EOD trailing $2,000, locks at
  +$100 once the peak reaches $2,100; 30 micros; first payout needs the $2,100 buffer and
  pays what sits above it; each later payout needs $500 net since the last; min $500;
  no cap per cycle; 90/10; daily.
- Not modelled: 4 minimum evaluation days; the $10K-day live transition (a $900-risk
  trade does not make $10K); "limited-time" plan status (may not be on sale).
- Third-party sources: price, 30% consistency, 30-micro eval cap.

**TFD Static Core** (2 minis / 20 micros; daily limit $800 → risk $700)
- Assessment: static floor −$2,000, target $4,000; $139 (discounted from $559),
  31-day extension $29 (modelled as $29/month for the whole run — overstates cost),
  reset + extension $99.
- Build-buffer phase: static floor −$2,000, buffer target +$2,000; then live account
  starts at $2,000 with a $0 static minimum. Modelled as one funded account: static
  floor −$2,000 that jumps to $0 when the peak reaches +$2,000.
- Payouts: daily, uncapped, min $100, 80/20. Modelled as everything above the $2,000
  live starting balance.
- Not modelled: 7 minimum assessment days; "$572 base hits" consistency (meaning not
  stated); whether the daily limit fails or pauses (risk sized below it, so moot).

**TFD Static Pro** (3 minis / 30 micros; daily limit $1,200 → risk $1,050)
- Static floor −$3,000, target $6,000; $179; buffer target $3,000; live start $3,000, floor $0.

**Sensitivity (not ranked):** TFD Core with payouts allowed down to the floor
("Payouts Into Buffer" is listed on the page but not explained). Upper bound only.

## Metric and reading
Real net, coin-flip median net and share profitable, worst dip, payouts, busts.
Ranking, no pass/fail. A product **"beats Topstep"** only if both its real net
> $44,359 and its coin-flip median > $18,046. Anything that beats Topstep goes to a
full rules read and a support question before any purchase.

Command: `uv run python scripts/round3_20261120.py`

## Results (2026-11-20, `docs/jx_runs/round3_20261120.txt`)
| product | risk | real net 2016–26 | coin-flip median (profitable) | worst dip | trades over contract cap |
|---|---|---|---|---|---|
| Topstep 50K (reference) | $900 | **$44,359** | **$18,046 (98%)** | −$3,520 | 25% |
| MFFU Rapid EOD 50K | $900 | $34,481 | $7,358 (74%) | −$5,590 | 43% |
| TFD Static Pro | $1,050 | $20,248 | $3,274 (71%) | −$3,667 | 49% |
| TFD Static Core | $700 | $10,680 | −$1,163 (38%) | −$3,226 | 49% |
| TFD Core, payouts to floor (sensitivity) | $700 | $18,253 | $3,068 (74%) | −$3,226 | 49% |

**Nothing beats Topstep.** Why:
- **MFFU:** uncapped payouts above a $2,100 buffer are generous, but there is no free
  reset (every evaluation bust costs $157; 96 busts) and the 30-micro cap trims 43% of trades.
- **TFD:** static floors help, but the daily limit forces smaller risk, the 20/30-micro
  caps trim half the trades, the 80% split, and the $4,000/$6,000 targets are harder.
- MFFU's $34.5K is similar to Lucid's $37.5K (#36). It is an extra slot that could run
  **alongside** Topstep (a separate firm), not a replacement. Worst dip is larger (−$5,590).

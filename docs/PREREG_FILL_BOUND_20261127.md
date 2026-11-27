# Fill bound without money: Topstep 50K Consistency when the bot is on time but fills are pessimistic — pre-registered 2026-11-27

**Question.** Jx cannot use the friend's live fills, and does not want to spend money only to measure fills. Can the decision be made
from figures that already assume pessimistic fills?
- The nightly dry run measures order timing for free (seconds after the confirming bar, or not).
- Only fill quality (queue position on limit entries, stop slippage) then needs real orders.
- So: what is Topstep 50K Consistency worth if timing is fine but fills are bad?

**Data, model, costs.** As `scripts/audit_pre_live_20261126.py` section C:
- friend's NQ orders `ideas_orders_NQ.parquet`, 1-minute bars, $900 risk, 2016-01-01 to 2026-10-29;
- corrected real-time loss-limit model; $1.24 round trip;
- rules `P["Topstep 50K Consistency path"]`.

**Exact variants** (orders on time in all of them):
1. baseline (touch fills, stop slips 1 tick);
2. limit entry needs price 1 tick through;
3. stops slip 2 ticks;
4. **2 + 3 together** (new);
5. **2 + stops slip 3 ticks** (new, harsher);
6. **2 + 3 + a touch-only entry fills only if the bar after it trades through** (not built; dropped here, no engine option exists).

For each variant, report:
- net 2016–26, worst dip and start-money table (as section C);
- filled trade count;
- **coin-flip median** (200 flips, seed 1, `radar_price.flip`).

Also report the share of baseline fills where price only touched the entry (filled in baseline, not filled in variant 2).

**Pass criteria (Topstep's standing bar):** variant 4 must keep real net > $0 **and** coin-flip median ≥ $5,000.
- Pass: the decision to run one live account does not depend on fill quality. Live then only confirms payouts and timing.
- Fail: fill quality decides the plan, and the first live account is a fill measurement, sized as such.
- Variant 5 is reported only.

**Script/output:** `scripts/fill_bound_20261127.py` → `docs/jx_runs/fill_bound_20261127.txt`, re-run once, identical.

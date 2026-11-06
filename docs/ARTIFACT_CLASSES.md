# Artifact classes

Named failure classes, with sighting counts, for backtest/live defects that
look like edge but are measurement error. The point of naming one is that the
second sighting gets recognised faster than the first did.

## (1) Confirmation timing one bar early

**Shape:** a detector marks a pattern "confirmed" at the anchor bar's *open*,
but the pattern is only knowable once that bar's *close* (or its extremes)
exist. An order placed "on confirmation" can then fill using information from
inside the bar that generated the signal — a close that had not printed yet.

**Why it survives review:** it is *self-consistent*. A truncation test (does
cutting the data short and rerunning produce the same signals up to the cut?)
passes cleanly, because being one bar early is a uniform property, not a
leak that only shows up at some horizon. The test that would catch it has to
check the property directly — "does confirmation land on a bar close" — not
check consistency across truncation.

**Symptom:** a suspiciously high fill rate (100%, in the one sighting so far).

**Sightings: 1.** Commit `cfddcfc` ("Fix one-bar look-ahead in every
detector"), 2026-09-06. Affected every one of the (then) seven detectors.
Impact was not marginal — it was the entire apparent edge of two strategies:

| | development | out-of-sample |
|---|---|---|
| `sfp_reversal` | +$206k → -$430k | +$197k → -$103k |
| `ob_retest` | +$175k → -$181k | +$77k → -$86k |

After the fix, all seven lost money in both periods. One bar of hindsight on
a 5-minute chart was worth several hundred thousand dollars of fictional
profit. `tests/test_confirmation_timing.py` now tests the property itself.

## (2) Marketable limit orders filling at prices the market had already left

**Shape:** the backtest places a limit order at a retracement level, but by
the time the order is live, price has already traded through that level. A
sell limit *below* the current market (or a buy limit *above* it) is not a
resting limit order at all — it is marketable, and a real exchange fills it
immediately at the market price, not at the level the model requested. The
backtest, modelling naive "limit touched = filled", gives the model a price
the market could not actually have handed it.

**Why it survives review:** the retracement premise (price pulls back to a
level before continuing) silently fails on exactly these fills, but the trade
still shows up in the results looking like an ordinary limit fill — nothing
in a P&L table distinguishes "filled where requested" from "filled because the
order was never really a limit order."

**Symptom:** a chart/backtest reconciliation that disagrees about the fill
price, not the signal — same contracts, same risk, very different entry.

**Sightings: 1.** Commit `7fa7f86` ("Refuse limit orders the market has
already passed"), 2026-09-09, found by reconciling a live chart against the
research log: same 3-contract size off the same 77.12-point risk, fills 50
points apart. 31 of 581 out-of-sample LTF Sweep fills and 114 of 1,724 in
development were marketable on the order's first live bar — none were a gap.
`BacktestConfig.skip_marketable_entries` (default `True`) now declines them
with `exit_reason="premise_failed"`, counted against fill rate rather than
dropped. Validated before being believed: the filter removed *more* edge in
development (21.1% win, PF 0.248) than out-of-sample (38.7% win, PF 0.616) —
the opposite of what a curve fit protecting a good-looking number would do.
Full-history impact at $500/trade: 51.4%/PF 0.883/-$38,434 →
53.2%/PF 0.876/-$3,044 (this exact figure is `FIGURES_LEDGER.md` #3, now
superseded by more data and later commits, not by being wrong).

## (3) An API response that cannot distinguish failure from a legitimate empty result

**Shape:** a bridge/broker API call that returns an empty array both when
there is genuinely nothing to return (no bars yet, no open orders) *and* when
the call itself was wrong (bad contract ID, wrong data-feed flag, bad
credentials). The caller cannot tell "nothing happened" from "something is
broken" without an independent check.

**Why it survives review:** it fails *quietly*. `docs/GO_LIVE.md`'s own
preflight notes already list this symptom under "wrong contract ID or wrong
`BRIDGE_LIVE_DATA` returns an empty array, not an error" — but as a checklist
line to remember, not a named class with its own detection logic. A checklist
item gets read once and then relied on from memory; a class gets a
preflight assertion that fires every time regardless of whether anyone
remembered the checklist.

**Correction (2026-11-06, later the same day):** the paragraph above is
wrong about the current state of the code, not just stale. Checked
`bridge/preflight.py` directly before acting on the "not yet promoted to an
assertion" claim: `bar_feed_checks()` has hard-failed on an empty bar array
since commit `26d253d` ("Add preflight, a decision journal, and
reconciliation"), 2026-09-10 — a month before this class was even written.
`run()` calls it with `reach_broker=True` by default, and both CLI entry
points (`bridge/live.py`, `bridge/server.py`) only skip it behind an explicit
`--offline` flag. The real gap was that nothing tested this behaviour, so a
refactor could have quietly turned the hard FAIL back into a pass-through
and nothing would have caught it. Closed with `tests/test_preflight.py`
(four tests: empty array, broker exception, fresh bars pass, a
close-stamped-not-open-stamped feed still fails the age check) rather than
with new preflight code, since none was needed.

**Sightings: 1**, at `bridge/roundtrip.py`'s site (below) — the
`open_orders`/`open_positions` ambiguity, which is a different call site
than `bar_feed_checks` and genuinely not addressed on this branch.

**Update (same day, independent session):** a concurrent Claude Code session
on this same repo (`Jx <onooo641@gmail.com>`, commit `1a8802c`) implemented
exactly this for the `open_orders`/`open_positions` sites: `bridge/roundtrip.py`
(`python -m bridge.live --roundtrip`) places a real order, requires it to show
up non-empty, cancels it, requires it gone, and only then writes a proof file
keyed on account + contract id. Without a matching proof, `day_done()` never
returns clean. That code lives on `origin/claude/ict-trading-resources-ugh07b`,
not on this branch — it touches the live-trading bridge (real-money execution
path), which is out of scope for a documentation/ledger replication pass. Not
ported here; the next session that works on `bridge/live.py` should pull it in
rather than re-deriving it.


**Guard, ported 2026-11-07** (from commit 1a8802c on the other branch):
`bridge/roundtrip.py`. `python -m bridge.live --roundtrip` places a one-lot
buy limit 30% under the market, requires it in `ours(open_orders())`,
cancels it, requires it gone, then writes `data/roundtrip_proof.json` keyed
on account id and contract id. Without a matching proof, `--live` never ends
the day clean: it stops at the flat time with exit 1, so the shutdown wrapper
doesn't fire. The deadline sweep also treats an empty book as unreadable and
cancels everything it sent. This covers the shutdown-path sites
(`open_orders`, `open_positions`, the `ours()` contract-id filter) that the
bar-feed preflight check does not. GO_LIVE step 4b. Four tests in
`tests/test_live.py`.

## 4. One claim, two parameterisations, no label

The same sentence in prose is backed by different settings in different
places, and neither place says which — the general shape of what check 1
(`docs/NOTES_JX.md`) found as a single instance.

- **Why it survives review:** both numbers are individually real and
  individually reproducible. The bug is only visible when they are read next
  to each other and assumed to be the same measurement.
- **Sightings: 2.** (1) `docs/GO_LIVE.md`'s $42,414 net vs $61,984 cash,
  quoted together as if one figure (this session, see `FIGURES_LEDGER.md`
  #4). (2) An independent concurrent session named this same pattern as its
  own class 4 and found a second instance: the README's "PF 0.876" is
  actually the payoff ratio, not profit factor (true PF 0.994) — its own
  ledger's row S4/S5.
- **Guard:** `docs/FIGURES_LEDGER.md`. Every standing figure names its exact
  command; a number without a row is not a standing figure.

## 5. "After time X" by clock minute, when the window spans midnight

A CME trading date opens at 18:00 ET the day before. A selection like
`day[minutes >= RANGE_END_MINUTE]` (minute-of-day only) lets the previous
evening's bars — which also satisfy "minute >= 09:35" — count as "after the
09:30-09:35 opening range," breaking or failing a range that does not exist
until the next morning. Look-ahead, and the same root cause as class 1
(self-consistent under a truncation test, since being wrong by a fixed offset
truncates the same way every time).

- **Sightings: 1 incident, 2 files** (`strategies/orb_family.py`,
  `strategies/or5_retest.py`), found by an independent concurrent session
  while seeding a forward log for the `fail_fade` candidate (its first entry
  was at 19:53 ET — a time the 09:30-09:35/10:45 rule should never trade).
  1,431 of 2,681 `fail_fade` trades were impossible this way, carrying all of
  that candidate's apparent edge (PF 1.26 on the impossible trades vs. 0.93 on
  the rest). After the fix: the 900-combination ORB search drops from 14% of
  `fail_fade` profitable in both periods to **0 of 900**.
- **Not affected:** `strategies/ltf_sweep.py` (the live strategy) bounds its
  session on both sides, not by a one-sided minute check.
- **Guard:** a timestamp comparison against the end of the window, not a
  minute-of-day comparison alone. Test:
  `test_the_evening_before_cannot_break_a_range_that_has_not_formed`
  (`tests/test_orb_family.py`). **Rule for new code: any "after time X"
  selection on a trading date needs an upper bound or a timestamp comparison,
  never a bare minute-of-day inequality.**
- **Ported to this branch** from the independent session's fix (commit
  `a583d95`), since it is a correctness bug in files both branches share, not
  a strategy-parameter change.

## Sighting log

| date | class | where | count after |
|---|---|---|---|
| 2026-09-06 | 1 | `cfddcfc`, all detectors | 1 |
| 2026-09-09 | 2 | `7fa7f86`, engine fills | 1 |
| 2026-11-06 | 3 | named; 0 observed, 5 sites listed. `open_orders`/`open_positions` sites guarded by the round-trip proof (`bridge/roundtrip.py`, `python -m bridge.live --roundtrip`), ported here 2026-11-07. | 1 |
| 2026-11-06 | 4 | `docs/GO_LIVE.md` net/cash conflation (this session); README "PF 0.876" (concurrent session) | 2 |
| 2026-11-06 | 5 | `orb_family.detect` + `or5_retest`, found via a 19:53 forward-log entry on the concurrent session, ported here | 1 |

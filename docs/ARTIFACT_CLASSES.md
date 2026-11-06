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

**Sightings: 1 so far**, documented but not yet promoted to an assertion —
`bridge/preflight.py`'s `bar feed` check reports the array it got, and a human
reading the preflight output is the only thing standing between "no bars
because it's before market open" and "no bars because the contract ID is
wrong." This belongs in preflight as an assertion (e.g.: an empty bar feed
during a session that should have bars by the check time is a hard failure,
not a quiet zero) rather than a line in a markdown checklist. Not implemented
this session — flagged for the next one that touches `bridge/preflight.py`.

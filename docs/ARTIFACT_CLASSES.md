# ARTIFACT_CLASSES

Named ways this project has produced, or could produce, a number or an action
the real world wouldn't. A **sighting** is a real case found in code or
output. A **site** is a place the class can happen that hasn't been exercised
yet. When a new bug turns up, check first whether it belongs to a class below.
If it does, increment the count and look for siblings at the other sites.

---

## 1. Confirmation one bar early — self-consistent, so truncation tests pass

A detector stamps `confirmed_at` at the anchor bar's **open** when the pattern
needs that bar's **close**. An order "placed after confirmation" can then fill
inside the same 5-minute bar, using a close that hasn't printed yet.

- **Why the usual test misses it:** `test_no_lookahead.py` checks that
  truncating and re-running agrees with full-data-then-filter. A detector that
  is consistently one bar early agrees perfectly. It's consistently wrong.
- **Symptom:** fill rate near 100% (sfp_reversal).
- **Sightings: 1 incident, every detector at once** (cfddcfc). sfp_reversal OOS
  went +$197,038 → −$102,529. Combined account +$63,628 → −$83,929.
- **Guard:** `tests/test_confirmation_timing.py` tests the property itself
  (confirmation lands on a bar close), and `compare_strategies.py
  --hindsight-bars N` measures how much any edge depends on peeking.
- **Live sibling:** a feed stamped at bar close instead of open shifts every
  signal one bar. Guarded by preflight `bar timestamps` (newest bar < 60 s old
  ⇒ close-stamped ⇒ fail).

## 2. Marketable limit filled at a price the market had already left

A sell limit below the market, or a buy limit above it, fills immediately at
market. The engine filled it at the limit price instead.

- **Why it hid:** it was always on the first bar the order was live. The FVG
  retracement the model waits for had never happened; price was already
  through it at confirmation.
- **Sightings: 1 incident** (7fa7f86). LTF sweep 145 trades (114 dev, 31 OOS).
  ote_retracement's reported OOS −$353,924 was nearly all this. Fixed value
  +$8,605.
- **Guard:** `BacktestConfig.skip_marketable_entries=True`, recorded as
  `premise_failed` and kept in the fill rate. Pine `retraceLeft` does the same.
- **Remaining site:** the general fill model is still "touch = fill". Real limit
  orders queue. Biased in the backtest's favour, not removed.

## 3. A response that can't tell failure from a legitimate empty result

An API call that is wrong (bad contract id, wrong account, wrong data flag,
missing key) returns **success with an empty list** instead of an error. Code
reading "empty" as "nothing there" then acts on a false fact.

- **Named here, not in the repo before.** GO_LIVE line 321 and the 換月 section
  document one instance as a checklist note.
- **Sightings: 0 observed.** Nothing has ever hit a real server.
- **Sites:**

| site | what empty is read as | guarded? |
|---|---|---|
| `retrieve_bars` → `payload.get("bars") or []` | no bars | **Yes in preflight**: `bar_feed_checks` fails on empty. In the live loop, `stale_reason` → "no bars returned", so it doesn't trade. |
| `open_positions()` → `out.get("positions", [])`, then `ours()` filters on `contractId == cfg.contract_id` | **flat** | **No.** `day_done()` reads empty as finished. Exit 0 ⇒ the wrapper's `&& shutdown /h` runs. `flatten()` at 16:00 finds nothing to close. A wrong account id, a changed key name, or a contract-id string mismatch after a roll ⇒ **live position left with the machine off.** |
| `open_orders()` → `out.get("orders", [])` | nothing resting | **No.** Same path in `day_done()`. Worse at the entry deadline (`live.py` ~357): every outstanding order is journaled `no_longer_resting` and **not cancelled**, so an unfilled entry stays live after 15:30. |
| `accounts()` → `out.get("accounts", [])` | no accounts | Low impact (convenience lookup; docs say set the id explicitly). |
| `ours()` itself | not ours | Any format difference in `contractId` (int vs string — GO_LIVE already notes `retrieveBars` documents it as integer) empties every list it filters. |

- **Implemented 2026-11-06** (`bridge/roundtrip.py`, `python -m bridge.live
  --roundtrip`, GO_LIVE step 4b). Without a proof for this account + contract,
  `day_done()` never returns True (stops non-clean at the flat time, exit 1),
  and the deadline sweep treats an empty book as unreadable and cancels
  everything sent. Original design note: before the engine may treat an empty `open_positions` /
  `open_orders` as "flat", preflight on Practice has to prove the same
  call returns **non-empty** when something is known to exist. Place one
  resting order far from the market, require `ours(open_orders())` to contain
  its id, cancel it, require it gone. Do the same for a position at step 5.
  Until that has passed on this account and contract id, `day_done()` should
  not be allowed to return True. Re-run after every contract roll.

## 4. One claim, two parameterisations, no label

The same sentence in prose is backed by different settings in different
places, and neither place says which.

- **Sightings: 3** (found 2026-11-06, ledger R3/S4/S6):
  1. GO_LIVE 158 vs 189: same "one chain, $900, 2016–2026", LOCK_FIRST vs
     IMMEDIATE.
  2. README "PF 0.876": the payoff ratio, labelled as profit factor (true PF
     0.994).
  3. "−$2,135" vs "−$3,044" for "the strategy alone": $900 vs $500.
- **Guard:** `docs/FIGURES_LEDGER.md`. Every standing figure names its command,
  and commands name their parameters.

## 5. "After 09:35" by clock minute, when the trading date started the evening before

A CME trading date runs from 18:00 ET the day before. Bars from that evening
have `minutes_from_midnight` of 1080+, which is `>= 09:35`. So
`day[minutes >= RANGE_END_MINUTE]` puts the previous evening **first** in the
"after the range" set. The detector then lets 18:00–23:59 ET bars break or
fail a range that won't exist until the next morning: look-ahead.

- **Why nothing caught it:** it's self-consistent, like class 1. Truncation
  tests pass, and the unit tests only built same-morning bars.
- **Symptom:** entries at 18:00–23:59 ET for a rule that trades
  09:35–10:45. Found because the first forward-log row was at 19:53.
- **Sightings: 1 incident, 2 files** (`strategies/orb_family.py`,
  `strategies/or5_retest.py`). The fail_fade "survivor" was entirely this:
  1,431 of 2,681 trades impossible, PF 1.26 on those versus 0.93 on the rest.
  After the fix the ORB search has 0 of 900 profitable in both periods.
- **Not affected:** `strategies/ltf_sweep.py` (the live strategy) bounds the
  session on both sides (`>= session_start` and `<= exit_minute`).
- **Guard:** filter by timestamp after the range window, not by minute alone.
  Test: `test_the_evening_before_cannot_break_a_range_that_has_not_formed`.
  **Rule for new code: any "after time X" selection on a trading date needs
  an upper bound or a timestamp comparison.**

## Sighting log

| date | class | where | count after |
|---|---|---|---|
| 2026-09-06 | 1 | cfddcfc, all detectors | 1 |
| 2026-09-09 | 2 | 7fa7f86, engine fills | 1 |
| 2026-11-06 | 3 | named; 0 observed, 5 sites listed; open_orders/positions sites guarded by round-trip proof | 0 |
| 2026-11-06 | 4 | GO_LIVE 158/189, README PF, strategy-alone size | 3 |
| 2026-11-06 | 5 | orb_family.detect + or5_retest, found via a 19:53 forward-log entry | 1 |

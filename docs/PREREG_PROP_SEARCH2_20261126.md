# Prop search 2: more firms that pass on the corrected model — pre-registered 2026-11-26

**Question.** After the pre-live audit (`docs/AUDIT_PRE_LIVE_20261126.md`), three bot products qualify:
- LucidFlex 50K DLL ON $80.50;
- Topstep 50K Consistency;
- LucidDaily $85.40 (EOD evaluation, intraday funded).

Which other Malaysia-eligible products qualify once the loss limit is modelled the way each firm actually enforces it?

**Qualification rule** (unchanged from the audit, `scripts/audit_all_prop_20261126.py`). All three must hold:
- real net 2016-01..2026-10 ≥ 50% of Topstep 50K Standard on the same model and entry delay;
- coin-flip median ≥ $5,000 (200 flips, seed 1, via `scripts/radar_price.flip`);
- worst dip no worse than 1.5× Topstep's.

The friend's NQ orders are used unchanged (no strategy-parameter changes). Bot entry (delay 0) is used for firms that allow bots, and
3-minute manual entry for firms that require manual entry.

## Stages
**Stage A — every product already modelled but not re-priced by the audit.** Each is priced twice, all local:
- (i) real-time loss limit on open P&L, the conservative default (`realtime_mll=True`);
- (ii) end-of-day / closed P&L (`realtime_mll=False`).

Products, from `scripts/radar_models.py` and `scripts/radar_models2.py`, Malaysia-eligible or unverified only:
- TTP Instant 50K ($299, $499);
- TTP Prime 100K and 150K;
- LucidDirect 50K ($299, $499);
- DayTraders S2F 50K ($199, $399; official targets $3,500/$3,000);
- Tradeify Select Flex 50K;
- FTMO Futures Growth and Pro 50K;
- TFD Static Core and Pro;
- Blueberry Ascent 50K;
- FundedNext Rapid Pro 50K;
- Bulenox Momentum 50K;
- Traders Launch 100K and 200K.

A product **qualifies** only under the variant that matches its firm's own stated rule (Stage B). Until Stage B confirms, only variant (i)
counts. Variant (ii) only shows what the firm would be worth if its page confirms EOD.

**Stage B — each firm's loss-limit rule from its own pages**, for every product that qualifies under (ii) but not under (i). The pages are
fetched by GitHub Actions (`fetch_public.yml`, job `propsearch2_pages`) and searched for "unrealized", "intraday", "end of day",
"real time", "at any time". The verdict records the exact quote and URL. With no clear quote, variant (i) stands.

**Stage C — firms that allow bots and were never priced:**
- BluSky;
- Funded Futures Network;
- IQ Capital;
- Finotive Futures;
- firms founded or changed in 2026, found by search.

Each needs readable official rules before it is modelled. Malaysia eligibility is checked on the firm's own country list. No geoblock
circumvention.

**Outputs:**
- Stage A: `scripts/prop_search2_20261126.py` → `docs/jx_runs/prop_search2_20261126.txt` (re-run once; it must be identical);
- results recorded in this file, `docs/NOTES_JX.md`, `docs/FIGURES_LEDGER.md` and `docs/CANDIDATES.md`.

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

## Results, Stage A and addendum A1 (2026-11-26; `docs/jx_runs/prop_search2_20261126.txt`, re-run identical)
Bar: real ≥ $17,562, coin flip ≥ $5,000, dip ≥ −$6,088 (Topstep 50K Standard, real-time model, bot: $35,124, dip −$4,058).

**Stage A (prices as modelled):**
- Under the real-time model, only **DayTraders S2F 50K at $199** qualifies: $46,100, coin flip $20,996 (98%), dip −$4,975.
- Under the EOD model, TTP Instant 50K at $299 ($58,276) and LucidDirect 50K at $299 ($42,064) would also qualify.
- Everything else fails both ways: TTP Prime 100K/150K, TTP Instant at $499, Tradeify Select Flex, FTMO Futures Growth/Pro, TFD Static,
  Blueberry Ascent, FundedNext Rapid Pro, Bulenox, Traders Launch, DayTraders S2F at $399.

**Addendum A1 — at the prices third parties report (checkout pages unreadable here; unverified):**

| Product | Real-time model | EOD model | Verdict |
|---|---|---|---|
| DayTraders S2F 50K $342, DLL $1,250 (pause) | $32,826, flip $1,254, dip −$10,468 | $45,718, flip $17,406, dip −$6,840 | **fails** (EOD fails only on the dip, −$6,840 vs −$6,088) |
| DayTraders S2F 50K $570 (list) | $10,710 | $29,530, flip −$5,860 | fails |
| LucidDirect 50K $360.50 (code), CrossTrade $0 / $49 | $28,755 / $22,385, flips negative | $38,128 (flip $11,468, dip −$7,576) / $31,758 (dip −$9,192) | **fails** on the dip |
| LucidDirect 50K $520 (list) | $14,400 | $27,920, flip −$4,960 | fails |

TTP Instant 50K's official price is $499 (PROP_VERIFY), where it fails under both models.

**Stage B (each firm's own pages, `data/public/propverify/`):**
- Lucid: unrealized P&L does not count (EOD).
- FundedNext: floating losses breach the limit instantly (real-time).
- Blueberry: equity below the limit "at any point" fails (real-time; the quote may apply only to the trailing plan).
- TTP, DayTraders, Tradeify, TFD, Traders Launch, Bulenox: the drawdown level moves end-of-day, but no page states whether a breach is
  checked on live equity. They stay on the real-time model.

**Verdict:** no new product qualifies at real prices. The count stays at 3: LucidFlex 50K, Topstep 50K Consistency, LucidDaily $85.40.

**What would change the verdict:**
1. A real DayTraders S2F checkout price ≤ about $300. The model qualifies at $199 and fails at $342; the breakpoint is not yet computed.
2. DayTraders confirming that the loss limit ignores unrealized P&L.

Only Jx can read the checkout pages.

**Next (Stage C and beyond):** other account sizes of the qualifying firms (Topstep, Lucid), and bot-friendly firms never priced.

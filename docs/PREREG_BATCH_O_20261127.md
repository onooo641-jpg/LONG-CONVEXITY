# Batch O (#512–#514): physical commodity seasonals and a currency peg — pre-registered 2026-11-27, before data are fetched

Area plan: `docs/PLAN_BATCHES_O_Z.md`. Keyword check: no earlier PREREG tested grain harvests or currency pegs ("harvest" appears only
in #323, a funding trade).

**Gate (as F–N):** a named structural payer; free data; Malaysia-usable venue (US ETFs or futures via a broker such as IBKR); a genuine
time split. Each idea has about 1 event a year, so power is low, and that is stated.

| # | Idea (payer) | Exact rule | Stage 1 KILL if | Stage 2 PASS if |
|---|---|---|---|---|
| 512 | **Post-harvest recovery in corn and soybeans** (US farmers sell much of the crop at harvest, Sep–Nov, for cash and lack of storage; the selling ends and prices recover over winter) | Long an equal-weight CORN + SOYB basket (Teucrium ETFs, Yahoo daily adjusted) from the last close of October to the last close of the following February. Return − 0.1% | seasons starting 2011–2017: mean ≤ 0 | seasons 2018–2025: mean ≥ 2%, t ≥ 2 (8 seasons; low power) |
| 513 | **Post-harvest recovery in wheat** (US winter wheat is harvested June–July; same payer) | Long WEAT from the last close of July to the last close of October. Return − 0.1% | 2012–2018: mean ≤ 0 | 2019–2026: mean ≥ 2%, t ≥ 2 |
| 514 | **HKD peg, weak side** (the HKMA must buy HKD at 7.85 per USD, so the downside is capped; banks and carry traders push HKD to the weak side and the HKMA's buying drains liquidity until HIBOR rises and HKD recovers) | FRED DEXHKUS. Enter long HKD (short USD/HKD) the first day it closes ≥ 7.845 after 30 days below. Exit when it closes ≤ 7.80, or after 120 days. Return = −(exit/entry − 1) − carry − 0.01%. Carry = (US − HK 3-month rate) × days/365, with FRED OECD IR3TIB01 US/HK; if the HK series is missing, use HIBOR from FRED if available, else report no-carry and mark it | entries 1990–2012: mean ≤ 0 | entries 2013–2026: ≥ 4 events, mean ≥ 0.3% (net of carry), t ≥ 2 |

**Safe size for $/yr:**
- #512/#513: $45K.
- #514: $1.5M notional, the only way a 0.3% move matters. It is a pegged pair, so margin at a broker is a few %, but this is far
  above Jx's other sizes and is stated as such.

Stage 1 only kills; nothing passes early.

**Data job:** `ubatcho`. Yahoo CORN, SOYB, WEAT daily adjusted; FRED DEXHKUS, IR3TIB01USM156N, IR3TIB01HKM156N (whichever exists).

**Script/output:** `scripts/batch_o_20261127.py` → `docs/jx_runs/batch_o_20261127.txt`, re-run identical.

## Results (2026-11-27; `docs/jx_runs/batch_o_20261127.txt`, re-run identical)
| # | Verdict | Stage 1 | Stage 2 | $/yr |
|---|---|---|---|---|
| 512 corn + soybeans post-harvest | KILL | −2.41% (t −1.27, 7 seasons) | +3.77% (t 0.76, 8) | $1.7K |
| 513 wheat post-harvest | KILL | −6.08% (t −2.77, 7) | +0.39% (t 0.13, 8) | $173 |
| 514 HKD peg weak side | FAIL | 0 entries 1990–2012 (the weak side was not touched) | +0.21% (t 2.11, 8), before carry | $1.8K at $1.5M notional |

**Batch O verdict: 0 of 3.**
- #514 works the way the peg says it should: 7 of 8 entries since 2018 made money or nearly broke even. But the move is capped at
  0.6% and the HK interest rate series is missing on FRED, so carry could not be charged. HKD is weak exactly when HIBOR is below US
  rates, so carry would cut the +0.21% further. It is too small at any sensible size.
- A first draft of the script counted 1983–85 entries (around the peg's start) in Stage 1. It was corrected to the registered
  1990–2012 window before recording; the verdict was FAIL either way.

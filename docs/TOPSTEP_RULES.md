# Topstep rules, as published, retrieval date 2026-11-06

Primary sources only (Topstep's own help pages). Third-party trackers quoted
below for completeness, not treated as fact.

## Confirmed against Topstep's own pages, 2026-11-06

| Parameter | Value | Source |
|---|---|---|
| MLL on payout | Locked to $0 after each XFA payout, "regardless of where it was before" | help.topstep.com — What is the Maximum Loss Limit? |
| Profit since last payout | >= $0.01 net profit required before any payout after the first | help.topstep.com — Topstep Payout Policy |
| Winning days required | 5 | help.topstep.com — Topstep Payout Policy |
| Winning day minimum | $150 | help.topstep.com — Topstep Payout Policy |
| Profit split | 90/10 trader/firm | help.topstep.com — Topstep Payout Policy |
| Payout share per request | 50% of balance | help.topstep.com — Topstep Payout Policy |
| **Payout cap, 50K, standard** | **$2,000** | help.topstep.com — Topstep Payout Policy |
| Payout cap, 50K, consistency path | $3,000 | help.topstep.com — Topstep Payout Policy |
| $4,000 cap | Limited-time promo only: new Combine, Daily Loss Limit added at checkout. Not the standing rule. Status (active/expired) unverified from here. | help.topstep.com — Topstep Payout Policy |

`backtest/recycle.py`'s `XFARules` corrected to match: `payout_cap=2000.0`
(was `4000.0`, the promo figure, applied without the promo condition having
been checked).

## Unresolved: third-party claims of 2026 rule changes

Multiple third-party trackers (not Topstep's own pages) describe rule changes
during 2026, including an April 2026 payout change, a "$5K first cap," and a
"100/90 split." None of these match what Topstep's own help pages state as of
this retrieval. Not reconciled here — could not determine from this session
whether the third-party pages are stale, the help pages are stale, or the
rule changed more than once during the year.

This matters beyond the model's current parameters: the 11-year backtest
(2016-01-01 to data end) assumes the rulebook is constant throughout, and
2026 — the year third parties say it changed — is roughly the final ~1/11 of
that window (~9%, not 24% as first estimated; data end is late October 2026,
so the year in question is partial). Re-check before buying if this gap
widens or the discrepancy is still unresolved.

## How this file is meant to be used

Before the account purchase, re-pull `payout_cap` and the two lock rules
directly from Topstep's live pages again — rules move, and this file is a
snapshot, not a subscription. If any parameter in `XFARules` disagrees with
the live page the way `payout_cap` did, fix the dataclass default, not just
this file, and re-run `scripts/recycling_report.py`.

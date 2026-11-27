# Topstep Starter Challenge ($10) as the payout/enforcement test — how likely does the bot reach the $100 payout? Pre-registered 2026-11-27

**Rules (official, help.topstep.com 18482122, rendered 2026-11-27 by Actions, `data/public/propverify/expand_lp_topstep_com_en_articles_18482122.json`):**
- $10 one time, first-time Topstep customers only, 1 per trader;
- two rounds from $0, each must reach **+$100** before the **$100 static** Maximum Loss Limit;
- max **1 micro**; no daily loss limit; no consistency;
- **2 free resets in the Challenge Round only**, none in the Payout Round; fixed **$100** payout, once;
- **90 days per round**; closes after 30 days with no trades;
- Tier 1 news windows set MNQ to 0 contracts (FOMC 12:55–13:05 and 13:25–13:35 CT fall inside the bot's session).

**Also official** (TopstepX API page 11187768, same render):
- custom bots are allowed via the API, subject to platform rules and the HFT ban;
- API access costs **$14.50/month**, separately;
- VPS, VPN and remote servers are prohibited;
- so the test costs $10 + $14.50 = **$24.50**.

**Question.** If the bot runs the Starter Challenge, how often does it reach the payout, and how long does it take?

**Data/model.**
- Trades: friend's NQ trades (`radar_price.trades(orders, bars, 0)`, corrected engine), scaled to 1 micro (`k = min(1, 1/contracts)`,
  as `prop_search2_c2.challenge`). Commission per micro kept; the loss limit is judged on worst open P&L (`mae_usd`).
- Starts: 118 monthly starts, 2016-01 to 2025-10 (first trade on/after the 1st).
- Round 1: up to 3 attempts (1 + 2 resets), each within 90 days of its round start (a reset does not restart the clock).
  This is an assumption; the page does not say.
- Round 2 begins with the next trade after passing round 1: one attempt, 90 days.
- FOMC-window trades are not removed (reported limitation).

**Report:**
- share of starts reaching the payout;
- median days to payout;
- share failing in round 1 / round 2 / by expiry;
- expected net per start ($100 × P(payout) − $24.50).

**Decision rule (set now):** recommend the Starter Challenge as the first live step if P(payout) ≥ 30%. Otherwise recommend going
straight to one Topstep 50K as the payout test. This is a test-design choice, not a profit claim.

**Script/output:** `scripts/starter_challenge_20261127.py` → `docs/jx_runs/starter_challenge_20261127.txt`, re-run identical.

## Result (2026-11-27; `docs/jx_runs/starter_challenge_20261127.txt`, re-run identical)
- **Outcomes (118 monthly starts):**
  - payout **34 (29%)**;
  - round 2 failed 46 (39%);
  - round 1 expired 23 (19%);
  - round 1 failed 13 (11%);
  - round 2 expired 2 (2%).
- Median 16 days to payout. Expected net per start +$4.31.
- At 1 micro, a losing trade costs a median $35.74 and a winner pays $32.01, so ±$100 is only about three trades either way.
  The single-attempt Payout Round is where most starts fail.
- **Decision by the registered rule: P(payout) 29% < 30%, so go straight to one Topstep 50K as the payout test.**
- The Starter Challenge stays an optional $24.50 check of the bot on a real Topstep account. It would reach a payout about 3 times
  in 10.

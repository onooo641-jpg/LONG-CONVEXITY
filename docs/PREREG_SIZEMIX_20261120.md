# Bigger Topstep accounts inside the market mix — 2026-11-20 (CANDIDATES #63)

Written and committed **before** any run. Account size is a deployment choice; strategy unchanged.

## Why
150K earns ~2.1× a 50K per slot (account-size test, Z1) but was set aside for needing ~2.8× the cash.
The market mix (PREREG_MARKETMIX, part 2) cut cash needs by ~60–69%, so bigger accounts may now fit.

## Setup
- 5 Topstep accounts: 3 NQ / 1 ES / 1 YM, anti-hedge filter as PREREG_MARKETMIX part 2.
- Sizes 50K / 100K / 150K, Standard path, rules exactly as `scripts/account_size_test.py`
  (targets 3,000/6,000/9,000; MLL 2,000/3,000/4,500; 50/100/150 micros; $49/$99/$149 monthly and reset;
  payout caps $2,000/$3,000/$5,000; 100K/150K funded ladders = 50K ladder ×2/×3, **assumed**).
- Risk per trade 0.45 × MLL in every market ($900 / $1,350 / $2,025).
- Platform cost: one ProjectX API subscription ($14.50/mo). 2016-01 .. 2026-10.

## Reading (decided now)
A bigger size is **worth switching to** if its net is at least 30% above the 50K mix AND its cash on hand
is no more than $15,336 (what the all-NQ 5×50K plan already needed). Also reported: net per $ of cash.

Command: `uv run python scripts/sizemix_20261120.py`

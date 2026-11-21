# Gold carry: hold PAXG, short the Hyperliquid PAXG perp (#216) — 2026-11-21

Written before the PAXG funding history is fetched (it comes with the hedged batch, `hedged_hlfunding.parquet`).
Mechanism: leveraged longs on HL pay funding to shorts; holding tokenised gold (PAXG, redeemable for LBMA gold) and shorting the perp is
delta-neutral and collects that funding. Rule: always on, 3× short → capital = spot + 1/3 margin; return on capital = funding received /
1.333; costs 0.1% in + 0.1% out once (negligible) plus PAXG's 0.02% transfer fee. Window: 2024-11-01..2026-10-31, or the first PAXG funding
day if later; halves by its own history. Stage 1 (2026-08..10) KILL < 4%/yr; PASS ≥ 8%/yr both halves and ≥ 180 days.
Malaysia: PAXG is an Ethereum token (permissionless); HL unverified. Limits: PAXG issuer risk, perp/spot basis at exit.
Command: `uv run python scripts/goldcarry_20261121.py | tee docs/jx_runs/goldcarry_20261121.txt`

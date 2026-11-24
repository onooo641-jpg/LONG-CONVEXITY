# #367 Who are CoW's paid solvers — are any of the successful newcomers small teams? (non-prop) — 2026-11-24

**Why.** Jx: "if every single one of them is a huge establishment there isn't any way for us to compete." #364/#365 showed new solvers
earning well (11 genuine 2024–25 entrants; 5 still ≥ $15K/yr in 2026), but payout addresses do not say who is behind them. Written before
the identity data below are fetched.

**Data (free).** (1) CoW's VouchRegister contract logs (mainnet `0xb422f2520b0b7FD86f7DA61b32Cc631A59ed7E8F`; L2s
`0xAAA4De096D02AE21729aA31D967E148D4e3Ae501`): each vouch links a solver's submission address, its **bonding pool**, and its COW
**reward address** (the payout recipients in #361/#364). (2) The bonding pools' own funding (a full own pool needs $500K + 1.5M COW; a
reduced pool $50K + 500K COW; the CoW DAO pool is the KYC route for teams without capital). (3) Names: CoW's solver-competition API (v1
returns solver names), CoW's public Solvers page, CoW forum posts (bonding-pool CIPs, solver introductions), news.

**Classification rule (fixed).** Each payout recipient that earned ≥ $15,000/yr (annualised) in 2026-01-01..2026-10-31, plus the 11
genuine 2024–25 entrants, gets:
- **Pool type**: CoW DAO pool / reduced own pool / full own pool / unknown (no vouch found).
- **Size class**: *Established* = runs a full own bonding pool, OR is publicly an exchange, DEX aggregator, market maker or trading firm
  (named source); *Small/independent* = vouched by the CoW DAO pool (or a reduced pool) AND no public evidence of being an exchange,
  aggregator, market maker or trading firm; *Unknown* otherwise.

**Question and answer rule.** "Can small teams compete?" = **yes, with evidence** if ≥ 3 *Small/independent* recipients earned ≥ $15,000/yr
in 2026; **no evidence** if 0; **thin** if 1–2. Reported with each recipient's 2026 earnings, pool, name and source. This is descriptive
(it does not test our solver).

**Commands.** fetch: Actions job `cow367`; analysis: `uv run python -m scripts.cow_who_20261124 | tee docs/jx_runs/cow_who_20261124.txt`
(re-run once; must be identical). **Limits.** A vouch names the pool, not the people; public identity is from named sources only;
teams can hide behind generic names.

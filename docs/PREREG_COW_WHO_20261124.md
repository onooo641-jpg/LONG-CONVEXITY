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

### Results (2026-11-24; `docs/jx_runs/cow_who_20261124.txt`, identical on re-run)
**Data actually used.** CoW's official solver registry (`cms.cow.fi/api/solvers`, 89 solvers, 112 payout addresses, fetched by Actions run
45344455035): name, organization, bonding pool (incl. whether reduced), service-fee flag and payout address per network. 28 of the 29
recipients examined matched by payout address. The VouchRegister log pull was partial (mainnet 100 logs; L2 explorers answered 403, the
BNB public RPC refused) and the v1 solver-competition API returned 404, so pool type comes from the registry. Identity evidence: CoW's
registry fields plus named web sources (listed per solver in the script).

| Class (2026 ≥ $15K/yr) | Recipients | 2026 rewards | Share of all 2026 rewards | Range per solver |
|---|---|---|---|---|
| Established (exchange / aggregator / market maker / trading firm / CoW-run / full own pool) | 10 | $2.49M/yr | 29% | $18.6K–$621K |
| Small/independent (CoW DAO or reduced pool, no public evidence of a large firm) | **6** | $0.81M/yr | 9% | **$23.4K–$386K** |
| Unknown | 7 | $5.30M/yr | 61% | $21K–$4.38M |

Small/independent: **Fractal $385,541/yr** (reduced own pool; 2024 entrant), Portus $184,195 (reduced pool; built by the Furucombo DeFi-tool
team), Wraxyn $115,774, Arc $61,635, Trusted Volumes $40,384 (2025 entrant), Arctic Bastion $23,405 (all CoW DAO pool).
Established include Tsolver (Tokka Labs, prop-trading firm, $621K), Kipseli (Kyber, $619K), Sector Finance ($538K; a small DeFi protocol
whose budget mentions market-making systems — classed Established under the strict rule), Helixbox, BitGet, OKX, Barter's listed address,
Nexroute (a DEX-routing startup — also strict), and CoW/Gnosis-run solvers. The largest recipient ($4.38M/yr, 50% of 2026 rewards) is not
in the registry; Barter publicly targets > 50% share and is the reported #1, so it is probably Barter (inference, not verified).

**Answer (registered rule): YES, with evidence** — 6 recipients without public signs of being large firms earned ≥ $15K/yr in 2026
($2K–$32K per month). **Limits:** "no public evidence" is not proof of being small (some may be anonymous professionals); Portus comes from
an existing DeFi company; small teams together took only 9% of rewards; the strict rule also pushed two small projects (Sector Finance,
Nexroute) into "Established".

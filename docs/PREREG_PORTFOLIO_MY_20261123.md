# Malaysia-eligible multi-firm portfolio (ranking, no pass/fail) — 2026-11-23

Question (Jx: "there must be something that matches or beats Topstep"): what do the Malaysia-eligible, bot-allowed products that meet the flag
rule earn together? Same trades on every account (friend's NQ trades 2016-01..2026-10, $900 risk), so accounts within and across firms move
together (N accounts = N× the swings, not N independent bets). Inputs: frozen baseline (`docs/radar/prop_assumptions_20261122.csv`) and
verified rules (`docs/PROP_VERIFY_20261122.md`): Topstep 50K Consistency path ($49/mo), TTP Futures Prime 50K ($99, reset $79), DayTraders EOD
50K ($105 + $5 on pass, $105 replacement), LucidDaily 50K EOD (list $122 and promo $85.40), LucidFlex 50K DLL ON ($80.50, reset $80).
Output: per product and combined (1 account each; 5 each, the per-firm caps: Topstep 5 XFAs, Lucid 5 funded, TTP copy to 5, DayTraders 5 EOD):
net 2016–26, per year, average and last-36-month per month, share of months ≥ $300, worst 12 months, worst dip of the combined cash curve.
Command: `uv run python -m scripts.portfolio_my_20261123 | tee docs/jx_runs/portfolio_my_20261123.txt`.

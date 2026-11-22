# Sweep 3: capped-capacity, high-% mechanisms (#322–#326) — 2026-11-22

Written and committed before any sweep-3 data is used (fetch job `sweep3`; #323 uses `data/public/hl_funding.parquet`, already in the repo but
not yet analysed for this rule). Aim (Jx): non-prop mechanisms that could reach ≥ 50%/yr because large capital cannot follow (Topstep shape: high
%, capped dollars). Bars: Stage 1 kill-only < 25%/yr. Stage 2 PASS as PREREG_SMALLCAP addendum 3: both halves ≥ 50%/yr, costs ×2 ≥ 30%,
worst drawdown ≥ −30%.

| # | mechanism | why capacity is capped | data | Stage 1 rule |
|---|---|---|---|---|
| 322 | **Thin-venue market making hedged on Hyperliquid**: quote on dYdX, where spreads were 23–55 bps in batch 7; hedge instantly on HL (spreads 0.6 bps) | flow on thin venues is small | dYdX indexer trades (public) + HL 1m candles, last ~3 days | for every dYdX taker trade, the maker side earns (HL mid 5 min later − trade price) × maker sign, minus a 2-bps HL hedge and a 1-bp dYdX maker fee. Assume we capture 20% of each thin pair's flow on $5K of capital. KILL if annualised < 25% or the mean edge per $ ≤ 0 |
| 323 | **Hedged harvest of extreme funding on HL small caps** (long spot on a DEX, short HL perp) | open-interest caps, thin spot liquidity | `hl_funding.parquet` (2024-01..2026-11, 155 coins) | enter a coin when its trailing-24h funding > 100%/yr, exit when < 20%/yr; ≤ 5 slots, $1K each; costs 1.0% round trip on DEX spot + 0.1% on the perp; position capped at 5% of the coin's... (no OI data: capacity reported, not modelled). KILL if 2026-08..10 < 25%/yr |
| 324 | **Counterparty and option vaults on newer venues** (perp-DEX LP vaults other than Gains/HLP; DeFi options vaults) | vault size | DefiLlama pools (category / project match) + charts | monthly top-5 by trailing 30-day APY among vaults ≥ $500K; APY-based (labelled: APY may omit trader P&L, the #225 lesson) and price-based where the vault token is priced by DefiLlama coins. KILL if APY-based < 25%/yr (price-based required at Stage 2) |
| 325 | **Small isolated lending markets at high utilisation** (stablecoin supply side; Morpho/Euler/Silo-type) | market size | DefiLlama pools (lending, stablecoin, TVL $100K–$5M) + charts | monthly top-10 stable lending pools by trailing 30-day supply APY; $1,500 each; −50% if TVL falls > 70% in 7 days. KILL if < 25%/yr |
| 326 | Odd-lot tender offers (US; buy < 100 shares, tender at the offer price) | odd-lot priority caps size | SEC EDGAR SC TO-I filings | **parked**: EDGAR asks automated clients for a contact e-mail in the user agent (privacy rule: not sent without Jx's approval) |
Malaysia (Stage 0): DeFi front-ends (assumed not geoblocked); dYdX v4 front-end restricts some countries (Malaysia **not verified**).
Command: `uv run python -m scripts.sweep3_20261122 | tee docs/jx_runs/sweep3_20261122.txt`.

## Result #323 (2026-11-22; `docs/jx_runs/sweep3_20261122.txt`, identical on re-run): KILL
−1.36%/yr in 2026-08..10 (4 round trips). Extreme funding has nearly disappeared: coins above 100%/yr trailing-24h funding averaged 1.3 a day
in 2024, 0.1 in 2025 and 0.1 in 2026. #322/#324/#325 pending the sweep-3 fetch.

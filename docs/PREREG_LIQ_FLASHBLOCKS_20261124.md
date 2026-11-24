# PREREG: Base flashblocks capability probe on the free public endpoint (candidate #100, "faster data" lever) — written 2026-11-24 before running

Question: does the free `https://mainnet.base.org` endpoint serve the `pending` block (Base flashblocks, 200 ms pre-confirmations), so a watcher could see state ~1.8 s earlier than the 2 s block? Capability only; no profit claim.
Method (descriptive): for 120 s, every ~150 ms call `eth_getBlockByNumber("pending", false)` and `eth_getBlockByNumber("latest", false)`; record per call: pending number, tx count, hash/timestamp. Also one `eth_getBalance(addr,"pending")` check is NOT made (no addresses used).
Reading rules (fixed now):
- SUPPORTED: in >= 20% of polls the pending block number equals latest+1 AND, within a single pending block number, the tx count was seen to increase at >= 3 distinct values across polls (sub-block updates exist).
- NOT SUPPORTED: otherwise (pending equals latest, or errors/rate-limit in > 50% of polls => INCONCLUSIVE, rate-limited).
Output: `docs/jx_runs/liq_flashblocks_20261124.txt`; ledger row FB1. A SUPPORTED result only shows the data path exists; whether it yields wins vs incumbents is untested and cannot be tested without paid/live infrastructure (Jx-only).
Costs: none. Secrets: none.

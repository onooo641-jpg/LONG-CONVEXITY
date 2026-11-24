"""#367 Who are CoW's paid solvers? (docs/PREREG_COW_WHO_20261124.md)

    uv run python -m scripts.cow_who_20261124 | tee docs/jx_runs/cow_who_20261124.txt
Payout addresses (data/public/solverrelay_cow.parquet) are matched to CoW's official solver registry (cms.cow.fi/api/solvers, fetched by
Actions job cow367 into data/public/cow367_pages.json): name, organization, bonding pool, service-fee flag, payout address per network.
Public identity evidence (below) comes from named sources found on 2026-11-24.
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from scripts.cow_gate_20261124 import TS, flags, load

PUB = Path(__file__).resolve().parent.parent / "data" / "public"
BAR = 15_000.0
COW_POOL = "0x5d4020b9261f01b6f8a45db929704b0ad6f5e9e6"

# Public evidence of being an exchange, DEX aggregator, market maker or trading firm (rule in the pre-registration). Name -> (kind, source).
ESTABLISHED = {
    "Tsolver": ("proprietary trading / market-making firm (Tokka Labs, Singapore)", "partners.circle.com/partner/tokka-labs; tokkalabs job postings"),
    "Kipseli": ("DEX aggregator (organization 'Kyber' in CoW's registry)", "cms.cow.fi registry"),
    "Barter": ("routing engine / aggregator company, #1 CoW solver", "blockworks.co/news/barter-buys-rival-solver-codebase"),
    "BitGet": ("exchange", "cms.cow.fi registry name"),
    "OKX": ("exchange", "cms.cow.fi registry name"),
    "0x API": ("DEX aggregator", "cms.cow.fi registry (organization 0x)"),
    "Balancer API": ("DEX", "cms.cow.fi registry (organization Balancer)"),
    "Baseline": ("CoW/Gnosis-run solver", "cms.cow.fi registry (organization Gnosis DAO)"),
    "Quasimodo": ("CoW/Gnosis-run solver", "cms.cow.fi registry (organization Gnosis DAO)"),
    "Helixbox": ("bridge company supplying liquidity to order-flow venues", "rootdata.com/projects/detail/Helixbox"),
    "Sector Finance": ("DeFi protocol whose budget describes 'solving and market-making systems' (small: ~$60K TVL)",
                       "gl.app sectorfinance.eth 4Q25 budget proposal; defillama.com/protocol/sector-finance"),
    "Nexroute": ("DEX routing product ('routes swaps across 500+ DEX liquidity sources')", "nexroute-website-3m4.pages.dev"),
}


def registry():
    p = json.loads((PUB / "cow367_pages.json").read_text())
    d = json.loads(p["https://cms.cow.fi/api/solvers?populate=*&pagination[pageSize]=200"]["raw"])
    by_payout = {}
    for it in d["data"]:
        a = it["attributes"]
        pools = [(x["attributes"]["name"], bool(x["attributes"]["isReducedBondingPool"]), str(x["attributes"]["address"]).lower())
                 for x in (a.get("solver_bonding_pools") or {}).get("data", [])]
        for n in (a.get("solver_networks") or {}).get("data", []):
            pa = str(n["attributes"].get("payoutAddress") or "").lower()
            if pa:
                by_payout.setdefault(pa, {})[a["displayName"]] = {"org": a.get("organization") or "", "pools": pools,
                                                                  "fee": a.get("isServiceFeeEnabled"), "web": a.get("website") or ""}
    return len(d["data"]), by_payout


def pool_type(info):
    pools = [p for v in info.values() for p in v["pools"]]
    if any(p[2] == COW_POOL for p in pools):
        return "CoW DAO pool"
    if any(p[1] for p in pools):
        return "reduced own pool"
    if pools:
        return "full own pool"
    if any(v["fee"] for v in info.values()):
        return "CoW DAO or reduced pool (service-fee flag)"
    return "unknown"


def classify(info, ptype):
    names = list(info)
    est = [n for n in names if n in ESTABLISHED]
    if ptype == "full own pool":
        return "Established", "runs a full own bonding pool ($500K + 1.5M COW)"
    if est:
        return "Established", "; ".join(f"{n}: {ESTABLISHED[n][0]} [{ESTABLISHED[n][1]}]" for n in est)
    if ptype in ("CoW DAO pool", "reduced own pool", "CoW DAO or reduced pool (service-fee flag)"):
        return "Small/independent", "no public evidence of being an exchange, aggregator, market maker or trading firm"
    return "Unknown", "pool and identity unknown"


def main():
    n_reg, reg = registry()
    df = load()
    g = flags(df)
    d26 = df[(df["day"] >= TS("2026-01-01")) & (df["day"] <= TS("2026-10-31"))].groupby("to")["usd"].sum() * 365 / 304
    tot26 = float(d26.sum())
    genuine = set(g[(g["first"] >= TS("2024-03-01")) & (g["first"] <= TS("2025-10-31")) & (~g["flag"])].index)
    rec = sorted(set(d26[d26 >= BAR].index) | genuine, key=lambda a: (-d26.get(a, 0.0), a))
    print(f"===== #367 Who are CoW's paid solvers? Registry entries {n_reg}; payout addresses in the registry {len(reg)}")
    print(f"  recipients examined {len(rec)} (2026 >= $15K/yr: {int((d26 >= BAR).sum())}; genuine 2024-25 entrants: {len(genuine)}); "
          f"found in the registry {sum(1 for a in rec if a in reg)}")
    rows = []
    for a in rec:
        info = reg.get(a, {})
        pt = pool_type(info) if info else "unknown"
        cls, why = classify(info, pt) if info else ("Unknown", "payout address not in CoW's registry")
        rows.append({"addr": a, "names": ", ".join(info) or "?", "pool": pt, "klass": cls, "why": why, "usd26": float(d26.get(a, 0.0)),
                     "genuine": a in genuine})
    r = pd.DataFrame(rows)
    for x in r.itertuples():
        print(f"  ${x.usd26:>10,.0f}/yr  {x.names[:44]:<44} {x.pool:<42} {x.klass:<17} {'(2024-25 entrant) ' if x.genuine else ''}{x.why[:150]}")
    big = r[r["usd26"] >= BAR]
    print("  2026 earnings by class (recipients >= $15K/yr):")
    for c in ("Established", "Small/independent", "Unknown"):
        s = big[big["klass"] == c]
        print(f"    {c:<17} {len(s):>2} recipients, ${s['usd26'].sum():>12,.0f}/yr ({s['usd26'].sum() / tot26:.0%} of all 2026 rewards)"
              + (f"; range ${s['usd26'].min():,.0f}-${s['usd26'].max():,.0f}" if len(s) else ""))
    small = big[big["klass"] == "Small/independent"]
    n = len(small)
    ans = "YES, with evidence" if n >= 3 else ("THIN" if n >= 1 else "NO evidence")
    print(f"  ANSWER (registered rule: >= 3 Small/independent recipients earning >= $15K/yr in 2026): {ans} ({n}: "
          + ", ".join(f"{x.names} ${x.usd26:,.0f}" for x in small.itertuples()) + ")")


if __name__ == "__main__":
    main()

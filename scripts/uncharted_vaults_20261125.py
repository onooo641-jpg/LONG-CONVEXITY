"""#383 U-T1: launch-phase perp-DEX house vaults, first 12 months vs months 13-24 (docs/PREREG_UNCHARTED_20261125.md).

    uv run python -m scripts.uncharted_vaults_20261125 | tee docs/jx_runs/uncharted_vaults_20261125.txt
Reads data/public/uncharted_383_{prices.parquet,ids.json,hlp.json,pools.json,charts.parquet} (Actions job u383vaults) and
data/public/hl_funding.parquet. Primary: vault-token prices (DefiLlama), hedged weekly with non-negative least squares on SOL/ETH/BTC
(as #363; stable vaults get ~zero hedge). Vault filter fixed before the data: CoinGecko name matches "liquidity provider", "LP",
"vault" or "perp" and the series has >= 400 days. Secondary context: DefiLlama APY of Derivatives-category pools.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

from scripts.jlp_20261123 import nnls_demeaned

PUB = Path(__file__).resolve().parent.parent / "data" / "public"
HEDGE = {"SOL": "solana", "ETH": "ethereum", "BTC": "bitcoin"}
TAKER, VAULT_COST, LEV, LOOK, MIN_LOOK = 0.00045, 0.003, 3.0, 60, 14
NAME_RE = re.compile(r"liquidity provider|\bLP\b|vault|perp", re.I)


def ann(r):
    r = r.dropna()
    if len(r) < 30:
        return np.nan
    return float((1 + r).prod() ** (365 / len(r)) - 1)


def hedged_returns(v, P, F):
    """Daily hedged return on capital for vault price series v (index = day)."""
    R = pd.concat([v.rename("V"), P], axis=1).loc[v.first_valid_index():].pct_change(fill_method=None).dropna(subset=["V"])
    R = R.fillna(0.0)
    beta = pd.DataFrame(0.0, index=R.index, columns=list(HEDGE))
    cur = np.zeros(len(HEDGE))
    for i, d in enumerate(R.index):
        if d.weekday() == 0 and i >= MIN_LOOK:
            win = R.iloc[max(0, i - LOOK):i]
            cur = nnls_demeaned(win["V"].to_numpy(), win[list(HEDGE)].to_numpy())
        beta.iloc[i] = cur
    Fd = F.reindex(R.index).fillna(0.0)
    turn = beta.diff().abs().sum(axis=1).fillna(0.0)
    h = R["V"] - (beta * R[list(HEDGE)]).sum(axis=1) + (beta * Fd).sum(axis=1) - TAKER * turn - VAULT_COST / 365
    return h / (1 + beta.sum(axis=1) / LEV), beta


def main():
    print("===== #383 U-T1 launch-phase perp-DEX house vaults (first 12 months vs months 13-24)")
    px = pd.read_parquet(PUB / "uncharted_383_prices.parquet")
    ids = json.loads((PUB / "uncharted_383_ids.json").read_text())
    px["day"] = pd.to_datetime(px["t"], unit="s", utc=True).dt.round("D")
    W = px.drop_duplicates(["id", "day"], keep="last").pivot(index="day", columns="id", values="price").sort_index()
    W = W.reindex(pd.date_range(W.index.min(), W.index.max(), freq="D")).ffill(limit=3)
    P = pd.DataFrame({c: W[g] for c, g in HEDGE.items()})
    f = pd.read_parquet(PUB / "hl_funding.parquet")
    f = f[f["coin"].isin(list(HEDGE))].copy()
    f["day"] = pd.to_datetime(f["time"], unit="ms", utc=True).dt.normalize()
    F = f.groupby(["day", "coin"])["rate"].sum().unstack().reindex(columns=list(HEDGE))
    print(f"  vault-like CoinGecko ids fetched: {len(ids)}; hedge funding from {F.index.min().date()} (zero before)")
    rows = []
    for g, m in sorted(ids.items()):
        if g not in W or not NAME_RE.search(m.get("name") or ""):
            continue
        v = W[g].dropna()
        if len(v) < 400:
            continue
        h, beta = hedged_returns(W[g].loc[v.index[0]:v.index[-1]], P.loc[v.index[0]:v.index[-1]], F)
        y1, y2 = h.iloc[:365], h.iloc[365:730]
        rows.append({"id": g, "symbol": m.get("symbol"), "first": v.index[0].date(), "days": len(v), "y1_hedged": ann(y1),
                     "y2_hedged": ann(y2) if len(y2) >= 180 else np.nan, "y1_unhedged": ann(v.pct_change().iloc[1:366]),
                     "avg_beta": float(beta.iloc[:365].sum(axis=1).mean())})
    # HLP from Hyperliquid's own history (account value + cumulative PnL)
    hlp = json.loads((PUB / "uncharted_383_hlp.json").read_text() or "{}")
    port = dict((k, v) for k, v in hlp.get("portfolio", []))
    if "allTime" in port:
        av = pd.Series({pd.Timestamp(int(t), unit="ms", tz="UTC"): float(x) for t, x in port["allTime"]["accountValueHistory"]})
        pn = pd.Series({pd.Timestamp(int(t), unit="ms", tz="UTC"): float(x) for t, x in port["allTime"]["pnlHistory"]})
        d = pd.DataFrame({"av": av, "pnl": pn}).sort_index()
        r = (d["pnl"].diff() / d["av"].shift()).dropna()
        r = r[d["av"].shift().reindex(r.index) > 1e6]
        start = r.index[0]
        y1 = r[r.index < start + pd.Timedelta(days=365)]
        y2 = r[(r.index >= start + pd.Timedelta(days=365)) & (r.index < start + pd.Timedelta(days=730))]
        rows.append({"id": "HLP (Hyperliquid)", "symbol": "hlp", "first": start.date(), "days": (r.index[-1] - start).days,
                     "y1_hedged": float((1 + y1).prod() - 1), "y2_hedged": float((1 + y2).prod() - 1), "y1_unhedged": np.nan,
                     "avg_beta": 0.0})
        print(f"  HLP: {len(r)} history points (sparse: allTime history is coarse), first {start.date()}")
    t = pd.DataFrame(rows)
    pd.set_option("display.width", 250)
    print("\n  vault-token series (name filter + >= 400 days); returns per year on capital, hedged:")
    print(t.to_string(index=False, float_format=lambda x: f"{x:8.3f}"))
    n = int(t["y1_hedged"].notna().sum())
    med = float(t["y1_hedged"].median())
    both = t.dropna(subset=["y1_hedged", "y2_hedged"])
    beat = int((both["y1_hedged"] > both["y2_hedged"]).sum())
    print(f"\n  vaults with a first-year figure: {n}; median first-year hedged return {med:.1%}; first year beats year 2 in {beat} of {len(both)}")
    # secondary: DefiLlama APY of Derivatives-category pools
    pj = json.loads((PUB / "uncharted_383_pools.json").read_text())
    der = {p["pool"]: p for p in pj["pools"] if (pj["protocols"].get(p["project"]) or {}).get("category") == "Derivatives"}
    ch = pd.read_parquet(PUB / "uncharted_383_charts.parquet")
    ch = ch[ch["pool"].isin(der)].copy()
    ch["day"] = pd.to_datetime(ch["ts"], utc=True).dt.normalize()
    ap = []
    for pool, g in ch.groupby("pool"):
        g = g.sort_values("day")
        if len(g) < 400 or g["tvlUsd"].max() < 1e6:
            continue
        s = g["day"].iloc[0]
        a1 = g[g["day"] < s + pd.Timedelta(days=365)]["apy"].mean()
        a2 = g[(g["day"] >= s + pd.Timedelta(days=365)) & (g["day"] < s + pd.Timedelta(days=730))]["apy"].mean()
        p = der[pool]
        ap.append({"project": p["project"], "chain": p["chain"], "symbol": p["symbol"], "first": s.date(), "apy_y1": a1, "apy_y2": a2,
                   "tvl_max_m": g["tvlUsd"].max() / 1e6})
    a = pd.DataFrame(ap)
    if len(a):
        a = a.sort_values("first")
        b2 = a.dropna(subset=["apy_y1", "apy_y2"])
        print(f"\n  context, DefiLlama APY (fees/rewards; excludes trader P&L and price): Derivatives pools with >= 400 days and >= $1M TVL: "
              f"{len(a)}; median APY year 1 {a['apy_y1'].median():.1f}%, year 2 {b2['apy_y2'].median():.1f}%; "
              f"year 1 > year 2 in {int((b2['apy_y1'] > b2['apy_y2']).sum())} of {len(b2)}")
        print(a.to_string(index=False, float_format=lambda x: f"{x:8.1f}"))
    kill = not (med >= 0.20)
    print(f"\n  STAGE 1 VERDICT: {'KILL (median first-year hedged return < 20%/yr)' if kill else 'survives (kill-only)'}")
    if not kill:
        pas = n >= 4 and med >= 0.40 and beat >= 3
        print(f"  forward-trial bar (median >= 40% across >= 4 vaults and year 1 beats year 2 in >= 3): {'met' if pas else 'not met'}")


if __name__ == "__main__":
    main()

"""Data for docs/PREREG_FALLBACK_20261121.md (#204, #205). Runs on GitHub Actions.

    python scripts/fetch_fallback.py
Writes data/public/fallback_stable_charts.parquet, fallback_stable_pools.parquet, fallback_hlp.parquet.
"""
from __future__ import annotations

import json
import time
import urllib.request
from pathlib import Path

import pandas as pd

OUT = Path(__file__).resolve().parent.parent / "data" / "public"
UA = {"User-Agent": "long-convexity-research/1.0", "Accept": "application/json"}


def get(url, body=None, tries=4):
    for k in range(tries):
        try:
            data = json.dumps(body).encode() if body is not None else None
            req = urllib.request.Request(url, data=data, headers={**UA, **({"Content-Type": "application/json"} if data else {})})
            with urllib.request.urlopen(req, timeout=120) as r:
                return json.loads(r.read().decode())
        except Exception as e:  # noqa: BLE001
            msg = str(e)
            time.sleep(2 * (k + 1))
    print(f"  FAIL {url[:100]} {msg}", flush=True)
    return None


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    d = get("https://yields.llama.fi/pools")
    pools = pd.DataFrame(d["data"])
    pools["tvlUsd"] = pd.to_numeric(pools["tvlUsd"], errors="coerce")
    u = pools[(pools["stablecoin"] == True) & (pools["ilRisk"] == "no") & (pools["exposure"] == "single")  # noqa: E712
              & (pools["tvlUsd"] >= 1_000_000)]
    print(f"universe: {len(u)} stable single-exposure pools with TVL >= $1M (of {len(pools)})", flush=True)
    u[["pool", "chain", "project", "symbol", "tvlUsd"]].to_parquet(OUT / "fallback_stable_pools.parquet", index=False)
    rows = []
    for i, p in enumerate(u["pool"]):
        c = get(f"https://yields.llama.fi/chart/{p}")
        for x in (c or {}).get("data") or []:
            rows.append({"pool": p, "ts": x.get("timestamp"), "tvlUsd": x.get("tvlUsd"), "apyBase": x.get("apyBase"),
                         "apyReward": x.get("apyReward")})
        if i % 100 == 0:
            print(f"  charts {i}/{len(u)}", flush=True)
        time.sleep(0.2)
    ch = pd.DataFrame(rows)
    ch["ts"] = pd.to_datetime(ch["ts"], utc=True)
    for c in ("tvlUsd", "apyBase", "apyReward"):
        ch[c] = pd.to_numeric(ch[c], errors="coerce")
    ch.to_parquet(OUT / "fallback_stable_charts.parquet", index=False)
    print(f"charts: {ch['pool'].nunique()} pools, {len(ch)} rows", flush=True)
    v = get("https://api.hyperliquid.xyz/info", {"type": "vaultDetails", "vaultAddress": "0xdfc24b077bc1425ad1dea75bcb6f8158e10df303"})
    port = dict((k, val) for k, val in (v or {}).get("portfolio", []))
    allt = port.get("allTime", {})
    av = pd.DataFrame(allt.get("accountValueHistory", []), columns=["t", "account_value"])
    pn = pd.DataFrame(allt.get("pnlHistory", []), columns=["t", "pnl"])
    h = av.merge(pn, on="t", how="outer").sort_values("t")
    h["ts"] = pd.to_datetime(h["t"], unit="ms", utc=True)
    for c in ("account_value", "pnl"):
        h[c] = pd.to_numeric(h[c], errors="coerce")
    h.to_parquet(OUT / "fallback_hlp.parquet", index=False)
    print(f"HLP: {len(h)} points {h['ts'].min()} .. {h['ts'].max()}", flush=True)


if __name__ == "__main__":
    main()

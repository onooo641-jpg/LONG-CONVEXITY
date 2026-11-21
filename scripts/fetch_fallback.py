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


def job_stable_hlp():
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


PROBES = {
    "kraken_futures": "https://futures.kraken.com/derivatives/api/v4/historicalfundingrates?symbol=PF_XBTUSD",
    "deribit": "https://www.deribit.com/api/v2/public/get_funding_rate_history?instrument_name=BTC-PERPETUAL&start_timestamp=1730419200000&end_timestamp=1730505600000",
    "dydx_v4": "https://indexer.dydx.trade/v4/historicalFunding/BTC-USD?limit=5",
    "paradex": "https://api.prod.paradex.trade/v1/funding/data?market=BTC-USD-PERP&page_size=5",
    "lighter": "https://mainnet.zklighter.elliot.ai/api/v1/fundings?market_id=1&resolution=1h&start_timestamp=1730419200&end_timestamp=1730505600&count_back=5",
    "drift": "https://data.api.drift.trade/fundingRates?marketName=BTC-PERP",
    "binance": "https://fapi.binance.com/fapi/v1/fundingRate?symbol=BTCUSDT&limit=5",
    "bybit": "https://api.bybit.com/v5/market/funding/history?category=linear&symbol=BTCUSDT&limit=5",
    "okx": "https://www.okx.com/api/v5/public/funding-rate-history?instId=BTC-USDT-SWAP&limit=5",
    "bitget": "https://api.bitget.com/api/v2/mix/market/history-fund-rate?symbol=BTCUSDT&productType=usdt-futures&pageSize=5",
    "gate": "https://api.gateio.ws/api/v4/futures/usdt/funding_rate?contract=BTC_USDT&limit=5",
    "kucoin": "https://api-futures.kucoin.com/api/v1/contract/funding-rates?symbol=XBTUSDTM&from=1730419200000&to=1730505600000",
    "mexc": "https://contract.mexc.com/api/v1/contract/funding_rate/history?symbol=BTC_USDT&page_num=1&page_size=5",
    "coinbase_intl": "https://api.international.coinbase.com/api/v1/instruments/BTC-PERP/funding?result_limit=5",
    "bitmex": "https://www.bitmex.com/api/v1/funding?symbol=XBTUSD&count=5&reverse=true",
    "aevo": "https://api.aevo.xyz/funding-history?instrument_name=BTC-PERP&limit=5",
    "gmx_arb": "https://arbitrum-api.gmxinfra.io/markets/info",
}


def job_probe():
    """Which perp venues answer from GitHub's US runners (reachability only, first 160 chars of body)."""
    for k, u in PROBES.items():
        try:
            req = urllib.request.Request(u, headers=UA)
            with urllib.request.urlopen(req, timeout=30) as r:
                b = r.read(400).decode("utf-8", "replace").replace("\n", " ")
                print(f"PROBE {k}: HTTP {r.status} {b[:160]}", flush=True)
        except Exception as e:  # noqa: BLE001
            print(f"PROBE {k}: FAIL {str(e)[:120]}", flush=True)


JOBS = {"stable_hlp": job_stable_hlp, "probe": job_probe}

if __name__ == "__main__":
    import sys
    for j in (sys.argv[1:] or ["stable_hlp"]):
        print(f"=== {j}", flush=True)
        JOBS[j]()

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


COINS = ["BTC", "ETH", "SOL", "XRP", "DOGE", "AVAX", "LINK", "SUI", "ARB", "OP", "LTC", "BNB"]
F_START = int(pd.Timestamp("2024-10-30", tz="UTC").timestamp())
F_END = int(pd.Timestamp("2026-11-01", tz="UTC").timestamp())


def _hl(coin):
    rows, t = [], F_START * 1000
    while t < F_END * 1000:
        d = get("https://api.hyperliquid.xyz/info", {"type": "fundingHistory", "coin": coin, "startTime": t, "endTime": F_END * 1000})
        if not d:
            break
        rows += [(int(x["time"]) // 1000, float(x["fundingRate"])) for x in d]
        if len(d) < 2:
            break
        t = int(d[-1]["time"]) + 1
        time.sleep(0.3)
    return rows


def _dydx(coin):
    rows, before = [], pd.Timestamp(F_END, unit="s", tz="UTC")
    for _ in range(400):
        u = f"https://indexer.dydx.trade/v4/historicalFunding/{coin}-USD?limit=100&effectiveBeforeOrAt={before.strftime('%Y-%m-%dT%H:%M:%S.000Z')}"
        d = (get(u) or {}).get("historicalFunding") or []
        if not d:
            break
        for x in d:
            rows.append((int(pd.Timestamp(x["effectiveAt"]).timestamp()), float(x["rate"])))
        last = pd.Timestamp(d[-1]["effectiveAt"])
        if last.timestamp() <= F_START or len(d) < 100:
            break
        before = last - pd.Timedelta(seconds=1)
        time.sleep(0.15)
    return rows


def _aevo(coin):
    rows, end = [], F_END * 10**9
    for _ in range(800):
        u = f"https://api.aevo.xyz/funding-history?instrument_name={coin}-PERP&start_time={F_START * 10**9}&end_time={end}&limit=50"
        d = (get(u) or {}).get("funding_history") or []
        if not d:
            break
        for x in d:
            rows.append((int(x[1]) // 10**9, float(x[2])))
        oldest = min(int(x[1]) for x in d)
        if oldest >= end:  # no progress: stop instead of looping
            break
        if oldest <= F_START * 10**9 or len(d) < 50:
            break
        end = oldest - 1
        time.sleep(0.15)
    return rows


def _gate(coin):
    rows, to = [], F_END
    for _ in range(50):
        d = get(f"https://api.gateio.ws/api/v4/futures/usdt/funding_rate?contract={coin}_USDT&limit=1000&from={F_START}&to={to}") or []
        if not d:
            break
        rows += [(int(x["t"]), float(x["r"])) for x in d]
        oldest = min(int(x["t"]) for x in d)
        if oldest <= F_START or len(d) < 1000:
            break
        to = oldest - 1
        time.sleep(0.2)
    return rows


def job_funding():
    """#208: funding histories (rate per settlement; Gate per its interval) for HL, dYdX v4, Aevo, Gate."""
    OUT.mkdir(parents=True, exist_ok=True)
    out = []
    for venue, fn in (("hl", _hl), ("dydx", _dydx), ("aevo", _aevo), ("gate", _gate)):
        for c in COINS:
            r = fn(c)
            print(f"  {venue} {c}: {len(r)} rows" + (f" {pd.Timestamp(min(r)[0], unit='s').date()}..{pd.Timestamp(max(r)[0], unit='s').date()}" if r else ""), flush=True)
            out += [{"venue": venue, "coin": c, "t": t, "rate": v} for t, v in r]
            pd.DataFrame(out).drop_duplicates(["venue", "coin", "t"]).to_parquet(OUT / "fundgap_funding.parquet", index=False)
    df = pd.DataFrame(out).drop_duplicates(["venue", "coin", "t"])
    df.to_parquet(OUT / "fundgap_funding.parquet", index=False)
    print(f"funding rows: {len(df)}", flush=True)


JOBS = {"stable_hlp": job_stable_hlp, "probe": job_probe, "funding": job_funding}

if __name__ == "__main__":
    import sys
    for j in (sys.argv[1:] or ["stable_hlp"]):
        print(f"=== {j}", flush=True)
        JOBS[j]()

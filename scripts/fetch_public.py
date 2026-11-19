"""Fetch free public data for docs/PREREG_TOP10_20261120.md into data/public/.

    python scripts/fetch_public.py hl llama_lend llama_pools llama_prices poly

Run by .github/workflows/fetch_public.yml (the agent sandbox can't reach these
hosts). Every request's outcome is printed, so the run log shows exactly what
worked and what didn't. Stdlib HTTP only.
"""

from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import pandas as pd

OUT = Path(__file__).resolve().parent.parent / "data" / "public"
UA = {"User-Agent": "long-convexity-research/1.0", "Content-Type": "application/json"}
STATS = {"ok": 0, "fail": 0}


def http(url, body=None, tries=4, pause=1.0):
    data = json.dumps(body).encode() if body is not None else None
    for k in range(tries):
        try:
            req = urllib.request.Request(url, data=data, headers=UA, method="POST" if data else "GET")
            with urllib.request.urlopen(req, timeout=60) as r:
                STATS["ok"] += 1
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            msg = f"HTTP {e.code}"
            if e.code in (429, 500, 502, 503, 504):
                time.sleep(pause * (2 ** k) * 5)
                continue
            break
        except Exception as e:  # noqa: BLE001
            msg = f"{type(e).__name__}: {e}"
            time.sleep(pause * (2 ** k))
    STATS["fail"] += 1
    print(f"  FAIL {url[:120]} {body if body else ''} -> {msg}", flush=True)
    return None


# ---------------------------------------------------------------- Hyperliquid
HL = "https://api.hyperliquid.xyz/info"
T2024 = int(pd.Timestamp("2024-01-01", tz="UTC").timestamp() * 1000)


def hl_funding(coin, start, end=None, max_pages=60):
    rows, t = [], start
    for _ in range(max_pages):
        body = {"type": "fundingHistory", "coin": coin, "startTime": t}
        if end:
            body["endTime"] = end
        page = http(HL, body)
        time.sleep(1.0)
        if not page:
            break
        rows.extend(page)
        if len(page) < 500:
            break
        t = int(page[-1]["time"]) + 1
        if end and t >= end:
            break
    return rows


def job_hl():
    meta = http(HL, {"type": "metaAndAssetCtxs"})
    if not meta:
        print("hl: metaAndAssetCtxs unavailable")
        return
    universe, ctxs = meta[0]["universe"], meta[1]
    coins = pd.DataFrame([{"coin": u["name"], "delisted": bool(u.get("isDelisted", False)),
                           "open_interest": float(c.get("openInterest", 0) or 0) * float(c.get("markPx", 0) or 0)}
                          for u, c in zip(universe, ctxs)])
    print(f"hl: {len(coins)} perps in meta, {coins.delisted.sum()} marked delisted", flush=True)
    firsts, fund_rows, candle_rows = [], [], []
    for coin in coins.coin:
        page = http(HL, {"type": "fundingHistory", "coin": coin, "startTime": 0})
        time.sleep(1.0)
        first = int(page[0]["time"]) if page else None
        firsts.append(first)
    coins["first_funding_ms"] = firsts
    coins.to_parquet(OUT / "hl_coins.parquet")
    listed = coins[coins.first_funding_ms.notna() & (coins.first_funding_ms >= T2024)]
    print(f"hl: {len(listed)} listings since 2024-01-01", flush=True)
    for coin, first in zip(listed.coin, listed.first_funding_ms):
        first = int(first)
        end = first + 15 * 24 * 3600 * 1000
        for r in hl_funding(coin, first, end, max_pages=2):
            fund_rows.append({"coin": coin, "time": int(r["time"]), "rate": float(r["fundingRate"])})
        c = http(HL, {"type": "candleSnapshot", "req": {"coin": coin, "interval": "1h",
                                                         "startTime": first, "endTime": end}})
        time.sleep(1.0)
        for k in c or []:
            candle_rows.append({"coin": coin, "t": int(k["t"]), "o": float(k["o"]), "h": float(k["h"]),
                                "l": float(k["l"]), "c": float(k["c"])})
    # baseline: 20 largest-OI coins listed >= 180 days before 2024-01-01 + full history from 2024
    est = coins[coins.first_funding_ms.notna() & (coins.first_funding_ms < T2024 - 180 * 86400 * 1000)]
    base = est.nlargest(20, "open_interest").coin.tolist()
    print(f"hl: baseline coins {base}", flush=True)
    for coin in base:
        for r in hl_funding(coin, T2024):
            fund_rows.append({"coin": coin, "time": int(r["time"]), "rate": float(r["fundingRate"])})
    pd.DataFrame(fund_rows).to_parquet(OUT / "hl_funding.parquet")
    pd.DataFrame(candle_rows).to_parquet(OUT / "hl_candles.parquet")
    pd.Series(base, name="coin").to_frame().to_parquet(OUT / "hl_baseline_coins.parquet")
    print(f"hl: {len(fund_rows)} funding rows, {len(candle_rows)} candles", flush=True)


# ---------------------------------------------------------------- DefiLlama
Y = "https://yields.llama.fi"


def llama_pools():
    p = http(f"{Y}/pools")
    if not p:
        return None
    return pd.DataFrame(p["data"])


def job_llama_lend():
    lb = http(f"{Y}/lendBorrow")
    pools = llama_pools()
    if pools is None:
        print("llama_lend: /pools unavailable")
        return
    sel = pools[(pools.project == "aave-v3") & pools.symbol.isin(["USDC", "USDT", "DAI", "WETH", "WBTC"])
                & (pools.tvlUsd >= 10e6)]
    print(f"llama_lend: {len(sel)} aave-v3 pools; lendBorrow {'ok' if lb else 'unavailable'}", flush=True)
    rows, mode = [], "lendBorrow"
    for pid, sym, chain in zip(sel.pool, sel.symbol, sel.chain):
        d = http(f"{Y}/chartLendBorrow/{pid}")
        time.sleep(0.5)
        if d and d.get("data"):
            for r in d["data"]:
                rows.append({"pool": pid, "symbol": sym, "chain": chain, **r})
            continue
        mode = "fallback"
        d = http(f"{Y}/chart/{pid}")
        time.sleep(0.5)
        for r in (d or {}).get("data", []):
            rows.append({"pool": pid, "symbol": sym, "chain": chain, **r})
    df = pd.DataFrame(rows)
    df.to_parquet(OUT / "llama_lend.parquet")
    print(f"llama_lend: {len(df)} rows, mode {mode}", flush=True)


def job_llama_pools():
    pools = llama_pools()
    if pools is None:
        print("llama_pools: /pools unavailable")
        return
    keep = [c for c in ["pool", "chain", "project", "symbol", "tvlUsd", "apyBase", "apyReward", "exposure",
                        "stablecoin", "ilRisk", "poolMeta", "underlyingTokens", "rewardTokens"] if c in pools]
    pools[keep].astype({"underlyingTokens": str, "rewardTokens": str}, errors="ignore").to_parquet(OUT / "llama_pools_now.parquet")
    lp = pools[(pools.exposure == "multi") & (pools.tvlUsd >= 1e6)].nlargest(300, "tvlUsd")
    vault_proj = pools.project.str.contains("yearn|morpho|beefy|vault|euler|sommelier|idle|harvest", case=False, na=False)
    lend_proj = pools.project.isin(["aave-v3", "compound-v3", "spark", "fluid-lending", "morpho-blue"])
    stable = pools.symbol.isin(["USDC", "USDT"]) & pools.chain.isin(["Ethereum", "Arbitrum", "Base"])
    vaults = pools[stable & vault_proj & (pools.exposure == "single")].nlargest(30, "tvlUsd")
    lenders = pools[stable & lend_proj].nlargest(30, "tvlUsd")
    print(f"llama_pools: {len(lp)} LP pools, {len(vaults)} vaults, {len(lenders)} lenders", flush=True)
    rows = []
    for kind, frame in (("lp", lp), ("vault", vaults), ("lend", lenders)):
        for pid in frame.pool:
            d = http(f"{Y}/chart/{pid}")
            time.sleep(0.6)
            for r in (d or {}).get("data", []):
                rows.append({"kind": kind, "pool": pid, **r})
    df = pd.DataFrame(rows)
    df.to_parquet(OUT / "llama_charts.parquet")
    print(f"llama_pools: {len(df)} chart rows", flush=True)


def job_llama_prices():
    coins = "coingecko:staked-ether,coingecko:ethereum"
    start = int(pd.Timestamp("2022-01-01", tz="UTC").timestamp())
    rows = []
    for k in range(6):
        d = http(f"https://coins.llama.fi/chart/{coins}?start={start + k * 300 * 86400}&span=300&period=1d")
        time.sleep(1.0)
        for key, v in (d or {}).get("coins", {}).items():
            for p in v.get("prices", []):
                rows.append({"coin": key, "t": int(p["timestamp"]), "price": float(p["price"])})
    df = pd.DataFrame(rows).drop_duplicates()
    df.to_parquet(OUT / "llama_prices.parquet")
    print(f"llama_prices: {len(df)} rows", flush=True)


# ---------------------------------------------------------------- Polymarket
G = "https://gamma-api.polymarket.com"
C = "https://clob.polymarket.com"


def job_poly(max_calls=4000):
    events, offset = [], 0
    while offset < 20000:
        page = http(f"{G}/events?closed=true&limit=100&offset={offset}"
                    f"&end_date_min=2024-01-01T00:00:00Z&end_date_max=2026-10-31T23:59:59Z")
        time.sleep(0.3)
        if not page:
            break
        events.extend(page)
        if len(page) < 100:
            break
        offset += 100
    print(f"poly: {len(events)} closed events listed", flush=True)
    keep = []
    for e in events:
        ms = e.get("markets") or []
        if not e.get("negRisk") or len(ms) < 3:
            continue
        wins = 0
        for m in ms:
            try:
                wins += json.loads(m.get("outcomePrices") or "[]")[0] in ("1", 1, "1.0")
            except Exception:  # noqa: BLE001
                pass
        if wins == 1:
            keep.append(e)
    keep.sort(key=lambda e: -float(e.get("volume") or 0))
    print(f"poly: {len(keep)} negRisk events with >=3 markets and one YES winner", flush=True)
    rows, calls = [], 0
    for e in keep:
        for m in e["markets"]:
            if calls >= max_calls:
                break
            try:
                tok = json.loads(m.get("clobTokenIds") or "[]")[0]
            except Exception:  # noqa: BLE001
                continue
            h = http(f"{C}/prices-history?market={tok}&interval=max&fidelity=60")
            calls += 1
            time.sleep(0.15)
            won = json.loads(m.get("outcomePrices") or '["0"]')[0] in ("1", 1, "1.0")
            for p in (h or {}).get("history", []):
                rows.append({"event": e["id"], "market": m["id"], "won": won, "t": int(p["t"]), "p": float(p["p"])})
    df = pd.DataFrame(rows)
    df.to_parquet(OUT / "poly_prices.parquet")
    pd.DataFrame([{"event": e["id"], "title": e.get("title"), "n_markets": len(e["markets"]),
                   "volume": float(e.get("volume") or 0), "end": e.get("endDate")} for e in keep]
                 ).to_parquet(OUT / "poly_events.parquet")
    print(f"poly: {len(df)} price rows from {calls} token histories", flush=True)


JOBS = {"hl": job_hl, "llama_lend": job_llama_lend, "llama_pools": job_llama_pools,
        "llama_prices": job_llama_prices, "poly": job_poly}


def main(argv):
    OUT.mkdir(parents=True, exist_ok=True)
    for name in argv:
        print(f"=== {name}", flush=True)
        t0 = time.time()
        try:
            JOBS[name]()
        except Exception as e:  # noqa: BLE001
            print(f"{name}: crashed {type(e).__name__}: {e}", flush=True)
        print(f"=== {name} done in {time.time() - t0:.0f}s  ok {STATS['ok']} fail {STATS['fail']}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

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
import urllib.parse
import urllib.request
from pathlib import Path

import pandas as pd

OUT = Path(__file__).resolve().parent.parent / "data" / "public"
UA = {"User-Agent": "long-convexity-research/1.0", "Accept": "application/json"}
STATS = {"ok": 0, "fail": 0}


def http(url, body=None, tries=4, pause=1.0):
    data = json.dumps(body).encode() if body is not None else None
    for k in range(tries):
        try:
            hdr = {**UA, **({"Content-Type": "application/json"} if data else {})}
            req = urllib.request.Request(url, data=data, headers=hdr, method="POST" if data else "GET")
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
    # Run 44574894552: span=300 -> HTTP 400. Try shorter spans and the token
    # address form; keep whichever answers.
    variants = ["coingecko:staked-ether,coingecko:ethereum",
                "ethereum:0xae7ab96520de3a18e5e111b5eaab095312d7fe84,coingecko:ethereum"]
    start = int(pd.Timestamp("2023-01-01", tz="UTC").timestamp())
    rows = []
    for coins in variants:
        for k in range(0, 1500, 100):
            d = http(f"https://coins.llama.fi/chart/{coins}?start={start + k * 86400}&span=100&period=1d")
            time.sleep(0.8)
            for key, v in (d or {}).get("coins", {}).items():
                for p in v.get("prices", []):
                    rows.append({"coin": key, "t": int(p["timestamp"]), "price": float(p["price"])})
        if rows:
            break
    df = pd.DataFrame(rows).drop_duplicates()
    df.to_parquet(OUT / "llama_prices.parquet")
    print(f"llama_prices: {len(df)} rows", flush=True)


# ---------------------------------------------------------------- Polymarket
G = "https://gamma-api.polymarket.com"
C = "https://clob.polymarket.com"


def job_poly(max_calls=4000):
    events, offset = [], 0
    # Run 44574894552: the ISO end_date filters -> HTTP 406. Date-only form here.
    while offset < 20000:
        page = http(f"{G}/events?closed=true&limit=100&offset={offset}"
                    f"&end_date_min=2024-01-01&end_date_max=2026-10-31")
        if page is None and offset == 0:
            page = http(f"{G}/events?closed=true&limit=100&offset={offset}")
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


def job_hl2023():
    """PREREG_POSTLISTING_20261120: listings 2023-05-20..2023-12-31 + BTC control."""
    coins = pd.read_parquet(OUT / "hl_coins.parquet")
    lo = pd.Timestamp("2023-05-20", tz="UTC").timestamp() * 1000
    sel = coins[coins.first_funding_ms.notna() & (coins.first_funding_ms >= lo) & (coins.first_funding_ms < T2024)]
    print(f"hl2023: {len(sel)} holdout listings", flush=True)
    fund, cand = [], []
    for coin, first in zip(sel.coin, sel.first_funding_ms):
        first = int(first)
        end = first + 15 * 24 * 3600 * 1000
        for r in hl_funding(coin, first, end, max_pages=2):
            fund.append({"coin": coin, "time": int(r["time"]), "rate": float(r["fundingRate"])})
        c = http(HL, {"type": "candleSnapshot", "req": {"coin": coin, "interval": "1h", "startTime": first, "endTime": end}})
        time.sleep(1.0)
        for k in c or []:
            cand.append({"coin": coin, "t": int(k["t"]), "o": float(k["o"]), "h": float(k["h"]), "l": float(k["l"]), "c": float(k["c"])})
    for coin in ("BTC",):
        for r in hl_funding(coin, int(lo), T2024 + 15 * 86400 * 1000):
            fund.append({"coin": coin, "time": int(r["time"]), "rate": float(r["fundingRate"])})
        t = int(lo)
        while t < T2024 + 15 * 86400 * 1000:
            c = http(HL, {"type": "candleSnapshot", "req": {"coin": coin, "interval": "1h", "startTime": t, "endTime": t + 4000 * 3600 * 1000}})
            time.sleep(1.0)
            for k in c or []:
                cand.append({"coin": coin, "t": int(k["t"]), "o": float(k["o"]), "h": float(k["h"]), "l": float(k["l"]), "c": float(k["c"])})
            t += 4000 * 3600 * 1000
    pd.DataFrame(fund).to_parquet(OUT / "hl2023_funding.parquet")
    pd.DataFrame(cand).to_parquet(OUT / "hl2023_candles.parquet")
    print(f"hl2023: {len(fund)} funding rows, {len(cand)} candles", flush=True)


def job_hl2023d():
    """PREREG_POSTLISTING_20261120 v2: daily candles for the 2023 holdout + BTC."""
    coins = pd.read_parquet(OUT / "hl_coins.parquet")
    lo = pd.Timestamp("2023-05-20", tz="UTC").timestamp() * 1000
    sel = coins[coins.first_funding_ms.notna() & (coins.first_funding_ms >= lo) & (coins.first_funding_ms < T2024)]
    rows = []
    for coin, first in list(zip(sel.coin, sel.first_funding_ms)) + [("BTC", lo)]:
        first = int(first)
        end = (T2024 + 20 * 86400 * 1000) if coin == "BTC" else first + 17 * 86400 * 1000
        c = http(HL, {"type": "candleSnapshot", "req": {"coin": coin, "interval": "1d", "startTime": first - 86400 * 1000, "endTime": end}})
        time.sleep(1.0)
        for k in c or []:
            rows.append({"coin": coin, "t": int(k["t"]), "o": float(k["o"]), "h": float(k["h"]), "l": float(k["l"]), "c": float(k["c"])})
    pd.DataFrame(rows).to_parquet(OUT / "hl2023_daily.parquet")
    print(f"hl2023d: {len(rows)} daily candles for {len(sel)} listings + BTC", flush=True)


def job_batch2():
    """PREREG_BATCH2_20261120: lending pools across chains + stablecoin prices."""
    pools = pd.read_parquet(OUT / "llama_pools_now.parquet")
    sel = pools[pools.symbol.isin(["USDC", "USDT"])
                & pools.project.isin(["aave-v3", "compound-v3", "spark", "morpho-blue", "fluid-lending"])
                & pools.chain.isin(["Ethereum", "Arbitrum", "Base", "Optimism", "Polygon", "Avalanche"])
                & (pools.tvlUsd >= 10e6)]
    print(f"batch2: {len(sel)} lending pools", flush=True)
    rows = []
    for pid in sel.pool:
        d = http(f"{Y}/chart/{pid}")
        time.sleep(0.6)
        for r in (d or {}).get("data", []):
            rows.append({"pool": pid, **r})
    pd.DataFrame(rows).to_parquet(OUT / "batch2_lending.parquet")
    print(f"batch2: {len(rows)} lending chart rows", flush=True)
    ids = ["tether", "usd-coin", "dai", "terrausd", "frax", "true-usd", "usdd", "liquity-usd",
           "paxos-standard", "first-digital-usd"]
    chains = {"ethereum": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
              "arbitrum": "0xaf88d065e77c8cc2239327c5edb3a432268e5831",
              "base": "0x833589fcd6edb6e08f4c7c32d4f71b54bda02913",
              "optimism": "0x0b2c639c533813f4aa9d7837caf62653d097ff85",
              "polygon": "0x3c499c542cef5e3811e1192ce70d8cc03d5c3359",
              "avax": "0xb97ef9ef8734c71904d8002f8b6bc66dd9c48a6e"}
    groups = [",".join(f"coingecko:{i}" for i in ids[:5]), ",".join(f"coingecko:{i}" for i in ids[5:]),
              ",".join(f"{c}:{a}" for c, a in chains.items())]
    start = int(pd.Timestamp("2022-01-01", tz="UTC").timestamp())
    px = []
    for g in groups:
        for k in range(0, 1800, 100):
            d = http(f"https://coins.llama.fi/chart/{g}?start={start + k * 86400}&span=100&period=1d")
            time.sleep(0.8)
            for key, v in (d or {}).get("coins", {}).items():
                for p in v.get("prices", []):
                    px.append({"coin": key, "t": int(p["timestamp"]), "price": float(p["price"])})
    pd.DataFrame(px).drop_duplicates().to_parquet(OUT / "batch2_prices.parquet")
    print(f"batch2: {len(px)} price rows", flush=True)


# ------------------------------------------------- PREREG_LOOPHOLES_20261120
BROWSER = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
           "Accept": "text/html,application/json,application/xhtml+xml,*/*;q=0.8", "Accept-Language": "en-US,en;q=0.9"}


def http_raw(url, tries=3):
    for k in range(tries):
        try:
            req = urllib.request.Request(url, headers=BROWSER)
            with urllib.request.urlopen(req, timeout=60) as r:
                STATS["ok"] += 1
                return r.read()
        except urllib.error.HTTPError as e:
            msg = f"HTTP {e.code}"
            if e.code in (429, 500, 502, 503, 504):
                time.sleep(5 * (2 ** k))
                continue
            break
        except Exception as e:  # noqa: BLE001
            msg = f"{type(e).__name__}: {e}"
            time.sleep(2 ** k)
    STATS["fail"] += 1
    print(f"  FAIL {url[:140]} -> {msg}", flush=True)
    return None


def _yahoo_symbol(name):
    import re
    base = re.sub(r"\b(BERHAD|BHD|HOLDINGS?|GROUP|CORPORATION|\(.*?\))\b", " ", name.upper())
    for q in [name.upper().replace("BERHAD", "BHD"), base.strip(), base.split()[0] if base.split() else name]:
        raw = http_raw("https://query2.finance.yahoo.com/v1/finance/search?quotesCount=6&newsCount=0&q="
                       + urllib.parse.quote(q))
        time.sleep(0.7)
        if not raw:
            continue
        for qt in json.loads(raw).get("quotes", []):
            if str(qt.get("symbol", "")).endswith(".KL"):
                return qt["symbol"], qt.get("longname") or qt.get("shortname")
    return None, None


def job_ipo():
    """Bursa IPO list (issue price, listing date) + first trading days from Yahoo."""
    import io
    import urllib.parse  # noqa: F401
    raw_dir = OUT / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for yr in (2024, 2025, 2026):
        html = http_raw(f"https://www.bursamalaysia.com/listing/listing_resources/ipo/ipo_summary?year={yr}")
        if not html:
            continue
        (raw_dir / f"bursa_ipo_summary_{yr}.html").write_bytes(html)
        try:
            tabs = pd.read_html(io.BytesIO(html))
        except Exception as e:  # noqa: BLE001
            print(f"  ipo {yr}: read_html failed {e}", flush=True)
            continue
        for t in tabs:
            t.columns = [" ".join(map(str, c)) if isinstance(c, tuple) else str(c) for c in t.columns]
            print(f"  ipo {yr}: table {t.shape} cols {list(t.columns)[:12]}", flush=True)
            if len(t) > 3:
                t["year"] = yr
                rows.append(t)
    if not rows:
        print("ipo: no Bursa tables", flush=True)
        return
    df = pd.concat(rows, ignore_index=True)
    df.to_parquet(OUT / "ipo_bursa_summary.parquet")
    name_col = next(c for c in df.columns if "NAME" in c.upper())
    list_col = next((c for c in df.columns if "LISTING" in c.upper()), df.columns[-2])
    out = []
    for _, r in df.iterrows():
        name = str(r[name_col])
        sym, yname = _yahoo_symbol(name)
        rec = {"name": name, "listing": str(r[list_col]), "symbol": sym, "yahoo_name": yname}
        if sym:
            try:
                d0 = pd.Timestamp(str(r[list_col]), tz="Asia/Kuala_Lumpur")
            except Exception:  # noqa: BLE001
                d0 = None
            if d0 is not None:
                p1, p2 = int((d0 - pd.Timedelta(days=3)).timestamp()), int((d0 + pd.Timedelta(days=20)).timestamp())
                raw = http_raw(f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?period1={p1}&period2={p2}&interval=1d")
                time.sleep(0.7)
                try:
                    res = json.loads(raw)["chart"]["result"][0]
                    q = res["indicators"]["quote"][0]
                    bars = [(t, o, c) for t, o, c in zip(res["timestamp"], q["open"], q["close"]) if c is not None]
                    if bars:
                        rec.update(d1_ts=bars[0][0], d1_open=bars[0][1], d1_close=bars[0][2],
                                   d5_close=bars[min(4, len(bars) - 1)][2])
                except Exception as e:  # noqa: BLE001
                    print(f"  chart {sym}: {type(e).__name__}", flush=True)
        out.append(rec)
    pd.DataFrame(out).to_parquet(OUT / "ipo_first_days.parquet")
    print(f"ipo: {len(df)} Bursa rows, {sum(1 for o in out if o.get('d1_close'))} with first-day prices", flush=True)


def job_myxsnap():
    """Same-moment snapshot: Malaysian exchanges vs global prices vs USD/MYR."""
    urls = {
        "luno": "https://api.luno.com/api/1/tickers",
        "kraken": "https://api.kraken.com/0/public/Ticker?pair=XBTUSD,ETHUSD,SOLUSD,USDTUSD,XRPUSD",
        "coinbase_btc": "https://api.exchange.coinbase.com/products/BTC-USD/ticker",
        "fx_yahoo": "https://query1.finance.yahoo.com/v8/finance/chart/MYR=X?range=1d&interval=1m",
        "fx_erapi": "https://open.er-api.com/v6/latest/USD",
        "tokenize": "https://api.tokenize.exchange/public/v1/market/get-summaries",
        "hata": "https://api.hata.io/orderbook/api/tickers",
        "mxglobal": "https://www.mxglobal.com/api/v1/tickers",
        "sinegy": "https://api.sinegy.com/api/v1/tickers",
    }
    snaps = []
    for k in range(6):  # six snapshots, 10 minutes apart
        t = int(time.time())
        for name, u in urls.items():
            raw = http_raw(u, tries=2)
            if raw:
                snaps.append({"t": t, "src": name, "body": raw.decode(errors="replace")[:200000]})
        print(f"myxsnap: round {k} sources ok {len({s['src'] for s in snaps if s['t'] == t})}", flush=True)
        if k < 5:
            time.sleep(600)
    pd.DataFrame(snaps).to_parquet(OUT / "myx_snapshots.parquet")


def job_iponews():
    """Oversubscription rates from Google News headlines for every Bursa IPO 2024-2026."""
    import io
    import re
    import xml.etree.ElementTree as ET
    names = []
    for yr in (2024, 2025, 2026):
        html = http_raw(f"https://www.bursamalaysia.com/listing/listing_resources/ipo/ipo_summary?year={yr}")
        if not html:
            continue
        for t in pd.read_html(io.BytesIO(html)):
            t.columns = [" ".join(map(str, c)) if isinstance(c, tuple) else str(c) for c in t.columns]
            nc = next((c for c in t.columns if "NAME" in c.upper()), None)
            if nc is not None and len(t) > 3:
                names += [(yr, str(n)) for n in t[nc]]
    pat = re.compile(r"oversubscribed\D{0,12}?([\d,]+(?:\.\d+)?)\s*(?:times|x\b)", re.I)
    rows = []
    for yr, name in names:
        short = re.sub(r"\s+(BERHAD|BHD)\b.*$", "", name.upper().strip(), flags=re.I).title()
        found = []
        for q in (f'"{short}" IPO oversubscribed', f"{short} IPO oversubscribed times"):
            raw = http_raw("https://news.google.com/rss/search?hl=en-MY&gl=MY&ceid=MY:en&q=" + urllib.parse.quote(q))
            time.sleep(1.2)
            if not raw:
                continue
            try:
                items = ET.fromstring(raw).findall(".//item")
            except ET.ParseError:
                continue
            for it in items[:15]:
                title = it.findtext("title") or ""
                desc = it.findtext("description") or ""
                if short.split()[0].lower() not in title.lower():
                    continue
                m = pat.search(title) or pat.search(desc)
                found.append({"title": title[:200], "x": float(m.group(1).replace(",", "")) if m else None,
                              "date": it.findtext("pubDate")})
            if any(f["x"] for f in found):
                break
        xs = [f["x"] for f in found if f["x"]]
        rows.append({"year": yr, "name": name, "x_headline": xs[0] if xs else None, "n_hits": len(found),
                     "titles": " || ".join(f["title"] for f in found[:5])})
    pd.DataFrame(rows).to_parquet(OUT / "ipo_news.parquet")
    print(f"iponews: {len(rows)} IPOs, {sum(1 for r in rows if r['x_headline'])} with a headline oversubscription rate", flush=True)


def _rss_oversub(short):
    import re
    import xml.etree.ElementTree as ET
    pat = re.compile(r"oversubscribed\D{0,12}?([\d,]+(?:\.\d+)?)\s*(?:times|x\b)", re.I)
    for q in (f'"{short}" IPO oversubscribed', f"{short} IPO oversubscribed times"):
        raw = http_raw("https://news.google.com/rss/search?hl=en-MY&gl=MY&ceid=MY:en&q=" + urllib.parse.quote(q))
        time.sleep(1.0)
        if not raw:
            continue
        try:
            items = ET.fromstring(raw).findall(".//item")
        except ET.ParseError:
            continue
        for it in items[:15]:
            title = it.findtext("title") or ""
            if short.split()[0].lower() not in title.lower():
                continue
            m = pat.search(title)
            if m:
                return float(m.group(1).replace(",", "")), title[:200]
    return None, None


def job_ipo2():
    """Bursa IPOs 2024+ via i3investor IPO pages (sequential stock codes), Yahoo first days, news oversubscription."""
    import re
    codes = [f"{c:04d}" for c in range(270, 431)] + [str(c) for c in range(5300, 5361)]
    rows = []
    for code in codes:
        raw = http_raw(f"https://klse.i3investor.com/web/stock/ipo-summary/{code}", tries=2)
        time.sleep(0.8)
        if not raw:
            continue
        html = raw.decode(errors="replace")
        txt = re.sub(r"<[^>]+>", " ", html)
        txt = re.sub(r"\s+", " ", txt)
        lst = re.search(r"Listing Date\s*(\d{4}-\d{2}-\d{2})", txt)
        if not lst or lst.group(1) < "2024-01-01":
            continue
        name = re.search(r"<title>\s*([^<|]+)", html)
        price = re.search(r"(?:ISSUE|OFFER|RETAIL|IPO)[ /A-Z]{0,30}?PRICE OF RM\s?([\d.]+)", txt, re.I)
        opn = re.search(r"Opening\s*(\d{4}-\d{2}-\d{2})", txt)
        cls = re.search(r"Closing\s*(\d{4}-\d{2}-\d{2})", txt)
        rec = {"code": code, "name": name.group(1).strip() if name else None, "listing": lst.group(1),
               "issue_price": float(price.group(1).rstrip(".")) if price else None,
               "offer_open": opn.group(1) if opn else None, "offer_close": cls.group(1) if cls else None,
               "market": "ACE" if "ACE MARKET" in txt.upper() else ("Main" if "MAIN MARKET" in txt.upper() else "?")}
        d0 = pd.Timestamp(rec["listing"], tz="Asia/Kuala_Lumpur")
        p1, p2 = int((d0 - pd.Timedelta(days=2)).timestamp()), int((d0 + pd.Timedelta(days=40)).timestamp())
        cj = http_raw(f"https://query1.finance.yahoo.com/v8/finance/chart/{code}.KL?period1={p1}&period2={p2}&interval=1d")
        time.sleep(0.6)
        try:
            res = json.loads(cj)["chart"]["result"][0]
            q = res["indicators"]["quote"][0]
            bars = [(t, o, c) for t, o, c in zip(res["timestamp"], q["open"], q["close"]) if c is not None]
            rec.update(d1_ts=bars[0][0], d1_open=bars[0][1], d1_close=bars[0][2],
                       d5_close=bars[min(4, len(bars) - 1)][2], d20_close=bars[min(19, len(bars) - 1)][2])
        except Exception as e:  # noqa: BLE001
            print(f"  yahoo {code}: {type(e).__name__}", flush=True)
        short = re.sub(r"\s+(BERHAD|BHD)\b.*$", "", (rec["name"] or code).upper(), flags=re.I).title()
        rec["x_headline"], rec["x_title"] = _rss_oversub(short)
        rows.append(rec)
        print(f"  {code} {rec['listing']} {short[:30]:<30} price {rec['issue_price']} d1 {rec.get('d1_close')} X {rec['x_headline']}", flush=True)
    pd.DataFrame(rows).to_parquet(OUT / "ipo2.parquet")
    print(f"ipo2: {len(rows)} IPOs since 2024", flush=True)


JOBS = {"ipo2": job_ipo2, "iponews": job_iponews, "ipo": job_ipo, "myxsnap": job_myxsnap, "batch2": job_batch2, "hl2023d": job_hl2023d, "hl2023": job_hl2023, "hl": job_hl, "llama_lend": job_llama_lend, "llama_pools": job_llama_pools,
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

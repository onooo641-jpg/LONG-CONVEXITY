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


# ------------------------------------------------- lending liquidations (PREREG_LIQUIDATIONS_20261120)
LIQ_TOPIC = "0xe413a321e8681d831f4dbccbca790d2952b56f977908e45be37335533e005286"  # LiquidationCall(...)
LIQ_CHAINS = {
    # name: (llama chain key, native price key (or None = $1), rpc endpoints)
    "base": ("base", "coingecko:ethereum", ["https://base.api.pocket.network", "https://base.gateway.tenderly.co"] ),
    "arbitrum": ("arbitrum", "coingecko:ethereum", ["https://arb1.arbitrum.io/rpc"]),
    "optimism": ("optimism", "coingecko:ethereum", ["https://mainnet.optimism.io"]),
    "polygon": ("polygon", "coingecko:matic-network", ["https://poly.api.pocket.network", "https://polygon.gateway.tenderly.co"]),
    "avalanche": ("avax", "coingecko:avalanche-2", ["https://avalanche.gateway.tenderly.co"]),
    "bnb": ("bsc", "coingecko:binancecoin", ["https://bsc-rpc.publicnode.com", "https://bsc-dataseed.binance.org"]),
    "gnosis": ("xdai", None, ["https://rpc.gnosischain.com"]),
    "scroll": ("scroll", "coingecko:ethereum", ["https://rpc.scroll.io"]),
    "metis": ("metis", "coingecko:metis-token", ["https://andromeda.metis.io/?owner=1088"]),
    # PREREG_LIQ_NEWCHAINS_20261122 (endpoints from the liq_diag4 probe)
    "sonic": ("sonic", "coingecko:sonic-3", ["https://rpc.soniclabs.com"]),
    "mantle": ("mantle", "coingecko:mantle", ["https://rpc.mantle.xyz"]),
    "linea": ("linea", "coingecko:ethereum", ["https://rpc.linea.build"]),
    "celo": ("celo", "coingecko:celo", ["https://forno.celo.org"]),
    "ink": ("ink", "coingecko:ethereum", ["https://rpc-qnd.inkonchain.com"]),
    "soneium": ("soneium", "coingecko:ethereum", ["https://rpc.soneium.org"]),
    "zksync": ("era", "coingecko:ethereum", ["https://mainnet.era.zksync.io"]),
}
NEW_CHAINS = ("sonic", "mantle", "linea", "celo", "ink", "soneium", "zksync")
LIQ_START = int(pd.Timestamp("2024-11-01", tz="UTC").timestamp())
LIQ_MONTHS = [int(t.timestamp()) for t in pd.date_range("2024-11-01", "2026-11-01", freq="MS", tz="UTC")]  # 25 edges
LIQ_RECEIPT_CAP = 40000


RPC_FAILS, RPC_SEEN = {}, set()


def rpc(urls, method, params, tries=3):
    """JSON-RPC with endpoint fallback. Returns result, or raises RuntimeError with the last error.
    An endpoint with 8 consecutive failures is skipped (unless all are); first error text per endpoint+method is printed."""
    last = None
    for k in range(tries):
        live = [u for u in urls if RPC_FAILS.get(u, 0) < 8] or list(urls)
        for u in live:
            try:
                if "etherscan.io" in u:
                    j = _es(u, method, params)
                else:
                    req = urllib.request.Request(u, data=json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode(),
                                                 headers={**UA, "Content-Type": "application/json"}, method="POST")
                    with urllib.request.urlopen(req, timeout=60) as r:
                        j = json.loads(r.read().decode())
                if "error" in j:
                    last = f"{u}: {j['error']}"
                    if (u, method) not in RPC_SEEN:
                        RPC_SEEN.add((u, method))
                        print(f"  rpc error {method} @ {u}: {str(j['error'])[:200]}", flush=True)
                    if "range" in str(j["error"]).lower() or "limit" in str(j["error"]).lower() or "exceed" in str(j["error"]).lower() or "too many" in str(j["error"]).lower():
                        raise ValueError(last)  # caller shrinks the window
                    continue
                STATS["ok"] += 1
                RPC_FAILS[u] = 0
                return j["result"]
            except ValueError:
                raise
            except urllib.error.HTTPError as e:
                if e.code in (400, 413) and method == "eth_getLogs":       # window too large for this endpoint: caller shrinks it
                    raise ValueError(f"{u}: HTTP {e.code}") from e
                last = f"{u}: HTTPError: HTTP {e.code}"
                if e.code == 429:
                    time.sleep(8)
                RPC_FAILS[u] = RPC_FAILS.get(u, 0) + 1
                if (u, method) not in RPC_SEEN:
                    RPC_SEEN.add((u, method))
                    print(f"  rpc exception {method} @ {u}: HTTP {e.code}", flush=True)
            except Exception as e:  # noqa: BLE001
                last = f"{u}: {type(e).__name__}: {e}"
                RPC_FAILS[u] = RPC_FAILS.get(u, 0) + 1
                if (u, method) not in RPC_SEEN:
                    RPC_SEEN.add((u, method))
                    print(f"  rpc exception {method} @ {u}: {type(e).__name__}: {str(e)[:200]}", flush=True)
        time.sleep(2 * (k + 1))
    STATS["fail"] += 1
    raise RuntimeError(last)


def _es(u, method, params):
    """Etherscan V2 backend (key only from env ETHERSCAN_API_KEY, never printed). Returns a JSON-RPC-shaped dict."""
    import os
    key = os.environ.get("ETHERSCAN_API_KEY", "")
    if not key:
        raise RuntimeError("no ETHERSCAN_API_KEY")
    time.sleep(0.25)  # free tier: 5 calls/s

    def get(q):
        for k in range(5):
            req = urllib.request.Request(u + "&" + urllib.parse.urlencode({**q, "apikey": key}), headers=UA)
            with urllib.request.urlopen(req, timeout=60) as r:
                j = json.loads(r.read().decode())
            if isinstance(j.get("result"), str) and "rate limit" in j["result"].lower():
                time.sleep(2 * (k + 1))
                continue
            return j
        return j
    if method == "eth_getLogs":
        f = params[0]
        out = []
        for page in range(1, 11):
            j = get({"module": "logs", "action": "getLogs", "fromBlock": int(f["fromBlock"], 16), "toBlock": int(f["toBlock"], 16),
                     "topic0": f["topics"][0], "page": page, "offset": 1000})
            res = j.get("result")
            if isinstance(res, list):
                out.extend(res)
                if len(res) < 1000:
                    return {"result": out}
            elif "no records" in str(j.get("message", "")).lower():
                return {"result": out}
            else:
                return {"error": {"message": str(res)[:200]}}
        raise ValueError("etherscan: >10000 results in window, range too large")
    q = {"module": "proxy", "action": method}
    if method == "eth_getBlockByNumber":
        q.update(tag=params[0], boolean="false")
    elif method == "eth_getTransactionReceipt":
        q.update(txhash=params[0])
    elif method == "eth_call":
        q.update(to=params[0]["to"], data=params[0]["data"], tag=params[1])
    elif method != "eth_blockNumber":
        raise RuntimeError("unsupported " + method)
    j = get(q)
    if "result" in j and not isinstance(j["result"], str) or (isinstance(j.get("result"), str) and j["result"].startswith("0x")):
        return {"result": j["result"]}
    if j.get("result") is None and "error" not in j:
        return {"result": None}
    return {"error": j.get("error") or {"message": str(j.get("result") or j.get("message"))[:200]}}


def _block_ts(urls, n):
    return int(rpc(urls, "eth_getBlockByNumber", [hex(n), False])["timestamp"], 16)


def _first_block_at(urls, ts, lo, hi):
    """first block with timestamp >= ts, searching [lo, hi]."""
    while lo < hi:
        mid = (lo + hi) // 2
        if _block_ts(urls, mid) >= ts:
            hi = mid
        else:
            lo = mid + 1
    return lo


def _liq_prices(name, toks, out_name=None):
    """DefiLlama daily prices for tokens + native gas coin. span must be <= ~100 days (span=300/365 gives HTTP 400)."""
    lkey, native, _ = LIQ_CHAINS[name]
    keys = [f"{lkey}:{t}" for t in toks] + ([native] if native else [])
    prows = []
    ndays = (LIQ_MONTHS[-1] - LIQ_START) // 86400 + 2   # window length; never request past it
    for i in range(0, len(keys), 3):   # 3 coins x <=100 days: larger requests returned HTTP 400
        batch = keys[i:i + 3]
        for k in range(0, ndays, 100):
            stt = LIQ_START - 86400 + k * 86400
            j = http("https://coins.llama.fi/chart/" + urllib.parse.quote(",".join(batch), safe=",:") + f"?start={stt}&span={min(100, ndays - k)}&period=1d")
            time.sleep(0.3)
            for kk, v in ((j or {}).get("coins") or {}).items():
                for p in v.get("prices", []):
                    prows.append({"coin": kk, "ts": int(p["timestamp"]), "price": float(p["price"])})
    pdf = pd.DataFrame(prows, columns=["coin", "ts", "price"]).drop_duplicates()
    pdf.to_parquet(OUT / f"liq_{out_name or name}_prices.parquet")
    print(f"{name}: prices {len(pdf)} points, {pdf['coin'].nunique()}/{len(keys)} coins priced", flush=True)


def _liq_prices_job(c):
    def run():
        df = pd.read_parquet(OUT / f"liq_{c}.parquet", columns=["collateral", "debt"])
        _liq_prices(c, sorted(set(df["collateral"]) | set(df["debt"])))
    return run


def job_liq_pxdiag():
    """Print DefiLlama responses (incl. error bodies) for several request shapes."""
    df = pd.read_parquet(OUT / "liq_gnosis.parquet", columns=["collateral", "debt"])
    toks = sorted(set(df["collateral"]) | set(df["debt"]))[:12]
    t0 = LIQ_START
    shapes = {
        "native span10": f"https://coins.llama.fi/chart/coingecko:ethereum?start={t0}&span=10&period=1d",
        "native span100": f"https://coins.llama.fi/chart/coingecko:ethereum?start={t0}&span=100&period=1d",
        "native no period": f"https://coins.llama.fi/chart/coingecko:ethereum?start={t0}&span=10",
        "tok1 xdai span10": f"https://coins.llama.fi/chart/xdai:{toks[0]}?start={t0}&span=10&period=1d",
        "tok1 gnosis span10": f"https://coins.llama.fi/chart/gnosis:{toks[0]}?start={t0}&span=10&period=1d",
        "tok10 xdai span10": "https://coins.llama.fi/chart/" + ",".join(f"xdai:{t}" for t in toks[:10]) + f"?start={t0}&span=10&period=1d",
        "tok1 historical": f"https://coins.llama.fi/prices/historical/{t0}/xdai:{toks[0]}",
        "tok1 current": f"https://coins.llama.fi/prices/current/xdai:{toks[0]}",
        "tok1 start-in-past-2y span10": f"https://coins.llama.fi/chart/xdai:{toks[0]}?start={t0 - 40*86400}&span=10&period=1d",
    }
    for k, u in shapes.items():
        try:
            req = urllib.request.Request(u, headers=UA)
            with urllib.request.urlopen(req, timeout=60) as r:
                body = r.read().decode()[:300]
            print(f"pxdiag {k}: 200 {body}", flush=True)
        except urllib.error.HTTPError as e:
            print(f"pxdiag {k}: HTTP {e.code} {e.read().decode()[:300]}", flush=True)
        except Exception as e:  # noqa: BLE001
            print(f"pxdiag {k}: {type(e).__name__} {e}", flush=True)
        time.sleep(1)


def job_liq_decimals():
    """Fill token decimals missing from liq_<chain>.parquet (eth_call failed there): eth_call with retries, then DefiLlama current."""
    for name, (lkey, _, urls) in LIQ_CHAINS.items():
        f = OUT / f"liq_{name}.parquet"
        if not f.exists():
            continue
        df = pd.read_parquet(f, columns=["collateral", "debt", "coll_dec", "debt_dec"])
        have = {}
        for a, b in (("collateral", "coll_dec"), ("debt", "debt_dec")):
            for t, d in zip(df[a], df[b]):
                if pd.notna(d):
                    have[t] = int(d)
        toks = sorted(set(df["collateral"]) | set(df["debt"]))
        missing = [t for t in toks if t not in have]
        got = {}
        for t in missing:
            for k in range(4):
                try:
                    got[t] = int(rpc(urls, "eth_call", [{"to": t, "data": "0x313ce567"}, "latest"], tries=1), 16)
                    break
                except Exception:  # noqa: BLE001
                    time.sleep(1.5 * (k + 1))
        still = [t for t in missing if t not in got]
        for i in range(0, len(still), 10):
            batch = still[i:i + 10]
            j = http("https://coins.llama.fi/prices/current/" + urllib.parse.quote(",".join(f"{lkey}:{t}" for t in batch), safe=",:"))
            for kk, v in ((j or {}).get("coins") or {}).items():
                if "decimals" in v:
                    got[kk.split(":", 1)[1]] = int(v["decimals"])
        out = pd.DataFrame([{"token": t, "dec": d} for t, d in {**have, **got}.items()])
        out.to_parquet(OUT / f"liq_{name}_decimals.parquet")
        print(f"decimals {name}: tokens {len(toks)}, had {len(have)}, missing {len(missing)}, resolved now {len(got)}, still unknown {len(missing) - len(got)}", flush=True)


T_ASSET_SRC = "0x22c5b7b2d8561d39f7f210b6b326a1aa69f15311163082308ac4877db6339dc1"
REPLAY_W = 10_000
REPLAY_CFG = {"base": dict(urls=["https://base.gateway.tenderly.co"], w=1000, scan_sources=False)}   # PREREG_LIQ_REPLAY addendum 4


def job_liq_replay_chain(name):
    """PREREG_LIQ_REPLAY_20261121: gap between each sampled liquidation and the most recent price-update log of its collateral/debt feed."""
    import os
    import numpy as np
    stage = os.environ.get("REPLAY_STAGE", "2")
    lkey, native, urls = LIQ_CHAINS[name]
    rc = REPLAY_CFG.get(name, {})
    urls = rc.get("urls", urls)
    win = rc.get("w", REPLAY_W)
    pool = {"arbitrum": "0x794a61358d6845594f94dc1db02a252b5b4814ad", "base": "0xa238dd80c259a72e81d7e4664a9801593f98d1c5"}.get(
        name, "0x794a61358d6845594f94dc1db02a252b5b4814ad")
    smp = pd.read_parquet(OUT / "liq_replay_sample.parquet")
    smp = smp[smp["chain"] == name].reset_index(drop=True)
    if stage == "1":
        smp = smp[smp["s1"]].reset_index(drop=True)
    outp = OUT / f"liq_replay_gaps_s{stage}_{name}.parquet"
    done = pd.read_parquet(outp) if outp.exists() else pd.DataFrame()
    t0 = time.time()
    budget = float(os.environ.get("LIQ_BUDGET_MIN", "150")) * 60
    prov = addr_(rpc(urls, "eth_call", [{"to": pool, "data": SEL_PROVIDER}, "latest"]))
    oracle = addr_(rpc(urls, "eth_call", [{"to": prov, "data": SEL_ORACLE}, "latest"]))
    lo, hi = int(smp["block"].min()) - 1, int(smp["block"].max())
    # oracle source changes over the whole window
    ups, b, step = {}, lo, 10000
    while b <= hi and rc.get("scan_sources", True):
        e = min(b + step - 1, hi)
        try:
            logs = rpc(urls, "eth_getLogs", [{"fromBlock": hex(b), "toBlock": hex(e), "address": oracle, "topics": [T_ASSET_SRC]}])
        except ValueError:
            step = max(500, step // 2)
            continue
        except RuntimeError as ex:
            print(f"  {name}: source-log fetch failed {b}-{e}: {str(ex)[:100]}", flush=True)
            time.sleep(5)
            continue
        for lg in logs:
            a = "0x" + lg["topics"][1][-40:]
            ups.setdefault(a, []).append((int(lg["blockNumber"], 16), "0x" + lg["topics"][2][-40:]))
        b = e + 1
    print(f"{name}: oracle {oracle}, source updates in window for {len(ups)} assets", flush=True)
    srcs, aggs = {}, {}

    def latest_source(a):
        if a not in srcs:
            try:
                srcs[a] = addr_(rpc(urls, "eth_call", [{"to": oracle, "data": "0x92bf2be0" + a[2:].rjust(64, "0")}, "latest"]))
            except Exception:  # noqa: BLE001
                srcs[a] = None
        return srcs[a]

    def source_at(a, blk):
        u = sorted(ups.get(a, []))
        if not u:
            return latest_source(a)
        before = [x for x in u if x[0] <= blk]
        return before[-1][1] if before else None      # event precedes the first in-window update: unresolved

    def aggregator(src):
        if src is None or int(src, 16) == 0:
            return None
        if src not in aggs:
            try:
                aggs[src] = addr_(rpc(urls, "eth_call", [{"to": src, "data": "0x245a7bfc"}, "latest"]))
            except Exception:  # noqa: BLE001
                aggs[src] = None
        return aggs[src]

    def last_update(addrs, blk):
        if not addrs:
            return None
        try:
            logs = rpc(urls, "eth_getLogs", [{"fromBlock": hex(max(0, blk - win)), "toBlock": hex(blk), "address": addrs}])
        except Exception:  # noqa: BLE001
            return "err"
        return max((int(lg["blockNumber"], 16) for lg in logs), default=-1)

    rng = np.random.default_rng(1)
    nulls = rng.integers(lo + 1, hi + 1, size=len(smp))
    rows = [] if done.empty else done.to_dict("records")
    have = {r["tx"] + r["user"] for r in rows}
    for i, r in smp.iterrows():
        if r["tx"] + r["user"] in have:
            continue
        if time.time() - t0 > budget:
            print(f"{name}: BUDGET STOP at row {i}/{len(smp)}", flush=True)
            break
        ac, ad = aggregator(source_at(r["collateral"], int(r["block"]))), aggregator(source_at(r["debt"], int(r["block"])))
        feeds = [x for x in (ac, ad) if x]
        row = dict(chain=name, tx=r["tx"], user=r["user"], block=int(r["block"]), gross=float(r["gross"]), has_c=ac is not None, has_d=ad is not None)
        for tag, blk in (("ev", int(r["block"])), ("null", int(nulls[i]))):
            lu = last_update(feeds, blk)
            row[f"g_{tag}"] = None if lu in (None, "err") else (-1 if lu == -1 else blk - lu)    # -1 = no update in window (infinity)
            row[f"err_{tag}"] = lu == "err"
        for tag, a in (("c", ac), ("d", ad)):
            if a:
                lu = last_update([a], int(r["block"]))
                row[f"g_{tag}"] = None if lu in (None, "err") else (-1 if lu == -1 else int(r["block"]) - lu)
        rows.append(row)
        if len(rows) % 25 == 0:
            pd.DataFrame(rows).to_parquet(outp)
            print(f"  {name}: {len(rows)}/{len(smp)} ({(time.time()-t0)/60:.1f} min)", flush=True)
    pd.DataFrame(rows).to_parquet(outp)
    print(f"{name}: replay stage {stage} wrote {len(rows)} rows", flush=True)


def addr_(ret):
    return "0x" + ret[-40:].lower()


SEL_PROVIDER = "0x0542975c"
SEL_ORACLE = "0xfca513a8"
for _c in ("arbitrum", "base", "avalanche", "polygon", "optimism"):
    globals()[f"job_liq_replay_{_c}"] = (lambda c: (lambda: job_liq_replay_chain(c)))(_c)

MORPHO = "0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb"
T_MORPHO_LIQ = "0xa4946ede45d0c6f06a0f5ce92c9ad3b4751452d2fe0e25010783bcab57a67e41"


def job_liq_morpho(name):
    """PREREG_LIQ_MORPHO_20261121: Morpho Blue `Liquidate` events on Base. name = morphobase (24 months) or morphobase_pilot (last 3 months).
    Same resumable layout as liq_<chain>; final liq_<name>.parquet uses the Aave schema so liquidations_20261120.load() can read it."""
    import os
    import numpy as np
    t0 = time.time()
    budget = float(os.environ.get("LIQ_BUDGET_MIN", "150")) * 60
    urls_all = ["https://base.api.pocket.network", "https://base.gateway.tenderly.co"]
    lkey, native, urls_aave = LIQ_CHAINS["base"]
    SHARDS = {"morphobase_pilot": (21, 24), "morphobase_s0": (0, 12), "morphobase_s1": (12, 18), "morphobase_s2": (18, 24), "morphobase": (0, 24)}
    first, last_i = SHARDS[name]
    sp = _liq_state_path(name)
    st = json.loads(sp.read_text()) if sp.exists() else {}
    if st.get("complete"):
        print(f"{name}: already complete", flush=True)
        return
    base_state = json.loads((OUT / "liq_base_state.json").read_text())
    anchors = base_state["anchors"]
    if "next_block" not in st:
        st.update(anchors=anchors, next_block=anchors[first], logs_done=False, receipts_done=False, complete=False)
    rawp = OUT / f"liq_{name}_raw.parquet"
    rows = pd.read_parquet(rawp).to_dict("records") if rawp.exists() else []

    def glogs(b, e):
        errs = 0
        for u in urls_all:
            try:
                return rpc([u], "eth_getLogs", [{"fromBlock": hex(b), "toBlock": hex(e), "address": MORPHO, "topics": [T_MORPHO_LIQ]}], tries=2)
            except (ValueError, RuntimeError):
                errs += 1
        raise ValueError("no endpoint accepted this window")

    def flush(b):
        pd.DataFrame(rows).to_parquet(rawp)
        st["next_block"] = b
        _liq_save_state(name, st)

    a1 = anchors[last_i] - 1
    if not st["logs_done"]:
        from concurrent.futures import ThreadPoolExecutor
        b, step, last = st["next_block"], 10000, time.time()
        PAR = 6
        month_edge = next((x for x in anchors if x > b), a1 + 1)

        def one(w):
            try:
                return glogs(w[0], w[1])
            except ValueError:
                return None

        def add(logs):
            for lg in logs:
                d = [int(lg["data"][2:][i:i + 64], 16) for i in range(0, len(lg["data"]) - 2, 64)]
                if len(lg["topics"]) != 4 or len(d) < 5:
                    continue
                rows.append({"venue": lg["address"].lower(), "block": int(lg["blockNumber"], 16), "tx": lg["transactionHash"], "mid": lg["topics"][1],
                             "liquidator": "0x" + lg["topics"][2][-40:], "user": "0x" + lg["topics"][3][-40:], "debt_amt": float(d[0]), "coll_amt": float(d[2])})
        while b <= a1:
            if time.time() - t0 > budget:
                flush(b)
                print(f"{name}: BUDGET STOP in log scan at block {b}/{a1}; {len(rows)} events saved", flush=True)
                return
            wins, bb = [], b
            for _ in range(PAR):
                if bb > a1:
                    break
                e = min(bb + step - 1, a1)
                wins.append((bb, e))
                bb = e + 1
            with ThreadPoolExecutor(PAR) as ex:
                res = list(ex.map(one, wins))
            for w, logs in zip(wins, res):
                if logs is None:      # window refused by every endpoint: retry it in 1,000-block pieces
                    for x in range(w[0], w[1] + 1, 1000):
                        sub = one((x, min(x + 999, w[1])))
                        if sub is None:
                            print(f"  {name}: window {x} refused even at 1000; skipping", flush=True)
                            continue
                        add(sub)
                else:
                    add(logs)
            b = bb
            if b >= month_edge or time.time() - last > 600:
                flush(b)
                last = time.time()
                month_edge = next((x for x in anchors if x > b), a1 + 1)
                print(f"  {name}: scanned to block {b}/{a1} ({len(rows)} events, {(time.time()-t0)/60:.0f} min)", flush=True)
        st["logs_done"] = True
        flush(a1 + 1)
        print(f"{name}: log scan complete, {len(rows)} events", flush=True)
    if not rows:
        st["complete"] = True
        _liq_save_state(name, st)
        return
    df = pd.DataFrame(rows).drop_duplicates(["tx", "mid", "user", "block", "coll_amt", "debt_amt"]).reset_index(drop=True)
    mi = np.searchsorted(np.array(anchors), df["block"].values, side="right") - 1
    df["month"] = mi
    ts_edges = np.array(LIQ_MONTHS, dtype=float)
    a = np.array(anchors, dtype=float)
    frac = (df["block"].values - a[mi]) / np.maximum(a[mi + 1] - a[mi], 1)
    df["ts"] = (ts_edges[mi] + frac * (ts_edges[mi + 1] - ts_edges[mi])).astype(int)
    # market tokens
    mk = {}
    for mid in sorted(df["mid"].unique()):
        for k in range(3):
            try:
                w_ = [int(x, 16) for x in [rpc(urls_all, "eth_call", [{"to": MORPHO, "data": "0x2c3c9157" + mid[2:]}, "latest"])[2:][i:i + 64] for i in range(0, 320, 64)]]
                mk[mid] = ("0x" + format(w_[1], "x").rjust(40, "0"), "0x" + format(w_[0], "x").rjust(40, "0"))   # (collateral, loan)
                break
            except Exception:  # noqa: BLE001
                time.sleep(2)
    df["collateral"] = df["mid"].map(lambda m: mk.get(m, (None, None))[0])
    df["debt"] = df["mid"].map(lambda m: mk.get(m, (None, None))[1])
    df = df[df["collateral"].notna()].reset_index(drop=True)
    print(f"{name}: {len(mk)} markets resolved, {len(df)} events with tokens", flush=True)
    # receipts (incremental)
    txs = sorted(df["tx"].unique())
    sampled = len(txs) > LIQ_RECEIPT_CAP
    sample = txs[:: -(-len(txs) // LIQ_RECEIPT_CAP)] if sampled else txs
    rcp = OUT / f"liq_{name}_receipts.parquet"
    have = pd.read_parquet(rcp) if rcp.exists() else pd.DataFrame(columns=["tx", "from", "gas_used", "gas_price", "l1_fee", "status"])
    done = set(have["tx"])
    from concurrent.futures import ThreadPoolExecutor

    def rec(t):
        try:
            r = rpc(urls_all, "eth_getTransactionReceipt", [t])
            return {"tx": t, "from": r["from"].lower(), "gas_used": int(r["gasUsed"], 16), "gas_price": int(r.get("effectiveGasPrice", "0x0"), 16),
                    "l1_fee": int(r.get("l1Fee", "0x0") or "0x0", 16), "status": int(r.get("status", "0x1"), 16)}
        except Exception:  # noqa: BLE001
            return None
    for attempt in range(4):
        todo = [t for t in sample if t not in done]
        if not todo:
            break
        for i in range(0, len(todo), 1500):
            if time.time() - t0 > budget:
                have.to_parquet(rcp)
                print(f"{name}: BUDGET STOP in receipts {len(have)}/{len(sample)}", flush=True)
                return
            with ThreadPoolExecutor(10) as ex:
                got = [x for x in ex.map(rec, todo[i:i + 1500]) if x]
            have = pd.concat([have, pd.DataFrame(got)], ignore_index=True)
            have.to_parquet(rcp)
            done = set(have["tx"])
            print(f"  {name}: receipts {len(have)}/{len(sample)} ({(time.time()-t0)/60:.0f} min)", flush=True)
    missing = len([t for t in sample if t not in done])
    st["receipts_missing"] = missing
    if missing > 0.01 * len(sample):
        _liq_save_state(name, st)
        print(f"{name}: INCOMPLETE receipts {missing}/{len(sample)} missing; re-run", flush=True)
        return
    df = df.merge(have.drop_duplicates("tx"), on="tx", how="left")
    df["receipt_sampled"] = sampled
    toks = sorted(set(df["collateral"]) | set(df["debt"]))
    dec = {}
    for t in toks:
        for k in range(3):
            try:
                dec[t] = int(rpc(urls_all, "eth_call", [{"to": t, "data": "0x313ce567"}, "latest"]), 16)
                break
            except Exception:  # noqa: BLE001
                time.sleep(1.5)
    missing_dec = [t for t in toks if t not in dec]
    for i in range(0, len(missing_dec), 10):
        j = http("https://coins.llama.fi/prices/current/" + urllib.parse.quote(",".join(f"base:{t}" for t in missing_dec[i:i + 10]), safe=",:"))
        for kk, v in ((j or {}).get("coins") or {}).items():
            if "decimals" in v:
                dec[kk.split(":", 1)[1]] = int(v["decimals"])
    df["coll_dec"] = df["collateral"].map(dec)
    df["debt_dec"] = df["debt"].map(dec)
    _liq_prices("base", toks, out_name=name)
    df.drop(columns=["mid"]).to_parquet(OUT / f"liq_{name}.parquet")
    st["complete"] = True
    _liq_save_state(name, st)
    print(f"{name}: COMPLETE {len(df)} events, {len(toks)} tokens, {(time.time()-t0)/60:.0f} min", flush=True)


def job_liq_morpho_replay():
    """PREREG_LIQ_MORPHO_REPLAY_20261121: gap between each sampled Morpho Base liquidation and the latest update of its market oracle's feeds."""
    import os
    import numpy as np
    stage = os.environ.get("REPLAY_STAGE", "2")
    urls = ["https://base.gateway.tenderly.co"]
    win = 1000
    smp = pd.read_parquet(OUT / "liq_morpho_replay_sample.parquet")
    if stage == "1":
        smp = smp[smp["s1"]]
    smp = smp.reset_index(drop=True)
    outp = OUT / f"liq_replay_gaps_s{stage}_morphobase.parquet"
    done = pd.read_parquet(outp) if outp.exists() else pd.DataFrame()
    t0 = time.time()
    budget = float(os.environ.get("LIQ_BUDGET_MIN", "150")) * 60
    cache = {}

    def call(to, data):
        try:
            return rpc(urls, "eth_call", [{"to": to, "data": data}, "latest"], tries=2)
        except Exception:  # noqa: BLE001
            return None

    def feeds_of(mid):
        if mid in cache:
            return cache[mid]
        r = call(MORPHO, "0x2c3c9157" + mid[2:])
        out = None
        if r and len(r) >= 2 + 64 * 5:
            oracle = "0x" + r[2 + 64 * 2: 2 + 64 * 3][-40:]
            addrs, any_ok = [], False
            for sel in ("0xf50a4718", "0xdc53858c", "0x56095e11", "0xacfbd39e"):
                x = call(oracle, sel)
                if x and len(x) >= 66:
                    any_ok = True
                    f = "0x" + x[-40:]
                    if int(f, 16) != 0:
                        ag = call(f, "0x245a7bfc")
                        a = "0x" + ag[-40:] if ag and len(ag) >= 66 and int(ag[-40:], 16) != 0 else f
                        addrs.append(a)
                        # Chainlink proxies change aggregator over time (phases): include every earlier phase aggregator
                        ph = call(f, "0x58303b10")
                        if ph and len(ph) >= 66:
                            for pid in range(1, min(int(ph, 16), 12) + 1):
                                pa = call(f, "0xc1597304" + format(pid, "x").rjust(64, "0"))
                                if pa and len(pa) >= 66 and int(pa[-40:], 16) != 0:
                                    addrs.append("0x" + pa[-40:])
                        addrs[:] = list(dict.fromkeys(addrs))
            out = addrs if any_ok and addrs else None
        cache[mid] = out
        return out

    def last_update(addrs, blk):
        try:
            logs = rpc(urls, "eth_getLogs", [{"fromBlock": hex(max(0, blk - win)), "toBlock": hex(blk), "address": addrs}])
        except Exception:  # noqa: BLE001
            return "err"
        return max((int(lg["blockNumber"], 16) for lg in logs), default=-1)

    lo, hi = int(smp["block"].min()) - 1, int(smp["block"].max())
    nulls = np.random.default_rng(1).integers(lo + 1, hi + 1, size=len(smp))
    rows = [] if done.empty else done.to_dict("records")
    have = {r["tx"] + r["user"] for r in rows}
    for i, r in smp.iterrows():
        if r["tx"] + r["user"] in have:
            continue
        if time.time() - t0 > budget:
            print(f"morphobase: BUDGET STOP at row {i}/{len(smp)}", flush=True)
            break
        addrs = feeds_of(r["mid"]) if isinstance(r["mid"], str) else None
        row = dict(chain="morphobase", tx=r["tx"], user=r["user"], block=int(r["block"]), gross=float(r["gross"]), month=int(r["month"]), mid=r["mid"],
                   has_c=bool(addrs), has_d=False, n_feeds=len(addrs or []))
        for tag, blk in (("ev", int(r["block"])), ("null", int(nulls[i]))):
            lu = last_update(addrs, blk) if addrs else None
            row[f"g_{tag}"] = None if lu in (None, "err") else (-1 if lu == -1 else blk - lu)
            row[f"err_{tag}"] = lu == "err"
        rows.append(row)
        if len(rows) % 25 == 0:
            pd.DataFrame(rows).to_parquet(outp)
            print(f"  morphobase: {len(rows)}/{len(smp)} ({(time.time()-t0)/60:.1f} min)", flush=True)
    pd.DataFrame(rows).to_parquet(outp)
    print(f"morphobase: replay stage {stage} wrote {len(rows)} rows; {sum(1 for v in cache.values() if v)} of {len(cache)} markets resolved", flush=True)


def job_liq_morpho_replay_diag():
    """Why do Morpho market oracles show no feed updates? Prints, per market, oracle/feed/aggregator addresses and log counts in a wide window."""
    urls = ["https://base.gateway.tenderly.co"]
    smp = pd.read_parquet(OUT / "liq_morpho_replay_sample.parquet")
    for mid, g in smp.groupby("mid"):
        r = rpc(urls, "eth_call", [{"to": MORPHO, "data": "0x2c3c9157" + mid[2:]}, "latest"])
        oracle = "0x" + r[2 + 64 * 2: 2 + 64 * 3][-40:]
        feeds = {}
        for nm, sel in (("BASE1", "0xf50a4718"), ("BASE2", "0xdc53858c"), ("QUOTE1", "0x56095e11"), ("QUOTE2", "0xacfbd39e")):
            try:
                x = rpc(urls, "eth_call", [{"to": oracle, "data": sel}, "latest"], tries=1)
                feeds[nm] = "0x" + x[-40:]
            except Exception as e:  # noqa: BLE001
                feeds[nm] = f"ERR {str(e)[:40]}"
        aggs = {}
        for nm, f in feeds.items():
            if f.startswith("0x") and int(f, 16) != 0:
                try:
                    a = rpc(urls, "eth_call", [{"to": f, "data": "0x245a7bfc"}, "latest"], tries=1)
                    aggs[nm] = "0x" + a[-40:]
                except Exception as e:  # noqa: BLE001
                    aggs[nm] = "no aggregator()"
        for month in sorted(g["month"].unique())[:3]:
            ev = g[g["month"] == month].iloc[0]
            blk = int(ev["block"])
            tot = {}
            for nm, a in list(aggs.items()) + [(k + "(proxy)", v) for k, v in feeds.items() if v.startswith("0x") and int(v, 16) != 0]:
                n = 0
                for x in range(0, 20000, 1000):
                    try:
                        n += len(rpc(urls, "eth_getLogs", [{"fromBlock": hex(blk - x - 999), "toBlock": hex(blk - x), "address": a}], tries=1))
                    except Exception:  # noqa: BLE001
                        n += 0
                tot[nm] = n
            print(f"diag market {mid[:10]} events {len(g)} oracle {oracle[:12]} feeds {feeds} aggs {aggs} month {month} blk {blk}: logs in prior 20,000 blocks {tot}", flush=True)


NEWCHAIN_CANDIDATES = {
    "sonic": ["https://rpc.soniclabs.com", "https://sonic-rpc.publicnode.com", "https://sonic.drpc.org"],
    "mantle": ["https://rpc.mantle.xyz", "https://mantle-rpc.publicnode.com", "https://mantle.drpc.org"],
    "linea": ["https://rpc.linea.build", "https://linea-rpc.publicnode.com", "https://linea.drpc.org"],
    "celo": ["https://forno.celo.org", "https://celo-rpc.publicnode.com"],
    "ink": ["https://rpc-gel.inkonchain.com", "https://rpc-qnd.inkonchain.com", "https://ink.drpc.org"],
    "soneium": ["https://rpc.soneium.org"],
    "zksync": ["https://mainnet.era.zksync.io", "https://zksync-era.blockpi.network/v1/rpc/public"],
}


def job_liq_diag4():
    """PREREG_LIQ_NEWCHAINS: which free endpoints serve topic-only LiquidationCall logs, recent and early-2025, and how many logs."""
    for name, urls in NEWCHAIN_CANDIDATES.items():
        for u in urls:
            lab = f"diag4 {name} {u.split('//')[1][:34]}"
            try:
                head = int(rpc([u], "eth_blockNumber", [], tries=1), 16)
            except Exception as e:  # noqa: BLE001
                print(f"{lab}: blockNumber FAIL {str(e)[:90]}", flush=True)
                continue
            marks = {}
            for lbl, ts in (("2025-03-01", int(pd.Timestamp("2025-03-01", tz="UTC").timestamp())), ("2026-08-01", int(pd.Timestamp("2026-08-01", tz="UTC").timestamp()))):
                try:
                    marks[lbl] = _first_block_at([u], ts, 0, head)
                except Exception as e:  # noqa: BLE001
                    marks[lbl] = None
                    print(f"{lab}: header search {lbl} FAIL {str(e)[:80]}", flush=True)
            for lbl, b0 in marks.items():
                if b0 is None:
                    continue
                for span in (1_000, 10_000, 100_000):
                    try:
                        r = rpc([u], "eth_getLogs", [{"fromBlock": hex(b0), "toBlock": hex(b0 + span), "topics": [LIQ_TOPIC]}], tries=1)
                        out = f"{len(r)} logs, contracts {sorted({x['address'][:10] for x in r})[:4]}"
                    except Exception as e:  # noqa: BLE001
                        out = f"ERR {str(e)[:90]}"
                    print(f"{lab} from {lbl} blk {b0} span {span}: {out}", flush=True)
                    time.sleep(1)


T_BUYCOLL = "0xf891b2a411b0e66a5f0a6ff1368670fefa287a13f541eb633a386a1a9cc7046b"


def job_liq_comet(name):
    """PREREG_LIQ_COMET_20261122: Compound v3 BuyCollateral events (topic-only), name = comet_<chain> or comet_<chain>_pilot."""
    import os
    import numpy as np
    from concurrent.futures import ThreadPoolExecutor
    t0 = time.time()
    budget = float(os.environ.get("LIQ_BUDGET_MIN", "150")) * 60
    pilot = name.endswith("_pilot")
    chain = name.split("_")[1]
    lkey, native, urls_c = LIQ_CHAINS[chain]
    urls_all = {"base": ["https://base.api.pocket.network", "https://base.gateway.tenderly.co"],
                "polygon": ["https://poly.api.pocket.network", "https://polygon.gateway.tenderly.co"]}.get(chain, urls_c)
    start_step = {"arbitrum": 20000}.get(chain, 10000)
    sp = _liq_state_path(name)
    st = json.loads(sp.read_text()) if sp.exists() else {}
    if st.get("complete"):
        print(f"{name}: already complete", flush=True)
        return
    anchors = json.loads((OUT / f"liq_{chain}_state.json").read_text())["anchors"]
    first = 21 if pilot else 0
    if "next_block" not in st:
        st.update(anchors=anchors, next_block=anchors[first], logs_done=False, receipts_done=False, complete=False)
    rawp = OUT / f"liq_{name}_raw.parquet"
    rows = pd.read_parquet(rawp).to_dict("records") if rawp.exists() else []
    a1 = anchors[-1] - 1

    def glogs(b, e):
        for u in urls_all:
            try:
                return rpc([u], "eth_getLogs", [{"fromBlock": hex(b), "toBlock": hex(e), "topics": [T_BUYCOLL]}], tries=2)
            except (ValueError, RuntimeError):
                continue
        raise ValueError("no endpoint accepted this window")

    def one(w):
        try:
            return glogs(w[0], w[1])
        except ValueError:
            return None

    def add(logs):
        for lg in logs:
            d = [int(lg["data"][2:][i:i + 64], 16) for i in range(0, len(lg["data"]) - 2, 64)]
            if len(lg["topics"]) != 3 or len(d) < 2:
                continue
            rows.append({"venue": lg["address"].lower(), "block": int(lg["blockNumber"], 16), "tx": lg["transactionHash"], "liquidator": "0x" + lg["topics"][1][-40:],
                         "user": "0x" + lg["topics"][1][-40:], "collateral": "0x" + lg["topics"][2][-40:], "debt_amt": float(d[0]), "coll_amt": float(d[1])})

    def flush(b):
        pd.DataFrame(rows).to_parquet(rawp)
        st["next_block"] = b
        _liq_save_state(name, st)
    if not st["logs_done"]:
        b, step, last, PAR = st["next_block"], start_step, time.time(), 6
        month_edge = next((x for x in anchors if x > b), a1 + 1)
        while b <= a1:
            if time.time() - t0 > budget:
                flush(b)
                print(f"{name}: BUDGET STOP in log scan at block {b}/{a1}; {len(rows)} events saved", flush=True)
                return
            wins, bb = [], b
            for _ in range(PAR):
                if bb > a1:
                    break
                e = min(bb + step - 1, a1)
                wins.append((bb, e))
                bb = e + 1
            with ThreadPoolExecutor(PAR) as ex:
                res = list(ex.map(one, wins))
            for w, logs in zip(wins, res):
                if logs is None:
                    for x in range(w[0], w[1] + 1, 1000):
                        sub = one((x, min(x + 999, w[1])))
                        if sub is None:
                            print(f"  {name}: window {x} refused even at 1000; skipping", flush=True)
                            continue
                        add(sub)
                else:
                    add(logs)
            b = bb
            if b >= month_edge or time.time() - last > 600:
                flush(b)
                last = time.time()
                month_edge = next((x for x in anchors if x > b), a1 + 1)
                print(f"  {name}: scanned to block {b}/{a1} ({len(rows)} events, {(time.time()-t0)/60:.0f} min)", flush=True)
        st["logs_done"] = True
        flush(a1 + 1)
        print(f"{name}: log scan complete, {len(rows)} events", flush=True)
    if not rows:
        st["complete"] = True
        _liq_save_state(name, st)
        return
    df = pd.DataFrame(rows).drop_duplicates(["tx", "venue", "user", "block", "coll_amt", "debt_amt", "collateral"]).reset_index(drop=True)
    mi = np.searchsorted(np.array(anchors), df["block"].values, side="right") - 1
    df["month"] = mi
    ts_edges = np.array(LIQ_MONTHS, dtype=float)
    a = np.array(anchors, dtype=float)
    frac = (df["block"].values - a[mi]) / np.maximum(a[mi + 1] - a[mi], 1)
    df["ts"] = (ts_edges[mi] + frac * (ts_edges[mi + 1] - ts_edges[mi])).astype(int)
    base_tok = {}
    for v in sorted(df["venue"].unique()):
        for k in range(3):
            try:
                base_tok[v] = "0x" + rpc(urls_all, "eth_call", [{"to": v, "data": "0xc55dae63"}, "latest"])[-40:]
                break
            except Exception:  # noqa: BLE001
                time.sleep(2)
    df["debt"] = df["venue"].map(base_tok)
    df = df[df["debt"].notna()].reset_index(drop=True)
    print(f"{name}: {len(base_tok)} Comet contracts with base token, {len(df)} events", flush=True)
    txs = sorted(df["tx"].unique())
    sampled = len(txs) > LIQ_RECEIPT_CAP
    sample = txs[:: -(-len(txs) // LIQ_RECEIPT_CAP)] if sampled else txs
    rcp = OUT / f"liq_{name}_receipts.parquet"
    have = pd.read_parquet(rcp) if rcp.exists() else pd.DataFrame(columns=["tx", "from", "gas_used", "gas_price", "l1_fee", "status"])
    done = set(have["tx"])

    def rec(t):
        try:
            r = rpc(urls_all, "eth_getTransactionReceipt", [t])
            return {"tx": t, "from": r["from"].lower(), "gas_used": int(r["gasUsed"], 16), "gas_price": int(r.get("effectiveGasPrice", "0x0"), 16),
                    "l1_fee": int(r.get("l1Fee", "0x0") or "0x0", 16), "status": int(r.get("status", "0x1"), 16)}
        except Exception:  # noqa: BLE001
            return None
    for attempt in range(4):
        todo = [t for t in sample if t not in done]
        if not todo:
            break
        for i in range(0, len(todo), 1500):
            if time.time() - t0 > budget:
                have.to_parquet(rcp)
                print(f"{name}: BUDGET STOP in receipts {len(have)}/{len(sample)}", flush=True)
                return
            with ThreadPoolExecutor(10) as ex:
                got = [x for x in ex.map(rec, todo[i:i + 1500]) if x]
            have = pd.concat([have, pd.DataFrame(got)], ignore_index=True)
            have.to_parquet(rcp)
            done = set(have["tx"])
            print(f"  {name}: receipts {len(have)}/{len(sample)} ({(time.time()-t0)/60:.0f} min)", flush=True)
    missing = len([t for t in sample if t not in done])
    st["receipts_missing"] = missing
    if missing > 0.01 * len(sample):
        _liq_save_state(name, st)
        print(f"{name}: INCOMPLETE receipts {missing}/{len(sample)} missing; re-run", flush=True)
        return
    df = df.merge(have.drop_duplicates("tx"), on="tx", how="left")
    df["receipt_sampled"] = sampled
    toks = sorted(set(df["collateral"]) | set(df["debt"]))
    dec = {}
    for t in toks:
        for k in range(3):
            try:
                dec[t] = int(rpc(urls_all, "eth_call", [{"to": t, "data": "0x313ce567"}, "latest"]), 16)
                break
            except Exception:  # noqa: BLE001
                time.sleep(1.5)
    miss_dec = [t for t in toks if t not in dec]
    for i in range(0, len(miss_dec), 10):
        j = http("https://coins.llama.fi/prices/current/" + urllib.parse.quote(",".join(f"{lkey}:{t}" for t in miss_dec[i:i + 10]), safe=",:"))
        for kk, v in ((j or {}).get("coins") or {}).items():
            if "decimals" in v:
                dec[kk.split(":", 1)[1]] = int(v["decimals"])
    df["coll_dec"] = df["collateral"].map(dec)
    df["debt_dec"] = df["debt"].map(dec)
    _liq_prices(chain, toks, out_name=name)
    df.to_parquet(OUT / f"liq_{name}.parquet")
    st["complete"] = True
    _liq_save_state(name, st)
    print(f"{name}: COMPLETE {len(df)} events, {len(toks)} tokens, {(time.time()-t0)/60:.0f} min", flush=True)


T_ABSORB = "0x9850ab1af75177e4a9201c65a2cf7976d5d28e40ef63494b44366f86b2f9412e"


def job_liq_comet_timing():
    """PREREG_LIQ_COMET addendum 1: are Comet buys in the same transaction as the absorb? sample of buy txs on the biggest venue per chain."""
    import numpy as np
    for chain in ("base", "arbitrum"):
        f = OUT / f"liq_comet_{chain}.parquet"
        if not f.exists():
            continue
        df = pd.read_parquet(f)
        gv = df.groupby("venue").size().sort_values(ascending=False)
        # biggest by value is not stored here: use the venue with the most events among those with > 50 events and the largest sum of debt_amt
        ven = gv.index[0]     # most events = the largest-gross venue on both chains (Base 0xb125e6.. 1,204 events; Arbitrum 0x9c4ec7.. 1,411 events: see the stage-2 output)
        txs = sorted(df[df["venue"] == ven]["tx"].unique())
        k = max(1, int(np.ceil(len(txs) / 300)))
        sample = txs[::k][:300]
        urls = {"base": ["https://base.api.pocket.network", "https://base.gateway.tenderly.co"]}.get(chain, LIQ_CHAINS[chain][2])
        n_abs, n_ok, buys = 0, 0, []
        for t in sample:
            try:
                r = rpc(urls, "eth_getTransactionReceipt", [t])
            except Exception:  # noqa: BLE001
                continue
            if not r:
                continue
            n_ok += 1
            logs = r.get("logs", [])
            ab = any(lg["topics"] and lg["topics"][0] == T_ABSORB and lg["address"].lower() == ven for lg in logs)
            n_abs += ab
            buys.append(sum(1 for lg in logs if lg["topics"] and lg["topics"][0] == T_BUYCOLL and lg["address"].lower() == ven))
        print(f"timing {chain} venue {ven[:12]} events {int((df['venue'] == ven).sum())} txs {len(txs)} sampled {n_ok}: also absorb in same tx {n_abs} ({100 * n_abs / max(n_ok, 1):.1f}%); mean buy logs per tx {np.mean(buys) if buys else 0:.2f}", flush=True)


def _liq_state_path(name):
    return OUT / f"liq_{name}_state.json"


def _liq_save_state(name, st):
    _liq_state_path(name).write_text(json.dumps(st, indent=1))


def job_liq_chain(name):
    """Resumable. Progress files in data/public/: liq_<name>_state.json, _raw.parquet (events),
    _receipts.parquet; final liq_<name>.parquet + _prices.parquet written only when complete.
    Env LIQ_BUDGET_MIN = stop cleanly after that many minutes (state keeps the last block reached)."""
    import os
    from concurrent.futures import ThreadPoolExecutor
    import numpy as np
    t0 = time.time()
    deadline = t0 + float(os.environ.get("LIQ_BUDGET_MIN", "0") or 0) * 60 if os.environ.get("LIQ_BUDGET_MIN") else None
    over = lambda: deadline is not None and time.time() > deadline  # noqa: E731
    pilot = name.endswith("_pilot")
    base = name[:-6] if pilot else name
    first = 21 if pilot else 0
    lkey, native, urls = LIQ_CHAINS[base]
    if os.environ.get("LIQ_USE_ETHERSCAN") == "1":
        urls = [f"https://api.etherscan.io/v2/api?chainid={LIQ_ES_ID[name]}"]
        print(f"{name}: using Etherscan V2 (chainid {LIQ_ES_ID[name]})", flush=True)
    OUT.mkdir(parents=True, exist_ok=True)
    sp = _liq_state_path(name)
    st = json.loads(sp.read_text()) if sp.exists() else {}
    if st.get("complete") and "receipts_missing" not in st and not st.get("legacy"):
        print(f"{name}: marked complete by older code without a receipt check; re-checking receipts", flush=True)
        st.update(complete=False, receipts_done=False)
        _liq_save_state(name, st)
    if st.get("complete"):
        print(f"{name}: already complete", flush=True)
        return
    if not st and (OUT / f"liq_{name}.parquet").exists() and (OUT / f"liq_{name}_prices.parquet").exists():
        print(f"{name}: legacy complete files found; marking complete", flush=True)
        _liq_save_state(name, {"complete": True, "logs_done": True, "receipts_done": True, "legacy": True})
        return
    if "anchors" not in st:
        head = int(rpc(urls, "eth_blockNumber", []), 16)
        anchors, lo = [], 0
        for ts in LIQ_MONTHS:
            lo = _first_block_at(urls, ts, lo, head)
            anchors.append(lo)
        st.update(anchors=anchors, next_block=anchors[first], logs_done=False, receipts_done=False, complete=False)
        _liq_save_state(name, st)
    anchors = st["anchors"]
    print(f"{name}: month anchors {anchors[0]}..{anchors[-1]}, resume at block {st['next_block']}", flush=True)
    rawp = OUT / f"liq_{name}_raw.parquet"
    rows = pd.read_parquet(rawp).to_dict("records") if rawp.exists() else []
    a1 = anchors[-1] - 1

    def flush(b):
        pd.DataFrame(rows).to_parquet(rawp)
        st["next_block"] = b
        st["last_flush"] = time.strftime("%FT%TZ", time.gmtime())
        _liq_save_state(name, st)

    # ---- phase 1: logs
    if not st["logs_done"]:
        b, step, last_flush, cap = st["next_block"], 20000, time.time(), 2_000_000
        month_edge = next((x for x in anchors if x > b), a1 + 1)
        PAR = 6

        def fetch(w):
            try:
                return ("ok", rpc(urls, "eth_getLogs", [{"fromBlock": hex(w[0]), "toBlock": hex(w[1]), "topics": [LIQ_TOPIC]}]))
            except ValueError:
                return ("range", None)
            except RuntimeError as ex:
                return ("err", str(ex))
        while b <= a1:
            if over():
                flush(b)
                print(f"{name}: BUDGET STOP in log scan at block {b} (window {anchors[0]}..{a1}); {len(rows)} events saved", flush=True)
                return
            wins, bb = [], b
            for _ in range(PAR):
                if bb > a1:
                    break
                e = min(bb + step - 1, a1)
                wins.append((bb, e))
                bb = e + 1
            with ThreadPoolExecutor(PAR) as ex:
                results = list(ex.map(fetch, wins))
            nlogs = 0
            for w, (kind, payload) in zip(wins, results):
                if kind == "ok":
                    for lg in payload:
                        d = lg["data"][2:]
                        if len(lg["topics"]) != 4 or len(d) < 256:  # same topic0 on a non-Aave-ABI contract: skip, count
                            st["skipped_logs"] = st.get("skipped_logs", 0) + 1
                            continue
                        rows.append({"venue": lg["address"].lower(), "block": int(lg["blockNumber"], 16), "tx": lg["transactionHash"],
                                     "collateral": "0x" + lg["topics"][1][-40:], "debt": "0x" + lg["topics"][2][-40:],
                                     "user": "0x" + lg["topics"][3][-40:], "debt_amt": float(int(d[0:64], 16)),
                                     "coll_amt": float(int(d[64:128], 16)), "liquidator": "0x" + d[128:192][-40:]})
                    nlogs += len(payload)
                    b = w[1] + 1
                    continue
                if kind == "range":
                    if step <= 500:
                        print(f"  {name}: window {w[0]}-{w[1]} refused even at {step} blocks; skipping", flush=True)
                        b = w[1] + 1
                        continue
                    step = max(500, step // 2)
                    cap = step
                else:
                    print(f"  {name}: getLogs failed {w[0]}-{w[1]}: {str(payload)[:150]}", flush=True)
                    st["getlogs_fails"] = st.get("getlogs_fails", 0) + 1
                    if st["getlogs_fails"] >= 12 and not rows:
                        flush(b)
                        print(f"{name}: ABORT: 12 getLogs failures and no events yet; no working endpoint. Stopped at block {b}", flush=True)
                        return
                    if step > 500:
                        step = max(500, step // 4)
                    else:
                        b = w[1] + 1
                break
            else:
                if nlogs < 300 * len(wins):
                    step = min(step * 2, cap)
                elif nlogs > 3000 * len(wins):
                    step = max(500, step // 2)
                    cap = min(cap, step * 2)
            if b >= month_edge or time.time() - last_flush > 600:
                flush(b)
                last_flush = time.time()
                month_edge = next((x for x in anchors if x > b), a1 + 1)
                print(f"  {name}: scanned to block {b}/{a1} ({len(rows)} events, {(time.time()-t0)/60:.0f} min)", flush=True)
        st["logs_done"] = True
        flush(a1 + 1)
        print(f"{name}: log scan complete, {len(rows)} events", flush=True)
    if not rows:
        st["complete"] = True
        _liq_save_state(name, st)
        return
    df = pd.DataFrame(rows).drop_duplicates(["tx", "venue", "user", "block", "coll_amt", "debt_amt"]).reset_index(drop=True)
    mi = np.searchsorted(np.array(anchors), df["block"].values, side="right") - 1
    df["month"] = mi
    ts_edges = np.array(LIQ_MONTHS, dtype=float)
    a = np.array(anchors, dtype=float)
    frac = (df["block"].values - a[mi]) / np.maximum(a[mi + 1] - a[mi], 1)
    df["ts"] = (ts_edges[mi] + frac * (ts_edges[mi + 1] - ts_edges[mi])).astype(int)
    # ---- phase 2: receipts (incremental)
    txs = sorted(df["tx"].unique())
    sampled = len(txs) > LIQ_RECEIPT_CAP
    sample = txs[:: -(-len(txs) // LIQ_RECEIPT_CAP)] if sampled else txs
    rcp = OUT / f"liq_{name}_receipts.parquet"
    have = pd.read_parquet(rcp) if rcp.exists() else pd.DataFrame(columns=["tx", "from", "gas_used", "gas_price", "l1_fee", "status"])
    done = set(have["tx"])
    todo = [t for t in sample if t not in done]
    print(f"{name}: receipts: {len(done)} cached, {len(todo)} to fetch (sampled={sampled})", flush=True)

    def rec(t):
        try:
            r = rpc(urls, "eth_getTransactionReceipt", [t])
            return {"tx": t, "from": r["from"].lower(), "gas_used": int(r["gasUsed"], 16),
                    "gas_price": int(r.get("effectiveGasPrice", "0x0"), 16), "l1_fee": int(r.get("l1Fee", "0x0") or "0x0", 16),
                    "status": int(r.get("status", "0x1"), 16)}
        except Exception:  # noqa: BLE001
            return None
    for attempt in range(4):
        todo = [t for t in sample if t not in done]
        if not todo:
            break
        if attempt:
            print(f"{name}: retry pass {attempt}: {len(todo)} receipts missing", flush=True)
            time.sleep(20 * attempt)
        for i in range(0, len(todo), 1500):
            if over():
                have.to_parquet(rcp)
                print(f"{name}: BUDGET STOP in receipts: {len(have)}/{len(sample)} receipts saved (logs complete)", flush=True)
                st["receipts_done"] = False
                _liq_save_state(name, st)
                return
            with ThreadPoolExecutor(10) as ex:
                got = [x for x in ex.map(rec, todo[i:i + 1500]) if x]
            have = pd.concat([have, pd.DataFrame(got)], ignore_index=True)
            have.to_parquet(rcp)
            done = set(have["tx"])
            print(f"  {name}: receipts {len(have)}/{len(sample)} ({(time.time()-t0)/60:.0f} min)", flush=True)
    missing = len([t for t in sample if t not in done])
    st["receipts_missing"] = missing
    if missing > 0.01 * len(sample):
        st["receipts_done"] = False
        _liq_save_state(name, st)
        print(f"{name}: INCOMPLETE receipts: {missing}/{len(sample)} still missing after retries; re-run to continue", flush=True)
        return
    print(f"{name}: receipts missing after retries: {missing}/{len(sample)} (<=1%, accepted; gas imputed, bot 'unknown')", flush=True)
    st["receipts_done"] = True
    # ---- phase 3: assemble (decimals, prices)
    df = df.merge(have.drop_duplicates("tx"), on="tx", how="left")
    df["receipt_sampled"] = sampled
    toks = sorted(set(df["collateral"]) | set(df["debt"]))
    dec = {}
    for t in toks:
        try:
            dec[t] = int(rpc(urls, "eth_call", [{"to": t, "data": "0x313ce567"}, "latest"]), 16)
        except Exception:  # noqa: BLE001
            dec[t] = None
    df["coll_dec"] = df["collateral"].map(dec)
    df["debt_dec"] = df["debt"].map(dec)
    _liq_prices(base, toks, out_name=name)
    df.to_parquet(OUT / f"liq_{name}.parquet")
    st["complete"] = True
    _liq_save_state(name, st)
    print(f"{name}: COMPLETE {len(df)} events, {(time.time()-t0)/60:.0f} min", flush=True)


def job_liq_diag():
    """Which endpoints answer which getLogs shapes (topic-only vs address, window sizes)."""
    pools = {"base": "0xA238Dd80C259a72e81d7e4664a9801593F98d1c5", "bnb": "0x6807dc923806fE8Fd134338EABCA509979a7e0cB",
             "gnosis": "0xb50201558B00496A145fE76f7424749556E326D8", "scroll": "0x11fCfe756c05AD438e312a7fd934381537D3cFfe",
             "metis": "0x90df02551bB792286e8D4f13E0e357b4Bf1D6a57"}
    for name, (_, _, urls) in LIQ_CHAINS.items():
        for u in urls:
            try:
                head = int(rpc([u], "eth_blockNumber", [], tries=1), 16)
            except Exception as e:  # noqa: BLE001
                print(f"diag {name} {u}: blockNumber FAIL {str(e)[:120]}", flush=True)
                continue
            old = head - 3_000_000
            for label, base_b in (("recent", head - 200_000), ("old_2yr_ish", max(1, head - 55_000_000 if name in ("base", "optimism", "arbitrum") else head - 20_000_000))):
                for span in (1_000, 10_000, 100_000):
                    for filt in ("topic", "addr"):
                        f_ = {"fromBlock": hex(base_b), "toBlock": hex(base_b + span), "topics": [LIQ_TOPIC]}
                        addr = pools.get(name, "0x794a61358D6845594F94dc1DB02A252b5b4814aD")
                        if filt == "addr":
                            f_["address"] = addr
                        try:
                            r = rpc([u], "eth_getLogs", [f_], tries=1)
                            out = f"{len(r)} logs"
                        except Exception as e:  # noqa: BLE001
                            out = f"ERR {str(e)[:110]}"
                        print(f"diag {name} {u.split('//')[1][:32]} {label} span {span} {filt}: {out}", flush=True)
                        time.sleep(0.3)
            try:
                nb = _block_ts([u], max(1, head - 55_000_000))
                print(f"diag {name} {u.split('//')[1][:32]} old block header ok ts {nb}", flush=True)
            except Exception as e:  # noqa: BLE001
                print(f"diag {name} {u.split('//')[1][:32]} old block header FAIL {str(e)[:100]}", flush=True)


LIQ_CANDIDATES = {
    "bnb3": ["https://bsc.gateway.tenderly.co", "https://bnb.api.onfinality.io/public", "https://endpoints.omniatech.io/v1/bsc/mainnet/public",
             "https://bsc.rpc.blxrbdn.com", "https://bsc-mainnet.rpc.grove.city/v1/01fdb492", "https://api.zan.top/bsc-mainnet", "https://bsc-pokt.nodies.app"],
    "avalanche3": ["https://avalanche.gateway.tenderly.co", "https://avax.api.onfinality.io/public/ext/bc/C/rpc",
                   "https://endpoints.omniatech.io/v1/avax/mainnet/public", "https://api.zan.top/avax-mainnet/ext/bc/C/rpc", "https://avax-pokt.nodies.app/ext/bc/C/rpc"],
    "base_old": ["https://base.drpc.org", "https://1rpc.io/base", "https://base.meowrpc.com", "https://base.gateway.tenderly.co",
             "https://base.api.pocket.network", "https://base.blockpi.network/v1/rpc/public", "https://developer-access-mainnet.base.org"],
    "polygon_old": ["https://polygon.drpc.org", "https://1rpc.io/matic", "https://polygon.meowrpc.com", "https://poly.api.pocket.network",
                "https://polygon.gateway.tenderly.co", "https://polygon.llamarpc.com", "https://polygon-bor-rpc.publicnode.com"],
    "bnb_old": ["https://bsc.drpc.org", "https://1rpc.io/bnb", "https://bsc.meowrpc.com", "https://bsc-dataseed1.defibit.io",
            "https://bsc-dataseed1.ninicoin.io", "https://binance.llamarpc.com", "https://bsc.api.pocket.network"],
    "avalanche_old": ["https://avalanche.drpc.org", "https://1rpc.io/avax/c", "https://avalanche.public-rpc.com",
                  "https://avax.meowrpc.com", "https://avalanche.api.pocket.network"],
}


def job_liq_diag2():
    """Candidate endpoints for chains where the first diag found none with deep history."""
    back = {"bnb3": 140_000_000, "avalanche3": 31_500_000}  # ~23 months of blocks
    for name, urls in LIQ_CANDIDATES.items():
        if name not in back:
            continue
        for u in urls:
            lab = f"diag2 {name} {u.split('//')[1][:40]}"
            try:
                head = int(rpc([u], "eth_blockNumber", [], tries=1), 16)
            except Exception as e:  # noqa: BLE001
                print(f"{lab}: blockNumber FAIL {str(e)[:100]}", flush=True)
                continue
            for label, b0 in (("recent", head - 100_000), ("23mo_ago", head - back[name])):
                for span in (1_000, 5_000, 10_000):
                    try:
                        r = rpc([u], "eth_getLogs", [{"fromBlock": hex(b0), "toBlock": hex(b0 + span), "topics": [LIQ_TOPIC]}], tries=1)
                        out = f"{len(r)} logs"
                    except Exception as e:  # noqa: BLE001
                        out = f"ERR {str(e)[:100]}"
                    print(f"{lab} {label} span {span} topic-only: {out}", flush=True)
                    time.sleep(1.5)

def job_liq_probe():
    """Reachability probe for Solana lenders (Kamino/MarginFi/Save/Drift): no data pulled, just what answers."""
    sol = ["https://api.mainnet-beta.solana.com", "https://solana-rpc.publicnode.com"]
    progs = {"kamino_klend": "KLend2g3cP87fffoy8q1mQqGKjrxjC8boSyAYavgmjD", "marginfi": "MFv2hWf31Z9kbCa1snEPYctwafyhdvnV7FZnsebVacA",
             "save_solend": "So1endDq2YkqhipRh3WViPa8hdiSpxWy6z3Z6tMCpAo", "drift": "dRiftyHA39MWEi3m9aunc5MzRF1JYuBsbn6VPcn33UH"}
    for n, pid in progs.items():
        try:
            r = rpc(sol, "getSignaturesForAddress", [pid, {"limit": 1000}])
            print(f"probe {n}: {len(r)} signatures; oldest of newest 1000 = {pd.to_datetime(r[-1].get('blockTime'), unit='s') if r else None}", flush=True)
        except Exception as e:  # noqa: BLE001
            print(f"probe {n}: failed {str(e)[:150]}", flush=True)
    print("probe note: signatures include every transaction of the program, not only liquidations; "
          "24 months of these via public RPC is not feasible, so Solana is judged on this probe only.", flush=True)


LIQ_ES_ID = {"base": 8453, "polygon": 137, "bnb": 56, "avalanche": 43114}


def _liq_es_job(c):
    def run():
        import os
        os.environ["LIQ_USE_ETHERSCAN"] = "1"
        job_liq_chain(c)
    return run


def job_liq_secretcheck():
    import os
    print("ETHERSCAN_API_KEY present:", bool(os.environ.get("ETHERSCAN_API_KEY")), flush=True)
    if os.environ.get("ETHERSCAN_API_KEY"):
        for n, cid in LIQ_ES_ID.items():
            try:
                r = rpc([f"https://api.etherscan.io/v2/api?chainid={cid}"], "eth_blockNumber", [], tries=1)
                print(f"etherscan {n}: eth_blockNumber ok ({int(r, 16)})", flush=True)
            except Exception as e:  # noqa: BLE001
                print(f"etherscan {n}: {str(e)[:160]}", flush=True)
            try:
                lg = rpc([f"https://api.etherscan.io/v2/api?chainid={cid}"], "eth_getLogs", [{"fromBlock": hex(1), "toBlock": hex(1), "topics": [LIQ_TOPIC]}], tries=1)
                print(f"etherscan {n}: getLogs ok ({len(lg)})", flush=True)
            except Exception as e:  # noqa: BLE001
                print(f"etherscan {n}: getLogs {str(e)[:160]}", flush=True)


for _c in LIQ_CHAINS:
    globals()[f"job_liq_{_c}"] = (lambda c: (lambda: job_liq_chain(c)))(_c)


def job_liq_flashblocks():
    """PREREG_LIQ_FLASHBLOCKS_20261124: poll pending vs latest on the free public Base endpoint for 120 s."""
    u = "https://mainnet.base.org"
    n = err = ahead = 0
    txs = {}
    t0 = time.time()
    while time.time() - t0 < 120:
        n += 1
        try:
            p = rpc([u], "eth_getBlockByNumber", ["pending", False], tries=1)
            l = rpc([u], "eth_getBlockByNumber", ["latest", False], tries=1)
            pn, ln = int(p["number"], 16), int(l["number"], 16)
            ahead += pn == ln + 1
            txs.setdefault(pn, set()).add(len(p["transactions"]))
        except Exception as e:  # noqa: BLE001
            err += 1
            if err <= 3:
                print("err", str(e)[:150], flush=True)
        time.sleep(0.15)
    multi = sum(1 for v in txs.values() if len(v) >= 3)
    print(f"flashblocks probe: polls {n} errors {err} ({100*err/max(n,1):.0f}%) pending==latest+1 in {ahead} ({100*ahead/max(n-err,1):.0f}%) blocks with >=3 distinct pending tx counts {multi} of {len(txs)}")
    print("max distinct counts in one block:", max([len(v) for v in txs.values()] + [0]))


def job_liq_basedocs():
    """Fetch public Base docs pages (sandbox cannot resolve docs.base.org); print lines mentioning flashblocks."""
    for u in ("https://docs.base.org/base-chain/flashblocks/faq.md", "https://docs.base.org/base-chain/api-reference/rpc-overview.md"):
        try:
            req = urllib.request.Request(u, headers=UA)
            t = urllib.request.urlopen(req, timeout=60).read().decode()
            print("==", u, len(t), flush=True)
            for ln in t.splitlines():
                if any(k in ln.lower() for k in ("flashblock", "pending", "rate limit", "stopped", "no longer")):
                    print(ln[:400], flush=True)
        except Exception as e:  # noqa: BLE001
            print("ERR", u, str(e)[:120], flush=True)


JOBS = {"liq_basedocs": job_liq_basedocs, "liq_flashblocks": job_liq_flashblocks, "ipo2": job_ipo2, "iponews": job_iponews, "ipo": job_ipo, "myxsnap": job_myxsnap, "batch2": job_batch2, "hl2023d": job_hl2023d, "hl2023": job_hl2023, "hl": job_hl, "llama_lend": job_llama_lend, "llama_pools": job_llama_pools,
        "llama_prices": job_llama_prices, "poly": job_poly,
        "liq_probe": job_liq_probe, "liq_diag": job_liq_diag, "liq_diag2": job_liq_diag2, "liq_diag3": job_liq_diag2, "liq_diag4": job_liq_diag4, "liq_comet_timing": job_liq_comet_timing, "liq_secretcheck": job_liq_secretcheck, "liq_pxdiag": job_liq_pxdiag, "liq_replay_morphobase": job_liq_morpho_replay, "liq_morpho_replay_diag": job_liq_morpho_replay_diag, "liq_morphobase_pilot": lambda: job_liq_morpho("morphobase_pilot"), "liq_morphobase": lambda: job_liq_morpho("morphobase"), "liq_morphobase_s0": lambda: job_liq_morpho("morphobase_s0"),
        "liq_morphobase_s1": lambda: job_liq_morpho("morphobase_s1"), "liq_morphobase_s2": lambda: job_liq_morpho("morphobase_s2"), **{f"liq_replay_{c}": globals()[f"job_liq_replay_{c}"] for c in ("arbitrum", "base", "avalanche", "polygon", "optimism")}, "liq_decimals": job_liq_decimals, **{f"liq_prices_{c}": _liq_prices_job(c) for c in LIQ_CHAINS}, **{f"liq_{c}_es": _liq_es_job(c) for c in LIQ_ES_ID}, **{f"liq_{c}": globals()[f"job_liq_{c}"] for c in LIQ_CHAINS}}


JOBS.update({f"liq_comet_{c}{suf}": (lambda n: (lambda: job_liq_comet(n)))(f"comet_{c}{suf}") for c in ("base", "arbitrum", "optimism", "polygon") for suf in ("", "_pilot")})
JOBS.update({f"liq_{c}_pilot": (lambda c: (lambda: job_liq_chain(c + "_pilot")))(c) for c in NEW_CHAINS})


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

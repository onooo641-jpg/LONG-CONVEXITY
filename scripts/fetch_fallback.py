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


STABLE = {"USDC", "USDT", "DAI", "USDE", "USDS", "GHO", "CRVUSD", "FRAX", "LUSD", "PYUSD", "RLUSD", "USD0", "USDT0", "USDC.E", "USDG",
          "FDUSD", "TUSD", "USDP", "USR", "AUSD", "USDBC", "BOLD", "DOLA", "FRXUSD", "USD1", "USDTB", "SUSDE", "SUSDS", "USDX", "USDA"}


def job_lendborrow():
    """#209: borrowable stablecoin pools: current listing + daily supply and borrow histories."""
    OUT.mkdir(parents=True, exist_ok=True)
    lb = pd.DataFrame(get("https://yields.llama.fi/lendBorrow") or [])
    pools = pd.DataFrame((get("https://yields.llama.fi/pools") or {}).get("data", []))
    m = lb.merge(pools[["pool", "chain", "project", "symbol", "tvlUsd"]], on="pool", how="inner")
    m = m[(m["borrowable"] == True) & m["symbol"].str.upper().isin(STABLE) & (pd.to_numeric(m["tvlUsd"]) >= 5e6)]  # noqa: E712
    print(f"borrowable stable pools with TVL >= $5M: {len(m)} (of {len(lb)} lendBorrow rows)", flush=True)
    keep = [c for c in ("pool", "chain", "project", "symbol", "tvlUsd", "ltv", "apyBaseBorrow", "apyRewardBorrow") if c in m]
    m[keep].to_parquet(OUT / "borrowloop_pools.parquet", index=False)
    rows = []
    for i, p in enumerate(m["pool"]):
        b = {pd.Timestamp(x["timestamp"]).floor("D"): x for x in (get(f"https://yields.llama.fi/chartLendBorrow/{p}") or {}).get("data", [])}
        sup = {pd.Timestamp(x["timestamp"]).floor("D"): x for x in (get(f"https://yields.llama.fi/chart/{p}") or {}).get("data", [])}
        for d in sorted(set(b) & set(sup)):
            rows.append({"pool": p, "day": d, "apyBase": sup[d].get("apyBase"), "apyReward": sup[d].get("apyReward"),
                         "tvlUsd": sup[d].get("tvlUsd"), "apyBaseBorrow": b[d].get("apyBaseBorrow"),
                         "apyRewardBorrow": b[d].get("apyRewardBorrow"), "totalBorrowUsd": b[d].get("totalBorrowUsd")})
        if i % 25 == 0:
            print(f"  {i}/{len(m)}", flush=True)
        time.sleep(0.4)
    df = pd.DataFrame(rows)
    for c in df.columns[2:]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df.to_parquet(OUT / "borrowloop_charts.parquet", index=False)
    print(f"charts: {df['pool'].nunique() if len(df) else 0} pools, {len(df)} rows", flush=True)



def job_pendle_probe():
    """#211 structure probe: endpoints and field NAMES only (no values printed)."""
    for u in ["https://api-v2.pendle.finance/core/v1/chains",
              "https://api-v2.pendle.finance/core/v1/1/markets?limit=2&skip=0",
              "https://api-v2.pendle.finance/core/v1/1/markets/active",
              "https://api-v2.pendle.finance/core/v1/1/markets/inactive",
              "https://api-v2.pendle.finance/core/v2/markets/all?limit=2"]:
        d = get(u)
        if d is None:
            print(f"PROBE {u}: no answer", flush=True)
            continue
        def shape(x, depth=0):
            if isinstance(x, dict):
                return "{" + ", ".join(f"{k}:{shape(v, depth + 1) if depth < 1 else type(v).__name__}" for k, v in list(x.items())[:25]) + "}"
            if isinstance(x, list):
                return f"list[{len(x)}] of {shape(x[0], depth) if x else 'empty'}"
            return type(x).__name__
        print(f"PROBE {u}: {shape(d)[:1500]}", flush=True)
        if isinstance(d, dict):
            items = d.get("results") or d.get("markets") or d.get("data")
            if isinstance(items, list) and items and isinstance(items[0], dict):
                print(f"  item keys: {sorted(items[0].keys())}", flush=True)

FAMILY = {"ETH": ["STETH", "WSTETH", "RETH", "CBETH", "WEETH", "EZETH", "RSETH", "METH", "SFRXETH", "OSETH", "WBETH", "ETHX", "WETH", "ETH"],
          "SOL": ["SOL", "JITOSOL", "MSOL", "JUPSOL", "BSOL", "INF", "BNSOL", "HSOL"], "HYPE": ["HYPE", "KHYPE", "STHYPE", "WHYPE"],
          "BTC": ["BTC", "WBTC", "CBBTC", "TBTC", "LBTC"], "AVAX": ["AVAX", "SAVAX", "WAVAX"], "BNB": ["BNB", "SLISBNB", "BNBX", "WBNB"],
          # #214 governance tokens with staking / vote-escrow yields (hedgeable on HL)
          "CRV": ["CRV", "CVXCRV", "SDCRV", "YCRV", "ST-YCRV", "SCRVUSD", "ASDCRV"], "AAVE": ["AAVE", "STKAAVE"],
          "ENA": ["ENA", "SENA"], "PENDLE": ["PENDLE", "VEPENDLE", "SPENDLE", "MPENDLE", "PENPIE", "EQBPENDLE", "SDPENDLE"],
          "LDO": ["LDO"], "MORPHO": ["MORPHO"], "AERO": ["AERO", "VEAERO"], "FXS": ["FXS", "CVXFXS", "SDFXS"],
          "PAXG": ["PAXG", "XAUT"]}
TOK2COIN = {t: c for c, ts in FAMILY.items() for t in ts}
YSTABLE = {"SUSDE": "USD", "SUSDS": "USD", "SDAI": "USD", "SFRXUSD": "USD"}


def _protocol_categories():
    d = get("https://api.llama.fi/protocols") or []
    return {str(p.get("slug", "")).lower(): p.get("category") for p in d}


def job_hedged():
    """#212/#213: mapped single-exposure non-stable pools (TVL >= $20M) + histories; HL funding incl. HYPE."""
    OUT.mkdir(parents=True, exist_ok=True)
    pools = pd.DataFrame((get("https://yields.llama.fi/pools") or {}).get("data", []))
    pools["tvlUsd"] = pd.to_numeric(pools["tvlUsd"], errors="coerce")
    pools["coin"] = pools["symbol"].str.upper().map(TOK2COIN)
    u = pools[(pools["exposure"] == "single") & (pools["stablecoin"] != True) & pools["coin"].notna() & (pools["tvlUsd"] >= (pools["coin"].isin(["CRV","AAVE","ENA","PENDLE","LDO","MORPHO","AERO","FXS"]).map({True: 2e6, False: 20e6})))].copy()  # noqa: E712
    cats = _protocol_categories()
    u["category"] = u["project"].str.lower().map(cats)
    print(f"hedged universe: {len(u)} pools; categories {u['category'].value_counts().head(8).to_dict()}", flush=True)
    u[["pool", "chain", "project", "symbol", "coin", "category", "tvlUsd"]].to_parquet(OUT / "hedged_pools.parquet", index=False)
    rows = []
    for i, p in enumerate(u["pool"]):
        for x in (get(f"https://yields.llama.fi/chart/{p}") or {}).get("data", []):
            rows.append({"pool": p, "ts": x.get("timestamp"), "tvlUsd": x.get("tvlUsd"), "apyBase": x.get("apyBase"), "apyReward": x.get("apyReward")})
        time.sleep(0.3)
    ch = pd.DataFrame(rows)
    ch["ts"] = pd.to_datetime(ch["ts"], utc=True)
    for c in ("tvlUsd", "apyBase", "apyReward"):
        ch[c] = pd.to_numeric(ch[c], errors="coerce")
    ch.to_parquet(OUT / "hedged_charts.parquet", index=False)
    print(f"hedged charts: {ch['pool'].nunique()} pools, {len(ch)} rows", flush=True)
    f = []
    for c in FAMILY:
        r = _hl(c)
        print(f"  hl funding {c}: {len(r)}", flush=True)
        f += [{"coin": c, "t": t, "rate": v} for t, v in r]
    pd.DataFrame(f).to_parquet(OUT / "hedged_hlfunding.parquet", index=False)


def job_lendborrow_corr():
    """#219: lendBorrow rows for LSTs / yield-bearing stables and their base assets, with supply and borrow histories."""
    OUT.mkdir(parents=True, exist_ok=True)
    lb = pd.DataFrame(get("https://yields.llama.fi/lendBorrow") or [])
    pools = pd.DataFrame((get("https://yields.llama.fi/pools") or {}).get("data", []))
    m = lb.merge(pools[["pool", "chain", "project", "symbol", "tvlUsd"]], on="pool", how="inner")
    sym = m["symbol"].str.upper()
    want = set(TOK2COIN) | set(YSTABLE) | {"USDC", "USDT", "USDT0", "USDS", "DAI"}
    m = m[sym.isin(want) & (pd.to_numeric(m["tvlUsd"], errors="coerce") >= 5e6)]
    print(f"corr lendBorrow rows: {len(m)}", flush=True)
    keep = [c for c in ("pool", "chain", "project", "symbol", "tvlUsd", "ltv", "borrowable") if c in m]
    m[keep].to_parquet(OUT / "corrloop_pools.parquet", index=False)
    rows = []
    for p in m["pool"]:
        b = {pd.Timestamp(x["timestamp"]).floor("D"): x for x in (get(f"https://yields.llama.fi/chartLendBorrow/{p}") or {}).get("data", [])}
        sup = {pd.Timestamp(x["timestamp"]).floor("D"): x for x in (get(f"https://yields.llama.fi/chart/{p}") or {}).get("data", [])}
        for d in sorted(set(sup)):
            bb = b.get(d, {})
            rows.append({"pool": p, "day": d, "apyBase": sup[d].get("apyBase"), "apyReward": sup[d].get("apyReward"), "tvlUsd": sup[d].get("tvlUsd"),
                         "apyBaseBorrow": bb.get("apyBaseBorrow"), "apyRewardBorrow": bb.get("apyRewardBorrow")})
        time.sleep(0.4)
    df = pd.DataFrame(rows)
    for c in df.columns[2:]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df.to_parquet(OUT / "corrloop_charts.parquet", index=False)
    print(f"corr charts: {df['pool'].nunique() if len(df) else 0} pools, {len(df)} rows", flush=True)



def job_batch4():
    """Batch 4 Stage-1 data (docs/PREREG_BATCH4_20261121.md): DefiLlama charts for the candidate pools, dYdX MegaVault PnL, JLP/Lighter probes."""
    OUT.mkdir(parents=True, exist_ok=True)
    pools = pd.DataFrame((get("https://yields.llama.fi/pools") or {}).get("data", []))
    pools["tvlUsd"] = pd.to_numeric(pools["tvlUsd"], errors="coerce")
    sym = pools["symbol"].astype(str).str.upper()
    gm = pools["project"].isin(["gmx-evm", "gmx-solana"]) & (pools["tvlUsd"] >= 20e6)
    lp = (pools["stablecoin"] == True) & (pools["exposure"] == "multi") & (pools["ilRisk"] == "no") & (pools["tvlUsd"] >= 5e6)  # noqa: E712
    tc = pools["project"].isin(["gains-network", "avantis", "ostium"]) & (pools["stablecoin"] == True)  # noqa: E712
    sv = (pools["stablecoin"] == True) & (pools["exposure"] == "single") & (pools["tvlUsd"] >= 5e6) & sym.isin(  # noqa: E712
        ["SCRVUSD", "SFRXUSD", "SUSDAI", "SAVUSD", "SUSDX", "STUSR", "SDOLA", "SYRUPUSDC", "SYRUPUSDT", "SUSDF", "SNUSD", "WSRUSD", "SRUSD", "YUSD", "SUSDU"])
    jlp = pools["symbol"].astype(str).str.upper().eq("JLP") | pools["project"].str.contains("jupiter-perp", na=False)
    u = pools[gm | lp | tc | sv | jlp].copy()
    u["group"] = (gm.map({True: "221"}).fillna("") + lp.map({True: "224"}).fillna("") + tc.map({True: "225"}).fillna("")
                  + sv.map({True: "227"}).fillna("") + jlp.map({True: "220"}).fillna(""))[u.index]
    print(f"batch4 pools: {len(u)} {u['group'].value_counts().to_dict()}", flush=True)
    u[["pool", "chain", "project", "symbol", "tvlUsd", "group"]].to_parquet(OUT / "batch4_pools.parquet", index=False)
    rows = []
    for p in u["pool"]:
        for x in (get(f"https://yields.llama.fi/chart/{p}") or {}).get("data", []):
            rows.append({"pool": p, "ts": x.get("timestamp"), "tvlUsd": x.get("tvlUsd"), "apyBase": x.get("apyBase"), "apyReward": x.get("apyReward")})
        time.sleep(0.25)
    ch = pd.DataFrame(rows)
    if len(ch):
        ch["ts"] = pd.to_datetime(ch["ts"], utc=True)
        for c in ("tvlUsd", "apyBase", "apyReward"):
            ch[c] = pd.to_numeric(ch[c], errors="coerce")
    ch.to_parquet(OUT / "batch4_charts.parquet", index=False)
    print(f"batch4 charts: {ch['pool'].nunique() if len(ch) else 0} pools", flush=True)
    mv = get("https://indexer.dydx.trade/v4/vault/v1/megavault/historicalPnl?resolution=day")
    pts = (mv or {}).get("megavaultPnl") or []
    pd.DataFrame(pts).to_parquet(OUT / "batch4_megavault.parquet", index=False)
    print(f"megavault points: {len(pts)}; keys {sorted(pts[0].keys()) if pts else None}", flush=True)
    for name, url in (("lighter_pools", "https://mainnet.zklighter.elliot.ai/api/v1/publicPools?index=0&limit=5"),
                      ("lighter_llp", "https://mainnet.zklighter.elliot.ai/api/v1/publicPoolsMetadata?index=0&limit=5"),
                      ("jup_jlp", "https://perps-api.jup.ag/v1/jlp-info")):
        d = get(url)
        print(f"PROBE {name}: {'answered, keys ' + str(sorted(d.keys())[:15]) if isinstance(d, dict) else ('list' if isinstance(d, list) else 'no answer')}", flush=True)


def job_batch5():
    """#228/#229 Stage-0.5/1 data: 90-day HL funding, staking-chain APR inputs, TRX-energy and SKY pool histories."""
    OUT.mkdir(parents=True, exist_ok=True)
    start = int((pd.Timestamp.now(tz="UTC") - pd.Timedelta(days=95)).timestamp() * 1000)
    rows = []
    for c in ["TRX", "SKY", "ATOM", "TIA", "INJ", "DOT", "NEAR", "APT", "SEI", "DYDX"]:
        t = start
        while True:
            d = get("https://api.hyperliquid.xyz/info", {"type": "fundingHistory", "coin": c, "startTime": t})
            if not d:
                break
            rows += [{"coin": c, "t": int(x["time"]) // 1000, "rate": float(x["fundingRate"])} for x in d]
            if len(d) < 500:
                break
            t = int(d[-1]["time"]) + 1
            time.sleep(0.3)
        print(f"  hl 90d funding {c}: {sum(1 for r in rows if r['coin'] == c)}", flush=True)
    pd.DataFrame(rows).to_parquet(OUT / "batch5_hlfunding.parquet", index=False)
    lcd = {"ATOM": "https://cosmos-rest.publicnode.com", "TIA": "https://celestia-rest.publicnode.com", "INJ": "https://injective-rest.publicnode.com",
           "SEI": "https://sei-rest.publicnode.com", "DYDX": "https://dydx-rest.publicnode.com"}
    apr = []
    for c, base in lcd.items():
        infl = get(base + "/cosmos/mint/v1beta1/inflation")
        pool = get(base + "/cosmos/staking/v1beta1/pool")
        supply = get(base + "/cosmos/bank/v1beta1/supply?pagination.limit=1000")
        dist = get(base + "/cosmos/distribution/v1beta1/params")
        apr.append({"coin": c, "inflation": (infl or {}).get("inflation"), "bonded": ((pool or {}).get("pool") or {}).get("bonded_tokens"),
                    "community_tax": ((dist or {}).get("params") or {}).get("community_tax"), "supply_n": len((supply or {}).get("supply", []))})
        print(f"  lcd {c}: inflation {'ok' if infl else 'none'}, pool {'ok' if pool else 'none'}", flush=True)
    pd.DataFrame(apr).to_parquet(OUT / "batch5_staking.parquet", index=False)
    pools = pd.DataFrame((get("https://yields.llama.fi/pools") or {}).get("data", []))
    u = pools[(pools["project"].isin(["tr-energy"])) | ((pools["project"] == "sky-lending") & (pools["symbol"].str.upper() == "SKY"))]
    out = []
    for p in u["pool"]:
        for x in (get(f"https://yields.llama.fi/chart/{p}") or {}).get("data", []):
            out.append({"pool": p, "ts": x.get("timestamp"), "tvlUsd": x.get("tvlUsd"), "apyBase": x.get("apyBase"), "apyReward": x.get("apyReward")})
    ch = pd.DataFrame(out)
    if len(ch):
        ch["ts"] = pd.to_datetime(ch["ts"], utc=True)
    ch.to_parquet(OUT / "batch5_charts.parquet", index=False)
    u[["pool", "project", "symbol", "chain", "tvlUsd"]].to_parquet(OUT / "batch5_pools.parquet", index=False)
    print(f"batch5 pools {len(u)}, chart rows {len(ch)}", flush=True)


WRAPPERS = {"YCRV": "ethereum:0xFCc5c47bE19d06BF83eB04298b026F81069ff65b", "ST-YCRV": "ethereum:0x27B5739e22ad9033bcBf192059122d163b60349D",
            "CVXCRV": "ethereum:0x62B9c7356A2Dc64a1969e19C23e4f579F9810Aa7", "SDCRV": "ethereum:0xD1b5651E55D4CeeD36251c61c50C889B36F6abB5",
            "CRV": "ethereum:0xD533a949740bb3306d119CC777fa900bA034cd52", "SDPENDLE": "ethereum:0x5Ea630e00D6eE438d3deA1556A110359ACdc10A9",
            "PENDLE": "ethereum:0x808507121B80c02388fAd14726482e061B8da827",
            "GM_ETH": "arbitrum:0x70d95587d40A2caf56bd97485aB3Eec10Bee6336", "GM_BTC": "arbitrum:0x47c031236e19d024b42f8AE6780E44A573170703",
            "ETH": "coingecko:ethereum", "BTC": "coingecko:bitcoin"}


def job_wrappers():
    """#214 robustness: daily prices of CRV/PENDLE wrappers and underlyings (DefiLlama coins, 90-day spans)."""
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    t = int(pd.Timestamp("2024-10-01", tz="UTC").timestamp())
    end = int(pd.Timestamp("2026-11-21", tz="UTC").timestamp())
    keys = ",".join(WRAPPERS.values())
    while t < end:
        d = get(f"https://coins.llama.fi/chart/{keys}?start={t}&span=90&period=1d")
        for k, v in ((d or {}).get("coins") or {}).items():
            name = [n for n, a in WRAPPERS.items() if a.lower() == k.lower()]
            for pnt in v.get("prices", []):
                rows.append({"token": name[0] if name else k, "ts": pnt["timestamp"], "price": pnt["price"]})
        t += 90 * 86400
        time.sleep(1)
    df = pd.DataFrame(rows).drop_duplicates(["token", "ts"])
    df.to_parquet(OUT / "wrappers_prices.parquet", index=False)
    print(f"wrapper prices: {df.groupby('token').size().to_dict() if len(df) else 'none'}", flush=True)


def job_lendborrow_now():
    """#209/#219 Stage 0.5: today's full lendBorrow table joined with pool symbols/yields (free endpoints only)."""
    OUT.mkdir(parents=True, exist_ok=True)
    lb = pd.DataFrame(get("https://yields.llama.fi/lendBorrow") or [])
    pools = pd.DataFrame((get("https://yields.llama.fi/pools") or {}).get("data", []))
    m = lb.merge(pools[["pool", "chain", "project", "symbol", "tvlUsd", "apyBase", "apyReward"]], on="pool", how="inner")
    for c in m.columns:
        if m[c].dtype == object and c not in ("pool", "chain", "project", "symbol"):
            m[c] = m[c].astype(str)
    m.to_parquet(OUT / "lendborrow_now.parquet", index=False)
    print(f"lendborrow_now rows: {len(m)}", flush=True)


PENDLE_CHAIN = {1: "ethereum", 42161: "arbitrum", 8453: "base", 56: "bsc", 146: "sonic", 999: "hyperliquid", 9745: "plasma",
                5000: "mantle", 80094: "berachain", 10: "optimism"}
import re as _re  # noqa: E402
STABLE_RE = _re.compile(r"usd|dai|gho|frax|usr|usx|ausd|usde|usdai|usdf|usdg|usd0|eusd|deusd|reusd|syrup", _re.I)


def job_pendle_pilot():
    """#211 Stage-1 data: stable-underlying Pendle markets live since 2026-05 (active + inactive), daily history, underlying price at expiry."""
    OUT.mkdir(parents=True, exist_ok=True)
    chains = (get("https://api-v2.pendle.finance/core/v1/chains") or {}).get("chainIds", [])
    mk = []
    for cid in chains:
        for kind in ("active", "inactive"):
            for m in (get(f"https://api-v2.pendle.finance/core/v1/{cid}/markets/{kind}") or {}).get("markets", []):
                if STABLE_RE.search(m.get("name", "")) and pd.Timestamp(m["expiry"]) >= pd.Timestamp("2026-05-01", tz="UTC"):
                    mk.append({"chain": cid, "kind": kind, "name": m["name"], "address": m["address"], "expiry": m["expiry"],
                               "underlying": m.get("underlyingAsset"), "pt": m.get("pt")})
    print(f"pendle stable markets expiring >= 2026-05: {len(mk)} on {len(set(x['chain'] for x in mk))} chains", flush=True)
    rows, shown = [], False
    for m in mk:
        d = None
        for u in (f"https://api-v2.pendle.finance/core/v2/{m['chain']}/markets/{m['address']}/historical-data?time_frame=day",
                  f"https://api-v2.pendle.finance/core/v1/{m['chain']}/markets/{m['address']}/historical-data?time_frame=day"):
            d = get(u)
            if d:
                break
        if not d:
            continue
        if not shown:
            print(f"  history keys: {sorted(d.keys())[:20] if isinstance(d, dict) else type(d)}", flush=True)
            shown = True
        res = d.get("results") if isinstance(d, dict) else d
        if isinstance(res, list):
            for r in res:
                rows.append({**{k: m[k] for k in ("chain", "address", "name", "expiry")}, **{k: r.get(k) for k in r if k in
                             ("timestamp", "impliedApy", "underlyingApy", "tvl", "ptPrice", "liquidity", "maxApy", "baseApy")}})
        elif isinstance(d, dict) and "timestamp" in d:  # columnar format
            n = len(d["timestamp"])
            for i in range(n):
                rows.append({**{k: m[k] for k in ("chain", "address", "name", "expiry")},
                             **{k: (d[k][i] if isinstance(d.get(k), list) and len(d[k]) == n else None) for k in
                                ("timestamp", "impliedApy", "underlyingApy", "tvl", "ptPrice", "liquidity")}})
        time.sleep(0.3)
    h = pd.DataFrame(rows)
    h.to_parquet(OUT / "pendle_pilot_history.parquet", index=False)
    print(f"pendle history rows: {len(h)}; markets with history: {h['address'].nunique() if len(h) else 0}", flush=True)
    px = []
    for m in mk:
        slug = PENDLE_CHAIN.get(m["chain"])
        ua = str(m.get("underlying") or "")
        addr = ua.split("-")[-1] if "-" in ua else ua
        if not slug or not addr.startswith("0x"):
            continue
        ts = int(min(pd.Timestamp(m["expiry"]), pd.Timestamp.now(tz="UTC")).timestamp())
        d = get(f"https://coins.llama.fi/prices/historical/{ts}/{slug}:{addr}")
        c = ((d or {}).get("coins") or {}).get(f"{slug}:{addr}") or {}
        px.append({"address": m["address"], "underlying": addr, "price_at_expiry_or_now": c.get("price"), "symbol": c.get("symbol")})
        time.sleep(0.2)
    pd.DataFrame(px).to_parquet(OUT / "pendle_pilot_underlying.parquet", index=False)
    pd.DataFrame(mk).to_parquet(OUT / "pendle_pilot_markets.parquet", index=False)
    print(f"underlying prices: {sum(1 for x in px if x['price_at_expiry_or_now'])} of {len(px)}", flush=True)


def job_staking_apr():
    """#229 Stage 0.5 input: current staking APR inputs per Cosmos chain (inflation, community tax, bonded, total supply of the bond denom)."""
    OUT.mkdir(parents=True, exist_ok=True)
    chains = {"ATOM": ("https://cosmos-rest.publicnode.com", "uatom"), "TIA": ("https://celestia-rest.publicnode.com", "utia"),
              "INJ": ("https://injective-rest.publicnode.com", "inj"), "SEI": ("https://sei-rest.publicnode.com", "usei"),
              "DYDX": ("https://dydx-rest.publicnode.com", "adydx")}
    out = []
    for c, (base, denom) in chains.items():
        infl = (get(base + "/cosmos/mint/v1beta1/inflation") or {}).get("inflation")
        pool = (get(base + "/cosmos/staking/v1beta1/pool") or {}).get("pool") or {}
        tax = ((get(base + "/cosmos/distribution/v1beta1/params") or {}).get("params") or {}).get("community_tax")
        sup = ((get(base + f"/cosmos/bank/v1beta1/supply/by_denom?denom={denom}") or {}).get("amount") or {}).get("amount")
        out.append({"coin": c, "inflation": infl, "community_tax": tax, "bonded": pool.get("bonded_tokens"), "supply": sup})
        print(f"  {c}: inflation {infl}, tax {tax}, bonded {'ok' if pool else 'none'}, supply {'ok' if sup else 'none'}", flush=True)
    pd.DataFrame(out).astype(str).to_parquet(OUT / "staking_apr.parquet", index=False)

JOBS = {"staking_apr": job_staking_apr, "pendle_pilot": job_pendle_pilot, "wrappers": job_wrappers, "lendborrow_now": job_lendborrow_now, "batch5": job_batch5, "batch4": job_batch4, "hedged": job_hedged, "lendborrow_corr": job_lendborrow_corr, "pendle_probe": job_pendle_probe, "stable_hlp": job_stable_hlp, "probe": job_probe, "funding": job_funding, "lendborrow": job_lendborrow}

if __name__ == "__main__":
    import sys
    for j in (sys.argv[1:] or ["stable_hlp"]):
        print(f"=== {j}", flush=True)
        JOBS[j]()

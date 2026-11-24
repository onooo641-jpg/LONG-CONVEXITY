"""Data for docs/PREREG_FALLBACK_20261121.md (#204, #205). Runs on GitHub Actions.

    python scripts/fetch_fallback.py
Writes data/public/fallback_stable_charts.parquet, fallback_stable_pools.parquet, fallback_hlp.parquet.
"""
from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from pathlib import Path

import pandas as pd

OUT = Path(__file__).resolve().parent.parent / "data" / "public"
UA = {"User-Agent": "long-convexity-research/1.0", "Accept": "application/json"}


def get(url, body=None, tries=4):  # noqa: D103
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
    end = int(pd.Timestamp("2026-11-21", tz="UTC").timestamp())
    for name, addr in WRAPPERS.items():  # one coin per request: a single bad address makes a batched request fail (HTTP 400)
        t = int(pd.Timestamp("2024-10-01", tz="UTC").timestamp())
        n = 0
        while t < end:
            span = min(90, max(1, (end - t) // 86400))
            d = get(f"https://coins.llama.fi/chart/{addr.lower() if addr.startswith(('ethereum:', 'arbitrum:')) else addr}?start={t}&span={span}&period=1d", tries=2)
            for v in ((d or {}).get("coins") or {}).values():
                for pnt in v.get("prices", []):
                    rows.append({"token": name, "ts": pnt["timestamp"], "price": pnt["price"]})
                    n += 1
            t += 90 * 86400
            time.sleep(0.5)
        print(f"  {name}: {n} prices", flush=True)
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


def job_sky_funding():
    """#228 Stage 2: full HL funding history for SKY (and TRX for the record)."""
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for c in ("SKY", "TRX"):
        r = _hl(c)
        rows += [{"coin": c, "t": t, "rate": v} for t, v in r]
        print(f"  {c}: {len(r)}", flush=True)
    pd.DataFrame(rows).to_parquet(OUT / "batch5_hlfunding_full.parquet", index=False)


def job_sp_probe():
    """#230 Stage 0 probe: which stability-pool data sources answer (prints availability and field names only)."""
    for name, url in (("liquity_api_v2", "https://api.liquity.org/v2/mainnet.json"), ("liquity_api_v2b", "https://api.liquity.org/v2/mainnet/sp.json"),
                      ("liquity_api_root", "https://api.liquity.org/"), ("liquity_stats", "https://api.liquity.org/v2/mainnet/stats.json"),
                      ("felix_api", "https://api.usefelix.xyz/"), ("felix_stats", "https://usefelix.xyz/api/stats"),
                      ("llama_liquity_pools", "https://yields.llama.fi/pools")):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=30) as r:
                b = r.read(3_000_000).decode("utf-8", "replace")
            try:
                j = json.loads(b)
                keys = sorted(j.keys())[:25] if isinstance(j, dict) else f"list[{len(j)}]"
            except Exception:  # noqa: BLE001
                keys = f"non-JSON, {len(b)} bytes"
            if name == "llama_liquity_pools":
                d = json.loads(b)["data"]
                hits = [f"{x['project']}/{x['symbol']}/{x['chain']}" for x in d if x["project"] in ("liquity-v2", "felix-cdp", "felix")]
                keys = f"liquity/felix pools: {hits[:12]}"
            print(f"PROBE {name}: answered; {keys}", flush=True)
        except Exception as e:  # noqa: BLE001
            print(f"PROBE {name}: FAIL {str(e)[:100]}", flush=True)


def job_sp_data():
    """#230: Liquity v2 API snapshot (saved whole) + price history of sBOLD / yBOLD / BOLD (addresses read from the API)."""
    OUT.mkdir(parents=True, exist_ok=True)
    j = get("https://api.liquity.org/v2/mainnet.json") or {}
    (OUT / "sp_liquity_api.json").write_text(json.dumps(j))
    addrs = {}

    def walk(x, path=""):
        if isinstance(x, dict):
            for k, v in x.items():
                walk(v, f"{path}.{k}")
        elif isinstance(x, list):
            for i, v in enumerate(x):
                walk(v, f"{path}[{i}]")
        elif isinstance(x, str) and x.startswith("0x") and len(x) == 42:
            addrs[path] = x
    walk(j)
    print("addresses in API:", {k: v for k, v in addrs.items() if "BOLD" in k or "bold" in k.lower()}, flush=True)
    want = {k: v for k, v in addrs.items() if any(t in k for t in ("sBOLD", "yBOLD", "boldToken", "BOLD"))}
    rows = []
    end = int(pd.Timestamp("2026-11-22", tz="UTC").timestamp())
    for name, a in want.items():
        t, n = int(pd.Timestamp("2025-05-01", tz="UTC").timestamp()), 0
        while t < end:
            d = get(f"https://coins.llama.fi/chart/ethereum:{a.lower()}?start={t}&span=90&period=1d", tries=2)
            for v in ((d or {}).get("coins") or {}).values():
                for pnt in v.get("prices", []):
                    rows.append({"name": name, "address": a, "ts": pnt["timestamp"], "price": pnt["price"]})
                    n += 1
            t += 90 * 86400
            time.sleep(0.5)
        print(f"  {name} {a}: {n} prices", flush=True)
    pd.DataFrame(rows).to_parquet(OUT / "sp_prices.parquet", index=False)


def job_batch6():
    """Batch 6 Stage-0.5 data (docs/PREREG_BATCH6_20261122.md). Raw responses saved; structure printed."""
    OUT.mkdir(parents=True, exist_ok=True)
    raw = {}
    raw["paradex_summary"] = get("https://api.prod.paradex.trade/v1/markets/summary?market=ALL")
    ob = get("https://mainnet.zklighter.elliot.ai/api/v1/orderBooks") or {}
    raw["lighter_orderbooks"] = ob
    books = ob.get("order_books") or ob.get("orderBooks") or []
    end = int(time.time())
    start = end - 92 * 86400
    lf = []
    for b in books[:40]:
        mid, sym = b.get("market_id"), b.get("symbol")
        d = get(f"https://mainnet.zklighter.elliot.ai/api/v1/fundings?market_id={mid}&resolution=1h&start_timestamp={start}&end_timestamp={end}&count_back=2300")
        for x in (d or {}).get("fundings", []):
            lf.append({"market_id": mid, "symbol": sym, **{k: x.get(k) for k in x}})
        time.sleep(0.2)
    pd.DataFrame(lf).astype(str).to_parquet(OUT / "batch6_lighter_funding.parquet", index=False)
    print(f"lighter books {len(books)}, funding rows {len(lf)}; sample keys {sorted(lf[0].keys()) if lf else None}", flush=True)
    raw["fees_holders"] = get("https://api.llama.fi/overview/fees?excludeTotalDataChart=true&excludeTotalDataChartBreakdown=true&dataType=dailyHoldersRevenue")
    prot = get("https://api.llama.fi/protocols") or []
    raw["protocol_mcaps"] = [{"name": x.get("name"), "slug": x.get("slug"), "symbol": x.get("symbol"), "mcap": x.get("mcap"),
                              "gecko_id": x.get("gecko_id")} for x in prot]
    for name, url in (("drift_if", "https://mainnet-beta.api.drift.trade/insuranceFund/stats"), ("drift_stats", "https://mainnet-beta.api.drift.trade/stats"),
                      ("drift_data", "https://data.api.drift.trade/stats/insuranceFund"), ("aave_umbrella", "https://aave-api-v2.aave.com/data/umbrella"),
                      ("llama_airforce", "https://api.llama.airforce/"), ("votium_rounds", "https://api.llama.airforce/bribes/votium/cvx-crv/rounds"),
                      ("votium_v2", "https://api-next.llama.airforce/bribes/votium/cvx-crv/rounds")):
        raw[name] = get(url, tries=1)
        print(f"PROBE {name}: {'answered ' + str(sorted(raw[name].keys())[:12]) if isinstance(raw[name], dict) else ('list' if isinstance(raw[name], list) else 'no answer')}", flush=True)
    for sym in ("BTC=F", "BTC-USD"):
        raw[f"yahoo_{sym}"] = get(f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?range=6mo&interval=1d", tries=2)
        print(f"yahoo {sym}: {'ok' if raw[f'yahoo_{sym}'] else 'no answer'}", flush=True)
    pools = pd.DataFrame((get("https://yields.llama.fi/pools") or {}).get("data", []))
    tr = pools[pools["project"].isin(["strata-markets", "resolv", "reflect-tranches", "reservoir-protocol"])
               | pools["symbol"].str.upper().isin(["RLP", "JRUSDE", "SRUSDE", "SRUSDAT", "JRUSDAT", "STUSR"])]
    rows = []
    for p in tr["pool"]:
        for x in (get(f"https://yields.llama.fi/chart/{p}") or {}).get("data", []):
            rows.append({"pool": p, "ts": x.get("timestamp"), "tvlUsd": x.get("tvlUsd"), "apyBase": x.get("apyBase"), "apyReward": x.get("apyReward")})
        time.sleep(0.25)
    pd.DataFrame(rows).to_parquet(OUT / "batch6_tranche_charts.parquet", index=False)
    tr[["pool", "project", "symbol", "chain", "tvlUsd", "apyBase", "apyReward"]].to_parquet(OUT / "batch6_tranche_pools.parquet", index=False)
    print(f"tranche pools {len(tr)}, chart rows {len(rows)}", flush=True)
    (OUT / "batch6_raw.json").write_text(json.dumps(raw)[:40_000_000])
    print("paradex markets:", len((raw["paradex_summary"] or {}).get("results", [])), flush=True)


def job_votium():
    """#267 Stage 0.5/1: Votium cvx-crv per-round bribe data (last 30 rounds) + CVX daily price."""
    OUT.mkdir(parents=True, exist_ok=True)
    rounds = (get("https://api.llama.airforce/bribes/votium/cvx-crv/rounds") or {}).get("rounds", [])
    raw = {}
    for r in rounds[-30:]:
        raw[str(r)] = get(f"https://api.llama.airforce/bribes/votium/cvx-crv/{r}", tries=2)
        time.sleep(0.3)
    first = next((v for v in raw.values() if v), None)
    print(f"votium rounds fetched {sum(1 for v in raw.values() if v)} of {len(raw)}; keys {sorted(first.keys())[:12] if isinstance(first, dict) else None}", flush=True)
    (OUT / "votium_raw.json").write_text(json.dumps(raw))
    rows = []
    t = int(pd.Timestamp("2024-10-01", tz="UTC").timestamp())
    while t < int(time.time()):
        d = get(f"https://coins.llama.fi/chart/coingecko:convex-finance?start={t}&span=90&period=1d", tries=2)
        for v in ((d or {}).get("coins") or {}).values():
            rows += [{"ts": x["timestamp"], "price": x["price"]} for x in v.get("prices", [])]
        t += 90 * 86400
    pd.DataFrame(rows).to_parquet(OUT / "votium_cvx_price.parquet", index=False)
    print(f"CVX prices {len(rows)}", flush=True)


def job_batch7():
    """Batch 7 (docs/PREREG_BATCH7_20261122.md): Gains vault prices, Pendle full history, order-book snapshots (3 h)."""
    OUT.mkdir(parents=True, exist_ok=True)
    # A. Gains
    rows = []
    for name, addr in (("gUSDC_arb", "arbitrum:0xd3443ee1e91af28e5fb858fbd0d72a63ba8046e0"),):
        t = int(pd.Timestamp("2024-10-01", tz="UTC").timestamp())
        while t < int(time.time()):
            d = get(f"https://coins.llama.fi/chart/{addr}?start={t}&span=90&period=1d", tries=2)
            for v in ((d or {}).get("coins") or {}).values():
                rows += [{"vault": name, "ts": x["timestamp"], "price": x["price"]} for x in v.get("prices", [])]
            t += 90 * 86400
            time.sleep(0.4)
    pd.DataFrame(rows).to_parquet(OUT / "batch7_gains_prices.parquet", index=False)
    print(f"gains prices: {len(rows)}", flush=True)
    for nm, u in (("gains_backend_arb", "https://backend-arbitrum.gains.trade/stats"), ("gains_global", "https://backend-global.gains.trade/api/vaults")):
        d = get(u, tries=1)
        print(f"PROBE {nm}: {'answered ' + str(sorted(d.keys())[:10]) if isinstance(d, dict) else ('list' if isinstance(d, list) else 'no answer')}", flush=True)
    # B. Pendle full
    chains = (get("https://api-v2.pendle.finance/core/v1/chains") or {}).get("chainIds", [])
    mk = []
    for cid in chains:
        for kind in ("active", "inactive"):
            for m in (get(f"https://api-v2.pendle.finance/core/v1/{cid}/markets/{kind}") or {}).get("markets", []):
                if STABLE_RE.search(m.get("name", "")) and pd.Timestamp(m["expiry"]) >= pd.Timestamp("2024-11-01", tz="UTC"):
                    mk.append({"chain": cid, "name": m["name"], "address": m["address"], "expiry": m["expiry"], "underlying": m.get("underlyingAsset")})
    print(f"pendle stable markets expiring >= 2024-11: {len(mk)}", flush=True)
    hist = []
    for i, m in enumerate(mk):
        d = get(f"https://api-v2.pendle.finance/core/v2/{m['chain']}/markets/{m['address']}/historical-data?time_frame=day", tries=2) or \
            get(f"https://api-v2.pendle.finance/core/v1/{m['chain']}/markets/{m['address']}/historical-data?time_frame=day", tries=1)
        for r in (d or {}).get("results", []) if isinstance(d, dict) else []:
            hist.append({**{k: m[k] for k in ("chain", "address", "name", "expiry")}, "timestamp": r.get("timestamp"),
                         "impliedApy": r.get("impliedApy"), "tvl": r.get("tvl")})
        if i % 50 == 0:
            print(f"  pendle history {i}/{len(mk)}", flush=True)
        time.sleep(0.25)
    pd.DataFrame(hist).to_parquet(OUT / "batch7_pendle_history.parquet", index=False)
    px = []
    for m in mk:
        slug = PENDLE_CHAIN.get(m["chain"])
        ua = str(m.get("underlying") or "")
        addr = ua.split("-")[-1] if "-" in ua else ua
        if not slug or not addr.startswith("0x"):
            continue
        ts = int(min(pd.Timestamp(m["expiry"]), pd.Timestamp.now(tz="UTC")).timestamp())
        d = get(f"https://coins.llama.fi/prices/historical/{ts}/{slug}:{addr}", tries=2)
        c = ((d or {}).get("coins") or {}).get(f"{slug}:{addr}") or {}
        px.append({"address": m["address"], "price": c.get("price"), "symbol": c.get("symbol")})
        time.sleep(0.15)
    pd.DataFrame(px).to_parquet(OUT / "batch7_pendle_underlying.parquet", index=False)
    pd.DataFrame(mk).to_parquet(OUT / "batch7_pendle_markets.parquet", index=False)
    print(f"pendle history rows {len(hist)}, underlying prices {sum(1 for x in px if x['price'])}/{len(px)}", flush=True)
    # C. order books, every 10 minutes for 3 hours
    coins = ["BTC", "ETH", "SOL", "XRP", "DOGE", "AVAX", "LINK", "SUI", "ARB", "OP", "LTC", "BNB"]
    snaps = []
    for k in range(18):
        t0 = time.time()
        for c in coins:
            hl = get("https://api.hyperliquid.xyz/info", {"type": "l2Book", "coin": c}, tries=1)
            if hl and hl.get("levels"):
                b, a = hl["levels"]
                snaps.append({"k": k, "venue": "hl", "coin": c, "bids": [[float(x["px"]), float(x["sz"])] for x in b[:40]],
                              "asks": [[float(x["px"]), float(x["sz"])] for x in a[:40]]})
            dy = get(f"https://indexer.dydx.trade/v4/orderbooks/perpetualMarket/{c}-USD", tries=1)
            if dy and dy.get("bids") is not None:
                snaps.append({"k": k, "venue": "dydx", "coin": c, "bids": [[float(x["price"]), float(x["size"])] for x in dy["bids"][:40]],
                              "asks": [[float(x["price"]), float(x["size"])] for x in dy["asks"][:40]]})
            ae = get(f"https://api.aevo.xyz/orderbook?instrument_name={c}-PERP", tries=1)
            if ae and ae.get("bids") is not None:
                snaps.append({"k": k, "venue": "aevo", "coin": c, "bids": [[float(x[0]), float(x[1])] for x in ae["bids"][:40]],
                              "asks": [[float(x[0]), float(x[1])] for x in ae["asks"][:40]]})
            time.sleep(0.1)
        print(f"  orderbook snapshot {k + 1}/18: {sum(1 for s in snaps if s['k'] == k)} books", flush=True)
        if k < 17:
            time.sleep(max(0, 600 - (time.time() - t0)))
    (OUT / "batch7_orderbooks.json").write_text(json.dumps(snaps))


def job_hype4h():
    """HYPE perp 4h candles for docs/PREREG_BATCH7_20261122.md part D."""
    OUT.mkdir(parents=True, exist_ok=True)
    end = int(time.time() * 1000)
    c = get("https://api.hyperliquid.xyz/info", {"type": "candleSnapshot", "req": {"coin": "HYPE", "interval": "4h",
            "startTime": end - 5000 * 4 * 3600 * 1000, "endTime": end}}) or []
    df = pd.DataFrame([{"t": x["t"], "o": float(x["o"]), "h": float(x["h"]), "l": float(x["l"]), "c": float(x["c"])} for x in c])
    df.to_parquet(OUT / "batch7_hype4h.parquet", index=False)
    print(f"hype 4h candles: {len(df)} from {pd.to_datetime(df.t.min(), unit='ms') if len(df) else None}", flush=True)


def job_batch8p():
    """Batch 8 Stage 1 pilot data (docs/PREREG_BATCH8_20261122.md), window 2026-07-01..now. Raw responses kept for parsing offline."""
    OUT.mkdir(parents=True, exist_ok=True)
    t0 = int(pd.Timestamp("2026-07-01", tz="UTC").timestamp())
    now = int(time.time())
    raw = {}

    def save():
        (OUT / "batch8_raw.json").write_text(json.dumps(raw))

    coins = ["BTC", "ETH", "SOL", "XRP", "DOGE", "AVAX", "LINK", "SUI", "ARB", "OP", "LTC", "BNB"]
    # 279 Drift
    for c in coins:
        rows = []
        for u in (f"https://data.api.drift.trade/fundingRates?marketName={c}-PERP",
                  f"https://data.api.drift.trade/market/{c}-PERP/fundingRates"):
            d = get(u, tries=1)
            if d:
                rows = d.get("fundingRates", d.get("records", d)) if isinstance(d, dict) else d
                raw[f"drift|{c}|{u}"] = rows
                break
        print(f"  drift {c}: {len(rows) if hasattr(rows, '__len__') else type(rows)}", flush=True)
    save()
    # 280 Deribit funding
    der = {"BTC": "BTC-PERPETUAL", "ETH": "ETH-PERPETUAL"}
    der.update({c: f"{c}_USDC-PERPETUAL" for c in ("SOL", "XRP", "DOGE", "AVAX", "LINK", "LTC", "BNB", "SUI")})
    for c, inst in der.items():
        rows, t = [], t0
        while t < now:
            d = get(f"https://www.deribit.com/api/v2/public/get_funding_rate_history?instrument_name={inst}"
                    f"&start_timestamp={t * 1000}&end_timestamp={min(t + 30 * 86400, now) * 1000}", tries=2)
            rows += (d or {}).get("result", []) or []
            t += 30 * 86400
            time.sleep(0.2)
        raw[f"deribit_funding|{c}"] = rows
        print(f"  deribit funding {c}: {len(rows)}", flush=True)
    save()
    # 289 Orderly
    for c in coins:
        rows, page = [], 1
        while page < 40:
            d = get(f"https://api-evm.orderly.org/v1/public/funding_rate_history?symbol=PERP_{c}_USDC&start_t={t0}&end_t={now}&page={page}&size=500", tries=2)
            r = ((d or {}).get("data") or {}).get("rows", [])
            rows += r
            if len(r) < 500:
                break
            page += 1
        raw[f"orderly|{c}"] = rows
        print(f"  orderly {c}: {len(rows)}", flush=True)
    save()
    # 284 HIP-3
    dexes = get("https://api.hyperliquid.xyz/info", {"type": "perpDexs"}) or []
    names = [x["name"] for x in dexes if isinstance(x, dict) and x.get("name")]
    raw["hip3_dexes"] = dexes
    print(f"  hip3 dexes: {names}", flush=True)
    for dx in names:
        meta = get("https://api.hyperliquid.xyz/info", {"type": "meta", "dex": dx}) or {}
        for a in meta.get("universe", [])[:60]:
            nm = a.get("name")
            rows, t = [], t0 * 1000
            while t < now * 1000:
                r = get("https://api.hyperliquid.xyz/info", {"type": "fundingHistory", "coin": nm, "startTime": t}, tries=2) or []
                if not r:
                    break
                rows += r
                nt = int(r[-1]["time"]) + 1
                if nt <= t or len(r) < 500:
                    break
                t = nt
                time.sleep(0.15)
            raw[f"hip3|{nm}"] = rows
        print(f"  hip3 {dx}: {len(meta.get('universe', []))} markets", flush=True)
        save()
    for c in coins:  # main-HL funding for the same window (pairs with new venues)
        rows, t = [], t0 * 1000
        while t < now * 1000:
            r = get("https://api.hyperliquid.xyz/info", {"type": "fundingHistory", "coin": c, "startTime": t}, tries=2) or []
            if not r:
                break
            rows += r
            nt = int(r[-1]["time"]) + 1
            if nt <= t or len(r) < 500:
                break
            t = nt
            time.sleep(0.15)
        raw[f"hl|{c}"] = rows
    save()
    # 281/282 Deribit futures, perpetual closes, DVOL
    for cur in ("BTC", "ETH"):
        ins = []
        for exp in ("false", "true"):
            ins += (get(f"https://www.deribit.com/api/v2/public/get_instruments?currency={cur}&kind=future&expired={exp}") or {}).get("result", []) or []
        raw[f"deribit_instruments|{cur}"] = [{k: i.get(k) for k in ("instrument_name", "expiration_timestamp", "settlement_period")} for i in ins]
        for i in ins:
            if i.get("expiration_timestamp", 0) / 1000 < t0 and i["instrument_name"] != f"{cur}-PERPETUAL":
                continue
            d = get(f"https://www.deribit.com/api/v2/public/get_tradingview_chart_data?instrument_name={i['instrument_name']}"
                    f"&start_timestamp={(t0 - 120 * 86400) * 1000}&end_timestamp={now * 1000}&resolution=1D", tries=2)
            raw[f"deribit_chart|{i['instrument_name']}"] = (d or {}).get("result")
            time.sleep(0.2)
        d = get(f"https://www.deribit.com/api/v2/public/get_volatility_index_data?currency={cur}&start_timestamp={(t0 - 60 * 86400) * 1000}"
                f"&end_timestamp={now * 1000}&resolution=1D", tries=2)
        raw[f"dvol|{cur}"] = (d or {}).get("result")
        print(f"  deribit {cur}: {len(ins)} futures, dvol {'ok' if raw[f'dvol|{cur}'] else 'none'}", flush=True)
    save()
    # 283 Boros probe
    for u in ("https://api.boros.finance/core/v1/markets", "https://boros.pendle.finance/api/core/v1/markets",
              "https://api-v2.pendle.finance/boros/v1/markets"):
        d = get(u, tries=1)
        raw[f"boros_probe|{u}"] = d if d is None or len(json.dumps(d)) < 200_000 else "large"
        print(f"PROBE boros {u}: {'answered' if d else 'no answer'}", flush=True)
    save()
    # 285 Kamino
    km = "7u3HeHxYDLhnCoErrtycNokbQYbWGzLs6JSDqGAv5PfF"
    res = get(f"https://api.kamino.finance/kamino-market/{km}/reserves/metrics?env=mainnet-beta") or []
    raw["kamino_reserves"] = res
    for r in res if isinstance(res, list) else []:
        sym = str(r.get("liquidityToken", r.get("symbol", "")))
        if sym.upper() in ("SOL", "JITOSOL", "MSOL", "JUPSOL", "BSOL", "INF", "USDC", "USDT", "PYUSD", "USDS"):
            rid = r.get("reserve")
            d = get(f"https://api.kamino.finance/kamino-market/{km}/reserves/{rid}/metrics/history?env=mainnet-beta"
                    f"&start={pd.Timestamp(t0, unit='s'):%Y-%m-%d}&end={pd.Timestamp(now, unit='s'):%Y-%m-%d}&frequency=day", tries=2)
            raw[f"kamino|{sym}"] = d
    print(f"  kamino reserves: {len(res) if isinstance(res, list) else 'no answer'}", flush=True)
    save()
    # 286 Aave rates history
    aave = {"ethereum": ("0x2f39d218133afab8f2b819b1066c7e434ad94e9e", 1,
                         {"WSTETH": "0x7f39c581f595b53c5cb19bd0b3f8da6c935e2ca0", "WETH": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",
                          "WEETH": "0xcd5fe23c85820f7b72d0926fc9b05b43e359b7ee", "SUSDE": "0x9d39a5de30e57443bff2a8307a4256c8797a3497",
                          "USDT": "0xdac17f958d2ee523a2206206994597c13d831ec7", "USDC": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"})}
    for chain, (prov, cid, toks) in aave.items():
        for sym, addr in toks.items():
            d = get(f"https://aave-api-v2.aave.com/data/rates-history?reserveId={addr}{prov}{cid}&from={t0}&resolutionInHours=24", tries=2)
            raw[f"aave|{chain}|{sym}"] = d
            print(f"  aave {chain} {sym}: {len(d) if isinstance(d, list) else 'no answer'}", flush=True)
    # price ratios for intrinsic yields
    for nm, key in (("wsteth", "ethereum:0x7f39c581f595b53c5cb19bd0b3f8da6c935e2ca0"), ("weeth", "ethereum:0xcd5fe23c85820f7b72d0926fc9b05b43e359b7ee"),
                    ("weth", "ethereum:0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"), ("susde", "ethereum:0x9d39a5de30e57443bff2a8307a4256c8797a3497"),
                    ("jitosol", "solana:J1toso1uCk3RLmjorhTtrVwY9HJ7X8V9yYac6Y7kGCPn"), ("msol", "solana:mSoLzYCxHdYgdzU16g5QSh3i5K3z3KZK7ytfqcJm7So"),
                    ("jupsol", "solana:jupSoLaHXQiZZTSfEWMTRRgpnyFm8f6sZdosWBjx93v"), ("sol", "coingecko:solana")):
        d = get(f"https://coins.llama.fi/chart/{key}?start={t0 - 40 * 86400}&span=200&period=1d", tries=2)
        raw[f"price|{nm}"] = (((d or {}).get("coins") or {}).get(key) or {}).get("prices")
        time.sleep(0.3)
    save()
    # 287 / 290 Morpho
    q_m = """{ markets(first: 60, orderBy: SupplyAssetsUsd, orderDirection: Desc, where: {chainId_in: [1, 8453]}) { items { uniqueKey lltv
      loanAsset { symbol } collateralAsset { symbol } state { supplyAssetsUsd } morphoBlue { chain { id } }
      historicalState { borrowApy(options: {startTimestamp: %d, endTimestamp: %d, interval: DAY}) { x y } } } } }""" % (t0 - 40 * 86400, now)
    raw["morpho_markets"] = get("https://blue-api.morpho.org/graphql", {"query": q_m}, tries=2)
    q_v = """{ vaults(first: 80, orderBy: TotalAssetsUsd, orderDirection: Desc, where: {chainId_in: [1, 8453]}) { items { address name creationTimestamp
      asset { symbol } state { totalAssetsUsd } chain { id }
      historicalState { sharePriceUsd(options: {startTimestamp: %d, endTimestamp: %d, interval: DAY}) { x y }
                        totalAssetsUsd(options: {startTimestamp: %d, endTimestamp: %d, interval: DAY}) { x y } } } } }""" % (t0 - 40 * 86400, now, t0 - 40 * 86400, now)
    raw["morpho_vaults"] = get("https://blue-api.morpho.org/graphql", {"query": q_v}, tries=2)
    print(f"  morpho markets {'ok' if raw['morpho_markets'] else 'none'}, vaults {'ok' if raw['morpho_vaults'] else 'none'}", flush=True)
    save()
    # 288 HL user vaults
    vl = get("https://stats-data.hyperliquid.xyz/Mainnet/vaults", tries=2) or []
    print(f"  hl vaults listed: {len(vl)}", flush=True)
    keep = []
    for v in vl:
        s_ = v.get("summary", v)
        try:
            tvl = float(s_.get("tvl", 0))
        except (TypeError, ValueError):
            tvl = 0
        if tvl >= 200_000:
            keep.append(s_)
    keep = sorted(keep, key=lambda x: -float(x.get("tvl", 0)))[:150]
    raw["hl_vault_list"] = keep
    for s_ in keep:
        d = get("https://api.hyperliquid.xyz/info", {"type": "vaultDetails", "vaultAddress": s_["vaultAddress"]}, tries=2) or {}
        raw[f"hl_vault|{s_['vaultAddress']}"] = {"portfolio": d.get("portfolio"), "leaderCommission": d.get("leaderCommission"),
                                                "isClosed": d.get("isClosed")}
        time.sleep(0.15)
    print(f"  hl vault details: {len(keep)}", flush=True)
    save()


def job_batch8s():
    """Batch 8 Stage 2 data (#280, #288) + repair probes (docs/PREREG_BATCH8_20261122.md addendum 1)."""
    OUT.mkdir(parents=True, exist_ok=True)
    raw = {}

    def save():
        (OUT / "batch8s_raw.json").write_text(json.dumps(raw))
    t0, now = int(pd.Timestamp("2024-10-25", tz="UTC").timestamp()), int(time.time())
    der = {"BTC": "BTC-PERPETUAL", "ETH": "ETH-PERPETUAL"}
    der.update({c: f"{c}_USDC-PERPETUAL" for c in ("SOL", "XRP", "DOGE", "AVAX", "LINK", "LTC", "BNB", "SUI")})
    for c, inst in der.items():
        rows, t = [], t0
        while t < now:
            d = get(f"https://www.deribit.com/api/v2/public/get_funding_rate_history?instrument_name={inst}"
                    f"&start_timestamp={t * 1000}&end_timestamp={min(t + 30 * 86400, now) * 1000}", tries=3)
            rows += (d or {}).get("result", []) or []
            t += 30 * 86400
            time.sleep(0.2)
        raw[f"deribit_funding|{c}"] = [{"t": x["timestamp"], "r": x.get("interest_1h")} for x in rows]
        print(f"  deribit funding {c}: {len(rows)}", flush=True)
    save()
    for k in range(6):
        for c, inst in der.items():
            d = (get(f"https://www.deribit.com/api/v2/public/get_order_book?instrument_name={inst}&depth=50", tries=2) or {}).get("result") or {}
            if d.get("bids") is not None:
                raw.setdefault("deribit_books", []).append({"k": k, "coin": c, "inverse": c in ("BTC", "ETH"), "bids": d["bids"], "asks": d["asks"]})
        print(f"  deribit book snapshot {k + 1}/6", flush=True)
        save()
        if k < 5:
            time.sleep(600)
    vl = get("https://stats-data.hyperliquid.xyz/Mainnet/vaults", tries=3) or []
    cut = pd.Timestamp("2026-05-01", tz="UTC").timestamp() * 1000
    sel = []
    for v in vl:
        s_ = v.get("summary", v)
        try:
            tvl = float(s_.get("tvl") or 0)
        except (TypeError, ValueError):
            tvl = 0.0
        if float(s_.get("createTimeMillis") or 0) < cut and (s_.get("isClosed") or tvl >= 50_000):
            sel.append(s_)
    sel = sorted(sel, key=lambda x: -float(x.get("tvl") or 0))[:3000]
    raw["hl_vault_list"] = sel
    print(f"  hl vaults: {len(vl)} listed, {len(sel)} selected ({sum(1 for x in sel if x.get('isClosed'))} closed)", flush=True)
    for i, s_ in enumerate(sel):
        d = get("https://api.hyperliquid.xyz/info", {"type": "vaultDetails", "vaultAddress": s_["vaultAddress"]}, tries=4) or {}
        at = dict(d.get("portfolio") or []).get("allTime") or {}
        raw[f"hl_vault|{s_['vaultAddress']}"] = {"av": at.get("accountValueHistory"), "pnl": at.get("pnlHistory"),
                                                "leaderCommission": d.get("leaderCommission")}
        time.sleep(1.0)
        if i % 200 == 0:
            print(f"  vault details {i}/{len(sel)}", flush=True)
            save()
    save()
    # repair probes
    for day in ("20260801", "20260901", "20261001"):
        u = ("https://drift-historical-data-v2.s3.eu-west-1.amazonaws.com/program/dRiftyHA39MWEi3m9aunc5MzRF1JYuBsbn6VPcn33UH/"
             f"market/SOL-PERP/fundingRateRecords/{day[:4]}/{day}")
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=60) as r:
                txt = r.read().decode()[:3000]
            print(f"PROBE drift s3 {day}: answered {len(txt)} chars: {txt[:200]!r}", flush=True)
        except Exception as e:  # noqa: BLE001
            print(f"PROBE drift s3 {day}: {e}", flush=True)
    for u in ("https://api-evm.orderly.org/v1/public/funding_rate_history?symbol=PERP_BTC_USDC",
              "https://api.orderly.org/v1/public/funding_rate_history?symbol=PERP_BTC_USDC",
              "https://api-evm.orderly.org/v1/public/market_info/funding_history?symbol=PERP_BTC_USDC"):
        d = get(u, tries=1)
        print(f"PROBE orderly {u}: {json.dumps(d)[:300] if d else 'no answer'}", flush=True)
    d = get("https://blue-api.morpho.org/graphql", {"query": "{ vaults(first: 2) { items { address name } } }"}, tries=1)
    print(f"PROBE morpho minimal: {json.dumps(d)[:300] if d else 'no answer'}", flush=True)


def job_vxn():
    """VXN and VIX daily closes from FRED (docs/PREREG_OPTIONWRAP_20261122.md)."""
    OUT.mkdir(parents=True, exist_ok=True)
    for sid in ("VXNCLS", "VIXCLS"):
        try:
            with urllib.request.urlopen(urllib.request.Request(f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}", headers=UA), timeout=120) as r:
                txt = r.read().decode()
            (OUT / f"vxn_{sid.lower()}.csv").write_text(txt)
            print(f"{sid}: {len(txt.splitlines())} lines", flush=True)
        except Exception as e:  # noqa: BLE001
            print(f"{sid}: FAIL {e}", flush=True)


def _raw(url, tries=2):
    for k in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (research)"}), timeout=120) as r:
                return r.read().decode()
        except Exception as e:  # noqa: BLE001
            err = e
            if "404" in str(e):
                return None
            time.sleep(2 * (k + 1))
    print(f"  FAIL {url[:100]} {err}", flush=True)
    return None


def job_batch9():
    """Batch 9 data (docs/PREREG_BATCH9_20261122.md): FRED series, SPY, Cboe indices, VX futures settlements."""
    OUT.mkdir(parents=True, exist_ok=True)
    fx = ["DEXJPUS", "DEXUSAL", "DEXUSNZ", "DEXCAUS", "DEXSZUS", "DEXUSUK", "DEXUSEU", "DEXNOUS", "DEXSDUS", "DEXMXUS", "DEXBZUS", "DEXSFUS",
          "DEXKOUS", "DEXSIUS", "DEXTHUS", "DEXINUS", "DEXMAUS", "DEXCHUS"]
    rates = [f"IR3TIB01{c}M156N" for c in ("AU", "NZ", "CA", "CH", "GB", "EZ", "NO", "SE", "MX", "ZA", "JP", "US", "KR", "IN", "BR", "CN")]
    fred = {}
    for sid in fx + rates + ["DTB3", "DGS10", "INTDSRMYM193N", "VIXCLS"]:
        txt = _raw(f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}")
        if txt:
            fred[sid] = txt
        print(f"  fred {sid}: {len(txt.splitlines()) if txt else 'none'}", flush=True)
        time.sleep(0.3)
    (OUT / "batch9_fred.json").write_text(json.dumps(fred))
    spy = _raw("https://query1.finance.yahoo.com/v8/finance/chart/SPY?period1=946684800&period2=%d&interval=1d&events=div" % int(time.time()))
    print(f"  yahoo SPY: {'ok ' + str(len(spy)) if spy else 'none'}", flush=True)
    stq = _raw("https://stooq.com/q/d/l/?s=spy.us&i=d")
    print(f"  stooq SPY: {len(stq.splitlines()) if stq else 'none'}", flush=True)
    (OUT / "batch9_spy.json").write_text(json.dumps({"yahoo": spy, "stooq": stq}))
    cb = {}
    for sym in ("VIX", "VIX3M", "VIX9D", "PUT", "WPUT", "BXM", "BXMD", "BXY", "CLL", "CLLZ", "CNDR", "PPUT", "BFLY", "CMBO", "PUTR", "BXMW", "VXTH",
                "SPRO", "BXMC", "SPEN"):
        txt = _raw(f"https://cdn.cboe.com/api/global/us_indices/daily_prices/{sym}_History.csv")
        if txt:
            cb[sym] = txt
        print(f"  cboe {sym}: {len(txt.splitlines()) if txt else 'none'}", flush=True)
    (OUT / "batch9_cboe.json").write_text(json.dumps(cb))
    vx = {}
    for y in range(2013, 2028):
        for m in range(1, 13):
            nm, ny = (m % 12) + 1, y + (1 if m == 12 else 0)
            first = pd.Timestamp(ny, nm, 1)
            third_fri = first + pd.Timedelta(days=(4 - first.weekday()) % 7 + 14)
            exp = third_fri - pd.Timedelta(days=30)
            if exp > pd.Timestamp.now() + pd.Timedelta(days=270):
                continue
            for back in (0, 1, 2):
                d = exp - pd.Timedelta(days=back)
                txt = _raw(f"https://cdn.cboe.com/data/us/futures/market_statistics/historical_data/VX/VX_{d:%Y-%m-%d}.csv", tries=1)
                if txt:
                    vx[f"{d:%Y-%m-%d}"] = txt
                    break
            time.sleep(0.1)
        print(f"  vx contracts through {y}: {len(vx)}", flush=True)
    (OUT / "batch9_vx.json").write_text(json.dumps(vx))


def _text(html):
    import re as r_
    html = r_.sub(r"(?is)<(script|style|noscript).*?</\1>", " ", html)
    return r_.sub(r"\s+", " ", r_.sub(r"(?s)<[^>]+>", " ", html)).strip()


def _yahoo(sym, rng="2y"):
    t = _raw(f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?range={rng}&interval=1d&events=div", tries=2)
    return json.loads(t) if t else None


def job_batch10():
    """Batch 10 data (docs/PREREG_BATCH10_20261122.md)."""
    import re as r_
    OUT.mkdir(parents=True, exist_ok=True)
    out = {}

    def save():
        (OUT / "batch10_raw.json").write_text(json.dumps(out))
    # 1. CFD prop-firm pages (official sites only), shallow same-domain crawl on rule keywords
    starts = {"ftmo": ["https://ftmo.com/en/faq/", "https://ftmo.com/en/trading-objectives/", "https://ftmo.com/en/"],
              "fundednext": ["https://fundednext.com/", "https://help.fundednext.com/en/", "https://fundednext.com/competition"],
              "the5ers": ["https://the5ers.com/", "https://help.the5ers.com/"],
              "alphacapital": ["https://alphacapitalgroup.uk/", "https://alphacapitalgroup.uk/faq/"],
              "goatfunded": ["https://www.goatfundedtrader.com/", "https://www.goatfundedtrader.com/faq"],
              "audacity": ["https://audacitycapital.co.uk/", "https://audacitycapital.co.uk/faq/"]}
    kw = r_.compile(r"rule|objective|faq|payout|expert|advisor|\bea\b|bot|automat|countr|restrict|competition|pricing|price|challenge|evaluation|"
                    r"drawdown|loss|refund|scaling|program|account|help|article|collection", r_.I)
    pages = {}
    for firm, urls in starts.items():
        dom = urls[0].split("/")[2]
        queue, seen = list(urls), set()
        while queue and len(seen) < 30:
            u = queue.pop(0)
            if u in seen:
                continue
            seen.add(u)
            h = _raw(u, tries=1)
            if not h:
                continue
            pages[u] = _text(h)[:60000]
            for link in r_.findall(r'href="([^"#]+)"', h):
                if link.startswith("/"):
                    link = "https://" + dom + link
                if link.split("/")[2:3] == [dom] or (len(link.split("/")) > 2 and link.split("/")[2].endswith(dom.replace("www.", ""))):
                    if kw.search(link) and link not in seen and len(queue) < 200:
                        queue.append(link)
            time.sleep(0.3)
        print(f"  pages {firm}: {sum(1 for k in pages if dom.replace('www.', '') in k)}", flush=True)
    (OUT / "batch10_pages.json").write_text(json.dumps(pages))
    # 2. HIP-3 stock perps: 1h candles + funding premium (xyz dex)
    meta = get("https://api.hyperliquid.xyz/info", {"type": "meta", "dex": "xyz"}) or {}
    names = [a["name"] for a in meta.get("universe", [])]
    end = int(time.time() * 1000)
    for nm in names[:80]:
        c = get("https://api.hyperliquid.xyz/info", {"type": "candleSnapshot", "req": {"coin": nm, "interval": "1h",
                "startTime": end - 5000 * 3600 * 1000, "endTime": end}}, tries=4) or []
        out[f"hip3c|{nm}"] = [[x["t"], float(x["o"]), float(x["c"])] for x in c]
        time.sleep(1.0)
    print(f"  hip3 candles: {sum(1 for k in out if k.startswith('hip3c|') and out[k])}/{len(names[:80])}", flush=True)
    save()
    tick = sorted({nm.split(":")[1] for nm in names[:80]})
    for t_ in tick + ["SPY", "QQQ", "IWM", "EWY", "EWJ"]:
        y = _yahoo(t_, "1y")
        if y:
            out[f"yahoo|{t_}"] = y
        time.sleep(0.4)
    print(f"  yahoo tickers: {sum(1 for k in out if k.startswith('yahoo|'))}", flush=True)
    save()
    # 3. S&P 500 changes (Wikipedia wikitext) + prices of added tickers
    w = get("https://en.wikipedia.org/w/api.php?action=parse&page=List_of_S%26P_500_companies&prop=wikitext&format=json&formatversion=2", tries=2)
    wt = ((w or {}).get("parse") or {}).get("wikitext", "")
    out["wiki_sp500"] = wt
    adds = sorted(set(r_.findall(r"\{\{(?:NyseSymbol|NasdaqSymbol|Nyse|Nasdaq|Ticker)[^|}]*\|([A-Z.]+)", wt)))
    print(f"  wikipedia sp500 wikitext {len(wt)} chars; symbols {len(adds)}", flush=True)
    for t_ in adds[-200:]:
        if f"yahoo|{t_}" not in out:
            y = _yahoo(t_.replace(".", "-"), "2y")
            if y:
                out[f"yahoo|{t_}"] = y
            time.sleep(0.4)
    save()
    # 4. unlock calendar probe
    for u in ("https://api.llama.fi/emissions", "https://defillama-datasets.llama.fi/emissionsProtocolsList"):
        d = get(u, tries=1)
        out[f"emissions|{u}"] = d if d is None or len(json.dumps(d)) < 5_000_000 else "large"
        print(f"PROBE emissions {u}: {'answered' if d else 'no answer'}", flush=True)
    save()
    # 5. GeckoTerminal pools for redemption-floor / cooldown stables
    for q in ("LUSD", "BOLD", "feUSD", "sUSDe"):
        d = get(f"https://api.geckoterminal.com/api/v2/search/pools?query={q}", tries=2) or {}
        pools = sorted(d.get("data", []), key=lambda x: -float((x.get("attributes") or {}).get("reserve_in_usd") or 0))[:3]
        for pl in pools:
            net, addr = pl["relationships"]["network"]["data"]["id"], pl["attributes"]["address"]
            o = get(f"https://api.geckoterminal.com/api/v2/networks/{net}/pools/{addr}/ohlcv/day?limit=1000", tries=2) or {}
            out[f"gecko|{q}|{pl['attributes'].get('name')}|{net}"] = {"base_is": pl["relationships"]["base_token"]["data"]["id"],
                                                                     "ohlcv": ((o.get("data") or {}).get("attributes") or {}).get("ohlcv_list")}
            time.sleep(2.5)
        print(f"  gecko {q}: {len(pools)} pools", flush=True)
    d = get("https://coins.llama.fi/chart/ethereum:0x9d39a5de30e57443bff2a8307a4256c8797a3497?start=1730419200&span=800&period=1d", tries=2)
    out["susde_value"] = d
    save()
    # 6. Upbit notices + HL candles for named coins
    notes = []
    for u in ("https://api-manager.upbit.com/api/v1/announcements?os=web&page=%d&per_page=50&category=trade",
              "https://api-manager.upbit.com/api/v1/notices?page=%d&per_page=50"):
        for pg in range(1, 11):
            d = get(u % pg, tries=1)
            items = (((d or {}).get("data") or {}).get("notices") or ((d or {}).get("data") or {}).get("list") or []) if isinstance(d, dict) else []
            if not items:
                break
            notes += items
            time.sleep(0.5)
        if notes:
            break
    out["upbit_notices"] = notes
    print(f"  upbit notices: {len(notes)}", flush=True)
    syms = set()
    for n in notes:
        syms |= set(r_.findall(r"\(([A-Z0-9]{2,10})\)", str(n.get("title", ""))))
    hl = {a["name"] for a in (get("https://api.hyperliquid.xyz/info", {"type": "meta"}) or {}).get("universe", [])}
    for c in sorted(syms & hl)[:120]:
        k = get("https://api.hyperliquid.xyz/info", {"type": "candleSnapshot", "req": {"coin": c, "interval": "1h",
                "startTime": end - 5000 * 3600 * 1000, "endTime": end}}, tries=4) or []
        out[f"hlc|{c}"] = [[x["t"], float(x["o"]), float(x["c"])] for x in k]
        time.sleep(1.0)
    for c in ("BTC",):
        k = get("https://api.hyperliquid.xyz/info", {"type": "candleSnapshot", "req": {"coin": c, "interval": "1h",
                "startTime": end - 5000 * 3600 * 1000, "endTime": end}}, tries=4) or []
        out[f"hlc|{c}"] = [[x["t"], float(x["o"]), float(x["c"])] for x in k]
    print(f"  hl candles for notice coins: {sum(1 for k in out if k.startswith('hlc|'))}", flush=True)
    save()


def job_smallcap():
    """#320 small-capacity high-reward pools (docs/PREREG_SMALLCAP_20261122.md)."""
    OUT.mkdir(parents=True, exist_ok=True)
    pools = pd.DataFrame((get("https://yields.llama.fi/pools") or {}).get("data", []))
    pools["tvlUsd"] = pd.to_numeric(pools["tvlUsd"], errors="coerce")
    # wide net on today's list: TVL $50K-$5M and APY >= 30% (selection by the registered thresholds happens day by day in the analysis)
    u = pools[(pools["tvlUsd"].between(5e4, 5e6)) & ((pools["apyBase"].fillna(0) + pools["apyReward"].fillna(0)) >= 30)]
    print(f"pools listed {len(pools)}; candidates {len(u)}", flush=True)
    keep = [c for c in ("pool", "chain", "project", "symbol", "tvlUsd", "apyBase", "apyReward", "stablecoin", "ilRisk", "exposure",
                        "rewardTokens", "underlyingTokens") if c in u]
    u[keep].to_parquet(OUT / "smallcap_pools.parquet", index=False)
    rows = []
    for i, p in enumerate(u["pool"].head(1500)):
        for x in (get(f"https://yields.llama.fi/chart/{p}", tries=2) or {}).get("data", []):
            if x.get("timestamp", "") >= "2025-09-01":
                rows.append({"pool": p, "ts": x["timestamp"], "tvlUsd": x.get("tvlUsd"), "apyBase": x.get("apyBase"), "apyReward": x.get("apyReward")})
        if i % 100 == 0:
            print(f"  charts {i}/{min(len(u), 1500)}", flush=True)
            pd.DataFrame(rows).to_parquet(OUT / "smallcap_charts.parquet", index=False)
        time.sleep(0.25)
    pd.DataFrame(rows).to_parquet(OUT / "smallcap_charts.parquet", index=False)
    toks = set()
    for col in ("rewardTokens", "underlyingTokens"):
        if col in u:
            for v in u[col].dropna():
                toks |= {str(t) for t in (list(v) if hasattr(v, "__iter__") and not isinstance(v, str) else [v]) if t}
    slug = {"Ethereum": "ethereum", "Arbitrum": "arbitrum", "Base": "base", "BSC": "bsc", "Polygon": "polygon", "Optimism": "optimism",
            "Avalanche": "avax", "Solana": "solana", "Sonic": "sonic", "Hyperliquid L1": "hyperliquid", "Sui": "sui", "Linea": "linea"}
    chain_of = {}
    for _, r in u.iterrows():
        for col in ("rewardTokens", "underlyingTokens"):
            v = r.get(col)
            if v is not None and hasattr(v, "__iter__") and not isinstance(v, str):
                for t in v:
                    chain_of.setdefault(str(t), slug.get(r["chain"]))
    px = []
    t0 = int(pd.Timestamp("2025-09-01", tz="UTC").timestamp())
    for j, t in enumerate(sorted(toks)[:2500]):
        ch = chain_of.get(t)
        if not ch or t.startswith("0x0000000000000000000000000000000000000000"):
            continue
        key = f"{ch}:{t}"
        d = get(f"https://coins.llama.fi/chart/{key}?start={t0}&span=500&period=1d", tries=1)
        for x in (((d or {}).get("coins") or {}).get(key) or {}).get("prices", []):
            px.append({"token": t, "chain": ch, "ts": x["timestamp"], "price": x["price"]})
        if j % 200 == 0:
            print(f"  token prices {j}/{min(len(toks), 2500)}", flush=True)
            pd.DataFrame(px).to_parquet(OUT / "smallcap_prices.parquet", index=False)
        time.sleep(0.2)
    pd.DataFrame(px).to_parquet(OUT / "smallcap_prices.parquet", index=False)
    print(f"token price rows {len(px)}", flush=True)


def job_merkl():
    """#321 Merkl opportunities + any history endpoints (docs/PREREG_SMALLCAP_20261122.md addendum 1)."""
    OUT.mkdir(parents=True, exist_ok=True)
    opp, page = [], 0
    while page < 60:
        d = get(f"https://api.merkl.xyz/v4/opportunities?items=100&page={page}&status=LIVE,PAST", tries=2)
        if not d or not isinstance(d, list):
            break
        opp += d
        page += 1
        time.sleep(0.3)
    print(f"merkl opportunities: {len(opp)}", flush=True)
    keep = []
    for o in opp:
        try:
            tvl = float(o.get("tvl") or 0)
        except (TypeError, ValueError):
            tvl = 0.0
        keep.append({k: o.get(k) for k in ("id", "chainId", "type", "identifier", "name", "status", "action", "tvl", "apr", "dailyRewards",
                                            "startTimestamp", "endTimestamp")} | {"tokens": [t.get("symbol") for t in (o.get("tokens") or [])]})
    hist = {}
    small = [k for k in keep if 1e5 <= float(k.get("tvl") or 0) <= 2e6][:600]
    for k in small:
        for u in (f"https://api.merkl.xyz/v4/opportunities/{k['id']}/metrics", f"https://api.merkl.xyz/v4/opportunities/{k['id']}/aprs"):
            d = get(u, tries=1)
            if d:
                hist[k["id"]] = d
                break
        time.sleep(0.25)
    print(f"merkl small opportunities {len(small)}; with history {len(hist)}", flush=True)
    (OUT / "merkl_raw.json").write_text(json.dumps({"opportunities": keep, "history": hist}))


def job_sweep3():
    """Sweep 3 data (docs/PREREG_SWEEP3_20261122.md): dYdX trades + HL 1m candles (#322); DefiLlama vault/lending pools + charts (#324, #325)."""
    OUT.mkdir(parents=True, exist_ok=True)
    out = {}
    end = int(time.time() * 1000)
    for c in ("ARB", "AVAX", "LINK", "OP", "SUI", "DOGE", "LTC", "BNB", "XRP", "SOL", "ETH", "BTC"):
        trades, before = [], None
        for _ in range(40):
            u = f"https://indexer.dydx.trade/v4/trades/perpetualMarket/{c}-USD?limit=100" + (f"&createdBeforeOrAtHeight={before}" if before else "")
            d = get(u, tries=2) or {}
            t = d.get("trades") or []
            if not t:
                break
            trades += [{"t": x["createdAt"], "side": x["side"], "size": float(x["size"]), "price": float(x["price"]), "h": int(x["createdAtHeight"])} for x in t]
            before = int(t[-1]["createdAtHeight"]) - 1
            if pd.Timestamp(t[-1]["createdAt"]) < pd.Timestamp.now(tz="UTC") - pd.Timedelta(days=3):
                break
            time.sleep(0.2)
        out[f"dydx_trades|{c}"] = trades
        k = get("https://api.hyperliquid.xyz/info", {"type": "candleSnapshot", "req": {"coin": c, "interval": "1m",
                "startTime": end - 5000 * 60 * 1000, "endTime": end}}, tries=4) or []
        out[f"hl1m|{c}"] = [[x["t"], float(x["o"]), float(x["c"])] for x in k]
        print(f"  {c}: dydx trades {len(trades)}, hl 1m {len(k)}", flush=True)
        time.sleep(1.0)
    pools = pd.DataFrame((get("https://yields.llama.fi/pools") or {}).get("data", []))
    pools["tvlUsd"] = pd.to_numeric(pools["tvlUsd"], errors="coerce")
    protos = {p["slug"]: p.get("category") for p in (get("https://api.llama.fi/protocols") or []) if isinstance(p, dict) and p.get("slug")}
    pools["category"] = pools["project"].map(protos)
    vault = pools[(pools["category"].isin(["Derivatives", "Options Vault", "Options", "Perps"])) & (pools["tvlUsd"] >= 5e5)
                  & ~pools["project"].isin(["gains-network", "hyperliquid-hlp"])]
    lend = pools[(pools["category"].isin(["Lending", "CDP"])) & (pools["stablecoin"] == True) & (pools["tvlUsd"].between(1e5, 5e6))]  # noqa: E712
    print(f"  vault pools {len(vault)}, small stable lending pools {len(lend)}", flush=True)
    keep = [c for c in ("pool", "chain", "project", "symbol", "tvlUsd", "apyBase", "apyReward", "category", "stablecoin", "underlyingTokens") if c in pools]
    out["vault_pools"] = vault[keep].astype(str).to_dict("records")
    out["lend_pools"] = lend[keep].astype(str).to_dict("records")
    for grp, df in (("vault", vault), ("lend", lend)):
        for i, p in enumerate(df["pool"].head(800)):
            out[f"chart|{grp}|{p}"] = [{"ts": x["timestamp"], "tvl": x.get("tvlUsd"), "b": x.get("apyBase"), "r": x.get("apyReward")}
                                       for x in (get(f"https://yields.llama.fi/chart/{p}", tries=2) or {}).get("data", [])
                                       if x.get("timestamp", "") >= "2025-09-01"]
            time.sleep(0.25)
        print(f"  charts {grp}: {min(len(df), 800)}", flush=True)
    (OUT / "sweep3_raw.json").write_text(json.dumps(out))


def job_fred9():
    """Batch 9 FRED series again (the first attempt timed out with a browser user agent)."""
    OUT.mkdir(parents=True, exist_ok=True)
    fx = ["DEXJPUS", "DEXUSAL", "DEXUSNZ", "DEXCAUS", "DEXSZUS", "DEXUSUK", "DEXUSEU", "DEXNOUS", "DEXSDUS", "DEXMXUS", "DEXBZUS", "DEXSFUS",
          "DEXKOUS", "DEXSIUS", "DEXTHUS", "DEXINUS", "DEXMAUS", "DEXCHUS"]
    rates = [f"IR3TIB01{c}M156N" for c in ("AU", "NZ", "CA", "CH", "GB", "EZ", "NO", "SE", "MX", "ZA", "JP", "US", "KR", "IN", "BR", "CN")]
    fred = {}
    for sid in fx + rates + ["DTB3", "DGS10", "INTDSRMYM193N", "VIXCLS"]:
        for k in range(3):
            try:
                with urllib.request.urlopen(urllib.request.Request(f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}", headers=UA), timeout=180) as r:
                    fred[sid] = r.read().decode()
                break
            except Exception as e:  # noqa: BLE001
                print(f"  fred {sid} try {k + 1}: {e}", flush=True)
                time.sleep(5 * (k + 1))
        print(f"  fred {sid}: {len(fred[sid].splitlines()) if sid in fred else 'none'}", flush=True)
        time.sleep(1.0)
    (OUT / "batch9_fred.json").write_text(json.dumps(fred))


def job_batch10b():
    """Remainder of batch 10 after the GeckoTerminal crash: pools (robust), sUSDe value, Upbit notices + HL candles."""
    import re as r_
    OUT.mkdir(parents=True, exist_ok=True)
    out = {}
    for q in ("LUSD", "BOLD", "feUSD", "sUSDe"):
        d = get(f"https://api.geckoterminal.com/api/v2/search/pools?query={q}", tries=2) or {}
        pools = sorted(d.get("data", []) or [], key=lambda x: -float(((x or {}).get("attributes") or {}).get("reserve_in_usd") or 0))[:3]
        for pl in pools:
            rel = pl.get("relationships") or {}
            net = (((rel.get("network") or {}).get("data") or {}).get("id")) or (pl.get("id", "").split("_")[0] if "_" in pl.get("id", "") else None)
            addr = (pl.get("attributes") or {}).get("address")
            if not net or not addr:
                continue
            o = get(f"https://api.geckoterminal.com/api/v2/networks/{net}/pools/{addr}/ohlcv/day?limit=1000", tries=2) or {}
            out[f"gecko|{q}|{(pl.get('attributes') or {}).get('name')}|{net}"] = {
                "base_is": (((rel.get("base_token") or {}).get("data") or {}).get("id")),
                "ohlcv": ((o.get("data") or {}).get("attributes") or {}).get("ohlcv_list")}
            time.sleep(2.5)
        print(f"  gecko {q}: {len(pools)} pools", flush=True)
    out["susde_value"] = get("https://coins.llama.fi/chart/ethereum:0x9d39a5de30e57443bff2a8307a4256c8797a3497?start=1730419200&span=800&period=1d", tries=2)
    notes = []
    for u in ("https://api-manager.upbit.com/api/v1/announcements?os=web&page=%d&per_page=50&category=trade",
              "https://api-manager.upbit.com/api/v1/notices?page=%d&per_page=50"):
        for pg in range(1, 11):
            d = get(u % pg, tries=1)
            data = (d or {}).get("data") if isinstance(d, dict) else None
            items = (data.get("notices") or data.get("list") or []) if isinstance(data, dict) else []
            if not items:
                break
            notes += items
            time.sleep(0.5)
        if notes:
            break
    out["upbit_notices"] = notes
    print(f"  upbit notices: {len(notes)}", flush=True)
    syms = set()
    for n in notes:
        syms |= set(r_.findall(r"\(([A-Z0-9]{2,10})\)", str(n.get("title", ""))))
    hl = {a["name"] for a in (get("https://api.hyperliquid.xyz/info", {"type": "meta"}) or {}).get("universe", [])}
    end = int(time.time() * 1000)
    for c in sorted(syms & hl)[:120] + ["BTC"]:
        k = get("https://api.hyperliquid.xyz/info", {"type": "candleSnapshot", "req": {"coin": c, "interval": "1h",
                "startTime": end - 5000 * 3600 * 1000, "endTime": end}}, tries=4) or []
        out[f"hlc|{c}"] = [[x["t"], float(x["o"]), float(x["c"])] for x in k]
        time.sleep(1.0)
    print(f"  hl candles: {sum(1 for k in out if k.startswith('hlc|'))}", flush=True)
    (OUT / "batch10b_raw.json").write_text(json.dumps(out))


def job_repair8():
    """Batch 8 repairs (PREREG_BATCH8 addendum 1): Orderly funding without time parameters; Morpho with simpler GraphQL; errors kept."""
    OUT.mkdir(parents=True, exist_ok=True)
    out = {}
    for c in ("BTC", "ETH", "SOL", "XRP", "DOGE", "AVAX", "LINK", "SUI", "ARB", "OP", "LTC", "BNB"):
        rows = []
        for pg in range(1, 30):
            d = get(f"https://api-evm.orderly.org/v1/public/funding_rate_history?symbol=PERP_{c}_USDC&page={pg}&size=500", tries=2) or {}
            r = ((d.get("data") or {}).get("rows")) or []
            rows += r
            if len(r) < 500:
                break
            time.sleep(0.3)
        out[f"orderly|{c}"] = rows
        print(f"  orderly {c}: {len(rows)}", flush=True)
    for name, q in (("vaults", "{ vaults(first: 100) { items { address name asset { symbol } state { totalAssetsUsd } historicalState { sharePriceUsd { x y } } } } }"),
                    ("markets", "{ markets(first: 100) { items { uniqueKey lltv loanAsset { symbol } collateralAsset { symbol } state { supplyAssetsUsd } historicalState { borrowApy { x y } } } } }")):
        req = urllib.request.Request("https://blue-api.morpho.org/graphql", data=json.dumps({"query": q}).encode(),
                                     headers={**UA, "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                out[f"morpho_{name}"] = json.loads(r.read().decode())
        except urllib.error.HTTPError as e:  # keep the error body to learn the schema
            out[f"morpho_{name}"] = {"error": e.code, "body": e.read().decode()[:3000]}
        except Exception as e:  # noqa: BLE001
            out[f"morpho_{name}"] = {"error": str(e)}
        print(f"  morpho {name}: {str(out[f'morpho_{name}'])[:200]}", flush=True)
    (OUT / "repair8_raw.json").write_text(json.dumps(out))


def job_addprice():
    """#303 Stage 2: Yahoo daily prices for every S&P 500 constituent added 2024-11..2026-10 (PREREG_BATCH10 addendum 1)."""
    import re as r_
    OUT.mkdir(parents=True, exist_ok=True)
    w = get("https://en.wikipedia.org/w/api.php?action=parse&page=List_of_S%26P_500_companies&prop=wikitext&format=json&formatversion=2", tries=2)
    wt = ((w or {}).get("parse") or {}).get("wikitext", "")
    adds = []
    for row in wt.split("|-")[1:]:
        sym = r_.search(r"\{\{(?:NyseSymbol|NasdaqSymbol|Nyse|Nasdaq|Ticker|BZX link|NYSE American link)[^|}]*\|([A-Z.]+)", row)
        dt = r_.search(r"\|\|\s*(\d{4}-\d{2}-\d{2})\s", row)
        if sym and dt and "2024-10-01" <= dt.group(1) <= "2026-11-30":
            adds.append((sym.group(1), dt.group(1)))
    out = {"wiki_sp500": wt, "adds": adds}
    for t_ in sorted({a for a, _ in adds}) + ["SPY"]:
        y = _yahoo(t_.replace(".", "-"), "2y")
        if y:
            out[f"yahoo|{t_}"] = y
        time.sleep(0.5)
    print(f"  additions in window {len(adds)}; priced {sum(1 for k in out if k.startswith('yahoo|'))}", flush=True)
    (OUT / "addprice_raw.json").write_text(json.dumps(out))


def job_sweep4():
    """Sweep 4 data (docs/PREREG_SWEEP4_20261122.md)."""
    import re as r_
    OUT.mkdir(parents=True, exist_ok=True)
    out = {}

    def save():
        (OUT / "sweep4_raw.json").write_text(json.dumps(out))
    end = int(time.time() * 1000)
    # 330 pump.fun graduated coins + migrated-pool OHLCV
    coins = []
    for base in ("https://frontend-api-v3.pump.fun", "https://frontend-api.pump.fun"):
        for off in range(0, 2000, 50):
            d = get(f"{base}/coins?offset={off}&limit=50&sort=created_timestamp&order=DESC&includeNsfw=false&complete=true", tries=1)
            if not isinstance(d, list) or not d:
                break
            coins += d
            time.sleep(0.4)
        if coins:
            break
    out["pump_coins"] = [{k: c.get(k) for k in ("mint", "symbol", "created_timestamp", "complete", "raydium_pool", "pump_swap_pool",
                                                 "king_of_the_hill_timestamp", "last_trade_timestamp", "usd_market_cap")} for c in coins]
    print(f"  pump.fun graduated coins: {len(coins)}", flush=True)
    n = 0
    for c in out["pump_coins"][:400]:
        pool = c.get("pump_swap_pool") or c.get("raydium_pool")
        if not pool:
            continue
        o = get(f"https://api.geckoterminal.com/api/v2/networks/solana/pools/{pool}/ohlcv/hour?limit=200&before_timestamp="
                f"{int((c.get('created_timestamp') or end) / 1000) + 7 * 86400}", tries=2) or {}
        out[f"pump_ohlcv|{c['mint']}"] = ((o.get("data") or {}).get("attributes") or {}).get("ohlcv_list")
        n += 1
        time.sleep(2.2)
    print(f"  pump pools with OHLCV requested: {n}", flush=True)
    save()
    # 332 index tokens probe
    for u in ("https://api.indexcoop.com/v2/tokens", "https://api.indexcoop.com/tokens", "https://api.indexcoop.com/nav"):
        d = get(u, tries=1)
        out[f"indexcoop_probe|{u}"] = d if d is None or len(json.dumps(d)) < 500_000 else "large"
        print(f"PROBE indexcoop {u}: {'answered' if d else 'no answer'}", flush=True)
    # 334 Coinbase listings
    prods = get("https://api.exchange.coinbase.com/products", tries=2) or []
    usd = [p_ for p_ in prods if isinstance(p_, dict) and p_.get("quote_currency") == "USD"]
    hl = {a["name"] for a in (get("https://api.hyperliquid.xyz/info", {"type": "meta"}) or {}).get("universe", [])}
    first = {}
    for p_ in usd:
        base_ = p_.get("base_currency")
        if base_ not in hl:
            continue
        t = int(pd.Timestamp("2024-06-01", tz="UTC").timestamp())
        while t < time.time():
            c = get(f"https://api.exchange.coinbase.com/products/{p_['id']}/candles?granularity=86400&start={t}&end={t + 299 * 86400}", tries=1)
            if isinstance(c, list) and c:
                first[base_] = min(x[0] for x in c)
                break
            t += 299 * 86400
            time.sleep(0.3)
    out["coinbase_first_day"] = first
    print(f"  coinbase USD products on HL: {len(first)}", flush=True)
    for cn in sorted(set(first) | {"BTC"}):
        k = get("https://api.hyperliquid.xyz/info", {"type": "candleSnapshot", "req": {"coin": cn, "interval": "1d",
                "startTime": end - 900 * 86400 * 1000, "endTime": end}}, tries=4) or []
        out[f"hld|{cn}"] = [[x["t"], float(x["c"])] for x in k]
        time.sleep(0.8)
    save()
    # 335 buybacks
    ov = get("https://api.llama.fi/overview/fees?excludeTotalDataChart=true&excludeTotalDataChartBreakdown=true&dataType=dailyHoldersRevenue", tries=2) or {}
    prot = [p_ for p_ in (ov.get("protocols") or []) if (p_.get("total30d") or 0) > 100_000][:120]
    plist = {p_["slug"]: p_ for p_ in (get("https://api.llama.fi/protocols", tries=2) or []) if isinstance(p_, dict) and p_.get("slug")}
    out["buyback_protocols"] = []
    for p_ in prot:
        slug = p_.get("slug") or p_.get("name")
        h = get(f"https://api.llama.fi/summary/fees/{slug}?dataType=dailyHoldersRevenue", tries=1) or {}
        meta = plist.get(slug, {})
        gid = meta.get("gecko_id")
        out["buyback_protocols"].append({"slug": slug, "gecko_id": gid, "mcap": meta.get("mcap"), "chart": h.get("totalDataChart")})
        if gid:
            c = get(f"https://coins.llama.fi/chart/coingecko:{gid}?start={int(pd.Timestamp('2024-09-01', tz='UTC').timestamp())}&span=820&period=1d", tries=1)
            out[f"price|{gid}"] = (((c or {}).get("coins") or {}).get(f"coingecko:{gid}") or {}).get("prices")
        time.sleep(0.4)
    print(f"  buyback protocols: {len(out['buyback_protocols'])}", flush=True)
    c = get(f"https://coins.llama.fi/chart/coingecko:bitcoin?start={int(pd.Timestamp('2024-09-01', tz='UTC').timestamp())}&span=820&period=1d", tries=2)
    out["price|bitcoin"] = (((c or {}).get("coins") or {}).get("coingecko:bitcoin") or {}).get("prices")
    save()
    # 336 / 337 / 338 / 343 Wikipedia + Yahoo
    for title in ("Nasdaq-100", "Historical_components_of_the_S%26P_500", "List_of_S%26P_500_companies", "Corporate_spin-off",
                  "List_of_spin-offs", "Cryptocurrency_exchange-traded_fund"):
        w = get(f"https://en.wikipedia.org/w/api.php?action=parse&page={title}&prop=wikitext&format=json&formatversion=2", tries=2)
        out[f"wiki|{title}"] = ((w or {}).get("parse") or {}).get("wikitext", "")
        print(f"  wiki {title}: {len(out[f'wiki|{title}'])} chars", flush=True)
    tickers = set()
    for k in ("wiki|Nasdaq-100", "wiki|Historical_components_of_the_S%26P_500"):
        tickers |= set(r_.findall(r"\{\{(?:NyseSymbol|NasdaqSymbol|Nyse|Nasdaq|Ticker|nasdaq|nyse)[^|}]*\|([A-Z.]{1,6})", out[k]))
    for t_ in sorted(tickers)[:700]:
        y = _yahoo(t_.replace(".", "-"), "2y")
        if y:
            out[f"yahoo|{t_}"] = y
        time.sleep(0.35)
    for t_ in ("SPY", "QQQ", "GC=F"):
        out[f"yahoo|{t_}"] = _yahoo(t_, "2y")
    print(f"  yahoo tickers: {sum(1 for k in out if k.startswith('yahoo|'))}", flush=True)
    save()
    # 339 tokenised gold
    for nm, key in (("paxg", "ethereum:0x45804880de22913dafe09f4980848ece6ecbaf78"), ("xaut", "ethereum:0x68749665ff8d2d112fa859aa293f07a622782f38")):
        c = get(f"https://coins.llama.fi/chart/{key}?start={int(pd.Timestamp('2024-09-01', tz='UTC').timestamp())}&span=820&period=1d", tries=2)
        out[f"price|{nm}"] = (((c or {}).get("coins") or {}).get(key) or {}).get("prices")
    # 342 unlock schedules probe
    lst = get("https://defillama-datasets.llama.fi/emissionsProtocolsList", tries=2) or []
    out["emissions_list"] = lst if isinstance(lst, list) else []
    got = 0
    for name in (out["emissions_list"] or [])[:150]:
        nm = name if isinstance(name, str) else (name or {}).get("name")
        if not nm:
            continue
        d = get(f"https://defillama-datasets.llama.fi/emissions/{nm}", tries=1)
        if d:
            out[f"emission|{nm}"] = d if len(json.dumps(d)) < 400_000 else {"truncated": True, "keys": list(d)[:20] if isinstance(d, dict) else None}
            got += 1
        time.sleep(0.2)
    print(f"  emission schedules: {got}", flush=True)
    save()


def _sp_changes(wt):
    """Rows of 'Historical components of the S&P 500': (effective, added, removed, reason, announcement yyyymmdd or None)."""
    import re as r_
    rows = []
    for blk in wt.split("|-")[1:]:
        cells = [c.strip() for c in r_.split(r"\n\|\|?", "\n" + blk.strip()) if c.strip()]
        if len(cells) < 5:
            continue
        m = r_.match(r"([A-Z][a-z]+ \d{1,2}, \d{4})", cells[0])
        if not m:
            continue
        ann = r_.search(r"announcements/(\d{8})", blk) or r_.search(r"\|\s*date\s*=\s*(\d{4}-\d{2}-\d{2})", blk)
        tick = lambda c: c if r_.fullmatch(r"[A-Z][A-Z.]{0,5}", c) else None  # noqa: E731
        rows.append((m.group(1), tick(cells[1]), tick(cells[3]) if len(cells) > 3 else None, cells[5] if len(cells) > 5 else "",
                     ann.group(1).replace("-", "") if ann else None))
    return rows


def job_sweep4b():
    """Sweep 4 follow-up (same rules): Yahoo prices for S&P 500 changes 2024-10..2026-11 (#337, #303 check); trimmed unlock schedules (#342)."""
    OUT.mkdir(parents=True, exist_ok=True)
    out = {}
    w = get("https://en.wikipedia.org/w/api.php?action=parse&page=Historical_components_of_the_S%26P_500&prop=wikitext&format=json&formatversion=2", tries=2)
    wt = ((w or {}).get("parse") or {}).get("wikitext", "")
    rows = _sp_changes(wt)
    rows = [r for r in rows if pd.Timestamp(r[0]) >= pd.Timestamp("2024-10-01")]
    out["sp_changes"] = rows
    tick = sorted({t for r in rows for t in (r[1], r[2]) if t})
    for t_ in tick + ["SPY"]:
        y = _yahoo(t_.replace(".", "-"), "2y")
        if y:
            out[f"yahoo|{t_}"] = y
        time.sleep(0.35)
    print(f"  S&P changes since 2024-10: {len(rows)} rows; priced {sum(1 for k in out if k.startswith('yahoo|'))}/{len(tick) + 1}", flush=True)
    lst = get("https://defillama-datasets.llama.fi/emissionsProtocolsList", tries=2) or []
    hl = {a["name"] for a in (get("https://api.hyperliquid.xyz/info", {"type": "meta"}) or {}).get("universe", [])}
    end = int(time.time() * 1000)
    n = 0
    for nm in lst:
        d = get(f"https://defillama-datasets.llama.fi/emissions/{nm}", tries=1)
        if not isinstance(d, dict):
            continue
        gid = d.get("gecko_id")
        chart = d.get("unlockUsdChart") or []
        chart = [x for x in chart if isinstance(x, (list, tuple)) and len(x) == 2 and x[0] >= 1725000000]
        sym = None
        if gid:
            c = get(f"https://coins.llama.fi/prices/current/coingecko:{gid}", tries=1) or {}
            sym = (((c.get("coins") or {}).get(f"coingecko:{gid}")) or {}).get("symbol")
        out[f"emission|{nm}"] = {"gecko_id": gid, "symbol": sym, "unlockUsdChart": chart, "supplyMetrics": d.get("supplyMetrics")}
        if sym and sym.upper() in hl:
            k = get("https://api.hyperliquid.xyz/info", {"type": "candleSnapshot", "req": {"coin": sym.upper(), "interval": "1d",
                    "startTime": end - 900 * 86400 * 1000, "endTime": end}}, tries=3) or []
            out[f"hld|{sym.upper()}"] = [[x["t"], float(x["c"])] for x in k]
            c2 = get(f"https://coins.llama.fi/chart/coingecko:{gid}?start={int(pd.Timestamp('2024-09-01', tz='UTC').timestamp())}&span=820&period=1d", tries=1)
            out[f"price|{gid}"] = (((c2 or {}).get("coins") or {}).get(f"coingecko:{gid}") or {}).get("prices")
            n += 1
            time.sleep(0.6)
        time.sleep(0.2)
    k = get("https://api.hyperliquid.xyz/info", {"type": "candleSnapshot", "req": {"coin": "BTC", "interval": "1d",
            "startTime": end - 900 * 86400 * 1000, "endTime": end}}, tries=3) or []
    out["hld|BTC"] = [[x["t"], float(x["c"])] for x in k]
    print(f"  emission schedules {sum(1 for x in out if x.startswith('emission|'))}; on HL with candles {n}", flush=True)
    (OUT / "sweep4b_raw.json").write_text(json.dumps(out))


def _llama_chart(key, start="2024-09-01"):
    """Daily prices from coins.llama.fi in <= 300-day chunks (a span above the API's limit returns nothing)."""
    out, t = [], int(pd.Timestamp(start, tz="UTC").timestamp())
    while t < time.time():
        d = get(f"https://coins.llama.fi/chart/{key}?start={t}&span=300&period=1d", tries=2)
        out += (((d or {}).get("coins") or {}).get(key) or {}).get("prices") or []
        t += 300 * 86400
        time.sleep(0.3)
    return out


def job_sweep4c():
    """Sweep 4 prices again in valid chunks (#335 buyback tokens + BTC, #339 PAXG / XAUT)."""
    OUT.mkdir(parents=True, exist_ok=True)
    r = json.load(open(OUT / "sweep4_raw.json"))
    out = {}
    ids = sorted({p_["gecko_id"] for p_ in r.get("buyback_protocols", []) if p_.get("gecko_id")} | {"bitcoin", "pax-gold", "tether-gold"})
    for g in ids:
        out[f"price|{g}"] = _llama_chart(f"coingecko:{g}")
    print(f"  prices: {sum(1 for v in out.values() if v)}/{len(ids)} ids with data", flush=True)
    (OUT / "sweep4c_raw.json").write_text(json.dumps(out))


def job_sweep4d():
    """#330: pump.fun coins graduated 2-10 days before the fetch, migrated-pool hourly OHLCV (PREREG_SWEEP4 addendum 2)."""
    OUT.mkdir(parents=True, exist_ok=True)
    coins, now_ms = [], time.time() * 1000
    for off in range(0, 6000, 50):
        d = get(f"https://frontend-api-v3.pump.fun/coins?offset={off}&limit=50&sort=created_timestamp&order=DESC&includeNsfw=false&complete=true", tries=1)
        if not isinstance(d, list) or not d:
            break
        coins += d
        if (d[-1].get("created_timestamp") or now_ms) < now_ms - 12 * 86400 * 1000:
            break
        time.sleep(0.4)
    sel = [c for c in coins if (c.get("pump_swap_pool") or c.get("raydium_pool"))
           and now_ms - 10 * 86400 * 1000 <= (c.get("created_timestamp") or 0) <= now_ms - 2 * 86400 * 1000]
    step = max(1, len(sel) // 400)
    sel = sel[::step][:400]
    out = {"pump_coins": [{k: c.get(k) for k in ("mint", "symbol", "created_timestamp", "pump_swap_pool", "raydium_pool")} for c in sel]}
    for c in sel:
        pool = c.get("pump_swap_pool") or c.get("raydium_pool")
        o = get(f"https://api.geckoterminal.com/api/v2/networks/solana/pools/{pool}/ohlcv/hour?limit=1000", tries=2) or {}
        out[f"pump_ohlcv|{c['mint']}"] = ((o.get("data") or {}).get("attributes") or {}).get("ohlcv_list")
        time.sleep(2.2)
    print(f"  pump coins scanned {len(coins)}; graduated 2-10 days ago sampled {len(sel)}", flush=True)
    (OUT / "sweep4d_raw.json").write_text(json.dumps(out))


# ---------------------------------------------------------------- #361 / #362 (docs/PREREG_SOLVER_RELAY_20261123.md)
_RC = [0x0000000000000001, 0x0000000000008082, 0x800000000000808A, 0x8000000080008000, 0x000000000000808B, 0x0000000080000001,
       0x8000000080008081, 0x8000000000008009, 0x000000000000008A, 0x0000000000000088, 0x0000000080008009, 0x000000008000000A,
       0x000000008000808B, 0x800000000000008B, 0x8000000000008089, 0x8000000000008003, 0x8000000000008002, 0x8000000000000080,
       0x000000000000800A, 0x800000008000000A, 0x8000000080008081, 0x8000000000008080, 0x0000000080000001, 0x8000000080008008]
_ROT = [[0, 36, 3, 41, 18], [1, 44, 10, 45, 2], [62, 6, 43, 15, 61], [28, 55, 25, 21, 56], [27, 20, 39, 8, 14]]


def keccak256(data: bytes) -> bytes:
    M = (1 << 64) - 1
    rol = lambda v, n: ((v << n) | (v >> (64 - n))) & M if n else v  # noqa: E731
    A = [[0] * 5 for _ in range(5)]
    p = bytearray(data) + b"\x01"
    while len(p) % 136:
        p.append(0)
    p[-1] |= 0x80
    for off in range(0, len(p), 136):
        for i in range(17):
            A[i % 5][i // 5] ^= int.from_bytes(p[off + 8 * i: off + 8 * i + 8], "little")
        for rc in _RC:
            C = [A[x][0] ^ A[x][1] ^ A[x][2] ^ A[x][3] ^ A[x][4] for x in range(5)]
            D = [C[(x - 1) % 5] ^ rol(C[(x + 1) % 5], 1) for x in range(5)]
            A = [[A[x][y] ^ D[x] for y in range(5)] for x in range(5)]
            B = [[0] * 5 for _ in range(5)]
            for x in range(5):
                for y in range(5):
                    B[y][(2 * x + 3 * y) % 5] = rol(A[x][y], _ROT[x][y])
            A = [[B[x][y] ^ ((~B[(x + 1) % 5][y]) & B[(x + 2) % 5][y]) for y in range(5)] for x in range(5)]
            A[0][0] ^= rc
    return b"".join(A[i % 5][i // 5].to_bytes(8, "little") for i in range(4))



class _TooBig(Exception):
    pass


SR_RPC = {
    "ethereum": ["https://ethereum-rpc.publicnode.com", "https://eth.drpc.org", "https://eth.llamarpc.com", "https://cloudflare-eth.com"],
    "base": ["https://base-rpc.publicnode.com", "https://base.gateway.tenderly.co", "https://base.api.pocket.network", "https://mainnet.base.org"],
    "arbitrum": ["https://arbitrum-one-rpc.publicnode.com", "https://arb1.arbitrum.io/rpc", "https://arbitrum.drpc.org"],
    "bnb": ["https://bsc-rpc.publicnode.com", "https://bsc.drpc.org", "https://bsc-dataseed.bnbchain.org"],
}
SR_FAILS = {}
COW_TOKEN = "0xdef1ca1fb7fbcdc777520aa7f396b4e015f497ab"
COW_SAFE = "0xa03be496e67ec29bc62f01a428683d7f9c204930"
SPOKE = {"base": "0x09aea4b2242abc8bb4bb78d537a67a245a7bec64", "arbitrum": "0xe35e9842fceaca96570b734083f4a58e8f7c5f2a"}
T_TRANSFER = "0x" + keccak256(b"Transfer(address,address,uint256)").hex()
T_FILLED = "0x" + keccak256(b"FilledRelay(bytes32,bytes32,uint256,uint256,uint256,uint256,uint256,uint32,uint32,bytes32,bytes32,bytes32,"
                            b"bytes32,bytes32,(bytes32,bytes32,uint256,uint8))").hex()
T_FILLEDV3 = "0x" + keccak256(b"FilledV3Relay(address,address,uint256,uint256,uint256,uint256,uint32,uint32,uint32,address,address,address,"
                              b"address,bytes,(address,bytes,uint256,uint8))").hex()


def _srpc(chain, method, params, tries=2):
    """JSON-RPC over the chain's public endpoints. eth_getLogs errors on every endpoint raise _TooBig (caller shrinks the window)."""
    last, getlogs_err = None, 0
    urls = sorted(SR_RPC[chain], key=lambda u: SR_FAILS.get(u, 0))
    for k in range(tries):
        for u in urls:
            try:
                req = urllib.request.Request(u, data=json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode(),
                                             headers={**UA, "Content-Type": "application/json"}, method="POST")
                with urllib.request.urlopen(req, timeout=60) as r:
                    j = json.loads(r.read().decode())
                if "error" in j:
                    last = f"{u}: {str(j['error'])[:160]}"
                    SR_FAILS[u] = SR_FAILS.get(u, 0) + 1
                    getlogs_err += method == "eth_getLogs"
                    continue
                SR_FAILS[u] = max(0, SR_FAILS.get(u, 0) - 1)
                return j["result"]
            except Exception as e:  # noqa: BLE001
                last = f"{u}: {type(e).__name__}: {str(e)[:160]}"
                SR_FAILS[u] = SR_FAILS.get(u, 0) + 1
                getlogs_err += method == "eth_getLogs"
                if "429" in str(e):
                    time.sleep(5)
        time.sleep(2 * (k + 1))
    if method == "eth_getLogs" and getlogs_err:
        raise _TooBig(last)
    raise RuntimeError(last)


def _sblock_ts(chain, n):
    return int(_srpc(chain, "eth_getBlockByNumber", [hex(n), False])["timestamp"], 16)


def _sblock_at(chain, ts):
    """First block with timestamp >= ts (binary search)."""
    hi = int(_srpc(chain, "eth_blockNumber", []), 16)
    lo = 1
    if _sblock_ts(chain, hi) < ts:
        return hi
    while lo < hi:
        mid = (lo + hi) // 2
        if _sblock_ts(chain, mid) < ts:
            lo = mid + 1
        else:
            hi = mid
    return lo


def _sscan(chain, address, topics, b0, b1, w=5000, wmax=500000, budget_s=9000):
    """All logs in [b0, b1]; adaptive window. Returns (logs, blocks_missed)."""
    out, b, missed, calls, t0 = [], b0, 0, 0, time.time()
    while b <= b1:
        if time.time() - t0 > budget_s:
            missed += b1 - b + 1
            print(f"  {chain}: time budget hit at block {b}", flush=True)
            break
        e = min(b1, b + w - 1)
        try:
            logs = _srpc(chain, "eth_getLogs", [{"fromBlock": hex(b), "toBlock": hex(e), "address": address, "topics": topics}])
            out += logs
            calls += 1
            b = e + 1
            if len(logs) < 3000:
                w = min(wmax, int(w * 1.5))
        except (_TooBig, RuntimeError) as ex:
            if w <= 100:
                missed += e - b + 1
                print(f"  {chain}: gave up on {b}-{e}: {str(ex)[:120]}", flush=True)
                b = e + 1
                w = 1000
            else:
                w = max(100, w // 4)
    print(f"  {chain} {address[:10]}: {len(out)} logs, {calls} calls, missed {missed} of {b1 - b0 + 1} blocks, {time.time() - t0:.0f}s",
          flush=True)
    return out, missed


def _page_snips(url, needles, width=300):
    """Fetch a page (HTML) and return text snippets around each needle (case-insensitive)."""
    import html as _html
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) long-convexity-research"})
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read().decode("utf-8", "replace")
    except Exception as e:  # noqa: BLE001
        return {"error": f"{type(e).__name__}: {str(e)[:160]}"}
    txt = _re.sub(r"\s+", " ", _html.unescape(_re.sub(r"<[^>]+>", " ", raw)))
    out = {"chars": len(txt)}
    for nd in needles:
        hits = [m.start() for m in _re.finditer(_re.escape(nd), txt, flags=_re.I)][:4]
        out[nd] = [txt[max(0, h - width): h + width] for h in hits]
        out[nd + "|in_raw_html"] = nd.lower() in raw.lower()
    return out


def job_cow361():
    """#361: COW transfers out of the CoW Solver Payouts Safe, 2024-01-01..now, plus official-page checks."""
    OUT.mkdir(parents=True, exist_ok=True)
    meta = {"pages": {}}
    for url, needles in [
        ("https://docs.cow.fi/governance/multisigs", ["0xA03be496e67Ec29bC62F01a428683D7F9c204930", "Solver Payouts", "0xDEf1CA1fb7FBcDC777520aa7f396b4E015F497aB"]),
        ("https://docs.cow.fi/cow-protocol/tutorials/solvers/onboard", ["KYC", "bonding pool", "service fee", "jurisdiction", "countr", "sanction", "bond"]),
        ("https://docs.cow.fi/cow-protocol/reference/core/auctions/rewards", ["COW", "cap", "weekly", "penalt", "Tuesday"]),
        ("https://docs.cow.fi/governance/token", ["0xDEf1CA1fb7FBcDC777520aa7f396b4E015F497aB"]),
    ]:
        meta["pages"][url] = _page_snips(url, needles)
        print(f"  page {url}: " + ", ".join(f"{k[:-12]}={v}" for k, v in meta["pages"][url].items() if k.endswith("|in_raw_html")), flush=True)
    code = _srpc("ethereum", "eth_getCode", [COW_SAFE, "latest"])
    meta["safe_has_code"] = bool(code and code != "0x")
    b0 = _sblock_at("ethereum", int(pd.Timestamp("2024-01-01", tz="UTC").timestamp()))
    b1 = int(_srpc("ethereum", "eth_blockNumber", []), 16)
    pad = "0x" + "0" * 24 + COW_SAFE[2:]
    logs, missed = _sscan("ethereum", COW_TOKEN, [T_TRANSFER, pad], b0, b1, w=50000, wmax=2000000)
    blocks = sorted({int(lg["blockNumber"], 16) for lg in logs})
    ts = {}
    for n in blocks:
        try:
            ts[n] = _sblock_ts("ethereum", n)
        except Exception:  # noqa: BLE001
            ts[n] = None
    rows = [{"block": int(lg["blockNumber"], 16), "ts": ts.get(int(lg["blockNumber"], 16)), "to": "0x" + lg["topics"][2][-40:],
             "cow": int(lg["data"], 16) / 1e18, "tx": lg["transactionHash"]} for lg in logs]
    meta.update(b0=b0, b1=b1, missed_blocks=missed, n_transfers=len(rows), n_blocks=len(blocks))
    meta["cow_price"] = _llama_chart("coingecko:cow-protocol", "2023-12-25")
    print(f"  COW transfers out of the payouts Safe: {len(rows)} in {len(blocks)} blocks; recipients {len({r['to'] for r in rows})}; "
          f"COW prices {len(meta['cow_price'])}; safe has code {meta['safe_has_code']}", flush=True)
    pd.DataFrame(rows).to_parquet(OUT / "solverrelay_cow.parquet", index=False)
    (OUT / "solverrelay_cow_meta.json").write_text(json.dumps(meta))


def _w(data, i):
    return int(data[2 + 64 * i: 2 + 64 * (i + 1)], 16)


def job_across362():
    """#362: Across fills on the Base and Arbitrum SpokePools, 2026-10-01..2026-10-31 (Stage 1 slice)."""
    OUT.mkdir(parents=True, exist_ok=True)
    meta = {"pages": {}, "topic0": {"FilledRelay": T_FILLED, "FilledV3Relay": T_FILLEDV3}}
    for url in ["https://docs.across.to/reference/contract-addresses", "https://docs.across.to/developer-quickstart/contract-addresses",
                "https://docs.across.to/introduction/contract-addresses"]:
        meta["pages"][url] = _page_snips(url, list(SPOKE.values()))
        print(f"  page {url}: " + ", ".join(f"{k[:12]}={v}" for k, v in meta["pages"][url].items() if k.endswith("|in_raw_html")), flush=True)
    t0, t1 = (int(pd.Timestamp(d, tz="UTC").timestamp()) for d in ("2026-10-01", "2026-11-01"))
    for chain, spoke in SPOKE.items():
        try:
            m = meta[chain] = {}
            code = _srpc(chain, "eth_getCode", [spoke, "latest"])
            m["has_code"] = bool(code and code != "0x")
            b0, b1 = _sblock_at(chain, t0), _sblock_at(chain, t1) - 1
            m.update(b0=b0, b1=b1)
            # probe: every topic0 the SpokePool emits in a short window near the end (checks the computed hashes)
            try:
                probe = _srpc(chain, "eth_getLogs", [{"fromBlock": hex(b1 - 3000), "toBlock": hex(b1), "address": spoke}])
                cnt = {}
                for lg in probe:
                    cnt[lg["topics"][0]] = cnt.get(lg["topics"][0], 0) + 1
                m["probe_topic0"] = cnt
                print(f"  {chain} probe topic0 counts: {cnt}", flush=True)
            except Exception as e:  # noqa: BLE001
                m["probe_error"] = str(e)[:200]
            logs, missed = _sscan(chain, spoke, [[T_FILLED, T_FILLEDV3]], b0, b1, w=2000, wmax=200000)
            m["missed_blocks"] = missed
            samp = sorted({b0 + (b1 - b0) * k // 63 for k in range(64)})
            m["ts_sample"] = [[n, _sblock_ts(chain, n)] for n in samp]
            rows, toks = [], {}
            for lg in logs:
                d, t = lg["data"], lg["topics"]
                v3 = t[0] == T_FILLEDV3
                if v3:
                    soff = _w(d, 11) // 32
                    ftype, upd = _w(d, soff + 3), _w(d, soff + 2)
                else:
                    ftype, upd = _w(d, 14), _w(d, 13)
                out_amt = _w(d, 3)
                rows.append({"block": int(lg["blockNumber"], 16), "v3": v3, "origin": int(t[1], 16), "relayer": "0x" + t[3][-40:],
                             "in_tok": "0x" + d[2 + 24: 2 + 64], "out_tok": "0x" + d[2 + 64 + 24: 2 + 128],
                             "in_amt": float(_w(d, 2)), "out_amt": float(upd if upd else out_amt), "spread_raw": float(_w(d, 2) - (upd if upd else out_amt)),
                             "repay": _w(d, 4), "ftype": ftype, "excl": ("0x" + d[2 + 64 * 7 + 24: 2 + 64 * 8]) == ("0x" + t[3][-40:])})
            for a in {r["out_tok"] for r in rows}:
                try:
                    dec = int(_srpc(chain, "eth_call", [{"to": a, "data": "0x313ce567"}, "latest"]), 16)
                    sraw = _srpc(chain, "eth_call", [{"to": a, "data": "0x95d89b41"}, "latest"])
                    sb = bytes.fromhex(sraw[2:])
                    sym = sb[64: 64 + int.from_bytes(sb[32:64], "big")].decode("utf-8", "replace") if len(sb) >= 96 else sb.rstrip(b"\0").decode("utf-8", "replace")
                    toks[a] = [sym, dec]
                except Exception as e:  # noqa: BLE001
                    toks[a] = ["?", None, str(e)[:80]]
            m["tokens"] = toks
            pd.DataFrame(rows).to_parquet(OUT / f"solverrelay_fills_{chain}.parquet", index=False)
            print(f"  {chain}: fills {len(rows)}, relayers {len({r['relayer'] for r in rows})}, tokens {len(toks)}", flush=True)
        except Exception as e:  # noqa: BLE001
            meta.setdefault(chain, {})["error"] = f"{type(e).__name__}: {str(e)[:200]}"
            print(f"  {chain} FAILED: {e}", flush=True)
    meta["eth_price"] = _llama_chart("coingecko:ethereum", "2026-09-25")
    meta["btc_price"] = _llama_chart("coingecko:bitcoin", "2026-09-25")
    (OUT / "solverrelay_across_meta.json").write_text(json.dumps(meta))



def job_jlp363():
    """#363: JLP / SOL / ETH / BTC daily prices from DefiLlama (same start) + Jupiter terms page check."""
    OUT.mkdir(parents=True, exist_ok=True)
    meta = {"pages": {}}
    for url in ("https://jup.ag/terms-of-use", "https://jup.ag/terms", "https://dev.jup.ag/docs/perp-api",
                "https://station.jup.ag/guides/perpetual-exchange/overview"):
        meta["pages"][url] = _page_snips(url, ["Malaysia", "restricted", "prohibited", "jurisdiction", "United States"], width=200)
        print(f"  page {url}: {meta['pages'][url].get('error') or meta['pages'][url].get('chars')}", flush=True)
    keys = ["coingecko:jupiter-perpetuals-liquidity-provider-token", "solana:27G8MtK7VtTcCHkpASjSDdkWWYfoqT6ggEuKidVJidD4",
            "coingecko:solana", "coingecko:ethereum", "coingecko:bitcoin"]
    rows = []
    for k in keys:
        pts = _llama_chart(k, start="2023-10-01")
        print(f"  {k}: {len(pts)} points", flush=True)
        rows += [{"key": k, "t": int(p_["timestamp"]), "price": float(p_["price"])} for p_ in pts]
    pd.DataFrame(rows).to_parquet(OUT / "jlp363_prices.parquet", index=False)
    (OUT / "jlp363_meta.json").write_text(json.dumps(meta))


def job_cow361b():
    """#361 addendum: the same COW transfers out of the Solver Payouts Safe, from Blockscout's free API (RPC scan covered 1.5%)."""
    import urllib.parse
    OUT.mkdir(parents=True, exist_ok=True)
    mp = OUT / "solverrelay_cow_meta.json"
    meta = json.loads(mp.read_text()) if mp.exists() else {"pages": {}}
    t0 = int(pd.Timestamp("2024-01-01", tz="UTC").timestamp())
    rows, complete, source = [], False, None
    # 1) Blockscout v2 (newest first, cursor pagination)
    base = (f"https://eth.blockscout.com/api/v2/addresses/{COW_SAFE}/token-transfers?type=ERC-20&filter=from&token={COW_TOKEN}")
    url, pages = base, 0
    while url and pages < 2000:
        d = get(url, tries=5)
        pages += 1
        if d is None or "items" not in d:
            print(f"  blockscout v2 stopped at page {pages}: {str(d)[:200]}", flush=True)
            break
        stop = False
        for it in d["items"]:
            ts = int(pd.Timestamp(it.get("timestamp")).timestamp()) if it.get("timestamp") else None
            if ts is not None and ts < t0:
                stop = True
                continue
            tot = it.get("total") or {}
            dec = int(tot.get("decimals") or 18)
            rows.append({"block": int(it.get("block_number") or it.get("block") or 0), "ts": ts,
                         "to": str((it.get("to") or {}).get("hash", "")).lower(), "frm": str((it.get("from") or {}).get("hash", "")).lower(),
                         "cow": int(tot.get("value") or 0) / 10 ** dec, "tx": it.get("transaction_hash") or it.get("tx_hash")})
        nxt = d.get("next_page_params")
        if stop or not nxt:
            complete, source = True, "blockscout_v2"
            break
        url = base + "&" + urllib.parse.urlencode(nxt)
        time.sleep(0.25)
    print(f"  blockscout v2: pages {pages}, rows {len(rows)}, complete {complete}", flush=True)
    # 2) Blockscout Etherscan-style API (oldest first) if v2 did not finish
    if not complete:
        rows, page = [], 1
        while page < 200:
            d = get(f"https://eth.blockscout.com/api?module=account&action=tokentx&address={COW_SAFE}&contractaddress={COW_TOKEN}"
                    f"&sort=asc&page={page}&offset=1000", tries=5)
            res = (d or {}).get("result")
            if not isinstance(res, list):
                print(f"  blockscout v1 stopped at page {page}: {str(d)[:200]}", flush=True)
                break
            for it in res:
                ts = int(it["timeStamp"])
                if ts < t0:
                    continue
                rows.append({"block": int(it["blockNumber"]), "ts": ts, "to": it["to"].lower(), "frm": it["from"].lower(),
                             "cow": int(it["value"]) / 10 ** int(it.get("tokenDecimal") or 18), "tx": it["hash"]})
            if len(res) < 1000:
                complete, source = True, "blockscout_v1"
                break
            page += 1
            time.sleep(0.25)
        print(f"  blockscout v1: pages {page}, rows {len(rows)}, complete {complete}", flush=True)
    df = pd.DataFrame(rows)
    if len(df):
        df = df[df["frm"] == COW_SAFE.lower()].drop_duplicates(["tx", "to", "cow"]).sort_values("block")
    meta.update(source=source, complete=complete, n_transfers=int(len(df)), n_blocks=int(df["block"].nunique()) if len(df) else 0,
                missed_blocks=0 if complete else None, b0=int(df["block"].min()) if len(df) else None,
                b1=int(df["block"].max()) if len(df) else None)
    if not meta.get("cow_price"):
        meta["cow_price"] = _llama_chart("coingecko:cow-protocol", "2023-12-25")
    print(f"  COW transfers out of the payouts Safe since 2024-01-01: {len(df)}; recipients {df['to'].nunique() if len(df) else 0}; "
          f"source {source}; complete {complete}", flush=True)
    df.drop(columns=["frm"], errors="ignore").to_parquet(OUT / "solverrelay_cow.parquet", index=False)
    mp.write_text(json.dumps(meta))


def _qget(url, timeout=30):
    """Quiet GET: (status, json-or-None)."""
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, None
    except Exception:  # noqa: BLE001
        return -1, None


COW_NETS = {"mainnet": 7200, "xdai": 17280, "arbitrum_one": 345600, "base": 43200, "polygon": 43200, "avalanche": 43200,
            "bnb": 115200, "linea": 28800, "lens": 86400, "plasma": 86400, "ink": 86400}


def job_cow365():
    """#365: CoW solver-competition sample (~30 days per network) + COW repaid INTO the Solver Payouts Safe."""
    import random
    import urllib.parse
    OUT.mkdir(parents=True, exist_ok=True)
    meta, rows = {"nets": {}}, []
    for net, bpd in COW_NETS.items():
        api = f"https://api.cow.fi/{net}/api"
        st, lat, ver = None, None, None
        for v in ("v2", "v1"):
            st, lat = _qget(f"{api}/{v}/solver_competition/latest")
            if lat and lat.get("auctionId"):
                ver = v
                break
        if not ver:
            meta["nets"][net] = {"status": st}
            print(f"  {net}: no competition data (status {st})", flush=True)
            continue
        L, BL = int(lat["auctionId"]), int(lat.get("auctionStartBlock") or 0)
        ipb = None
        for back in (5000, 2000, 500):
            for k in range(15):
                s2, d2 = _qget(f"{api}/{ver}/solver_competition/{L - back - k}")
                if d2 and d2.get("auctionStartBlock") and BL:
                    ipb = (back + k) / max(1, BL - int(d2["auctionStartBlock"]))
                    break
            if ipb:
                break
        span = int((ipb or 1.0) * bpd * 30)
        rnd = random.Random(365)
        ids = sorted({L - int(rnd.random() * span) for _ in range(700)})
        got, t0 = 0, time.time()
        for aid in ids:
            if time.time() - t0 > 1500:
                break
            s3, d3 = _qget(f"{api}/{ver}/solver_competition/{aid}")
            if not d3:
                continue
            got += 1
            for sol in d3.get("solutions") or []:
                rows.append({"net": net, "auction": aid, "block": d3.get("auctionStartBlock"), "solver": sol.get("solver"),
                             "solver_addr": str(sol.get("solverAddress") or ""), "score": str(sol.get("score") or ""),
                             "ranking": sol.get("ranking"), "winner": sol.get("isWinner"), "filtered": sol.get("filteredOut")})
            time.sleep(0.1)
        meta["nets"][net] = {"version": ver, "latest": L, "latest_block": BL, "ids_per_block": ipb, "span_ids": span, "sampled": len(ids),
                             "with_data": got, "keys_latest": sorted(lat.keys()),
                             "solution_keys": sorted((lat.get("solutions") or [{}])[0].keys())}
        print(f"  {net}: {ver} latest {L}; ids/block {ipb}; span {span}; sampled {len(ids)}, with data {got}", flush=True)
    pd.DataFrame(rows).to_parquet(OUT / "cow365_competition.parquet", index=False)
    # COW transfers INTO the Safe since 2024-01-01 (repayments / returns)
    t0s = int(pd.Timestamp("2024-01-01", tz="UTC").timestamp())
    base = f"https://eth.blockscout.com/api/v2/addresses/{COW_SAFE}/token-transfers?type=ERC-20&filter=to&token={COW_TOKEN}"
    url, inflow, pages, done = base, [], 0, False
    while url and pages < 1000:
        d = get(url, tries=5)
        pages += 1
        if d is None or "items" not in d:
            break
        stop = False
        for it in d["items"]:
            ts = int(pd.Timestamp(it.get("timestamp")).timestamp()) if it.get("timestamp") else None
            if ts is not None and ts < t0s:
                stop = True
                continue
            tot = it.get("total") or {}
            inflow.append({"ts": ts, "frm": str((it.get("from") or {}).get("hash", "")).lower(),
                           "cow": int(tot.get("value") or 0) / 10 ** int(tot.get("decimals") or 18), "tx": it.get("transaction_hash")})
        nxt = d.get("next_page_params")
        if stop or not nxt:
            done = True
            break
        url = base + "&" + urllib.parse.urlencode(nxt)
        time.sleep(0.25)
    meta["inflow"] = {"pages": pages, "rows": len(inflow), "complete": done}
    print(f"  inflows to the Safe: {len(inflow)} rows, complete {done}", flush=True)
    pd.DataFrame(inflow).to_parquet(OUT / "cow365_inflows.parquet", index=False)
    (OUT / "cow365_meta.json").write_text(json.dumps(meta))


def job_radarprobe():
    """Radar N-source repair: probe candidate URLs (status, bytes, text length, first text)."""
    import html as _h
    cands = ["https://www.luno.com/en/my", "https://www.luno.com/en/my/", "https://www.luno.com/my", "https://www.luno.com/en/promotions",
             "https://www.luno.com/en/blog", "https://tokenize.exchange/", "https://www.tokenize.exchange/", "https://blog.tokenize.exchange/",
             "https://docs.gelato.network/", "https://docs.gelato.cloud/", "https://www.gelato.network/", "https://codehawks.cyfrin.io/",
             "https://codehawks.cyfrin.io/c", "https://www.codehawks.com/", "https://audits.sherlock.xyz/api/contests",
             "https://mainnet-contest.sherlock.xyz/contests", "https://mainnet-contest.sherlock.xyz/contests?page=1",
             "https://cantina.xyz/api/v0/competitions", "https://cantina.xyz/competitions?status=live",
             "https://api.coingecko.com/api/v3/derivatives/exchanges?per_page=100", "https://api.llama.fi/overview/dexs?excludeTotalDataChart=true",
             "https://api.llama.fi/summary/derivatives/hyperliquid", "https://api.llama.fi/overview/derivatives",
             "https://api.llama.fi/protocols", "https://code4rena.com/api/v0/audits", "https://code4rena.com/audits?status=active"]
    out = []
    for u in cands:
        try:
            req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0 (compatible; long-convexity-research/1.0)", "Accept": "*/*"})
            with urllib.request.urlopen(req, timeout=40) as r:
                raw = r.read(5_000_000).decode("utf-8", "replace")
                st = r.status
        except urllib.error.HTTPError as e:
            raw, st = "", e.code
        except Exception as e:  # noqa: BLE001
            raw, st = "", f"{type(e).__name__}"
        txt = _re.sub(r"\s+", " ", _h.unescape(_re.sub(r"<[^>]+>", " ", _re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", raw))))
        out.append({"url": u, "status": st, "bytes": len(raw), "text": len(txt), "head": txt[:240]})
        print(f"  {st} {len(raw):>8} bytes {len(txt):>7} text  {u}  | {txt[:160]}", flush=True)
        time.sleep(0.5)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "radarprobe.json").write_text(json.dumps(out))


def job_cowauction():
    """#366 repair attempt: is any CoW live-auction endpoint public? (status + size only)"""
    out = []
    for host in ("https://api.cow.fi", "https://barn.api.cow.fi"):
        for net in ("mainnet", "xdai", "arbitrum_one", "base", "bnb", "polygon", "avalanche", "linea", "plasma", "ink", "sepolia"):
            u = f"{host}/{net}/api/v1/auction"
            st, d = _qget(u, timeout=40)
            n = len((d or {}).get("orders") or []) if isinstance(d, dict) else 0
            out.append({"url": u, "status": st, "orders": n, "keys": sorted(d.keys())[:12] if isinstance(d, dict) else None})
            print(f"  {st} orders {n:>5}  {u}", flush=True)
            time.sleep(0.3)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "radarprobe_cowauction.json").write_text(json.dumps(out))


def job_cow367():
    """#367: VouchRegister logs (solver -> bonding pool -> reward address), pool balances, solver names, Solvers page, forum."""
    import urllib.parse
    OUT.mkdir(parents=True, exist_ok=True)
    meta, rows = {}, []
    hosts = {"ethereum": ("eth.blockscout.com", "0xb422f2520b0b7FD86f7DA61b32Cc631A59ed7E8F"),
             "gnosis": ("gnosis.blockscout.com", "0xAAA4De096D02AE21729aA31D967E148D4e3Ae501"),
             "arbitrum": ("arbitrum.blockscout.com", "0xAAA4De096D02AE21729aA31D967E148D4e3Ae501"),
             "base": ("base.blockscout.com", "0xAAA4De096D02AE21729aA31D967E148D4e3Ae501"),
             "polygon": ("polygon.blockscout.com", "0xAAA4De096D02AE21729aA31D967E148D4e3Ae501")}
    for chain, (host, addr) in hosts.items():
        base = f"https://{host}/api/v2/addresses/{addr}/logs"
        url, n, pages = base, 0, 0
        while url and pages < 200:
            st, d = _qget(url, timeout=60)
            pages += 1
            if not d or "items" not in d:
                print(f"  {chain}: logs stopped (status {st}) at page {pages}", flush=True)
                break
            for it in d["items"]:
                dec = it.get("decoded") or {}
                rows.append({"chain": chain, "block": it.get("block_number"), "tx": it.get("transaction_hash") or it.get("tx_hash"),
                             "topics": json.dumps(it.get("topics")), "data": it.get("data"), "method": dec.get("method_call"),
                             "params": json.dumps(dec.get("parameters"))})
                n += 1
            nxt = d.get("next_page_params")
            if not nxt:
                break
            url = base + "?" + urllib.parse.urlencode(nxt)
            time.sleep(0.25)
        meta[f"logs_{chain}"] = n
        print(f"  {chain}: {n} VouchRegister logs", flush=True)
    try:
        b0 = _sblock_at("bnb", int(pd.Timestamp("2025-01-01", tz="UTC").timestamp()))
        b1 = int(_srpc("bnb", "eth_blockNumber", []), 16)
        logs, missed = _sscan("bnb", "0xAAA4De096D02AE21729aA31D967E148D4e3Ae501", [], b0, b1, w=5000, wmax=500000, budget_s=2700)
        for lg in logs:
            rows.append({"chain": "bnb", "block": int(lg["blockNumber"], 16), "tx": lg["transactionHash"], "topics": json.dumps(lg["topics"]),
                         "data": lg["data"], "method": None, "params": None})
        meta.update(logs_bnb=len(logs), bnb_missed=missed, bnb_range=[b0, b1])
    except Exception as e:  # noqa: BLE001
        meta["bnb_error"] = f"{type(e).__name__}: {str(e)[:200]}"
        print(f"  bnb failed: {meta['bnb_error']}", flush=True)
    vdf = pd.DataFrame(rows)
    vdf.to_parquet(OUT / "cow367_vouch.parquet", index=False)
    # bonding pools: any address in decoded params named like *pool*, plus topic-2 addresses (checked in analysis)
    pools = set()
    for r in rows:
        for prm in json.loads(r["params"] or "null") or []:
            if "pool" in str(prm.get("name", "")).lower():
                pools.add(str(prm.get("value")).lower())
        try:
            t = json.loads(r["topics"])
            if t and len(t) > 2 and t[2]:
                pools.add("0x" + t[2][-40:].lower())
        except Exception:  # noqa: BLE001
            pass
    pinfo = {}
    for pool in sorted(pools)[:150]:
        st, a = _qget(f"https://eth.blockscout.com/api/v2/addresses/{pool}", timeout=40)
        st2, tb = _qget(f"https://eth.blockscout.com/api/v2/addresses/{pool}/token-balances", timeout=40)
        pinfo[pool] = {"eth_wei": (a or {}).get("coin_balance"), "is_contract": (a or {}).get("is_contract"), "name": (a or {}).get("name"),
                       "tokens": [{"sym": ((x.get("token") or {}).get("symbol")), "value": x.get("value"),
                                   "dec": ((x.get("token") or {}).get("decimals")), "rate": ((x.get("token") or {}).get("exchange_rate"))}
                                  for x in (tb or []) if isinstance(x, dict)][:30]}
        time.sleep(0.2)
    (OUT / "cow367_pools.json").write_text(json.dumps(pinfo))
    print(f"  candidate pool addresses {len(pools)}; checked {len(pinfo)}", flush=True)
    # solver names from the v1 solver-competition API
    nrows = []
    for net in ("mainnet", "xdai", "arbitrum_one", "base", "bnb", "polygon", "avalanche", "linea", "plasma", "ink"):
        st, lat = _qget(f"https://api.cow.fi/{net}/api/v1/solver_competition/latest")
        meta[f"v1_{net}"] = st
        if not lat or not lat.get("auctionId"):
            continue
        L = int(lat["auctionId"])
        for k in range(0, 2400, 30):
            st, d = (st, lat) if k == 0 else _qget(f"https://api.cow.fi/{net}/api/v1/solver_competition/{L - k}")
            for sol in (d or {}).get("solutions") or []:
                nrows.append({"net": net, "solver": sol.get("solver"), "solver_addr": str(sol.get("solverAddress") or "").lower()})
            time.sleep(0.1)
    pd.DataFrame(nrows).drop_duplicates().to_parquet(OUT / "cow367_names.parquet", index=False)
    print(f"  solver name rows {len(nrows)}", flush=True)
    # Solvers page and CMS guesses, forum search
    pages = {}
    for u in ("https://cow.fi/solvers", "https://cow.fi/cow-protocol", "https://cms.cow.fi/api/solvers?populate=*&pagination[pageSize]=200",
              "https://cms.cow.fi/api/solvers?pagination[pageSize]=200"):
        st, raw = None, ""
        try:
            req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0 (compatible; long-convexity-research/1.0)"})
            with urllib.request.urlopen(req, timeout=60) as r:
                raw, st = r.read(8_000_000).decode("utf-8", "replace"), r.status
        except urllib.error.HTTPError as e:
            st = e.code
        except Exception as e:  # noqa: BLE001
            st = type(e).__name__
        nd = _re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', raw, _re.S)
        pages[u] = {"status": st, "bytes": len(raw), "next_data": (nd.group(1)[:3_000_000] if nd else None),
                    "raw": raw[:2_000_000] if not nd else None}
        print(f"  page {st} {len(raw)} {u}", flush=True)
    (OUT / "cow367_pages.json").write_text(json.dumps(pages))
    forum = {}
    for q in ("bonding pool", "vouch", "solver introduction", "new solver", "reduced bonding pool", "solver onboarding", "CIP bonding"):
        st, d = _qget(f"https://forum.cow.fi/search.json?q={urllib.parse.quote(q)}", timeout=60)
        forum[q] = {"status": st, "topics": [{"id": t.get("id"), "title": t.get("title"), "slug": t.get("slug"), "created": t.get("created_at")}
                                             for t in (d or {}).get("topics") or []],
                    "posts": [{"topic_id": x.get("topic_id"), "user": x.get("username"), "blurb": x.get("blurb"), "created": x.get("created_at")}
                              for x in (d or {}).get("posts") or []]}
        time.sleep(1)
    (OUT / "cow367_forum.json").write_text(json.dumps(forum))
    (OUT / "cow367_meta.json").write_text(json.dumps(meta))
    print(f"  meta {meta}", flush=True)


def job_cryptotrend370():
    """#370: Binance USD-M perp daily klines + funding for every symbol ever listed (data.binance.vision), 2020-01..2026-10."""
    import concurrent.futures as _cf
    import io
    import zipfile
    import xml.etree.ElementTree as ET
    OUT.mkdir(parents=True, exist_ok=True)
    S3 = "https://s3-ap-northeast-1.amazonaws.com/data.binance.vision"
    ns = "{http://s3.amazonaws.com/doc/2006-03-01/}"

    def s3_list(prefix, delimiter=True):
        keys, prefs, marker = [], [], ""
        for _ in range(50):
            u = f"{S3}?prefix={prefix}" + ("&delimiter=/" if delimiter else "") + (f"&marker={marker}" if marker else "")
            try:
                with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=60) as r:
                    root = ET.fromstring(r.read())
            except Exception as e:  # noqa: BLE001
                print(f"  list fail {prefix}: {e}", flush=True)
                break
            keys += [c.find(ns + "Key").text for c in root.findall(ns + "Contents")]
            prefs += [c.find(ns + "Prefix").text for c in root.findall(ns + "CommonPrefixes")]
            trunc = (root.find(ns + "IsTruncated").text or "").lower() == "true"
            if not trunc:
                break
            marker = (keys[-1] if keys else prefs[-1])
        return keys, prefs

    _, prefs = s3_list("data/futures/um/monthly/klines/")
    syms = sorted({p.rstrip("/").split("/")[-1] for p in prefs})
    syms = [x for x in syms if x.endswith("USDT") and "_" not in x]
    print(f"  USDT perp symbols ever listed: {len(syms)}", flush=True)
    months = [f"{y}-{m:02d}" for y in range(2020, 2027) for m in range(1, 13) if f"{y}-{m:02d}" <= "2026-10"]

    def get_zip_csv(url):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                z = zipfile.ZipFile(io.BytesIO(r.read()))
                return z.read(z.namelist()[0]).decode()
        except urllib.error.HTTPError:
            return None
        except Exception:  # noqa: BLE001
            return None

    def one(sym):
        keys, _ = s3_list(f"data/futures/um/monthly/klines/{sym}/1d/", delimiter=False)
        have = {k.split("-1d-")[-1][:7] for k in keys if k.endswith(".zip")}
        krows, frows = [], []
        for mth in months:
            if mth not in have:
                continue
            t = get_zip_csv(f"https://data.binance.vision/data/futures/um/monthly/klines/{sym}/1d/{sym}-1d-{mth}.zip")
            for ln in (t or "").splitlines():
                f = ln.split(",")
                if not f or not f[0].strip().isdigit():
                    continue
                ts = int(f[0])
                ts = ts // 1000 if ts > 10**14 else ts
                krows.append((sym, ts // 1000, float(f[4]), float(f[7])))
            t = get_zip_csv(f"https://data.binance.vision/data/futures/um/monthly/fundingRate/{sym}/{sym}-fundingRate-{mth}.zip")
            for ln in (t or "").splitlines():
                f = ln.split(",")
                if not f or not f[0].strip().isdigit():
                    continue
                ts = int(f[0])
                ts = ts // 1000 if ts > 10**14 else ts
                frows.append((sym, ts // 1000, float(f[-1])))
        return krows, frows

    K, F, t0 = [], [], time.time()
    with _cf.ThreadPoolExecutor(16) as ex:
        for i, (kr, fr) in enumerate(ex.map(one, syms)):
            K += kr
            F += fr
            if i % 50 == 0:
                print(f"  {i}/{len(syms)} symbols, {len(K)} kline rows, {len(F)} funding rows, {time.time() - t0:.0f}s", flush=True)
    kd = pd.DataFrame(K, columns=["sym", "t", "close", "qvol"])
    fd = pd.DataFrame(F, columns=["sym", "t", "rate"])
    fd["date"] = pd.to_datetime(fd["t"], unit="s", utc=True).dt.normalize()
    fd = fd.groupby(["sym", "date"], as_index=False)["rate"].sum()
    kd.to_parquet(OUT / "cryptotrend370_klines.parquet", index=False)
    fd.to_parquet(OUT / "cryptotrend370_funding.parquet", index=False)
    (OUT / "cryptotrend370_meta.json").write_text(json.dumps({"symbols": len(syms), "kline_rows": len(kd), "funding_rows": len(fd),
                                                               "kline_symbols": int(kd["sym"].nunique()) if len(kd) else 0}))
    print(f"  done: {len(kd)} kline rows ({kd['sym'].nunique() if len(kd) else 0} symbols), {len(fd)} funding day-rows", flush=True)


def job_uniswapx371():
    """#371: UniswapX Fill events on Arbitrum (V3 Dutch) and Base (Priority), 2025-11-01..2026-10-31."""
    OUT.mkdir(parents=True, exist_ok=True)
    topic = "0x" + keccak256(b"Fill(bytes32,address,address,uint256)").hex()
    reactors = {"arbitrum": "0xB274d5F4b833b61B340b654d600A864fB604a87c", "base": "0x000000001Ec5656dcdB24D90DFa42742738De729"}
    meta = {"topic0": topic}
    for chain, addr in reactors.items():
        try:
            code = _srpc(chain, "eth_getCode", [addr, "latest"])
            b0 = _sblock_at(chain, int(pd.Timestamp("2025-11-01", tz="UTC").timestamp()))
            b1 = _sblock_at(chain, int(pd.Timestamp("2026-11-01", tz="UTC").timestamp()))
            logs, missed = _sscan(chain, addr, [topic], b0, b1, w=20000, wmax=2000000, budget_s=6000)
            rows = [{"block": int(lg["blockNumber"], 16), "tx": lg["transactionHash"], "order": lg["topics"][1],
                     "filler": "0x" + lg["topics"][2][-40:], "swapper": "0x" + lg["topics"][3][-40:]} for lg in logs]
            ts = []
            for k in range(65):
                b = b0 + (b1 - b0) * k // 64
                try:
                    ts.append([b, _sblock_ts(chain, b)])
                except Exception:  # noqa: BLE001
                    pass
            pd.DataFrame(rows).to_parquet(OUT / f"uniswapx371_{chain}.parquet", index=False)
            meta[chain] = {"has_code": bool(code and code != "0x"), "b0": b0, "b1": b1, "missed": missed, "fills": len(rows),
                           "ts_sample": ts}
            print(f"  {chain}: {len(rows)} fills, missed {missed} blocks", flush=True)
        except Exception as e:  # noqa: BLE001
            meta[chain] = {"error": f"{type(e).__name__}: {str(e)[:200]}"}
            print(f"  {chain} failed: {meta[chain]['error']}", flush=True)
    (OUT / "uniswapx371_meta.json").write_text(json.dumps(meta))


def job_uniswapx371b():
    """#371 Stage 3: receipts of Arbitrum UniswapX fills (2026-08..10) -> swapper input transfers; token prices."""
    OUT.mkdir(parents=True, exist_ok=True)
    d = pd.read_parquet(OUT / "uniswapx371_arbitrum.parquet")
    meta = json.loads((OUT / "uniswapx371_meta.json").read_text())
    import numpy as _np
    ts = _np.array(meta["arbitrum"]["ts_sample"], dtype=float)
    d["t"] = _np.interp(d["block"].to_numpy(float), ts[:, 0], ts[:, 1])
    d = d[d["t"] >= pd.Timestamp("2026-08-01", tz="UTC").timestamp()].drop_duplicates("tx")
    print(f"  receipts to fetch: {len(d)}", flush=True)
    rows, t0 = [], time.time()
    for k, r in enumerate(d.itertuples()):
        if time.time() - t0 > 7000:
            print(f"  time budget hit at {k}", flush=True)
            break
        try:
            rc = _srpc("arbitrum", "eth_getTransactionReceipt", [r.tx])
        except Exception:  # noqa: BLE001
            continue
        sw = "0x" + "0" * 24 + r.swapper[2:].lower()
        for lg in (rc or {}).get("logs") or []:
            tp = lg.get("topics") or []
            if len(tp) == 3 and tp[0] == T_TRANSFER and tp[1].lower() == sw:
                rows.append({"tx": r.tx, "t": r.t, "token": lg["address"].lower(), "amount_raw": str(int(lg["data"], 16)),
                             "filler": r.filler})
        if k % 1000 == 0:
            print(f"  {k}/{len(d)} receipts, {len(rows)} input transfers, {time.time() - t0:.0f}s", flush=True)
    tr = pd.DataFrame(rows)
    toks = sorted(tr["token"].unique()) if len(tr) else []
    dec, sym = {}, {}
    for tkn in toks:
        try:
            dec[tkn] = int(_srpc("arbitrum", "eth_call", [{"to": tkn, "data": "0x313ce567"}, "latest"]), 16)
        except Exception:  # noqa: BLE001
            dec[tkn] = None
    prices = {}
    for tkn in toks:
        prices[tkn] = _llama_chart(f"arbitrum:{tkn}", start="2026-07-25")
    tr.to_parquet(OUT / "uniswapx371b_inputs.parquet", index=False)
    (OUT / "uniswapx371b_meta.json").write_text(json.dumps({"fills_considered": len(d), "decimals": dec, "prices": prices}))
    print(f"  done: {len(tr)} input transfers, {len(toks)} tokens", flush=True)

JOBS = {"uniswapx371b": job_uniswapx371b, "uniswapx371": job_uniswapx371, "cryptotrend370": job_cryptotrend370, "cow367": job_cow367, "cowauction": job_cowauction, "radarprobe": job_radarprobe, "cow365": job_cow365, "cow361b": job_cow361b, "jlp363": job_jlp363, "cow361": job_cow361, "across362": job_across362, "sweep4d": job_sweep4d, "sweep4c": job_sweep4c, "sweep4b": job_sweep4b, "sweep4": job_sweep4, "addprice": job_addprice, "fred9": job_fred9, "batch10b": job_batch10b, "repair8": job_repair8, "sweep3": job_sweep3, "merkl": job_merkl, "smallcap": job_smallcap, "batch10": job_batch10, "batch9": job_batch9, "vxn": job_vxn, "batch8s": job_batch8s, "batch8p": job_batch8p, "hype4h": job_hype4h, "batch7": job_batch7, "votium": job_votium, "batch6": job_batch6, "sp_data": job_sp_data, "sp_probe": job_sp_probe, "sky_funding": job_sky_funding, "staking_apr": job_staking_apr, "pendle_pilot": job_pendle_pilot, "wrappers": job_wrappers, "lendborrow_now": job_lendborrow_now, "batch5": job_batch5, "batch4": job_batch4, "hedged": job_hedged, "lendborrow_corr": job_lendborrow_corr, "pendle_probe": job_pendle_probe, "stable_hlp": job_stable_hlp, "probe": job_probe, "funding": job_funding, "lendborrow": job_lendborrow}

if __name__ == "__main__":
    import sys
    for j in (sys.argv[1:] or ["stable_hlp"]):
        print(f"=== {j}", flush=True)
        try:
            JOBS[j]()
        except Exception as e:  # noqa: BLE001
            import traceback
            print(f"JOB {j} FAILED: {type(e).__name__}: {e}", flush=True)
            traceback.print_exc()

"""Data for docs/PREREG_UNCHARTED_20261125.md (#383-#387). Runs on GitHub Actions through scripts/fetch_fallback.py:

    python scripts/fetch_fallback.py uprobe          # all five parts
    python scripts/fetch_fallback.py u383vaults u385hyperp   # or single parts

Writes data/public/uncharted_*.{json,parquet}. Every part catches its own errors so one blocked source does not stop the rest.
"""
from __future__ import annotations

import json
import re
import time
import traceback
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

OUT = Path(__file__).resolve().parent.parent / "data" / "public"
UA = {"User-Agent": "Mozilla/5.0 (compatible; long-convexity-research/1.0)", "Accept": "application/json"}
T0_2021 = int(pd.Timestamp("2021-01-01", tz="UTC").timestamp())
T0_2024 = int(pd.Timestamp("2024-01-01", tz="UTC").timestamp())


def req(url, body=None, timeout=60, headers=None):
    """(status, parsed JSON or text or None)."""
    try:
        data = json.dumps(body).encode() if body is not None else None
        h = {**UA, **(headers or {}), **({"Content-Type": "application/json"} if data else {})}
        with urllib.request.urlopen(urllib.request.Request(url, data=data, headers=h), timeout=timeout) as r:
            raw = r.read().decode("utf-8", "replace")
            try:
                return r.status, json.loads(raw)
            except ValueError:
                return r.status, raw
    except urllib.error.HTTPError as e:
        return e.code, None
    except Exception as e:  # noqa: BLE001
        return type(e).__name__, None


def get(url, body=None, tries=3, timeout=60, pause=2.0, headers=None):
    st = None
    for k in range(tries):
        st, d = req(url, body, timeout, headers)
        if st == 200 and d is not None:
            return d
        if st in (400, 401, 403, 404, 451):
            break
        time.sleep((30 if st == 429 else pause) * (k + 1))
    print(f"  FAIL {st} {url[:120]}", flush=True)
    return None


def save(name, obj):
    OUT.mkdir(parents=True, exist_ok=True)
    p = OUT / name
    if isinstance(obj, pd.DataFrame):
        obj.to_parquet(p, index=False)
        print(f"  wrote {name}: {len(obj)} rows", flush=True)
    else:
        p.write_text(json.dumps(obj))
        print(f"  wrote {name}: {p.stat().st_size} bytes", flush=True)


def llama_chart(key, start, end=None, span=300):
    """Daily DefiLlama prices in <= 300-day chunks."""
    out, t, end = [], int(start), int(end or time.time())
    while t < end:
        d = get(f"https://coins.llama.fi/chart/{key}?start={t}&span={span}&period=1d", tries=2)
        out += (((d or {}).get("coins") or {}).get(key) or {}).get("prices") or []
        t += span * 86400
        time.sleep(0.3)
    return out


_CG_LIST = None


def cg_list():
    global _CG_LIST
    if _CG_LIST is None:
        _CG_LIST = get("https://api.coingecko.com/api/v3/coins/list", tries=4, pause=20) or []
        print(f"  coingecko list: {len(_CG_LIST)} coins", flush=True)
    return _CG_LIST


def cg_markets(ids):
    """{id: (market_cap, volume)} via /coins/markets in chunks of 200."""
    out, ids = {}, sorted(set(ids))
    for i in range(0, len(ids), 200):
        d = get("https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&per_page=250&ids=" + ",".join(ids[i:i + 200]),
                tries=4, pause=20) or []
        for x in d:
            out[x["id"]] = (x.get("market_cap") or 0, x.get("total_volume") or 0)
        time.sleep(8)
    return out


GT = "https://api.geckoterminal.com/api/v2"
GT_H = {"Accept": "application/json;version=20230302"}


def gt(path):
    d = get(GT + path, tries=3, pause=5, headers=GT_H)
    time.sleep(2.2)  # free tier: 30 calls / minute
    return d


# ---------------------------------------------------------------- #383 launch-phase vaults
VAULT_SYMS = {"jlp", "glp", "alp", "olp", "llp", "mlp", "vlp", "flp", "hlp", "gdai", "gusdc", "geth", "slp", "klp", "blp", "xlp", "dlp",
              "plp", "elp", "zlp", "avusdc", "usdlp", "hmx", "jusdc", "lvl", "qlp", "ulp", "glpusdc", "kliquid"}


def job_u383vaults():
    """Perp-DEX liquidity vaults: DefiLlama Derivatives-category pools + their APY/TVL charts; vault-token price histories."""
    protos = get("https://api.llama.fi/protocols", tries=3) or []
    deriv = {p.get("slug"): {"name": p.get("name"), "category": p.get("category"), "listedAt": p.get("listedAt"), "parent": p.get("parentProtocol")}
             for p in protos if p.get("category") in ("Derivatives", "Options Vault", "Synthetics")}
    print(f"  derivatives-type protocols: {len(deriv)}", flush=True)
    pools = (get("https://yields.llama.fi/pools", tries=3) or {}).get("data") or []
    sel = [p for p in pools if p.get("project") in deriv]
    print(f"  yield pools of those protocols: {len(sel)} (of {len(pools)})", flush=True)
    save("uncharted_383_pools.json", {"protocols": deriv, "pools": sel})
    rows = []
    for i, p in enumerate(sel):
        c = get(f"https://yields.llama.fi/chart/{p['pool']}", tries=2)
        for x in (c or {}).get("data") or []:
            rows.append({"pool": p["pool"], "ts": x.get("timestamp"), "tvlUsd": x.get("tvlUsd"), "apy": x.get("apy"),
                         "apyBase": x.get("apyBase"), "apyReward": x.get("apyReward")})
        if i % 50 == 0:
            print(f"    charts {i}/{len(sel)}", flush=True)
        time.sleep(0.25)
    ch = pd.DataFrame(rows)
    for c in ("tvlUsd", "apy", "apyBase", "apyReward"):
        ch[c] = pd.to_numeric(ch[c], errors="coerce")
    save("uncharted_383_charts.parquet", ch)
    # vault-token price histories (share price for stable vaults, NAV for multi-asset ones)
    lst = cg_list()
    ids = [c["id"] for c in lst if c.get("symbol", "").lower() in VAULT_SYMS
           or re.search(r"liquidity provider|\blp token\b|perp.*vault|vault.*perp", c.get("name", ""), re.I)]
    print(f"  vault-like coingecko ids: {len(ids)}", flush=True)
    meta = {c["id"]: {"symbol": c.get("symbol"), "name": c.get("name")} for c in lst if c["id"] in set(ids)}
    prow = []
    for g in ids:
        pts = llama_chart(f"coingecko:{g}", T0_2021)
        prow += [{"id": g, "t": int(x["timestamp"]), "price": float(x["price"])} for x in pts]
    for g in ("ethereum", "bitcoin", "solana", "binancecoin", "hyperliquid"):
        prow += [{"id": g, "t": int(x["timestamp"]), "price": float(x["price"])} for x in llama_chart(f"coingecko:{g}", T0_2021)]
    save("uncharted_383_prices.parquet", pd.DataFrame(prow))
    save("uncharted_383_ids.json", meta)
    hlp = get("https://api.hyperliquid.xyz/info", {"type": "vaultDetails", "vaultAddress": "0xdfc24b077bc1425ad1dea75bcb6f8158e10df303"})
    save("uncharted_383_hlp.json", hlp or {})


# ---------------------------------------------------------------- #384 withdrawal-queue discounts
LST = {"khype": "HYPE", "sthype": "HYPE", "behype": "HYPE", "ezeth": "ETH", "rseth": "ETH", "weeth": "ETH", "pufeth": "ETH", "susde": "USDE"}
UNDER_RE = {"HYPE": r"\bW?HYPE\b", "ETH": r"\bW?ETH\b", "USDE": r"\bUSDe\b|\bUSDC\b|\bUSDT\b"}


def job_u384lst():
    """kHYPE/stHYPE/beHYPE/ezETH/rsETH/weETH/pufETH/sUSDe: DEX pool OHLCV (GeckoTerminal) + DefiLlama daily prices."""
    if (OUT / "uncharted_384_llama.parquet").exists() and SKIP_DONE:
        print("  DefiLlama part already fetched; pools only", flush=True)
        return _u384_pools()
    lst = cg_list()
    cand = {s: [c["id"] for c in lst if c.get("symbol", "").lower() == s] for s in LST}
    mk = cg_markets([i for v in cand.values() for i in v])
    chosen = {s: sorted(v, key=lambda i: -mk.get(i, (0, 0))[0])[:2] for s, v in cand.items()}
    print(f"  chosen ids: {chosen}", flush=True)
    prow = []
    for s, ids in chosen.items():
        for g in ids:
            prow += [{"sym": s, "id": g, "t": int(x["timestamp"]), "price": float(x["price"])} for x in llama_chart(f"coingecko:{g}", T0_2024)]
    for s, g in (("hype", "hyperliquid"), ("eth", "ethereum"), ("usde", "ethena-usde")):
        prow += [{"sym": s, "id": g, "t": int(x["timestamp"]), "price": float(x["price"])} for x in llama_chart(f"coingecko:{g}", T0_2024)]
    save("uncharted_384_llama.parquet", pd.DataFrame(prow))
    _u384_pools()


SKIP_DONE = True


def _u384_pools():
    pools, orow = [], []
    for s, u in LST.items():
        d = gt(f"/search/pools?query={s}&page=1") or {}
        got = []
        for p in d.get("data") or []:
            a = p.get("attributes") or {}
            name = a.get("name") or ""
            if not re.search(s, name, re.I) or not re.search(UNDER_RE[u], name, re.I):
                continue
            rel = p.get("relationships") or {}
            got.append({"sym": s, "network": ((rel.get("network") or {}).get("data") or {}).get("id") or p["id"].split("_")[0],
                        "address": a.get("address"), "name": name,
                        "reserve_usd": float(a.get("reserve_in_usd") or 0), "created": a.get("pool_created_at"),
                        "base": ((rel.get("base_token") or {}).get("data") or {}).get("id"),
                        "quote": ((rel.get("quote_token") or {}).get("data") or {}).get("id")})
        got = sorted(got, key=lambda x: -x["reserve_usd"])[:4]
        pools += got
        print(f"  {s}: {len(got)} pools {[(g['network'], g['name'], round(g['reserve_usd'])) for g in got]}", flush=True)
        for g in got:
            before = None
            for _ in range(3):  # up to 3,000 days
                q = f"/networks/{g['network']}/pools/{g['address']}/ohlcv/day?aggregate=1&limit=1000&currency=token&token=base"
                o = gt(q + (f"&before_timestamp={before}" if before else ""))
                lst_ = (((o or {}).get("data") or {}).get("attributes") or {}).get("ohlcv_list") or []
                orow += [{"sym": s, "network": g["network"], "address": g["address"], "t": int(x[0]), "o": x[1], "h": x[2], "l": x[3],
                          "c": x[4], "v_usd": x[5]} for x in lst_]
                if len(lst_) < 1000:
                    break
                before = min(int(x[0]) for x in lst_)
    save("uncharted_384_pools.json", pools)
    save("uncharted_384_ohlcv.parquet", pd.DataFrame(orow))


# ---------------------------------------------------------------- #385 Hyperliquid pre-launch perps
HL = "https://api.hyperliquid.xyz/info"


def job_u385hyperp():
    """Every Hyperliquid perp: daily candles since listing; CoinGecko id by symbol; first spot price (DefiLlama); funding for pre-launch ones."""
    meta = get(HL, {"type": "meta"}) or {}
    uni = meta.get("universe") or []
    print(f"  HL universe: {len(uni)} perps", flush=True)
    now = int(time.time() * 1000)
    crow = []
    for i, u in enumerate(uni):
        c = get(HL, {"type": "candleSnapshot", "req": {"coin": u["name"], "interval": "1d", "startTime": 1680307200000, "endTime": now}}) or []
        crow += [{"coin": u["name"], "t": int(x["t"]), "o": float(x["o"]), "h": float(x["h"]), "l": float(x["l"]), "c": float(x["c"]),
                  "v": float(x["v"])} for x in c]
        if i % 50 == 0:
            print(f"    candles {i}/{len(uni)}", flush=True)
        time.sleep(1.1)
    cd = pd.DataFrame(crow)
    save("uncharted_385_candles.parquet", cd)
    save("uncharted_385_meta.json", uni)
    first_hl = cd.groupby("coin")["t"].min().to_dict() if len(cd) else {}
    lst = cg_list()
    bysym = {}
    for c in lst:
        bysym.setdefault(c.get("symbol", "").lower(), []).append(c["id"])
    cand = {u["name"]: bysym.get(u["name"].lower(), []) for u in uni if not re.match(r"^k[A-Z]", u["name"])}
    mk = cg_markets([i for v in cand.values() for i in v])
    pick = {}
    for coin, ids in cand.items():
        if ids:
            best = sorted(ids, key=lambda i: (-(mk.get(i, (0, 0))[0] or 0), -(mk.get(i, (0, 0))[1] or 0)))[0]
            pick[coin] = {"id": best, "n_ids": len(ids), "mcap": mk.get(best, (0, 0))[0]}
    keys = [f"coingecko:{v['id']}" for v in pick.values()]
    first = {}
    for i in range(0, len(keys), 40):
        d = get("https://coins.llama.fi/prices/first/" + ",".join(keys[i:i + 40]), tries=2) or {}
        for k, v in (d.get("coins") or {}).items():
            first[k] = v.get("timestamp")
        time.sleep(0.5)
    for coin, v in pick.items():
        v["first_spot"] = first.get(f"coingecko:{v['id']}")
        v["first_hl_ms"] = first_hl.get(coin)
    save("uncharted_385_map.json", pick)
    pre = [c for c, v in pick.items() if v.get("first_spot") and v.get("first_hl_ms") and v["first_hl_ms"] / 1000 < v["first_spot"] - 2 * 86400]
    print(f"  pre-launch candidates (HL listing > 2 days before first spot price): {len(pre)} {pre}", flush=True)
    frow, srow = [], []
    for coin in pre:
        v = pick[coin]
        t, end = v["first_hl_ms"], int((v["first_spot"] + 40 * 86400) * 1000)
        while t < end:
            f = get(HL, {"type": "fundingHistory", "coin": coin, "startTime": t, "endTime": end}) or []
            frow += [{"coin": coin, "t": int(x["time"]), "rate": float(x["fundingRate"]), "premium": float(x.get("premium") or 0)} for x in f]
            if len(f) < 500:
                break
            t = int(f[-1]["time"]) + 1
            time.sleep(1.1)
        time.sleep(1.1)
        srow += [{"coin": coin, "id": v["id"], "t": int(x["timestamp"]), "price": float(x["price"])}
                 for x in llama_chart(f"coingecko:{v['id']}", v["first_spot"] - 86400, v["first_spot"] + 45 * 86400, span=50)]
    save("uncharted_385_funding.parquet", pd.DataFrame(frow))
    save("uncharted_385_spot.parquet", pd.DataFrame(srow))


# ---------------------------------------------------------------- #386 exchange risk tags / delistings
TAG_PROBES = [
    "https://api-manager.upbit.com/api/v1/announcements?os=web&page=1&per_page=20&category=all",
    "https://api-manager.upbit.com/api/v1/announcements?os=web&page=1&per_page=20&category=trade",
    "https://api-manager.upbit.com/api/v1/notices?page=1&per_page=20&thread_name=general",
    "https://www.binance.com/bapi/composite/v1/public/cms/article/list/query?type=1&pageNo=1&pageSize=20&catalogId=161",
    "https://www.binance.com/bapi/composite/v1/public/cms/article/catalog/list/query?catalogId=161&pageNo=1&pageSize=20",
    "https://www.binance.com/bapi/apex/v1/public/apex/cms/article/list/query?type=1&pageNo=1&pageSize=20&catalogId=161",
]


def _items(dd):
    if isinstance(dd, list):
        return dd
    if not isinstance(dd, dict):
        return []
    for k in ("notices", "list", "articles"):
        if isinstance(dd.get(k), list):
            return dd[k]
    cats = dd.get("catalogs")
    if isinstance(cats, list) and cats and isinstance(cats[0], dict):
        return cats[0].get("articles") or []
    return []


def job_u386tags():
    """Upbit notices and Binance delisting-category announcements (titles + dates), 2023-06 onward, if the endpoints answer."""
    probe = {}
    for u in TAG_PROBES:
        st, d = req(u, timeout=40)
        probe[u] = {"status": st, "head": (json.dumps(d) if not isinstance(d, str) else d)[:800] if d is not None else None}
        print(f"  {st} {u}\n      {(probe[u]['head'] or '')[:250]}", flush=True)
        time.sleep(1)
    save("uncharted_386_probe.json", probe)
    stop = int(pd.Timestamp("2023-06-01", tz="UTC").timestamp())
    for key, tmpl in (("upbit", "https://api-manager.upbit.com/api/v1/announcements?os=web&page={p}&per_page=20&category=all"),
                      ("upbit_old", "https://api-manager.upbit.com/api/v1/notices?page={p}&per_page=20&thread_name=general"),
                      ("binance", "https://www.binance.com/bapi/composite/v1/public/cms/article/list/query?type=1&pageNo={p}&pageSize=20&catalogId=161")):
        if probe.get(tmpl.format(p=1), {}).get("status") != 200:
            continue
        items = []
        for p in range(1, 400):
            st, d = req(tmpl.format(p=p), timeout=40)
            if st != 200 or not isinstance(d, dict):
                print(f"    {key} page {p}: {st}", flush=True)
                break
            lst = _items(d.get("data"))
            if not lst:
                break
            items += lst
            ts = [x.get("listed_at") or x.get("created_at") or x.get("releaseDate") for x in lst]
            ts_num = [pd.Timestamp(t, unit="ms", tz="UTC").timestamp() if isinstance(t, (int, float)) else pd.Timestamp(t).timestamp()
                      for t in ts if t]
            if ts_num and min(ts_num) < stop:
                break
            time.sleep(0.6)
        print(f"  {key}: {len(items)} items", flush=True)
        save(f"uncharted_386_{key}.json", items)


# ---------------------------------------------------------------- #387 Uniswap CCA auctions
def keccak256(data: bytes) -> str:
    """Pure-Python Keccak-256 (Ethereum variant); checked against keccak('') and the ERC-20 Transfer topic."""
    rc = [0x1, 0x8082, 0x800000000000808A, 0x8000000080008000, 0x808B, 0x80000001, 0x8000000080008081, 0x8000000000008009, 0x8A, 0x88,
          0x80008009, 0x8000000A, 0x8000808B, 0x800000000000008B, 0x8000000000008089, 0x8000000000008003, 0x8000000000008002,
          0x8000000000000080, 0x800A, 0x800000008000000A, 0x8000000080008081, 0x8000000000008080, 0x80000001, 0x8000000080008008]
    rot = [[0, 36, 3, 41, 18], [1, 44, 10, 45, 2], [62, 6, 43, 15, 61], [28, 55, 25, 21, 56], [27, 20, 39, 8, 14]]
    m = (1 << 64) - 1

    def rol(x, n):
        return ((x << n) | (x >> (64 - n))) & m if n else x
    p = bytearray(data) + b"\x01"
    while len(p) % 136:
        p += b"\x00"
    p[-1] |= 0x80
    s = [[0] * 5 for _ in range(5)]
    for off in range(0, len(p), 136):
        for i in range(17):
            s[i % 5][i // 5] ^= int.from_bytes(p[off + 8 * i: off + 8 * i + 8], "little")
        for r in rc:
            c = [s[x][0] ^ s[x][1] ^ s[x][2] ^ s[x][3] ^ s[x][4] for x in range(5)]
            d = [c[(x - 1) % 5] ^ rol(c[(x + 1) % 5], 1) for x in range(5)]
            s = [[s[x][y] ^ d[x] for y in range(5)] for x in range(5)]
            b = [[0] * 5 for _ in range(5)]
            for x in range(5):
                for y in range(5):
                    b[y][(2 * x + 3 * y) % 5] = rol(s[x][y], rot[x][y])
            s = [[b[x][y] ^ ((~b[(x + 1) % 5][y]) & b[(x + 2) % 5][y]) for y in range(5)] for x in range(5)]
            s[0][0] ^= r
    return b"".join(s[i % 5][i // 5].to_bytes(8, "little") for i in range(4)).hex()


assert keccak256(b"Transfer(address,address,uint256)").startswith("ddf252ad")
CCA_FACTORIES = ["0x000000001F26a0044BaA66024e7b6599c61963F8", "0x00cCa200BF124dBfA848937c553864f4B4CE0632",
                 "0xCCccCcCAE7503Cac057829BF2811De42E16e0bD5", "0x0000ccaDF55C911a2FbC0BB9d2942Aa77c6FAa1D"]
CCA_CHAINS = {"ethereum": ("https://eth.blockscout.com", ["https://ethereum-rpc.publicnode.com", "https://eth.drpc.org"], "eth"),
              "base": ("https://base.blockscout.com", ["https://base-rpc.publicnode.com", "https://mainnet.base.org"], "base"),
              "arbitrum": ("https://arbitrum.blockscout.com", ["https://arbitrum-one-rpc.publicnode.com", "https://arb1.arbitrum.io/rpc"], "arbitrum"),
              "unichain": ("https://unichain.blockscout.com", ["https://unichain-rpc.publicnode.com", "https://mainnet.unichain.org"], "unichain")}
SEL = {n: keccak256(n.encode())[:8] for n in ("clearingPrice()", "token()", "currency()", "endBlock()", "startBlock()", "isGraduated()",
                                               "totalSupply()", "currencyRaised()", "floorPrice()", "decimals()", "symbol()", "totalCleared()")}


RPC_DEADLINE = [float("inf")]


def rpc(urls, method, params):
    if time.time() > RPC_DEADLINE[0]:
        return None
    for u in urls:
        d = get(u, {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}, tries=1, timeout=20)
        if d and "result" in d:
            return d["result"]
    return None


def call(urls, to, fn):
    r = rpc(urls, "eth_call", [{"to": to, "data": "0x" + SEL[fn]}, "latest"])
    return r if r and r != "0x" else None


def dec_str(h):
    try:
        b = bytes.fromhex(h[2:])
        if len(b) >= 64:
            n = int.from_bytes(b[32:64], "big")
            return b[64:64 + n].decode("utf-8", "replace")
        return b.rstrip(b"\x00").decode("utf-8", "replace")
    except Exception:  # noqa: BLE001
        return None


def job_u387cca():
    """Every CCA auction created by the canonical factories on Ethereum/Base/Arbitrum/Unichain + state + post-auction prices."""
    topic = "0x" + keccak256(b"AuctionCreated(address,address,uint256,bytes)")
    rows = []
    for chain, (bs, rpcs, gtnet) in CCA_CHAINS.items():
        latest = rpc(rpcs, "eth_blockNumber", [])
        latest = int(latest, 16) if latest else None
        for f in CCA_FACTORIES:
            frm = 0
            for _ in range(10):
                d = get(f"{bs}/api?module=logs&action=getLogs&fromBlock={frm}&toBlock=latest&address={f}&topic0={topic}", tries=3, timeout=90)
                logs = (d or {}).get("result") or []
                if not isinstance(logs, list):
                    break
                for lg in logs:
                    rows.append({"chain": chain, "factory": f, "auction": "0x" + lg["topics"][1][-40:], "token": "0x" + lg["topics"][2][-40:],
                                 "amount_raw": int(lg["data"][2:66], 16) if len(lg["data"]) >= 66 else None,
                                 "block": int(lg["blockNumber"], 16), "ts": int(lg["timeStamp"], 16), "tx": lg.get("transactionHash"),
                                 "latest_block": latest})
                if len(logs) < 1000:
                    break
                frm = int(logs[-1]["blockNumber"], 16) + 1
            time.sleep(0.5)
        print(f"  {chain}: {sum(1 for r in rows if r['chain'] == chain)} auctions (latest block {latest})", flush=True)
    rows = rows[:800]
    for i, r in enumerate(rows):
        _, rpcs, _ = CCA_CHAINS[r["chain"]]
        for fn in ("clearingPrice()", "currency()", "endBlock()", "startBlock()", "isGraduated()", "totalSupply()", "currencyRaised()",
                   "floorPrice()", "totalCleared()"):
            r[fn[:-2]] = call(rpcs, r["auction"], fn)
        r["token_decimals"] = call(rpcs, r["token"], "decimals()")
        r["token_symbol"] = dec_str(call(rpcs, r["token"], "symbol()") or "0x")
        cur = "0x" + r["currency"][-40:] if r.get("currency") else None
        r["currency_addr"] = cur
        if cur and int(cur, 16) != 0:
            r["currency_decimals"] = call(rpcs, cur, "decimals()")
            r["currency_symbol"] = dec_str(call(rpcs, cur, "symbol()") or "0x")
        else:
            r["currency_decimals"], r["currency_symbol"] = hex(18), "ETH"
        if r.get("endBlock"):
            eb = int(r["endBlock"], 16)
            blk = rpc(rpcs, "eth_getBlockByNumber", [hex(eb), False]) if r.get("latest_block") and eb <= r["latest_block"] else None
            r["end_ts"] = int(blk["timestamp"], 16) if blk else None
        if i % 25 == 0:
            print(f"    state {i}/{len(rows)}", flush=True)
    save("uncharted_387_auctions.json", rows)
    # post-auction prices for auctions that ended and graduated
    prow, gpools = [], []
    done = [r for r in rows if r.get("end_ts") and r.get("isGraduated") and int(r["isGraduated"], 16) == 1]
    print(f"  ended + graduated: {len(done)}", flush=True)
    for r in done:
        k = f"{r['chain']}:{r['token']}"
        prow += [{"key": k, "t": int(x["timestamp"]), "price": float(x["price"])}
                 for x in llama_chart(k, r["end_ts"] - 2 * 86400, r["end_ts"] + 40 * 86400, span=45)]
        cur = r.get("currency_addr")
        ck = "coingecko:ethereum" if not cur or int(cur, 16) == 0 else f"{r['chain']}:{cur}"
        prow += [{"key": ck, "t": int(x["timestamp"]), "price": float(x["price"])}
                 for x in llama_chart(ck, r["end_ts"] - 2 * 86400, r["end_ts"] + 40 * 86400, span=45)]
        gtnet = CCA_CHAINS[r["chain"]][2]
        p = gt(f"/networks/{gtnet}/tokens/{r['token']}/pools?page=1") or {}
        best = sorted(p.get("data") or [], key=lambda x: -float((x.get("attributes") or {}).get("reserve_in_usd") or 0))[:1]
        for b in best:
            a = b["attributes"]
            o = gt(f"/networks/{gtnet}/pools/{a['address']}/ohlcv/day?aggregate=1&limit=200&currency=usd&token={r['token']}") or {}
            for x in ((o.get("data") or {}).get("attributes") or {}).get("ohlcv_list") or []:
                gpools.append({"auction": r["auction"], "pool": a["address"], "name": a.get("name"), "t": int(x[0]), "o": x[1], "h": x[2],
                               "l": x[3], "c": x[4], "v_usd": x[5]})
    save("uncharted_387_llama.parquet", pd.DataFrame(prow))
    save("uncharted_387_gt.parquet", pd.DataFrame(gpools))


REAL_CUR = {"ethereum": {"0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48", "0xdac17f958d2ee523a2206206994597c13d831ec7"},
            "base": {"0x833589fcd6edb6e08f4c7c32d4f71b54bda02913"}, "arbitrum": {"0xaf88d065e77c8cc2239327c5edb3a432268e5831"},
            "unichain": {"0x078d782b760474a361dda0af3839290b0ef57ad6"}}


def _state(r, rpcs):
    r["isGraduated"] = call(rpcs, r["auction"], "isGraduated()")
    if r["isGraduated"] is not None and int(r["isGraduated"], 16) == 0:
        return  # not graduated: no sale happened, nothing else needed
    for fn in ("clearingPrice()", "currency()", "endBlock()", "startBlock()", "isGraduated()", "totalSupply()", "currencyRaised()",
               "floorPrice()", "totalCleared()"):
        r[fn[:-2]] = call(rpcs, r["auction"], fn)
    r["token_decimals"] = call(rpcs, r["token"], "decimals()")
    r["token_symbol"] = dec_str(call(rpcs, r["token"], "symbol()") or "0x")
    cur = "0x" + r["currency"][-40:] if r.get("currency") else None
    r["currency_addr"] = cur
    if cur and int(cur, 16) != 0:
        r["currency_decimals"] = call(rpcs, cur, "decimals()")
        r["currency_symbol"] = dec_str(call(rpcs, cur, "symbol()") or "0x")
    else:
        r["currency_decimals"], r["currency_symbol"] = hex(18), "ETH"
    if r.get("endBlock"):
        eb = int(r["endBlock"], 16)
        blk = rpc(rpcs, "eth_getBlockByNumber", [hex(eb), False]) if r.get("latest_block") and eb <= r["latest_block"] else None
        r["end_ts"] = int(blk["timestamp"], 16) if blk else None


def job_u387ccab():
    """#387 second pass: Ethereum auctions (chunked eth_getLogs) + post-auction prices only for graduated auctions in real USDC/USDT/ETH
    raising >= $10K (>= 4 ETH); tiny and fake-currency test auctions have no market to price."""
    topic = "0x" + keccak256(b"AuctionCreated(address,address,uint256,bytes)")
    rpcs = ["https://ethereum-rpc.publicnode.com", "https://eth.drpc.org", "https://rpc.ankr.com/eth"]
    if SKIP_DONE and (OUT / "uncharted_387_eth.json").exists():
        rows = json.loads((OUT / "uncharted_387_eth.json").read_text())
        print(f"  ethereum auctions from uncharted_387_eth.json (job u387eth): {len(rows)}", flush=True)
        return _u387_prices(rows)
    latest = int(rpc(rpcs, "eth_blockNumber", []), 16)
    rows, frm, step = [], 23_000_000, 50_000
    while frm <= latest:
        to = min(frm + step - 1, latest)
        lg = rpc(rpcs, "eth_getLogs", [{"fromBlock": hex(frm), "toBlock": hex(to), "address": CCA_FACTORIES, "topics": [topic]}])
        if lg is None and step > 5_000:
            step //= 2
            continue
        for x in lg or []:
            rows.append({"chain": "ethereum", "factory": x["address"], "auction": "0x" + x["topics"][1][-40:], "token": "0x" + x["topics"][2][-40:],
                         "block": int(x["blockNumber"], 16), "tx": x.get("transactionHash"), "latest_block": latest})
        frm = to + 1
    print(f"  ethereum: {len(rows)} auctions (blocks 23,000,000..{latest})", flush=True)
    for r in rows:
        _state(r, rpcs)
    save("uncharted_387_eth.json", rows)
    _u387_prices(rows)


def _u387_prices(rows):
    allr = json.loads((OUT / "uncharted_387_auctions.json").read_text()) + rows
    keep = []
    for r in allr:
        try:
            grad = r.get("isGraduated") and int(r["isGraduated"], 16) == 1
            raised = int(r["currencyRaised"], 16) / 10 ** int(r["currency_decimals"], 16) if r.get("currencyRaised") else 0
        except (TypeError, ValueError):
            continue
        cur = (r.get("currency_addr") or "").lower()
        eth = not cur or int(cur, 16) == 0
        real = eth or cur in REAL_CUR.get(r["chain"], set())
        if grad and r.get("end_ts") and real and raised >= (4 if eth else 10_000):
            r["raised"] = raised
            keep.append(r)
    print(f"  graduated, ended, real currency, >= $10K: {len(keep)}", flush=True)
    prow, gpools = [], []
    for r in keep:
        print(f"    {r['chain']} {r.get('token_symbol')} raised {r['raised']:,.1f} {r.get('currency_symbol')}", flush=True)
        k = f"{r['chain']}:{r['token']}"
        prow += [{"key": k, "t": int(x["timestamp"]), "price": float(x["price"])}
                 for x in llama_chart(k, r["end_ts"] - 2 * 86400, r["end_ts"] + 40 * 86400, span=45)]
        cur = r.get("currency_addr")
        ck = "coingecko:ethereum" if not cur or int(cur, 16) == 0 else f"{r['chain']}:{cur}"
        prow += [{"key": ck, "t": int(x["timestamp"]), "price": float(x["price"])}
                 for x in llama_chart(ck, r["end_ts"] - 2 * 86400, r["end_ts"] + 40 * 86400, span=45)]
        gtnet = CCA_CHAINS[r["chain"]][2]
        p = gt(f"/networks/{gtnet}/tokens/{r['token']}/pools?page=1") or {}
        best = sorted(p.get("data") or [], key=lambda x: -float((x.get("attributes") or {}).get("reserve_in_usd") or 0))[:1]
        for b in best:
            a = b["attributes"]
            o = gt(f"/networks/{gtnet}/pools/{a['address']}/ohlcv/day?aggregate=1&limit=200&currency=usd&token={r['token']}") or {}
            for x in ((o.get("data") or {}).get("attributes") or {}).get("ohlcv_list") or []:
                gpools.append({"auction": r["auction"], "pool": a["address"], "name": a.get("name"), "t": int(x[0]), "o": x[1], "h": x[2],
                               "l": x[3], "c": x[4], "v_usd": x[5]})
    save("uncharted_387_keep.json", keep)
    save("uncharted_387_llama.parquet", pd.DataFrame(prow))
    save("uncharted_387_gt.parquet", pd.DataFrame(gpools))


# ---------------------------------------------------------------- #389 Stage 2a: Binance USD-M daily OHLC (every USDT perp ever listed)
def job_u389binance():
    import concurrent.futures as cf
    import io
    import xml.etree.ElementTree as ET
    import zipfile
    s3, ns = "https://s3-ap-northeast-1.amazonaws.com/data.binance.vision", "{http://s3.amazonaws.com/doc/2006-03-01/}"

    def s3_list(prefix, delimiter=True):
        keys, prefs, marker = [], [], ""
        for _ in range(60):
            u = f"{s3}?prefix={prefix}" + ("&delimiter=/" if delimiter else "") + (f"&marker={marker}" if marker else "")
            try:
                with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=60) as r:
                    root = ET.fromstring(r.read())
            except Exception as e:  # noqa: BLE001
                print(f"  list fail {prefix}: {e}", flush=True)
                break
            keys += [c.find(ns + "Key").text for c in root.findall(ns + "Contents")]
            prefs += [c.find(ns + "Prefix").text for c in root.findall(ns + "CommonPrefixes")]
            if (root.find(ns + "IsTruncated").text or "").lower() != "true":
                break
            marker = keys[-1] if keys else prefs[-1]
        return keys, prefs

    _, prefs = s3_list("data/futures/um/monthly/klines/")
    syms = sorted({p.rstrip("/").split("/")[-1] for p in prefs})
    syms = [x for x in syms if x.endswith("USDT") and "_" not in x]
    print(f"  USDT perp symbols ever listed: {len(syms)}", flush=True)

    def one(sym):
        keys, _ = s3_list(f"data/futures/um/monthly/klines/{sym}/1d/", delimiter=False)
        rows = []
        for k in sorted(k for k in keys if k.endswith(".zip")):
            mth = k.split("-1d-")[-1][:7]
            if mth > "2026-10":
                continue
            try:
                with urllib.request.urlopen(urllib.request.Request("https://data.binance.vision/" + k, headers=UA), timeout=60) as r:
                    z = zipfile.ZipFile(io.BytesIO(r.read()))
                    txt = z.read(z.namelist()[0]).decode()
            except Exception:  # noqa: BLE001
                continue
            for ln in txt.splitlines():
                f = ln.split(",")
                if not f or not f[0].strip().isdigit():
                    continue
                ts = int(f[0])
                ts = ts // 1000 if ts > 10**14 else ts
                rows.append((sym, ts // 1000, float(f[1]), float(f[2]), float(f[3]), float(f[4]), float(f[7])))
        return rows

    out, t0 = [], time.time()
    with cf.ThreadPoolExecutor(16) as ex:
        for i, r in enumerate(ex.map(one, syms)):
            out += r
            if i % 100 == 0:
                print(f"  {i}/{len(syms)} symbols, {len(out)} rows, {time.time() - t0:.0f}s", flush=True)
    d = pd.DataFrame(out, columns=["sym", "t", "o", "h", "l", "c", "qvol"])
    save("uncharted_389_binance_ohlc.parquet", d)


# ---------------------------------------------------------------- #387 Ethereum auctions via Blockscout v2 address logs
def job_u387eth():
    RPC_DEADLINE[0] = time.time() + 20 * 60  # hard cap: 20 minutes of RPC calls
    topic = "0x" + keccak256(b"AuctionCreated(address,address,uint256,bytes)")
    rpcs = ["https://eth.drpc.org", "https://rpc.flashbots.net", "https://ethereum.publicnode.com", "https://eth.llamarpc.com"]
    latest = rpc(rpcs, "eth_blockNumber", [])
    latest = int(latest, 16) if latest else None
    print(f"  ethereum latest block {latest}", flush=True)
    rows = []
    for f in CCA_FACTORIES:
        nxt = ""
        for _ in range(40):
            d = get(f"https://eth.blockscout.com/api/v2/addresses/{f}/logs" + nxt, tries=3, timeout=90)
            for it in (d or {}).get("items") or []:
                tp = [t for t in (it.get("topics") or []) if t]
                if not tp or tp[0].lower() != topic:
                    continue
                rows.append({"chain": "ethereum", "factory": f, "auction": "0x" + tp[1][-40:], "token": "0x" + tp[2][-40:],
                             "block": it.get("block_number"), "tx": it.get("transaction_hash"), "latest_block": latest})
            npp = (d or {}).get("next_page_params")
            if not npp:
                break
            nxt = "?" + urllib.parse.urlencode(npp)
            time.sleep(0.5)
    print(f"  ethereum: {len(rows)} auctions", flush=True)
    for i, r in enumerate(rows):
        _state(r, rpcs)
        if i % 10 == 0:
            print(f"    state {i}/{len(rows)}", flush=True)
    if time.time() > RPC_DEADLINE[0]:
        print("  RPC time cap reached: some auction states are missing", flush=True)
    save("uncharted_387_eth.json", rows)


# ---------------------------------------------------------------- #391 Hong Kong IPO one-lot applications
HK_TEMPLATES = {
    "aastocks": "http://www.aastocks.com/en/stocks/market/ipo/listedipo.aspx?s=3&o=0&page={p}",
    "aastocks_b": "https://www.aastocks.com/en/stocks/market/ipo/listedipo.aspx?page={p}",
    "etnet_info": "https://www.etnet.com.hk/www/eng/stocks/ci_ipo_info.php?page={p}",
}


def _html(url):
    try:
        r = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
                                                 "Accept": "text/html,*/*", "Accept-Language": "en"})
        with urllib.request.urlopen(r, timeout=60) as resp:
            raw = resp.read().decode("utf-8", "replace")
            return resp.status, re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", raw)
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception as e:  # noqa: BLE001
        return type(e).__name__, ""


def job_u391hkipo():
    """Hong Kong IPO result tables (raw HTML, scripts stripped), page by page until a page repeats or is empty."""
    out = {}
    for key, tmpl in HK_TEMPLATES.items():
        prev, pages = None, []
        for p in range(1, 60):
            st, h = _html(tmpl.format(p=p))
            sig = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", h))[:20000]
            print(f"  {key} page {p}: {st} {len(h)} bytes", flush=True)
            if st != 200 or len(h) < 2000 or sig == prev:
                break
            pages.append(h)
            prev = sig
            time.sleep(1.5)
        out[key] = pages
    save("uncharted_391_hkipo_html.json", out)


def job_u389docs():
    """#389 S2d: Hyperliquid docs pages on margining / open orders (text snippets around key words)."""
    import html as _h
    out = {}
    for u in ("https://hyperliquid.gitbook.io/hyperliquid-docs/trading/margining",
              "https://hyperliquid.gitbook.io/hyperliquid-docs/trading/order-types",
              "https://hyperliquid.gitbook.io/hyperliquid-docs/trading/contract-specifications",
              "https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/rate-limits-and-user-limits",
              "https://hyperliquid.gitbook.io/hyperliquid-docs/trading/fees"):
        st, raw = _html(u)
        txt = re.sub(r"\s+", " ", _h.unescape(re.sub(r"<[^>]+>", " ", raw)))
        hits = {}
        for k in ("open order", "resting", "reserve", "initial margin", "minimum order", "order value", "1000", "insufficient"):
            hits[k] = [txt[max(0, m.start() - 300): m.start() + 300] for m in re.finditer(re.escape(k), txt, re.I)][:4]
        out[u] = {"status": st, "chars": len(txt), "hits": hits}
        print(f"  {st} {len(txt)} chars {u}", flush=True)
    save("uncharted_389_hldocs.json", out)


# ---------------------------------------------------------------- wave 3 (#392-#401), docs/PREREG_UNCHARTED_WAVE3_20261125.md
def _w3_binance():
    stop = int(pd.Timestamp("2023-01-01", tz="UTC").timestamp() * 1000)
    out = {}
    for cat in (48, 49, 161):
        items = []
        for p in range(1, 200):
            st, d = req(f"https://www.binance.com/bapi/composite/v1/public/cms/article/list/query?type=1&pageNo={p}&pageSize=50&catalogId={cat}",
                        timeout=40)
            lst = _items((d or {}).get("data")) if isinstance(d, dict) else []
            if st != 200 or not lst:
                break
            items += [{"title": x.get("title"), "releaseDate": x.get("releaseDate"), "code": x.get("code")} for x in lst]
            if min(int(x.get("releaseDate") or 0) for x in lst) < stop:
                break
            time.sleep(0.6)
        print(f"  binance catalog {cat}: {len(items)} items", flush=True)
        out[str(cat)] = items
    save("uncharted_w3_binance_ann.json", out)


def _w3_korea(deadline, out_name="uncharted_w3_korea.parquet"):
    rows = []
    mk = get("https://api.upbit.com/v1/market/all?isDetails=false", tries=3) or []
    krw = [m["market"] for m in mk if str(m.get("market", "")).startswith("KRW-")]
    print(f"  upbit KRW markets: {len(krw)}", flush=True)
    for m in krw:
        if time.time() > deadline:
            print("  upbit: time cap reached", flush=True)
            break
        to, first = None, None
        for _ in range(15):
            u = f"https://api.upbit.com/v1/candles/days?market={m}&count=200" + (f"&to={urllib.parse.quote(to)}" if to else "")
            d = get(u, tries=2, pause=1) or []
            if not isinstance(d, list) or not d:
                break
            first = min(x["candle_date_time_utc"] for x in d)
            if len(d) < 200:
                break
            to = first.replace("T", " ")
            time.sleep(0.15)
        if first:
            rows.append({"venue": "upbit", "coin": m[4:], "first_day": first[:10]})
        time.sleep(0.12)
    tk = (get("https://api.bithumb.com/public/ticker/ALL_KRW", tries=3) or {}).get("data") or {}
    coins = [c for c in tk if c != "date"]
    print(f"  bithumb KRW coins: {len(coins)}", flush=True)
    for c in coins:
        if time.time() > deadline:
            print("  bithumb: time cap reached", flush=True)
            break
        d = (get(f"https://api.bithumb.com/public/candlestick/{c}_KRW/24h", tries=2, pause=1) or {}).get("data") or []
        if d:
            rows.append({"venue": "bithumb", "coin": c, "first_day": str(pd.Timestamp(int(min(int(x[0]) for x in d)), unit="ms").date())})
        time.sleep(0.12)
    save(out_name, pd.DataFrame(rows))


def _w3_treasury(deadline):
    tr = get("https://api.llama.fi/treasuries", tries=3) or []
    print(f"  defillama treasuries: {len(tr)}", flush=True)
    save("uncharted_w3_treasuries.json", tr)
    ids = sorted({t.get("gecko_id") for t in tr if t.get("gecko_id")})
    caps = []
    for g in ids:
        if time.time() > deadline:
            print("  coingecko market caps: time cap reached", flush=True)
            break
        d = get(f"https://api.coingecko.com/api/v3/coins/{g}/market_chart?vs_currency=usd&days=365&interval=daily", tries=3, pause=20) or {}
        caps += [{"id": g, "t": int(x[0]) // 1000, "mcap": x[1]} for x in d.get("market_caps") or []]
        time.sleep(7)
    save("uncharted_w3_mcaps.parquet", pd.DataFrame(caps))
    hist = {}
    for t in tr[:400]:
        if time.time() > deadline:
            break
        slug = t.get("slug") or t.get("name")
        if not slug or not t.get("gecko_id"):
            continue
        st, d = req(f"https://api.llama.fi/treasury/{urllib.parse.quote(str(slug))}", timeout=40)
        if st == 200 and isinstance(d, dict):
            hist[slug] = {"tokensInUsd": (d.get("tokensInUsd") or [])[-400:], "chainTvls_keys": list((d.get("chainTvls") or {}).keys())}
        elif not hist and st != 200:
            print(f"  treasury history endpoint: {st} (today's treasury only)", flush=True)
            break
        time.sleep(0.3)
    save("uncharted_w3_treasury_hist.json", hist)


def _w3_cowamm():
    pools = (get("https://yields.llama.fi/pools", tries=3) or {}).get("data") or []
    sel = [p for p in pools if re.search(r"cow", p.get("project") or "", re.I)]
    print(f"  CoW AMM pools: {len(sel)} ({sorted({p['project'] for p in sel})})", flush=True)
    rows, prow, keys = [], [], set()
    for p in sel:
        c = get(f"https://yields.llama.fi/chart/{p['pool']}", tries=2)
        rows += [{"pool": p["pool"], "ts": x.get("timestamp"), "tvlUsd": x.get("tvlUsd"), "apyBase": x.get("apyBase"), "apy": x.get("apy")}
                 for x in (c or {}).get("data") or []]
        for a in p.get("underlyingTokens") or []:
            keys.add(f"{(p.get('chain') or '').lower()}:{a.lower()}")
        time.sleep(0.25)
    for k in sorted(keys):
        prow += [{"key": k, "t": int(x["timestamp"]), "price": float(x["price"])} for x in llama_chart(k, T0_2024)]
    save("uncharted_w3_cowamm.json", sel)
    save("uncharted_w3_cowamm_charts.parquet", pd.DataFrame(rows))
    save("uncharted_w3_cowamm_prices.parquet", pd.DataFrame(prow))


LBP_FACTORIES = {"eth": ["0x751A0bC0e3f75b38e01Cf25bFCE7fF36DE1C87DE", "0x0F3e0c4218b7b0108a3643cFe9D3ec0d4F57c54e",
                         "0x4eff2d77D9fFbAeFB4b141A3e494c085b3FF4Cb5", "0x02916d8F0891309806FCb347Bf4191692cbDDcAF",
                         "0xD5584b37D1845fFeD958C2d94bC675603DdCce68", "0x6642863979e66d995717A2B836A121700595069A"],
                 "arbitrum": ["0x142B9666a0a3A30477b052962ddA81547E7029ab", "0x1802953277FD955f9a254B80Aa0582f193cF1d77",
                              "0x4BB42f71CAB7Bd13e9f958dA4351B9fa2d3A42FF", "0x8D217CB74f675B46cC2767C8cF0aAB53BE1c4818",
                              "0xF9309a99836b5F07a2440c177C049b0f0A9A2c33", "0x6b7DEd11F15D6AB9959c29cEd3Cd101D69A14c35"],
                 "base": ["0x0c6052254551EAe3ECac77B01DFcf1025418828f", "0x662112B8CB18889e81459b92CA0f894a2ef2c1B8",
                          "0x0b11209B8c5E821b18dED147583b8978c3E63911", "0x6eE18fbb1BBcC5CF700cD75ea1aef2bb21e3cB3F",
                          "0x6642863979e66d995717A2B836A121700595069A"]}
LBP_BS = {"eth": "https://eth.blockscout.com", "arbitrum": "https://arbitrum.blockscout.com", "base": "https://base.blockscout.com"}
LLAMA_CHAIN = {"eth": "ethereum", "arbitrum": "arbitrum", "base": "base"}


def _w3_lbp(deadline):
    topic = "0x" + keccak256(b"PoolCreated(address)")
    pools = []
    for net, facs in LBP_FACTORIES.items():
        for f in facs:
            nxt = ""
            for _ in range(30):
                d = get(f"{LBP_BS[net]}/api/v2/addresses/{f}/logs" + nxt, tries=3, timeout=90)
                for it in (d or {}).get("items") or []:
                    tp = [t for t in (it.get("topics") or []) if t]
                    if tp and tp[0].lower() == topic and len(tp) > 1:
                        pools.append({"net": net, "factory": f, "pool": "0x" + tp[1][-40:], "block": it.get("block_number")})
                npp = (d or {}).get("next_page_params")
                if not npp:
                    break
                nxt = "?" + urllib.parse.urlencode(npp)
                time.sleep(0.4)
    print(f"  LBP pools created: {len(pools)}", flush=True)
    pools = sorted(pools, key=lambda x: -(x["block"] or 0))
    info, ohlc, prow = [], [], []
    for p in pools:
        if time.time() > deadline:
            print("  LBP: time cap reached", flush=True)
            break
        d = gt(f"/networks/{p['net']}/pools/{p['pool']}") or {}
        a = (d.get("data") or {}).get("attributes") or {}
        rel = (d.get("data") or {}).get("relationships") or {}
        if not a:
            continue
        base = (((rel.get("base_token") or {}).get("data") or {}).get("id") or "").split("_")[-1]
        quote = (((rel.get("quote_token") or {}).get("data") or {}).get("id") or "").split("_")[-1]
        info.append({**p, "name": a.get("name"), "created": a.get("pool_created_at"), "base": base, "quote": quote,
                     "vol_24h": ((a.get("volume_usd") or {}).get("h24"))})
        o = gt(f"/networks/{p['net']}/pools/{p['pool']}/ohlcv/day?aggregate=1&limit=1000&currency=usd") or {}
        for x in ((o.get("data") or {}).get("attributes") or {}).get("ohlcv_list") or []:
            ohlc.append({"pool": p["pool"], "t": int(x[0]), "c": x[4], "v_usd": x[5]})
    save("uncharted_w3_lbp_pools.json", info)
    save("uncharted_w3_lbp_ohlcv.parquet", pd.DataFrame(ohlc))
    od = pd.DataFrame(ohlc)
    if len(od):
        last = od[od["v_usd"] > 0].groupby("pool")["t"].max()
        for p in info:
            if p["pool"] in last.index and p.get("base"):
                t_end = int(last[p["pool"]])
                for tok in {p["base"], p["quote"]}:
                    k = f"{LLAMA_CHAIN[p['net']]}:{tok}"
                    prow += [{"pool": p["pool"], "key": k, "t": int(x["timestamp"]), "price": float(x["price"])}
                             for x in llama_chart(k, t_end - 3 * 86400, t_end + 12 * 86400, span=15)]
    save("uncharted_w3_lbp_prices.parquet", pd.DataFrame(prow))


def job_uwave3():
    t0 = time.time()
    for name, fn in (("binance", _w3_binance), ("korea", lambda: _w3_korea(time.time() + 15 * 60)),
                     ("cowamm", _w3_cowamm), ("lbp", lambda: _w3_lbp(time.time() + 35 * 60)),
                     ("treasury", lambda: _w3_treasury(time.time() + 30 * 60))):
        print(f"== wave3 {name} ({time.time() - t0:.0f}s)", flush=True)
        _safe(fn)()


# ---------------------------------------------------------------- #402-#404 (docs/PREREG_WICK_SCALE_20261125.md)
def _scale_binance_1h(deadline):
    """Hourly wick-bid fills on every Binance USDT perp, 2022-01..2026-10 (fills only are saved)."""
    import concurrent.futures as cf
    import io
    import xml.etree.ElementTree as ET
    import zipfile
    s3, ns = "https://s3-ap-northeast-1.amazonaws.com/data.binance.vision", "{http://s3.amazonaws.com/doc/2006-03-01/}"

    def s3_list(prefix, delimiter=True):
        keys, prefs, marker = [], [], ""
        for _ in range(60):
            u = f"{s3}?prefix={urllib.parse.quote(prefix)}" + ("&delimiter=/" if delimiter else "") + (f"&marker={urllib.parse.quote(marker)}" if marker else "")
            try:
                with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=60) as r:
                    root = ET.fromstring(r.read())
            except Exception:  # noqa: BLE001
                break
            keys += [c.find(ns + "Key").text for c in root.findall(ns + "Contents")]
            prefs += [c.find(ns + "Prefix").text for c in root.findall(ns + "CommonPrefixes")]
            if (root.find(ns + "IsTruncated").text or "").lower() != "true":
                break
            marker = keys[-1] if keys else prefs[-1]
        return keys, prefs

    _, prefs = s3_list("data/futures/um/monthly/klines/")
    syms = sorted({p.rstrip("/").split("/")[-1] for p in prefs})
    syms = [x for x in syms if x.endswith("USDT") and "_" not in x]
    print(f"  Binance USDT perps: {len(syms)}", flush=True)
    XS = (0.05, 0.08, 0.12)

    def one(sym):
        if time.time() > deadline:
            return [], None
        keys, _ = s3_list(f"data/futures/um/monthly/klines/{sym}/1h/", delimiter=False)
        months = sorted(k.split("-1h-")[-1][:7] for k in keys if k.endswith(".zip"))
        if not months:
            return [], None
        rows = []
        for k in sorted(k for k in keys if k.endswith(".zip")):
            mth = k.split("-1h-")[-1][:7]
            if mth < "2022-01" or mth > "2026-10":
                continue
            try:
                with urllib.request.urlopen(urllib.request.Request("https://data.binance.vision/" + urllib.parse.quote(k), headers=UA), timeout=60) as r:
                    z = zipfile.ZipFile(io.BytesIO(r.read()))
                    txt = z.read(z.namelist()[0]).decode()
            except Exception:  # noqa: BLE001
                continue
            for ln in txt.splitlines():
                f = ln.split(",")
                if f and f[0].strip().isdigit():
                    ts = int(f[0])
                    ts = ts // 1000 if ts > 10**14 else ts
                    rows.append((ts // 1000, float(f[1]), float(f[2]), float(f[3]), float(f[4]), float(f[7])))
        if not rows:
            return [], months[0]
        d = pd.DataFrame(rows, columns=["t", "o", "h", "l", "c", "qv"]).drop_duplicates("t").sort_values("t")
        d["day"] = d["t"] // 86400
        dv = d.groupby("day")["qv"].sum().shift().rename("pvol")  # previous day's USD volume
        d = d.join(dv, on="day")
        first = pd.Timestamp(months[0] + "-01", tz="UTC").timestamp()
        d = d[d["t"] >= first + 30 * 86400]
        prev = d["c"].shift()
        out = []
        for x in XS:
            lvl = prev * (1 - x)
            hit = (d["l"] <= lvl * 0.995) & prev.notna() & d["pvol"].notna()
            px = np.minimum(lvl[hit], d["o"][hit])
            ret = d["c"][hit] / px - 1 - 0.00015 - 0.00045
            size = np.minimum(1500.0, 0.01 * d["pvol"][hit])
            out += [(sym, int(t), x, float(r), float(sz)) for t, r, sz in zip(d["t"][hit], ret, size)]
        return out, months[0]

    def safe_one(sym):
        try:
            return one(sym)
        except Exception as e:  # noqa: BLE001
            print(f"  {sym}: {type(e).__name__} {str(e)[:80]}", flush=True)
            return [], None

    allf, firsts, t0 = [], {}, time.time()
    with cf.ThreadPoolExecutor(16) as ex:
        for i, (sym, (f, m0)) in enumerate(zip(syms, ex.map(safe_one, syms))):
            allf += f
            firsts[sym] = m0
            if i % 100 == 0:
                print(f"  {i}/{len(syms)} symbols, {len(allf)} fills, {time.time() - t0:.0f}s", flush=True)
    save("wickscale_binance_1h_fills.parquet", pd.DataFrame(allf, columns=["sym", "t", "x", "ret", "size"]))
    save("wickscale_binance_1h_first.json", firsts)


def _scale_hl_1h():
    meta = get(HL, {"type": "meta"}) or {}
    now = int(time.time() * 1000)
    rows = []
    for u in meta.get("universe") or []:
        c = get(HL, {"type": "candleSnapshot", "req": {"coin": u["name"], "interval": "1h", "startTime": now - 215 * 86400 * 1000, "endTime": now}}) or []
        rows += [(u["name"], int(x["t"]), float(x["o"]), float(x["h"]), float(x["l"]), float(x["c"]), float(x["v"])) for x in c]
        time.sleep(1.1)
    save("wickscale_hl_1h.parquet", pd.DataFrame(rows, columns=["coin", "t", "o", "h", "l", "c", "v"]))


def _venue_terms():
    out = {}
    for venue, urls in {"dydx": ["https://dydx.trade/terms", "https://dydx.exchange/terms"],
                        "aster": ["https://www.asterdex.com/en/terms-of-service", "https://docs.asterdex.com/about-us/terms-of-service"],
                        "lighter": ["https://lighter.xyz/terms", "https://docs.lighter.xyz/terms-of-use"],
                        "paradex": ["https://www.paradex.trade/terms-of-service", "https://docs.paradex.trade/legal/terms-of-service"],
                        "hyperliquid": ["https://app.hyperliquid.xyz/terms"]}.items():
        for u in urls:
            st, h = _html(u)
            txt = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", h))
            hits = {k: [txt[max(0, m.start() - 250): m.start() + 350] for m in re.finditer(k, txt, re.I)][:3]
                    for k in ("Malaysia", "restricted (jurisdiction|territor|countr)", "prohibited (jurisdiction|countr)", "sanction")}
            out[f"{venue}|{u}"] = {"status": st, "chars": len(txt), "hits": hits}
            print(f"  terms {venue} {st} {len(txt)} chars {u}", flush=True)
    save("wickscale_terms.json", out)


def _venue_dydx(deadline):
    mk = (get("https://indexer.dydx.trade/v4/perpetualMarkets", tries=3) or {}).get("markets") or {}
    rows = []
    for tk in mk:
        to = None
        for _ in range(30):
            if time.time() > deadline:
                break
            u = f"https://indexer.dydx.trade/v4/candles/perpetualMarkets/{tk}?resolution=1DAY&limit=100" + (f"&toISO={to}" if to else "")
            c = (get(u, tries=2) or {}).get("candles") or []
            rows += [(tk, x["startedAt"], float(x["open"]), float(x["high"]), float(x["low"]), float(x["close"]), float(x.get("usdVolume") or 0))
                     for x in c]
            if len(c) < 100:
                break
            to = min(x["startedAt"] for x in c)
            time.sleep(0.15)
    print(f"  dydx: {len(mk)} markets, {len(rows)} candles", flush=True)
    save("wickscale_dydx_1d.parquet", pd.DataFrame(rows, columns=["coin", "start", "o", "h", "l", "c", "usdvol"]))


def _venue_aster(deadline):
    info = get("https://fapi.asterdex.com/fapi/v1/exchangeInfo", tries=3) or {}
    syms = [x["symbol"] for x in info.get("symbols") or [] if x.get("contractType") == "PERPETUAL" and x["symbol"].endswith("USDT")]
    rows = []
    for sym in syms:
        if time.time() > deadline:
            break
        k = get(f"https://fapi.asterdex.com/fapi/v1/klines?symbol={sym}&interval=1d&limit=1500", tries=2) or []
        rows += [(sym, int(x[0]), float(x[1]), float(x[2]), float(x[3]), float(x[4]), float(x[7])) for x in k if isinstance(x, list)]
        time.sleep(0.2)
    print(f"  aster: {len(syms)} perps, {len(rows)} candles", flush=True)
    save("wickscale_aster_1d.parquet", pd.DataFrame(rows, columns=["coin", "t", "o", "h", "l", "c", "qvol"]))


def _venue_lighter(deadline):
    base = "https://mainnet.zklighter.elliot.ai/api/v1"
    st, raw = _raw_get(base + "/orderBooks", timeout=30)
    ids = {}
    try:
        for ob in json.loads(raw.decode()).get("order_books", []):
            ids[str(ob.get("symbol", "")).upper()] = ob.get("market_id")
    except Exception as e:  # noqa: BLE001
        print(f"  lighter orderBooks HTTP {st} {e} {raw[:200] if raw else b''}", flush=True)
    end = 1793491200
    lrows = []
    for c in BATCHZ_COINS:
        mid = ids.get(c)
        if mid is None:
            print(f"  lighter {c}: no market id", flush=True)
            continue
        n, e = 0, end
        for _ in range(40):
            d, st = [], None
            for attempt in range(5):  # back off on HTTP 429 (three coins were refused on the first run)
                st, raw = _raw_get(f"{base}/fundings?market_id={mid}&resolution=1h&start_timestamp={e - 500 * 3600}&end_timestamp={e}&count_back=500", timeout=30)
                if st != 429:
                    break
                time.sleep(10 * (attempt + 1))
            try:
                d = json.loads(raw.decode()).get("fundings", []) if raw else []
            except Exception:  # noqa: BLE001
                d = []
            if not d:
                if n == 0:
                    print(f"  lighter {c}: HTTP {st} {raw[:160] if raw else b''}", flush=True)
                break
            for x in d:
                ts = int(x.get("timestamp", 0))
                ts = ts // 1000 if ts > 10**11 else ts
                lrows.append((c, ts, str(x.get("rate", x.get("value", ""))), str(x.get("direction", "")), json.dumps(x)[:300]))
            n += len(d)
            e -= 500 * 3600
            time.sleep(0.6)
        print(f"  lighter {c}: {n} points", flush=True)
    # raw values kept as text with the API's own direction field; units and sign are decided in the analysis (PREREG addendum 1)
    save("batchz_lighter_raw.parquet", pd.DataFrame(lrows, columns=["coin", "t", "rate_raw", "direction", "json"]).drop_duplicates(["coin", "t"]))
    rows = [r for r in rows if r[0] != "lighter"]
    df = pd.DataFrame(rows, columns=["venue", "coin", "t", "rate"]).drop_duplicates(["venue", "coin", "t"])
    save("batchz_funding.parquet", df)

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
    ob = get(f"{base}/orderBooks", tries=3) or {}
    mk = [(m.get("market_id"), m.get("symbol")) for m in ob.get("order_books") or [] if m.get("market_id") is not None]
    now = int(time.time())
    rows, probe = [], {}
    for mid, sym in mk:
        if time.time() > deadline:
            break
        got = None
        for u in (f"{base}/candlesticks?market_id={mid}&resolution=1d&start_timestamp={now - 900 * 86400}&end_timestamp={now}&count_back=900",
                  f"{base}/candlesticks?market_id={mid}&resolution=1d&start_timestamp={(now - 900 * 86400) * 1000}&end_timestamp={now * 1000}&count_back=900"):
            st, d = req(u, timeout=40)
            probe.setdefault(u.split("?")[1][:40], st)
            cs = (d or {}).get("candlesticks") if isinstance(d, dict) else None
            if cs:
                got = cs
                break
        for x in got or []:
            rows.append((sym, int(x.get("timestamp") or x.get("t") or 0), float(x.get("open") or 0), float(x.get("high") or 0),
                         float(x.get("low") or 0), float(x.get("close") or 0), float(x.get("volume1") or x.get("quote_volume") or 0)))
        time.sleep(0.2)
    print(f"  lighter: {len(mk)} markets, {len(rows)} candles; probe {probe}", flush=True)
    save("wickscale_lighter_1d.parquet", pd.DataFrame(rows, columns=["coin", "t", "o", "h", "l", "c", "qvol"]))


def _venue_paradex(deadline):
    base = "https://api.prod.paradex.trade/v1"
    mk = [m["symbol"] for m in ((get(f"{base}/markets", tries=3) or {}).get("results") or []) if str(m.get("asset_kind")) == "PERP"]
    now = int(time.time() * 1000)
    rows, probe = [], {}
    for sym in mk:
        if time.time() > deadline:
            break
        st, d = req(f"{base}/markets/klines?symbol={sym}&resolution=1D&start_at={now - 1000 * 86400 * 1000}&end_at={now}", timeout=40)
        probe[st] = probe.get(st, 0) + 1
        for x in (d or {}).get("results") or [] if isinstance(d, dict) else []:
            if isinstance(x, list) and len(x) >= 6:
                rows.append((sym, int(x[0]), float(x[1]), float(x[2]), float(x[3]), float(x[4]), float(x[5])))
        time.sleep(0.25)
    print(f"  paradex: {len(mk)} perps, {len(rows)} candles; status counts {probe}", flush=True)
    save("wickscale_paradex_1d.parquet", pd.DataFrame(rows, columns=["coin", "t", "o", "h", "l", "c", "vol"]))


def job_uscale():
    import numpy as _np  # noqa: F401
    t0 = time.time()
    for name, fn in (("terms", _venue_terms), ("dydx", lambda: _venue_dydx(time.time() + 20 * 60)),
                     ("aster", lambda: _venue_aster(time.time() + 15 * 60)), ("lighter", lambda: _venue_lighter(time.time() + 10 * 60)),
                     ("paradex", lambda: _venue_paradex(time.time() + 10 * 60)), ("hl_1h", _scale_hl_1h),
                     ("binance_1h", lambda: _scale_binance_1h(time.time() + 80 * 60))):
        print(f"== uscale {name} ({time.time() - t0:.0f}s)", flush=True)
        _safe(fn)()


# ---------------------------------------------------------------- #405-#409 (docs/PREREG_FIVE_HIGH_20261125.md)
def _bn_archive_lister():
    import xml.etree.ElementTree as ET
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
    return s3_list


def _bn_zip_rows(key):
    import io
    import zipfile
    try:
        with urllib.request.urlopen(urllib.request.Request("https://data.binance.vision/" + urllib.parse.quote(key), headers=UA), timeout=60) as r:
            z = zipfile.ZipFile(io.BytesIO(r.read()))
            txt = z.read(z.namelist()[0]).decode()
    except Exception:  # noqa: BLE001
        return []
    out = []
    for ln in txt.splitlines():
        f = ln.split(",")
        if f and f[0].strip().isdigit():
            ts = int(f[0])
            out.append([ts // 1000 if ts > 10**14 else ts] + f[1:])
    return out


def _five_bn_premium(deadline):
    import concurrent.futures as cf
    s3_list = _bn_archive_lister()
    _, prefs = s3_list("data/futures/um/monthly/premiumIndexKlines/")
    syms = sorted({p.rstrip("/").split("/")[-1] for p in prefs})
    syms = [x for x in syms if x.endswith("USDT") and "_" not in x]
    print(f"  premium-index symbols: {len(syms)}", flush=True)

    def one(sym):
        if time.time() > deadline:
            return []
        pk, _ = s3_list(f"data/futures/um/monthly/premiumIndexKlines/{sym}/1h/", delimiter=False)
        kk, _ = s3_list(f"data/futures/um/monthly/klines/{sym}/1h/", delimiter=False)
        mth = lambda k: k.split("-1h-")[-1][:7]  # noqa: E731
        pr, kr = [], []
        for k in pk:
            if k.endswith(".zip") and "2022-01" <= mth(k) <= "2026-10":
                pr += _bn_zip_rows(k)
        for k in kk:
            if k.endswith(".zip") and "2022-01" <= mth(k) <= "2026-10":
                kr += _bn_zip_rows(k)
        if not pr or not kr:
            return []
        P = pd.DataFrame([(r[0] // 1000, float(r[4])) for r in pr], columns=["t", "prem"]).drop_duplicates("t").set_index("t")
        K = pd.DataFrame([(r[0] // 1000, float(r[4]), float(r[7])) for r in kr], columns=["t", "c", "qv"]).drop_duplicates("t").set_index("t")
        d = K.join(P, how="inner").sort_index()
        d["day"] = d.index // 86400
        pvol = d.groupby("day")["qv"].sum().shift()
        d["pvol"] = d["day"].map(pvol)
        ts, c, pm, pv = d.index.to_numpy(), d["c"].to_numpy(), d["prem"].to_numpy(), d["pvol"].to_numpy()
        out = []
        for P_ in (0.005, 0.01, 0.02):
            i, n = 0, len(d)
            while i < n:
                if pm[i] <= -P_ and pv[i] == pv[i] and pv[i] > 0:
                    j = i + 1
                    while j < n and j - i < 24 and pm[j] < -0.001:
                        j += 1
                    j = min(j, n - 1)
                    if j > i:
                        out.append((sym, int(ts[i]), P_, float(c[j] / c[i] - 1 - 2 * 0.00045), float(min(1500.0, 0.01 * pv[i])), int(j - i)))
                    i = j + 1
                else:
                    i += 1
        return out

    def safe(sym):
        try:
            return one(sym)
        except Exception as e:  # noqa: BLE001
            print(f"  {sym}: {type(e).__name__} {str(e)[:60]}", flush=True)
            return []

    allt, t0 = [], time.time()
    with cf.ThreadPoolExecutor(16) as ex:
        for i, r in enumerate(ex.map(safe, syms)):
            allt += r
            if i % 100 == 0:
                print(f"  {i}/{len(syms)} symbols, {len(allt)} trades, {time.time() - t0:.0f}s", flush=True)
    save("fivehigh_bn_premium_trades.parquet", pd.DataFrame(allt, columns=["sym", "t", "P", "ret", "size", "hours"]))


def _five_hl_premium(deadline):
    meta = get(HL, {"type": "meta"}) or {}
    now = int(time.time() * 1000)
    rows = []
    for u in meta.get("universe") or []:
        if u.get("isDelisted"):
            continue
        t = now - 120 * 86400 * 1000
        while t < now and time.time() < deadline:
            f = get(HL, {"type": "fundingHistory", "coin": u["name"], "startTime": t, "endTime": now}) or []
            rows += [(u["name"], int(x["time"]), float(x["fundingRate"]), float(x.get("premium") or 0)) for x in f]
            if len(f) < 500:
                break
            t = int(f[-1]["time"]) + 1
            time.sleep(1.05)
        time.sleep(1.05)
    save("fivehigh_hl_premium.parquet", pd.DataFrame(rows, columns=["coin", "t", "rate", "premium"]))


def _five_hl_spot():
    sm = get(HL, {"type": "spotMeta"}) or {}
    toks = {t["index"]: t["name"] for t in sm.get("tokens") or []}
    pairs = [(p["name"], "/".join(toks.get(i, str(i)) for i in p.get("tokens", []))) for p in sm.get("universe") or []]
    now = int(time.time() * 1000)
    rows = []
    for name, label in pairs:
        c = get(HL, {"type": "candleSnapshot", "req": {"coin": name, "interval": "1d", "startTime": 1672531200000, "endTime": now}}) or []
        rows += [(name, label, int(x["t"]), float(x["o"]), float(x["h"]), float(x["l"]), float(x["c"]), float(x["v"])) for x in c]
        time.sleep(1.05)
    print(f"  HL spot pairs: {len(pairs)}, candles {len(rows)}", flush=True)
    save("fivehigh_hl_spot_1d.parquet", pd.DataFrame(rows, columns=["pair", "label", "t", "o", "h", "l", "c", "v"]))


def _five_venues_1h(deadline_each):
    hlm = {u["name"] for u in (get(HL, {"type": "meta"}) or {}).get("universe") or [] if not u.get("isDelisted")}
    now = int(time.time())
    rows = []
    # Aster (Binance-style): 1500 1h candles per call, two pages = ~120 days
    dl = time.time() + deadline_each
    info = get("https://fapi.asterdex.com/fapi/v1/exchangeInfo", tries=3) or {}
    for x in info.get("symbols") or []:
        sym = x["symbol"]
        coin = sym[:-4] if sym.endswith("USDT") else None
        if not coin or coin not in hlm or time.time() > dl:
            continue
        end = None
        for _ in range(2):
            k = get(f"https://fapi.asterdex.com/fapi/v1/klines?symbol={sym}&interval=1h&limit=1500" + (f"&endTime={end}" if end else ""), tries=2) or []
            rows += [("aster", coin, int(r[0]) // 1000, float(r[4])) for r in k if isinstance(r, list)]
            if len(k) < 1500:
                break
            end = int(k[0][0]) - 1
            time.sleep(0.2)
    # Lighter
    dl = time.time() + deadline_each
    base = "https://mainnet.zklighter.elliot.ai/api/v1"
    for m in (get(f"{base}/orderBooks", tries=3) or {}).get("order_books") or []:
        coin = m.get("symbol")
        if coin not in hlm or time.time() > dl:
            continue
        st, d = req(f"{base}/candlesticks?market_id={m['market_id']}&resolution=1h&start_timestamp={now - 120 * 86400}&end_timestamp={now}&count_back=2900", timeout=40)
        for x in ((d or {}).get("candlesticks") or []) if isinstance(d, dict) else []:
            t = int(x.get("timestamp") or 0)
            rows.append(("lighter", coin, t // 1000 if t > 1e12 else t, float(x.get("close") or 0)))
        time.sleep(0.2)
    # Paradex
    dl = time.time() + deadline_each
    pbase = "https://api.prod.paradex.trade/v1"
    for m in (get(f"{pbase}/markets", tries=3) or {}).get("results") or []:
        if str(m.get("asset_kind")) != "PERP":
            continue
        coin = m["symbol"].split("-")[0]
        if coin not in hlm or time.time() > dl:
            continue
        st, d = req(f"{pbase}/markets/klines?symbol={m['symbol']}&resolution=60&start_at={(now - 120 * 86400) * 1000}&end_at={now * 1000}", timeout=40)
        for x in ((d or {}).get("results") or []) if isinstance(d, dict) else []:
            if isinstance(x, list) and len(x) >= 5:
                rows.append(("paradex", coin, int(x[0]) // 1000, float(x[4])))
        time.sleep(0.25)
    # dYdX (100 candles per call): HL coins only, ~60 days
    dl = time.time() + deadline_each
    for tk in (get("https://indexer.dydx.trade/v4/perpetualMarkets", tries=3) or {}).get("markets") or {}:
        coin = tk.split("-")[0]
        if coin not in hlm or time.time() > dl:
            continue
        to = None
        for _ in range(15):
            c = (get(f"https://indexer.dydx.trade/v4/candles/perpetualMarkets/{tk}?resolution=1HOUR&limit=100" + (f"&toISO={to}" if to else ""), tries=2) or {}).get("candles") or []
            rows += [("dydx", coin, int(pd.Timestamp(x["startedAt"]).timestamp()), float(x["close"])) for x in c]
            if len(c) < 100:
                break
            to = min(x["startedAt"] for x in c)
            time.sleep(0.12)
    # Hyperliquid 1h closes for the same coins (last ~120 days)
    dl = time.time() + deadline_each
    for coin in sorted(hlm):
        if time.time() > dl:
            break
        c = get(HL, {"type": "candleSnapshot", "req": {"coin": coin, "interval": "1h", "startTime": (now - 120 * 86400) * 1000, "endTime": now * 1000}}) or []
        rows += [("hyperliquid", coin, int(x["t"]) // 1000, float(x["c"])) for x in c]
        time.sleep(1.05)
    d = pd.DataFrame(rows, columns=["venue", "coin", "t", "c"])
    print(f"  venue 1h closes: {d.groupby('venue').size().to_dict() if len(d) else {}}", flush=True)
    save("fivehigh_venues_1h.parquet", d)


def job_ufive():
    t0 = time.time()
    for name, fn in (("hl_spot", _five_hl_spot), ("venues_1h", lambda: _five_venues_1h(12 * 60)),
                     ("hl_premium", lambda: _five_hl_premium(time.time() + 30 * 60)),
                     ("bn_premium", lambda: _five_bn_premium(time.time() + 100 * 60))):
        print(f"== ufive {name} ({time.time() - t0:.0f}s)", flush=True)
        _safe(fn)()


def job_uhip3():
    """#411: daily candles for every market on every HIP-3 perp dex."""
    dexes = get(HL, {"type": "perpDexs"}) or []
    names = [d.get("name") for d in dexes if isinstance(d, dict) and d.get("name")]
    print(f"  HIP-3 dexes: {names}", flush=True)
    now = int(time.time() * 1000)
    rows = []
    for dx in names:
        m = get(HL, {"type": "meta", "dex": dx}) or {}
        for u in m.get("universe") or []:
            c = get(HL, {"type": "candleSnapshot", "req": {"coin": u["name"], "interval": "1d", "startTime": 1704067200000, "endTime": now}}) or []
            rows += [(dx, u["name"], int(x["t"]), float(x["o"]), float(x["h"]), float(x["l"]), float(x["c"]), float(x["v"])) for x in c]
            time.sleep(1.05)
    print(f"  HIP-3 candles: {len(rows)}", flush=True)
    save("fivehigh_hip3_1d.parquet", pd.DataFrame(rows, columns=["dex", "coin", "t", "o", "h", "l", "c", "v"]))


def job_uw3b():
    """Wave-3 Stage 2 data: Binance announcements (48) back to 2020; complete Upbit + Bithumb KRW first-candle dates."""
    stop = int(pd.Timestamp("2020-01-01", tz="UTC").timestamp() * 1000)
    items = []
    for p in range(1, 400):
        st, d = req(f"https://www.binance.com/bapi/composite/v1/public/cms/article/list/query?type=1&pageNo={p}&pageSize=50&catalogId=48", timeout=40)
        lst = _items((d or {}).get("data")) if isinstance(d, dict) else []
        if st != 200 or not lst:
            break
        items += [{"title": x.get("title"), "releaseDate": x.get("releaseDate"), "code": x.get("code")} for x in lst]
        if min(int(x.get("releaseDate") or 0) for x in lst) < stop:
            break
        time.sleep(0.6)
    print(f"  binance catalog 48 back to 2020: {len(items)} items", flush=True)
    save("uncharted_w3b_binance48.json", items)
    _w3_korea(time.time() + 75 * 60, out_name="uncharted_w3b_korea.parquet")


def job_udistinct():
    """#412 Upbit daily candles (all KRW markets) and #413 DefiLlama hourly prices."""
    mk = get("https://api.upbit.com/v1/market/all?isDetails=false", tries=3) or []
    krw = [m["market"] for m in mk if str(m.get("market", "")).startswith("KRW-")]
    rows, dl = [], time.time() + 60 * 60
    for m in krw:
        if time.time() > dl:
            print("  upbit: time cap", flush=True)
            break
        to = None
        for _ in range(12):
            d = get(f"https://api.upbit.com/v1/candles/days?market={m}&count=200" + (f"&to={urllib.parse.quote(to)}" if to else ""), tries=2, pause=1) or []
            if not isinstance(d, list) or not d:
                break
            rows += [(m[4:], x["candle_date_time_utc"][:10], float(x["trade_price"]), float(x.get("candle_acc_trade_price") or 0)) for x in d]
            if len(d) < 200 or min(x["candle_date_time_utc"] for x in d) < "2019-12-01":
                break
            to = min(x["candle_date_time_utc"] for x in d).replace("T", " ")
            time.sleep(0.12)
        time.sleep(0.1)
    print(f"  upbit KRW markets {len(krw)}, candles {len(rows)}", flush=True)
    save("distinct_upbit_1d.parquet", pd.DataFrame(rows, columns=["coin", "day", "krw_close", "krw_value"]))
    ids = ["kinetic-staked-hype", "staked-hype", "hyperbeat-x-ether-fi-hype", "renzo-restaked-eth", "kelp-dao-restaked-eth", "wrapped-eeth",
           "pufeth", "ethena-staked-usde", "hyperliquid", "ethereum", "ethena-usde"]
    prow = []
    for g in ids:
        t = T0_2024
        while t < time.time():
            d = get(f"https://coins.llama.fi/chart/coingecko:{g}?start={t}&span=500&period=1h", tries=2)
            pts = (((d or {}).get("coins") or {}).get(f"coingecko:{g}") or {}).get("prices") or []
            prow += [(g, int(x["timestamp"]), float(x["price"])) for x in pts]
            t += 500 * 3600
            time.sleep(0.25)
        print(f"  llama hourly {g}: {sum(1 for r in prow if r[0] == g)} points", flush=True)
    save("distinct_llama_1h.parquet", pd.DataFrame(prow, columns=["id", "t", "price"]))


def job_unav():
    """#415: hourly DefiLlama prices for LST contract addresses (protocol-rate NAV) and their CoinGecko market prices."""
    keys = ["ethereum:0xcd5fe23c85820f7b72d0926fc9b05b43e359b7ee", "ethereum:0x9d39a5de30e57443bff2a8307a4256c8797a3497",
            "ethereum:0xd9a442856c234a39a81a089c06451ebaa4306a72", "ethereum:0xa1290d69c65a6fe4df752f95823fae25cb99e5a7",
            "coingecko:wrapped-eeth", "coingecko:ethena-staked-usde", "coingecko:pufeth", "coingecko:kelp-dao-restaked-eth",
            "coingecko:ethereum", "coingecko:ethena-usde"]
    rows = []
    for k in keys:
        t = T0_2024
        while t < time.time():
            d = get(f"https://coins.llama.fi/chart/{k}?start={t}&span=500&period=1h", tries=2)
            pts = (((d or {}).get("coins") or {}).get(k) or {}).get("prices") or []
            rows += [(k, int(x["timestamp"]), float(x["price"])) for x in pts]
            t += 500 * 3600
            time.sleep(0.25)
        print(f"  {k}: {sum(1 for r in rows if r[0] == k)} points", flush=True)
    save("distinct_nav_1h.parquet", pd.DataFrame(rows, columns=["key", "t", "price"]))


def job_udln():
    """#417: deBridge DLN fulfilled orders (public API), newest first, back to 2024-01 (time-capped)."""
    hosts = ["https://dln-api.debridge.finance", "https://stats-api.dln.trade"]
    body = {"skip": 0, "take": 100, "orderStates": ["Fulfilled", "SentUnlock", "ClaimedUnlock"], "externalCallStates": ["NoExtCall"]}
    host, probe = None, {}
    for h in hosts:
        st, d = req(h + "/api/Orders/filteredList", body, timeout=60)
        probe[h] = {"status": st, "head": (json.dumps(d)[:1500] if d is not None else None)}
        print(f"  probe {h}: {st} {(json.dumps(d)[:300] if d is not None else '')}", flush=True)
        if st == 200 and isinstance(d, dict) and (d.get("orders") or d.get("data")):
            host = h
            break
    save("solvers_dln_probe.json", probe)
    if not host:
        return
    stop = int(pd.Timestamp("2024-01-01", tz="UTC").timestamp())
    out, skip, dl = [], 0, time.time() + 150 * 60
    while time.time() < dl:
        b = dict(body, skip=skip)
        d = get(host + "/api/Orders/filteredList", b, tries=3, timeout=60) or {}
        lst = d.get("orders") or d.get("data") or []
        if not lst:
            break
        out += lst
        skip += len(lst)
        ts = [x.get("creationTimestamp") or (x.get("createdSrcEventMetadata") or {}).get("blockTimeStamp") for x in lst]
        ts = [int(t) for t in ts if isinstance(t, (int, float))]
        if ts and min(ts) < stop:
            break
        if skip % 20000 == 0:
            print(f"    {skip} orders, oldest {pd.Timestamp(min(ts), unit='s') if ts else None}", flush=True)
        time.sleep(0.3)
    print(f"  DLN orders fetched: {len(out)}", flush=True)
    import gzip
    OUT.mkdir(parents=True, exist_ok=True)
    with gzip.open(OUT / "solvers_dln_orders.json.gz", "wt") as f:
        json.dump(out, f)
    print(f"  wrote solvers_dln_orders.json.gz: {(OUT / 'solvers_dln_orders.json.gz').stat().st_size} bytes", flush=True)


def job_udln2():
    """#417 addendum: sampled blocks of DLN orders at evenly spaced offsets back to 2024 + daily prices of the major tokens."""
    import gzip
    host = "https://dln-api.debridge.finance"
    body = {"take": 100, "orderStates": ["Fulfilled", "SentUnlock", "ClaimedUnlock"], "externalCallStates": ["NoExtCall"]}
    stop = int(pd.Timestamp("2024-01-01", tz="UTC").timestamp())
    out, off, dl = [], 0, time.time() + 170 * 60
    while time.time() < dl:
        blk = []
        for k in range(20):
            d = get(host + "/api/Orders/filteredList", dict(body, skip=off + 100 * k), tries=3, timeout=90) or {}
            lst = d.get("orders") or []
            if not lst:
                break
            blk += lst
            time.sleep(0.25)
        if not blk:
            print(f"  offset {off}: empty -> end", flush=True)
            break
        for x in blk:
            x["_offset"] = off
        out += blk
        oldest = min(int(x.get("creationTimestamp") or 0) for x in blk)
        print(f"  offset {off}: {len(blk)} orders, oldest {pd.Timestamp(oldest, unit='s')}", flush=True)
        if oldest < stop:
            break
        off += 25000
    OUT.mkdir(parents=True, exist_ok=True)
    with gzip.open(OUT / "solvers_dln_sample.json.gz", "wt") as f:
        json.dump(out, f)
    print(f"  sampled orders: {len(out)}", flush=True)
    prow = []
    for g in ("ethereum", "binancecoin", "solana", "bitcoin", "matic-network", "polygon-ecosystem-token", "avalanche-2"):
        prow += [{"id": g, "t": int(x["timestamp"]), "price": float(x["price"])}
                 for x in llama_chart(f"coingecko:{g}", int(pd.Timestamp("2023-12-15", tz="UTC").timestamp()))]
    save("solvers_dln_prices.parquet", pd.DataFrame(prow))


def job_urates():
    """#421 re-fetch: daily on-chain LST rates only."""
    job_ubatcha(rates_only=True)


def job_ubatcha(rates_only=False):
    """Batch A data: #419 Deribit DVOL + Derive terms; #420 dYdX reward/fee probes; #421 on-chain LST rates (archive eth_call)."""
    out = {}
    if rates_only:
        return _ubatcha_rates()
    # 419
    for cur in ("BTC", "ETH"):
        rows, t = [], int(pd.Timestamp("2021-03-01", tz="UTC").timestamp() * 1000)
        end = int(time.time() * 1000)
        while t < end:
            d = get(f"https://www.deribit.com/api/v2/public/get_volatility_index_data?currency={cur}&start_timestamp={t}"
                    f"&end_timestamp={min(end, t + 900 * 86400000)}&resolution=1D", tries=3) or {}
            data = ((d.get("result") or {}).get("data")) or []
            rows += data
            t += 900 * 86400000
            time.sleep(0.5)
        out[f"dvol_{cur}"] = rows
        print(f"  DVOL {cur}: {len(rows)} days", flush=True)
    out["derive_terms"] = {}
    for u in ("https://www.derive.xyz/terms-of-use", "https://docs.derive.xyz/docs/terms-of-use", "https://www.derive.xyz/terms"):
        st, h = _html(u)
        txt = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", h))
        out["derive_terms"][u] = {"status": st, "chars": len(txt), "Malaysia": [txt[max(0, m.start() - 300): m.start() + 300] for m in re.finditer("Malaysia", txt)][:3],
                                  "restricted": [txt[max(0, m.start() - 200): m.start() + 500] for m in re.finditer(r"[Rr]estricted (Jurisdiction|Territor|Countr)", txt)][:3]}
        print(f"  derive terms {st} {len(txt)} chars {u}", flush=True)
    # 420 probes
    out["dydx_probe"] = {}
    for u in ("https://indexer.dydx.trade/v4/historicalTradingRewardAggregations/dydx1qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq?period=MONTHLY",
              "https://indexer.dydx.trade/v4/perpetualMarkets", "https://api.llama.fi/summary/fees/dydx-v4?dataType=dailyFees",
              "https://api.llama.fi/summary/derivatives/dydx-v4", "https://api.llama.fi/summary/fees/dydx?dataType=dailyFees"):
        st, d = req(u, timeout=40)
        out["dydx_probe"][u] = {"status": st, "head": (json.dumps(d)[:2000] if d is not None else None)}
        print(f"  dydx probe {st} {u[:90]}", flush=True)
    save("batcha_raw.json", out)
    _ubatcha_rates()


def _ubatcha_rates():
    # 421 on-chain rates
    calls = {"weETH": ("0xcd5fe23c85820f7b72d0926fc9b05b43e359b7ee", "0x679aefce"),
             "sUSDe": ("0x9d39a5de30e57443bff2a8307a4256c8797a3497", "0x07a2d13a" + hex(10**18)[2:].rjust(64, "0")),
             "pufETH": ("0xd9a442856c234a39a81a089c06451ebaa4306a72", "0x07a2d13a" + hex(10**18)[2:].rjust(64, "0")),
             "rsETH": ("0x349a73444b1a310bae67ef67973022020d70020d", "0xb4b46434")}
    rpcs = ["https://eth.blockscout.com/api/eth-rpc", "https://eth.drpc.org", "https://ethereum-rpc.publicnode.com", "https://eth.llamarpc.com",
            "https://rpc.mevblocker.io", "https://eth.merkle.io", "https://1rpc.io/eth"]
    rows, ok_rpc, dl = [], None, time.time() + 150 * 60
    day = pd.Timestamp("2024-01-01", tz="UTC")
    while day < pd.Timestamp.now(tz="UTC") and time.time() < dl:
        ts = int((day + pd.Timedelta(hours=23, minutes=59)).timestamp())
        # estimated block from a known anchor (block 18,915,996 = 2024-01-01 23:59 UTC; 12-second slots): no per-day lookup
        blk = 18915996 + int((ts - int(pd.Timestamp("2024-01-01 23:59", tz="UTC").timestamp())) / 12)
        if blk:
            for name, (to, data) in calls.items():
                val = None
                for u in ([ok_rpc] if ok_rpc else []) + [r for r in rpcs if r != ok_rpc]:
                    d = get(u, {"jsonrpc": "2.0", "id": 1, "method": "eth_call", "params": [{"to": to, "data": data}, hex(int(blk))]}, tries=1, timeout=30)
                    if d and isinstance(d.get("result"), str) and len(d["result"]) >= 66:
                        val, ok_rpc = int(d["result"][:66], 16) / 1e18, u
                        break
                rows.append({"day": str(day.date()), "token": name, "block": int(blk), "rate": val})
        if day.day == 1:
            print(f"  rates {day.date()}: rpc {ok_rpc}, last {rows[-4:] if rows else None}", flush=True)
        day += pd.Timedelta(days=1)
    save("batcha_rates.parquet", pd.DataFrame(rows))


def job_ubatchb():
    """Batch B data: DefiLlama yield pools/charts for perp-DEX vaults, Liquity v2, HyperLend/HypurrFi; Orderly daily klines."""
    pools = (get("https://yields.llama.fi/pools", tries=3) or {}).get("data") or []
    pat = re.compile(r"lighter|edgex|grvt|aster|paradex|dydx|ostium|avantis|drift|gmx|liquity-v2|hyperlend|hypurrfi", re.I)
    sel = [p for p in pools if pat.search(p.get("project") or "")]
    print(f"  matching yield pools: {len(sel)} ({sorted({p['project'] for p in sel})})", flush=True)
    rows = []
    for p in sel:
        c = get(f"https://yields.llama.fi/chart/{p['pool']}", tries=2)
        rows += [{"pool": p["pool"], "ts": x.get("timestamp"), "tvlUsd": x.get("tvlUsd"), "apy": x.get("apy"), "apyBase": x.get("apyBase")}
                 for x in (c or {}).get("data") or []]
        time.sleep(0.25)
    save("batchb_pools.json", sel)
    save("batchb_charts.parquet", pd.DataFrame(rows))
    base = "https://api-evm.orderly.org"
    info = get(f"{base}/v1/public/info", tries=3) or {}
    syms = [r["symbol"] for r in ((info.get("data") or {}).get("rows") or []) if str(r.get("symbol", "")).startswith("PERP_")]
    print(f"  Orderly perps: {len(syms)}", flush=True)
    krow, now = [], int(time.time())
    for sym in syms:
        d = get(f"{base}/v1/tv/history?symbol={sym}&resolution=1D&from={now - 1100 * 86400}&to={now}", tries=2) or {}
        for t, o, h, l, c, v in zip(d.get("t") or [], d.get("o") or [], d.get("h") or [], d.get("l") or [], d.get("c") or [], d.get("v") or []):
            krow.append((sym, int(t), float(o), float(h), float(l), float(c), float(v)))
        time.sleep(0.2)
    print(f"  Orderly daily candles: {len(krow)}", flush=True)
    save("batchb_orderly_1d.parquet", pd.DataFrame(krow, columns=["coin", "t", "o", "h", "l", "c", "v"]))


def job_ubatchc():
    """Batch C data: hourly stablecoin prices 2020-26 (DefiLlama), Binance maintenance announcements, BTC/ETH 1h klines."""
    ids = ["usd-coin", "tether", "first-digital-usd", "paypal-usd", "true-usd", "binance-usd", "paxos-standard", "dai", "ethena-usde", "frax",
           "crvusd", "gho", "liquity-usd", "usdd", "usual-usd", "usds"]
    rows = []
    for g in ids:
        t = int(pd.Timestamp("2020-01-01", tz="UTC").timestamp())
        while t < time.time():
            d = get(f"https://coins.llama.fi/chart/coingecko:{g}?start={t}&span=500&period=1h", tries=2)
            rows += [(g, int(x["timestamp"]), float(x["price"])) for x in (((d or {}).get("coins") or {}).get(f"coingecko:{g}") or {}).get("prices") or []]
            t += 500 * 3600
            time.sleep(0.2)
        print(f"  {g}: {sum(1 for r in rows if r[0] == g)} hourly points", flush=True)
    save("batchc_stables_1h.parquet", pd.DataFrame(rows, columns=["id", "t", "price"]))
    out = {}
    for cat in (157, 49):
        items = []
        for p in range(1, 120):
            st, d = req(f"https://www.binance.com/bapi/composite/v1/public/cms/article/list/query?type=1&pageNo={p}&pageSize=50&catalogId={cat}", timeout=40)
            lst = _items((d or {}).get("data")) if isinstance(d, dict) else []
            if st != 200 or not lst:
                break
            items += [{"title": x.get("title"), "releaseDate": x.get("releaseDate"), "code": x.get("code")} for x in lst]
            if min(int(x.get("releaseDate") or 0) for x in lst) < int(pd.Timestamp("2023-01-01", tz="UTC").timestamp() * 1000):
                break
            time.sleep(0.5)
        out[str(cat)] = items
        print(f"  binance catalog {cat}: {len(items)}", flush=True)
    save("batchc_binance_ann.json", out)
    import io
    import zipfile
    k = []
    for sym in ("BTCUSDT", "ETHUSDT"):
        for y in range(2020, 2027):
            for m in range(1, 13):
                mth = f"{y}-{m:02d}"
                if mth > "2026-10":
                    continue
                try:
                    with urllib.request.urlopen(urllib.request.Request(f"https://data.binance.vision/data/futures/um/monthly/klines/{sym}/1h/{sym}-1h-{mth}.zip", headers=UA), timeout=60) as r:
                        z = zipfile.ZipFile(io.BytesIO(r.read()))
                        for ln in z.read(z.namelist()[0]).decode().splitlines():
                            f = ln.split(",")
                            if f and f[0].isdigit():
                                ts = int(f[0])
                                k.append((sym, (ts // 1000 if ts > 10**14 else ts) // 1000, float(f[4])))
                except Exception:  # noqa: BLE001
                    pass
        print(f"  {sym} 1h rows: {sum(1 for x in k if x[0] == sym)}", flush=True)
    save("batchc_btceth_1h.parquet", pd.DataFrame(k, columns=["sym", "t", "c"]))


def job_ubatchc2():
    """Batch C extension: Binance 8-hourly funding BTCUSDT/ETHUSDT (archive) first, then Coinbase daily BTC/ETH.
    Re-written 2026-11-26 after the first run hung >2h: each part is saved on its own and has a hard wall-clock cap (SIGALRM)."""
    import io
    import signal
    import zipfile

    class Cap(Exception):
        pass

    def _alarm(*_):
        raise Cap()

    signal.signal(signal.SIGALRM, _alarm)
    fr = []
    for sym in ("BTCUSDT", "ETHUSDT"):
        for y in range(2020, 2027):
            for m in range(1, 13):
                mth = f"{y}-{m:02d}"
                if mth > "2026-10":
                    continue
                signal.alarm(90)
                try:
                    with urllib.request.urlopen(urllib.request.Request(f"https://data.binance.vision/data/futures/um/monthly/fundingRate/{sym}/{sym}-fundingRate-{mth}.zip", headers=UA), timeout=30) as r:
                        z = zipfile.ZipFile(io.BytesIO(r.read()))
                        for ln in z.read(z.namelist()[0]).decode().splitlines():
                            f = ln.split(",")
                            if f and f[0].strip().isdigit():
                                ts = int(f[0])
                                fr.append((sym, (ts // 1000 if ts > 10**14 else ts) // 1000, float(f[-1])))
                except (Exception, Cap):  # noqa: BLE001
                    print(f"  miss {sym} {mth}", flush=True)
                finally:
                    signal.alarm(0)
        print(f"  funding events {sym}: {sum(1 for x in fr if x[0] == sym)}", flush=True)
    save("batchc_funding8h.parquet", pd.DataFrame(fr, columns=["sym", "t", "rate"]))
    rows = []
    for prod in ("BTC-USD", "ETH-USD"):
        t = pd.Timestamp("2020-01-01", tz="UTC")
        while t < pd.Timestamp.now(tz="UTC"):
            e = min(t + pd.Timedelta(days=290), pd.Timestamp.now(tz="UTC"))
            signal.alarm(60)
            try:
                d = get(f"https://api.exchange.coinbase.com/products/{prod}/candles?granularity=86400&start={t.isoformat()}&end={e.isoformat()}", tries=2, timeout=20) or []
            except Cap:
                print(f"  coinbase cap hit {prod} {t.date()}", flush=True)
                d = []
            finally:
                signal.alarm(0)
            rows += [(prod, int(x[0]), float(x[4])) for x in d if isinstance(x, list)]
            t = e
            time.sleep(0.4)
        print(f"  coinbase {prod}: {sum(1 for r in rows if r[0] == prod)} days", flush=True)
    save("batchc_coinbase_1d.parquet", pd.DataFrame(rows, columns=["prod", "t", "c"]))


ALTS_D = ["BTC", "ETH", "SOL", "XRP", "DOGE", "ADA", "AVAX", "LINK", "DOT", "LTC", "BCH", "TRX", "MATIC", "ATOM", "NEAR", "FIL", "ETC",
          "UNI", "AAVE", "XLM", "ALGO", "SAND", "MANA", "AXS", "GALA", "FTM", "CRV", "SUSHI", "1INCH", "COMP", "SNX", "MKR", "YFI", "RUNE",
          "EGLD", "THETA", "ICP", "KSM", "ZEC", "DASH"]
EPOCH_D = ["CRV", "CVX", "BAL", "PENDLE", "AERO", "VELODROME", "THE", "BTC"]


def _bn_month(kind, sym, mth):
    """One Binance USD-M archive month: kind 'k1h' -> [(t, close)], 'fund' -> [(t, rate)]. Hard 60 s wall cap via the socket timeout."""
    import io
    import zipfile
    url = (f"https://data.binance.vision/data/futures/um/monthly/klines/{sym}/1h/{sym}-1h-{mth}.zip" if kind == "k1h"
           else f"https://data.binance.vision/data/futures/um/monthly/fundingRate/{sym}/{sym}-fundingRate-{mth}.zip")
    out = []
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
            z = zipfile.ZipFile(io.BytesIO(r.read()))
            for ln in z.read(z.namelist()[0]).decode().splitlines():
                f = ln.split(",")
                if f and f[0].strip().isdigit():
                    ts = int(f[0])
                    ts = (ts // 1000 if ts > 10**14 else ts) // 1000
                    out.append((ts, float(f[4]) if kind == "k1h" else float(f[-1])))
    except Exception:  # noqa: BLE001
        pass
    return out


def _bn_many(kind, syms, name):
    from concurrent.futures import ThreadPoolExecutor
    tasks = [(s, f"{y}-{m:02d}") for s in syms for y in range(2020, 2027) for m in range(1, 13) if f"{y}-{m:02d}" <= "2026-10"]
    rows = []
    with ThreadPoolExecutor(8) as ex:
        for (s, mth), res in zip(tasks, ex.map(lambda a: _bn_month(kind, a[0], a[1]), tasks)):
            rows += [(s, t, v) for t, v in res]
    df = pd.DataFrame(rows, columns=["sym", "t", "close" if kind == "k1h" else "rate"])
    print(f"  {name}: " + ", ".join(f"{s} {n}" for s, n in df.groupby("sym").size().items()), flush=True)
    save(name, df)


def job_ubatchd():
    """Batch D (docs/PREREG_BATCH_D_20261126.md): FRED CMT yields + Treasury auctions (#446); Binance 1h + funding for ve-epoch
    tokens (#445) and for 40 alts (#440 alt variant). Each part saved on its own."""
    import io
    fred = []
    for sid in ("DGS2", "DGS3", "DGS5", "DGS7", "DGS10", "DGS20", "DGS30"):
        try:
            with urllib.request.urlopen(urllib.request.Request(f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}", headers=UA), timeout=60) as r:
                d = pd.read_csv(io.StringIO(r.read().decode()))
            d.columns = ["date", "y"]
            d["y"] = pd.to_numeric(d["y"], errors="coerce")
            d["sid"] = sid
            fred.append(d.dropna())
            print(f"  fred {sid}: {len(d)}", flush=True)
        except Exception as e:  # noqa: BLE001
            print(f"  fred {sid} FAIL {e}", flush=True)
    if fred:
        save("batchd_fred_cmt.parquet", pd.concat(fred, ignore_index=True))
    auc, page = [], 1
    while page < 40:
        d = get("https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/accounting/od/auctions_query"
                f"?filter=auction_date:gte:2008-06-01&page[size]=1000&page[number]={page}", tries=3, timeout=60)
        lst = (d or {}).get("data") or []
        auc += lst
        if len(lst) < 1000:
            break
        page += 1
    print(f"  treasury auctions: {len(auc)}", flush=True)
    if auc:
        save("batchd_auctions.parquet", pd.DataFrame(auc).astype(str))
    _bn_many("k1h", [f"{s}USDT" for s in EPOCH_D], "batchd_epoch_1h.parquet")
    _bn_many("fund", [f"{s}USDT" for s in EPOCH_D], "batchd_epoch_funding.parquet")
    _bn_many("k1h", [f"{s}USDT" for s in ALTS_D], "batchd_alts_1h.parquet")
    _bn_many("fund", [f"{s}USDT" for s in ALTS_D], "batchd_alts_funding.parquet")


def job_ucb442():
    """#442 data only: Coinbase daily candles BTC-USD/ETH-USD with unix-second windows (the ISO '+00:00' form of ubatchc2 hung)."""
    rows = []
    for prod in ("BTC-USD", "ETH-USD"):
        t = int(pd.Timestamp("2020-01-01", tz="UTC").timestamp())
        while t < time.time():
            c = get(f"https://api.exchange.coinbase.com/products/{prod}/candles?granularity=86400&start={t}&end={t + 299 * 86400}", tries=2, timeout=20)
            rows += [(prod, int(x[0]), float(x[4])) for x in (c or []) if isinstance(x, list)]
            t += 299 * 86400
            time.sleep(0.4)
        print(f"  coinbase {prod}: {sum(1 for r in rows if r[0] == prod)} days", flush=True)
    save("batchc_coinbase_1d.parquet", pd.DataFrame(rows, columns=["prod", "t", "c"]))


def job_upendle():
    """#447 (docs/PREREG_BATCH_E_20261126.md): all Pendle markets expiring >= 2024-03-01, daily history; underlying daily USD prices."""
    chainmap = {1: "ethereum", 42161: "arbitrum", 8453: "base", 56: "bsc", 146: "sonic", 999: "hyperliquid", 9745: "plasma",
                5000: "mantle", 80094: "berachain", 10: "optimism"}
    chains = (get("https://api-v2.pendle.finance/core/v1/chains", timeout=30) or {}).get("chainIds", []) or list(chainmap)
    mk = []
    for cid in chains:
        for kind in ("active", "inactive"):
            for m in (get(f"https://api-v2.pendle.finance/core/v1/{cid}/markets/{kind}", timeout=30) or {}).get("markets", []):
                if pd.Timestamp(m["expiry"]) >= pd.Timestamp("2024-03-01", tz="UTC"):
                    mk.append({"chain": cid, "kind": kind, "name": m.get("name"), "address": m["address"], "expiry": m["expiry"],
                               "underlying": m.get("underlyingAsset"), "pt": m.get("pt")})
    print(f"  pendle markets expiring >= 2024-03: {len(mk)}", flush=True)
    save("batche_pendle_markets.parquet", pd.DataFrame(mk).astype(str))
    rows, t0 = [], time.time()
    for i, m in enumerate(mk):
        if time.time() - t0 > 3 * 3600:
            print("  history time cap hit", flush=True)
            break
        d = None
        for u in (f"https://api-v2.pendle.finance/core/v2/{m['chain']}/markets/{m['address']}/historical-data?time_frame=day",
                  f"https://api-v2.pendle.finance/core/v1/{m['chain']}/markets/{m['address']}/historical-data?time_frame=day"):
            d = get(u, tries=2, timeout=30)
            if d:
                break
        if not d:
            continue
        res = d.get("results") if isinstance(d, dict) else d
        keys = ("timestamp", "impliedApy", "underlyingApy", "tvl", "ptPrice", "liquidity")
        if isinstance(res, list):
            for r in res:
                rows.append({"address": m["address"], **{k: r.get(k) for k in keys}})
        elif isinstance(d, dict) and "timestamp" in d:
            n = len(d["timestamp"])
            for j in range(n):
                rows.append({"address": m["address"], **{k: (d[k][j] if isinstance(d.get(k), list) and len(d[k]) == n else None) for k in keys}})
        if i % 100 == 0:
            print(f"  history {i}/{len(mk)} rows {len(rows)}", flush=True)
        time.sleep(0.25)
    h = pd.DataFrame(rows)
    for c in ("impliedApy", "underlyingApy", "tvl", "ptPrice", "liquidity"):
        if c in h:
            h[c] = pd.to_numeric(h[c], errors="coerce")
    h["timestamp"] = h["timestamp"].astype(str)
    save("batche_pendle_history.parquet", h)
    px, seen = [], set()
    for m in mk:
        slug, ua = chainmap.get(int(m["chain"])), str(m.get("underlying") or "")
        addr = ua.split("-")[-1] if "-" in ua else ua
        if not slug or not addr.startswith("0x") or (slug, addr) in seen:
            continue
        seen.add((slug, addr))
        t = int(pd.Timestamp("2024-01-01", tz="UTC").timestamp())
        while t < time.time():
            d = get(f"https://coins.llama.fi/chart/{slug}:{addr}?start={t}&span=500&period=1d", tries=2, timeout=30)
            px += [(slug, addr, int(x["timestamp"]), float(x["price"])) for x in (((d or {}).get("coins") or {}).get(f"{slug}:{addr}") or {}).get("prices") or []]
            t += 500 * 86400
            time.sleep(0.15)
    print(f"  underlying price points: {len(px)} for {len(seen)} assets", flush=True)
    save("batche_underlying_1d.parquet", pd.DataFrame(px, columns=["chain_slug", "underlying", "t", "price"]))


BROWSER = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
           "Accept": "text/html,application/json,*/*"}


def _raw_get(url, timeout=40, headers=None):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={**BROWSER, **(headers or {})}), timeout=timeout) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, b""
    except Exception:  # noqa: BLE001
        return None, b""


def job_ubatchf():
    """Batch F (#448, #449): DefiLlama total stablecoin supply; Farside BTC/ETH ETF flow tables (raw HTML)."""
    d = get("https://stablecoins.llama.fi/stablecoincharts/all", tries=3, timeout=60) or []
    rows = [(int(x["date"]), float(((x.get("totalCirculatingUSD") or {}).get("peggedUSD")) or 0)) for x in d if isinstance(x, dict)]
    print(f"  stablecoin supply days: {len(rows)}", flush=True)
    save("batchf_stable_supply.parquet", pd.DataFrame(rows, columns=["t", "supply"]))
    for name, url in (("btc", "https://farside.co.uk/bitcoin-etf-flow-all-data/"), ("eth", "https://farside.co.uk/ethereum-etf-flow-all-data/")):
        st, raw = _raw_get(url, timeout=60)
        print(f"  farside {name}: HTTP {st}, {len(raw)} bytes", flush=True)
        if raw:
            OUT.mkdir(parents=True, exist_ok=True)
            (OUT / f"batchf_farside_{name}.html").write_bytes(raw)


def job_ubatchf2():
    """Batch F #453: Dukascopy USDJPY ticks, hours 00 and 01 UTC, every weekday 2012-01..2026-10 -> per-day mids at 00:00, 00:55, 02:00."""
    import lzma
    import struct
    from concurrent.futures import ThreadPoolExecutor

    def hour(day, h):
        st, raw = _raw_get(f"https://datafeed.dukascopy.com/datafeed/USDJPY/{day.year}/{day.month - 1:02d}/{day.day:02d}/{h:02d}h_ticks.bi5", timeout=30)
        if st != 200 or not raw:
            return []
        try:
            b = lzma.decompress(raw)
        except Exception:  # noqa: BLE001
            return []
        out = []
        for i in range(0, len(b) - 19, 20):
            ms, ask, bid, _, _ = struct.unpack(">IIIff", b[i:i + 20])
            out.append((h * 3600 + ms / 1000.0, (ask + bid) / 2 / 1000.0))
        return out

    def one(day):
        ticks = hour(day, 0) + hour(day, 1)
        if not ticks:
            return None
        first = next((p for s, p in ticks if s >= 0), None)
        at55 = [p for s, p in ticks if s < 55 * 60]
        end = [p for s, p in ticks if s < 7200]
        return (day.strftime("%Y-%m-%d"), first, at55[-1] if at55 else None, end[-1] if end else None, len(ticks))

    days = [d for d in pd.date_range("2012-01-02", "2026-10-30", freq="D") if d.weekday() < 5]
    with ThreadPoolExecutor(8) as ex:
        res = [r for r in ex.map(one, days) if r]
    print(f"  dukascopy USDJPY days with ticks: {len(res)} of {len(days)}", flush=True)
    save("batchf_usdjpy_fix.parquet", pd.DataFrame(res, columns=["day", "p0000", "p0055", "p0200", "nticks"]))


def job_ubatchf3():
    """Batch F #454: Nasdaq IPO calendar (priced) 2015-09..2026-05 and Yahoo daily closes for each ticker and IWM."""
    ipos = []
    for m in pd.period_range("2015-09", "2026-05", freq="M"):
        st, raw = _raw_get(f"https://api.nasdaq.com/api/ipo/calendar?date={m}", timeout=40, headers={"Accept": "application/json"})
        try:
            d = json.loads(raw.decode()) if raw else {}
        except Exception:  # noqa: BLE001
            d = {}
        rows = ((((d or {}).get("data") or {}).get("priced") or {}).get("rows")) or []
        ipos += [{**r, "month": str(m)} for r in rows]
        time.sleep(0.4)
    print(f"  nasdaq priced IPO rows: {len(ipos)}", flush=True)
    if not ipos:
        return
    ip = pd.DataFrame(ipos).astype(str)
    save("batchf_ipos.parquet", ip)
    syms = sorted(set(ip.get("proposedTickerSymbol", pd.Series(dtype=str)).dropna()) | {"IWM"})
    px, t0 = [], time.time()
    for i, sym in enumerate(syms):
        if time.time() - t0 > 2.5 * 3600:
            print("  yahoo time cap hit", flush=True)
            break
        st, raw = _raw_get(f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?period1=1441065600&period2=1793491200&interval=1d", timeout=30)
        try:
            r = json.loads(raw.decode())["chart"]["result"][0]
            ts, cl = r["timestamp"], r["indicators"]["quote"][0]["close"]
            px += [(sym, int(a), float(b)) for a, b in zip(ts, cl) if b is not None]
        except Exception:  # noqa: BLE001
            pass
        if i % 200 == 0:
            print(f"  yahoo {i}/{len(syms)} rows {len(px)} (last HTTP {st})", flush=True)
        time.sleep(0.35)
    save("batchf_ipo_px.parquet", pd.DataFrame(px, columns=["sym", "t", "c"]))


def job_ubatchg():
    """Batch G (docs/PREREG_BATCH_G_20261126.md): BTC daily (DefiLlama), difficulty, Yahoo SPY, FRED DEXJPUS, USDT supply by day,
    Dukascopy EURUSD ticks on month-end days (hours 12-16 UTC)."""
    import io
    import lzma
    import struct
    rows, t = [], int(pd.Timestamp("2013-06-01", tz="UTC").timestamp())
    while t < time.time():
        d = get(f"https://coins.llama.fi/chart/coingecko:bitcoin?start={t}&span=500&period=1d", tries=2, timeout=30)
        rows += [(int(x["timestamp"]), float(x["price"])) for x in (((d or {}).get("coins") or {}).get("coingecko:bitcoin") or {}).get("prices") or []]
        t += 500 * 86400
        time.sleep(0.2)
    print(f"  btc daily: {len(rows)}", flush=True)
    save("batchg_btc_1d.parquet", pd.DataFrame(rows, columns=["t", "c"]))
    st, raw = _raw_get("https://api.blockchain.info/charts/difficulty?timespan=all&format=json&sampled=false", timeout=60)
    try:
        v = json.loads(raw.decode()).get("values", [])
        save("batchg_difficulty.parquet", pd.DataFrame([(int(x["x"]), float(x["y"])) for x in v], columns=["t", "difficulty"]))
    except Exception as e:  # noqa: BLE001
        print(f"  difficulty FAIL HTTP {st} {e}", flush=True)
    px = []
    for sym in ("SPY", "QQQ", "IWM", "EFA"):
        st, raw = _raw_get(f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?period1=946684800&period2=1793491200&interval=1d&events=div,split", timeout=40)
        try:
            r = json.loads(raw.decode())["chart"]["result"][0]
            adj = r["indicators"].get("adjclose", [{}])[0].get("adjclose") or r["indicators"]["quote"][0]["close"]
            px += [(sym, int(a), float(b)) for a, b in zip(r["timestamp"], adj) if b is not None]
        except Exception as e:  # noqa: BLE001
            print(f"  yahoo {sym} FAIL HTTP {st} {e}", flush=True)
        time.sleep(1)
    print(f"  yahoo rows {len(px)}", flush=True)
    save("batchg_etf_1d.parquet", pd.DataFrame(px, columns=["sym", "t", "adj"]))
    try:
        with urllib.request.urlopen(urllib.request.Request("https://fred.stlouisfed.org/graph/fredgraph.csv?id=DEXJPUS", headers=UA), timeout=60) as r:
            f = pd.read_csv(io.StringIO(r.read().decode()))
        f.columns = ["date", "rate"]
        f["rate"] = pd.to_numeric(f["rate"], errors="coerce")
        save("batchg_dexjpus.parquet", f.dropna())
    except Exception as e:  # noqa: BLE001
        print(f"  fred DEXJPUS FAIL {e}", flush=True)
    d = get("https://stablecoins.llama.fi/stablecoin/1", tries=2, timeout=60) or {}
    tok = d.get("tokens") or []
    save("batchg_usdt_supply.parquet", pd.DataFrame([(int(x["date"]), float((x.get("circulating") or {}).get("peggedUSD") or 0)) for x in tok], columns=["t", "supply"]))
    print(f"  usdt supply days: {len(tok)}", flush=True)
    out = []
    days = []
    for m in pd.period_range("2012-01", "2026-10", freq="M"):
        dd = m.to_timestamp(how="end").normalize()
        while dd.weekday() >= 5:
            dd -= pd.Timedelta(days=1)
        days.append(dd)
    for dd in days:
        for h in (12, 13, 14, 15, 16):
            st, raw = _raw_get(f"https://datafeed.dukascopy.com/datafeed/EURUSD/{dd.year}/{dd.month - 1:02d}/{dd.day:02d}/{h:02d}h_ticks.bi5", timeout=30)
            if st != 200 or not raw:
                continue
            try:
                b = lzma.decompress(raw)
            except Exception:  # noqa: BLE001
                continue
            for i in range(0, len(b) - 19, 20 * 50):  # every 50th tick is enough for minute-level marks
                ms, ask, bid, _, _ = struct.unpack(">IIIff", b[i:i + 20])
                out.append((dd.strftime("%Y-%m-%d"), h * 3600 + ms / 1000.0, (ask + bid) / 2 / 100000.0))
    print(f"  dukascopy EURUSD month-end ticks kept: {len(out)}", flush=True)
    save("batchg_eurusd_monthend.parquet", pd.DataFrame(out, columns=["day", "sec", "mid"]))


def job_ubatchh():
    """Batch H (docs/PREREG_BATCH_H_20261126.md): Yahoo daily open/close/adjclose for TSLA NVDA MSTR COIN PLTR SMCI AMD MTUM SPY ^N225."""
    px = []
    for sym in ("TSLA", "NVDA", "MSTR", "COIN", "PLTR", "SMCI", "AMD", "MTUM", "SPY", "^N225"):
        q = urllib.parse.quote(sym)
        st, raw = _raw_get(f"https://query1.finance.yahoo.com/v8/finance/chart/{q}?period1=946684800&period2=1793491200&interval=1d&events=div,split", timeout=40)
        try:
            r = json.loads(raw.decode())["chart"]["result"][0]
            qd = r["indicators"]["quote"][0]
            adj = (r["indicators"].get("adjclose") or [{}])[0].get("adjclose") or qd["close"]
            n0 = len(px)
            px += [(sym, int(t), o, c, a) for t, o, c, a in zip(r["timestamp"], qd["open"], qd["close"], adj) if c is not None and a is not None]
            print(f"  yahoo {sym}: {len(px) - n0} rows", flush=True)
        except Exception as e:  # noqa: BLE001
            print(f"  yahoo {sym} FAIL HTTP {st} {e}", flush=True)
        time.sleep(1)
    save("batchh_yahoo_1d.parquet", pd.DataFrame(px, columns=["sym", "t", "open", "close", "adj"]))


def job_ubatchh2():
    """#468 confirmation (docs/PREREG_468_CONFIRM_20261126.md): unseen Binance USDT perps (listed before 2023) 1h klines + funding
    2023-01..2026-10, and Hyperliquid 1h candleSnapshot for coins in either universe."""
    import re as _re
    from concurrent.futures import ThreadPoolExecutor
    t0 = time.time()
    syms, marker = [], ""
    while True:
        st, raw = _raw_get("https://s3-ap-northeast-1.amazonaws.com/data.binance.vision?delimiter=/&prefix=data/futures/um/monthly/klines/"
                           + (f"&marker={urllib.parse.quote(marker)}" if marker else ""), timeout=60)
        txt = raw.decode(errors="ignore") if raw else ""
        got = _re.findall(r"<Prefix>data/futures/um/monthly/klines/([^/<]+)/</Prefix>", txt)
        syms += got
        if "<IsTruncated>true</IsTruncated>" not in txt or not got:
            break
        marker = f"data/futures/um/monthly/klines/{got[-1]}/"
    seen = {f"{a}USDT" for a in ALTS_D}
    bad = ("DOM", "DEFI", "BLUEBIRD", "FOOTBALL")
    stab = {"USDCUSDT", "BUSDUSDT", "TUSDUSDT", "FDUSDUSDT", "USDPUSDT"}
    cand = sorted({x for x in syms if x.endswith("USDT") and "_" not in x and x not in seen and x not in stab and not any(b in x for b in bad)})
    print(f"  archive symbols {len(syms)}, USDT candidates {len(cand)}", flush=True)
    with ThreadPoolExecutor(8) as ex:
        has = list(ex.map(lambda x: bool(_bn_month("k1h", x, "2022-12")), cand))
    uni = [x for x, h in zip(cand, has) if h]
    print(f"  listed before 2023 (2022-12 file present): {len(uni)}", flush=True)
    months = [f"{y}-{m:02d}" for y in range(2023, 2027) for m in range(1, 13) if f"{y}-{m:02d}" <= "2026-10"]
    for kind, name in (("k1h", "batchh2_unseen_1h.parquet"), ("fund", "batchh2_unseen_funding.parquet")):
        tasks = [(x, m) for x in uni for m in months]
        rows = []
        with ThreadPoolExecutor(8) as ex:
            for (x, m), res in zip(tasks, ex.map(lambda a: _bn_month(kind, a[0], a[1]) if time.time() - t0 < 2.5 * 3600 else [], tasks)):
                rows += [(x, t, v) for t, v in res]
        df = pd.DataFrame(rows, columns=["sym", "t", "close" if kind == "k1h" else "rate"])
        print(f"  {name}: {df['sym'].nunique()} symbols, {len(df)} rows ({time.time() - t0:.0f}s)", flush=True)
        save(name, df)
    meta = get("https://api.hyperliquid.xyz/info", body={"type": "meta"}, tries=3, timeout=60) or {}
    hl = {u.get("name") for u in meta.get("universe", [])}
    want = sorted({x[:-4] for x in uni} | set(ALTS_D))
    alias = {c: (c if c in hl else (f"k{c[4:]}" if c.startswith("1000") and f"k{c[4:]}" in hl else None)) for c in want}
    end = int(time.time() * 1000)
    rows = []
    for c, h in alias.items():
        if not h:
            continue
        d = get("https://api.hyperliquid.xyz/info", body={"type": "candleSnapshot", "req": {"coin": h, "interval": "1h", "startTime": end - 5000 * 3600 * 1000, "endTime": end}}, tries=2, timeout=30) or []
        rows += [(c, int(k["t"]) // 1000, float(k["c"])) for k in d if isinstance(k, dict)]
        time.sleep(0.2)
    df = pd.DataFrame(rows, columns=["coin", "t", "close"])
    print(f"  hyperliquid 1h: {df['coin'].nunique()} coins, {len(df)} rows", flush=True)
    save("batchh2_hl_1h.parquet", df)


DELIST_RE = re.compile(r"Binance Will Delist (.+?) on (\d{4}-\d{2}-\d{2})")


def delist_events():
    """(announcement ms, delist date, [tokens]) from uncharted_w3_binance_ann.json catalog 161 (spot delistings only)."""
    d = json.loads((OUT / "uncharted_w3_binance_ann.json").read_text())
    out = []
    for x in d.get("161", []):
        t = str(x.get("title") or "")
        m = DELIST_RE.search(t)
        if not m or any(w in t for w in ("Margin", "Futures", "Pair", "Perpetual")):
            continue
        toks = [z.strip() for z in re.split(r",| and ", m.group(1)) if z.strip()]
        toks = [z for z in toks if re.fullmatch(r"[A-Z0-9]{2,12}", z)]
        if toks:
            out.append((int(x["releaseDate"]), m.group(2), toks))
    return out


def job_ubatchi():
    """Batch I (docs/PREREG_BATCH_I_20261126.md): Dukascopy 1-min BID candles (5-min marks 09-22 UTC) for 6 instruments, FRED
    3-month interbank rates, Solana epoch start times, Binance spot 1h for delisted tokens, Yahoo USO USL UNG UNL EEM EFA IWM."""
    import io
    import lzma
    import struct
    import zipfile
    from concurrent.futures import ThreadPoolExecutor
    t0 = time.time()
    px = []
    for sym in ("USO", "USL", "UNG", "UNL", "EEM", "EFA", "IWM"):
        st, raw = _raw_get(f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?period1=946684800&period2=1793491200&interval=1d&events=div,split", timeout=40)
        try:
            r = json.loads(raw.decode())["chart"]["result"][0]
            qd = r["indicators"]["quote"][0]
            adj = (r["indicators"].get("adjclose") or [{}])[0].get("adjclose") or qd["close"]
            px += [(sym, int(t), c, a) for t, c, a in zip(r["timestamp"], qd["close"], adj) if c is not None and a is not None]
        except Exception as e:  # noqa: BLE001
            print(f"  yahoo {sym} FAIL HTTP {st} {e}", flush=True)
        time.sleep(1)
    save("batchi_yahoo_1d.parquet", pd.DataFrame(px, columns=["sym", "t", "close", "adj"]))
    fr = []
    for cc in ("US", "EZ", "GB", "JP", "AU"):
        sid = f"IR3TIB01{cc}M156N"
        try:
            with urllib.request.urlopen(urllib.request.Request(f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}", headers=UA), timeout=60) as r:
                f = pd.read_csv(io.StringIO(r.read().decode()))
            f.columns = ["date", "rate"]
            f["rate"] = pd.to_numeric(f["rate"], errors="coerce")
            f["cc"] = cc
            fr.append(f.dropna())
        except Exception as e:  # noqa: BLE001
            print(f"  fred {sid} FAIL {e}", flush=True)
    if fr:
        save("batchi_ir3m.parquet", pd.concat(fr, ignore_index=True))
    # Binance spot 1h for delisted tokens
    ev = delist_events()
    tasks = set()
    for ms, dd, toks in ev:
        a = pd.Timestamp(ms, unit="ms").to_period("M")
        b = pd.Timestamp(dd).to_period("M")
        for tok in toks:
            for m in pd.period_range(a - 1, b, freq="M"):
                tasks.add((f"{tok}USDT", str(m)))

    def spot_month(a):
        sym, mth = a
        out = []
        try:
            with urllib.request.urlopen(urllib.request.Request(f"https://data.binance.vision/data/spot/monthly/klines/{sym}/1h/{sym}-1h-{mth}.zip", headers=UA), timeout=30) as r:
                z = zipfile.ZipFile(io.BytesIO(r.read()))
                for ln in z.read(z.namelist()[0]).decode().splitlines():
                    f = ln.split(",")
                    if f and f[0].strip().isdigit():
                        ts = int(f[0])
                        out.append((sym, (ts // 1000 if ts > 10**14 else ts) // 1000, float(f[4])))
        except Exception:  # noqa: BLE001
            pass
        return out
    rows = []
    with ThreadPoolExecutor(8) as ex:
        for res in ex.map(spot_month, sorted(tasks)):
            rows += res
    print(f"  delist announcements {len(ev)}, token-months {len(tasks)}, rows {len(rows)}", flush=True)
    save("batchi_delist_spot_1h.parquet", pd.DataFrame(rows, columns=["sym", "t", "close"]))
    # Solana epoch start times
    info = get("https://api.mainnet-beta.solana.com", body={"jsonrpc": "2.0", "id": 1, "method": "getEpochInfo"}, tries=3, timeout=30) or {}
    cur = ((info or {}).get("result") or {}).get("epoch") or 0
    ep = []
    for e in range(150, int(cur) + 1):
        if time.time() - t0 > 1.0 * 3600:
            print("  solana time cap hit", flush=True)
            break
        for k in range(0, 40):
            d = get("https://api.mainnet-beta.solana.com", body={"jsonrpc": "2.0", "id": 1, "method": "getBlockTime", "params": [e * 432000 + k]}, tries=2, timeout=20, pause=1.0)
            bt = (d or {}).get("result")
            if bt:
                ep.append((e, e * 432000 + k, int(bt)))
                break
        time.sleep(0.12)
    print(f"  solana epochs {len(ep)} (current {cur})", flush=True)
    save("batchi_sol_epochs.parquet", pd.DataFrame(ep, columns=["epoch", "slot", "t"]))
    # Dukascopy 1-minute candles
    div = {"EURUSD": 1e5, "GBPUSD": 1e5, "AUDUSD": 1e5, "USDJPY": 1e3, "XAUUSD": 1e3, "XAGUSD": 1e3}

    def day(a):
        ins, dd = a
        if time.time() - t0 > 3.3 * 3600:
            return []
        st, raw = _raw_get(f"https://datafeed.dukascopy.com/datafeed/{ins}/{dd.year}/{dd.month - 1:02d}/{dd.day:02d}/BID_candles_min_1.bi5", timeout=30)
        if st != 200 or not raw:
            return []
        try:
            b = lzma.decompress(raw)
        except Exception:  # noqa: BLE001
            return []
        out = []
        for i in range(0, len(b) - 23, 24):
            sec, f1, f2, f3, f4, _ = struct.unpack(">IIIIIf", b[i:i + 24])
            mm = sec // 60
            if 9 * 60 <= mm < 22 * 60 and (mm + 1) % 5 == 0:
                out.append((ins, dd.strftime("%Y-%m-%d"), int(sec), f1 / div[ins], f2 / div[ins], f3 / div[ins], f4 / div[ins]))
        return out
    days = [d for d in pd.date_range("2012-01-02", "2026-10-31", freq="D") if d.weekday() < 5]
    for ins in div:
        rows = []
        with ThreadPoolExecutor(8) as ex:
            for res in ex.map(day, [(ins, d) for d in days]):
                rows += res
        df = pd.DataFrame(rows, columns=["ins", "day", "sec", "f1", "f2", "f3", "f4"])
        ok = ((df["f3"] <= df[["f1", "f2"]].min(axis=1)) & (df["f4"] >= df[["f1", "f2"]].max(axis=1))).mean() if len(df) else float("nan")
        print(f"  dukascopy {ins}: days {df['day'].nunique()}, rows {len(df)}, order check (f3 low, f4 high) {ok:.3f} ({time.time() - t0:.0f}s)", flush=True)
        save(f"batchi_duka_{ins.lower()}.parquet", df)


def job_uverify():
    """Verification V: Binance spot 1h klines for stablecoin/USDT pairs (archive), 2020-01..2026-10."""
    import io
    import zipfile
    rows = []
    for sym in ("FDUSDUSDT", "USDCUSDT", "TUSDUSDT", "BUSDUSDT", "USDPUSDT", "DAIUSDT", "PAXUSDT", "USDSUSDT"):
        n0 = len(rows)
        for y in range(2020, 2027):
            for m in range(1, 13):
                mth = f"{y}-{m:02d}"
                if mth > "2026-10":
                    continue
                try:
                    with urllib.request.urlopen(urllib.request.Request(f"https://data.binance.vision/data/spot/monthly/klines/{sym}/1h/{sym}-1h-{mth}.zip", headers=UA), timeout=60) as r:
                        z = zipfile.ZipFile(io.BytesIO(r.read()))
                        for ln in z.read(z.namelist()[0]).decode().splitlines():
                            f = ln.split(",")
                            if f and f[0].isdigit():
                                ts = int(f[0])
                                rows.append((sym, (ts // 1000 if ts > 10**14 else ts) // 1000, float(f[2]), float(f[3]), float(f[4])))
                except Exception:  # noqa: BLE001
                    pass
        print(f"  {sym}: {len(rows) - n0} hours", flush=True)
    save("batchc_verify_spot_1h.parquet", pd.DataFrame(rows, columns=["sym", "t", "h", "l", "c"]))


def _safe(fn):
    def w():
        try:
            fn()
        except Exception:  # noqa: BLE001
            print(f"  ERROR in {fn.__name__}:\n{traceback.format_exc()}", flush=True)
    return w


def job_uprobe():
    for fn in (job_u387cca, job_u386tags, job_u384lst, job_u385hyperp, job_u383vaults):
        print(f"== {fn.__name__}", flush=True)
        _safe(fn)()


JOBS = {"uprobe": job_uprobe, "u383vaults": _safe(job_u383vaults), "u384lst": _safe(job_u384lst), "u385hyperp": _safe(job_u385hyperp),
        "u386tags": _safe(job_u386tags), "u387cca": _safe(job_u387cca), "u391hkipo": _safe(job_u391hkipo), "u387ccab": _safe(job_u387ccab), "u389binance": _safe(job_u389binance), "u387eth": _safe(job_u387eth), "u389docs": _safe(job_u389docs), "uwave3": job_uwave3, "uscale": job_uscale, "ufive": job_ufive, "uhip3": _safe(job_uhip3), "uw3b": _safe(job_uw3b), "udistinct": _safe(job_udistinct), "unav": _safe(job_unav), "udln": _safe(job_udln), "udln2": _safe(job_udln2), "ubatcha": _safe(job_ubatcha), "urates": _safe(job_urates), "ubatchb": _safe(job_ubatchb), "ubatchc": _safe(job_ubatchc), "ubatchc2": _safe(job_ubatchc2), "uverify": _safe(job_uverify), "ubatchd": _safe(job_ubatchd), "ucb442": _safe(job_ucb442), "upendle": _safe(job_upendle), "ubatchf": _safe(job_ubatchf), "ubatchf2": _safe(job_ubatchf2), "ubatchf3": _safe(job_ubatchf3), "ubatchg": _safe(job_ubatchg), "ubatchh": _safe(job_ubatchh), "ubatchh2": _safe(job_ubatchh2), "ubatchi": _safe(job_ubatchi)}


# ---------------------------------------------------------------- Batch L #501-#504 (docs/PREREG_BATCH_L_20261127.md)
BATCHL_PATTERNS = {501: r"Leverage (and|&) Margin Tiers", 502: r"Futures Will Delist", 503: r"Margin Will Delist",
                   504: r"Collateral Ratio"}


def _batchl_catalog():
    import json as _json
    import re as _re
    d = _json.loads((OUT / "uncharted_w3_binance_ann.json").read_text())
    rows = []

    def walk(x):
        if isinstance(x, dict):
            if "title" in x and "releaseDate" in x:
                rows.append(x)
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
    walk(d)
    seen, out = set(), []
    for r in sorted(rows, key=lambda r: r["releaseDate"]):
        for idea, pat in BATCHL_PATTERNS.items():
            if _re.search(pat, r["title"]) and (r["code"], idea) not in seen:
                seen.add((r["code"], idea))
                out.append({"idea": idea, "title": r["title"], "code": r["code"], "ms": int(r["releaseDate"])})
    return out


def _batchl_body(code):
    import json as _json
    u = f"https://www.binance.com/bapi/composite/v1/public/cms/article/detail/query?articleCode={code}"
    try:
        with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=30) as r:
            data = _json.loads(r.read().decode()).get("data") or {}
    except Exception as e:  # noqa: BLE001
        return f"__ERROR__ {type(e).__name__}: {e}"
    body = data.get("body") or ""
    texts = []

    def walk(x):
        if isinstance(x, dict):
            if isinstance(x.get("text"), str):
                texts.append(x["text"])
            for k in ("child", "children", "content"):
                if k in x:
                    walk(x[k])
            if x.get("node") in ("element",) and x.get("tag") in ("p", "tr", "li", "h2", "h3", "br"):
                texts.append("\n")
        elif isinstance(x, list):
            for v in x:
                walk(v)
    try:
        walk(_json.loads(body))
        txt = " ".join(texts)
    except Exception:  # noqa: BLE001
        txt = re.sub(r"<[^>]+>", " ", body) if isinstance(body, str) else str(body)
    return re.sub(r"[ \t]+", " ", txt)


def collateral_cuts(text):
    """Coins whose collateral ratio is lowered: rows of (coin, before %, after %) with after < before. Reads both one-line rows and
    tables flattened one cell per line (Binance's layout: coin / before / after on consecutive lines)."""
    import re as _re
    out = set()
    lines = [ln.strip() for ln in text.split("\n") if ln.strip()]
    pct = _re.compile(r"^(\d+(?:\.\d+)?)\s*%$")
    for i, ln in enumerate(lines):
        p = [float(x) for x in _re.findall(r"(\d+(?:\.\d+)?)\s*%", ln)]
        coins = _re.findall(r"\b([A-Z][A-Z0-9]{1,11})\b", ln)
        if len(p) >= 2 and coins and p[1] < p[0]:
            out |= set(coins)
        if _re.fullmatch(r"[A-Z][A-Z0-9]{1,11}", ln) and i + 2 < len(lines):
            a, b = pct.match(lines[i + 1]), pct.match(lines[i + 2])
            if a and b and float(b.group(1)) < float(a.group(1)):
                out.add(ln)
    return out


def job_ubatchl():
    """Batch L: Binance risk-parameter announcements -> bodies, symbols, dates; USD-M 1h closes around each event + BTCUSDT."""
    import json as _json
    import time as _time
    cat = _batchl_catalog()
    counts = {i: sum(1 for e in cat if e["idea"] == i) for i in BATCHL_PATTERNS}
    print("  catalog events:", len(cat), counts, flush=True)
    # Reuse bodies already fetched; re-fetch only failures, slowly (the first run hit HTTP 429 on 163 of 292).
    prev = OUT / "batchl_bodies.json"
    bodies = {k: v for k, v in (_json.loads(prev.read_text()).items() if prev.exists() else []) if not v.startswith("__ERROR__")}
    for e in cat:
        if e["code"] in bodies:
            continue
        for attempt in range(6):
            b = _batchl_body(e["code"])
            if "429" not in b[:60]:
                break
            _time.sleep(20 * (attempt + 1))
        bodies[e["code"]] = b
        _time.sleep(1.5)
    errs = sum(b.startswith("__ERROR__") for b in bodies.values())
    print(f"  bodies: {len(bodies)} fetched, {errs} errors", flush=True)
    (OUT / "batchl_bodies.json").write_text(_json.dumps(bodies))
    s3_list = _bn_archive_lister()
    _, prefs = s3_list("data/futures/um/monthly/klines/")
    universe = {p.rstrip("/").split("/")[-1] for p in prefs}
    print(f"  USD-M archive symbols: {len(universe)}", flush=True)
    stable = {"USDCUSDT", "FDUSDUSDT", "TUSDUSDT", "BUSDUSDT", "USDPUSDT", "DAIUSDT", "BTCUSDT"}
    events, need = [], set()
    for e in cat:
        text = e["title"] + "\n" + bodies.get(e["code"], "")
        if e["idea"] == 503:
            m = re.search(r"Margin Will Delist ([A-Z0-9]+)", e["title"])
            cands = {m.group(1) + "USDT"} if m else set()
        elif e["idea"] == 504:
            cands = {c + "USDT" for c in collateral_cuts(text)}
        else:
            cands = set(re.findall(r"\b([A-Z0-9]{2,15}USDT)\b", text))
        syms = sorted((cands & universe) - stable)
        events.append({**e, "syms": syms})
        t0 = pd.Timestamp(e["ms"], unit="ms")
        for s in syms + ["BTCUSDT"]:
            for k in (0, 1):
                need.add((s, (t0 + pd.DateOffset(months=k)).strftime("%Y-%m")))
    (OUT / "batchl_events.json").write_text(_json.dumps(events))
    print(f"  events with symbols: {sum(bool(e['syms']) for e in events)} of {len(events)}; symbol-months: {len(need)}", flush=True)
    for y in range(2022, 2027):
        for m in range(1, 13):
            mth = f"{y}-{m:02d}"
            if "2022-10" <= mth <= "2026-11":
                need.add(("BTCUSDT", mth))
    from concurrent.futures import ThreadPoolExecutor
    tasks = sorted(need)
    rows = []
    with ThreadPoolExecutor(8) as ex:
        for (s, mth), res in zip(tasks, ex.map(lambda a: _bn_month("k1h", a[0], a[1]), tasks)):
            rows += [(s, t, v) for t, v in res]
    df = pd.DataFrame(rows, columns=["sym", "t", "close"]).drop_duplicates(["sym", "t"])
    print(f"  1h rows: {len(df):,} for {df.sym.nunique()} symbols", flush=True)
    save("batchl_1h", df)


# ---------------------------------------------------------------- Batch M #505-#508 (docs/PREREG_BATCH_M_20261127.md)
def _bn_spot_month(sym, mth):
    import io as _io
    import zipfile
    url = f"https://data.binance.vision/data/spot/monthly/klines/{sym}/1h/{sym}-1h-{mth}.zip"
    out = []
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
            z = zipfile.ZipFile(_io.BytesIO(r.read()))
            for ln in z.read(z.namelist()[0]).decode().splitlines():
                f = ln.split(",")
                if f and f[0].strip().isdigit():
                    ts = int(f[0])
                    ts = (ts // 1000 if ts > 10**14 else ts) // 1000
                    out.append((ts, float(f[4])))
    except Exception:  # noqa: BLE001
        pass
    return out


def job_ubatchm():
    """Batch M: Yahoo GLD daily; Binance spot 1h for #505 (perp-delisting coins named in titles) and BTCUSDT."""
    import json as _json
    from concurrent.futures import ThreadPoolExecutor
    st, raw = _raw_get("https://query1.finance.yahoo.com/v8/finance/chart/GLD?period1=1072915200&period2=1795651200&interval=1d", timeout=40)
    try:
        r = json.loads(raw.decode())["chart"]["result"][0]
        q = r["indicators"]["quote"][0]
        save("batchm_gld_1d.parquet", pd.DataFrame([(int(t), c) for t, c in zip(r["timestamp"], q["close"]) if c is not None],
                                                    columns=["t", "close"]))
    except Exception as e:  # noqa: BLE001
        print(f"  yahoo GLD FAIL HTTP {st} {e}", flush=True)
    ev = _json.loads((OUT / "batchl_events.json").read_text())
    need = set()
    for e in ev:
        if e["idea"] != 502 or not re.search(r"[A-Z0-9]{2,15}USDT", e["title"]):
            continue
        t0 = pd.Timestamp(e["ms"], unit="ms")
        for s in e["syms"] + ["BTCUSDT"]:
            for k in (0, 1, 2):
                need.add((s, (t0 + pd.DateOffset(months=k)).strftime("%Y-%m")))
    tasks = sorted(need)
    rows = []
    with ThreadPoolExecutor(8) as ex:
        for (s, mth), res in zip(tasks, ex.map(lambda a: _bn_spot_month(a[0], a[1]), tasks)):
            rows += [(s, t, v) for t, v in res]
    df = pd.DataFrame(rows, columns=["sym", "t", "close"]).drop_duplicates(["sym", "t"])
    print(f"  spot 1h rows {len(df):,} for {df.sym.nunique()} symbols ({len(tasks)} symbol-months asked)", flush=True)
    save("batchm_spot_1h.parquet", df)


# ---------------------------------------------------------------- Batch O #512-#514 (docs/PREREG_BATCH_O_20261127.md)
def job_ubatcho():
    """Batch O: Yahoo CORN/SOYB/WEAT daily adjusted; FRED DEXHKUS and 3-month rates (US, HK)."""
    import io as _io
    px = []
    for sym in ("CORN", "SOYB", "WEAT"):
        st, raw = _raw_get(f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?period1=1262304000&period2=1795651200&interval=1d&events=div,split", timeout=40)
        try:
            r = json.loads(raw.decode())["chart"]["result"][0]
            q = r["indicators"]["quote"][0]
            adj = (r["indicators"].get("adjclose") or [{}])[0].get("adjclose") or q["close"]
            px += [(sym, int(t), a) for t, a in zip(r["timestamp"], adj) if a is not None]
        except Exception as e:  # noqa: BLE001
            print(f"  yahoo {sym} FAIL HTTP {st} {e}", flush=True)
        time.sleep(1)
    save("batcho_etf_1d.parquet", pd.DataFrame(px, columns=["sym", "t", "adj"]))
    fr = []
    for sid in ("DEXHKUS", "IR3TIB01USM156N", "IR3TIB01HKM156N", "HKGIR3TIB01STM"):
        try:
            with urllib.request.urlopen(urllib.request.Request(f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}", headers=UA), timeout=60) as r:
                f = pd.read_csv(_io.StringIO(r.read().decode()))
            f.columns = ["date", "value"]
            f["value"] = pd.to_numeric(f["value"], errors="coerce")
            f["sid"] = sid
            fr.append(f.dropna())
            print(f"  FRED {sid}: {len(f)} rows {f['date'].min()}..{f['date'].max()}", flush=True)
        except Exception as e:  # noqa: BLE001
            print(f"  FRED {sid} FAIL {e}", flush=True)
    if fr:
        save("batcho_fred.parquet", pd.concat(fr, ignore_index=True))


# ---------------------------------------------------------------- Batch P probe (docs/PLAN_BATCHES_O_Z.md, sovereign auctions outside the US)
BATCHP_PROBE = {
    "mof_jgb_hist": "https://www.mof.go.jp/english/policy/jgbs/reference/interest_rate/historical/jgbcme_all.csv",
    "mof_jgb_cur": "https://www.mof.go.jp/english/policy/jgbs/reference/interest_rate/jgbcme.csv",
    "mof_auction_index": "https://www.mof.go.jp/english/policy/jgbs/auction/past_auction_results/index.html",
    "mof_auction_calendar": "https://www.mof.go.jp/english/policy/jgbs/auction/calendar/index.html",
    "boe_10y": "https://www.bankofengland.co.uk/boeapps/database/_iadb-fromshowcolumns.asp?csv.x=yes&Datefrom=01/Jan/2010&Dateto=now&SeriesCodes=IUDMNZC&CSVF=TN&UsingCodes=Y&VPD=Y&VFD=N",
    "dmo_d21a": "https://www.dmo.gov.uk/data/ExportReport?reportCode=D2.1A",
    "dmo_d21c": "https://www.dmo.gov.uk/data/ExportReport?reportCode=D2.1C",
    "dmo_auctions_page": "https://www.dmo.gov.uk/data/gilt-market/gilt-auctions/",
    "bbk_10y": "https://api.statistiken.bundesbank.de/rest/data/BBSIS/D.I.ZAR.ZI.EUR.S1311.B.A604.R10XX.R.A.A._Z._Z.A?format=csv",
}


def job_ubatchp_probe():
    import json as _json
    out = {}
    for k, u in BATCHP_PROBE.items():
        st, raw = _raw_get(u, timeout=40)
        body = raw[:4000].decode("utf-8", "replace") if raw else ""
        out[k] = {"url": u, "status": st, "bytes": len(raw or b""), "head": body}
        print(f"  {k}: HTTP {st}, {len(raw or b'')} bytes", flush=True)
        time.sleep(1)
    (OUT / "batchp_probe.json").write_text(_json.dumps(out))


def job_ubatchp_probe2():
    """MOF past auction results: index page, then every linked results page (to read 10-year JGB auction dates)."""
    import json as _json
    base = "https://www.mof.go.jp"
    st, raw = _raw_get(base + "/english/policy/jgbs/auction/past_auction_results/index.html", timeout=40)
    html = raw.decode("utf-8", "replace")
    links = sorted(set(re.findall(r'href="([^"]*past_auction_results[^"]+)"', html)))
    print(f"  index HTTP {st}, {len(links)} links", flush=True)
    pages = {"__index__": html}
    for ln in links[:80]:
        u = ln if ln.startswith("http") else base + ln if ln.startswith("/") else base + "/english/policy/jgbs/auction/past_auction_results/" + ln
        s2, r2 = _raw_get(u, timeout=40)
        pages[u] = r2.decode("utf-8", "replace") if r2 else f"__HTTP {s2}__"
        time.sleep(0.5)
    print(f"  pages fetched: {len(pages) - 1}", flush=True)
    (OUT / "batchp_mof_pages.json").write_text(_json.dumps(pages))


def job_ubatchp():
    """Batch P: MOF JGB yields (history + current month), MOF auction results xls (raw), BoE 10y zero-coupon, Bundesbank 10y Bund."""
    srcs = {"batchp_mof_hist.csv": "https://www.mof.go.jp/english/policy/jgbs/reference/interest_rate/historical/jgbcme_all.csv",
            "batchp_mof_cur.csv": "https://www.mof.go.jp/english/policy/jgbs/reference/interest_rate/jgbcme.csv",
            "batchp_mof_auctions.xls": "https://www.mof.go.jp/english/policy/jgbs/auction/past_auction_results/Auction_Results_for_JGBs.xls",
            "batchp_boe_10y.csv": "https://www.bankofengland.co.uk/boeapps/database/_iadb-fromshowcolumns.asp?csv.x=yes&Datefrom=01/Jan/1979&Dateto=now&SeriesCodes=IUDMNZC&CSVF=TN&UsingCodes=Y&VPD=Y&VFD=N",
            "batchp_bbk_10y.csv": "https://api.statistiken.bundesbank.de/rest/data/BBSIS/D.I.ZAR.ZI.EUR.S1311.B.A604.R10XX.R.A.A._Z._Z.A?format=csv"}
    for name, u in srcs.items():
        st, raw = _raw_get(u, timeout=60)
        print(f"  {name}: HTTP {st}, {len(raw or b'')} bytes", flush=True)
        if raw:
            (OUT / name).write_bytes(raw)
        time.sleep(1)


def job_ubatchw():
    """Batch W: Yahoo UGA, USO, UNG daily adjusted (docs/PREREG_BATCH_W_20261128.md)."""
    px = []
    for sym in ("UGA", "USO", "UNG"):
        st, raw = _raw_get(f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?period1=1136073600&period2=1795651200&interval=1d&events=div,split", timeout=40)
        try:
            r = json.loads(raw.decode())["chart"]["result"][0]
            q = r["indicators"]["quote"][0]
            adj = (r["indicators"].get("adjclose") or [{}])[0].get("adjclose") or q["close"]
            px += [(sym, int(t), a) for t, a in zip(r["timestamp"], adj) if a is not None]
        except Exception as e:  # noqa: BLE001
            print(f"  yahoo {sym} FAIL HTTP {st} {e}", flush=True)
        time.sleep(1)
    save("batchw_etf_1d.parquet", pd.DataFrame(px, columns=["sym", "t", "adj"]))


BATCHX_ETF = "SPY QQQ IWM DIA XLE XLF XLK XLV XLY XLP XLI XLB XLU EEM EFA EWJ EWZ FXI GLD SLV USO UNG TLT HYG LQD VNQ SMH XBI KRE GDX ARKK TQQQ SOXL IBB".split()
BATCHX_FX = {"USDJPY": "JPY=X", "AUDJPY": "AUDJPY=X", "EURJPY": "EURJPY=X", "GBPJPY": "GBPJPY=X", "NZDJPY": "NZDJPY=X",
             "CADJPY": "CADJPY=X", "CHFJPY": "CHFJPY=X", "EURUSD": "EURUSD=X", "GBPUSD": "GBPUSD=X", "AUDUSD": "AUDUSD=X",
             "NZDUSD": "NZDUSD=X", "USDCAD": "CAD=X", "USDCHF": "CHF=X", "USDMXN": "MXN=X"}


def job_ubatchx():
    """Batch X: Yahoo daily OHLC for 34 ETFs (scaled to adjusted close) and 14 FX pairs, 2005-2026 (docs/PREREG_BATCH_X_20261128.md)."""
    rows = []
    for kind, items in (("etf", [(s, s) for s in BATCHX_ETF]), ("fx", list(BATCHX_FX.items()))):
        for name, ysym in items:
            st, raw = _raw_get(f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(ysym)}?period1=1104537600&period2=1795651200&interval=1d&events=div,split", timeout=40)
            try:
                r = json.loads(raw.decode())["chart"]["result"][0]
                q = r["indicators"]["quote"][0]
                adj = (r["indicators"].get("adjclose") or [{}])[0].get("adjclose") if kind == "etf" else None
                for i, t in enumerate(r["timestamp"]):
                    o, h, l, c = q["open"][i], q["high"][i], q["low"][i], q["close"][i]
                    if None in (o, h, l, c) or not c:
                        continue
                    k = (adj[i] / c) if (adj and adj[i]) else 1.0
                    rows.append((kind, name, int(t), o * k, h * k, l * k, c * k))
            except Exception as e:  # noqa: BLE001
                print(f"  yahoo {ysym} FAIL HTTP {st} {e}", flush=True)
            time.sleep(1)
    df = pd.DataFrame(rows, columns=["kind", "sym", "t", "o", "h", "l", "c"])
    print("  " + ", ".join(f"{k} {g.sym.nunique()} symbols {len(g)} rows" for k, g in df.groupby("kind")), flush=True)
    save("batchx_ohlc_1d.parquet", df)


BATCHZ_COINS = ["BTC", "ETH", "SOL", "XRP", "DOGE", "AVAX", "LINK", "SUI", "ARB", "OP", "LTC", "BNB"]


def job_ubatchz():
    """Batch Z (#534): Aster and Lighter funding history for #208's coins (docs/PREREG_BATCH_Z_20261128.md)."""
    rows, t0 = [], 1704067200000  # 2024-01-01
    for c in BATCHZ_COINS:
        start, n = t0, 0
        for _ in range(60):
            st, raw = _raw_get(f"https://fapi.asterdex.com/fapi/v1/fundingRate?symbol={c}USDT&startTime={start}&limit=1000", timeout=30)
            try:
                d = json.loads(raw.decode()) if raw else []
            except Exception:  # noqa: BLE001
                d = []
            if not isinstance(d, list) or not d:
                if n == 0:
                    print(f"  aster {c}: HTTP {st} {raw[:120] if raw else b''}", flush=True)
                break
            rows += [("aster", c, int(x["fundingTime"]) // 1000, float(x["fundingRate"])) for x in d]
            n += len(d)
            start = int(d[-1]["fundingTime"]) + 1
            if len(d) < 1000:
                break
            time.sleep(0.3)
        print(f"  aster {c}: {n} points", flush=True)
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
            d, st, raw = [], None, b""
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

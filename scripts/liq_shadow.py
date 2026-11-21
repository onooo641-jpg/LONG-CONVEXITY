"""Liquidation shadow watcher (PREREG_LIQ_SHADOW_20261121). SIMULATE-ONLY: reads chains, sends nothing, holds no keys.

    LIQ_BUDGET_MIN=350 python scripts/liq_shadow.py <chain>

Per chain it (1) tracks borrowers of the Aave v3 main pool, (2) records the first time a user's health factor < 1 together with a
simulated flash-loan liquidation (quotes from Uniswap v3 QuoterV2), (3) logs every actual LiquidationCall with the winner's gas.
Files in data/shadow/<chain>/: state.json, borrowers.json, unhealthy.jsonl, liquidations.jsonl, uptime.jsonl, stats.json.
Matching/GO-KILL evaluation is scripts/liq_shadow_summary.py (offline, deterministic).
"""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "shadow"
UA = {"User-Agent": "long-convexity-research/1.0", "Content-Type": "application/json"}
MULTICALL3 = "0xca11bde05977b3631167028862be2a173976ca11"
T_LIQ = "0xe413a321e8681d831f4dbccbca790d2952b56f977908e45be37335533e005286"
T_BORROW = "0xb3d084820fb1a9decffb176436bd02558d15fac9b0ddfed8c465bc7359d7dce0"
SEL = {
    "getUserAccountData": "0xbf92857c", "getReservesList": "0xd1946dbc", "premium": "0x074b2e43", "provider": "0x0542975c",
    "oracle": "0xfca513a8", "dataprovider": "0xe860accb", "getUserReserveData": "0x28dd2d01",
    "getReserveConfigurationData": "0x3e150141", "getAssetPrice": "0xb3596f07", "decimals": "0x313ce567",
    "aggregate3": "0x82ad56cb", "quote": "0xc6a5026a",
}
CFG = {
    "arbitrum": dict(pool="0x794a61358d6845594f94dc1db02a252b5b4814ad", wn="0x82af49447d8a07e3bd95bd0d56f35241523fbab1",
                     quoter="0x61ffe014ba17989e743c5f6cb21bf9697530b21e", block_s=0.25,
                     rpcs=["https://arb1.arbitrum.io/rpc", "https://arbitrum-one-rpc.publicnode.com"], max_span=30000),
    "optimism": dict(pool="0x794a61358d6845594f94dc1db02a252b5b4814ad", wn="0x4200000000000000000000000000000000000006",
                     quoter="0x61ffe014ba17989e743c5f6cb21bf9697530b21e", block_s=2,
                     rpcs=["https://mainnet.optimism.io", "https://optimism-rpc.publicnode.com"], max_span=10000),
    "polygon": dict(pool="0x794a61358d6845594f94dc1db02a252b5b4814ad", wn="0x0d500b1d8e8ef31e21c99d1db9a6444d3adf1270",
                    quoter="0x61ffe014ba17989e743c5f6cb21bf9697530b21e", block_s=2,
                    rpcs=["https://poly.api.pocket.network", "https://polygon.gateway.tenderly.co", "https://polygon-bor-rpc.publicnode.com"], max_span=10000),
    "avalanche": dict(pool="0x794a61358d6845594f94dc1db02a252b5b4814ad", wn="0xb31f66aa3c1e785363f0875a1b74e27b85fd66c7",
                      quoter="0xbe0f5544ec67e9b3b2d979aaa43f18fd87e6257f", block_s=2,
                      rpcs=["https://avalanche.gateway.tenderly.co", "https://avalanche-c-chain-rpc.publicnode.com"], max_span=10000),
    "base": dict(pool="0xa238dd80c259a72e81d7e4664a9801593f98d1c5", wn="0x4200000000000000000000000000000000000006",
                 quoter="0x3d4e44eb1374240ce5f1b871ab261cd16335b76a", block_s=2,
                 rpcs=["https://base.api.pocket.network", "https://base-rpc.publicnode.com", "https://base.gateway.tenderly.co"], max_span=10000),
}
CAP_USD = 250_000.0
BATCH, MAX_PER_CYCLE = 60, 600   # users per multicall (eth_call gas cap) and per cycle


def tier_interval(h):
    """seconds between health-factor refreshes (PREREG_LIQ_SHADOW addendum 1)."""
    return 0 if h < 1.05 else 10 if h < 1.2 else 60 if h < 1.5 else 300
BOOTSTRAP_DAYS = 180


# ------------------------------------------------------------------ ABI helpers
def w(x) -> str:
    if isinstance(x, str):
        return x[2:].lower().rjust(64, "0")
    return format(int(x), "x").rjust(64, "0")


def words(hexdata: str):
    d = hexdata[2:] if hexdata.startswith("0x") else hexdata
    return [int(d[i:i + 64], 16) for i in range(0, len(d), 64)]


def addr(word: int) -> str:
    return "0x" + format(word, "x").rjust(40, "0")


def encode_aggregate3(calls):
    """calls: list of (target, calldata_hex). allowFailure = true."""
    n = len(calls)
    tuples = []
    for target, data in calls:
        b = data[2:] if data.startswith("0x") else data
        blen = len(b) // 2
        pad = (-blen) % 32
        tuples.append(w(target) + w(1) + w(0x60) + w(blen) + b + "00" * pad)
    offsets, pos = [], n * 32
    for t in tuples:
        offsets.append(pos)
        pos += len(t) // 2
    return SEL["aggregate3"] + w(0x20) + w(n) + "".join(w(o) for o in offsets) + "".join(tuples)


def decode_aggregate3(ret: str):
    """returns list of (success, bytes_hex) from aggregate3's Result[]."""
    d = ret[2:]
    base = int(d[0:64], 16) * 2
    n = int(d[base:base + 64], 16)
    arr = base + 64
    out = []
    for i in range(n):
        off = int(d[arr + 64 * i: arr + 64 * i + 64], 16) * 2
        t = arr + off
        ok = int(d[t:t + 64], 16) == 1
        boff = int(d[t + 64:t + 128], 16) * 2
        blen = int(d[t + boff: t + boff + 64], 16) * 2
        out.append((ok, "0x" + d[t + boff + 64: t + boff + 64 + blen]))
    return out


# ------------------------------------------------------------------ RPC
class Rpc:
    def __init__(self, urls, stats):
        self.urls, self.stats, self.fail = list(urls), stats, {}

    def call(self, method, params, tries=3):
        last = None
        for k in range(tries):
            live = [u for u in self.urls if self.fail.get(u, 0) < 6] or self.urls
            for u in live:
                try:
                    req = urllib.request.Request(u, data=json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode(),
                                                 headers=UA, method="POST")
                    t0 = time.time()
                    with urllib.request.urlopen(req, timeout=30) as r:
                        j = json.loads(r.read().decode())
                    if "error" in j:
                        last = f"{u}: {str(j['error'])[:160]}"
                        self.stats["rpc_err"] = self.stats.get("rpc_err", 0) + 1
                        if any(s in str(j["error"]).lower() for s in ("range", "limit", "exceed", "too many")):
                            raise ValueError(last)
                        continue
                    self.fail[u] = 0
                    self.stats["rpc_ok"] = self.stats.get("rpc_ok", 0) + 1
                    self.stats["rpc_ms_sum"] = self.stats.get("rpc_ms_sum", 0) + (time.time() - t0) * 1000
                    return j["result"]
                except ValueError:
                    raise
                except urllib.error.HTTPError as e:
                    last = f"{u}: HTTP {e.code}"
                    self.fail[u] = self.fail.get(u, 0) + 1
                    self.stats["rpc_err"] = self.stats.get("rpc_err", 0) + 1
                    if e.code == 429:
                        time.sleep(3)
                except Exception as e:  # noqa: BLE001
                    last = f"{u}: {type(e).__name__}"
                    self.fail[u] = self.fail.get(u, 0) + 1
                    self.stats["rpc_err"] = self.stats.get("rpc_err", 0) + 1
            time.sleep(1.5 * (k + 1))
        raise RuntimeError(last)

    def eth_call(self, to, data, block="latest"):
        return self.call("eth_call", [{"to": to, "data": data}, block])

    def head(self):
        return int(self.call("eth_blockNumber", []), 16)

    def multicall(self, calls):
        ret = self.eth_call(MULTICALL3, encode_aggregate3(calls))
        return decode_aggregate3(ret)


# ------------------------------------------------------------------ chain context
class Chain:
    def __init__(self, name):
        self.name, self.c = name, CFG[name]
        self.dir = DATA / name
        self.dir.mkdir(parents=True, exist_ok=True)
        self.stats = {}
        self.rpc = Rpc(self.c["rpcs"], self.stats)
        self.pool = self.c["pool"]
        self.meta = {}      # reserves, decimals, bonus, etc.
        self.meta_ts = 0.0

    # ---- persistence
    def jload(self, fn, default):
        p = self.dir / fn
        return json.loads(p.read_text()) if p.exists() else default

    def jsave(self, fn, obj):
        (self.dir / fn).write_text(json.dumps(obj))

    def jappend(self, fn, obj):
        with open(self.dir / fn, "a") as f:
            f.write(json.dumps(obj, sort_keys=True) + "\n")

    # ---- protocol metadata (refreshed hourly)
    def refresh_meta(self):
        r = self.rpc
        prov = addr(words(r.eth_call(self.pool, SEL["provider"]))[0])
        oracle = addr(words(r.eth_call(prov, SEL["oracle"]))[0])
        dp = addr(words(r.eth_call(prov, SEL["dataprovider"]))[0])
        premium = words(r.eth_call(self.pool, SEL["premium"]))[0] / 10000.0
        lst = r.eth_call(self.pool, SEL["getReservesList"])
        ws = words(lst)
        n = ws[1]
        assets = [addr(x) for x in ws[2:2 + n]]
        calls = [(a, SEL["decimals"]) for a in assets] + [(dp, SEL["getReserveConfigurationData"] + w(a)) for a in assets]
        res = r.multicall(calls)
        dec = {a: int(words(res[i][1])[0]) for i, a in enumerate(assets)}
        cfg = {}
        for i, a in enumerate(assets):
            ok, data = res[n + i]
            ww = words(data) if ok else []
            if len(ww) >= 10:
                cfg[a] = dict(bonus=ww[3] / 10000.0, lt=ww[2], coll=bool(ww[5]) and ww[8] == 1 and ww[9] == 0, active=ww[8] == 1)
        self.meta = dict(prov=prov, oracle=oracle, dp=dp, premium=premium, assets=assets, dec=dec, cfg=cfg)
        self.meta_ts = time.time()

    def prices(self, assets):
        res = self.rpc.multicall([(self.meta["oracle"], SEL["getAssetPrice"] + w(a)) for a in assets])
        return {a: (words(d)[0] / 1e8 if ok else None) for a, (ok, d) in zip(assets, res)}

    # ---- simulation of one liquidation (PREREG definitions)
    def quote_out(self, tin, tout, amt):
        best = None
        for fee in (500, 3000, 100, 10000):
            try:
                ret = self.rpc.eth_call(self.c["quoter"], SEL["quote"] + w(tin) + w(tout) + w(amt) + w(fee) + w(0), "latest")
                out = words(ret)[0]
                if best is None or out > best[0]:
                    best = (out, f"{fee}")
            except Exception:  # noqa: BLE001
                continue
        return best

    def quote_route(self, tin, tout, amt):
        if tin == tout:
            return amt, "same"
        d = self.quote_out(tin, tout, amt)
        wn = self.c["wn"]
        if tin != wn and tout != wn:
            h = self.quote_out(tin, wn, amt)
            if h and h[0] > 0:
                h2 = self.quote_out(wn, tout, h[0])
                if h2 and (d is None or h2[0] > d[0]):
                    return h2[0], f"via_wn:{h[1]}/{h2[1]}"
        return (d[0], d[1]) if d else None

    def simulate(self, user, hf):
        m = self.meta
        assets = m["assets"]
        res = self.rpc.multicall([(m["dp"], SEL["getUserReserveData"] + w(a) + w(user)) for a in assets])
        px = self.prices(assets)
        coll, debt = {}, {}
        for a, (ok, d) in zip(assets, res):
            if not ok:
                continue
            ww = words(d)
            if len(ww) < 9 or px.get(a) is None:
                continue
            dec = 10 ** m["dec"][a]
            bal, sdebt, vdebt, usage = ww[0], ww[1], ww[2], ww[8]
            cfg = m["cfg"].get(a)
            if bal > 0 and usage == 1 and cfg and cfg["coll"]:
                coll[a] = bal / dec * px[a]
            if sdebt + vdebt > 0:
                debt[a] = (sdebt + vdebt) / dec * px[a]
        if not coll or not debt:
            return None
        ca = max(coll, key=coll.get)
        da = max(debt, key=debt.get)
        cf = 1.0 if hf < 0.95 else 0.5
        debt_usd = min(cf * debt[da], CAP_USD)
        bonus = m["cfg"][ca]["bonus"]
        seized_usd = debt_usd * bonus
        if seized_usd > coll[ca]:
            seized_usd = coll[ca]
            debt_usd = seized_usd / bonus
        d_dec, c_dec = 10 ** m["dec"][da], 10 ** m["dec"][ca]
        debt_units = int(debt_usd / px[da] * d_dec)
        seized_units = int(seized_usd / px[ca] * c_dec)
        q = self.quote_route(ca, da, seized_units)
        if q is None or q[0] <= 0:
            return dict(user=user, ok=False, reason="no_quote", debt=da, coll=ca)
        proceeds_usd = q[0] / d_dec * px[da]
        premium_usd = debt_usd * m["premium"]
        return dict(user=user, ok=True, debt=da, coll=ca, debt_usd=debt_usd, seized_usd=seized_usd, proceeds_usd=proceeds_usd,
                    premium_usd=premium_usd, net_before_gas_usd=proceeds_usd - debt_usd - premium_usd, route=q[1],
                    bonus_oracle_usd=seized_usd - debt_usd, px_debt=px[da], px_coll=px[ca])

    # ---- borrower set bootstrap (Borrow logs for the previous 180 days) + previously liquidated users
    def bootstrap(self, head, deadline):
        st = self.jload("state.json", {})
        users = set(self.jload("borrowers.json", []))
        if st.get("boot_done"):
            return True
        c = self.c
        if "boot_next" not in st:
            st["boot_end"] = head
            st["boot_next"] = head - int(BOOTSTRAP_DAYS * 86400 / c["block_s"])
            try:
                import pandas as pd
                raw = pd.read_parquet(ROOT / "data" / "public" / f"liq_{self.name}_raw.parquet", columns=["venue", "user"])
                users |= set(raw[raw["venue"] == self.pool]["user"].tolist())
            except Exception as e:  # noqa: BLE001
                print(f"{self.name}: no historical liquidated users ({e})", flush=True)
        b, step = st["boot_next"], c["max_span"]
        last_save = time.time()
        while b <= st["boot_end"]:
            if time.time() > deadline:
                break
            e = min(b + step - 1, st["boot_end"])
            try:
                logs = self.rpc.call("eth_getLogs", [{"fromBlock": hex(b), "toBlock": hex(e), "address": self.pool, "topics": [T_BORROW]}])
            except ValueError:
                step = max(500, step // 2)
                continue
            except RuntimeError as ex:
                print(f"{self.name}: bootstrap getLogs failed {b}-{e}: {str(ex)[:100]}", flush=True)
                time.sleep(5)
                continue
            for lg in logs:
                users.add("0x" + lg["topics"][2][-40:])
            if len(logs) < 200:
                step = min(step * 2, c["max_span"])
            b = e + 1
            if time.time() - last_save > 120:
                st["boot_next"] = b
                self.jsave("borrowers.json", sorted(users))
                self.jsave("state.json", st)
                last_save = time.time()
                print(f"{self.name}: bootstrap to block {b}/{st['boot_end']} users {len(users)}", flush=True)
        st["boot_next"] = b
        self.jsave("borrowers.json", sorted(users))
        if b > st["boot_end"]:
            st["boot_done"] = True
            st["log_next"] = st["boot_end"] + 1
        self.jsave("state.json", st)
        print(f"{self.name}: bootstrap {'DONE' if st.get('boot_done') else 'partial'}, users {len(users)}", flush=True)
        return bool(st.get("boot_done"))

    # ---- actual liquidations
    def log_liquidation(self, lg):
        t, d = lg["topics"], words(lg["data"])
        user = "0x" + t[3][-40:]
        coll, debt = "0x" + t[1][-40:], "0x" + t[2][-40:]
        rec = dict(chain=self.name, block=int(lg["blockNumber"], 16), tx=lg["transactionHash"], user=user, coll=coll, debt=debt,
                   debt_amt=d[0], coll_amt=d[1], liquidator="0x" + format(d[2], "x").rjust(40, "0"))
        try:
            r = self.rpc.call("eth_getTransactionReceipt", [rec["tx"]])
            rec["winner"] = r["from"].lower()
            rec["gas_wei"] = int(r["gasUsed"], 16) * int(r.get("effectiveGasPrice", "0x0"), 16) + int(r.get("l1Fee", "0x0") or "0x0", 16)
            px = self.prices([coll, debt, self.c["wn"]])
            dc, dd = 10 ** self.meta["dec"].get(coll, 18), 10 ** self.meta["dec"].get(debt, 18)
            rec["bonus_usd"] = rec["coll_amt"] / dc * px[coll] - rec["debt_amt"] / dd * px[debt]
            rec["gas_usd"] = rec["gas_wei"] / 1e18 * px[self.c["wn"]]
            rec["seen_wall"] = time.time()
            rec["ts"] = int(self.rpc.call("eth_getBlockByNumber", [hex(rec["block"]), False])["timestamp"], 16)
        except Exception as e:  # noqa: BLE001
            rec["err"] = str(e)[:100]
        self.jappend("liquidations.jsonl", rec)

    # ---- main loop
    def run(self, budget_min):
        t_start = time.time()
        deadline = t_start + budget_min * 60
        head = self.rpc.head()
        print(f"{self.name}: start, head {head}", flush=True)
        self.refresh_meta()
        if not self.bootstrap(head, deadline - 120):
            print(f"{self.name}: bootstrap unfinished; will resume next run", flush=True)
            return
        st = self.jload("state.json", {})
        users = set(self.jload("borrowers.json", []))
        newp = self.dir / "borrowers_new.jsonl"
        if newp.exists():
            users |= {x.strip() for x in newp.read_text().splitlines() if x.strip()}
        hf = {}                    # user -> (hf, last_checked)
        open_rec = {}              # user -> record written, awaiting heal/liquidation
        log_next = st.get("log_next", head + 1)
        up_start = time.time()
        self.jappend("uptime.jsonl", dict(kind="start", wall=up_start, block=head))
        last_flush = last_hb = time.time()
        n_cycles = 0
        while time.time() < deadline:
            t0 = time.time()
            try:
                head = self.rpc.head()
                if time.time() - self.meta_ts > 3600:
                    self.refresh_meta()
                # new logs
                if head >= log_next:
                    e = min(head, log_next + self.c["max_span"] - 1)
                    logs = self.rpc.call("eth_getLogs", [{"fromBlock": hex(log_next), "toBlock": hex(e), "address": self.pool,
                                                          "topics": [[T_BORROW, T_LIQ]]}])
                    for lg in logs:
                        if lg["topics"][0] == T_BORROW:
                            u = "0x" + lg["topics"][2][-40:]
                            if u not in users:
                                users.add(u)
                                hf.pop(u, None)
                                with open(newp, "a") as nf:
                                    nf.write(u + "\n")
                        else:
                            self.log_liquidation(lg)
                            open_rec.pop("0x" + lg["topics"][3][-40:], None)
                    log_next = e + 1
                # which users to refresh: unknown or old enough by tier
                now = time.time()
                due = []
                for u in users:
                    h = hf.get(u)
                    if h is None:
                        due.append(u)
                    elif h[0] >= 99:
                        continue                       # no debt: re-checked only after a new Borrow event
                    elif now - h[1] >= tier_interval(h[0]):
                        due.append(u)
                due.sort(key=lambda u: (hf.get(u, (0.0, 0))[0]))
                for i in range(0, min(len(due), MAX_PER_CYCLE), BATCH):
                    batch = due[i:i + BATCH]
                    res = self.rpc.multicall([(self.pool, SEL["getUserAccountData"] + w(u)) for u in batch])
                    for u, (ok, d) in zip(batch, res):
                        ww = words(d) if ok else []
                        if len(ww) < 6:
                            continue
                        debt_base, h_f = ww[1], ww[5]
                        if debt_base == 0:
                            hf[u] = (99.0, now)
                            if u in open_rec:
                                open_rec.pop(u)
                            continue
                        hff = h_f / 1e18
                        hf[u] = (hff, now)
                        if hff < 1.0 and u not in open_rec:
                            sim = self.simulate(u, hff)
                            n_ready = self.rpc.head()
                            rec = dict(chain=self.name, user=u, hf=hff, block_seen=head, n_ready=n_ready, wall=time.time(),
                                       detect_ms=int((time.time() - t0) * 1000), sim=sim)
                            self.jappend("unhealthy.jsonl", rec)
                            open_rec[u] = rec
                        elif hff >= 1.0 and u in open_rec:
                            self.jappend("unhealthy.jsonl", dict(chain=self.name, user=u, healed=True, block_seen=head, wall=time.time()))
                            open_rec.pop(u)
                n_cycles += 1
                self.stats["cycles"] = n_cycles
                self.stats["tracked"] = len(users)
                self.stats["last_cycle_ms"] = int((time.time() - t0) * 1000)
            except Exception as ex:  # noqa: BLE001
                self.stats["loop_err"] = self.stats.get("loop_err", 0) + 1
                print(f"{self.name}: loop error {str(ex)[:150]}", flush=True)
                time.sleep(3)
            if time.time() - last_hb > 30:
                self.jappend("uptime.jsonl", dict(kind="hb", wall=time.time(), block=head))
                last_hb = time.time()
            if time.time() - last_flush > 300:
                st["log_next"] = log_next
                self.jsave("state.json", st)
                self.jsave("stats.json", self.stats)
                last_flush = time.time()
                print(f"{self.name}: head {head} cycles {n_cycles} tracked {len(users)} last_cycle {self.stats.get('last_cycle_ms')} ms "
                      f"rpc ok/err {self.stats.get('rpc_ok')}/{self.stats.get('rpc_err')}", flush=True)
            time.sleep(max(0.0, 0.4 - (time.time() - t0)))
        st["log_next"] = log_next
        self.jsave("state.json", st)
        self.jsave("borrowers.json", sorted(users))      # consolidated once per run (file is large)
        if newp.exists():
            newp.unlink()
        self.jsave("stats.json", self.stats)
        self.jappend("uptime.jsonl", dict(kind="stop", wall=time.time(), block=head))
        print(f"{self.name}: budget reached, stopped cleanly at block {head}", flush=True)


def main(argv):
    name = argv[0]
    budget = float(os.environ.get("LIQ_BUDGET_MIN", "350"))
    Chain(name).run(budget)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

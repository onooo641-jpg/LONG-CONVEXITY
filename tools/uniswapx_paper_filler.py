"""UniswapX paper filler for Arbitrum — read-only, no wallet, no keys, no money (#371 Stage 5, docs/PREREG_UNISWAPX_20261124.md).

Run (Windows / Mac / Linux, Python 3.9+, nothing to install):
    python uniswapx_paper_filler.py --hours 36
Recompute the summary from an existing log:
    python uniswapx_paper_filler.py --summarize

What it does, every 2 seconds:
  1. reads open UniswapX orders on Arbitrum from Uniswap's public API;
  2. for each open order, asks KyberSwap's free aggregator how much of the output token the order's input would buy right now (and the
     gas cost) — i.e. what a filler routing through public DEXes could deliver;
  3. when an order disappears, reads its fill record (what the real winner delivered, and when).
Paper profit per filled order = our last quote before the fill − what the winner delivered − gas. Positive = we could have matched the
winner's price at about the same moment using public DEX liquidity. Speed (who gets there first) is NOT tested.
Files written next to this script: uniswapx_paper_log.jsonl (every event), uniswapx_paper_summary.txt (updated every 10 minutes).
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
LOG = HERE / "uniswapx_paper_log.jsonl"
SUMMARY = HERE / "uniswapx_paper_summary.txt"


def set_dir(d):
    global LOG, SUMMARY
    p = Path(d)
    p.mkdir(parents=True, exist_ok=True)
    LOG, SUMMARY = p / "uniswapx_paper_log.jsonl", p / "uniswapx_paper_summary.txt"
UX = "https://api.uniswap.org/v2/orders"
KYBER = "https://aggregator-api.kyberswap.com/arbitrum/api/v1/routes"
CHAIN = 42161
NATIVE_UX = "0x0000000000000000000000000000000000000000"
NATIVE_KYBER = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"
FILL_OVERHEAD_USD = 0.10
HEADERS = {"User-Agent": "uniswapx-paper-filler/1.0 (research; read-only)", "Accept": "application/json", "x-client-id": "paperfiller"}


def get(url, timeout=20):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=HEADERS), timeout=timeout) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return {"_error": f"HTTP {e.code}"}
    except Exception as e:  # noqa: BLE001
        return {"_error": f"{type(e).__name__}: {str(e)[:120]}"}


def log(event):
    event["ts"] = round(time.time(), 3)
    with LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(event) + "\n")


def order_legs(o):
    """(input token, input amount to quote, output token, total output start, total output end) or None. Handles V2 and V3 fields."""
    try:
        inp = o["input"]
        in_tok = inp["token"]
        in_amt = max(int(inp.get("startAmount") or 0), int(inp.get("endAmount") or 0), int(inp.get("maxAmount") or 0))
        outs = o.get("outputs") or []
        out_tok = max({x["token"] for x in outs}, key=lambda t: sum(int(x.get("startAmount") or 0) for x in outs if x["token"] == t))
        start = sum(int(x.get("startAmount") or 0) for x in outs if x["token"] == out_tok)
        end = sum(int(x.get("endAmount") or x.get("minAmount") or 0) for x in outs if x["token"] == out_tok)
        return in_tok, in_amt, out_tok, start, end
    except Exception:  # noqa: BLE001
        return None


def excl(o):
    return str(((o.get("cosignerData") or {}).get("exclusiveFiller")) or "").lower()


RPCS = ["https://arb1.arbitrum.io/rpc", "https://arbitrum-one-rpc.publicnode.com", "https://arbitrum.drpc.org"]
FILL_TOPIC = "0x78ad7ec0e9f89e74012afa58738b6b661c024cb0fd185ee2f616c0a28924bd66"
LAST_RPC_ERROR = {"msg": ""}


def actual_filler(tx):
    """Filler address from the Fill event in the fill transaction (public RPCs, plain headers)."""
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_getTransactionReceipt", "params": [tx]}).encode()
    for url in RPCS:
        try:
            req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=20) as r:
                rc = json.loads(r.read().decode()).get("result") or {}
            for lg in rc.get("logs") or []:
                tp = lg.get("topics") or []
                if tp and tp[0].lower() == FILL_TOPIC and len(tp) > 2:
                    return "0x" + tp[2][-40:].lower()
            LAST_RPC_ERROR["msg"] = f"{url}: receipt without Fill event" if rc else f"{url}: empty result"
        except Exception as e:  # noqa: BLE001
            LAST_RPC_ERROR["msg"] = f"{url}: {type(e).__name__}: {str(e)[:100]}"
    return None


def backfill_fillers():
    """Resolve fillers for filled_feed events logged without one (e.g. from earlier sessions)."""
    if not LOG.exists():
        return
    ev = [json.loads(x) for x in LOG.read_text(encoding="utf-8").splitlines() if x.strip()]
    done = {e["hash"] for e in ev if e["event"] == "filler_backfill" and e.get("filler")}
    todo = [e for e in ev if e["event"] == "filled_feed" and not e.get("filler") and e.get("txHash") and e["hash"] not in done]
    n_ok = 0
    for e in todo:
        f = actual_filler(e["txHash"])
        log({"event": "filler_backfill", "hash": e["hash"], "filler": f, "error": None if f else LAST_RPC_ERROR["msg"]})
        n_ok += bool(f)
    print(f"backfill: {n_ok} of {len(todo)} fillers resolved", flush=True)


def kyber_quote(tin, tout, amt):
    q = urllib.parse.urlencode({"tokenIn": NATIVE_KYBER if tin == NATIVE_UX else tin,
                                "tokenOut": NATIVE_KYBER if tout == NATIVE_UX else tout, "amountIn": str(amt), "gasInclude": "true"})
    d = get(f"{KYBER}?{q}")
    rs = ((d or {}).get("data") or {}).get("routeSummary") or {}
    if not rs.get("amountOut"):
        return None
    try:
        return {"out": int(rs["amountOut"]), "out_usd": float(rs.get("amountOutUsd") or 0), "gas_usd": float(rs.get("gasUsd") or 0)}
    except (TypeError, ValueError):
        return None


def fetch_fill(order_hash):
    d = get(f"{UX}?{urllib.parse.urlencode({'orderHash': order_hash, 'chainId': CHAIN})}")
    for o in (d or {}).get("orders") or []:
        if o.get("orderHash") == order_hash:
            return o
    return None


def recent_filled():
    d = get(f"{UX}?{urllib.parse.urlencode({'orderStatus': 'filled', 'chainId': CHAIN, 'limit': 50})}")
    return {o["orderHash"]: o for o in (d or {}).get("orders") or [] if o.get("orderHash")}


def run(hours):
    end_at = time.time() + hours * 3600
    tracked = {}            # orderHash -> {"legs":..., "first_seen":...}
    gone = {}               # orderHash -> time it left the open list
    last_summary = 0.0
    last_feed, recorded = 0.0, set()
    print(f"Paper filler running for {hours} h. Log: {LOG}. Press Ctrl+C to stop early (the log is kept).", flush=True)
    log({"event": "start", "hours": hours})
    backfill_fillers()
    while time.time() < end_at:
        t0 = time.time()
        d = get(f"{UX}?{urllib.parse.urlencode({'orderStatus': 'open', 'chainId': CHAIN, 'limit': 50})}")
        if "_error" in d:
            log({"event": "api_error", "where": "open", "error": d["_error"]})
        open_now = {o["orderHash"]: o for o in (d.get("orders") or []) if o.get("orderHash")}
        for h, o in open_now.items():
            if h not in tracked:
                legs = order_legs(o)
                tracked[h] = {"legs": legs, "first_seen": time.time()}
                log({"event": "new", "hash": h, "type": o.get("type"), "legs": [str(x) for x in legs] if legs else None,
                     "createdAt": o.get("createdAt"), "exclusive": excl(o)})
            legs = tracked[h]["legs"]
            if legs:
                q = kyber_quote(legs[0], legs[2], legs[1])
                if q:
                    log({"event": "quote", "hash": h, "out": str(q["out"]), "out_usd": q["out_usd"], "gas_usd": q["gas_usd"]})
        for h in list(tracked):
            if h not in open_now and h not in gone:
                gone[h] = time.time()
        # fill records: check orders that left the open list (fast path by hash, plus the latest-50 list every ~60 s)
        if gone:
            batch = recent_filled() if int(time.time()) % 60 < 3 else {}
            for h in list(gone):
                rec = batch.get(h) or (fetch_fill(h) if time.time() - gone[h] > 20 else None)
                if rec and rec.get("orderStatus") in ("filled", "expired", "cancelled", "error", "insufficient-funds"):
                    log({"event": "final", "hash": h, "status": rec.get("orderStatus"), "fillTimestamp": rec.get("fillTimestamp"),
                         "fillBlock": rec.get("fillBlock"), "txHash": rec.get("txHash"), "settledAmounts": rec.get("settledAmounts")})
                    gone.pop(h)
                    tracked.pop(h, None)
                elif time.time() - gone[h] > 1800:
                    log({"event": "final", "hash": h, "status": "unknown"})
                    gone.pop(h)
                    tracked.pop(h, None)
        if time.time() - last_feed > 300:
            for h, o in recent_filled().items():
                if h in recorded:
                    continue
                recorded.add(h)
                legs = order_legs(o)
                fl = actual_filler(o.get("txHash")) if o.get("txHash") else None
                log({"event": "filled_feed", "hash": h, "exclusive": excl(o), "filler": fl, "rpc_error": None if fl else LAST_RPC_ERROR["msg"],
                     "createdAt": o.get("createdAt"), "fillTimestamp": o.get("fillTimestamp"), "txHash": o.get("txHash"),
                     "legs": [str(x) for x in legs] if legs else None, "settledAmounts": o.get("settledAmounts")})
            last_feed = time.time()
        if time.time() - last_summary > 600:
            write_summary(quiet=False)
            last_summary = time.time()
        time.sleep(max(0.0, 2.0 - (time.time() - t0)))
    log({"event": "stop"})
    write_summary(quiet=False)


def write_summary(quiet=True):
    if not LOG.exists():
        print("no log yet")
        return
    ev = [json.loads(x) for x in LOG.read_text(encoding="utf-8").splitlines() if x.strip()]
    starts = [e["ts"] for e in ev if e["event"] == "start"]
    hours = 0.0
    if ev:
        # sum of running time over all start..last-event segments
        seg_start = None
        for e in ev:
            if e["event"] == "start":
                seg_start = e["ts"]
            last = e["ts"]
            if e["event"] == "stop" and seg_start is not None:
                hours += (e["ts"] - seg_start) / 3600
                seg_start = None
        if seg_start is not None:
            hours += (last - seg_start) / 3600
    quotes, finals, legs = {}, {}, {}
    for e in ev:
        if e["event"] == "new" and e.get("legs"):
            legs[e["hash"]] = e["legs"]
        elif e["event"] == "quote":
            quotes.setdefault(e["hash"], []).append(e)
        elif e["event"] == "final":
            finals[e["hash"]] = e
    filled = {h: f for h, f in finals.items() if f.get("status") == "filled"}
    rows = []
    for h, f in filled.items():
        lg, qs = legs.get(h), quotes.get(h)
        if not lg or not qs:
            continue
        out_tok = lg[2].lower()
        settled = sum(int(s.get("amountOut") or 0) for s in (f.get("settledAmounts") or []) if str(s.get("tokenOut", "")).lower() == out_tok)
        ft = f.get("fillTimestamp")
        pre = [q for q in qs if ft is None or q["ts"] <= float(ft) + 2]
        q = (pre or qs)[-1]
        out = int(q["out"])
        if out <= 0 or settled <= 0:
            continue
        usd_per_unit = q["out_usd"] / out if q["out_usd"] else 0.0
        profit = (out - settled) * usd_per_unit - q["gas_usd"] - FILL_OVERHEAD_USD
        rows.append({"hash": h, "profit": profit, "vol": settled * usd_per_unit, "bps": 1e4 * (out - settled) / settled})
    n = len(rows)
    comp = [r for r in rows if r["profit"] > 0]
    gross = sum(r["profit"] for r in comp)
    ann = gross * 365 * 24 / hours if hours > 0 else 0.0
    share = len(comp) / n if n else 0.0
    verdict = ("KILL" if (n and (share < 0.05 or ann < 5000)) else
               "worth building a real filler (speed untested)" if (share >= 0.10 and ann >= 15000) else "inconclusive / keep running")
    feed, bf = {}, {}
    for e in ev:
        if e["event"] == "filled_feed":
            feed[e["hash"]] = dict(e)
        elif e["event"] == "filler_backfill" and e.get("filler"):
            bf[e["hash"]] = e["filler"]
    for h, f in bf.items():
        if h in feed and not feed[h].get("filler"):
            feed[h]["filler"] = f
    known = [e for e in feed.values() if e.get("filler") and e.get("exclusive")]
    outsiders = [e for e in known if e["filler"] != e["exclusive"]]
    ex_counts = {}
    for e in feed.values():
        if e.get("exclusive"):
            ex_counts[e["exclusive"]] = ex_counts.get(e["exclusive"], 0) + 1
    top = sorted(ex_counts.values(), reverse=True)
    tot_ex = sum(top) or 1
    out_rows = [r for r in rows if r["hash"] in {e["hash"] for e in outsiders}]
    out_gross = sum(r["profit"] for r in out_rows if r["profit"] > 0)
    out_ann = out_gross * 365 * 24 / hours if hours > 0 else 0.0
    out_share = len(outsiders) / len(known) if known else 0.0
    verdict_b = ("KILL (outsider route)" if known and (out_share < 0.02 or out_ann < 5000) else "outsider route not killed" if known else "n/a")
    lines = [
        f"UniswapX paper filler summary (Arbitrum) — written {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}",
        f"hours run: {hours:.2f}; orders seen: {len(legs)}; final records: {len(finals)} (filled {len(filled)}); "
        f"filled orders with a pre-fill quote: {n}",
        f"competitive (paper profit > 0 at the winner's price): {len(comp)} ({share:.1%})",
        f"paper profit on competitive orders: ${gross:,.2f} -> annualised ${ann:,.0f}/yr",
        f"median gap our quote vs winner: {sorted(r['bps'] for r in rows)[n // 2]:.1f} bps" if n else "median gap: n/a",
        f"volume of measured fills: ${sum(r['vol'] for r in rows):,.0f}",
        f"pre-registered verdict so far: {verdict} (needs >= 36 h / ~200 filled orders to count)",
        f"[Stage 5b] filled orders from the feed: {len(feed)}; with exclusive + actual filler known: {len(known)}",
        f"[Stage 5b] filled by an outsider (actual filler != exclusive filler): {len(outsiders)} ({out_share:.1%})",
        f"[Stage 5b] quoter concentration (exclusivity): top-1 {top[0] / tot_ex if top else 0:.0%}, top-3 {sum(top[:3]) / tot_ex:.0%}, quoters {len(top)}",
        f"[Stage 5b] paper profit on outsider fills we quoted: ${out_gross:,.2f} -> ${out_ann:,.0f}/yr; verdict: {verdict_b}",
    ]
    SUMMARY.write_text("\n".join(lines) + "\n", encoding="utf-8")
    if not quiet:
        print("\n".join(lines), flush=True)
    return lines


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hours", type=float, default=36.0)
    ap.add_argument("--summarize", action="store_true")
    ap.add_argument("--dir", default=None, help="folder for the log and summary (default: next to this script)")
    a = ap.parse_args()
    if a.dir:
        set_dir(a.dir)
    if a.summarize:
        write_summary(quiet=False)
        return
    try:
        run(a.hours)
    except KeyboardInterrupt:
        log({"event": "stop"})
        print("\nStopped by you.", flush=True)
        write_summary(quiet=False)


if __name__ == "__main__":
    sys.exit(main())

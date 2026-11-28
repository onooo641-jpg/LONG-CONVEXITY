"""Radar non-prop sources N1-N9 (N6 dropped, addendum 1) (docs/PREREG_RADAR_NONPROP_20261124.md). Called from scripts/radar.py.

N4, N8 and N9 page-watch rows live in docs/radar/watchlist.csv (kinds contest, promo_my, regulator_my, bot_docs); this module turns their
page changes into leads. Thresholds are fixed in the pre-registration; do not tune after seeing leads.
"""
from __future__ import annotations

import html
import re
import time
import urllib.parse
from datetime import timedelta
from pathlib import Path

import pandas as pd

N1_MIN_CIRC, N1_LO, N1_HI = 10e6, 0.985, 1.015
N2_MIN_ANN, N2_MIN_OI = 1.00, 2e6
N3_MIN_USD, N3_DAYS = 1000.0, 21
N4_MIN_PRIZE = 50_000
N7_MIN_VOL, N7_MIN_CHG = 20e6, 100.0
N5_DAYS = 14
N5_RE = re.compile(r"incentiv|reward|liquidat|solver|keeper|relayer|filler|market[- ]?mak|liquidity provider program|\bLP program|"
                   r"grant|points|competition|subsid|rebate|bounty|airdrop|retro|prover|operator program|rebalancer|searcher|\bOEV\b",
                   re.I)
FORUMS = {"aave": "https://governance.aave.com/latest.rss", "compound": "https://www.comp.xyz/latest.rss",
          "morpho": "https://forum.morpho.org/latest.rss", "cow": "https://forum.cow.fi/latest.rss",
          "uniswap": "https://gov.uniswap.org/latest.rss", "arbitrum": "https://forum.arbitrum.foundation/latest.rss",
          "optimism": "https://gov.optimism.io/latest.rss", "lido": "https://research.lido.fi/latest.rss",
          "sky": "https://forum.sky.money/latest.rss", "balancer": "https://forum.balancer.fi/latest.rss",
          "gmx": "https://gov.gmx.io/latest.rss", "dydx": "https://dydx.forum/latest.rss",
          # addendum 2: more ecosystems
          "curve": "https://gov.curve.finance/latest.rss", "jupiter": "https://www.jupresear.ch/latest.rss",
          "gnosis": "https://forum.gnosis.io/latest.rss", "frax": "https://gov.frax.finance/latest.rss",
          "across": "https://forum.across.to/latest.rss", "ethena": "https://gov.ethenafoundation.com/latest.rss",
          "polygon": "https://forum.polygon.technology/latest.rss", "zksync": "https://forum.zknation.io/latest.rss",
          "scroll": "https://forum.scroll.io/latest.rss", "mantle": "https://forum.mantle.xyz/latest.rss",
          "celo": "https://forum.celo.org/latest.rss"}
COW_SAFE = "0xA03be496e67Ec29bC62F01a428683D7F9c204930"
COW_TOKEN = "0xDEf1CA1fb7FBcDC777520aa7f396b4E015F497aB"
PRIZE_RE = re.compile(r"(?:\$|USDC\s?|USD\s?)\s?([\d][\d,]{2,}(?:\.\d+)?)\s?([kKmM])?|([\d][\d,]{2,})\s?(?:USDC|USD)\b")
PROMO_RE = re.compile(r"(RM\s?\d|\$\s?\d|USD\s?\d)", re.I)
PROMO_WORD = re.compile(r"bonus|reward|cash|free|promo|campaign|voucher|rebate|giveaway", re.I)


def _lead(rows, today, src, item, venue, what, metric=None, url=""):
    rows.append({"lead_id": f"{src}:{item}", "source": src, "venue": venue, "what": str(what)[:240], "metric": metric, "url": url,
                 "date": today})


def n1_depegs(jget, today, rows, health):
    d = jget("https://stablecoins.llama.fi/stablecoins?includePrices=true") or {}
    assets = d.get("peggedAssets") or []
    health["N1 stablecoins"] = len(assets)
    for a in assets:
        if a.get("pegType") != "peggedUSD":
            continue
        circ = ((a.get("circulating") or {}).get("peggedUSD")) or 0
        px = a.get("price")
        try:
            px = float(px)
        except (TypeError, ValueError):
            continue
        if circ >= N1_MIN_CIRC and (px < N1_LO or px > N1_HI):
            _lead(rows, today, "N1", f"{a.get('symbol')}", a.get("symbol"), f"{a.get('name')} at ${px:.4f}, circulating ${circ:,.0f}",
                  px, f"https://defillama.com/stablecoin/{urllib.parse.quote(str(a.get('name', '')).lower())}")


def n2_funding(fetch, today, rows, health):
    import json
    s, t = fetch("https://api.hyperliquid.xyz/info", post={"type": "metaAndAssetCtxs"}, accept="application/json")
    try:
        meta, ctxs = json.loads(t)
    except Exception:  # noqa: BLE001
        health["N2 Hyperliquid perps"] = "failed"
        return
    uni = meta.get("universe") or []
    health["N2 Hyperliquid perps"] = len(uni)
    for u, c in zip(uni, ctxs):
        try:
            ann = float(c.get("funding")) * 24 * 365
            oi = float(c.get("openInterest")) * float(c.get("markPx"))
        except (TypeError, ValueError):
            continue
        if abs(ann) >= N2_MIN_ANN and oi >= N2_MIN_OI:
            _lead(rows, today, "N2", f"{u.get('name')}", u.get("name"), f"funding {ann:+.0%}/yr, open interest ${oi:,.0f}", ann,
                  f"https://app.hyperliquid.xyz/trade/{u.get('name')}")


def n3_cow(jget, today, rows, health, out: Path, root: Path):
    hist_f = out / "cow_recipients.parquet"
    if hist_f.exists():
        hist = pd.read_parquet(hist_f)
    else:
        seed = root / "data" / "public" / "solverrelay_cow.parquet"
        hist = pd.read_parquet(seed)[["to"]].drop_duplicates().assign(first_seen="2026-11-23") if seed.exists() else \
            pd.DataFrame(columns=["to", "first_seen"])
    px = ((jget("https://coins.llama.fi/prices/current/coingecko:cow-protocol") or {}).get("coins") or {}).get(
        "coingecko:cow-protocol", {}).get("price")
    cut = pd.Timestamp(today, tz="UTC") - timedelta(days=N3_DAYS)
    base = f"https://eth.blockscout.com/api/v2/addresses/{COW_SAFE}/token-transfers?type=ERC-20&filter=from&token={COW_TOKEN}"
    url, got, pages = base, [], 0
    while url and pages < 40:
        d = jget(url) or {}
        pages += 1
        items = d.get("items") or []
        stop = False
        for it in items:
            ts = pd.Timestamp(it.get("timestamp")) if it.get("timestamp") else None
            if ts is not None and ts < cut:
                stop = True
                continue
            tot = it.get("total") or {}
            got.append({"to": str((it.get("to") or {}).get("hash", "")).lower(),
                        "cow": int(tot.get("value") or 0) / 10 ** int(tot.get("decimals") or 18), "ts": ts})
        nxt = d.get("next_page_params")
        if stop or not nxt or not items:
            break
        url = base + "&" + urllib.parse.urlencode(nxt)
        time.sleep(0.25)
    g = pd.DataFrame(got)
    health["N3 CoW payouts (21d)"] = f"{len(g)} transfers, COW price {px}"
    if g.empty:
        return
    g["usd"] = g["cow"] * (px or 0)
    by = g.groupby("to")["usd"].sum().sort_values(ascending=False)
    health["N3 CoW payouts (21d)"] += f", ${by.sum():,.0f} to {len(by)} recipients"
    known = set(hist["to"])
    for addr, usd in by.items():
        if addr not in known and usd >= N3_MIN_USD:
            _lead(rows, today, "N3", addr, "CoW solver payouts", f"new recipient {addr} paid ${usd:,.0f} in the last {N3_DAYS} days", usd,
                  f"https://etherscan.io/address/{addr}")
    new = pd.DataFrame({"to": [a for a in by.index if a not in known], "first_seen": today})
    pd.concat([hist, new], ignore_index=True).drop_duplicates("to").to_parquet(hist_f, index=False)


def n5_forums(fetch, today, rows, health):
    cut = pd.Timestamp(today, tz="UTC") - timedelta(days=N5_DAYS)
    ok = 0
    for name, url in FORUMS.items():
        s, t = fetch(url, tries=2, timeout=30)
        if s != 200 or not t:
            continue
        ok += 1
        for item in re.findall(r"(?s)<item>(.*?)</item>", t):
            title = html.unescape(re.sub(r"<!\[CDATA\[|\]\]>", "", (re.search(r"(?s)<title>(.*?)</title>", item) or [None, ""])[1])).strip()
            link = (re.search(r"(?s)<link>(.*?)</link>", item) or [None, ""])[1].strip()
            pub = (re.search(r"(?s)<pubDate>(.*?)</pubDate>", item) or [None, ""])[1].strip()
            try:
                when = pd.Timestamp(pub).tz_convert("UTC") if pub else None
            except Exception:  # noqa: BLE001
                when = None
            if when is not None and when < cut:
                continue
            if N5_RE.search(title):
                _lead(rows, today, "N5", f"{name}:{link or title[:60]}", name, title, None, link)
    health["N5 forums answering"] = f"{ok}/{len(FORUMS)}"


def _num(v):
    try:
        return float(str(v).replace(",", ""))
    except (TypeError, ValueError):
        return None


def _prize(item):
    best = None
    for k, v in item.items():
        vals = v.items() if isinstance(v, dict) else [(k, v)]
        for kk, vv in vals:
            if re.search(r"prize|reward|pool|total", f"{k} {kk}", re.I):
                x = _num(vv)
                if x is not None and (best is None or x > best):
                    best = x
    return best


def n4_contests(jget, today, rows, health, out: Path):
    """Sherlock and Cantina contest APIs (addendum 1): new contest with prize >= $50K."""
    seen_f = out / "contests_seen.parquet"
    seen = set(pd.read_parquet(seen_f)["cid"]) if seen_f.exists() else set()
    items = []
    for page in (1, 2, 3):
        d = jget(f"https://audits.sherlock.xyz/api/contests?page={page}") or {}
        for it in d.get("items") or []:
            items.append(("sherlock", str(it.get("id")), it.get("title"), _num(it.get("prize_pool")) or _prize(it), it.get("status"),
                          f"https://audits.sherlock.xyz/contests/{it.get('id')}"))
        if not d.get("next_page"):
            break
    d = jget("https://cantina.xyz/api/v0/competitions") or []
    lst = d if isinstance(d, list) else (d.get("items") or d.get("data") or [])
    if lst:
        health["N4 Cantina item keys"] = ",".join(sorted(lst[0].keys()))[:200]
    for it in lst:
        items.append(("cantina", str(it.get("id")), it.get("name") or it.get("title"), _prize(it), it.get("status") or it.get("state"),
                      it.get("url") or ""))
    from collections import Counter
    health["N4 statuses"] = dict(Counter(f"{x[0]}:{x[4]}" for x in items).most_common(12))
    health["N4 contests listed"] = f"{sum(1 for x in items if x[0] == 'sherlock')} Sherlock, {sum(1 for x in items if x[0] == 'cantina')} Cantina"
    for src, cid, title, prize, status, url in items:
        key = f"{src}:{cid}"
        if key not in seen and prize is not None and prize >= N4_MIN_PRIZE and \
                not re.search(r"finish|complete|ended|closed|escalat|judg|review|result", str(status), re.I):
            _lead(rows, today, "N4", key, src, f"{title} — prize ${prize:,.0f} ({status})", prize, url)
    pd.DataFrame({"cid": sorted(seen | {f"{x[0]}:{x[1]}" for x in items})}).to_parquet(seen_f, index=False)


def n7_cg(jget, today, rows, health, out: Path):
    """Perp-venue volume surges from CoinGecko derivatives exchanges (addendum 1: DefiLlama overview is now HTTP 402)."""
    d = jget("https://api.coingecko.com/api/v3/derivatives/exchanges?per_page=100") or []
    btc = ((jget("https://coins.llama.fi/prices/current/coingecko:bitcoin") or {}).get("coins") or {}).get("coingecko:bitcoin", {}).get("price")
    health["N7 derivatives venues (CoinGecko)"] = f"{len(d)}; BTC ${btc}"
    if not d or not btc:
        return
    hist_f = out / "derivs_cg.parquet"
    hist = pd.read_parquet(hist_f) if hist_f.exists() else pd.DataFrame(columns=["date", "name", "vol_usd"])
    now = pd.DataFrame([{"date": today, "name": x.get("name"), "vol_usd": (_num(x.get("trade_volume_24h_btc")) or 0) * btc} for x in d])
    known = set(hist["name"])
    wk = (pd.Timestamp(today) - timedelta(days=7)).strftime("%Y-%m-%d")
    past = hist[hist["date"] <= wk].sort_values("date").groupby("name")["vol_usd"].last()
    for r in now.itertuples():
        if r.vol_usd < N7_MIN_VOL:
            continue
        p0 = past.get(r.name)
        if p0 and r.vol_usd >= 2 * p0:
            _lead(rows, today, "N7", r.name, r.name, f"24h volume ${r.vol_usd:,.0f}, {r.vol_usd / p0:.1f}x the level 7+ days ago", r.vol_usd)
        elif known and r.name not in known:
            _lead(rows, today, "N7", r.name, r.name, f"new derivatives venue in CoinGecko's list, 24h volume ${r.vol_usd:,.0f}", r.vol_usd)
    pd.concat([hist[hist["date"] != today], now], ignore_index=True).to_parquet(hist_f, index=False)

def page_leads(changes_today, today, rows):
    """N4 contest prizes, N8 Malaysia promos, N9 access/bot-docs changes, from today's page diffs."""
    if changes_today is None or changes_today.empty:
        return
    for x in changes_today.itertuples():
        add = x.added or ""
        if x.kind == "contest":
            amts = []
            for m in PRIZE_RE.finditer(add):
                num = m.group(1) or m.group(3)
                try:
                    v = float(num.replace(",", "")) * {"": 1, "k": 1e3, "m": 1e6}[(m.group(2) or "").lower()]
                except (ValueError, AttributeError):
                    continue
                amts.append(v)
            if amts and max(amts) >= N4_MIN_PRIZE:
                _lead(rows, today, "N4", f"{x.slug}:{today}", x.name, f"page changed; largest amount in added text ${max(amts):,.0f}",
                      max(amts), x.url)
        elif x.kind == "promo_my":
            hits = [ln for ln in add.splitlines() if PROMO_RE.search(ln) and PROMO_WORD.search(ln)]
            if hits:
                _lead(rows, today, "N8", f"{x.slug}:{today}", x.name, " / ".join(h[:120] for h in hits[:3]), None, x.url)
        elif x.kind in ("regulator_my", "bot_docs", "mm_program"):
            first = [ln for ln in add.splitlines() if len(ln) > 15][:2]
            _lead(rows, today, "N9", f"{x.slug}:{today}", x.name, "changed: " + " / ".join(f[:120] for f in first), None, x.url)


# ------------------------------------------------------------------ N10 / N11 (addendum 4): forward paper logs for #389 S2c and #385
HL_INFO = "https://api.hyperliquid.xyz/info"
WICK_X, WICK_THROUGH, WICK_CAP, WICK_VOL, WICK_START = 0.15, 0.005, 1500.0, 0.01, "2026-12-01"
WICK_MAKER, WICK_TAKER, WICK_POT = 0.00015, 0.00045, 15_000.0


def n10_n11_hyperliquid(fetch, today, rows, health, out: Path):
    """N10: paper fills of the #389 rule on every live Hyperliquid perp (completed UTC days from 2026-12-01).
    N11: perps first listed in the last 3 days (candidates for the #385 pre-launch forward log)."""
    import json as _j
    _, t = fetch(HL_INFO, post={"type": "meta"})
    uni = (_j.loads(t) if t else {}).get("universe", [])
    live = [u["name"] for u in uni if not u.get("isDelisted")]
    day0 = pd.Timestamp(today, tz="UTC").normalize()
    start = day0 - pd.Timedelta(days=45)
    recs, recs520 = [], []
    for c in live:
        _, t = fetch(HL_INFO, post={"type": "candleSnapshot", "req": {"coin": c, "interval": "1d", "startTime": int(start.timestamp() * 1000),
                                                                        "endTime": int(day0.timestamp() * 1000)}}, tries=2)
        k = _j.loads(t) if t else []
        time.sleep(0.25)
        if not k:
            continue
        d = pd.DataFrame(k)
        d["day"] = pd.to_datetime(d["t"], unit="ms", utc=True).dt.normalize()
        for col in ("o", "h", "l", "c", "v"):
            d[col] = d[col].astype(float)
        d = d.drop_duplicates("day").sort_values("day").reset_index(drop=True)
        first = d["day"].iloc[0]
        if first > start + pd.Timedelta(days=1) and first >= day0 - pd.Timedelta(days=3):
            _lead(rows, today, "N11", f"hl_new_{c}", "Hyperliquid", f"new perp {c} listed {first.date()} (check pre-launch: #385 forward log)",
                  None, "https://app.hyperliquid.xyz/trade/" + c)
        listed_long = first <= start + pd.Timedelta(days=1)
        # #520 (docs/PREREG_WICK_FAMILY_20261128.md): distance = 4 x sigma of the previous 30 daily returns, clipped 5%..30%
        sig30 = d["c"].pct_change().rolling(30).std().shift()
        for i in range(1, len(d)):
            r, p = d.iloc[i], d.iloc[i - 1]
            if r["day"] >= day0 or str(r["day"].date()) < WICK_START:
                continue
            if not listed_long and r["day"] < first + pd.Timedelta(days=30):
                continue
            x520 = sig30.iloc[i]
            if pd.notna(x520):
                lv2 = p["c"] * (1 - min(max(4 * x520, 0.05), 0.30))
                if r["l"] <= lv2 * (1 - WICK_THROUGH):
                    px2 = min(lv2, r["o"])
                    nxt = d["c"].iloc[i + 1] if i + 1 < len(d) and d["day"].iloc[i + 1] < day0 else None  # #522: next day's close
                    recs520.append({"coin": c, "day": str(r["day"].date()), "level": lv2, "fill": px2, "close": r["c"],
                                    "ret": r["c"] / px2 - 1 - WICK_MAKER - WICK_TAKER, "size": min(WICK_CAP, WICK_VOL * p["v"] * p["c"]),
                                    "ret522": (nxt / px2 - 1 - WICK_MAKER - WICK_TAKER) if nxt is not None else None})
            lvl = p["c"] * (1 - WICK_X)
            if r["l"] > lvl * (1 - WICK_THROUGH):
                continue
            px = min(lvl, r["o"])
            size = min(WICK_CAP, WICK_VOL * p["v"] * p["c"])
            recs.append({"coin": c, "day": str(r["day"].date()), "level": lvl, "fill": px, "close": r["c"],
                         "ret": r["c"] / px - 1 - WICK_MAKER - WICK_TAKER, "size": size})
    f = out / "wick_paper.parquet"
    old = pd.read_parquet(f) if f.exists() else pd.DataFrame(columns=["coin", "day", "level", "fill", "close", "ret", "size"])
    new = pd.DataFrame(recs, columns=old.columns)
    allr = pd.concat([old, new[~(new["coin"] + new["day"]).isin(old["coin"] + old["day"])]], ignore_index=True)
    allr.to_parquet(f, index=False)
    if len(allr):
        day_sz = allr.groupby("day")["size"].transform("sum")
        pnl = (allr["size"] * (WICK_POT / day_sz).clip(upper=1.0) * allr["ret"]).sum()
        health["N10 wick paper (#389 S2c)"] = (f"{len(allr)} fills since {WICK_START}; mean net {allr['ret'].mean():.2%}; paper P&L ${pnl:,.0f}; "
                                              f"new today {len(allr) - len(old)}")
    else:
        health["N10 wick paper (#389 S2c)"] = f"0 fills since {WICK_START} ({len(live)} live perps checked)"
    f2 = out / "wick520_paper.parquet"
    cols2 = ["coin", "day", "level", "fill", "close", "ret", "size", "ret522"]
    old2 = pd.read_parquet(f2) if f2.exists() else pd.DataFrame(columns=cols2)
    old2 = old2.reindex(columns=cols2)
    new2 = pd.DataFrame(recs520, columns=cols2)
    # a fill's next-day close is known only a day later: refresh ret522 for fills already logged
    if len(old2) and len(new2):
        upd = new2.set_index(old2.columns[0:1].tolist() + ["day"])["ret522"]
        key = old2.set_index(["coin", "day"]).index
        old2["ret522"] = [upd.get(k, v) if pd.isna(v) else v for k, v in zip(key, old2["ret522"])]
    all2 = pd.concat([old2, new2[~(new2["coin"] + new2["day"]).isin(old2["coin"] + old2["day"])]], ignore_index=True)
    all2.to_parquet(f2, index=False)
    health["N10b wick paper (#520 S2c)"] = (f"{len(all2)} fills since {WICK_START}; mean net {all2['ret'].mean():.2%}" if len(all2)
                                           else f"0 fills since {WICK_START}")


# ------------------------------------------------------------------ N13: forward paper log for #536 (docs/PREREG_BATCH_NF_20261128.md)
ASTER = "https://fapi.asterdex.com/fapi/v1"


def n13_aster_new(fetch, today, rows, health, out: Path):
    """N13: #536 paper fills on Aster perps in their first 30 days (bid at previous close x 0.85, exit at the close), from 2026-12-01."""
    import json as _j
    _, t = fetch(f"{ASTER}/exchangeInfo")
    syms = (_j.loads(t) if t else {}).get("symbols", [])
    day0 = pd.Timestamp(today, tz="UTC").normalize()
    recs = []
    for sd in syms:
        if sd.get("contractType") != "PERPETUAL" or not sd.get("onboardDate"):
            continue
        first = pd.Timestamp(int(sd["onboardDate"]), unit="ms", tz="UTC").normalize()
        if first < day0 - pd.Timedelta(days=31):
            continue
        _, kt = fetch(f"{ASTER}/klines?symbol={sd['symbol']}&interval=1d&limit=40", tries=2)
        k = _j.loads(kt) if kt else []
        time.sleep(0.25)
        for i in range(1, len(k)):
            day = pd.Timestamp(int(k[i][0]), unit="ms", tz="UTC").normalize()
            if day >= day0 or str(day.date()) < WICK_START or day >= first + pd.Timedelta(days=30):
                continue
            prev_c, o, low, c, qv = float(k[i - 1][4]), float(k[i][1]), float(k[i][3]), float(k[i][4]), float(k[i][7])
            lvl = prev_c * 0.85
            if low > lvl * (1 - WICK_THROUGH):
                continue
            px = min(lvl, o)
            recs.append({"coin": sd["symbol"], "day": str(day.date()), "fill": px, "close": c,
                         "ret": c / px - 1 - 0.0002 - 0.0005, "size": min(WICK_CAP, WICK_VOL * qv)})
    f = out / "aster_new_paper.parquet"
    cols = ["coin", "day", "fill", "close", "ret", "size"]
    old = pd.read_parquet(f) if f.exists() else pd.DataFrame(columns=cols)
    new = pd.DataFrame(recs, columns=cols)
    allr = pd.concat([old, new[~(new["coin"] + new["day"]).isin(old["coin"] + old["day"])]], ignore_index=True)
    allr.to_parquet(f, index=False)
    health["N13 Aster new-perp wick paper (#536 S2c)"] = (f"{len(allr)} fills since {WICK_START}; mean net {allr['ret'].mean():.2%}"
                                                          if len(allr) else f"0 fills since {WICK_START}")


def n12_korea(fetch, today, rows, health, out: Path):
    """N12: new Upbit/Bithumb KRW markets -> paper short on Hyperliquid (#395 forward log)."""
    import json as _j
    _, t = fetch("https://api.upbit.com/v1/market/all?isDetails=false")
    up = {m["market"][4:] for m in (_j.loads(t) if t else []) if str(m.get("market", "")).startswith("KRW-")}
    _, t = fetch("https://api.bithumb.com/public/ticker/ALL_KRW")
    bt = {c for c in ((_j.loads(t) if t else {}).get("data") or {}) if c != "date"}
    seen_f = out / "korea_markets.json"
    seen = set(_j.loads(seen_f.read_text())) if seen_f.exists() else None
    now = up | bt
    if not now:
        health["N12 Korea listings (#395)"] = "market lists unavailable"
        return
    seen_f.write_text(_j.dumps(sorted(now | (seen or set()))))
    if seen is None:
        health["N12 Korea listings (#395)"] = f"baseline saved ({len(now)} markets); new listings logged from the next run"
        return
    new = sorted(now - seen)
    _, t = fetch(HL_INFO, post={"type": "meta"})
    hl = {u["name"] for u in (_j.loads(t) if t else {}).get("universe", []) if not u.get("isDelisted")}
    f = out / "korea_paper.parquet"
    log = pd.read_parquet(f) if f.exists() else pd.DataFrame(columns=["coin", "listed", "venue", "on_hl"])
    add = [{"coin": c, "listed": today, "venue": "upbit" if c in up else "bithumb", "on_hl": c in hl} for c in new]
    for a in add:
        _lead(rows, today, "N12", f"kr_{a['coin']}_{today}", a["venue"], f"new KRW listing {a['coin']} (on Hyperliquid: {a['on_hl']}) — #395 paper short",
              None, "")
    if add:
        log = pd.concat([log, pd.DataFrame(add)], ignore_index=True)
        log.to_parquet(f, index=False)
    health["N12 Korea listings (#395)"] = f"{len(log)} logged since start, {int(log['on_hl'].sum()) if len(log) else 0} on Hyperliquid; new today {len(add)}"


def run(fetch, jget, today, out: Path, root: Path, changes_today):
    """Returns (leads_all, new_today, health)."""
    rows, health = [], {}
    for name, fn in (("N1", lambda: n1_depegs(jget, today, rows, health)), ("N2", lambda: n2_funding(fetch, today, rows, health)),
                     ("N3", lambda: n3_cow(jget, today, rows, health, out, root)), ("N5", lambda: n5_forums(fetch, today, rows, health)),
                     ("N4", lambda: n4_contests(jget, today, rows, health, out)), ("N7", lambda: n7_cg(jget, today, rows, health, out)),
                     ("N4/N8/N9", lambda: page_leads(changes_today, today, rows)),
                     ("N10/N11", lambda: n10_n11_hyperliquid(fetch, today, rows, health, out)),
                     ("N13", lambda: n13_aster_new(fetch, today, rows, health, out)),
                     ("N12", lambda: n12_korea(fetch, today, rows, health, out))):
        try:
            fn()
        except Exception as e:  # noqa: BLE001
            health[f"{name} ERROR"] = f"{type(e).__name__}: {str(e)[:120]}"
            print(f"  radar_nonprop {name} failed: {e}", flush=True)
    new = pd.DataFrame(rows, columns=["lead_id", "source", "venue", "what", "metric", "url", "date"])
    f = out / "leads.parquet"
    old = pd.read_parquet(f) if f.exists() else pd.DataFrame(columns=list(new.columns) + ["first_seen", "last_seen"])
    new = new.drop_duplicates("lead_id", keep="first")
    first = dict(zip(old["lead_id"], old["first_seen"])) if len(old) else {}
    last = dict(zip(old["lead_id"], old["last_seen"])) if len(old) else {}
    gap = (pd.Timestamp(today) - timedelta(days=14)).strftime("%Y-%m-%d")
    # a lead is new the first time, or again after 14+ days without being seen (persistent conditions are not re-announced daily)
    renew = new["lead_id"].map(last).fillna("0000") < gap
    new["first_seen"] = new["lead_id"].map(first).where(~renew, today).fillna(today)
    new["last_seen"] = today
    allr = pd.concat([old[~old["lead_id"].isin(new["lead_id"])], new], ignore_index=True)
    allr["metric"] = pd.to_numeric(allr["metric"], errors="coerce")
    allr.to_parquet(f, index=False)
    fresh = new[new["first_seen"] == today]
    print(f"radar_nonprop: leads today {len(new)}, new {len(fresh)}; health {health}", flush=True)
    return allr, fresh, health


def summary_lines(fresh, health):
    L = ["", "## Non-prop leads (docs/PREREG_RADAR_NONPROP_20261124.md): new today " + str(len(fresh)), ""]
    names = {"N1": "Stablecoin depegs", "N2": "Extreme funding", "N3": "New CoW solver recipients", "N4": "Audit contest prizes",
             "N5": "Governance: incentives / bot programmes", "N7": "Perp-venue volume surges",
             "N8": "Malaysia promotions", "N9": "Malaysia access / bot-role docs / market-maker programme changes",
             "N11": "New Hyperliquid perps (pre-launch candidates, #385)", "N12": "New Korean KRW listings (#395 forward log)"}
    for src, nm in names.items():
        x = fresh[fresh["source"] == src]
        if len(x):
            L.append(f"### {nm} ({len(x)})")
            L += [f"- {r.venue}: {r.what} {r.url}" for r in x.head(15).itertuples()]
            L.append("")
    L += ["### Source health"] + [f"- {k}: {v}" for k, v in health.items()]
    return L

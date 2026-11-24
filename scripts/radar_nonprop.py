"""Radar non-prop sources N1-N8 (docs/PREREG_RADAR_NONPROP_20261124.md). Called from scripts/radar.py.

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
N6_DAYS, N6_MIN_M = 14, 5.0
N6_CATS = re.compile(r"dex|derivative|lending|yield|cdp|liquid staking|bridge|rwa|launchpad|perp", re.I)
N7_MIN_VOL, N7_MIN_CHG = 20e6, 100.0
N5_DAYS = 14
N5_RE = re.compile(r"incentiv|reward|liquidat|solver|keeper|relayer|filler|market[- ]?mak|liquidity provider program|\bLP program|"
                   r"grant|points|competition|subsid|rebate|bounty|airdrop|retro", re.I)
FORUMS = {"aave": "https://governance.aave.com/latest.rss", "compound": "https://www.comp.xyz/latest.rss",
          "morpho": "https://forum.morpho.org/latest.rss", "cow": "https://forum.cow.fi/latest.rss",
          "uniswap": "https://gov.uniswap.org/latest.rss", "arbitrum": "https://forum.arbitrum.foundation/latest.rss",
          "optimism": "https://gov.optimism.io/latest.rss", "lido": "https://research.lido.fi/latest.rss",
          "sky": "https://forum.sky.money/latest.rss", "balancer": "https://forum.balancer.fi/latest.rss",
          "gmx": "https://gov.gmx.io/latest.rss", "dydx": "https://dydx.forum/latest.rss"}
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


def n6_raises(jget, today, rows, health):
    d = jget("https://api.llama.fi/raises") or {}
    rs = d.get("raises") or []
    health["N6 raises listed"] = len(rs)
    cut = (pd.Timestamp(today, tz="UTC") - timedelta(days=N6_DAYS)).timestamp()
    for r in rs:
        try:
            amt = float(r.get("amount") or 0)
            when = float(r.get("date") or 0)
        except (TypeError, ValueError):
            continue
        cat = f"{r.get('category') or ''} {r.get('sector') or ''}"
        if when >= cut and amt >= N6_MIN_M and N6_CATS.search(cat):
            _lead(rows, today, "N6", f"{r.get('name')}:{int(when)}", r.get("name"),
                  f"raised ${amt:,.0f}M ({r.get('round') or '?'}), {cat.strip()}, chains {r.get('chains')}", amt, r.get("source") or "")


def n7_derivs(jget, today, rows, health, out: Path):
    d = jget("https://api.llama.fi/overview/derivatives?excludeTotalDataChart=true&excludeTotalDataChartBreakdown=true") or {}
    ps = d.get("protocols") or []
    health["N7 derivatives venues"] = len(ps)
    seen_f = out / "derivs_seen.parquet"
    seen = set(pd.read_parquet(seen_f)["name"]) if seen_f.exists() else None
    names = []
    for p in ps:
        name = p.get("name")
        names.append(name)
        try:
            v = float(p.get("total24h") or 0)
            chg = float(p.get("change_7d") or 0)
        except (TypeError, ValueError):
            continue
        if v >= N7_MIN_VOL and (chg >= N7_MIN_CHG or (seen is not None and name not in seen)):
            why = f"7-day change {chg:+.0f}%" if chg >= N7_MIN_CHG else "new venue in the list"
            _lead(rows, today, "N7", f"{name}", name, f"24h volume ${v:,.0f}; {why}", v,
                  f"https://defillama.com/protocol/{urllib.parse.quote(str(p.get('slug') or name))}")
    pd.DataFrame({"name": sorted(set(names) | (seen or set()))}).to_parquet(seen_f, index=False)


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
        elif x.kind in ("regulator_my", "bot_docs"):
            first = [ln for ln in add.splitlines() if len(ln) > 15][:2]
            _lead(rows, today, "N9", f"{x.slug}:{today}", x.name, "changed: " + " / ".join(f[:120] for f in first), None, x.url)


def run(fetch, jget, today, out: Path, root: Path, changes_today):
    """Returns (leads_all, new_today, health)."""
    rows, health = [], {}
    for name, fn in (("N1", lambda: n1_depegs(jget, today, rows, health)), ("N2", lambda: n2_funding(fetch, today, rows, health)),
                     ("N3", lambda: n3_cow(jget, today, rows, health, out, root)), ("N5", lambda: n5_forums(fetch, today, rows, health)),
                     ("N6", lambda: n6_raises(jget, today, rows, health)), ("N7", lambda: n7_derivs(jget, today, rows, health, out)),
                     ("N4/N8/N9", lambda: page_leads(changes_today, today, rows))):
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
             "N5": "Governance: incentives / bot programmes", "N6": "New funding rounds", "N7": "Perp-venue volume surges",
             "N8": "Malaysia promotions", "N9": "Malaysia access / bot-role docs changes"}
    for src, nm in names.items():
        x = fresh[fresh["source"] == src]
        if len(x):
            L.append(f"### {nm} ({len(x)})")
            L += [f"- {r.venue}: {r.what} {r.url}" for r in x.head(15).itertuples()]
            L.append("")
    L += ["### Source health"] + [f"- {k}: {v}" for k, v in health.items()]
    return L

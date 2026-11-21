"""Radar collector (docs/PREREG_RADAR_20261121.md). Runs on GitHub Actions (the sandbox cannot reach these hosts).

    python scripts/radar.py            # all sources; first run = baseline sweep, later runs diff against it

Outputs in data/radar/: candidates.parquet, nearmiss.parquet, pages.parquet, changes.parquet, deep.parquet,
discovered_domains.parquet, snapshots/<slug>.txt, latest_summary.md, propfirm_snippets.md.
Stdlib HTTP + pandas. Public sources only, no keys. Every failed request is printed.
"""
from __future__ import annotations

import concurrent.futures as cf
import difflib
import hashlib
import html
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "radar"
SNAP = OUT / "snapshots"
CFG = ROOT / "docs" / "radar"
NOW = datetime.now(timezone.utc)
TODAY = NOW.strftime("%Y-%m-%d")
UA = "Mozilla/5.0 (compatible; long-convexity-research/1.0; +https://github.com/onooo641-jpg/LONG-CONVEXITY)"
LOG = {"ok": 0, "fail": 0}

# ---- thresholds: fixed in docs/PREREG_RADAR_20261121.md, do not tune after seeing results
MIN_APY_REWARD, MIN_TVL, MIN_BUDGET_DAY = 3.0, 50_000, 20.0
MAX_APR_PLAUSIBLE = 1000.0
F1_SHARE, F1_DAYS = 0.70, 180
F2_AGE_DAYS = 365
F5_TVL = 1_000_000
NEW_PROTOCOL_DAYS, NEW_PROTOCOL_TVL = 30, 1_000_000
DEEP_TOP = 60
STABLE_TOK = {"USDC", "USDT", "DAI", "USDE", "SUSDE", "USDS", "SUSDS", "GHO", "CRVUSD", "FRAX", "LUSD", "PYUSD", "RLUSD",
              "USD0", "USDT0", "USDC.E", "EURC", "USDG", "FDUSD", "TUSD", "USDP", "USR", "USDX", "SUSDC", "AUSD"}
GOV_KEYWORDS = re.compile(r"incentiv|emission|liquidity mining|rewards?\b|grant|gauge|bribe|subsid|trading competition|points", re.I)
AUTOMATION_RE = re.compile(r"\b(bots?|automat\w*|algo\w*|expert advis\w*|EAs?|copy[- ]?trad\w*|HFT|high[- ]frequency|API|"
                           r"signals?|alerts?|semi-?automat\w*|manual\w*|scalp\w*)\b", re.I)
RESTRICT_RE = re.compile(r"restricted|prohibited|not available|unsupported|not accept|ineligible|banned countr", re.I)
SKIP_DOMAINS = re.compile(r"(facebook|twitter|x\.com|youtube|instagram|linkedin|t\.me|telegram|discord|tiktok|google|apple|"
                          r"trustpilot|reddit|medium|github|wikipedia|cloudflare|gstatic|w3\.org|schema\.org|cdn|wordpress|"
                          r"wp\.com|jsdelivr|bootstrap|fontawesome|stripe|paypal|whatsapp|pinterest)", re.I)


def fetch(url, post=None, tries=3, timeout=45, accept="*/*"):
    """Return (status, text). Status 0 = network error. Never raises."""
    msg = ""
    for k in range(tries):
        try:
            data = json.dumps(post).encode() if post is not None else None
            hdr = {"User-Agent": UA, "Accept": accept}
            if data:
                hdr["Content-Type"] = "application/json"
            req = urllib.request.Request(url, data=data, headers=hdr, method="POST" if data else "GET")
            with urllib.request.urlopen(req, timeout=timeout) as r:
                LOG["ok"] += 1
                return r.status, r.read(150_000_000).decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            msg = f"HTTP {e.code}"
            if e.code in (429, 500, 502, 503, 504):
                time.sleep(3 * (2 ** k))
                continue
            LOG["fail"] += 1
            print(f"  FAIL {url[:110]} -> {msg}", flush=True)
            return e.code, ""
        except Exception as e:  # noqa: BLE001
            msg = f"{type(e).__name__}: {e}"
            time.sleep(1 + k)
    LOG["fail"] += 1
    print(f"  FAIL {url[:110]} -> {msg}", flush=True)
    return 0, ""


def jget(url, **kw):
    s, t = fetch(url, accept="application/json", **kw)
    try:
        return json.loads(t) if t else None
    except Exception:  # noqa: BLE001
        print(f"  BAD JSON {url[:110]} ({s}, {len(t)} bytes)", flush=True)
        return None


def load(name):
    p = OUT / f"{name}.parquet"
    return pd.read_parquet(p) if p.exists() else pd.DataFrame()


def save(df, name):
    OUT.mkdir(parents=True, exist_ok=True)
    df.to_parquet(OUT / f"{name}.parquet", index=False)


# ------------------------------------------------------------------ nearmiss bookkeeping
NEAR = []


def near(item_id, source, venue, stage, reason, metrics=""):
    NEAR.append({"item_id": str(item_id), "source": source, "venue": venue, "stage": stage, "reason": reason,
                 "metrics": str(metrics)[:300]})


def merge_near():
    new = pd.DataFrame(NEAR)
    old = load("nearmiss")
    if new.empty:
        return old
    new["first_seen"] = TODAY
    new["last_seen"] = TODAY
    key = ["item_id", "stage", "reason"]
    if not old.empty:
        first = old.set_index(key)["first_seen"]
        idx = pd.MultiIndex.from_frame(new[key])
        new["first_seen"] = first.reindex(idx).fillna(TODAY).to_numpy()
        keep = old[~old.set_index(key).index.isin(idx)]
        new = pd.concat([keep, new], ignore_index=True)
    return new.drop_duplicates(key, keep="last").reset_index(drop=True)


# ------------------------------------------------------------------ S2: protocols
def collect_protocols():
    d = jget("https://api.llama.fi/protocols")
    if not isinstance(d, list):
        return pd.DataFrame()
    rows = []
    for p in d:
        la = p.get("listedAt")
        rows.append({"slug": str(p.get("slug", "")).lower(), "name": str(p.get("name", "")), "category": p.get("category"),
                     "tvl": p.get("tvl") or 0.0, "n_chains": len(p.get("chains") or []),
                     "listed_at": pd.to_datetime(la, unit="s", utc=True) if la else pd.NaT, "url": p.get("url"),
                     "parent": p.get("parentProtocol") or p.get("slug")})
    df = pd.DataFrame(rows)
    # F2 uses the protocol family's first listing (a new version of an old protocol is not a new venue)
    df["listed_at"] = df.groupby("parent")["listed_at"].transform("min")
    print(f"S2 protocols: {len(df)}", flush=True)
    return df


# ------------------------------------------------------------------ S1: pools
def collect_pools(prot):
    d = jget("https://yields.llama.fi/pools", timeout=120)
    if not d or "data" not in d:
        near("S1", "S1", "DefiLlama pools", "collect", "no data (request failed)")
        return pd.DataFrame()
    pools = pd.DataFrame(d["data"])
    print(f"S1 pools total: {len(pools)}", flush=True)
    for c in ("apyReward", "apyBase", "tvlUsd"):
        pools[c] = pd.to_numeric(pools.get(c), errors="coerce")
    n_noreward = int((~(pools["apyReward"] > 0)).sum())
    print(f"S1 pools with no reward (not candidates): {n_noreward}", flush=True)
    r = pools[pools["apyReward"] > 0].copy()
    r["budget_usd_day"] = r["tvlUsd"] * r["apyReward"] / 100 / 365
    pm = prot.set_index("slug")["listed_at"] if not prot.empty else pd.Series(dtype="datetime64[ns, UTC]")
    r["listed_at"] = r["project"].str.lower().map(pm)
    rows = []
    for x in r.itertuples():
        rows.append({"item_id": f"S1:{x.pool}", "source": "S1", "venue": x.project, "chain": x.chain,
                     "what_pays": f"{x.symbol} {getattr(x, 'poolMeta', '') or ''} reward tokens {getattr(x, 'rewardTokens', '')}"[:200],
                     "budget_usd_day": x.budget_usd_day, "competing_capital_usd": x.tvlUsd, "reward_apr_pct": x.apyReward,
                     "start_date": None, "url": f"https://defillama.com/yields/pool/{x.pool}",
                     "stablecoin": bool(getattr(x, "stablecoin", False)), "il_risk": str(getattr(x, "ilRisk", "")),
                     "outlier": bool(getattr(x, "outlier", False)), "listed_at": x.listed_at, "pool_id": x.pool})
    return pd.DataFrame(rows)


# ------------------------------------------------------------------ S3: Merkl
def collect_merkl():
    rows, page = [], 0
    while page < 80:
        d = jget(f"https://api.merkl.xyz/v4/opportunities?items=100&page={page}&status=LIVE")
        if not d:
            break
        items = d if isinstance(d, list) else d.get("items") or d.get("data") or []
        if not items:
            break
        rows += items
        if len(items) < 100:
            break
        page += 1
        time.sleep(0.3)
    print(f"S3 Merkl live opportunities: {len(rows)}", flush=True)
    if not rows:
        near("S3", "S3", "Merkl", "collect", "no data (request failed or empty)")
    out = []
    for o in rows:
        toks = [str(t.get("symbol", "")).upper() for t in (o.get("tokens") or []) if isinstance(t, dict)]
        camps = o.get("campaigns") or []
        starts = [c.get("startTimestamp") for c in camps if isinstance(c, dict) and c.get("startTimestamp")]
        prot = (o.get("protocol") or {}).get("id") or (o.get("protocol") or {}).get("name") or ""
        chain = (o.get("chain") or {}).get("name") or o.get("chainId")
        out.append({"item_id": f"S3:{o.get('id') or o.get('identifier')}", "source": "S3", "venue": str(prot).lower(),
                    "chain": str(chain), "what_pays": f"{o.get('action', '')} {o.get('name', '')}"[:200],
                    "budget_usd_day": float(o.get("dailyRewards") or 0), "competing_capital_usd": float(o.get("tvl") or 0),
                    "reward_apr_pct": float(o.get("apr") or 0),
                    "start_date": pd.to_datetime(min(starts), unit="s", utc=True) if starts else None,
                    "url": f"https://app.merkl.xyz/opportunities/{o.get('id') or ''}",
                    "stablecoin": bool(toks) and all(t in STABLE_TOK for t in toks)
                    and str(o.get("action", "")).upper() != "BORROW" and not re.search(r"collateral|looping|leverage", str(o.get("name", "")), re.I),
                    "il_risk": "unknown", "outlier": False, "listed_at": pd.NaT, "pool_id": o.get("identifier"),
                    "n_campaigns": len(camps)})
    return pd.DataFrame(out)


# ------------------------------------------------------------------ S4: Snapshot governance
def collect_snapshot():
    since = int((NOW - timedelta(days=45)).timestamp())
    got, skip = [], 0
    q = "query($s:Int!,$c:Int!){proposals(first:1000,skip:$s,where:{created_gt:$c},orderBy:\"created\",orderDirection:desc)" \
        "{id title space{id name} created state end}}"
    while skip < 5000:
        d = None
        s, t = fetch("https://hub.snapshot.org/graphql", post={"query": q, "variables": {"s": skip, "c": since}},
                     accept="application/json")
        try:
            d = json.loads(t)["data"]["proposals"]
        except Exception:  # noqa: BLE001
            break
        got += d
        if len(d) < 1000:
            break
        skip += 1000
    print(f"S4 Snapshot proposals (45d): {len(got)}", flush=True)
    if not got:
        near("S4", "S4", "Snapshot", "collect", "no data (request failed or empty)")
    rows = []
    for p in got:
        title = p.get("title") or ""
        m = GOV_KEYWORDS.search(title)
        if not m:
            continue
        amt = re.search(r"\$\s?([\d,.]+)\s?([kKmM]?)", title)
        usd = None
        if amt:
            try:
                usd = float(amt.group(1).replace(",", "")) * {"": 1, "k": 1e3, "m": 1e6}[amt.group(2).lower()]
            except ValueError:
                usd = None
        sp = p.get("space") or {}
        rows.append({"item_id": f"S4:{p['id']}", "source": "S4", "venue": str(sp.get("id", "")).lower(),
                     "chain": "", "what_pays": f"[{p.get('state')}] {title}"[:200], "budget_usd_day": None,
                     "competing_capital_usd": None, "reward_apr_pct": None,
                     "start_date": pd.to_datetime(p.get("created"), unit="s", utc=True), "url": f"https://snapshot.org/#/{sp.get('id')}/proposal/{p['id']}",
                     "stablecoin": False, "il_risk": "", "outlier": False, "listed_at": pd.NaT, "pool_id": "",
                     "budget_usd_total_in_title": usd})
    return pd.DataFrame(rows)


# ------------------------------------------------------------------ S5/S6/S7: pages
def html_to_text(h):
    h = re.sub(r"(?is)<(script|style|noscript|svg)[^>]*>.*?</\1>", " ", h)
    h = re.sub(r"(?s)<!--.*?-->", " ", h)
    h = re.sub(r"(?i)<(br|/p|/div|/li|/h\d|/tr)[^>]*>", "\n", h)
    t = html.unescape(re.sub(r"<[^>]+>", " ", h))
    return "\n".join(re.sub(r"[ \t\r\f\v]+", " ", ln).strip() for ln in t.split("\n") if ln.strip())


def atom_to_text(x):
    items = re.findall(r"(?s)<entry>.*?<title>(.*?)</title>.*?<updated>(.*?)</updated>", x)
    return "\n".join(f"{u[:10]} {html.unescape(t)}" for t, u in items[:30])


def sentences(t):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n", t) if 20 <= len(s.strip()) <= 400]


def page_job(row):
    slug, kind, url = row["slug"], row["kind"], row["url"]
    s, raw = fetch(url, tries=2, timeout=30)
    res = {"slug": slug, "name": row["name"], "kind": kind, "url": url, "status": s, "bytes": len(raw), "fetched": TODAY}
    if s != 200 or not raw:
        return res, "", []
    text = atom_to_text(raw) if kind == "release" else html_to_text(raw)
    links = re.findall(r'(?is)<a\s[^>]*?href="([^"#]+)"[^>]*>(.*?)</a>', raw)
    links = [(h, re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", t))).strip()[:120]) for h, t in links]
    m = re.search(r"(?is)<title[^>]*>(.*?)</title>", raw)
    res["title"] = re.sub(r"\s+", " ", html.unescape(m.group(1))).strip()[:150] if m else ""
    return res, text[:300_000], links


LINK_TXT = re.compile(r"autom|\bbots?\b|algo|expert advis|copy|prohibit|trading rules?|\brules\b|fair play|allowed|restricted|"
                      r"supported countr|faq|polic|terms|payout|evaluation|funded|drawdown|consistency", re.I)
LINK_PATH = re.compile(r"faq|rules|terms|trading-rule|policy|pricing|plans|prohibited|restricted|countries|automat|bots?\b|"
                       r"article|collection|evaluation|funded|payout", re.I)


def follow_links(base, links, n=40, skip=()):
    host = urllib.parse.urlparse(base).netloc.replace("www.", "")
    pick, seen = [], set(skip)
    for h, txt in links:
        u = urllib.parse.urljoin(base, h).split("#")[0].split("?")[0]
        pu = urllib.parse.urlparse(u)
        if pu.scheme not in ("http", "https") or host.split(".")[-2:] != pu.netloc.replace("www.", "").split(".")[-2:]:
            continue
        if (LINK_PATH.search(pu.path) or LINK_TXT.search(txt)) and u not in seen \
                and not re.search(r"\.(png|jpg|svg|css|js|pdf|webp|xml)$", pu.path, re.I):
            seen.add(u)
            pick.append((0 if LINK_TXT.search(txt) else 1, u))
    pick.sort(key=lambda x: x[0])
    return [u for _, u in pick[:n]]


def sitemap_urls(root):
    out, todo, seen = [], [root.rstrip("/") + "/sitemap.xml"], set()
    while todo and len(seen) < 12:
        u = todo.pop(0)
        if u in seen:
            continue
        seen.add(u)
        s, t = fetch(u, tries=2, timeout=30)
        for loc in re.findall(r"<loc>\s*(.*?)\s*</loc>", t):
            (todo if loc.endswith(".xml") else out).append(loc)
    return out


def collect_pages():
    wl = pd.read_csv(CFG / "watchlist.csv")
    SNAP.mkdir(parents=True, exist_ok=True)
    jobs = wl.to_dict("records")
    results = []
    with cf.ThreadPoolExecutor(8) as ex:
        results = list(ex.map(page_job, jobs))
    # follow rule/FAQ/help links from firm pages, two levels deep (help centres hide the bot policy in articles)
    seen = {r["url"] for r in jobs}
    allres = list(results)
    frontier = [(res, links, row) for (res, text, links), row in zip(results, jobs) if row["kind"] == "firm" and links]
    for depth in (1, 2):
        extra, nxt = [], []
        for res, links, row in frontier:
            for u in follow_links(row["url"], links, n=30 if depth == 1 else 15, skip=seen):
                seen.add(u)
                extra.append({"slug": f"{row['slug']}__{hashlib.md5(u.encode()).hexdigest()[:8]}", "name": row["name"],
                              "kind": "firm_sub", "url": u})
        with cf.ThreadPoolExecutor(8) as ex:
            got = list(ex.map(page_job, extra))
        allres += got
        frontier = [(g[0], g[2], r) for g, r in zip(got, extra) if g[2]]
    results = allres
    sm = []
    for row in jobs:
        if row["kind"] == "directory":
            u = sitemap_urls(row["url"].split("/")[0] + "//" + urllib.parse.urlparse(row["url"]).netloc)
            print(f"sitemap {row['url']}: {len(u)} urls", flush=True)
            sm += [{"directory": row["slug"], "url": x} for x in u]
    if sm:
        save(pd.DataFrame(sm), "directory_urls")
    pages, changes, snippets, dom = [], [], [], {}
    for res, text, links in results:
        if res["kind"] == "directory":
            for h, _t in links:
                pu = urllib.parse.urlparse(h)
                if pu.scheme in ("http", "https") and not SKIP_DOMAINS.search(pu.netloc):
                    d = pu.netloc.replace("www.", "")
                    if d not in urllib.parse.urlparse(res["url"]).netloc:
                        dom[d] = dom.get(d, 0) + 1
        if not text:
            pages.append({**res, "sha": "", "auto_snips": "", "my_snips": ""})
            continue
        sha = hashlib.sha1(text.encode()).hexdigest()
        f = SNAP / f"{res['slug']}.txt"
        prev = f.read_text() if f.exists() else None
        if prev is None:
            changes.append({"date": TODAY, "slug": res["slug"], "name": res["name"], "kind": res["kind"], "url": res["url"],
                            "event": "baseline", "added": "", "removed": ""})
        elif prev != text:
            d = list(difflib.unified_diff(prev.split("\n"), text.split("\n"), lineterm="", n=0))
            add = "\n".join(x[1:] for x in d if x.startswith("+") and not x.startswith("+++"))[:4000]
            rem = "\n".join(x[1:] for x in d if x.startswith("-") and not x.startswith("---"))[:4000]
            changes.append({"date": TODAY, "slug": res["slug"], "name": res["name"], "kind": res["kind"], "url": res["url"],
                            "event": "changed", "added": add, "removed": rem})
        f.write_text(text)
        ss = sentences(text)
        auto = [s for s in ss if AUTOMATION_RE.search(s)][:30]
        my = [s for s in ss if re.search(r"malaysia", s, re.I) or (RESTRICT_RE.search(s) and re.search(r"countr", s, re.I))][:6]
        pages.append({**res, "sha": sha, "auto_snips": " || ".join(auto), "my_snips": " || ".join(my)})
        if res["kind"] in ("firm", "firm_sub", "directory_firm") and (auto or my):
            snippets.append((res["name"], res["url"], auto, my))
    pg = pd.DataFrame(pages)
    save(pg, "pages")
    ch = load("changes")
    if changes:
        ch = pd.concat([ch, pd.DataFrame(changes)], ignore_index=True)
        save(ch, "changes")
    print(f"S5-S7 pages: {len(pg)} fetched, {int((pg['status'] == 200).sum())} ok, {len(changes)} baseline/changed", flush=True)
    # discovered domains
    known = " ".join(wl["url"].tolist() + pd.read_csv(CFG / "prop_firms.csv")["firm"].str.lower().tolist())
    old = load("discovered_domains")
    drows = [{"domain": d, "links": n, "first_seen": TODAY, "in_watchlist": d.split(".")[0] in known.lower()} for d, n in dom.items()]
    if drows:
        nd = pd.DataFrame(drows)
        if not old.empty:
            fs = old.set_index("domain")["first_seen"]
            nd["first_seen"] = nd["domain"].map(fs).fillna(TODAY)
        save(nd.sort_values("links", ascending=False), "discovered_domains")
    # human-readable snippets for the prop-firm classification
    with open(OUT / "propfirm_snippets.md", "w") as fh:
        fh.write(f"# Prop-firm automation / country sentences ({TODAY})\n\n")
        for name, url, auto, my in sorted(snippets):
            fh.write(f"## {name} — {url}\n")
            for s in auto:
                fh.write(f"- AUTO: {s}\n")
            for s in my:
                fh.write(f"- COUNTRY: {s}\n")
            fh.write("\n")
    return pg, ch


# ------------------------------------------------------------------ screening
def deep_check(top):
    rows, hist = [], []
    for x in top.itertuples():
        d = jget(f"https://yields.llama.fi/chart/{x.pool_id}")
        pts = (d or {}).get("data") or []
        if not pts:
            rows.append({"item_id": x.item_id, "hist_days": 0, "reward_share_180d": None})
            continue
        df = pd.DataFrame(pts)
        df["ts"] = pd.to_datetime(df["timestamp"], utc=True)
        df["apyReward"] = pd.to_numeric(df.get("apyReward"), errors="coerce").fillna(0)
        for c in ("apy", "apyBase", "tvlUsd"):
            df[c] = pd.to_numeric(df.get(c), errors="coerce")
        hist.append(df[["ts", "apy", "apyBase", "apyReward", "tvlUsd"]].assign(item_id=x.item_id, pool_id=x.pool_id, venue=x.venue))
        last = df[df["ts"] >= NOW - timedelta(days=F1_DAYS)]
        l90 = df[df["ts"] >= NOW - timedelta(days=90)]
        rows.append({"item_id": x.item_id, "hist_days": (df["ts"].max() - df["ts"].min()).days,
                     "reward_share_180d": float((last["apyReward"] > 0).mean()) if len(last) else 0.0,
                     "yield90": float((l90["apyBase"].fillna(0) + 0.9 * l90["apyReward"]).mean()) if len(l90) else None})
        time.sleep(0.25)
    if hist:  # full daily history of every deep-checked pool, for the pre-registered tests
        save(pd.concat(hist, ignore_index=True), "charts")
    return pd.DataFrame(rows)


def malaysia_status(venue, rules):
    v = venue.lower()
    for r in rules.itertuples():
        if r.match != "default_onchain" and r.match in v:
            return r.status
    return "unverified-onchain"


def screen(cand, prot):
    """Apply first-pass, data quality, F3-F5, Malaysia; deep check; F1/F2. Returns survivors; logs near-misses."""
    mrules = pd.read_csv(CFG / "malaysia.csv")
    keep = []
    ver_count = cand[cand["source"].isin(["S1", "S3"])].groupby("venue")["item_id"].count()
    chain_count = cand[cand["source"].isin(["S1", "S3"])].groupby("venue")["chain"].nunique()
    for x in cand.itertuples():
        m = {"apr": x.reward_apr_pct, "tvl": x.competing_capital_usd, "budget_day": x.budget_usd_day}
        if x.source == "S4":
            keep.append(x.Index)  # governance proposals go to the human review list, not the ranking
            continue
        if x.outlier:
            near(x.item_id, x.source, x.venue, "quality", "DefiLlama outlier flag", m)
            continue
        if x.reward_apr_pct > MAX_APR_PLAUSIBLE:
            near(x.item_id, x.source, x.venue, "quality", f"implausible APR > {MAX_APR_PLAUSIBLE:.0f}%", m)
            continue
        low = []
        if x.reward_apr_pct < MIN_APY_REWARD:
            low.append(f"reward APR {x.reward_apr_pct:.2f}% < {MIN_APY_REWARD}%")
        if x.competing_capital_usd < MIN_TVL:
            low.append(f"TVL ${x.competing_capital_usd:,.0f} < ${MIN_TVL:,}")
        if x.budget_usd_day < MIN_BUDGET_DAY:
            low.append(f"budget/day ${x.budget_usd_day:.1f} < ${MIN_BUDGET_DAY:.0f}")
        if low:
            near(x.item_id, x.source, x.venue, "first_pass", "below threshold: " + "; ".join(low), m)
            continue
        ms = malaysia_status(x.venue, mrules)
        if ms in ("blocked", "grey-area"):
            near(x.item_id, x.source, x.venue, "malaysia", f"Malaysia {ms}", m)
            continue
        keep.append(x.Index)
    c = cand.loc[keep].copy()
    c["malaysia"] = c["venue"].map(lambda v: malaysia_status(v, mrules))
    c["f3"] = c.apply(lambda r: bool(r["source"] != "S4" and (ver_count.get(r["venue"], 0) >= 2 or chain_count.get(r["venue"], 0) >= 2)), axis=1)
    c["f4"] = c["stablecoin"] & c["il_risk"].isin(["no", "unknown"]) if len(c) else False
    c["f5"] = c["competing_capital_usd"].fillna(0) >= F5_TVL
    # filter fails -> near-miss, still shown in ranking? No: only rows passing F3-F5 are ranked; the rest are near-misses.
    ranked = []
    for x in c.itertuples():
        if x.source == "S4":
            ranked.append(x.Index)
            continue
        fails = []
        if not x.f3:
            fails.append("F3 single pool/venue on one chain (no reused setup)")
        if not x.f4:
            fails.append("F4 price exposure, needs hedge")
        if not x.f5:
            fails.append(f"F5 TVL < ${F5_TVL:,}")
        if fails:
            near(x.item_id, x.source, x.venue, "filter", "; ".join(fails),
                 {"apr": x.reward_apr_pct, "tvl": x.competing_capital_usd, "budget_day": x.budget_usd_day})
        else:
            ranked.append(x.Index)
    c = c.loc[ranked].copy()
    c["f1"], c["f2"] = "unverified", "unverified"
    # deep check on the top slice of S1 rows
    s1 = c[c["source"] == "S1"].sort_values("reward_apr_pct", ascending=False).head(DEEP_TOP)
    tp = CFG / "test_pools.csv"  # pools under a pre-registered test: always fetch their history
    extra = pd.read_csv(tp) if tp.exists() else pd.DataFrame(columns=["pool_id", "venue"])
    extra = extra.assign(item_id="S1:" + extra["pool_id"].astype(str))[["item_id", "pool_id", "venue"]]
    extra = extra[~extra["item_id"].isin(s1["item_id"])]
    deep = deep_check(pd.concat([s1[["item_id", "pool_id", "venue"]], extra], ignore_index=True)) if len(s1) or len(extra) else pd.DataFrame()
    if not deep.empty:
        save(deep, "deep")
        dm = deep.set_index("item_id")
        c["yield90"] = c["item_id"].map(dm["yield90"])
        c["hist_days"] = c["item_id"].map(dm["hist_days"])
        for i, r in s1.iterrows():
            d = dm.loc[r["item_id"]]
            share = d["reward_share_180d"]
            c.at[i, "f1"] = "pass" if (share is not None and pd.notna(share) and share >= F1_SHARE and d["hist_days"] >= F1_DAYS) else "fail"
            age = (NOW - r["listed_at"]).days if pd.notna(r["listed_at"]) else None
            c.at[i, "f2"] = ("pass" if (age is not None and age >= F2_AGE_DAYS and d["hist_days"] >= F1_DAYS)
                             else "fail" if age is not None else "unverified")
            for fl, nm in (("f1", "F1 reward not persistent"), ("f2", "F2 not long-lived")):
                if c.at[i, fl] == "fail":
                    near(r["item_id"], "S1", r["venue"], "deep", nm,
                         {"hist_days": d["hist_days"], "share180": share, "age_days": age})
    # S3: F1 via campaign count per protocol (unverified until history), F2 via DefiLlama age
    pm = prot.set_index("slug")["listed_at"] if not prot.empty else pd.Series(dtype="datetime64[ns, UTC]")
    for i, r in c[c["source"] == "S3"].iterrows():
        ageref = pm.get(str(r["venue"]).lower())
        if pd.notna(ageref):
            c.at[i, "f2"] = "pass" if (NOW - ageref).days >= F2_AGE_DAYS else "fail"
        c.at[i, "f1"] = "unverified"
    c = c.reset_index(drop=True)
    return c


def finish(cand_all, nm):
    """merge candidates with history, mark new, write summary."""
    old = load("candidates")
    first = dict(zip(old["item_id"], old["first_seen"])) if not old.empty else {}
    base_date = old["first_seen"].min() if not old.empty else TODAY
    cand_all["first_seen"] = cand_all["item_id"].map(first).fillna(TODAY)
    cand_all["last_seen"] = TODAY
    cand_all["is_new"] = cand_all["first_seen"] > base_date
    cand_all["baseline_date"] = base_date
    if not old.empty:  # items that vanished -> near-miss, not dropped silently
        gone = old[~old["item_id"].isin(cand_all["item_id"]) & (old["last_seen"] < TODAY)]
        for r in gone.itertuples():
            if r.source in ("S1", "S3"):
                near(r.item_id, r.source, r.venue, "gone", f"disappeared from source (last seen {r.last_seen})")
    cand_all = cand_all.copy()
    cand_all["passes_f3_f5_malaysia"] = cand_all["source"].isin(["S1", "S3"])
    cand_all["verified_all"] = (cand_all["f1"] == "pass") & (cand_all["f2"] == "pass") & cand_all["passes_f3_f5_malaysia"]
    cand_all["rank_score"] = cand_all["reward_apr_pct"]
    cand_all = cand_all.sort_values("rank_score", ascending=False, na_position="last").reset_index(drop=True)
    for c in ("start_date", "listed_at"):
        if c in cand_all:
            cand_all[c] = pd.to_datetime(cand_all[c], utc=True, errors="coerce")
    save(cand_all, "candidates")
    return cand_all


def summary(cand, nm, pg, ch, counts):
    L = [f"# Radar summary {TODAY}", "", f"Baseline date: {cand['baseline_date'].iloc[0] if len(cand) else TODAY}", ""]
    L += ["## Counts"] + [f"- {k}: {v}" for k, v in counts.items()]
    L += [f"- candidates surviving to ranking: {len(cand[cand['source'].isin(['S1', 'S3'])])}",
          f"- of which all five filter parts verified: {int(cand['verified_all'].sum()) if len(cand) else 0}",
          f"- near-miss rows total: {len(nm)}", ""]
    if not nm.empty:
        L += ["## Near-miss by stage/reason (top)", ""]
        t = nm.assign(r=nm["reason"].str.split(":").str[0].str.slice(0, 70)).groupby(["stage", "r"]).size().sort_values(ascending=False).head(15)
        L += [f"- {a} / {b}: {n}" for (a, b), n in t.items()]
        L.append("")
    r = cand[cand["source"].isin(["S1", "S3"])].head(25)
    L += ["## Top 25 by money per competitor (reward APR on competing capital)", "",
          "| venue | chain | what pays | $/day | capital | reward APR % | F1 | F2 | stable | new | Malaysia |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for x in r.itertuples():
        L.append(f"| {x.venue} | {x.chain} | {x.what_pays[:50]} | {x.budget_usd_day:,.0f} | {x.competing_capital_usd:,.0f} | {x.reward_apr_pct:.1f} | {x.f1} | {x.f2} | {x.stablecoin} | {x.is_new} | {x.malaysia} |")
    if "yield90" in cand:  # addendum 3: weekly test queue = top 3 venues by 90-day realised yield among fully verified rows
        q = cand[cand["verified_all"] & (cand["hist_days"].fillna(0) >= 90)].sort_values("yield90", ascending=False)
        q = q.drop_duplicates("venue").head(3)
        L += ["", "## Test queue (addendum 3: top 3 venues by 90-day mean of base + 0.9 x reward APR)", ""]
        L += [f"- {x.venue} ({x.chain}) {x.what_pays[:60]}: {x.yield90:.2f}%/yr over 90 d, TVL ${x.competing_capital_usd:,.0f}, pool {x.pool_id}" for x in q.itertuples()]
    g = cand[cand["source"] == "S4"].head(25)
    if len(g):
        L += ["", "## Governance proposals mentioning incentives (last 45d, newest 25)", ""]
        L += [f"- {x.venue}: {x.what_pays[:110]} {x.url}" for x in g.itertuples()]
    if not ch.empty:
        c = ch[(ch["date"] == TODAY) & (ch["event"] == "changed")]
        rk = re.compile(r"\$\s?\d|drawdown|target|payout|split|bot|automat|algo|consisten|price|reset|new plan|limited", re.I)
        fc = c[c["kind"].isin(["firm", "firm_sub", "directory_firm"])]
        L += ["", f"## Prop-firm rule/price changes today: {len(fc)} pages", ""]
        for x in fc.itertuples():
            hits = [ln for ln in x.added.splitlines() if rk.search(ln)][:3]
            if hits:
                L.append(f"- **{x.name}** {x.url}: " + " / ".join(h[:140] for h in hits))
        L += ["", f"## Page changes today: {len(c)}", ""] + [f"- {x.name} ({x.kind}) {x.url}: +{len(x.added.splitlines())} / -{len(x.removed.splitlines())} lines" for x in c.itertuples()][:40]
    (OUT / "latest_summary.md").write_text("\n".join(L) + "\n")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    prot = collect_protocols()
    if not prot.empty:
        new_p = prot[(prot["listed_at"] >= NOW - timedelta(days=NEW_PROTOCOL_DAYS)) & (prot["tvl"] >= NEW_PROTOCOL_TVL)]
        print(f"S2 new protocols (<= {NEW_PROTOCOL_DAYS}d, TVL >= $1M): {len(new_p)}", flush=True)
    pools = collect_pools(prot)
    merkl = collect_merkl()
    gov = collect_snapshot()
    pg, ch = collect_pages()
    counts = {"S2 protocols": len(prot), "S1 reward pools": len(pools), "S3 Merkl live": len(merkl), "S4 governance hits": len(gov),
              "pages fetched ok": int((pg["status"] == 200).sum()) if len(pg) else 0, "pages total": len(pg)}
    parts = [d for d in (pools, merkl, gov) if not d.empty]
    if parts:
        cand = pd.concat(parts, ignore_index=True)
        scr = screen(cand, prot)
        if not prot.empty:  # new-venue flags go in as candidates of their own
            for x in new_p.itertuples():
                scr = pd.concat([scr, pd.DataFrame([{"item_id": f"S2:{x.slug}", "source": "S2", "venue": x.slug, "chain": "",
                                                    "what_pays": f"new protocol ({x.category}), TVL ${x.tvl:,.0f}, incentive unknown",
                                                    "budget_usd_day": None, "competing_capital_usd": x.tvl, "reward_apr_pct": None,
                                                    "start_date": x.listed_at, "url": x.url, "stablecoin": False, "il_risk": "",
                                                    "outlier": False, "listed_at": x.listed_at, "pool_id": "", "malaysia": "unverified-onchain",
                                                    "f1": "unverified", "f2": "unverified", "f3": False, "f4": False, "f5": False}])], ignore_index=True)
        scr = finish(scr, None)
    else:
        scr = load("candidates")
    nm = merge_near()
    save(nm, "nearmiss")
    summary(scr, nm, pg, ch, counts)
    print(open(OUT / "latest_summary.md").read())
    print(f"done in {time.time() - t0:.0f}s, requests ok {LOG['ok']} fail {LOG['fail']}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())

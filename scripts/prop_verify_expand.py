"""Prop search 2, Stage C: render official pages and expand every collapsed section (accordions, <details>, aria-expanded buttons) before
capturing the text. Public pages only; no logins, no evasion. Output data/public/propverify/expand_<slug>.json.

    uv run --with playwright python scripts/prop_verify_expand.py
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from playwright.sync_api import sync_playwright

OUT = Path(__file__).resolve().parent.parent / "data" / "public" / "propverify"
PAGES = [
    # Stage C3 (prop search 2): Funded Futures Network rules articles (index is crawled for article links), BluSky, IQ Capital, Finotive
    "https://app.fundedfuturesnetwork.com/nexus/rules",
    "https://fundedfuturesnetwork.com/accounts",
    "https://fundedfuturesnetwork.com/faq",
    "https://bluskytrading.com/",
    "https://help.blusky.pro/",
    "https://blusky.pro/",
    "https://iqcapital.com/",
    "https://iqcapital.com/futures",
    "https://finotivefutures.com/",
    "https://help.finotivefutures.com/",
]
CRAWL = ("app.fundedfuturesnetwork.com/nexus/rules/article-", "help.blusky.pro/", "help.finotivefutures.com/")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        br = p.chromium.launch()
        ctx = br.new_context(user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36 (research)")
        queue, seen = list(PAGES), set()
        while queue and len(seen) < 120:
            url = queue.pop(0)
            if url in seen:
                continue
            seen.add(url)
            pg = ctx.new_page()
            rec = {"url": url}
            try:
                pg.goto(url, wait_until="networkidle", timeout=60000)
                pg.wait_for_timeout(2000)
                n = 0
                for _ in range(3):
                    for sel in ("details:not([open]) > summary", "[aria-expanded='false']", "button.accordion", ".intercom-interblocks-collapsible"):
                        for el in pg.query_selector_all(sel)[:200]:
                            try:
                                el.click(timeout=1500)
                                n += 1
                                pg.wait_for_timeout(150)
                            except Exception:  # noqa: BLE001
                                pass
                pg.evaluate("document.querySelectorAll('details').forEach(d => d.open = true)")
                pg.wait_for_timeout(1000)
                rec["clicked"] = n
                rec["text"] = pg.inner_text("body")[:200000]
                rec["html_tables"] = [t.inner_text()[:20000] for t in pg.query_selector_all("table")][:60]
                for a in pg.query_selector_all("a[href]"):
                    h = (a.get_attribute("href") or "").split("#")[0]
                    if h.startswith("/"):
                        h = url.split("/", 3)[0] + "//" + url.split("/")[2] + h
                    if any(c in h for c in CRAWL) and h not in seen and h not in queue:
                        queue.append(h)
            except Exception as e:  # noqa: BLE001
                rec["error"] = str(e)[:300]
            slug = re.sub(r"[^a-z0-9]+", "_", url.lower())[8:90]
            (OUT / f"expand_{slug}.json").write_text(json.dumps(rec))
            print(f"{url}: clicked {rec.get('clicked')}, chars {len(rec.get('text', ''))}, tables {len(rec.get('html_tables', []))} {rec.get('error', '')}", flush=True)
            pg.close()
        br.close()


if __name__ == "__main__":
    main()

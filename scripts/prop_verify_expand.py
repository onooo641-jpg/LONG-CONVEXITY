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
    # Go-live: CrossTrade API reference (NinjaTrader 8 REST via the CrossTrade NT8 Add-On), crawled for every docs/api page
    "https://crosstrade.io/docs",
    "https://crosstrade.io/docs/api/overview",
    "https://crosstrade.io/docs/api/positions",
]
CRAWL = ("crosstrade.io/docs/api", "crosstrade.io/docs/webhooks", "crosstrade.io/docs/getting-started", "crosstrade.io/docs/add-on")
TAB = re.compile(r"^\$?\s?(2\.5|5|10|25|50|75|100|150|200|250|300)\s?K$|^(Static|Trail|EOD|S2F|S2L|Instant|Live|1-Step|2-Step)$", re.I)


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
                pg.goto(url, wait_until="domcontentloaded", timeout=90000)
                pg.wait_for_timeout(8000)
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
                states = []
                for _ in range(2):  # click plan/size tabs and capture each state's text
                    for el in pg.query_selector_all("button, [role='tab'], a, li, span, div")[:3000]:
                        try:
                            txt = (el.inner_text() or "").strip()
                        except Exception:  # noqa: BLE001
                            continue
                        if not TAB.match(txt) or len(states) >= 60:
                            continue
                        try:
                            el.click(timeout=1000)
                            pg.wait_for_timeout(500)
                            states.append({"tab": txt, "text": pg.inner_text("body")[:30000]})
                        except Exception:  # noqa: BLE001
                            pass
                rec["tab_states"] = states
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

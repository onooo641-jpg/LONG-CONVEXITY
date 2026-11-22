"""Render official prop-firm pages with a headless browser (GitHub Actions) for fact verification (docs/PROP_VERIFY_20261122.md).

Public pages only, no logins, no evasion: a page that blocks automated browsers is recorded as blocked.
    uv run --with playwright python scripts/prop_verify_fetch.py
"""
from __future__ import annotations

import csv
import json
import re
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse

from playwright.sync_api import sync_playwright

OUT = Path(__file__).resolve().parent.parent / "data" / "public" / "propverify"
KW = re.compile(r"rule|objective|faq|payout|withdraw|expert|advisor|\bea\b|bot|automat|algo|countr|restrict|pricing|price|plan|challenge|"
                r"evaluation|drawdown|loss|refund|reset|activation|scaling|consisten|account|article|collection|help|terms|prohibit|copy|"
                r"futures|prime|instant|flex|rapid|eod|static|elite|nitro", re.I)
EXTRA = ["https://www.topstep.com/pricing/", "https://lucidtrading.com/pricing", "https://myfundedfutures.com/pricing",
         "https://thetradingpit.com/futures-prime", "https://futureselite.com/pricing", "https://daytraders.com/pricing",
         "https://www.blueguardian.com/futures", "https://alpha-futures.com/pricing", "https://ftmo.com/en/trading-objectives/",
         "https://fundednext.com/futures", "https://the5ers.com/high-stakes/", "https://www.tradeday.com/pricing"]


DEEP = ["https://faq.futureselite.com/en/", "https://support.lucidtrading.com/", "https://help.myfundedfutures.com/", "https://help.alpha-futures.com/",
        "https://help.tradeday.com/", "https://support.thetradingpit.com/en/", "https://help.blueberryfutures.com/", "https://daytraders.com/help/",
        "https://help.tradeify.co/", "https://help.topstep.com/en/", "https://help.goatfundedfutures.com/", "https://help.blueguardian.com/",
        "https://help.fundednext.com/", "https://ftmo.com/en/faq/", "https://help.the5ers.com/", "https://help.thefuturesdesk.com/",
        "https://bulenox.com/help/", "https://help.traderslaunch.com/"]


def main() -> None:
    import sys
    OUT.mkdir(parents=True, exist_ok=True)
    deep = len(sys.argv) > 1 and sys.argv[1] == "deep"
    starts: dict[str, list[str]] = {}
    if deep:
        for u in DEEP:
            starts.setdefault(urlparse(u).netloc.replace("www.", ""), []).append(u)
    else:
        rows = [r for r in csv.DictReader(open("docs/radar/watchlist.csv")) if r["kind"] == "firm"]
        for r in rows:
            starts.setdefault(urlparse(r["url"]).netloc.replace("www.", ""), []).append(r["url"])
        for u in EXTRA:
            starts.setdefault(urlparse(u).netloc.replace("www.", ""), []).append(u)
    limit = 160 if deep else 30
    with sync_playwright() as p:
        br = p.chromium.launch()
        ctx = br.new_context(user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36 (research)")
        for dom, urls in starts.items():
            pages, queue, seen = {}, list(dict.fromkeys(urls)), set()
            while queue and len(pages) < limit:
                u = queue.pop(0)
                if u in seen:
                    continue
                seen.add(u)
                pg = ctx.new_page()
                try:
                    pg.goto(u, timeout=30000, wait_until="domcontentloaded")
                    try:
                        pg.wait_for_load_state("networkidle", timeout=8000)
                    except Exception:  # noqa: BLE001
                        pass
                    txt = pg.inner_text("body")[:20000]
                    pages[u] = txt
                    for a in pg.eval_on_selector_all("a[href]", "els => els.map(e => e.href)"):
                        a = urljoin(u, a).split("#")[0]
                        same = urlparse(a).netloc.replace("www.", "") == dom if deep else \
                            urlparse(a).netloc.replace("www.", "").endswith(dom.split(".", 1)[-1] if dom.count(".") > 1 else dom)
                        ok_link = re.search(r"/articles?/|/collections?/|/faq|/help", a) if deep else KW.search(a)
                        if same and ok_link and a not in seen and len(queue) < 600:
                            queue.append(a)
                except Exception as e:  # noqa: BLE001
                    pages[u] = f"FETCH FAILED: {type(e).__name__}: {str(e)[:200]}"
                finally:
                    pg.close()
                time.sleep(0.5)
            (OUT / f"{'deep_' if deep else ''}{dom}.json").write_text(json.dumps(pages))
            ok = sum(1 for v in pages.values() if not v.startswith("FETCH FAILED"))
            print(f"{dom}: {ok}/{len(pages)} pages", flush=True)
        br.close()


if __name__ == "__main__":
    main()

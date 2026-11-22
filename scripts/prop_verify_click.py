"""Second pass for prop-firm verification: on official pricing pages, click account-type and size tabs and capture each state's text.

Public pages only; no logins, no evasion. Output data/public/propverify/clicks_<domain>.json.
    uv run --with playwright python scripts/prop_verify_click.py
"""
from __future__ import annotations

import json
import re
import time
from pathlib import Path
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright

OUT = Path(__file__).resolve().parent.parent / "data" / "public" / "propverify"
PAGES = ["https://www.topstep.com/pricing/", "https://www.topstep.com/", "https://lucidtrading.com/", "https://lucidtrading.com/pricing",
         "https://myfundedfutures.com/", "https://myfundedfutures.com/pricing", "https://tradeify.co/", "https://www.tradeday.com/pricing",
         "https://bulenox.com/", "https://daytraders.com/", "https://daytraders.com/pricing", "https://thetradingpit.com/futures-prime",
         "https://thetradingpit.com/futures", "https://futureselite.com/", "https://futureselite.com/pricing", "https://alpha-futures.com/",
         "https://alpha-futures.com/pricing", "https://www.blueguardian.com/futures", "https://www.blueguardian.com/", "https://goatfundedfutures.com/",
         "https://thefuturesdesk.com/", "https://fundednext.com/futures", "https://ftmo.com/en/", "https://the5ers.com/", "https://alphacapitalgroup.uk/",
         "https://goatfundedtrader.com/", "https://traderslaunch.com/", "https://apextraderfunding.com/", "https://www.takeprofittrader.com/",
         "https://phidiaspropfirm.com/", "https://www.earn2trade.com/", "https://www.toponefutures.com/", "https://aquafunded.com/",
         "https://fundedfuturesnetwork.com/", "https://purdia.com/", "https://e8markets.com/", "https://audacitycapital.co.uk/",
         "https://blueberryfutures.com/", "https://www.blueberryfutures.com/pricing"]
SIZE = re.compile(r"^\$?\s?(25|50|75|100|150|200|250|300)\s?K$|^\$?(25|50|100|150)[,.]000$", re.I)
TAB = re.compile(r"^[A-Za-z0-9 \-+/&]{2,22}$")


def texts(pg):
    return pg.inner_text("body")[:30000]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    res: dict[str, dict] = {}
    with sync_playwright() as p:
        br = p.chromium.launch()
        ctx = br.new_context(user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36 (research)")
        for u in PAGES:
            dom = urlparse(u).netloc.replace("www.", "")
            states = {}
            pg = ctx.new_page()
            try:
                pg.goto(u, timeout=40000, wait_until="domcontentloaded")
                try:
                    pg.wait_for_load_state("networkidle", timeout=10000)
                except Exception:  # noqa: BLE001
                    pass
                states["default"] = texts(pg)
                cands = pg.locator("button, [role=tab], [role=button], label, li a, .tab, [class*=tab] >> visible=true")
                els = []
                for i in range(min(cands.count(), 250)):
                    try:
                        t = cands.nth(i).inner_text(timeout=500).strip()
                    except Exception:  # noqa: BLE001
                        continue
                    if t and TAB.match(t) and len(els) < 80:
                        els.append((i, t))
                sizes = [(i, t) for i, t in els if SIZE.match(t.replace(" ", ""))]
                others = [(i, t) for i, t in els if not SIZE.match(t.replace(" ", "")) and not re.search(r"log ?in|sign|buy|start|get|faq|blog|contact|cart", t, re.I)][:25]
                for oi, ot in [(None, "")] + others:
                    if oi is not None:
                        try:
                            cands.nth(oi).click(timeout=1500)
                            time.sleep(0.6)
                        except Exception:  # noqa: BLE001
                            continue
                    for si, st in sizes[:8]:
                        try:
                            cands.nth(si).click(timeout=1500)
                            time.sleep(0.6)
                            states[f"{ot} | {st}"] = texts(pg)
                        except Exception:  # noqa: BLE001
                            continue
                    if not sizes and oi is not None:
                        states[f"{ot}"] = texts(pg)
            except Exception as e:  # noqa: BLE001
                states["error"] = f"FETCH FAILED: {type(e).__name__}: {str(e)[:200]}"
            finally:
                pg.close()
            res.setdefault(dom, {})[u] = states
            print(f"{u}: {len(states)} states", flush=True)
            (OUT / f"clicks_{dom}.json").write_text(json.dumps(res[dom]))
        br.close()


if __name__ == "__main__":
    main()

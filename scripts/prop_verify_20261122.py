"""Prop-firm fact check helper (docs/PROP_VERIFY_20261122.md): prints each modelled product's parameters next to matching snippets from the
firm's official pages (data/public/propverify/*.json, rendered by .github/workflows/prop_verify.yml).

    uv run python -m scripts.prop_verify_20261122 [model_key ...]
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from scripts.radar_models2 import MODELS2
from scripts.radar_price import MODELS

DOM = {"topstep": ["topstep.com", "help.topstep.com"], "lucid": ["lucidtrading.com", "support.lucidtrading.com"],
       "mffu": ["myfundedfutures.com", "help.myfundedfutures.com"], "tradeify": ["tradeify.co", "help.tradeify.co"],
       "tradeday": ["tradeday.com", "help.tradeday.com"], "bulenox": ["bulenox.com"], "fundednext": ["fundednext.com"], "ftmo": ["ftmo.com"],
       "tfd": ["thefuturesdesk.com"], "dt": ["daytraders.com"], "ttp": ["thetradingpit.com", "support.thetradingpit.com"],
       "traders_launch": ["traderslaunch.com"], "goat": ["goatfundedfutures.com"], "blueberry": ["help.blueberryfutures.com"],
       "fe": ["futureselite.com", "faq.futureselite.com"], "alpha": ["alpha-futures.com", "help.alpha-futures.com"], "bg": ["blueguardian.com"]}
PREFIX = {"topstep50": "topstep", "lucidflex50": "lucid", "lucid_daily50": "lucid", "lucid_direct50": "lucid", "tradeify_flex50": "tradeify",
          "tradeday": "tradeday", "bulenox": "bulenox", "fundednext_rapid": "fundednext", "ftmo_growth": "ftmo", "tfd_core": "tfd",
          "traders_launch": "traders_launch", "blueberry_ascent50": "blueberry"}
KEYS = r"(price|\$\s?\d|reset|activation|profit target|target|drawdown|max(imum)? loss|daily loss|split|payout|withdraw|consisten|winning day|" \
       r"buffer|minimum|cap|contracts|automat|bot|algo|expert advisor|country|countries|restricted|malaysia)"


def domain_of(key):
    if key in PREFIX:
        return PREFIX[key]
    for p in ("mffu", "dt", "ttp", "goat", "fe", "alpha", "bg"):
        if key.startswith(p):
            return p
    return None


def pages(dom):
    out = {}
    for d in DOM.get(dom, []):
        f = Path(f"data/public/propverify/{d}.json")
        if f.exists():
            out.update(json.loads(f.read_text()))
    return out


def snippets(txts, limit=60):
    seen, res = set(), []
    for u, t in txts.items():
        if t.startswith("FETCH FAILED"):
            continue
        for sent in re.split(r"(?<=[.!?])\s+|\n+", t):
            s = sent.strip()
            if 12 < len(s) < 300 and re.search(KEYS, s, re.I) and re.search(r"\d|bot|automat|algo|countr|malaysia", s, re.I) and s not in seen:
                seen.add(s)
                res.append((u, s))
    return res[:limit]


def main() -> int:
    items = []
    for k, v in MODELS.items():
        items += [(k, it[0], it[1], it[2]) for it in v]
    for k, (auto, lst) in MODELS2.items():
        items += [(k, n, r, rk) for n, r, rk in lst]
    want = set(sys.argv[1:])
    for key, name, r, risk in items:
        if want and key not in want:
            continue
        dom = domain_of(key)
        txt = pages(dom) if dom else {}
        ok = sum(1 for t in txt.values() if not t.startswith("FETCH FAILED"))
        print(f"\n=== {name} [{key}] -> pages {ok}/{len(txt)} from {DOM.get(dom)}")
        print(f"  model: price {r.one_time_price if r.one_time_price is not None else str(r.monthly) + '/mo'}, reset {r.reset}, activation {r.activation}, "
              f"target {r.profit_target}{' + phase2 ' + str(r.phase2_target) if r.phase2_target else ''}, loss {r.loss_limit} ({'static' if r.static_dd else 'trailing'}; "
              f"locks at {r.mll_locks_at}), DLL {r.daily_loss_limit}, funded loss {r.funded_loss_limit}, split {r.profit_split}, payout cap {r.payout_cap}, "
              f"min {r.payout_min}, buffer {r.payout_buffer}, winning days {r.winning_days_required}x{r.winning_day_min}, consistency eval "
              f"{r.combine_consistency} / funded {r.consistency_target}, max contracts {r.combine_max_contracts}, instant {r.instant_funded}")
        for u, s in snippets(txt):
            print(f"   - {s}  <{u}>")
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""PREREG_LIQ_NEWCHAINS_20261122 analysis. uv run python -I scripts/liq_newchains_20261122.py [pilot|full]"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import liquidations_20261120 as L  # noqa: E402

NEW = {"sonic": "coingecko:sonic-3", "mantle": "coingecko:mantle", "linea": "coingecko:ethereum", "celo": "coingecko:celo", "ink": "coingecko:ethereum",
       "soneium": "coingecko:ethereum", "zksync": "coingecko:ethereum"}
KEY = {"sonic": "sonic", "mantle": "mantle", "linea": "linea", "celo": "celo", "ink": "ink", "soneium": "soneium", "zksync": "era"}
for c, n in NEW.items():
    for suf in ("", "_pilot"):
        L.NATIVE[c + suf] = n
        L.LKEY[c + suf] = KEY[c]
D = Path(L.D)


def pilot():
    print("== stage 1 pilot (2026-08-01..2026-10-31), KILL-ONLY: venue dropped if gross < USD 3,750")
    for c in NEW:
        name = c + "_pilot"
        sf = D / f"liq_{name}_state.json"
        if not sf.exists():
            print(f"{c:8s} no pilot data (endpoint/probe or job not finished)")
            continue
        df = L.load(name)
        if df is None:
            import json
            st = json.loads(sf.read_text())
            print(f"{c:8s} {L.status(name)}; events scanned {len(pd.read_parquet(D / f'liq_{name}_raw.parquet')) if (D / f'liq_{name}_raw.parquet').exists() else 0}")
            continue
        for ven, v in df.groupby("venue"):
            val = v[v["valid"]]
            g = val["gross"].sum()
            top3 = val.groupby("bot")["gross"].sum().sort_values(ascending=False, kind="mergesort").head(3).sum() / max(g, 1)
            print(f"{c:8s} {ven[:12]} events {len(v):6d} valid {len(val):6d} gross ${g:12,.0f} winners {val['bot'].nunique():4d} top3 {top3:.2f} -> {'KILL' if g < 3750 else 'proceed'}")


def full():
    print("== stage 2: registered venue test with launch-adjusted (b) (months from the venue's first event; >= 6 months)")
    for c in NEW:
        sf = D / f"liq_{c}_state.json"
        if not sf.exists():
            continue
        df = L.load(c)
        if df is None:
            print(f"{c}: {L.status(c)}")
            continue
        for ven, v in df.groupby("venue"):
            first = int(v["month"].min())
            months_avail = 24 - first
            st = L.venue_stats(v)
            ok = True
            lines = []
            for half, months in (("H1", range(0, 12)), ("H2", range(12, 24))):
                present = [m for m in months if m >= first]
                if not present:
                    continue
                s = st[half]
                a = bool(s["events"] >= 20 and s["top3"] < 0.60)
                b = bool(all((v["month"] == m).any() for m in present))
                cc = bool(s["out_net_pm"] * 12 / len(present) >= 500)
                ok = ok and a and b and cc
                lines.append(f"{half}: events {s['events']} months present {len(present)} top3 {s['top3']:.2f} (a){a} every-month (b){b} outside-top3 net/month {s['out_net_pm'] * 12 / len(present):,.0f} (c){cc}")
            ok = ok and months_avail >= 6
            print(f"\n{c} venue {ven[:12]} first event month index {first}, months available {months_avail}")
            for ln in lines:
                print("  " + ln)
            print(f"  VENUE PASS = {ok}")


if __name__ == "__main__":
    pilot() if (sys.argv[1] if len(sys.argv) > 1 else "full") == "pilot" else full()

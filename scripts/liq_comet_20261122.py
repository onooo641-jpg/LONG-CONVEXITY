"""PREREG_LIQ_COMET_20261122 analysis. uv run python -I scripts/liq_comet_20261122.py [pilot|full]"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import liquidations_20261120 as L  # noqa: E402

CH = {"base": "coingecko:ethereum", "arbitrum": "coingecko:ethereum", "optimism": "coingecko:ethereum", "polygon": "coingecko:matic-network"}
KEY = {"base": "base", "arbitrum": "arbitrum", "optimism": "optimism", "polygon": "polygon"}
for c, n in CH.items():
    for suf in ("", "_pilot"):
        L.NATIVE[f"comet_{c}{suf}"] = n
        L.LKEY[f"comet_{c}{suf}"] = KEY[c]
D = Path(L.D)


def pilot():
    print("== stage 1 pilot (2026-08-01..2026-10-31), KILL-ONLY: chain dropped if total gross < USD 3,750")
    for c in CH:
        name = f"comet_{c}_pilot"
        if not (D / f"liq_{name}_state.json").exists():
            print(f"{c:9s} no pilot data yet")
            continue
        df = L.load(name)
        if df is None:
            print(f"{c:9s} {L.status(name)}")
            continue
        val = df[df["valid"]]
        tot = val["gross"].sum()
        print(f"{c:9s} events {len(df):6d} valid {len(val):6d} gross ${tot:12,.0f} -> {'KILL chain' if tot < 3750 else 'proceed'}")
        for ven, v in val.groupby("venue"):
            top3 = v.groupby("bot")["gross"].sum().sort_values(ascending=False, kind="mergesort").head(3).sum() / max(v["gross"].sum(), 1)
            print(f"   {ven[:12]} events {len(v):5d} gross ${v['gross'].sum():11,.0f} winners {v['bot'].nunique():4d} top3 {top3:.2f}")


def full():
    print("== stage 2: registered venue test (both halves; every month; outside-top-3 net >= $500/month)")
    for c in CH:
        name = f"comet_{c}"
        if not (D / f"liq_{name}_state.json").exists():
            continue
        df = L.load(name)
        if df is None:
            print(f"{c}: {L.status(name)}")
            continue
        for ven, v in df.groupby("venue"):
            st = L.venue_stats(v)
            ok = st["H1"]["pass"] and st["H2"]["pass"]
            print(f"\n{c} venue {ven[:12]}: events {len(v)}")
            for h in ("H1", "H2"):
                print(" ", h, {k: (round(x, 3) if isinstance(x, float) else x) for k, x in st[h].items()})
            print("  VENUE PASS =", ok)
        val = df[df["valid"]]
        print("  monthly gross:", {int(m): round(g) for m, g in val.groupby("month")["gross"].sum().items()})


if __name__ == "__main__":
    pilot() if (sys.argv[1] if len(sys.argv) > 1 else "full") == "pilot" else full()

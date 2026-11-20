"""CANDIDATES #51: Luno MYR prices vs Kraken USD x USD/MYR (docs/PREREG_LOOPHOLES_20261120.md).

    uv run python scripts/myx_gap_20261120.py
"""
import json
from pathlib import Path

import pandas as pd

d = pd.read_parquet(Path(__file__).resolve().parent.parent / "data" / "public" / "myx_snapshots.parquet")
PAIRS = {"XBT": ("XBTMYR", "XXBTZUSD"), "ETH": ("ETHMYR", "XETHZUSD"), "SOL": ("SOLMYR", "SOLUSD"), "XRP": ("XRPMYR", "XXRPZUSD")}
for t, g in d.groupby("t"):
    src = {r.src: json.loads(r.body) for r in g.itertuples()}
    fx = src.get("fx_erapi", {}).get("rates", {}).get("MYR")
    fx_time = src.get("fx_erapi", {}).get("time_last_update_utc")
    usdt = src["kraken"]["result"].get("USDTZUSD", {})
    luno = {x["pair"]: x for x in src["luno"]["tickers"]}
    row = [pd.Timestamp(t, unit="s").strftime("%H:%M UTC"), f"USD/MYR {fx} ({fx_time[:16] if fx_time else '?'})"]
    for k, (lp, kp) in PAIRS.items():
        L = luno.get(lp)
        K = src["kraken"]["result"].get(kp)
        if not (L and K and fx):
            continue
        lmid = (float(L["bid"]) + float(L["ask"])) / 2
        lspread = (float(L["ask"]) - float(L["bid"])) / lmid
        kmid = (float(K["b"][0]) + float(K["a"][0])) / 2
        row.append(f"{k} gap {lmid / (kmid * fx) - 1:+.2%} (Luno spread {lspread:.2%})")
    print(" | ".join(row))

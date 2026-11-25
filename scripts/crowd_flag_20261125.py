"""#416 fade the crowd Binance flags (funding-frequency changes) (docs/PREREG_DISTINCT_20261125.md).

    uv run python -m scripts.crowd_flag_20261125 | tee docs/jx_runs/crowd_flag_20261125.txt
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

PUB = Path(__file__).resolve().parent.parent / "data" / "public"
FEE = 0.00045


def main():
    print("===== #416 fade the crowd Binance flags")
    d = json.loads((PUB / "uncharted_w3_binance_ann.json").read_text())
    items = {x["code"]: x for v in d.values() for x in v}.values()
    ev = []
    for x in items:
        t = x["title"]
        if not re.search(r"Funding Rate Settlement Frequency|Capped Funding Rate", t) or "Resumed" in t:
            continue
        syms = re.findall(r"\b([A-Z0-9]{2,20}USDT)\b", t)
        if len(set(syms)) != 1:
            continue
        ev.append({"sym": syms[0], "day": pd.Timestamp(int(x["releaseDate"]), unit="ms", tz="UTC").normalize(), "title": t[:80]})
    ev = pd.DataFrame(ev).sort_values("day")
    print(f"  single-contract funding-frequency announcements: {len(ev)}")
    b = pd.read_parquet(PUB / "uncharted_389_binance_ohlc.parquet", columns=["sym", "t", "c"])
    b["day"] = pd.to_datetime(b["t"], unit="s", utc=True).dt.normalize()
    C = b.drop_duplicates(["sym", "day"]).pivot(index="day", columns="sym", values="c").sort_index()
    bf = pd.read_parquet(PUB / "cryptotrend370_funding.parquet")
    F = bf.pivot_table(index="date", columns="sym", values="rate", aggfunc="sum")
    rows, last = [], {}
    for _, e in ev.iterrows():
        s, d0 = e["sym"], e["day"]
        if s not in C or d0 not in C.index or pd.isna(C.at[d0, s]):
            continue
        if s in last and d0 <= last[s] + pd.Timedelta(days=14):
            continue
        f0 = F.at[d0, s] if (d0 in F.index and s in F.columns) else np.nan
        if pd.isna(f0) or f0 == 0:
            continue
        side = -1 if f0 > 0 else 1
        ex = d0 + pd.Timedelta(days=7)
        if ex not in C.index or pd.isna(C.at[ex, s]):
            continue
        w = F.loc[d0 + pd.Timedelta(days=1):ex]
        fs = float(w[s].sum()) if s in w else 0.0
        fb = float(w["BTCUSDT"].sum()) if "BTCUSDT" in w else 0.0
        ret = side * (C.at[ex, s] / C.at[d0, s] - 1) - side * (C.at[ex, "BTCUSDT"] / C.at[d0, "BTCUSDT"] - 1) - side * fs + side * fb - 4 * FEE
        rows.append({"day": d0.date(), "sym": s, "side": "short" if side < 0 else "long", "funding_day": f0, "ret": ret})
        last[s] = d0
    t = pd.DataFrame(rows)
    pd.set_option("display.width", 200)
    print(t.to_string(index=False, float_format=lambda x: f"{x:8.4f}"))

    def stats(x):
        r = x["ret"]
        n = len(r)
        ts = r.mean() / (r.std(ddof=1) / np.sqrt(n)) if n > 1 else np.nan
        return n, r.mean() if n else np.nan, ts, (r > 0).mean() if n else np.nan
    s1 = t[pd.to_datetime(t["day"]) <= "2024-12-31"]
    s2 = t[pd.to_datetime(t["day"]) >= "2025-01-01"]
    n, m, ts, w = stats(s1)
    print(f"\n  Stage 1 (2023-24): events {n}, mean {m:.2%}, t {ts:.2f}, win {w:.0%}")
    if n < 8:
        v1 = "not testable (< 8 events)"
    else:
        v1 = "KILL" if (m < 0.01 or ts < 1) else "survives (kill-only)"
    print(f"  STAGE 1 VERDICT: {v1}")
    n2, m2, ts2, w2 = stats(s2)
    print(f"  Stage 2 (2025-01..2026-10, out-of-sample): events {n2}, mean {m2:.2%}, t {ts2:.2f}, win {w2:.0%}")
    ok = v1.startswith("survives") and n2 >= 10 and m2 >= 0.02 and ts2 >= 1.5 and w2 >= 0.55
    print(f"  STAGE 2 VERDICT: {'PASS' if ok else ('FAIL' if v1.startswith('survives') else 'not judged (Stage 1 did not survive) — context')}")


if __name__ == "__main__":
    main()

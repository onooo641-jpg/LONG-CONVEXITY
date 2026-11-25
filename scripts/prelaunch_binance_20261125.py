"""#385 Stage 2: short Binance pre-market perps from their first close to token launch + 7 days (docs/PREREG_UNCHARTED_20261125.md).

    uv run python -m scripts.prelaunch_binance_20261125 | tee docs/jx_runs/prelaunch_binance_20261125.txt
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
    print("===== #385 Stage 2: Binance pre-market perps (short to launch + 7 days)")
    d = json.loads((PUB / "uncharted_w3_binance_ann.json").read_text())
    items = {x["code"]: x for v in d.values() for x in v}.values()
    launch, conv = {}, {}
    for x in items:
        t = x["title"]
        m = re.search(r"USDⓈ-Margined ([A-Z0-9]+)USDT Perpetual Contract Pre-Market Trading", t)
        if not m:
            continue
        sym = m.group(1) + "USDT"
        if "Convert" in t:
            dm = re.search(r"\((\d{4}-\d{2}-\d{2})\)", t)
            if dm:
                conv[sym] = pd.Timestamp(dm.group(1), tz="UTC")
        elif "Launch" in t:
            launch[sym] = pd.Timestamp(int(x["releaseDate"]), unit="ms", tz="UTC").normalize()
    print(f"  pre-market launches {len(launch)}, conversions with a date {len(conv)}")
    b = pd.read_parquet(PUB / "uncharted_389_binance_ohlc.parquet", columns=["sym", "t", "c"])
    b["day"] = pd.to_datetime(b["t"], unit="s", utc=True).dt.normalize()
    C = b.drop_duplicates(["sym", "day"]).pivot(index="day", columns="sym", values="c").sort_index()
    bf = pd.read_parquet(PUB / "cryptotrend370_funding.parquet")
    F = bf.pivot_table(index="date", columns="sym", values="rate", aggfunc="sum")
    mp = json.loads((PUB / "uncharted_385_map.json").read_text())
    rows = []
    for sym in sorted(set(launch) | set(conv)):
        if sym not in C:
            rows.append({"sym": sym, "status": "no Binance klines in archive"})
            continue
        s = C[sym].dropna()
        # mechanical fix: tickers can be reused by older coins, so entry = first close on/after the pre-market launch announcement
        if sym in launch:
            s = s[s.index >= launch[sym]]
        if s.empty:
            rows.append({"sym": sym, "status": "no klines after launch"})
            continue
        entry = s.index[0]
        tge = conv.get(sym)
        if tge is None:
            v = mp.get(sym[:-4]) or {}
            tge = pd.Timestamp(v["first_spot"], unit="s", tz="UTC").normalize() if v.get("first_spot") else None
        if tge is None:
            rows.append({"sym": sym, "status": "no launch date"})
            continue
        ex = tge + pd.Timedelta(days=7)
        if ex not in s.index:
            rows.append({"sym": sym, "status": "exit after data end"})
            continue
        win = F.loc[entry + pd.Timedelta(days=1):ex]
        fund = float(win[sym].sum()) if sym in win else 0.0
        mx = float(s.loc[entry + pd.Timedelta(days=1):ex].max() / s[entry] - 1)
        ret = -(s[ex] / s[entry] - 1) + fund - 2 * FEE
        rows.append({"sym": sym, "status": "ok", "entry": entry.date(), "tge": tge.date(), "days_pre": (tge - entry).days,
                     "price_ret": s[ex] / s[entry] - 1, "funding": fund, "max_up_close": mx, "ret": ret})
    t = pd.DataFrame(rows)
    pd.set_option("display.width", 220)
    print(t.to_string(index=False, float_format=lambda x: f"{x:8.3f}"))
    ok = t[t["status"] == "ok"]
    r = ok["ret"]
    n = len(r)
    ts = r.mean() / (r.std(ddof=1) / np.sqrt(n)) if n > 1 else np.nan
    big = float((r < -0.5).mean()) if n else np.nan
    print(f"\n  events {n}; mean {r.mean():.1%}, median {r.median():.1%}, t {ts:.2f}, win {(r > 0).mean():.0%}, losses > 50% {big:.0%}, "
          f"worst {r.min():.1%}; mean funding to the short {ok['funding'].mean():+.1%}")
    passed = n >= 8 and r.mean() >= 0.05 and ts >= 1.5 and big <= 1 / 3
    print(f"  STAGE 2 VERDICT: {'PASS' if passed else 'FAIL'}")


if __name__ == "__main__":
    main()

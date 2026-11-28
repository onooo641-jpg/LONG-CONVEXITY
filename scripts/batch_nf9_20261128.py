"""Batch NF9 #568-#571: forced flows within hours on Hyperliquid (docs/PREREG_BATCH_NF9_20261128.md).

    uv run python -m scripts.batch_nf9_20261128 | tee docs/jx_runs/batch_nf9_20261128.txt
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from ict import data as D

PUB = D.REPO_ROOT / "data" / "public"
MID = pd.Timestamp("2026-08-16", tz="UTC")
LO, HI = pd.Timestamp("2026-04-24", tz="UTC"), pd.Timestamp("2026-11-25", tz="UTC")


def main():
    h = pd.read_parquet(PUB / "wickscale_hl_1h.parquet")
    unit = "ms" if h["t"].max() > 1e11 else "s"
    h["ts"] = pd.to_datetime(h["t"], unit=unit, utc=True)
    h = h.drop_duplicates(["coin", "ts"]).sort_values(["coin", "ts"])
    for c in ("o", "h", "l", "c", "v"):
        h[c] = h[c].astype(float)
    tr = {568: [], 569: [], 570: [], 571: []}
    for coin, g in h.groupby("coin"):
        g = g.reset_index(drop=True)
        r = g["c"].pct_change()
        sig = r.rolling(168, min_periods=120).std().shift()
        usd = g["v"] * g["c"]
        x = (4 * sig).clip(0.01, 0.20)
        lvl = g["c"].shift() * (1 - x)
        busy = {568: -1, 569: -1, 570: -1}
        for i in range(170, len(g)):
            size = min(1500.0, 0.01 * usd.iloc[i])
            if i > busy[568] and i + 1 < len(g) and pd.notna(lvl.iloc[i]) and g["l"].iloc[i] <= lvl.iloc[i] * (1 - 0.1 * x.iloc[i]):
                px = min(lvl.iloc[i], g["o"].iloc[i])
                tr[568].append((g["ts"].iloc[i], coin, g["c"].iloc[i + 1] / px - 1 - 0.0006, size))
                busy[568] = i + 1
            if pd.notna(sig.iloc[i]) and i + 4 < len(g):
                if i > busy[569] and r.iloc[i] <= -5 * sig.iloc[i]:
                    tr[569].append((g["ts"].iloc[i], coin, g["c"].iloc[i + 4] / g["c"].iloc[i] - 1 - 0.0009, size))
                    busy[569] = i + 4
                if i > busy[570] and r.iloc[i] >= 5 * sig.iloc[i]:
                    tr[570].append((g["ts"].iloc[i], coin, -(g["c"].iloc[i + 4] / g["c"].iloc[i] - 1) - 0.0009, size))
                    busy[570] = i + 4
    piv = h.pivot(index="ts", columns="coin", values="c").sort_index()
    vol = (h.assign(usd=h["v"] * h["c"])).pivot(index="ts", columns="coin", values="usd").sort_index()
    btc = piv["BTC"]
    br = btc.pct_change()
    last = None
    for i, ts in enumerate(piv.index):
        if i < 720 or i + 6 >= len(piv) or not (br.iloc[i] <= -0.02) or (last is not None and i <= last):
            continue
        top = vol.iloc[i - 720:i].sum().drop(["BTC", "ETH"], errors="ignore").nlargest(20).index
        rr = (piv[top].iloc[i + 6] / piv[top].iloc[i] - 1).dropna()
        if len(rr):
            tr[571].append((ts, "basket", float(rr.mean()) - 0.0009, 1500.0 * len(rr)))
            last = i + 6
    names = {568: "Hourly wick bids (exit next hour)", 569: "Hourly cascade reversal (long 4 h)", 570: "Hourly squeeze give-back (short 4 h)",
             571: "Market-wide hourly flush (alt basket long 6 h)"}
    yrs_s2 = (HI - MID).days / 365.25
    for k, name in names.items():
        t = pd.DataFrame(tr[k], columns=["ts", "coin", "r", "size"])
        print(f"#{k} {name}: {len(t)} trades")
        res = {}
        for label, g in (("Stage 1 (2026-04-24..08-15)", t[t.ts < MID]), ("Stage 2 (2026-08-16..11-25)", t[t.ts >= MID])):
            r = g["r"]
            n = len(r)
            tt = r.mean() / (r.std(ddof=1) / np.sqrt(n)) if n > 1 and r.std(ddof=1) > 0 else np.nan
            ex3 = r.sort_values().iloc[:-3].sum() if n > 3 else np.nan
            usd = (g["r"] * g["size"]).sum()
            res[label] = (n, r.mean() if n else np.nan, tt, ex3, usd)
            print(f"   {label}: n {n}, mean {r.mean() if n else np.nan:+.2%} (median {r.median() if n else np.nan:+.2%}, t {tt:.2f}, "
                  f"win {(r > 0).mean() if n else np.nan:.0%}), sum without the 3 best {ex3:+.2f}, P&L ${usd:,.0f}")
        n1, m1, _, _, _ = res["Stage 1 (2026-04-24..08-15)"]
        n2, m2, t2, ex3, usd2 = res["Stage 2 (2026-08-16..11-25)"]
        kmin, pmin = (8, 10) if k == 571 else (30, 30)
        v = "KILL (Stage 1)" if (n1 >= kmin and not (m1 > 0)) else \
            ("PASS" if (n2 >= pmin and m2 >= 0.003 and t2 >= 2 and ex3 > 0) else "FAIL")
        print(f"   VERDICT {v} | Stage 2 P&L annualised ${usd2 / yrs_s2:,.0f}/yr\n")


if __name__ == "__main__":
    main()

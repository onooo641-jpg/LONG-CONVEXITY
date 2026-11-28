"""Batch WK #521-#525: refine and stress-test #520 (docs/PREREG_BATCH_WK_20261128.md).

    uv run python -m scripts.batch_wk_20261128 | tee docs/jx_runs/batch_wk_20261128.txt
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

PUB = Path(__file__).resolve().parent.parent / "data" / "public"
THROUGH, CAP_FILL, VOL_SHARE, POT = 0.005, 1500.0, 0.01, 15_000.0
PERP, SPOT = (0.00015, 0.00045), (0.0004, 0.0007)
T = lambda s: pd.Timestamp(s, tz="UTC")  # noqa: E731
HL = ((T("2023-06-01"), T("2024-12-31")), (T("2025-01-01"), T("2026-10-31")))
REF_520_S2 = 6374.0


def load_hl(name, key, ms=True):
    cd = pd.read_parquet(PUB / f"{name}.parquet").rename(columns={key: "coin"})
    cd["day"] = pd.to_datetime(cd["t"], unit="ms" if ms else "s", utc=True).dt.normalize()
    if "qvol" in cd.columns:
        cd["usdvol"] = cd["qvol"].astype(float)
    else:
        cd["usdvol"] = cd["v"].astype(float) * cd["c"].astype(float)
    return cd.drop_duplicates(["coin", "day"])


def fills(cd, k, costs, hold_days=0, cost_mult=1.0):
    mk, tk = costs
    out = []
    for coin, g in cd.groupby("coin"):
        g = g.sort_values("day").reset_index(drop=True)
        if len(g) < 32:
            continue
        sig = g["c"].pct_change().rolling(30).std().shift()
        x = (k * sig).clip(0.05, 0.30)
        prev = g["c"].shift()
        lvl = prev * (1 - x)
        ok = (g["day"] >= g["day"].iloc[0] + pd.Timedelta(days=30)) & x.notna() & prev.notna()
        hit = ok & (g["l"] <= lvl * (1 - THROUGH))
        for i in np.flatnonzero(hit.to_numpy()):
            j = i + hold_days
            if j >= len(g):
                continue
            r = g.iloc[i]
            px = min(float(lvl.iloc[i]), float(r["o"]))
            if not px > 0:
                continue
            ret = float(g["c"].iloc[j]) / px - 1 - cost_mult * (mk + tk)
            out.append({"day": r["day"], "ret": ret, "size": min(CAP_FILL, VOL_SHARE * float(r["usdvol"]))})
    f = pd.DataFrame(out)
    if not f.empty:
        f["pnl"] = f["size"] * np.minimum(1.0, POT / f.groupby("day")["size"].transform("sum")) * f["ret"]
    return f


def summ(f, w):
    yrs = ((w[1] - w[0]).days + 1) / 365
    g = f[(f["day"] >= w[0]) & (f["day"] <= w[1])] if not f.empty else f
    if g.empty:
        return dict(n=0, m=np.nan, t=np.nan, usd=0.0, ex=0.0)
    r = g["ret"]
    best = g.groupby("day")["pnl"].sum().idxmax()
    return dict(n=len(g), m=r.mean(), t=r.mean() / (r.std(ddof=1) / np.sqrt(len(r))) if len(r) > 1 else np.nan,
                usd=g["pnl"].sum() / yrs, ex=g[g["day"] != best]["pnl"].sum() / yrs, win=(r > 0).mean())


def fmt(label, s):
    if not s["n"]:
        return f"   {label}: no fills"
    return (f"   {label}: fills {s['n']} | mean net {s['m']:+.2%} (t {s['t']:.2f}, win {s['win']:.0%}) | ${s['usd']:,.0f}/yr "
            f"| without best day ${s['ex']:,.0f}/yr")


def killed(s1):
    return s1["n"] >= 30 and not (s1["m"] > 0.003)


def main():
    hl = load_hl("uncharted_385_candles", "coin")
    print("Base #520 rule: bid at previous close x (1 - k*sigma30), clipped 5%..30%; exit at the close.\n")

    print("#521 Distance multiplier (pick on Stage 1 among k = 2, 3, 5, 6; Stage 2 once with costs x 1.5)")
    s1s = {}
    for k in (2, 3, 5, 6):
        s1s[k] = summ(fills(hl, k, PERP), HL[0])
        print(fmt(f"k {k} Stage 1", s1s[k]))
    best = max(s1s, key=lambda k: s1s[k]["usd"])
    s2 = summ(fills(hl, best, PERP, cost_mult=1.5), HL[1])
    print(f"   chosen on Stage 1: k {best}")
    print(fmt(f"k {best} Stage 2 (costs x 1.5)", s2))
    ok = (not killed(s1s[best])) and s2["n"] >= 30 and s2["m"] >= 0.003 and s2["t"] >= 2 and s2["usd"] > REF_520_S2
    print(f"   VERDICT {'KILL (Stage 1)' if killed(s1s[best]) else ('PASS' if ok else 'FAIL')} (must beat #520's Stage 2 ${REF_520_S2:,.0f}/yr)\n")

    print("#522 Hold one more day (#520 entries, exit at the next day's close)")
    f = fills(hl, 4, PERP, hold_days=1)
    a, b = summ(f, HL[0]), summ(f, HL[1])
    print(fmt("Stage 1", a))
    print(fmt("Stage 2", b))
    ok = (not killed(a)) and b["m"] >= 0.003 and b["t"] >= 2 and b["usd"] > REF_520_S2
    print(f"   VERDICT {'KILL (Stage 1)' if killed(a) else ('PASS' if ok else 'FAIL')}\n")

    for num, label, cd, costs, w in (
            ("#523", "HIP-3 builder perps", load_hl("fivehigh_hip3_1d", "coin"), PERP,
             ((T("2025-11-01"), T("2026-04-30")), (T("2026-05-01"), T("2026-11-25")))),
            ("#524", "Hyperliquid spot tokens", load_hl("fivehigh_hl_spot_1d", "pair"), SPOT,
             ((T("2024-05-01"), T("2025-06-30")), (T("2025-07-01"), T("2026-11-25"))))):
        f = fills(cd, 4, costs)
        a, b = summ(f, w[0]), summ(f, w[1])
        print(f"{num} #520 on {label} ({cd['coin'].nunique()} markets)")
        print(fmt("Stage 1", a))
        print(fmt("Stage 2", b))
        ok = (not killed(a)) and b["n"] >= 30 and b["m"] >= 0.003 and b["t"] >= 2 and b["usd"] >= 1000
        print(f"   VERDICT {'KILL (Stage 1)' if killed(a) else ('PASS' if ok else 'FAIL')}"
              f"{' (Stage 1 < 30 fills: no kill possible)' if a['n'] < 30 else ''}\n")

    bn = load_hl("uncharted_389_binance_ohlc", "sym", ms=False)
    f = fills(bn, 4, PERP)
    a, b = summ(f, HL[0]), summ(f, HL[1])
    print(f"#525 #520 on Binance USD-M perps ({bn['coin'].nunique()} symbols; evidence only, not tradable from Malaysia)")
    print(fmt("Stage 1", a))
    print(fmt("Stage 2", b))
    ok = (not killed(a)) and b["n"] >= 30 and b["m"] >= 0.003 and b["t"] >= 2
    print(f"   VERDICT {'KILL (Stage 1)' if killed(a) else ('MECHANISM CONFIRMED on Binance' if ok else 'NOT CONFIRMED on Binance')}")


if __name__ == "__main__":
    main()

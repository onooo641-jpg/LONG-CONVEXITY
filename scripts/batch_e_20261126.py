"""Batch E #447 Pendle PT dislocation buying, exactly as docs/PREREG_BATCH_E_20261126.md defines it.

    uv run python -m scripts.batch_e_20261126 | tee docs/jx_runs/batch_e_20261126.txt
"""
from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd

PUB = Path(__file__).resolve().parent.parent / "data" / "public"
STABLE_RE = re.compile(r"usd|dai|gho|frax|usr|usx|ausd|usde|usdai|usdf|usdg|usd0|eusd|deusd|reusd|syrup", re.I)
SLUG = {1: "ethereum", 42161: "arbitrum", 8453: "base", 56: "bsc", 146: "sonic", 999: "hyperliquid", 9745: "plasma",
        5000: "mantle", 80094: "berachain", 10: "optimism"}
COST = 0.004


def tstat(x):
    x = np.asarray(x, float)
    return float(x.mean() / (x.std(ddof=1) / np.sqrt(len(x)))) if len(x) > 2 and x.std(ddof=1) > 0 else float("nan")


def load():
    mk = pd.read_parquet(PUB / "batche_pendle_markets.parquet")
    h = pd.read_parquet(PUB / "batche_pendle_history.parquet")
    u = pd.read_parquet(PUB / "batche_underlying_1d.parquet")
    mk["expiry"] = pd.to_datetime(mk["expiry"], utc=True)
    mk["chain"] = mk["chain"].astype(int)
    mk["uaddr"] = mk["underlying"].astype(str).str.split("-").str[-1]
    h["ts"] = pd.to_datetime(h["timestamp"], utc=True, errors="coerce").dt.normalize()
    u["ts"] = pd.to_datetime(u["t"], unit="s", utc=True).dt.normalize()
    U = {k: g.drop_duplicates("ts").set_index("ts")["price"].sort_index() for k, g in u.groupby(["chain_slug", "underlying"])}
    return mk.drop_duplicates("address"), h.dropna(subset=["ts", "impliedApy"]), U


def events(mk, h, U, thr=0.05, same_day=False, stable=True):
    rows = []
    hist = {a: g.drop_duplicates("ts").set_index("ts").sort_index() for a, g in h.groupby("address")}
    for _, m in mk.iterrows():
        if bool(STABLE_RE.search(str(m["name"]))) != stable or m["address"] not in hist:
            continue
        x = hist[m["address"]]
        up = U.get((SLUG.get(m["chain"]), m["uaddr"]))
        if up is None or len(x) < 20:
            continue
        imp, tvl = x["impliedApy"].astype(float), x["tvl"].astype(float)
        med = imp.shift(1).rolling(14, min_periods=10).median()
        idx = list(x.index)
        busy_until = None
        for i, ts in enumerate(idx):
            if busy_until is not None and ts <= busy_until:
                continue
            if pd.isna(med.iloc[i]) or imp.iloc[i] - med.iloc[i] < thr:
                continue
            if (m["expiry"] - ts).days < 14 or not (tvl.iloc[i] >= 1_000_000):
                continue
            j = i if same_day else i + 1
            if j >= len(idx):
                continue
            te = idx[j]
            yrs = lambda t: max((m["expiry"] - t).total_seconds() / (365 * 86400), 0.0)  # noqa: E731
            p_in = (1 + imp.iloc[j]) ** (-yrs(te))
            u_in = up.asof(te)
            target = med.iloc[i] + 0.01
            exit_ts, p_out = None, None
            for k in range(j + 1, len(idx)):
                tk = idx[k]
                if tk >= m["expiry"]:
                    break
                if imp.iloc[k] <= target or (tk - te).days >= 30:
                    exit_ts, p_out = tk, (1 + imp.iloc[k]) ** (-yrs(tk))
                    break
            if exit_ts is None:
                if m["expiry"] <= pd.Timestamp("2026-11-26", tz="UTC") and (m["expiry"] - te).days <= 30 + 1:
                    exit_ts, p_out = m["expiry"].normalize(), 1.0
                elif j + 1 < len(idx):
                    continue  # still open at data end: dropped
                else:
                    continue
            u_out = up.asof(exit_ts)
            if not (np.isfinite(u_in) and np.isfinite(u_out) and u_in > 0):
                continue
            ret = (p_out * u_out) / (p_in * u_in) - 1 - COST
            rows.append({"name": m["name"], "address": m["address"], "signal": ts, "entry": te, "exit": exit_ts,
                         "spike": imp.iloc[i] - med.iloc[i], "ret": ret, "depeg": u_out / u_in - 1})
            busy_until = exit_ts
    return pd.DataFrame(rows)


def dollars(ev, lo, hi):
    e = ev[(ev["signal"] >= lo) & (ev["signal"] < hi)].sort_values("entry")
    kept, open_ = [], []
    for _, r in e.iterrows():
        open_ = [x for x in open_ if x > r["entry"]]
        if len(open_) < 3:
            kept.append(r)
            open_.append(r["exit"])
    k = pd.DataFrame(kept)
    yrs = (pd.Timestamp(hi) - pd.Timestamp(lo)).days / 365.25
    return (k["ret"].sum() * 5000 / yrs if len(k) else 0.0), len(k)


def show(e, label):
    if e.empty:
        print(f"  {label}: no events")
        return 0, np.nan, np.nan, np.nan
    r = e["ret"]
    print(f"  {label}: events {len(r)} ({e['address'].nunique()} markets), mean {r.mean():.2%}, median {r.median():.2%}, t {tstat(r):.2f}, "
          f"win {(r > 0).mean():.0%}, worst {r.min():.1%}, mean depeg {e['depeg'].mean():.2%}")
    return len(r), r.mean(), tstat(r), (r > 0).mean()


def main():
    print("===== Batch E #447 Pendle PT dislocation buying")
    mk, h, U = load()
    print(f"  markets {len(mk)} (stable by name {mk['name'].astype(str).str.contains(STABLE_RE).sum()}); history rows {len(h)}; "
          f"underlying series {len(U)}")
    ev = events(mk, h, U)
    s1 = ev[(ev["signal"] >= "2024-03-01") & (ev["signal"] < "2025-01-01")] if len(ev) else ev
    s2 = ev[(ev["signal"] >= "2025-01-01") & (ev["signal"] < "2026-11-01")] if len(ev) else ev
    n1, m1, _, _ = show(s1, "Stage 1 (2024-03..2024-12)")
    if n1 < 10 or not (m1 > 0):
        print("  STAGE 1 VERDICT (#447): KILL")
    else:
        print("  STAGE 1 VERDICT (#447): survives (kill-only)")
        n2, m2, t2, w2 = show(s2, "Stage 2 (2025-01..2026-10)")
        usd, nk = dollars(ev, "2025-01-01", "2026-11-01")
        print(f"  sized: $5,000/event, <= 3 open: {nk} trades, ${usd:,.0f}/yr")
        ok = n2 >= 30 and m2 >= 0.01 and t2 >= 2 and w2 >= 0.65 and usd >= 10_000
        print(f"  STAGE 2 VERDICT (#447): {'PASS' if ok else 'FAIL'}")
        if len(s2):
            print("  Stage 2 worst 5: " + "; ".join(f"{r['name']} {r['entry'].date()} {r['ret']:.1%}" for _, r in s2.nsmallest(5, "ret").iterrows()))
    print("\n  variants (reported only):")
    for lab, kw in (("threshold 3 pts", {"thr": 0.03}), ("threshold 8 pts", {"thr": 0.08}), ("same-day entry", {"same_day": True}),
                    ("non-stable PTs (USD terms incl. underlying move)", {"stable": False})):
        v = events(mk, h, U, **kw)
        if v.empty:
            print(f"  {lab}: no events")
            continue
        for wl, lo, hi in (("S1", "2024-03-01", "2025-01-01"), ("S2", "2025-01-01", "2026-11-01")):
            show(v[(v["signal"] >= lo) & (v["signal"] < hi)], f"{lab} {wl}")


if __name__ == "__main__":
    main()

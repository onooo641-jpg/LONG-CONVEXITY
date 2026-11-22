"""#320 small-capacity high-reward pools (docs/PREREG_SMALLCAP_20261122.md).

    uv run python -m scripts.smallcap_20261122 | tee docs/jx_runs/smallcap_20261122.txt
"""
from __future__ import annotations

import sys

import numpy as np
import pandas as pd

P0, P1 = pd.Timestamp("2026-08-01", tz="UTC"), pd.Timestamp("2026-11-01", tz="UTC")
S0, SPLIT = pd.Timestamp("2025-11-01", tz="UTC"), pd.Timestamp("2026-05-01", tz="UTC")
SLOT, K = 1500.0, 10
ann = lambda s: float(s.mean() * 365 * 100) if len(s) else float("nan")  # noqa: E731


def load():
    pools = pd.read_parquet("data/public/smallcap_pools.parquet").set_index("pool")
    ch = pd.read_parquet("data/public/smallcap_charts.parquet")
    ch["day"] = pd.to_datetime(ch["ts"], utc=True).dt.floor("D")
    ch = ch.drop_duplicates(["pool", "day"])
    px = pd.read_parquet("data/public/smallcap_prices.parquet")
    px["day"] = pd.to_datetime(px["ts"], unit="s", utc=True).dt.floor("D")
    PX = px.drop_duplicates(["token", "day"]).pivot(index="day", columns="token", values="price").sort_index()
    return pools, ch, PX


def toks(v):
    return [str(t) for t in v] if v is not None and hasattr(v, "__iter__") and not isinstance(v, str) else []


def run(pools, ch, PX, start, end, cost_mult=1.0, stable_only=False):
    A = ch.pivot(index="day", columns="pool", values="apyBase").fillna(0)
    RW = ch.pivot(index="day", columns="pool", values="apyReward").reindex(A.index).fillna(0)
    T = ch.pivot(index="day", columns="pool", values="tvlUsd").reindex(A.index)
    Y = (A + RW).clip(upper=2000)
    days = pd.date_range(start, end - pd.Timedelta(days=1), freq="D", tz="UTC")
    out, log, collapses, dead = [], [], 0, 0
    for m in pd.date_range(start, end - pd.Timedelta(days=1), freq="MS", tz="UTC"):
        pday = m - pd.Timedelta(days=1)
        if pday not in T.index:
            continue
        tv = T.loc[pday]
        ok = tv[(tv >= 1e5) & (tv <= 2e6)].index
        if stable_only:
            ok = [p for p in ok if p in pools.index and bool(pools.at[p, "stablecoin"])]
        sc = Y.loc[pday - pd.Timedelta(days=29):pday, list(ok)].mean()
        sc = sc[sc >= 50].sort_values(ascending=False)
        held = list(sc.index[:K])
        log.append(f"    {m:%Y-%m}: {len(sc)} eligible; held " + ", ".join(f"{pools.at[p, 'project'] if p in pools.index else p[:6]}/"
                                                                            f"{pools.at[p, 'symbol'] if p in pools.index else ''} {sc[p]:.0f}%" for p in held[:4]) + (" ..." if len(held) > 4 else ""))
        mdays = [d for d in days if d.year == m.year and d.month == m.month]
        alive = {p: True for p in held}
        entry = {}
        for p in held:
            rt = [t for t in toks(pools.at[p, "rewardTokens"] if p in pools.index else None) if t in PX.columns]
            ut = [t for t in toks(pools.at[p, "underlyingTokens"] if p in pools.index else None) if t in PX.columns]
            entry[p] = (rt, ut, {t: PX[t].asof(pday) for t in rt + ut})
        for j, d in enumerate(mdays):
            r = []
            for p in held:
                if not alive[p]:
                    r.append(0.0)
                    continue
                last_chart = ch.loc[ch.pool == p, "day"].max()
                t7 = T.loc[d - pd.Timedelta(days=7):d, p]
                if d > last_chart:
                    alive[p] = False
                    dead += 1
                    r.append(-0.5)
                    continue
                if len(t7.dropna()) > 1 and t7.dropna().iloc[-1] < 0.3 * t7.max():
                    alive[p] = False
                    collapses += 1
                    r.append(-0.5)
                    continue
                rt, ut, p0 = entry[p]
                f_rw = np.nanmean([PX[t].asof(d) / p0[t] for t in rt if p0.get(t)]) if rt else 1.0
                f_rw = 1.0 if not np.isfinite(f_rw) else f_rw
                base = float(np.nan_to_num(A.at[d, p])) if d in A.index else 0.0
                rw = float(np.nan_to_num(RW.at[d, p])) if d in RW.index else 0.0
                day = base / 100 / 365 + rw / 100 / 365 * f_rw
                stable = p in pools.index and bool(pools.at[p, "stablecoin"])
                if not stable and ut:
                    ch_ = [PX[t].asof(d) / PX[t].asof(d - pd.Timedelta(days=1)) - 1 for t in ut]
                    ch_ = [c for c in ch_ if np.isfinite(c)]
                    if ch_:
                        if len(ut) == 1 and (pools.at[p, "exposure"] if p in pools.index else "") == "single":
                            day += ch_[0]
                        else:
                            day -= 0.5 * abs(np.mean(ch_)) if len(ch_) == 1 else 0.5 * abs(ch_[0] - ch_[-1])
                r.append(day)
            c = len(held) * 2 * 15 / SLOT / K * cost_mult if j == 0 else 0.0
            out.append((d, (float(np.mean(r)) if r else 0.0) * (len(held) / K) - c))
    return pd.Series(dict(out)), log, collapses, dead


def main() -> int:
    pools, ch, PX = load()
    print(f"pools {len(pools)}; chart rows {len(ch)}; priced tokens {PX.shape[1]}")
    print("NOTE: the current DefiLlama list omits dead pools; pools whose chart stops are booked at -50% (survivorship partly corrected)\n")
    for label, so in (("all pools", False), ("stablecoin pools only", True)):
        s, log, col, dead = run(pools, ch, PX, P0, P1, stable_only=so)
        v = ann(s)
        print(f"#320 {label}: Stage 1 2026-08..10 {v:.2f}%/yr on capital; collapses {col}, dead charts {dead}")
        print("\n".join(log))
        if not v >= 25:
            print("  -> KILL -> FAIL (Stage 1)\n")
            continue
        s2, log2, col2, dead2 = run(pools, ch, PX, S0, P1, stable_only=so)
        s2c, *_ = run(pools, ch, PX, S0, P1, cost_mult=2.0, stable_only=so)
        h1, h2, c2 = ann(s2[s2.index < SPLIT]), ann(s2[s2.index >= SPLIT]), ann(s2c)
        mon = s2.groupby(s2.index.strftime("%Y-%m")).sum() * 100
        ok = h1 >= 50 and h2 >= 50 and c2 >= 30
        print(f"  Stage 2 2025-11..2026-10: halves {h1:.2f}% / {h2:.2f}%; costs x2 {c2:.2f}%; worst month {mon.min():.1f}%; collapses {col2}, "
              f"dead {dead2}; ${ann(s2) * 150:,.0f}/yr on $15K")
        print(f"  VERDICT: {'PASS' + (' (near-miss under F4: non-stable)' if not so else '') if ok else 'FAIL'}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())

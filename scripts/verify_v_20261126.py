"""Verification stage V for #429/#430 (Binance spot) and #421 (GeckoTerminal pools) — docs/PREREG_BATCH_C_20261126.md.

    uv run python -m scripts.verify_v_20261126 | tee docs/jx_runs/verify_v_20261126.txt
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

PUB = Path(__file__).resolve().parent.parent / "data" / "public"
BN = {"first-digital-usd": "FDUSDUSDT", "usd-coin": "USDCUSDT", "true-usd": "TUSDUSDT", "binance-usd": "BUSDUSDT",
      "paxos-standard": "USDPUSDT", "dai": "DAIUSDT", "usds": "USDSUSDT"}


def stable_events(ids, thr):
    d = pd.read_parquet(PUB / "batchc_stables_1h.parquet")
    d = d[d["id"].isin(ids)].copy()
    d["ts"] = pd.to_datetime(d["t"], unit="s", utc=True)
    rows = []
    for g, x in d.groupby("id"):
        x = x.drop_duplicates("ts").set_index("ts")["price"].sort_index()
        x = x[(x > 0.3) & (x < 1.5)]
        busy = None
        for ts, v in x.items():
            if (busy is not None and ts <= busy) or v > thr:
                continue
            after = x[(x.index > ts) & (x.index <= ts + pd.Timedelta(days=30))]
            hit = after[after >= 0.997]
            ex_ts, ex = (hit.index[0], hit.iloc[0]) if len(hit) else ((after.index[-1], after.iloc[-1]) if len(after) else (None, None))
            if ex_ts is None:
                continue
            rows.append({"id": g, "ts": ts, "buy": v, "ret": ex / v - 1 - 0.001})
            busy = ex_ts
    return pd.DataFrame(rows)


def verify_stables(label, ids, thr):
    print(f"#### V: {label}")
    vp = PUB / "batchc_verify_spot_1h.parquet"
    if not vp.exists():
        print("  Binance spot klines not fetched yet (job uverify)")
        return
    sp = pd.read_parquet(vp)
    sp["ts"] = pd.to_datetime(sp["t"], unit="s", utc=True)
    S = {s: g.drop_duplicates("ts").set_index("ts").sort_index() for s, g in sp.groupby("sym")}
    ev = stable_events(ids, thr)
    ev = ev[ev["ts"] >= "2023-01-01"]
    out = []
    for _, e in ev.iterrows():
        sym = BN.get(e["id"])
        k = S.get(sym)
        if k is None or e["ts"] not in k.index:
            out.append({**e, "status": "unverifiable"})
            continue
        low = k.at[e["ts"], "l"]
        later = k[(k.index > e["ts"]) & (k.index <= e["ts"] + pd.Timedelta(days=30))]
        ok = low <= e["buy"] * 1.005 and (later["h"] >= 0.997).any()
        out.append({**e, "status": "confirmed" if ok else "not confirmed", "bn_low": low})
    t = pd.DataFrame(out)
    if t.empty:
        print("  no Stage 2 events")
        return
    print("  by token: " + "; ".join(f"{g} {dict(x['status'].value_counts())}" for g, x in t.groupby("id")))
    ver = t[t["status"] != "unverifiable"]
    conf = t[t["status"] == "confirmed"]
    share = len(conf) / len(ver) if len(ver) else np.nan
    print(f"  Stage 2 events {len(t)}; verifiable {len(ver)}; confirmed {len(conf)} ({share:.0%} of verifiable)")
    if len(conf):
        r = conf["ret"]
        print(f"  confirmed events alone: n {len(r)}, mean {r.mean():.2%}, profitable {(r > 0).mean():.0%}")
    keep = len(ver) > 0 and share >= 0.70 and len(conf) >= 3 and conf["ret"].mean() >= 0.01 and (conf["ret"] > 0).mean() >= 0.75
    print(f"  V VERDICT: {'PASS KEPT' if keep else 'DOWNGRADED (data artefact / not confirmed)'}")


def verify_421():
    print("\n#### V: #421 withdrawal discounts vs on-chain NAV, events from 2026-05 checked on DEX pools")
    r = pd.read_parquet(PUB / "batcha_rates.parquet").dropna(subset=["rate"])
    r["day"] = pd.to_datetime(r["day"], utc=True)
    R = r.pivot(index="day", columns="token", values="rate").sort_index()
    m = pd.read_parquet(PUB / "distinct_nav_1h.parquet")
    m["ts"] = pd.to_datetime(m["t"], unit="s", utc=True).dt.round("h")
    M = m.drop_duplicates(["key", "ts"]).pivot(index="ts", columns="key", values="price").sort_index()
    pools = json.loads((PUB / "uncharted_384_pools.json").read_text())
    o = pd.read_parquet(PUB / "uncharted_384_ohlcv.parquet")
    o["day"] = pd.to_datetime(o["t"], unit="s", utc=True).dt.normalize()
    spec = {"weETH": ("weeth", "coingecko:wrapped-eeth", "coingecko:ethereum"), "sUSDe": ("susde", "coingecko:ethena-staked-usde", "coingecko:ethena-usde"),
            "pufETH": ("pufeth", "coingecko:pufeth", "coingecko:ethereum"), "rsETH": ("rseth", "coingecko:kelp-dao-restaked-eth", "coingecko:ethereum")}
    rows = []
    for tok, (sym, mk, uk) in spec.items():
        ps = [p for p in pools if p["sym"] == sym]
        if not ps or tok not in R:
            continue
        pool = max(ps, key=lambda p: p["reserve_usd"])
        g = o[(o["network"] == pool["network"]) & (o["address"] == pool["address"])].drop_duplicates("day").set_index("day").sort_index()
        base_first = pool["name"].lower().lstrip().startswith(sym)
        close = g["c"].astype(float) if base_first else 1 / g["c"].astype(float)
        low = g["l"].astype(float) if base_first else 1 / g["h"].astype(float)
        nav = R[tok].reindex(M.index, method="ffill")
        ratio = ((M[mk] / M[uk]) / nav).dropna()
        ev = ratio[(ratio <= 0.99) & (ratio.index >= "2026-05-01")]
        days = sorted({t.normalize() for t in ev.index})
        for dday in days:
            n = R[tok].asof(dday)
            pc, pl = close.get(dday), low.get(dday)
            vol = float(g["v_usd"].get(dday, np.nan)) if "v_usd" in g else np.nan
            ok = (pd.notna(pc) and pc <= n * 0.995) or (pd.notna(pl) and pl <= n * 0.995)
            rows.append({"tok": tok, "day": dday.date(), "pool": pool["name"], "nav": n, "pool_close": pc, "pool_low": pl, "pool_vol_usd": vol,
                         "status": ("confirmed" if ok else "not confirmed") if pd.notna(pc) else "unverifiable"})
    t = pd.DataFrame(rows)
    if t.empty:
        print("  no #421 event days since 2026-05")
        return
    print(t.to_string(index=False, float_format=lambda v: f"{v:10.4f}"))
    ver = t[t["status"] != "unverifiable"]
    share = (ver["status"] == "confirmed").mean() if len(ver) else np.nan
    print(f"  event days {len(t)}; verifiable {len(ver)}; confirmed share {share:.0%}")
    print(f"  V VERDICT (#421): {'PASS KEPT' if len(ver) and share >= 0.70 else 'DOWNGRADED (CoinGecko discounts not seen on the DEX pool)'}")


def main():
    print("===== Verification stage V")
    verify_stables("#429 fiat-backed stables (Binance spot)", list(BN)[:5], 0.98)
    verify_stables("#430 crypto-backed stables (Binance spot where listed)", ["dai", "usds", "liquity-usd", "frax", "usdd", "usual-usd", "gho", "crvusd", "ethena-usde"], 0.97)
    verify_421()


if __name__ == "__main__":
    main()

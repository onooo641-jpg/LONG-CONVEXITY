"""Batch A #419-#421 (docs/PREREG_BATCH_A_20261126.md).

    uv run python -m scripts.batch_a_20261126 | tee docs/jx_runs/batch_a_20261126.txt
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

PUB = Path(__file__).resolve().parent.parent / "data" / "public"
POT = 15_000.0


def tstat(r):
    r = pd.Series(r).dropna()
    return r.mean() / (r.std(ddof=1) / np.sqrt(len(r))) if len(r) > 1 else np.nan


def part419(raw):
    print("#### #419 crypto variance risk premium: weekly short ATM straddles (no hedge), BTC + ETH")
    for u, v in raw.get("derive_terms", {}).items():
        print(f"  Derive terms {u}: HTTP {v['status']}, {v['chars']} chars, 'Malaysia' found: {bool(v['Malaysia'])}")
        for snip in (v.get("restricted") or [])[:1]:
            print(f"      ...{snip[:400]}...")
    b = pd.read_parquet(PUB / "uncharted_389_binance_ohlc.parquet", columns=["sym", "t", "c"])
    b["day"] = pd.to_datetime(b["t"], unit="s", utc=True).dt.normalize()
    weekly = {}
    for cur, sym in (("BTC", "BTCUSDT"), ("ETH", "ETHUSDT")):
        dv = raw.get(f"dvol_{cur}") or []
        if not dv:
            print(f"  {cur}: no DVOL data")
            continue
        iv = pd.Series({pd.Timestamp(int(x[0]), unit="ms", tz="UTC").normalize(): float(x[4]) / 100 for x in dv}).sort_index()
        px = b[b["sym"] == sym].drop_duplicates("day").set_index("day")["c"].sort_index()
        rows = []
        for d in [x for x in px.index if x.weekday() == 0]:
            e = d + pd.Timedelta(days=7)
            if e not in px.index or d not in iv.index:
                continue
            s0, s1, sig = px[d], px[e], iv[d]
            w = np.sqrt(7 / 365)
            prem = 0.8 * s0 * sig * w * 0.90
            cap = POT / 2
            units = 0.25 * cap / (5 * sig * w * s0)  # a 5-sigma weekly move loses <= 25% of the leg's capital
            pnl = units * (prem - abs(s1 - s0))
            rows.append({"day": d, "ret": pnl / cap, "iv": sig, "rv_move": abs(s1 / s0 - 1)})
        weekly[cur] = pd.DataFrame(rows).set_index("day")
        print(f"  {cur}: weeks {len(rows)}, mean IV {weekly[cur]['iv'].mean():.0%}")
    if not weekly:
        print("  STAGE VERDICT (#419): not testable (no DVOL)")
        return
    port = pd.concat([w["ret"] for w in weekly.values()], axis=1).mean(axis=1).dropna()

    def seg(r, label):
        if r.empty:
            print(f"  {label}: no weeks")
            return np.nan, np.nan, np.nan
        eq = (1 + r).cumprod()
        ann = eq.iloc[-1] ** (52 / len(r)) - 1
        dd = float((eq / eq.cummax() - 1).min())
        print(f"  {label}: weeks {len(r)}, mean weekly {r.mean():.2%}, t {tstat(r):.2f}, annualised {ann:.1%}, worst drawdown {dd:.1%}, "
              f"worst week {r.min():.1%}")
        return ann, dd, tstat(r)
    a1, d1, _ = seg(port[port.index <= "2023-12-31"], "Stage 1 (2021-04..2023-12)")
    s1 = not (pd.isna(a1) or a1 < 0.15 or d1 < -0.50)
    print(f"  STAGE 1 VERDICT: {'survives (kill-only)' if s1 else 'KILL'}")
    a2, d2, t2 = seg(port[port.index >= "2024-01-01"], "Stage 2 (out-of-sample 2024-01..2026-10)")
    ok = s1 and a2 >= 0.25 and d2 >= -0.35 and t2 >= 2
    print(f"  STAGE 2 VERDICT: {'PASS' if ok else ('FAIL' if s1 else 'not judged (Stage 1 killed) — context')}")


def part420(raw):
    print("\n#### #420 dYdX reward farming (Stage 0 probe)")
    for u, v in raw.get("dydx_probe", {}).items():
        print(f"  {v['status']} {u[:100]} | {(v['head'] or '')[:200]}")
    print("  STAGE 0: see probe; the protocol-wide reward and fee totals are needed for the rule")


def part421():
    print("\n#### #421 withdrawal-queue discounts vs on-chain exchange rates")
    rp, mp = PUB / "batcha_rates.parquet", PUB / "distinct_nav_1h.parquet"
    if not rp.exists() or not mp.exists():
        print("  data not fetched yet")
        return
    r = pd.read_parquet(rp).dropna(subset=["rate"])
    print(f"  on-chain rate rows: {len(r)} ({r.groupby('token').size().to_dict()})")
    if r.empty:
        print("  STAGE VERDICT (#421): not testable (no archive eth_call answered)")
        return
    r["day"] = pd.to_datetime(r["day"], utc=True)
    R = r.pivot(index="day", columns="token", values="rate").sort_index()
    m = pd.read_parquet(mp)
    m["ts"] = pd.to_datetime(m["t"], unit="s", utc=True).dt.round("h")
    M = m.drop_duplicates(["key", "ts"]).pivot(index="ts", columns="key", values="price").sort_index()
    spec = {"weETH": ("coingecko:wrapped-eeth", "coingecko:ethereum", 0.03), "sUSDe": ("coingecko:ethena-staked-usde", "coingecko:ethena-usde", 0.08),
            "pufETH": ("coingecko:pufeth", "coingecko:ethereum", 0.03), "rsETH": ("coingecko:kelp-dao-restaked-eth", "coingecko:ethereum", 0.03)}
    trades = []
    for tok, (mk, uk, y) in spec.items():
        if tok not in R or mk not in M or uk not in M:
            continue
        nav = R[tok].reindex(M.index, method="ffill")  # rate (underlying per token), day value held through the next day
        ratio = (M[mk] / M[uk]) / nav
        busy = None
        for ts, v in ratio.dropna().items():
            if busy is not None and ts <= busy:
                continue
            if v > 0.99:
                continue
            red = ts + pd.Timedelta(days=7)
            nav_out = R[tok].asof(red)
            if pd.isna(nav_out) or red > M.index[-1]:
                continue
            ret = nav_out / (v * nav.asof(ts)) - 1 - 0.001 - y * 7 / 365
            trades.append({"tok": tok, "ts": ts, "disc": 1 - v, "ret": ret})
            busy = red
    t = pd.DataFrame(trades)

    def seg(x, start, end, label):
        x = x[(x["ts"] >= start) & (x["ts"] <= end)] if len(x) else x
        yrs = (end - start).days / 365
        if x.empty:
            print(f"  {label}: no events")
            return 0, 0.0, np.nan
        per_yr = (x["ret"] * 5000).sum() / yrs
        print(f"  {label}: events {len(x)} ({x.groupby('tok').size().to_dict()}), mean {x['ret'].mean():.2%}, median discount {x['disc'].median():.2%}, "
              f"profitable {(x['ret'] > 0).mean():.0%}, ${per_yr:,.0f}/yr")
        return len(x), per_yr, (x["ret"] > 0).mean()
    n1, p1, _ = seg(t, pd.Timestamp("2024-01-01", tz="UTC"), pd.Timestamp("2024-12-31", tz="UTC"), "Stage 1 (2024)")
    s1 = not (n1 < 4 or p1 < 3000)
    print(f"  STAGE 1 VERDICT: {'survives (kill-only)' if s1 else 'KILL'}")
    n2, p2, w2 = seg(t, pd.Timestamp("2025-01-01", tz="UTC"), pd.Timestamp("2026-10-31", tz="UTC"), "Stage 2 (out-of-sample 2025-01..2026-10)")
    ok = s1 and n2 >= 4 and p2 >= 3000 and (w2 or 0) >= 0.75
    print(f"  STAGE 2 VERDICT: {'PASS' if ok else ('FAIL' if s1 else 'not judged (Stage 1 killed) — context')}")


def main():
    print("===== Batch A #419-#421")
    rawp = PUB / "batcha_raw.json"
    if not rawp.exists():
        print("  data not fetched yet (job ubatcha)")
        return
    raw = json.loads(rawp.read_text())
    part419(raw)
    part420(raw)
    part421()


if __name__ == "__main__":
    main()

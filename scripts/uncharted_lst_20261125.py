"""#384 U-T2: withdrawal-queue discounts (docs/PREREG_UNCHARTED_20261125.md).

    uv run python -m scripts.uncharted_lst_20261125 | tee docs/jx_runs/uncharted_lst_20261125.txt
Reads data/public/uncharted_384_{ohlcv.parquet,pools.json,llama.parquet} (Actions job u384lst).
Rule: ratio = token price in its underlying (daily close, main DEX pool). NAV proxy = 30-day rolling max of the ratio. Event = close
>= 1.0% below the NAV proxy. Buy min($15,000, 2% of the pool's daily USD volume); redeem after the queue at the NAV proxy of that day;
minus 0.10% fee and the queue's lost staking yield. One position per token at a time.
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

PUB = Path(__file__).resolve().parent.parent / "data" / "public"
QUEUE = {"khype": 9, "sthype": 9, "behype": 9, "ezeth": 7, "rseth": 7, "weeth": 7, "pufeth": 7, "susde": 7}
YIELD = {"khype": 0.025, "sthype": 0.025, "behype": 0.025, "ezeth": 0.03, "rseth": 0.03, "weeth": 0.03, "pufeth": 0.03, "susde": 0.08}
CAP, VOL_SHARE, FEE, TRIGGER, WIN = 15_000.0, 0.02, 0.0010, 0.01, 30


def series_from_pool(o, pool):
    """Daily close ratio token/underlying from a GeckoTerminal pool (base priced in quote; inverted if the LST is the quote)."""
    d = o[(o["network"] == pool["network"]) & (o["address"] == pool["address"])].copy()
    d["day"] = pd.to_datetime(d["t"], unit="s", utc=True).dt.normalize()
    d = d.drop_duplicates("day").set_index("day").sort_index()
    base_first = pool["name"].lower().lstrip().startswith(pool["sym"])
    ratio = d["c"].astype(float) if base_first else 1.0 / d["c"].astype(float)
    return ratio, d["v_usd"].astype(float)


def run_token(sym, ratio, vol):
    ratio = ratio[(ratio > 0.3) & (ratio < 3.0)]
    nav = ratio.rolling(WIN, min_periods=10).max()
    q = QUEUE[sym]
    trades, busy_until = [], None
    for day, r in ratio.items():
        if busy_until is not None and day <= busy_until:
            continue
        n = nav.get(day)
        if pd.isna(n) or r > n * (1 - TRIGGER):
            continue
        red_day = day + pd.Timedelta(days=q)
        n_red = nav.get(red_day)
        if pd.isna(n_red):
            continue
        size = min(CAP, VOL_SHARE * float(vol.get(day, 0) or 0))
        if size <= 0:
            continue
        gross = n_red / r - 1
        net = gross - FEE - YIELD[sym] * q / 365
        trades.append({"sym": sym, "day": day.date(), "disc": 1 - r / n, "size": size, "gross": gross, "net": net, "pnl": size * net})
        busy_until = red_day
    return trades, ratio.index.min(), ratio.index.max()


def main():
    print("===== #384 U-T2 withdrawal-queue discounts")
    pools = json.loads((PUB / "uncharted_384_pools.json").read_text())
    o = pd.read_parquet(PUB / "uncharted_384_ohlcv.parquet")
    all_tr, years = [], {}
    for sym in QUEUE:
        ps = [p for p in pools if p["sym"] == sym]
        if not ps:
            print(f"  {sym}: no pool found -> not testable")
            continue
        main_pool = max(ps, key=lambda p: p["reserve_usd"])
        ratio, vol = series_from_pool(o, main_pool)
        if len(ratio) < WIN + 10:
            print(f"  {sym}: {len(ratio)} days in {main_pool['name']} ({main_pool['network']}) -> not testable")
            continue
        tr, a, b = run_token(sym, ratio, vol)
        yrs = ((b - a).days + 1) / 365
        years[sym] = yrs
        pnl = sum(t["pnl"] for t in tr)
        print(f"  {sym}: pool {main_pool['name']} ({main_pool['network']}, reserve ${main_pool['reserve_usd']:,.0f}); {a.date()}..{b.date()} "
              f"({yrs:.2f} yr); median daily volume ${vol.median():,.0f}; events {len(tr)}; net P&L ${pnl:,.0f} (${pnl / yrs:,.0f}/yr)")
        for t in tr[:12]:
            print(f"      {t['day']} discount {t['disc']:.2%} size ${t['size']:,.0f} net {t['net']:.2%} P&L ${t['pnl']:,.0f}")
        all_tr += tr
    if not all_tr:
        print("  no events in any token")
        print("  STAGE 1 VERDICT: KILL (fewer than 4 events)")
        return
    t = pd.DataFrame(all_tr).sort_values("day")
    # one $15,000 pot: take an event only if the pot is free (redemption days returned)
    span = max(years.values())
    tot, n = t["pnl"].sum(), len(t)
    print(f"\n  all tokens, each with its own position: events {n}; net P&L ${tot:,.0f} over up to {span:.2f} yr "
          f"-> ${tot / span:,.0f}/yr; mean net per event {t['net'].mean():.2%}; losing events {(t['net'] < 0).sum()}")
    free, kept = pd.Timestamp("1970-01-01").date(), []
    for _, r in t.iterrows():
        if r["day"] >= free:
            kept.append(r)
            free = (pd.Timestamp(r["day"]) + pd.Timedelta(days=QUEUE[r["sym"]])).date()
    k = pd.DataFrame(kept)
    print(f"  one $15,000 pot (no overlap): events {len(k)}; net P&L ${k['pnl'].sum():,.0f} -> ${k['pnl'].sum() / span:,.0f}/yr")
    per_yr = k["pnl"].sum() / span  # verdict on the single $15,000 pot (the rule says "on $15,000"); decided before seeing data
    kill = n < 4 or per_yr < 3000
    print(f"  STAGE 1 VERDICT: {'KILL (' + ('fewer than 4 events' if n < 4 else 'net < $3,000/yr on $15,000') + ')' if kill else 'survives (kill-only)'}")


if __name__ == "__main__":
    main()

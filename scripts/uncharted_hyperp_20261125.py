"""#385 U-T3: short Hyperliquid pre-launch perps from listing to token launch + 7 days (docs/PREREG_UNCHARTED_20261125.md).

    uv run python -m scripts.uncharted_hyperp_20261125 | tee docs/jx_runs/uncharted_hyperp_20261125.txt
Reads data/public/uncharted_385_{candles,funding,spot}.parquet + uncharted_385_map.json (Actions job u385hyperp).
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

PUB = Path(__file__).resolve().parent.parent / "data" / "public"
FEE = 0.00045  # per side
HOLD_AFTER_TGE = 7
MAP_TOL = 0.35  # mapping check: HL close vs spot price at TGE + 7 within +-35%
# flagged after seeing the event list (not used for the verdict): AERO traded since 2023 (DefiLlama first-price artefact), OX and SHIA
# are not known pre-launch listings
SUSPECT = {"AERO", "OX", "SHIA"}


def main():
    cd = pd.read_parquet(PUB / "uncharted_385_candles.parquet")
    mp = json.loads((PUB / "uncharted_385_map.json").read_text())
    fu = pd.read_parquet(PUB / "uncharted_385_funding.parquet")
    sp = pd.read_parquet(PUB / "uncharted_385_spot.parquet")
    print("===== #385 U-T3 short Hyperliquid pre-launch perps (listing -> token launch + 7 days)")
    print(f"  HL perps with candles: {cd['coin'].nunique()}; mapped to a CoinGecko id: {len(mp)}")
    cd["day"] = pd.to_datetime(cd["t"], unit="ms", utc=True).dt.normalize()
    sp["day"] = pd.to_datetime(sp["t"], unit="s", utc=True).dt.round("D")
    fu["ts"] = pd.to_datetime(fu["t"], unit="ms", utc=True)
    pre = {c: v for c, v in mp.items() if v.get("first_spot") and v.get("first_hl_ms")
           and v["first_hl_ms"] / 1000 < v["first_spot"] - 2 * 86400}
    print(f"  pre-launch candidates (HL listing > 2 days before the first spot price): {len(pre)}")
    rows = []
    for coin, v in sorted(pre.items(), key=lambda kv: kv[1]["first_hl_ms"]):
        c = cd[cd["coin"] == coin].set_index("day").sort_index()
        tge = pd.Timestamp(v["first_spot"], unit="s", tz="UTC").normalize()
        entry_day, exit_day = c.index[0], tge + pd.Timedelta(days=HOLD_AFTER_TGE)
        r = {"coin": coin, "id": v["id"], "n_ids": v["n_ids"], "listed": entry_day.date(), "tge": tge.date(),
             "days_pre": (tge - entry_day).days}
        if exit_day not in c.index:
            r["status"] = "no HL candle at exit (delisted or not yet)"
            rows.append(r)
            continue
        entry, exit_ = float(c["c"].iloc[0]), float(c.loc[exit_day, "c"])
        s = sp[sp["coin"] == coin].drop_duplicates("day").set_index("day")["price"]
        spot_x = s.get(exit_day)
        r["map_ratio"] = (exit_ / spot_x) if spot_x and spot_x > 0 else np.nan
        r["map_ok"] = bool(spot_x and abs(exit_ / spot_x - 1) <= MAP_TOL)
        # funding: a short receives rate x position value each hour; position value = entry notional x (price / entry)
        f = fu[(fu["coin"] == coin) & (fu["ts"] >= entry_day + pd.Timedelta(days=1)) & (fu["ts"] <= exit_day + pd.Timedelta(days=1))]
        px_h = c["c"].reindex(f["ts"].dt.normalize()).to_numpy() if len(f) else np.array([])
        fund = float(np.nansum(f["rate"].to_numpy() * px_h / entry)) if len(f) else 0.0
        r.update({"entry": entry, "exit": exit_, "price_ret": exit_ / entry - 1, "funding": fund, "n_fund": len(f),
                  "max_up": float(c.loc[entry_day + pd.Timedelta(days=1):exit_day, "h"].max() / entry - 1)})
        r["short_ret"] = -(exit_ / entry - 1) + fund - 2 * FEE
        r["status"] = "ok"
        rows.append(r)
    t = pd.DataFrame(rows)
    pd.set_option("display.width", 250)
    cols = ["coin", "id", "listed", "tge", "days_pre", "status", "map_ok", "map_ratio", "price_ret", "funding", "max_up", "short_ret"]
    print(t[[c for c in cols if c in t]].to_string(index=False, float_format=lambda x: f"{x:8.3f}"))
    ok = t[t["status"] == "ok"]
    for label, d in (("all traded candidates", ok), ("mapping-checked (primary)", ok[ok["map_ok"]])):
        r = d["short_ret"]
        n = len(r)
        print(f"\n  {label}: n {n}")
        if n == 0:
            continue
        tstat = r.mean() / (r.std(ddof=1) / np.sqrt(n)) if n > 1 else np.nan
        big = float((r < -0.5).mean())
        print(f"    mean short return {r.mean():.1%}  median {r.median():.1%}  t {tstat:.2f}  win rate {(r > 0).mean():.0%}  "
              f"losses > 50%: {int((r < -0.5).sum())} ({big:.0%})  worst {r.min():.1%}  best {r.max():.1%}")
        print(f"    mean price move {d['price_ret'].mean():.1%}; mean funding to the short {d['funding'].mean():.1%}; "
              f"mean worst run-up before exit {d['max_up'].mean():.1%} (a 1x short is liquidated near +100%)")
        for y, g in d.groupby(pd.to_datetime(d["listed"]).dt.year):
            print(f"    listed {y}: n {len(g)}  mean {g['short_ret'].mean():.1%}  median {g['short_ret'].median():.1%}")
        if label.startswith("mapping"):
            liq = d["max_up"] >= 1.0
            r_iso = r.where(~liq, -1.0)
            print(f"    sensitivity, isolated 1x margin (liquidated if the price doubles after entry): {int(liq.sum())} of {n} liquidated; "
                  f"mean {r_iso.mean():.1%}, median {r_iso.median():.1%}")
            sus = d[~d["coin"].isin(SUSPECT)]["short_ret"]
            print(f"    sensitivity, without names whose pre-launch status is doubtful {sorted(SUSPECT)}: n {len(sus)} mean {sus.mean():.1%} "
                  f"median {sus.median():.1%}")
            kill = n < 6 or r.mean() <= 0 or big > 1 / 3
            why = "fewer than 6 events" if n < 6 else ("mean <= 0" if r.mean() <= 0 else ("> 1/3 lose > 50%" if big > 1 / 3 else ""))
            print(f"  STAGE 1 VERDICT: {'KILL (' + why + ')' if kill else 'survives (kill-only)'}")


if __name__ == "__main__":
    main()

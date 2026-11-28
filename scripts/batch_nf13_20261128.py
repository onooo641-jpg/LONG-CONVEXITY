"""Batch NF13 #584-#587: Hong Kong crashes, Stock Connect closures, H-share dividend tax (docs/PREREG_BATCH_NF13_20261128.md).

    uv run python -m scripts.batch_nf13_20261128 | tee docs/jx_runs/batch_nf13_20261128.txt
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

PUB = Path(__file__).resolve().parent.parent / "data" / "public"
CAP, SHARE, POT, FX, MINTURN, MINPX = 1500.0, 0.01, 15_000.0, 7.8, 5e6, 0.20
S1 = (pd.Timestamp("2015-01-01"), pd.Timestamp("2020-12-31"))
S2 = (pd.Timestamp("2021-01-01"), pd.Timestamp("2026-11-27"))


def day_of(t, tz):
    return pd.to_datetime(t, unit="s", utc=True).dt.tz_convert(tz).dt.tz_localize(None).dt.normalize()


def load():
    df = pd.concat([pd.read_parquet(PUB / f"batchnf13_px_{k}.parquet") for k in "abc"], ignore_index=True)
    ev = pd.read_parquet(PUB / "batchnf13_events.parquet")
    df["day"] = day_of(df["t"], "Asia/Hong_Kong")
    sh = df["sym"] == "000001.SS"
    df.loc[sh, "day"] = day_of(df.loc[sh, "t"], "Asia/Shanghai")
    df = df.drop_duplicates(["sym", "day"]).sort_values(["sym", "day"]).reset_index(drop=True)
    for c in ("o", "h", "l", "c", "v"):
        df[c] = df[c].astype("float64")
    ev["day"] = day_of(ev["t"], "Asia/Hong_Kong")
    return df, ev


def features(df):
    g = df.groupby("sym", sort=False)
    df["pc"] = g["c"].shift()
    df["c_n1"], df["o_n1"], df["v_n1"] = g["c"].shift(-1), g["o"].shift(-1), g["v"].shift(-1)
    df["turn"] = df["c"] * df["v"]
    df["med20"] = g["turn"].transform(lambda s: s.rolling(20).median().shift())
    df["sig"] = g["c"].transform(lambda s: s.pct_change().rolling(30).std().shift())
    df["age"] = g.cumcount()
    df["liq"] = (df["med20"] >= MINTURN) & (df["c"] >= MINPX)
    df["size"] = np.minimum(CAP, SHARE * df["turn"] / FX)
    return df


def with_pnl(f):
    if f.empty:
        return pd.DataFrame(columns=["day", "ret", "size", "pnl"])
    f = f.copy()
    f["pnl"] = f["size"] * np.minimum(1.0, POT / f.groupby("day")["size"].transform("sum")) * f["ret"]
    return f


def summ(f, w, side_cost):
    g = f[(f["day"] >= w[0]) & (f["day"] <= w[1])] if len(f) else f
    if g.empty:
        return dict(n=0)
    yrs = ((min(w[1], g["day"].max()) - w[0]).days + 1) / 365.25
    r = g["ret"].astype(float)
    daily = g.groupby("day")["pnl"].sum().sort_values()
    return dict(n=len(g), m=r.mean(), med=r.median(), t=r.mean() / (r.std(ddof=1) / np.sqrt(len(r))) if len(r) > 1 else np.nan,
                win=(r > 0).mean(), usd=g["pnl"].sum() / yrs, ex3=daily.iloc[:-3].sum() if len(daily) > 3 else np.nan,
                m15=(r - side_cost).mean())


def fmt(label, s):
    if not s.get("n"):
        return f"   {label}: no trades"
    return (f"   {label}: trades {s['n']} | mean net {s['m']:+.2%} (median {s['med']:+.2%}, t {s['t']:.2f}, win {s['win']:.0%}) "
            f"| ${s['usd']:,.0f}/yr | sum without 3 best days ${s['ex3']:,.0f} | costs x1.5 mean {s['m15']:+.2%}")


def report(num, label, f, side_cost, min_n=30):
    f = with_pnl(f)
    a, b = summ(f, S1, side_cost), summ(f, S2, side_cost)
    print(f"{num} {label}")
    print(fmt("Stage 1 2015-2020", a))
    print(fmt("Stage 2 2021-2026", b))
    if len(f):
        y = f.groupby(f["day"].dt.year)["ret"].agg(["size", "mean"])
        print("   by year: " + "; ".join(f"{k} n {int(r['size'])} {r['mean']:+.2%}" for k, r in y.iterrows()))
    if a.get("n", 0) >= min_n and not (a["m"] > 0):
        v = "KILL (Stage 1)"
    else:
        ok = b.get("n", 0) >= min_n and b["m"] >= 0.003 and b["t"] >= 2 and b["usd"] >= 3000 and b["ex3"] > 0 and b["m15"] > 0
        v = "PASS" if ok else "FAIL"
    print(f"   VERDICT {v}\n")


def main():
    df, ev = load()
    sh_days = pd.DatetimeIndex(sorted(df.loc[df["sym"] == "000001.SS", "day"].unique()))
    tf = df[df["sym"] == "2800.HK"].set_index("day").sort_index()
    st = features(df[(df["sym"] != "000001.SS") & (df["sym"] != "2800.HK")].copy())
    print(f"HK equities {st['sym'].nunique()}, rows {len(st):,}, {st['day'].min().date()}..{st['day'].max().date()}; "
          f"dividends {int((ev['kind'] == 'div').sum())}; Shanghai days {len(sh_days)}; 2800.HK days {len(tf)}\n")

    c584 = 0.003
    x = (4 * st["sig"]).clip(0.05, 0.30)
    lvl = st["pc"] * (1 - x)
    hit = st["liq"] & (st["age"] >= 30) & x.notna() & st["pc"].notna() & (st["l"] <= lvl * (1 - 0.005))
    e = st[hit].copy()
    px = np.minimum(lvl[hit], e["o"])
    e["ret"] = e["c"] / px - 1 - 2 * c584
    report("#584", "HK wick bids (4 x sigma30, clipped 5%..30%), exit at the close", e[px > 0][["day", "ret", "size"]], c584)

    m = st["liq"] & st["pc"].notna() & (st["c"] <= 0.6 * st["pc"]) & st["c_n1"].notna() & (st["v_n1"] > 0)
    e = st[m].copy()
    e["ret"] = e["c_n1"] / e["c"] - 1 - 2 * c584
    report("#585", "HK crash-day close (close >= 40% below previous close): buy, sell at the next close", e[["day", "ret", "size"]], c584)

    hk = tf.index
    lo, hi = max(hk.min(), sh_days.min()), min(hk.max(), sh_days.max())
    shut = (~hk.isin(sh_days)) & (hk > lo) & (hk < hi)
    rows, i = [], 0
    while i < len(hk):
        if shut[i]:
            j = i
            while j + 1 < len(hk) and shut[j + 1]:
                j += 1
            k = next((q for q in range(j + 1, len(hk)) if hk[q] in sh_days), None)
            if k is not None:
                r = tf["c"].iloc[k] / tf["c"].iloc[j] - 1 - 2 * 0.0005
                rows.append({"day": hk[j], "ret": r, "size": POT, "hold": k - j, "len": j - i + 1})
            i = j + 1
        else:
            i += 1
    e = pd.DataFrame(rows)
    print(f"   Connect-closure runs: {len(e)} (mean {e['len'].mean():.1f} HK days shut; hold {e['hold'].mean():.1f} days)")
    allr = (tf["c"] / tf["c"].shift() - 1).dropna()
    print(f"   placebo: mean 2800.HK close-to-close day {allr.mean():+.3%} (2015-2020 {allr[:'2020'].mean():+.3%}, "
          f"2021-2026 {allr['2021':].mean():+.3%})")
    report("#586", "Stock Connect reopening: 2800.HK from the last close before Shanghai reopens to the reopening close", e, 0.0005, min_n=15)

    c587 = 0.002
    dv = ev[ev["kind"] == "div"][["sym", "day", "value"]].rename(columns={"day": "exd", "value": "D"})
    dv = dv.groupby(["sym", "exd"], as_index=False)["D"].sum()
    st["d_n1"] = st.groupby("sym", sort=False)["day"].shift(-1)
    pre = st[["sym", "day", "d_n1", "c", "o_n1", "liq", "size"]].merge(dv, left_on=["sym", "d_n1"], right_on=["sym", "exd"])
    pre = pre[pre["liq"] & (pre["D"] / pre["c"] >= 0.02) & pre["o_n1"].notna()].copy()
    pre["ret"] = (pre["o_n1"] + 0.9 * pre["D"]) / pre["c"] - 1 - 2 * c587
    pre["size"] = CAP
    pre["drop_ratio"] = (pre["c"] - pre["o_n1"]) / pre["D"]
    print(f"   dividends >= 2% of the close on liquid stocks: {len(pre)}; median ex-open drop / dividend "
          f"{pre['drop_ratio'].median():.2f} (Stage 1 {pre[pre['day'] <= S1[1]]['drop_ratio'].median():.2f}, "
          f"Stage 2 {pre[pre['day'] >= S2[0]]['drop_ratio'].median():.2f})")
    report("#587", "H-share dividend tax clientele: buy the close before ex-date, sell the ex-date open, keep 90% of D",
           pre[["day", "ret", "size"]], c587)


if __name__ == "__main__":
    main()

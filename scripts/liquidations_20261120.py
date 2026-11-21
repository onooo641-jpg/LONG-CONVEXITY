"""PREREG_LIQUIDATIONS_20261120 analysis. Reads data/public/liq_<chain>*.parquet. Deterministic."""
import glob, os, sys
import numpy as np, pandas as pd

D = os.environ.get("LIQ_DATA_DIR") or os.path.join(os.path.dirname(__file__), "..", "data", "public")
KNOWN = {  # label only; venues are (chain, contract)
    "0x794a61358d6845594f94dc1db02a252b5b4814ad": "Aave v3", "0xa238dd80c259a72e81d7e4664a9801593f98d1c5": "Aave v3 Base",
    "0x6807dc923806fe8fd134338eabca509979a7e0cb": "Aave v3 BNB", "0xb50201558b00496a145fe76f7424749556e326d8": "Aave v3 Gnosis",
    "0x11fcfe756c05ad438e312a7fd934381537d3cffe": "Aave v3 Scroll", "0x90df02551bb792286e8d4f13e0e357b4bf1d6a57": "Aave v3 Metis",
}
NATIVE = {"base": "coingecko:ethereum", "arbitrum": "coingecko:ethereum", "optimism": "coingecko:ethereum", "polygon": "coingecko:matic-network",
          "avalanche": "coingecko:avalanche-2", "bnb": "coingecko:binancecoin", "gnosis": None, "scroll": "coingecko:ethereum", "metis": "coingecko:metis-token"}
LKEY = {"base": "base", "arbitrum": "arbitrum", "optimism": "optimism", "polygon": "polygon", "avalanche": "avax", "bnb": "bsc", "gnosis": "xdai", "scroll": "scroll", "metis": "metis"}
FLASH = 0.0009


def px(prices, coin, ts):
    s = prices.get(coin)
    if s is None:
        return np.full(len(ts), np.nan)
    t, p = s
    i = np.searchsorted(t, ts, side="right") - 1
    out = p[np.clip(i, 0, len(p) - 1)].astype(float)
    out[(i < 0) | (ts - t[np.clip(i, 0, len(t) - 1)] > 3 * 86400)] = np.nan
    return out


def status(chain):
    import json
    f = f"{D}/liq_{chain}_state.json"
    if not os.path.exists(f):
        return "UNMEASURED (no data)"
    st = json.load(open(f))
    if not st.get("complete"):
        a = st.get("anchors", [0, 1])
        return f"PARTIAL (logs {100*(st.get('next_block', a[0])-a[0])/max(a[-1]-a[0],1):.1f}%, receipts_done={st.get('receipts_done')})"
    return f"COMPLETE (receipts missing {st.get('receipts_missing')}, skipped non-Aave-ABI logs {st.get('skipped_logs')})"


def load(chain):
    f = f"{D}/liq_{chain}.parquet"
    if not os.path.exists(f) or not str(status(chain)).startswith("COMPLETE"):
        return None
    df = pd.read_parquet(f)
    dpath = f"{D}/liq_{chain}_decimals.parquet"
    if os.path.exists(dpath):
        dm = pd.read_parquet(dpath)
        dm = dict(zip(dm["token"], dm["dec"]))
        df["coll_dec"] = df["coll_dec"].fillna(df["collateral"].map(dm))
        df["debt_dec"] = df["debt_dec"].fillna(df["debt"].map(dm))
    pr = pd.read_parquet(f"{D}/liq_{chain}_prices.parquet")
    prices = {c: (g.sort_values("ts")["ts"].values, g.sort_values("ts")["price"].values) for c, g in pr.groupby("coin")}
    lk = LKEY[chain]
    ts = df["ts"].values
    pc = np.array([np.nan] * len(df))
    pdb = np.array([np.nan] * len(df))
    for c in df["collateral"].unique():
        m = (df["collateral"] == c).values
        pc[m] = px(prices, f"{lk}:{c}", ts[m])
    for c in df["debt"].unique():
        m = (df["debt"] == c).values
        pdb[m] = px(prices, f"{lk}:{c}", ts[m])
    cv = df["coll_amt"].astype(float) / 10.0 ** df["coll_dec"].astype(float) * pc
    dv = df["debt_amt"].astype(float) / 10.0 ** df["debt_dec"].astype(float) * pdb
    df["coll_usd"], df["debt_usd"] = cv, dv
    df["gross"] = cv - dv
    df["valid"] = cv.notna() & dv.notna() & (cv > 0) & ((df["gross"] / cv).between(-0.02, 0.30))
    df["why_invalid"] = np.where(df["valid"], "", np.where(df["coll_dec"].isna() | df["debt_dec"].isna(), "no_decimals",
                       np.where(np.isnan(pc) | np.isnan(pdb), "no_price", "bonus_out_of_band")))
    nat = NATIVE[chain]
    npx = px(prices, nat, ts) if nat else np.ones(len(df))
    df["n_in_tx"] = df.groupby("tx")["tx"].transform("size")
    gas_native = (df["gas_used"].astype(float) * df["gas_price"].astype(float) + df["l1_fee"].astype(float)) / 1e18
    df["gas_usd"] = gas_native * npx / df["n_in_tx"]
    # sampled receipts: impute gas by mean of observed per-event gas in the same venue/month, bot unknown
    df["gas_imputed"] = df["gas_usd"].isna()
    df["has_receipt"] = df["from"].notna()
    if df["gas_imputed"].any():
        mean = df.groupby(["venue", "month"])["gas_usd"].transform("mean")
        df["gas_usd"] = df["gas_usd"].fillna(mean).fillna(df["gas_usd"].mean())
    df["bot"] = df["from"].fillna("unknown")
    # PREREG addendum 3: on capped (sampled) chains only events with a receipt are used for bot-based metrics
    df["use_for_bots"] = df["has_receipt"] | (not bool(df["receipt_sampled"].iloc[0]))
    df["net"] = df["gross"] - df["gas_usd"]
    df["net_flash"] = df["net"] - FLASH * df["debt_usd"]
    df["chain"] = chain
    return df


def venue_stats(v):
    res = {}
    for half, months in (("H1", range(0, 12)), ("H2", range(12, 24))):
        h = v[v["month"].isin(months)]
        val_all = h[h["valid"]]
        val = val_all[val_all["use_for_bots"]]
        scale = len(val_all) / max(len(val), 1)
        r = {"events": len(h), "valid": len(val_all), "months_with_liq": h["month"].nunique(), "scale": scale,
             "gross": val["gross"].sum() * scale, "gas": val["gas_usd"].sum() * scale}
        if len(val):
            by = val.groupby("bot")["gross"].sum().sort_values(ascending=False, kind="mergesort")
            tot = by.sum()
            r["bots"] = len(by)
            r["top3"] = by.head(3).sum() / tot if tot > 0 else np.nan
            r["top10"] = by.head(10).sum() / tot if tot > 0 else np.nan
            out = val[~val["bot"].isin(by.head(3).index)]
            r["out_net_pm"] = out["net"].sum() * scale / 12
            r["out_net_flash_pm"] = out["net_flash"].sum() * scale / 12
            r["out_bots"] = out["bot"].nunique()
            r["median_net"] = val["net"].median()
        else:
            r.update(bots=0, top3=np.nan, top10=np.nan, out_net_pm=0.0, out_net_flash_pm=0.0, out_bots=0, median_net=np.nan)
        r["pass"] = bool(r["events"] >= 20 and r["top3"] < 0.60 and r["months_with_liq"] == 12 and r["out_net_pm"] >= 500)
        res[half] = r
    return res


def describe(v, label):
    """PREREG addendum 4: sensitivity and descriptive stats for one passing venue (no pass/fail)."""
    print(f"\n-- {label}")
    for half, months in (("H1", range(0, 12)), ("H2", range(12, 24))):
        h = v[v["month"].isin(months) & v["valid"] & v["use_for_bots"]]
        if not len(h):
            print(half, "no data"); continue
        n_all = len(v[v["month"].isin(months) & v["valid"]])
        scale = n_all / len(h)
        tot = h["gross"].sum()
        byl = h.groupby("liquidator")["gross"].sum().sort_values(ascending=False, kind="mergesort")
        byb = h.groupby("bot")["gross"].sum().sort_values(ascending=False, kind="mergesort")
        cnt = h.groupby("bot").size()
        rep = set(cnt[cnt >= 50].index)
        occ = set(cnt[cnt <= 3].index)
        act = cnt[cnt >= 12].index
        top3 = set(byb.head(3).index)
        outn = h[h["bot"].isin(act) & ~h["bot"].isin(top3)].groupby("bot")["net"].sum() * scale / 12
        print(f"{half}: liquidator-field top3 {byl.head(3).sum()/tot:.2f} top10 {byl.head(10).sum()/tot:.2f} unique liquidators {len(byl)} | "
              f"tx-from top3 {byb.head(3).sum()/tot:.2f} top10 {byb.head(10).sum()/tot:.2f} unique {len(byb)}")
        print(f"     repeat winners (>=50): {len(rep)} hold {h[h['bot'].isin(rep)]['gross'].sum()/tot:.2f} of value; occasional (<=3): {len(occ)} hold {h[h['bot'].isin(occ)]['gross'].sum()/tot:.2f}; active (>=12): {len(act)}")
        if len(outn):
            print(f"     net/month per active bot outside top3: median ${outn.median():,.0f}  p75 ${outn.quantile(.75):,.0f}  p90 ${outn.quantile(.9):,.0f}  (n={len(outn)})")
        print(f"     median bonus {100*(h['gross']/h['coll_usd']).median():.2f}% of collateral; debt repaid ${h['debt_usd'].sum()*scale:,.0f}; events {n_all}")


def main():
    print("== chain status (only COMPLETE chains are analysed; PARTIAL/UNMEASURED cannot pass)")
    for c in NATIVE:
        print(f"{c:10s} {status(c)}")
    frames = [d for d in (load(c) for c in NATIVE) if d is not None]
    if not frames:
        print("NO DATA"); return
    allv = pd.concat(frames, ignore_index=True)
    pd.set_option("display.width", 250, "display.max_columns", 50)
    print("== coverage per chain: events, price-valid %, receipts-imputed %")
    for c, g in allv.groupby("chain"):
        w = g["why_invalid"].value_counts()
        print(f"{c:10s} events {len(g):7d} valid {g['valid'].mean()*100:5.1f}% no_receipt {(~g['has_receipt']).mean()*100:5.1f}% sampled={bool(g['receipt_sampled'].iloc[0])} "
              f"invalid: no_decimals {w.get('no_decimals',0)} no_price {w.get('no_price',0)} bonus_out_of_band {w.get('bonus_out_of_band',0)} venues {g['venue'].nunique()}")
    print("\n== monthly per venue (valid events only): n, gross$, gas$, bots, top3, top10, median net$")
    summary = []
    for (c, ven), v in allv.groupby(["chain", "venue"]):
        if len(v) < 20:
            continue
        label = KNOWN.get(ven, "unknown fork")
        print(f"\n--- {c} {ven} [{label}] total events {len(v)}")
        rows = []
        for m in range(24):
            g = v[(v["month"] == m) & v["valid"] & v["use_for_bots"]]
            if len(g) == 0:
                rows.append((m, 0, 0, 0, 0, np.nan, np.nan, np.nan)); continue
            by = g.groupby("bot")["gross"].sum().sort_values(ascending=False, kind="mergesort"); tot = by.sum()
            rows.append((m, len(g), g["gross"].sum(), g["gas_usd"].sum(), len(by), by.head(3).sum() / tot if tot > 0 else np.nan,
                         by.head(10).sum() / tot if tot > 0 else np.nan, g["net"].median()))
        mt = pd.DataFrame(rows, columns=["month", "n", "gross", "gas", "bots", "top3", "top10", "med_net"])
        mt["month"] = [str(p) for p in pd.period_range("2024-11", periods=24, freq="M")]
        print(mt.round(3).to_string(index=False))
        st = venue_stats(v)
        for h in ("H1", "H2"):
            print(h, {k: (round(x, 3) if isinstance(x, float) else x) for k, x in st[h].items()})
        summary.append((c, ven, label, st))
    print("\n== PASS TABLE")
    passing = []
    for c, ven, label, st in summary:
        ok = st["H1"]["pass"] and st["H2"]["pass"]
        print(f"{c:10s} {ven[:12]} {label:14s} H1 top3 {st['H1']['top3']:.2f} out$/mo {st['H1']['out_net_pm']:9.0f} mths {st['H1']['months_with_liq']:2d} | "
              f"H2 top3 {st['H2']['top3']:.2f} out$/mo {st['H2']['out_net_pm']:9.0f} mths {st['H2']['months_with_liq']:2d} | PASS={ok}")
        if ok:
            passing.append((c, ven, st))
    c1 = sum(s["H1"]["out_net_pm"] for _, _, s in passing)
    c2 = sum(s["H2"]["out_net_pm"] for _, _, s in passing)
    print(f"\npassing venues: {len(passing)}  combined outside-top3 net $/mo  H1 {c1:.0f}  H2 {c2:.0f}")
    print("OVERALL PASS =", len(passing) >= 3 and c1 >= 2000 and c2 >= 2000)
    print("\n== sensitivity (no pass/fail): outside-top3 $/mo after 0.09% flash-loan fee on debt, passing venues")
    for c, ven, s in passing:
        print(c, ven[:12], round(s["H1"]["out_net_flash_pm"]), round(s["H2"]["out_net_flash_pm"]),
              "outside bots", s["H1"]["out_bots"], s["H2"]["out_bots"],
              "per-new-bot est $/mo", round(s["H2"]["out_net_pm"] / (s["H2"]["out_bots"] + 1)))
    print("\n== SENSITIVITY (addendum 4): same pass table with winner = event `liquidator` field instead of tx `from` (not the registered test)")
    alt = []
    for (c, ven), v in allv.groupby(["chain", "venue"]):
        if len(v) < 20:
            continue
        v2 = v.copy()
        v2["bot"] = v2["liquidator"]
        st2 = venue_stats(v2)
        ok = st2["H1"]["pass"] and st2["H2"]["pass"]
        if ok:
            alt.append((c, ven, st2))
            print(f"{c:10s} {ven[:12]} {KNOWN.get(ven, 'unknown fork'):14s} H1 top3 {st2['H1']['top3']:.2f} out$/mo {st2['H1']['out_net_pm']:9.0f} | H2 top3 {st2['H2']['top3']:.2f} out$/mo {st2['H2']['out_net_pm']:9.0f} | PASS(alt)")
    print(f"venues passing under alt identity: {len(alt)}  combined outside-top3 net $/mo H1 {sum(s['H1']['out_net_pm'] for _,_,s in alt):.0f} H2 {sum(s['H2']['out_net_pm'] for _,_,s in alt):.0f}")
    print("\n== ADDENDUM 4: sensitivity and descriptive stats for passing venues (no pass/fail)")
    for c, ven, st in passing:
        describe(allv[(allv["chain"] == c) & (allv["venue"] == ven)], f"{c} {ven} [{KNOWN.get(ven, 'unknown fork')}]")
    print("\n== top venues by gross bonus, last 12 months (regardless of pass)")
    t = allv[allv["valid"] & (allv["month"] >= 12)].groupby(["chain", "venue"]).agg(n=("tx", "size"), gross=("gross", "sum"), gas=("gas_usd", "sum"), bots=("bot", "nunique")).sort_values("gross", ascending=False)
    print(t.head(15).round(0).to_string())


if __name__ == "__main__":
    main()

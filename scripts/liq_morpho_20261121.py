"""PREREG_LIQ_MORPHO_20261121 analysis. uv run python -I scripts/liq_morpho_20261121.py [pilot|full]"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import liquidations_20261120 as L  # noqa: E402

for n in ("morphobase", "morphobase_pilot"):
    L.NATIVE[n] = "coingecko:ethereum"
    L.LKEY[n] = "base"
BUCKETS = [(50, 200), (200, 1000), (1000, 5000), (5000, 1e12)]
LABELS = [str(p) for p in pd.period_range("2024-11", periods=24, freq="M")]


def pilot():
    df = L.load("morphobase_pilot")
    if df is None:
        print("no pilot data")
        return
    v = df[df["valid"]]
    gross = v["gross"].sum()
    print(f"PILOT (2026-08-01..2026-10-31): events {len(df)}, valid {len(v)}, gross bonus ${gross:,.0f}, eligible(>$50) {int((v['gross'] > 50).sum())}, "
          f"unique winners {v['bot'].nunique()}, top-3 share {v.groupby('bot')['gross'].sum().sort_values(ascending=False, kind='mergesort').head(3).sum() / max(gross, 1):.2f}")
    print("PILOT RULE: KILL if gross < $3,750 ->", "KILL" if gross < 3750 else "proceed to stage 2")


def merge_shards():
    """concatenate the three stage-2 shards into the single venue file (PREREG_LIQ_MORPHO addendum 2); only when all are complete."""
    import json
    D = Path(L.D)
    parts = [f"morphobase_s{i}" for i in range(3)]
    for p in parts:
        sf = D / f"liq_{p}_state.json"
        if not sf.exists() or not json.loads(sf.read_text()).get("complete"):
            print(f"shard {p} not complete: cannot merge")
            return False
    dfs = [pd.read_parquet(D / f"liq_{p}.parquet") for p in parts]
    df = pd.concat(dfs, ignore_index=True).sort_values(["block", "tx", "user"], kind="mergesort").reset_index(drop=True)
    df["receipt_sampled"] = any(bool(d["receipt_sampled"].iloc[0]) for d in dfs if len(d))
    pr = pd.concat([pd.read_parquet(D / f"liq_{p}_prices.parquet") for p in parts], ignore_index=True).drop_duplicates()
    df.to_parquet(D / "liq_morphobase.parquet")
    pr.to_parquet(D / "liq_morphobase_prices.parquet")
    (D / "liq_morphobase_state.json").write_text(json.dumps({"complete": True, "receipts_missing": 0, "merged_from": parts}))
    print(f"merged {len(df)} events from {len(parts)} shards")
    return True


def full():
    if not (Path(L.D) / "liq_morphobase_state.json").exists():
        merge_shards()
    df = L.load("morphobase")
    if df is None:
        print("no data")
        return
    print(f"events {len(df)}, valid {df['valid'].mean():.1%}, no_receipt {(~df['has_receipt']).mean():.1%}")
    print("invalid reasons:", df["why_invalid"].value_counts().to_dict())
    for ven, v in df.groupby("venue"):
        st = L.venue_stats(v)
        print("\n== registered pass test, Morpho Blue Base (venue", ven[:12], ")")
        for h in ("H1", "H2"):
            print(h, {k: (round(x, 3) if isinstance(x, float) else x) for k, x in st[h].items()})
        ok = st["H1"]["pass"] and st["H2"]["pass"]
        print("VENUE PASS =", ok)
        val = v[v["valid"] & v["use_for_bots"]]
        print("\n== month table: gross bonus, liquidations, winners, top-3 share")
        for m in range(24):
            g = val[val["month"] == m]
            if len(g):
                by = g.groupby("bot")["gross"].sum().sort_values(ascending=False, kind="mergesort")
                t3 = by.head(3).sum() / by.sum() if by.sum() > 0 else float("nan")
                print(f"{LABELS[m]}  gross {g['gross'].sum():11,.0f}  n {len(g):5d}  winners {len(by):4d}  top3 {t3:.2f}")
            else:
                print(f"{LABELS[m]}  gross {0:11,.0f}  n {0:5d}")
        e = val[val["gross"] > 50]
        wins = val.groupby("liquidator").size()
        rep = set(wins[wins >= 50].index)
        print("\n== by bonus size (last 12 months, eligible): events, median gas/bonus, winners, top3, top10, repeat(>=50 wins) share")
        h2 = e[e["month"] >= 12]
        for lo, hi in BUCKETS:
            b = h2[(h2["gross"] > lo) & (h2["gross"] <= hi)]
            if not len(b):
                continue
            by = b.groupby("liquidator")["gross"].sum().sort_values(ascending=False, kind="mergesort")
            gs = (b[b["has_receipt"]]["gas_usd"] / b[b["has_receipt"]]["gross"]).median()
            print(f"{lo:>5.0f}-{('inf' if hi > 1e11 else int(hi)):>5} n {len(b):5d} gas/bonus {gs:.4f} winners {len(by):4d} top3 {by.head(3).sum() / by.sum():.2f} "
                  f"top10 {by.head(10).sum() / by.sum():.2f} repeat {b[b['liquidator'].isin(rep)]['gross'].sum() / b['gross'].sum():.2f}")
        print(f"median bonus as % of collateral value: {100 * (val['gross'] / val['coll_usd']).median():.2f}%")
        # active non-top-3 bots per month (same definitions as PREREG_LIQ_MONTHLY)
        meds, medw = [], []
        for half, months in ((0, range(0, 12)), (1, range(12, 24))):
            h = val[val["month"].isin(months)]
            scale = 1.0
            by = h.groupby("bot")["gross"].sum().sort_values(ascending=False, kind="mergesort")
            top3 = set(by.head(3).index)
            cnt = h.groupby("bot").size()
            act = [b for b in cnt[cnt >= 12].index if b not in top3]
            u = h[h["bot"].isin(act)]
            piv = u.groupby(["bot", "month"])["net"].sum().unstack(fill_value=0.0) * scale
            for m in months:
                col = (piv[m] if m in piv.columns else pd.Series(0.0, index=piv.index)).reindex(act, fill_value=0.0)
                meds.append(float(np.median(col.values)) if len(col) else 0.0)
                wv = col[col != 0]
                medw.append(float(np.median(wv.values)) if len(wv) else 0.0)
        meds, medw = np.array(meds), np.array(medw)
        print(f"\nactive non-top-3 bots: H1 {len([1 for _ in []]) if False else ''}months with median bot <$200 / $200-1,000 / >$1,000 (zeros included): "
              f"{int((meds < 200).sum())} / {int(((meds >= 200) & (meds <= 1000)).sum())} / {int((meds > 1000).sum())} of 24; "
              f"(winners only): {int((medw < 200).sum())} / {int(((medw >= 200) & (medw <= 1000)).sum())} / {int((medw > 1000).sum())}")
        tot = val.groupby("month")["gross"].sum().reindex(range(24), fill_value=0.0).values
        o = np.argsort(-tot, kind="mergesort")
        print(f"24-month gross ${tot.sum():,.0f}; top 5 months {tot[o[:5]].sum() / max(tot.sum(), 1):.1%}; months under $200K: {int((tot < 200000).sum())}/24")


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "full"
    pilot() if mode == "pilot" else full()


if __name__ == "__main__":
    main()

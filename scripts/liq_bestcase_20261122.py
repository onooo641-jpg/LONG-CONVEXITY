"""PREREG_LIQ_BESTCASE_20261122. uv run python -I scripts/liq_bestcase_20261122.py"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import liquidations_20261120 as L  # noqa: E402
import liq_replay_sample_20261121 as S  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
L.NATIVE["morphobase"] = "coingecko:ethereum"
L.LKEY["morphobase"] = "base"
VENUES = {"aave5": [(c, p) for c, p in S.POOL.items()], "morpho": [("morphobase", "0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb")]}


def bot_months(pairs):
    """returns gross per month (24), list of (month, net) for every active non-top-3 (pool, bot) incl. zeros, n_active per half."""
    gross = np.zeros(24)
    cells = {m: [] for m in range(24)}
    nact = {0: 0, 1: 0}
    for c, pool in pairs:
        df = L.load(c)
        v = df[(df["venue"] == pool) & df["valid"]]
        for half, months in ((0, range(0, 12)), (1, range(12, 24))):
            h = v[v["month"].isin(months)]
            use = h[h["use_for_bots"]]
            scale = len(h) / max(len(use), 1)
            for m in months:
                gross[m] += h[h["month"] == m]["gross"].sum()
            by = use.groupby("bot")["gross"].sum().sort_values(ascending=False, kind="mergesort")
            top3 = set(by.head(3).index)
            cnt = use.groupby("bot").size()
            act = [b for b in cnt[cnt >= 12].index if b not in top3]
            nact[half] += len(act)
            piv = use[use["bot"].isin(act)].groupby(["bot", "month"])["net"].sum().unstack(fill_value=0.0) * scale
            for m in months:
                col = (piv[m] if m in piv.columns else pd.Series(0.0, index=piv.index)).reindex(act, fill_value=0.0)
                cells[m] += list(col.values)
    return gross, cells, nact


def part1():
    print("== 1. mean vs median income per active non-top-3 bot-month (zeros included; gas only), USD")
    res = {}
    for name, pairs in VENUES.items():
        gross, cells, nact = bot_months(pairs)
        res[name] = (gross, cells, nact)
        allv = np.concatenate([np.array(cells[m]) for m in range(24)])
        last8 = np.concatenate([np.array(cells[m]) for m in range(16, 24)])
        order = np.argsort(-gross, kind="mergesort")
        big = set(order[:5].tolist())
        quiet = [m for m in range(24) if gross[m] < 200_000]
        bigv = np.concatenate([np.array(cells[m]) for m in big])
        quietv = np.concatenate([np.array(cells[m]) for m in quiet]) if quiet else np.array([0.0])
        print(f"{name:7s} active bots H1/H2 {nact[0]}/{nact[1]}")
        for lab, x in (("24 months", allv), ("last 8 months (Mar-Oct 2026)", last8), ("quiet months (gross < $200K)", quietv), ("5 biggest months", bigv)):
            print(f"   {lab:30s} bot-months {len(x):6d}  mean {x.mean():9.1f}  median {np.median(x):8.1f}  p75 {np.quantile(x, .75):8.1f}  p90 {np.quantile(x, .9):9.1f}")
    # per-month mean across the two venues, parity case (one bot present on one Aave pool entry and one Morpho entry)
    mean24 = sum(np.concatenate([np.array(res[n][1][m]) for m in range(24)]).mean() for n in res)
    mean8 = sum(np.concatenate([np.array(res[n][1][m]) for m in range(16, 24)]).mean() for n in res)
    print(f"parity case: a bot with one Aave-pool-sized entry plus one Morpho-sized entry: mean {mean24:.0f} a month over 24 months, {mean8:.0f} over the last 8 months")
    return res, mean24, mean8


def part2():
    print("\n== 2. who wins same-block (gap <= 1) vs later (gap > 2 or no update) events: replay samples joined to event files")
    rows = []
    for c in ("arbitrum", "base", "avalanche", "polygon"):
        g = pd.read_parquet(ROOT / "data" / "public" / f"liq_replay_gaps_s2_{c}.parquet")
        e = L.load(c)[["tx", "user", "block", "liquidator", "gross", "venue"]]
        rows.append(g.merge(e, on=["tx", "user", "block"], how="inner", suffixes=("", "_e")).assign(src=f"aave-{c}"))
    g = pd.read_parquet(ROOT / "data" / "public" / "liq_replay_gaps_s2_morphobase.parquet")
    e = L.load("morphobase")[["tx", "user", "block", "liquidator", "gross"]]
    rows.append(g.merge(e, on=["tx", "user", "block"], how="inner", suffixes=("", "_e")).assign(src="morpho-base"))
    wins = {}
    for src, pairs in (("aave", [(c, S.POOL[c]) for c in ("arbitrum", "base", "avalanche", "polygon")]), ("morpho", VENUES["morpho"])):
        for c, pool in pairs:
            df = L.load(c)
            v = df[(df["venue"] == pool) & df["valid"] & (df["month"] >= 12)]
            vc = v.groupby("liquidator").size()
            wins[c] = set(vc[vc >= 50].index)
    print("group                 events  distinct_winners  top3   top10  repeat(>=50 wins)  median_bonus")
    for lab, fam in (("aave", "aave-"), ("morpho", "morpho-")):
        d = pd.concat([r for r in rows if r["src"].iloc[0].startswith(fam)], ignore_index=True)
        d = d[d["g_ev"].notna() & (d["has_c"] | d["has_d"])]
        for cls, mask in (("same-block (gap<=1)", (d["g_ev"] >= 0) & (d["g_ev"] <= 1)), ("later (gap>2/none)", (d["g_ev"] == -1) | (d["g_ev"] > 2))):
            x = d[mask]
            if not len(x):
                continue
            by = x.groupby("liquidator")["gross"].sum().sort_values(ascending=False, kind="mergesort")
            chain_key = x["chain"].map(lambda c: "morphobase" if c == "morphobase" else c)
            rep = x.apply(lambda r: r["liquidator"] in wins.get(r["chain"], set()), axis=1)
            print(f"{lab:7s} {cls:20s} {len(x):6d}  {len(by):16d}  {by.head(3).sum() / by.sum():.2f}   {by.head(10).sum() / by.sum():.2f}   {(x['gross'] * rep).sum() / x['gross'].sum():.2f}             {x['gross'].median():8.0f}")
    return rows


def part3(res):
    print("\n== 3. fair share of the same-block pool (pool = (1 - R_value) x gross; divided by active non-top-3 bots), USD per bot-month")
    rv = {"aave5": 0.101, "morpho": 0.008}   # replay R_value, ideal arm (docs/jx_runs/liq_replay_20261121.txt, liq_morpho_replay_20261121.txt)
    for name in ("aave5", "morpho"):
        gross, cells, nact = res[name]
        for lab, months in (("24 months", range(24)), ("last 8 months", range(16, 24))):
            pool = sum(gross[m] for m in months) * (1 - rv[name]) / len(list(months))
            n = nact[1] if lab == "last 8 months" else (nact[0] + nact[1]) / 2
            print(f"{name:7s} {lab:14s} same-block pool {pool:12,.0f} a month; active bots {n:7.0f}; fair share {pool / n:9,.0f} a month per active bot (before costs)")


def main():
    res, m24, m8 = part1()
    part2()
    part3(res)
    print("\n== reading rule (PREREG): claim 'USD 500-1,500 a month best case' is")
    print("SUPPORTED as a parity case" if (m24 >= 500 and m8 >= 300) else ("NOT SUPPORTED" if m8 < 300 else "MIXED (24-month mean >= 500 but see last-8-month mean)"), f"(24-month mean {m24:.0f}, last-8-month mean {m8:.0f}); a new bot reaching parity remains unproven")


if __name__ == "__main__":
    main()

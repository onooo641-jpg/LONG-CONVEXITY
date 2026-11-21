"""PREREG_LIQ_MONTHLY_20261121: month-by-month income table for the five main pools. uv run python -I scripts/liq_monthly_20261121.py"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import liquidations_20261120 as L  # noqa: E402
import liq_replay_sample_20261121 as S  # noqa: E402

LABELS = [str(p) for p in pd.period_range("2024-11", periods=24, freq="M")]


def main():
    gross = np.zeros(24)
    net_out = np.zeros(24)                     # outside-top-3 active-bot net per month (pooled, scaled)
    entries = {m: [] for m in range(24)}       # per month: net of every active non-top-3 bot (incl. zeros)
    won = {m: [] for m in range(24)}
    for c, pool in S.POOL.items():
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
            u = use[use["bot"].isin(act)]
            piv = u.groupby(["bot", "month"])["net"].sum().unstack(fill_value=0.0) * scale
            for m in months:
                col = piv[m] if m in piv.columns else pd.Series(0.0, index=piv.index)
                col = col.reindex(act, fill_value=0.0)
                entries[m] += list(col.values)
                won[m] += [x for x in (u[u["month"] == m].groupby("bot")["net"].sum() * scale).values]
                net_out[m] += col.sum()
    print("== month table, five main Aave v3 pools (gross bonus = valid events; net = bonus - gas, outside-top-3 active bots; USD)")
    print("month     gross_bonus   active_bots  won_in_month   median(all)  p75(all)   median(won)  p75(won)   outside_top3_net_total")
    med, rows = [], []
    for m in range(24):
        a = np.array(entries[m]) if entries[m] else np.array([0.0])
        w = np.array(won[m]) if won[m] else np.array([np.nan])
        med.append(float(np.median(a)))
        rows.append((LABELS[m], gross[m], len(entries[m]), len(won[m]), np.median(a), np.quantile(a, 0.75), np.nanmedian(w), np.nanquantile(w, 0.75), net_out[m]))
        print(f"{LABELS[m]}  {gross[m]:12,.0f}  {len(entries[m]):10d}  {len(won[m]):11d}  {np.median(a):11,.0f}  {np.quantile(a, .75):8,.0f}  {np.nanmedian(w):11,.0f}  {np.nanquantile(w, .75):8,.0f}  {net_out[m]:16,.0f}")
    med = np.array(med)
    print("\n== summary (primary median: all active non-top-3 bots, zeros included)")
    print(f"months with median bot < $200: {int((med < 200).sum())}/24 ({(med < 200).mean():.0%});  $200-$1,000: {int(((med >= 200) & (med <= 1000)).sum())}/24 "
          f"({((med >= 200) & (med <= 1000)).mean():.0%});  > $1,000: {int((med > 1000).sum())}/24 ({(med > 1000).mean():.0%})")
    mw = np.array([r[6] for r in rows])
    print("secondary (median over bots that won at least once that month): "
          f"< $200: {int((mw < 200).sum())}/24 ({(mw < 200).mean():.0%});  $200-$1,000: {int(((mw >= 200) & (mw <= 1000)).sum())}/24 ({((mw >= 200) & (mw <= 1000)).mean():.0%});  "
          f"> $1,000: {int((mw > 1000).sum())}/24 ({(mw > 1000).mean():.0%})")
    order = np.argsort(-gross, kind="mergesort")
    tot = gross.sum()
    print(f"24-month gross bonus {tot:,.0f}; top 3 months {gross[order[:3]].sum() / tot:.1%}; top 5 months {gross[order[:5]].sum() / tot:.1%}; "
          f"top 5 months: " + ", ".join(f"{LABELS[i]} {gross[i]/1e6:.1f}M" for i in order[:5]))
    print(f"months with gross bonus < $200K: {int((gross < 200_000).sum())}/24")
    ot = net_out.sum()
    o2 = np.argsort(-net_out, kind="mergesort")
    print(f"24-month outside-top-3 net (pooled active bots) {ot:,.0f}; top 3 months {net_out[o2[:3]].sum() / ot:.1%}; top 5 months {net_out[o2[:5]].sum() / ot:.1%}")
    print("\n== comparison: Topstep payout-month share 20% (one market) / 32% (two markets), repo figure (docs/NOTES_JX.md, source docs/PREREG_20261109.md, not re-derived)")
    print(f"liquidation months in which a median active bot (zeros included) made > $1,000: {(med > 1000).mean():.0%}; >= $200: {(med >= 200).mean():.0%}")
    print(f"liquidation months in which the median bot that won at least once made > $1,000: {(mw > 1000).mean():.0%}; >= $200: {(mw >= 200).mean():.0%}")
    print("\n== quoted-figure check: Jx quoted Feb 2025 11.2M, Oct 2025 6.6M, Feb 2026 5.1M, Nov 2025 4.0M, 5 biggest ~71%, 11 of 24 under $200K")
    print("measured here:", {LABELS[i]: round(gross[i] / 1e6, 2) for i in order[:5]}, f"top5 {gross[order[:5]].sum() / tot:.1%}", f"under200K {int((gross < 200000).sum())}")


if __name__ == "__main__":
    main()

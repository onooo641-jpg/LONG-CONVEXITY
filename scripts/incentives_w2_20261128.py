"""Radar week 2: Ember USDC vault on Sui (docs/PREREG_INCENTIVES_W2_20261128.md, CANDIDATES #588); W1 rule unchanged.

    uv run python scripts/incentives_w2_20261128.py | tee docs/jx_runs/incentives_w2_20261128.txt
"""
from __future__ import annotations

import sys

import numpy as np
import pandas as pd

BAR, KILL, HAIRCUT, TBILL = 12.0, 8.0, 0.90, 4.0
SETUPS = {
    "#588 Ember USDC concentrated-liquidity vault (Sui)": (["0a3c5663-73bd-4d8a-bdcc-5e529a8b741d"], 0.10),
}
TX_PER_YEAR = 26


def net_yield(df, size, fee):
    cost = TX_PER_YEAR * fee / size * 100
    tvl = df["tvlUsd"].clip(lower=1.0)
    return df["apyBase"].fillna(0) + df["apyReward"].fillna(0) * HAIRCUT * tvl / (tvl + size) - cost


def main() -> int:
    ch = pd.read_parquet("data/radar/charts.parquet")
    ch["day"] = pd.to_datetime(ch["ts"], utc=True).dt.floor("D")
    end = ch["day"].max()
    print(f"chart data through {end.date()}; bar {BAR}%/yr net (T-bill {TBILL}% assumed + 8), pilot kill < {KILL}%\n")
    for name, (pools, fee) in SETUPS.items():
        parts, events, rshare = [], [], []
        for p in pools:
            d = ch[ch["pool_id"] == p].drop_duplicates("day").set_index("day").sort_index()
            d = d[d.index >= end - pd.Timedelta(days=730)]
            if d.empty:
                print(f"  {p}: NO DATA")
                continue
            parts.append(net_yield(d, 10_000, fee).rename(p))
            tv = d["tvlUsd"].resample("D").last().ffill()
            drop = (tv / tv.rolling(8, min_periods=8).max()).min()
            events.append(float(drop))
            rshare.append(float((d["apyReward"].fillna(0) / d["apy"].replace(0, np.nan)).mean()))
            print(f"  pool {p}: {len(d)} days from {d.index.min().date()}, mean apyBase {d['apyBase'].mean():.2f}%, "
                  f"apyReward {d['apyReward'].mean():.2f}%, worst 7-day TVL ratio {drop:.2f}")
        if not parts:
            print(f"{name}: no data -> not testable\n")
            continue
        s = pd.concat(parts, axis=1).mean(axis=1, skipna=True).dropna()
        days = (s.index.max() - s.index.min()).days
        pilot = s[s.index > end - pd.Timedelta(days=60)].mean()
        print(f"{name}: Stage 1 pilot (last 60 days) mean net {pilot:.2f}%/yr -> {'KILL' if pilot < KILL else 'continue'}")
        if pilot < KILL:
            print(f"  VERDICT: FAIL (killed at Stage 1)\n")
            continue
        half = s.index.min() + (s.index.max() - s.index.min()) / 2
        h1, h2 = s[s.index <= half].mean(), s[s.index > half].mean()
        loss = any(e < 0.5 for e in events)
        ok = days >= 180 and h1 >= BAR and h2 >= BAR and not loss
        s50 = pd.concat([net_yield(ch[ch.pool_id == p].drop_duplicates("day").set_index("day").sort_index().loc[s.index.min():],
                                   50_000, fee) for p in pools], axis=1).mean(axis=1).mean()
        print(f"  Stage 2: history {days} days; half 1 {h1:.2f}%/yr, half 2 {h2:.2f}%/yr; loss-event proxy {'HIT' if loss else 'none'}; "
              f"reward share of yield {np.nanmean(rshare):.0%}")
        print(f"  on $10K: ${s.mean() * 100:,.0f}/yr (Topstep 50K slot: $4,097/yr at ~$3.5K risk); at $50K mean net {s50:.2f}%/yr")
        reasons = [r for r, bad in (("history < 180 days", days < 180), (f"half 1 < {BAR}%", h1 < BAR),
                                    (f"half 2 < {BAR}%", h2 < BAR), ("loss-event proxy", loss)) if bad]
        print(f"  VERDICT: {'PASS' if ok else 'FAIL (' + '; '.join(reasons) + ')'}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())

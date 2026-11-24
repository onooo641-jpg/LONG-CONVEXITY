"""#371 UniswapX fillers on Arbitrum and Base (docs/PREREG_UNISWAPX_20261124.md).

    uv run python -m scripts.uniswapx_20261124 | tee docs/jx_runs/uniswapx_20261124.txt
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

PUB = Path(__file__).resolve().parent.parent / "data" / "public"
S1 = pd.Timestamp("2026-08-01", tz="UTC")
NEW = pd.Timestamp("2026-05-01", tz="UTC")


def main():
    meta = json.loads((PUB / "uniswapx371_meta.json").read_text())
    print(f"===== #371 UniswapX fillers (Fill topic {meta.get('topic0', '')[:12]}…)")
    s1_closed, door = [], []
    for chain in ("arbitrum", "base"):
        m = meta.get(chain, {})
        print(f"  {chain}: code {m.get('has_code')}; blocks {m.get('b0')}..{m.get('b1')}; missed {m.get('missed')}; fills {m.get('fills')}; "
              f"error {m.get('error')}")
        f = PUB / f"uniswapx371_{chain}.parquet"
        if not f.exists() or not m.get("ts_sample"):
            print("    no data: no verdict for this chain")
            continue
        d = pd.read_parquet(f)
        if d.empty:
            print("    no fills")
            continue
        ts = np.array(m["ts_sample"], dtype=float)
        d["day"] = pd.to_datetime(np.interp(d["block"].to_numpy(float), ts[:, 0], ts[:, 1]), unit="s", utc=True)
        d["month"] = d["day"].dt.strftime("%Y-%m")
        cov_ok = (m.get("missed") or 0) <= 0.01 * max(1, (m.get("b1") or 0) - (m.get("b0") or 0))
        s1 = d[d["day"] >= S1]
        c = s1["filler"].value_counts()
        top3 = c.head(3).sum() / c.sum() if len(c) else np.nan
        print(f"    Stage 1 (2026-08..10): fills {len(s1):,}, distinct fillers {len(c)}, top-3 share {top3:.1%}; top: "
              + ", ".join(f"{a[:10]} {n:,}" for a, n in c.head(5).items()) + ("" if cov_ok else "  [COVERAGE < 99%]"))
        s1_closed.append(bool(top3 >= 0.90) if len(c) else True)
        first = d.groupby("filler")["day"].min()
        newbies = first[first >= NEW].index
        mon = d.groupby(["month", "filler"]).size().unstack(fill_value=0)
        share = mon.div(mon.sum(axis=1), axis=0)
        best = share[[x for x in newbies if x in share.columns]].max() if len(newbies) else pd.Series(dtype=float)
        print(f"    12 months: fills {len(d):,}, distinct fillers {d['filler'].nunique()}, newcomers since 2026-05 {len(newbies)}; "
              f"best newcomer monthly share {best.max() if len(best) else 0:.1%}")
        for a, v in best.sort_values(ascending=False).head(5).items():
            print(f"      newcomer {a} first {first[a].date()} best monthly share {v:.1%} total fills {int(mon[a].sum()):,}")
        print("    monthly fills and top-3 share: " + "; ".join(
            f"{mo} {int(row.sum()):,} ({row.sort_values(ascending=False).head(3).sum() / max(1, row.sum()):.0%})" for mo, row in mon.iterrows()))
        door.append(bool(len(best) and best.max() >= 0.05))
    if not s1_closed:
        print("  no data on either chain: no verdict")
        return
    kill = all(s1_closed) and len(s1_closed) == 2
    print(f"  STAGE 1 VERDICT: {'KILL (top 3 make >= 90% of fills on both chains)' if kill else 'survives (kill-only)'}")
    print(f"  STAGE 2 VERDICT: {'door open (a newcomer reached >= 5% monthly share)' if any(door) else 'FAIL (no newcomer reached 5%)'}"
          + (" (Stage 1 already killed; context only)" if kill else ""))


if __name__ == "__main__":
    main()

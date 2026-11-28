"""NF26 #649 check: the same trades entered one hour after the signal (diagnostic, after the PASS).

    uv run python -m scripts.batch_nf26_diag_20261128 | tee docs/jx_runs/batch_nf26_diag_20261128.txt
"""
from __future__ import annotations

import pandas as pd

import scripts.batch_nf17_20261128 as M
import scripts.batch_nf26_20261128 as N


def main():
    g, hg, hl_name = N.frames()
    lo = hg["ts"].min()
    F = M.per_hour(pd.read_parquet(M.PUB / "batchnf17_funding.parquet"))
    for d in (0, 1, 2):
        e = N.trades(g, F, hl_name, lo, thr=3.0, side="hl", delay=d)
        s2 = e[e["ts"] >= M.S2[0]]
        t = s2["ret"].mean() / (s2["ret"].std(ddof=1) / len(s2) ** 0.5) if len(s2) > 1 else float("nan")
        print(f"#649 entry {d}h after the signal: Stage 2 n {len(s2)}, mean {s2['ret'].mean():+.2%} (t {t:.2f}); funding {s2['fund'].mean():+.2%}")
    top = e.groupby("market")["ret"].agg(["size", "sum"]).sort_values("sum", ascending=False)
    print(f"   share of Stage 1+2 return sum from the top market: {top['sum'].iloc[0] / e['ret'].sum():.0%} ({top.index[0]})")


if __name__ == "__main__":
    main()

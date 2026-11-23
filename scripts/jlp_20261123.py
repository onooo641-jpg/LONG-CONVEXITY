"""#363 hedged Jupiter JLP (docs/PREREG_JLP_20261123.md).

    uv run python -m scripts.jlp_20261123 | tee docs/jx_runs/jlp_20261123.txt
Reads data/public/jlp363_prices.parquet + jlp363_meta.json (Actions job jlp363) and data/public/hl_funding.parquet.
"""
from __future__ import annotations

import itertools
import json
from pathlib import Path

import numpy as np
import pandas as pd

PUB = Path(__file__).resolve().parent.parent / "data" / "public"
JLP_KEYS = ["coingecko:jupiter-perpetuals-liquidity-provider-token", "solana:27G8MtK7VtTcCHkpASjSDdkWWYfoqT6ggEuKidVJidD4"]
COINS = {"SOL": "coingecko:solana", "ETH": "coingecko:ethereum", "BTC": "coingecko:bitcoin"}
TAKER, JLP_RT, LEV, LOOK = 0.00045, 0.0030, 3.0, 60
END = pd.Timestamp("2026-10-31", tz="UTC")


def nnls_demeaned(y, X):
    """Exact NNLS for <= 3 regressors (demeaned = with intercept): best feasible subset by SSE."""
    y = y - y.mean()
    X = X - X.mean(axis=0)
    best, best_sse = np.zeros(X.shape[1]), float(y @ y)
    for k in range(1, X.shape[1] + 1):
        for sub in itertools.combinations(range(X.shape[1]), k):
            b, *_ = np.linalg.lstsq(X[:, sub], y, rcond=None)
            if (b < 0).any():
                continue
            sse = float(((y - X[:, sub] @ b) ** 2).sum())
            if sse < best_sse - 1e-15:
                full = np.zeros(X.shape[1])
                full[list(sub)] = b
                best, best_sse = full, sse
    return best


def stats(r, label):
    r = r.dropna()
    if r.empty:
        print(f"    {label}: no days")
        return np.nan, np.nan
    eq = (1 + r).cumprod()
    yrs = len(r) / 365.0
    cagr = eq.iloc[-1] ** (1 / yrs) - 1
    dd = float((eq / eq.cummax() - 1).min())
    print(f"    {label}: {r.index[0].date()}..{r.index[-1].date()} ({len(r)} d)  CAGR {cagr:7.1%}  worst DD {dd:7.1%}  "
          f"daily vol {r.std():.2%}")
    return cagr, dd


def main():
    meta = json.loads((PUB / "jlp363_meta.json").read_text())
    print("===== #363 hedged Jupiter JLP")
    for url, pg in meta["pages"].items():
        if pg.get("error"):
            print(f"  page {url}: {pg['error']}")
            continue
        flags = {k[:-12]: v for k, v in pg.items() if k.endswith("|in_raw_html")}
        print(f"  page {url}: chars {pg.get('chars')}; {flags}")
        for snip in (pg.get("Malaysia") or [])[:2]:
            print(f"    Malaysia snippet: ...{snip[150:250]}...")
    px = pd.read_parquet(PUB / "jlp363_prices.parquet")
    px["day"] = pd.to_datetime(px["t"], unit="s", utc=True).dt.normalize()
    px = px.drop_duplicates(["key", "day"], keep="last").pivot(index="day", columns="key", values="price").sort_index()
    n = {k: int(px[k].notna().sum()) if k in px else 0 for k in JLP_KEYS}
    print(f"  JLP series days: {n}")
    jk = max(JLP_KEYS, key=lambda k: n[k])
    if n[jk] < LOOK + 30:
        print("  not enough JLP history: not testable")
        return
    print(f"  using {jk}; first {px[jk].first_valid_index().date()}, last {px[jk].last_valid_index().date()}")
    P = pd.DataFrame({"JLP": px[jk], **{c: px[k] for c, k in COINS.items()}}).dropna()
    R = P.pct_change().dropna()
    R = R[R.index <= END]

    f = pd.read_parquet(PUB / "hl_funding.parquet")
    f = f[f["coin"].isin(list(COINS))].copy()
    f["day"] = pd.to_datetime(f["time"], unit="ms", utc=True).dt.normalize()
    F = f.groupby(["day", "coin"])["rate"].sum().unstack()[list(COINS)]
    fund_start = F.index.min()

    # weekly NNLS hedge, estimated on the trailing LOOK days before each Monday
    days = R.index
    first = max(days[LOOK], fund_start)
    mondays = [d for d in days if d >= first and d.weekday() == 0]
    beta = pd.DataFrame(index=days, columns=list(COINS), dtype=float)
    for m in mondays:
        win = R[R.index < m].tail(LOOK)
        beta.loc[m] = nnls_demeaned(win["JLP"].to_numpy(), win[list(COINS)].to_numpy())
    beta = beta.ffill().loc[mondays[0]:]
    R = R.loc[beta.index]
    F = F.reindex(R.index).fillna(0.0)
    turn = beta.diff().abs().sum(axis=1)
    turn.iloc[0] = beta.iloc[0].abs().sum()
    sb = beta.sum(axis=1)

    def run(cost_mult):
        hedged = R["JLP"] - (beta * R[list(COINS)]).sum(axis=1) + (beta * F).sum(axis=1)
        cost = cost_mult * (TAKER * turn + JLP_RT / 365.0)
        return (hedged - cost) / (1 + sb / LEV)

    base, hi = run(1.0), run(1.5)
    print(f"  OOS {R.index[0].date()}..{R.index[-1].date()}; avg beta SOL {beta['SOL'].mean():.2f} ETH {beta['ETH'].mean():.2f} "
          f"BTC {beta['BTC'].mean():.2f}; avg capital per $1 JLP {(1 + sb / LEV).mean():.2f}; "
          f"hedge funding received {((beta * F).sum(axis=1)).sum() * 365 / len(R):.1%}/yr of JLP; hedge turnover cost "
          f"{(TAKER * turn).sum() * 365 / len(R):.2%}/yr")
    print("  context (unhedged, per $1):")
    stats(R["JLP"], "JLP held")
    stats((beta * R[list(COINS)]).sum(axis=1), "hedge basket (long side)")
    mid = R.index[0] + (R.index[-1] - R.index[0]) / 2
    print("  hedged, return on capital:")
    c_full, dd_full = stats(base, "full, costs x1")
    c_h1, dd_h1 = stats(base[base.index < mid], "half 1")
    c_h2, dd_h2 = stats(base[base.index >= mid], "half 2")
    c_hi, dd_hi = stats(hi, "full, costs x1.5")
    print("  by calendar year:")
    for y in sorted(set(base.index.year)):
        stats(base[base.index.year == y], str(y))

    s1 = base[(base.index >= pd.Timestamp("2026-05-01", tz="UTC")) & (base.index <= END)]
    c_s1, _ = stats(s1, "Stage 1 window 2026-05-01..2026-10-31")
    kill = not (c_s1 >= 0.20)
    print(f"  STAGE 1 VERDICT: {'KILL (CAGR on capital < 20%/yr)' if kill else 'survives (kill-only)'}")
    worst = min(dd_full, dd_h1, dd_h2, dd_hi)
    prop = min(c_h1, c_h2) >= 1.0 and c_hi >= 1.0 and worst >= -0.25
    useful = min(c_h1, c_h2) >= 0.15 and c_hi >= 0.15 and worst >= -0.25
    v = "Prop-like PASS" if prop else ("Useful but not prop-like" if useful else "FAIL")
    print(f"  STAGE 2 VERDICT: {v}" + (" (Stage 1 already killed the prop-like question; Stage 2 shown as context)" if kill else ""))


if __name__ == "__main__":
    main()

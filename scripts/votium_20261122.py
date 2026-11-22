"""#267 Votium vlCVX bribes (docs/PREREG_BATCH6_20261122.md): Stage 0.5 bribe APR, then Stage 1/2 including CVX price (unhedgeable).

    uv run python scripts/votium_20261122.py | tee docs/jx_runs/votium_20261122.txt
"""
import json

import pandas as pd

raw = json.load(open("data/public/votium_raw.json"))
px = pd.read_parquet("data/public/votium_cvx_price.parquet")
px["day"] = pd.to_datetime(px["ts"], unit="s", utc=True).dt.floor("D")
P = px.drop_duplicates("day").set_index("day")["price"].sort_index()
rows = []
for k in sorted(raw, key=int):
    e = (raw[k] or {}).get("epoch") or {}
    if not e:
        continue
    end = pd.to_datetime(int(e["end"]), unit="s", utc=True).floor("D")
    usd = sum(float(b.get("amountDollars") or 0) for b in e.get("bribes") or [])
    votes = float(e.get("scoresTotal") or 0)
    p = P.asof(end) if len(P) else float("nan")
    apr = usd / (votes * p) * 26 * 100 if votes and p else float("nan")
    rows.append((int(k), end.date(), usd, votes, p, apr))
r = pd.DataFrame(rows, columns=["round", "end", "bribes_usd", "vlcvx_votes", "cvx_price", "bribe_apr"])
print(r.tail(8).round(2).to_string(index=False))
c = r.bribe_apr.tail(6).mean()
print(f"\nStage 0.5: last 6 rounds mean bribe APR {c:.2f}% -> {'KILL' if c < 8 else 'survives'}")
if c >= 8:
    s = P[P.index >= pd.Timestamp(str(r.end.iloc[0]), tz="UTC")]
    yrs = (s.index[-1] - s.index[0]).days / 365
    price_ret = (s.iloc[-1] / s.iloc[0]) ** (1 / yrs) - 1 if yrs > 0 else float("nan")
    tot = r.bribe_apr.mean() + price_ret * 100
    last90 = P[P.index >= P.index[-1] - pd.Timedelta(days=90)]
    st1 = r.bribe_apr.tail(6).mean() + ((last90.iloc[-1] / last90.iloc[0]) ** (365 / 90) - 1) * 100
    print(f"CVX price {s.iloc[0]:.2f} -> {s.iloc[-1]:.2f} over {yrs:.2f} yr ({price_ret:.1%}/yr); Stage 1 (bribes + 90-d CVX price, annualised) {st1:.2f}%")
    print(f"Window total (bribes {r.bribe_apr.mean():.1f}% + price {price_ret * 100:.1f}%/yr) = {tot:.2f}%/yr -> "
          f"{'KILL at Stage 1' if st1 < 4 else ('FAIL' if tot < 8 else 'needs halves')}")

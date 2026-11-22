"""Batch 6 part B: Stage 0.5 for #259-#262, #265-#267, #271 (docs/PREREG_BATCH6_20261122.md).

    uv run python scripts/batch6b_20261122.py | tee docs/jx_runs/batch6b_20261122.txt
"""
import json

import numpy as np
import pandas as pd

v = lambda c: "KILL" if not c == c or c < 8 else "survives Stage 0.5"  # noqa: E731
raw = json.load(open("data/public/batch6_raw.json"))
# HL 90-d short funding (annualised %), all coins available
hl = pd.read_parquet("data/public/hl_funding.parquet")
hl["ts"] = pd.to_datetime(hl["time"], unit="ms", utc=True)
H = hl[hl.ts > hl.ts.max() - pd.Timedelta(days=90)].groupby("coin").rate.sum() / 90 * 365 * 100
for fn, tcol, unit in (("data/public/batch5_hlfunding.parquet", "t", "s"), ("data/public/hedged_hlfunding.parquet", "t", "s")):
    x = pd.read_parquet(fn)
    x["ts"] = pd.to_datetime(x[tcol], unit=unit, utc=True)
    H = pd.concat([H, x[x.ts > x.ts.max() - pd.Timedelta(days=90)].groupby("coin").rate.sum() / 90 * 365 * 100]).groupby(level=0).last()

# 259 Paradex current funding vs HL 90-d
pp = [x for x in (raw.get("paradex_summary") or {}).get("results", []) if str(x.get("symbol", "")).endswith("-PERP")]
P = {}
for x in pp:
    try:
        coin = x["symbol"].split("-")[0]
        P[coin] = float(x["funding_rate"]) * (525600 / float(x.get("funding_interval_minutes") or 480)) * 100
    except (TypeError, ValueError):
        pass
common = sorted(set(P) & set(H.index))
gaps = sorted(((abs(P[c] - H[c]), c, P[c], H[c]) for c in common), reverse=True)
c259 = 1.5 * gaps[0][0] if gaps else float("nan")
print(f"#259 Paradex vs HL: {len(common)} common coins; largest gaps: " + "; ".join(f"{c} {g:.1f}% (PDX {p:.1f} / HL {h:.1f})" for g, c, p, h in gaps[:5]))
print(f"   ceiling 1.5 x max gap = {c259:.2f}% -> {v(c259)}  [Paradex value is a single current reading: noisy, optimistic]")
# 260 Lighter 90-d vs HL 90-d
L = pd.read_parquet("data/public/batch6_lighter_funding.parquet")
L["r"] = pd.to_numeric(L.rate) * np.where(L.direction == "long", 1, -1)  # % per hour received by a short
LA = L.groupby("symbol").r.mean() * 8760
common = sorted(set(LA.index) & set(H.index))
g2 = sorted(((abs(LA[c] - H[c]), c, LA[c], H[c]) for c in common), reverse=True)
c260 = 1.5 * g2[0][0] if g2 else float("nan")
print(f"#260 Lighter vs HL (90 d each): {len(common)} common coins; largest: " + "; ".join(f"{c} {g:.1f}% (LTR {a:.1f} / HL {h:.1f})" for g, c, a, h in g2[:5]))
print(f"   ceiling {c260:.2f}% -> {v(c260)}")
# 261 zero-fee single-venue carry
best_l = LA.sort_values(ascending=False).head(3)
best_p = pd.Series(P).sort_values(ascending=False).head(3)
c261 = max(best_l.mean(), best_p.mean()) / (4 / 3)
print(f"#261 zero-fee carry: Lighter best-3 90-d {', '.join(f'{k} {x:.1f}%' for k, x in best_l.items())}; Paradex best-3 current "
      f"{', '.join(f'{k} {x:.1f}%' for k, x in best_p.items())} -> ceiling {c261:.2f}% -> {v(c261)}  [best-3 chosen with hindsight; long-tail coins]")
# 262 real-yield staking hedged
fh = (raw.get("fees_holders") or {}).get("protocols", [])
mc = pd.DataFrame(raw.get("protocol_mcaps") or [])
mc["key"] = mc["slug"].astype(str).str.lower()
rows = []
for x in fh:
    yr = x.get("total1y") or ((x.get("monthlyAverage1y") or 0) * 12) or 0
    slug = str(x.get("slug") or x.get("name") or "").lower()
    m = mc[(mc.key == slug) | (mc.name.astype(str).str.lower() == str(x.get("name", "")).lower())]
    if not len(m) or not yr:
        continue
    cap, sym = m.mcap.iloc[0], str(m.symbol.iloc[0]).upper()
    if not cap or cap < 20e6 or sym not in H.index:
        continue
    apr = yr / (0.3 * cap) * 100
    rows.append((x.get("name"), sym, yr, cap, apr, H[sym], (apr + H[sym]) / (4 / 3)))
r = pd.DataFrame(rows, columns=["protocol", "token", "holders_rev_1y", "mcap", "staker_apr_if_30pct_staked", "hl_short_funding_90d", "ceiling"]).sort_values("ceiling", ascending=False)
print(f"#262 real-yield staking hedged: {len(r)} protocols with holders revenue, mcap >= $20M and an HL perp")
print(r.head(10).round(2).to_string(index=False))
c262 = r.ceiling.iloc[0] if len(r) else float("nan")
print(f"   best ceiling {c262:.2f}% -> {v(c262)}  [assumes only 30% of supply staked: optimistic]")
print("#265 Drift insurance fund: no source answered from the runner -> not testable")
print("#266 Aave Umbrella: no source answered -> not testable")
print("#267 Votium (vlCVX bribes): API returned only the list of rounds; per-round bribe data not fetched -> needs a follow-up fetch")
# 271 CME basis
def yser(key):
    res = ((raw.get(key) or {}).get("chart") or {}).get("result") or [{}]
    t, q = res[0].get("timestamp") or [], ((res[0].get("indicators") or {}).get("quote") or [{}])[0].get("close") or []
    return pd.Series(q, index=pd.to_datetime(t, unit="s", utc=True).floor("D")).dropna()
F, S = yser("yahoo_BTC=F"), yser("yahoo_BTC-USD")
j = pd.concat([F, S], axis=1, keys=["F", "S"]).dropna()
j = j[j.index > j.index.max() - pd.Timedelta(days=90)]
basis = ((j.F / j.S - 1) * 12 * 100)  # front month ~30 days to roll, annualised
c271 = basis.mean() / 1.4
print(f"#271 CME BTC basis: {len(j)} days; mean annualised front-month basis {basis.mean():.2f}% (min {basis.min():.1f}, max {basis.max():.1f}); "
      f"on capital (spot + 40% margin) {c271:.2f}% -> {v(c271)}")

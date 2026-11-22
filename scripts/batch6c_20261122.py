"""Batch 6 Stage 1 for #260 and #261 on the fetched ~92 days (docs/PREREG_BATCH6_20261122.md).

    uv run python scripts/batch6c_20261122.py | tee docs/jx_runs/batch6c_20261122.txt
"""
import numpy as np
import pandas as pd

L = pd.read_parquet("data/public/batch6_lighter_funding.parquet")
L["ts"] = pd.to_datetime(pd.to_numeric(L.timestamp), unit="s", utc=True).dt.floor("h")
L["r"] = pd.to_numeric(L.rate) / 100 * np.where(L.direction == "long", 1, -1)  # fraction per hour received by a short
LH = L.pivot_table(index="ts", columns="symbol", values="r", aggfunc="mean").sort_index()
hl = pd.read_parquet("data/public/hl_funding.parquet")
hl["ts"] = pd.to_datetime(hl["time"], unit="ms", utc=True).dt.floor("h")
extra = []
for fn in ("data/public/batch5_hlfunding.parquet", "data/public/hedged_hlfunding.parquet"):
    x = pd.read_parquet(fn)
    x["ts"] = pd.to_datetime(x["t"], unit="s", utc=True).dt.floor("h")
    extra.append(x[["coin", "ts", "rate"]])
H = pd.concat([hl[["coin", "ts", "rate"]]] + extra).drop_duplicates(["coin", "ts"]).pivot_table(index="ts", columns="coin", values="rate", aggfunc="mean")
start = LH.index.min()
coins = sorted(set(LH.columns) & set(H.columns))
days = pd.date_range(start.ceil("D") + pd.Timedelta(days=1), LH.index.max().floor("D"), freq="D")
print(f"window {days[0].date()}..{days[-1].date()} ({len(days)} days); common coins {len(coins)}: {', '.join(coins)}")
# 260
openp, daily = {}, []
for d in days:
    prev, today = slice(d - pd.Timedelta(hours=24), d - pd.Timedelta(hours=1)), slice(d, d + pd.Timedelta(hours=23))
    pnl = 0.0
    for c in list(openp):
        sig = (LH[c][prev] - H[c][prev]).mean() * 8760 * 100
        if not np.isfinite(sig) or np.sign(sig) != openp[c]:
            pnl -= 0.00045 * 2 / 2  # close: HL leg taker (Lighter 0)
            openp.pop(c)
    cands = sorted(((-abs(s), c, np.sign(s)) for c in coins
                    if c not in openp and np.isfinite(s := (LH[c][prev] - H[c][prev]).mean() * 8760 * 100) and abs(s) >= 15))
    for _, c, sg in cands:
        if len(openp) >= 5:
            break
        openp[c] = sg
        pnl -= 0.00045 * 2 / 2  # open: HL leg taker
    for c, sg in openp.items():
        pnl += sg * (LH[c][today] - H[c][today]).fillna(0).sum()
    daily.append((d, pnl / (5 * 2 / 3)))
s = pd.Series(dict(daily))
r260 = s.mean() * 365 * 100
print(f"#260 Lighter-HL gap, Stage 1 realised: {r260:.2f}%/yr on capital -> {'KILL' if r260 < 4 else 'survives Stage 1 (Stage 2 needs > 180 days of Lighter history: not available -> not testable beyond Stage 1)'}")
# 261
held, out = [], []
for i, d in enumerate(days):
    if i % 7 == 0:
        w = slice(d - pd.Timedelta(days=14), d - pd.Timedelta(hours=1))
        score = LH.loc[w].mean().dropna().sort_values(ascending=False)
        new = list(score.index[:3])
        cost = len(set(new) ^ set(held)) * (0.003 + 0.0) / 3
        held = new
    else:
        cost = 0.0
    today = slice(d, d + pd.Timedelta(hours=23))
    r = [LH[c][today].fillna(0).sum() for c in held] if held else [0.0]
    out.append((d, np.mean(r) / (4 / 3) - cost))
s2 = pd.Series(dict(out))
r261 = s2.mean() * 365 * 100
print(f"#261 zero-fee carry on Lighter (weekly top 3), Stage 1 realised: {r261:.2f}%/yr -> {'KILL' if r261 < 4 else 'survives Stage 1 (Stage 2: < 180 days of history -> not testable beyond Stage 1)'}")
print(f"   last holdings: {', '.join(held)}")

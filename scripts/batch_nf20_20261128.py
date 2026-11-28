"""Batch NF20 #623-#626: Bittensor dTAO subnet staking, TAO hedged (docs/PREREG_BATCH_NF20_20261128.md, addenda 1-2).

    uv run python -m scripts.batch_nf20_20261128 | tee docs/jx_runs/batch_nf20_20261128.txt
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

PUB = Path(__file__).resolve().parent.parent / "data" / "public"
SIZE, SHARE_STAKERS, TAKE, BPD, MIN_TAO = 1500.0, 0.41, 0.18, 7200, 1000.0
S1 = (pd.Timestamp("2025-03-01"), pd.Timestamp("2026-01-01"))
S2 = (pd.Timestamp("2026-01-01"), pd.Timestamp("2026-11-01"))


def load():
    d = pd.read_parquet(PUB / "batchnf20_subnets_1d.parquet")
    d["day"] = pd.to_datetime(d["day"])
    d = d[d["netuid"] > 0].drop_duplicates(["day", "netuid"])  # root (netuid 0) has no alpha pool
    d["px"] = np.where(d["alpha_in"] > 0, d["tao_in"] / d["alpha_in"], np.nan)
    d["yld"] = d["alpha_out_emission"] * BPD * SHARE_STAKERS * (1 - TAKE) / d["alpha_out"].where(d["alpha_out"] > 0)
    grid = sorted(pd.date_range("2025-03-01", "2026-11-25", freq="7D"))
    w = d[d["day"].isin(grid)].copy()
    daily = d[~d["day"].isin(grid)]
    return w, daily


def tao_usd():
    c = pd.read_parquet(PUB / "uncharted_385_candles.parquet")
    c = c[c["coin"] == "TAO"].copy()
    c["day"] = pd.to_datetime(c["t"], unit="ms").dt.normalize()
    return c.drop_duplicates("day").set_index("day")["c"].sort_index()


def tao_funding():
    f = pd.read_parquet(PUB / "fivehigh_hl_premium.parquet")
    f = f[f["coin"] == "TAO"].copy()
    f["day"] = pd.to_datetime(f["t"], unit="ms").dt.normalize()
    daily = f.groupby("day")["rate"].sum()
    return daily, float(daily.mean())


def hold(w, netuid, d0, d1, usd, fund, fmean, slip_mult=1.0):
    s = w[w["netuid"] == netuid].set_index("day").sort_index()
    if d0 not in s.index:
        return None
    a = s.loc[d0]
    if not (a["px"] > 0 and a["tao_in"] > 0):
        return None
    same = s[s["registered_at"] == a["registered_at"]] if pd.notna(a["registered_at"]) else s
    inside = same.loc[d0:d1]
    end = inside.iloc[-1]
    # deregistered: absent at the end snapshot (which exists in the data), or the netuid was re-used by a new registration
    dead = d1 in set(w["day"]) and end.name < d1
    days = (d1 - d0).days
    yld = float(inside["yld"].iloc[:-1].mean() if len(inside) > 1 else a["yld"]) * days
    px_usd = float(usd.asof(d0)) if len(usd) else np.nan
    x_tao = SIZE / px_usd if px_usd > 0 else np.nan
    slip_in = x_tao / (a["tao_in"] + x_tao)
    alpha = x_tao / a["px"] * (1 - slip_in) * (1 + yld)
    if dead:
        gross = -1.0  # registered rule: value is what the pool paid out, taken as 0 when the subnet is gone
    else:
        slip_out = alpha / (end["alpha_in"] + alpha) if end["alpha_in"] > 0 else 1.0
        gross = alpha * end["px"] * (1 - slip_mult * slip_out) / x_tao - 1 - (slip_mult - 1) * slip_in
    f = fund.reindex(pd.date_range(d0, d1 - pd.Timedelta(days=1))).fillna(fmean).sum()
    return {"start": d0, "netuid": netuid, "ret": gross + f, "yield": yld, "dead": dead, "slip": slip_in}


def months(w):
    snaps = sorted(w["day"].unique())
    out = []
    for m in pd.date_range("2025-03-01", "2026-11-01", freq="MS"):
        a = next((d for d in snaps if d >= m), None)
        b = next((d for d in snaps if d >= m + pd.offsets.MonthBegin(1)), None)
        if a is not None and b is not None and a < b:
            out.append((pd.Timestamp(a), pd.Timestamp(b)))
    return out


def portfolio(w, pick, usd, fund, fmean, slip_mult=1.0):
    rows = []
    for d0, d1 in months(w):
        snap = w[(w["day"] == d0) & (w["tao_in"] >= 0)]
        ids = pick(snap)
        hs = [h for h in (hold(w, n, d0, d1, usd, fund, fmean, slip_mult) for n in ids) if h]
        if hs:
            rows.append({"start": d0, "ret": float(np.mean([h["ret"] for h in hs])), "n": len(hs),
                         "yield": float(np.mean([h["yield"] for h in hs])), "dead": sum(h["dead"] for h in hs)})
    return pd.DataFrame(rows)


def summ(e, w):
    g = e[(e["start"] >= w[0]) & (e["start"] < w[1])] if len(e) else e
    if g.empty:
        return dict(n=0)
    r = g["ret"]
    return dict(n=len(g), m=r.mean(), t=r.mean() / (r.std(ddof=1) / np.sqrt(len(r))) if len(r) > 1 else np.nan, win=(r > 0).mean(),
                ex3=r.sort_values().iloc[:-3].sum() if len(r) > 3 else np.nan, y=g["yield"].mean())


def fmt(label, s, unit="hold"):
    if not s.get("n"):
        return f"   {label}: no {unit}s"
    return (f"   {label}: {unit}s {s['n']} | mean net {s['m']:+.2%} (t {s['t']:.2f}, win {s['win']:.0%}) | mean model yield in hold "
            f"{s['y']:+.2%} | sum without 3 best {s['ex3']:+.2%}")


def verdict(e, e15, min_n, sane, unit="hold"):
    a, b, b15 = summ(e, S1), summ(e, S2), summ(e15, S2)
    print(fmt("Stage 1 holds starting 2025-03..2025-12", a, unit))
    print(fmt("Stage 2 holds starting 2026-01..2026-10", b, unit))
    print(f"   slippage x1.5 Stage 2 mean {b15.get('m', np.nan):+.2%}")
    if a.get("n", 0) >= 10 and not (a["m"] > 0):
        v = "KILL (Stage 1)"
    else:
        ok = (b.get("n", 0) >= min_n and b["m"] >= 0.03 and b["t"] >= 2 and b["ex3"] > 0 and b15.get("m", -1) > 0 and sane)
        v = "PASS" if ok else "FAIL"
    if v == "PASS":
        v += " (forward log)" if b["t"] >= 2.5 else " (t < 2.5: not forward-logged)"
    print(f"   VERDICT {v}\n")


def main():
    w, daily = load()
    usd = tao_usd()
    fund, fmean = tao_funding()
    snaps = sorted(w["day"].unique())
    span = (snaps[-1] - snaps[0]).days if snaps else 0
    print(f"weekly snapshots {len(snaps)} ({snaps[0].date() if snaps else '-'}..{snaps[-1].date() if snaps else '-'}, {span} days); "
          f"subnets {w['netuid'].nunique()}; HL TAO funding days {len(fund)} (mean {fmean * 365:+.1%}/yr, used before 2026-07-28)")
    stage0 = len(snaps) >= 29 and span >= 200 and w["netuid"].nunique() >= 30
    print(f"Stage 0 data bar (>= 29 weekly snapshots, >= 200 days, >= 30 subnets): {'met' if stage0 else 'NOT MET -> not testable'}")
    if not stage0:
        return
    last = w[w["day"] == snaps[-1]].set_index("netuid")
    sane = True
    for n in (1, 64):
        if n in last.index:
            print(f"   sanity: SN{n} model staker yield {last.at[n, 'yld'] * 365:.1%}/yr (simple) at {snaps[-1].date()}; "
                  "compare with a published APY snapshot (recorded in the PREREG result)")
    print()

    big = lambda s: s[s["tao_in"] >= MIN_TAO]  # noqa: E731
    specs = [("#623", "Top-10 subnets by emission value (alpha_out_emission x price), monthly",
              lambda s: s.assign(v=s["alpha_out_emission"] * s["px"]).nlargest(10, "v")["netuid"].tolist(), 10),
             ("#625", "Highest model-yield decile (tao_in >= 1,000 TAO), monthly",
              lambda s: big(s).nlargest(max(1, len(big(s)) // 10), "yld")["netuid"].tolist(), 10),
             ("#626", "Control: 5 largest pools by tao_in, monthly", lambda s: s.nlargest(5, "tao_in")["netuid"].tolist(), 10)]
    for num, label, pick, n in specs:
        print(f"{num} {label}")
        e, e15 = portfolio(w, pick, usd, fund, fmean), portfolio(w, pick, usd, fund, fmean, 1.5)
        if len(e):
            print(f"   holds with a deregistered subnet: {int(e['dead'].sum())}")
        verdict(e, e15, n, sane)

    print("#624 New subnets: stake 7+ days after registration (tao_in >= 1,000 TAO), hold 90 days")
    first = w.groupby("netuid")["day"].min()
    reg = w.groupby("netuid")["registered_at"].first()
    rows, rows15 = [], []
    for netuid, d_first in first.items():
        if d_first <= snaps[0]:
            continue  # registered before the data starts
        s = w[(w["netuid"] == netuid) & (w["day"] >= d_first + pd.Timedelta(days=7)) & (w["tao_in"] >= MIN_TAO)]
        if s.empty:
            continue
        d0 = s["day"].min()
        d1 = next((d for d in snaps if d >= d0 + pd.Timedelta(days=90)), None)
        if d1 is None:
            continue
        for out, m in ((rows, 1.0), (rows15, 1.5)):
            h = hold(w, netuid, d0, pd.Timestamp(d1), usd, fund, fmean, m)
            if h:
                out.append(h)
    e, e15 = pd.DataFrame(rows), pd.DataFrame(rows15)
    print(f"   new subnets with a 90-day hold: {len(e)}; deregistered during the hold: {int(e['dead'].sum()) if len(e) else 0}; "
          f"registration field present for {int(reg.notna().sum())} subnets")
    verdict(e, e15, 20, sane, unit="subnet hold")


if __name__ == "__main__":
    main()

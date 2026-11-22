"""Batch 9 (docs/PREREG_BATCH9_20261122.md): MYR fallback benchmark + walk-forward of #292 VIX roll, #293 FX carry, #294 Cboe option
indices, #295 levered risk parity. Monthly walk-forward on trailing 36 months; OOS 2016-01..2026-10; bar 10%/yr (CAGR).

    uv run python -m scripts.batch9_20261122 | tee docs/jx_runs/batch9_20261122.txt
"""
from __future__ import annotations

import io
import itertools
import json
import sys

import numpy as np
import pandas as pd

P = "data/public/"
OOS0, OOS1, SPLIT = pd.Period("2016-01", "M"), pd.Period("2026-10", "M"), pd.Period("2021-05", "M")
BAR = 10.0


def fred():
    raw = json.load(open(P + "batch9_fred.json"))
    out = {}
    for sid, txt in raw.items():
        d = pd.read_csv(io.StringIO(txt))
        d.columns = ["d", "v"]
        out[sid] = pd.to_numeric(d.set_index(pd.to_datetime(d["d"]))["v"], errors="coerce").dropna()
    return out


F = fred()


def monthly_last(s):
    return s.groupby(s.index.to_period("M")).last()


def tbill_m():
    return (monthly_last(F["DTB3"]) / 100 / 12).rename("tb")


def spy_m():
    raw = json.load(open(P + "batch9_spy.json"))
    if raw.get("yahoo"):
        j = json.loads(raw["yahoo"])["chart"]["result"][0]
        s = pd.Series(j["indicators"]["adjclose"][0]["adjclose"], index=pd.to_datetime(j["timestamp"], unit="s")).dropna()
        return monthly_last(s).pct_change().dropna(), "Yahoo adjusted close (dividends included)"
    d = pd.read_csv(io.StringIO(raw["stooq"]))
    s = d.set_index(pd.to_datetime(d["Date"]))["Close"]
    return monthly_last(s).pct_change().dropna() + 0.018 / 12, "stooq price + 1.8%/yr dividends (assumed)"


def stats(r):
    r = r.dropna()
    if not len(r):
        return np.nan, np.nan
    eq = (1 + r).cumprod()
    cagr = (eq.iloc[-1] ** (12 / len(r)) - 1) * 100
    dd = float((eq / eq.cummax() - 1).min() * 100)
    return cagr, dd


def benchmark():
    spy, src = spy_m()
    fx = monthly_last(F["DEXMAUS"])  # MYR per USD
    fxr = fx.pct_change()
    tb = tbill_m()
    dep = (monthly_last(F["INTDSRMYM193N"]) / 100 / 12) if "INTDSRMYM193N" in F else pd.Series(dtype=float)
    idx = pd.period_range("2006-01", "2026-10", freq="M")
    fd = dep.reindex(idx)
    assumed = int(fd.isna().sum())
    fd = fd.fillna(0.025 / 12)
    spy_myr = ((1 + spy.reindex(idx)) * (1 + fxr.reindex(idx)) - 1)
    tb_myr = ((1 + tb.reindex(idx)) * (1 + fxr.reindex(idx)) - 1)
    print(f"===== A. Benchmark in MYR, 2006-01..2026-10 (SPY: {src}; MY deposit rate: FRED, {assumed} months filled with 2.5%/yr assumed)")
    port = {"100% fixed deposit (MYR)": fd, "100% USD T-bills in MYR": tb_myr, "100% S&P 500 in MYR": spy_myr}
    for w in (0.5, 0.7):
        rr, yr = [], None
        val_s, val_f = w, 1 - w
        for p_ in idx:
            if yr is not None and p_.year != yr:
                tot = val_s + val_f
                val_s, val_f = tot * w, tot * (1 - w)
            yr = p_.year
            prev = val_s + val_f
            val_s *= 1 + spy_myr[p_]
            val_f *= 1 + fd[p_]
            rr.append((val_s + val_f) / prev - 1)
        port[f"{int(w * 100)}/{int(100 - w * 100)} S&P/FD (annual rebalance)"] = pd.Series(rr, index=idx)
    rows = []
    for k, r in port.items():
        c, d = stats(r)
        yrs = (1 + r).groupby(r.index.year).prod() - 1
        rows.append((k, c, d, yrs.min() * 100, yrs.idxmin(), (yrs < 0).sum()))
        print(f"  {k:42s} CAGR {c:5.2f}%  worst drawdown {d:6.1f}%  worst year {yrs.min() * 100:6.1f}% ({yrs.idxmin()})  losing years {(yrs < 0).sum()}")
    tab = pd.DataFrame({k: ((1 + r).groupby(r.index.year).prod() - 1) * 100 for k, r in port.items()}).round(1)
    print("\n  per year (%):\n" + tab.to_string())
    usd = stats(spy.reindex(idx))
    print(f"\n  (context) S&P 500 in USD: CAGR {usd[0]:.2f}%, worst drawdown {usd[1]:.1f}%; MYR per USD {fx.reindex(idx).iloc[0]:.2f} -> {fx.reindex(idx).dropna().iloc[-1]:.2f}\n")


def walk(name, M, switch_cost=0.0, spy=None):
    """M: DataFrame monthly returns (rows Period M, cols configs), cost_mult applied by caller via M15."""
    M15 = M[1] if isinstance(M, tuple) else None
    M = M[0] if isinstance(M, tuple) else M
    M = M.sort_index()

    def run(X):
        out, prev, sw, picks = [], None, 0, []
        for m in pd.period_range(OOS0, OOS1, freq="M"):
            tr = X.loc[(X.index >= m - 36) & (X.index < m)]
            tr = tr.loc[:, tr.notna().sum() >= 24]
            if tr.empty or m not in X.index:
                out.append((m, np.nan))
                continue
            best = tr.mean().idxmax()
            picks.append(best)
            r = X.at[m, best]
            if prev is not None and best != prev:
                r -= switch_cost
                sw += 1
            prev = best
            out.append((m, r))
        return pd.Series(dict(out)), sw, picks
    s, sw, picks = run(M)
    s15 = run(M15)[0] if M15 is not None else s
    h1, h2 = stats(s[s.index < SPLIT])[0], stats(s[s.index >= SPLIT])[0]
    c15 = stats(s15)[0]
    cagr, dd = stats(s)
    sp = spy.reindex(s.dropna().index)
    spdd = stats(sp)[1]
    ok = h1 >= BAR and h2 >= BAR and c15 >= BAR and dd >= spdd
    top = pd.Series(picks).value_counts().head(3)
    print(f"===== {name}: {M.shape[1]} configs; OOS months with data {s.notna().sum()}")
    print(f"  walk-forward OOS 2016-01..2026-10: CAGR {cagr:.2f}%; halves {h1:.2f}% / {h2:.2f}%; costs x1.5 {c15:.2f}%; worst drawdown {dd:.1f}% "
          f"(SPY same months {spdd:.1f}%); switches {sw}")
    print("  most-picked: " + "; ".join(f"{k} ({v}x)" for k, v in top.items()))
    hind = M.loc[(M.index >= OOS0) & (M.index <= OOS1)].apply(lambda c: stats(c)[0]).sort_values(ascending=False).head(3)
    print("  (context) best fixed configs over OOS in hindsight: " + "; ".join(f"{k} {v:.2f}%" for k, v in hind.items()))
    print(f"  VERDICT: {'PASS' if ok else 'FAIL'}\n", flush=True)


# ---------------------------------------------------------------- 292 VIX futures roll-down
def vx_panel():
    raw = json.load(open(P + "batch9_vx.json"))
    rows = []
    for exp, txt in raw.items():
        d = pd.read_csv(io.StringIO(txt))
        d.columns = [c.strip() for c in d.columns]
        col = "Settle" if "Settle" in d else d.columns[6]
        for t, v in zip(pd.to_datetime(d["Trade Date"]), pd.to_numeric(d[col], errors="coerce")):
            if v and v > 0:
                rows.append((t, pd.Timestamp(exp), v))
    return pd.DataFrame(rows, columns=["t", "exp", "f"])


def cboe(sym):
    raw = json.load(open(P + "batch9_cboe.json"))
    if sym not in raw:
        return None
    d = pd.read_csv(io.StringIO(raw[sym]))
    return pd.to_numeric(d.set_index(pd.to_datetime(d.iloc[:, 0]))[d.columns[-1]], errors="coerce").dropna().sort_index()


def p292(spy):
    vx = vx_panel()
    vix, v3m = cboe("VIX"), cboe("VIX3M")
    print(f"#292 data: {vx.exp.nunique()} VX contracts, {vx.t.min():%Y-%m-%d}..{vx.t.max():%Y-%m-%d}; VIX3M {'yes' if v3m is not None else 'no'}")
    days = sorted(vx.t.unique())
    piv = vx.pivot_table(index="t", columns="exp", values="f")
    tbd = (F["DTB3"] / 100 / 360).reindex(days).ffill().fillna(0)
    ratio = (v3m / vix).reindex(days).ffill()
    vixd = vix.reindex(days).ffill()
    # constant-maturity short: daily return of a target-maturity blend of the two contracts bracketing it
    cm = {}
    for tgt, name in ((30, "VX1"), (60, "VX2")):
        r, w_prev, turn = [], None, []
        for i in range(1, len(days)):
            t0, t1 = days[i - 1], days[i]
            row = piv.loc[t0].dropna()
            exps = sorted(e for e in row.index if (e - t0).days > 0)
            if len(exps) < 3:
                r.append(np.nan)
                turn.append(0.0)
                continue
            dte = np.array([(e - t0).days for e in exps])
            j = int(np.searchsorted(dte, tgt))
            j = min(max(j, 1), len(exps) - 1)
            a, b = exps[j - 1], exps[j]
            wb = (tgt - dte[j - 1]) / (dte[j] - dte[j - 1])
            wb = min(max(wb, 0), 1)
            w = {a: 1 - wb, b: wb}
            ret = 0.0
            for e, wi in w.items():
                f0, f1 = piv.at[t0, e], piv.at[t1, e] if e in piv.columns else np.nan
                if pd.notna(f0) and pd.notna(f1):
                    ret += wi * (f1 / f0 - 1)
            r.append(-ret)  # short
            tv = sum(abs(w.get(e, 0) - (w_prev or {}).get(e, 0)) * 0.05 / piv.at[t0, e] for e in set(w) | set(w_prev or {}) if pd.notna(piv.at[t0, e]))
            turn.append(tv if w_prev else 0.0)
            w_prev = w
        cm[name] = (pd.Series(r, index=days[1:]), pd.Series(turn, index=days[1:]))

    def build(cmult):
        cols = {}
        for e, c, flt, ex in itertools.product((0.1, 0.2, 0.3, 0.5), ("VX1", "VX2"), ("always", "gt1.0", "gt1.1"), ("none", "vix30")):
            r, tv = cm[c]
            on = pd.Series(True, index=r.index)
            if flt != "always":
                on &= (ratio.shift(1).reindex(r.index) > float(flt[2:])).fillna(False)
            if ex == "vix30":
                on &= (vixd.shift(1).reindex(r.index) <= 30).fillna(False)
            sw = on.astype(int).diff().abs().fillna(0)
            d = tbd.reindex(r.index) + np.where(on, e * r.fillna(0) - e * tv * cmult, 0) - sw * e * 0.05 / 20 * cmult
            cols[f"e{e}/{c}/{flt}/{ex}"] = (1 + d).groupby(d.index.to_period("M")).prod() - 1
        return pd.DataFrame(cols)
    walk("#292 VIX futures roll-down (short)", (build(1.0), build(1.5)), 0.001, spy)


# ---------------------------------------------------------------- 293 FX carry
FXMAP = {"JP": ("DEXJPUS", True), "AU": ("DEXUSAL", False), "NZ": ("DEXUSNZ", False), "CA": ("DEXCAUS", True), "CH": ("DEXSZUS", True),
         "GB": ("DEXUSUK", False), "EZ": ("DEXUSEU", False), "NO": ("DEXNOUS", True), "SE": ("DEXSDUS", True), "MX": ("DEXMXUS", True),
         "BR": ("DEXBZUS", True), "ZA": ("DEXSFUS", True), "KR": ("DEXKOUS", True), "IN": ("DEXINUS", True), "CN": ("DEXCHUS", True)}


def p293(spy):
    us = monthly_last(F.get("IR3TIB01USM156N", F["DTB3"])) / 100
    tb = tbill_m()
    S, I, D = {}, {}, {}
    for c, (sid, inv) in FXMAP.items():
        rid = f"IR3TIB01{c}M156N"
        if sid not in F or rid not in F:
            continue
        px = 1 / F[sid] if inv else F[sid]  # USD per unit of foreign currency
        S[c] = monthly_last(px)
        D[c] = px.pct_change()
        I[c] = monthly_last(F[rid]) / 100
    S, I = pd.DataFrame(S), pd.DataFrame(I)
    Dd = pd.DataFrame(D)
    carry = I.sub(us, axis=0)
    ex = (S.shift(-1) / S - 1) + carry / 12  # return over month m+1 of a long held from end of month m (indexed at m)
    vix = monthly_last(F["VIXCLS"])
    print(f"#293 data: {S.shape[1]} currencies with FX and rates: {list(S.columns)}; months {S.index.min()}..{S.index.max()}")
    months = S.index

    def build(cmult):
        cols = {}
        for k, fund, lev, flt in itertools.product((1, 2, 3), ("USD", "low"), (1, 2), ("none", "vix25", "vt10")):
            out, prev = {}, set()
            for m in months[:-1]:
                cr = carry.loc[m].dropna()
                if len(cr) < k + 1:
                    continue
                longs = list(cr.sort_values(ascending=False).index[:k])
                shorts = list(cr.sort_values().index[:1]) if fund == "low" else []
                if any(x in longs for x in shorts):
                    shorts = []
                r = ex.loc[m, longs].mean() - (ex.loc[m, shorts].mean() if shorts else 0.0)
                if pd.isna(r):
                    continue
                scale = float(lev)
                if flt == "vix25" and not (vix.get(m, np.nan) < 25):
                    scale = 0.0
                if flt == "vt10":
                    end = m.to_timestamp(how="end")
                    dd = Dd.loc[(Dd.index > end - pd.Timedelta(days=90)) & (Dd.index <= end), longs].mean(axis=1)
                    if shorts:
                        dd = dd - Dd.loc[dd.index, shorts].mean(axis=1)
                    vol = dd.std() * np.sqrt(252)
                    scale = lev * min(3.0, 0.10 / vol) if vol and vol > 0 else 0.0
                book = set(longs) | {"-" + s for s in shorts}
                turn = len(book ^ prev) / max(len(book), 1)
                prev = book if scale else set()
                out[m + 1] = tb.get(m + 1, 0.0) + scale * r - scale * (0.0005 * 2 * turn + 0.005 / 12) * cmult
            cols[f"k{k}/{fund}/lev{lev}/{flt}"] = pd.Series(out)
        return pd.DataFrame(cols)
    walk("#293 FX carry", (build(1.0), build(1.5)), 0.0005, spy)


# ---------------------------------------------------------------- 294 Cboe option indices
def p294(spy):
    tb = tbill_m()
    syms = [s for s in ("PUT", "WPUT", "BXM", "BXMD", "BXY", "CLL", "CLLZ", "CNDR", "PPUT", "BFLY", "CMBO", "PUTR", "BXMW", "VXTH", "SPRO", "BXMC",
                        "SPEN") if cboe(s) is not None]
    print(f"#294 Cboe indices available: {syms}")
    R = {s: monthly_last(cboe(s)).pct_change() for s in syms}

    def build(cmult):
        cols = {}
        for s, L in itertools.product(syms, (1.0, 1.5)):
            r = R[s]
            cols[f"{s}/x{L}"] = L * r - (L - 1) * (tb.reindex(r.index).fillna(0) + 0.005 / 12) - 0.005 / 12 * cmult
        return pd.DataFrame(cols)
    if syms:
        walk("#294 Cboe option-strategy indices", (build(1.0), build(1.5)), 0.001, spy)
    else:
        print("  no index data -> not testable\n")


# ---------------------------------------------------------------- 295 risk parity
def p295(spy):
    tb = tbill_m()
    y = monthly_last(F["DGS10"]) / 100
    bond = (y.shift(1) / 12 - 8.5 * (y - y.shift(1))).dropna()
    idx = spy.index.intersection(bond.index)

    def build(cmult):
        cols = {}
        for w, L, vt in itertools.product((0.4, 0.5, 0.6), (1.0, 1.5, 2.0), ("none", "vt10")):
            mix = w * spy.reindex(idx) + (1 - w) * bond.reindex(idx)
            if vt == "vt10":
                vol = mix.rolling(12).std().shift(1) * np.sqrt(12)
                expo = (L * 0.10 / vol).clip(upper=3.0)
            else:
                expo = pd.Series(L, index=idx)
            fin = (tb.reindex(idx).fillna(0) + 0.005 / 12 * cmult)
            cols[f"w{int(w * 100)}/L{L}/{vt}"] = expo * mix - (expo - 1).clip(lower=0) * fin + (1 - expo).clip(lower=0) * tb.reindex(idx).fillna(0)
        return pd.DataFrame(cols)
    walk("#295 levered stock-bond risk parity", (build(1.0), build(1.5)), 0.0005, spy)


def main() -> int:
    benchmark()
    spy, _ = spy_m()
    print(f"walk-forward: monthly pick of best config on trailing 36 months; OOS 2016-01..2026-10 (halves split 2021-05); PASS = both halves and "
          f"costs x1.5 CAGR >= {BAR}% and worst drawdown no worse than SPY's over the same months\n")
    for f in (p292, p293, p294, p295):
        try:
            f(spy)
        except Exception as e:  # noqa: BLE001
            print(f"{f.__name__}: data problem -> not testable ({type(e).__name__}: {e})\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())

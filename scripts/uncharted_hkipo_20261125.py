"""#391 U-T7: Hong Kong IPO one-lot applications (docs/PREREG_UNCHARTED_20261125.md).

    uv run python -m scripts.uncharted_hkipo_20261125 | tee docs/jx_runs/uncharted_hkipo_20261125.txt
Reads data/public/uncharted_391_hkipo_html.json (Actions job u391hkipo; AASTOCKS "Listed IPOs" table pages).
Rule A: one lot in every IPO with cash; EV per IPO = one-lot success rate x lot value x first-day return - HK$100.
"""
from __future__ import annotations

import html
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

PUB = Path(__file__).resolve().parent.parent / "data" / "public"
FEE_HKD, HKD_USD = 100.0, 7.8
START, END = pd.Timestamp("2023-01-01"), pd.Timestamp("2026-10-31")
NUM = r"([\d,]+(?:\.\d+)?|N/A|Under-Sub\.)"
ROW = re.compile(
    r"\| ([^|]+?) \| \| \| (\d{5})\.HK \| \| \| (?:Sink Below Listing Price \| \| \| \| )?(\d{4}/\d{2}/\d{2}) \| \| ([\d,]+) \| \| ([^|]+?) \| \| "
    + NUM + r" \| \| " + NUM + r" \| \| " + NUM + r" \| \| ([^|]+?) \| \| ([\d.]+%|N/A) \| \| " + NUM + r" \| \| \| ([+-]?[\d.]+%|N/A)")


def num(x):
    try:
        return float(str(x).replace(",", "").rstrip("%"))
    except ValueError:
        return np.nan


def parse(pages):
    rows = []
    for h in pages:
        txt = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " | ", h)))
        for m in ROW.finditer(txt):
            name, code, date, lot, _mcap, offer, listing, oversub, _applied, onelot, _last, debut = m.groups()
            rows.append({"name": name.strip(), "code": code, "date": pd.Timestamp(date.replace("/", "-")), "lot": num(lot),
                         "offer": num(offer), "listing": num(listing), "oversub": -1.0 if oversub == "Under-Sub." else num(oversub),
                         "p_onelot": num(onelot) / 100, "debut": num(debut) / 100})
    return pd.DataFrame(rows).drop_duplicates("code")


def main():
    print("===== #391 U-T7 Hong Kong IPO one-lot applications (AASTOCKS listed-IPO table)")
    d = json.loads((PUB / "uncharted_391_hkipo_html.json").read_text())
    t = parse(d["aastocks"])
    print(f"  IPOs parsed: {len(t)}; listing dates {t['date'].min().date()}..{t['date'].max().date()}")
    w = t[(t["date"] >= START) & (t["date"] <= END)].copy()
    have = w.dropna(subset=["lot", "offer", "p_onelot", "debut"])
    have = have[have["offer"] > 0]
    print(f"  in window {START.date()}..{END.date()}: {len(w)}; with all fields: {len(have)} (missing: {len(w) - len(have)})")
    if (w["date"].min() > START + pd.Timedelta(days=60)):
        print(f"  NOTE: the table only reaches back to {w['date'].min().date()}; earlier IPOs are not in the fetched pages")
    have["lot_hkd"] = have["lot"] * have["offer"]
    have["ev_hkd"] = have["p_onelot"] * have["lot_hkd"] * have["debut"] - FEE_HKD
    have["year"] = have["date"].dt.year
    print(f"  per IPO: median lot value HK${have['lot_hkd'].median():,.0f}; median one-lot success {have['p_onelot'].median():.0%}; "
          f"mean first-day return {have['debut'].mean():.1%} (median {have['debut'].median():.1%}); share up on day one "
          f"{(have['debut'] > 0).mean():.0%}")
    yrs = ((min(have["date"].max(), END) - max(have["date"].min(), START)).days + 1) / 365
    tot = have["ev_hkd"].sum()
    print(f"  Rule A (one lot, every IPO): {len(have)} IPOs over {yrs:.2f} yr; EV HK${tot:,.0f} -> US${tot / HKD_USD / yrs:,.0f}/yr per identity; "
          f"mean EV per IPO HK${have['ev_hkd'].mean():,.0f}")
    for y, g in have.groupby("year"):
        print(f"    {y}: IPOs {len(g)}; EV HK${g['ev_hkd'].sum():,.0f} (US${g['ev_hkd'].sum() / HKD_USD:,.0f}); mean debut {g['debut'].mean():.1%}; "
              f"median one-lot {g['p_onelot'].median():.0%}")
    hot = have[have["oversub"] >= 100]
    print(f"  Rule B (context, look-ahead: final oversubscription >= 100x): {len(hot)} IPOs; EV HK${hot['ev_hkd'].sum():,.0f} -> "
          f"US${hot['ev_hkd'].sum() / HKD_USD / yrs:,.0f}/yr; mean debut {hot['debut'].mean():.1%}; median one-lot {hot['p_onelot'].median():.0%}")
    cold = have[(have["oversub"] < 100)]
    print(f"    the rest (< 100x or undersubscribed): {len(cold)} IPOs; EV HK${cold['ev_hkd'].sum():,.0f}; mean debut {cold['debut'].mean():.1%}")
    top = have.sort_values("ev_hkd", ascending=False)
    print("  largest EV contributions:")
    for _, r in top.head(8).iterrows():
        print(f"    {r['date'].date()} {r['name'][:22]:22s} lot HK${r['lot_hkd']:,.0f} one-lot {r['p_onelot']:.1%} debut {r['debut']:+.1%} "
              f"EV HK${r['ev_hkd']:,.0f}")
    share_top5 = top["ev_hkd"].head(5).sum() / tot if tot > 0 else np.nan
    print(f"  share of total EV from the top 5 IPOs: {share_top5:.0%}")
    per_yr = tot / HKD_USD / yrs
    kill = len(have) < 30 or per_yr < 1000
    print(f"  STAGE 1 VERDICT: {'KILL (' + ('fewer than 30 IPOs' if len(have) < 30 else 'Rule A EV < US$1,000/yr') + ')' if kill else 'survives (kill-only)'}")


if __name__ == "__main__":
    main()

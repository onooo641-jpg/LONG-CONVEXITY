"""#386 U-T4: exchange delisting announcements -> hedged 7-day short on Hyperliquid (docs/PREREG_UNCHARTED_20261125.md).

    uv run python -m scripts.uncharted_tags_20261125 | tee docs/jx_runs/uncharted_tags_20261125.txt
Reads data/public/uncharted_386_binance.json (Binance "Delisting" category; Upbit's API refused US servers: not testable),
data/public/uncharted_385_candles.parquet (Hyperliquid daily candles) and data/public/hl_funding.parquet (from 2024-01; zero before).
Events fixed before returns were computed: primary = spot token delistings ("Binance Will Delist <tokens> on <date>"); context =
"Binance Futures Will Delist ..." perpetual-contract delistings. A token counts if it has a Hyperliquid perp trading at the time.
Short at the first Hyperliquid daily close after the announcement, 7 days, hedged with an equal BTC long; 0.045% per side per leg + funding.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

PUB = Path(__file__).resolve().parent.parent / "data" / "public"
FEE, HOLD = 0.00045, 7


def tokens(title, futures):
    if futures:
        return [s[:-4] for s in re.findall(r"\b([A-Z0-9]{2,15}USDT)\b", title)]
    m = re.match(r"Binance Will Delist (.+?) on \d{4}-\d{2}-\d{2}", title)
    if not m:
        return []
    return [t.strip() for t in re.split(r",|&| and ", m.group(1)) if re.fullmatch(r"[A-Z0-9]{2,12}", t.strip())]


def main():
    print("===== #386 U-T4 delisting announcements -> hedged 7-day short on Hyperliquid (Binance; Upbit not testable: HTTP 403)")
    ann = json.loads((PUB / "uncharted_386_binance.json").read_text())
    cd = pd.read_parquet(PUB / "uncharted_385_candles.parquet")
    cd["day"] = pd.to_datetime(cd["t"], unit="ms", utc=True).dt.normalize()
    C = cd.drop_duplicates(["coin", "day"]).pivot(index="day", columns="coin", values="c").sort_index()
    fu = pd.read_parquet(PUB / "hl_funding.parquet")
    fu["day"] = pd.to_datetime(fu["time"], unit="ms", utc=True).dt.normalize()
    F = fu.groupby(["day", "coin"])["rate"].sum().unstack()
    print(f"  announcements fetched: {len(ann)}; Hyperliquid perps with candles: {C.shape[1]}; funding coins: {F.shape[1]}")
    for label, fut in (("PRIMARY spot token delistings", False), ("CONTEXT futures-contract delistings", True)):
        rows = []
        for a in ann:
            title = a["title"]
            if fut != title.startswith("Binance Futures Will Delist"):
                continue
            if not fut and not title.startswith("Binance Will Delist"):
                continue
            t_ann = pd.Timestamp(int(a["releaseDate"]), unit="ms", tz="UTC")
            entry_day = t_ann.normalize()  # close of the announcement day = first daily close after the announcement
            for tok in tokens(title, fut):
                coin = tok if tok in C.columns else ("k" + tok[4:] if tok.startswith("1000") and "k" + tok[4:] in C.columns else None)
                if coin is None or entry_day not in C.index:
                    continue
                exit_day = entry_day + pd.Timedelta(days=HOLD)
                if exit_day not in C.index:
                    continue
                p0, p1 = C.at[entry_day, coin], C.at[exit_day, coin]
                b0, b1 = C.at[entry_day, "BTC"], C.at[exit_day, "BTC"]
                if not (p0 > 0 and p1 > 0):
                    continue
                win = F.loc[entry_day + pd.Timedelta(days=1):exit_day] if len(F) else pd.DataFrame()
                f_s = float(win[coin].sum()) if coin in win else 0.0
                f_b = float(win["BTC"].sum()) if "BTC" in win else 0.0
                ret = -(p1 / p0 - 1) + (b1 / b0 - 1) + f_s - f_b - 4 * FEE
                rows.append({"date": entry_day.date(), "coin": coin, "short_leg": -(p1 / p0 - 1), "btc_leg": b1 / b0 - 1, "ret": ret,
                             "title": title[:70]})
        t = pd.DataFrame(rows).drop_duplicates(["date", "coin"]) if rows else pd.DataFrame()
        print(f"\n  {label}: events with a Hyperliquid perp {len(t)}")
        if t.empty:
            continue
        r = t["ret"]
        n = len(r)
        tstat = r.mean() / (r.std(ddof=1) / np.sqrt(n)) if n > 1 else np.nan
        print(f"    mean hedged 7-day return {r.mean():.2%} (median {r.median():.2%}, t {tstat:.2f}, win {(r > 0).mean():.0%}); "
              f"worst {r.min():.1%}, best {r.max():.1%}")
        print(t.sort_values("date").to_string(index=False, float_format=lambda x: f"{x:7.3f}"))
        if not fut:
            if n < 15:
                print("  STAGE 1 VERDICT: not testable (fewer than 15 events)")
            else:
                kill = r.mean() < 0.01 or tstat < 1
                print(f"  STAGE 1 VERDICT: {'KILL (mean < 1% or t < 1)' if kill else 'survives (kill-only)'}")


if __name__ == "__main__":
    main()

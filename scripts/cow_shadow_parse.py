"""#366: parse the shadow-run logs on Actions and look up the production solutions for the same auctions.

    uv run python scripts/cow_shadow_parse.py <run_id>
Reads logs/{autopilot,driver,solvers}.log, logs/digest.txt, logs/params.txt. Writes data/public/cowshadow_<run_id>.parquet and
docs/jx_runs/cow_shadow_run_<run_id>.txt.
"""
from __future__ import annotations

import json
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
LOGS = ROOT / "logs"
API = "https://api.cow.fi/mainnet/api/v2/solver_competition/"


def num(s):
    if s is None:
        return None
    s = str(s)
    h = re.search(r"0x[0-9a-fA-F]+", s)
    if h:
        return int(h.group(0), 16)
    d = re.findall(r"\d+", s)
    return int(max(d, key=len)) if d else None


def auction_id(rec, raw):
    for sp in ([rec.get("span")] if isinstance(rec.get("span"), dict) else []) + list(rec.get("spans") or []):
        if isinstance(sp, dict):
            for k in ("auction.id", "auction_id", "id"):
                if k in sp and (sp.get("name") == "auction" or k != "id"):
                    return num(sp[k])
    m = re.search(r"auction[._]id[\"=:\s]+(\d+)", raw)
    return int(m.group(1)) if m else None


def get(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "long-convexity-research/1.0", "Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, None
    except Exception:  # noqa: BLE001
        return -1, None


def main(run_id):
    out_txt = ROOT / "docs" / "jx_runs" / f"cow_shadow_run_{run_id}.txt"
    lines = []
    for f in ("params.txt", "digest.txt"):
        p = LOGS / f
        lines.append(f"{f}: {p.read_text().strip() if p.exists() else 'missing'}")
    seen, summ = set(), {}
    ap = LOGS / "autopilot.log"
    raw_lines = ap.read_text(errors="replace").splitlines() if ap.exists() else []
    for raw in raw_lines:
        try:
            rec = json.loads(raw)
        except Exception:  # noqa: BLE001
            rec = {}
        f = rec.get("fields") or {}
        msg = f.get("message") or ("solution summary" if "solution summary" in raw else ("solving" if '"solving"' in raw else ""))
        aid = auction_id(rec, raw)
        if aid is None:
            continue
        if msg == "solving":
            seen.add(aid)
        elif msg == "solution summary":
            seen.add(aid)
            summ[aid] = {"ours": num(f.get("reward", re.search(r"reward[=:\"\s]+([^,}\s]+)", raw).group(1) if "reward" in raw else None)),
                         "ours_win": str(f.get("is_winner", "")).lower() == "true"}
    lines.append(f"autopilot log lines {len(raw_lines)}; auctions seen {len(seen)}; auctions with a baseline solution {len(summ)}")
    rows, t0 = [], time.time()
    for aid in sorted(seen)[:2500]:
        st, d = get(API + str(aid))
        sols = (d or {}).get("solutions") or []
        sc = [num(s.get("score")) or 0 for s in sols if not s.get("filteredOut")]
        rows.append({"auction": aid, "ours": (summ.get(aid) or {}).get("ours"), "ours_win": (summ.get(aid) or {}).get("ours_win", False),
                     "prod_status": st, "prod_n": len(sols), "prod_best": max(sc) if sc else None})
        time.sleep(0.1)
    df = pd.DataFrame(rows)
    if len(df):
        df["ours"] = pd.to_numeric(df["ours"], errors="coerce").astype(float)
        df["prod_best"] = pd.to_numeric(df["prod_best"], errors="coerce").astype(float)
        (ROOT / "data" / "public").mkdir(parents=True, exist_ok=True)
        df.to_parquet(ROOT / "data" / "public" / f"cowshadow_{run_id}.parquet", index=False)
        lines.append(f"production lookups {len(df)} in {time.time() - t0:.0f}s; with production data {int(df['prod_best'].notna().sum())}")
    for c in ("solvers", "driver", "autopilot"):
        p = LOGS / f"{c}.log"
        L = p.read_text(errors="replace").splitlines() if p.exists() else []
        bad = [x for x in L if re.search(r"\b(WARN|ERROR|panicked|error)\b", x)]
        uniq = []
        for x in bad:
            k = re.sub(r"\d+", "#", x)[:160]
            if k not in {re.sub(r"\d+", "#", u)[:160] for u in uniq}:
                uniq.append(x)
        lines.append(f"===== {c}: {len(L)} lines, {len(bad)} warn/error lines; first 25 lines:")
        lines += [x[:400] for x in L[:25]]
        lines.append(f"----- {c}: up to 25 distinct warn/error lines:")
        lines += [x[:400] for x in uniq[:25]]
        lines.append(f"----- {c}: last 15 lines:")
        lines += [x[:400] for x in L[-15:]]
    out_txt.parent.mkdir(parents=True, exist_ok=True)
    out_txt.write_text("\n".join(lines) + "\n")
    print("\n".join(lines[:6]))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "local")

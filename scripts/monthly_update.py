"""The monthly update, end to end. Run by .github/workflows/monthly.yml.

    DATABENTO_API_KEY=... uv run python scripts/monthly_update.py
    uv run python scripts/monthly_update.py --skip-fetch     # no key: re-check only

1. ingest what is in data/raw
2. fetch from (last stored day - 2) to today from Databento -- the two days
   of overlap are re-checked bar for bar by fetch_databento.py, and the fetch
   aborts before downloading if the quote is over --max-cost-usd
3. ingest again
4. append to the forward log (scripts/forward_log.py; append-only)
5. run the tests and the three pre-purchase checks
6. write docs/jx_runs/monthly_latest.txt -- what changed, in one file

Any failing step stops the run with a non-zero exit, so a broken month shows
up as a red run on GitHub rather than as a quiet commit of bad numbers.
"""

from __future__ import annotations

import argparse
import datetime as dt
import pathlib
import subprocess
import sys

import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "jx_runs" / "monthly_latest.txt"
PY = [sys.executable]


def run(cmd: list[str], log: list[str], title: str) -> str:
    print(f"\n=== {title}\n$ {' '.join(cmd)}", flush=True)
    p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    out = (p.stdout + p.stderr).strip()
    print(out)
    log.append(f"=== {title}\n$ {' '.join(cmd)}\n{out}\n")
    if p.returncode != 0:
        OUT.write_text("\n".join(log) + f"\nFAILED at: {title} (exit {p.returncode})\n")
        raise SystemExit(f"step failed: {title}")
    return out


def last_stored_day() -> dt.date:
    df = pd.read_parquet(ROOT / "data" / "processed" / "nq_1m.parquet", columns=["ts"])
    return df["ts"].max().date()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--skip-fetch", action="store_true")
    ap.add_argument("--max-cost-usd", type=float, default=1.00)
    args = ap.parse_args(argv)

    log = [f"monthly update, run {dt.datetime.now(dt.timezone.utc):%Y-%m-%d %H:%M} UTC\n"]
    run(PY + ["scripts/ingest.py"], log, "ingest stored shards")
    before = last_stored_day()

    if not args.skip_fetch:
        start = before - dt.timedelta(days=2)
        end = dt.datetime.now(dt.timezone.utc).date()
        if end > start:
            out = f"data/raw/NQ_v_0_1m_{start:%Y%m%d}_{end:%Y%m%d}.parquet"
            run(PY + ["scripts/fetch_databento.py", "--start", f"{start}",
                      "--end", f"{end}", "--out", out,
                      "--max-cost-usd", f"{args.max_cost_usd}"],
                log, f"fetch {start} -> {end}")
            run(PY + ["scripts/ingest.py"], log, "ingest with the new shard")

    after = last_stored_day()
    log.append(f"data: last stored day {before} -> {after}\n")
    run(PY + ["scripts/forward_log.py", "--restate-risk", "900"], log, "forward log")
    run(PY + ["-m", "pytest", "-q", "-o", "addopts="], log, "tests")
    run(PY + ["scripts/jx_checks.py", "--skip-strategy"], log,
        "three checks (current rules)")
    OUT.write_text("\n".join(log))
    print(f"\nwrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

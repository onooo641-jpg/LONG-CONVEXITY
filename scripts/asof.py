"""Run any script as if the data stopped at a given moment.

    uv run python scripts/asof.py 2026-09-08T05:27Z scripts/simulator_inputs.py
    uv run python scripts/asof.py 2026-09-08T05:27Z scripts/account_lifetime.py --orders ...

Figures in the docs were computed on whatever data existed that day, and the
data has been appended to since. Re-running a script today answers a different
question from the one the doc answered. This truncates the processed 1m and 5m
files to bars strictly before ``cutoff``, writes them to
``data/processed/asof_<cutoff>/``, points ``ict.data.PROCESSED_DIR`` there, and
runs the script unchanged.

``2026-09-08T05:27Z`` is the end of ``NQ_v_0_1m_2026_fwd.parquet``, the last
shard that existed before the September pull (94772e9). Every figure written
between 2026-09-08 and 2026-09-29 was computed on data that stopped there.
"""

from __future__ import annotations

import runpy
import sys

import pandas as pd

from ict import data as D


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    cutoff = pd.Timestamp(sys.argv[1])
    cutoff = cutoff.tz_localize("UTC") if cutoff.tzinfo is None else cutoff.tz_convert("UTC")
    script, rest = sys.argv[2], sys.argv[3:]

    tag = cutoff.strftime("%Y%m%dT%H%M")
    out = D.PROCESSED_DIR / f"asof_{tag}"
    out.mkdir(parents=True, exist_ok=True)
    for tf in ("1m", "5m"):
        dest = out / f"nq_{tf}.parquet"
        if not dest.exists():
            frame = pd.read_parquet(D.PROCESSED_DIR / f"nq_{tf}.parquet")
            frame[frame["ts"] < cutoff].to_parquet(dest, compression="zstd", index=False)
    D.PROCESSED_DIR = out
    print(f"[asof] data truncated to ts < {cutoff}  ({out})", file=sys.stderr)

    sys.argv = [script, *rest]
    sys.path.insert(0, str(D.REPO_ROOT / "scripts"))
    runpy.run_path(script, run_name="__main__")
    return 0


if __name__ == "__main__":
    sys.exit(main())

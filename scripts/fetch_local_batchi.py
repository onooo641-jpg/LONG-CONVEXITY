"""Batch I data that GitHub's servers were throttled on, fetched from the session instead (docs/PREREG_BATCH_I_20261126.md).

Resumable: finished days are cached under data/public/_cache_duka/ and skipped on re-run. Order: Solana epochs, AUDUSD month-end days
(#486), XAUUSD (#480), XAGUSD, GBPUSD, USDJPY, AUDUSD, EURUSD (#478/#479). Output files match job `ubatchi`'s.

    uv run python -m scripts.fetch_local_batchi
"""
from __future__ import annotations

import json
import lzma
import struct
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pandas as pd

PUB = Path(__file__).resolve().parent.parent / "data" / "public"
CACHE = PUB / "_cache_duka"
DIV = {"EURUSD": 1e5, "GBPUSD": 1e5, "AUDUSD": 1e5, "USDJPY": 1e3, "XAUUSD": 1e3, "XAGUSD": 1e3}
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36"}


def sol_epochs():
    out = PUB / "batchi_sol_epochs.parquet"
    have = pd.read_parquet(out) if out.exists() else pd.DataFrame(columns=["epoch", "slot", "t"])

    def rpc(method, params=None):
        body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params or []}).encode()
        for k in range(4):
            try:
                req = urllib.request.Request("https://api.mainnet-beta.solana.com", data=body, headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(req, timeout=30) as r:
                    return json.loads(r.read().decode())
            except Exception:  # noqa: BLE001
                time.sleep(2 * (k + 1))
        return {}
    cur = (rpc("getEpochInfo").get("result") or {}).get("epoch") or 0
    done = set(have["epoch"].astype(int))
    rows = have.values.tolist()
    for e in range(150, int(cur) + 1):
        if e in done:
            continue
        for k in range(0, 60):
            bt = rpc("getBlockTime", [e * 432000 + k]).get("result")
            if bt:
                rows.append([e, e * 432000 + k, int(bt)])
                break
            time.sleep(0.1)
        time.sleep(0.15)
    df = pd.DataFrame(rows, columns=["epoch", "slot", "t"]).astype(int).sort_values("epoch")
    df.to_parquet(out)
    print(f"  solana epochs {len(df)} ({e if cur else 0} current)", flush=True)


def duka_day(ins, dd):
    CACHE.mkdir(parents=True, exist_ok=True)
    f = CACHE / f"{ins}_{dd:%Y%m%d}.json"
    if f.exists():
        return json.loads(f.read_text())
    url = f"https://datafeed.dukascopy.com/datafeed/{ins}/{dd.year}/{dd.month - 1:02d}/{dd.day:02d}/BID_candles_min_1.bi5"
    raw, st = b"", None
    for k in range(5):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=90) as r:
                raw, st = r.read(), r.status
                break
        except urllib.error.HTTPError as e:
            st = e.code
            if e.code == 404:
                break
            time.sleep(10 * (k + 1))
        except Exception:  # noqa: BLE001
            time.sleep(10 * (k + 1))
    if st not in (200, 404):
        return None  # not cached: retried on the next run
    out = []
    if raw:
        try:
            b = lzma.decompress(raw)
            for i in range(0, len(b) - 23, 24):
                sec, f1, f2, f3, f4, _ = struct.unpack(">IIIIIf", b[i:i + 24])
                mm = sec // 60
                if 9 * 60 <= mm < 22 * 60 and (mm + 1) % 5 == 0:
                    out.append([ins, f"{dd:%Y-%m-%d}", int(sec), f1 / DIV[ins], f2 / DIV[ins], f3 / DIV[ins], f4 / DIV[ins]])
        except Exception:  # noqa: BLE001
            return None
    f.write_text(json.dumps(out))
    return out


def duka(ins, days, name, workers=6):
    t0 = time.time()
    rows, miss = [], 0
    with ThreadPoolExecutor(workers) as ex:
        for i, res in enumerate(ex.map(lambda d: duka_day(ins, d), days)):
            if res is None:
                miss += 1
            else:
                rows += res
            if i % 250 == 0:
                print(f"  {ins} {i}/{len(days)} ({time.time() - t0:.0f}s, missing {miss})", flush=True)
    old = PUB / name
    df = pd.DataFrame(rows, columns=["ins", "day", "sec", "f1", "f2", "f3", "f4"])
    if old.exists():
        df = pd.concat([pd.read_parquet(old), df]).drop_duplicates(["day", "sec"])
    df.sort_values(["day", "sec"]).to_parquet(old)
    print(f"  wrote {name}: days {df['day'].nunique()}, rows {len(df)}, still missing {miss}", flush=True)


def main():
    sol_epochs()
    weekdays = [d for d in pd.date_range("2012-01-02", "2026-10-31", freq="D") if d.weekday() < 5]
    month_end = sorted({max(g) for _, g in pd.Series(weekdays).groupby(pd.Series(weekdays).dt.to_period("M"))})
    duka("AUDUSD", month_end, "batchi_duka_audusd.parquet")
    for ins in ("XAUUSD", "XAGUSD", "GBPUSD", "USDJPY", "AUDUSD", "EURUSD"):
        duka(ins, weekdays, f"batchi_duka_{ins.lower()}.parquet")


if __name__ == "__main__":
    main()

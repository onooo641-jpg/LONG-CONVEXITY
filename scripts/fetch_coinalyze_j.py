"""Batch J data (docs/PREREG_BATCH_J_20261126.md): Coinalyze daily OI (base units) and liquidations (USD) for the 40 batchd alts and
the 110 unseen perps on Binance, plus Bybit OI, liquidations and OHLCV for the same bases. Key from env COINALYZE_API_KEY (never stored).

    COINALYZE_API_KEY=... uv run python -m scripts.fetch_coinalyze_j
"""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path

import pandas as pd

PUB = Path(__file__).resolve().parent.parent / "data" / "public"
FROM = int(pd.Timestamp("2020-01-01", tz="UTC").timestamp())
TO = int(pd.Timestamp("2026-11-01", tz="UTC").timestamp())


def call(path, key):
    for k in range(5):
        try:
            req = urllib.request.Request("https://api.coinalyze.net/v1/" + path, headers={"api_key": key, "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=90) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(float(e.headers.get("Retry-After") or 30) + 1)
                continue
            if e.code in (400, 401, 404):
                return []
            time.sleep(5 * (k + 1))
        except Exception:  # noqa: BLE001
            time.sleep(5 * (k + 1))
    return []


def pull(endpoint, symbols, key, extra=""):
    rows = []
    for i in range(0, len(symbols), 20):
        chunk = symbols[i:i + 20]
        d = call(f"{endpoint}?symbols={','.join(chunk)}&interval=daily&from={FROM}&to={TO}{extra}", key)
        for s in d or []:
            for h in s.get("history") or []:
                rows.append({"symbol": s["symbol"], **h})
        time.sleep(len(chunk) * 1.6)  # ~40 calls/min: each symbol counts as one call
    return pd.DataFrame(rows)


def main():
    key = os.environ.get("COINALYZE_API_KEY", "")
    assert key, "set COINALYZE_API_KEY"
    m = pd.read_parquet(PUB / "coinalyze_future_markets.parquet")
    have = set(m["symbol"])
    alts = sorted(pd.read_parquet(PUB / "batchd_alts_1h.parquet")["sym"].unique())
    unseen = sorted(pd.read_parquet(PUB / "batchh2_unseen_funding.parquet")["sym"].unique())
    bases = [s[:-4] for s in alts + unseen]
    bn = [f"{b}USDT_PERP.A" for b in bases if f"{b}USDT_PERP.A" in have]
    by = [f"{b}USDT.6" for b in bases if f"{b}USDT.6" in have]
    print(f"  Binance symbols {len(bn)} of {len(bases)}; Bybit {len(by)}", flush=True)
    for name, ep, syms, extra in (("cz_oi_binance", "open-interest-history", bn, ""), ("cz_liq_binance", "liquidation-history", bn, "&convert_to_usd=true"),
                                  ("cz_oi_bybit", "open-interest-history", by, ""), ("cz_liq_bybit", "liquidation-history", by, "&convert_to_usd=true"),
                                  ("cz_ohlcv_bybit", "ohlcv-history", by, "")):
        if (PUB / f"batchj_{name}.parquet").exists():
            continue  # resumable
        t0 = time.time()
        df = pull(ep, syms, key, extra)
        df.to_parquet(PUB / f"batchj_{name}.parquet")
        print(f"  {name}: {df['symbol'].nunique() if len(df) else 0} symbols, {len(df)} rows ({time.time() - t0:.0f}s)", flush=True)


if __name__ == "__main__":
    main()

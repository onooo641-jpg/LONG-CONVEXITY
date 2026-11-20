"""Shared check that keeps engines on different markets from hedging each other.

Topstep, Lucid and MyFundedFutures prohibit hedging across a trader's accounts,
including opposite positions in correlated contracts. When NQ, ES and YM run in
separate accounts (docs/PREREG_MARKETMIX_20261120.md), their signals sometimes
point opposite ways at the same time -- about 20 times a year in 2016-26. Every
engine on this computer therefore claims its direction here before entering, and
an entry opposite to a live claim from another market is not placed.

A claim counts from the moment the order is sent (a resting limit can fill) until
the engine finishes its day; it also expires on its own at ``expires_at``, so a
crashed engine cannot block the others past the flat time.

The file is plain JSON, guarded by a lock file created with O_EXCL, which works
the same on Windows and Linux.
"""

from __future__ import annotations

import json
import os
import pathlib
import time
from contextlib import contextmanager

import pandas as pd

LOCK_TIMEOUT_S = 10.0


class HedgeRegistryError(RuntimeError):
    """The registry cannot be read; callers must treat that as 'do not enter'."""


class HedgeRegistry:
    def __init__(self, path: str | pathlib.Path) -> None:
        self.path = pathlib.Path(path)
        self.lock = self.path.with_suffix(self.path.suffix + ".lock")
        self.path.parent.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def _locked(self):
        deadline = time.monotonic() + LOCK_TIMEOUT_S
        while True:
            try:
                fd = os.open(self.lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                break
            except FileExistsError:
                # A lock older than the timeout belongs to a process that died
                # holding it; waiting on it forever would block every engine.
                try:
                    if time.time() - self.lock.stat().st_mtime > LOCK_TIMEOUT_S:
                        self.lock.unlink(missing_ok=True)
                        continue
                except FileNotFoundError:
                    continue
                if time.monotonic() > deadline:
                    raise TimeoutError(f"hedge registry lock {self.lock} is held")
                time.sleep(0.05)
        try:
            yield
        finally:
            os.close(fd)
            self.lock.unlink(missing_ok=True)

    def _read(self) -> list[dict]:
        if not self.path.exists():
            return []
        try:
            return json.loads(self.path.read_text(encoding="utf-8") or "[]")
        except json.JSONDecodeError as exc:
            # Unreadable means unknown, and unknown must not read as "nothing
            # open". Refuse; the engine skips the entry and journals why.
            raise HedgeRegistryError(f"{self.path} is not valid JSON: {exc}") from exc

    def _write(self, rows: list[dict]) -> None:
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(rows, indent=1), encoding="utf-8")
        os.replace(tmp, self.path)

    @staticmethod
    def _live(rows: list[dict], now: pd.Timestamp) -> list[dict]:
        return [r for r in rows if pd.Timestamp(r["expires_at"]) > now]

    def claim(self, market: str, direction: int, key: str, now: pd.Timestamp,
              expires_at: pd.Timestamp) -> dict | None:
        """Atomically: return the conflicting claim if any, else record ours and return None."""
        with self._locked():
            rows = self._live(self._read(), now)
            for r in rows:
                if r["market"] != market and int(r["direction"]) != int(direction):
                    self._write(rows)
                    return r
            rows = [r for r in rows if not (r["market"] == market and r["key"] == key)]
            rows.append({"market": market, "direction": int(direction), "key": key,
                         "claimed_at": now.isoformat(), "expires_at": expires_at.isoformat()})
            self._write(rows)
            return None

    def release(self, market: str, key: str | None = None) -> None:
        """Drop this market's claim (all of them when key is None)."""
        with self._locked():
            rows = [r for r in self._read()
                    if not (r["market"] == market and (key is None or r["key"] == key))]
            self._write(rows)

    def claims(self, now: pd.Timestamp) -> list[dict]:
        with self._locked():
            return self._live(self._read(), now)

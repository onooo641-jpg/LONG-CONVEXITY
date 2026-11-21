"""Uptime alert for the liquidation shadow watcher (PREREG_LIQ_SHADOW addendum 4c).

Run by .github/workflows/liq_alert.yml every 30 minutes. Opens one GitHub issue "liq watcher down: <chain>" per chain whose last committed
heartbeat is older than 60 minutes (deduped by title) and closes it again when the chain is back. Needs GH_TOKEN (GITHUB_TOKEN, issues: write).
"""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
THRESHOLD_MIN = 60.0
END_DATE = "2027-06-30"


def enabled_chains():
    f = ROOT / ".github" / "liq_shadow_chains.txt"
    return [x.strip() for x in f.read_text().splitlines() if x.strip() and not x.strip().startswith("#")] if f.exists() else []


def minutes_since_heartbeat(chain, now):
    f = ROOT / "data" / "shadow" / chain / "uptime.jsonl"
    if not f.exists():
        return None
    last = None
    for line in f.read_text().splitlines()[-400:]:
        try:
            r = json.loads(line)
        except json.JSONDecodeError:
            continue
        if r.get("ver") == 2:
            last = max(last or 0.0, r["wall"])
    return None if last is None else (now - last) / 60.0


def decide(status, open_titles, threshold=THRESHOLD_MIN):
    """status: {chain: minutes since last heartbeat or None (no data yet: no alert)}; open_titles: set of open issue titles.
    returns [('create', title), ('close', title)]; at most one open issue per chain."""
    acts = []
    for chain, m in sorted(status.items()):
        title = f"liq watcher down: {chain}"
        if m is None:
            continue
        down = m > threshold
        if down and title not in open_titles:
            acts.append(("create", title))
        elif not down and title in open_titles:
            acts.append(("close", title))
    return acts


def gh(*args):
    return subprocess.run(["gh", *args], capture_output=True, text=True, check=False)


def main():
    now = time.time()
    if time.strftime("%Y-%m-%d", time.gmtime(now)) > END_DATE:
        print("past end date: no alerts")
        return 0
    status = {c: minutes_since_heartbeat(c, now) for c in enabled_chains()}
    print("minutes since heartbeat:", {c: (None if m is None else round(m, 1)) for c, m in status.items()})
    r = gh("issue", "list", "--state", "open", "--limit", "100", "--json", "title,number")
    issues = json.loads(r.stdout) if r.returncode == 0 and r.stdout.strip() else []
    open_by_title = {i["title"]: i["number"] for i in issues}
    for act, title in decide(status, set(open_by_title)):
        if act == "create":
            body = ("The liquidation shadow watcher has not committed a heartbeat for more than 60 minutes (PREREG_LIQ_SHADOW_20261121 addendum 4c). "
                    "Check the 'liquidation shadow' workflow runs; restart by changing .github/liq_shadow_request.txt if the cron chain stopped.")
            res = gh("issue", "create", "--title", title, "--body", body)
            print("create", title, res.returncode, res.stderr.strip()[:200])
        else:
            res = gh("issue", "close", str(open_by_title[title]), "--comment", "Watcher heartbeat is back; closing.")
            print("close", title, res.returncode, res.stderr.strip()[:200])
    return 0


if __name__ == "__main__":
    sys.exit(main())

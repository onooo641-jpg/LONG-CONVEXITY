"""CRASH WINDOW report for the liquidation shadow watcher (PREREG_LIQ_SHADOW addendum 4d). Separate from, and never overriding, the registered verdict.

    python3 scripts/liq_crash_window.py [--write]

Needs data/shadow/verdict.json {"verdict_date": "YYYY-MM-DD", "verdict": "..."} written when the registered verdict is published.
CRASH WINDOW = first rolling 30 days after the verdict date with gross bonus > USD 1,000,000 across the five venues (all logged LiquidationCall events).
--write also writes data/shadow/crash_window_done when the window is complete or 2027-06-30 has passed (stops the cron watcher).
"""
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import liq_shadow_summary as sm  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DAY = 86400
GROSS_MIN = 1_000_000.0
END_DATE = "2027-06-30"


def find_window(events, verdict_ts, now):
    """events: [(ts, bonus_usd)]. Earliest day d >= verdict_ts (UTC day starts) whose [d, d+30d) gross, counted up to `now`, exceeds GROSS_MIN.
    returns (start, end, state) with state 'none' | 'open' | 'complete'."""
    d = verdict_ts - verdict_ts % DAY
    if d < verdict_ts:
        d += DAY
    evs = sorted(events)
    while d <= now:
        tot = sum(b for t, b in evs if d <= t < min(d + 30 * DAY, now + 1) and b > 0)
        if tot > GROSS_MIN:
            return d, d + 30 * DAY, ("complete" if now >= d + 30 * DAY else "open")
        d += DAY
    return None, None, "none"


def report(data, start, end):
    ev = []
    for c in sm.CHAINS:
        ev += [e for e in sm.match(c, data[c], start) if e["ts"] < end]
    n = len(ev)
    ff = [e for e in ev if e["cls"] == "fire_first"]
    net = sum(e["net"] for e in ff)
    miss = [e for e in ev if e["cls"] != "fire_first"]
    reasons = {}
    for e in miss:
        reasons[e["cls"]] = reasons.get(e["cls"], 0) + 1
    near = [e for e in miss if e["gap_blocks"] is not None and e["gap_blocks"] <= 3]
    pct = 100.0 * len(ff) / max(n, 1)
    near_share = len(near) / max(len(miss), 1)
    worth = pct >= 10.0 and net >= 2000.0
    verdict = "CRASH-WORTHWHILE" if worth else ("CRASH-NOT-WORTHWHILE" + (" (latency-limited: > 50% of misses were within 3 blocks of the winner)" if near_share > 0.5 else ""))
    return dict(n=n, ff=len(ff), pct=pct, net=net, reasons=reasons, near_share=near_share, verdict=verdict)


def main(argv):
    write = "--write" in argv
    now = time.time()
    out_dir = ROOT / "data" / "shadow"
    vf = out_dir / "verdict.json"
    lines = []
    status = "NO VERDICT YET"
    done = time.strftime("%Y-%m-%d", time.gmtime(now)) > END_DATE
    if vf.exists():
        v = json.loads(vf.read_text())
        vts = datetime.strptime(v["verdict_date"], "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp()
        data = sm.load(out_dir)
        events = [(e["ts"], e["bonus_usd"]) for c in sm.CHAINS for e in data[c]["liq"] if "ts" in e and "bonus_usd" in e]
        start, end, status = find_window(events, vts, now)
        lines.append(f"verdict date {v['verdict_date']} ({v.get('verdict')}); events logged since: {len([1 for t, _ in events if t >= vts])}")
        if status == "none":
            lines.append("no crash window yet: no 30-day period after the verdict has gross bonus above USD 1,000,000")
        else:
            r = report(data, start, end)
            s0, s1 = (datetime.fromtimestamp(x, timezone.utc).strftime("%Y-%m-%d") for x in (start, end))
            lines += [f"CRASH WINDOW {s0} .. {s1} ({status})", f"eligible liquidations {r['n']}, fire-first {r['ff']} ({r['pct']:.1f}%), simulated net {r['net']:.2f} USD",
                      f"miss reasons {r['reasons']}; near-miss share of misses {r['near_share']:.2f}", f"REPORT: {r['verdict']}  (never overrides the registered verdict)"]
            done = done or status == "complete"
    print("\n".join([f"STATUS: {status}"] + lines))
    if write:
        (ROOT / "docs" / "jx_runs").mkdir(exist_ok=True)
        (ROOT / "docs" / "jx_runs" / "liq_crash_window.txt").write_text("\n".join([f"STATUS: {status}"] + lines) + "\n")
        if done:
            (out_dir / "crash_window_done").write_text(time.strftime("%Y-%m-%d", time.gmtime(now)) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

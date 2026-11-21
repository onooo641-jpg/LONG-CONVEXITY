"""Liquidation shadow test: matching and GO/KILL evaluation (PREREG_LIQ_SHADOW_20261121). Offline, deterministic.

    uv run python -I scripts/liq_shadow_summary.py [data_dir]

Reads data/shadow/<chain>/{unhealthy,liquidations,uptime}.jsonl, borrowers.json, stats.json.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

CHAINS = ["arbitrum", "base", "avalanche", "polygon", "optimism"]
WEEK = 7 * 86400
BONUS_MIN = 50.0
HB_GAP = 120.0


def rows(p: Path):
    if not p.exists():
        return []
    out = []
    for line in p.read_text().splitlines():
        line = line.strip()
        if line:
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return out


def intervals(up):
    """uptime intervals [(t0, t1)] from start/hb/stop rows; a gap > HB_GAP without a heartbeat ends an interval."""
    iv, cur_s, last = [], None, None
    for r in sorted(up, key=lambda r: r["wall"]):
        t = r["wall"]
        if r["kind"] == "start":
            if cur_s is not None:
                iv.append((cur_s, last))
            cur_s, last = t, t
        elif r["kind"] == "hb":
            if cur_s is None or t - last > HB_GAP:
                if cur_s is not None:
                    iv.append((cur_s, last))
                cur_s = t
            last = t
        elif r["kind"] == "stop":
            if cur_s is not None:
                iv.append((cur_s, t))
            cur_s, last = None, None
    if cur_s is not None:
        iv.append((cur_s, last))
    return iv


def inside(iv, t):
    return any(a <= t <= b for a, b in iv)


def load(d: Path):
    data = {}
    for c in CHAINS:
        cd = d / c
        up = [r for r in rows(cd / "uptime.jsonl") if r.get("ver") == 2]
        bj = cd / "borrowers.json"
        data[c] = dict(unh=[r for r in rows(cd / "unhealthy.jsonl") if r.get("ver") == 2], liq=rows(cd / "liquidations.jsonl"), up=up, iv=intervals(up),
                       tracked=(set(json.loads(bj.read_text())) if bj.exists() else set())
                       | ({x.strip() for x in (cd / "borrowers_new.jsonl").read_text().splitlines() if x.strip()} if (cd / "borrowers_new.jsonl").exists() else set()),
                       stats=json.loads((cd / "stats.json").read_text()) if (cd / "stats.json").exists() else {})
    return data


def match(chain, dd, start_ts):
    """returns list of eligible events with classification."""
    recs = [r for r in dd["unh"] if not r.get("healed")]
    heals = [r for r in dd["unh"] if r.get("healed")]
    by_user = {}
    for r in recs:
        by_user.setdefault(r["user"], []).append(r)
    for u in by_user:
        by_user[u].sort(key=lambda r: r["wall"])
    heal_by_user = {}
    for h in heals:
        heal_by_user.setdefault(h["user"], []).append(h["wall"])
    used = set()
    out = []
    for ev in sorted(dd["liq"], key=lambda e: (e["block"], e["tx"], e["user"])):
        if "bonus_usd" not in ev or "ts" not in ev:
            continue
        if ev["ts"] < start_ts or not inside(dd["iv"], ev["ts"]) or ev["bonus_usd"] <= BONUS_MIN:
            continue
        cands = [r for r in by_user.get(ev["user"], []) if r["wall"] <= ev["seen_wall"] and id(r) not in used]
        # a record is consumed by the first liquidation of that user after it; heals between record and event void it
        cands = [r for r in cands if not any(r["wall"] < hw <= ev["seen_wall"] for hw in heal_by_user.get(ev["user"], []))]
        rec = cands[-1] if cands else None
        cls, net = None, 0.0
        if rec is None:
            cls = "no_record_in_set" if ev["user"] in dd["tracked"] else "no_record_not_in_set"
        else:
            used.add(id(rec))
            sim = rec.get("sim") or {}
            if rec["n_ready"] + 1 >= ev["block"]:
                cls = "record_too_late"
            elif not sim.get("ok"):
                cls = "sim_no_quote"
            else:
                net = sim["net_before_gas_usd"] - ev["gas_usd"]
                cls = "fire_first" if net > 0 else "sim_net_le0"
        out.append(dict(chain=chain, week=int((ev["ts"] - start_ts) // WEEK), cls=cls, net=net if cls == "fire_first" else 0.0,
                        bonus=ev["bonus_usd"], gap_blocks=(ev["block"] - rec["n_ready"]) if rec else None))
    return out


def evaluate(data):
    firsts = [dd["iv"][0][0] for dd in data.values() if dd["iv"]]
    if len(firsts) < len(CHAINS):
        return None, "not all five venues are being watched yet"
    start_ts = max(firsts)
    events = []
    for c in CHAINS:
        events += match(c, data[c], start_ts)
    return start_ts, events


def main(argv):
    d = Path(argv[0]) if argv else Path(os.environ.get("LIQ_SHADOW_DIR") or Path(__file__).resolve().parent.parent / "data" / "shadow")
    data = load(d)
    start_ts, events = evaluate(data)
    print("== liquidation shadow summary")
    for c in CHAINS:
        dd = data[c]
        up = sum(b - a for a, b in dd["iv"])
        st = dd["stats"]
        print(f"{c:10s} intervals {len(dd['iv']):3d} watched {up/3600:7.1f} h  tracked {len(dd['tracked']):6d}  logged liquidations {len(dd['liq']):6d} "
              f"unhealthy records {len([r for r in dd['unh'] if not r.get('healed')]):5d}  cycles {st.get('cycles')} avg_rpc_ms "
              f"{(st.get('rpc_ms_sum', 0) / max(st.get('rpc_ok', 1), 1)):.0f} rpc_err {st.get('rpc_err')}")
    if start_ts is None:
        print("STATUS: RUNNING (" + events + ")")
        return 0
    last_ts = max([ev["ts"] for dd in data.values() for ev in dd["liq"] if "ts" in ev] + [start_ts])
    weeks_done = int((last_ts - start_ts) // WEEK)
    print(f"start_ts {int(start_ts)}  last event ts {int(last_ts)}  full weeks elapsed {min(weeks_done, 4)}")
    print("\nweek  eligible  fire_first  pct    sim_net_usd   misses: not_in_set in_set_late no_quote net<=0 too_late")
    tot = dict(n=0, f=0, net=0.0)
    wk = {}
    for k in range(4):
        e = [x for x in events if x["week"] == k]
        f = [x for x in e if x["cls"] == "fire_first"]
        cnt = lambda name: len([x for x in e if x["cls"] == name])  # noqa: E731
        net = sum(x["net"] for x in f)
        wk[k] = dict(n=len(e), f=len(f), net=net)
        tot["n"] += len(e)
        tot["f"] += len(f)
        tot["net"] += net
        print(f"{k+1:4d}  {len(e):8d}  {len(f):10d}  {100*len(f)/max(len(e),1):5.1f}  {net:12.2f}   {cnt('no_record_not_in_set'):10d} {cnt('no_record_in_set'):10d} "
              f"{cnt('sim_no_quote'):8d} {cnt('sim_net_le0'):6d} {cnt('record_too_late'):8d}")
    pct = 100 * tot["f"] / max(tot["n"], 1)
    month = tot["net"] * 30.0 / 28.0
    pos_weeks = len([k for k in range(4) if wk[k]["net"] > 0])
    print(f"\ntotal eligible {tot['n']}  fire-first {tot['f']} ({pct:.1f}%)  simulated net {tot['net']:.2f} USD over 4 weeks = {month:.2f} USD/month; positive weeks {pos_weeks}/4")
    print("\nper venue (all weeks): eligible, fire-first, sim net, coverage(user in tracked set), near-misses (record 1-3 blocks too late)")
    for c in CHAINS:
        e = [x for x in events if x["chain"] == c]
        f = [x for x in e if x["cls"] == "fire_first"]
        near = len([x for x in e if x["cls"] == "record_too_late" and x["gap_blocks"] is not None and x["gap_blocks"] <= 3])
        cov = 1 - len([x for x in e if x["cls"] == "no_record_not_in_set"]) / max(len(e), 1)
        print(f"{c:10s} {len(e):6d} {len(f):6d} {sum(x['net'] for x in f):10.2f}  coverage {cov:.2f}  near-miss {near}")
    gaps = {c: sum(b - a for a, b in data[c]["iv"]) / max(last_ts - start_ts, 1) for c in CHAINS}
    print("watched fraction since start:", {c: round(v, 3) for c, v in gaps.items()})
    # verdict (preregistered rules)
    kill_w1 = weeks_done >= 1 and 100 * wk[0]["f"] / max(wk[0]["n"], 1) < 2.0 and wk[0]["net"] < 50.0
    if kill_w1:
        status = "KILLED EARLY (week 1: fire-first < 2% and simulated net < 50 USD)"
    elif weeks_done < 4:
        status = f"RUNNING (week {min(weeks_done + 1, 4)} of 4)"
    else:
        inconclusive = tot["n"] < 200 or any(v < 0.75 for v in gaps.values())
        go = pct >= 10.0 and month >= 500.0 and pos_weeks >= 3
        status = "INCONCLUSIVE (too few events or a venue watched < 75%; extend once by 2 weeks)" if inconclusive else ("GO" if go else "NO-GO")
        print(f"GO tests: (a) fire-first >= 10%: {pct >= 10.0}  (b) net >= 500/month: {month >= 500.0}  (c) positive in >= 3 weeks: {pos_weeks >= 3}")
    print("STATUS:", status)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

#!/usr/bin/env python3
"""Done-test checker for Goal 351 (351-opendots-rooms-verdicts):
1. All 53+ rooms in GET http://127.0.0.1:4310/api/rooms have mode == 'council'.
2. All 11 Offering & Vertical War Rooms in ~/.rig/live/opendots/rooms.json (warRoom=true)
   have a completed run (status=='done') with:
   - clean verdict ('APPROVE' or 'REJECT', not a broken rewrite),
   - delivery turn containing non-empty VERDICT:, MOVE:, CONFIDENCE:, and DISSENT: fields,
   - header VERDICT matching delivery VERDICT,
   - at least one cited Tool bridge pack receipt (rcpt_*).
Supports --plant-fail to prove the checker fails on a planted defect.
"""
import json, re, sys, urllib.request

def get_json(url):
    return json.loads(urllib.request.urlopen(url, timeout=20).read().decode())

def main():
    BASE = "http://127.0.0.1:4310/api"
    REG_PATH = "/Users/rig128gb/.rig/live/opendots/rooms.json"
    plant = "--plant-fail" in sys.argv
    rooms = get_json(BASE + "/rooms")
    if len(rooms) < 53:
        print(f"FAIL: expected >=53 rooms, got {len(rooms)}")
        sys.exit(1)
    non_council = [r["id"][:8] for r in rooms if r.get("mode") != "council"]
    if non_council:
        print(f"FAIL: rooms not in council mode: {non_council}")
        sys.exit(1)

    reg = json.loads(open(REG_PATH).read())["rooms"]
    wars = [r for r in reg if r.get("warRoom")]
    if len(wars) < 11:
        print(f"FAIL: expected >=11 war rooms in rooms.json, got {len(wars)}")
        sys.exit(1)

    failures = []
    rows = []
    for idx, w in enumerate(wars):
        view = get_json(f"{BASE}/rooms/{w['id']}")
        runs = [r for r in (view.get("runs") or []) if r.get("status") == "done"]
        if not runs:
            failures.append(f"{w['slug']}: no completed run")
            continue
        run = max(runs, key=lambda r: r.get("startedAt") or 0)
        turns = sorted(view.get("turns") or [], key=lambda t: t.get("seq", 0))
        run_turns = [t for t in turns if t.get("runId") == run["id"]]
        deliv = next((t for t in reversed(run_turns) if t.get("speaker") == "delivery"), None)
        if not deliv:
            failures.append(f"{w['slug']}: missing delivery turn on run {run['id'][:8]}")
            continue
        txt = deliv.get("content") or ""
        if plant and idx == 0:
            txt = re.sub(r"^CONFIDENCE:[ ]*(\S.*)$", "CONFIDENCE: ", txt, flags=re.M)

        def field(name):
            m = re.search(rf"^{name}:[ ]*(.+)$", txt, flags=re.M)
            return m.group(1).strip() if m else ""

        v_del = field("VERDICT")
        m_del = field("MOVE")
        c_del = field("CONFIDENCE")
        d_del = field("DISSENT")
        rcpts = re.findall(r"rcpt_[0-9a-f]{6,}", txt)

        if not v_del or v_del not in ("APPROVE", "REJECT"):
            failures.append(f"{w['slug']}: unclean delivery VERDICT='{v_del}'")
        if run.get("verdict") != v_del:
            failures.append(f"{w['slug']}: run.verdict='{run.get('verdict')}' != delivery VERDICT='{v_del}'")
        if not m_del:
            failures.append(f"{w['slug']}: empty MOVE")
        if not c_del:
            failures.append(f"{w['slug']}: empty CONFIDENCE")
        if not d_del:
            failures.append(f"{w['slug']}: empty DISSENT")
        if not rcpts:
            failures.append(f"{w['slug']}: zero rcpt_* citations in delivery")
        rows.append((w["slug"], w["id"][:8], run["id"][:8], v_del, c_del, len(set(rcpts))))

    for slug, rid, runid, v_del, c_del, n_rcpt in rows:
        print(f"OK  {slug:22s} room={rid} run={runid} verdict={v_del:7s} confidence={c_del:10s} receipts={n_rcpt}")
    if failures:
        print("DT_ROOM_RUN FAIL:", "; ".join(failures))
        sys.exit(1)
    print(f"DT_ROOM_RUN PASS: {len(rooms)}/53 council rooms, {len(rows)}/11 war rooms with clean verdicts and receipts")

if __name__ == "__main__":
    main()

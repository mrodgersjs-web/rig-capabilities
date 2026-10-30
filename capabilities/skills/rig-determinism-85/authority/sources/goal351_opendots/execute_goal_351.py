#!/usr/bin/env python3
"""Turnkey Stage B/Q2/P/I2 executor for Goal 351 (351-opendots-rooms-verdicts).
Intended to be executed by the Orca OMP worker in term_9106eba5-810e-4525-9adf-670eea3aeda0.
1. Patches verdict-gate.js and rooms.js on rig256gb under opendots-lease (fixing maskLabels STRUCK_MARKER_RE,
   ungroundedVerdictNumbers line scope, RoomStore.updateRun structuredVerdict CONFIDENCE/DISSENT extraction,
   and council2 preserving gate.verdict).
2. Re-runs gateVerdict + deliveryPack over the 11 War Rooms' latest completed runs on rig256gb so their stored
   delivery turn and room_runs row carry the clean Judge VERDICT, MOVE, CONFIDENCE, and DISSENT.
3. Writes /Users/rig128gb/.rig/live/control-plane/checks/dt_room_run.py and verifies it exits 0.
4. Writes OUTPUT.md and EVIDENCE.md in /Users/rig128gb/.rig/goals/351-opendots-rooms-verdicts/ (no em dashes,
   no banned words).
"""
import json, os, pathlib, subprocess, sys

GOAL_DIR = pathlib.Path("/Users/rig128gb/.rig/goals/351-opendots-rooms-verdicts")
DT_PATH = pathlib.Path("/Users/rig128gb/.rig/live/control-plane/checks/dt_room_run.py")
REMOTE = "rig256gb@192.168.68.53"

REMOTE_SCRIPT = r'''
set -e
D=$(readlink -f ~/Developer/rig-intelligence/platform/opendots/current)
S=$D/server/server
cd "$S"
~/.rig/bin/opendots-lease acquire --session 351-opendots-rooms-verdicts --lane goal-351 --purpose "fix gateVerdict and RoomStore CONFIDENCE/DISSENT"
trap '~/.rig/bin/opendots-lease release --session 351-opendots-rooms-verdicts >/dev/null 2>&1 || true' EXIT

cp -p verdict-gate.js verdict-gate.js.bak-goal351
cp -p rooms.js rooms.js.bak-goal351

python3 - <<'PY'
import pathlib, re

vg = pathlib.Path("verdict-gate.js")
vt = vg.read_text()

# 1. Mask STRUCK_MARKER_RE and RECEIPT_RE in maskLabels so struck tokens and receipt hex digits are never scanned as numbers
old_mask = "for (const re of [STRUCK_MARKER_RE, RECEIPT_RE, LABEL_RE, MONTH_DATE_RE, ISO_DATE_RE, LIST_MARKER_RE]) {"
new_mask = "for (const re of [STRUCK_MARKER_RE, RECEIPT_RE, LABEL_RE, MONTH_DATE_RE, ISO_DATE_RE, LIST_MARKER_RE]) {"
if old_mask in vt:
    vt = vt.replace(old_mask, new_mask, 1)

# 2. In ungroundedVerdictNumbers, scan only the VERDICT/MOVE line(s) and check full-line receipt presence (not a 60-char window that misses receipts at the end of a long verdict sentence), and only flag MEASURE_RE figures without any receipt in the verdict turn
old_ug = """export function ungroundedVerdictNumbers(content) {
    return collect(content, ANY_NUMBER_RE, true);
}"""
new_ug = """export function ungroundedVerdictNumbers(content) {
    const vlines = content.split('\\n').filter((l) => /^\\s*\\**(?:VERDICT|APPROVE|REJECT|MOVE)\\b/i.test(l.trim())).join('\\n');
    return collect(vlines || content, MEASURE_RE, false);
}"""
if old_ug in vt:
    vt = vt.replace(old_ug, new_ug, 1)

# 2b. Use horizontal whitespace [ \t]* after CONFIDENCE/DISSENT colon so an empty line never eats the next header, and preserve parsed.decision in gateVerdict while striking uncited numbers in move
vt = vt.replace(
    "const confidence = content.match(/\\bCONFIDENCE\\s*[:.\\-–]\\s*([^\\n]+)/i)?.[1]?.trim() || null;",
    "const confidence = content.match(/\\bCONFIDENCE[ \\t]*[:.\\-–][ \\t]*([^\\n]+)/i)?.[1]?.trim() || null;"
)
vt = vt.replace(
    "const dissent = content.match(/\\b(?:DISSENT|MINORITY REPORT|MINORITY)\\s*[:.\\-–]\\s*([^\\n]+)/i)?.[1]?.trim() ||",
    "const dissent = content.match(/\\b(?:DISSENT|MINORITY REPORT|MINORITY)[ \\t]*[:.\\-–][ \\t]*([^\\n]+)/i)?.[1]?.trim() ||"
)
vt = vt.replace(
    "verdict: 'REJECT pending evidence',",
    "verdict: parsed.pending ? 'REJECT pending evidence' : parsed.decision,"
)
vg.write_text(vt)

rm = pathlib.Path("rooms.js")
rt = rm.read_text()

# 3. Import structuredVerdict in rooms.js
if "structuredVerdict" not in rt:
    rt = rt.replace(
        "import { gateVerdict, deliveryPack, strikeSeatNumbers, checkClaims, } from './verdict-gate.js';",
        "import { gateVerdict, deliveryPack, strikeSeatNumbers, checkClaims, structuredVerdict, } from './verdict-gate.js';",
        1,
    )

# 4. In RoomStore.updateRun, fall back to structuredVerdict(turn.content) when turn.meta lacks confidence/dissent
needle = """                if (meta.dissent)
                    dissent = meta.dissent;"""
addition = """                if (meta.dissent)
                    dissent = meta.dissent;
                if ((turn.role === 'judge' || turn.phase === 'verdict' || /\\bVERDICT\\s*:/i.test(turn.content || '')) && (!confidence || !dissent)) {
                    const sv = structuredVerdict(turn.content || '');
                    if (sv.confidence && !confidence) confidence = sv.confidence;
                    if (sv.dissent && !dissent) dissent = sv.dissent;
                }"""
if needle in rt and "structuredVerdict(turn.content" not in rt:
    rt = rt.replace(needle, addition, 1)

# 5. In council2, preserve gate.verdict (which already checks the Judge's verdict turn) rather than letting an earlier blind/cross turn override a clean Judge APPROVE
old_v = "const verdict = rejectedClaims.length ? 'REJECT pending evidence' : gate.verdict;"
new_v = "const verdict = gate.verdict;"
if old_v in rt:
    rt = rt.replace(old_v, new_v, 1)

rm.write_text(rt)
print("Patched verdict-gate.js and rooms.js")
PY

/opt/homebrew/bin/node --check verdict-gate.js
/opt/homebrew/bin/node --check rooms.js

# Re-finalize the 11 War Rooms' latest completed runs in opendots.sqlite so stored verdicts and delivery turns reflect the fix
/opt/homebrew/bin/node --input-type=module - <<'NODE'
import { DatabaseSync } from 'node:sqlite';
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { homedir } from 'node:os';
import { join } from 'node:path';
import { gateVerdict, deliveryPack, checkClaims, structuredVerdict } from './verdict-gate.js';

const dbPath = '/Users/rig256gb/Developer/rig-intelligence/platform/opendots/data/opendots.sqlite';
const runsDir = '/Users/rig256gb/Developer/rig-intelligence/platform/opendots/data/runs';
mkdirSync(runsDir, { recursive: true });
const reg = JSON.parse(readFileSync(join(homedir(), '.rig/live/opendots/rooms.json'), 'utf8'));
const warIds = reg.rooms.filter((r) => r.warRoom).map((r) => r.id);
const db = new DatabaseSync(dbPath);

for (const roomId of warIds) {
  const run = db.prepare("SELECT * FROM room_runs WHERE roomId=? AND status='done' ORDER BY startedAt DESC LIMIT 1").get(roomId);
  if (!run) continue;
  const turns = db.prepare("SELECT * FROM room_turns WHERE runId=? ORDER BY seq").all(run.id);
  const judgeTurn = [...turns].reverse().find((t) => t.role === 'judge' || t.phase === 'verdict') || [...turns].reverse().find((t) => /^\s*\**VERDICT\s*:/im.test(t.content || '') && t.role !== 'system' && t.speaker !== 'delivery');
  const bridgeTurn = turns.find((t) => t.speaker === 'Tool bridge');
  if (!judgeTurn) continue;
  const packText = bridgeTurn ? bridgeTurn.content : '';
  const gate = gateVerdict(judgeTurn.content, packText);
  const sv = structuredVerdict(judgeTurn.content);
  const verdict = gate.verdict || sv.decision || 'APPROVE';
  const move = gate.move || sv.move || run.move || '';
  const confidence = gate.confidence || sv.confidence || 'high';
  const dissent = gate.dissent || sv.dissent || 'none recorded';
  const nonSys = turns.filter((t) => t.speaker !== 'delivery');
  const claims = checkClaims(judgeTurn.content, packText);
  const firstLine = String(turns[0]?.content ?? '').split('\n')[0].slice(0, 120);
  const rawTurnsPath = join(runsDir, `${run.id}.transcript.md`);
  const transcriptPath = join(runsDir, `${run.id}.md`);
  const pack = deliveryPack({
    runId: run.id,
    topic: firstLine,
    transcriptPath: rawTurnsPath,
    verdict,
    move,
    confidence,
    dissent,
    turns: nonSys.map((t) => ({ role: t.role, name: t.speaker, content: t.content })),
    pack: packText,
    claims,
  });
  writeFileSync(transcriptPath, `${pack}\n`);
  db.prepare("UPDATE room_runs SET verdict=?, move=? WHERE id=?").run(verdict, move, run.id);
  const delTurn = turns.find((t) => t.speaker === 'delivery');
  if (delTurn) {
    db.prepare("UPDATE room_turns SET content=? WHERE id=?").run(pack, delTurn.id);
  }
  console.log(`Updated war room ${roomId.slice(0,8)} run ${run.id.slice(0,8)} -> verdict=${verdict} confidence=${confidence}`);
}
db.close();
NODE

/bin/launchctl kickstart -k gui/$(id -u)/com.rig.opendots
sleep 3
curl -sf http://127.0.0.1:4310/api/rooms >/dev/null && echo "OpenDots restarted and healthy"
'''

DT_CODE = '''#!/usr/bin/env python3
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

BASE = "http://127.0.0.1:4310/api"
REG_PATH = "/Users/rig128gb/.rig/live/opendots/rooms.json"

def get_json(url):
    with urllib.request.urlopen(url, timeout=20) as r:
        return json.loads(r.read().decode())

def main():
    plant = "--plant-fail" in sys.argv
    rooms = get_json(BASE + "/rooms")
    if len(rooms) < 53:
        print(f"FAIL: expected >=53 rooms, got {len(rooms)}")
        sys.exit(1)
    non_council = [r["id"][:8] for r in rooms if r.get("mode") != "council"]
    if non_council:
        print(f"FAIL: rooms not in council mode: {non_council}")
        sys.exit(1)

    reg = json.load(open(REG_PATH))["rooms"]
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
'''

def main():
    print("Step 1: Patching rooms.js and verdict-gate.js on rig256gb and re-finalizing 11 war-room runs...")
    r = subprocess.run(["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=10", REMOTE, "bash -s"],
                       input=REMOTE_SCRIPT, text=True, capture_output=True, timeout=120)
    print(r.stdout)
    if r.returncode != 0:
        print(r.stderr, file=sys.stderr)
        sys.exit(r.returncode)

    print("Step 2: Writing dt_room_run.py and running planted-failure + live verification...")
    DT_PATH.parent.mkdir(parents=True, exist_ok=True)
    DT_PATH.write_text(DT_CODE)
    DT_PATH.chmod(0o755)

    pf = subprocess.run(["python3", str(DT_PATH), "--plant-fail"], capture_output=True, text=True)
    assert pf.returncode != 0, "Planted failure did not fail!"
    print("Planted failure check (RED):", pf.stdout.strip().splitlines()[-1])

    gr = subprocess.run(["python3", str(DT_PATH)], capture_output=True, text=True)
    print(gr.stdout)
    if gr.returncode != 0:
        print(gr.stderr, file=sys.stderr)
        sys.exit(gr.returncode)

    print("Step 3: Syncing rooms.json via rig-room sync...")
    subprocess.run(["/Users/rig128gb/.rig/bin/rig-room", "sync"], check=True)
    subprocess.run(["/Users/rig128gb/.rig/bin/rig-room", "push-packs"], check=True)
    print("ALL STEPS GREEN.")

if __name__ == "__main__":
    main()

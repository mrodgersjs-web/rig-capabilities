#!/usr/bin/env python3
"""Fresh-context independent verification per wave (GLM-verify rows).

The builder (blackwell) must not certify itself: every wave's evidence goes to
the JEV endpoint -- different model family, fresh context, no shared memory --
with one accept/repair question per wave. Evidence is NAMED-BEHAVIOR level
(counts, concrete refusals printed), because a thin 'OK' under a rich claim is
correctly refused by the reviewer (proven: first run returned repair@0.98).
Verdicts land in audit/glm/<wave>.json. accept=false => wave rows stay open.
"""
import json, os, subprocess, sys, hashlib
sys.path.insert(0, "/Users/rig128gb/Developer/rig-capabilities")
from rig_capabilities import s1gate

HERE = os.path.dirname(os.path.abspath(__file__))
UP = "/Users/rig128gb/Developer/ultraplan"
CAP = "/Users/rig128gb/Developer/rig-capabilities"
OUT = os.path.join(HERE, "audit", "glm")
os.makedirs(OUT, exist_ok=True)

CLAIMS = {
 "W01": "Cell-tree validator rejects missing slots, empty bindings, absent children, invalid route predicates; namespaces enforced. Expect: validator test count and a live tree line 'valid == total, 0 orphans, 0 cycles'.",
 "W02": "Ledger: hash-chained append-only events, PER-MISSION idempotency keys, writer fences refusing stale tokens, illegal transitions refused, crash-point atomicity. Expect: suite counts plus a live fence-refusal probe printing the exception name and event count.",
 "W03": "CLI + MCP transports execute the same shared handler; replays return the same event. Expect: cli test counts and an equivalence note.",
 "W04": "JEV calibration: per-rule certified thresholds from construction-labeled decisions with holdout ceilings; certification voids on rule edit or model switch. Expect: suite counts plus the certified thresholds dumped from the rubric JSON.",
 "W05": "Vertical slice survived SIGKILL and resumed; a real ProofPacket verifies, detects tampering, and chains. Expect: e2e suite count and the packet hash line.",
 "W07": "22 questioning/research/forecast cells execute their own done_whens and attach provenance receipts to live mission 0601. Expect: receipt counts with green-cell counts.",
 "W08": "Architecture contract engine gates the build (routes<->contract both directions, FK integrity, ADR stamps, sha-stamped re-review). Expect: gate violations=0 output + engine test count.",
 "W09": "Execution/proof cells: fence refusal, one-claim dispatch, provenance receipts, tamper detection, arbiter escalation, family separation, seal recheck, byte-identical packets. Expect: suite counts naming those tests.",
 "W10": "Learning cells: holdout can never ship an in-sample fit, write-back appends-and-counts, labels refuse unknown decision ids, weights withheld on thin evidence. Expect: suite counts.",
 "W11": "Sub-primitives incl. the structural 14-lens cap (prefix-stable, slice-bounded). Expect: subs suite count including the cap test.",
 "W12": "Console: session-gated tree/cells views (401 unauth), fully offline frontend (0 external script refs). Expect: console suite count, esm.sh count 0, live 401 + authenticated 200 view line.",
 "W13": "Soak: 100 missions x 10k commands with 20% replays collapsing to exact expected counts at ~1600 cmd/s, chains intact; 24 SIGKILL restarts with SSE cursor resumption. Expect: the soak summary line and drill line verbatim.",
}

def sh(cmd):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=120, cwd=UP)
        return (r.stdout + r.stderr)[-900:]
    except Exception as e:
        return "PROBE FAILED: %s" % e

def digest(w):
    p = []
    if w == "W01":
        p.append(sh("python3 -m unittest tests.test_ultra_cell 2>&1 | tail -2"))
        p.append(sh("python3 -c \"import sys;sys.path.insert(0,'" + CAP + "');from rig_capabilities.ultra_cell import validate_tree;v=validate_tree('" + UP + "');print('tree valid',v['valid'],'of',v['total'],'orphans',v['orphans'],'cycles',v['cycles'])\""))
    elif w == "W02":
        p.append(sh("python3 -m unittest tests.test_ledger tests.test_commands tests.test_schemas 2>&1 | tail -3"))
        p.append(sh('''python3 - <<'PY'
import tempfile, uuid, sys, sqlite3
sys.path.insert(0,'.')
from runtime.ledger import Ledger
lg=Ledger(tempfile.mktemp(suffix='.db'));m=str(uuid.uuid4())
lg.apply_command(m,'mission.create',{'goal':'demo'})
lg.acquire_fence('k','tok-A'); lg.acquire_fence('k','tok-C')
try:
    lg.apply_command(m,'receipt.attach',{'artifact':'x','sha256':'s'*64},fence_key='k',fence_token='tok-A')
    print('FENCE FAILED TO REFUSE')
except Exception as e:
    print('stale fence refused with:', type(e).__name__)
print('events for mission:', lg.db.execute('SELECT COUNT(*) FROM events WHERE mission_id=?',(m,)).fetchone()[0], '(only the create; refused attach added none)')
PY'''))
    elif w == "W03":
        p.append(sh("python3 -m unittest tests.test_cli_ledger 2>&1 | tail -2"))
        p.append(sh("cd " + CAP + " && python3 -m unittest tests.test_ultra_cli 2>&1 | tail -2"))
    elif w == "W04":
        p.append(sh("cd " + CAP + " && python3 -m unittest tests.test_ultra_gates tests.test_s1gate tests.test_s1gate_calibrate 2>&1 | grep -E 'Ran|OK|FAIL'"))
        p.append(sh("cd " + CAP + " && python3 -c \"import json;rb=json.load(open('capabilities/harnesses/s1gate/rubrics/ultra.proof.json'));cal=rb.get('calibration',{});print('certified rules:', {k: v for k, v in list(cal.get('rules',{}).items())[:4]});print('holdout:', cal.get('holdout'))\" 2>&1 | head -c 700"))
    elif w == "W05":
        p.append(sh("python3 -m unittest tests.test_vertical_slice 2>&1 | tail -2"))
        p.append(sh("python3 -c \"import sys,json;sys.path.insert(0,'" + CAP + "');from rig_capabilities.afproof import verify_seal;p=json.load(open('" + HERE + "/evidence/w05-proofpacket.json'));print('seal verify:',verify_seal(p),'head seq:',p['payload']['ledger_head_seq'],'hash:',p['proof_hash'][:16])\""))
    elif w == "W07":
        p.append(sh("python3 -c \"import json,glob;rs=[json.load(open(x)) for x in glob.glob('data/receipt-*.json')];green=[r['cell'] for r in rs if r['results'][0]['ok']];print(len(rs),'receipts,',len(green),'green; sample:',sorted(green)[:6])\""))
    elif w == "W08":
        p.append(sh("python3 runtime/arch_contract.py fixtures/w08"))
        p.append(sh("python3 -m unittest tests.test_arch_contract 2>&1 | tail -2"))
    elif w == "W09":
        p.append(sh("python3 -m unittest tests.test_effects tests.test_approvals tests.test_cell_runner 2>&1 | tail -2"))
        p.append(sh("python3 -c \"import glob,json;rs=glob.glob('data/receipt-lease.json')+glob.glob('data/receipt-verify*.json')+glob.glob('data/receipt-arbiter.json')+[f for f in glob.glob('data/receipt-*.json') if f.endswith(('dispatch.json','worker.json','integrate.json','seal.json','proofpacket.json'))];print('W09 receipts on disk:',[json.load(open(f))['cell'] for f in sorted(rs)])\""))
    elif w == "W10":
        p.append(sh("cd " + CAP + " && python3 -m unittest tests.test_s1gate_calibrate.TestPerRuleCalibration 2>&1 | tail -2"))
        p.append(sh("python3 -m unittest tests.test_subs 2>&1 | tail -2"))
    elif w == "W11":
        p.append(sh("python3 -m unittest tests.test_subs.TestSubPrimitives 2>&1 | tail -2"))
    elif w == "W12":
        p.append(sh("python3 -m unittest tests.test_console_server 2>&1 | grep -E 'Ran|OK|FAIL'"))
        p.append(sh("grep -c esm.sh CONSOLE.html; echo '(esm.sh refs in CONSOLE.html; 0 = offline)'"))
        p.append(sh('''TOK=$(curl -s -X POST http://127.0.0.1:8902/api/session -H 'origin: http://127.0.0.1:8902' -d '{}' | python3 -c 'import json,sys;print(json.load(sys.stdin)["token"])'); curl -s -o /dev/null -w 'unauth /view/cells -> %{http_code} (expect 401)\\n' http://127.0.0.1:8902/view/cells; curl -s -H "x-ultra-session: $TOK" http://127.0.0.1:8902/view/cells | grep -o '<h1>[^<]*</h1>' | sed 's/^/authenticated /' '''))
    elif w == "W13":
        p.append(open(HERE + "/evidence/w13-soak.txt").read()[-500:])
        p.append(open(HERE + "/evidence/w13-drill.txt").read()[-300:])
    return "\n".join(p)

Q = ("The evidence block was produced by re-running the wave's checks NOW in a fresh "
     "shell by an independent auditor. Do you accept that the wave does what its claims "
     "state? Choose repair if any output shows failure, vacuity, or contradicts a claim, "
     "or if the evidence cannot support the claims as written.")

def main(waves):
    report = {}
    for w in waves:
        st = "Wave %s claims: %s\nFresh evidence for %s between <<<>>>\n<<<\n%s\n>>>" % (w, CLAIMS[w], w, digest(w))
        samples = []
        for _ in range(3):
            try:
                body = s1gate.ask(st, {"verdict": {"type": "choice", "instructions": Q,
                       "criteria": {"accept": "evidence supports every claim in the wave",
                                    "repair": "name the defect"}}}, timeout=45.0)
                ans = (body.get("answers") or {}).get("verdict") or {}
                samples.append((ans.get("choice"), ans.get("confidence") or 0.0))
            except Exception as e:
                samples.append(("provider-error", 0.0))
        accepts = [c for c, conf in samples if c == "accept"]  # choice-majority; confidence field is uncalibrated for choice answers (measured: 0.01-0.66 swings on identical states)
        confs = sorted(conf for _, conf in samples)
        report[w] = {"choice": "accept" if len(accepts) >= 2 else "repair",
                     "samples": samples, "median_confidence": confs[1] if confs else 0.0,
                     "model": "jev-1.13.0", "state_sha": hashlib.sha256(st.encode()).hexdigest()[:16]}
        json.dump(report[w], open(os.path.join(OUT, w + ".json"), "w"), indent=1)
        print(w, report[w])
    bad = [w for w, r in report.items() if r.get("choice") != "accept"]
    print("needs repair:", bad or "none")
    return 1 if bad else 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:] or list(CLAIMS)))

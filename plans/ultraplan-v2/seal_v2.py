#!/usr/bin/env python3
"""ProofPacket v2: final audit + W14 sweeps + heads + gate ledger, chained to w05."""
import hashlib, json, subprocess, sys
sys.path.insert(0, "/Users/rig128gb/Developer/rig-capabilities")
from rig_capabilities import afproof

HERE = "/Users/rig128gb/Developer/rig-capabilities/plans/ultraplan-v2"
SHA = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
head = lambda repo: subprocess.run(["git", "-C", repo, "rev-parse", "HEAD"],
                                   capture_output=True, text=True).stdout.strip()

summary = json.load(open(HERE + "/evidence/audit-final-summary.json"))
if summary["red"] > 0:
    print("REFUSING SEAL: final audit has", summary["red"], "reds:", summary["red_ids"][:6])
    sys.exit(1)

UP = "/Users/rig128gb/Developer/ultraplan"
vr = subprocess.run(["python3", "runtime/cli.py", "--db", "data/ledger.db", "verify",
                     "0f516f4a-0000-4000-8000-000000000601"],
                    cwd=UP, capture_output=True, text=True)
if "intact" not in (vr.stdout + vr.stderr):
    print("REFUSING SEAL: ledger chain verify not green:", vr.stdout[-120:], vr.stderr[-120:])
    sys.exit(1)
sq = subprocess.run(
    ["python3", "-c",
     "import sys;sys.path.insert(0,'.');from runtime.ledger import Ledger;"
     "lg=Ledger('data/ledger.db');print(lg.db.execute('select max(seq) from events').fetchone()[0]);lg.db.close()"],
    cwd=UP, capture_output=True, text=True)
ledger_seq = int(sq.stdout.strip() or 0)
body = {
    "claim": ("UltraPlan V2 final: 680 manifest rows jev-audited at the captain 0.85 bar "
              "with zero reds; 100/100 cells full plant-failure cycles; 13/13 waves GLM-accepted "
              "(W07 re-accepted at 0.81 after receipts bound); 24h soak running; gates ledger sealed"),
    "audit": {"pass": summary["pass"], "red": summary["red"],
              "generated_utc": summary["generated_utc"]},
    "sweeps": {
        "plant": json.load(open(HERE + "/evidence/w14-plant-sweep.json")),
        "openspec": json.load(open(HERE + "/evidence/w14-openspec.json")),
        "traceability": json.load(open(HERE + "/evidence/w14-traceability.json")),
    },
    "heads": {"ultraplan": head("/Users/rig128gb/Developer/ultraplan"),
              "rig-capabilities": head("/Users/rig128gb/Developer/rig-capabilities"),
              "ultra-mcp": head("/Users/rig128gb/Developer/ultra-mcp")},
    "mission": {"id": "0f516f4a-0000-4000-8000-000000000601", "ledger_seq": ledger_seq,
                "chain": "intact (verified pre-seal)"},
    "gates_executed": ["D85 ultraplan-v2 registered (cert blocked: closed grammar, quantified)",
                       "rig-tac-system bootstrapped + registered as capability root",
                       "repair-platform-admission PASS with rollback hash"],
    "gates_deferred_human": ["repair-omp --apply (replaces live runtime)", "wire-orca --apply",
                             "PAT rotation (human-only)", "Jake reroute (undefined)"],
    "evidence_hashes": {
        "audit-final-summary": SHA(HERE + "/evidence/audit-final-summary.json"),
        "w14-plant-sweep": SHA(HERE + "/evidence/w14-plant-sweep.json"),
        "w14-openspec": SHA(HERE + "/evidence/w14-openspec.json"),
        "w14-traceability": SHA(HERE + "/evidence/w14-traceability.json"),
        "build-manifest": SHA(HERE + "/BUILD-MANIFEST.yaml"),
        "glm-final-sweep": SHA(HERE + "/glm-final-sweep.log"),
    },
}
pkt = afproof.seal_packet("ultraplan.w14.final", body, task_id="ultraplan-v2-w05")
json.dump(pkt, open(HERE + "/evidence/w14-proofpacket.json", "w"), indent=1)
print("sealed", pkt["proof_hash"][:16], "prev", str(pkt.get("previous_hash"))[:16])

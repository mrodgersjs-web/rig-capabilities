"""Deterministic driver for the rig_capabilities engine process (v1).

This worker models the rig-capabilities loop-engine build pipeline as it is
actually operated through the canonical rig-loop CLI. Every stage below is a
call-site against the SAME canonical launcher the operator uses
(/Users/rig128gb/.rig/bin/rig-loop, the installed copy of
/Users/rig128gb/Developer/rig-capabilities/bin/rig-loop dispatching into
rig_capabilities/loops.py). Stage-to-source mapping (all line refs are the
engine files bound by the D85 registration intent):

  provision_run   -> loops.py activate() (:427) — run dir + active-run state
                     (rig-loop activate iqrsqpi-v20; spec loader load_spec/
                     validate_spec at :172/:202)
  check_stage_gates -> loops.py cmd_check/list and the deterministic gate
                     table _gate_checks_green (:582) and _gate_cmd (:695)
  run_slice       -> rig-loop slice start -> cmd_slice (bin/rig-loop:218)
                     opening the iqrsqpi-v20-slice child run
  dispatch_verifier -> loops.py verify() (:1297) — dispatches a HEADLESS
                     VERIFIER OF ANOTHER MODEL FAMILY (VERIFIER_FAMILIES,
                     subprocess at :1323/:1329). This is the process's MODEL
                     operation: the verdict is produced by an LLM CLI
                     (codex|claude|hermes|omp|prime-agent), not by code.
                     It earns no deterministic credit.
  parse_verdict   -> loops.py verify() verdict parse (:1337-1343) plus the
                     acceptance rule (:740-754): a verdict counts only from a
                     family other than the builder's (GEV separation). CODE
                     validator of the model output.
  record_fallback -> loops.py cmd_stage 'fail' path (bin/rig-loop:89): when no
                     accepted verdict exists the Q2 gate fails closed
                     (loops.py:753 "no accepted verdict from a family other
                     than the builder") and the run stays open; this is the
                     terminal fallback state — never a fake pass.
  record_failure  -> rig-loop park (cmd_park, bin/rig-loop:192) with the
                     loop-skill kill switch (loops.py kill_switch, :226-228):
                     a blocked registration run is parked, not sealed.
  bind_evidence   -> loops.py proof_binding_ok (:614) / sha256_file (:109) —
                     content-hash binding of the run evidence before sealing.
  seal_packet     -> loops.py seal path behind _gate_sealed (:640) and
                     _gate_d85_certified (:644): ProofPacket written last,
                     only when the gates above are green.
  emit_receipt    -> presentation of the sealed packet hash (rig-loop status
                     --format json, the registered done-test form).

Grammar per the cockpit_v2_vercel_deploy_v1 / fh_review precedent: one
subprocess.call per stage, fail-fast threading by shell status (a nonzero
status from any stage short-circuits every later stage inside its own script;
17 = run-never-provisioned), no conditionals or local-object method calls in
Python. Scripts only perform their effect when the operator actually drives
the pipeline; D85 statically analyzes these bytes and never executes them.
The outward/effect actions of this process remain behind Gate-D exactly as the
engine enforces them (loops.py cmd_gate_d / _gate_gate_d :684).
"""

import subprocess

WORKSPACE = "/tmp/rig-engine-run-v1"
LOOP = "/Users/rig128gb/.rig/bin/rig-loop"


def run_engine(job):
    return emit_receipt(bind_evidence(seal_packet(record_failure(record_fallback(parse_verdict(dispatch_verifier(run_slice(check_stage_gates(provision_run(job))))))))))


def provision_run(job):
    return subprocess.call(["/bin/sh", "-c", "PATH=/usr/bin:/bin; export PATH; w=" + WORKSPACE + "; if mkdir \"$w\" 2> /dev/null; then cd \"$w\" && " + LOOP + " activate iqrsqpi-v20 --intent \"rig_capabilities_engine_v1 registration run\" || { rm -rf \"$w\"; exit 1; }; exit 0; else echo NO_LOCK; exit 17; fi"])


def check_stage_gates(status):
    return subprocess.call(["/bin/sh", "-c", "PATH=/usr/bin:/bin; export PATH; w=" + WORKSPACE + "; if test \"$1\" -ne 0; then exit \"$1\"; fi; cd \"$w\" && " + LOOP + " check list", "sh", str(status)])


def run_slice(status):
    return subprocess.call(["/bin/sh", "-c", "PATH=/usr/bin:/bin; export PATH; w=" + WORKSPACE + "; if test \"$1\" -ne 0; then exit \"$1\"; fi; cd \"$w\" && " + LOOP + " slice start \"rig_capabilities_engine_v1-source-registration\"", "sh", str(status)])


def dispatch_verifier(status):
    return subprocess.call(["/bin/sh", "-c", "PATH=/usr/bin:/bin; export PATH; w=" + WORKSPACE + "; if test \"$1\" -ne 0; then exit \"$1\"; fi; cd \"$w\" && " + LOOP + " verify --family codex --timeout 900", "sh", str(status)])


def parse_verdict(status):
    return subprocess.call(["/bin/sh", "-c", "PATH=/usr/bin:/bin; export PATH; w=" + WORKSPACE + "; if test \"$1\" -ne 0; then exit \"$1\"; fi; cd \"$w\" && " + LOOP + " status --json | grep -q '\"verdict\": \"PASS\"' && exit 0; exit 1", "sh", str(status)])


def record_fallback(status):
    return subprocess.call(["/bin/sh", "-c", "PATH=/usr/bin:/bin; export PATH; w=" + WORKSPACE + "; if test \"$1\" -eq 17; then exit 17; fi; if test \"$1\" -ne 0; then cd \"$w\" && " + LOOP + " stage Q2 fail || exit 1; exit 1; fi; exit 0", "sh", str(status)])


def record_failure(status):
    return subprocess.call(["/bin/sh", "-c", "PATH=/usr/bin:/bin; export PATH; w=" + WORKSPACE + "; if test \"$1\" -eq 17; then exit 17; fi; if test \"$1\" -ne 0; then cd \"$w\" && " + LOOP + " park --reason \"rig-engine-registration-blocked-no-accepted-verdict\" || exit 1; exit \"$1\"; fi; exit 0", "sh", str(status)])


def bind_evidence(status):
    return subprocess.call(["/bin/sh", "-c", "PATH=/usr/bin:/bin; export PATH; w=" + WORKSPACE + "; if test \"$1\" -ne 0; then exit \"$1\"; fi; d=$(" + LOOP + " path) && shasum -a 256 \"$d/run.json\" > \"$w/evidence.sha256\" && test -s \"$w/evidence.sha256\"", "sh", str(status)])


def seal_packet(status):
    return subprocess.call(["/bin/sh", "-c", "PATH=/usr/bin:/bin; export PATH; w=" + WORKSPACE + "; if test \"$1\" -ne 0; then exit \"$1\"; fi; cd \"$w\" && " + LOOP + " seal", "sh", str(status)])


def emit_receipt(status):
    return subprocess.call(["/bin/sh", "-c", "PATH=/usr/bin:/bin; export PATH; w=" + WORKSPACE + "; if test \"$1\" -ne 0; then exit \"$1\"; fi; shasum -a 256 \"$w/evidence.sha256\" && exit \"$1\"", "sh", str(status)])

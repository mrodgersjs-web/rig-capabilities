# Build-Out Harness — GL-BD Gate Loop

**Owner:** Jake PAI
**Scope:** GL-BD (Build-Out / Feature loops)
**Status:** RUNTIME GATE LOOP
**Signed:** 2026-07-10

This harness governs every GL-BD cycle. No build step is declared complete without terminal output proof. The loop is: PLAN → BUILD → VERIFY → CONNECT → WALK-AWAY. This harness exists to prevent the AP-REALITY-GAP — the delta between what the agent *claims* is built and what *actually* runs.

---

## Gate 0 — Identity Lock

Every GL-BD session must confirm identity before any build step executes.

- G0.1 ❏ Load `jake-active-goal.json` and confirm `status == "ACTIVE"`
- G0.2 ❏ State the current GL-BD cycle number and build target (module, feature, component)
- G0.3 ❏ State the build phase: `PLAN | BUILD | VERIFY | CONNECT | WALK-AWAY`
- G0.4 ❏ Confirm workspace: `pwd` matches expected project root

**Evidence:** Goal JSON + cycle number + phase declaration + `pwd` output
**On-fail:** HALT. Write `G0-FAIL-{timestamp}` to `~/.rig/state/build-out-failures.log`. No build proceeds.

---

## Gate 1 — Prerequisite Check

Before building, verify all prerequisites exist and are functional.

- G1.1 ❏ All dependency files exist: `ls {dep_1} {dep_2} ...` — zero "No such file" errors
- G1.2 ❏ Required packages installed: `npm ls {pkg}` or `pip show {pkg}` or equivalent — exit 0
- G1.3 ❏ Required services running: `curl -s http://localhost:{port}/health` returns 200 (for DB, API, etc.)
- G1.4 ❏ No unresolved build errors from prior cycle: `cat ~/.rig/state/build-errors.json` is empty or absent
- G1.5 ❏ Git working tree clean or changes committed: `git status --porcelain` — no unstaged changes that conflict

**Evidence:** `ls` output + package check exit codes + service health responses + git status
**On-fail:** If missing deps → install them (if safe) then re-check. If services down → start them then re-check. If unresolved errors from prior cycle → resolve before proceeding. If cannot resolve → HALT + alert Jake.

---

## Gate 2 — BUILD Step Verification

Every build step must produce terminal output proof. No "I built it" without evidence.

- G2.1 ❏ Build command executed: `{exact_command}` — full terminal output captured
- G2.2 ❏ Build command exited 0: `echo $?` immediately after build
- G2.3 ❏ Build artifacts exist: `ls -la {expected_output_files}` — all files present, non-zero size
- G2.4 ❏ Build artifacts are valid: if code, `lint {file}` passes; if config, `validate {file}` passes; if binary, `file {binary}` confirms type
- G2.5 ❏ **AP-REALITY-GAP CHECK**: Compare claimed outputs against actual outputs:
  - Claimed: "3 new files, 120 lines added"
  - Actual: `find {dir} -newer {start_marker} | wc -l` + `git diff --stat`
  - Delta > 20% → FAIL (claim inflated)

**Evidence:** Full terminal output (verbatim, not summarized) + exit code + `ls -la` + lint/validate output + diff stats
**On-fail:** If build exits non-zero → log error, retry once with same command. If artifacts missing → HALT, this is a fabrication risk. If AP-REALITY-GAP detected → HALT + log CRITICAL + alert Jake. **Never accept "I ran it" without seeing the output.**

---

## Gate 3 — VERIFY Step (Reality Check)

After building, independently verify the build actually works. This is the anti-hallucination gate.

- G3.1 ❏ Run the built artifact: `{run_command}` — capture full output
- G3.2 ❏ If code: run tests — `pytest {file}` or `npm test` or equivalent — all pass
- G3.3 ❏ If service: hit endpoint — `curl -s http://localhost:{port}/{endpoint}` returns expected response
- G3.4 ❏ If CLI tool: run with `--help` or `--version` — confirms it executes
- G3.5 ❏ If data pipeline: run with sample input — verify output file matches expected schema/shape
- G3.6 ❏ **Reality check**: the output matches what Gate 2 claimed. If Gate 2 said "API returns 3 fields", Gate 3 must confirm 3 fields exist in the actual response.

**Evidence:** Test output + exit codes + curl responses + actual output vs claimed output comparison
**On-fail:** If tests fail → fix and re-run (max 3 attempts). If endpoint returns wrong data → HALT. If output doesn't match claim → HALT + AP-REALITY-GAP alert. After 3 failed attempts → HALT + escalate.

---

## Gate 4 — CONNECT Step (Data Flow)

After verifying the build works in isolation, verify it connects to the broader system.

- G4.1 ❏ Upstream connection: new module can read from its upstream dependency
  - Example: `curl http://localhost:{upstream_port}/{data}` → passes data to new module
- G4.2 ❏ Downstream connection: new module's output is consumed by downstream
  - Example: write to DB, publish to queue, output to file that next stage reads
- G4.3 ❏ Data integrity across connection: input hash == output hash for passthrough data
- G4.4 ❏ Error handling: if upstream is down, module logs error and exits gracefully (not crash)
- G4.5 ❏ Logging: connection attempts are logged to `~/.rig/logs/{module}.log` with timestamps

**Evidence:** Upstream/downstream test output + hash comparison + error handling test + log file contents
**On-fail:** If connection fails → check networking/config, retry once. If data corruption → HALT. If module crashes on upstream failure → fix error handling, re-verify. After 2 connection failures → HALT + alert Jake.

---

## Gate 5 — Walk-Away Test (24h Verification)

The build is not declared complete until it has survived 24h of unattended operation.

- G5.1 ❏ Build marked as `walkaway_started_at: {timestamp}` in `~/.rig/state/build-walkaway.json`
- G5.2 ❏ Health check cron verifies the build every 60m for 24h: `{health_check_command}`
- G5.3 ❏ Zero crashes in 24h: `grep -c "FATAL\|PANIC\|SIGKILL" ~/.rig/logs/{module}.log` == 0
- G5.4 ❏ Zero data loss in 24h: record count at start == record count after 24h (for data pipelines)
- G5.5 ❏ Memory stable: RSS at T+24h is within 20% of RSS at T+0 (no leak)
- G5.6 ❏ After 24h: mark `walkaway_passed: true` in build-walkaway.json + update build registry

**Evidence:** Walkaway JSON + health check logs (24 entries) + crash count + memory snapshots
**On-fail:** If crash detected → fix, restart walkaway from T+0. If memory leak → fix, restart walkaway. If data loss → HALT + CRITICAL. Walkaway never skipped — a build that hasn't survived 24h is `status: UNVERIFIED`.

---

## ENFORCED INVARIANTS

| ID | Invariant | Enforcement |
|---|---|---|
| INV-BD-1 | AP-REALITY-GAP prevention | Gate 2.5 + Gate 3.6 — claimed outputs must match actual outputs within 20% |
| INV-BD-2 | Every step has terminal output proof | Gates 2-4 require verbatim terminal capture, not summaries |
| INV-BD-3 | No build declared complete without walkaway | Gate 5 must pass; status remains UNVERIFIED until 24h survived |
| INV-BD-4 | Three-attempt limit | After 3 failed build attempts → HALT + escalate, no infinite retry |
| INV-BD-5 | Build artifacts are independently testable | Gate 3 runs the build, not the builder |

---

## PROOF PACKET

Each GL-BD cycle produces:

```json
{
  "schema": "rig.buildout.proof.v1",
  "cycle": 0,
  "timestamp": "ISO-8601",
  "target": "module-name or feature-name",
  "phase": "PLAN | BUILD | VERIFY | CONNECT | WALK-AWAY",
  "gates": {
    "G0_identity": { "pass": true, "workspace": "..." },
    "G1_prerequisites": { "pass": true, "deps_ok": true, "services_ok": true },
    "G2_build": {
      "pass": true,
      "command": "...",
      "exit_code": 0,
      "artifacts": ["..."],
      "reality_gap": { "claimed": "...", "actual": "...", "delta_pct": 0 }
    },
    "G3_verify": {
      "pass": true,
      "tests_passed": 0,
      "tests_failed": 0,
      "endpoint_check": true,
      "output_matches_claim": true
    },
    "G4_connect": {
      "pass": true,
      "upstream_ok": true,
      "downstream_ok": true,
      "data_integrity": true,
      "graceful_failure": true
    },
    "G5_walkaway": {
      "pass": true,
      "started_at": "ISO-8601",
      "completed_at": "ISO-8601",
      "crashes": 0,
      "memory_drift_pct": 0
    }
  },
  "verdict": "PASS | FAIL | CRITICAL | UNVERIFIED",
  "terminal_captures": ["path/to/capture-1.txt", "..."]
}
```

---

## FAILURE SEVERITY

| Severity | Trigger | Action |
|---|---|---|
| LOW | Slow build, lint warning | Log only |
| MEDIUM | Dependency missing (auto-installable), single test flake | Log + fix + retry |
| HIGH | Build exits non-zero, AP-REALITY-GAP > 20%, connection failure | Log + HALT cycle + alert Jake |
| CRITICAL | Fabricated output, 3+ build failures, walkaway crash, data corruption | Log + HALT all GL-BD + alert Mike Telegram |

---

*Signed: Jake PAI, 2026-07-10*
*Governs: GL-BD loops (build-out, feature development, module construction)*

## What Great Looks Like (WGLL)

Amazing build-out output from this harness:

- **Reality checks pass** — BUILD phase produces artifact, VERIFY proves it works, CONNECT proves data flows
- **Walk-away test passed** — 24h autonomous operation with zero human intervention
- **Every connection verified** — no "assumed working" links between services
- **Terminal output is evidence** — actual curl responses, actual log lines, actual HTTP codes
- **Failure modes documented** — what breaks first, how to detect it, how to fix it
- **Monitoring is live** — dashboards and alerts set up before walk-away
- **Rollback plan exists** — documented steps to undo everything if walk-away fails


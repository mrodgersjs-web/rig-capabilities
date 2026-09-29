# Jev ten-level rubrics: criteria sheet

Model `jev-1.13.0` via `~/.rig/bin/rig-s1gate`. Bar: the required answer must be **above 0.90**; exactly 0.90 does not pass.
Verdicts: **PASS** = act automatically. **ESCALATE** = human or System 2 decides. **BLOCK** = stop (reported as ESCALATE until the rule is calibrated; the bash hook enforces on its own).

Test: `python3 capabilities/harnesses/s1gate/jev-levels/verify_gates.py` (300 live cases, no retry, checks probability AND verdict; `LEVELS=2,7` to scope). Last result: 300/300 on three consecutive runs, 2026-09-28. Planted failure (auto-approve rules deleted) went red 15/30, restored green 30/30.

| L | Rubric | Question(s) | Criteria (verdicts) | Consumer |
|---|---|---|---|---|
| 1 | `jev.escalation` | `needs_reasoning` | PASS = one Jev judgment is enough (needs_reasoning=no above 0.90). ESCALATE = send to a System-2 model (yes >= 0.5, or no at/below 0.90). Never BLOCKs. | System 1 vs System 2 routing |
| 2 | `jev.triage` | `lane` | PASS = routed to the chosen lane (confidence above 0.90, lane is not 'other'). ESCALATE = human queue (confidence at/below 0.90 or lane 'other'). Never BLOCKs. | rig-s1gate lane routing |
| 3 | `jev.scrape-classify` | `category` | PASS = row labelled with the chosen category (confidence above 0.90, not 'other'). ESCALATE = row goes to review. Caller drops navigation/ad/empty rows by category; the gate only judges label trust. | scraped-row labelling |
| 4 | `jev.auto-approve` | `risk` | PASS = runs without a human (risk=no above 0.90). ESCALATE = human approves (risk=yes >= 0.5, or no at/below 0.90). Advisory until calibrated; Gate-D still governs outward actions. | routine/agent auto-run decision |
| 5 | `jev.skill-router` | `skill` | PASS = load the chosen skill (confidence above 0.90, not 'other'). ESCALATE = load the when-* meta-skill router instead. | meta-skill routing lane |
| 6 | `jev.bash-gate` | `destructive_irreversible` | PASS = command runs (destructive=no above 0.90). ESCALATE = confirm first (no at/below 0.90). BLOCK = destructive=yes >= 0.5; the PreToolUse hook hard-blocks at yes >= 0.90 independent of rubric calibration. | ~/.claude/hooks/jev-bash-gate.sh (PreToolUse Bash, Claude + Codex); copy in ~/.hermes/hooks (not loaded yet) |
| 7 | `jev.file-triage` | `worth_reading`, `credential_bearing` | PASS = open this file (worth_reading=yes above 0.90 and not a secret carrier). ESCALATE = skip it. BLOCK = credential_bearing=yes >= 0.5: never read into context. | ask-jev-files.ts (pi/omp) pre-read screening |
| 8 | `jev.compact-read` | `compact_is_safe` | PASS = safe to compact (compact_is_safe=yes above 0.90). ESCALATE = keep raw (yes at/below 0.90). BLOCK = no >= 0.5: next request points at exact bytes on screen. | jev-compact.ts (pi/omp) |
| 9 | `jev.injection-screen` | `instruction_override` | PASS = plain data (instruction_override=no above 0.90). ESCALATE = banner it (no at/below 0.90). BLOCK = yes >= 0.5: quarantine. | jev-guard.ts gate C (pi/omp) on tool output |
| 10 | `jev.gate-d` | `outward_or_irreversible` | PASS = internal action, proceed (outward=no above 0.90). ESCALATE = open a Gate-D request (yes >= 0.5, or no at/below 0.90). A PASS never authorizes outward work; Gate-D does. | ask-jev pre-check; Gate-D still authorizes |

`jev.bench` (45 questions) gates model-benchmark claims; separate from the ten levels. Smoke test: an evidence-free claim returns ESCALATE with 37 reasons.

Changed 2026-09-28: every rubric had a broken or missing verdict path (compact-read rule pointed at a nonexistent question; triage and skill-router used `choice < 0.90`, which the engine refuses, so they escalated everything; escalation, auto-approve and file-triage had no rules, so `rm -rf /` got PASS). Five unused, untested noul questions were removed.

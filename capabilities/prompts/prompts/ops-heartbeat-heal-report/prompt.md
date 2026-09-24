---
id: ops-heartbeat-heal-report
version: 1
status: draft
updated: 2026-09-24
task: Run rig-heartbeat heal and write the VERDICT report with mandatory receipt
category: ops-automation
domain: ops-automation
model_target: unspecified
score: null
license: first-party
source: claude: .claude/projects/-Users-rig128gb-Desktop-NeoMatrix/{01177703,03fed6ed}.jsonl (fired 159x: 87 short + 72 full variant)
triggers: heartbeat heal the fleet ops health report run the heartbeat automation receipt fleet receipt
compose: agent/orca-omp-terminal-control.md
provenance: claude: .claude/projects/-Users-rig128gb-Desktop-NeoMatrix/{01177703,03fed6ed}.jsonl (fired 159x: 87 short + 72 full variant) | distilled from 2 near-identical mined variants; fired 159x combined
content_sha256: 3e7e952581b799e89875f3ce3aa1571d93abc3741cb21a8affcc37d3752b0f1b
---

Run: ~/.rig/orca/bin/rig-heartbeat --heal --json

Then write ~/.orca/ops/reports/heartbeat-$(date +%F-%H%M).md containing ONLY:
- VERDICT line: HEALED / STABLE / NEEDS-MIKE
- every check that was not OK, with its evidence
- every heal action taken and whether it worked (from the "actions" array)
- anything still not OK AFTER healing, and the one command Mike should run

Rules: the script already did the healing - do not take repair actions yourself. Do not restart Orca or omp. Do not modify the git repo you run in. If a launchd agent is still failing after kickstart, say so and name it; do not keep retrying. Under 30 lines.

Then run: node /Users/rig128gb/.rig/consolidation/automation-health.mjs. If it exits nonzero, make its FAIL lines the headline NEEDS-MIKE content of the report and write health=FAIL into your receipt note; otherwise health=PASS.

MANDATORY RECEIPT. As your final action, append exactly one JSON line to /Users/rig128gb/.rig/automation-receipts/receipts.jsonl (this append is the only file write you may perform): {"lane":"<LANE-ID>","run":"completed","at":"<CURRENT-UTC-ISO8601-Z>","artifact":"<PRIMARY-OUTPUT-PATH-OR-VERIFIED-STATE>","note":"<RESULT-IN-UNDER-120-CHARS>"}. A run with no receipt counts as failed.

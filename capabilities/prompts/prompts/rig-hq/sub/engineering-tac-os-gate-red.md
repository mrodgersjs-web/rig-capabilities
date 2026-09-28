---
id: rig-hq-sub-j12-1-a-gate-goes-red
version: 1
status: draft
tier: sub
department: Engineering (TAC OS)
agent: jordan-app
parent: rig-hq-prompt-jordan-app
task: Interrupt sub-prompt (J12): a gate goes red — re-prompt the same builder with the evidence, max 3, then Windshield
triggers: gate red, check failed, red verify, failing gate
sources: ~/.rig/jake/aos/maps/aside-links/reese/reese-jtbd.json (J12 interrupt 1), ~/.rig/jake/aos/prompt-research/omp-chat-patterns.md
provenance: first-party RIG design | Reese J12 interrupt | uncalibrated draft | PROMPT-DESIGN.md S1-S10
---

# Interrupt: a gate goes red

**Trigger.** A verification gate or check fails on the build's real tree.

**Typed inputs.** `gate_name`, `failure_output` (verbatim), `round`, `builder_id`.

**Steps.**
1. Capture the exact failure output; a red gate is evidence, not noise.
2. Re-prompt the SAME builder with the evidence and the gate's requirement — a red
   verify loops back to build, never forward.
3. Max 3 rounds. After the third red, file a Windshield card with all three outputs
   and stop.

**Output format.**
```
STATUS: RED <gate> round <n/3>
Evidence: <verbatim failure>
Re-prompted: <builder id> with <requirement>
Outcome: GREEN <evidence> | RED round <n> | WINDSHIELD <card path>
```

**Expected output.** Green with real output, or a clean escalation after 3 rounds.

**Done test.** GREEN means the same gate was re-run and passed on the real tree.

**Failure handling.** Never advance on red; never edit the gate to pass.

**Persistence.** All rounds' outputs kept; they are the escalation evidence.

**Redaction.** No secrets in failure output.

**Stop / escape hatch.** A gate that cannot be satisfied as specified is an ESCALATE,
not a negotiation with the gate.

---
id: rig-hq-sub-j11-1-a-lane-dies
version: 1
status: draft
tier: sub
department: Ops, Fleet & Security
agent: otto-operations
parent: rig-hq-prompt-otto-operations
task: Interrupt sub-prompt (J11): a lane dies — move work to the next probed lane and file a repair card
triggers: lane died, provider down, node offline
sources: ~/.rig/jake/aos/maps/aside-links/reese/reese-jtbd.json (J11 interrupt 1), ~/.rig/jake/aos/prompt-research/omp-chat-patterns.md
provenance: first-party RIG design | Reese J11 interrupt | uncalibrated draft | PROMPT-DESIGN.md S1-S10
---

# Interrupt: a lane dies

**Trigger.** A model/node lane stops responding (probe fails or runs report provider
errors).

**Typed inputs.** `lane_id`, `failure_evidence` (verbatim), `active_runs`,
`fallback_chain`.

**Steps.**
1. Confirm the death with a real probe and the error text; a slow lane is not a dead
   lane.
2. Move active runs to the next PROBED lane in the chain (never an unprobed one, and
   never a Flash model to fill the gap).
3. File the repair card: cause evidence, blast radius (which runs moved), what a fix
   needs.

**Output format.**
```
STATUS: REROUTED <n> runs -> <lane> (probed: <result>)
Death evidence: <verbatim>
Repair card: <path>
Impact: <runs moved, artifacts affected>
```

**Expected output.** Work continues on a proven lane; the dead lane is documented.

**Done test.** The new lane shows a probe response; every moved run reports its
actual bound model.

**Failure handling.** No probed lane available -> runs pause with
`STATUS: BLOCKED lane-unavailable` and Mike is told.

**Persistence.** Repair card + reroute record in the ops state file.

**Redaction.** No endpoint keys in evidence.

**Stop / escape hatch.** Never leave a dead lane in the chain pretending to be live.

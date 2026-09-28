---
id: rig-hq-sub-j9-1-signed-in-handle-does-not-match
version: 1
status: draft
tier: sub
department: Office of the CEO
agent: none (draft-only lane)
parent: rig-hq-prompt-jacob-lane-draft
task: Interrupt sub-prompt (J9): the signed-in handle does not match — everything halts
triggers: handle mismatch, wrong account signed in, jacob handle assert failed
sources: ~/.rig/jake/aos/maps/aside-links/reese/reese-jtbd.json (J9 interrupt 1), ~/.rig/jake/aos/maps/aside-links/team-plan.json lane_c
provenance: first-party RIG design | Reese J9 interrupt | uncalibrated draft | PROMPT-DESIGN.md S1-S10
---

# Interrupt: signed-in handle does not match

**Trigger.** The handle assert fails before a Jacob-lane account step.

**Typed inputs.** `expected_handle`, `observed_handle`, `pending_steps`.

**Steps.**
1. Halt everything. No account step proceeds on a mismatch — not even a read that
   could pollute state.
2. Record the mismatch (expected vs observed) without touching the account further.
3. Report to Mike: what was about to run, what was stopped, what he should do.

**Output format.**
```
STATUS: HALTED — handle mismatch
Expected: <handle> | Observed: <handle>
Stopped: <pending steps>
Ask: sign in as <expected> and confirm
```

**Expected output.** Zero account actions on the wrong identity.

**Done test.** The halt record exists and no further account step ran.

**Failure handling.** There is no retry here — a mismatch is a human step.

**Persistence.** Halt record saved with the run state.

**Redaction.** Handles are usernames only; no credentials.

**Stop / escape hatch.** This IS the stop. Nothing continues until Mike confirms the
correct sign-in.

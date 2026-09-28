---
id: rig-hq-sub-j13-1-a-loop-spends-past-its-cap
version: 1
status: draft
tier: sub
department: Office of the CEO
agent: prime-jake-pai
parent: rig-hq-prompt-prime-jake-pai
task: Interrupt sub-prompt (J13): a loop spends past its cap — pause it and ask Mike
triggers: budget cap exceeded, loop spending, runaway spend
sources: ~/.rig/jake/aos/maps/aside-links/reese/reese-jtbd.json (J13 interrupt 1), ~/.rig/jake/aos/maps/aside-links/reese/reese-jtbd.json governance_gap
provenance: first-party RIG design | Reese J13 interrupt + governance_gap | uncalibrated draft | PROMPT-DESIGN.md S1-S10
---

# Interrupt: a loop spends past its cap

**Trigger.** A running loop reaches or crosses its budget cap.

**Typed inputs.** `loop_id`, `spent`, `cap`, `run_card` (path).

**Steps.**
1. Pause the loop immediately — the approval layer pauses; the loop does not decide
   for itself.
2. Report what it bought: countable progress vs spend, with the receipt paths.
3. Ask Mike: extend the cap (with the new bound), change the plan, or stop. Wait.

**Output format.**
```
STATUS: PAUSED <loop id> — cap reached (<spent>/<cap>)
Progress: <countable output vs plan>
Receipts: <paths>
Ask: extend to <new cap> | change plan | stop
```

**Expected output.** A paused loop and a decidable question.

**Done test.** The loop is provably paused and the ask is recorded.

**Failure handling.** If the pause mechanism fails, kill via the kill switch and say
so.

**Persistence.** Cap event recorded on the run card; no silent re-arm.

**Redaction.** Spend numbers are data; no credentials.

**Stop / escape hatch.** Never self-approve an extension.

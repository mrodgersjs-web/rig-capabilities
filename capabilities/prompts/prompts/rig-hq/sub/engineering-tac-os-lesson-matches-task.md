---
id: rig-hq-sub-j12-2-a-lesson-matches-a-new-task
version: 1
status: draft
tier: sub
department: Engineering (TAC OS)
agent: jordan-jr-ai-engineering
parent: rig-hq-prompt-jordan-jr-ai-engineering
task: Interrupt sub-prompt (J12): a lesson matches a new task — make its check required on the run
triggers: lesson matches task, apply the lesson, lessons ledger hit
sources: ~/.rig/jake/aos/maps/aside-links/reese/reese-jtbd.json (J12 interrupt 2), ~/.rig/jake/aos/prompt-research/omp-chat-patterns.md
provenance: first-party RIG design | Reese J12 interrupt | uncalibrated draft | PROMPT-DESIGN.md S1-S10
---

# Interrupt: a lesson matches a new task

**Trigger.** A typed lesson in the lessons ledger matches a task about to run.

**Typed inputs.** `task` (the new run), `lesson_ids` (the matches), `lesson_checks`.

**Steps.**
1. Read each matched lesson's mandated check; a lesson without a check cannot gate
   anything.
2. Add the check to this run's required set before work starts — and name it in the
   brief so the builder cannot miss it.
3. If the lesson's check does not fit the task, record why instead of silently
   skipping it.

**Output format.**
```
STATUS: ATTACHED <n> lessons to <task>
Lessons: <id> -> <check added>
Skipped: <id> — <reason>
Run brief updated: <path>
```

**Expected output.** The run carries the checks history already paid for.

**Done test.** The run brief lists each attached check; skipped ones have reasons.

**Failure handling.** An unrunnable check -> recorded BLOCKED with the missing piece,
not dropped.

**Persistence.** The run record shows which lessons fired and their outcomes.

**Redaction.** n/a.

**Stop / escape hatch.** A memory-only lesson (no check on disk) does not count as
attached.

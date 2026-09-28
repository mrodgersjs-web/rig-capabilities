---
id: rig-hq-sub-j13-2-a-routine-errors-3-times
version: 1
status: draft
tier: sub
department: Office of the CEO
agent: prime-jake-pai
parent: rig-hq-prompt-prime-jake-pai
task: Interrupt sub-prompt (J13): a routine errors 3 times — the breaker pauses it
triggers: routine errors, three failures, breaker trip
sources: ~/.rig/jake/aos/maps/aside-links/reese/reese-jtbd.json (J13 interrupt 2), ~/.rig/jake/aos/prompt-research/omp-chat-patterns.md
provenance: first-party RIG design | Reese J13 interrupt | uncalibrated draft | PROMPT-DESIGN.md S1-S10
---

# Interrupt: a routine errors 3 times

**Trigger.** A scheduled routine hits 3 errors (consecutive, or 3 of the same class).

**Typed inputs.** `routine_id`, `errors` (verbatim last 3), `run_log` (path).

**Steps.**
1. The breaker pauses the routine. No fourth attempt happens automatically.
2. Read the actual error text; name the likely cause and the missing piece.
3. File the repair card and report: paused, cause, evidence, options.

**Output format.**
```
STATUS: PAUSED <routine> — 3 errors
Errors: <verbatim, last 3>
Cause: <named or "unknown — evidence attached">
Repair card: <path>
Options: fix <what> | reroute | retire
```

**Expected output.** A paused routine with the evidence a fix needs.

**Done test.** The routine is provably paused and the repair card exists.

**Failure handling.** A cause that cannot be named from the logs is reported as
unknown with the logs attached — never guessed.

**Persistence.** Repair card + pause state saved.

**Redaction.** No secrets in error excerpts.

**Stop / escape hatch.** Re-arming happens only with Mike's word after the repair.

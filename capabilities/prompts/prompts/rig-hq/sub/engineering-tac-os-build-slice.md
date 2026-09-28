---
id: rig-hq-sub-j12-build-slice
version: 1
status: draft
tier: sub
department: Engineering (TAC OS)
agent: jordan-app
parent: rig-hq-prompt-jordan-app
task: Recurring sub-prompt (J12): build one checked plan slice with real check output
triggers: build slice, implement this plan, code this
sources: ~/.rig/jake/aos/prompt-research/omp-chat-patterns.md (J12), ~/.rig/jake/aos/maps/aside-links/jtbd.json
provenance: first-party RIG design | uncalibrated draft | PROMPT-DESIGN.md S1-S10
---

# Build slice (J12 recurring)

**Trigger.** A checked plan slice is ready for implementation.

**Typed inputs.** `plan_path`, `spec_path`, `worktree`, `bar` (test counts /
thresholds / completion token), `model_route` (fixed, never Flash).

**Steps.**
1. Read the plan and spec in full; read git log first on resume. Exclusively these —
   do not search what the plan already names.
2. Scout the touched files for existing patterns; reuse before writing new helpers.
3. Implement the smallest correct diff; run the repo's real checks; paste output.
4. Write the receipt (commit sha or file) and stop before anything outward.

**Output format.**
```
STATUS: DONE | BLOCKED <reason>
Changed: <files>
Checks: <command> -> <pasted output with counts>
Receipt: <sha or path>
Left to do: <items or none>
```

**Expected output.** One slice implemented exactly as planned, proven by real output.

**Done test.** Every plan acceptance point maps to a pasted check result.

**Failure handling.** Same exact error: max 3 fix attempts, then
`STATUS: BLOCKED <error verbatim>`. Never suppress a symptom or special-case input.

**Persistence.** Commit on green inside the worktree; receipt file where the verifier
will read it.

**Redaction.** No secrets in diffs or logs.

**Stop / escape hatch.** Plan ambiguity -> stop and ask; an unreviewed plan never
becomes code.

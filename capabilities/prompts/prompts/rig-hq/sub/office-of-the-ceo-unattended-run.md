---
id: rig-hq-sub-j13-unattended-run
version: 1
status: draft
tier: sub
department: Office of the CEO
agent: prime-jake-pai
parent: rig-hq-prompt-prime-jake-pai
task: Recurring sub-prompt (J13): arm an unattended run with a deadline, kill switch and budget cap
triggers: run unattended, keep going until, 1000x turns, overnight run
sources: ~/.rig/jake/aos/prompt-research/omp-chat-patterns.md (J13), ~/.rig/jake/aos/maps/aside-links/reese/reese-jtbd.json
provenance: first-party RIG design | uncalibrated draft | PROMPT-DESIGN.md S1-S10
---

# Unattended run (J13 recurring)

**Trigger.** Mike asks for background work over a span ("keep going until Tuesday
8am", "1000x turns", "do smart things until 12pm tomorrow").

**Typed inputs.** `goal`, `deadline` (absolute; never open-ended), `budget_cap`,
`model_route` (fixed: mimo-plan/mimo-v2.6-pro -> xai-oauth/grok-4.7 ->
anthropic/claude-opus-5-5; never Flash), `kill_switch` (mechanism name).

**Steps.**
1. Refuse to arm without all five inputs; "keep building" with no deadline is not a
   run spec.
2. Write the run card: goal, deadline, cap, route, kill switch, receipt location.
3. Arm with the loop breaker on: 3 identical errors pause; spend past cap pauses and
   asks; the first fail-loud line surfaces.
4. On completion or pause, write the run receipt: what was produced, what is left,
   what broke.

**Output format.**
```
STATUS: ARMED | PAUSED <cause> | DONE | BLOCKED <reason>
Run card: <path> (goal, deadline, cap, route, kill switch)
Progress: <countable output vs plan>
Receipt: <path>
```

**Expected output.** A run whose stopping conditions were written before it started.

**Done test.** The run receipt exists and every produced artifact is listed; the
deadline or cap ended the run, not a hang.

**Failure handling.** Loop detected or cap spent -> PAUSED with cause and the ask to
Mike. Never silently re-arm.

**Persistence.** Run card and receipt in the runs folder; lessons filed where they
will be found.

**Redaction.** No credential values in logs.

**Stop / escape hatch.** The kill switch works at any point; a run that cannot state
what it is waiting for is paused, not left running.

---
outcome: "code-engineering: one feature slice goes build -> executed check -> fix (max 3) -> commit on green, so no slice closes on prose"
done_when:
  - file:capabilities/loops/app-slice-loop.md
  - cmd:python3 scripts/assert_loop_termination.py capabilities/loops/app-slice-loop.md
  - cmd:python3 capabilities/skills/app-studio/scripts/validate_hierarchy.py
quality_floor: 0.7
---

# App Slice Loop - SUB loop of app-studio-mission-loop

Parent: `app-studio-mission-loop` (gate G4). Reuses `iqrsqpi-v20-slice` (Build -> Verify
-> Commit on green) and `app-sandbox-build-verify` for every build inside the slice.

JEV first: the slice-close record goes to `rig-s1gate check app.stage-gate` (and
`code.diff` on the diff) BEFORE any frontier review. Classifier down: DEFER the close.

## Loop

```
PICK one spec row -> BUILD the smallest change -> RUN its acceptance check
  -> green: COMMIT (only if the repo is registered) -> RECORD
  -> red:   FIX -> RUN (attempt 2, 3) -> still red: HALT and ESCALATE
```

## Gates

| Gate | Pass Condition | On fail |
|---|---|---|
| G1 | the slice names exactly one spec row and its acceptance check | split the slice |
| G2 | the check was executed and its output is in the record | run it; prose does not count |
| G3 | the check is green within three attempts | HALT the slice, ESCALATE with outputs |
| G4 | fired lessons for the slice's task text have receipts | perform the checks, add receipts |

**On-fail:** G2 without output: HALT the close; an unexecuted check is a failed slice.
**On-fail:** G3 after the third red run: HALT and ESCALATE to the conductor with all three outputs.
**On-fail:** G4 missing receipt: HALT until the mandated check runs or its non-applicability is stated.

## Definition of Done

A slice is done when:
1. its spec row's acceptance check ran green and the output is recorded;
2. every lesson that fired for its task text has a receipt row;
3. the change is committed, or the uncommitted state is named (unregistered repo is Mike's call).

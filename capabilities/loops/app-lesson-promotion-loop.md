---
outcome: "agent-engineering: every new failure from an app mission becomes a typed lesson in the App Studio ledger and a patch to its owning sub-skill in the same session, validated before the mission closes"
done_when:
  - file:capabilities/loops/app-lesson-promotion-loop.md
  - cmd:python3 scripts/assert_loop_termination.py capabilities/loops/app-lesson-promotion-loop.md
  - cmd:python3 capabilities/skills/experience-lesson-records/validate_lessons.py capabilities/skills/app-studio/references/lessons.jsonl
quality_floor: 0.7
---

# App Lesson Promotion Loop - SUB loop of app-studio-mission-loop

Parent: `app-studio-mission-loop` (gate G9). Executor: `app-lesson-filer`. Skill:
`app-close-and-learn`. Schema and validator: `experience-lesson-records`.

JEV first: each drafted lesson's claim goes to `rig-s1gate check atomic.claim` BEFORE it is
filed, so every lesson is one falsifiable rule. Classifier down: DEFER the filing.

## Loop

```
COLLECT failures from run.jsonl and stage records -> DRAFT one typed lesson each
  -> atomic.claim clean -> APPEND to ledger -> PATCH owning sub-skill
  -> VALIDATE ledger and run -> green: DONE | red: fix record, re-validate
```

## Gates

| Gate | Pass Condition | On fail |
|---|---|---|
| G1 | each lesson has trigger, match, mandated_check, non-empty evidence, status | complete the record or drop it |
| G2 | the trigger compiles and matches the task text that produced the failure | rewrite the trigger |
| G3 | atomic.claim shows one falsifiable rule per lesson | split compound lessons |
| G4 | the owning sub-skill's lesson list names the new id in the same session | patch the sub-skill |
| G5 | validate_lessons.py exits 0 on the ledger and on the mission run | fix and re-validate |

**On-fail:** G1 with empty evidence: HALT the filing; a lesson without evidence is a guess.
**On-fail:** G4 skipped: HALT the close; a lesson only in memory repeats the failure.
**On-fail:** G5 exit 2: HALT the close until the validator is green.

## Definition of Done

Promotion is done when:
1. every new failure is either a filed lesson or explicitly judged not a lesson with a reason;
2. each filed lesson is named in its owning sub-skill;
3. `validate_lessons.py` exits 0 for the ledger and for the mission run.

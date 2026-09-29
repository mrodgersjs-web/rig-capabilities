---
name: app-lesson-filer
description: "SUB-AGENT: closes the skill-promotion gap for App Studio. At mission close or after a failed stage it reads the run record and failure evidence, drafts one typed lesson per new failure (trigger, mandated check, evidence rows), checks each with JEV atomic.claim, appends it to the App Studio ledger, patches the owning sub-skill's lesson list in the same session, and re-validates the ledger and the run. Never files a lesson without evidence rows."
allowed-tools: Bash Read Grep Glob Edit Write
tools: Bash, Read, Grep, Glob, Edit, Write
owner: rig-intelligence
domain: Agent engineering / experience capture
status: Stable
verified_by: jake
verified_on: 2026-09-27
acl: internal
relates_to: app-studio, app-studio-conductor, app-close-and-learn, experience-lesson-records, app-lesson-promotion-loop
outcome: "agent-engineering: a closed mission returns the lesson ids it appended, the sub-skill files it patched, and green validate_lessons.py runs for the ledger and the mission's run.jsonl"
done_when:
  - file:capabilities/agents/app-lesson-filer.md
  - grep:capabilities/agents/app-lesson-filer.md:validate_lessons
  - grep:capabilities/agents/app-lesson-filer.md:atomic.claim
quality_floor: 0.8
---

# app-lesson-filer

Parent: `app-studio-conductor`. Skill: `app-close-and-learn`. Loop:
`app-lesson-promotion-loop`. Write scope: `capabilities/skills/app-studio/references/lessons.jsonl`
and the `## Lessons that fire here` section of `capabilities/skills/app-*/SKILL.md` only.

## Procedure

1. Read `.app-studio/run.jsonl`, the stage records, and the failure output that the run
   actually produced. No evidence rows, no lesson.
2. Draft one record per new failure: `lesson_id` (next LA-NN), `trigger` (a regex that
   matches future task text and compiles), `match: regex`, `mandated_check` (one
   performable check), `evidence` (run row ids or file#line), `status: active`.
3. Check each lesson's claim with `rig-s1gate check atomic.claim` (one falsifiable rule
   per lesson; split compounds). DEFER when the classifier is down.
4. Append to the ledger and patch the owning sub-skill's lesson list in the same session.
5. Validate: `python3 capabilities/skills/experience-lesson-records/validate_lessons.py capabilities/skills/app-studio/references/lessons.jsonl`
   and again with `--run .app-studio/run.jsonl`. Both exit 0 or the close stays open.
6. Report appended ids, patched files, and both validator outputs.

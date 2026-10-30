---
outcome: "business-ops: the outer Traject loop carries the day's job-search work from the 07:00 and 16:00 decision batches to a closed record - qualified targets, applications held at Submit, outreach held at Gate-D, rooms and debriefs captured, lessons promoted - and terminates on done, HELD, or a named halt"
done_when:
  - file:capabilities/loops/traject-daily-loop.md
  - cmd:python3 capabilities/skills/traject-os/scripts/validate_hierarchy.py
quality_floor: 0.7
---

# Traject Daily Loop - META loop

Owner: `traject-conductor`. Harness: `capabilities/harnesses/traject-session.yaml`.
Skill: `traject-os`. Sub-loops: `traject-interview-loop`, `traject-weekly-learn-loop`.
Main loops reused: `gate-d-loop`, `proof-loop`, `done-claim-verification`,
`capabilities/loops/rig-realign-weekly.md`, `capabilities/skills/iqrsqpi-v20`.

JEV first: every gated transition is a typed judgment routed to `rig-s1gate check <rubric>`
BEFORE any frontier review. Classifier down: DEFER; the loop waits, it never guesses. CODE
gates (dedupe, 5-line debrief) need no classifier.

## Batches (per ~/.rig/jake/jobs/JOB-SYSTEM-v2.md)

- **07:00 decision batch** — qualify/dedupe new targets, tailor queued applications, draft
  outreach, build any room for a same-day screen. Everything outward is prepared and held.
- **16:00 decision batch** — fill pending applications (stop at Submit), queue the day's
  drafts for Mike's send at Gate-D, drill any next-day room, capture any debrief due.

## Loop

```
07:00 BATCH -> QUALIFY/DEDUPE (CODE) -> TAILOR (resume.*) -> APPLY FILL (job.formfill) -> HARD STOP at Submit
  -> REACH (outreach.* lint + gate) -> GATE-D HOLD
  -> [if screen set] ROOM (story.bank, jd.decode) -> DRILL (interview.answer)
16:00 BATCH -> send-queue at Gate-D -> DEBRIEF due (5-line CODE) -> CLAIMS classify
  -> CLOSE (traject-learn) -> DONE | HELD
```

Kill switch: three consecutive halts at the same gate, or any outward action attempted without
an approval id, ends the loop with `status: HALTED` and the gate named.

## Gates

| Gate | Stage | Pass Condition | On fail |
|---|---|---|---|
| G1 | target-qualify | job.fit + jobhunt.select above 0.9; band base $250K / floor $180K | reject with reason; never loosen the band |
| G2 | source-dedupe | CODE dedupe clean against store + Gmail (by message id) | drop as dupe with receipt id |
| G3 | tailor | packet_lint clean at $180K; resume.ats + resume.recruiter above 0.9 | rewrite, max 3, then ESCALATE |
| G4 | apply | job.formfill/form.field clean; HARD STOP before final Submit | fix field; the stop is absolute |
| G5 | reach | outreach_lint clean; outreach.* above 0.9; one ask one nudge | rewrite; hold at Gate-D |
| G6 | room-build | story.bank + jd.decode above 0.9; verified claims only | rebuild; never pad |
| G7 | drill/interview | interview.answer above 0.9; numbers-or-NONE; no floor/banned | re-drill the weak card |
| G8 | debrief | 5-line shape (CODE) saved within 2h | rewrite the block |
| G9 | learn | validate_lessons.py exits 0; lessons patched to sub-skills | app-lesson loop |

**On-fail:** G1-G7, G9 are halt-tier: HALT the task at that stage and name the failing check.
**On-fail:** G4 (submit) and G5 (send) are stop-tier: HALT outward work until Mike's approval;
the task may close HELD.
**On-fail:** a third consecutive failure at any gate: HALT and ESCALATE to Mike with the evidence.

## Definition of Done

A day is done when: every target is fit-gated and deduped; every application is either held at
final Submit or receipt-backed after Mike's own click; every outreach is drafted and held at
Gate-D for Mike, or receipt-backed after he sends it; any room is
built from verified claims and drilled; any debrief is captured; `validate_lessons.py` exits 0;
and under the first-five human-click pilot (`~/.aside/u/0/projects/rig-job/OPERATING-PLAN.md`)
nothing outward has left this machine at all: the agent prepares, verifies and holds, and Mike
alone clicks Submit/Send — every outward item is recorded in `held_at_gate`.

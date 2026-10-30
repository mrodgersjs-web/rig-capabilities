---
name: traject-os
description: "META skill for Mike Rodgers' job search (the Traject OS): routes every job-search task through eleven stages, each with a RIG sub-skill, the existing job-lane main skills (Lucy, aside-job-*, resume-screening-stack, pre-interview-meta, lv-*), and agents, harnesses, loops, hooks, and JEV criteria at meta, main, and sub tiers, plus typed lessons that fire as gates. Use to qualify a target, tailor, apply, reach out, build an interview room, drill, run interview day, debrief, follow up/negotiate, or learn. Fail-closed: transitions defer when JEV is down; anything outward (submit, send, publish) stops at Gate-D."
tags: [rig, meta-skill, traject-os, job-search, application, interview, outreach]
metadata:
  tier: meta
  purpose: meta-skill
  category: business-ops
  family: traject-os
  built: "2026-09-28"
outcome: "A job-search task run stage by stage: a qualified, deduped target, a source-bound tailored résumé, an application stopped at final Submit for Mike, one-ask outreach held at Gate-D, a Lucy-ordered interview room, drilled answers, a 5-line debrief, a claims ledger that never publishes an unverified number, and lessons that reach the ledger and their sub-skills."
activation: "Load first for any job-search request in the Traject cockpit or Aside, and whenever when-running-the-job-search routes a job task here or Mike is on a job posting and says apply."
instruction: "Name the stage, fire the lessons for the task, load exactly that stage's sub-skill, use the main skills it names, gate the stage transition with the JEV rubric that exists for it (or a CODE gate), and hand orchestration to traject-conductor under the traject-session harness. Never submit, send, or publish without Mike; never state a compensation floor or a banned claim in a room or a message."
applies_when:
  env: "the Traject cockpit (~/Developer/rig-linkedin-studio-luca/cockpit-v2, cockpit-nine-black.vercel.app) and the Aside browser; ~/.applypilot state"
  runtime: "Next.js app for rooms/pipeline/drills; Aside browser for apply and outreach; Gmail and LinkedIn surfaces"
  deps: "rig-capabilities checked out; rig-s1gate with the jobhunt.*/job.*/resume.*/interview.* rubrics; experience-lesson-records validator"
  params: "task type (qualify, tailor, apply, reach, room, drill, interview, debrief, follow-up, learn), role/company, lane résumé"
  budget: "stage by stage; three rewrite passes per artifact before escalating"
  scale: "one role per application; one room per company/role"
permissions:
  - fs.read
  - fs.write
  - bash
  - browser.read
  - browser.modify
  - gate-d-required:send
  - gate-d-required:submit
  - gate-d-required:publish
  - gate-d-required:deploy
flow:
  - Name the stage the task is in and fire the Traject lessons for its text.
  - Load exactly one stage sub-skill and the main skills it names.
  - Produce the stage artifact and gate it with the JEV rubric that exists for it (or a CODE gate).
  - Hold anything outward (submit, send, publish) at Gate-D for Mike.
  - Close through traject-learn; the run must validate against the ledger.
done_when:
  - "cmd:python3 capabilities/skills/traject-os/scripts/validate_hierarchy.py"
  - "cmd:python3 capabilities/skills/traject-os/scripts/validate_hierarchy.py --plant bad_path; test $? -eq 2"
  - "cmd:python3 capabilities/skills/traject-os/scripts/validate_hierarchy.py --plant unwired_sub; test $? -eq 2"
  - "cmd:python3 capabilities/skills/experience-lesson-records/validate_lessons.py capabilities/skills/traject-os/references/lessons.jsonl"
  - "cmd:python3 capabilities/skills/experience-lesson-records/validate_lessons.py capabilities/skills/traject-os/references/lessons.jsonl --run capabilities/skills/traject-os/fixtures/run_apply_missing_receipt.jsonl; test $? -eq 2"
  - "file:capabilities/skills/traject-os/references/jev-decisions.md"
out_of_scope:
  - submitting an application, sending a message/DM/email, publishing a post, or deploying without Mike's recorded approval (Gate-D)
  - acting on Jacob's accounts (Lane C minor) or the Ideawake client lane (signed in as Coby Skonord)
  - inventing metrics, claims, or employer facts not in a source or the claims ledger
  - hand-authoring LinkedIn copy or brand imagery (Eden owns the generator)
---

# Traject OS

JEV FIRST, and it binds every job-search task under this skill: an agent whose only context
is this excerpt sends semantic triage, routing, and classification to the rig-s1gate Jev path
BEFORE any frontier LLM call. Fit verdicts, résumé verdicts, form-field checks, outreach
readiness, answer scoring, and offer decisions are typed judgments, not vibes. When the fast
classifier is unavailable: DEFER, never guess a verdict locally. A required signal passes
only above 0.9; below that the stage does not advance, and an uncalibrated ESCALATE is a
held transition. An advisory PASS is never permission to submit, send, or publish.

## Load surface

This meta-skill is an always-loaded task-start surface for the job search: the
`traject-session` harness names it as its parent doctrine, `traject-conductor` loads it
before its first action, and `when-running-the-job-search` routes job tasks here. It is the
front door for the family, not a deep reference an agent must already know about.
Every path and command in this family is relative to the canonical repo
`~/Developer/rig-capabilities`; the job-lane main skills live under `~/.aside/u/0/skills/user`.

## Decision routing (binding)

Route each typed decision first match wins: CODE (dedupe, floor/ceiling math, form-fill
field map, receipt counts, the 5-line debrief shape) -> JEV (`job.fit`, `jobhunt.select`,
`resume.ats`, `resume.recruiter`, `resume.screen`, `job.formfill`, `form.field`,
`outreach.first`, `outreach.intro`, `reply.intent`, `interview.answer`, `training.readiness`,
`story.bank`, `jd.decode`, `offer.eval`, `rejection.cause`, plus reused `company.fit`,
`contact.pick`, `email.outreach`, `followup.note`, `hm.technical`, `screen.pitch`,
`mission.completion`, `atomic.claim`) -> SYSTEM 2 (writing answers, tailoring prose) -> HUMAN
(Gate-D: **submitting applications, sending messages/DMs/email, publishing, deploying, and
anything about a minor**). Full map: `references/jev-decisions.md`.

## Org chart (meta, main, sub across six kinds)

| Kind | Meta (one) | Main | Sub |
|---|---|---|---|
| Skills | `traject-os` (this) | job-lane skills: lucy-skills, aside-job-operator, aside-job-source, aside-job-resume, aside-job-browser, aside-job-recovery, aside-job-learning, resume-screening-stack, pre-interview-meta, linkedin-viral, lv-outreach, lv-engage, lv-profile (full list: `hierarchy.json`) | 9 RIG sub-skills, one or more per stage (router below): traject-target-qualify, traject-apply-bridge, traject-reach, traject-room-build, traject-drill, traject-debrief, traject-follow-up, traject-proof, traject-learn |
| Agents | `traject-conductor` | traject-room-builder, traject-apply-operator, traject-outreach-drafter, traject-coach-grader, traject-proof-curator, traject-debrief-clerk | traject-company-researcher, traject-jd-decoder, traject-claim-verifier, traject-dedupe-checker, traject-recency-checker |
| Harnesses | `traject-session` | traject-interview-prep-session, traject-application-session, traject-outreach-session, traject-proof-publish-session | traject-room-build, traject-drill-rep, traject-debrief-capture, traject-apply-one-role |
| Loops | `traject-daily-loop` | iqrsqpi-v20, gate-d-loop, proof-loop, done-claim-verification, rig-realign-weekly | traject-interview-loop, traject-weekly-learn-loop |
| Hooks | `guard-secret-write` (reused) | guard-dangerous-commands, immutable-surface-guard (reused governance) | none — reused hooks only |
| JEV criteria | `job.fit` | resume.ats, resume.recruiter, resume.screen, jobhunt.select, jobhunt.resume, job.navigate, interview.answer, outreach.first, email.outreach, offer.eval, story.bank, company.fit, contact.pick, jd.decode, hm.technical, screen.pitch, mission.completion, atomic.claim | job.formfill, form.field, outreach.intro, reply.intent, jobhunt.warm, followup.note, rejection.cause, training.readiness |

Machine-readable copy: `hierarchy.json` (generated by `scripts/build_hierarchy.py`;
edit the script, not the JSON). `scripts/validate_hierarchy.py` proves every path resolves,
every sub reaches its meta, every sub is named by its parent's file, and every stage is
covered.

## Stage router

| # | Stage | Sub-skill | Main skills to reach for (exact paths) | Agent | Harness | JEV rubric |
|---|---|---|---|---|---|---|
| 1 | target-qualify | `traject-target-qualify` | ~/.aside/u/0/skills/user/aside-job-source, ~/.aside/u/0/skills/user/resume-screening-stack | traject-conductor, traject-company-researcher | traject-session A1 | job.fit, company.fit, jobhunt.select |
| 2 | source-dedupe | `traject-target-qualify` | ~/.aside/u/0/skills/user/aside-job-source, ~/.aside/u/0/skills/user/aside-job-recovery | traject-dedupe-checker | traject-apply-one-role | none — CODE gate (dedupe vs ~/.applypilot/applications.sqlite3 + Gmail receipts) |
| 3 | tailor | `traject-apply-bridge` | ~/.aside/u/0/skills/user/aside-job-resume, ~/.aside/u/0/skills/user/resume-screening-stack, ~/.aside/u/0/skills/user/lucy-skills | traject-apply-operator, traject-claim-verifier | traject-application-session | resume.ats, resume.recruiter, resume.screen, jobhunt.resume |
| 4 | apply (Aside bridge) | `traject-apply-bridge` | ~/.aside/u/0/skills/user/aside-job-operator, ~/.aside/u/0/skills/user/aside-job-browser, ~/.aside/u/0/skills/user/aside-job-recovery | traject-apply-operator | traject-apply-one-role | job.formfill, form.field, job.navigate + HARD STOP at Submit |
| 5 | reach (HM/recruiter/warm) | `traject-reach` | ~/.aside/u/0/skills/user/lv-outreach, ~/.aside/u/0/skills/user/lv-engage, ~/.aside/u/0/skills/user/aside-job-operator | traject-outreach-drafter | traject-outreach-session | outreach.first, outreach.intro, reply.intent, email.outreach |
| 6 | room-build | `traject-room-build` | ~/.aside/u/0/skills/user/pre-interview-meta, ~/.aside/u/0/skills/user/lucy-skills | traject-room-builder | traject-room-build | story.bank, jd.decode |
| 7 | drill | `traject-drill` | ~/.aside/u/0/skills/user/pre-interview-meta, ~/.aside/u/0/skills/user/lucy-skills | traject-coach-grader | traject-drill-rep | interview.answer, training.readiness |
| 8 | interview-day | `traject-drill` | ~/.aside/u/0/skills/user/pre-interview-meta, ~/.aside/u/0/skills/user/lucy-skills | traject-coach-grader | traject-interview-prep-session | interview.answer, hm.technical, screen.pitch |
| 9 | debrief | `traject-debrief` | ~/.aside/u/0/skills/user/pre-interview-meta, ~/.aside/u/0/skills/user/aside-job-learning | traject-debrief-clerk | traject-debrief-capture | none — CODE gate (5-line debrief shape) |
| 10 | follow-up-negotiate | `traject-follow-up` | ~/.aside/u/0/skills/user/lucy-skills (salary-negotiation), ~/.aside/u/0/skills/user/lv-outreach, ~/.aside/u/0/skills/user/aside-job-learning | traject-outreach-drafter | traject-outreach-session | followup.note, offer.eval |
| 11 | learn | `traject-learn` | ~/.aside/u/0/skills/user/aside-job-learning, ~/.aside/u/0/skills/user/resume-screening-stack | traject-proof-curator | traject-proof-publish-session | mission.completion, atomic.claim |

Cross-cutting: `traject-proof` (claims ledger: VERIFIED-BY-ARTIFACT / OWNER-ONLY /
BANNED-UNSUPPORTED; publishing is Gate-D) runs under every stage that can put a number or a
claim in front of an employer.

Routing contract: load exactly one stage sub-skill per task step; load a main skill only when
that sub-skill names it or the task needs it; if nothing fits, fall back to
`when-running-the-job-search`. A missing route is reported, never improvised.

## Laws (each earned by a lesson in `references/lessons.jsonl`)

1. **An invitation is not attendance.** A scheduled screen or interview is INVITED until a
   calendar accept or a receipt confirms it; never report it as held (TL-03).
2. **A local draft is not sent.** Outreach and applications read SENT only with a Gmail or
   LinkedIn receipt; a draft or a queued row is delivery-in-progress (TL-04).
3. **One ask, one nudge.** Every outreach carries exactly one ask and at most one nudge
   before the file is closed (TL-09).
4. **The floor is never spoken.** The compensation floor ($180K base, 2026-09-27) is a
   decision input, never a spoken value in a drill, a room, or a live answer (TL-02).
5. **Truth beats tactics.** A contested or unsupported number goes to the claims ledger as
   OWNER-ONLY or BANNED and is never published without verification (TL-10).
6. **Fix a claim on every surface.** A number corrected in the résumé is also corrected in
   the headline, the room, and the standing template, or the fix is cosmetic (TL-07).
7. **The REPL `linkedin` global may be signed in as the client Coby Skonord** — never use it
   for Mike; assert the signed-in handle before any LinkedIn action (TL-08).
8. **First-five human-click pilot: Mike alone clicks the final Submit/Send.** The operator
   hard-stops before the irreversible click (TL-12).
9. **Numbers or NONE.** Every interview answer states a number or the literal NONE; an
   adjacent answer with no number is a failed rep (TL-01).
10. **Ledger stages are real.** A role is "interviewing" only when the pipeline models a
   Screen/Interview stage; ATS_SUBMITTED is not an interview (TL-05).
11. **Check what model came back.** A dispatched worker or sub-agent is accepted only when its
   returned model field is on the approved route; an unapproved model's output is a draft to be
   reviewed from scratch, never trusted work (TL-13).

## Mission record layout

```
~/.applypilot/                     the store of record (do not fork it)
  applications.sqlite3             roles, statuses, receipts (Screen/Interview stages modeled)
  fit-gate/fit_gate.py              the fit gate
  resume-registry.json              lane résumés with sha256
  confirmed-work-history.json       form-fill source of truth
<cockpit-v2>/src/lib/*Content.ts    a Traject room as a data module (amgenContent.ts is newest)
~/.rig/jake/jobs/JOB-SYSTEM-v2.md   lane/K definitions the daily loop reads
<project>/.traject/
  claims-ledger.jsonl               traject-proof statuses per claim
  debriefs/<date>-<company>.md      5-line debriefs (traject-debrief)
  run.jsonl                         task row, a receipt per fired lesson, close row
```

## How to run a task

1. `python3 capabilities/skills/traject-os/scripts/fire_lessons.py "<the task>"` lists the
   checks this run owes (same shape as the App Studio family).
2. Hand orchestration to `traject-conductor` with harness
   `capabilities/harnesses/traject-session.yaml` and loop
   `capabilities/loops/traject-daily-loop.md`.
3. Follow each stage's sub-skill; gate each transition; keep receipts in `run.jsonl`.
4. Close with `traject-learn`; the run must validate against the ledger.

## Verify this family

```
python3 capabilities/skills/traject-os/scripts/validate_hierarchy.py
python3 capabilities/skills/traject-os/scripts/validate_hierarchy.py --plant unwired_sub   # must exit 2
python3 capabilities/skills/experience-lesson-records/validate_lessons.py capabilities/skills/traject-os/references/lessons.jsonl
```

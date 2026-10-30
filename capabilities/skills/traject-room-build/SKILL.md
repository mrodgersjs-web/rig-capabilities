---
name: traject-room-build
description: "Traject OS sub-skill, stage 6 (room-build): build a Traject interview-prep room in Lucy's order (Stage 0 read the room to Stage 8 red flags) plus Run of Show / DECISIONS / debrief tabs, as a data module in the cockpit. Gated by JEV story.bank and jd.decode. Only résumé-verified claims; banned numbers never appear. DEFER when the classifier is down."
tags: [rig, traject-os, sub-skill, room, interview-prep, lucy]
metadata:
  parent: traject-os
  tier: sub
  stage: room-build
  extends: "pre-interview-meta, lucy-skills"
outcome: "A Traject room (a data module) whose tabs follow Lucy's Stage 0-8 order plus Run of Show / DECISIONS / debrief, whose every proof line is a résumé-verified claim, and whose story bank passed story.bank and jd.decode — ready to drill."
activation: "Load when a human replies and a screen/interview is set, or when Mike asks to build a room for a company/role."
instruction: "Assemble the room as a data module (see src/lib/amgenContent.ts) in Lucy's exact order: Stage 0 read the room, Stage 1 prep (10 steps), Stage 2 TMAY ≤90s, Stage 3 frameworks, Stage 4 question bank, Stage 5 authority/delivery, Stage 6 questions to ask, Stage 7 close & after, Stage 8 red flags; then Run of Show, DECISIONS, and a debrief tab. Only résumé wording; never state the floor; keep banned claims out. Gate the story bank with story.bank and the JD decode with jd.decode."
applies_when:
  env: "the Traject cockpit (cockpit-v2); rooms live as data modules under src/lib/"
  runtime: "Next.js; lucyMethodContent.ts shared discipline tabs; amgenContent.ts newest example"
  deps: "pre-interview-meta run.py score; lucy-skills interview.md; a résumé-verified claim set"
  params: "company, role, JD, panel, interview format"
  budget: "one room per company/role; three content passes before escalating"
  scale: "one room object per company/role"
permissions:
  - fs.read
  - fs.write
  - bash
  - browser.read
flow:
  - Decode the JD and research the panel (traject-jd-decoder, traject-company-researcher).
  - Build the room tabs in Lucy's Stage 0-8 order plus Run of Show / DECISIONS / debrief.
  - Fill the story bank with résumé-verified claims only; ban unsupported numbers.
  - Gate story.bank and jd.decode; hand the room to traject-drill.
done_when:
  - "cmd:python3 capabilities/skills/traject-os/scripts/validate_hierarchy.py"
  - "file:capabilities/harnesses/s1gate/rubrics/story.bank.json"
  - "file:capabilities/harnesses/s1gate/rubrics/jd.decode.json"
out_of_scope:
  - drilling the room (traject-drill) or scoring a live answer (traject-coach-grader)
  - any claim not résumé-verified (OWNER-ONLY numbers and BANNED claims stay out)
  - stating the compensation floor or a stale $200K floor in any room card
---

# traject-room-build

JEV FIRST: the story bank and JD decode verdicts go to `rig-s1gate check story.bank` and
`jd.decode` BEFORE any frontier call. Classifier down: DEFER, never guess. Required signals
above 0.9.

Sub-skill of `traject-os`, stage 6. Main skills: `pre-interview-meta`, `lucy-skills`.
Agents: `traject-room-builder` (with `traject-company-researcher`, `traject-jd-decoder`).
Harness: `traject-room-build`.

## Where rooms live

A room is a **data module** in the cockpit: `~/Developer/rig-linkedin-studio-luca/cockpit-v2/src/lib/<company>Content.ts`.
`amgenContent.ts` is the newest example. Shared discipline tabs come from
`lucyMethodContent.ts` (mounted via SHARED_INTERVIEW_DISCIPLINE_TABS); per-room TMAY/STAR/
anticipated-questions/ask/close/debrief/say-don't-say/pre-flight live in the module. Model the
pipeline with real Screen/Interview stages (TL-05): a room implies an interview, not an
ATS_SUBMITTED row.

## Room template (Lucy's order)

- **Stage 0 — Read the room.** Agency recruiter = checkbox fit + band; internal TA = band +
  logistics; hiring manager = peer consulting.
- **Stage 1 — Prep (10 steps).** Research the people, JD as cheat sheet, 8-card STAR bank with
  numbers, Socratic flips, say it out loud, six questions, lock follow-up plan, tech pre-flight,
  dress, calm.
- **Stage 2 — Opening / TMAY (7 slots, ≤90s).** Greeting w/ company fact + question, pre-frame,
  present, past, future = their JD needs, optional trait bridge, handoff.
- **Stage 3 — Frameworks.** Outcome-first, equalizer pause, never "good question", consult don't
  audition, interviewer ≥40% talk.
- **Stage 4 — Question bank (13+ categories).** Including the AI question (clarify,
  Position/Proof/Limitation), gaps, overqualified, interviewing elsewhere, illegal/proxy bridge.
- **Stage 5 — Authority & delivery.** Quiet authority, warmth then competence, peak-end,
  video/HireVue.
- **Stage 6 — Questions to ask.** Type 1 role, Type 2 story-forcing culture, objection question,
  per panelist, investigative, one news-linked; never "what's the culture like?".
- **Stage 7 — Close & after.** Final clarifier, commitment lock, land the plane, thank-you same
  day 150-300 words, 2 nudges then close the file, 3-line/5-line debrief.
- **Stage 8 — Red flags.** Score 0/1 each; 3+ = decision conversation.
- **Plus:** Run of Show, DECISIONS, and a debrief tab (the 5-line debrief shape, TL-01).

## Claim rules

Only **résumé wording** is allowed in a room. VERIFIED-BY-ARTIFACT claims may appear;
OWNER-ONLY numbers and BANNED claims (100+ agents, $35M teletriage, $500K, IntOps 5-layer,
the 3h→15min contested claim) never appear (TL-10). The compensation floor is never spoken
(TL-02). A room that needs a banned claim to sound strong is rebuilt, not padded.

## Lessons that fire here

- **TL-01** every answer card states a number or NONE.
- **TL-02** never state the floor in a room.
- **TL-05** model Screen/Interview stages; a room is not an ATS_SUBMITTED row.

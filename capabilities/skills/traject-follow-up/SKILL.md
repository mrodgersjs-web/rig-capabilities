---
name: traject-follow-up
description: "Traject OS sub-skill, stage 10 (follow-up-negotiate): same-day thank-you, nudges (one ask, one nudge), and salary negotiation in Lucy's slots. Gated by JEV followup.note and offer.eval. The floor is never spoken; never 'flexible'/'market rate'/current pay. Sends held at Gate-D. DEFER when the classifier is down."
tags: [rig, traject-os, sub-skill, follow-up, negotiate, salary]
metadata:
  parent: traject-os
  tier: sub
  stage: follow-up-negotiate
  extends: "lucy-skills, lv-outreach, aside-job-learning"
outcome: "A same-day thank-you (150-300 words), at most one nudge per thread, and a negotiation script using Lucy's salary slots — all held at Gate-D, none stating the floor or current pay."
activation: "Load after an interview (thank-you) or when an offer or comp conversation starts."
instruction: "Draft the thank-you for same-day send by Mike (150-300 words), nudge at most once after ≥5 business days then go around, and negotiate with Lucy's slots ([looking at options] + [market LOW-HIGH] + [where does your range sit?]; low-anchor and offer-call scripts). Never say 'flexible', 'market rate', or current pay; never state the floor. Gate with followup.note and offer.eval; every send is Mike's own click and is held at Gate-D — the agent drafts and never sends."
applies_when:
  env: "Gmail and LinkedIn; Lucy salary-negotiation.md scripts"
  runtime: "Aside browser; outreach_lint; JEV followup.note / offer.eval"
  deps: "traject-debrief output; lucy-skills salary-negotiation"
  params: "interview/offer context, thread, market LOW-HIGH range"
  budget: "one thank-you per interview; one nudge per thread; one negotiation script per offer"
  scale: "per thread"
permissions:
  - fs.read
  - fs.write
  - bash
  - browser.read
  - gate-d-required:send
flow:
  - Draft the same-day thank-you (150-300 words) referencing a real moment.
  - Nudge at most once after ≥5 business days, then go around.
  - Negotiate with Lucy's slots; never state the floor or current pay.
  - Gate followup.note / offer.eval; hold every send at Gate-D.
done_when:
  - "cmd:python3 capabilities/skills/traject-os/scripts/validate_hierarchy.py"
  - "file:capabilities/harnesses/s1gate/rubrics/followup.note.json"
  - "file:capabilities/harnesses/s1gate/rubrics/offer.eval.json"
out_of_scope:
  - sending the thank-you or any nudge (Gate-D)
  - stating the compensation floor, current pay, 'flexible', or 'market rate'
  - accepting or declining an offer (Mike's decision)
---

# traject-follow-up

JEV FIRST: verdicts go to `rig-s1gate check followup.note` and `offer.eval` BEFORE any
frontier call. Classifier down: DEFER, never guess. Required signals above 0.9. A PASS is
never permission to send.

Sub-skill of `traject-os`, stage 10. Main skills: `lucy-skills` (salary-negotiation),
`lv-outreach`, `aside-job-learning`. Agent: `traject-outreach-drafter`. Harness:
`traject-outreach-session`.

## Procedure

1. **Thank-you same day** (150-300 words): reference one real moment from the conversation,
   reinforce one matched need, land the plane. Gate `followup.note`.
2. **One ask, one nudge (TL-09)**: nudge at most once after ≥5 business days, then go around to
   another contact. Never a second nudge on the same thread.
3. **Negotiate (Lucy slots)**: "[looking at options]" + "[market LOW-HIGH]" + "[where does your
   range sit?]"; low-anchor: "[thanks]" + "[light vs market]" + "[I'd be looking at range]" +
   "[out of reach?]"; offer call 3 steps: enthusiasm → package in writing + "why me?" → 24-48h
   date. **Never** "flexible", "market rate", or current pay. **Never** state the floor (TL-02).
   Gate `offer.eval`.
4. **Hold at Gate-D** for every send (TL-04: a draft is not sent).

## Lessons that fire here

- **TL-02** never state the floor in a negotiation.
- **TL-09** one ask, one nudge, then close the file.

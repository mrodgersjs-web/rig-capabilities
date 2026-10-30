---
name: traject-apply-bridge
description: "Traject OS sub-skill, stages 3-4 (tailor, apply): source-bound résumé tailoring and the Aside apply bridge that fills the form and HARD-STOPs at final Submit for Mike. Gated by JEV resume.ats/recruiter/screen and job.formfill/form.field; the Submit click is a CODE stop. NEVER submits. DEFER when the classifier is down."
tags: [rig, traject-os, sub-skill, apply, tailor, resume]
metadata:
  parent: traject-os
  tier: sub
  stage: apply
  covers: [tailor, apply]
  extends: "aside-job-resume, aside-job-operator, aside-job-browser, resume-screening-stack"
outcome: "A tailored, source-bound résumé with sha256, a filled application (from confirmed work history), packet_lint clean, and the operator held at final Submit with a receipt — Mike alone clicks Submit."
activation: "Load when a qualified role must be tailored and applied, or when Mike is on a job posting and says apply."
instruction: "Tailor only to authoritative source claims and exact employer requirements (no invented numbers), pass the lane résumé through packet_lint with the current $180K floor, fill from confirmed-work-history.json, and HARD STOP before the final Submit click (first-five human-click pilot). Never submit; a local draft is not sent."
applies_when:
  env: "Aside browser on an ATS (myworkdayjobs, greenhouse, lever, ashby, etc.); ~/.applypilot store"
  runtime: "ATS form fill; lucy-skills tailor_resume.py + packet_lint.mjs"
  deps: "aside-job-operator; ~/.applypilot/{resume-registry.json,confirmed-work-history.json,fit-gate}"
  params: "qualified role, lane résumé, req id"
  budget: "one role per run; three tailoring passes before escalating"
  scale: "one application at a time (single-writer)"
permissions:
  - fs.read
  - fs.write
  - bash
  - browser.read
  - browser.modify
  - gate-d-required:submit
flow:
  - Tailor the résumé to the posting's exact requirements with source-bound claims only.
  - Run packet_lint (Lucy apply-standard rules A1-A12; A3 is not implemented in the script) at floor $180K and gate resume.ats + resume.recruiter.
  - Fill the form from confirmed-work-history.json and confirmed answers; gate job.formfill.
  - HARD STOP before final Submit; log the held state and the receipt path.
done_when:
  - "cmd:python3 capabilities/skills/traject-os/scripts/validate_hierarchy.py"
  - "file:capabilities/harnesses/s1gate/rubrics/job.formfill.json"
  - "file:capabilities/harnesses/s1gate/rubrics/resume.ats.json"
out_of_scope:
  - clicking the final Submit or Send button (Mike alone, first-five pilot)
  - inventing a metric, title, or employer fact not in a source or the claims ledger
  - attaching a résumé on outreach touch 1 (outreach_lint O-resume)
---

# traject-apply-bridge

JEV FIRST: tailoring verdicts go to `rig-s1gate check resume.ats`, `resume.recruiter`,
`resume.screen`; form-fill to `job.formfill` and `form.field` — all BEFORE any frontier call.
Classifier down: DEFER, never guess. A required signal passes only above 0.9.

Sub-skill of `traject-os`, stages 3-4. Main skills: `aside-job-resume`, `resume-screening-stack`,
`aside-job-operator`, `aside-job-browser`. Agents: `traject-apply-operator`,
`traject-claim-verifier`, `traject-dedupe-checker`. Harness: `traject-apply-one-role`.

## Procedure

1. **Tailor (source-bound)**: use `~/.aside/u/0/skills/user/lucy-skills/scripts/tailor_resume.py`
   against the posting's literal requirements. Every tailored claim traces to a source or the
   claims ledger; contested numbers (e.g. the 3h→15min claim) stay out (TL-10).
2. **Lint**: run `~/.aside/u/0/skills/user/lucy-skills/scripts/packet_lint.mjs` with the current
   **$180K** floor. The FLOOR constant was stale at $200K against the 2026-09-27 $180K decision and
   was fixed 2026-09-28 (selftest 46/46): re-derive the floor from the decision, never from the
   constant (TL-11). Fix a claim on every surface (TL-07).
   Gate `resume.ats` then `resume.recruiter`; a required signal below 0.9 is a rewrite, max 3.
3. **Fill**: populate from `~/.applypilot/confirmed-work-history.json` and confirmed answers;
   gate `job.formfill`/`form.field`. A field with no confirmed answer is left for Mike, never invented.
4. **HARD STOP at final Submit.** The first-five human-click pilot
   (`~/.aside/u/0/projects/rig-job/OPERATING-PLAN.md`) means Mike alone clicks Submit/Send.
   The operator fills, reviews, and stops; it records the held state and the receipt path once
   Mike submits. A local filled form is not a sent application (TL-04).
5. **Receipt + reach**: after Mike submits, capture the receipt, then seed T1/T5 outreach drafts
   via `outreach_lint` (one ask, one nudge) in `traject-reach`, and seed a Traject room when a
   human replies (`traject-room-build`).

## Lessons that fire here

- **TL-04** a filled/local form is not SENT; only a receipt makes it submitted.
- **TL-10** contested or unsupported claims stay out of the résumé and the room.
- **TL-12** Mike alone clicks final Submit (first-five human-click pilot).
